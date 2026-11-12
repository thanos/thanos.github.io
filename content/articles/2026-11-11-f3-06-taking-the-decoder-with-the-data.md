---
title: "F3: Taking the Decoder with the Data"
description: "Wasm, trust, and what stays off unless you pass wasm: :sandbox."
date: 2026-11-11
tags:
  - F3
  - Elixir
  - WebAssembly
  - Wasmtime
  - security
draft: false
authors:
  - Thanos Vassilakis
series: f3
---

This is part 6 of [F3](https://thanos.github.io/series/f3/). Upstream pin `bd92506447dc1333820cfe9a34ebbf497fe0219e`.

F3 can store a decoder next to the bytes it decodes. The pinned writer does that for `custom_wasm.f3` by embedding `fff-ude-example-fff`, compiled for `wasm32-wasip1`. The encoding label on those units is `CUSTOM_WASM`. The Wasm ABI symbol is `FFFUDE_VERSION_1_0`. This library accepts major 1 only.

An Elixir extension is not an F3 file field. `F3.Registry` is process-local policy. Two reads share it only when both are given the same pid.

```mermaid
flowchart TD
  read[F3.read]
  cascade{CASCADE 0.21.0}
  ext{Registered extension}
  opt{wasm: :sandbox}
  host[Wasmtime 28 on a dirty scheduler]
  refuse[unsupported_encoding]
  read --> cascade
  cascade -->|yes| native[Vortex NIF]
  cascade -->|no| ext
  ext -->|yes| elixir[F3.Extension]
  ext -->|no| opt
  opt -->|yes| host
  opt -->|no| refuse
```

[`examples/tutorial_06.exs`](https://github.com/thanos/f3/blob/main/examples/tutorial_06.exs) opens `test/fixtures/custom_wasm.f3`. The default read does not execute the module:

```text
command: mix run examples/tutorial_06.exs
wasm: off
extension rows:
[%{"trade_id" => 1}, %{"trade_id" => 2}, %{"trade_id" => 3}]
wasm: sandbox needs the native decoder
```

That block is `mix run examples/tutorial_06.exs` without `F3_BUILD_NATIVE`. The extension returns the manifest rows. It does not prove the embedded module. With the native decoder compiled, the same script's sandbox branch prints:

```text
sandbox rows:
[%{"trade_id" => 1}, %{"trade_id" => 2}, %{"trade_id" => 3}]
```

That second list is `F3_BUILD_NATIVE=1 mix run examples/tutorial_06.exs` on this machine. The fuel budget is 5_000_000 instructions. Upstream sets no fuel. Linear memory is capped at 8 MiB. `lib_urls` are not fetched.

## What is experimental?

Upstream F3 at this pin is a research prototype. Wasm stays off unless the caller passes `wasm: :sandbox`. Majors 2 and 3 of the ABI are not accepted. Nested Wasm output is not implemented upstream and is not claimed here. `small.f3` remains a Vortex file. Nothing here is a production sandbox.

## Next

**Previous:** [F3: Writing F3 from Elixir](https://thanos.github.io/articles/2026-11-11-f3-05-writing-f3-from-elixir/)

**Read next:** [F3, Apache Arrow, and Parquet](https://thanos.github.io/articles/2026-11-11-f3-07-f3-arrow-and-parquet/)

## Sources

- Pinned `fff-ude/src/ffi.rs`, `fff-ude-wasm/src/lib.rs`, and `fff-poc/src/decoder/encunit.rs`
- `test/fixtures/custom_wasm.f3` and [`test/fixtures/manifest.json`](https://github.com/thanos/f3/blob/main/test/fixtures/manifest.json)
- [`docs/upstream-compatibility.md`](https://github.com/thanos/f3/blob/main/docs/upstream-compatibility.md) and [`docs/security.md`](https://github.com/thanos/f3/blob/main/docs/security.md)
- Example: [`examples/tutorial_06.exs`](https://github.com/thanos/f3/blob/main/examples/tutorial_06.exs)
