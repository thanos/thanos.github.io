---
title: "SoftGPU"
description: "A developer-oriented virtual GPU: keep the real HIP compiler, substitute ROCr/HSA, and never let a green test mean more than the evidence you have."
date: 2026-09-17
tags:
  - SoftGPU
  - Rust
  - HIP
  - AMD
  - ROCm
  - HSA
  - GPU
  - virtual GPU
  - sanitizer
  - emulator
draft: false
authors:
  - Thanos Vassilakis
---

[SoftGPU](https://github.com/thanos/softgpu) is a software GPU runtime for developers. The first integration target is AMD HIP. The host implementation is Rust. The point is not to replace an R9700. The point is to inspect execution, test assumptions, and eventually catch memory and synchronization mistakes with diagnostics another engineer can reproduce.

The series starts from a flaky kernel: it passes until you change the input size; logging makes the bug vanish; a driver change brings it back differently. Hardware remains essential for performance and agreement. Vendor sanitizers already exist. SoftGPU is for control over the execution environment — and for being honest about what a passing test has actually shown.

The integration boundary is [ADR-0001](https://github.com/thanos/softgpu/blob/main/docs/adr/0001-rocr-hsa-substitution-boundary.md): keep the official AMD compiler and HIP runtime; substitute at ROCr/HSA userspace. SoftGPU does not mock HIP as its compatibility path, and it does not start by emulating PCIe or firmware.

As of the repository’s 16 September 2026 snapshot ([status](https://github.com/thanos/softgpu/blob/main/docs/status.md), v0.8.0), SoftGPU can load as an HSA library, observe queues and AQL packets, inspect AMDGPU code-object metadata, run a disclosed functional IR, sanitize and debug that IR, and execute a **named** gfx1201 subset for a tiny registered kernel. Arbitrary hipcc binaries and hardware differential are **not** claimed.

<!-- Each installment is written to stand alone for Medium and Substack. The canonical URLs live on this site. When you cross-post, import the article body, keep the absolute links, and set the canonical URL to the matching `https://thanos.github.io/articles/…/` page so search engines and LLMs keep one identity.

On Medium: *Import a story* from the canonical URL, or paste the markdown and add that URL under *Canonical link* in story settings. On Substack: paste the body into a post and put the canonical URL in SEO / canonical settings if your plan exposes it; otherwise lead with a link to the site copy. -->

The [status document](https://github.com/thanos/softgpu/blob/main/docs/status.md) is the evidence ledger. If an article and the status file disagree, trust the status file.
