---
title: "SoftGPU: Debugging a Machine Made of Lanes"
description: "A sanitizer finding is only useful if another engineer can reproduce it, stop at the responsible step, and inspect wave and lane state."
date: 2026-09-17
tags:
  - SoftGPU
  - debugger
  - sanitizer
  - GPU
  - trace
  - replay
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 10 of [SoftGPU](https://thanos.github.io/series/softgpu/). A sanitizer finding is only useful if another engineer can reproduce it, stop at the responsible SoftGPU step, and inspect wave and lane state — without SoftGPU inventing source locations it does not have.

## The debugger model

```text
SFIR program + ExecConfig(+schedule_seed)
        ↓
interpreter + ExecObserver (DebugSession)
        ├── TraceLog (JSONL)
        └── DebugStop / SanitizeFinding
                ↓
        inspect / explore_and_minimize_race
```

| Concept | SoftGPU meaning |
| --- | --- |
| **Trace** | Versioned JSONL `softgpu-debug-trace-v1` with a hard event budget |
| **Breakpoint** | `after_step` (SoftGPU global step) or `on_memory_access` |
| **Snapshot** | Actor id, registers, op label, program `source_provenance` only |
| **Schedule seed** | `schedule_seed` bit0 reverses SoftGPU wave order under `wave_barrier` |
| **Explore** | Bounded seeded search for SoftGPU race / missing-barrier findings, then minimize workgroup and step |

`parse_trace_jsonl` treats input as untrusted: size limits, per-line limits, schema check, parse failures. Junk must not panic the debugger.

## Source mapping policy

SoftGPU **never invents** file/line mappings. `StateSnapshot.source_mapping` is always `None` unless a future phase verifies a real SFIR→source map. The only source string is `Program.source_provenance`.

That is the same honesty rule as empty numeric limits on a device profile. A fabricated line number is worse than no line number.

## What is verified

Breakpoint accuracy, snapshots, and JSONL replay are covered by tests. Corrupt or oversized traces fail closed. Seeded explore finds and minimizes a SoftGPU race.

Out of scope: an interactive TUI, hardware schedule fidelity, AMDGPU memory-order debugging.

```bash
cargo test -p softgpu-functional --test phase9_debug --locked
cargo run --locked -- debug-functional --builtin tiny_add --break-step 5
```

The functional machine can now explain a declared class of defects. The next question is whether SoftGPU can decode real gfx1201 bytes without inventing an ISA manual.

Next: [decoding an AMD GPU ISA responsibly](https://thanos.github.io/articles/2026-09-17-softgpu-11-decoding-amdgpu-isa/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-10-debugging-lanes/).
