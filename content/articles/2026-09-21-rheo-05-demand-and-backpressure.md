---
title: "Demand, Backpressure, and Database Consumers"
description: "If you fetch without a bound, a crash turns into a redelivery storm. I use max_demand for that."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - backpressure
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 5 of [Rheo](https://thanos.github.io/series/rheo/). The first version of every database consumer I have written looks like this:

```elixir
def loop(state) do
  {:ok, leases} = Rheo.fetch(stream, group, limit: 10_000, rheo: state.rheo)
  Enum.each(leases, &handle/1)
  loop(state)
end
```

It works in a demo. In production it does four things at once:

- holds thousands of leases that all expire together if the node GC pauses
- overloads handlers until every one of them times out
- turns a single crash into a thundering herd of redeliveries
- makes “lag” meaningless, because the store thinks the work is in flight when it is actually queued in your mailbox

Rheo’s answer is not clever. It is a bound.

```elixir
use Rheo.Consumer,
  stream: "market-events",
  group: "risk",
  max_demand: 10,
  concurrency: 4
```

`max_demand` is how many unsettled leases the Group will hold. `concurrency` is how many handler tasks may run at once. They are not the same number. Treating them as one knob is how you starve workers or drown the database.

## Two knobs, two resources

| Option | Resource it claims |
|---|---|
| `:max_demand` | Leases in the backend — rows locked, PEL entries, fencing tokens to renew |
| `:concurrency` | BEAM schedulers and whatever your handler touches (Repo, HTTP, CPU) |

If `concurrency` is 32 and `max_demand` is 8, twenty-four tasks sit idle. If `max_demand` is 500 and `concurrency` is 2, you are renting 498 leases so they can expire in unison when the two workers fall behind.

Start small. Raise `max_demand` when lag is real and handlers are keeping up. Raise `concurrency` when the handler is I/O-bound and the backend still has room.

## Idle poll, not an unbounded cursor

`Rheo.Group` does not open a cursor of leased work and hope. It fetches when it has spare demand, processes, settles, and polls again when idle. Default `poll_ms` is 200. Some backends can hint earlier — Postgres `NOTIFY`, Redis blocking read on a waiter connection — but a lost wakeup only costs a poll interval. The Group never depends on wakeup for correctness.

This is ADR 007. GenStage is not used inside the Group. The Group is a bounded fetch loop with a task pool. Since v0.7 there is also `Rheo.Producer`, a real GenStage producer that applies the same `max_demand` bound to downstream demand so Broadway can consume the group. Part 14 is that seam. The bound is the same idea in two process shapes.

## Renewal is part of demand

A lease you have fetched is not free. Something has to renew it at about half `lease_ms`, or the backend will redeliver it to someone else while your handler is still running.

The Group does that. So does `Rheo.Producer`. They share `Rheo.Inflight`: the set of outstanding leases, the capacity check, `renew_all/2`. A renewal that comes back `:stale_lease` drops the entry. You lost the race. Do not nack. The other worker now owns the event.

This is why `max_demand` is a lease bound and not a mailbox bound. Every inflight slot is a timer you have agreed to keep alive.

## Backoff when the store is unhappy

Fetch can fail. If you retry immediately you turn a Mongo blip into a busy loop. `Rheo.Backoff` is the shared schedule for that. Group and Producer both use it. The handler never sees it. The handler only sees events.

## Drain without blocking the coordinator

Shutting down a consumer is the other half of backpressure. A drain that freezes the Group until every handler finishes also freezes renewals, which expires the leases you were trying to finish.

Rheo drain is non-blocking on the coordinator. The caller is answered when inflight work settles or the timeout fires. Renewals keep running during the wait. You either settle cleanly or you let expiry do the job part 3 already defined.

This is not Kafka-style fetch-min-bytes. This is not Broadway rate limiting — Broadway can add that on top when you use `Rheo.Producer`. This is the minimum bound that stops a database consumer from becoming a denial-of-service against its own store.

If you take one number into the next article, take `max_demand`. It is the size of the promise you have made to the log.

**Read next:** [MongoDB as a Searchable Event Log](https://thanos.github.io/articles/2026-09-21-rheo-06-mongodb-searchable-event-log/)

*Docs: [ADR 007](https://github.com/thanos/rheo/blob/main/docs/adr/007-demand-and-backpressure.md) · [Configuration](https://rheo.hexdocs.pm/configuration.html)*
