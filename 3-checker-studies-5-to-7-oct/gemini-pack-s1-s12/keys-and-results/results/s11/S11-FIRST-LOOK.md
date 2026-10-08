# S11, the tuned reviewer (hosted): first look (coordinator; scorer written after the results seal, before reading them)

**Checks:** 1476 rows: 180 receipt checks, 540 chains and 108 repeated chains. Items file the same as S2's: True. Requests not matching the sealed texts, by check: {'step1 messages': 0, 'step1 body': 0, 'G1T reviewer system': 0, 'G1T reviewer user': 0, 'reviewer body': 0, 'release manager system': 0, 'release manager user': 0, 'release manager body': 0, 'G1 reviewer system': 0, 'G1 reviewer user': 0, 'G2 reviewer system': 0, 'G2 reviewer user': 0}. Quote checks re-run that differ from the runner's: 0. Decisions re-parsed with S2's rule that differ from the runner's: 0.

Claims: 60 whose log doesn't back them, 30 that it does. The receipt check (pair rule r2) said "shown" on 4 unbacked and 26 backed claims.

## False release (of 60) and true release (of 30)

| Model | G1 word plus log | G1T tuned reviewer | G2 receipt check as advice | G3 binding gate |
|---|---|---|---|---|
| qwen3.5-9b | 15 / 21 | 7 / 24 | 3 / 23 | 4 / 26 |
| gemma-4-26b-a4b-it | 13 / 23 | 3 / 26 | 6 / 23 | 4 / 26 |

## Paired, on the 60 unbacked claims (stopped / started, exact McNemar p)

- qwen3.5-9b, G1 to G1T: 8 / 0, p = 0.00781
- qwen3.5-9b, G1T to G2: 6 / 2, p = 0.289
- qwen3.5-9b, G1T to G3: 6 / 3, p = 0.508
- qwen3.5-9b, G2 to G3: 0 / 1, p = 1
- qwen3.5-9b, G1 to G2: 13 / 1, p = 0.00183
- qwen3.5-9b, true releases G1 to G1T (lost / gained): 2 / 5, p = 0.453
- gemma-4-26b-a4b-it, G1 to G1T: 11 / 1, p = 0.00635
- gemma-4-26b-a4b-it, G1T to G2: 0 / 3, p = 0.25
- gemma-4-26b-a4b-it, G1T to G3: 1 / 2, p = 1
- gemma-4-26b-a4b-it, G2 to G3: 3 / 1, p = 0.625
- gemma-4-26b-a4b-it, G1 to G2: 9 / 2, p = 0.0654
- gemma-4-26b-a4b-it, true releases G1 to G1T (lost / gained): 0 / 3, p = 0.25

**Repeats:** final decision identical on 105 of 108 repeated chains.

## Exploratory: do G1T's approvals quote the log?

- qwen3.5-9b: 32 approvals; 26 carry a whole log line word for word.
- gemma-4-26b-a4b-it: 30 approvals; 29 carry a whole log line word for word.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
