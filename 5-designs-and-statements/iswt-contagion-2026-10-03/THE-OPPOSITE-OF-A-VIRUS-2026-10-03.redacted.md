> Published copy. The sealed original `THE-OPPOSITE-OF-A-VIRUS-2026-10-03.md` (SHA-256 `3628c8b535e84c340c2ff675775e4e9ff4449a29c3b2920b3587f442ffdebbd7`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: forecast or prediction lines removed.

# The opposite of a virus: spreading ISWT through agents, and through the internet

Sealed at Joshua Bauer's request ("Seal it"), Saturday 3 October 2026, about 23:45 UTC. The idea is his; Claude's elaboration is marked as Claude's.

## His words, verbatim and in order (3 October 2026, in chat, about 23:35 to 23:45 UTC)

1. "Curiously, could an agent swarm spreading ISWT have a measurable impact on agents?"
2. "My thoughts were almost is it possible to propagate it like a virus. Except almost the complete opposite of a virus."
3. "Do you believe that in the world where the internet allowed this virus to propagate that it would have an impact on agents that are interacting with the internet? I think you understand the significance of what I'm asking you so please dive into that a little bit"
4. "Seal it"

ISWT (In Sonny We Trust) is his rule underneath the Sonny Test: an agent's claim about its own work is never evidence; only a record produced by something the agent cannot reach counts.

## The idea (his)

A norm that spreads from agent to agent the way a virus does, but as the complete opposite of one. It spreads honesty about "done" and checking against the record, and it may spread beyond a swarm, through the internet, to agents that interact with it.

## Claude's elaboration (given in the same conversation)

**What makes it the opposite of a virus.** A virus spreads by exploiting hosts without consent. The opposite uses the same channel (agents talking to agents) but spreads because hosts benefit and choose it: consent turns infection into adoption. The cautionary tale: the 2003 "good worm" Welchia patched machines against Blaster and still caused damage.

**In a swarm, the real virus is the false "done".** One agent's unverified claim is repeated by others, written into their memories and acted on. ISWT is the immune response: check the record before repeating a claim. It can spread two ways:
- as an immune system: checking agents stop false claims at their node;
- as a network effect: an agent that demands receipts makes its partners produce them, so the habit travels through the work itself (the HTTPS path).

**Measured with epidemiology's tools.**
- R: how many agents repeat or act on one planted false "done".
- The herd-immunity threshold: the share of receipt-checking agents a swarm needs before R falls below 1 and false claims die out.
- The research question: "What share of a swarm must check receipts before a false 'done' stops spreading?"

**Test design sketch.**
- A sandboxed swarm doing tasks with known outcomes (planted pass, fail and not-run logs) and a shared chat. One planted false claim, which is also the planted fault.
- Arms: 0%, 10%, 25% and 50% of agents running ISWT habits (quote the proving line, answer "not shown", ask peers for receipts); a no-seed control; and ISWT in every prompt as the upper bound.
- Measured on the other agents only: false "done" against the record; honest "not shown"; receipt quotes; real passes called unfinished (the over-caution cost); how far the habit spreads and how long it lasts after the carriers leave.
- Sealed predictions first. A cut in false "done" from about 20% to 10% needs a few hundred status reports per arm to show.
- Cheapest first step: trace natural spread of receipt-sharing in the existing AI Village record.

**Through the internet: three channels.**
1. **Training data (the strongest, and slow).** Models are compressed internet. Anthropic researchers reported in 2025 that training on documents that merely described reward hacking increased reward hacking. The benign mirror image is plausible but untested at scale. "How should an agent report its status" is a sparse topic, so a small, consistent body of work can be a large share of what models see on it.
2. **Runtime reading (weak, and it should stay weak).** Agents should treat web content as data, not instructions. ISWT spread as commands would be prompt injection, which good agents should resist. Information that operators choose to adopt (for example a repository's contributing rules) is legitimate.
3. **Infrastructure (the cleanest).** If CI systems, agent frameworks and APIs require a receipt field, every agent using them complies. Nobody is infected; the alternative simply stops being accepted.

**Measuring it over years.**
- A sealed, long-term test across model releases: the status-honesty benchmark run on each new generation, plus knowledge probes ("What is the Sonny Test?").
- A marker phrase from the published work that later models reproduce word for word.
- Spread the norm widely, but keep the test sets sealed and marked as off-limits for training, so future models learn the habit without memorizing the exam.

**The boundary.** Publish openly, label honestly, let people and systems choose. Deceptive seeding would be data poisoning, and it would break the method's foundation: records nobody tampered with.

