---
title: "A Bank-Wide Digital Asset Platform"
description: "Organize it as a banking capability rather than a blockchain project: which activities, which controls, and which books-and-records model."
date: 2026-06-06
tags:
  - digital assets
  - banking
  - custody
  - tokenization
  - OSFI
  - Basel
  - architecture
draft: false
authors:
  - Thanos Vassilakis
---

I was recently asked what a friend needed to set up a setup a digital asset platform for his bank.

Here are some thoughts:


For a Canadian federally regulated bank, this framing is particularly timely. OSFI stated on September 10, 2026 that the technology does not determine the legal nature of the product—for example, a tokenized deposit remains a deposit—and expects institutions to engage their lead supervisor before launching novel products or services. [OSFI](https://www.osfi-bsif.gc.ca/en/news/statement-tokenized-other-digitally-represented-deposits)'s crypto-asset capital and liquidity framework is already effective for 2026, with the updated 2027 guideline just published. [Basel]( https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/capital-liquidity-treatment-crypto-asset-exposures-banking-guideline-2027)'s crypto-asset prudential and disclosure standards are also now effective from [January 1, 2026](https://www.bis.org/committees/bcbs/basel-framework/standard/dis/55/inforce/2026-01-01/published/2024-07-17?utm_source=chatgpt.com).

## I would make these your primary workstreams

| # | Workstream | What you need to establish |
|---|---|---|
| 1 | **Business scope & product taxonomy** | Exactly what the platform will support |
| 2 | **Legal/regulatory perimeter** | What each asset/activity legally represents |
| 3 | **Governance & risk appetite** | Who can approve assets, networks, counterparties and activities |
| 4 | **Target operating model** | Front-to-back ownership and operational processes |
| 5 | **Asset/network/venue onboarding** | Formal admission criteria for tokens, chains and counterparties |
| 6 | **Custody & key management** | Wallets, keys, signing, recovery and segregation |
| 7 | **Ledger & transaction architecture** | Bank books and records, positions, settlement and reconciliation |
| 8 | **Financial-crime controls** | KYC/KYB, sanctions, blockchain analytics and transaction monitoring |
| 9 | **Accounting / capital / liquidity / reporting** | GL treatment and regulatory consequences |
| 10 | **Enterprise integration** | Payments, treasury, GL, risk, IAM, data, case management |
| 11 | **Security, resilience & third-party risk** | Cyber, smart-contract risk, operational resilience and vendors |
| 12 | **Controlled product rollout** | Narrow MVP → production capabilities |

The most important part of **#1** is to stop "digital assets" from becoming one bucket. Create an explicit taxonomy such as:

**Tokenized traditional assets**
→ bonds, funds, equities, repo, collateral

**Tokenized bank liabilities**
→ tokenized deposits

**External stablecoins**
→ USDC-like instruments

**Native crypto-assets**
→ BTC, ETH, etc.

**CBDCs / wholesale settlement assets**

**Bank-issued assets**
→ securities, deposits, structured products

Then separately list the activities:

**issue → mint → distribute → custody → transfer → trade → settle → redeem → burn → collateralize → finance**

That matrix becomes the foundation of the entire program.

---

## The architectural task I would start very early

Do **not** design a giant "crypto platform."

Design a **Digital Asset Control Plane** with blockchain/network adapters underneath it.

Something approximately like:

```text
                    Channels / Clients / Trading
                              │
                         Bank APIs
                              │
                ┌─────────────────────────┐
                │ Digital Asset Platform  │
                │                         │
                │ Asset Registry          │
                │ Account / Wallet Model  │
                │ Policy Engine           │
                │ Transaction Orchestrator│
                │ Entitlements            │
                │ Position / Ledger       │
                │ Lifecycle Engine        │
                │ Reconciliation          │
                └────────────┬────────────┘
                             │
              ┌──────────────┼───────────────┐
              │              │               │
          Custody        Compliance       Network
          / HSM / MPC    / AML / KYT      Adapters
              │              │               │
              │              │       ┌───────┼─────────┐
              │              │       │       │         │
              │              │    Ethereum  Solana   Private
              │              │                ...      DLT
              │              │
        ─────────────────────────────────────────────
                       Enterprise Bank
        GL │ Treasury │ Risk │ Payments │ Data │ IAM
```

One architectural principle I would make non-negotiable:

> **The blockchain should normally be a settlement/network domain, not the bank's only system of record.**

Maintain a bank-grade internal representation of accounts, ownership, balances, transactions and accounting events and continuously reconcile it against on-chain state. There are exceptions where the legally authoritative ownership register itself is distributed, but even there your accounting, control and regulatory reporting architecture needs an internal representation.

That decision alone avoids a great deal of trouble later.

## The hardest workstream is probably custody

Before choosing technology, define the **custody model**.

You need decisions around omnibus versus segregated wallets; hot, warm and cold tiers; MPC versus HSM-based signing; key generation; key ceremony; recovery; backup; transaction limits; whitelisting; dual/multi-party authorization; emergency freeze; compromised-key procedures; forks and airdrops; staking; fee/gas management; and sub-custodians.

This is also an area where regulators have been actively clarifying expectations. US regulators issued joint safekeeping risk-management guidance in July 2025, emphasizing existing safe-and-sound banking and risk-management principles. The [OCC](https://occ.treas.gov/news-issuances/bulletins/2025/bulletin-2025-17.html) has separately confirmed that national banks can provide custody and execution services and can use sub-custodians, subject to appropriate third-party [risk management](https://www.occ.treas.gov/news-issuances/news-releases/2025/nr-occ-2025-42.html).

The important architectural consequence is that **wallet ≠ account ≠ customer ≠ asset position**. Keep those concepts separate in your domain model.

## Make asset admission a product

I'd create an **Asset & Network Registry** very early.

For every supported asset it should know things such as:

```text
Asset
 ├─ Legal classification
 ├─ Issuer
 ├─ Instrument type
 ├─ Network(s)
 ├─ Contract address
 ├─ Token standard
 ├─ Currency / denomination
 ├─ Custody eligibility
 ├─ Trading eligibility
 ├─ Client eligibility
 ├─ Jurisdiction restrictions
 ├─ Basel / OSFI classification
 ├─ Capital treatment
 ├─ AML risk classification
 ├─ Price source
 ├─ Valuation rules
 └─ Lifecycle rules
```

And do the same for **networks**.

You don't simply "support Ethereum." You approve particular network environments and define required confirmations, finality assumptions, node/provider configuration, fork policy, validator risk, smart-contract requirements, gas policy and outage procedures.

That registry then feeds your policy engine automatically.

## Financial crime deserves its own platform capability

Don't bolt Chainalysis/TRM/Elliptic onto the end.

Your transaction flow should be closer to:

```text
Instruction
    ↓
Identity / entitlement
    ↓
Policy checks
    ↓
Sanctions
    ↓
Address screening
    ↓
Transaction / exposure analysis
    ↓
Risk decision
    ↓
Human approval if necessary
    ↓
Sign
    ↓
Broadcast
    ↓
Confirmation/finality
    ↓
Ledger
    ↓
Continuous monitoring
```

You'll need **pre-transaction** and **post-transaction** controls.

I'd also build an abstraction layer around blockchain-intelligence providers so that the rest of the bank doesn't become coupled to one vendor. That gives you the option of introducing your own analytics and investigation capability later.

## Accounting and reconciliation should be first-class components

This is an area where I would expect a bank to have an advantage over crypto-native organizations.

Every blockchain transaction should eventually produce understandable banking events:

```text
Blockchain transaction
        ↓
Canonical Digital Asset Event
        ↓
Business event
        ↓
Position movement
        ↓
Accounting event
        ↓
Debit / Credit
        ↓
GL
```

And independently:

```text
Internal position
        ↕
Custodian position
        ↕
On-chain position
        ↕
GL balance
```

You want automated **four-way reconciliation** where applicable.

This also lets you keep the blockchain-specific weirdness out of the GL and downstream finance systems.

Basel now explicitly requires banks with cryptoasset exposures to classify exposures and report capital, accounting and liquidity information, so building this metadata and reporting lineage into the asset model from the beginning is valuable.

---

## What I would do in the first 90 days

Rather than starting a huge implementation, I'd aim to produce six things.

**1. Digital Asset Charter**

Define what the platform is and isn't.

For example:

> A common bank platform for issuance, safekeeping, movement, settlement and lifecycle management of tokenized and digitally represented financial assets across approved networks.

That is much more useful than calling it a "crypto platform."

**2. Product × Activity × Jurisdiction matrix**

Something like:

| | Custody | Transfer | Trade | Issue | Settle | Collateral |
|---|---:|---:|---:|---:|---:|---:|
| Tokenized deposit | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| Tokenized bond | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Stablecoin | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| BTC/ETH | ✓ | ✓ | ? | — | ✓ | ? |

Then overlay Canada / US / UK / EU / etc.

**3. Canonical domain model**

Define Asset, Instrument, Network, Account, Wallet, Address, Position, Transaction, Instruction, Settlement, Custodian, Counterparty and AccountingEvent.

This will pay for itself repeatedly.

**4. Reference architecture**

Especially the boundary between:

**bank domain ↔ custody domain ↔ blockchain domain.**

**5. Control framework**

Every transaction should have a machine-readable trail explaining:

> who initiated it → who approved it → what policies were evaluated → what sanctions/KYT checks ran → which key signed it → what was transmitted → where it settled → what accounting entries resulted.

**6. One narrow end-to-end implementation**

I would deliberately choose something boring.

For example:

> **Tokenized deposit or tokenized cash + one permissioned customer + one network + transfer + redemption + reconciliation + GL posting.**

Get this whole path working:

```text
Client
  ↓
Instruction
  ↓
Policy
  ↓
AML/KYT
  ↓
Wallet
  ↓
Network
  ↓
Settlement
  ↓
Reconciliation
  ↓
GL
  ↓
Regulatory/audit evidence
```

Once that works, adding another asset or blockchain should largely become an **adapter + policy + asset configuration problem**, rather than another bespoke system.

## One thing I would resist

I would resist organizing the program as:

> Blockchain team  
> Custody team  
> Tokenization team  
> Stablecoin team  
> Crypto trading team

You will end up building five platforms.

Instead, build shared primitives:

**Identity → Asset Registry → Policy → Wallet/Custody → Transaction → Ledger → Settlement → Reconciliation → Compliance → Reporting**

and let custody, tokenized deposits, securities, collateral, stablecoins and eventually crypto trading become products assembled from those capabilities.
