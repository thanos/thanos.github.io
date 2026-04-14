---
title: "Polymarket and the Global Prediction Market Ecosystem"
description: "The Evolution of Information Finance: A Comprehensive Technical and Comparative Analysis of Polymarket and the Global Prediction Market Ecosystem*"
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


#  Polymarket and the Global Prediction Market Ecosystem

**The Evolution of Information Finance: A Comprehensive Technical and Comparative Analysis of Polymarket and the Global Prediction Market Ecosystem**

The landscape of global forecasting has undergone a fundamental transformation since the emergence of blockchain-based prediction markets, transitioning from academic experiments such as the Iowa Electronic Markets to high-volume financial venues like Polymarket.[^1]  By early 2026, the sector has established itself as a critical component of "Information Finance" (InfoFi), where the primary utility of a market is not merely speculation but the extraction of accurate, real-time probabilistic data regarding future events.[^3] Polymarket, as the leading decentralized protocol in this domain, has demonstrated the capacity to aggregate the "wisdom of crowds" with greater speed and accuracy than traditional polling methods, influencing journalists, policymakers, and institutional investors alike.[^4] This report provides an exhaustive technical examination of Polymarket's architecture, a detailed comparative study of its primary regulated and decentralized alternatives, and a nuanced analysis of the economic and regulatory mechanisms that sustain these complex systems.

## **The Architectural Foundation of Polymarket**

Polymarket is a decentralized, non-custodial prediction market platform that allows users to trade on the outcome of binary, categorical, and scalar events using stablecoin collateral.[^4] Its success is largely attributed to a hybrid architectural model that balances the transparency of decentralized settlement with the high-performance user experience of traditional electronic exchanges.[^1]

### **The Hybrid Execution Layer: Off-Chain Matching and On-Chain Settlement**

Unlike earlier decentralized exchanges that relied solely on on-chain execution, which often led to high latency and prohibitive gas costs, Polymarket employs a bifurcated system.[^1] The platform utilizes the Polygon blockchain, an Ethereum Layer-2 scaling solution, as its primary settlement layer.[^4] Polygon provides a high-throughput, low-fee environment that is essential for maintaining the real-time odds necessary for high-frequency trading.[^4]

The trading mechanism itself is structured as an off-chain Central Limit Order Book (CLOB).[^1] Traders interact with the platform by signing EIP-712-compliant order messages with their private keys.[^1] These orders, which specify the asset, price, and quantity, are sent to an off-chain matching engine.[^1] This engine, frequently referred to as the "operator," matches buy and sell orders instantly.[^1] Once a match is confirmed, the operator submits the signed orders to the on-chain exchange contracts—specifically the CTFExchange for standard markets or the NegRiskCtfExchange for categorical markets—where the final trade is executed and the collateral is moved.[^1] This process enables a gas-less experience for users when creating or canceling orders, as blockchain transactions are only triggered upon successful matching and settlement.[^1]

### **The Conditional Token Framework (CTF)**

At the core of Polymarket's financial logic is the Gnosis Conditional Token Framewor.[^7] This framework tokenizes event outcomes by locking collateral (typically USDC) and minting a set of tokens that represent the possible results of a given question.[^9] For a standard binary "YES/NO" market, the minting process involves a self-enforcing economic mechanism known as BuyCompleteSets and SellCompleteSets.[^9] 

When a user provides $1.00 of USDC to the contract, they receive one YES share and one NO share. Because the event is binary, exactly one of these shares will be worth $1.00 upon resolution, while the other will be worth $0.00. This ensures that the combined value of a complete set always equals the underlying collateral, creating an arbitrage-enforced peg that maintains the internal consistency of market prices.If the price of a YES share is $0.70 and the price of a NO share is $0, an arbitrageur can purchase a complete set for $1.00, sell both shares for a total of $1.05, and pocket a risk-free profit of $0.05.This mechanism effectively utilizes market participants to maintain price accuracy without the need for central oversight.[^9] 

### **Programmatic Access and API Infrastructure**

To support the growing demand for institutional and algorithmic trading, Polymarket provides a robust API suite.[^7] By early 2026, the API architecture has evolved into several distinct services:

| API Service | Functionality | Primary Use Case |
| :---- | :---- | :---- |
| **Gamma Market Data API** | Provides market listings, event metadata, and live outcome prices. | Market discovery and frontend integration. |
| **CLOB Trading API** | Offers programmatic access to the order book, including depth, bidd/ask spreads, and trade execution. | Automated market making and algorithmic trading. |
| **Data API** | Enables querying of historical price data, user positions, and global volume metrics. | Quant research and trend analysis. |

These services provide 23 REST endpoints and 2 WebSocket endpoints, allowing developers to stream real-time market updates for up to 10 instruments simultaneously.[^13] The API utilizes Ed25519 authentication for security and is optimized for low-latency VPS infrastructure, catering to the millisecond-level precision required for modern predictive analytics.[^13] 

## **Decentralized Truth Verification: The UMA Optimistic Oracle**

One of the most significant technical hurdles for decentralized markets is the "Oracle Problem"—the difficulty of verifying real-world events in a trustless environment.[^12] Polymarket addresses this by utilizing UMA’s Optimistic Oracle, a decentralized verification system that relies on economic incentives rather than a central authority. [^4]

### **The Request-Propose-Dispute Cycle**

The resolution of a Polymarket event follows a rigorous, game-theoretic process designed to ensure the integrity of the data.[^12] When a market reaches its expiration or a triggering event occurs, a request is submitted to the UMA oracle.[^12] The process is structured as follows:

1. **Proposal:** A participant (proposer) asserts the outcome of the event (e.g., "Candidate A won the election") and posts a bond, typically $750 USDC.[^9]  
2. **Optimistic Window:** The system enters a "challenge window," usually lasting two hours.[^4] During this time, the proposal is assumed to be correct unless it is contested.[^12] 
3. **Dispute:** Any other participant (disputer) who believes the proposal is incorrect can challenge it by posting a matching bond.[^12] 
4. **Escalation:** If a dispute is raised, the matter is escalated to UMA’s Data Verification Mechanism (DVM).[^12] $UMA stakers then vote on the correct outcome.[^12] 
5. **Settlement:** Accurate voters and the successful party in the dispute are rewarded with a portion of the loser's bond, while the dishonest actor's bond is slashed.[^12] 

