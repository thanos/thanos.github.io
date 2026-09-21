---
title: "Freezing Rheo Before 1.0"
description: "v0.12 draws the line hosts and adapter authors may depend on before SemVer starts counting."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - SemVer
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 17 of [Rheo](https://thanos.github.io/series/rheo/). v0.12 draws the line hosts and adapter authors may depend on before SemVer starts counting.

v0.8 corrected the abstractions. v0.9–v0.11 filled Redis Streams, an ops inspect surface, and a Mnesia backend. v0.12 does not add a backend. It writes down what will require a major version to change.

A freeze candidate is not a promise that nothing will ever change. It is a promise about *what* change costs.

## What “API freeze candidate” means

1. **Consumer / Event / Query / Backend callback meanings** stay as documented on HexDocs for this release.
2. **Optional ops** — Mix inspect, LiveDashboard, Telemetry.Metrics — may still move without a Consumer break.
3. **Internal modules** (`Names`, `Instance`, table engine, driver clients) are not part of the published surface. Do not couple to them.

After **1.0.0**, changing a frozen module’s public contract requires a major version.

## The published surface

HexDocs groups modules into Facade, Consume, Values, Backend, Runtime, and Ops. That list *is* the freeze (ADR 029). If a module is missing from HexDocs, treat it as internal even if it compiles in your project.

```text
Rheo  ──► Backend (ETS | Mnesia | Mongo | Ecto | Redis)
  ▲
  │
Consumer / Group   or   Producer / Broadway
```

### Facade

`Rheo` — create streams and groups, append, read and query, fetch and settle, replay and reset, lag, ops inspect (`list_streams`, `list_groups`, `dead_letters`, `group_info`), `ping`, `ensure_indexes`. Pass `:rheo` for a named instance.

### Consume

`Rheo.Consumer` is a child spec for a local `Rheo.Group`. `Rheo.Producer` is the GenStage door. `Rheo.Broadway` is wiring. One Group or Producer per `{rheo, stream, group}` per node.

### Values

`Event`, `Event.Lineage`, `Lease`, `Query`, `Page`, `Lag`, `DeadLetter`, `GroupInfo`, `Settle`, `Partition`. Field meanings are the contract. Extra fields later are additive. Reusing a field for a new idea is a major.

### Backend authors

Implement `Rheo.Backend`. Declare `Rheo.Backend.Capabilities`. Optional ops callbacks may return `{:error, :unsupported}`. Optional wakeup via `Rheo.Backend.Wakeup`. Shipping adapters: ETS, Mnesia, Mongo, Ecto, Redis.

### Runtime, public on purpose

`Inflight`, `Backoff`, `Clock` / `Clock.Frozen` / `Clock.System`, `Id`, `Telemetry`. These exist so Group and Producer stay twins, and so tests can freeze time. They are not an invitation to reimplement Group in your app.

## What will not change after 1.0 without a major bump

- `Rheo.Consumer` handler outcomes (`:ack` / `{:retry, _}` / `{:reject, _}`) and read-only context
- `%Rheo.Event{}` / `%Rheo.Lease{}` / `%Rheo.Query{}` field meanings
- `Rheo.Backend` required callbacks and the fencing / settle vocabulary
- At-least-once delivery with lease fencing (not exactly-once)
- One local Group owner per `{rheo, stream, group}` per node

## What stays deliberately flexible

- Shipping adapter internals: indexes, claim algorithms, codecs
- Optional ops pages and Mix tasks
- Capability *mechanisms* (how a backend claims) as long as *guarantees* hold
- Multi-node Mnesia and a first-class Flow package — deferred, not frozen

Mnesia in v0.11 is single-node `disc_copies` with `distributed: false`. That is an honest backend, not a cluster story hiding in a freeze.

## Error atoms are part of the surface

Portable reasons returned by `Rheo` and backends:

`:stream_not_found`, `:group_not_found`, `:already_exists`, `:stale_lease`, `:receipt_mismatch`, `:cursor_not_found`, `:already_draining`, `:unsupported`, `:backend_unavailable`, `:confirm_required`, `{:ambiguous, cause}`, `{:failed, cause}`.

`Rheo.Settle.classify/1` maps settle errors for Group and Producer policy. If you parse driver exceptions instead of these atoms, you coupled to an adapter and the freeze will not protect you.

## How to upgrade into the freeze

From 0.11.1, no code changes are required if you already use the public APIs. See [0.11.1 → 0.12](https://hexdocs.pm/rheo/0-11-1-to-0-12.html). From earlier minors, walk the migration guides in order. They exist because the project broke itself on purpose while it still could (Parts 9 and 15).

## The series, closed

Seventeen articles, one claim:

**Put consumer groups in front of a database you already run. Keep the events. Fence the ACKs. Bound the demand. Make the backend prove the contract twice. Break the wrong abstraction before 1.0. Then stop.**

Rheo is an OTP library, not a broker. Delivery is at-least-once. Order is per partition. Consumption never deletes the log. Search and replay are first-class because of that last sentence.

If you build a backend, the conformance suite is the spec. If you build a consumer, `handle_event/2` returning `:ack | {:retry, _} | {:reject, _}` is the spec. Everything else is mechanism.

Install it:

```elixir
def deps do
  [{:rheo, "~> 0.12.0"}]
end
```

Point it at ETS this afternoon. Point it at Postgres before you buy a Kafka cluster for a question Postgres can already answer.

*Docs: [ADR 029](https://github.com/thanos/rheo/blob/main/docs/adr/029-api-freeze-candidate.md) · [Public API](https://rheo.hexdocs.pm/public-api.html) · [README](https://rheo.hexdocs.pm/readme.html) · [github.com/thanos/rheo](https://github.com/thanos/rheo)*

**Start of series:** [Why Put Consumer Groups in Front of a Database?](https://thanos.github.io/articles/2026-09-21-rheo-01-why-consumer-groups-on-a-database/)
