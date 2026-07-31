---
title: "Building a BEAM-native drone controller: processes, UDP, safety, and simulation"
description: "Part 1 of Programming Drones with OTP: why one GenServer per vehicle, how Tello UDP fits the mailbox, how a pure safety pipeline protects flight, and why the simulator is the real development surface."
date: 2026-07-20
tags:
  - Elixir
  - OTP
  - GenServer
  - UDP
  - drones
  - Tello
  - safety
  - simulation
  - telemetry
  - ex_drone

draft: false
series: programming-drones-with-otp
---

Drones look like robotics. On the BEAM they look like processes.

A programmable drone is a stateful actor with a protocol, a mode machine, and a hard requirement that some commands never reach the motors. That is an OTP problem long before it is a PID-control problem. [ex_drone](https://github.com/thanos/ex_drone) is a small Elixir library built around that observation: one supervised GenServer per vehicle, adapters behind a behaviour, a pure safety pipeline in front of every command, and a first-class simulator so you can develop without buying a hospital visit.

This is the first article in *Programming Drones with OTP*. It covers the v0.1.0 foundation—processes, UDP, safety, and simulation. Swarms come next; they only make sense once a single vehicle is honest.

---

## Why BEAM for drones?

Most drone SDKs are thin wrappers around sockets and SDK strings. That is fine until you need:

- isolation between vehicles,
- sequential command handling that matches a request/response radio,
- a restart story when a connection dies,
- a place to put policy that is not sprinkled through `if` statements in demos.

OTP already has names for those things. A GenServer owns state and serializes work through its mailbox. A `DynamicSupervisor` starts and stops vehicles. A `Registry` gives them names you can call from scripts. `:telemetry` gives you observability without inventing a logging API.

The mapping is almost embarrassingly direct:

| Physical concern | OTP shape |
|---|---|
| One drone | One `Drone.Vehicle` GenServer |
| Independent battery / pose / mode | Process-local state |
| One command at a time | Mailbox + `handle_call` |
| Crash or disconnect | Supervision + `:temporary` restart |
| Look up by name | `{:via, Registry, {Drone.Vehicle.Registry, name}}` |

If you have ever wrapped a serial port or a GPIO chip in a GenServer, you already know this design. The novelty is applying it to something that can leave the desk.

---

## Hardware-first is a trap

The fastest way to learn drone APIs is also the worst: open Wi-Fi to a Tello, send `"takeoff"`, hope.

That workflow teaches you almost nothing about failure modes, and it teaches the wrong lesson about safety—namely that safety is something you remember when the room is clear. In ex_drone the simulator is not a toy bolted on after the UDP adapter. It implements the same `Drone.Adapter` behaviour, the same mode machine, and it sits behind the same safety checks.

```elixir
{:ok, drone} = Drone.connect(:sim, name: :demo)
Drone.connect_sdk(drone)
Drone.takeoff(drone)
Drone.move(drone, :forward, 100)
Drone.rotate(drone, :cw, 90)
Drone.land(drone)
Drone.disconnect(drone)
```

When you are ready for hardware, the call site changes by one atom:

```elixir
{:ok, drone} = Drone.connect(:tello, name: :demo)
```

Everything else—missions, safety policy, telemetry—stays put. That is the point of adapters as behaviours.

---

## One drone, one process

`Drone.Vehicle` is the heart of the library. It owns:

- the resolved adapter module and adapter state,
- the safety policy,
- an estimated vehicle state (`mode`, `x/y/z`, `yaw`, `battery`, `flying`).

Public calls go through the `Drone` façade, which looks up the named process and issues a `GenServer.call`. The vehicle never exposes its mailbox as an API surface; scripts talk to `Drone.takeoff/1`, not to `Vehicle` internals.

A trimmed supervision tree looks like this:

```
Drone.Supervisor.Root
  ├── Drone.Vehicle.Registry
  ├── Drone.Swarm.Registry          # used later for v0.2.0
  ├── Drone.Supervisor              # DynamicSupervisor for vehicles
  │     ├── Drone.Vehicle :demo
  │     └── ...
  └── Drone.Swarm.Supervisor
```

Why one process per drone, not one big “fleet GenServer”?

1. **State isolation.** A bad parse or a stuck socket should not take every vehicle with it.
2. **Protocol fidelity.** Tello’s command channel is sequential. A mailbox is a sequential channel.
3. **Naming.** `Drone.takeoff(:demo)` is a teaching API and a production API.
4. **Composition.** Once vehicles are named processes, a swarm coordinator is fan-out plus policy—not a rewrite of the vehicle.

Vehicles use `:temporary` restart. Flying state is not something you casually resurrect from a blank slate; reconnecting is an explicit act.

---

## Adapters: swap the world under the API

```elixir
@callback connect(keyword()) :: {:ok, state()} | {:error, term()}
@callback command(state(), Command.t()) ::
            {:ok, reply, state()} | {:error, reason, state()}
@callback telemetry(state()) :: {:ok, map(), state()} | {:error, term(), state()}
@callback disconnect(state()) :: :ok
```

That is the whole contract. Sim keeps an in-process struct. Tello keeps a UDP socket and connection options. Future Crazyflie or MAVLink adapters only have to speak this dialect.

The public API never branches on hardware:

```
User -> Drone API -> Vehicle -> Safety -> Adapter -> Sim | Tello | ...
```

Safety, missions, and telemetry sit above the adapter line. If a feature only works for one radio, it does not belong in the façade.

---

## UDP and Tello: ASCII over Wi-Fi

The DJI Tello SDK is almost refreshingly rude. You join the drone’s Wi-Fi access point, open UDP to `192.168.10.1:8889`, and send ASCII:

| Intent | Wire |
|---|---|
| Enter SDK mode | `command` |
| Take off | `takeoff` |
| Move | `forward 100` |
| Rotate | `cw 90` |
| Query | `battery?` |
| Kill motors | `emergency` |

No framing. No protobuf. Complexity lives in *state* and *policy*, which is where Elixir is strong.

ex_drone’s Tello connection uses passive sockets on purpose:

```elixir
:gen_udp.open(local_port, [:inet, {:active, false}])
:gen_udp.send(socket, ip, port, command)
:gen_udp.recv(socket, 0, timeout)
```

That pattern matches the radio: send one command, wait for one response (default timeout 10 seconds), then accept the next call. Because the GenServer mailbox already serializes callers, we do not need an active-mode UDP pump fighting `handle_call`. Research notes in the repo discuss `active: :once` for event-driven telemetry streams; the command channel stays synchronous and boring.

Two protocol lessons matter for any BEAM port of this SDK:

- **SDK mode first.** Until `"command"` succeeds, movement is undefined.
- **Do not auto-retry movement.** A lost UDP reply after `forward 100` is ambiguous—did it move? Retrying can double the displacement. Queries and SDK-mode handshakes are the retryable class; motion is not.

---

## Safety as a pure function

Every non-emergency command hits `Drone.Safety.check/3` before the adapter:

```elixir
case Safety.check(cmd, state.safety_policy, state.vehicle_state) do
  {:error, :safety, reason} ->
    # emit [:drone, :safety, :reject], reply error, no adapter call
  {:ok, cmd} ->
    execute_command(cmd, state, [])
  {:ok, cmd, warnings} ->
    # soft warnings (low battery, missing prop guards), then execute
    execute_command(cmd, state, warnings)
end
```

The pipeline is ordered and total. Roughly:

1. Argument ranges (Tello SDK limits: move 20–500 cm, rotate 1–3600°, speed 10–100 cm/s, …)
2. Mode (`:idle` / `:sdk_mode` / `:flying` / `:emergency`)
3. Allowlist, if configured
4. Flying requirements (`:already_flying`, `:not_flying`)
5. Max altitude and max distance from origin
6. Battery hard-reject on takeoff; soft warning on moves
7. Geofence contains-check
8. Prop-guard warning on flips

Returns are boring on purpose:

- `{:ok, command}`
- `{:ok, command, warnings}`
- `{:error, :safety, reason}`

No logging inside the check. No socket. No process dictionary. That means you can unit-test “indoor policy rejects a 5 m climb” without opening Wi-Fi:

```elixir
{:ok, drone} = Drone.connect(:sim, name: :safe, safety: [indoor: true])
Drone.connect_sdk(drone)
Drone.takeoff(drone)
{:error, :safety, :max_altitude} = Drone.move(drone, :up, 500)
```

Indoor preset tightens altitude/distance and raises battery thresholds. Outdoor defaults are looser but still present. Unrestricted mode exists for research and is not the default—defaults should be the thing that keeps fingers attached.

### Emergency and dry-run

Emergency is a separate path. `Drone.emergency/1` does not stroll through the allowlist and altitude math; it goes straight to the adapter and forces vehicle mode to `:emergency`. Soft policy must never trap a kill switch.

Dry-run is the opposite kindness: validate and update estimated state without talking to motors. Useful for classroom walkthroughs and CI.

```
command
  → emergency? ──yes──→ adapter (bypass)
  → Safety.check
       ├─ reject → telemetry + error
       └─ ok → dry_run? → {:ok, :dry_run}
                       → adapter.command → update pose / mode → telemetry
```

---

## Simulator-first internals

`Drone.Adapters.Sim` is a state machine with numbers attached:

```
:idle --sdk_mode--> :sdk_mode --takeoff--> :flying
                         ^                    |
                         +---- land / emergency
```

It tracks pose, yaw-aware motion (yaw `0` faces `+Y`), battery drain, and cumulative flight time. Takeoff settles at `z: 30` cm to mirror Tello’s hover height. You can seed battery, inject `failure_rate` or `fail_commands`, and place multiple sims in a shared world with `initial_x` / `initial_y` / `initial_yaw`—the same knobs swarm formations will need later.

The educational claim is strong: **if a mission is unsafe in sim under a given policy, it is unsafe on hardware under that policy.** The simulator does not invent a friendlier physics. It refuses the same climbs.

---

## Telemetry for physical systems

Physical systems fail quietly if you only `Logger.info` in demos. ex_drone emits standard `:telemetry` events, including:

- `[:drone, :connect, :start]` / `[:drone, :connect, :stop]`
- `[:drone, :command, :start]` / `[:drone, :command, :stop]` / `[:drone, :command, :error]`
- `[:drone, :safety, :reject]` (and warning events)
- `[:drone, :emergency]`

Attach handlers in tests or wire LiveDashboard / StatsD in an app. The library stays thin; observability is a subscription, not a fork.

---

## Missions: scripts, not threads

Once commands are data, sequences become data:

```elixir
mission =
  Drone.Mission.new(name: "square")
  |> Drone.Mission.sdk_mode()
  |> Drone.Mission.takeoff()
  |> Drone.Mission.move(:forward, 100)
  |> Drone.Mission.rotate(:cw, 90)
  |> Drone.Mission.move(:forward, 100)
  |> Drone.Mission.rotate(:cw, 90)
  |> Drone.Mission.move(:forward, 100)
  |> Drone.Mission.rotate(:cw, 90)
  |> Drone.Mission.move(:forward, 100)
  |> Drone.Mission.land()

{:ok, _results} = Drone.Mission.run(mission, :demo)
```

A mission is an ordered list of `Drone.Command` values executed against a named vehicle. It does not bypass safety. It does not invent parallelism. It is a readable script you can print, test, and later hand to a swarm planner as a per-drone artifact.

---

## What this design already buys you for swarms

v0.2.0 adds `Drone.Swarm`, formations, and fail-fast fan-out. Almost none of that required rethinking the vehicle:

- vehicles were already named and supervised,
- safety was already local,
- sims already accepted world-frame offsets,
- missions were already pure command lists.

The slogan for the next article is already latent here: **shared coordination, local enforcement.** The swarm orchestrates; each vehicle still runs the safety pipeline. OTP models the software swarm well. Physics and sensing still constrain the hardware swarm—and we will be honest about that when we get to Tellos that cannot hold absolute choreography.

In [part 2](/articles/02-otp-drone-swarms/) we take that composition seriously: thin swarm coordinators, Registry vs membership, fail-fast partial results, formations as planners, the Good/Bad Advisor demo, and where [Nerves](https://nerves-project.org/) fits as a companion-computer destination—not as a replacement for PX4 or ArduPilot.

---

## Try it

```elixir
# mix.exs
{:ex_drone, "~> 0.2.0"}
```

Start in the simulator. Tighten an indoor policy until a careless climb fails. Attach a telemetry handler and watch rejects. Only then join a Tello AP—with prop guards on, people out of the arc, and a finger ready for `Drone.emergency/1`.

Drones are not metaphors. The BEAM just happens to be a good place to keep the metaphors from becoming accidents.

---

## References and further reading

### ex_drone

- [ex_drone on Hex](https://hex.pm/packages/ex_drone) and [HexDocs](https://hexdocs.pm/ex_drone)
- [Source repository](https://github.com/thanos/ex_drone)
- In-repo guides: [Architecture](https://github.com/thanos/ex_drone/blob/main/docs/architecture.md), [Safety](https://github.com/thanos/ex_drone/blob/main/docs/safety.md), [Simulator](https://github.com/thanos/ex_drone/blob/main/docs/simulator.md), [Tello](https://github.com/thanos/ex_drone/blob/main/docs/tello.md), [Getting Started](https://github.com/thanos/ex_drone/blob/main/docs/getting_started.md)
- Design notes: [Safety pipeline](https://github.com/thanos/ex_drone/blob/main/docs/design/safety_pipeline.md), [Adapter contract](https://github.com/thanos/ex_drone/blob/main/docs/design/adapter_contract.md), [Telemetry events](https://github.com/thanos/ex_drone/blob/main/docs/design/telemetry_events.md)
- Research notes: [Tello SDK](https://github.com/thanos/ex_drone/blob/main/docs/research/tello_sdk.md), [BEAM UDP](https://github.com/thanos/ex_drone/blob/main/docs/research/beam_udp.md), [Safety model](https://github.com/thanos/ex_drone/blob/main/docs/research/safety_model.md), [Simulator design](https://github.com/thanos/ex_drone/blob/main/docs/research/simulator_design.md)

### Tello and classroom hardware

- [DJI Tello SDK 2.0 User Guide (PDF)](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf) — official command and response reference
- [Ryze Tello](https://www.ryzerobotics.com/tello) — hardware overview and EDU variants
- Local aviation / recreational UAS rules for your region (FAA or equivalent)

### BEAM, OTP, and telemetry

- [OTP Design Principles](https://www.erlang.org/doc/system/design_principles.html)
- [Elixir GenServer](https://hexdocs.pm/elixir/GenServer.html), [Registry](https://hexdocs.pm/elixir/Registry.html), [DynamicSupervisor](https://hexdocs.pm/elixir/DynamicSupervisor.html)
- [`:telemetry`](https://hexdocs.pm/telemetry/)
- Armstrong, J. *Programming Erlang*. Pragmatic Bookshelf.
- Cesarini, F., and Vinoski, S. *Designing for Scalability with Erlang/OTP*. O’Reilly.

### Safety

- Leveson, N. G. *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press, 2011.
- ISO 12100:2010 — Safety of machinery: general principles for design and risk assessment
- [ASTM Committee F38](https://www.astm.org/get-involved/technical-committees/committee-f38) — unmanned aircraft systems standards

### Geometry, missions, and later platforms

- LaValle, S. M. *Planning Algorithms*. Cambridge University Press, 2006. Free online: [lavalle.pl/planning](http://lavalle.pl/planning/)
- Craig, J. J. *Introduction to Robotics: Mechanics and Control*. Pearson.
- Roadmap context (not yet shipped in the single-vehicle story): [Bitcraze Crazyflie docs](https://www.bitcraze.io/documentation/), [MAVLink](https://mavlink.io/en/)
- Embedded Elixir / companion hosting: briefly, [Nerves](https://nerves-project.org/) boots the BEAM on small Linux systems; ex_drone’s v1.0 roadmap includes a Pi + Tello guide. Architecture trade-offs (GCS vs companion vs autopilot) are covered in [part 2](/articles/02-otp-drone-swarms/).

Next: [Why OTP is a natural model for drone swarms](/articles/02-otp-drone-swarms/). For a head start on the code, see the in-repo [swarm](https://github.com/thanos/ex_drone/blob/main/docs/swarm.md) and [formations](https://github.com/thanos/ex_drone/blob/main/docs/formations.md) guides.
