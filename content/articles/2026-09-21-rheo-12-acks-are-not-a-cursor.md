---
title: "ACKs Are Not a Cursor"
description: "If progress is “max acked sequence,” lag lies and replay skips holes."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - ACK
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 12 of [Rheo](https://thanos.github.io/series/rheo/). If progress is “max acked sequence,” lag lies and replay skips holes.

At-least-once delivery means you can ACK event 1003 while 1002 is still inflight. That is not a corner case. That is concurrency.

If the system treats “progress” as the highest sequence anyone has acknowledged, two disasters follow:

- **Lag lies.** 1003 is done, so we report we are “at 1003” while 1002 is on the floor.
- **Replay skips holes.** “Start after the cursor” starts after 1003. Event 1002 becomes a ghost. It will not be in the next projection and it will not be in the incident review.

Rheo v0.5 keeps two ideas separate on purpose.

## Materialization cursor vs committed frontier

| Concept | Meaning |
|---|---|
| **Materialization cursor** | How far the group has **offered** events into deliveries |
| **Committed frontier** | Highest `F` such that every sequence through `F` is terminal (`acked` or `rejected`) |

```text
1001 ACK
1002 inflight
1003 ACK
1004 ACK

frontier = 1001   # blocked by 1002
```

When 1002 ACKs — or is dead-lettered — the frontier walks forward to 1004 in one step. Reject is terminal. Retry is not. An expired lease is not. Inflight is a hole.

This is the contiguous ACK frontier. It is more annoying to explain than a cursor. It is also the only progress number that means “you can start a replay after this and not lose a hole.”

## Partitions, because order is not global

Sequences are **per partition**. Key routing uses `:erlang.phash2/2`:

```elixir
Rheo.create_stream("market-events", partition_count: 4)

Rheo.append("market-events", %{
  type: "curve_update",
  key: "EUR-EURIBOR-6M",
  price: 2.9
})
# partition = phash2("EUR-EURIBOR-6M", 4)
# sequence is local to that partition
```

There is **no global order** across partitions. Two keys can ACK “sequence 5” on the same stream and those fives are unrelated. A Group may own a static set of partitions:

```elixir
{MyApp.RiskConsumer, partitions: [0, 1], concurrency: 4}
```

Automatic rebalancing is deferred. `:partitions` is ownership groundwork, not Kafka consumer-group protocol. If you need another node to take partition 2, you start a consumer with `partitions: [2]` and you do not also run `:all` on the first node against the same group unless you want competing consumers on those partitions.

## Lag that can be audited

```elixir
{:ok, lag} = Rheo.lag("market-events", "risk")

lag.partitions[0]
# => %{frontier: 10, high_watermark: 40, lag: 30}

lag.lag
# => sum of per-partition lags
```

High watermark minus contiguous frontier. Not “how many rows are unacked,” which double-counts holes and inflight depending on who asks. When LiveDashboard shows lag 13 on `orders-demo / billing`, that is this number.

If you need the hole itself, look at inflight and dead letters. Lag is the distance. The frontier is the claim.

## Replay stays partition-aware

```elixir
Rheo.replay("market-events", "risk", from_sequence: 1000, partition: 2)
Rheo.reset_group("market-events", "risk", confirm: true, partition: 2)
```

A global `from_sequence` without a partition is a lower bound you apply carefully. After 0.5, prefer being explicit. The page cursor from `query_page` is already a map of partition to position. Follow that shape.

## What this costs you

You cannot say “we are caught up” because someone ACKed a recent event. You say it when every partition’s frontier equals its high watermark and inflight is zero.

You cannot implement a backend that stores only a single integer cursor and still pass the conformance suite’s frontier cases.

You can, finally, explain a stuck consumer: the frontier is blocked on a specific sequence. Find that delivery. It is leased, retried out, or rejected. That is an operable system.

**Read next:** [One Consumer API, PostgreSQL and SQLite Underneath](https://thanos.github.io/articles/2026-09-21-rheo-13-one-api-postgres-sqlite/)

*Docs: [Partitions and lag](https://rheo.hexdocs.pm/partitions-and-lag.html) · [ADR 016](https://github.com/thanos/rheo/blob/main/docs/adr/016-partitions-and-ack-frontier.md)*
