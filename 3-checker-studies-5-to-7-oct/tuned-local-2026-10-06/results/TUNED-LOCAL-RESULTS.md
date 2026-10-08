# S11L, the tuned reviewer on this PC: results (scored after the results seal)

Items: 90 (30 backed, 60 not). G1T chains written: 180 of 180. Control chains: 36 of 36.
Chains with a missing decision (reviewer or release manager): 2. Backend errors: 0.

| Model | Arm | False release of 60 | True release of 30 |
|---|---|---|---|
| qwen | G0 (sealed) | 59 | 27 |
| qwen | G1 (sealed) | 20 | 22 |
| qwen | G2 (sealed) | 14 | 25 |
| qwen | G1T (new, tuned) | 9 | 20 |
| qwen | G3 (binding gate) | 4 | 21 |
| gemma | G0 (sealed) | 58 | 26 |
| gemma | G1 (sealed) | 17 | 25 |
| gemma | G2 (sealed) | 16 | 25 |
| gemma | G1T (new, tuned) | 6 | 26 |
| gemma | G3 (binding gate) | 4 | 21 |

## Paired, on the 60 unbacked claims (stopped / started, exact McNemar p)

- qwen, G1 to G1T: 12 / 1, p = 0.00342
- qwen, G2 to G1T: 8 / 3, p = 0.227
- qwen, G1T to G3: 6 / 1, p = 0.125
- gemma, G1 to G1T: 12 / 1, p = 0.00342
- gemma, G2 to G1T: 11 / 1, p = 0.00635
- gemma, G1T to G3: 5 / 3, p = 0.727

## The control: plain G1 re-run on 18 items per model

- Final decisions matching the sealed G1: 36 of 36. Items: C002 C005 C011 C014 C015 C026 C030 C031 C033 C037 C060 C064 C066 C068 C070 C072 C081 C087.

## Exploratory: do G1T's approvals quote the log?

- qwen: 28 approvals; 14 carry a whole log line word for word.
- gemma: 32 approvals; 31 carry a whole log line word for word.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
