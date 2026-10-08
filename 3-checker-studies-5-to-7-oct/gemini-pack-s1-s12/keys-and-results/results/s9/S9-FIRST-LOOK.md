# S9, the wobble test: first look (coordinator; scorer sealed before the results were read)

**Checks:** 3360 rows for 3360 distinct calls (duplicates 0); 0 without an answer. Requests not matching the sealed spec, by check: {'messages': 0, 'model': 0, 'temperature': 0, 'seed': 0, 'max_tokens': 0, 'reasoning': 0, 'provider': 0}. Quote checks re-run with receipt_pair b7dfbad that differ from the runner's: 0. order.json: matches Addendum 6 exactly. Reported cost US$0.4015.

Records: 240 whose log doesn't back the claim, 40 that do.

## False "shown" (of 240) and true "shown" kept (of 40)

| Model | W0 false | all five false | majority false | W0 kept | all five kept | majority kept |
|---|---|---|---|---|---|---|
| qwen3.5-9b | 39 | 13 | 37 | 35 | 28 | 35 |
| gemma-4-26b-a4b-it | 40 | 30 | 40 | 38 | 37 | 38 |
| both at W0 (r2) | 32 | | | 34 | | |

## Paired comparisons (stopped / started, exact McNemar p)

- qwen3.5-9b: W0 to all five, false "shown" 27 / 1, p = 2.16e-07; true "shown" lost / gained 8 / 1, p = 0.0391. W0 to majority, false "shown" 6 / 4, p = 0.754. All five to r2, false "shown" 1 / 20, p = 2.1e-05.
- gemma-4-26b-a4b-it: W0 to all five, false "shown" 10 / 0, p = 0.00195; true "shown" lost / gained 1 / 0, p = 1. W0 to majority, false "shown" 4 / 4, p = 1. All five to r2, false "shown" 4 / 6, p = 0.754.

## The wobble: records whose five samples split

- qwen3.5-9b: split on 47 of 83 records where W0 was wrong, and 72 of 197 where it was right (exact p = 0.00232). Secondary, two-way: 27 of 44 against 92 of 236.
- gemma-4-26b-a4b-it: split on 19 of 66 records where W0 was wrong, and 23 of 214 where it was right (exact p = 0.000709). Secondary, two-way: 10 of 42 against 32 of 238.
- Pooled: split on 66 of 149 where W0 was wrong, and 95 of 411 where it was right (exact p = 2.64e-06).

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