This mechanism is "optimistic" because it avoids the gas costs and latency of a continuous on-chain data feed for every market.[^12] Most markets resolve without a challenge, allowing for fast settlement.[^12] The threat of a dispute, backed by significant financial consequences, creates a "Schelling Point" where participants are incentivized to report the truth.[^12] Unlike "push" oracles like Chainlink, which provide continuous price feeds for financial assets, UMA’s request-driven model is better suited for the subjective or intersubjective data often found in prediction markets, such as cultural events or political outcomes.[^12] 

## **Comparative Analysis of Major Alternatives**

While Polymarket dominates the decentralized space, several other platforms offer competing models for event-based trading, each with distinct regulatory, technical, and economic characteristics.[^16] ### **Kalshi: The Federally Regulated Model**

Kalshi represents the primary centralized alternative to Polymarket in the United States.[^16] Founded in 2018, Kalshi is a Designated Contract Market (DCM) regulated by the Commodity Futures Trading Commission (CFTC).[^5] 
| Feature | Polymarket | Kalshi |
| :---- | :---- | :---- |
| **Asset Class** | Crypto-native (USDC) | CFTC-Regulated Derivatives |
| **User Base** | Global / Web3 Native | US-Focused Retail & Institutional |
| **Market Share (OI)** | \~40% ($409.[^67]M) | \~45% ($474.01M) |
| **Fee Model** | 0.10% Taker Fee (US) | Probability-Weighted Dynamic |
| **Mechanism** | Hybrid CLOB | Institutional Order Book |

Kalshi's growth in 2025 was driven significantly by the sports betting sector, which accounts for 89% of its revenue.[^16] Its pricing model utilizes a complex formula where fees peak at 50/50 odds (approximately 1.75%) and decrease toward the extremes.[^20] Kalshi's regulatory status allows it to partner with established retail brokers like Robinhood and Coinbase, providing a level of institutional trust that remains a challenge for decentralized protocols.[^16] ### **PredictIt: The Academic Experiment**

PredictIt, operated by the Victoria University of Wellington, has been a staple of political forecasting since 2014\.[^22] 
It functions under a CFTC no-action letter, which imposes specific constraints to maintain its status as an educational project.[^22] 
In July 2025, several of these constraints were updated: the per-contract investment cap was raised from $850 to $3,500, and the 5,000-trader-per-market limit was removed entirely.[^23]

PredictIt is characterized by its exceptionally high fees: 10% on net profits and a 5% withdrawal fee.[^20] These fees create what is known as the "PredictIt Premium," where contract prices often trade at levels that reflect the high cost of cashing out rather than the true probability of the event.[^25] However, its demographic—a "crowd of peers" rather than "whales"—has been credited with high predictive accuracy in US political races, with one 2025 study finding a 93% accuracy rate across 2,500 contracts.[^25]

### **Manifold Markets: The Play-Money Social Platform**

Manifold Markets offers a non-financial alternative, utilizing a virtual currency called "Mana" (M$).[^27] Because Mana has no cash value and cannot be redeemed, the platform operates outside the scope of gambling and derivatives regulation, allowing for extreme innovation and the creation of markets on virtually any topic.[^3] 

Manifold uses an AMM model known as "Maniswap," a variation of the Uniswap constant-product formula.[^3] Users start with free Mana and earn more through accurate predictions, successful market creation, and daily engagement.[^3] While Manifold briefly experimented with a real-money "Sweepcash" layer, this was sunsetted in March 2025 due to regulatory concerns in several US states.[^27] Manifold’s value lies in its role as a "social stock exchange for probabilities," where the primary incentive is reputation and calibration rather than financial gain.28

## **Deep Dive into Mechanism Design: AMM vs. CLOB**

The choice of trading mechanism—Automated Market Maker (AMM) or Central Limit Order Book (CLOB)—has profound implications for liquidity, price discovery, and the profitability of participants.[^9] 

### **The Limits of Standard AMMs in Prediction Markets**

In the broader DeFi ecosystem, standard AMMs (like Uniswap) are popular because they provide continuous liquidity without the need for active market makers.[^34] However, in prediction markets, standard AMMs suffer from a critical flaw: realized impermanent loss.[^33] In a typical AMM, liquidity providers (LPs) earn fees from trades between two assets.[^35] In a prediction market, once the event resolves, one of the outcome tokens becomes worth $1.00 and the other becomes $0.00.[^9] This binary outcome ensures that one side of the LP's position always becomes worthless, often eroding all accumulated trading fees.[^33]

To address this, some platforms utilize specialized AMMs. For example, the pm-AMM introduced by Paradigm assumes that outcome tokens follow Gaussian score dynamics, allowing it to concentrate liquidity where trading is most likely to occur rather than spreading it across extreme price ranges.[^9] This approach utilizes the "Loss-vs-Rebalancing" (LVR) framework to make LP economics more predictable.[^9] 

### **The Rise of the CLOB**

Polymarket’s transition to a CLOB reflects a maturation of the industry.[^9] CLOBs are significantly more efficient for mature markets with high trading volumes.[^9] They allow professional market makers to place limit orders at specific prices, providing tighter bid-ask spreads and deeper liquidity.[^9] For market makers, income is derived not just from the spread, but also from platform subsidies and rebates.[^36] This model enables "Inventory Balancing," where market makers skew their quotes to reduce exposure to one side of a contract as the event resolution approaches.[^36]

## **Specialized Protocols: Azuro and Zeitgeist**

Beyond individual platforms, a new generation of infrastructure protocols is building specialized frameworks for decentralized forecasting.[^37]

### **Azuro's Liquidity Tree and vAMM**

Azuro is an infrastructure protocol designed for specialized prediction markets, particularly sports betting.[^37] Its defining innovation is the "Liquidity Tree," a data structure based on the Segment Tree principle.[^40]

The Liquidity Tree allows multiple prediction markets (conditions) to draw from a single, unified "singleton" liquidity pool.[^39] This is functionally distinct from Polymarket, where each market requires its own liquidity pool or order book.[^39] The Liquidity Tree uses a "deferred lazy update" approach: changes in LP balances arising from market resolutions are merely annotated on the parent nodes of the tree.[^40] These changes are only applied "for real" when an individual LP initiates a withdrawal.[^40] This mechanism dramatically reduces gas costs on EVM-compatible chains, enabling the protocol to handle tens of thousands of concurrent markets with  _O(logN)_ time complexity.

