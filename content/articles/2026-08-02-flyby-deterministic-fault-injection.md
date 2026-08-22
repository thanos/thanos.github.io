---
title: "FlyBy: Deterministic Fault Injection"
description: "Part 2: LCG-seeded packet drops in FlyBy’s packet_loss scenario—5% drop at 10 kpps for 10 virtual seconds, with counters you can assert in CI."
date: 2026-08-22
tags:
  - simulator
  - fault injection
  - testing
  - determinism
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

A simulator that only generates happy packets teaches the wrong lesson. Networks drop, corrupt, and stall. FlyBy’s fault injector is part of the public simulator API: drop, corrupt, latency spike, each observable as events and counters.

This is part 2 of *FlyBy*. In [part 1](/articles/2026-08-01-flyby-simulator-before-hardware/) we ran `constant_rate` with zero faults. Here the workload is `packet_loss`.

---

## The scenario

`Scenario::packet_loss()` is 10 kpps for **10 virtual seconds**, 5% random drop, 1 ms ticks, virtual clock. Ten thousand packets per second for ten seconds is 100,000 generated. Five percent of that is about 5,000 drops.

The drop stream is **LCG-seeded**. Same seed, same packets removed. That is the point: you can write a test that asserts a count, not a vibe.

```rust
use flyby_simulator::FaultSpec;

let fault = FaultSpec {
    drop_rate: 0.05,
    corrupt_rate: 0.0,
    latency_spike_rate: 0.0,
    latency_spike_ns: 0,
};
```

The same rates appear in FlyScenario as `[nic.fault]` and as timeline `set_fault` actions if you want the loss to start mid-run.

| Fault | Effect |
|---|---|
| Drop | Packet removed from the delivered batch |
| Corrupt | One payload byte flipped |
| Latency spike | Virtual time advances by `latency_spike_ns` |

Every injected fault shows up on the event sink (`SimEvent`) and on the CLI counters. Silent loss is a bug in the simulator, not a feature of UDP.

---

## Reproduce

```bash
cargo run -p flyby-simulator --bin flyby-sim -- packet_loss
./scripts/reproduce-article.sh part-vi-fault-injection
cargo run -p flyby-simulator --bin flyby-sim -- tui packet_loss
```

In the TUI, watch the drop counter while you single-step (`s`) then auto-run (`Space`). The header still says **\[SIMULATED\]**.

Approximate CLI (catalog expected output; exact drop count is deterministic for a given seed):

```text
Running scenario 'packet_loss': 10 kpps with 5% random drop rate.
  Faults   : drop=5.0% ...
  Note     : results are SIMULATED (not hardware)

Results (simulated):
  Packets generated : 100000
  Packets dropped   : ~5000  (LCG-seeded; exact count is deterministic)
```

---

## Why seed beats “random 5%”

Non-deterministic loss is fine for a chaos demo. It is useless for a regression. If a decoder change mishandles a gap, you want the **same** gap tomorrow.

Virtual time matters here too. A 500 µs latency spike is a clock increment, not a `thread::sleep`. CI does not wait on wall time to inject delay.

What this still cannot do: interrupt coalescing, NUMA, PCIe. If your bug is in those, you still need hardware. If your bug is “decoder panics when 5% of quotes vanish,” the simulator is the right machine.

Next: [protocol-aware traffic](/articles/2026-08-03-flyby-protocol-aware-quotes/)—binary AAPL quotes instead of 8-byte sequence pads.
