---
title: "SoftGPU: Decoding an AMD GPU ISA Responsibly"
description: "ISA tables are easy to invent and hard to defend. SoftGPU’s gfx1201 subset is sourced from llvm-mc goldens, traps unknown encodings, and still does not claim a full GPU."
date: 2026-09-17
tags:
  - SoftGPU
  - AMDGPU
  - gfx1201
  - ISA
  - llvm-mc
  - GPU
  - Rust
draft: false
authors:
  - Thanos Vassilakis
series: softgpu
---

This is part 11 of [SoftGPU](https://thanos.github.io/series/softgpu/). ISA tables are easy to invent and hard to defend. SoftGPU must never claim “gfx1201 compatible” from blog posts, guessed bitfields, or restricted manuals copied into the tree. Encoding facts need provenance, a narrow subset, and fail-closed traps.

## The subset, named

| Piece | SoftGPU meaning |
| --- | --- |
| **Target** | `gfx1201` only |
| **Subset** | `softgpu-gfx1201-salu-v1`: `s_nop`, `s_endpgm`, `s_sleep`, `s_waitcnt`, `s_mov_b32`, `s_add_co_u32` |
| **Goldens** | Little-endian words observed with `llvm-mc -arch=amdgcn -mcpu=gfx1201 -show-encoding` |
| **Docs cross-check** | Public [LLVM AMDGPUUsage](https://llvm.org/docs/AMDGPUUsage.html) (layout vocabulary; goldens win for bytes) |
| **Fidelity** | **Architectural ISA** for the named subset only |
| **Trap** | Unknown encoding, opcode, or operand → error before SGPR/SCC corruption |

```text
LE instruction words
        ↓
fetch_word → decode_word (SOPP / SOP1 / SOP2 keys)
        ├── Inst (named subset) → step/run on MachineState
        └── TrapKind (unsupported) → IsaError (fail closed)
                ↓
        disasm_word  (matches golden asm strings)
```

Checked-in JSON under `crates/softgpu-amd-isa/goldens/` keeps CI independent of a local LLVM install. Tables are hand-maintained with provenance comments — not copied from restricted AMD ISA PDFs.

```bash
# Optional: requires LLVM AMDGPU llvm-mc
./tools/regen-isa-goldens.sh
cargo test -p softgpu-amd-isa --test phase10_isa --locked
```

## Machine state, explicit

SoftGPU models PC, an SGPR file, per-lane VGPR storage (unused in this subset), SCC, EXEC, VCC, halt, and SoftGPU `wave_size` (32 or 64 as a software parameter — not R9700 wavefront evidence). SALU ops in this subset update SGPRs and SCC only.

Honest treatments:

- `s_waitcnt` and `s_sleep` decode and execute as **no-ops** under SoftGPU’s sequential interpreter (no hardware memory pipeline, no sleep).
- Immediate scalar operands: SGPR `0..=105`, inline `0..=64` and `-1` only.

`s_add_co_u32` carry updates SoftGPU SCC. That is not a claim about every hardware SCC side effect.

## What this is not

Full gfx1201 ISA, VALU, and memory ops are out of scope here. Cycle accuracy and scoreboards are out of scope. Unknown words trap before they corrupt state.

```bash
cargo test -p softgpu-amd-isa --locked
cargo run --locked -- decode-isa 0xbe800081 0xbfb00000
cargo run --locked -- run-isa --words 0xbe800081,0xbe810082,0x80020100,0xbfb00000
```

Next: [the first real gfx1201 kernel in SoftGPU](https://thanos.github.io/articles/2026-09-17-softgpu-12-first-gfx1201-kernel/).

Canonical: [thanos.github.io](https://thanos.github.io/articles/2026-09-17-softgpu-11-decoding-amdgpu-isa/).
