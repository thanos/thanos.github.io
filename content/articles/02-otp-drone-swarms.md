---
title: "Why OTP is a natural model for drone swarms"
description: "Part 2 of Programming Drones with OTP: thin swarm coordinators, Registry vs membership, fail-fast fan-out, formations as planners, local safety, Good/Bad Advisor, and where Nerves fits as a companion—not an autopilot."
date: 2026-07-31
tags:
  - Elixir
  - OTP
  - GenServer
  - drones
  - swarms
  - formations
  - safety
  - simulation
  - Nerves
  - embedded Elixir
  - MAVLink
  - ex_drone

draft: false
series: programming-drones-with-otp
---

A swarm is not one robot with many propellers. It is several concurrent actors that share a plan and fail independently.

That sentence is why OTP keeps showing up in multi-drone software. In [part 1](/articles/01-beam-native-drone-controller/) we built a single honest vehicle: one GenServer, a pure safety pipeline, UDP to Tello, and a simulator that refuses the same climbs as hardware. [ex_drone](https://github.com/thanos/ex_drone) v0.2.0 does not invent a second architecture for groups. It adds a thin coordinator on top of the same vehicles.

This article is about that coordinator—and about what OTP does *not* buy you in the air.

---

## Recap: one drone, one GenServer

Each vehicle already owns:

- adapter I/O (sim or Tello),
- estimated pose and mode,
- `Drone.Safety.check/3` before motors,
- a name in `Drone.Vehicle.Registry`.

If you centralize all of that into one “fleet GenServer,” you fight the problem:

- commands to different drones serialize behind one mailbox,
- a choreography bug can take every vehicle’s state machine with it,
- adapters with different latency profiles share one bottleneck.

OTP’s better fit is the boring one: **keep one Vehicle process per drone**, then add a sibling that knows membership and group operations.

```
Drone.Swarm  -->  Drone.takeoff(:good)
             -->  Drone.takeoff(:bad)
```

The swarm orchestrates. The vehicles execute and enforce safety.

---

## The coordinator pattern

`Drone.Swarm` is a GenServer, but a thin one. It does not own sockets. It does not reimplement altitude checks. It holds an ordered member list, default formation options, and fan-out policy.

Under the application root:

```
Drone.Supervisor.Root (:one_for_one)
├── Drone.Vehicle.Registry
├── Drone.Swarm.Registry
├── Drone.Supervisor              # DynamicSupervisor → Vehicles
└── Drone.Swarm.Supervisor        # DynamicSupervisor → Swarms
```

Vehicles and swarms are siblings. A swarm crash does not restart airframes; killing a vehicle does not take down the coordinator. Both use `:temporary` restart—group flight state is not something you casually resurrect from a blank slate.

```elixir
{:ok, swarm} =
  Drone.Swarm.start(
    name: :advisors,
    members: [
      {:good, adapter: :sim, initial_x: -50},
      {:bad, adapter: :sim, initial_x: 50, safety: [max_altitude_cm: 50]}
    ]
  )

Drone.Swarm.connect_sdk(swarm)
{:ok, _} = Drone.Swarm.takeoff(swarm)
```

That `takeoff/1` is not magic synchronization. It is explicit fan-out.

---

## Registry vs membership

v0.1.0 already solved vehicle identity: `Drone.takeoff(:good)` looks up a Registry entry. Swarms do not invent a second naming system for drones. They need something else:

1. an **ordered membership list** (who is in this group, in what order),
2. optional naming for the swarm process itself (`Drone.Swarm.Registry`).

That split mirrors distributed systems: Registry is service discovery; swarm state is cluster membership.

There is a third store for a reason. On application start, ex_drone creates a public ETS table, `Drone.Swarm.Members`. Normal group ops go through the swarm GenServer mailbox. **Emergency does not.** `Drone.Swarm.emergency/1` runs in the caller, reads membership from ETS, and best-effort stops every vehicle—even if the coordinator is busy inside a long `run/2`. A kill switch that waits behind choreography is not a kill switch.

---

## Fan-out, fail-fast, and partial results

Group operations return a map of per-member outcomes:

```elixir
{:ok, %{good: :ok, bad: :ok}}
# or
{:error, :partial, %{good: :ok, bad: {:error, reason}}}
```

Default policy is `:fail_fast`: sequential calls (deterministic in tests), halt on first error, **do not silently undo** members that already succeeded. If one of three takeoffs works, two stay on the ground and one is flying until you `land` or `emergency`. That is uncomfortable—and correct. Robotics groups fail partially; pretending otherwise teaches the wrong recovery story.

Lesson for the classroom: **group success is an aggregation policy, not a boolean.** Partial failure is the normal hard case.

---

## Formations are planners, not pilots

Classic shapes—`:front`, `:column`, `:vee`, `:diamond`, `:echelon`, `:circle`—are pure functions in `Drone.Formation`:

```
positions + heading + spacing
  → {:ok, %{drone => Mission}}
  | {:error, reason}
```

They emit missions the existing DSL already understands. They do not run control loops. They do not hold slots against wind. The default reference is the centroid (or an explicit origin)—not a living leader process. An optional `leader:` is a **plan-time pose snapshot**, not mid-flight follow-the-leader.

At plan time, `min_separation_cm` (default 80) applies Reynolds’ Separate rule to the *target slots*. Paths between slots are not deconflicted. Live Align / Cohere, closed-loop hold, morphing, and leader election are intentional non-goals for v0.2.0—see the [deferred catalogue](https://github.com/thanos/ex_drone/blob/main/docs/design/v0_2_0_deferred.md).

```elixir
{:ok, _} = Drone.Swarm.run(swarm, :front)
{:ok, _} = Drone.Swarm.land(swarm)
```

`run/2` also accepts a map of per-drone missions or a function of the member list. Formations are one convenient producer of those maps.

---

## Shared coordination, local enforcement

Centralizing safety only in the swarm would be a mistake. Members can differ: battery, indoor vs outdoor policy, geofence, prop guards. v0.2.0 keeps `Drone.Safety` on every Vehicle and adds only plan-time separation in Formation.

Educational punchline: **shared coordination, local enforcement.**

The coordinator may ask everyone to climb. The vehicle with `max_altitude_cm: 50` still says no.

---

## Good Advisor / Bad Advisor

The runnable teaching demo is `examples/good_bad_advisor.exs` (`mix run examples/good_bad_advisor.exs`). Two sims share a swarm. `:bad` carries a tight altitude cap.

```elixir
good =
  Drone.Mission.new()
  |> Drone.Mission.move(:forward, 40)
  |> Drone.Mission.hover(seconds: 1)

bad =
  Drone.Mission.new()
  |> Drone.Mission.move(:up, 200)

{:error, :partial, results} =
  Drone.Swarm.run(swarm, %{good: good, bad: bad})

# results.good == :ok
# results.bad == {:error, {:safety, :max_altitude}}
```

Observers should notice three things:

1. **Process isolation** — bad’s reject does not crash good’s GenServer.
2. **Partial results** — the swarm return value names winners and losers.
3. **Simulator-first** — you can rehearse multi-drone failure before any Wi-Fi AP is involved.

Open Observer. You should see two Vehicles and one Swarm. Ask the hard question: if takeoff succeeds for one of three, who lands the orphan? (You do. The library will not invent a silent undo.)

---

## Hardware honesty: software swarm ≠ physics swarm

Stock Tello networking and the lack of a shared global pose make absolute formations unreliable outdoors or across multiple APs. Tello EDU station mode helps **connectivity**, not **localization**. You can fan out `"takeoff"` over UDP. You cannot honestly claim centimeter slot-holding without sensing the library does not provide.

So the boundary is sharp:

> **OTP models the software swarm; physics and sensing still constrain the hardware swarm.**

OTP solves process identity, supervision, messaging, and failure boundaries. It does not solve mid-air physics. Claiming otherwise is how demo videos become incident reports.

---

## Where this wants to live: embedded Elixir and Nerves

Today, the natural home for ex_drone is a **ground-station BEAM**: a laptop or GCS process tree talking UDP to sims or Tellos. That is what v0.2.0 ships and tests.

The same OTP shape wants a second home on the edge. [Nerves](https://nerves-project.org/) is the Elixir project’s toolkit for building small embedded Linux images that boot the Erlang VM early and let an OTP application take over—not a general-purpose distro bolted onto a Pi after the fact ([getting started](https://hexdocs.pm/nerves/getting-started.html), [github.com/nerves-project/nerves](https://github.com/nerves-project/nerves)). A Nerves application *is* an OTP supervision tree. That is the entire point.

Three architectures, only one of which is ex_drone’s present tense:

| Architecture | Role of the BEAM | Status |
|---|---|---|
| **A. Ground-station BEAM** | Swarm + Vehicles on a laptop/GCS; radios to vehicles | **Shipped** (sim + Tello) |
| **B. Nerves companion computer** | BEAM on an SBC beside a real autopilot; policy, missions, links, video | **Roadmap** (ex_drone v1.0 checklist: Nerves + Pi + Tello guide) |
| **C. Autopilot replacement** | Elixir in the inner attitude loop | **Out of scope** — wrong layer |

Option B is the industrially honest pattern. Flight controllers such as [PX4](https://docs.px4.io/) or [ArduPilot](https://ardupilot.org/) own hard real-time estimation and motor mixing. A companion SBC speaks [MAVLink](https://mavlink.io/en/) over UART or UDP for missions, telemetry, and higher-level policy. The BEAM is excellent at that companion layer: supervised links, fan-out, safety allowlists, OTA-friendly releases. It is a poor substitute for a purpose-built autopilot firmware loop.

The ecosystem is already exploring the edges of this. Damir Batinović’s NervesConf / Goatmire talk [*Fly me a camera*](https://video.goatmire.com/v/w5vve) (summary: [Elixir Merge](https://elixirmerge.com/p/streaming-live-video-from-drones-using-elixir)) combines Nerves packaging, Membrane video pipelines, and drone control on the BEAM—control and streaming in one OTP application, on embedded hardware. Projects such as [colibri-cam’s Nerves ground-station images](https://github.com/colibri-cam/nerves_system_rpi5_gs) show the same gravitational pull: Elixir at the ground station or companion, not as a drop-in PX4.

[NervesHub](https://www.nerves-hub.org/) adds a different “fleet” metaphor—firmware updates and device health across many embedded nodes. That is orthogonal to geometric formations, and useful to keep straight in class: **device fleets ≠ airframe formations**.

ex_drone’s README lists a Nerves integration guide under v1.0.0. Until that lands, treat companion hosting as a destination for this process model, not a feature checkbox in 0.2.0.

```
Laptop / Nerves GCS          Companion SBC (Nerves)         Flight controller
─────────────────────        ──────────────────────         ─────────────────
Drone.Swarm                  Vehicle adapters / links       PX4 / ArduPilot
Drone.Vehicle × N            safety policy, missions        attitude / motors
     │                              │                              │
     └──────── Wi‑Fi / radio ───────┴──────── MAVLink / UART ──────┘
```

Same supervision ideas at every tier. Different real-time budgets.

---

## Looking ahead (intentionally deferred)

Do not read the following as “coming next week.” They are catalogued non-goals for v0.2.0 ([full list](https://github.com/thanos/ex_drone/blob/main/docs/design/v0_2_0_deferred.md)):

- live Separate / Align / Cohere flocking,
- closed-loop formation hold and morphing,
- leader election and mid-run replan,
- neighbor-aware collision checks in flight,
- async fan-out and alternate aggregation policies (`:best_effort`, `:all_or_nothing`),
- multi-node distributed swarms,
- Crazyflie / MAVLink multi-vehicle adapters,
- real-hardware localization good enough for absolute slots,
- Nerves packaging and an on-Pi Tello guide.

Keeping the surface small is what makes the teaching story true: Observer can show the processes; the sim can show the partial failure; the safety reject is local.

---

## Try it

```elixir
{:ex_drone, "~> 0.2.0"}
```

```bash
mix run examples/good_bad_advisor.exs
```

Change the bad advisor’s `max_altitude_cm`. Inject `failure_rate` on a sim member. Watch fail-fast leave a successful peer flying until you land it. Then—and only then—think about radios.

OTP is a natural model for drone swarms because swarms were always concurrent systems with partial failure. The BEAM did not invent that. It just refuses to let you paper over it.

---

## References and further reading

### Prior article and ex_drone

- Part 1: [Building a BEAM-native drone controller](/articles/01-beam-native-drone-controller/)
- [ex_drone on Hex](https://hex.pm/packages/ex_drone) · [HexDocs](https://hexdocs.pm/ex_drone) · [source](https://github.com/thanos/ex_drone)
- Guides: [Swarms](https://github.com/thanos/ex_drone/blob/main/docs/swarm.md), [Formations](https://github.com/thanos/ex_drone/blob/main/docs/formations.md), [Architecture](https://github.com/thanos/ex_drone/blob/main/docs/architecture.md)
- Design: [v0.2.0 deferred work](https://github.com/thanos/ex_drone/blob/main/docs/design/v0_2_0_deferred.md), [Telemetry events](https://github.com/thanos/ex_drone/blob/main/docs/design/telemetry_events.md)
- Research: [Swarm coordination](https://github.com/thanos/ex_drone/blob/main/docs/research/swarm_coordination.md)
- Demo: [`examples/good_bad_advisor.exs`](https://github.com/thanos/ex_drone/blob/main/examples/good_bad_advisor.exs)

### OTP

- [OTP Design Principles](https://www.erlang.org/doc/system/design_principles.html)
- [GenServer](https://hexdocs.pm/elixir/GenServer.html), [Registry](https://hexdocs.pm/elixir/Registry.html), [DynamicSupervisor](https://hexdocs.pm/elixir/DynamicSupervisor.html)
- Cesarini, F., and Vinoski, S. *Designing for Scalability with Erlang/OTP*. O’Reilly.
- Armstrong, J. *Programming Erlang*. Pragmatic Bookshelf.

### Swarming and formation control

- Reynolds, C. W. “Flocks, Herds, and Schools: A Distributed Behavioral Model.” *Computer Graphics* (SIGGRAPH), 1987.
- Balch, T., and Arkin, R. C. “Behavior-based formation control for multirobot teams.” *IEEE Transactions on Robotics and Automation*, 14(6), 1998.
- Brambilla, M., et al. “Swarm robotics: a review from the swarm engineering perspective.” *Swarm Intelligence*, 7, 2013.
- Oh, K.-K., Park, M.-C., and Ahn, H.-S. “A survey of multi-agent formation control.” *Automatica*, 53, 2015.
- Ren, W., and Beard, R. W. *Distributed Consensus in Multi-vehicle Cooperative Control*. Springer, 2008.
- LaValle, S. M. *Planning Algorithms*. Cambridge University Press, 2006. [lavalle.pl/planning](http://lavalle.pl/planning/)

### Embedded Elixir, Nerves, and companions

- [Nerves Project](https://nerves-project.org/) — embed the BEAM on small Linux systems
- [Nerves getting started](https://hexdocs.pm/nerves/getting-started.html)
- [nerves-project/nerves](https://github.com/nerves-project/nerves)
- [NervesHub](https://www.nerves-hub.org/) — firmware fleet management (orthogonal to flight formations)
- Batinović, D. [*Fly me a camera*](https://video.goatmire.com/v/w5vve) — Nerves + Membrane + drone control/video (NervesConf / Goatmire); [Elixir Merge summary](https://elixirmerge.com/p/streaming-live-video-from-drones-using-elixir)
- [colibri-cam `nerves_system_rpi5_gs`](https://github.com/colibri-cam/nerves_system_rpi5_gs) — Nerves system image oriented as a camera/drone ground station
- [MAVLink](https://mavlink.io/en/), [PX4](https://docs.px4.io/), [ArduPilot](https://ardupilot.org/) — autopilot / companion protocol stack (ex_drone does not replace the inner loop)
- [Bitcraze Crazyflie documentation](https://www.bitcraze.io/documentation/) — planned multi-vehicle platform direction

### Tello caveats

- [DJI Tello SDK 2.0 User Guide (PDF)](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
- [Ryze Tello](https://www.ryzerobotics.com/tello) — EDU station mode helps connectivity, not shared global pose
