---
title: "Why ACK Is Harder Than It Looks"
description: "The happy path is one line. The failure timeline is the product."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - ACK
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 3 of [Rheo](https://thanos.github.io/series/rheo/). The happy path is one line. The failure timeline is the product.

Acknowledging a message is the easiest function in every queue library and the hardest invariant in every one that has been to production.

Happy path:

```elixir
{:ok, [lease]} = Rheo.fetch("orders", "fulfillment", limit: 1, rheo: MyRheo)
:ok = do_work(lease.event)
:ok = Rheo.ack(lease, rheo: MyRheo)
```

That looks like a transaction. It is not. Between `fetch` and `ack` the worker can die, the network can partition, the ACK can land after a newer lease has been issued for the same event, and a restarted worker can try to settle work it no longer owns.

If any of those cases silently “succeed,” you have either lost an event or double-committed with a smile.

## The timeline that matters

```text
t0  worker A fetches event E → lease L1
t1  worker A crashes before ACK
t2  lease L1 expires
t3  worker B fetches event E → lease L2
t4  worker A (restarted, delayed) tries ACK L1 → rejected (:stale_lease)
t5  worker B ACK L2 → durable progress
```

Five steps. One event. Two leases. Exactly one ACK that is allowed to count.

Rheo fences ACKs with an opaque `lease_id`. Only the current lease holder can acknowledge. A stale token is not a retry. It is a no. The backend returns `:stale_lease`, and the runtime drops the work instead of fighting the worker who now owns it.

On backends with a native claim identity — Redis entry ids, for example — there is a second token: `lease.receipt`. Settle fences on the lease id and, when a receipt is present, on the receipt. Handlers must not interpret receipts. They are the adapter’s private claim identity traveling with the lease.

## At-least-once is a decision, not a footnote

Between t1 and t5, event E may have been processed twice. Worker A might have done the side effect and died before ACK. Worker B will do it again.

That is intentional.

Exactly-once *processing* is not something a library can give you once the handler has touched the world. Exactly-once *delivery claims* are a different, narrower property, and Rheo does not claim them. The contract is:

- every event is delivered at least once to each group
- a stale lease cannot ACK
- expired leases become eligible for redelivery
- handlers must be idempotent on `event.id`

If your side effect cannot be made idempotent, you do not have an ACK problem. You have a side-effect problem. Put a unique constraint on the event id, or record the id you processed before you do the irreversible thing.

## When the handler succeeds and the ACK fails

The timeline above is the crash case. There is a nastier one: the handler returned `:ack`, `Rheo.ack/2` was called, and the backend said something other than `:ok`.

`Rheo.Settle` classifies every settle, renew, and fetch error into a portable vocabulary:

| Class | Runtime policy |
|---|---|
| `:stale_lease` or `:receipt_mismatch` | Lease is lost. Drop it. Do not nack. |
| `:backend_unavailable` or `{:ambiguous, _}` | Leave the lease to expire. The ACK might already be durable. |
| `{:failed, _}` or `{:invalid, _}` | Nack for immediate redelivery. |

The ambiguous case is the one people want to “just retry.” Don’t. If the write timed out, the ACK may have committed. Retrying the ACK with the same token is fine; inventing a nack on top of a possible commit is how you create a hole and a duplicate at the same time. Fencing makes the redelivery safe either way. Telemetry carries the classified reason, not the driver exception.

## Tests that do not sleep

A lease system tested with `Process.sleep(lease_ms + 50)` is a system that will flake in CI and lie on a slow machine. Rheo injects a clock.

`Rheo.Clock.Frozen` lets the suite advance lease time without waiting for the wall. `test/rheo/lease_test.exs` covers stale ACK, expiry, retry, max attempts, and reject that way. If you are building your own backend, this is the first suite that should stay green when you pull the power cord in software.

## What “processed” means

After this article, “we processed the event” should mean three separate facts:

1. A worker ran a handler against a leased event.
2. That worker still held the fencing token when it settled.
3. The group’s committed frontier — not the max sequence anyone has seen — moved past that event.

(3) is Part 12. (1) without (2) is a ghost write. (2) without idempotency is a duplicate that you chose to accept.

Kill the process on purpose and watch the lease move. That is not chaos engineering as theater. That is the smallest demo that proves you built infrastructure.

**Read next:** [Building Rheo as an Elixir/OTP Library](https://thanos.github.io/articles/2026-09-21-rheo-04-rheo-as-otp-library/)

*Docs: [Architecture — delivery](https://rheo.hexdocs.pm/architecture.html) · [ADR 004](https://github.com/thanos/rheo/blob/main/docs/adr/004-lease-and-fencing-model.md)*
