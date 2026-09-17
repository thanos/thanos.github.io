---
title: "SoftGPU: Impersonating a GPU Without Lying"
description: "Discovery APIs tempt emulators to invent CU counts and wave sizes. SoftGPU treats device identity as a contract with provenance."
date: 2026-08-10
tags:
  - SoftGPU
  - HSA
  - HIP
  - GPU
  - device profile
  - honesty
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 3 of [SoftGPU](https://thanos.github.io/series/softgpu/). Part 2 put SoftGPU at the ROCr/HSA boundary. Once you are there, discovery APIs start asking questions you may not be able to answer.

How many compute units? What is the wave size? How large is a queue? Emulators like to invent those numbers so HIP will treat them as a device. SoftGPU treats identity as a **contract with provenance**. An empty field is useful information. A guessed 64 is a lie that will surface three layers later as someone else’s bug.

## Identity has a source

```text
DeviceProfile (JSON, provenance fields)
        ↓
VirtualAgent (name, vendor, device=GPU, FEATURE=KERNEL_DISPATCH)
        ↓
PackedHandle [kind | generation | index]
        ↓
hsa_iterate_agents / hsa_agent_get_info
        ├── regions/pools → SoftGPU host allocator
        └── signals / queues → observe; do not execute packets
```

Handles are generation-safe ([ADR-0002](https://github.com/thanos/softgpu/blob/main/docs/adr/0002-generation-safe-handles.md)). A handle that survives shutdown and re-init is invalid, not recycled luck. Stale and forged handles fail closed.

Advertised agent fields are labeled by where they come from:

| Attribute | Value source | Provenance |
| --- | --- | --- |
| `NAME` | profile `product_name` | profile identity |
| `VENDOR_NAME` | profile `vendor` | profile identity |
| `DEVICE` | GPU | SoftGPU virtual-agent policy |
| `FEATURE` | `KERNEL_DISPATCH` | queue + AQL intercept — **not** kernel execution |
| `QUEUE_*` | SoftGPU software defaults | SoftGPU software limits |
| `VERSION_MAJOR` / `MINOR` | `1` / `2` | HSA Runtime 1.2 family target |

Unsupported attributes still return `HSA_STATUS_ERROR_INVALID_ARGUMENT`. A wavefront-size query does not get a guessed 32 or 64.

The R9700 profile records a product name and a compiler target. It leaves numeric limits unknown where they have not been established. Recording “R9700” is not evidence of that card’s VRAM or LDS capacity.

## What FEATURE actually means

`HSA_AGENT_INFO_FEATURE` is a capability bitfield. `KERNEL_DISPATCH` means “this agent can be treated as something you submit kernel-dispatch packets to.” It does not mean SoftGPU ran a kernel.

SoftGPU advertises the bit so queue create is meaningful. Packet observation, and later diagnostic completion, still have to say in logs that they are not kernel success. See [what FEATURE means](https://github.com/thanos/softgpu/blob/main/docs/what-feature-means.md) in the repo.

A HIP-linked probe may load SoftGPU, discover the agent via **HSA** APIs, and create SoftGPU queues. SoftGPU does **not** promise packet execution or guaranteed `hipGetDeviceCount > 0`.

## Reproducing it

```bash
cargo test -p softgpu-hsa --locked
cargo test -p softgpu-core --locked runtime::
# Linux x86_64 + ROCm (CI):
#   bash environments/rocm-x86_64/ci-entrypoint.sh
```

Traces record profile and fidelity on init, plus memory, queue, and doorbell events.

Next: [HSA queues and signals](https://thanos.github.io/articles/2026-09-17-softgpu-04-hsa-queues-and-signals/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-03-impersonating-without-lying/). Repo: [github.com/thanos/softgpu](https://github.com/thanos/softgpu).
