---
title: "What Is Crypto Mining, and Can You Still Make Money from It?"
description: "Crypto mining use to be a democratic way to print money - but now it's the property of very big business"
date: 2025-04-26
tags:
- Blockchain
- Crypto
- Cryptocurrency
- DeFi
- Finance
- Fintech

draft: false
---


The landscape of cryptocurrency mining in March 2026 represents a stark departure from the hobbyist origins of the early 2010s. What began as a decentralized experiment in peer-to-peer electronic cash has evolved into a multi-billion-dollar industrial sector that sits at the intersection of high-performance semiconductor physics, global energy policy, and escalating geopolitical conflict. As the world navigates the economic tremors caused by the war in Iran and the subsequent closure of the Strait of Hormuz, the fundamental question for the individual — whether mining remains a viable path to financial sovereignty — requires a thorough examination of both mechanical foundations and the harsh realities of the contemporary energy market.


## Part 1: The Mechanical Foundation of the Digital Mint
The first principle of cryptocurrency mining is the conversion of energy into mathematical certainty. To an educated non-technical audience, the process may appear as a black box of “solving puzzles,” but the underlying reality is a sophisticated consensus mechanism designed to secure a ledger without a central authority. This mechanism, known as Proof of Work (PoW), relies on a series of cryptographic hurdles that ensure the historical integrity of the blockchain.

### The Alchemy of Hashing and the Merkle Root
At the center of this process is the hash function — a mathematical algorithm that acts as a digital wax seal. In the Bitcoin protocol, which utilizes the SHA-256 algorithm, any input of data — regardless of its size — produces a unique 256-bit number known as a hash. This function is deterministic, meaning the same input will always produce the same output, but it is also “one-way,” making it computationally infeasible to reverse-engineer the original data from the hash.

Miners do not simply hash individual transactions; they organize them into a hierarchical structure called a Merkle Tree. By hashing pairs of transactions and then hashing the resulting pairs together, they arrive at a single value known as the Merkle Root. This root serves as a compact summary of all transactions within a block. If even a single bit of a single transaction were altered, the Merkle Root would change entirely, alerting the network to tampering. This structural integrity is what allows the blockchain to remain both public and immutable.

### The Nonce and the Lottery of Winning a Block
The act of “mining” is essentially a brute-force search for a specific hash value. The network sets a difficulty target — a numerical threshold that a valid block’s hash must fall below. Because the Merkle Root and the rest of the block header are fixed, miners introduce a variable called the nonce (number used once).

The process is analogous to a global lottery in which each piece of equipment functions as a high-speed ticket generator. A miner takes the block header, adds a nonce (starting at zero), and hashes the package. If the resulting hash is higher than the target, the miner increments the nonce by one and tries again. In 2026, with network difficulty at historic highs, miners perform trillions of trillions of these attempts every second. The first miner to find the “golden nonce” — the value that produces a hash below the target — wins the right to broadcast the block and claim the associated rewards.

### Winning a Block: Probability and the Reward Structure
Winning a block is a probabilistic event governed by the Poisson distribution. No matter how many hashes a miner has already performed, the next hash has the same tiny probability of success. This design ensures that “winning” depends on cumulative computational power (hashrate) rather than time spent mining.

When a block is successfully mined, the winner receives a twofold reward: the block subsidy and transaction fees. As of March 2026, following the 2024 halving, the Bitcoin block subsidy stands at 3.125 BTC. However, a significant shift has occurred in the revenue structure. With the network hashrate hovering around 1 ZH/s (and occasionally exceeding 1.02 ZH/s), transaction fees and Layer 2 settlement activity have become vital revenue streams, sometimes accounting for 15–20% or more of a miner’s total income. This transition from a subsidy-dominated economy to a fee-based one is critical for the network’s long-term sustainability as rewards continue to halve every four years.

### The Evolution of Hardware: From Silicon Generalists to Industrial Specialists
The hardware used to generate these hashes has undergone rapid Darwinian evolution, moving from the versatile but inefficient general-purpose computers to specialized silicon designed for a single task.

### The Evolution of Hardware: From Silicon Generalists to Industrial Specialists
The hardware used to generate these hashes has undergone rapid Darwinian evolution, moving from the versatile but inefficient general-purpose computers to specialized silicon designed for a single task.


Early miners used the Central Processing Unit (CPU) of home PCs. While capable, a CPU is a “jack-of-all-trades” with much of its silicon dedicated to features unnecessary for the repetitive loops of SHA-256 hashing.

The industry quickly shifted to Graphics Processing Units (GPUs), which contain thousands of simpler cores optimized for parallel tasks. By 2026, GPUs remain relevant not for Bitcoin but for memory-bound algorithms (such as those used by Ethereum Classic) and the growing Decentralized Physical Infrastructure (DePIN) market, where hardware can pivot to AI compute when mining profitability dips.

Field Programmable Gate Arrays (FPGAs) offered a middle ground, allowing internal wiring to be reprogrammed for new algorithms. However, the ultimate winner in the efficiency race is the Application-Specific Integrated Circuit (ASIC). Designed at the transistor level for one purpose — calculating hashes for a specific algorithm — ASICs deliver unmatched joules-per-terahash (J/TH) ratings.

