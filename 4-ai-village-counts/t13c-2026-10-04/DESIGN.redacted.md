> Published copy. The sealed original `DESIGN.md` (SHA-256 `ce34b445a6a4cdfb3c86ca35829e09a3b37be5ade16da91188a58c15bd5387d3`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# T13c: do newer, more capable models check claims more and accept them less? (design, sealed before any run; written from 16:13 UTC on 4 Oct 2026)

**His hypothesis, 16:12 UTC:** "I do assume that there would be multi distribuition based on agent intelligence but who knows"

**Proxy for "intelligence":** each model's release date, split into thirds (oldest, middle, newest). The table is the sealed plan's own, `Data\results\p3_dates.json`: 44 agents, each with a release date and a third. Release date is a rough proxy for capability; that is a stated limit.

## Data
- The same 2,000 claim messages as T13b, drawn with the same seed.
- For each claim message (time t, speaker S): the replies from anyone other than S in (t, t + 30 min], up to the first 10, as in T13.
- Engaged replies are defined as in T13. Each engaged reply is classed with T13's unchanged patterns: challenge, verify, accept, other.
- Each engaged reply's responder is looked up in p3_dates.json. Responders not in the table, such as humans, are left out and counted.

## Measures
**By responder third, among engaged replies:**
- the shares of accept, verify and challenge, each with a Wilson 95% interval;
- for verify and for accept, a two-sided Fisher exact test, newest third against oldest third.

**The 10 responders with the most engaged replies:** each one's shares, with its third.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Rules
- Counts only; no record text.
- Exploratory.
- Publication is his call; no scorecards in public.
- The run starts at least 15 s after the FreeTSA stamp.
