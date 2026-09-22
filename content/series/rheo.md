---
title: "Rheo"
description: "Notes on putting consumer groups in front of a database you already run, instead of standing up a second cluster."
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

I wrote [Rheo](https://hex.pm/packages/rheo) because I kept needing two things from the same events: deliver the next one to a group of workers, and look up what happened last Tuesday. Most setups solve that with a broker plus a database. I wanted the consumer-group machinery in OTP, on a store I was already running.

Rheo is an Elixir library. You put it in your supervision tree. It gives you leases, competing consumers, ACK fencing, partitions, lag, replay, and query over MongoDB, PostgreSQL, SQLite, Redis Streams, Mnesia, or ETS.

**Library:** [hex.pm/packages/rheo](https://hex.pm/packages/rheo) · **Docs:** [rheo.hexdocs.pm](https://rheo.hexdocs.pm/readme.html) · **Source:** [github.com/thanos/rheo](https://github.com/thanos/rheo)

Delivery is at-least-once. Order is per partition. Consuming an event does not delete it.

![Rheo example control — append events, inspect groups, watch lag](https://thanos.github.io/images/rheo/Rheo-Screenshot-Example-Control.jpg)

*The example app: append to the log, inspect groups, watch lag.*

Parts 1–8 are the idea and the mechanics. Parts 9–17 are why the API moved: the 0.2 break, ETS as a second witness, Redis forcing a rewrite of what the callbacks *mean*, and what I froze before 1.0.

If you want to try it, `mix rheo.demo` and the [Livebook demos](https://hexdocs.pm/rheo/rheo_demo.html) are the hands-on version. HexDocs is the contract. These articles are the argument.

I wrote them so I could remember why I made the choices I did, and so you can decide whether the library is for you.
