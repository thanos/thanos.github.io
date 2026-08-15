---
title: "Data Sketches Beyond the One Billion Row Challenge"
description: "A small, mergeable approximation is more valuable than an exact answer whose state is expensive to retain, move, or combine. The original 1BRC min/mean/max result does not need a sketch."
date: 2026-08-15
tags:
  - Elixir
  - ex_data_sketch
  - data sketches
  - HyperLogLog
  - KLL
  - FrequentItems
  - Theta
  - CMS
  - 1BRC
  - streaming analytics

draft: false
---

*A data sketch is useful when a small, mergeable approximation is more valuable than an exact answer whose state is expensive to retain, move, or combine.*

The One Billion Row Challenge is a good analytical story and a bad sketch tutorial if you stop at the original result.

Gunnar Morling’s [1BRC](https://github.com/gunnarmorling/1brc) asks for minimum, mean, and maximum temperature per weather station, from a billion observations, printed alphabetically and rounded to one decimal place. That contract is exact. It does not become more honest if you sprinkle HyperLogLog on it.

This article is about the questions *around* that contract: quantiles, distinct sensors, heavy hitters, set overlap, and rollups you can ship between regions. The sketches come from [`ex_data_sketch`](https://hex.pm/packages/ex_data_sketch) `~> 0.9`. If you want an optimized Elixir 1BRC—file generation, parsing, profiling, schedulers—read [Raj Rajhans’s `elixir_1brc`](https://github.com/rajrajhans/elixir_1brc) instead. That work already exists. This one starts after the rows are structured observations.

How the file was opened is out of scope. We assume records that already look like this:

```elixir
%{station: "Abha", temperature: 18.4, sensor_id: "sensor-1042", region: "west"}
```

Estimates below were executed against `ex_data_sketch` 0.10.0 (compatible with `~> 0.9`) on Elixir 1.18.4 / OTP 28, using the Pure backend. Timings are local observations, not a benchmark.

---

## The original result is exact, and that is the point

The official challenge output is a single line of `{name=min/mean/max, ...}` groups. The repository documents this shape, including a short excerpt:

```text
{Abha=-23.0/18.0/59.2, Abidjan=-16.2/26.0/67.3,
 Abéché=-10.0/29.4/69.0, Accra=-10.1/26.4/66.4, ...}
```

Those numbers are **not** from the tutorial fixture below. They are the documented 1BRC form: `min/mean/max` per station.

A tiny already-structured fixture is enough to show the same contract completely:

```elixir
fixture = [
  %{station: "Abha", temperature: -2.0},
  %{station: "Abha", temperature: 10.0},
  %{station: "Abha", temperature: 22.0},
  %{station: "Abidjan", temperature: 24.0},
  %{station: "Abidjan", temperature: 26.0},
  %{station: "Abidjan", temperature: 28.0},
  %{station: "Accra", temperature: 15.5},
  %{station: "Accra", temperature: 16.5},
  %{station: "Cracow", temperature: 8.0},
  %{station: "Cracow", temperature: 8.0},
  %{station: "Cracow", temperature: 8.0},
  %{station: "Cracow", temperature: 12.0},
  %{station: "Hamburg", temperature: 12.3},
  %{station: "Hamburg", temperature: 12.1}
]
```

Complete exact result for that fixture (mean shown to one decimal, matching the 1BRC presentation):

```text
{Abha=-2.0/10.0/22.0, Abidjan=24.0/26.0/28.0, Accra=15.5/16.0/16.5,
 Cracow=8.0/9.0/12.0, Hamburg=12.1/12.2/12.3}
```

No sketch was involved. None is required.

---

## Which sketches reproduce min / mean / max?

None are needed.

Minimum and maximum are exactly mergeable: `min(min_a, min_b)` and `max(max_a, max_b)`. Mean is exactly mergeable if you keep **sum** and **count**, not the mean itself. Per station that is four scalars:

```elixir
%{min: -2.0, max: 22.0, sum: 30.0, count: 3}
```

Call that a compact exact summary. It is not a probabilistic sketch. With a few hundred station names, the whole map is tiny. Approximating it would weaken the answer without solving a state-size problem.

| Question | Best structure | Exact or estimated? | Why? |
|---|---|---|---|
| Minimum by station | Scalar accumulator | Exact | Constant state |
| Mean by station | Sum and count | Exact | Exactly mergeable |
| Maximum by station | Scalar accumulator | Exact | Constant state |

That table is the conceptual anchor. Everything that follows is a *different question*.

---

## Questions 1BRC did not ask

Keep the weather-station vocabulary, then add fields the original challenge never scored:

| Question | Why exact state grows | Sketch |
|---|---|---|
| Median, p95, p99 temperature | Rank statistics need ordered values, or an equivalent | `ExDataSketch.KLL` (or `DDSketch` for relative value error) |
| Distinct sensor IDs | A set of IDs grows with cardinality | `ExDataSketch.HLL` |
| Dominant stations or alert codes | A full frequency map grows with distinct keys | `ExDataSketch.FrequentItems` |
| Sensors seen in region A **or** region B | Exact sets grow; union of sketches stays bounded | `ExDataSketch.Theta` (`merge/2` is union) |
| Frequency of a *specified* error code | Point queries over a huge key space | `ExDataSketch.CMS` |

Each sketch returns an estimate with an explicit accuracy budget. Compatible sketches (same parameters, same hash identity where hashing is used) merge. Incompatible ones should refuse.

The rest of this article develops KLL, HLL, and FrequentItems. Theta, CMS, and DDSketch stay short.

---

## A deterministic telemetry stream

Twelve thousand already-structured observations, generated lazily in index order `0..11_999`:

- `station`: `"S#{rem(i, 40)}"` — 40 stations
- `sensor_id`: `"sensor-#{rem(i, 1800)}"` — 1,800 distinct sensors
- `region`: west / east / north by `rem(i, 3)`
- `temperature`: `rem(i * 17, 401) / 10.0 - 10.0`
- `alert_code`: mostly `"OK"`, plus `"HIGH_TEMP"` and `"SENSOR_FAULT"`

Exact reference values, computed independently of any sketch:

| Measurement | Exact |
|---|---:|
| Rows | 12,000 |
| Distinct sensors | 1,800 |
| Distinct stations | 40 |
| Median temperature (nearest-rank 0.50) | 10.0 |
| p95 (nearest-rank 0.95) | 28.0 |
| p99 (nearest-rank 0.99) | 29.6 |
| Alert `OK` | 11,280 |
| Alert `HIGH_TEMP` | 600 |
| Alert `SENSOR_FAULT` | 120 |

Nearest-rank means: sort the values, take index `ceil(rank * n) - 1`, clamped to the list. That is an evaluation method for this sample, not a streaming algorithm.

---

## Distinct sensors with HLL

[HyperLogLog](https://ex-data-sketch.hexdocs.pm/ExDataSketch.HLL.html) estimates cardinality. Precision `p` allocates `m = 2^p` registers. Relative standard error is about `1.04 / sqrt(m)`. You do not store the IDs.

```elixir
alias ExDataSketch.HLL

sensors = Enum.map(observations, & &1.sensor_id)

hll_p8 = HLL.new(p: 8) |> HLL.update_many(sensors)
hll_p14 = HLL.new(p: 14) |> HLL.update_many(sensors)

HLL.estimate(hll_p8)
HLL.estimate(hll_p14)
HLL.size_bytes(hll_p8)
byte_size(HLL.serialize(hll_p14))
```

Executed on the 12,000-row stream (exact distinct = 1,800):

| Config | Estimate | Abs. error | Rel. error | `size_bytes` | Serialized | Update time |
|---|---:|---:|---:|---:|---:|---:|
| HLL `p: 8` | 1713.71 | 86.29 | 4.79% | 260 | 300 | 34.1 ms |
| HLL `p: 14` | 1787.01 | 12.99 | 0.72% | 16,388 | 16,428 | 6.0 ms |

The tighter precision used more memory and produced a closer estimate here. The faster `p: 14` update is a **local observation** (warmup, allocator, backend)—do not read it as “higher `p` is quicker.”

Region-local sketches with the same `p: 14` merged to the same estimate as the single-pass sketch: **1787.01**. Compatible parameters are not optional.

```elixir
parts =
  observations
  |> Enum.group_by(& &1.region)
  |> Enum.map(fn {_region, rows} ->
    HLL.new(p: 14) |> HLL.update_many(Enum.map(rows, & &1.sensor_id))
  end)

HLL.estimate(HLL.merge_many(parts))
# 1787.0059514889374  — same as the direct p: 14 sketch
```

On the original 1BRC station list, exact `MapSet` counting is practical. HLL starts to earn its keep when identifiers are devices, request keys, or anything whose distinct set will not fit next to the dashboard.

---

## Quantiles with KLL

A **quantile** is a value at a rank: median is rank 0.50, p95 is 0.90… here 0.95. Exact streaming quantiles want ordered observations. [KLL](https://ex-data-sketch.hexdocs.pm/ExDataSketch.KLL.html) keeps compact levels of samples and approximates **rank**. The accuracy parameter `k` trades memory for rank error (library docs: roughly `1.65 / k`).

KLL’s error concept is rank, not “the number came out 0.2°C off.” A 0.3°C gap can be a small rank miss or a large one, depending on the distribution.

```elixir
alias ExDataSketch.KLL

temps = Enum.map(observations, & &1.temperature)

kll = KLL.new(k: 200) |> KLL.update_many(temps)
KLL.quantiles(kll, [0.50, 0.95, 0.99])
```

Executed results:

| Measurement | Exact | Estimate | Abs. error | Rank error | Config | Size / serialized |
|---|---:|---:|---:|---:|---|---:|
| KLL median | 10.0 | 10.2 | 0.2 | 0.65% | `k: 50` | 748 / 790 |
| KLL p95 | 28.0 | 28.0 | 0.0 | 0.02% | `k: 50` | 748 / 790 |
| KLL p99 | 29.6 | 29.8 | 0.2 | 0.50% | `k: 50` | 748 / 790 |
| KLL median | 10.0 | 10.3 | 0.3 | 0.90% | `k: 200` | 2,699 / 2,741 |
| KLL p95 | 28.0 | 28.4 | 0.4 | 1.01% | `k: 200` | 2,699 / 2,741 |
| KLL p99 | 29.6 | 29.8 | 0.2 | 0.50% | `k: 200` | 2,699 / 2,741 |

`k: 200` used more memory and did **not** win every individual query on this sample. That is expected. More memory buys a stronger statistical guarantee, not a monotonic improvement of every draw. Relative numeric error is `n/a` here: rank error is the quantity KLL budgets.

Exact min and max still belong in the four-scalar station summary. Do not replace them with a quantile sketch.

Independent `k: 200` sketches, one per region, merged with `KLL.merge_many/1`. Merged count was 12,000. Merged median was 10.0. The single-pass `k: 200` median was 10.3. Merge is compatible and associative at the estimate level; internal compaction means query results need not be bit-identical to a one-shot sketch.

---

## Heavy hitters with FrequentItems

[FrequentItems](https://ex-data-sketch.hexdocs.pm/ExDataSketch.FrequentItems.html) is SpaceSaving: at most `k` counters. Each tracked item carries an estimate and a maximum overcount (`error`). `lower` is `max(estimate - error, 0)`; `upper` equals the estimate. Low-frequency keys can be **evicted**.

When the key set is smaller than `k`, the sketch can match exact counts. On the three alert codes, `k: 8` did exactly that:

```elixir
alias ExDataSketch.FrequentItems

alerts = Enum.map(observations, & &1.alert_code)

fi = FrequentItems.new(k: 8) |> FrequentItems.update_many(alerts)
FrequentItems.top_k(fi)
```

| Item | Exact | Estimate | Error bound | Lower–upper |
|---|---:|---:|---:|---|
| `OK` | 11,280 | 11,280 | 0 | 11,280–11,280 |
| `HIGH_TEMP` | 600 | 600 | 0 | 600–600 |
| `SENSOR_FAULT` | 120 | 120 | 0 | 120–120 |

Serialized size: 158 bytes (`size_bytes` 115). Region-local sketches merged to the same three rows.

That is the easy case. Capacity `k: 5` on a **skewed station** stream with 40 keys is the instructive one. Exact top counts were `S0` 1,200, `S1` 700, then several stations at 300. The sketch returned `S9`, `S6`, `S7`, `S8`, `S5` with overcounts of 2,100–2,200. The true heavy hitters were gone. The error fields said so, if you read them.

FrequentItems answers “who looks hot, in bounded space?” It is not a frequency table. If you already know the key and need a point query, [CMS](https://ex-data-sketch.hexdocs.pm/ExDataSketch.CMS.html) is the better shape. On this alert stream, `CMS.new(width: 256, depth: 3)` estimated `OK` as 11,280 and `HIGH_TEMP` as 600—matching exact counts, in 3,081 bytes of state.

---

## Error is a budget, not a vibe

- **HLL** is relative cardinality error. `p` buys registers. Individual estimates wander with the hash and the set.
- **KLL** is rank error. Do not quote a Celsius gap as if it were the guarantee.
- **FrequentItems** is capacity plus eviction plus documented overcount. Ignore `error` / `lower` and you will believe ghosts.

Also:

- Reproducible hashing and matching parameters are part of merge correctness.
- Distributions matter. A sketch that looks perfect on three alert codes can lie on forty skewed stations.
- Approximate does not mean casually inaccurate. It means accuracy has an explicit budget you chose.

---

## What sketches actually optimize

They do not make parsing faster. They do not automatically beat `min/max/sum/count` on a 40-station map.

They do:

- bound or sublinearize state as rows grow;
- cut memory pressure when the alternative is “keep every ID or every latency”;
- serialize into small EXSK payloads (`HLL.serialize/1`, `KLL.serialize/1`, …);
- merge partial results instead of shipping raw observations;
- roll up across workers, windows, nodes, and regions.

```text
region A observations → sketch A ┐
region B observations → sketch B ├→ merge → global estimate
region C observations → sketch C ┘
```

Not retaining raw events can reduce how much identifiable payload you keep around. That is a retention property, not a security guarantee. Hashes and heavy hitters still leak structure.

---

## A problem where the sketch is the point

Leave 1BRC’s few hundred station names. Picture a global telemetry platform:

- billions of readings per day;
- tens or hundreds of millions of sensor IDs;
- many regions and processing nodes;
- minute / hour / day windows;
- dashboards that want distinct devices, latency quantiles, hot error codes, and set union across regions;
- compact summaries kept for months, not indefinite raw retention.

Exact distinct sets become maps of millions of IDs. Exact latency history becomes a warehouse query. Exact frequency maps grow with every new alert key.

Mergeable sketches invert that: store one HLL, one KLL, one FrequentItems (and optionally CMS / Theta) **per window per region**, then combine.

Symbolic cost, not a fabricated production bill: an exact ID set is O(distinct IDs). An HLL at `p: 14` is 16 KiB of registers whether you saw 1,800 sensors or 80 million. A KLL at `k: 200` stayed under 3 KiB on 12,000 values in this run; it will not grow linearly with a day’s samples.

```elixir
alias ExDataSketch.{FrequentItems, HLL, KLL}

summarize_region = fn rows ->
  %{
    sensors: HLL.new(p: 14) |> HLL.update_many(Enum.map(rows, & &1.sensor_id)),
    temps: KLL.new(k: 200) |> KLL.update_many(Enum.map(rows, & &1.temperature)),
    alerts: FrequentItems.new(k: 8) |> FrequentItems.update_many(Enum.map(rows, & &1.alert_code))
  }
end

per_region =
  observations
  |> Enum.group_by(& &1.region)
  |> Map.new(fn {region, rows} -> {region, summarize_region.(rows)} end)

global_sensors =
  per_region
  |> Map.values()
  |> Enum.map(& &1.sensors)
  |> HLL.merge_many()

HLL.estimate(global_sensors)
```

Inputs are already structured. The merge is the product.

[Theta](https://ex-data-sketch.hexdocs.pm/ExDataSketch.Theta.html) is the sketch family aimed at set algebra. In `ex_data_sketch` `~> 0.9`, `Theta.merge/2` is **union**. On this stream, a `k: 256` union of the three regional sensor sketches estimated 1,713.07 distinct IDs against an exact 1,800. Module docs describe intersection and difference; this version’s public API used here is construction, update, union-merge, estimate, and serialize. Do not invent an `intersect/2`.

[DDSketch](https://ex-data-sketch.hexdocs.pm/ExDataSketch.DDSketch.html) is the quantile cousin when you care about **relative value** error (typical for latency SLOs) rather than KLL’s rank error. It wants non-negative values—shift temperatures, or use it on latencies.

---

## When not to use sketches

Give this list more weight than the happy path.

- The answer is legally, financially, or operationally required to be exact: balances, dosages, billing line items, safety interlocks.
- An exact accumulator is already constant-size. **That is the original 1BRC min / mean / max result.** A sketch would only add error.
- Cardinality is small. Forty stations and three alert codes fit in a map.
- The dataset is small, or you will query it once and throw it away.
- Rare items matter more than heavy hitters. SpaceSaving is allowed to forget the rare key.
- Future questions need columns the sketch discarded. You cannot ask “show me the raw trace for sensor-1042 last Tuesday” of an HLL.
- You need corrections or deletes the chosen sketch does not support.
- Parameters, versions, seeds, or hash strategies do not match. Merge will raise `IncompatibleSketchesError`, or worse, you will force it and get nonsense.
- Nobody can define or monitor an error budget.
- Inputs may be adversarial against the hash.
- Audit, debugging, or model retraining still needs raw events.

Sketches complement exact aggregates and warehouses. They do not automatically replace them.

---

## A five-question decision

1. **What exact question must the summary answer?** Min/mean/max is not a quantile, and neither is a distinct count.
2. **How does exact state grow with rows or distinct keys?** Four scalars per station stay cheap. A set of sensor IDs does not.
3. **What error can consumers tolerate?** Rank error, relative cardinality error, and overcount bounds are different sentences. Write the one you mean.
4. **Must summaries merge across partitions or time windows?** If yes, you need compatible, associative merge—not a shared process that eats one message per row.
5. **Will future queries need information the sketch discards?** If yes, keep a raw or exact path beside the sketch, or do not sketch.

Process the billion rows. Retain only the state the questions justify.

---

## Links

- [One Billion Row Challenge](https://github.com/gunnarmorling/1brc)
- [Raj Rajhans, Elixir 1BRC](https://github.com/rajrajhans/elixir_1brc)
- [`ex_data_sketch` on Hex](https://hex.pm/packages/ex_data_sketch)
- [HexDocs](https://ex-data-sketch.hexdocs.pm/)
- [Integration guide](https://ex-data-sketch.hexdocs.pm/integrations.html)
