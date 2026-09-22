---
title: "One Consumer API, PostgreSQL and SQLite Underneath"
description: "v0.6 adds Ecto. The handler does not change. The host keeps the Repo."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - PostgreSQL
  - SQLite
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 13 of [Rheo](https://thanos.github.io/series/rheo/). Rheo’s public surface — `Rheo.Consumer`, leases, ACK, query, replay, lag — does not change when you switch backends. That sentence is cheap until a second durable backend exists. ETS proved the contract in memory. v0.6 has to prove it on SQL.

`Rheo.Backend.Ecto` sits on a host-owned `Ecto.Repo`. PostgreSQL or SQLite. Same OTP tree.

```elixir
children = [
  MyApp.Repo,
  {Rheo, name: MyRheo, backend: {Rheo.Backend.Ecto, repo: MyApp.Repo}},
  {MyApp.RiskConsumer, rheo: MyRheo, concurrency: 8, max_demand: 100}
]
```

Handlers still return `:ack`, `{:retry, reason}`, or `{:reject, reason}`. Partitions, the contiguous frontier, and `Rheo.lag/3` behave as in v0.5. Only the durable store changes.

## Host owns the Repo

Rheo never starts the connection pool. You already have opinions about pool size, timeouts, sandboxing in tests, and where migrations run in a release. A library that starts its own `Repo` is a library that fights you.

Schema comes from either:

```bash
mix rheo.ecto.gen_migration --repo MyApp.Repo
mix ecto.migrate
```

or `Rheo.ensure_indexes(rheo: MyRheo)` on boot, which creates the `rheo_*` tables idempotently. Prefer the migration in production so it runs once under your release’s migrate step. Pass `prefix: "rheo"` if you want the tables in their own schema. Pass `notify: true` on PostgreSQL for a `NOTIFY rheo_events` wakeup hint.

## PostgreSQL vs SQLite

| Concern | PostgreSQL | SQLite |
|---|---|---|
| Multi-node | Shared DB; `distributed: true` | Single-writer; `distributed: false` |
| Claim | `FOR UPDATE SKIP LOCKED` | Transactional select + update |
| Payload columns | `jsonb` | JSON text |
| Wakeup hint | Optional `notify: true` | Not available |

Use PostgreSQL when more than one BEAM node competes for the same group. `SKIP LOCKED` is the claim primitive; Rheo puts fencing tokens on top so a stale ACK still fails even if the row lock already moved on.

Use SQLite for durable local demos, tests, and single-node apps that should survive a restart without Docker. Same API. Honest capability flags.

On PostgreSQL, `metadata` and `payload` as `jsonb` means the event log stays queryable in plain SQL. That matters. Rheo.query is portable; `SELECT payload->>'currency' FROM rheo_events` is the escape hatch you actually wanted from a SQL backend.

## What “Ecto” does not mean

Mongo stays on `Rheo.Backend.Mongo`. Ecto here means **SQL**, not `mongodb_ecto`. One adapter, two dialects (Postgres and SQLite), host-owned repo. If you fold Mongo into Ecto you inherit a lowest-common-denominator schema and lose the Mongo indexes part 6 cared about.

## What stays true on SQL

- At-least-once delivery and `lease_id` fencing
- Immutable events; consumption never deletes history
- Ordering **within** a partition only
- Contiguous ACK frontier (holes block lag)
- Replay and reset touch deliveries, not event rows

The conformance suite runs against SQLite always and PostgreSQL when tagged. If a frontier case passes on ETS and fails on Postgres, the SQL dialect’s claim transaction is wrong — not the Group.

## Why this backend changed the adoption story

ETS is a tutorial. Mongo is a commitment some Elixir shops do not want. Postgres is already in the room with Oban, your accounts table, and your backups. Rheo-on-Ecto is the version of the pitch that does not start with “first, install another database.”

SQLite is the version that does not start with “first, install a database.”

Same handler. Same leases. Different durability story.

**Read next:** [Rheo Is Not Broadway — It Feeds Broadway](https://thanos.github.io/articles/2026-09-21-rheo-14-rheo-is-not-broadway/)

*Docs: [Using Ecto](https://rheo.hexdocs.pm/using-ecto.html) · [ADR 017](https://github.com/thanos/rheo/blob/main/docs/adr/017-ecto-backend.md) · [0.5 → 0.6](https://hexdocs.pm/rheo/0-5-to-0-6.html)*
