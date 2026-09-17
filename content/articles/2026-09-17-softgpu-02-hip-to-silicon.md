---
title: "SoftGPU: The GPU Stack from HIP to Silicon"
description: "Applications talk HIP. Silicon speaks packets and firmware. SoftGPU substitutes at ROCr/HSA so the real compiler and runtime stay in the path."
date: 2026-09-17
tags:
  - SoftGPU
  - HIP
  - ROCm
  - HSA
  - AMD
  - GPU
  - ABI
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 2 of [SoftGPU](https://thanos.github.io/series/softgpu/). Part 1 asked for a virtual GPU that can explain a failure. This part picks the seam where that GPU enters the stack.

Applications talk HIP. Silicon speaks packets, memory fabrics, and firmware. If you intercept at the wrong layer you either invent a HIP of your own, or you take on a driver and a guest kernel before you have a diagnostic a developer can use.

SoftGPU starts at **ROCr/HSA userspace**, not by mocking HIP and not by emulating PCIe. That is [ADR-0001](https://github.com/thanos/softgpu/blob/main/docs/adr/0001-rocr-hsa-substitution-boundary.md).

## The layers

```text
HIP application
    → hipcc / AMD compiler
    → HIP runtime
        → ROCr / HSA userspace     ← SoftGPU libhsa_runtime64 substitutes here
            → amdgpu / ROCK
                → firmware / GPU
```

The launched process keeps the real AMD HIP compiler and runtime. It resolves a SoftGPU compatibility library in place of system ROCr. That library translates the supported runtime operations into SoftGPU’s core.

That gives us concrete things to model: agents, queues, dispatch packets, completion signals, compiled code objects. It also keeps runtime integration inside the problem we are testing. A successful kernel that never went through HIP’s idea of a device would answer a different question.

## What the first integration actually proves

The first useful HIP-linked test has a deliberately modest job: prove that the process loaded SoftGPU’s library. If it accidentally loaded `/opt/rocm/.../libhsa-runtime64`, a green test would tell us nothing about our implementation.

The probe prints SoftGPU’s mapped path via `dl_iterate_phdr` and **fails** if the system ROCr library is mapped. No kernel-execution claim rides on that result.

On the HSA surface, the early phases look like this:

| Piece | SoftGPU meaning |
| --- | --- |
| `hsa_init` / `hsa_shut_down` | Reference-counted session |
| `hsa_iterate_agents` / `hsa_agent_get_info` | One virtual GPU agent, with provenance |
| Other `hsa_*` / AMD extension entry points | Fail-closed generated C stubs |
| HIP-linked load proof | `environments/rocm-x86_64/run-phase1-load-proof.sh` on pinned ROCm **7.14.0** |

Layouts and enums are checked against vendored `hsa.h`. Panic containment on Rust exports is a policy, not a proof that every AMD extension HIP might `dlsym` is implemented. Those extra symbols stay stubs that fail closed.

## Reproducing it

```bash
cargo test --workspace --locked
cc -I third_party/rocr-headers -o target/hsa-layout-probe tools/hsa-layout-probe/probe.c
./target/hsa-layout-probe

# Linux x86_64 + pinned ROCm image (CI):
bash environments/rocm-x86_64/ci-entrypoint.sh
```

The canonical integration gate is Linux x86-64 and pinned ROCm, not macOS. That is a consequence of substituting ROCr, not a slight against laptops.

## What this part does not claim

Passing the load proof is not `hipInit` success. It is not full HIP runtime semantics. It is not “we are a GPU.” It is: the application reached us.

Next: [impersonating a GPU without lying](https://thanos.github.io/articles/2026-09-17-softgpu-03-impersonating-without-lying/).

The repo is [github.com/thanos/softgpu](https://github.com/thanos/softgpu). Canonical URL for this installment is on [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-02-hip-to-silicon/).
