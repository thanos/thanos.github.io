---
title: "Rheo"
description: "A 17-part design series about putting durable consumer groups in front of a searchable event log — without standing up Kafka."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - MongoDB
  - PostgreSQL
  - Redis
  - Broadway
  - consumer groups
draft: false
authors:
  - Thanos Vassilakis
---

Rheo: consumer groups on the database you already run.

Most teams that need “deliver this event, then find out what happened last Tuesday” end up running two systems: a broker for delivery and a database for history. Rheo is an Elixir/OTP library that refuses that split. It embeds in your supervision tree and gives you leases, competing consumers, ACK fencing, partitions, lag, replay, and query over a store you already run: MongoDB, PostgreSQL, SQLite, Redis Streams, Mnesia, or ETS.

This series is the design argument behind that library. It follows the official Rheo tutorials — the long-form essays in the repo — expanded into pieces you can read on the train and then take back to a `mix.exs`.

**Library:** [hex.pm/packages/rheo](https://hex.pm/packages/rheo) · **Docs:** [rheo.hexdocs.pm](https://rheo.hexdocs.pm/readme.html) · **Source:** [github.com/thanos/rheo](https://github.com/thanos/rheo)

Delivery is **at-least-once**. Ordering is **per partition**. Consumption **never deletes events**. Those three sentences are the whole plot.

![Rheo example control — append events, inspect groups, watch lag](https://thanos.github.io/images/rheo/Rheo-Screenshot-Example-Control.jpg)

*The example app: append to the log, inspect groups, watch lag. The database is the system of record.*

## Who this series is for

- Elixir engineers who already run Postgres, Mongo, Redis, or Mnesia and do not want a second cluster just to get consumer groups.
- People comparing Broadway, Oban, Kafka, and “we’ll just poll the table.”
- Anyone who has been burned by “the cursor moved, so we must have processed it.”

## How to read it

Read 1–8 if you want the product idea. Read 9–17 if you want the architectural evolution — why the API broke, how ETS proved the contract, why Redis forced a rewrite of the *meanings* of the callbacks, and what is frozen before 1.0.

Hands-on companion: `mix rheo.demo` and the [Livebook demos](https://hexdocs.pm/rheo/rheo_demo.html).

Canonical technical source of truth remains HexDocs — these articles are the argument, not the API contract.
