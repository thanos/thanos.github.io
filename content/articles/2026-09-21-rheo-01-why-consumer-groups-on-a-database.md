---
title: "Why Put Consumer Groups in Front of a Database?"
description: "I wanted to deliver events to a group of workers and still be able to look those events up later, without running two systems."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - databases
  - Kafka
draft: false
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 1 of [Rheo](https://thanos.github.io/series/rheo/). I started this series because I kept needing two things from the same events: deliver the next one to a group of workers, and find the one that explains what happened at 13:04.

Message brokers are good at the first part. They get a payload to a consumer, compete for it, retry it, dead-letter it. They are not good at the second. Ask a broker what happened to EUR-EURIBOR-6M and you end up with log shipping, retention tickets, and a second index, because the broker was never a system of record.

Databases store history and answer questions. But consuming from a database as a load-balanced consumer group is hard. You have to write leases, fencing, competing workers, lag, retries, and so on. I have written that code more than once. It is always worse than I thought it would be.

Rheo is for when you need both:

- deliver the next event to a consumer group
- find the event that explains what happened

That comes up a lot in market data, orders, risk, and audit trails.

## What teams usually do

They keep the queue and put a database behind it as the golden record. A dedicated consumer copies each event into the database and then ACKs. After a while they purge the queues. Less often they spool the database off to S3 and purge that too.

Now they maintain two systems, and they still throw the history away. They just do it in stages.

I wanted something simpler. One database you already run, consumer groups on top, and you can still scale out workers.

## Brokers vs databases vs Rheo

Brokers and Rheo both let you consume some events and not others. They do not do it in the same place.

| | Interest model | Consume unit |
|---|---|---|
| **NATS JetStream** | Subject hierarchy and wildcards (`*`, `>`) | A consumer can pull from many matching subjects |
| **RabbitMQ** | Exchanges and bindings (routing keys, `#` / `*`) | A queue is bound to patterns; one queue can fan-in many routes |
| **Redis Streams** | Named stream key. `XREAD` can list several keys; no subject tree | A consumer group (`XGROUP`) is one stream, with a native PEL |
| **Rheo** | Explicit stream name | One group on one stream. Filters are inside the log (type, key, query), not across stream names |
| **Mongo / Postgres / SQLite alone** | Whatever you query | No consumer group unless you write one |

Rheo can filter. It does not subscribe to a subject tree. You pick a stream, then you search or query inside that log. One group, one stream. If you need pattern fan-in, run more than one group, or put the topic on the event and query it. Rheo is not a topic bus.

What you get instead is searchable history, leases and frontiers, and the database you already run. Same public API on each backend. Consumption does not delete the event. No second cluster.

## Two kinds of data

I ended up with a simple split.

- **Events are immutable.** They stay in the backend until a retention policy you chose says otherwise. An event has a stream, a partition, a per-partition sequence, a type, a payload, and optional lineage metadata.
- **Delivery state is mutable and per group.** Leases, ACKs, retries, dead letters, the materialization cursor, and the committed frontier live beside the log, not inside it.

That is what lets two teams consume the same stream independently. Risk and surveillance both see every `curve_update`. Neither deletes the row the other still needs. When someone asks what the price was at 13:04, you query the log. You do not reconstruct it from a queue that already forgot.

```text
append  →  immutable event log
              ├── group "risk"          (own leases, own frontier)
              └── group "surveillance"  (own leases, own frontier)

query   →  the same log, no group involved
```

## When I use it

I use Rheo when I want an immutable, queryable event log in a database I already run, with consumer groups, leases, ACK, retry, and dead-lettering. Competing consumers on one group, or independent groups on the same stream. Partitions with key routing. A durable source for Broadway, if I need a pipeline.

I do not use it when I need a dedicated broker (many languages on one bus, huge fan-out, exactly-once *claims*), or when the problem is really a job queue. Oban is a better job system. Broadway is a better pipeline topology. Rheo is the durable log those things can read from.

Brokers add latency — extra hops, persistence, ACK rounds. If you care about microseconds you do not use a broker; you use ZeroMQ or something else that is not a broker. People keep Kafka or Rabbit when they already have it.

Rheo is about keeping the rest simple: a library you embed, not a server you operate.

Next I will explain what I mean by a consumer group.

*Docs: [Rheo README](https://rheo.hexdocs.pm/readme.html) · [Architecture](https://rheo.hexdocs.pm/architecture.html)*
