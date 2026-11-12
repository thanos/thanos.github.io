---
title: "F3: Performance, Compatibility, and What Remains Experimental"
description: "Numbers only from a recorded run — and an honest list of what is still off."
date: 2026-11-11
tags:
  - F3
  - Elixir
  - benchmarks
  - experimental
draft: true
authors:
  - Thanos Vassilakis
series: f3
---

This is part 9 of [F3](https://thanos.github.io/series/f3/). Upstream pin `bd92506447dc1333820cfe9a34ebbf497fe0219e`.

The numbers in this article are the output of one command on one machine. They are not a comparison with Parquet, and they are not decode times. The native stamp was `0`, so `F3.read/2` returned before decoding a payload.

## The recorded run

Command, from the [f3](https://github.com/thanos/f3) repository root, on Darwin arm64 with Elixir 1.20.2 and OTP 28:

```shell
/usr/bin/time -l mix run scripts/bench.exs
```

`/usr/bin/time -l` exited 0. It printed `maximum resident set size` 109854720 and `peak memory footprint` 97747616. The script also printed `ps_rss_kb: 107136` from `ps`. That figure is the resident set `ps` reported, not the `time` peak.

```text
command: mix run scripts/bench.exs
elixir: 1.20.2
otp: 28
native_stamp: 0
---
fixture: test/fixtures/compressed_lz4.f3
bytes: 1391
read_us: 10889
read: error category=native_unavailable
stream_us: 106
stream: error category=native_unavailable
---
fixture: test/fixtures/compressed_zstd.f3
bytes: 1216
read_us: 229
read: error category=native_unavailable
stream_us: 27
stream: error category=native_unavailable
---
fixture: test/fixtures/custom_wasm.f3
bytes: 10663647
read_us: 1072
read: error category=unsupported_encoding
stream_us: 96
stream: error category=unsupported_encoding
---
fixture: test/fixtures/dictionary.f3
bytes: 4912
read_us: 270
read: error category=native_unavailable
stream_us: 58
stream: error category=native_unavailable
---
fixture: test/fixtures/multi_row_group.f3
bytes: 3072
read_us: 263
read: error category=native_unavailable
stream_us: 29
stream: error category=native_unavailable
---
fixture: test/fixtures/nested.f3
bytes: 7200
read_us: 220
read: error category=native_unavailable
stream_us: 48
stream: error category=native_unavailable
---
fixture: test/fixtures/nullable.f3
bytes: 5064
read_us: 91
read: error category=native_unavailable
stream_us: 39
stream: error category=native_unavailable
---
fixture: test/fixtures/small.f3
bytes: 4168
read_us: 81
read: error category=native_unavailable
stream_us: 49
stream: error category=native_unavailable
---
fixture: test/fixtures/wide.f3
bytes: 30640
read_us: 298
read: error category=native_unavailable
stream_us: 128
stream: error category=native_unavailable
---
ps_rss_kb: 107136
---
parquet comparison: skipped
---
batch_size: default
projection: all columns
```

`custom_wasm.f3` is `:unsupported_encoding` because the default read does not execute Wasm. The other eight fixtures are `:native_unavailable` because the decoder was not compiled. `parquet-cli` and a `pyarrow` binary were not on `PATH`, so the comparison was skipped. The script did not download a dataset.

`batch_size` stayed 8192. Projection stayed every column. A chunk is still one `pread/3`. This run does not name a defect in those defaults, so they were not changed.

[`examples/tutorial_09.exs`](https://github.com/thanos/f3/blob/main/examples/tutorial_09.exs) prints this recorded result. It does not time the fixtures again.

## What remains experimental

Version `0.1.0` has not been published to Hex. Precompiled NIFs are not part of the package. A source build needs `nightly-2025-11-15` for the NIF and `nightly-2025-02-24` plus a fetch of pinned `fff-poc` for the writer.

Still off, or only present when the caller opts in:

- Wasm, unless `wasm: :sandbox`
- shared dictionaries
- signed int8 and int16, float16, binary, decimal, dates, timestamps, and map
- remote writes
- fetches of `lib_urls`

The MinIO tag was not run for the stage 5 report. Linux arm64 and upstream's Intel Debian 12 claim were not run from this machine.

## What is experimental?

Upstream F3 at this pin is a research prototype. These timings are the cost of refusing a read on small fixtures. They are not a throughput number for Vortex or Wasm.

## Next

**Previous:** [F3: Building a Safe Binary-File Reader on the BEAM](https://thanos.github.io/articles/2026-11-11-f3-08-a-safe-reader-on-the-beam/)

**Start of series:** [F3: Why Another File Format?](https://thanos.github.io/articles/2026-11-11-f3-01-why-f3/)

## Sources

- [`scripts/bench.exs`](https://github.com/thanos/f3/blob/main/scripts/bench.exs)
- [`docs/test-reports/stage-5.md`](https://github.com/thanos/f3/blob/main/docs/test-reports/stage-5.md)
- Example: [`examples/tutorial_09.exs`](https://github.com/thanos/f3/blob/main/examples/tutorial_09.exs)
