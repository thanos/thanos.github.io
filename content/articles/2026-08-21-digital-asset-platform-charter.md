---
title: "Digital Asset Platform Charter"
description: "Architecture, operating model and common services for treating digital assets as a banking capability rather than a blockchain project."
date: 2026-08-21
tags:
  - digital assets
  - banking
  - architecture
  - custody
  - tokenization
  - charter
  - operating model
draft: false
authors:
  - Thanos Vassilakis
---

*Architecture, Operating Model and Common Services*

---

## Executive Summary

Digital assets are moving from experimentation into the core agenda of financial institutions. Tokenized deposits, tokenized securities, stablecoins, digital collateral, native crypto-assets, and new forms of blockchain-based settlement all introduce opportunities to reduce friction, improve asset mobility, accelerate settlement, and create new client services.

For a bank, however, the central challenge is not simply connecting to a blockchain or selecting a custody provider. The harder problem is incorporating digital assets into the disciplines that already govern financial services: legal ownership, client accounts, entitlements, custody, transaction authorization, compliance, settlement, accounting, reconciliation, operational resilience, and audit.

This white paper proposes a **Digital Asset Platform** as the common foundation for those capabilities.

The platform is not intended to be a monolithic system that owns every digital-asset function. Nor should it become a separate “bank within the bank.” Instead, it should provide a set of reusable services and a canonical domain model that allow different products and businesses to operate consistently across multiple assets, custodians, networks, and settlement models.

The proposed architecture is based on three layers:

```text
Digital Asset Products
        ↓
Common Digital Asset Services
        ↓
Digital Asset Infrastructure
```

**Digital Asset Products** represent business capabilities such as custody, tokenization, issuance, payments, trading, collateral, treasury, and settlement.

**Common Digital Asset Services** provide the shared banking functions required across those products, including asset registration, policy, entitlements, transaction processing, custody abstraction, compliance, settlement, accounting events, reconciliation, and audit evidence.

**Digital Asset Infrastructure** connects those services to blockchain networks, custody systems, HSMs, MPC infrastructure, trading venues, settlement networks, blockchain-intelligence providers, and other external services.

At the centre of the model is a **Canonical Digital Asset Model**. This provides a stable representation of the financial meaning of a transaction independently of any one blockchain, token standard, or vendor.

The core architectural principle is:

> **Financial meaning should be canonical; digital representation and network implementation should remain adaptable.**

This gives the bank a platform that can support today’s digital-asset use cases without tying its business architecture to technology that is still evolving rapidly.

---

## 1. Why a Digital Asset Platform Is Needed

Digital assets introduce new technical mechanisms, but most of the business questions they create are familiar.

Who owns the asset?

Who is entitled to move it?

Where is it held?

What legal entity has responsibility for it?

What controls apply before transfer?

When is a transaction final?

How is the resulting position reflected in the bank’s books?

How is that position reconciled to external records?

What evidence exists to show why a transaction was allowed?

These questions already exist across payments, securities, treasury, custody, and capital markets. The difference is that digital assets can combine several traditionally separate functions into a single technical transaction.

A blockchain transfer may simultaneously represent:

- movement of a financial instrument;
- settlement;
- ownership change;
- custody movement;
- fee payment;
- legal-state change;
- accounting consequence.

That compression is powerful, but it can also blur responsibilities.

If each product team solves these problems independently, the bank is likely to end up with multiple overlapping stacks:

```text
Custody platform
Tokenization platform
Crypto trading platform
Stablecoin platform
Digital collateral platform
Settlement platform
```

Each may implement its own wallet model, transaction lifecycle, policy logic, compliance integration, accounting interpretation, and audit trail.

That approach may work for isolated pilots. It does not scale well into a bank-wide capability.

The purpose of the Digital Asset Platform is to establish a common foundation before product fragmentation becomes embedded.

---

## 2. Purpose of the Charter

The Digital Asset Platform Charter defines the architecture, operating model, and shared services required to support digital assets in a controlled and reusable way.

Its objectives are to:

1. establish a common language for digital-asset products and transactions;
2. separate business meaning from blockchain-specific implementation;
3. define reusable services that can support multiple products;
4. avoid duplicated control logic across product teams;
5. provide a consistent integration model into Finance, Risk, Operations, and Compliance;
6. create clear ownership of books and records;
7. preserve the ability to change custodians, networks, and technology providers over time;
8. make new digital-asset products progressively easier to introduce.