Azuro utilizes a "virtual AMM" (vAMM) to price markets.[^37] Data Providers push sell-side odds to the protocol, and bettors move these odds through their trading flows (buy-side).[^39] The singleton LP profits if the spread embedded in the Data Provider's odds exceeds the degree of mispricing exploited by the bettors.[^39]

### **Zeitgeist: Combinatorial Markets and Futarchy**

Zeitgeist, built using the Substrate framework, focuses on the "combinatorial" nature of future events.[^38] In standard markets, you bet on outcome A or outcome B. Zeitgeist allows for complex, multi-layered contracts that reflect the interconnectedness of real-world outcomes.[^43]

A core feature of Zeitgeist is its support for "combinatorial tokens," which allow users to combine outcome tokens from different markets into a single liquidity pool.[^43] This enables "contingent betting," where a user can bet on outcome B *given* outcome A.[^43] For instance, a trader might bet that the Democratic Party will win the general election *if* a specific candidate is nominated.[^43]

Zeitgeist is also a pioneer in "Futarchy," a governance model proposed by economist Robin Hanson.[^38] In a Futarchy system, organizations "vote on values but bet on beliefs".[^44] Decisions are made based on prediction market signals: if a market predicts that firing a CEO will increase the company’s stock price, the protocol can automatically execute that decision.[^44] Zeitgeist utilizes the "Rikiddo" scoring rule, an implementation of the LS-LMSR (Logarithmic Market Scoring Rule), which is mathematically optimized for combinatorial markets and futarchy.[^42]

## **Evaluating Predictive Accuracy: The "Whale" and the "Crowd"**

The primary claim of prediction markets is their superior accuracy compared to traditional polling or expert analysis.[^5] However, by 2026, academic research has begun to highlight significant nuances in this performance.[^26]

### **The Calibration Conflict**

Accuracy is generally measured in two ways: binary outcome success (who won?) and calibration (if the market said 70%, did it happen 70% of the time?).[^26]

* **Polymarket Performance:** A longitudinal analysis by Calibration City found that Polymarket generally maintains better calibration than Kalshi, particularly as markets approach their close.[^49] It is notably more accurate in the "Culture" and "Technology" sectors.[^49] However, because Polymarket allows near-unlimited stakes and attracts "whales," its prices can be distorted by individual beliefs rather than a true collective consensus.[^26]  
* **The "French Whale" Phenomenon:** During the 2024 US election, a single trader on Polymarket bet over $50 million, significantly moving the national odds.[^16] Researchers found that this created "negative serial correlation," where a price spike on one day was typically reversed the next as other traders reacted to the whale's activity rather than to new information.[^26]  
* **Regulated Accuracy:** PredictIt’s $3,500 cap prevents single actors from dominating the market.[^23] This "enforced diversity" is credited with its superior binary accuracy in political races, as it functions more like a massive, incentive-compatible survey of informed voters.[^25]

### **Real-Time Macroeconomic Forecasting**

Despite the "whale" risk, prediction markets have become indispensable for macroeconomic forecasting.[^47] A study by the Federal Reserve Bank of New York in early 2026 compared Kalshi’s macroeconomic markets (e.g., CPI, unemployment, Fed decisions) to traditional surveys and futures markets.[^50] The findings indicated that Kalshi provides a "distributionally rich benchmark" that updates continuously in response to news, often providing a more accurate modal path than professional forecasters who only provide snapshots every six weeks.[^50]

| Forecast Type | Source | Frequency | Accuracy (FOMC Meeting) |
| :---- | :---- | :---- | :---- |
| **Traditional Survey** | FRBNY Survey | Every 6 Weeks | Moderate |
| **Futures Market** | Fed Funds Futures | Daily | High |
| **Prediction Market** | Kalshi | High-Frequency | Perfect (Day Before) |

Kalshi's median and mode forecasts were found to have a statistically significant improvement over fed funds futures on the day prior to FOMC meetings, highlighting the efficiency of prediction markets in aggregating discrete information points into a single probability density.[^50]

## **The Economic Impact of Fee Structures**

Fee structures are the primary driver of friction within prediction markets and fundamentally alter the "true" probability signals.[^20] ### **Comparative Cost Analysis for a $1,000 Position (Binary Outcome)**

| Platform | Fee Model | Total Fees ($1000 spend) | Effective Drag |
| :---- | :---- | :---- | :---- |
| **Polymarket US** | 0.10% Taker Fee | $1.00 | Minimal |
| **Kalshi** | Formula-based (Dynamic) | \~$35.00 (at 50/50 odds) | Moderate |
| **FanDuel Predicts** | Payout-based | $40.00 (approximate) | High |
| **PredictIt** | Profit \+ Withdrawal | \~$140.00 (assuming $500 profit) | Severe |

PredictIt’s fee structure creates a significant "hurdle rate" for traders, which often leads to mispricing as participants require a higher margin of safety to break even.[^20] In contrast, the newly launched Polymarket US has introduced a hyper-competitive 0.10% fee to aggressively lure volume away from Kalshi and other regulated venues.[^2] 
## **Regulatory Evolution and Legislative Challenges in 2026**

The rapid growth of the prediction market sector has triggered a significant legislative and regulatory backlash, particularly regarding the intersection of gambling and financial derivatives.[^1] 
### **The US Regulatory Landscape: Federal vs. State**

By early 2026, a major jurisdictional conflict has emerged between the CFTC and state gaming commissions.[^5] The CFTC, under Chairman Michael Selig, has asserted exclusive federal jurisdiction over prediction markets, viewing them as financial derivatives regulated under the Commodity Exchange Act (CEA).[^52] However, dozens of state attorneys general have challenged this, arguing that they retain the authority to regulate gambling within their borders.[^24]

This tension is most visible in New York, where the **ORACLE Act (Assembly Bill A9251)** was re-introduced in January 2026\.[^51] The bill proposes to ban prediction contracts on sports, elections, and "catastrophic events" (such as wars, natural disasters, or mass shootings).[^56] Proponents of the bill, such as Assemblymember Clyde Vanel, argue that these markets are effectively unlicensed gambling products that "erode the public's confidence in government".[^56] The penalties defined in the act include $10,000 civil fines per violation and daily penalties of $1 million for platforms that defy court-ordered shutdowns.[^56]

### **The Insider Trading Narrative and the Public Integrity Act**

