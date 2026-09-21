---
title: "Why Put Consumer Groups in Front of a Database?"
description: "Brokers deliver. Databases remember. Some workloads need both from the same log."
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

This is part 1 of [Rheo](https://thanos.github.io/series/rheo/). Brokers deliver. Databases remember. Some workloads need both from the same log.

Message brokers are excellent at a specific job: get this payload to a consumer, compete for it, retry it, dead-letter it. Ask a broker “what happened to EUR-EURIBOR-6M at 13:04?” and you have left the product’s comfort zone. You are now in log shipping, retention tickets, and a second index you built because the broker was never a system of record.

Databases are excellent at the opposite job. They store durable, indexed history and they answer investigative questions. Ask Postgres or Mongo to behave like a consumer group — leases, fencing, competing workers, independent progress per team — and you will invent a broker inside a table, badly.

Rheo exists for the workloads that refuse to pick one:

- deliver the next event to a consumer group
- find the event that explains what happened

If your domain is market data, orders, risk signals, audit trails, or anything else where *delivery* and *investigation* share a timeline, that split is the whole product problem.

## The false choice

Teams usually resolve the tension in one of three ways.

**Stand up Kafka (or Pulsar, or Redpanda).** You get partitions, consumer groups, and a mature ops story. You also get a cluster that is not your application database, a second backup story, and historical search that is possible but operationally heavy. Kafka is a log. It is not a query engine.

**Use RabbitMQ or NATS.** You get routing and ACKs. You do not get an immutable searchable event log. After ACK, the message is gone, or it is sitting in a retention policy that was never designed for “show me every curve update for this instrument last quarter.”

**Roll a queue table.** `FOR UPDATE SKIP LOCKED` is a fine claiming trick. It is not a consumer group. You still have to invent fencing tokens, independent groups on the same events, replay without copying rows, lag that does not lie, and a story for what happens when the worker that processed the row dies before the UPDATE commits.

Rheo’s claim is narrower than “databases replace brokers.” Brokers remain better for massive fan-out, ultra-low-latency messaging, and shops already standardized on them. The claim is: *if you already run a store that can hold an immutable log, the consumer-group machinery can live in OTP on top of that store.*

## Brokers vs databases vs Rheo

| System | Delivery | Historical search |
|---|---|---|
| RabbitMQ | Strong queues and ACKs | Weak long-term query |
| NATS / JetStream | Fast streams | Limited investigative query |
| Kafka | Partitioned log + groups | Possible, operationally heavy |
| MongoDB alone | Do it yourself | Strong indexes and query |
| PostgreSQL / SQLite alone | Do it yourself | Strong SQL and indexes |
| Redis Streams alone | Native PEL and groups | History search is secondary |
| **Rheo + those stores** | Leases, groups, fencing in OTP | First-class `Rheo.query/2` plus the store’s own query |

The last row is the product. Same public API. Different backends. The log stays queryable because consumption is not deletion.

## Rheo’s split

Two kinds of data, two kinds of mutability:

- **Events are immutable.** They live in the backend forever, until a retention policy you chose says otherwise. An event has a stream, a partition, a per-partition sequence, a type, a payload, and optional lineage metadata.
- **Delivery state is mutable and per group.** Leases, ACKs, retries, dead letters, the materialization cursor, and the committed frontier live beside the log, not inside it.

That split is what lets two teams consume the same stream independently. Risk and surveillance both see every `curve_update`. Neither deletes the row the other still needs. When someone asks what the price was at 13:04, you query the log — you do not reconstruct it from a queue that already forgot.

```text
append  →  immutable event log
              ├── group "risk"          (own leases, own frontier)
              └── group "surveillance"  (own leases, own frontier)

query   →  the same log, no group involved
```

## When to use it

Use Rheo when you want:

- an immutable, queryable event log in a database you already run
- consumer groups with leases, ACK, retry, and dead-lettering
- competing consumers *and* independent groups on the same stream
- partitions with key routing and honest lag
- a durable source for Broadway, instead of a second broker
- OTP-native demand and lease renewal, without a Kafka cluster

Skip it when you need a dedicated broker (cross-language clients, huge fan-out, exactly-once *claims*), or when a job queue is actually the problem. Oban is a better job system. Broadway is a better pipeline topology. Rheo is the durable log those things can read from.

## The sentence to keep

Databases already store and search historical events well. Message brokers already coordinate consumers well. Rheo combines those strengths in a library you embed, not a server you operate.

Next: what a consumer group actually is — streams, competing workers, and independent progress.

<!-- **Read next:** [What Is a Consumer Group?](https://thanos.github.io/articles/2026-09-21-rheo-02-what-is-a-consumer-group/) -->

*Docs: [Rheo README](https://rheo.hexdocs.pm/readme.html) · [Architecture](https://rheo.hexdocs.pm/architecture.html)*
