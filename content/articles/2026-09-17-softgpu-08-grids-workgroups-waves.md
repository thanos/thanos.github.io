---
title: "SoftGPU: Grids, Workgroups, Waves, and Barriers"
description: "Wave, warp, and subgroup mean different things on different vendors. SoftGPU defines a software semantic machine without pretending it is gfx1201 silicon."
date: 2026-09-07
tags:
  - SoftGPU
  - waves
  - workgroups
  - barriers
  - GPU
  - synchronization
  - functional IR
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 8 of [SoftGPU](https://thanos.github.io/series/softgpu/). “Wave,” “warp,” and “subgroup” mean different things on different vendors. SoftGPU must define a **software** semantic machine without pretending it is gfx1201 silicon.

## SoftGPU vocabulary

| Term | SoftGPU meaning |
| --- | --- |
| **Grid / workgroup / local id** | Same indexing formulas as the functional IR in part 7 |
| **Wave** | Contiguous block of `wave_size` flat local ids inside a workgroup |
| **Lane** | Index of a workitem inside its SoftGPU wave (`flat_local % wave_size`) |
| **Group memory** | Per-workgroup CPU arena; not R9700 LDS capacity evidence |
| **Barrier** | SoftGPU generation sync between barrier-separated program segments |
| **Divergence** | Structured `if` / `while` with per-lane masks; reconverge after the construct |

Partial waves (workgroup size not divisible by `wave_size`) are first-class: the last wave simply has fewer live lanes. SoftGPU’s `wave_size` is a software parameter, 32 or 64, not R9700 wavefront evidence.

## The barrier model

SoftGPU splits a program body on top-level `barrier` ops. For each segment, every wave runs the segment to completion (lockstep within the wave for divergent `if`). Then the next segment begins. That is a deterministic **wave_barrier** schedule.

Divergent barriers (a barrier inside `if` or `while`) are **unsupported** and fail validation. They are not silently linearized.

## Atomics, honestly

`atomic_add` on global or group returns the previous i32 value. SoftGPU applies a **functional** sequential atomic on the host arena. Named `scope` and `order` fields are recorded in the IR for honesty. They do **not** claim AMDGPU memory-model semantics.

## What this is not

- Not gfx1201 wavefront scheduling
- Not a proof of HIP kernel success via AQL
- Not a sanitizer completeness claim — that is the next part, and even there the subset is declared

Next: [building GPU sanitizers on SoftGPU](https://thanos.github.io/articles/2026-09-17-softgpu-09-gpu-sanitizers/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-08-grids-workgroups-waves/).
