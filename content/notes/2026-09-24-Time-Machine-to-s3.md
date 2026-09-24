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


Dgitoing a double-check reveals two crucial macOS networking and protocol quirks you **must** handle to make `tmutil` accept it.

Here is exactly what it takes to make the SMB loopback approach work:

### 1. The Loopback Alias Trick (Avoiding `127.0.0.1`)

You cannot simply bind your custom SMB daemon to `127.0.0.1:445`. macOS has built-in protections (and potential deadlocks) regarding loopback SMB mounts, and it frequently conflicts with macOS's native File Sharing daemon (if enabled).

**The Solution:** You must bind an IP alias to the macOS loopback interface (`lo0`).

```bash
sudo ifconfig lo0 alias 127.0.0.2/32

```

You then bind your custom SMB server to `127.0.0.2:445`. When you do this, the macOS network stack treats it as a distinct remote network device. You can then register the destination:

```bash
sudo tmutil setdestination -a "smb://user:password@127.0.0.2/s3-backup"

```

### 2. Apple SMB Extensions (AAPL Context)

You cannot use a vanilla SMB2/3 library. Time Machine aggressively validates the destination before it will start a backup. During the initial SMB protocol negotiation, Time Machine looks for **Apple SMB Extensions (AAPL Context)**.

Your SMB server must negotiate the `AAPL` context and explicitly advertise the `TM_SUPPORT` flag. If it doesn't, macOS will reject the drive, treating it as a generic Windows file share rather than a Time Machine-capable NAS.

**The Shortcut:** You don't have to write this from scratch. The developers of FUSE-T (a project that replaces macFUSE by using localhost SMB or NFS instead of Kernel Extensions) maintain a specialized Go fork: `macos-fuse-t/go-smb2`. It already implements Apple's proprietary extensions, including Bonjour advertisement, UNIX file modes, extended attributes (xattr), and the AAPL context.

### 3. Fsync to S3 Translation (The Gateway Logic)

Because Time Machine operates by modifying 8MB chunk files (`bands`) inside the `.backupbundle`, your SMB server still has to do the heavy lifting of caching and flushing.

* **Read/Write Operations:** When the SMB server receives `SMB2 READ` or `SMB2 WRITE` requests for a band file, it operates on a local NVMe/SSD staging directory.
* **The S3 Trigger:** When Time Machine finishes a backup phase, it sends `SMB2 FLUSH` (POSIX `fsync`). Your SMB server intercepts this flush. It looks at the "dirty" 8MB bands in the local staging directory and dispatches them to S3 via asynchronous `PutObject` or multipart uploads.

### Why this beats FUSE on macOS

By using the local SMB approach, you completely eliminate the need for Apple's **FSKit** or legacy Kernel Extensions (KEXTs). You are building a standard user-space networking application that macOS trusts implicitly because it speaks Apple's own dialect of SMB3. All network timeouts, sleep/wake cycles, and APFS bundle management are handled perfectly by the native macOS SMB client.