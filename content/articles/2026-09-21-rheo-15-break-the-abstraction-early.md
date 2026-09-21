---
title: "Breaking Rheo Before Anyone Depends on the Wrong Abstraction"
description: "v0.8 adds no backend. It corrects the meanings of the ones you already have."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - architecture
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 15 of [Rheo](https://thanos.github.io/series/rheo/). v0.8 adds no backend. It corrects the meanings of the ones you already have.

v0.1 through v0.7 were discovery releases. They proved a consumer group can live over a searchable database: an immutable log, leases with fencing tokens, retries and dead-letters, partitions with a contiguous ACK frontier, replay without copying events, ETS, MongoDB, PostgreSQL and SQLite, and a GenStage producer that feeds Broadway.

v0.8 adds no backend. It is the release where the abstractions are corrected while almost nobody depends on them.

That sounds like churn. It is the opposite of churn. It is paying the break *once*, before SemVer makes each correction a major version with a compatibility layer you will hate.

## Why more backends expose false abstractions

The first backend defines the vocabulary. Rheo’s vocabulary came from MongoDB: a `deliveries` collection, a document per `{group, event}`, a compare-and-set on `lease_id`. ETS and Ecto fit that shape. Three backends passed the same conformance suite. The abstraction looked proven.

It was not. Three row-shaped stores agreeing with each other says nothing about a store that already implements consumer groups.

## Why Redis Streams is different

Redis Streams has `XGROUP`, `XREADGROUP`, `XPENDING`, `XACK`, and `XAUTOCLAIM`. The pending-entries list *is* the delivery table. The entry id *is* the claim identity. Reclaiming expired work is a server command.

A Redis backend that “materializes delivery documents” would be a second, slower consumer-group implementation running on top of a native one. That is the kind of adapter that looks done in a sprint and is wrong for the life of the project.

```text
Mongo / Ecto / ETS                 Redis Streams
append → events table              XADD → stream
fetch  → deliveries CAS            XREADGROUP / XAUTOCLAIM → PEL
lease_id on a row                  entry id + fence hash
```

Rheo must describe what a backend *guarantees*, not how it stores rows.

## Semantics versus mechanisms

The v0.8 backend contract keeps the same callbacks and changes their meaning from storage algorithm to promise:

- `fetch` claims fenced leases
- `ack` settles only when the token still matches
- `lag` reports a contiguous frontier

Capabilities split the same way. Guarantees such as `durable`, `partitions`, and `contiguous_frontier` gate conformance. Mechanisms such as `native_consumer_groups` or `blocking_reads` describe how the backend gets there. `at_least_once` and `lease_fencing` cannot be declared false.

If a new backend cannot offer partitions yet, it says so. It does not get to offer ACK without fencing.

## Logical sequence and native identity

Rheo orders events with an integer `sequence` per partition. Redis orders them with entry ids like `1700000000000-0`. Replacing the sequence with an opaque position would have made the frontier, lag, replay cursors, and every query backend-specific. Keeping only the sequence would have forced Redis to look up its own entries by a foreign key on every settle.

v0.8 keeps both. `event.sequence` stays the portable order. `lease.receipt` carries the backend’s claim identity (ADR 021). Settle callbacks fence on `lease_id` and, when set, on the receipt.

A test double shaped like a native stream runs the full conformance suite with exactly this layout — *before* Redis ships. That double is the point of 0.8. 0.9 is just the double coming true.

## One runtime, not two

`Rheo.Group` runs handler callbacks. `Rheo.Producer` satisfies GenStage demand. They are different processes with different contracts. By v0.7 they had grown two copies of lease renewal, fetch backoff, inflight tracking, and drain.

v0.8 moves the pure parts into `Rheo.Inflight` and `Rheo.Backoff` and leaves each process with its effects. Draining no longer blocks the coordinator: the caller is answered when inflight work settles. Renewals keep running. Part 5’s backpressure story becomes one module instead of two myths.

## Callback state under concurrency

v0.7 handlers returned `{:ack, new_state}` while `concurrency: 8` ran eight tasks against a snapshot of that state. Whichever task finished last won. The documentation said “use an Agent.” The API said “this is GenServer state.”

v0.8 removes the ambiguity. `handle_event(event, context)` receives a read-only map built once by `setup/1` and returns `:ack`, `{:retry, reason}`, or `{:reject, reason}`. State lives in processes the application owns.

The bridge process that started or joined a group is gone too. A consumer module is a child spec for `Rheo.Group`. The host supervisor owns it. A second consumer for the same `{rheo, stream, group}` fails to start.

## Settlement failures are explicit

A handler can succeed and the ACK can still fail. `Rheo.Settle` classifies the failure and the runtime acts on the class: lost lease dropped, definite failure nacked, unavailable or ambiguous left to expire because the ACK may already be durable. Telemetry carries the class, not the driver exception.

This is Part 3, promoted from “good advice” to “the runtime does it.”

## Dependencies in libraries

A library that hard-depends on `mongodb_driver`, `ecto_sql`, `gen_stage`, and `broadway` makes every ETS-only user download all of them. Every new backend makes it worse.

v0.8 makes each integration optional: the dependency is `optional: true` and the module is wrapped in a compile-time guard. A CI check builds a project on Rheo with none of the integrations to keep the guards honest (ADR 020).

## Why now

Rheo is pre-1.0 with a small user base. Each of these changes is a breaking change. Together they are one migration guide. After 1.0 the same corrections would take a major version each.

The executable definition of a Rheo backend is `test/support/backend_contract.ex`, grouped by guarantee: lifecycle, event log, queries, consumer groups, leases and fencing, retry and reject, replay, partitions and frontier. ETS, Mongo, SQLite, PostgreSQL, and the native-stream double run it.

If `Rheo.Backend.Redis` can ship in 0.9 without touching `Rheo.Consumer`, `Rheo.Group`, `Rheo.Event`, `Rheo.Query`, or the frontier arithmetic, the reset did its job.

Spoiler: it did.

**Read next:** [Rheo on Redis Streams: Portable Sequence, Native PEL](https://thanos.github.io/articles/2026-09-21-rheo-16-redis-streams/)

*Docs: [0.7 → 0.8](https://hexdocs.pm/rheo/0-7-to-0-8.html) · [ADR 019](https://github.com/thanos/rheo/blob/main/docs/adr/019-v0-8-architectural-reset.html)*
