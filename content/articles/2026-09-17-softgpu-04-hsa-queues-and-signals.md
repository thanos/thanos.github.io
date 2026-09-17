---
title: "SoftGPU: HSA Queues and Signals"
description: "HIP eventually submits work through user-mode queues. SoftGPU proves observation, wraparound, and wait-cancel before it ever runs a kernel."
date: 2026-09-17
tags:
  - SoftGPU
  - HSA
  - AQL
  - queues
  - signals
  - concurrency
  - ROCm
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 4 of [SoftGPU](https://thanos.github.io/series/softgpu/). HIP and ROCm eventually submit work through **user-mode queues**: a ring of AQL packets, write and read indexes, and a **doorbell signal**. If you skip concurrency and ownership tests and jump to “run the ISA,” the races you hit later will look like instruction bugs.

## The ring, before a processor exists

```text
producer writes packet[i] (type byte last)
producer stores write_index = i+1
producer stores doorbell
        ↓
SoftGPU observes packets in [observed_through, write_index)
  - validate header type
  - record packet index exactly once
  - do NOT execute kernels
  - do NOT pretend HSA read_index advanced as GPU completion
```

Queue size is a power of two. Logical indexes grow monotonically; the physical slot is `index % size`. SoftGPU tests walk past one full ring so wraparound is covered before any packet processor exists. A write index advanced over packets that are still `INVALID` is a validate failure, not a successful dispatch. Producers publish the type byte last so observers never see a half-written packet as `KERNEL_DISPATCH`.

SoftGPU advertises `FEATURE=KERNEL_DISPATCH` so queue create is meaningful. Observation remains an honesty boundary: SoftGPU saw and classified the packet. SoftGPU did not run it as a GPU kernel.

## Signals and waiting

Signals are SoftGPU host atomics. Wait conditions (`EQ`, `NE`, `LT`, `GTE`) spin with an optional timeout. Destroy, queue teardown, and runtime shutdown **cancel** waiters so “queue destroy during wait” is deterministic.

HSA wait APIs clone the signal `Arc` under SoftGPU’s process mutex, then wait **outside** the lock so cancel can proceed. That is a host-runtime rule, not a claim about hardware memory ordering of doorbells.

## Ownership

| Object | SoftGPU rule |
| --- | --- |
| Allocation | Tracked base pointer and metadata; unknown free fails closed |
| Signal | Generation-safe handle; doorbells owned by their queue |
| Queue | SoftGPU owns the ABI struct and the packet buffer; destroy frees both |
| Packet | Observed once; not “completed” as kernel success |

Free of a non-SoftGPU pointer is invalid argument. Queue create with a non-power-of-two size is invalid argument. Exceeding SoftGPU’s queue cap is out of resources.

## Why this precedes execution

A packet processor that runs kernels before proving observe-once under producer/consumer stress, wait-cancel on destroy, wraparound, and resource caps will mis-attribute races as ISA bugs. SoftGPU’s charter therefore places queue and signal stress here, and AQL interception — still not kernel execution — in the next part.

```bash
cargo test -p softgpu-core --locked --test phase3_charter
cargo test -p softgpu-hsa --locked --test phase3_memory_queue
```

See also [concurrency-phase3.md](https://github.com/thanos/softgpu/blob/main/docs/concurrency-phase3.md).

Next: [HSA/AQL dispatch](https://thanos.github.io/articles/2026-09-17-softgpu-05-hsa-aql-dispatch/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-04-hsa-queues-and-signals/).
