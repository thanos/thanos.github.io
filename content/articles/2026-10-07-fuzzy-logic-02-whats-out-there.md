---
title: "Fuzzy Logic, What's out there?"
description: "A survey of fuzzy-logic libraries: MATLAB, FuzzyLite, Python, Julia, Rust, Elixir, and Zig — and why a fuzzy extension to ex_datalog may be the most interesting gap."
date: 2026-10-09
tags:
  - fuzzy logic
  - FuzzyLite
  - MATLAB
  - Elixir
  - Rust
  - Zig
  - Julia
  - Datalog
draft: true
authors:
  - Thanos Vassilakis
series: fuzzy-logic
---

This is part 2 of [Fuzzy Logic](https://thanos.github.io/series/fuzzy-logic/).

# Fuzzy Logic, What's out there?

I looked at the current ecosystem, and it is more alive than I expected. The interesting finding is that **Python/C++/MATLAB have mature fuzzy ecosystems, Julia has an unusually good modern implementation, while Rust, Elixir and especially Zig have substantial room for a serious library.**

### Current landscape

| Language / library | Mamdani | Sugeno/TSK | Type-2 | Rule DSL | FCL/FIS import | Maturity | My view |
|---|---:|---:|---:|---:|---:|---|---|
| MATLAB Fuzzy Logic Toolbox | ✅ | ✅ | ✅ | ✅ | `.fis` | ★★★★★ | Reference commercial implementation |
| C++ FuzzyLite | ✅ | ✅ | some/other variants | ✅ | FCL/FIS | ★★★★★ | Best mature embeddable engine |
| Python scikit-fuzzy | ✅ | partial | limited | ✅ | — | ★★★★ | Best-known OSS scientific toolkit |
| Python Simpful | ✅ | ✅ | — | **excellent** | — | ★★★★ | Very nice rule-oriented API |
| Julia FuzzyLogic.jl | ✅ | ✅ | ✅ | **excellent** | FCL/FML/FIS | ★★★★½ | Perhaps best modern OSS design |
| Java jFuzzyLogic | ✅ | ✅ | — | ✅ | **FCL** | ★★★★ | Mature, standards-oriented, aging |
| Rust fuzzy-logic-rs | ✅ | planned | planned | basic | planned | ★★ | Promising but immature |
| Elixir `flex` | ✅/basic FLS | limited | — | basic | — | ★★ | Small, little ecosystem |
| Zig | — | — | — | — | — | ★ | **Essentially an open field** |

A few deserve closer examination.

### 1. MATLAB — still the benchmark

[MATLAB Fuzzy Logic Toolbox](https://www.mathworks.com/products/fuzzy-logic.html?utm_source=chatgpt.com) is considerably more sophisticated than a historical fuzzy-controller package. The current version supports Mamdani and Sugeno, type-1 and interval type-2 systems, fuzzy trees, tuning/optimization and even fuzzy systems for explaining black-box AI models. [MathWorks](https://www.mathworks.com/help/fuzzy/types-of-fuzzy-inference-systems.html?utm_source=chatgpt.com)

It's arguably the feature reference against which a new implementation should be measured.

**Strengths:** extremely complete, visualization, Simulink integration, tuning, type-2, mature tooling.

**Weaknesses:** proprietary, heavy, not something you'd naturally embed into a server or low-level application.

---

### 2. C++ — FuzzyLite is probably the strongest OSS implementation

[FuzzyLite](https://github.com/fuzzylite/fuzzylite?utm_source=chatgpt.com) is impressive. It implements six controller styles including Mamdani, Takagi-Sugeno, Larsen and Tsukamoto; 25 linguistic terms; many T/S norms; seven defuzzifiers; hedges; and import/export of FCL, MATLAB FIS and its own FLL format. [GitHub](https://github.com/fuzzylite/fuzzylite?utm_source=chatgpt.com)

It also produces C++/Java representations and builds as static/shared libraries.

This would be my **reference implementation for an engine**.

One caveat is licensing: GPLv3 or a commercial license. [GitHub](https://github.com/fuzzylite/fuzzylite?utm_source=chatgpt.com)

---

### 3. Python — biggest practical OSS ecosystem

[scikit-fuzzy](https://github.com/scikit-fuzzy/scikit-fuzzy?utm_source=chatgpt.com) is the obvious name. It integrates naturally with NumPy/SciPy and provides membership functions, defuzzification, fuzzy mathematics, intervals, fuzzy C-means and control systems. [GitHub](https://github.com/scikit-fuzzy/scikit-fuzzy?utm_source=chatgpt.com)

But I actually find [Simpful](https://github.com/aresio/simpful?utm_source=chatgpt.com) more interesting architecturally for what we're discussing.

It supports Mamdani and arbitrary-order Sugeno reasoning and allows rules resembling:

```text
IF (Temperature IS hot)
AND (Humidity IS wet)
THEN (FanSpeed IS fast)
```

That's much closer to a **knowledge/rule system** than numerical-array programming. [GitHub](https://github.com/aresio/simpful?utm_source=chatgpt.com)

So:

**scikit-fuzzy:** better scientific toolkit.

**Simpful:** better inspiration for an expressive fuzzy rule engine.

---

### 4. Julia — FuzzyLogic.jl is the surprise winner

I would definitely study [FuzzyLogic.jl](https://github.com/lucaferranti/FuzzyLogic.jl?utm_source=chatgpt.com) before designing anything.

It supports:

- Mamdani
- Sugeno
- Type-1
- Type-2
- multiple membership/inference algorithms
- a human-readable Julia DSL
- IEC 61131-7 FCL
- IEEE 1855 Fuzzy Markup Language
- MATLAB `.fis` [GitHub](https://github.com/lucaferranti/FuzzyLogic.jl?utm_source=chatgpt.com)


That's an unusually good combination of **modern language design + standards + mathematical completeness**.

For API inspiration I'd rank:

**FuzzyLogic.jl → Simpful → FuzzyLite → MATLAB**

rather than blindly copying scikit-fuzzy.

---

## Now the three languages you're particularly interested in

### Rust

The ecosystem exists, but it's surprisingly immature.

One current implementation is [fuzzy-logic-rs](https://github.com/MohammadAminSadat/fuzzy-logic-rs?utm_source=chatgpt.com). It is `std`-only and currently describes Mamdani Type-1 as completed, while Type-2, TSK, serialization, ANFIS, fuzzy C-means and other capabilities remain future work. [GitHub](https://github.com/MohammadAminSadat/fuzzy-logic-rs?utm_source=chatgpt.com)

That's a big gap.

Rust is arguably **an ideal language for a modern fuzzy engine** because fuzzy evaluation can be:

```text
no GC
no runtime
no allocation in inference path
deterministic
SIMD-able
no_std capable
WASM capable
embedded capable
FFI friendly
```

Imagine a mature Rust crate with:

```rust
let risk = fuzzy! {
    exposure: {
        small  => triangle(0., 0., 100_000.),
        medium => triangle(50_000., 500_000., 2_000_000.),
        large  => sigmoid(1_000_000., 0.00001)
    }

    rule {
        exposure.is(large) & activity.is(unusual)
            => risk.is(high)
    }
};
```

That could be genuinely useful.

**Opportunity: very high.**

---

### Elixir

There actually is a Hex package: [`flex` on Hex](https://hex.pm/users/valiot?utm_source=chatgpt.com).

It's currently version 0.2.2 with only around a thousand historical downloads. It describes itself as a toolkit for fuzzy variables, fuzzy sets and rules for constructing fuzzy logic systems. [Hex](https://hex.pm/users/valiot?utm_source=chatgpt.com)

So there isn't what I would call a substantial Elixir fuzzy ecosystem.

But Elixir presents a *different* opportunity from Rust.

I wouldn't build Elixir fuzzy logic primarily for motor controllers. I'd build it for:

**knowledge representation and rule processing.**

This is where your Datalog work becomes relevant.

Imagine extending a Datalog-like language from:

```prolog
high_risk(X) :-
    exposure(X, E),
    E > 1000000.
```

toward:

```text
large_exposure(X) ~ 0.82
unusual_activity(X) ~ 0.67

high_risk(X) :-
    large_exposure(X),
    unusual_activity(X).
```

And allow:

```text
AND     min(a,b)
OR      max(a,b)
NOT     1-a

VERY(x) x²
SOMEWHAT(x) sqrt(x)
```

Now you're approaching **fuzzy Datalog**, rather than merely implementing another HVAC controller.

That is much more interesting to me.

---

### Zig

This was the starkest result: I couldn't identify a significant, established Zig fuzzy-logic library comparable to any of the above.

That makes Zig an almost clean slate.

And fuzzy logic is extremely well suited to Zig:

```text
embedded
real-time
deterministic
no hidden allocation
C ABI
microcontrollers
SIMD
tiny binaries
cross compilation
```

A Zig engine could reasonably aim for something like:

```text
libfuzzyzig

        ↓

C ABI
 ├── Zig
 ├── C/C++
 ├── Rust
 ├── Python
 └── Elixir NIF
```

But I'd question whether that's worth doing if a high-quality Rust implementation already provides the same low-level role.

---

## What I would build

This is where I think it intersects unusually well with your existing work.

I **wouldn't create three independent fuzzy libraries**.

I'd separate fuzzy mathematics from fuzzy reasoning:

```text
                 ┌───────────────────────┐
                 │     Rule / Logic      │
                 │                       │
                 │ Elixir / Datalog DSL  │
                 │ explanations          │
                 │ provenance            │
                 └──────────┬────────────┘
                            │
                     fuzzy predicates
                            │
                 ┌──────────▼────────────┐
                 │    Fuzzy Engine       │
                 │                       │
                 │ membership functions  │
                 │ Mamdani / Sugeno      │
                 │ norms                 │
                 │ inference             │
                 │ defuzzification       │
                 └──────────┬────────────┘
                            │
                       Rust or Zig
```

I'd probably choose **Rust for the core** rather than Zig because Cargo, documentation, testing, WASM and library distribution make it much easier to establish an ecosystem. Zig would make sense later if ultra-small embedded deployment becomes important.

Elixir then becomes the **reasoning/orchestration layer**, potentially integrated with `ex_datalog`.

And that's where this stops being "yet another fuzzy logic library."

You could represent facts such as:

```text
market_data_mismatch(trade_123) = 0.83
curve_difference(trade_123)     = 0.91
large_pnl_break(trade_123)      = 0.72
```

and infer:

```text
likely_curve_issue(T) :-
    market_data_mismatch(T),
    curve_difference(T),
    large_pnl_break(T).
```

with an associated truth degree and, importantly, **a complete derivation explaining where that degree came from**.

That starts to look extremely relevant to your P&L reconciliation and supervision ideas: LLMs extract qualitative evidence; fuzzy membership represents vagueness; Datalog performs explicit inference; provenance explains the conclusion.

### My ranking

For **using fuzzy logic today**, I'd choose **FuzzyLogic.jl** for experimentation, **Simpful/scikit-fuzzy** for Python/data science, **FuzzyLite** for mature C++ deployment, and MATLAB for industrial engineering environments.

For **building something new**, however, my ranking changes:

**1. Elixir + `ex_datalog` fuzzy extension — most intellectually interesting**  
**2. Rust — biggest general-purpose ecosystem opportunity**  
**3. Rust core + Elixir reasoning layer — probably the strongest overall architecture**  
**4. Zig — technically elegant but smaller potential audience**

In particular, I think there may be a surprisingly good **`ex_datalog` 0.x feature hiding here: fuzzy predicates / fuzzy Datalog**. That's worth investigating separately, because fuzzy Datalog is an established research area and we should see what semantics already exist rather than inventing our own.

Next: [who is using it in 2026](/articles/2026-10-07-fuzzy-logic-03-who-is-using-it/).