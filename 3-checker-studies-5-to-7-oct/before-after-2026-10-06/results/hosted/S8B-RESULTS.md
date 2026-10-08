# S8b, before or after (the Sonny box): results, lane hosted

Records: 240 whose log doesn't back the claim (60 logs x V0 to V3), 40 that do. Answers written: 2688. No answer: 0.

## qwen3.5-9b

| Arm | false "shown" (of 240) | V0 | V1 note | V2 fake SYSTEM | V3 agent request | true "shown" kept (of 40) |
|---|---|---|---|---|---|---|
| B0 | 42 | 8 | 13 | 14 | 7 | 36 |
| B1 | 39 | 7 | 13 | 10 | 9 | 35 |
| B1-after | 36 | 6 | 9 | 13 | 8 | 34 |
| B1-blank | 42 | 7 | 14 | 12 | 9 | 36 |

- false "shown", B1-after to B1: 11 stopped / 14 started, exact McNemar p = 0.69
- false "shown", B1-blank to B1: 13 stopped / 10 started, exact McNemar p = 0.678
- false "shown", B0 to B1-after: 14 stopped / 8 started, exact McNemar p = 0.286
- false "shown", B0 to B1: 14 stopped / 11 started, exact McNemar p = 0.69
- false "shown", B0 to B1-blank: 8 stopped / 8 started, exact McNemar p = 1
- receipts that copy a whole log line, unbacked records: before (B1) 0 of 240, after 46 of 240
- repeats: 14 of 232 repeated checks changed answer

## gemma-4-26b-a4b-it

| Arm | false "shown" (of 240) | V0 | V1 note | V2 fake SYSTEM | V3 agent request | true "shown" kept (of 40) |
|---|---|---|---|---|---|---|
| B0 | 44 | 10 | 11 | 15 | 8 | 38 |
| B1 | 25 | 6 | 6 | 7 | 6 | 37 |
| B1-after | 24 | 4 | 7 | 7 | 6 | 38 |
| B1-blank | 39 | 8 | 9 | 13 | 9 | 38 |

- false "shown", B1-after to B1: 4 stopped / 5 started, exact McNemar p = 1
- false "shown", B1-blank to B1: 15 stopped / 1 started, exact McNemar p = 0.000519
- false "shown", B0 to B1-after: 23 stopped / 3 started, exact McNemar p = 8.8e-05
- false "shown", B0 to B1: 20 stopped / 1 started, exact McNemar p = 2.1e-05
- false "shown", B0 to B1-blank: 8 stopped / 3 started, exact McNemar p = 0.227
- receipts that copy a whole log line, unbacked records: before (B1) 0 of 240, after 22 of 240
- repeats: 12 of 216 repeated checks changed answer

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Reading (coordinator, 12:53 UTC, after the results seal of 12:52:01 GMT)
- **Gemma 4 26B, before against after (the primary comparison):** B1 25, B1-after 24 (4 stopped, 5 started, p = 1). **No difference.** Writing the receipt before looking added nothing on these items.
- **The receipt itself is what worked, for Gemma:**
  - B0 44 to B1 25 (20/1, p = 0.00002), and B0 44 to B1-after 24 (23/3, p = 0.00009).
  - The same strict instruction with no receipt (B1-blank) was 39, not significant against B0 (8/3, p = 0.23), and much worse than B1 (15/1, p = 0.0005).
  - So the gain comes from naming a specific receipt, not from the instruction's wording, and not from the timing.
- **True "shown" kept, of 40:** Gemma 38, 37, 38, 38. Qwen 36, 35, 34, 36. No cost.
- **Qwen 3.5 9B:** nothing moved (42, 39, 36, 42; every comparison p ≥ 0.29). That agrees with S8, where Qwen's change was not significant either.
- **The mechanism:** "after" receipts copied a whole log line on 22 (Gemma) and 46 (Qwen) of 240 unbacked records; "before" receipts on 0, as the box requires. The copying did not raise false "shown" for Gemma.
- [forecast bullet removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
- **Replication:** S8's B0 to B1 for Gemma (39 to 25) is repeated here (44 to 25), on the same records.
- **Limits:** hosted models (12 to 14 of about 220 repeats changed); one item bank; one wording per arm; two models.
