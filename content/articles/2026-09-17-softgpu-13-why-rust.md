---
title: "Why Rust for a Software GPU — and What Rust Cannot Prove"
description: "Rust is SoftGPU’s host language because ownership and explicit types fit an evidence system. It does not prove an HSA ABI, a GPU memory model, or an R9700."
date: 2026-09-17
tags:
  - SoftGPU
  - Rust
  - FFI
  - HSA
  - GPU
  - unsafe
  - Zig
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 13 of [SoftGPU](https://thanos.github.io/series/softgpu/), a companion to the runtime path in parts 1–12. Choosing Rust does not make a virtual GPU correct. It changes which mistakes are cheap to catch in the host, and which still need probes, traces, and hardware.

## Two different “Rust GPU” stories

| Story | What it means | SoftGPU stance |
| --- | --- | --- |
| Rust **host** runtime | Emulator, adapters, parsers, sanitizers, CLI in Rust | **Primary path** |
| Rust **device** kernels | `amdgcn-amd-amdhsa` / rust-gpu style kernels | Optional research; **not** the compatibility gate |

The rustc book labels `amdgcn-amd-amdhsa` as **Tier 3** with special build requirements ([rustc platform support](https://doc.rust-lang.org/rustc/platform-support/amdgcn-amd-amdhsa.html)). SoftGPU’s compatibility story uses the **real HIP compiler** and real HIP userspace. That is the same boundary as [part 2](https://thanos.github.io/articles/2026-09-17-softgpu-02-hip-to-silicon/).

## Why Rust fits this project

- Explicit ownership helps manage handle tables, packet buffers, and trace lifetimes.
- Enums and newtypes make fidelity levels, error categories, and profile provenance harder to mix up accidentally.
- A small, auditable `unsafe` surface at the cdylib boundary is preferable to a large implicit unsafe culture — **if** it is reviewed per [unsafe-ffi-policy.md](https://github.com/thanos/softgpu/blob/main/docs/unsafe-ffi-policy.md).
- `clippy`, rustfmt, fuzzers, and Miri where applicable support a fail-closed CI culture.

## What Rust cannot prove

Rust’s type system does **not** prove:

- ROCr/HSA **C ABI** layouts, symbol versions, or calling conventions;
- AQL producer/consumer memory ordering against a foreign runtime;
- gfx1201 instruction semantics;
- that a kernel is data-race-free on a GPU memory model;
- employment outcomes, or “we replace an R9700.”

Those require specifications, independent C probes, traces, differential tests, and eventually hardware. SoftGPU’s layout probe, load-proof harness, and llvm-mc goldens exist because Rust is not a substitute for them.

## Rust versus Zig, locally

Zig is excellent for explicit memory and cross-compilation. SoftGPU chooses Rust for the host runtime to leverage algebraic types, a strong testing culture, and ecosystem sanitizers and fuzzers for a long-lived evidence system. That is a project-local choice, not a universal ranking. Existing Zig inference work remains a separate client, not something SoftGPU rewrites.

## Unsafe as negative space

The earliest SoftGPU skeleton deliberately contained **no** `unsafe` and **no** FFI exports. The educational point is negative space: do not open an ABI surface until layout probes and panic policy exist. The first exported function, queue atomics against foreign memory, parsers that need `unsafe`, and generated ISA tables are the moments to re-audit, not the moments to relax the honesty rule.

The [nomicon](https://doc.rust-lang.org/nomicon/) is relevant reading. It is not a certificate.

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-13-why-rust/). Series index: [SoftGPU](https://thanos.github.io/series/softgpu/). Repo: [github.com/thanos/softgpu](https://github.com/thanos/softgpu).
