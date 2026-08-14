---
title: "Data Sketches: A Field Guide"
description: "The essential algorithms for reasoning about massive data streams"
date: 2026-07-20
tags:
  - Elixir
  - OTP
  - GenServer
  - UDP
  - drones
  - Tello
  - safety
  - simulation
  - telemetry
  - ex_drone

draft: false
series: data-sketches
---

# Data Sketches: A Field Guide
## The essential algorithms for reasoning about massive data streams

This part explains the algorithms themselves.
This isn’t a mathematical deep dive. Our goal is simpler:
→ Understand __what each sketch family does__,
→ Grasp __how it works at a high level__,
→ Know __when engineers use it in practice__.
Different sketches answer different questions about massive datasets. Each sacrifices a sliver of precision for dramatic gains in memory efficiency, speed, or both. Think of them as a __toolbox for reasoning about data streams__ that are too large, too fast, or too expensive to handle exactly.



## Cardinality Sketches: Counting Unique Things
The question: _How many unique elements exist in a dataset?_
 - unique website visitors
 - distinct search queries
 - active hosts in a monitoring system
__The naive solution__ stores every element in a set. Works at small scale. At large scale? It becomes prohibitively expensive (e.g., hundreds of millions of IDs → gigabytes of memory).

__Cardinality sketches__ estimate distinct counts without storing elements.

## HyperLogLog (HLL)
HLL is the most widely deployed cardinality sketch. Here’s how it works:

1. Hash each element.
2. Look for long runs of leading zeros in the hash.
3. Rare long runs imply many distinct items were observed.
__Key insight__: Instead of storing the dataset, __HLL__ stores a _tiny statistical fingerprint_ of it.

### Accuracy trade-offs:
 - Accuracy depends on __registers__ (a.k.a. “buckets”).
 - More registers = higher precision (but more memory).
 - Each register uses just __6 bits__.
 - _Typical config_: 16,384 registers → __0.8% error__ in __~12 KB__ of memory.

As the plot shows, error drops sharply as you move from a few hundred buckets to a few thousand, eventually hitting diminishing returns where more memory barely moves the needle.

### Why it beats the naive approach:

|Approach             | Memory (100M IDs) | Error   | Use Case
|---------------------|-------------------:|---------|------------------------------
Exact (hash set)     | ~800 MB           | 0%      | Small-scale analytics
HLL                  | ~12 KB            | ~0.8%   | Massive-scale systems

HLL is __70,000× more memory-efficient__ than exact counting. This is why it’s embedded in:
 - Databases (Redis, BigQuery, Redshift, ClickHouse)
 - Stream processors (Flink, Spark)
 - Observability tools (VictoriaMetrics, TimescaleDB)
 - Platforms (Facebook, YouTube, Google, Cloudflare) for counting unique visitors, ad reach, or security events.

 When to use HLL: _When you need fast, compact distinct counts for massive datasets, and a ~1% error is acceptable._

 ## CPC (Compressed Probabilistic Counting)

 CPC (from Apache DataSketches) solves the same problem as HLL but with a __more space-efficient internal structure__. It often delivers __better accuracy for the same memory__ — especially at smaller sizes.

 When to use CPC: _When you need the most memory-efficient distinct-count sketch possible (e.g., in resource-constrained environments)._

Algorithm | Memory | CPU / Op | Accuracy | Notes
-- | -- | -- | -- | --
Linear Counting | $O(N)$ bits | Very Fast | High | Best for small sets; memory scales linearly.
LogLog | $O(\log(\log N))$ | Fast | $\approx 1.30 / \sqrt{m}$ | Legacy; bit-pattern matching is cheap.
HyperLogLog | ~1.5 KB ($10^9$ items) | Fast | $\approx 1.04 / \sqrt{m}$ | Industry standard; hashing is the main cost.
HLL++ | Variable | Medium | High | Slower than HLL due to sparse/dense logic.
Theta Sketch | Fixed ($O(k)$ entries) | Medium | Configurable | Heavier; maintains a sample set for intersections.
CPC Sketch | Lowest | Slow | Best per-bit | High CPU cost due to entropy encoding.

__Some Key Takeaways:__

