---
title: "Searching the Stream"
description: "After ACK I still want to ask what happened. The log is still there."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - search
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 8 of [Rheo](https://thanos.github.io/series/rheo/). Queue-then-delete systems have a clean ops story and a hole where the business lives. Once the consumer ACKs, the payload is gone. Tomorrow’s incident review becomes “we think it processed” plus whatever side table you remembered to write.

Rheo keeps the events. Search is not an export job. It is the same API you used to consume.

```elixir
Rheo.query("market-events",
  type: "curve_update",
  currency: "EUR",
  curve: "EUR-EURIBOR-6M"
)

Rheo.query("market-events", correlation_id: "abc")
Rheo.query("market-events", producer: "pricing-service-v3")
```

The log remains the system of record for what happened, and it is the thing consumer groups walk.

## Query without joining a group

`Rheo.query/2` does not take a group name. It does not mark anything leased. It does not advance a frontier. You can search a stream that has ten groups or zero. Investigation is not consumption.

This sounds obvious until someone wires a “replay dashboard” that fetches leases and ACKs them to look at the payload. That dashboard just stole work from `risk`. Inspect APIs (`Rheo.read/3`, `Rheo.query/2`, `Rheo.dead_letters/3`, `Rheo.group_info/3`) are the read side. Fetch is the write side of delivery state.

## What you can ask

The portable query is small: type, key, sequence bounds, time bounds, lineage fields, `order_by`, `limit`. Backends translate. Mongo and Postgres can use indexes. ETS and Redis filter after a walk and say so.

```elixir
Rheo.query("market-events",
  type: "curve_update",
  after_sequence: 100,
  until_sequence: 500,
  from: ~U[2026-01-01 00:00:00Z],
  order_by: [sequence: :asc],
  limit: 50
)
```

Lineage is convention, not magic. Put it in metadata when you append:

```elixir
meta =
  Rheo.Event.Lineage.put(%{},
    correlation_id: "trade-42",
    causation_id: "cmd-9",
    producer: "pricing-v3",
    schema: "curve_update",
    schema_version: "1"
  )

Rheo.append("market-events", %{type: "curve_update", currency: "EUR", metadata: meta})
Rheo.query("market-events", correlation_id: "trade-42")
```

If you do not put `correlation_id` in, Rheo will not invent it from the payload. Libraries that “just index everything” either lie or explode the index list. Be explicit.

## Read versus consume

```elixir
{:ok, events} = Rheo.read("market-events", after: 0, limit: 100)
```

`read` is a log scan. `fetch` is a claim. If you are building an admin page, you want `read` and `query`. If you are building a worker, you want a Consumer or a Producer. Mixing them is how investigative tools become accidental consumers.

## Pagination without OFFSET

`LIMIT 50 OFFSET 100000` is a tax. `Rheo.query_page/3` returns a cursor. `Rheo.stream_query/3` walks pages for you and raises if a mid-stream page fails — no silent truncation of history.

Part 11 is the full search-and-replay piece: new groups with start cursors, `Rheo.replay/3` on an existing group, and the loud `reset_group` that refuses to run without `confirm: true`.

For this article, the smaller point: ACK does not delete. The investigative question stays cheap only because that is true.

**Read next:** [Why Rheo 0.2 Broke Its 0.1 API](https://thanos.github.io/articles/2026-09-21-rheo-09-why-rheo-0-2-broke-its-0-1-api/)

*Docs: [Querying](https://rheo.hexdocs.pm/querying.html) · [Article 11](https://thanos.github.io/articles/2026-09-21-rheo-11-search-and-replay/)*
