---
title: "Why Rheo 0.2 Broke Its 0.1 API"
description: "0.1 proved the idea and also painted the architecture into a corner. I broke the API while I still could."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - API
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 9 of [Rheo](https://thanos.github.io/series/rheo/). Rheo 0.1 was a good demo that accidentally became an API. Durable consumer groups on MongoDB: immutable events, leases, ACK, competing consumers, a convenient `Rheo.Consumer` GenServer. That shape was good enough to ship. It was also sharp enough to lock in three mistakes:

- the consumer process *is* the group
- `concurrency` means something
- there is one topology, and it looks like Mongo

0.2 broke the API so later versions could add backends without carrying those as compatibility.

## Process topology is not durable truth

In 0.1, each consumer process polled the backend and ACKed inline. It felt like the consumer *was* the group. Crashes were handled by lease expiry — which is correct — but the OTP tree and the durable group were casually the same noun in the docs.

In 0.2, a local `Rheo.Group` is an OTP lifecycle boundary: demand, workers, renewals, drain. The backend remains the authority for leases and ACKs. Multiple nodes may run Groups for the same durable group; the store arbitrates.

That split is why the Consumer API changed from “I am a poll loop” to “I join a Group with a handler module.” The words are similar. The ownership is not.

If you have ever restarted a GenServer and been surprised that “the consumer group reset,” you have lived the 0.1 confusion. Progress was in the process because that was the only place 0.1 taught you to look, even though the documents were already in Mongo.

## Concurrency was a lie

The 0.1 README advertised `concurrency`. The GenServer processed leases sequentially.

Once you introduce real worker tasks, shared mutable handler state, renewals, and failed ACKs stop being theoretical. They need a coordinator. Group is that coordinator. Concurrency becomes “how many tasks,” demand becomes “how many leases,” and those numbers can finally disagree in public.

A documented option that does nothing is worse than a missing option. People size production around it.

## Handles beat global topology

`Application.get_env(:rheo, :topology)` made a second Rheo instance awkward. It also told every future backend it must look like Mongo’s process tree.

0.2 introduced an opaque `Rheo.Backend.handle` plus named `Rheo.Instance` processes. Callers pass `rheo: SomeName`. Backends start whatever child they need. ETS can own tables. Redis can own two connections. Ecto can own nothing and borrow your Repo.

This had to happen before the second backend, not after. An abstraction designed around one process name is not an abstraction.

## Queries should travel

A public `:sort` map is a Mongo document in disguise. It looks friendly in a README and becomes a migration tax the day Postgres arrives.

`%Rheo.Query{}` is small on purpose: order_by, limits, bounds, a few fields. Backends translate. Escape hatches can come later without teaching every application Mongo’s sort dialect.

Event decoding moved toward the backend for the same reason. The public event is a struct with a stable meaning. The document shape is an adapter detail.

## Break it while the user count is the author

Pre-1.0 is a privilege. I used it.

The broken surfaces were supervision opts, Consumer startup, query sort, and Event decoding. Each one would have been a major version after 1.0, plus a compatibility layer that existed only to protect accidents.

See the [0.1 → 0.2 migration](https://hexdocs.pm/rheo/0-1-to-0-2.html) if you are an archaeologist. If you are starting today, you already live in the 0.2 world: named instances, Group as runtime, portable query.

The next proof is harsher than a migration guide. If the contract is real, a second backend should satisfy it without looking like Mongo.

**Read next:** [If Rheo Really Is Database-Agnostic, Prove It with ETS](https://thanos.github.io/articles/2026-09-21-rheo-10-prove-it-with-ets/)

*Docs: [0.1 → 0.2](https://hexdocs.pm/rheo/0-1-to-0-2.html) · [ADR 010](https://github.com/thanos/rheo/blob/main/docs/adr/010-backend-handle-and-instance-model.md)*
