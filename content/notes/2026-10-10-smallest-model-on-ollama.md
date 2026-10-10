---
title: "The smallest models you can download in Ollama"
description: "SmolLM and SmolLM2 at 135M, functiongemma at 270M, and TinyLlama at 1.1B — the smallest model families available in Ollama, with download size and what each is good for."
date: 2026-10-10
tags:
  - Ollama
  - SmolLM
  - TinyLlama
  - LLMs
draft: false
authors:
  - Thanos Vassilakis
---

The smallest model family you can download in Ollama is SmolLM and SmolLM2 (with a 135M parameter size) or TinyLlama (at 1.1B parameters / ~638MB download size), alongside function-calling models like functiongemma (270M parameters). [1](https://ollama.com/search?q=small), [2](https://ollama.com/library/tinyllama), [3](https://ollama.com/library/smollm), [4](https://ollama.com/library/smollm2)

## Smallest Options Available in Ollama

### SmolLM2 / SmolLM (135M)

- Size: Around 135 million parameters (download size is roughly ~90MB to ~150MB depending on the quantization).
- Command to run: `ollama run smollm2` (or `smollm`)
- Best for: Lightweight testing, rapid experimentation, and learning. [1](https://machinelearningmastery.com/top-7-small-language-models-you-can-run-on-a-laptop/), [2](https://ollama.com/library/smollm), [3](https://ollama.com/library/smollm2)

### functiongemma (270M)

- Size: 270 million parameters.
- Command to run: `ollama run functiongemma`
- Best for: Function-calling tasks. [1](https://ollama.com/search?q=small)

### TinyLlama (1.1B)

- Size: 1.1 billion parameters (download size is about 638MB).
- Command to run: `ollama run tinyllama`
- Best for: Basic text generation on a strict memory budget. [1](https://ollama.com/library/tinyllama)

## Comparison of Smallest Ollama Models

| Model Name | Parameter Size | Approximate Download Size | Primary Use Case |
|---|---|---|---|
| SmolLM2 | 135M | ~90MB – 150MB | Prototyping & basic experiments |
| functiongemma | 270M | < 300MB | Function and tool calling |
| TinyLlama | 1.1B | 638MB | General lightweight text |

If you are trying to run a model within a specific RAM limit or looking for a model capable of a specific task (like coding or summarization), let me know and I can recommend the best fit! [1](https://needtoknowit.com.au/blog/best-ollama-models-to-download/)
