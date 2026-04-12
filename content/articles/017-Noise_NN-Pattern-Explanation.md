---
title: "Explanating Noise_NN Pattern"
description: "Article 17: The Noise_NN pattern is the simplest interactive handshake in the Noise Protocol Framework. It stands for 'No static keys, No pre-shared knowledge.'"
date: 2025-11-17
tags:
- Blockchain
- Crypto
- Cryptocurrency
- DeFi
- Finance
- Fintech
- smartcontract

draft: false
series: mining-foundations
---

# Explanating Noise_NN Pattern

The **Noise_NN** pattern is the simplest interactive handshake in the Noise Protocol Framework. It stands for “No static keys, No pre-shared knowledge.”

**Handshake Structure**  
```
NN:
  -> e
  <- e, ee
```

**Step-by-Step**  
1. Initiator sends only its ephemeral public key.  
2. Responder sends its ephemeral public key and both parties compute the ee Diffie-Hellman shared secret to derive transport keys.

**Security Properties**  
- Provides confidentiality and forward secrecy.  
- Provides **no authentication whatsoever**.

**Analogy**: Noise_NN is like two strangers quickly agreeing on a temporary secret code in a public square. They can talk privately for this conversation, but neither knows or proves who the other person really is.

**Relevance to Mining**  
Noise_NN is almost never used alone for Stratum V2 pool connections because authentication is essential. It occasionally appears in internal/test scenarios or behind stronger outer tunnels (e.g., WireGuard). Best practice is to avoid NN for anything exposed to the public internet and to prefer authenticated patterns like IK or XK.

