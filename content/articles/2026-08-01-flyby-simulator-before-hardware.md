---
title: "FlyBy: A Simulator Before the Hardware"
description: "Part 1: why FlyBy ships a first-class simulator, how VirtualNic and virtual time work, and how to run the constant_rate baseline at 100 kpps without privileged networking."
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
  - VirtualNic
draft: false
authors:
  - Thanos Vassilakis
series: flyby-part-vi
---

FlyBy’s production path is kernel-bypass networking and fast storage. AF_XDP, DPDK, io_uring, and SPDK are the named backends. None of them run on a normal laptop, and none of them belong in CI as a smoke test.

That is why [FlyBy](https://github.com/thanos/flyby) ships a simulator **before** those adapters are real. The decision is written down as [ADR-0007](https://github.com/thanos/flyby/blob/main/docs/src/adr/0007-simulator-before-hardware.md) (simulator before hardware) and [ADR-0008](https://github.com/thanos/flyby/blob/main/docs/src/adr/0008-simulator-is-a-product-feature.md) (the simulator is a product feature, not a `tests/` leftover).

This is part 1 of *FlyBy*. The workload is the built-in scenario `constant_rate`: one virtual second of steady 100 kpps, no faults.

---

## The pipeline, without the NIC

FlyBy’s public shape is still:

```text
Source -> Decode -> Transform -> Route -> Sink
```

The simulator sits on the **source** side. Virtual NICs, pcap files, and virtual storage emit the same batch stream the hardware adapters will eventually emit. Downstream code should not know which adapter filled the batch.

```text
Virtual NICs / Pcap      Virtual Storage
      │                         │
      └────────────┬────────────┘
                   ▼
            Source Adapters
                   ▼
             Raw Batch Stream
                   ▼
          Virtual Shared Memory
                   ▼
          Virtual Consumers
```

`VirtualNic` implements the same `NetworkSource` contract the AF_XDP and DPDK backends will implement. If a type only works with the simulator, that is a bug in the type, not a reason to hide the simulator.

---

## Run the baseline

From a clone of [thanos/flyby](https://github.com/thanos/flyby):

```bash
cargo run -p flyby-simulator --bin flyby-sim -- constant_rate
```

Or the article reproduce hook, which prints the catalog banner and then runs the same workload:

```bash
./scripts/reproduce-article.sh part-vi-simulator-intro
```

The Ratatui dashboard is the same scenario with a clock, ring gauge, and sparklines:

```bash
cargo run -p flyby-simulator --bin flyby-sim -- tui constant_rate
```

Keys: `Space` run/pause · `s` step · `+`/`-` speed · `r` restart · `q` quit.

The equivalent FlyScenario file is `scenarios/constant_rate.fly.toml`: 1 ms ticks, virtual clock, 100,000 packets per second, 8-byte sequence payloads, a 4096-slot ring, unlimited consumer drain, seed `0`.

---

## What “simulated” means

Under virtual time the scheduler does not sleep. One virtual second at 1 ms ticks is 1,000 ticks. At 100 kpps that is **100,000 packets generated, 0 dropped** for this scenario. Those packet counts should be stable. Wall-clock throughput in the CLI footer is machine-dependent and labelled simulated.

Approximate CLI (from the article catalog—not a hardware measurement):

```text
Running scenario 'constant_rate': Steady 100 kpps, no faults, 1 second virtual time.
  Note     : results are SIMULATED (not hardware)

Results (simulated):
  Ticks             : 1000
  Packets generated : 100000
  Packets dropped   : 0
  Throughput        : <machine-dependent> pps (wall-clock, simulated)
```

Do not put that throughput number in a benchmark table next to AF_XDP. Use the scenario for correctness, relative comparisons, tutorials, and CI.

---

## Why this is part of the product

A mock that returns `Ok(())` cannot pace 100 kpps, inject a 5% drop, or replay a pcap against a virtual clock. A hardware-only loop cannot run on GitHub-hosted macOS runners. The simulator is the third option: public types, a `flyby-sim` binary, versioned scenarios, and the same source traits as production.

Next: [deterministic fault injection](/articles/2026-08-02-flyby-deterministic-fault-injection/)—LCG-seeded drops you can count.
