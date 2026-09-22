---
title: "Search and Replay the Event History"
description: "Queues that delete on ACK cannot answer what happened last Tuesday. Replay should not copy the log."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - replay
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 11 of [Rheo](https://thanos.github.io/series/rheo/). Parts 6 and 8 argued that search belongs on the event log. This article is the operational half: pagination, lineage, and re-driving a group without cloning millions of events into a “replay topic.”

The picture is two structures, not one:

```text
events (immutable)          deliveries (per group)
+------------------+        +------------------------+
| seq 1..N         | <----- | risk: available/leased |
| never deleted    |        | risk-replay-…: fresh   |
+------------------+        +------------------------+
```

Replay writes delivery state. It does not duplicate the log.

## Search that can walk

```elixir
Rheo.query("market-events",
  type: "curve_update",
  currency: "EUR",
  after_sequence: 100,
  until_sequence: 500,
  from: ~U[2026-01-01 00:00:00Z],
  order_by: [sequence: :asc],
  limit: 50
)
```

Offset pagination pretends the log is a static array. It is not. Use a cursor:

```elixir
{:ok, page} = Rheo.query_page("market-events", type: "curve_update", limit: 100)
# page.next_cursor => %{0 => ..., 1 => ...}   # per partition

{:ok, page2} =
  Rheo.query_page("market-events",
    type: "curve_update",
    limit: 100,
    cursor: page.next_cursor
  )
```

Or stream, and accept that a mid-stream failure raises. Silent truncation is how you ship a report that is “mostly the history.”

```elixir
Rheo.stream_query("market-events", type: "curve_update", limit: 100)
|> Enum.take(250)
```

## Lineage is metadata you chose to write

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

`correlation_id` / `causation_id` are how you explain a trade without grepping payloads. They are also how query stays portable: backends index known lineage fields instead of offering a different JSON path language each.

## Replay without copying events

Three tools, in the order I prefer them.

**1. A new group with a start cursor.** Best default. The original group keeps its frontier. The replay group is a new independent consumer with a name you can kill later.

```elixir
Rheo.create_group("market-events", "risk-replay-2026-01", start_after: 1_000)
# or start_at: ~U[2026-01-15 00:00:00Z]
```

**2. Replay on the existing group.** Reopens deliveries. At-least-once duplicates are expected. Use this when the group *is* the projection and you cannot stand up a second one.

```elixir
Rheo.replay("market-events", "risk", from_sequence: 1_000)
Rheo.replay("market-events", "risk", from: ~U[2026-01-15 00:00:00Z])
Rheo.replay("market-events", "risk", query: [type: "curve_update", currency: "EUR"])
```

Query-selected replay upserts deliveries for matching ids. Unrelated groups never change. Other events in the same group stay as they were.

**3. Destructive reset.** Loud on purpose.

```elixir
Rheo.reset_group("market-events", "risk", confirm: true)
# optional: start_after: 500
```

Without `confirm: true`, Rheo returns `{:error, :confirm_required}`. Reset clears *that group’s* deliveries. Events remain. Other groups are untouched. If a dashboard ever calls this without the flag, the dashboard is wrong — and the library will refuse.

## Failure cases you should plan for

- Replay after a partial bugfix will redeliver events the already-fixed handler already processed. Idempotency on `event.id` is not optional here.
- A filtered replay is not a filtered log. The events you did not select are still in the stream.
- Streaming query that swallows a failed page will lie. Rheo raises instead.

## Replay is not seek

People coming from Kafka want “set the offset to 1000.” Rheo will let you start a group there. It will not let you confuse that starting point with the committed frontier of a group that already has holes. After 0.5, replay is partition-aware:

```elixir
Rheo.replay("market-events", "risk", from_sequence: 1000, partition: 2)
Rheo.reset_group("market-events", "risk", confirm: true, partition: 2)
```

Which only makes sense once you stop treating ACK as a single cursor. That is the next article.

**Read next:** [ACKs Are Not a Cursor](https://thanos.github.io/articles/2026-09-21-rheo-12-acks-are-not-a-cursor/)

*Docs: [Replay guide](https://rheo.hexdocs.pm/replay.html) · [ADR 015](https://github.com/thanos/rheo/blob/main/docs/adr/015-replay-semantics.md)*
