---
title: "SoftGPU: The First gfx1201 Kernel"
description: "Dispatch to machine code to a memory result for tiny_add — a named gfx1201 subset, a SoftGPU calling convention, and still not unrestricted hipLaunchKernel."
date: 2026-09-17
tags:
  - SoftGPU
  - gfx1201
  - AMDGPU
  - ISA
  - AQL
  - HIP
  - kernel
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 12 of [SoftGPU](https://thanos.github.io/series/softgpu/). Decoding a SALU subset is not yet a kernel. Developers still need a **real dispatch → machine code → memory result** path without SoftGPU pretending to run arbitrary hipcc fat binaries.

## What SoftGPU claims here

| Claim | SoftGPU meaning |
| --- | --- |
| **Kernel** | `tiny_add`: `b[i] = a[i] + 1` for `i32` elements |
| **Machine code** | `llvm-mc -mcpu=gfx1201` bytes (`TINY_ADD_TEXT`) |
| **Subset** | `softgpu-gfx1201-e2e-tiny-v1` (SMEM/VOP2/GLOBAL plus prior SALU) |
| **Calling convention** | SoftGPU sets `s[4:5]=kernarg`, `v0=global_id_x`, EXEC |
| **AQL** | Registered `kernel_object` plus SoftGPU kernarg → `softgpu_kernel_success` |
| **Fidelity** | **Architectural ISA** for that subset only |

Unregistered kernels still complete as `diagnostic_complete_no_execution`. That is the part-5 contract, still in force.

```text
AQL KERNEL_DISPATCH
        ↓
Runtime: registered SoftGPU ISA image?
        ├── no  → diagnostic_complete_no_execution
        └── yes → run_code_1d (waves) on SoftGPU allocations
                        ↓
                 softgpu_kernel_success + completion signal 0
```

## Instruction coverage (enumerated)

- `s_load_b64`, `s_waitcnt`, `s_endpgm`
- `v_lshlrev_b32_e32`, `v_add_nc_u32_e32`
- `global_load_b32`, `global_store_b32`
- the earlier SALU subset remains available

Everything else traps.

## Differential

ISA `tiny_add` matches SoftGPU host reference (`tiny_add_host_ref`) and the Functional IR `tiny_add` semantics (`b[i] = a[i] + 1`). Hardware differential against an R9700 is deferred. As of the 16 September 2026 status snapshot that is still **not claimed** (Phase 12 / v0.9).

Encodings and `.text` were observed with llvm-mc (Homebrew LLVM 21.1.8), 16 September 2026, cross-checked against LLVM AMDGPUUsage. SoftGPU packaging is hand-maintained tables plus `TINY_ADD_TEXT`.

```bash
cargo test -p softgpu-amd-isa --test phase11_kernel --locked
cargo test -p softgpu-core --test phase11_aql_isa --locked
cargo run --locked -- run-kernel --builtin tiny_add --n 64
```

## Honesty limits

This is not a claim of full gfx1201 or unrestricted HIP `hipLaunchKernel` success. The calling convention is SoftGPU-defined for this tiny kernel. `s_waitcnt` remains a SoftGPU no-op under the sequential interpreter.

The next hardware gate is R9700 conformance and profile hardening. Until that evidence exists, do not quote these results as agreement with a particular AMD GPU.

Next: [why Rust for a software GPU, and what Rust cannot prove](https://thanos.github.io/articles/2026-09-17-softgpu-13-why-rust/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-12-first-gfx1201-kernel/).