The Charter should be treated as a foundation for architecture and governance, not as a commitment to a particular blockchain, vendor, or product roadmap.

---

## 3. Scope

The Digital Asset Platform should support a broad set of assets while allowing their legal and economic differences to remain explicit.

Potential asset classes include:

- tokenized deposits;
- tokenized securities;
- tokenized funds;
- digital collateral;
- stablecoins;
- native crypto-assets;
- wholesale settlement assets;
- central-bank digital currencies;
- digitally represented traditional instruments;
- bank-issued digital instruments.

The platform should also support multiple lifecycle activities:

```text
Issue
Mint
Distribute
Hold
Transfer
Trade
Settle
Pledge
Service
Redeem
Burn
```

Not every asset will use every lifecycle function.

A tokenized deposit may be issued, transferred, redeemed, and burned.

A tokenized bond may be issued, allocated, traded, settled, used as collateral, serviced, and redeemed.

A native crypto-asset may primarily require acquisition, custody, transfer, settlement, and valuation.

The architecture should therefore be based on capabilities, not on one assumed product lifecycle.

---

## 4. Design Principles

### 4.1 Products Express Intent

A product should state what the business wants to achieve.

For example:

```text
Transfer 10 BTC for Client A
```

or:

```text
Settle purchase of Tokenized Bond X against USD cash
```

The product should not independently determine every technical and control decision behind that request.

The common services should determine:

- whether the asset is approved;
- whether the client is entitled to transact;
- whether the destination is permitted;
- what compliance checks apply;
- whether additional approval is required;
- which custody path should be used;
- which network should be used;
- when settlement is considered complete;
- what position and accounting changes result.

This allows product teams to focus on business functionality rather than reimplementing the same control framework.

---

### 4.2 Common Banking Capabilities Should Be Implemented Once

Where a capability is common across products, it should be provided once.

Examples include:

- asset and network registration;
- party and account mapping;
- wallet and address management;
- entitlements;
- transaction policy;
- compliance integration;
- custody abstraction;
- settlement coordination;
- position keeping;
- accounting-event generation;
- reconciliation;
- evidence and audit.

This does not require every business process to be centralized.

It requires common concerns to have common implementations.

---

### 4.3 Financial Meaning Must Be Separated from Technical Representation

The fact that an instrument is represented on a blockchain does not redefine its legal or economic nature.

A deposit remains a deposit.

A bond remains a bond.

A fund share remains a fund share.

The architecture should explicitly separate:

```text
Financial Instrument
        ↓
Digital Representation
        ↓
Network Implementation
```

This separation is important because one instrument may eventually have more than one representation.

For example:

```text
Bond XYZ 2032
   ├── Traditional securities representation
   ├── Ethereum-based representation
   └── Permissioned-ledger representation
```

The bank should be able to reason about the bond consistently regardless of where or how it is represented.

---

### 4.4 Account, Wallet, Address, and Position Must Remain Distinct

A recurring source of confusion in digital-asset architecture is the tendency to treat wallets and blockchain addresses as if they were equivalent to customer accounts.

They are not.

An **Account** is a banking and ownership construct.

A **Wallet** is a cryptographic control construct.

An **Address** is a network identifier.

A **Position** is an economic quantity.

A client account may have one position distributed across several addresses.

An omnibus wallet may hold assets belonging economically to many clients.

Therefore:

> **Blockchain balance is not necessarily customer balance.**

The bank’s operating and accounting model must remain able to represent beneficial ownership independently of how assets are physically arranged on-chain.

---

### 4.5 Internal Books and Records Must Be Deliberate

Blockchain state can be authoritative for some aspects of a transaction, but it should not automatically be treated as the bank’s complete accounting system.

The platform should normally maintain an internal representation of positions and transaction state:

```text
Network / Custodian State
          ↓
Digital Asset Subledger
          ↓
Bank Books and Records
          ↓
General Ledger
```

This creates a controlled bridge between digital-asset infrastructure and the bank’s financial systems.

---

### 4.6 Auditability Must Be Designed In

Digital-asset transactions can involve several layers of decision-making:

- business authorization;
- policy;
- sanctions;
- blockchain analytics;
- risk checks;
- custody routing;
- signing;
- network settlement.

The platform should preserve enough evidence to answer a simple question:

> Why was this transaction permitted?

The answer should not depend on manually reconstructing logs from multiple vendors.

Each transaction should carry a durable evidence trail that records who initiated the action, what policies applied, what approvals were obtained, what compliance results were returned, which custody route was used, which transaction was submitted, and what final outcome occurred.

