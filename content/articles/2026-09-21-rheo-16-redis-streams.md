---
title: "Rheo on Redis Streams: Portable Sequence, Native PEL"
description: "v0.8 asked whether the abstractions could describe Redis without pretending Redis is a deliveries table. v0.9 answers in code."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - Redis
draft: false
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 16 of [Rheo](https://thanos.github.io/series/rheo/). v0.8 asked whether the abstractions could describe Redis without pretending Redis is a deliveries table. v0.9 answers in code.

This is the narrative companion to ADR 026 and the Redis guide. Part 15 set up the question. This article records what shipped.

## The exit test, answered

Which core modules changed their *meaning* for Redis?

**None.** `Rheo.Consumer`, `Rheo.Event`, `Rheo.Query`, partition order, and the at-least-once / fencing invariants are the same as in v0.8.

What landed:

- optional `{:redix, "~> 1.5"}` and guarded `Rheo.Backend.Redis*` modules
- fence hashes plus Redis Streams consumer groups
- ADR 025 wakeup (`wait/2` + reader Task); polling still the fallback
- docs, Livebook backends section, conformance tagged `:redis`

If you already write handlers against ETS or Mongo, pointing the same handler at Redis is a supervision-tree change, not a rewrite.

## Model C on a real PEL

Redis orders entries with ids like `1700000000000-0`. Rheo orders with a portable integer `sequence` per partition. v0.9 keeps both (ADR 021):

| Rheo | Redis |
|---|---|
| `event.sequence` | Counter + ZSET index per partition |
| `lease.receipt` | Stream entry id |
| `lease.lease_id` | Fence hash field (Rheo fencing token) |
| `fetch` | `XREADGROUP` + reclaim via `XPENDING` / `XCLAIM` |
| `ack` | Fence check, then `XACK` |

```text
worker A fetches → lease L1, receipt 1700-0
worker A stalls past lease_ms
worker B fetches (reclaim) → lease L2, same receipt 1700-0
worker A acks L1 → stale_lease, no XACK
worker B acks L2 → ok, XACK
```

`XACK` alone is not fencing. Anyone who can talk to Redis can XACK an entry they no longer own if the library treats the entry id as sufficient authority. The adapter stores the current `lease_id` in a per-entry fence hash and refuses settle when the caller’s token is stale. That is the native-stream double from 0.8, now against Redis 6.2+.

## Mechanisms without fake guarantees

Capabilities declare what Redis actually provides:

- `native_consumer_groups`, `native_pending_list`, `native_reclaim`, `blocking_reads`, `native_group_lag`
- `secondary_indexes: false` — `query` walks stream ranges and filters in the adapter. Do not pretend RediSearch is on.

Guarantees (`durable`, `distributed`, `partitions`, `contiguous_frontier`, `replay`) stay honest. Conformance gates optional cases on those flags. It never skips fencing.

This is the part people want to fudge in a README. “We have Redis, so search is fine.” Search is *possible*. It is not indexed. Say that, then let the caller pick Postgres when investigation is the product.

## Wakeup without blocking the Group

A Redix connection that runs `XREAD … BLOCK` cannot also serve appends and acks on the same TCP session. v0.9 starts **two** connections per instance: the handle for commands, and a `….Waiter` used only by `wait/2`.

The Group and Producer keep their poll timers. A reader Task may send an early `:fetch` hint (ADR 025). Lost wakeups only cost latency. Correctness never depends on the hint arriving.

`:pool_size` is not supported yet. One command connection plus one waiter is enough to prove the contract. Scale out with more BEAM nodes sharing one Redis group, not with a silent pool inside the adapter.

## What you write

```elixir
children = [
  {Rheo,
   name: MyRheo,
   backend:
     {Rheo.Backend.Redis,
      name: MyRheo.Redis,
      url: System.get_env("RHEO_REDIS_URL", "redis://localhost:6379")}},
  {MyApp.RiskConsumer, rheo: MyRheo, concurrency: 8, max_demand: 100}
]
```

Handlers still return `:ack | {:retry, reason} | {:reject, reason}`. Broadway still uses `Rheo.Producer` + `transformer: {Rheo.Broadway, :transform, []}`. Receipts look different (`"1700-0"` instead of equalling `lease_id`). Handlers must not interpret them.

## How we know it works

- Shared backend contract suite tagged `:redis`
- Fencing and multi-instance Redis tests
- Property checks for contiguous sequences, frontiers, and stale tokens on Redis
- Broadway / Producer smoke against Redis (receipts through the acknowledger)
- `mix core.check` — Redis modules absent without Redix

## What v0.9 deliberately skips

- Redis Cluster multi-slot topology
- RediSearch as the query engine
- Lua scripts for append/ack (fence hashes + multi-command settle are enough for the fencing exercise)
- Redix connection pools
- Treating ops / LiveDashboard as Redis-specific — the inspect API is portable

Skipping is a feature. Each of those items is a way to smuggle a new abstraction through a backend-shaped door. The freeze in Part 17 only works if Redis did not force a rewrite.

## Takeaway

v0.8 fixed the abstractions so a native stream backend would not force another core rewrite. v0.9 is that backend. Portable sequence, native PEL, fenced settle, optional dependency — and the same Consumer API you already have.

Several BEAM nodes, one Redis group, one handler module. That is the multi-node story for shops that already run Redis and do not want to give Rheo their primary Postgres.

**Read next:** [Freezing Rheo Before 1.0](https://thanos.github.io/articles/2026-09-21-rheo-17-freezing-rheo-before-1-0/)

*Docs: [Redis guide](https://rheo.hexdocs.pm/redis.html) · [ADR 026](https://github.com/thanos/rheo/blob/main/docs/adr/026-redis-streams-backend.html) · [0.8 → 0.9](https://hexdocs.pm/rheo/0-8-to-0-9.html)*
