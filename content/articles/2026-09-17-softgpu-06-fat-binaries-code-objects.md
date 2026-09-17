---
title: "SoftGPU: Fat Binaries, ELF Notes, and gfx1201"
description: "HIP ships device binaries, not source. SoftGPU reads AMDGPU metadata notes with a bounded parser — and still does not execute the ISA bytes."
date: 2026-08-22
tags:
  - SoftGPU
  - ELF
  - AMDGPU
  - gfx1201
  - HIP
  - code object
  - metadata
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 6 of [SoftGPU](https://thanos.github.io/series/softgpu/). HIP applications ship **device binaries**, not source. SoftGPU cannot “run a kernel” until it can **safely identify** which ELF notes and metadata describe that kernel — without inventing fields or decoding ISA prematurely.

## Fat binary versus code object

```text
HIP fat binary / bundle
    └── one or more device images
            └── AMDGPU code object (ELF)
                    ├── machine-code sections (ISA — SoftGPU does not execute yet)
                    └── notes: AMDGPU / NT_AMDGPU_METADATA (MessagePack)
```

A **code object** is the ELF image the HSA loader registers. SoftGPU reads the **metadata note**, not the ISA bytes. Finding a kernel name is not proof SoftGPU can execute it. The inspect tool prints JSON labeled `metadata_only_no_isa_execution`.

## The notes that matter

For code-object V3+ (LLVM AMDGPUUsage):

| Owner | Type | Payload |
| --- | --- | --- |
| `AMDGPU` | `NT_AMDGPU_METADATA` (32) | MessagePack map |

Important keys:

- `amdhsa.version` — SoftGPU accepts `[1,0]`…`[1,2]`
- `amdhsa.target` — SoftGPU requires a `gfx1201` substring
- `amdhsa.kernels[]` — name, symbol, kernarg/group/private sizes, `.args`

`amdhsa.target` strings look like `amdgcn-amd-amdhsa--gfx1201`. The gate is intentionally narrow: **gfx1201 only**. Other targets are rejected with `UnsupportedTarget`, not silently coerced.

## Why bounds matter

Code objects are untrusted input. SoftGPU uses a **bounded** ELF walker and MessagePack decoder: file size, section count, note count, string/map/array limits, recursion depth. Oversized or exotic encodings fail closed. A parser that panics on junk is a vulnerability, not a GPU.

Details live in [code-object.md](https://github.com/thanos/softgpu/blob/main/docs/code-object.md). Fixtures sit under `fixtures/amd-code-object/`.

## What this enables next

Inspection is the prerequisite for two different later paths. One is a disclosed **functional** IR that is *not* “run the code object.” The other is architectural ISA for a named subset, with goldens from `llvm-mc`. Neither path is implied by successfully printing a kernel name.

Next: [emulation versus simulation](https://thanos.github.io/articles/2026-09-17-softgpu-07-emulation-vs-simulation/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-06-fat-binaries-code-objects/).
