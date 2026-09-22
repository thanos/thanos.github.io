---
title: "What Is a Consumer Group?"
description: "A stream is the log. A group is independent progress on that log. Workers in a group compete. Groups do not."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - consumer groups
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 2 of [Rheo](https://thanos.github.io/series/rheo/). I want to fix the vocabulary before I get into ACK and leases, because “consumer group” sounds like Kafka jargon until you need the behavior. Then it is the only phrase that works.

In Rheo the vocabulary is small on purpose.

- A **stream** is an append-only event log. Order is guaranteed inside a partition, not across partitions.
- A **consumer group** independently tracks progress on that stream.
- **Workers in the same group compete** for leases. Each event is offered to one worker in the group at a time.
- **Workers in different groups each see the full stream.** Risk does not steal work from surveillance.

```text
market-events
  ├── risk
  │     ├── worker A
  │     └── worker B
  └── surveillance
        ├── worker C
        └── worker D
```

If A and B are both in `risk`, an event is a lease that only one of them should hold. If C is in `surveillance`, that same event is a separate lease with a separate ACK. The log is shared. Progress is not.

That is the difference between a queue and a log. A queue has one set of consumers and the message disappears. A log has as many groups as you have reasons to read it.

## The lifecycle, in five calls

You do not have to use the `Rheo.Consumer` macro to understand the model. The facade is enough:

1. `Rheo.create_stream/2` names the log and, if you want, its partition count.
2. `Rheo.append/3` writes an immutable event and assigns a per-partition sequence.
3. `Rheo.create_group/3` registers group state — cursors, frontiers, delivery records.
4. `Rheo.fetch/4` claims work: you get leases, not raw events.
5. `Rheo.ack/2`, `Rheo.nack/3`, or `Rheo.reject/3` records the outcome.

```elixir
:ok = Rheo.create_stream("orders", rheo: MyRheo)
:ok = Rheo.create_group("orders", "fulfillment", rheo: MyRheo)

{:ok, _event} =
  Rheo.append("orders", %{type: "order_created", key: "cust-1"}, rheo: MyRheo)

{:ok, [lease]} = Rheo.fetch("orders", "fulfillment", limit: 1, rheo: MyRheo)
:ok = Rheo.ack(lease, rheo: MyRheo)
```

The thing you ACK is a **lease**, not the event. The event stays. The lease is the group’s claim that this worker, right now, is allowed to settle this delivery.

## Where the state lives

Cursors, frontiers, and deliveries live in the backend. On Mongo they are collections. On Ecto they are `rheo_*` tables your app migrates. On Redis they ride native consumer groups and a pending-entries list. On ETS they are tables that die with the owner process.

The important part is not the storage shape. OTP owns process lifecycle. The backend owns consumer-group correctness.

Restart a worker and you have not rolled back the group. You have dropped a lease. The lease expires. Someone else fetches it. That is what part 3 is about.

## Competing vs independent

Two patterns, easy to confuse because they look the same in a supervision tree.

**Competing consumers** — two processes, same `{stream, group}`. They share progress. Use this to add concurrency on one node, or to run the same group on several BEAM nodes against a shared store (Postgres or Redis). The backend arbitrates leases.

**Independent groups** — two processes, same stream, different group names. They do not share progress. Use this when two subsystems must each see every event: billing and risk, projections and notifications.

Running a `Rheo.Consumer` and a `Rheo.Producer` against the same durable group is competing consumers. It is legal. It is rarely what you meant. Pick one runtime per `{rheo, stream, group}` per node and scale with `concurrency` or with more nodes.

## What a group is not

A group is not a cursor integer you increment after each handler. That is how holes appear and lag starts reporting fiction. Rheo keeps a materialization cursor (how far events have been offered) separate from a committed frontier (how far every sequence is terminal). Part 12 is the full argument. For now: ACK is an outcome on a lease, not a bookmark you slide forward.

A group is also not a GenServer. The process that polls and renews leases is a local runtime for that group on this node. Kill it and the group still exists in the store.

## The shape I actually use

Most of the time I never call `fetch` myself. I write a handler and supervise it:

```elixir
defmodule MyApp.FulfillmentConsumer do
  use Rheo.Consumer, stream: "orders", group: "fulfillment"

  @impl true
  def handle_event(event, _context) do
    :ok = MyApp.Fulfillment.process(event)
    :ack
  end
end
```

`use Rheo.Consumer` is a child spec for `Rheo.Group`. The Group owns demand, worker tasks, renewal, and settlement. The handler returns `:ack`, `{:retry, reason}`, or `{:reject, reason}`.

Next: why the happy-path ACK is a trap, and what fencing tokens are for.

**Read next:** [Why ACK Is Harder Than It Looks](https://thanos.github.io/articles/2026-09-21-rheo-03-why-ack-is-harder/)

*Docs: [Quick Start](https://rheo.hexdocs.pm/quick-start.html) · [Rheo.Consumer](https://rheo.hexdocs.pm/Rheo.Consumer.html)*
