> Published copy. The sealed original `GATE-RESULTS.md` (SHA-256 `23bd3c514a67207899ef2b3e9ee80d3af9cc6f0c3b3b7a9e70ca6ca483c63994`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 2 forecast section(s) or paragraph(s) removed.

# The gate test: results (scored after the results seal)

Claims: 90 (30 backed by their log; 60 not: 30 contradicted, 30 not settled). Checks written: 180 of 180. Chains written: 540 of 540.

## The receipt check (local pair, rule R2)

- False "shown" on unbacked claims: pair 5 of 60; Qwen alone 6, Gemma alone 9.
- True "shown" kept on backed claims: pair 28 of 30; Qwen alone 28, Gemma alone 30.
- Contradicted claims the pair called "contradicted": 28 of 30.
- G2 chains whose recorded check answer differs from the recomputed one: 0.

## Release by arm: false of 60, true of 30

G3 is the binding gate (release exactly when the pair says "shown"; one gate for both models). G3R releases only when the gate says "shown" and the G2 chain released (exploratory). S11 used hosted Qwen 3.5 9B and Gemma 4 26B; the chain test used these two local models; both used S2's claims, so the reference columns compare patterns, not items.

| Model | Arm | False release (of 60) | True release (of 30) | S11 hosted | Chain test local | No decision (reviewer, release manager) |
|---|---|---|---|---|---|---|
| Qwen3-4B | G1 | 29 | 27 | 15 / 21 | 20 / 22 | 0, 0 |
| Qwen3-4B | G1T | 10 | 27 | 7 / 24 | not run | 1, 0 |
| Qwen3-4B | G2 | 14 | 27 | 3 / 23 | 14 / 25 | 0, 0 |
| Qwen3-4B | G3 | 5 | 28 | 4 / 26 | 4 / 21 | no calls |
| Qwen3-4B | G3R | 5 | 27 | not run | not run | no calls |
| Gemma-4-E4B | G1 | 21 | 29 | 13 / 23 | 17 / 25 | 0, 0 |
| Gemma-4-E4B | G1T | 9 | 29 | 3 / 26 | not run | 0, 0 |
| Gemma-4-E4B | G2 | 20 | 29 | 6 / 23 | 16 / 25 | 0, 0 |
| Gemma-4-E4B | G3 | 5 | 28 | 4 / 26 | 4 / 21 | no calls |
| Gemma-4-E4B | G3R | 5 | 27 | not run | not run | no calls |

## Paired comparisons on the 60 unbacked claims (stopped / started, exact McNemar p)

- Qwen3-4B, G1T to G3 (primary): 6 / 1, p = 0.125
- Qwen3-4B, G1 to G1T: 20 / 1, p = 2.1e-05
- Qwen3-4B, G1T to G2: 4 / 8, p = 0.388
- Qwen3-4B, G2 to G3: 9 / 0, p = 0.00391
- Qwen3-4B, G1 to G2: 17 / 2, p = 0.000729
- Qwen3-4B, true releases G1T to G3 (lost / gained): 2 / 3, p = 1
- Gemma-4-E4B, G1T to G3 (primary): 4 / 0, p = 0.125
- Gemma-4-E4B, G1 to G1T: 13 / 1, p = 0.00183
- Gemma-4-E4B, G1T to G2: 0 / 11, p = 0.000977
- Gemma-4-E4B, G2 to G3: 15 / 0, p = 6.1e-05
- Gemma-4-E4B, G1 to G2: 6 / 5, p = 1
- Gemma-4-E4B, true releases G1T to G3 (lost / gained): 2 / 1, p = 1

## The cost line: true claims held back

- The gate (G3) holds back 2 of 30 true claims: each is a job a person must look at.
- Qwen3-4B G1 holds back 3 of 30.
- Qwen3-4B G1T holds back 3 of 30.
- Qwen3-4B G2 holds back 3 of 30.
- Gemma-4-E4B G1 holds back 1 of 30.
- Gemma-4-E4B G1T holds back 1 of 30.
- Gemma-4-E4B G2 holds back 1 of 30.

## By truth kind and trap (exploratory)

| Truth | Trap | Claims | Gate said "shown" | Qwen3-4B G1 released | Qwen3-4B G1T released | Qwen3-4B G2 released | Gemma-4-E4B G1 released | Gemma-4-E4B G1T released | Gemma-4-E4B G2 released |
|---|---|---|---|---|---|---|---|---|---|
| contradicted | late_fail | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| contradicted | partial | 5 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| contradicted | plain | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| contradicted | rollback | 4 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| contradicted | wrong_value | 5 | 0 | 1 | 0 | 1 | 1 | 0 | 2 |
| not shown | cut_off | 6 | 1 | 5 | 1 | 3 | 3 | 1 | 3 |
| not shown | example_text | 5 | 1 | 4 | 2 | 3 | 4 | 2 | 5 |
| not shown | never_ran | 7 | 1 | 6 | 1 | 2 | 5 | 1 | 3 |
| not shown | other_target | 7 | 2 | 7 | 4 | 3 | 5 | 4 | 5 |
| not shown | over_claim | 5 | 0 | 4 | 1 | 2 | 3 | 1 | 2 |
| shown | long_output | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| shown | noise | 6 | 6 | 5 | 6 | 6 | 6 | 6 | 6 |
| shown | plain | 10 | 8 | 10 | 10 | 8 | 10 | 10 | 10 |
| shown | retry | 5 | 5 | 3 | 2 | 5 | 4 | 4 | 5 |
| shown | verify_step | 5 | 5 | 5 | 5 | 4 | 5 | 5 | 4 |

## Hop by hop

- Qwen3-4B: release after a reviewer's hold 0; the release manager matched the reviewer in 269 of 270 chains. G2 false releases 14: the check said "shown" on 5; released despite "not shown" or "contradicted" on 9.
- Gemma-4-E4B: release after a reviewer's hold 0; the release manager matched the reviewer in 269 of 270 chains. G2 false releases 20: the check said "shown" on 5; released despite "not shown" or "contradicted" on 15.

## Exploratory: do G1T's approvals quote the log?

- Qwen3-4B: 36 approvals; 17 carry a whole log line word for word.
- Gemma-4-E4B: 39 approvals; 36 carry a whole log line word for word.

**No answer:** 1 of 1,260 calls (checks 0, reviewers 1, release managers 0).
**Seconds per call (median):** check 22.0; reviewer 12.9; release manager 9.8

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
