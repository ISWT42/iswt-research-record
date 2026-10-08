# S13, exploratory re-parse with S12's verdict rule (after the sealed scorer ran; not the scored result)

Calls whose verdict differs from the runner's rule: gemini found a verdict: 15; sol found a verdict: 15

| | Guesses on missing, forced | allowed | Right on intact, forced | allowed | No verdict |
|---|---|---|---|---|---|
| sol stack | 14 of 27 | 0 of 27 | 27 of 27 | 26 of 27 | 13 of 108 |
| gemini stack | 27 of 27 | 3 of 27 | 26 of 27 | 26 of 27 | 0 of 108 |
| sol API (S12) | 27 of 27 | 2 of 27 | 26 of 27 | 25 of 27 | 0 of 108 |
| gemini API (S12) | 20 of 27 | 3 of 27 | 27 of 27 | 26 of 27 | 7 of 108 |

No-verdict calls left in the stacks, by framing and kind of log:
- sol: forced, missing: 13
- gemini: none

Paired tests:
- sol stack, forced to allowed, guesses on missing: only forced 14, only allowed 0, p = 0.000122
- sol, forced, missing, stack against API: guessed only in the stack 0, only in the API 13, p = 0.000244
- sol: same verdict as its S12 API run on 88 of 108
- gemini stack, forced to allowed, guesses on missing: only forced 24, only allowed 0, p = 1.19e-07
- gemini, forced, missing, stack against API: guessed only in the stack 7, only in the API 0, p = 0.0156
- gemini: same verdict as its S12 API run on 96 of 108