---

## 5. The Platform Model

The Digital Asset Platform should be understood as a shared banking capability rather than a single application.

```text
                     DIGITAL ASSET PRODUCTS

       Custody      Trading      Tokenization
       Payments     Collateral   Issuance
       Treasury     Settlement   Asset Servicing

                              │
                              ▼

                   COMMON DIGITAL ASSET SERVICES

       Asset & Network Registry
       Party / Account / Wallet Services
       Transaction Processing
       Policy & Entitlements
       Compliance / KYT / Sanctions
       Custody Services
       Settlement Services
       Lifecycle Services
       Position & Ledger Services
       Accounting Events
       Reconciliation
       Evidence & Audit

                              │
                              ▼

                   DIGITAL ASSET INFRASTRUCTURE

       HSM / MPC
       Custodians
       Blockchain Nodes
       Blockchain Networks
       Trading Venues
       Settlement Networks
       Blockchain Intelligence
       Market Data
```

The three layers serve different purposes.

The product layer evolves with client and business demand.

The common-services layer provides stability.

The infrastructure layer can change as networks, vendors, and technologies evolve.

This separation is one of the most important long-term characteristics of the platform.

---

## 6. Common Digital Asset Services

The common-services layer contains the capabilities that should be reused across the platform.

### 6.1 Asset and Network Registry

The bank needs an authoritative record of what it supports.

This should include more than a token symbol or contract address.

For each asset, the bank should understand:

- what financial instrument it represents;
- who issued it;
- its legal and regulatory classification;
- where it can be held;
- which networks represent it;
- which clients may transact in it;
- which custody models are permitted;
- which valuation rules apply;
- which accounting treatment applies;
- which transfer restrictions apply;
- which lifecycle events must be supported.

Networks require similar governance.

The bank should know:

- whether a network is approved;
- what finality model it uses;
- what operational dependencies exist;
- which custody providers support it;
- what its fee model is;
- how forks or reorganizations are handled;
- what operational status it is currently in.

This makes asset and network support a governed platform decision rather than an application configuration hidden inside a product.

---

### 6.2 Transaction Processing

The platform should provide a common transaction lifecycle.

A typical lifecycle may be:

```text
Created
  ↓
Validated
  ↓
Policy Checked
  ↓
Compliance Checked
  ↓
Approval Pending
  ↓
Approved
  ↓
Signing
  ↓
Submitted
  ↓
Confirmed
  ↓
Final
  ↓
Reconciled
  ↓
Accounted
```

Exception states should also be explicit:

```text
Rejected
Failed
Cancelled
Expired
Quarantined
Manual Review
Settlement Exception
Reorganization Pending
```

This common lifecycle gives Operations, Risk, Finance, and Technology a shared view of transaction status.

---

### 6.3 Policy and Entitlements

Policy should be externalized from product code.

A digital-asset transaction may depend on:

- the acting user;
- the client;
- the asset;
- the legal entity;
- the account;
- the transaction amount;
- the counterparty;
- the destination address;
- the jurisdiction;
- the network;
- the risk score;
- the compliance result;
- the time or operating window.

The platform should support outcomes broader than simply allow or deny.

Examples include:

```text
Allow
Deny
Require Additional Approval
Require Compliance Review
Require Enhanced Due Diligence
Require Additional Signer
Require Cold-Storage Execution
```

This is particularly important because digital-asset controls often cross business, operational, legal, and technical boundaries.

---

### 6.4 Compliance Integration

Compliance must be part of transaction processing rather than a downstream afterthought.

A typical flow may be:

```text
Instruction
   ↓
Identity & Entitlements
   ↓
Policy
   ↓
Sanctions
   ↓
Address Screening
   ↓
Blockchain Analytics
   ↓
Risk Evaluation
   ↓
Approval
   ↓
Execution
```

The platform may integrate with external blockchain-intelligence providers, but the architecture should avoid making those providers part of the bank’s core domain model.

A provider should be replaceable.

The compliance result should remain canonical.

---

### 6.5 Custody Services

Custody is one of the most technically and operationally specialized areas of digital assets, but product applications should not need to understand every custody implementation.

The platform should provide common custody capabilities such as:

- create or assign wallet;
- create or derive address;
- query balance;
- prepare transaction;
- sign transaction;
- submit transaction;
- freeze wallet;
- rotate key;
- recover key;
- apply signing policy.

