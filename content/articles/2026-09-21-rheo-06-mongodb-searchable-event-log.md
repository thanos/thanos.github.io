---
title: "MongoDB as a Searchable Event Log"
description: "The first backend was Mongo because the product is “query the history,” not “pop a queue.”"
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - MongoDB
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 6 of [Rheo](https://thanos.github.io/series/rheo/). The first backend was Mongo because the product is “query the history,” not “pop a queue.”

Rheo’s first durable backend is MongoDB for a reason that has nothing to do with fashion. Mongo is an indexed document store that is already good at the question brokers dodge: *what happened?*

If your events look like market-data updates — a curve, a currency, a producer, a correlation id — you want a document you can filter without reconstructing a payload from a byte log.

## The event document

```javascript
{
  _id: "…",
  stream: "market-events",
  partition: 0,
  sequence: 12345,
  timestamp: ISODate("…"),
  type: "curve_update",
  key: null,
  metadata: { correlation_id: "abc", producer: "pricing-service-v3" },
  payload: { currency: "EUR", curve: "EUR-EURIBOR-6M", price: 2.913 }
}
```

That document is the system of record. Consumption does not update it. Consumption writes a *delivery* somewhere else.

## Sequences are integrity, not decoration

On append, the backend atomically increments a per-partition counter (`streams.next_sequence` on Mongo). A unique index on `(stream, partition, sequence)` is the integrity constraint. If two appends could take the same sequence, every later idea — frontier, lag, replay — becomes folklore.

Sequences are integers on purpose. They travel across backends. Redis has its own entry ids; those go in `lease.receipt`. The portable order stays `event.sequence`. Part 16 is that split in detail.

## Deliveries are the mutable half

`deliveries` documents track per-group status: `available`, `leased`, `acked`, `rejected`. Claiming work is `findOneAndUpdate` with status and expiry predicates. The update carries a new `lease_id`. If the predicate does not match, you did not get the work.

That shape — one row per `{group, event}` and a compare-and-set on the token — is what ETS and Ecto also implement. It is a fine model for row stores. It is the model Redis later refused to pretend to be. Remember that tension; Part 15 exists because of it.

## Query is product surface

`Rheo.query/2` is not an admin afterthought. It is why you used a database.

```elixir
Rheo.query("market-events",
  type: "curve_update",
  currency: "EUR",
  curve: "EUR-EURIBOR-6M"
)

Rheo.query("market-events", correlation_id: "abc")
Rheo.query("market-events", producer: "pricing-service-v3")
```

The query struct is portable (`%Rheo.Query{}`). Backends translate. You do not pass a Mongo sort document through the public API. That was a 0.1 accident and a 0.2 break, which is the right kind of break.

On Mongo, secondary indexes make this cheap. On ETS and Redis, query walks and filters. Capabilities declare that difference (`secondary_indexes: true | false`). They do not change the caller’s shape.

## Indexes are part of the backend, not the README

ADR 008 is the schema and index list. You should not be inventing a unique key on `(stream, partition, sequence)` at 2 a.m. because lag looks “almost right.” `Rheo.ensure_indexes/1` is idempotent. Use it. Then go look at the actual indexes once, so you know what you are paying for.

## Why Mongo first, not only

Mongo-first was a bet: if the log is searchable by default, people will stop treating history as a dump they might get to later. The later backends had to keep that promise or the product became “a Mongo library with extra steps.”

They kept it. Postgres stores `jsonb` payloads you can query in SQL. SQLite stores JSON text. ETS answers the same `%Rheo.Query{}` in memory. Redis walks the stream and admits it is not RediSearch.

The document above is still the clearest picture of what an event *is*. Everything after Part 6 is that picture surviving contact with other stores.

**Read next:** [Killing Consumers on Purpose](https://thanos.github.io/articles/2026-09-21-rheo-07-killing-consumers/)

*Docs: [Mongo guide](https://rheo.hexdocs.pm/mongo.html) · [ADR 008](https://github.com/thanos/rheo/blob/main/docs/adr/008-mongodb-schema-and-indexes.md)*
