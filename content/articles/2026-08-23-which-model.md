---
title: "Which Model Would You Choose for Apple Silicon?"
description: "If you are building an inference engine for Apple’s M-series, start small and conventional. Qwen3-8B in 4-bit is the optimization target; Llama is the bootstrap."
date: 2026-08-23
tags:
  - Apple Silicon
  - MLX
  - Qwen
  - Llama
  - LLM
  - Metal
  - Zig
  - quantization
  - MoE
draft: false
authors:
  - Thanos Vassilakis
---

I was recently asked: which OS model would you choose for Apple’s M-series architecture?

Assuming “OS model” means an open-weight LLM, the best one to run and optimize on Apple Silicon is **Qwen3-8B in 4-bit quantization**. That is the model I chose for my Zig engine, `zynfer`.

Why it fits Apple Silicon well:

- Approximately 5–6 GB of quantized weights, leaving room for the KV cache and workspace on a 16 GB Mac.
- A dense transformer that cleanly exercises RMSNorm, RoPE, GQA, SwiGLU, KV caching, prefill, and decode.
- Decode is strongly memory-bandwidth-bound, which makes it a useful target for Apple’s unified memory.
- Mature MLX implementations exist, so you have a reference for correctness and performance. MLX officially supports Qwen3 on Apple Silicon: [MLX-LM](https://github.com/ml-explore/mlx-lm), [supported models](https://github.com/ml-explore/mlx-swift-lm/blob/main/skills/mlx-swift-lm/references/supported-models.md).

The development sequence I used:

| Apple memory | Development model | Purpose |
|---:|---|---|
| 8–16 GB | **Qwen3-0.6B / 1.7B** | Kernel correctness and rapid debugging |
| 16–24 GB | **Qwen3-8B 4-bit** | Primary optimization target |
| 32–48 GB | **Qwen3-14B 4-bit** | More demanding production test |
| 64 GB+ | **Qwen3-30B-A3B 4-bit** | MoE and large-memory experimentation |
| 96–192 GB | 32B–70B-class 4-bit models | Max/Ultra bandwidth and capacity testing |

For `zynfer` specifically:

1. **Qwen3-0.6B** as the correctness bootstrap.
2. **Qwen3-8B 4-bit** as the main Apple optimization target.
3. **Qwen3-30B-A3B 4-bit** later, to see whether MoE’s smaller active-parameter set improves generation efficiency.

I did not begin with Qwen3.5 or another hybrid attention/SSM architecture. Those models add recurrent-state and cache complexity before the backend boundary, Metal kernels, and a standard KV cache are proven. Current MLX reports also show prefix-cache complications for hybrid architectures. I started with a conventional dense Qwen3 transformer, and I will add hybrid models deliberately later.

Apple’s MLX notes that large-model memory wiring requires macOS 15 or later. See [MLX-LM large-model guidance](https://github.com/ml-explore/mlx-lm).

Qwen is a strong choice. It is not uniquely suited to Apple Silicon. MLX also supports Llama, Mistral, Gemma, Phi, DeepSeek-derived models, GPT-OSS, and many others. [MLX supported-model list](https://github.com/ml-explore/mlx-swift-lm/blob/main/skills/mlx-swift-lm/references/supported-models.md).

For a Zig/Metal engine, I ranked the families like this:

| Family | Apple Silicon fit | Implementation difficulty | Best role |
|---|---|---|---|
| **Llama 3.x** | Excellent | Low | First architecture / reference |
| **Qwen3** | Excellent | Low–medium | Primary quality/performance target |
| **Mistral** | Excellent | Low–medium | Sliding-window and long-context testing |
| **Gemma 3** | Very good | Medium | Multimodal and memory-efficient testing |
| **Phi** | Very good | Low–medium | Small Macs and fast development |
| **DeepSeek-R1 Distill** | Excellent | Same as its base model | Reasoning-quality workload |
| **GPT-OSS 20B** | Promising | High | MoE and quantized-kernel target |
| **Mixtral / Qwen MoE** | Good with enough RAM | High | Sparse-MoE optimization research |
| **Hybrid SSM models** | Potentially excellent | Very high | Later research target |

## Llama: best first implementation

**Llama 3.1 8B or Llama 3.2 3B** is probably the cleanest family for establishing the engine.

Advantages:

- Conventional decoder-only transformer.
- RMSNorm, RoPE, GQA, SwiGLU, and ordinary KV caching.
- Enormous ecosystem and many reference implementations.
- Straightforward weight conversion and intermediate-output comparison.
- MLX uses Llama 3.2 3B 4-bit as its default chat model. [MLX-LM](https://github.com/ml-explore/mlx-lm)

Disadvantages:

- Meta’s custom license is less permissive than Apache 2.0.
- The available small Llama releases are no longer necessarily the strongest models at their sizes.
- Fewer unusual architectural features for later research.

**Verdict:** best architectural bootstrap, even if Qwen becomes the main performance target.

## Qwen: best overall project target

Qwen3 remained the preferred balance:

- Strong small and medium models.
- Dense and MoE variants within one family.
- Apache 2.0 releases.
- GQA and standard transformer operations map naturally onto the backend.
- A clean progression from a tiny correctness model to a serious MoE experiment.
- Strong coding, reasoning, and multilingual capability.

The progression:

```text
Qwen3-0.6B
    ↓ correctness
Qwen3-4B or 8B
    ↓ dense Metal optimization
Qwen3-30B-A3B
    ↓ sparse MoE implementation
```

**Verdict:** the best primary family once the backend works.

## Mistral: an excellent second dense architecture

Mistral 7B is attractive because it is close enough to Llama to reuse most kernels, while adding meaningful scheduling and cache differences.

Advantages:

- Compact, well-understood architecture.
- Strong reference support.
- A useful sliding-window-attention test.
- MLX directly supports Mistral 7B 4-bit. [MLX server example](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/SERVER.md)

Disadvantages:

- Older Mistral 7B models are no longer leading their size class.
- Sliding-window attention complicates cache semantics without exercising entirely new compute kernels.

**Verdict:** an excellent test that the backend/model separation is real. If adding Mistral requires Metal-backend changes, the boundary is probably leaking model semantics.

## Gemma 3: particularly interesting for Apple

Gemma 3 is a compelling Apple target because it provides 1B, 4B, 12B, and 27B sizes, multimodality, and long-context support. The 4B, 12B, and 27B variants advertise 128K input context. [Gemma 3 model card](https://huggingface.co/google/gemma-3-12b-it)

Advantages:

- Good quality per parameter.
- Convenient range of model sizes.
- Quantization-aware releases can behave well at 4-bit.
- Vision support creates a path toward a multimodal Apple backend.
- A 12B 4-bit model is a good 16–24 GB Mac target.

Disadvantages:

- Local/sliding attention patterns complicate KV-cache handling.
- Multimodality introduces a vision encoder, preprocessing, and additional graph shapes.
- Google’s Gemma terms are not as simple as Apache 2.0.
- Less suitable than Llama or Qwen as the very first model.

**Verdict:** the best second-stage model if multimodal inference matters.

## Phi: best for limited-memory Macs

Phi-3.5 Mini and related small models are useful on base M-series machines.

Advantages:

- Small enough for rapid compile-test-debug cycles.
- Leaves substantial memory for debugging buffers and intermediate captures.
- Good for testing whether GPU dispatch overhead overwhelms useful work.
- A useful benchmark for deciding when Accelerate CPU execution beats Metal.

Disadvantages:

- Less representative of large-model memory-bandwidth behavior.
- Optimizations that win on a small Phi model may not transfer to 8B–30B workloads.

**Verdict:** a valuable development fixture, not the final optimization target.

## DeepSeek-R1 Distill: a workload, not a new backend

Models such as DeepSeek-R1-Distill-Qwen-7B use the Qwen architecture. Supporting the corresponding Qwen base generally gives you the distilled model automatically.

That is useful because you can test:

- Longer reasoning generations.
- KV-cache growth.
- Sustained thermal behavior.
- Long-run token latency.
- Sampling and chat-template correctness.

**Verdict:** include it as a workload after Qwen support. Do not treat it as a separate kernel architecture.

## GPT-OSS 20B: a fascinating Apple/MoE target

GPT-OSS 20B is a 21B-parameter mixture-of-experts model with approximately 3.6B active parameters per token, distributed under Apache 2.0. [Official GPT-OSS 20B model card](https://huggingface.co/openai/gpt-oss-20b)

Why it is interesting:

- MoE reduces arithmetic per token relative to total parameter count.
- Its original distribution uses MXFP4, which is a serious quantized-kernel target.
- It exercises expert routing, top-k selection, grouped expert execution, and sparse weight access.
- MLX has a native GPT-OSS implementation.

The Apple-specific catch matters: **inactive weights still occupy unified memory, and sparse expert access can produce irregular bandwidth behavior**. Low active parameters do not automatically mean low memory traffic. Efficient expert batching and fused dequantized matvec kernels become essential.

**Verdict:** probably the most intellectually interesting model after the dense backend is fast — and a poor first implementation.

## The model roadmap

```text
1. Llama 3.2 1B/3B
   Establish the simplest conventional architecture

2. Qwen3-0.6B
   Cross-family correctness and weight-loader validation

3. Qwen3-8B 4-bit
   Primary Metal, UMA, decode, and quantization target

4. Mistral 7B
   Validate sliding-window KV-cache behavior

5. Gemma 3 4B or 12B
   Add local attention and eventually vision

6. Qwen3-30B-A3B or GPT-OSS 20B
   Implement MoE routing and expert kernels
```

If I had to choose only one family, I would still choose **Qwen**. The engineering sequence can start with **Llama**, make **Qwen3-8B** the main performance target, and reserve **GPT-OSS 20B** for the advanced Apple-specific MoE work.