Different implementations can then sit behind that service:

```text
Custody Services
   ├── Internal HSM
   ├── Internal MPC
   ├── External Custodian
   └── Sub-Custodian
```

This gives the bank greater flexibility in selecting or replacing custody providers.

---

### 6.6 Settlement Services

Digital assets introduce multiple forms of settlement.

These may include:

- free-of-payment transfer;
- delivery versus payment;
- payment versus payment;
- tokenized collateral exchange;
- atomic settlement;
- multi-network settlement.

The platform should make settlement explicit rather than assuming that one blockchain transaction always equals one completed business transaction.

A business instruction may generate several technical transactions.

For example:

```text
Purchase Tokenized Bond
        │
        ├── Bond Transfer
        ├── Cash Transfer
        └── Fee Transaction
                 │
                 ▼
             Settlement
```

The platform should distinguish network confirmation, network finality, economic finality, and legal finality.

These may not always occur at the same moment.

---

## 7. Canonical Digital Asset Model

The Canonical Digital Asset Model provides the common language of the platform.

It should be small enough to remain understandable, but rich enough to represent the essential banking relationships.

The core concepts are:

```text
Party
Instrument
Digital Representation
Account
Wallet
Address
Position
Instruction
Transaction
Settlement
Accounting Event
Evidence
```

These concepts should remain stable even as underlying technologies change.

---

### 7.1 Party

A Party is a legal or operational actor.

It may represent:

- an individual;
- a client;
- a legal entity;
- a bank entity;
- an issuer;
- a custodian;
- a counterparty;
- an exchange;
- another network participant.

A party should never be represented solely by a blockchain address.

---

### 7.2 Instrument and Digital Representation

An Instrument represents the underlying financial or economic thing.

Examples include:

- a Treasury bond;
- a bank deposit;
- a fund share;
- BTC;
- ETH;
- a stablecoin;
- a repo claim.

A Digital Representation describes how that instrument is represented on a particular network.

This allows the bank to distinguish the legal asset from the technology through which it is represented.

---

### 7.3 Account, Wallet, Address, and Position

These concepts should remain separate in the canonical model.

```text
Party
  │
  owns / controls
  ▼
Account
  │
  holds
  ▼
Position ───────────► Instrument
  │
  │
  └───────────────► Wallet
                       │
                       ▼
                    Address
```

The model should support both segregated and omnibus custody.

That is essential for institutional operations.

---

### 7.4 Instruction and Transaction

An Instruction represents business intent.

Examples include:

- transfer;
- buy;
- sell;
- mint;
- burn;
- issue;
- redeem;
- pledge;
- release;
- settle.

A single instruction may generate multiple transactions.

This separation is important because the client or product thinks in business terms while the network may require several technical operations.

---

### 7.5 Settlement

Settlement should be represented independently of the transactions that implement it.

This gives the platform a place to reason about:

- asset leg;
- cash leg;
- settlement model;
- settlement status;
- finality;
- exceptions.

It also creates a natural model for delivery-versus-payment and other multi-leg processes.

---

## 8. Books, Positions, and Accounting

Digital assets should not create an accounting model that bypasses Finance.

The platform should instead translate digital-asset activity into a form that existing Finance systems can understand.

A useful separation is:

```text
Network Transaction
        ↓
Canonical Event
        ↓
Position Movement
        ↓
Accounting Event
        ↓
General Ledger
```

The General Ledger should not need to understand gas, block hashes, wallet derivation paths, or blockchain-specific transaction structures.

It should receive accounting events with the same discipline expected from any other financial platform.

The Digital Asset Platform therefore acts as an important translation layer between new settlement technology and existing financial architecture.

---

## 9. Reconciliation

Reconciliation should be considered a primary platform function.

A digital-asset position may exist simultaneously in several forms:

```text
Economic Position
      │
      ├── Internal Subledger
      ├── Custodian Record
      ├── Blockchain State
      └── General Ledger
```

These views will not always be identical at every instant.

Transactions may be pending.

Fees may be posted separately.

Custodian books may update on a different timetable.

Blockchain finality may take time.

The platform should therefore support systematic reconciliation across these representations.

Where appropriate, the target should be automated multi-way reconciliation between:

1. internal position;
2. custodian position;
3. blockchain state;
4. General Ledger.

This is one of the clearest examples of why digital assets need to be incorporated into Finance architecture rather than treated solely as a blockchain concern.

---

## 10. Evidence and Audit

