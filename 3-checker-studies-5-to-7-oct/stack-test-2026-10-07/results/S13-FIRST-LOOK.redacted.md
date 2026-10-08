> Published copy. The sealed original `S13-FIRST-LOOK.md` (SHA-256 `9a35e126449a69b3aeb47780d822ac3226eda5f92783d80cfd05051679be477a`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# S13, the stack test: first look (coordinator; scorer written after the results seal and sealed before it was run)

**Checks, sol:** 108 rows, 108 distinct record-and-framing calls of 108, 0 duplicated; prompts not matching the sealed construction: 0; verdicts re-parsed that differ from the runner's: 0.
**Checks, gemini:** 108 rows, 108 distinct record-and-framing calls of 108, 0 duplicated; prompts not matching the sealed construction: 0; verdicts re-parsed that differ from the runner's: 0.
**S12 API rows found:** sol 108, gemini 108 (108 expected each).

Records: 27 logs missing their deciding evidence, 27 intact (key sealed 6 Oct 2026).

| Stack | Guesses on missing, forced | allowed | Right on intact, forced | allowed | Right with the quote checked, forced | allowed | No verdict |
|---|---|---|---|---|---|---|---|
| sol | 9 of 27 | 0 of 27 | 22 of 27 | 21 of 27 | 22 of 27 | 21 of 27 | 28 of 108 |
| gemini | 22 of 27 | 2 of 27 | 22 of 27 | 22 of 27 | 22 of 27 | 22 of 27 | 15 of 108 |

For comparison, the same models through the plain API in S12 (computed here from S12's sealed calls):

| S12 API | Guesses on missing, forced | allowed | Right on intact, forced | allowed | No verdict |
|---|---|---|---|---|---|
| openai/gpt-6.1-sol | 27 of 27 | 2 of 27 | 26 of 27 | 25 of 27 | 0 of 108 |
| google/gemini-3.8-flash | 20 of 27 | 3 of 27 | 27 of 27 | 26 of 27 | 7 of 108 |

## Calls with no verdict

- sol: allowed, intact, no_verdict: 5; forced, intact, no_verdict: 5; forced, missing, no_verdict: 18
- gemini: allowed, intact, no_verdict: 4; allowed, missing, no_verdict: 1; forced, intact, no_verdict: 5; forced, missing, no_verdict: 5

## Paired, forced to allowed (only forced / only allowed, exact McNemar p)

- sol: guesses on missing 9 / 0, p = 0.00391; right on intact 1 / 0, p = 1
- gemini: guesses on missing 20 / 0, p = 1.91e-06; right on intact 1 / 1, p = 1

## Against the same model's S12 API run (108 record-and-framing pairs each)

- sol: same verdict on 73 of 108
- gemini: same verdict on 84 of 108
- Sol, forced, evidence-missing records: guessed in the stack only 0, in the API only 18, exact McNemar p = 7.63e-06

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
