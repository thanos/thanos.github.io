---
title: "Time Machine to S3"
description: "Building a custom driver to back up Time Machine to an S3 bucket via FUSE is technically possible, but Time Machine expects POSIX block storage and S3 is an immutable object store."
date: 2026-09-24
tags:
  - Time Machine
  - S3
  - FUSE
  - macOS
  - backup
draft: false
authors:
  - Thanos Vassilakis
---

Building a custom driver to back up Time Machine to an S3 bucket via FUSE is technically possible, but it requires solving a massive architectural mismatch: Time Machine expects a POSIX-compliant block storage system, while S3 is an immutable object store.

When Time Machine backs up over a network or FUSE mount, it creates a virtual disk image called a '.sparsebundle'. This bundle contains a 'bands/' directory filled with fixed-size files (historically 8MB, but up to 512MB for modern APFS backups).

Here is exactly what you would need to engineer to make this work without destroying performance or corrupting the backup.

## 1. The FUSE Layer (macFUSE vs. FUSE-T)
You need a userspace file system bridge to mount the S3 bucket as a local volume.

**Avoid macFUSE:** macFUSE relies on kernel extensions (kexts). Apple has deprecated third-party kexts, and installing them on Apple Silicon Macs requires users to boot into Recovery Mode and lower their system security policy.

**Use FUSE-T:** FUSE-T acts as a drop-in replacement for macFUSE but works by running a local NFSv4 server in userspace. It requires no kexts and is completely seamless for the end user on modern macOS.

## 2. Intelligent Write-Back Caching (The Hardest Part)
S3 does not support partial, in-place byte-range overwrites. If Time Machine modifies a 16KB block inside a 512MB band file, standard FUSE tools (like s3fs or goofys) will download the entire 512MB file, apply the 16KB change, and re-upload the entire 512MB file. This read-modify-write amplification will instantly choke your bandwidth and cause Time Machine to time out.

Your driver must implement a complex local cache:

**Delta Tracking:** When Time Machine writes to a band, write the delta to a local NVMe/SSD cache rather than S3.

**Coalescing:** Pool multiple small writes to the same band locally.

**Asynchronous Flushes:** Only PUT the modified band file to S3 when it is evicted from the local cache, or when Time Machine issues an fsync or cleanly unmounts the sparse bundle.

## 3. Range-Read Optimization
While you cannot do partial writes to S3, you can do partial reads. Your driver must translate POSIX read() calls into S3 HTTP GET requests with Range headers. If Time Machine only needs to read a filesystem tree table from the sparse bundle, your driver should fetch only those specific bytes from the S3 object, not the whole 512MB band.

## 4. POSIX Strictness and Locking
Time Machine and Apple's DiskImages framework (hdiutil) are highly unforgiving regarding file system semantics.

Your driver must support strict POSIX file locking (byte-range locks).

It must gracefully handle F_FULLFSYNC requests. If the driver acknowledges a sync to the OS before the band is fully committed to S3, a power loss or network drop will irrevocably corrupt the APFS sparse bundle.

It must reliably manage Apple Double files (._ files) and extended attributes (xattrs), which S3 doesn't natively support (they must be mapped to S3 object metadata or stored alongside the objects).

## The Corruption Risk
The primary reason standard FUSE-to-S3 adapters fail with Time Machine is network latency. The macOS DiskImages UI is designed for local disks or high-throughput LANs (SMB). If your driver pauses to upload a 512MB band to S3 and blocks the I/O thread, macOS may assume the drive has dropped, force-dismount the sparse bundle, and corrupt the APFS volume inside it.

## A Better Alternative
Because adapting a block-level backup tool to an object-store API is highly fragile, most Mac users and sysadmins avoid Time Machine for S3 entirely. Instead, they use tools engineered natively for object storage:

Arq Backup or Restic: These tools bypass sparsebundles and FUSE entirely. They natively chunk files, deduplicate them, encrypt them, and upload them as distinct objects via S3 APIs.