A critical driver of regulatory hostility is the concern over insider trading, particularly regarding geopolitical and national security events.[^51] The "Maduro Trade" of January 2026, where a Polymarket user allegedly profited $400,000 from a bet placed just hours before a US military operation in Venezuela, became a focal point for lawmakers.[^51]

In response, the **Public Integrity in Financial Prediction Markets Act of 2026** was introduced in the US Senate in March 2026 by a bipartisan group including Senators Todd Young, Elissa Slotkin, John Curtis, and Adam Schiff.[^61] The act explicitly prohibits:

* The President and Vice President.[^62]  
* Members of Congress and their staff.[^62]  
* Political appointees and employees of executive or independent regulatory agencies.[^62]

Violators face fines equal to double the profit made on the transaction.[^61] This legislation seeks to close a "dangerous loophole" that currently allows government officials to profit from material nonpublic information (MNPI) on prediction platforms.[^61]

## **Institutionalization and the Path Forward**

Despite the legal challenges, prediction markets have become integrated into the fabric of traditional finance.[^16] ### **ICE, NYSE, and the $9 Billion Valuation**

In October 2025, Polymarket announced a $2 billion strategic investment from Intercontinental Exchange (ICE), valuing the company at $9 billion.[^16] ICE, the parent company of the New York Stock Exchange, has become the "exclusive provider for institutional capital markets" for Polymarket’s data.[^47] This partnership signals a fundamental shift: prediction market data is no longer viewed as a "meme" but as a legitimate financial signal used by institutional investors to hedge macroeconomic risk and allocate capital effectively.[^47]

### **Media and Traditional Sportsbook Integration**

By late 2025 and early 2026, the boundaries between prediction markets and traditional betting began to blur.[^22] 
FanDuel launched "FanDuel Predicts," and DraftKings announced plans to rollout its own event-contract platform in 2026\.[^22] 
Meanwhile, Kalshi secured tie-ins with major media outlets like CNN and CNBC to provide live odds during election and economic coverage.[^47] These developments illustrate the mainstream acceptance of event-contract trading as a superior method for aggregating public information.[^47]

## **Synthesis: The Mechanics of a Mature Ecosystem**

To understand the contemporary prediction market, one must view it as an interplay of three core mechanisms: liquidity provision, truth verification, and regulatory navigation.[^67]

1. **Liquidity:** The move from AMMs to CLOBs has improved capital efficiency but concentrated power in the hands of institutional market makers.[^9] Protocols like Azuro are attempting to decentralize this through "singleton" pools and Liquidity Tree technology, which allows passive LPs to gain diversified exposure to thousands of markets simultaneously.[^39]  
2. **Truth:** Oracles have evolved from simple data feeds to complex, bonded dispute-resolution systems like UMA’s Optimistic Oracle.[^12] This creates a "cryptoeconomic truth layer" that is essential for the decentralized settlement of subjective real-world events.[^14] 
3. **Regulation:** The industry is currently in a state of "legal arbitrage".70 Platforms like Polymarket are building robust compliance frameworks, including identity verification (KYC), real-time surveillance, and partnerships with organizations like the National Futures Association (NFA), to survive the legislative onslaught of 2026.[^6] 
As artificial intelligence (AI) agents increasingly participate in these markets, the speed and granularity of predictions are expected to reach new heights.[^11] Automated agents can analyze vast quantities of data and execute trades in milliseconds, further refining the market's predictive power and pushing the industry toward a model of "real-time truth verification".[^11] 

## **Conclusion**

The evolution of prediction markets from niche blockchain protocols to multi-billion-dollar financial infrastructures represents a paradigm shift in collective intelligence.[^3] Polymarket, through its hybrid architectural design and integration with decentralized oracles, has set the standard for the industry.[^1] However, the detailed comparison with alternatives like Kalshi, PredictIt, and specialized protocols like Azuro and Zeitgeist reveals a diverse ecosystem with varied solutions to the problems of liquidity and truth.[^19] 

The defining challenge for the sector in 2026 and beyond will be the resolution of the ongoing legislative and jurisdictional battles.[^51] While bills like the ORACLE Act in New York represent an existential threat to specific market categories, the institutional backing from entities like ICE and the introduction of integrity-focused legislation like the Public Integrity in Financial Prediction Markets Act suggest that the industry is maturing rather than retreating.[^16] Ultimately, the capacity of these markets to provide accurate, incentive-compatible forecasts makes them "too significant to ignore" for the future of global finance and governance.[^47]

#### **Works cited**

