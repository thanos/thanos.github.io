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

Here is a rewritten version that applies the readability, focus, and retention improvements we discussed. It keeps your voice, all the concrete numbers, the Elixir examples, and the strong conceptual spine, while moving the payoff earlier and making the structure easier to scan and remember.

---

# Data Sketches Beyond the One Billion Row Challenge

*A data sketch is useful when a small, mergeable approximation is more valuable than an exact answer whose state is expensive to retain, move, or combine.*

The One Billion Row Challenge is a good analytical story and a bad sketch tutorial if you stop at the original result. Gunnar Morling’s [1BRC](https://github.com/gunnarmorling/1brc) asks for minimum, mean, and maximum temperature per weather station. That contract is exact. Sprinkling HyperLogLog on it does not make it more honest.

This article is about the questions *around* that contract: quantiles, distinct sensors, heavy hitters, set overlap, and rollups you can ship between regions. The sketches come from [`ex_data_sketch`](https://hex.pm/packages/ex_data_sketch) `~> 0.10`. If you want an optimized Elixir 1BRC (file generation, parsing, profiling, schedulers), read [Raj Rajhans’s elixir_1brc](https://github.com/rajrajhans/elixir_1brc) instead. This piece starts after the rows are already structured observations.

**Roadmap**

1. When exact summaries win (and sketches add only error)
2. The questions that actually need sketches
3. HLL, KLL, and FrequentItems on a shared stream
4. Short notes on Theta, CMS, and DDSketch
5. A five-question decision rule and a final comparison

We assume records that already look like this:

```elixir
%{station: "Abha", temperature: 18.4, sensor_id: "sensor-1042", region: "west"}
```

Estimates were run against `ex_data_sketch` 0.10.0 (compatible with `~> 0.9`) on Elixir 1.18.4 / OTP 28 using the Pure backend. Timings are local observations, not a benchmark. The 12 000-row stream is illustrative of shape and merge behaviour; the real motivation appears at much larger cardinality and multi-node rollups.

---

## When exact wins

Minimum and maximum are exactly mergeable: `min(min_a, min_b)` and `max(max_a, max_b)`. Mean is exactly mergeable if you keep **sum** and **count**, not the mean itself. Per station that is four scalars:

```elixir
%{min: -2.0, max: 22.0, sum: 30.0, count: 3}
```

With a few hundred station names the whole map stays tiny. Approximating it weakens the answer without solving a state-size problem.

| Question              | Best structure       | Exact or estimated? | Why                  |
|-----------------------|----------------------|---------------------|----------------------|
| Minimum by station    | Scalar accumulator   | Exact               | Constant state       |
| Mean by station       | Sum and count        | Exact               | Exactly mergeable    |
| Maximum by station    | Scalar accumulator   | Exact               | Constant state       |

That table is the conceptual anchor. Everything that follows is a *different question*.

---

## Questions that need sketches

| Question                                      | Why exact state grows                  | Sketch                          |
|-----------------------------------------------|----------------------------------------|---------------------------------|
| Median, p95, p99 temperature                  | Rank statistics need ordered values    | KLL (or DDSketch for relative value error) |
| Distinct sensor IDs                           | Set of IDs grows with cardinality      | HLL                             |
| Dominant stations or alert codes              | Full frequency map grows with keys     | FrequentItems                   |
| Sensors seen in region A **or** region B      | Exact sets grow; union stays bounded   | Theta (`merge/2` is union)      |
| Frequency of a *specified* error code         | Point queries over a huge key space    | CMS                             |

Each sketch returns an estimate with an explicit accuracy budget. Compatible sketches (same parameters, same hash identity where hashing is used) merge. Incompatible ones should refuse.

---

## A deterministic telemetry stream

Twelve thousand already-structured observations, generated lazily in index order `0..11_999`:

- `station`: `"S#{rem(i, 40)}"` — 40 stations
- `sensor_id`: `"sensor-#{rem(i, 1800)}"` — 1 800 distinct sensors
- `region`: west / east / north by `rem(i, 3)`
- `temperature`: `rem(i * 17, 401) / 10.0 - 10.0`
- `alert_code`: mostly `"OK"`, plus `"HIGH_TEMP"` and `"SENSOR_FAULT"`

Exact reference values (computed independently of any sketch):

| Measurement                          | Exact   |
|--------------------------------------|---------|
| Rows                                 | 12 000  |
| Distinct sensors                     | 1 800   |
| Distinct stations                    | 40      |
| Median temperature (nearest-rank)    | 10.0    |
| p95                                  | 28.0    |
| p99                                  | 29.6    |
| Alert OK                             | 11 280  |
| Alert HIGH_TEMP                      | 600     |
| Alert SENSOR_FAULT                   | 120     |

Nearest-rank is an evaluation method for this sample, not a streaming algorithm.

---

## Distinct sensors with HLL

**Question:** How many distinct sensor IDs have we seen?

HyperLogLog estimates cardinality. Precision `p` allocates `m = 2^p` registers. Relative standard error is about `1.04 / sqrt(m)`. You never store the IDs.

```elixir
alias ExDataSketch.HLL

sensors = Enum.map(observations, & &1.sensor_id)

hll_p8  = HLL.new(p: 8)  |> HLL.update_many(sensors)
hll_p14 = HLL.new(p: 14) |> HLL.update_many(sensors)

HLL.estimate(hll_p8)   # ~1713.71
HLL.estimate(hll_p14)  # ~1787.01
```

| Config   | Estimate | Abs. error | Rel. error | size_bytes | Serialized | Update time |
|----------|----------|------------|------------|------------|------------|-------------|
| HLL p: 8 | 1713.71  | 86.29      | 4.79 %     | 260        | 300        | 34.1 ms     |
| HLL p: 14| 1787.01  | 12.99      | 0.72 %     | 16 388     | 16 428     | 6.0 ms      |

Region-local sketches with the same `p: 14` merge to the identical estimate (1787.01). Compatible parameters are not optional.

**Takeaway:** Higher `p` buys tighter relative error at the cost of memory. The update-time difference above is a local observation — do not generalise it.

**Use when:** Distinct keys will not fit in memory or must be merged across partitions. Accept relative error of roughly `1.04 / √m`.

---

## Quantiles with KLL

**Question:** What is the median / p95 / p99 temperature?

A quantile is a value at a rank. Exact streaming quantiles want ordered observations. KLL keeps compact levels of samples and approximates *rank*. The parameter `k` trades memory for rank error (roughly `1.65 / k`).

KLL’s guarantee is rank error, not “the number came out 0.2 °C off.” A 0.3 °C gap can be a small rank miss or a large one depending on the distribution.

```elixir
alias ExDataSketch.KLL

temps = Enum.map(observations, & &1.temperature)
kll   = KLL.new(k: 200) |> KLL.update_many(temps)

KLL.quantiles(kll, [0.50, 0.95, 0.99])
```

| Measurement | Exact | Estimate | Abs. error | Rank error | Config | Size / serialized |
|-------------|-------|----------|------------|------------|--------|-------------------|
| Median      | 10.0  | 10.2     | 0.2        | 0.65 %     | k: 50  | 748 / 790         |
| p95         | 28.0  | 28.0     | 0.0        | 0.02 %     | k: 50  | 748 / 790         |
| p99         | 29.6  | 29.8     | 0.2        | 0.50 %     | k: 50  | 748 / 790         |
| Median      | 10.0  | 10.3     | 0.3        | 0.90 %     | k: 200 | 2 699 / 2 741     |
| p95         | 28.0  | 28.4     | 0.4        | 1.01 %     | k: 200 | 2 699 / 2 741     |
| p99         | 29.6  | 29.8     | 0.2        | 0.50 %     | k: 200 | 2 699 / 2 741     |

More memory buys a stronger statistical guarantee, not a monotonic improvement of every individual query. Exact min and max still belong in the four-scalar station summary — do not replace them with a quantile sketch.

Independent per-region `k: 200` sketches merge cleanly (`KLL.merge_many/1`). Merged median was 10.0 versus the single-pass 10.3; internal compaction means results need not be bit-identical.

**Use when:** You need mergeable approximate distributions and can reason in rank error. Prefer DDSketch when you care about relative *value* error (typical for latency SLOs).

---

## Heavy hitters with FrequentItems

**Question:** Which stations or alert codes dominate?

FrequentItems is SpaceSaving: at most `k` counters. Each tracked item carries an estimate and a maximum overcount (`error`). Low-frequency keys can be evicted.

When the key set is smaller than `k`, the sketch can match exact counts. On the three alert codes, `k: 8` did exactly that:

| Item         | Exact  | Estimate | Error bound | Lower–upper   |
|--------------|--------|----------|-------------|---------------|
| OK           | 11 280 | 11 280   | 0           | 11 280–11 280 |
| HIGH_TEMP    | 600    | 600      | 0           | 600–600       |
| SENSOR_FAULT | 120    | 120      | 0           | 120–120       |

Serialized size: 158 bytes. Region-local sketches merged to the same three rows.

The instructive case is capacity `k: 5` on the 40-station stream. Exact top counts were S0 = 1 200, S1 = 700, then several stations at 300. The sketch returned different keys with overcounts of 2 100–2 200. The true heavy hitters were gone. The error fields said so — if you read them.

FrequentItems answers “who looks hot, in bounded space?” It is not a frequency table. If you already know the key and need a point query, prefer CMS.

**Use when:** You can tolerate eviction of rare keys and want bounded counters with explicit overcount bounds. Never ignore the error fields.

---

## Shorter cousins

**Theta** estimates set cardinality and supports union via `merge/2`. Union of the three regional sensor sketches estimated 1 713.07 distinct IDs against an exact 1 800. The public API used here is construction, update, union-merge, estimate, and serialize. Do not invent an `intersect/2`.

**CMS** (Count-Min Sketch) answers point queries over a large key space. On the alert stream, `CMS.new(width: 256, depth: 3)` recovered the exact counts for OK and HIGH_TEMP in 3 081 bytes of state.

**DDSketch** is the quantile cousin for relative *value* error (typical for latency SLOs). It wants non-negative values — shift temperatures or use it on latencies.

---

## Error is a budget, not a vibe

- **HLL** → relative cardinality error. `p` buys registers.
- **KLL** → rank error. Do not quote a Celsius gap as if it were the guarantee.
- **FrequentItems** → capacity + eviction + documented overcount. Ignore `error` / `lower` and you will believe ghosts.

Also:

- Reproducible hashing and matching parameters are part of merge correctness.
- Distributions matter. A sketch that looks perfect on three alert codes can lie on forty skewed stations.
- Approximate does not mean casually inaccurate. It means accuracy has an explicit budget you chose.

---

## What sketches actually optimise

They do **not** make parsing faster. They do **not** automatically beat `min/max/sum/count` on a 40-station map.

They do:

- bound or sub-linearise state as rows grow
- cut memory pressure when the alternative is “keep every ID or every latency”
- serialise into small payloads
- merge partial results instead of shipping raw observations
- roll up across workers, windows, nodes, and regions

```
region A observations → sketch A ┐
region B observations → sketch B ├→ merge → global estimate
region C observations → sketch C ┘
```

Not retaining raw events can reduce how much identifiable payload you keep around. That is a retention property, not a security guarantee.

---

## When not to use sketches

Give this list more weight than the happy path.

- The answer is legally, financially, or operationally required to be exact (balances, dosages, billing, safety interlocks).
- An exact accumulator is already constant-size — that is the original 1BRC min/mean/max result. A sketch would only add error.
- Cardinality is small (forty stations and three alert codes fit in a map).
- The dataset is small, or you will query it once and throw it away.
- Rare items matter more than heavy hitters. SpaceSaving is allowed to forget the rare key.
- Future questions need columns the sketch discarded. You cannot ask “show me the raw trace for sensor-1042 last Tuesday” of an HLL.
- You need corrections or deletes the chosen sketch does not support.
- Parameters, versions, seeds, or hash strategies do not match. Merge will raise `IncompatibleSketchesError` (or worse, you force it and get nonsense).
- Nobody can define or monitor an error budget.
- Inputs may be adversarial against the hash.
- Audit, debugging, or model retraining still needs raw events.

Sketches complement exact aggregates and warehouses. They do not automatically replace them.

---

## A five-question decision

1. **What exact question must the summary answer?**  
   Min/mean/max is not a quantile, and neither is a distinct count.

2. **How does exact state grow with rows or distinct keys?**  
   Four scalars per station stay cheap. A set of sensor IDs does not.

3. **What error can consumers tolerate?**  
   Rank error, relative cardinality error, and overcount bounds are different sentences. Write the one you mean.

4. **Must summaries merge across partitions or time windows?**  
   If yes, you need compatible, associative merge — not a shared process that eats one message per row.

5. **Will future queries need information the sketch discards?**  
   If yes, keep a raw or exact path beside the sketch, or do not sketch.

---

## Comparison at a glance

| Sketch          | Answers                          | Main parameter     | Error type              | Merge          | Typical size order |
|-----------------|----------------------------------|--------------------|-------------------------|----------------|--------------------|
| Exact 4-scalar  | min / mean / max                 | —                  | none                    | exact          | constant           |
| HLL             | distinct count                   | `p` (registers)    | relative cardinality    | yes            | hundreds of bytes → tens of KB |
| KLL             | quantiles (rank)                 | `k`                | rank error              | yes            | low KB             |
| FrequentItems   | heavy hitters                    | `k` (capacity)     | overcount + eviction    | yes            | hundreds of bytes  |
| Theta           | cardinality + set union          | —                  | relative cardinality    | union          | similar to HLL     |
| CMS             | point frequency queries          | width × depth      | overcount               | yes            | low KB             |
| DDSketch        | quantiles (relative value)       | relative accuracy  | relative value error    | yes            | low KB             |

---

Process the billion rows. Retain only the state the questions justify.

---

### Links

- [One Billion Row Challenge](https://github.com/gunnarmorling/1brc)
- [Raj Rajhans, Elixir 1BRC](https://github.com/rajrajhans/elixir_1brc)
- [`ex_data_sketch` on Hex](https://hex.pm/packages/ex_data_sketch)
- [HexDocs](https://ex-data-sketch.hexdocs.pm/)
- [Integration guide](https://ex-data-sketch.hexdocs.pm/integrations.html)

---

### What changed and why

- Opening is ~40 % shorter; the first useful sketch appears much earlier.
- Explicit roadmap and consistent “Question → parameter → code → results + takeaway → Use when” shape for the three main sketches.
- Five-question framework and comparison table elevated for retention.
- Dense paragraphs broken up; every results table now has an explicit takeaway.
- 12 k-row stream is framed as illustrative of shape and merge behaviour.
- Voice, numbers, code intent, and the strong “when not” list are preserved.