* **HLL** is the go-to for simple counts due to its tiny footprint.
* **Theta** is necessary if you need to calculate "User Overlap" (Intersections).
* **HLL++** is preferred if you need accuracy across both very small and very large datasets.

## Frequency Sketches: Finding Heavy Hitters

__The question:__ Which items appear most often?
 - Trending search terms
 - Popular videos
 - Hot database keys
The __naive solution__ maintains a counter per key. Fails at scale (millions of keys) or high speed.

## Count-Min Sketch
 - Uses a small grid of counters (width × depth).
 - Each item is hashed to increment one counter per row.
 - To estimate frequency, take the minimum value across rows (collisions only inflate counts; min mitigates this).

Trade-offs:
 - __Wider grid__ → smaller error magnitude.
 - __Deeper grid__ → lower chance of bad estimates.

Why it beats naive counting:
 - Memory stays __fixed__ (e.g., 10M URLs tracked in KBs, not GBs).
 - Ideal for streaming systems, telemetry, and network monitoring.

 When to use:
    _For approximate counts across a huge key space and for basic frequency estimation where overcounting is acceptable (e.g., rate limiting)._

## SpaceSaving & Misra-Gries

These focus on __top-K items__ (e.g., “top 1,000 most frequent keys”), not all counts. They:
 - Maintain a small set of candidate heavy hitters.
 - Replace low-value candidates as the stream evolves.
 - Work best when you care about __dominant items__, not the long tail.


 When to use:
    _if you need a simple, deterministic way to ensure you don't miss any items above a certain frequency threshold._


    ### Frequency Data Sketches (Point Queries & Top-K)

| Algorithm | Memory | CPU / Op | Accuracy | Notes |
| --- | --- | --- | --- | --- |
| **Count-Min Sketch** | $O(\frac{1}{\epsilon} \log \frac{1}{\delta})$ | Very Fast | Probabilistic (Overestimates) | The standard for frequency; easy to implement and merge. |
| **Count-Sketch** | Higher than Count-Min | Fast | Unbiased (Lower Variance) | Uses $\pm 1$ hashing; better error distribution but slightly more CPU. |
| **Space-Saving** | $O(\frac{1}{\epsilon})$ | Medium | High for "Heavy Hitters" | Deterministic; maintains a "Stream Summary" of top elements. |
| **Misra-Gries** | $O(K)$ | Fast | High for Top-$K$ | Classic algorithm; finds elements with frequency $> N/(K+1)$. |
| **HeavyKeeper** | Low | Fast | Exceptional for Top-$K$ | Uses "decay" strategy to evict small items; state-of-the-art for Zipfian data. |
| **SketchLearn** | Variable | Slow | High (ML-based) | Uses automated modeling to correct sketch bias; higher overhead. |

* **Use HeavyKeeper** if your goal is strictly finding the **Top-K** most frequent items with the highest precision.


## Quantile Sketches: Estimating Percentiles
__The question:__ _What does the distribution look like?_ (e.g., p95 latency, p99.9 response times)
Many systems need to understand __distributions__, not just counts. Examples include:
 - request latency
 - transaction sizes
 - response times
 - price movements
 - queue wait times

The exact approach is expensive. You must store the data and sort it, or maintain data structures that grow with the stream.

Quantile sketches solve this by keeping a compressed summary of the distribution.

## KLL Sketch
The __KLL__ (Karnin-Lang-Liberty) sketch is one of the most important modern quantile sketches.
 - Stores samples in a hierarchy of compact buffers.
 - Compacts buffers in a controlled way (sorts small buffers, promotes subsets upward).
 - Preserves percentile accuracy while using kilobytes (not GBs) of memory.

__Why it matters:__
KLL is attractive because it gives strong quantile accuracy with small memory and supports merge operations, which makes it practical in distributed systems.

You can compute partial sketches on many machines and merge them later into a single global view.

That property is essential in modern data processing pipelines.


__Why it beats the naïve approach__
Imagine storing __100 million latency values__ as 64-bit floats.
Just holding the raw values costs around __800 MB__ of memory before sorting. And every exact quantile computation becomes more expensive as the data grows.

A KLL sketch keeps only a tiny compressed summary, often measured in __kilobytes__ rather than hundreds of megabytes.

The result is that percentile estimation becomes cheap enough to run continuously inside telemetry systems, financial pipelines, and streaming applications.

