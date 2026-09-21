---
title: "Killing Consumers on Purpose"
description: "If killing the worker loses the message, you built a demo, not infrastructure."
date: 2026-09-21
tags:
  - Rheo
  - Elixir
  - OTP
  - event-sourcing
  - distributed-systems
  - LiveDashboard
draft: true
authors:
  - Thanos Vassilakis
series: rheo
---

This is part 7 of [Rheo](https://thanos.github.io/series/rheo/). If killing the worker loses the message, you built a demo, not infrastructure.

Messaging infrastructure that cannot survive a killed worker is not infrastructure. It is a happy-path script with a supervision tree glued on.

The correct demo is rude:

1. Fetch leases for the `risk` group.
2. Kill the consumer process before ACK.
3. Advance lease time — or wait for expiry, if you enjoy watching clocks.
4. Another consumer obtains the same event.
5. ACK succeeds.

That flow ships as `mix rheo.demo`. Run it. Then run it again with the process kill on a different line. If step 4 ever fails to produce the event, you have a bug in fencing, expiry, or materialization. If step 5 succeeds with the *old* lease id, you have a worse bug: the dead worker can still commit.

## Crash is the common case

In OTP, crash is how you recover. `handle_event/2` raises? The task dies, the lease is released for redelivery, the Group keeps running. The node is SIGKILL’d? Every inflight lease expires and another node’s Group — on Postgres or Redis — takes them.

The design is only honest if those two sentences are true without a human running `Rheo.replay/3`. Replay is for “we shipped a bad handler and need the history again.” Expiry is for “the process vanished.” Mixing them up trains operators to treat every crash as an incident.

## Frozen clocks, not sleeps

The regression suite encodes the same invariant without wall-clock sleeps. `Rheo.Clock.Frozen` lets a test say “the lease is now expired” the way a good time library lets you say “it is Monday.” If your backend tests `Process.sleep/1` their way to expiry, they will pass on your laptop and fail in CI on a loaded runner.

This is not optional rigor. Lease expiry *is* the crash recovery path. A flaky test here is a flaky production story.

## What you should see

After the kill:

- the dead process is gone from the supervisor, or has been restarted empty
- the event is not missing from the log (it was never going to be)
- the group’s delivery for that event is `available` or newly `leased`, not stuck `leased` forever
- `Rheo.lag/3` still reports a hole until the new worker settles
- a stale ACK from a resurrected pid returns `:stale_lease`

If lag goes to zero because the crashed worker “must have been done,” you are using max-acked-sequence as progress. Part 12 exists to stop you.

## Kill it in the demo, then kill it in the test, then kill it in staging

The Livebook demos and `mix rheo.demo` are the first pass. The contract suite is the second. The third is a staging node with `lease_ms` short enough that you can watch LiveDashboard flip an inflight count back to zero and a lag number stay honest.

LiveDashboard is read-only on purpose. You do not ACK from a chart. You look, then you replay or you fix the handler.

![Rheo group health in Phoenix LiveDashboard — lag, inflight, dead letters](https://thanos.github.io/images/rheo/Rheo-Screenshot-LiveDashboard.jpg)

*Rheo’s LiveDashboard page: lag, inflight, dead letters. Inspect, don’t settle.*

Next: the reason you kept the events around while you were busy killing processes.

**Read next:** [Searching the Stream](https://thanos.github.io/articles/2026-09-21-rheo-08-searching-the-stream/)

*Docs: [Ops guide](https://rheo.hexdocs.pm/ops.html) · Livebook demos*
