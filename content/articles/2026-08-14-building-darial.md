---
title: "Coding an LLM gateway: the Darial journey"
description: "This is a walk through how Darial 0.1 was designed and built: the problem that forced the shape, the decisions we recorded as ADRs, the libraries we actually shipped, and the trade-offs we accepted."
date: 2026-08-14
tags:
- Rust
- LLM
- Gateways
- HTTP
- Caddy
- Docker
draft: false
---


# Coding an LLM gateway: the Darial journey

This is a walk through how Darial 0.1 was designed and built: the problem that forced the shape, the decisions we recorded as ADRs, the libraries we actually shipped, and the trade-offs we accepted. It is not a substitute for the [architecture](https://github.com/latentmeta/darial/blob/main/docs/architecture.md), [threat model](https://github.com/latentmeta/darial/blob/main/docs/threat-model.md), or [privacy](https://github.com/latentmeta/darial/blob/main/docs/privacy.md) docs. Those remain the source of truth. This is the story of why they look the way they do.

Darial is a **privacy-preserving, provider-neutral LLM gateway** in Rust. Approved applications talk to a local OpenAI-compatible API on loopback. Darial authenticates authorized use, applies policy and DLP, and routes only to administrator-configured providers. It is an authorized gateway, not a proxy, VPN, or firewall bypass.

## 1. The problem that set the architecture

The motivating path was personal, not an enterprise SSO diagram:

```text
OpenCode / Tidewave
    -> local agent on 127.0.0.1
    -> corporate firewall
    -> Darial gateway (HTTPS on an allowlisted hostname)
    -> OpenAI (or Anthropic / Gemini)
```

Coding agents want an OpenAI-shaped `/v1/chat/completions`. The network wants a single identifiable HTTPS hostname on 443. The operator wants provider keys off the laptop, prompts out of logs, and a last chance to redact secrets before anything leaves the workstation.

That path killed several tempting designs immediately:

- A **transparent proxy / SOCKS / CONNECT tunnel** would be the wrong product and the wrong ethics. Clients must not pick destinations. Upstream URLs come only from gateway config.
- A **pure cloud reverse proxy** would still leave the editor talking to a remote OpenAI URL, so keys and prompts would sit in the tool’s config.
- **In-process TLS in the gateway binary** would make local CA and Caddy integration harder than “HTTP internally, Caddy on 443.”
- **OIDC on day one** would have blocked the actual user. A scoped bearer token is enough for a single-operator gateway. Redis rate limits would have added a second process nobody needed.

So 0.1 optimized for: one binary, loopback agent, Caddy in front of the gateway, in-memory quotas, honest crypto labeling.

## 2. How we built it (the milestone path)

We wrote the docs and ADRs before the HTTP server. That sounds ceremonial until you try to implement “privacy” without an observer matrix. The order was:

| Milestone | What we actually shipped |
|-----------|--------------------------|
| 0 | Architecture, protocol skeleton, threat model, privacy matrix, ADRs, typed config, `tracing`, CI |
| 1 | Canonical IR + mock provider vertical slice: agent → gateway → mock |
| 2 | SSE streaming, backpressure, cancellation, OpenAI / Anthropic / Gemini adapters |
| 3 | Tools and bounded images through the IR (transported, never executed), deterministic DLP |
| 4 | Private buffered mode: HPKE envelopes, content-blind relay |
| 5 | Deploy: Compose + Caddy, Apple Container, Homebrew tap + `brew services`, crates.io packaging |
| 6 | Protected streaming: experimental flag only, off by default |

The important sequencing choice was **mock first**. Live provider adapters are easy to get wrong (streaming, refusals, tool JSON). A deterministic mock let us freeze the IR and the OpenAI-compatible agent surface before we spent tokens on `api.openai.com`.

The other sequencing choice was **direct mode before private mode**. Direct mode is the path people will run. Private mode is a narrower trust split (relay sees IP and sizes, gateway sees content). Building HPKE first would have delayed a usable gateway for a feature that is still review-pending.

## 3. Architecture decisions

### 3.1 One package, one binary, three roles

[ADR 0001](https://github.com/latentmeta/darial/blob/main/docs/adr/0001-single-package.md): a single Cargo package, executable `darial`, roles via `darial agent` / `darial relay` / `darial gateway`. Modules, not crates. Not an SDK.

**Pros**

- One release unit, one lockfile, one audit surface.
- Protocol types are shared by construction. You cannot drift `canonical_ir` between “agent crate 0.1” and “gateway crate 0.2.”
- Operators install one binary. Homebrew formulae wrap the same artifact with different `brew services` plists.

**Cons**

- You cannot depend on `darial` as a library without pulling the whole gateway. That is intentional; we still pay for it in compile time.
- Role-specific dependencies (HPKE, Prometheus exporter) land in every build.
- A future “agent-only tiny binary” would need a feature-flag split we deliberately did not do in 0.1.

A Cargo workspace of `darial-agent`, `darial-gateway`, `darial-protocol` would have looked more “professional” and would have been worse for a first release: three versions, three publish steps, and a temptation to pretend we have an SDK.

### 3.2 Canonical IR instead of “just speak OpenAI everywhere”

[ADR 0002](https://github.com/latentmeta/darial/blob/main/docs/adr/0002-canonical-ir.md): the gateway’s native language is a versioned IR (`ir_version`, capability negotiation). The agent speaks OpenAI Chat Completions on loopback and translates at the edge. Adapters translate IR → provider JSON. Provider-specific extensions may live in namespaced fields; they cannot override routing or security fields. Unsupported features fail with `unsupported_capability` unless an explicit compatibility policy says `strip`.

**Pros**

- Policy, DLP, quotas, and telemetry run on one model, not three JSON dialects.
- Adapters stay thin: map roles, system messages, finish reasons, then call `reqwest`.
- We can reject Anthropic-only or Gemini-only quirks instead of silently dropping them.

**Cons**

- Two translations on the hot path (OpenAI JSON ↔ IR ↔ provider JSON). Latency is small compared with the model; complexity is not.
- The OpenAI-compatible subset will always lag the real OpenAI API. That is documented as a non-goal, but users will still hit it.
- IR versioning is a compatibility tax. Gateways must reject unknown majors (fail closed, no silent downgrade).

The alternative — pass OpenAI JSON through unchanged and only adapt at the last hop — looks simpler until you try to apply DLP to tool arguments and still route to Anthropic.

### 3.3 Loopback-default agent

[ADR 0003](https://github.com/latentmeta/darial/blob/main/docs/adr/0003-loopback-default.md): bind `127.0.0.1` / `::1` by default. Non-loopback requires `allow_non_loopback = true` and a loud warning. Production profile refuses it without the flag. Optional local bearer even on loopback; unauthenticated loopback is a `dev` profile footgun we still allow because `curl` during development should not need a lecture.

**Pros**

- Avoids the classic “LLM proxy on `0.0.0.0:8080`” disaster (DNS rebinding, roommate on Wi-Fi, lateral movement).
- Matches the actual use case: the editor and the agent share a machine.

**Cons**

- A remote agent (agent on a jump host, editor elsewhere) is out of scope. You would need mTLS or a local SSH tunnel, which we did not build.
- IPv6-only and dual-stack quirks are now config problems.

### 3.4 TLS at Caddy, HTTP inside

The gateway listens for HTTP. Production HTTPS is Caddy (or any ordinary terminator). The agent verifies TLS with WebPKI plus optional `tls.additional_roots` for a local Caddy CA. Verification is never silently disabled.

**Pros**

- Certificate issuance, HTTP/2, and ACME stay in a tool that already does them well.
- The Rust process does not need to reload PEM files on every Let’s Encrypt rotation.
- Enterprise MITM / corporate roots are “add a PEM,” not “we invented a trust store.”

**Cons**

- Two processes in a real deploy. Misconfigure Caddy and you think Darial is down.
- It is possible to accidentally publish `:8443`. Compose does not; docs have to keep saying so.
- In-process rustls would have made `darial gateway serve` a one-binary HTTPS server for tiny installs. We chose operability over that convenience.

### 3.5 Direct mode vs private buffered mode

[ADR 0004](https://github.com/latentmeta/darial/blob/main/docs/adr/0004-private-mode.md): two privacy profiles.

**Direct:** agent → gateway → provider. The network sees the gateway hostname. The gateway sees prompts. Simple, streaming, what 0.1 is for.

**Private buffered:** agent → relay → gateway with HPKE (RFC 9180) envelopes, framing inspired by Oblivious HTTP (RFC 9458). The relay is honest-but-curious: client IP, sizes, timing, ciphertext — not plaintext. The gateway decrypts and still sends plaintext to the provider. Collusion between relay and gateway defeats the IP/content split; that is a documented residual risk, not a bug we forgot.

**Pros of splitting the roles**

- You can put the relay in a different administrative domain than the gateway.
- The relay implementation is small: forward configured URL, strip hop-by-hop headers, never decrypt.

**Cons**

- Buffered mode means the full response exists before the agent sees it. Latency and memory are worse than SSE. That is why protected **streaming** is experimental and off.
- Unlinkability is weaker than Privacy Pass. MVP puts short-lived bearer tokens *inside* the envelope so the relay cannot steal them, but the gateway can still link requests by token for quotas. We said so in [privacy.md](https://github.com/latentmeta/darial/blob/main/docs/privacy.md) rather than claiming anonymity.
- HPKE framing is Darial-specific until we have interoperability vectors against a real OHTTP stack. Review is pending; 0.1 must not market this as 1.0-stable crypto.

We did not invent a KEM. Suite is X25519 / HKDF-SHA256 / AES-128-GCM. AAD binds protocol version, direction, key id, and gateway origin so a response ciphertext cannot be replayed as a request.

### 3.6 Policy, quotas, and fail-closed behavior

No job queue. Over limit → 429 or 503 immediately. In-memory rate limiter and replay cache on a single gateway process. Concurrency is a `tokio::sync::Semaphore`.

**Pros**

- Fail closed is easier to reason about than a disk-backed prompt queue (which would be a retention bug waiting to happen).
- No Redis for a single-operator deploy.

**Cons**

- Horizontal scale of the gateway is not “add a replica and share state.” Two gateways have two quota counters. Fine for 0.1; not fine for a fleet.
- Replay protection is bounded and best-effort across restarts.

OIDC, Redis, and malware scanners were deferred on purpose ([ADR 0005](https://github.com/latentmeta/darial/blob/main/docs/adr/0005-mvp-scope.md)).

### 3.7 DLP on the agent, not only on the gateway

Deterministic regex DLP runs on the workstation before egress: allow / warn / redact / block. Findings record locations and categories, not the secret itself.

**Pros**

- A leaked `sk-…` key can die on loopback, before HPKE, before Caddy, before the provider.
- Rules are auditable. No cloud DLP vendor in the path.

**Cons**

- Regex is not a classifier. It will miss novel secrets and will false-positive on examples in this very repository unless tests are careful.
- DLP on the gateway as well would catch a compromised agent; we did not duplicate the engine there in 0.1.

Tools are **transported**, never executed. Darial is not an agent runtime. That keeps the threat model smaller: we do not run curl-from-the-model on the gateway host.

## 4. Libraries: what we picked and what we paid

Deny `unsafe_code` at the package level. MSRV 1.75. Release profile: LTO, one codegen unit, stripped symbols, `panic = "abort"`. That last one means no unwinding through secrets in frames; it also means a panic is a hard crash, so we avoid panics on the request path.

### Runtime and HTTP

| Crate | Role | Why | Cost |
|-------|------|-----|------|
| **tokio** | Async runtime | Default for this class of server; signals, timers, `Semaphore` | Feature flags need discipline; we enabled `rt-multi-thread`, not the kitchen sink |
| **axum 0.8** | Agent, relay, gateway HTTP | Extractors, SSE, `Router` composition, stays close to `hyper` | 0.7 → 0.8 API churn; we took 0.8 and lived with it |
| **tower / tower-http** | Timeouts, body limits, trace, tight CORS on the agent | Policy as middleware instead of ad-hoc `if` | Easy to over-layer; CORS is deny-by-default on purpose |
| **hyper 1** | Server HTTP/1 | Axum’s foundation | HTTP/2 to clients is Caddy’s job in production |
| **reqwest 0.12** (rustls, no default features) | Outbound to gateway, relay, providers | rustls avoids linking OpenSSL; `redirect: none` so a 302 cannot bounce us to a surprise host | rustls + corporate MITM needs `tls.additional_roots`; native-tls would have used the OS store more automatically |

We could have used `actix-web`. Axum won because the type-oriented extractors match how we wanted errors to flow (`DarialError` → public JSON body with no prompt echo).

We could have used OpenSSL via `native-tls`. rustls is easier to audit in a cargo tree and matches “never disable verify.” The con is local Caddy CA: you must add the root PEM. That is the right con.

### Serialization, CLI, errors

| Crate | Role | Why | Cost |
|-------|------|-----|------|
| **serde / serde_json** | IR, wire, OpenAI JSON | Inevitable | Alloc-heavy on large tool payloads; we bound body size (default 4 MiB) |
| **toml 0.8** | Config files | Human-editable, matches examples | Nested tables get noisy; env overlay (`DARIAL_*`) is the escape hatch |
| **clap 4 derive** | Subcommands | `agent serve`, `gateway key generate`, `check-config` | Compile-time; worth it |
| **thiserror + anyhow** | `thiserror` in the library, `anyhow` at the CLI edge | Typed `ErrorCode` for the wire; anyhow for “print and exit” | Two error styles in one package. A purist would pick one. Operators care about `ErrorCode`. |

### Security-ish crates

| Crate | Role | Why | Cost |
|-------|------|-----|------|
| **hpke 0.12** | RFC 9180, X25519 | Do not invent KEMs | API is low-level; we wrap it. Not byte-compatible OHTTP |
| **secrecy / zeroize** | Tokens and HPKE private keys | Best-effort wipe | Zeroization is not a guarantee against swap, cores, or compiler elision. We say so. |
| **subtle** | Constant-time compares where we remember | Token compare should not be `==` on a String | Easy to forget on a new path |
| **sha2 / hmac / hex / base64** | Token hashing, envelope encoding | Boring | Keep them boring |
| **rand 0.8** + `OsRng` | HPKE keygen | OS entropy | rand 0.9 exists; we stayed on 0.8 with the rest of the tree |

### DLP, telemetry, tests

| Crate | Role | Why | Cost |
|-------|------|-----|------|
| **regex + once_cell** | DLP rules | Deterministic, no ML weights | See DLP cons above |
| **tracing + tracing-subscriber** | Structured logs | JSON in production, pretty in dev, env-filter | You must never log request bodies. Culture + code review, not a crate |
| **metrics + metrics-exporter-prometheus** | Counters without prompts | `/metrics` on a separate bind | Do not put model names that are actually prompt prefixes into labels |
| **uuid / chrono** | `request_id`, `created_at`, replay window | Protocol §3 | Clock skew ±120s is a policy, not a library |
| **wiremock / proptest / tempfile** | Tests | Mock providers and property tests on IR | Live tests are `DARIAL_LIVE_TESTS=1` and ignored by default so CI never spends money or leaks keys |

`async-trait` is still here because `ProviderAdapter` is a trait with async methods. Edition 2024 / RPITIT could retire it later; 0.1 did not need that fight.

## 5. Design tensions we did not pretend to resolve

**Compatibility vs honesty.** Tools expect OpenAI. Providers are not OpenAI. The IR is the adult in the room. The agent lies a little (it looks like OpenAI). The gateway does not (it speaks Darial protocol with `Darial-Protocol: 1`).

**Privacy vs inference.** The provider must see plaintext. Anyone who wants “the model cannot read my prompt” needs a different product (encrypted inference research, local models). We wrote that in the README so a badge row could not bury it.

**Privacy vs quotas.** Strong unlinkability fights per-tenant rate limits. 0.1 chose quotas. Privacy Pass remains a 1.x idea.

**Fail closed vs helpfulness.** Unknown protocol version, bad HPKE, empty allowlist, TLS verify off in production: refuse. Users will call this unfriendly. The alternative is a silent downgrade to “just HTTP to wherever.”

**Single process quotas vs ops reality.** In-memory limits match a Homebrew-started gateway on a Mac Mini. They do not match Kubernetes with three replicas. We shipped k8s sketches anyway and left Redis out of the critical path.

## 6. Deployment: what 0.1 actually supports

There is no special Homebrew registry. **crates.io is the release.** Homebrew formulae in this repo download the crate tarball and compile it. Docker images wrap the same binary. Pick one path.

### Native / Homebrew (workstation agent + maybe local gateway)

Good when the editor and the agent must share loopback.

```text
brew tap latentmeta/darial https://github.com/latentmeta/darial.git
brew install darial darial-agent darial-gateway
brew services start darial-gateway
brew services start darial-agent
```

Agent: `http://127.0.0.1:8080`. Gateway: `http://127.0.0.1:8443` until you put Caddy on 443. Point OpenCode/Tidewave at the agent base URL and a local bearer that matches `DARIAL_LOCAL_TOKEN`.

**Pros:** no Docker, `brew services` maps to launchd. **Cons:** first compile is slow; you need a Rust toolchain via the `rust` formula.

`cargo install darial --locked` is the same binary without service wrappers.

### Docker Compose + Caddy (the intended “real” gateway)

```text
OpenCode -> 127.0.0.1:8080 (agent)
         -> https://gateway.example:443 (Caddy)
         -> gateway:8443 (not published)
         -> api.openai.com
```

Ask IT to allowlist the Caddy hostname on 443. Publish the egress inventory (`deploy/egress-inventory.json`) with the ticket. Do not ask them to allowlist the world.

**Pros:** TLS looks like every other internal HTTPS app. **Cons:** you now operate Caddy, Compose, and secrets in `.env` (never commit it).

### Apple Container

Same OCI image, `container` CLI on Apple silicon. Useful if you refuse Docker Desktop and still want the Compose-shaped split.

### What we did not deploy

- In-binary Let’s Encrypt
- Sidecar service mesh assumptions
- Multi-region failover mid-stream (explicit non-goal: no failover after streaming starts)

## 7. Usage ideas

These are intended uses, all assuming authorization and an allowlisted hostname where traffic leaves the machine.

**Personal coding agent.** OpenCode or Tidewave → local agent → company-approved gateway → one provider. Keys live in the gateway environment, not in the editor. DLP catches the AWS key you pasted into a prompt.

**Shared team gateway, personal agents.** Each laptop runs `darial agent`. One gateway behind Caddy. Tokens scoped per human. Disable private mode if the security team does not want a relay.

**Air-gapped demo / CI.** Mock provider, `examples/gateway.toml`, no network. `check-config` in CI already validates the sample files. Use this in unit tests of *your* agent harness without buying tokens.

**Split-trust private mode.** Relay in a DMZ (sees IPs). Gateway in a tighter zone (sees prompts, holds provider keys). Only useful if those operators will not share logs. If they will, just use direct mode; the HPKE tax buys nothing.

**Policy choke point.** Even without private mode, the gateway is where you restrict models, block tools, cap concurrency, and turn on JSON logs that contain request ids and token counts — not completions.

**Local-only loop.** Gateway and agent on the same Mac, mock or a personal OpenAI key, Caddy with an internal CA. This is how you debug the agent’s OpenAI dialect before you file the allowlist ticket.

Do **not** use Darial to: tunnel arbitrary HTTP, hide SNI, dodge TLS inspection, or point at a provider the admin did not configure. The software will not help you; the license and [ACCEPTABLE_USE.md](../ACCEPTABLE_USE.md) are not decorative.

## 8. What we would change after a crypto review (and what we would not)

After an independent look at `crypto_envelope.rs` and the AAD transcript, 1.0 might: freeze or replace the OHTTP-inspired framing with a library that has external vectors; add padding policy that is still honest about traffic analysis; consider Privacy Pass if unlinkability becomes a real requirement.

We would not: add a general proxy, execute tools on the gateway, log prompts “just for a week,” or skip Caddy in the recommended production path.

The libraries we would think twice about are not axum or serde. They are **regex-as-DLP** (replace or augment with a real secret scanner) and **in-memory quotas** (optional Redis or a shared limiter when someone actually runs two gateways).

## 9. Pointers

| If you want… | Read |
|--------------|------|
| Boxes and trust boundaries | [architecture.md](https://github.com/latentmeta/darial/blob/main/docs/architecture.md) |
| MUST/SHOULD wire behavior | [protocol.md](https://github.com/latentmeta/darial/blob/main/docs/protocol.md) |
| Observer matrix | [privacy.md](https://github.com/latentmeta/darial/blob/main/docs/privacy.md) |
| Who we designed against | [threat-model.md](https://github.com/latentmeta/darial/blob/main/docs/threat-model.md) |
| Install | [installation.md](https://github.com/latentmeta/darial/blob/main/docs/installation.md), [containers.md](https://github.com/latentmeta/darial/blob/main/docs/containers.md) |
| Allowlisting | [enterprise-deployment.md](https://github.com/latentmeta/darial/blob/main/docs/enterprise-deployment.md) |
| Recorded decisions | [adr/](https://github.com/latentmeta/darial/blob/main/docs/adr/) |
| What 0.1 still is not | [implementation-status.md](https://github.com/latentmeta/darial/blob/main/docs/implementation-status.md) |

The code is one package under `src/`. Start at `main.rs` (roles), then `canonical_ir.rs`, then `agent/` and `gateway/`. The relay is deliberately the boring file.