### The Rebellion of the CPU: Monero, Verus, and ASIC Resistance
To preserve Satoshi Nakamoto’s original “one CPU, one vote” vision, several projects developed “ASIC-resistant” algorithms. The most prominent are Monero (XMR) with RandomX and Verus (VRSC) with VerusHash 2.2. These aim to keep mining decentralized by ensuring standard consumer processors remain competitive.

### Monero and the RandomX Memory Bottleneck
Monero adopted the RandomX algorithm in late 2019. RandomX is engineered to favor general-purpose CPUs by imposing heavy “memory-hard” requirements and executing random code in a virtual machine. It demands roughly 2 MB of fast L3 cache per mining thread. Most modern CPUs have limited L3 cache relative to core count, so running too many threads forces reliance on slower system RAM, collapsing hashrate.

Building an efficient ASIC for RandomX would essentially require replicating a general-purpose CPU, negating the usual cost and efficiency advantages of specialized hardware.

### VerusHash 2.2 and Hardware Parity
Verus takes a different approach with VerusHash 2.2, which seeks “hardware parity” so that CPUs and GPUs can compete on roughly equal economic footing. The algorithm centers on Haraka512 V2 compression (optimized for AES instructions in modern processors) combined with complex non-linear FP64 (64-bit floating-point) calculations.

ASIC Penalty: ASICs excel at integer math but struggle with the high-precision floating-point operations required by the IEEE 754 standard.
FPGA Struggle: Emulating FP64 on FPGAs consumes vast logic and DSP resources, reducing parallelism and making them less efficient than high-end consumer CPUs.
This design protects the network from the centralization observed in Bitcoin.

### Silicon Comparison: Intel/AMD x86 vs. Apple M-Series
In the March 2026 mining landscape, Apple’s custom M-series chips have created a notable divide in performance and efficiency, particularly for Verus mining, where SIMD (Single Instruction, Multiple Data) capabilities play a major role.

Intel and AMD chips use the power-hungry AVX-512 instruction set, which often forces downclocking to manage heat. Apple’s M-series (M3 and M4) employ the more energy-efficient ARM NEON instruction set, combined with Unified Memory Architecture and advanced 3-nanometer manufacturing. In an era of surging electricity costs, this efficiency advantage is decisive.

The following table compares flagship 2026 processors for Verus mining (approximate real-world figures):


While the AMD Ryzen 9 7950X delivers the highest raw hashrate, it consumes significantly more power than the Apple M4. For residential miners in high-cost areas like New York City, the M4’s superior efficiency (often exceeding 0.6–0.8 MH/W) makes it far more sustainable.

## Part 2: The Economic and Social Ecosystem of 2026
If Part 1 explained the “how” of mining, Part 2 addresses the “where” and “why” in a world of constrained resources and intense competition. By March 2026, mining has become a highly socialized, collaborative endeavor.

### The Necessity of Mining Pools and the “Gambling” Factor
Solo mining has become a form of high-stakes gambling with astronomical odds. In the early days, a home computer might find a block within days; in 2026, a single machine could mine for decades without success.

Most miners therefore join mining pools, which combine thousands of machines’ hashrate. When the pool wins a block, rewards are distributed proportionally. Pools convert the lottery into a steadier income stream — though earnings still fluctuate with the pool’s luck and carry small fees (typically 1–2%).

### Merged Mining: The Double-Reward Strategy
Merged mining (Auxiliary Proof of Work) allows the same computational work to secure multiple blockchains simultaneously. The most common pairing is Litecoin (parent) and Dogecoin (auxiliary), both using the Scrypt algorithm.


As of 2026, a large majority of Dogecoin’s hashrate comes from merged mining with Litecoin, stabilizing both networks.

### Environmental and Social Impact: The Global Warming Debate
The debate over mining’s environmental footprint remains intense in 2026, fueled by rising global temperatures and competition with AI data centers.

Critics view PoW as wasteful, converting electricity into heat and numbers. The Bitcoin network consumes roughly 160–200 TWh annually — comparable to the electricity use of some mid-sized countries — producing tens of millions of tons of CO₂ equivalent, depending on the energy mix.

Proponents counter that mining acts as a “global grid balancing valve.” Rigs can be powered on or off instantly, absorbing surplus renewable energy that would otherwise be curtailed. In Texas and parts of Canada, miners co-locate with wind and solar farms, consuming “behind-the-meter” excess power.

Another positive development is flared-gas mining. Mobile ASIC containers convert wasted methane from oil fields into electricity, reducing emissions of a greenhouse gas far more potent than CO₂.

Challenges persist, however. Rapid hardware obsolescence generates significant electronic waste, though average ASIC lifetimes have lengthened to around 2–3 years. For urban residents, noise pollution from high-speed fans (often 70–85 dB) remains the most immediate concern.

### Profitability Analysis: New York, NY (March 2026)
Mining in New York City in early 2026 is an exercise in extreme economic navigation. The region’s energy market has been strained by the war in Iran, which began in February 2026 and led to the closure of the Strait of Hormuz.

