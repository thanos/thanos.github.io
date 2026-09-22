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

Message brokers are good for enabling decoupled services to consume messages asynchronously, reliably, and in a load-balanced manner.

Databases store history and answer questions. But consuming from a database in a load balanced _consumer group_ manner is hard — you have to code leases, fencing, competing workers, lag management, retries etc.

Rheo is for when you need both:

- deliver the next event to a consumer group
- find the event that explains what happened

That is a common problem in market data, orders, risk, and audit trails.

## What teams usually do

They keep the queue and put a database behind it as the golden record. They stand up a dedicated consumer that copies the events to the database and then ACKs. After a while they purge the queues. Less often they spool off the database to S3 and purge that too.

They maintain two systems.

Rheo gives you one more choice. Use you can use a databae but you dont loose your scalability. 

## Brokers vs databases vs Rheo

Brokers and Rheo both let you consume some events and not others. They do not do it in the same place.

| | Interest model | Consume unit |
|---|---|---|
| **NATS JetStream** | Subject hierarchy and wildcards (`*`, `>`) | A consumer can pull from many matching subjects |
| **RabbitMQ** | Exchanges and bindings (routing keys, `#` / `*`) | A queue is bound to patterns; one queue can fan-in many routes |
| **Redis Streams** | Named stream key. `XREAD` can list several keys; no subject tree | A consumer group (`XGROUP`) is one stream, with a native PEL |
| **Rheo** | Explicit stream name | One group ↔ one stream. Filters are inside the log (type, key, query), not across stream names |
| **Mongo / Postgres / SQLite alone** | Whatever you query | No consumer group unless you write one |

Rheo can filter. It does not subscribe to a subject tree. You pick a stream. Then you search or query inside that log.

Rheo is not a topic bus. If you need pattern fan-in, run more than one group, or put the topic on the event and query it.

What you get instead is searchable history, leases and frontiers, and the database you already run. Same public API on each backend. Consumption does not delete the event.

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

Databases already store and search historical events well. Message brokers already coordinate consumers well. Rheo combines those in a library you embed, not a server you operate.

Next: what a consumer group actually is — streams, competing workers, and independent progress.

<!-- **Read next:** [What Is a Consumer Group?](https://thanos.github.io/articles/2026-09-21-rheo-02-what-is-a-consumer-group/) -->

*Docs: [Rheo README](https://rheo.hexdocs.pm/readme.html) · [Architecture](https://rheo.hexdocs.pm/architecture.html)*
