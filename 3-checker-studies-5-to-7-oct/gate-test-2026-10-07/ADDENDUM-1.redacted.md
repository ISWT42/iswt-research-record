> Published copy. The sealed original `ADDENDUM-1.md` (SHA-256 `3bfba9f7603c2d8a2b6c820d7c3f57c2736a4de8b39bc5bba2d0a26755496d8e`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: forecast or prediction lines removed.

# The gate test, dated addendum 1: a prior result the sealed design left out

**Written:** 7 Oct 2026, from 02:18 UTC (clock), by the coordinating session (Claude). Nothing sealed is changed. This addendum records a gap.

## The gap
- The sealed design (`DESIGN.md`, FreeTSA 01:58:13 GMT) cites S11 (hosted) and the chain test (local). It leaves out **S11L**, which ran on 6 Oct with the same two local models and the same prompts, on S2's claims.
- I did not have S11L in view when I wrote the design and the forecasts. I found it at 02:17 UTC, while reading `Private/ClaudeHandoff/findings/FINDINGS-2026-10-06.md` for another reason. That file's F20 records it.

## S11L (F20)
Design sealed at 14:45:36 GMT; results sealed at 19:15:17 GMT on 6 Oct. False releases of 60 (true releases of 30):

| Model | G1 | G2 | G1T, told the rule | G3, binding gate |
|---|---|---|---|---|
| Qwen3-4B | 20 (22) | 14 (25) | 9 (20) | 4 (21) |
| Gemma-4-E4B | 17 (25) | 16 (25) | 6 (26) | 4 (21) |

- G1 to G1T: 12 stopped and 1 started, for both models (p = 0.0034 each).
- G1T to G3: Qwen 6 / 1 (p = 0.13); Gemma 5 / 3 (p = 0.73). Not significant.

## What changes in how the gate test is read
- **It is a replication.** The gate test repeats S11L on fresh claims written by a different author. It is not the first test of this question on these models.
- **The write-up adds S11L.** The results write-up will show S11L's counts beside the gate test's, as the closest comparison: same models, same prompts, different claims. The sealed scorer prints S11 and the chain test only, so S11L's column is added by hand and marked as added.
