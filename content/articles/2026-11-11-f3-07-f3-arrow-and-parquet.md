---
title: "F3, Apache Arrow, and Parquet"
description: "Three different jobs — not a speed contest."
date: 2026-11-11
tags:
  - F3
  - Arrow
  - Parquet
  - Elixir
  - columnar
draft: true
authors:
  - Thanos Vassilakis
series: f3
---

This is part 7 of [F3](https://thanos.github.io/series/f3/). Upstream pin `bd92506447dc1333820cfe9a34ebbf497fe0219e`.

This article compares jobs. It does not compare speeds. The recorded benchmark did not run a Parquet tool. See [part 9](https://thanos.github.io/articles/2026-11-11-f3-09-performance-and-what-remains-experimental/) for that run.

## Three jobs

Apache Arrow is an in-memory columnar representation. Engines pass arrays to each other without first agreeing on a file. The F3 footer stores an Arrow IPC schema so a reader can name fields and types. That schema is metadata. It is not an Arrow C Data Interface, and this library does not return Arrow arrays across the NIF. A decoded batch is an Elixir term.

Apache Parquet is a file format for exchanging columnar data. Readers in many languages already agree on it. A Parquet file does not carry a new decoder for an encoding the reader has never seen. That is the constraint the F3 paper is arguing with. This library does not read or write Parquet.

F3 is a research file format. The pinned writer puts Vortex-encoded values in the file, or a Wasm decoder when the writer was asked for one. A reader can refuse that decoder. This library does: `wasm: :off` is the default, and `:sandbox` is the only other accepted value.

```mermaid
flowchart LR
  arrow[Arrow in memory]
  parquet[Parquet file]
  f3[F3 file]
  arrow --- schema[Arrow IPC schema in the footer]
  f3 --- schema
  parquet --- interchange[Interchange without an embedded decoder]
  f3 --- decoder[Optional Wasm decoder]
```

## What this library actually opens

`small.f3` is three rows and an Arrow IPC schema in the footer. `F3.schema/1` returns that schema. `F3.read/2` returns columnar batches when the native decoder is compiled, and `:native_unavailable` when it is not. Neither call produces a Parquet file or an Arrow array.

From the [f3](https://github.com/thanos/f3) repository root:

```shell
mix run examples/tutorial_07.exs
```

The script prints the three jobs and the schema line for `small.f3`. It does not print a timing.

## What is experimental?

Upstream F3 at this pin is a research prototype. The footer schema is Arrow IPC. The payloads are not Parquet row groups and they are not Arrow arrays. Shared dictionaries are still `:unsupported_encoding`. Nothing here says F3 is faster or slower than Parquet.

## Next

**Previous:** [F3: Taking the Decoder with the Data](https://thanos.github.io/articles/2026-11-11-f3-06-taking-the-decoder-with-the-data/)

**Read next:** [F3: Building a Safe Binary-File Reader on the BEAM](https://thanos.github.io/articles/2026-11-11-f3-08-a-safe-reader-on-the-beam/)

## Sources

- Zeng, Meng, Prammer, McKinney, Patel, Pavlo, and Zhang, "F3: The Open-Source Data File Format for the Future", Proc. ACM Manag. Data 3, 4, Article 245 (2025). https://doi.org/10.1145/3749163
- Example: [`examples/tutorial_07.exs`](https://github.com/thanos/f3/blob/main/examples/tutorial_07.exs)
- Fixture: `test/fixtures/small.f3`
