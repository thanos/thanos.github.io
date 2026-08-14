---
title: "Sketching One Billion Temperature Rows in Elixir"
description: "Exact aggregates where they fit; probabilistic sketches where a billion values do not. Stream 1BRC-shaped weather data with ex_data_sketch—KLL, HLL, and FrequentItems—without loading a 12 GB file."
date: 2026-08-10
tags:
  - Elixir
  - ex_data_sketch
  - probabilistic data structures
  - HyperLogLog
  - KLL
  - FrequentItems
  - streaming
  - 1BRC
  - data sketches

draft: false
---

*Exact aggregates where they fit; probabilistic sketches where a billion values do not.*

One billion weather readings will not fit comfortably in an ordinary Elixir process heap as a list of floats. Most analytical questions do not need that list anyway. They need answers: how many stations, what are the extremes, where is the median, who dominates the stream?

This article walks through that problem using the public [One Billion Row Challenge](https://github.com/gunnarmorling/1brc) data shape and [`ex_data_sketch`](https://hex.pm/packages/ex_data_sketch) `~> 0.9`. You will stream delimited lines, keep exact per-station min/mean/max, and layer mergeable sketches for quantiles, distinct counts, and heavy hitters. The tutorial works with a tiny deterministic fixture. The full generated 1BRC file is roughly 12 GB; you do not need it to learn the ideas.

Central idea:

> Keep the smallest mergeable state that can answer the question accurately enough.

All code below is Elixir. Measurements shown for the fixture were executed against `ex_data_sketch` 0.10.0 (compatible with `~> 0.9`). Treat timings on your machine as observations, not universal benchmarks.

---

## The data shape

Each UTF-8 record is one line:

```text
station_name;temperature
```

Temperatures use one fractional digit. Examples:

```text
Hamburg;12.3
St. John's;-5.5
北京;15.2
```

The [1BRC repository](https://github.com/gunnarmorling/1brc) defines the challenge and generator. Here we care about the input format and the analytical questions it suggests, not about leaderboard micro-optimizations.

Companion runnable notebook: [`sketching_one_billion_rows.livemd`](https://github.com/thanos/ex_data_sketch/blob/main/baoulo/articles/sketching_one_billion_rows.livemd) in the `ex_data_sketch` repo.

---

## Stream the file; do not list the file

`File.stream!/3` yields lines lazily. Parse each record into a station name and an **integer temperature in tenths of a degree**. `"Hamburg;12.3"` becomes `{"Hamburg", 123}`. Integer tenths avoid float noise when summing and comparing.

```elixir
defmodule WeatherParser do
  @moduledoc false

  @spec parse_line(binary()) :: {:ok, {String.t(), integer()}} | {:error, term()}
  def parse_line(line) when is_binary(line) do
    line =
      line
      |> String.trim_trailing("\n")
      |> String.trim_trailing("\r")

    case String.split(line, ";", parts: 2) do
      [station, temp] when station != "" ->
        case Float.parse(temp) do
          {value, ""} ->
            {:ok, {station, round(value * 10)}}

          _ ->
            {:error, {:malformed_temperature, line}}
        end

      _ ->
        {:error, {:malformed_record, line}}
    end
  end

  @spec format_tenths(integer()) :: String.t()
  def format_tenths(tenths) when is_integer(tenths) do
    sign = if tenths < 0, do: "-", else: ""
    abs_t = abs(tenths)
    "#{sign}#{div(abs_t, 10)}.#{rem(abs_t, 10)}"
  end

  @spec stream_path(Path.t()) :: Enumerable.t()
  def stream_path(path) do
    path
    |> File.stream!([], :line)
    |> Stream.map(&parse_line/1)
  end
end
```

The parser:

- preserves UTF-8 station names;
- splits only on the first `;` so names stay intact;
- accepts negatives;
- returns clear errors for bad lines;
- never converts the whole stream into a list.

A small fixture is enough for the rest of the article:

```elixir
@fixture """
Hamburg;12.3
Bulawayo;8.9
Palembang;38.8
St. John's;-5.5
Cracow;12.6
Hamburg;12.1
Bulawayo;9.0
Palembang;38.7
Zürich;10.0
北京;15.2
"""
```

That is ten rows and seven distinct stations.

---

## Exact baseline first

Per-station **count**, **sum** (tenths), **minimum**, and **maximum** need constant memory per station. With hundreds of stations that is tiny. Do not sketch what an exact accumulator already answers perfectly.

```elixir
defmodule ExactStation do
  defstruct count: 0, sum: 0, min: nil, max: nil

  def new, do: %__MODULE__{}

  def update(%__MODULE__{count: 0}, {_station, temp}) do
    %__MODULE__{count: 1, sum: temp, min: temp, max: temp}
  end

  def update(%__MODULE__{} = s, {_station, temp}) do
    %{s | count: s.count + 1, sum: s.sum + temp, min: min(s.min, temp), max: max(s.max, temp)}
  end

  def merge(%__MODULE__{count: 0}, right), do: right
  def merge(left, %__MODULE__{count: 0}), do: left

  def merge(%__MODULE__{} = left, %__MODULE__{} = right) do
    %__MODULE__{
      count: left.count + right.count,
      sum: left.sum + right.sum,
      min: min(left.min, right.min),
      max: max(left.max, right.max)
    }
  end

  def mean(%__MODULE__{count: 0}), do: nil
  def mean(%__MODULE__{count: c, sum: sum}), do: sum / c
end
```

Derive mean only when presenting results. Exact min and max stay exact forever for this state; a quantile sketch should not replace them.

---

## Quantiles with KLL

A **quantile** answers “what value sits at a given rank?” The median is rank `0.50`. The 90th percentile is rank `0.90`.

Exact quantiles need sorted observations (or an equivalent order statistic). For streaming volumes that is expensive. [KLL](https://ex-data-sketch.hexdocs.pm/ExDataSketch.KLL.html) (`ExDataSketch.KLL`) keeps compact levels of samples and approximates ranks. Parameter `k` trades memory for rank accuracy (roughly `1.65 / k` rank error in the library docs).

Feed KLL **degrees as floats** (tenths / 10.0). Keep integer tenths in the exact accumulator.

```elixir
alias ExDataSketch.KLL

temps_c = Enum.map(rows, fn {_s, tenths} -> tenths / 10.0 end)

kll =
  Enum.reduce(temps_c, KLL.new(k: 50), fn t, sketch ->
    KLL.update(sketch, t)
  end)

[median, p90, p99] = KLL.quantiles(kll, [0.50, 0.90, 0.99])
```

On the ten-row fixture, nearest-rank exact values and KLL estimates were:

| Rank | Exact (°C) | KLL (°C) |
|------|------------|----------|
| 0.50 | 12.1       | 12.3     |
| 0.90 | 38.7       | 38.8     |
| 0.99 | 38.8       | 38.8     |

That closeness on ten points is illustrative, not a guarantee on arbitrary data. Empty sketches return `nil` from `quantile/2`. Compatible KLL sketches (same `k`) merge with `KLL.merge/2` or `KLL.merge_many/1`.

Why keep exact min/max separately? Extremes matter operationally, and the exact accumulator already stores them with no approximation story to explain.

---

## Distinct stations with HLL

[HyperLogLog](https://ex-data-sketch.hexdocs.pm/ExDataSketch.HLL.html) (`ExDataSketch.HLL`) estimates cardinality. Precision `p` sets `m = 2^p` registers. Relative standard error is about `1.04 / sqrt(m)`.

```elixir
alias ExDataSketch.HLL

hll =
  Enum.reduce(rows, HLL.new(p: 10), fn {station, _}, sketch ->
    HLL.update(sketch, station)
  end)

estimate = HLL.estimate(hll)
exact = rows |> Enum.map(&elem(&1, 0)) |> MapSet.new() |> MapSet.size()
```

Fixture results (executed):

| Metric | Value |
|--------|-------|
| Exact distinct | 7 |
| HLL estimate (`p: 10`) | ≈ 7.02 |
| Absolute error | ≈ 0.02 |
| Relative error | ≈ 0.3% |
| `size_bytes/1` | 1028 |
| `serialize/1` byte size | 1068 |

The standard 1BRC generator uses a modest station set, so exact `MapSet` counting is practical there. Use HLL when production identifiers explode: devices, sensors, users, request keys.

---

## Heavy hitters with FrequentItems

[FrequentItems](https://ex-data-sketch.hexdocs.pm/ExDataSketch.FrequentItems.html) implements SpaceSaving. Capacity `k` is the maximum number of tracked counters. Low-frequency items can be **evicted**; remaining estimates may overcount but include an error bound.

Create a skewed stream on purpose:

```elixir
alias ExDataSketch.FrequentItems

skewed =
  List.duplicate("Hamburg", 50) ++
    List.duplicate("Bulawayo", 20) ++
    List.duplicate("Cracow", 5) ++
    Enum.map(1..15, &"Rare#{&1}")

fi =
  FrequentItems.new(k: 5)
  |> FrequentItems.update_many(skewed)

FrequentItems.top_k(fi)
# Hamburg ~50, Bulawayo ~20, then approximate rare survivors
```

With `k: 5`, Cracow (exact count 5) can disappear while inflated rare keys remain. That is the teaching moment: approximate heavy-hitter detection is not exact frequency accounting.

When you already know the keys and need point queries (“how often did sensor X appear?”), prefer [`ExDataSketch.CMS`](https://ex-data-sketch.hexdocs.pm/ExDataSketch.CMS.html) (Count-Min Sketch). FrequentItems answers “who is hot?”; CMS answers “how hot is this specific item?”

---

## One composable summary

Bundle exact maps and sketches into a single mergeable summary:

```elixir
defmodule WeatherSketch do
  alias ExDataSketch.{FrequentItems, HLL, KLL}

  defstruct stations: %{}, kll: nil, hll: nil, frequent: nil, opts: []

  def new(opts \\ []) do
    kll_k = Keyword.get(opts, :kll_k, 50)
    hll_p = Keyword.get(opts, :hll_p, 10)
    fi_k = Keyword.get(opts, :frequent_k, 8)

    %__MODULE__{
      stations: %{},
      kll: KLL.new(k: kll_k),
      hll: HLL.new(p: hll_p),
      frequent: FrequentItems.new(k: fi_k),
      opts: [kll_k: kll_k, hll_p: hll_p, frequent_k: fi_k]
    }
  end

  def update(%__MODULE__{} = summary, {station, tenths} = row) do
    stations =
      Map.update(summary.stations, station, ExactStation.update(ExactStation.new(), row), fn s ->
        ExactStation.update(s, row)
      end)

    %{
      summary
      | stations: stations,
        kll: KLL.update(summary.kll, tenths / 10.0),
        hll: HLL.update(summary.hll, station),
        frequent: FrequentItems.update(summary.frequent, station)
    }
  end

  def merge(%__MODULE__{opts: opts} = left, %__MODULE__{opts: opts} = right) do
    stations =
      Map.merge(left.stations, right.stations, fn _k, a, b -> ExactStation.merge(a, b) end)

    %{
      left
      | stations: stations,
        kll: KLL.merge(left.kll, right.kll),
        hll: HLL.merge(left.hll, right.hll),
        frequent: FrequentItems.merge(left.frequent, right.frequent)
    }
  end

  def merge(%__MODULE__{}, %__MODULE__{}) do
    raise ArgumentError, message: "incompatible WeatherSketch options"
  end

  def report(%__MODULE__{} = summary) do
    %{
      station_count: map_size(summary.stations),
      exact_rows: summary.stations |> Map.values() |> Enum.reduce(0, &(&1.count + &2)),
      quantiles: %{
        p50: KLL.quantile(summary.kll, 0.50),
        p90: KLL.quantile(summary.kll, 0.90),
        p99: KLL.quantile(summary.kll, 0.99)
      },
      distinct_estimate: HLL.estimate(summary.hll),
      heavy_hitters: FrequentItems.top_k(summary.frequent, limit: 5),
      sizes: %{
        kll: KLL.size_bytes(summary.kll),
        hll: HLL.size_bytes(summary.hll),
        frequent: FrequentItems.size_bytes(summary.frequent),
        kll_serialized: byte_size(KLL.serialize(summary.kll)),
        hll_serialized: byte_size(HLL.serialize(summary.hll)),
        frequent_serialized: byte_size(FrequentItems.serialize(summary.frequent))
      }
    }
  end
end
```

Immutable updates require rebinding. Merge only summaries built with the same sketch parameters; incompatible sketches raise `ExDataSketch.Errors.IncompatibleSketchesError` (or your own options check).

---

## Partition, then merge

Private state plus merge fits the BEAM. Each worker owns a `WeatherSketch`. After work finishes, merge results. Avoid a single `Agent` that receives one message per row; that serializes the hot path.

File partitioning must preserve **complete lines** and UTF-8 boundaries. Do not pretend arbitrary byte slices are records. For teaching, split an already-parsed list into chunks:

```elixir
partitions = Enum.chunk_every(rows, 3)

merged =
  partitions
  |> Task.async_stream(
    fn chunk ->
      Enum.reduce(chunk, WeatherSketch.new(), &WeatherSketch.update(&2, &1))
    end,
    max_concurrency: System.schedulers_online(),
    ordered: false,
    timeout: :infinity
  )
  |> Enum.reduce(WeatherSketch.new(), fn
    {:ok, part}, acc -> WeatherSketch.merge(acc, part)
    {:exit, reason}, _acc -> exit(reason)
  end)
```

Discuss with your team:

- `max_concurrency` should track cores and I/O, not wishful thinking;
- `ordered: false` is fine when merge is commutative for the estimates you care about;
- worker failures should fail the reduce explicitly;
- concurrency will not help if parsing or disk is already the bottleneck.

Independently built compatible summaries must match a single-pass summary for exact station aggregates and should agree closely for sketches.

---

## Measure accuracy and size

For any sketch answer, record:

| Field | Meaning |
|-------|---------|
| Exact | Ground truth on the fixture or sample |
| Estimate | Sketch query |
| Absolute error | `\|estimate - exact\|` |
| Relative error | absolute / exact (when exact ≠ 0) |
| `size_bytes/1` | In-memory state bytes |
| `serialize/1` | Portable EXSK payload bytes |
| Elapsed | Wall time for that run only |

When publishing your own numbers, report Elixir version, OTP version, OS, CPU, input size, and whether the Pure or Rust backend ran.

Sketches are **not** automatically faster or more accurate than exact maps. They are smaller and mergeable under constraints you accept.

---

## Comparison at a glance

| Approach | Answers | Memory shape | Mergeable? | Best when |
|----------|---------|--------------|------------|-----------|
| Exact accumulator | count, sum, min, max, mean | O(stations) | Yes | Station set is modest |
| KLL | approximate quantiles / ranks | grows with `k`, sublinear in n | Yes (same `k`) | Rank questions over huge numeric streams |
| HLL | approximate distinct count | `2^p` registers | Yes (same `p`) | High-cardinality keys |
| FrequentItems | approximate heavy hitters | O(`k` counters) | Yes (same `k`, encoding) | “Who dominates?” without knowing keys |
| CMS | approximate frequency of a key | width × depth | Yes (same geometry) | Point queries for known keys |

---

## When not to use a sketch

- You need exact answers and can afford exact state.
- The key cardinality already fits in a map.
- Min, max, count, and mean are the whole story.
- Stakeholders cannot accept bounded error, even with documented error fields.
- You would spend more engineering time explaining approximation than the sketch saves.

## Production considerations

- Version sketch parameters (`k`, `p`, key encoding) beside the payloads you persist.
- Prefer documented `serialize/1` / `deserialize/1` over ad-hoc struct dumps.
- Merge only compatible sketches; fail loudly otherwise.
- Keep exact extrema next to quantile sketches when dashboards show both.
- Validate with a fixture and a sampled exact pass before trusting production estimates.
- See the [integration guide](https://ex-data-sketch.hexdocs.pm/integrations.html) for Stream, Flow, and Broadway patterns.

---

## Decision guide

- **Exact accumulators** for min, max, count, and mean.
- **KLL** for rank-based temperature questions.
- **HLL** for high-cardinality distinct counts.
- **FrequentItems** for retrieving heavy hitters.
- **CMS** for approximate frequency of specified items.
- **Mergeable summaries** when shipping raw rows is more expensive than shipping state.

A billion-row analysis does not require a billion-row data structure. It requires a clear question and the smallest mergeable state that answers it accurately enough.

---

## Exercises

1. Replace the global KLL with per-station KLL sketches for the top heavy hitters only. Discuss memory.
2. Feed the skewed stream into `ExDataSketch.CMS` and compare `CMS.estimate/2` for `"Hamburg"` and a rare key against exact counts.
3. Build two Theta sketches (`ExDataSketch.Theta`) over alternate station subsets and explore union/intersection cardinality estimates.
4. Swap KLL for `ExDataSketch.DDSketch` with a relative-accuracy parameter and compare p99 behavior on a heavy-tailed synthetic temperature stream.
5. Persist `KLL.serialize/1` (and friends) to disk, then reload with `{:ok, sketch} = KLL.deserialize(binary)`.

---

## Links

- [One Billion Row Challenge](https://github.com/gunnarmorling/1brc)
- [`ex_data_sketch` on Hex](https://hex.pm/packages/ex_data_sketch)
- [v0.9+ HexDocs](https://ex-data-sketch.hexdocs.pm/)
- [Integration guide](https://ex-data-sketch.hexdocs.pm/integrations.html)