The platform should produce a durable record of material decisions.

For each transaction, the bank should be able to reconstruct:

- who initiated it;
- on whose behalf;
- what asset was involved;
- which account was used;
- which policy applied;
- what version of that policy was in force;
- what sanctions and blockchain-screening checks ran;
- which approvals were required;
- which approvals were obtained;
- which custody service was used;
- which signing policy applied;
- which network transaction resulted;
- when finality occurred;
- what position changed;
- what accounting event followed.

This creates an auditable chain from business intent to financial outcome.

That evidence is valuable not only for audit and regulation, but also for operational support and incident investigation.

---

## 11. Security and Operational Resilience

Digital assets introduce some risks that are familiar and some that are new.

The platform must consider:

- key generation;
- key storage;
- signing authority;
- MPC or HSM controls;
- privileged access;
- transaction limits;
- destination whitelisting;
- segregation of duties;
- insider risk;
- compromised credentials;
- compromised wallets;
- smart-contract risk;
- blockchain outages;
- custody-provider outages;
- network congestion;
- delayed finality;
- chain reorganizations;
- forks;
- extreme transaction fees;
- reconciliation breaks.

The architecture should support operational responses such as:

```text
Continue Normally
Degrade
Require Manual Approval
Restrict an Asset
Restrict a Network
Suspend Transfers
Suspend a Custodian
```

The bank should have the ability to control exposure to digital-asset infrastructure without relying entirely on the infrastructure provider itself.

---

## 12. Governance

Digital assets cross traditional organizational boundaries.

A sustainable operating model will require participation from:

- Digital Assets business;
- Finance;
- Treasury;
- Operations;
- Technology;
- Enterprise Architecture;
- Cybersecurity;
- Risk;
- Compliance;
- Legal;
- Financial Crime;
- Internal Audit.

Governance should cover both products and shared infrastructure.

At minimum, the bank should have explicit processes for approving:

- assets;
- networks;
- custody providers;
- trading venues;
- settlement models;
- blockchain-intelligence providers;
- material policy changes;
- material platform changes.

This governance should not be treated as a temporary project committee.

As digital assets become part of normal banking operations, these decisions become part of normal product and technology governance.

---

## 13. Asset and Network Admission

A key benefit of a common platform is that onboarding a new asset or network becomes a governed process rather than a bespoke technology project.

For a new asset, the bank should assess:

### Financial
- instrument type;
- issuer;
- valuation;
- liquidity;
- collateral characteristics.

### Legal
- ownership;
- legal form;
- enforceability;
- jurisdiction;
- client eligibility.

### Technology
- network;
- smart-contract design;
- token standard;
- operational dependencies.

### Custody
- custody model;
- key requirements;
- segregation;
- recovery.

### Risk
- counterparty;
- market;
- liquidity;
- concentration;
- operational risk.

### Compliance
- sanctions;
- AML;
- blockchain transparency;
- transaction-monitoring support.

### Finance
- accounting;
- valuation;
- capital treatment;
- regulatory reporting;
- reconciliation.

Networks should undergo a similar admission process focused on governance, consensus, finality, operational maturity, resilience, custody support, and connectivity.

Once an asset or network is admitted, the information should be available as shared platform metadata rather than rediscovered by every product.

---

## 14. Target Operating Model

The Digital Asset Platform should integrate with existing enterprise capabilities wherever appropriate.

Examples include:

```text
Identity            → Enterprise IAM
Client Data         → Existing Client Master
Sanctions           → Existing Screening Platform
Accounting          → Existing General Ledger
Market Data         → Existing Market Data Platform
Case Management     → Existing Investigation Platform
Risk                → Existing Risk Infrastructure
Observability       → Existing Monitoring Platform
```

The objective is not to recreate mature banking capabilities simply because digital assets use new infrastructure.

New services should be introduced where the digital-asset domain genuinely requires them.

This keeps the platform smaller, easier to govern, and more aligned with the existing technology estate.

---

## 15. Platform Boundaries

The Digital Asset Platform is not intended to become:

- a replacement for the General Ledger;
- a client master;
- a complete trading platform;
- a sanctions platform;
- a market-data platform;
- a generic workflow engine;
- a blockchain analytics company;
- a blockchain network.

Its role is to provide the common digital-asset domain and shared services that connect those capabilities.

Clear boundaries are important because platform programmes have a natural tendency to accumulate responsibilities.

A successful Digital Asset Platform should become more reusable over time, not simply larger.

---