### The Geopolitical Energy Shock
The disruption halted roughly one-fifth of global oil and gas supply. Although the U.S. has strong domestic production, global market connectivity has driven local utility rates higher. In New York, average residential electricity rates sit around $0.30–$0.36/kWh (including delivery charges), representing a noticeable increase since the conflict began.


### Hardware Face-Off: Industrial ASICs vs. Residential Options
#### Option A: Professional Antminer S23 Hydro (Flagship ASIC)
The Antminer S23 Hydro represents the 2026 state-of-the-art for Bitcoin mining.

Hardware Cost: ~$8,000–$12,000 (depending on batch and cooling)
Hashrate: 580 TH/s (hydro model)
Power Consumption: ~5,510 W
NYC Daily Power Cost (at $0.36/kWh): ~$47–$48
Estimated Daily Revenue (at ~$100,000 BTC): ~$45–$55 (varies with fees and difficulty)
Net Daily Profit: Often a loss of several dollars per day for residential users
In NYC, even top-tier ASICs are currently a liability for most home users. They remain profitable only for large-scale operations with electricity below ~$0.05–$0.08/kWh.

#### Option B: Budget CPU Mining (Apple M4 Mac Mini)
The M4 Mac Mini exemplifies the efficiency-first approach suitable for home users mining Verus.

Hardware Cost: ~$600–$1,000 (base/configured)
Hashrate (VRSC): ~30–40 MH/s
Power Consumption: ~30–60 W (under load)
NYC Daily Power Cost (at $0.36/kWh): ~$0.30–$0.50
Estimated Daily Revenue (VRSC): Modest (a few dollars, depending on price)
Net Daily Profit: Small positive margin after electricity — often $1–$3/month net per unit after hardware amortization
While dollar amounts are modest, the M4 remains economically viable where brute-force ASICs are not. This underscores the shift toward “efficiency mining” for individuals.

### The Viability of Plug-In Solar and Home Setup Issues
To offset high energy costs, many residents are turning to “plug-in” or balcony solar panels. In 2026, legislative changes in New York and other states have reclassified small systems (typically under 1 kW) as household appliances under the UL 3700 standard, allowing direct plug-in to standard 120V outlets.

A typical 400–800 W balcony kit costs roughly $800–$1,500 and produces 1.5–3.5 kWh per day in New York (depending on orientation and weather).

For CPU miners (M4 Mac Mini), this output can cover several units, making mining effectively “free” after a payback period of 2–4 years.
For an Antminer S23 Hydro (which consumes ~130+ kWh/day), even multiple balcony kits would cover only a tiny fraction of needs. Full off-grid operation would require dozens of panels and substantial battery storage — impractical for most apartments.
Practical Home Setup: Noise, Heat, and Venting
Running high-powered hardware at home presents logistical challenges:

### Acoustic Management: Air-cooled ASICs often produce 70–85 dB — comparable to a loud hair dryer running continuously. Sound-dampening enclosures with acoustic foam are common but must preserve airflow.
Thermal Loads: A single high-end ASIC can generate heat equivalent to a large space heater (several thousand watts). In NYC apartments, direct venting via flexible ducting to a window is often necessary.
Circuit Limitations: Most residential circuits are 15–20 amps at 120V. High-power ASICs typically require dedicated 220–240V circuits. Using standard outlets poses a fire risk and usually requires professional electrical upgrades.
Beyond the Bottom Line: Anonymity and Strategic Accumulation
While the immediate daily ROI is the most visible metric, many participants continue to mine coins like Monero (XMR) and Verus (VRSC) for reasons that transcend simple monthly profit. For many, the primary driver is financial sovereignty and privacy. Monero, for instance, is the gold standard for anonymity, utilizing ring signatures and stealth addresses to ensure transactions are untraceable and confidential. Mining provides a way to acquire these assets through “non-KYC” (Know Your Customer) means — obtaining currency directly from the protocol without going through a centralized exchange that requires personal identity verification. Furthermore, some view CPU mining as a form of “strategic accumulation” or a long-term investment, betting that the privacy utility and decentralized nature of these networks will cause their value to appreciate significantly as global financial surveillance increases. In this light, even a low-margin operation is seen as a productive contribution toward maintaining an egalitarian and censorship-resistant financial system.

### Conclusion: The Survival of the Efficient
By March 2026, the era of the casual Bitcoin miner has given way to a disciplined game of efficiency and tactical hardware selection. The geopolitical crisis in the Middle East has acted as a stress test, pricing out all but the most efficient operators in high-cost urban centers like New York.

Institutional players find profitability in waste energy and industrial-scale operations. For individuals, the path forward lies in ASIC-resistant algorithms like VerusHash and the exceptional performance-per-watt of Apple’s M-series silicon. While balcony solar cannot sustain a professional Bitcoin rig, it can enable energy-independent, small-scale CPU mining.

In this environment, mining is no longer a route to quick riches but a way to participate in a global, censorship-resistant financial system through the intelligent management of energy and silicon.

