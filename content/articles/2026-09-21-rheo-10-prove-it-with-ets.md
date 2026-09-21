---
title: "If Rheo Really Is Database-Agnostic, Prove It with ETS"
description: "An abstraction with one implementation is a hope. v0.3 made ETS the second witness."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - ETS
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 10 of [Rheo](https://thanos.github.io/series/rheo/). An abstraction with one implementation is a hope. v0.3 made ETS the second witness.

Rheo 0.2 cleaned the architecture: opaque backend handles, a local `Rheo.Group`, a portable `%Rheo.Query{}`. That is necessary and not sufficient. Until two stores implement the same public flows, the behaviour still models Mongo.

**v0.3.0** ships `Rheo.Backend.ETS` and a shared conformance suite so the contract is exercised twice.

## Why a second backend is the real test

Mongo shaped the first callbacks: collections, indexes, `find_one_and_update`. Those nouns leak. You start calling everything a document. You start assuming compare-and-set is a single round trip. You start treating connection topology as a given.

ETS cannot hide behind any of that. If ETS cannot implement create stream, append, fetch, renew, ACK, retry, reject, and query, then `Rheo.Backend` is a Mongo driver with extra steps.

ETS is deliberately weak as a store (`durable: false`). That is the point. If the *semantics* still hold in memory — fencing, immutable events, independent groups — the semantics belong to Rheo.

## Opaque handles vs topology

A Rheo instance starts whatever `child_spec/1` the backend returns.

- Mongo’s handle is a driver process name.
- ETS’s handle is an owner GenServer that owns per-instance tables.

Callers never pass table refs or Mongo URLs through `Rheo.fetch/3`. They pass `rheo: MyRheo`. The day that rule slips, every backend grows a special case and the facade is dead.

## Capabilities without forked correctness

`Rheo.Backend.capabilities/0` declares honest differences:

| Flag | Mongo | ETS |
|---|---|---|
| `durable` | true | false |
| `secondary_indexes` | true | false |
| `atomic_compare_and_set` | true | false |

Capabilities gate **optional** suites: replay, partitions, things a backend might not offer yet. They must not make lease fencing optional. Both backends must refuse a stale ACK. If a capability could turn off correctness, it is not a capability. It is an excuse.

Later revisions split capabilities into *guarantees* and *mechanisms* (Part 15). The 0.3 version already had the right instinct: declare what you are, do not fork the meaning of ACK.

## Conformance, not copy-paste

The BackendContract ExUnit template (`test/support/backend_contract.ex`) injects the same cases into:

- ETS contract tests (always on in CI)
- Mongo contract tests (`@tag :mongo`)

When a test fails on one backend only, you found an abstraction leak. That sentence is worth more than any diagram. The suite is the contract. The markdown ADRs are commentary.

Correctness cases are never skipped because a backend is “simple.” Only cases for undeclared *guarantees* are skipped. ETS does not get to skip stale-lease tests because it is in memory.

## Ownership and restart

ETS tables die with the owner process. Restarting the ETS child empties the log. Document that. Do not pretend ETS is a production durable backend. Do not hide it behind a retry that “usually” works if the owner did not crash.

ETS is for tests, Livebook, ephemeral apps, and proving the API. Mnesia later gives you an ETS-shaped *durable* single node. Postgres and Redis give you multi-node. The ladder only works if the first rung is honest.

## What 0.3 refused to weaken

- At-least-once delivery with fencing tokens
- Immutable events; mutable deliveries per group
- Portable query shape (`order_by`, not Mongo `:sort`)
- Consumption never deletes events

Everything that came next — search and replay (0.4), partitions and frontiers (0.5), Ecto (0.6), Broadway (0.7), the 0.8 reset, Redis (0.9), Mnesia, ops, the 1.0 freeze — builds on a contract two backends already satisfied.

If you are writing a backend today, start with ETS in the suite and stay there until fencing is boring.

**Read next:** [Search and Replay the Event History](https://thanos.github.io/articles/2026-09-21-rheo-11-search-and-replay/)

*Docs: [ETS guide](https://rheo.hexdocs.pm/ets.html) · [ADR 012](https://github.com/thanos/rheo/blob/main/docs/adr/012-backend-conformance-suite.md) · [ADR 014](https://github.com/thanos/rheo/blob/main/docs/adr/014-ets-backend.md)*
