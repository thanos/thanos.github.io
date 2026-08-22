---
title: "FlyBy: Simulator Before Hardware"
description: "Four reproducible walks through FlyBy’s product simulator: a steady baseline, deterministic packet loss, protocol-aware quotes, and classic pcap replay—without privileged networking."
date: 2026-08-22
tags:
  - Rust
  - SPDK
  - io_uring
  - DPDK
  - user space
  - latency
  - simulator
  - AF_XDP
  - market data
draft: false
authors:
  - Thanos Vassilakis
---

[FlyBy](https://github.com/thanos/flyby) is a Rust pipeline framework aimed at high-rate ingest: source, decode, transform, route, sink. The hardware story is AF_XDP, io_uring, DPDK, SPDK. Those backends need Linux privileges and machines most laptops are not.

Part VI of the project treats the **simulator as a product feature**, not a test stub. You can develop, demo, and CI the pipeline on macOS. Throughput numbers from these runs are **simulated**. Do not quote them as hardware.

This series follows the four seed posts in the FlyBy [`articles/`](https://github.com/thanos/flyby/tree/main/articles) catalog. Each installment has a named workload you can reproduce from the repo:

```bash
./scripts/reproduce-article.sh part-vi-simulator-intro
```

The same catalog maps each slug to a Git tag (`medium/<slug>`), a built-in scenario or pcap fixture, and expected CLI output.
