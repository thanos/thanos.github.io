---
title: "Rikiddo Scoring Rule"
description: "The Rikiddo scoring rule** is a **specialized automated market maker (AMM) mechanism for prediction markets, designed to improve on classic models like LMSR."
date: 2026-04-14
tags:
- Blockchain
- Crypto
- Cryptocurrency
- DeFi
- Finance
- Fintech

draft: false
---

# Rikiddo Scoring Rule

The **Rikiddo scoring rule** is a **specialized automated market maker (AMM) mechanism for prediction markets**, designed to improve on classic models like LMSR by making pricing:

- more **capital efficient**
- more **adaptive to liquidity**
- more **stable under large trades**

It’s most closely associated with Gnosis / GnosisDAO research.

---

# First: What is a “scoring rule” market maker?

A **scoring rule** is a mathematical function that:

> rewards traders based on how accurate their probability estimates are.

In markets, this becomes:

- You “move” probabilities
- You pay a cost to do so
- If you're right → profit

---

## Canonical baseline: LMSR

The classic model is the **Logarithmic Market Scoring Rule (LMSR)**:

C(q) = b * log( sum_i exp(q_i / b) )

Where:
- q_i = shares for outcome *i*  
- b = liquidity parameter  

---

## Problem with LMSR

- Fixed liquidity parameter b
- Either:
  - too expensive → no trading  
  - too cheap → market maker risk explodes  

---

# Enter Rikiddo

**Rikiddo** is a **dynamic scoring rule** that:

> adapts liquidity based on market conditions (volume, uncertainty, participation)

---

# Core idea

Instead of fixed b, Rikiddo:

- adjusts pricing sensitivity dynamically
- reacts to:
  - trading volume
  - market entropy
  - participation levels

---

## Intuition

- Early market (low liquidity) → **gentle price movement**
- Active market → **tighter spreads, more confidence**
- Large trades → **controlled slippage**

---

# Conceptual model

Traditional LMSR:
- fixed curvature

Rikiddo:
- adaptive curvature (breathes with the market)

---

# What it improves

## 1. Capital efficiency
- Requires less locked capital than LMSR

## 2. Price stability
- Avoids extreme swings from small liquidity

## 3. Better early-stage markets
- Bootstrap liquidity without huge subsidies

---

# Comparison

| Feature | LMSR | Rikiddo |
|--------|------|---------|
| Liquidity parameter | Fixed | Dynamic |
| Capital efficiency | Low | Higher |
| Early market behavior | Fragile | Stable |
| Adaptivity | None | High |
| Complexity | Simple | More complex |

---

# Deep insight

Rikiddo is essentially:

> A **feedback-controlled AMM**

Where:

- the **pricing function adapts based on system state**

This is very different from:
- AMMs → static curves  
- vAMMs → static formula + funding  

Rikiddo introduces:

- **control theory into market design**

---

# Connection to systems thinking

## 1. Like a dynamic aggregation structure
- LMSR = static
- Rikiddo = adaptive weighting over time

## 2. Like a liquidity system with feedback
- liquidity becomes a **function of participation**

## 3. Similar to sketches
- not exact
- optimized for:
  - responsiveness
  - bounded risk
  - efficiency



# Trade-offs

## Pros
- More efficient
- Better UX for traders
- Lower capital requirements

## Cons
- Harder to reason about
- Requires tuning
- Less battle-tested than LMSR

---

# Where it fits

## Ideal for:
- prediction markets
- low-liquidity environments
- long-tail event markets

## Less ideal for:
- high-frequency trading
- deep, liquid markets

---

# Bottom line

> **Rikiddo is an adaptive scoring-rule market maker that dynamically adjusts liquidity to improve efficiency and stability in prediction markets.**