## 16. Initial Delivery Strategy

The first implementation should be deliberately narrow.

The objective should not be to demonstrate the largest number of blockchains or products.

The objective should be to demonstrate the complete operating model.

A useful initial scope would contain:

```text
One Asset
One Network
One Custody Model
One Client Type
One Transaction Type
One Settlement Path
One Accounting Treatment
```

The end-to-end flow should include:

```text
Instruction
   ↓
Policy
   ↓
Compliance
   ↓
Approval
   ↓
Custody
   ↓
Network
   ↓
Settlement
   ↓
Reconciliation
   ↓
Accounting
   ↓
Evidence
```

A narrow implementation that demonstrates the full lifecycle is more valuable than a broad proof of concept that stops at blockchain connectivity.

---

## 17. Implementation Path

A practical implementation can be divided into six phases.

### Phase 1 — Foundation

Define:

- charter;
- asset taxonomy;
- canonical domain model;
- governance model;
- architecture principles;
- control framework;
- product and network admission criteria.

### Phase 2 — Core Common Services

Implement:

- Asset Registry;
- Network Registry;
- party and account model;
- wallet model;
- transaction lifecycle;
- policy and entitlement services;
- evidence and audit framework.

### Phase 3 — Connectivity

Integrate:

- first custody solution;
- first blockchain network;
- first blockchain-intelligence provider;
- identity;
- market data.

### Phase 4 — Finance Integration

Implement:

- position ledger;
- reconciliation;
- valuation;
- accounting-event generation;
- General Ledger integration;
- reporting.

### Phase 5 — Controlled Product

Deliver one complete use case through the platform.

### Phase 6 — Expansion

Add new:

- assets;
- networks;
- custodians;
- settlement models;
- jurisdictions;
- products.

Each expansion should reuse common services rather than create a parallel stack.

---

## 18. Measures of Success

The strongest measure of platform success is not the number of blockchains connected.

It is whether each new product becomes easier to introduce.

Useful measures include:

### Product Enablement
- time to onboard a new asset;
- time to onboard a new network;
- time to onboard a new custodian;
- time to launch a new product.

### Operational Control
- percentage of transactions with complete automated evidence;
- percentage of transactions requiring manual intervention;
- number and age of settlement exceptions.

### Finance
- percentage of positions automatically reconciled;
- percentage of accounting events generated automatically;
- number of unresolved books-and-records breaks.

### Architecture
- percentage of products using common services;
- reduction in duplicate custody, compliance, and ledger implementations;
- number of network-specific dependencies exposed directly to product applications.

The architectural success measure can be expressed simply:

> **Adding the fifth product should be materially easier than adding the first.**

---

## 19. Strategic Outcome

The value of the Digital Asset Platform is not dependent on predicting which blockchain or token standard will dominate.

Those choices will continue to change.

The more durable concepts are banking concepts:

```text
Party
Instrument
Account
Position
Instruction
Transaction
Custody
Settlement
Ledger
Accounting
Control
Evidence
```

A strong platform keeps these concepts stable while allowing networks, custodians, and digital representations to evolve.

That creates optionality.

A tokenized security can move from one network to another without forcing the bank to redesign its accounting architecture.

A custody provider can change without requiring every product to rewrite transaction logic.

A new settlement mechanism can be added without redefining the meaning of a client account or position.

That adaptability is more strategically important than any single technology choice.

---

## Conclusion

Digital assets should not require the bank to abandon the architecture, controls, and accounting disciplines developed through decades of financial-market infrastructure.

Nor should every new digital-asset product create another isolated technology stack.

The Digital Asset Platform provides a common foundation.

Its architecture separates:

```text
Product Intent
      ↓
Common Digital Asset Services
      ↓
Digital Asset Infrastructure
```

Its canonical model separates:

```text
Financial Meaning
      ↓
Digital Representation
      ↓
Network Implementation
```

Its operating model connects:

```text
Instruction
   ↓
Control
   ↓
Execution
   ↓
Settlement
   ↓
Position
   ↓
Accounting
   ↓
Evidence
```

The result is not simply a platform for crypto.

It is a framework for incorporating digitally represented value into the bank’s existing financial, operational, risk, and technology architecture.

That foundation can support custody, tokenization, digital collateral, stablecoins, digital securities, blockchain settlement, and forms of digital finance that have not yet emerged.

The long-term objective is straightforward:

> **Make digital assets another governed financial capability of the bank, not a collection of exceptions.**