[^1]: The Anatomy of Polymarket: Evidence from the 2024 Presidential Election \- arXiv, accessed April 11, 2026, [https://arxiv.org/html/2603.03136v1](https://arxiv.org/html/2603.03136v1)  
[^2]: Makers and Takers: The Economics of the Kalshi Prediction Market \- Karl Whelan, accessed April 11, 2026, [https://www.karlwhelan.com/Papers/Kalshi.pdf](https://www.karlwhelan.com/Papers/Kalshi.pdf)  
[^3]: What Is Manifold Markets? Free Prediction Platform Rivaling Polymarket And Kalshi In 2026, accessed April 11, 2026, [https://blog.mexc.com/news/what-is-manifold-markets-free-prediction-platform-rivaling-polymarket-and-kalshi-in-2026/](https://blog.mexc.com/news/what-is-manifold-markets-free-prediction-platform-rivaling-polymarket-and-kalshi-in-2026/)  
[^4]: Polymarket's Use of Polygon and UMA for Decentralized Resolution, accessed April 11, 2026, [https://www.mexc.com/learn/article/polymarkets-use-of-polygon-and-uma-for-decentralized-resolution/1](https://www.mexc.com/learn/article/polymarkets-use-of-polygon-and-uma-for-decentralized-resolution/1)  
[^5]: Betting on the Future: A Legal Evaluation of Prediction Markets ..., accessed April 11, 2026, [https://law.vanderbilt.edu/betting-on-the-future-a-legal-evaluation-of-prediction-markets/](https://law.vanderbilt.edu/betting-on-the-future-a-legal-evaluation-of-prediction-markets/)  
[^6]: Polymarket Insider Trading Rules 2026: What the New CFTC-Backed Regulations Actually Mean \- TradingView, accessed April 11, 2026, [https://fr.tradingview.com/news/coinpedia%3Aac4caf233094b%3A0-polymarket-insider-trading-rules-2026-what-the-new-cftc-backed-regulations-actually-mean/](https://fr.tradingview.com/news/coinpedia%3Aac4caf233094b%3A0-polymarket-insider-trading-rules-2026-what-the-new-cftc-backed-regulations-actually-mean/)  
[^7]: The Polymarket API: Architecture, Endpoints, and Use Cases | by Jung-Hua Liu | Medium, accessed April 11, 2026, [https://medium.com/@gwrx2005/the-polymarket-api-architecture-endpoints-and-use-cases-f1d88fa6c1bf](https://medium.com/@gwrx2005/the-polymarket-api-architecture-endpoints-and-use-cases-f1d88fa6c1bf)  
[^8]: Semantic Non-Fungibility and Violations of the Law of One Price in Prediction Markets, accessed April 11, 2026, [https://arxiv.org/html/2601.01706v1](https://arxiv.org/html/2601.01706v1)  
[^9]: Market Mechanics Liquidity Provision Settlement and Price Discovery in Prediction Market Trading Systems \- SoftwareSeni, accessed April 11, 2026, [https://www.softwareseni.com/market-mechanics-liquidity-provision-settlement-and-price-discovery-in-prediction-market-trading-systems/](https://www.softwareseni.com/market-mechanics-liquidity-provision-settlement-and-price-discovery-in-prediction-market-trading-systems/)  
[^10]: Top Crypto Prediction Markets: The Complete 2026 Guide to Trading the Future, accessed April 11, 2026, [https://blog.tokenmetrics.com/p/top-crypto-prediction-markets-the-complete-2026-guide-to-trading-the-future-695f](https://blog.tokenmetrics.com/p/top-crypto-prediction-markets-the-complete-2026-guide-to-trading-the-future-695f)  
[11]: In-depth Research Report on the Evolution of Blockchain Prediction Markets, Technical Architecture, and the Rise of Info Finance | Paul加密奇葩聊 on Binance Square, accessed April 11, 2026, [https://www.binance.com/en-IN/square/post/35544080212761](https://www.binance.com/en-IN/square/post/35544080212761)  
[^12]: Inside UMA Oracle | How Prediction Markets Resolution Works, accessed April 11, 2026, [https://rocknblock.io/blog/how-prediction-markets-resolution-works-uma-optimistic-oracle-polymarket](https://rocknblock.io/blog/how-prediction-markets-resolution-works-uma-optimistic-oracle-polymarket)  
[^13]: Polymarket API Now Available in the U.S.: No Longer Geoblocked (2026 Update), accessed April 11, 2026, [https://www.quantvps.com/blog/polymarket-us-api-available](https://www.quantvps.com/blog/polymarket-us-api-available)  
[^14]: UMA Optimistic Oracle V3 Explained for Developers | ChainScore Blog, accessed April 11, 2026, [https://chainscorelabs.com/blog/other-topics/uma-optimistic-oracle-v3-polymarket/uma-optimistic-oracle-v3-polymarket](https://chainscorelabs.com/blog/other-topics/uma-optimistic-oracle-v3-polymarket/uma-optimistic-oracle-v3-polymarket)  
[^15]: UMA Oracle | PolymarketGuide \- GitBook, accessed April 11, 2026, [https://polymarketguide.gitbook.io/polymarketguide/resolution/uma-oracle](https://polymarketguide.gitbook.io/polymarketguide/resolution/uma-oracle)  
[^16]: Polymarket vs. Kalshi: Who is the king of prediction markets? | Biteye ..., accessed April 11, 2026, [https://www.binance.com/en/square/post/296003725548273](https://www.binance.com/en/square/post/296003725548273)  
[^17]: Top 10 Crypto Prediction Marketplaces in 2026 | BlockchainX, accessed April 11, 2026, [https://www.blockchainx.tech/top-crypto-prediction-marketplaces/](https://www.blockchainx.tech/top-crypto-prediction-marketplaces/)  
[^18]: Best Prediction Market Platforms 2026: Crypto vs. Fiat Compared \- MEXC Exchange, accessed April 11, 2026, [https://www.mexc.com/learn/article/best-prediction-market-platforms-2026-crypto-vs-fiat-compared/1](https://www.mexc.com/learn/article/best-prediction-market-platforms-2026-crypto-vs-fiat-compared/1)  
[^19]: Quick comparison of five prediction market platforms Polymarket, Kalshi, Opinion Labs, Robinhood, BitMart Exchange \- Reddit, accessed April 11, 2026, [https://www.reddit.com/r/btc/comments/1qpnphl/quick\_comparison\_of\_five\_prediction\_market/](https://www.reddit.com/r/btc/comments/1qpnphl/quick_comparison_of_five_prediction_market/)  
[^20]: Prediction Market Fees: Kalshi, Polymarket, Robinhood & Coinbase \- DeFi Rate, accessed April 11, 2026, [https://defirate.com/prediction-markets/fees/](https://defirate.com/prediction-markets/fees/)  
21. Polymarket Supported and Restricted Countries (2026) \- Datawallet, accessed April 11, 2026, [https://www.datawallet.com/crypto/polymarket-restricted-countries](https://www.datawallet.com/crypto/polymarket-restricted-countries)  
[^22]: Beyond Kalshi and Polymarket — The Broader Prediction Market Industry \- Sports Illustrated, accessed April 11, 2026, [https://www.si.com/betting/prediction-market/prediction-markets-101/beyond-kalshi-and-polymarket-the-broader-prediction-market-industry](https://www.si.com/betting/prediction-market/prediction-markets-101/beyond-kalshi-and-polymarket-the-broader-prediction-market-industry)  
[^23]: PredictIt \- Wikipedia, accessed April 11, 2026, [https://en.wikipedia.org/wiki/PredictIt](https://en.wikipedia.org/wiki/PredictIt)  
[^24]: Kalshi vs. PredictIt: Comparing US Political Betting Markets \- MEXC Exchange, accessed April 11, 2026, [https://www.mexc.com/learn/article/kalshi-vs-predictit-comparing-us-political-betting-markets/1](https://www.mexc.com/learn/article/kalshi-vs-predictit-comparing-us-political-betting-markets/1)  
[^25]: The Accuracy War: PredictIt vs. Kalshi vs. Polymarket \- FinancialContent \- Stock Market, accessed April 11, 2026, [https://markets.financialcontent.com/stocks/article/predictstreet-2026-1-19-the-accuracy-war-predictit-vs-kalshi-vs-polymarket](https://markets.financialcontent.com/stocks/article/predictstreet-2026-1-19-the-accuracy-war-predictit-vs-kalshi-vs-polymarket)  
[^26]: Are Polymarket and Kalshi as reliable as they say? Not quite, study warns \- DL News, accessed April 11, 2026, [https://www.dlnews.com/articles/markets/polymarket-kalshi-prediction-markets-not-so-reliable-says-study/](https://www.dlnews.com/articles/markets/polymarket-kalshi-prediction-markets-not-so-reliable-says-study/)  
[^27]: Manifold (prediction market) \- Wikipedia, accessed April 11, 2026, [https://en.wikipedia.org/wiki/Manifold\_(prediction\_market)](https://en.wikipedia.org/wiki/Manifold_\(prediction_market\))  
[^28]: Manifold Markets Review 2026: The Free Community Prediction Platform \- Crypto News, accessed April 11, 2026, [https://cryptonews.com/cryptocurrency/manifold-markets-review/](https://cryptonews.com/cryptocurrency/manifold-markets-review/)  
[^29]: Manifold Markets \- LessWrong, accessed April 11, 2026, [https://www.lesswrong.com/posts/ptEtB4wbLixRuy8MG/manifold-markets-1](https://www.lesswrong.com/posts/ptEtB4wbLixRuy8MG/manifold-markets-1)  
[^30]: Manifold Markets \- EA Forum, accessed April 11, 2026, [https://forum.effectivealtruism.org/topics/manifold-markets](https://forum.effectivealtruism.org/topics/manifold-markets)  
31. Manifold Markets Promo Code: Claim 1K Mana Coins at Signup \- RotoGrinders, accessed April 11, 2026, [https://rotogrinders.com/sports-betting/manifold](https://rotogrinders.com/sports-betting/manifold)  
[^32]: Manifold Markets Review: How It Works, and What Investors Should Know, accessed April 11, 2026, [https://www.valuethemarkets.com/prediction-markets/manifold-markets-review-how-it-works-and-what-investors-should-know](https://www.valuethemarkets.com/prediction-markets/manifold-markets-review-how-it-works-and-what-investors-should-know)  
[^33]: Market Making Mechanisms and Liquidity Dynamics in Blockchain-Based Prediction Markets \- Department of Computer Science, accessed April 11, 2026, [https://www.cs.cit.tum.de/fileadmin/w00cfj/sebis/\_my\_direct\_uploads/20250903\_Parshant\_MA\_Thesis.pdf](https://www.cs.cit.tum.de/fileadmin/w00cfj/sebis/_my_direct_uploads/20250903_Parshant_MA_Thesis.pdf)  
[^34]: Implementing Automated Market Making (AMM) in a Polymarket Clone: A Comprehensive Guide | by Jerald majella | Medium, accessed April 11, 2026, [https://medium.com/@jeraldmajella52/implementing-automated-market-making-amm-in-a-polymarket-clone-a-comprehensive-guide-9cdfb9e8c46c](https://medium.com/@jeraldmajella52/implementing-automated-market-making-amm-in-a-polymarket-clone-a-comprehensive-guide-9cdfb9e8c46c)  
[^35]: Part 1: Will Automated Market Makers (AMMs) disrupt the traditional order book model?, accessed April 11, 2026, [https://www.elixirr.com/en-us/part-1-will-automated-market-makers-amms-disrupt-the-traditional-order-book-model/](https://www.elixirr.com/en-us/part-1-will-automated-market-makers-amms-disrupt-the-traditional-order-book-model/)  
[^36]: Market Making on Prediction Markets: Complete 2026 Guide, accessed April 11, 2026, [https://newyorkcityservers.com/blog/prediction-market-making-guide](https://newyorkcityservers.com/blog/prediction-market-making-guide)  
[^37]: Azuro (AZUR): Understanding the Infrastructure Protocol for Prediction Markets | Gate Learn, accessed April 11, 2026, [https://www.gate.com/learn/articles/azuro-azur-understanding-the-infrastructure-protocol-for-prediction-markets/4923](https://www.gate.com/learn/articles/azuro-azur-understanding-the-infrastructure-protocol-for-prediction-markets/4923)  
[^38]: Zeitgeist: Decentralized Prediction Markets, accessed April 11, 2026, [https://zeitgeist.pm/](https://zeitgeist.pm/)  
[^39]: General · FAQs · Knowledge Hub · Azuro Gem, accessed April 11, 2026, [https://gem.azuro.org/knowledge-hub/faqs/general](https://gem.azuro.org/knowledge-hub/faqs/general)  
[^40]: LiquidityTree · How Azuro Works · Knowledge Hub · Azuro Gem, accessed April 11, 2026, [https://gem.azuro.org/knowledge-hub/how-azuro-works/liquidity-tree](https://gem.azuro.org/knowledge-hub/how-azuro-works/liquidity-tree)  
41. CFTC settles enforcement action against DeFi platform Polymarket \- DLA Piper, accessed April 11, 2026, [https://www.dlapiper.com/insights/publications/2022/1/cftc-settles-enforcement-action-against-defi-platform-polymarket](https://www.dlapiper.com/insights/publications/2022/1/cftc-settles-enforcement-action-against-defi-platform-polymarket)  
[^42]: zeitgeistpm/zeitgeist: An evolving blockchain for prediction markets and futarchy. \- GitHub, accessed April 11, 2026, [https://github.com/zeitgeistpm/zeitgeist](https://github.com/zeitgeistpm/zeitgeist)  
[^43]: Combinatorial Betting \- Zeitgeist Documentation, accessed April 11, 2026, [https://docs.zeitgeist.pm/docs/learn/combinatorial-tokens](https://docs.zeitgeist.pm/docs/learn/combinatorial-tokens)  
[^44]: Dialogue with Zeitgeist | Unlocking a New Era in Decentralized Prediction Markets with the Power of the Polkadot Ecosystem | by OneBlock+ | OneBlock Community | Medium, accessed April 11, 2026, [https://medium.com/oneblock-community/dialogue-with-zeitgeist-unlocking-a-new-era-in-decentralized-prediction-markets-with-the-power-of-549419c44734](https://medium.com/oneblock-community/dialogue-with-zeitgeist-unlocking-a-new-era-in-decentralized-prediction-markets-with-the-power-of-549419c44734)  
[^45]: Zeitgeist \- A Prediction Markets protocol helping steer humanity towards truth and progress, accessed April 11, 2026, [https://forum.polkadot.network/t/zeitgeist-a-prediction-markets-protocol-helping-steer-humanity-towards-truth-and-progress/1151](https://forum.polkadot.network/t/zeitgeist-a-prediction-markets-protocol-helping-steer-humanity-towards-truth-and-progress/1151)  
[^46]: Decentralized Prediction Market Protocol Zeitgeist: Pioneering a New Paradigm for Future Governance? | by OneBlock+ | OneBlock Community | Medium, accessed April 11, 2026, [https://medium.com/oneblock-community/decentralized-prediction-market-protocol-zeitgeist-pioneering-a-new-paradigm-for-future-governance-c845b2c3ef4d](https://medium.com/oneblock-community/decentralized-prediction-market-protocol-zeitgeist-pioneering-a-new-paradigm-for-future-governance-c845b2c3ef4d)  
[^47]: Prediction Markets: How Sure Is the Bet? \- GARP, accessed April 11, 2026, [https://www.garp.org/risk-intelligence/technology/prediction-markets-how-260227](https://www.garp.org/risk-intelligence/technology/prediction-markets-how-260227)  
[^48]: Prediction Markets? The Accuracy and Efficiency of $2.4 Billion in the 2024 Presidential Election \- ResearchGate, accessed April 11, 2026, [https://www.researchgate.net/publication/398449904\_Prediction\_Markets\_The\_Accuracy\_and\_Efficiency\_of\_24\_Billion\_in\_the\_2024\_Presidential\_Election](https://www.researchgate.net/publication/398449904_Prediction_Markets_The_Accuracy_and_Efficiency_of_24_Billion_in_the_2024_Presidential_Election)  
[^49]: Kalshi vs Polymarket? \- Medium, accessed April 11, 2026, [https://medium.com/@gaetanlion/kalshi-vs-polymarket-5acbbb0dc049](https://medium.com/@gaetanlion/kalshi-vs-polymarket-5acbbb0dc049)  
[^50]: Kalshi and the Rise of Macro Markets \- Federal Reserve Board, accessed April 11, 2026, [https://www.federalreserve.gov/econres/feds/files/2026010pap.pdf](https://www.federalreserve.gov/econres/feds/files/2026010pap.pdf)  
51. The Empire State's Existential Bet: Will New York Shutdown the Prediction Market Boom?, accessed April 11, 2026, [https://markets.financialcontent.com/stocks/article/predictstreet-2026-1-21-the-empire-states-existential-bet-will-new-york-shutdown-the-prediction-market-boom](https://markets.financialcontent.com/stocks/article/predictstreet-2026-1-21-the-empire-states-existential-bet-will-new-york-shutdown-the-prediction-market-boom)  
[^52]: Congress and Prediction Markets: The Current Landscape, the Outlook Ahead and What Clients Should Be Doing Now | Paul Hastings LLP, accessed April 11, 2026, [https://www.paulhastings.com/insights/client-alerts/congress-and-prediction-markets-the-current-landscape-the-outlook-ahead-and-what-clients-should-be-doing-now](https://www.paulhastings.com/insights/client-alerts/congress-and-prediction-markets-the-current-landscape-the-outlook-ahead-and-what-clients-should-be-doing-now)  
[^53]: Prediction markets are back in the spotlight, this time because of the war in Iran \- ICT, accessed April 11, 2026, [https://ictnews.org/news/prediction-markets-are-back-in-the-spotlight-this-time-because-of-the-war-in-iran/](https://ictnews.org/news/prediction-markets-are-back-in-the-spotlight-this-time-because-of-the-war-in-iran/)  
[^54]: States Clash with Prediction Markets Over Sports Betting Laws \- NYC Today, accessed April 11, 2026, [https://nationaltoday.com/us/ny/new-york/news/2026/03/08/states-clash-with-prediction-markets-over-sports-betting-laws/](https://nationaltoday.com/us/ny/new-york/news/2026/03/08/states-clash-with-prediction-markets-over-sports-betting-laws/)  
[^55]: Kalshi and Polymarket ban insider trading as senators look to curb prediction markets, accessed April 11, 2026, [https://www.theguardian.com/technology/2026/mar/24/kalshi-polymarket-insider-trading-regulation](https://www.theguardian.com/technology/2026/mar/24/kalshi-polymarket-insider-trading-regulation)  
[^56]: New York Bill Restricting Prediction Markets Re-Introduced For 2026 Session \- DeFi Rate, accessed April 11, 2026, [https://defirate.com/news/new-york-bill-restricting-prediction-markets-re-introduced-for-2026-session/](https://defirate.com/news/new-york-bill-restricting-prediction-markets-re-introduced-for-2026-session/)  
[^57]: New York Lawmakers Open 2026 Session With Proposal to Ban Prediction Market Sports Betting | Gambling Insider, accessed April 11, 2026, [https://www.gamblinginsider.com/news/102657/new-york-lawmakers-open-2026-session-with-proposal-to-ban-prediction-market-sports-betting](https://www.gamblinginsider.com/news/102657/new-york-lawmakers-open-2026-session-with-proposal-to-ban-prediction-market-sports-betting)  
[^58]: NY A09251 \- BillTrack50, accessed April 11, 2026, [https://www.billtrack50.com/billdetail/1910589](https://www.billtrack50.com/billdetail/1910589)  
[^59]: 2026-04-09\_Letter\_Polymarket-National Security \- Senator Richard Blumenthal, accessed April 11, 2026, [https://www.blumenthal.senate.gov/imo/media/doc/2026-04-09\_letter\_polymarket-national\_security.pdf](https://www.blumenthal.senate.gov/imo/media/doc/2026-04-09_letter_polymarket-national_security.pdf)  
[^60]: White House warns staff as Iran bets add to growing insider trading concerns, accessed April 11, 2026, [https://www.tradingview.com/news/cointelegraph:2b9fc3243094b:0-white-house-warns-staff-as-iran-bets-add-to-growing-insider-trading-concerns/](https://www.tradingview.com/news/cointelegraph:2b9fc3243094b:0-white-house-warns-staff-as-iran-bets-add-to-growing-insider-trading-concerns/)  
61. Young, Slotkin Lead Bipartisan Bill to Stop Insider Trading from Government Officials on Prediction Markets, accessed April 11, 2026, [https://www.young.senate.gov/newsroom/press-releases/young-slotkin-lead-bipartisan-bill-to-stop-insider-trading-from-government-officials-on-prediction-markets/](https://www.young.senate.gov/newsroom/press-releases/young-slotkin-lead-bipartisan-bill-to-stop-insider-trading-from-government-officials-on-prediction-markets/)  
[^62]: S4188 | US Congress 2025-2026 | Public Integrity in Financial Prediction Markets Act of 2026 \- Legislative Tracking | PolicyEngage, accessed April 11, 2026, [https://trackbill.com/bill/us-congress-senate-bill-4188-public-integrity-in-financial-prediction-markets-act-of-2026/2838997/](https://trackbill.com/bill/us-congress-senate-bill-4188-public-integrity-in-financial-prediction-markets-act-of-2026/2838997/)  
[^63]: Polymarket reenters US with launch of trading for waitlist members \- SBC Americas, accessed April 11, 2026, [https://sbcamericas.com/2025/12/03/polymarket-reenters-us-waitlist-launch/](https://sbcamericas.com/2025/12/03/polymarket-reenters-us-waitlist-launch/)  
[^64]: Polymarket Receives CFTC Approval to Resume US Operations After Years Offshore, accessed April 11, 2026, [https://www.thebulldog.law/polymarket-receives-cftc-approval-to-resume-us-operations-after-years-offshore](https://www.thebulldog.law/polymarket-receives-cftc-approval-to-resume-us-operations-after-years-offshore)  
[^65]: Polymarket Makes Long-Awaited US Return With Limited Rollout | Finance Police on Binance Square, accessed April 11, 2026, [https://www.binance.com/en/square/post/33263339858881](https://www.binance.com/en/square/post/33263339858881)  
[^66]: The perils of election prediction markets \- Good Authority, accessed April 11, 2026, [https://goodauthority.org/news/the-perils-of-election-prediction-markets/](https://goodauthority.org/news/the-perils-of-election-prediction-markets/)  
[^67]: How Different Prediction Markets Actually Work. | by Felix Osuya \- Medium, accessed April 11, 2026, [https://felixosuya.medium.com/how-different-prediction-markets-actually-work-0af2598c1bbf](https://felixosuya.medium.com/how-different-prediction-markets-actually-work-0af2598c1bbf)  
[^68]: Liquidity Providers · Protocol Actors · How Azuro Works · Knowledge Hub, accessed April 11, 2026, [https://gem.azuro.org/knowledge-hub/how-azuro-works/protocol-actors/liquidity-providers](https://gem.azuro.org/knowledge-hub/how-azuro-works/protocol-actors/liquidity-providers)  
[^69]: Introducing Azuro's Liquidity Tree: A New Liquidity Pool Design for Specialized Prediction Markets \- Medium, accessed April 11, 2026, [https://azuroprotocol.medium.com/introducing-azuros-liquidity-tree-a-new-liquidity-pool-design-for-specialized-prediction-markets-625d68be4727](https://azuroprotocol.medium.com/introducing-azuros-liquidity-tree-a-new-liquidity-pool-design-for-specialized-prediction-markets-625d68be4727)  
70. Prediction Markets Trading Without KYC: Arbitraging US Bans via Offshore DEX 2026 Workarounds \- OneKey Blog, accessed April 11, 2026, [https://onekey.so/blog/ecosystem/prediction-markets-trading-without-kyc-arbitraging-us-bans-via-offshore-dex-2026-workarounds/](https://onekey.so/blog/ecosystem/prediction-markets-trading-without-kyc-arbitraging-us-bans-via-offshore-dex-2026-workarounds/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEwAAAAYCAYAAABQiBvKAAADU0lEQVR4Xu2YSciNURjHHzNliGShkJKUhY0yLMgQFkphJfmyUIawIH07GwtDShlTJMWCQllYmD7zUISNUDKljJF59vydc7zP/d9z7n257v3cur/613v+z3PO+57znvecc69Igwb1xiQ26ozpbPwJA1TbVJtU3SkWY76qmbzeqiHk/c/MUO1ksxwbVD9Uc3y5v+qp6uPvjGL6qR6b8hhxbUAnjF8L0OE3kt1/V0HU8U2yODTBxC6rZplykrbiKp/igOer6jubHtTrzKa0zoAF7IDEwHMNYtOTqlMAku6yaRgvxW8DjFZ9Ii/QWgPWRnVEdVDcM8TWplKDck+1kU3LIyndAAgzcD/5X6R47Qq01oAtVQ3316lZhi8mxVSJ1/nFWHHBFvKZnuLyXpEPrwt5gdSA4VM4pzov2VrJ9FCtFLemdlKNUL2VMm/e88Jc43nxHHbjGqxaY8oxkgOGGYJgbA2yzBaXd8143byXIjZgF1V3THm9FG8oq8XV7arq5a/3qCb763LYHLwclG8Zb6+4tkuBOqPYBAjkeYjb4vJwfAiM814KHrAF3mPgnaXyclPGMhCrFwPr12HyuI952kLOXDb7+EDeBjgPDbJn4QGLtQGQwx1aaMo7vJcHu35ZD/XX+fJnE0uBfMz0Atr5wAcOEDPF5fGRo8n7KRA7SeVY/iFxPp4HYEG+koXlnbj1Kw8v2fCEew9VraJYDORiuSgi1QlLKmekxP1A3gHD4m99HB7vizv3wcd1XmLtg6PiYjg6pTYpC3KXsAleS/om4IG4eAcOSLZzpkDMzkrMmlh+2HgCsZw8tFcdZ9MTjkV520YezphRELzBpvJMXGdKgbod2fQgdj3i4TdqYJj3cIwIYGbh07ogbmZgV5tm4jHwOT9XXeKA4b2UX34CZQcWN0MStn00imucfcqBvGXkTVQ9UT0U9xsTs9iyW7K3jWMKZoblgI/FFGOfuHvg/IVzF34rxsDLWcRmBPzrkrpXxayQ/AtyHrZK8QAH0IntbFaBm6rFbP5L0BGeJX/LVdUZNj1Y/DGbqk3VZldgihSe3isFn5QdGLyMFsl3fqqUY+L6U3XWquaxWQEDVVtUp1WbVX0Lw1UB/8hgg6kZTWzUGfbXRYMGNeYnkk37KeeKdKAAAAAASUVORK5CYII=>
