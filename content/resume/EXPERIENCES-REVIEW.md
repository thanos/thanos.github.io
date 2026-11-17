# Experiences review catalog

Updated `2026-11-16` from CSV edits → YAML sync. **230** atoms.

Machine-readable: [`EXPERIENCES-REVIEW.csv`](EXPERIENCES-REVIEW.csv).
Your pre-sync CSV backup: [`EXPERIENCES-REVIEW.user.csv`](EXPERIENCES-REVIEW.user.csv).

## Sync notes

- Applied titles, domains, skills, dates, visibility, kind, and `responsible` from your CSV.
- Split `zingy-nyt-ebay` → `zingy-nyt` + `zingy-ebay`; added `zingy-fantasy`.
- Renamed `rbc-ml-pricing` to Credit Derivatives only (munis stays on `rbc-ml-pricing-munis`).
- Set `aah-patient-records` domain to Medical; `oss-flyby` domain to AI.
- Skipped duplicate empty-status ByteSwap/ByteChain rows under `infinigon-crypto-custody` (already `oss-byteeasy` / `oss-bytechain`).
- `kind: built|run` mapped to `kind: built` + `responsible: [built, run]`.

| id | start | client | title | responsible | status |
|----|-------|--------|-------|--------------|--------|
| `aah-patient-records` | 1993 | AAH Meditel | AAH Meditel patient registration & records | built | existing |
| `apple-newton-smalltalk` | 1993 | Apple | Apple/Handy — Newton Smalltalk port | built | new |
| `apple-newton-tools` | 1993 | Apple | Apple Newton — languages and developer tools | built | existing |
| `article-financial-algorithms-cookbook` | 2007 |  | Financial Algorithms Cookbook |  | existing |
| `article-pqe-series` | 2025 |  | Encrypt Once, Decrypt Many — tholos-pq series |  | existing |
| `article-programming-drones` | 2026 |  | Programming Drones with OTP (series) |  | existing |
| `async-j` | 2004 |  | async-j — Java NIO asynchat-style wrapper | built | new |
| `atari-games` | 1980 | Atari | Atari — arcade & ST games | built | existing |
| `atari-telecom` | 1980 | Atari | Atari —  ST applications | built | existing |
| `austin-knight-accounting` | 1987 | Austin Knight | Austin Knight — advertisement coupon accounting | built | new |
| `barclays-topic-trading` | 1984 | Barclays | Barclays Topic equities trading system | built | existing |
| `bbc-video-routing` | 1989 | BBC | BBC — video routing switches | built | new-thin |
| `bt-hope-telecom-gold` | 1986 | British Telecom | British Telecom — Telecom Gold & Hope language | built | existing |
| `bt-tcpip-router-os` | 1992 | British Telecom | BT — TCP/IP router OS (Hope prototype) | built | new |
| `bt-timeseries-db` | 1992 | British Telecom | BT — fast time-series database for telecom | built | new |
| `cable-wireless-telecom` |  | Cable & Wireless | Cable & Wireless — telecom systems | built | new-thin-dates |
| `caesars-internet-casino` | 1995 | Caesars Casino | Caesars — first internet casino & WebCheck | built | existing |
| `cs-commodities-market-data` | 2008 | Credit Suisse | Credit Suisse — commodities market data services | built | new |
| `cs-commodities-risk` | 2007 | Credit Suisse | Credit Suisse commodities (umbrella) | built | thinned-umbrella |
| `cs-openlink-pricing` | 2008 | Credit Suisse | Credit Suisse — OpenLink external pricing models | built | new |
| `cs-trade-repo` | 2008 | Credit Suisse | Credit Suisse — central trade repository | built | new |
| `drake-av-router` | 1989 | Philip Drake Ltd | Philip Drake — AV trunk line router (BBC) | built | new |
| `electric-coin-slots` | 1978 | Electric Coin Company | Electric Coin Company — slot & video poker machines | built | existing |
| `ep-first-website` | 1993 | European Parliament | European Parliament — first official website | built | new |
| `ep-workflow` | 1994 | European Parliament | European Parliament multilingual workflow & web services | built | existing |
| `ericsson-switch-mgmt` | 1995 | Ericsson | Remote telecom switch management | built | existing |
| `ferranti-lynx-rtos` | 1988 | Ferranti | Ferranti — Lynx helicopter real-time OS | built | existing |
| `ferranti-satellite-comms` | 1986 | Ferranti | Ferranti — armored satellite communications | built | new |
| `forsyth-darwin-beagle` | 1980 | Richard Forsyth | Richard Forsyth — Darwin / Beagle genetic programming | built | new |
| `handy-newton-minitel` | 1993 | Handy Software | Handy Software — Newton Minitel, browser, Smalltalk | built | new |
| `honeywell-bull-telecommuting` | 1990 | Honeywell Bull | Honeywell Bull — telecommuting / home-working system | built | new |
| `ibm-mobile-jvm` | 1996 | IBM | IBM Research — mobile phone JVM | built | existing |
| `icap-blackberry-trading` | 2004 | ICAP | BrokerTec/BlackBerry fixed-income trading PoC | built | new |
| `icap-brokertec-swing` | 2004 | ICAP | BrokerTec fixed-income trading app (Java/Swing) | built | new |
| `icap-conformance` | 2004 | ICAP | Market conformance analysis tools | built | new |
| `icap-emerging-markets-web` | 2004 | ICAP | BrokerTec lightweight emerging-markets web trading | built | new |
| `icap-fixed-income` | 2004 | ICAP | ICAP BrokerTec front-end (umbrella) | built | thinned-umbrella |
| `icap-gui-framework` | 2004 | ICAP | Lightweight GUI framework for trading systems | built | new |
| `icap-iconnect` | 2004 | ICAP | BrokerTec iConnect conversion | built | new |
| `icap-jabber-backend` | 2004 | ICAP | Distributed trading backend services (Jabber/async-j) | built | new |
| `ilabs-workflow` | 1994 |  | iLabs — object-oriented workflow (39 Eindhoven patterns) | built | new |
| `infinigon-crypto-custody` | 2012 | Infinigon | Cross-exchange custodial crypto trading platform | built | existing |
| `infinigon-social-ml` | 2012 | Infinigon | Infinigon — social-media ML trading analytics | built|architected | new |
| `interest-early-career-maker` | 1990 |  | Maker / systems roots — Python evangelism & industry firsts |  | existing |
| `interest-mentoring-opensource` |  |  | Mentoring, inner source, and continuous learning |  | existing |
| `interest-missing-persons-register` | 1994 |  | Global missing persons register |  | new |
| `interest-mykonos-festival` |  |  | Mykonos art & short-film festival |  | existing |
| `jpm-athena-energy` | 2007 | JPMorgan | JPMorgan Athena energy (umbrella) | built | thinned-umbrella |
| `jpm-athena-profiler` | 2007 | JPMorgan | Athena WxWindows/Python code profiler | built | new |
| `jpm-cme-fix` | 2007 | JPMorgan | CME FIX gateway to Athena | built | new |
| `jpm-energy-alerting` | 2007 | JPMorgan | Energy feeds alert & logging framework | built | new |
| `jpm-gauss-cpr` | 2010 | JPMorgan | GAUSS counterparty-risk performance (network & compute) | built | new |
| `jpm-ice-fix` | 2007 | JPMorgan | ICE FIX gateway to Athena | built | new |
| `jpm-recon-framework` | 2007 | JPMorgan | Energy feed reconciliation framework | built | new |
| `jpm-trade-feed-framework` | 2007 | JPMorgan | Athena energy trade-feed framework | built | new |
| `marita-webcheck` | 1995 | Marita Bank | Marita Bank — WebCheck early cyber currency | built | new |
| `multitone-paging` | 1984 | Multitone | Multitone — paging server & signaling | built | new |
| `nyse-market-share` | 1997 | NYSE/SIAC | NYSE Market Share service into Specialist Portfolio | built | new |
| `nyse-market-surveillance` | 1997 | NYSE/SIAC | NYSE market surveillance — Python log analyzer & Java browser | built | new |
| `nyse-member-firm-regulatory` | 1997 | NYSE/SIAC | NYSE Member Firm Regulatory Service — first XML feed | built | new |
| `nyse-sec-supervision` | 1997 | NYSE/SIAC | NYSE/SEC event-sourced trader supervision | built | new-verify-claim |
| `nyse-specialist-portfolio` | 1997 | NYSE/SIAC | NYSE Specialist Portfolio — Swing client & trade details | built | new |
| `nyse-stock-info-server` | 1997 | NYSE/SIAC | NYSE Stock Information Server (pub/sub) | built | new |
| `nyse-surveillance-python` | 1997 | NYSE/SIAC | NYSE/SIAC front-end systems (umbrella) | built | thinned-umbrella |
| `nyse-web-trading` | 1997 | NYSE/SIAC | NYSE first web-based trading / specialist service | built | new |
| `oss-aegis` | 2024 |  | Aegis — Zig zkML miner for Bittensor (Apple Silicon) | built | existing |
| `oss-aito` | 2024 |  | Aito Hash — fastest Verus Coin miner on Apple Silicon | built | existing |
| `oss-anex` | 2014 |  | ANEX — cryptocurrency exchange | built | new |
| `oss-aplos` | 2017 |  | Aplos — ERC-20 token contracts on Ethereum | built | existing |
| `oss-apo` | 2026 |  | APO — engineering evidence from Git repos | built | existing |
| `oss-archeio` | 2021 |  | Archeio — Solana token registry (Orphic / IceBlock) | built | existing |
| `oss-audiobook-caissa` | 2008 |  | AudioBook framework & Caissa chess on iPhone | built | new |
| `oss-azure-sdk` | 2026 |  | azure_sdk — modern Azure SDK for Elixir | built | existing |
| `oss-bytechain` | 2019 | Byteeasy | ByteChain — crypto arbitrage platform | built | existing |
| `oss-byteeasy` | 2019 | Byteeasy | Byteeasy / ByteSwap — anonymous crypto exchange (Zimbabwe) | built | existing |
| `oss-ccxtex` | 2018 |  | ccxtex — Elixir interop for multi-exchange crypto APIs | built | existing |
| `oss-chromite` | 2014 |  | Chromite — Bancor-style commodity-backed crypto | built | new |
| `oss-contract-cafe` | 2020 | Byteeasy | Contract Cafe — Ethereum outcome ledgers (Byteeasy) | built | existing |
| `oss-couchbase-zig` | 2025 |  | couchbase-zig-client — Zig Couchbase + Elixir port | built | existing |
| `oss-darial` | 2026 |  | Darial — privacy-preserving LLM gateway | built | existing |
| `oss-decimal-mining` | 2021 | Decimal Group | Decimal Group — NFT mining shares & marketplace (Ethereum) | built | existing |
| `oss-diavasi` | 2026 |  | Diavasi — durable consumer groups on existing databases | built | existing |
| `oss-echo-social` | 2012 |  | Echo — realtime social analytical engine | built | new |
| `oss-elixir-utcp` | 2025 |  | elixir-utcp — Universal Tool Calling Protocol for Elixir | built | existing |
| `oss-ex-arrow` | 2025 |  | ex_arrow — Native Apache Arrow for the BEAM | built | existing |
| `oss-ex-codecs` | 2026 |  | ExCodecs — codec framework for the Elixir data stack | built | existing |
| `oss-ex-data-sketch` | 2025 |  | ex_data_sketch — streaming data sketches | built | existing |
| `oss-ex-datalog` | 2025 |  | ex_datalog — Datalog rules engine for Elixir | built | existing |
| `oss-ex-drone` | 2026 |  | ex_drone — BEAM-native drone control | built | existing |
| `oss-ex-editor` | 2025 |  | ExEditor — headless LiveView code editor | built | existing |
| `oss-ex-flow-graph` | 2026 |  | ExFlowGraph — LiveView node editor | built | existing |
| `oss-ex-graphblas` | 2026 |  | ex_graphblas — sparse linear algebra for Elixir | built | existing |
| `oss-ex-memory` | 2025 |  | ex_memory — local-first memory for LLMs | built | existing |
| `oss-ex-outlines` | 2026 |  | ex_outlines — structured LLM output for Elixir | built | existing |
| `oss-ex-systolic` | 2025 |  | ex_systolic — systolic array / spatial dataflow simulator | built | existing |
| `oss-ex-zarr` | 2025 |  | ExZarr — chunked N-dimensional arrays | built | existing |
| `oss-flyby` | 2026 |  | FlyBy — composable data-ingestion pipelines | built | existing |
| `oss-gamma-options` | 2024 |  | Gamma Options Exchange — EVM options (IceBlock) | built | existing |
| `oss-gnosis` | 2026 |  | Gnosis — local-first knowledge compiler | built | existing |
| `oss-hyperstate` | 2008 |  | HyperState — iPhone gaming framework | built | new |
| `oss-kathikon` | 2026 |  | Kathikon — BEAM-native durable job queue | built | existing |
| `oss-kriterion` | 2026 |  | Kriterion — AI-assisted evaluation platform | built | existing |
| `oss-lendmonade` | 2025 |  | Lendmonade — Aave V3 lending on Hedera Testnet | built | existing |
| `oss-logistiki` | 2026 |  | Logistiki — embedded accounting engine | built | existing |
| `oss-logos` | 2025 |  | Logos — contracts that compile to EVM | built | existing |
| `oss-marketsource` | 2012 |  | MarketSource — market data framework | built | new |
| `oss-mneme` | 2026 |  | mneme — embedded vector / memory database | built | existing |
| `oss-nimalana` | 2023 |  | Nimalana — Nim Solana validator | built | existing |
| `oss-oratos` | 2026 |  | Oratos — website visibility intelligence | built | existing |
| `oss-phoenix-prerender` | 2026 |  | phoenix_prerender — static generation and ISR for Phoenix | built | existing |
| `oss-phonescript` | 2006 |  | Phonescript — PostScript on J2ME/Brew/Symbian | built | existing |
| `oss-pso-python-server-objects` | 1996 |  | Python Server Objects (PSO) — early Python web framework | built | existing |
| `oss-quantum-storage-mongodb` | 2024 |  | quantum_storage_mongodb — Quantum cron on MongoDB | built | existing |
| `oss-rheo` | 2026 |  | Rheo — database-backed consumer groups | built | existing |
| `oss-rust-bottle` | 2025 |  | rust-bottle — Bottle RFC message containers | built | existing |
| `oss-smile-ex` | 2018 |  | smile_ex — Smile binary JSON for Elixir | built | existing |
| `oss-softgpu` | 2026 |  | SoftGPU — Rust GPU emulation and sanitizer runtime | built | existing |
| `oss-solana-escrow` | 2021 |  | solana-escrow — Solana program (Rust) | built | existing |
| `oss-stabilos` | 2026 |  | Stabilos — policy-driven programmable money | built | existing |
| `oss-stratum-harness` | 2025 |  | stratum_harness — Verus Stratum mining-pool aggregator / simulator | built | existing |
| `oss-terminusdb-client` | 2026 |  | terminusdb_ex — Elixir client for TerminusDB | built | existing |
| `oss-tholos-pq` | 2025 |  | tholos-pq — post-quantum multi-recipient encryption | built | existing |
| `oss-tradesource` | 2012 |  | TradeSource — trade abstraction framework | built | new |
| `oss-zerum` | 2026 |  | Zerum — deterministic Python code governance | built | existing |
| `oss-zinto` | 2026 |  | Zinto — Zig desktop apps with Svelte | built | existing |
| `oss-zynfer` | 2026 |  | Zynfer — from-scratch LLM inference in Zig | built | existing |
| `panasonic-rip-fax` | 1988 | Panasonic | Panasonic — Forth RIP engines & fax drivers | built | new |
| `rbc-access-control` | 2023 | RBC CM | Central Access Control for Capital Markets | architected|built|run | existing |
| `rbc-agentic-workflow` | 2024 | RBC CM | Agentic service workflow service | architected|built|run | new |
| `rbc-architecture-operations` | 2018 | RBC CM | Architecture for Operations |  | existing |
| `rbc-blockchain-ledger-poc` | 2018 | RBC CM | Blockchain-based ledger PoC / IBM Reference Ledger | architected | new |
| `rbc-blockchain-muni-trading` | 2022 | RBC CM | Municipal bond trading platform (blockchain) | architected|run | new |
| `rbc-blockchain-notes-poc` | 2016 | RBC CM | Notes trading platform PoC (blockchain) | architected | new |
| `rbc-cash-management-bank` | 2020 | RBC | Cash Management Bank — 5th-generation core (umbrella) |  | thinned-umbrella |
| `rbc-cm-blockchain-ledger` | 2020 | RBC CM | Cash Management — blockchain ledger accounting | architected | new |
| `rbc-cm-business-supervision` | 2023 | RBC CM | CM Business Supervision Controls | architected|built|run | new |
| `rbc-cm-data-registry` | 2019 | RBC CM | CM Data Registry | architected|built|run | new |
| `rbc-cm-kyc-kyb` | 2020 | RBC CM | Cash Management — KYC/KYB, evidence & document store | built|architected | new |
| `rbc-cm-payment-rails` | 2020 | RBC CM | Cash Management — payment manager & rails | built|architected | new |
| `rbc-cm-virtual-accounts` | 2020 | RBC CM | Cash Management — virtual accounts & liquidity | built|architected | new |
| `rbc-cmla` | 2017 | RBC CM | CMLA — enterprise centralized logging | architected|built|run | new |
| `rbc-cobol-genai-migration` | 2024 | RBC CM | COBOL/mainframe ledger & stored-proc GenAI migration | built | new |
| `rbc-containerization` | 2016 | RBC CM | Containerization program (Docker/K8s → AES) | architected | new |
| `rbc-cookiecutters` | 2016 | RBC CM | Inner-sourced project cookiecutters / application framework | built | new |
| `rbc-cross-asset-ui` | 2019 | RBC CM | Cross-asset trading UI platform | built | new |
| `rbc-data-ingest` | 2019 | RBC CM | Single data ingest — RETE rules engine | architected | new |
| `rbc-data-lake` | 2016 | RBC CM | Capital Markets Data Lake | architected | new |
| `rbc-data-transport` | 2019 | RBC CM | One Data Transport — Kappa-style bank data fabric | architected|built|run | new |
| `rbc-distributed-compute` | 2018 | RBC CM | Distributed Compute Service | architected|built|run | new |
| `rbc-emac-cmacs` | 2023 | RBC CM | eMac / CMACS — Capital Markets access attestation | architected | new |
| `rbc-emds` | 2019 | RBC CM | EMDS — Enterprise Market Data Services | architected|built|run | new |
| `rbc-encompass-migration` | 2014 | RBC CM | Encompass commodities migration | built | new |
| `rbc-enterprise-reconciliation` | 2025 | RBC | Enterprise Reconciliation Service |  | existing |
| `rbc-expense-reporting-portal` | 2022 | RBC CM | Expense Reporting Portal | architected|run | new |
| `rbc-faas-notification` | 2017 | RBC CM | FaaS + SNS (umbrella) | architected|built|run | thinned-umbrella |
| `rbc-faas` | 2017 | RBC CM | On-prem Function-as-a-Service (Lambda) | architected|built|run | new |
| `rbc-financial-controls` | 2023 | RBC CM | Financial Controls — technical transformation mandate | architected|built|run | new |
| `rbc-five-rings` | 2016 | RBC CM | Five Rings mentorship program | architected|run | new |
| `rbc-frtb-aml` | 2018 | RBC CM | FRTB and AML infrastructure | architected | new |
| `rbc-gla-reporting` | 2023 | RBC CM | GLA reporting & analytical platform | architected | new |
| `rbc-global-market-supervision` | 2023 | RBC CM | Global Market Supervision | architected|built|run | existing |
| `rbc-gms-supervisor-control` | 2023 | RBC CM | Single supervisor control service for GMS | architected | new |
| `rbc-gpu-model-port` | 2015 | RBC CM | GPU model port — Numba/Python for pricing & risk | architected|built|run | existing |
| `rbc-gpu-model` | 2010 | RBC | GPU Cuda Counter Party Risk | architected|built|run | existing |
| `rbc-hpc-nic-fpga` | 2017 | RBC CM | HPC messaging — BPF, DPDK, Smart NIC, FPGA | architected | new |
| `rbc-ib-pipeline` | 2015 | RBC CM | Investment Bank Pipeline analytics | built | new |
| `rbc-idol` | 2023 | RBC CM | IDOL — next-gen single execution platform (FaaS) | architected | new |
| `rbc-iso-20022-mx` | 2024 | RBC | SWIFT FIN/MT → ISO 20022 (MX) migration | architected|built|run | existing |
| `rbc-jupyter-hub` | 2018 | RBC CM | Jupyter Hub — quant development environment | architected|built|run | new |
| `rbc-language-platform-adoption` | 2010 | RBC CM | Language & platform engineering adoption (umbrella) |  | thinned-umbrella |
| `rbc-llm-governance` | 2024 | RBC CM | Bank-wide LLM services with governance | architected|run | new |
| `rbc-lme-openlink` | 2011 | RBC CM | LME trading platform / OpenLink migration | built | new |
| `rbc-mandate` | 2025-09 | RBC | Current mandate — Finance IT modernization & AI |  | existing |
| `rbc-metals-financing` | 2014 | RBC CM | Metals Financing build-out | built | new |
| `rbc-ml-platform` | 2018 | RBC CM | Machine Learning Platform — governed model hosting | architected|run | new |
| `rbc-ml-pricing-munis` | 2020 | RBC CM | ML Pricing Service — Munis Bonds | built|architected|run | existing |
| `rbc-ml-pricing` | 2020 | RBC CM | ML Pricing Service — Credit Derivatives | built|architected|run | existing |
| `rbc-mla-sentry` | 2018 | RBC CM | MLA & SENTRY — fast bug/defect tooling | built|architected|run | new |
| `rbc-nextgen-oms-poc` | 2017 | RBC CM | Next-gen Sales and Trading OMS PoC | built|architected|run | new |
| `rbc-ops-team-restructure` | 2023 | RBC CM | Ops team restructure — maintenance → startup-style delivery | run | new |
| `rbc-org-scale` | 2023-09 | RBC CM | Engineering organization — scale and operating model |  | existing |
| `rbc-pitos-cache` | 2022 | RBC CM | PITOS cache — cross-VM cache for NextGen HA | built|architected|run | new |
| `rbc-pitos` | 2017 | RBC CM | PITOS — point-in-time object store | built|architected|run | new |
| `rbc-position-pnl` | 2020 | RBC CM | Real-time Position and PnL systems | built|architected|run | new |
| `rbc-prism` | 2018 | RBC CM | PRISM data-storage initiative | architected | new |
| `rbc-python-elixir-adoption` | 2010 | RBC CM | Python and Elixir enterprise adoption | architected | new |
| `rbc-raas` | 2018 | RBC CM | Rules as a Service (RaaS) | built|architected | new |
| `rbc-rabacus-studio` | 2016 | RBC CM | RABACUS Studio — dashboard builder for backend developers | built|architected | new |
| `rbc-rabacus` | 2019 | RBC CM | RABACUS — one browser for all the Bank’s data | built|architected | new |
| `rbc-revort` | 2023 | RBC CM | REVORT — Broadridge capacity replacement | architected|built|run | new |
| `rbc-risk-api` | 2019 | RBC CM | RISK API — controlled enterprise data delivery | architected|built|run | new |
| `rbc-rnd-opensource` | 2017 | RBC CM | R&D for Technology — inner source & OSS stewardship |  | existing |
| `rbc-sdi` | 2019 | RBC CM | SDI — Single Data Interface SDK | architected|built|run | new |
| `rbc-security-master` | 2018 | RBC CM | Universal Security Master | architected|built|run | new |
| `rbc-shared-data-services` | 2019 | RBC CM | Shared Data Services mandate (umbrella) | architected|built|run | thinned-umbrella |
| `rbc-shared-ops-services` | 2016 | RBC CM | Shared Operations Services portfolio (umbrella) |  | thinned-umbrella |
| `rbc-sns` | 2017 | RBC CM | Simple Notification Service (SNS) | built|architected|run | new |
| `rbc-structured-flow-ops` | 2019 | RBC CM | Structured & Flow trade maintenance | run | new |
| `rbc-sts` | 2016 | RBC CM | Shared Technical Services (STS) — AWS-like on-prem platform | built|architected|run | new |
| `rbc-t1-infrastructure` | 2023 | RBC CM | T+1 transaction processing infrastructure | built|architected|run | new |
| `rbc-test-automation-bcst` | 2023 | RBC CM | Test Automation for BCST (EOD / T+1 industry testing) | architected | new |
| `rbc-tokenization-platform` | 2022 | RBC CM | Digital Asset Tokenization Platform | built|architected|run | new |
| `rbc-trade-expense` | 2024 | RBC CM | Trade Expense & Agentic Invoice Processing | built|architected|run | existing |
| `rbc-trade-limits` | 2023 | RBC CM | Market Access & Trade Limits (Rule 15c3-5) | built|architected|run | existing |
| `rbc-trade-repository` | 2016 | RBC CM | Central Trade Repository | architected|run | new |
| `rbc-trading-data-core` | 2018 | RBC CM | Real-time Trading Data Core (Athena-style) | architected | new |
| `rbc-usct-cross-border` | 2023 | RBC CM | USCT and cross-border payments programs | run|architected | new |
| `rbc-workspaces` | 2019 | RBC CM | WORKSPACES — multi-tenant hierarchical metadata API | built|architected|run | new |
| `reuters-rnt-server` | 1988 | Reuters | Reuters RNT news & image server | built | existing |
| `startup-rip-engines` | 1985 |  | Startup — RIP engines for printer manufacturers | built | new |
| `symantec-cpp-numeric` | 1987 | Symantec | Zortech/Symantec — C++ debugger & numeric libraries | built | existing |
| `symantec-eispack-linpack` | 1992 | Symantec | Symantec/Zortech — EISPACK/LINPACK ports to C++/Ada | built | new |
| `talk-bloomberg-quant-series` | 2015 |  | Bloomberg Quant Seminar talks |  | existing |
| `uk-treasury-transputer-nn` | 1980 | UK Treasury | UK Treasury — Occam neural net on Transputers | built | new |
| `unilever-fuzzy-or` | 1982 | Unilever | Unilever — OR pallet packing & fuzzy-logic control | built | new |
| `unilever-robotics` | 1982 | Unilever | Unilever — die milling robotics control | built | existing |
| `visual-trading` | 2004 |  | VisualTrading — lightweight Java UI framework | built | new |
| `westlb-swaptions-pricing` | 1996 | WestLB | WestLB — maturity calculators / swaptions pricing | built | new |
| `westlb-var` | 1996 | West LB | West LB VAR — pricing & portfolio tools | built | existing |
| `zingy-async-backend` | 2006 | Zingy | Zingy async-j NIO backend & IPAY billing | built | new |
| `zingy-ebay` | 2006 | Zingy | eBay Mobile | built|run | new |
| `zingy-fantasy` | 2006 | Zingy | Official mobile Fantasy sports | built|run | new |
| `zingy-games-cms` | 2006 | Zingy | Mobile games CMS / high-score server | built|run | new |
| `zingy-mapquest` | 2006 | Zingy | MapQuest Mobile — #1 US phone app | built|run | new |
| `zingy-mobile` | 2006 | Zingy | Zingy mobile portfolio (umbrella) | built | thinned-umbrella |
| `zingy-moviegoer-flash` | 2006 | Zingy | Moviegoer — first US mobile Flash app | built|run | new |
| `zingy-nbc-weather` | 2006 | Zingy | NBC Weather Mobile | built|run | new |
| `zingy-nyt` | 2006 | Zingy | New York Times Mobile | built|run | new |
| `zingy-plaxo` | 2006 | Zingy | Plaxo mobile sync | built|run | new |
| `zingy-vindigo` | 2006 | Zingy | Vindigo City Guide — top-ten mobile | built|run | new |
