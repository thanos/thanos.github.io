---
title: "SoftGPU: HSA/AQL Dispatch, Without Running the Kernel"
description: "A HIP launch ends as a 64-byte AQL packet. SoftGPU validates, traces, and diagnostically completes that packet — and still does not execute it."
date: 2026-08-20
tags:
  - SoftGPU
  - AQL
  - HSA
  - HIP
  - dispatch
  - ROCm
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 5 of [SoftGPU](https://thanos.github.io/series/softgpu/). A HIP “kernel launch” is not one API call. It is a chain that ends in an **AQL packet** on a user-mode queue. Emulators that jump straight to “run ISA” skip the packet contract that HIP and ROCr actually share.

## The path HIP already uses

```text
HIP launch APIs
    → HIP runtime prepares kernel object + kernarg
    → producer writes hsa_kernel_dispatch_packet_t into the queue ring
    → producer stores write_index, then doorbell
    → packet processor reads packets, runs (or rejects), stores completion
```

SoftGPU implements the **middle**: decode, validate, trace, and an experimental **no-execution** completion. It does **not** run kernel code. That contract is written down as [aql-diagnostic-contract.md](https://github.com/thanos/softgpu/blob/main/docs/aql-diagnostic-contract.md).

## The 64-byte packet

Under the large model, each AQL packet is **64 bytes**. SoftGPU’s parser follows pinned ROCR `hsa.h` field offsets:

| Offset | Field |
| --- | --- |
| 0 | `header` (type in the low 8 bits) |
| 2 | `setup` (dimensions in the low bits) |
| 4–10 | workgroup size x/y/z |
| 12–24 | grid size x/y/z |
| 24 / 28 | private / group segment size |
| 32 | kernel object |
| 40 | kernarg address |
| 56 | completion signal |

Producers write the **type byte last** so observers never see a half-published packet as `KERNEL_DISPATCH`.

## What the processor does

```text
doorbell store
    → observe packets in [observed_through, write_index) once
    → parse_supported_packet (dispatch or minimal barrier)
    → on OK:  DispatchValidated + capture bytes
              store completion := 0 (diagnostic)
              invalidate slot; advance read_index
              label diagnostic_complete_no_execution / not_kernel_success
    → on Err: DispatchRejected
              leave completion unchanged
              still invalidate + advance read_index
```

`KERNEL_DISPATCH` gets full field validation. `BARRIER_AND` / `BARRIER_OR` get a minimal type-and-completion check; dependency signals are unchecked. `AGENT_DISPATCH` and other types are diagnostic rejects. A slot still marked `INVALID` is an observe error: the producer failed the publish-type-last rule.

## Capture and replay

Validated packets keep an owned `[u8; 64]`. Offline `replay_dispatch` re-parses those bytes without the original process and without depending on live host pointers SoftGPU once classified. Replay reclassifies a non-null kernarg as `foreign_opaque`.

## What “complete” means here

In hardware ROCr, completion usually means the GPU finished the dispatch. In this SoftGPU phase, completion means **only** that SoftGPU applied the documented diagnostic contract. Logs and probes must print that distinction. This is never unrestricted HIP kernel success.

Later, a registered SoftGPU ISA image with SoftGPU-owned kernarg can take a different path, `softgpu_kernel_success`. That is a later installment, not this one.

Next: [fat binaries and code-object metadata](https://thanos.github.io/articles/2026-09-17-softgpu-06-fat-binaries-code-objects/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-05-hsa-aql-dispatch/).
