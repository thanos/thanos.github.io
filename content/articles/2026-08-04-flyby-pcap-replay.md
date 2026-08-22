---
title: "FlyBy: Replaying Classic Pcap Captures"
description: "Part 4: replay FlyBy’s udp_quotes.pcap through the simulator—20 UDP binary quotes, full-speed or original timing, classic pcap only."
date: 2026-08-22
tags:
  - pcap
  - market data
  - replay
  - binary protocols
  - UDP
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

Generated traffic is a contract with yourself. A pcap is a contract with a capture. FlyBy’s simulator ingests **classic libpcap** (not pcap-ng) and replays it against the same virtual clock as `VirtualNic`.

This is part 4 of *FlyBy*, and the last of the seed catalog posts. [Part 3](/articles/2026-08-03-flyby-protocol-aware-quotes/) generated 34-byte AAPL quotes. This installment **replays** twenty of those frames from `simulator/fixtures/udp_quotes.pcap`.

---

## The fixture

Fixtures live under `simulator/fixtures/`. `udp_quotes.pcap` is 20 packets, 100 µs apart, UDP plus the same binary market-quote layout as `ProtocolMessage::MarketQuote`. Convert pcap-ng dumps with `editcap -F pcap` before feeding them in.

```bash
cargo run -p flyby-simulator --bin flyby-sim -- pcap simulator/fixtures/udp_quotes.pcap --full-speed
./scripts/reproduce-article.sh part-vi-pcap-replay
```

`--full-speed` ignores capture timestamps and emits as fast as the scheduler can tick. Omit it to honour original timing via `SimReplay` and `ReplayMode::OriginalTiming`.

Other checked-in captures: `tiny_3pkt.pcap` (smoke), `burst_100.pcap`, `quotes_1s_1kpps.pcap` (1,000 MSFT quotes, 1 ms apart). Regenerate after layout changes with `cargo run -p flyby-simulator --example gen_pcap_fixtures`.

---

## Replay modes

The storage replay engine and the simulator clock share modes. In Rust:

```rust
use flyby_simulator::{PcapConfig, PcapSource, load_pcap, NullEventSink};
use flyby::storage::ReplayMode;

let packets = load_pcap("simulator/fixtures/udp_quotes.pcap")?;
let src = PcapSource::new(
    packets,
    PcapConfig { replay: ReplayMode::FullSpeed, ..Default::default() },
    NullEventSink,
)?;
```

| Mode | Behaviour |
|---|---|
| `FullSpeed` | Ignore capture deltas |
| `OriginalTiming` | Pace from timestamps on the virtual clock |
| `TimeScaled` | Stretch or compress those deltas |
| `Burst` | Group arrivals |
| `SingleStep` | Educational one-packet-at-a-time |

FlyScenario exposes the same knobs as `[[pcap]] replay = …`.

Approximate CLI (catalog expected output):

```text
Replaying pcap 'simulator/fixtures/udp_quotes.pcap' (20 packets)
  Replay   : FullSpeed
  Note     : results are SIMULATED (not hardware)

Results (simulated):
  Packets generated : 20
  Slots written     : 20
```

Twenty in, twenty written: the ring did not overflow this tiny capture. That is the assertion. It is not a replay of a production matching engine.

---

## Generated quotes vs captured quotes

Use **generated** protocol traffic when you need a million packets, a seed, and a rate you chose. Use **pcap** when the question is “does this decoder still accept last Tuesday’s capture?” Both paths implement `NetworkSource`. Downstream should not care.

Classic pcap only keeps the tool boring in a useful way: one file format, one timestamp story, convert at the edge if Wireshark handed you pcap-ng.

---

## The series, in one pass

1. [A simulator before the hardware](/articles/01-flyby-simulator-before-hardware/) — `constant_rate`
2. [Deterministic fault injection](/articles/02-flyby-deterministic-fault-injection/) — `packet_loss`
3. [Protocol-aware generators](/articles/03-flyby-protocol-aware-quotes/) — `protocol_quotes`
4. This page — `udp_quotes.pcap`

Reproduce any of them from the [FlyBy](https://github.com/thanos/flyby) repo with `./scripts/reproduce-article.sh <slug>`. Treat every pps figure as simulated until a hardware backend is measuring on hardware.
