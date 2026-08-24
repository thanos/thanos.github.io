---
title: "From Transactions to Behaviour: MEV Detection with Datalog"
description: "A sandwich attack is three successful swaps. The blockchain never names it. Datalog can — with rules you can test, replay, and explain."
date: 2026-07-29
tags:
  - Datalog
  - Elixir
  - MEV
  - Ethereum
  - DeFi
  - sandwich attack
  - explainable systems
  - ex_datalog
draft: false
authors:
  - Thanos Vassilakis
---

*The chain records events. Behaviour is inferred.*

Alice wants to buy **100 ETH**. She opens her wallet, connects to a decentralized exchange, and gets a quote of **2,000 USDC per ETH**. She clicks **Swap**. A few seconds later the transaction is confirmed.

The contract executed. The tokens arrived. The explorer shows no errors. Later she notices she paid more than she expected, and asks a reasonable question:

> What happened?

An investigator finds three transactions that executed within seconds of one another.

| Order | Wallet | Action | Price |
|------:|--------|--------|------:|
| 1 | Wallet A | Buy 100 ETH | 2,000 USDC |
| 2 | Alice | Buy 100 ETH | 2,020 USDC |
| 3 | Wallet A | Sell 100 ETH | 2,020 USDC |

The blockchain records every one of these. What it does **not** record is whether they are related. It never says “Wallet A manipulated Alice’s trade” or “this was a sandwich attack.” It records three successful swaps.

The explanation lives in the relationship between them.

## What the chain doesn’t tell you

On its own, Wallet A buying 100 ETH is ordinary. Alice buying the same asset is ordinary. Large purchases move prices. The tell is the third leg: Wallet A immediately sells the same quantity it just bought.

Wallet A was not investing in ETH. It bought first at 2,000, let Alice’s order lift the price, then sold at 2,020. Ignoring fees and the pool’s exact curve, the capture is roughly:

```text
(2,020 − 2,000) × 100
= 2,000 USDC
```

That profit came out of Alice’s trade. The pattern is a **sandwich attack**: buy before the victim, let the victim move the market, sell after.

Notice what the ledger actually stored: three transactions, three timestamps, three prices, three successful executions. The sandwich exists only in the **interpretation** of those facts.

Events are recorded. Behaviour is inferred. That distinction is the whole subject.

## Can we teach a computer to see it?

An investigator sees the sequence and thinks: Wallet A bought first, sold immediately afterwards, and profited from Alice’s purchase. That is not a coincidence.

How do we get a machine to the same conclusion?

### Analytics platforms

Blockchain analytics platforms index enormous volumes of data, cluster wallets, visualise flows, and flag suspicious activity. Many already label common MEV patterns. The reasoning that produced the label usually lives inside proprietary software. You see the result. You do not see the logic.

### Large language models

Show the three swaps to a modern model and it will probably say “this appears to be a sandwich attack,” and it will probably be right.

Now ask a regulator: *why?* Can the model prove the conclusion? Would another model reach exactly the same answer tomorrow? Can you write thousands of automated tests against every rule?

Those questions matter the moment a decision has to be explainable and reproducible.

### Datalog

Datalog does not guess. You state the facts, then you state the behaviour as rules.

Facts:

- Wallet A bought ETH.
- Alice bought ETH.
- Wallet A sold ETH.
- The trades occurred in a particular order.
- They involved the same market.

Rule: if these conditions hold, the pattern is a sandwich.

Every conclusion traces back to the facts and the rules that produced it. Nothing is hidden. The reasoning is part of the system. In Elixir that engine is [`ex_datalog`](https://hex.pm/packages/ex_datalog); the worked examples are in [Using ExDatalog](/articles/ex_datalog_examples/).

This piece deliberately writes no Datalog yet. Before teaching a computer to reason, you have to be precise about what it is reasoning *about*.

## More than blockchain

A bank records payments. A trading platform records orders. A hospital records clinical events. A warehouse records inventory movements. Each system stores facts. The behaviours we care about — fraud, compliance breaches, money laundering, supply-chain failures, coordinated attacks — are almost never stored as such. They have to be inferred.

That is why this is not really a cryptocurrency article. Blockchain is a sharp example because every event is public and permanent. The real question is broader: how do we teach computers to recognise behaviour?

## What comes next

The next step is to take raw Ethereum swaps and turn them into a small vocabulary of facts. From those facts, sandwich detection is a handful of rules you can read, test, and replay. Then more MEV patterns, one rule at a time.

The goal is not to store more data. It is to say, in public, what the data means.
