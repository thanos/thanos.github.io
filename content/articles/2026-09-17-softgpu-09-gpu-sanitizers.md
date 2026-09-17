---
title: "SoftGPU: Building GPU Sanitizers"
description: "Hardware hides memory and sync defects until a rare schedule hits them. SoftGPU detects a declared class of defects with workgroup, wave, and lane context."
date: 2026-09-17
tags:
  - SoftGPU
  - sanitizer
  - race detection
  - GPU
  - memory safety
  - barriers
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 9 of [SoftGPU](https://thanos.github.io/series/softgpu/). Hardware runs hide many memory and synchronization defects until a rare schedule hits them. SoftGPU’s value for developers is to detect a **declared** class of defects with workgroup, wave, and lane context, without pretending to be an AMDGPU memory-model oracle.

NVIDIA’s Compute Sanitizer already exists for CUDA. SoftGPU is not a claim of parity with that tool. It is a path that can run without allocating a physical GPU to every CI job, on the execution model SoftGPU actually implements.

## The sanitizer model

| Concept | SoftGPU meaning |
| --- | --- |
| **Shadow** | Per-byte allocated / uninitialized / initialized / freed for global and group arenas |
| **Hard faults** | Out-of-bounds, use-after-free, shadow-size limit — always fail closed |
| **Soft findings** | Uninitialized read, race, missing barrier, cross-workgroup race — fail-fast or collect |
| **Happens-before** | SoftGPU barrier generations under `wave_barrier`; same generation ⇒ no SoftGPU sync |

Modes: `off`, `collect`, `fail_fast`. Findings carry actor `WorkItemId` (workgroup, wave, lane, flat local) and an optional `other` actor.

Every finding can be packaged as `softgpu-sanitizer-replay-v1` with program name, provenance, and exec config. Another engineer should be able to replay the finding without guessing the schedule.

## Declared race subset

SoftGPU reports a conflict when two **different** workitems touch overlapping bytes with at least one non-atomic write, and:

- **same workgroup, same barrier generation** → `race` (global) or `missing_barrier` (group);
- **different workgroups** on global → `cross_workgroup_race`.

SoftGPU atomics on both sides of an access are treated as ordered by the sequential interpreter. There is no SoftGPU race between those atomics. That is an interpreter rule, not a proof about `atomicAdd` on silicon.

## Blind spots (honest)

- Not AMDGPU acquire/release/scope evidence
- Not a claim about silent host-pointer aliasing outside SoftGPU arenas
- Not true hardware concurrency; schedule order alone does not define SoftGPU races
- Divergent barriers remain validate-time errors, not sanitizer findings

The suite covers OOB, use-after-free, uninitialized group reads, workgroup races, missing barriers, and cross-workgroup races in SFIR. It does not claim full GPU sanitizer parity with vendor tools, and it does not map findings to original HIP source lines.

```bash
cargo test -p softgpu-functional --test phase8_sanitize --locked
cargo run --locked -- run-functional --builtin tiny_add --sanitize collect
```

Next: [debugging a machine made of SoftGPU lanes](https://thanos.github.io/articles/2026-09-17-softgpu-10-debugging-lanes/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-09-gpu-sanitizers/).
