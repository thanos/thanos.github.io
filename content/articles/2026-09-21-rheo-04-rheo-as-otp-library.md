---
title: "Building Rheo as an Elixir/OTP Library"
description: "Rheo is not a server you run. It is a child spec you supervise. The database keeps the truth."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - supervision
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 4 of [Rheo](https://thanos.github.io/series/rheo/). I did not want to operate another cluster. I wanted a child spec.

Rheo is not a server. There is no Rheo cluster, no Rheo control plane, and no second settle path that lives in a dashboard. You add a dependency, you put a child in your supervision tree, and you append events.

```elixir
children = [
  {Rheo, name: MyRheo, backend: {Rheo.Backend.Mongo, url: "mongodb://localhost:27017/rheo"}},
  {MyApp.RiskConsumer, rheo: MyRheo, concurrency: 8, max_demand: 100}
]

Supervisor.start_link(children, strategy: :one_for_one)
```

That is the happy-path deployment. Compare it to “provision ZooKeeper, then brokers, then a schema registry, then a consumer app.” Kafka will still win on throughput. I am talking about operational surface.

## What belongs in processes

OTP is extremely good at some things and a trap for others.

| Process | Owns |
|---|---|
| Backend handle | Connections, topology, driver process, ETS owner |
| `Rheo.Instance` | Module + handle for a named Rheo |
| `Rheo.Group` | Poll loop, demand bound, worker tasks, renewals, drain |
| `Rheo.Producer` | The same fetch/renew job, shaped as GenStage |
| Handler tasks | One `handle_event/2` call each |

The host supervisor owns the Group. Under the Rheo instance sit the backend handle, the instance process, a `Task.Supervisor` for handler work, and a `Rheo.GroupSupervisor` only for groups started dynamically.

This is the split Oban got right. Oban does not keep job correctness in a GenServer. It keeps jobs in Postgres and uses OTP for execution. Rheo does the same for consumer groups.

## What does not belong in processes

Consumer-group truth: cursors, leases, ACKs, frontiers, dead letters.

Those records live in the backend so a process restart does not lose correctness. If the Group dies mid-handler, the lease expires and another worker fetches it. If the whole node dies, a Group on another node — against Postgres or Redis — claims the same durable group. ETS, SQLite, and single-node Mnesia cannot do that multi-node trick, and they say so (`distributed: false`).

The 0.1 design casually treated “the consumer process” and “the group” as the same thing. That felt natural and painted me into a corner. Part 9 is how I got out of it. A local `Rheo.Group` is an OTP lifecycle boundary. The backend is the authority.

## Embed, don’t daemonize

ADR 006 is short: Rheo is an embedded OTP library. That has consequences people like until they don’t.

- You do not operate Rheo. You operate Mongo, or Postgres, or Redis, or nothing (ETS).
- You do not get a cross-language client. The consumer is a BEAM process.
- You do get supervision, telemetry, LiveDashboard, and a programming model that looks like the rest of your application.

If you need many languages on one bus, you wanted a broker. If you need many Elixir services on one log, you wanted a shared store and this library.

## Named instances, opaque handles

A single global topology was convenient in 0.1 and hostile the moment I wanted two Rheo instances in one VM — tests next to an app, ETS next to Mongo.

Today you pass `rheo: MyRheo` into every call. The instance process holds an opaque `Rheo.Backend.handle`. Callers never pass table refs or driver pids through `Rheo.fetch/3`. Backends start whatever `child_spec/1` they need: a Mongo topology, an ETS owner, a pair of Redix connections, nothing extra for Ecto beyond the repo *you* already supervise.

```elixir
children = [
  MyApp.Repo,
  {Rheo, name: MyRheo, backend: {Rheo.Backend.Ecto, repo: MyApp.Repo}},
  {MyApp.RiskConsumer, rheo: MyRheo}
]
```

Rheo never starts the Ecto pool. Host-owned resources stay host-owned. That is how you avoid a library fighting your release for the database.

## Optional dependencies, one package

Core Rheo depends on `telemetry` and `jason`. ETS works out of the box. Mnesia is OTP. Everything else is optional:

| Dependency | Compiles |
|---|---|
| `mongodb_driver` | `Rheo.Backend.Mongo` |
| `redix` | `Rheo.Backend.Redis` |
| `ecto_sql` + `postgrex` or `ecto_sqlite3` | `Rheo.Backend.Ecto` |
| `gen_stage` | `Rheo.Producer` |
| `broadway` | `Rheo.Broadway` and its acknowledger |

`mix core.check` builds a project on Rheo with none of the Hex optionals. A library that hard-depends on every adapter makes ETS-only tests download Broadway. That is how a small library stops being small.

## Try it without a cluster

```elixir
children = [
  {Rheo, name: MyRheo, backend: Rheo.Backend.ETS},
  {MyApp.RiskConsumer, rheo: MyRheo, concurrency: 8, max_demand: 100}
]
```

No Docker. No port. Data dies with the owner process. That is documented, not hidden. It is also the fastest way to learn the API you will use unchanged against Postgres next week.

Next: how that Group refuses to lease the entire table at once.

**Read next:** [Demand, Backpressure, and Database Consumers](https://thanos.github.io/articles/2026-09-21-rheo-05-demand-and-backpressure/)

*Docs: [Architecture](https://rheo.hexdocs.pm/architecture.html) · [ADR 006](https://github.com/thanos/rheo/blob/main/docs/adr/006-rheo-as-embedded-otp-library.md)*
