---
title: "SoftGPU: Emulation Versus Simulation"
description: "People say GPU emulator when they mean four different things. SoftGPU names which kind of execution it is performing, or it will claim hardware fidelity it does not have."
date: 2026-09-01
tags:
  - SoftGPU
  - emulation
  - simulation
  - functional IR
  - GPU
  - HIP
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 7 of [SoftGPU](https://thanos.github.io/series/softgpu/). People say “GPU emulator” when they mean very different things. SoftGPU must name which kind of execution it is performing, or it will silently claim hardware fidelity it does not have.

## Four words, four claims

| Word people use | SoftGPU meaning |
| --- | --- |
| **ABI / protocol observation** | Call the same APIs; validate packets; do not run kernels (parts 2–6) |
| **Functional execution** | Run a disclosed IR on the CPU with GPU-like ids and memory; results are semantic, not ISA evidence |
| **Architectural ISA** | Decode and execute real gfx1201 encodings with sourced tables (later parts) |
| **Cycle-accurate simulation** | Not SoftGPU’s goal |

The first functional phase is **functional execution**, not ISA emulation. Cycle-accurate gem5-style modeling of an R9700 remains out of scope. Hardware still exists for agreement tests that have not landed.

## Why not “just run the code object”?

AMD code objects are ELF plus MessagePack metadata plus machine code. SoftGPU can **inspect** metadata. Claiming that those binaries contain a portable high-level IR SoftGPU can execute would be dishonest without toolchain proof.

So the functional path locks a **SoftGPU-owned** IR (`softgpu-sfir-v1`):

1. Tiny reference C (`tiny_add.ref.c`) defines intended semantics.
2. A hand translation produces SFIR (JSON and a Rust builder).
3. The CPU interpreter runs SFIR under a deterministic workgroup schedule.
4. Every report is labeled `not_gfx1201_isa_emulation`.

Details: [functional-path.md](https://github.com/thanos/softgpu/blob/main/docs/functional-path.md).

## What “global id” means here

SFIR exposes `global_id`, `local_id`, and `workgroup_id` as SoftGPU software identifiers. They match the usual HIP/OpenCL indexing formulas for the launch configuration SoftGPU was given. They are not evidence of how a particular wavefront scheduler would order memory on silicon.

That distinction is the whole point of this installment. A correct `b[i] = a[i] + 1` on the host is a semantic result. It is not gfx1201.

Next: [grids, workgroups, waves, and barriers](https://thanos.github.io/articles/2026-09-17-softgpu-08-grids-workgroups-waves/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-07-emulation-vs-simulation/).
