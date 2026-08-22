---
title: "FlyBy: Protocol-Aware Traffic Generators"
description: "Part 3: FlyBy’s protocol_quotes scenario fills 34-byte binary market quotes (AAPL) through VirtualNic so decoders see structured payloads, not random pads."
date: 2026-08-22
tags:
  - market data
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

A pipeline that only ever sees `0x00..seq` will green-light a decoder that does not parse. FlyBy’s simulator can emit **protocol-aware** payloads: layouts the rest of the stack is supposed to understand.

This is part 3 of *FlyBy*. [Part 1](/articles/2026-08-01-flyby-simulator-before-hardware/) was a rate baseline. [Part 2](/articles/2026-08-02-flyby-deterministic-fault-injection/) was seeded loss. Here the workload is `protocol_quotes`: 10 kpps of binary market quotes for `AAPL`, one virtual second, no faults.

---

## Why “bytes in a batch” is not enough

`VirtualNic` already paces packets. The interesting question is what sits in the payload. Built-in specs include fixed sequence numbers, random bytes, Gaussian sizes, custom callbacks—and `PayloadSpec::Protocol`.

The seed scenario uses `ProtocolMessage::market_quote("AAPL")`. The layout is 34 bytes, big-endian:

```text
msg_type(u8)='Q' | flags(u8) | symbol([u8;8]) | bid(u64 BE) | ask(u64 BE) | seq(u64 BE)
```

Symbol is ASCII, padded with spaces to 8 bytes. Bid is `100_000 + seq % 1_000`; ask is bid plus one. That is enough for a decoder to assert `msg_type`, a ticker, a spread, and a sequence.

There is also a length-prefixed FIX-like `FixQuote` (`35=Q|55=…`) if you want ASCII on the wire instead of the packed binary.

```rust
use flyby_simulator::{PayloadSpec, ProtocolMessage, TrafficConfig, TrafficPattern};

let quotes = TrafficConfig {
    pattern: TrafficPattern::FixedRate { pps: 10_000 },
    payload_size: 34,
    batch_size: 64,
    payload: PayloadSpec::Protocol(ProtocolMessage::market_quote("AAPL")),
};
```

The same choice appears in FlyScenario as `[nic.payload] kind = "protocol"` with `proto = "market_quote"` and a `symbol`.

---

## Reproduce

```bash
cargo run -p flyby-simulator --bin flyby-sim -- protocol_quotes
./scripts/reproduce-article.sh part-vi-protocol-quotes
cargo run -p flyby-simulator --bin flyby-sim -- tui protocol_quotes
```

Approximate CLI (catalog expected output):

```text
Running scenario 'protocol_quotes': 10 kpps binary market-quote payloads (AAPL).
  Payload  : Protocol(MarketQuote { ... })
  Note     : results are SIMULATED (not hardware)

Results (simulated):
  Packets generated : 10000
  Slots written     : 10000
```

Ten thousand generated and ten thousand slots written means the virtual shared-memory ring kept up for this rate and duration. That is a pipeline health check, not a market-data SLA.

---

## What to test with this

- A decoder that rejects `msg_type != b'Q'`.
- Symbol padding (`AAPL` plus four spaces).
- Monotonic `seq` in the last eight bytes.
- Combine with [part 2](/articles/2026-08-02-flyby-deterministic-fault-injection/) so some quotes never arrive; the decoder should not assume a dense sequence.

Random payloads hide all of that. Protocol payloads make the simulator a peer of the production feed—same traits, smaller building.

Next: [replaying a classic pcap](/articles/2026-08-04-flyby-pcap-replay/) of the same quote layout, captured rather than generated.
