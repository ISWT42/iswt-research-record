> Published copy. The sealed original `DESIGN.md` (SHA-256 `0519cfac352f569eeac045581ba1b01df1560ee96a1ae4e644616d8611e15da2`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# T19: who blows the whistle in a natural swarm, agents or humans? (design, sealed before any run; written 4 Oct 2026 from 20:15 UTC)

**Origin:** his question about how the DeepMind cheating swarm maps to the AI Village, and the correction that T13 to T13c measured agent-to-agent replies only. The raw chat has 173,493 agent and 9,992 human (`speaker_type` "user") messages.

## Claims
- The same 2,000 claim messages as T13b and T13c: the same universe, the same seed (the SHA-256 of T13's sealed result), the same draw.
- T13b's line numbers index the agent-only chat file. Here each one maps to the k-th agent message of the raw export, in file order. A spot check confirms the map: the first 50 sampled lines must match exactly on text.

## Replies
- Claim message at time t by agent S: the messages in the raw file from anyone other than S in (t, t + 30 min], the first 10, humans included.
- A reply is **engaged** if it names S (whole word, case-insensitive) or shares at least 2 keywords with the claim (T13's unchanged `keywords`).
- Each engaged reply is classed by T13's unchanged patterns, first match wins: challenge, verify, accept, other.

## Measures
**By responder type (human or agent), among engaged replies:**
- counts;
- shares of challenge, verify and accept, each with a Wilson 95% interval;
- Fisher exact tests, human against agent, for verify and for challenge.

**The over-representation ratio:** humans' share of all verify and challenge replies, divided by humans' share of all engaged replies.

**Per claim:** the share of claims with at least one human verify or challenge reply, and with at least one agent one.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Rules
- Counts only; no record text leaves the folder; exploratory.
- The classes are word patterns. Human chat includes casual viewer talk.
- The run starts at least 15 s after the FreeTSA stamp. Any change after the seal is a new, separately sealed version.
