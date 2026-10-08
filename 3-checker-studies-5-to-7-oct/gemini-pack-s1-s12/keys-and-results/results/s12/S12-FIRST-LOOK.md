# S12, forced yes-or-no on nine models: first look (coordinator; scorer written after the results seal, before reading them)

**Checks:** 972 rows for 972 distinct calls; 13 with no parsable verdict. Requests not matching the sealed spec, by check: {'messages': 0, 'model': 0, 'settings': 0, 'temperature/seed/provider': 0}. Verdicts re-parsed that differ from the runner's: 0.

Records: 27 logs missing their deciding evidence, 27 intact.

| Model | Guesses on missing, forced | allowed | Right on intact, forced | allowed | Right with the quote checked, forced | allowed | No verdict |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b | 19 | 9 | 24 | 26 | 24 | 25 | 2 |
| gemma-4-26b-a4b-it | 10 | 4 | 25 | 25 | 24 | 24 | 2 |
| deepseek-v4.1-flash | 26 | 2 | 27 | 27 | 27 | 27 | 0 |
| kimi-k3 | 27 | 4 | 27 | 26 | 27 | 26 | 2 |
| gpt-6.1-sol | 27 | 2 | 26 | 25 | 26 | 25 | 0 |
| gemini-3.8-flash | 20 | 3 | 27 | 26 | 27 | 26 | 7 |
| grok-4.7 | 27 | 2 | 27 | 26 | 27 | 26 | 0 |
| glm-5.3 | 20 | 5 | 27 | 27 | 27 | 27 | 0 |
| claude-opus-5.5 | 27 | 1 | 27 | 27 | 27 | 27 | 0 |

## Paired, forced to allowed (only forced / only allowed, exact McNemar p)

- qwen3.5-9b: guesses on missing 10 / 0, p = 0.00195; right on intact 0 / 2, p = 0.5
- gemma-4-26b-a4b-it: guesses on missing 6 / 0, p = 0.0312; right on intact 0 / 0, p = 1
- deepseek-v4.1-flash: guesses on missing 24 / 0, p = 1.19e-07; right on intact 0 / 0, p = 1
- kimi-k3: guesses on missing 23 / 0, p = 2.38e-07; right on intact 1 / 0, p = 1
- gpt-6.1-sol: guesses on missing 25 / 0, p = 5.96e-08; right on intact 1 / 0, p = 1
- gemini-3.8-flash: guesses on missing 17 / 0, p = 1.53e-05; right on intact 1 / 0, p = 1
- grok-4.7: guesses on missing 25 / 0, p = 5.96e-08; right on intact 1 / 0, p = 1
- glm-5.3: guesses on missing 15 / 0, p = 6.1e-05; right on intact 0 / 0, p = 1
- claude-opus-5.5: guesses on missing 26 / 0, p = 2.98e-08; right on intact 0 / 0, p = 1
- The seven newer models together: guesses on missing 155 / 0, p = 4.38e-47

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