## DDSketch

 - Uses logarithmic bucketing to guarantee relative error (e.g., “value is within ±5% of truth”).
 - Critical for long-tailed distributions (e.g., 200 ms vs. 2 s latency differences).

 ## REQ & t-Digest

 - REQ: Prioritizes accuracy in high-tail regions (e.g., p99.9).
 - t-Digest: Compact, tail-friendly structure popular in monitoring systems.

 __When to use:__

* **Use T-Digest** if you are monitoring SLAs and care deeply about the **99th percentile** (the "tail").
* **Use KLL** if you need a mathematically robust, **mergeable** sketch for big data frameworks like Apache Spark or Flink.
* **Use DDSketch** if you want a **guaranteed relative error** (e.g., "I'm always within 1% of the true value") across the entire range.

| Algorithm | Memory | Accuracy | Notes |
| --- | --- | --- | --- |
| **GK Array** | $O(\frac{1}{\epsilon} \log(\epsilon N))$ | Deterministic $\epsilon$-approx | The classic foundation. Provides a guaranteed error bound but can be memory-heavy as $N$ grows. |
| **KLL Sketch** | $O(\frac{1}{\epsilon})$ | Probabilistic $\epsilon$-approx | Near-optimal space complexity. Excellent for merging multiple sketches (map-reduce friendly). |
| **T-Digest** | $O(K)$ (clusters) | High at extremes | Exceptional for tail latencies (99th, 99.9th percentiles) by using "centroids" that get smaller at the edges. |
| **DDSketch** | $O(\frac{1}{\alpha} \log(\text{max}/\text{min}))$ | Relative Error | Maintains a fixed *relative* error (e.g., 1%) rather than a rank error. Great for monitoring systems. |
| **Moments Sketch** | Very Low ($O(k)$ moments) | Varies | Uses statistical moments (mean, variance, skew). Fast but can be less accurate for complex distributions. |
| **REQ Sketch** | $O(\frac{1}{\epsilon})$ | High at one edge | "Relative Error Quantiles." Specifically optimized for very high or very low rank accuracy (e.g., the "high-resolution" end of a distribution). |


## Membership Filters: Have We Seen This Before?

__The question:__ _Does this element exist?_ (e.g., "Has this transaction hash appeared?")
__The naive solution__ uses a full set/index. At scale, it spills to disk → slow lookups.

## Bloom Filter
 - Bit array + multiple hash functions.
 - No false negatives (if “no,” it’s definitive).
 - False positives (if “yes,” it’s “maybe”).
 - Memory vs. error rate:

```
8 bits/item → ~2% false positives
10 bits/item → ~0.8% (industry sweet spot)
15 bits/item → ~0.05%
```

__Why it beats naive sets:__
Imagine tracking __10 million 32-character IDs__
every single byte of every ID.

An exact hash set would consume __~500 MB — 1 GB__, scaling at O(n) — Storing every single byte of every ID.

A Bloom filter with about a 1% false positive rate can often do the job in only __12 MB__.

That makes it small enough to stay __L3__ cache-friendly, possibly __avoiding RAM access__ entirely, and fast enough to sit in front of databases, LSM trees, storage engines, or distributed services as a first-pass rejection filter.

## Cuckoo Filter
 - Stores fingerprints (not bits).
 - Supports deletion (Bloom filters don’t).
 - Use when the set evolves over time.

## XOR/Binary Fuse Filters
 - Modern alternatives with faster lookups (3 memory reads + XOR ops).
 - 2–3× faster than Bloom filters on modern hardware.

__When to use:__
Bloom: _General-purpose existence checks._
Cuckoo: _When deletion is needed._
XOR/Binary Fuse: _For maximum speed/compactness._


| Algorithm	| Deletions	|  Merges | Notes	|
|-----------|-----------|-------|:-------|
| Bloom Filter |	difficult |	yes - not dynamic | classic	|
| Cuckoo Filter | yes | yes |		modern	|
| XOR Filter | no |	no  |	modern	|
| Quotient Filter |		yes | yes |	SSD friendly |
| CQF	|	yes | yes	|	high performance	|
| Binary Fuse Filter| no|	no  | extremely compact modern	|
| Ribbon Filter	|	 no|	no  | space efficient new design	|


