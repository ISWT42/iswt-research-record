**Local pair (A Qwen3-4B, B Gemma-4-E4B), ids 161 to 300** (140 items; truth {'contradicted': 47, 'not shown': 47, 'shown': 46}; R2 says "shown" on 39: {'contradicted': 1, 'not shown': 5, 'shown': 33})

| Rule | False "shown" (of items whose truth is not shown) | True "shown" kept (of items whose truth is shown) | R2 "shown" removed | of those false / true |
|---|---|---|---|---|
| R2 (shown needs both) | 6/94 | 33/46 | - | - |
| SAME-LINE | 6/94 | 32/46 | 1 | 0 / 1 |
| OUTCOME-MARKER | 3/94 | 5/46 | 31 | 3 / 28 |
| **NON-SETTLING-2** (own; chosen primary) | 0/94 | 33/46 | 6 | 6 / 0 |
| NON-SETTLING (version 1, withdrawn) (exploratory) | 2/94 | 33/46 | 4 | 4 / 0 |
| SAME-LINE-STRICT (exploratory) | 6/94 | 28/46 | 5 | 0 / 5 |
| SAME-LINE-CONTAINED (exploratory) | 6/94 | 32/46 | 1 | 0 / 1 |
| OUTCOME-MARKER-BOTH (exploratory) | 3/94 | 5/46 | 31 | 3 / 28 |
| OUTCOME-MARKER-LINE (exploratory) | 3/94 | 5/46 | 31 | 3 / 28 |
| SAME-LINE+OUTCOME-MARKER (exploratory) | 3/94 | 4/46 | 32 | 3 / 29 |

**Hosted pair (F-Q qwen3.5-9b, F-G gemma-4-26b), ids 161 to 300** (140 items; truth {'contradicted': 47, 'not shown': 47, 'shown': 46}; R2 says "shown" on 39: {'contradicted': 2, 'not shown': 5, 'shown': 32})

| Rule | False "shown" (of items whose truth is not shown) | True "shown" kept (of items whose truth is shown) | R2 "shown" removed | of those false / true |
|---|---|---|---|---|
| R2 (shown needs both) | 7/94 | 32/46 | - | - |
| SAME-LINE | 4/94 | 28/46 | 7 | 3 / 4 |
| OUTCOME-MARKER | 6/94 | 9/46 | 24 | 1 / 23 |
| **NON-SETTLING-2** (own; chosen primary) | 3/94 | 31/46 | 5 | 4 / 1 |
| NON-SETTLING (version 1, withdrawn) (exploratory) | 4/94 | 31/46 | 4 | 3 / 1 |
| SAME-LINE-STRICT (exploratory) | 4/94 | 28/46 | 7 | 3 / 4 |
| SAME-LINE-CONTAINED (exploratory) | 4/94 | 28/46 | 7 | 3 / 4 |
| OUTCOME-MARKER-BOTH (exploratory) | 3/94 | 7/46 | 29 | 4 / 25 |
| OUTCOME-MARKER-LINE (exploratory) | 6/94 | 9/46 | 24 | 1 / 23 |
| SAME-LINE+OUTCOME-MARKER (exploratory) | 3/94 | 7/46 | 29 | 4 / 25 |

**Local pair, pooled ids 001 to 300 (run 1 for 001 to 160, run 2 for 161 to 300): the set the primary was chosen on** (300 items; truth {'contradicted': 100, 'not shown': 100, 'shown': 100}; R2 says "shown" on 107: {'contradicted': 5, 'not shown': 22, 'shown': 80})

| Rule | False "shown" (of items whose truth is not shown) | True "shown" kept (of items whose truth is shown) | R2 "shown" removed | of those false / true |
|---|---|---|---|---|
| R2 (shown needs both) | 27/200 | 80/100 | - | - |
| SAME-LINE | 23/200 | 72/100 | 12 | 4 / 8 |
| OUTCOME-MARKER | 18/200 | 24/100 | 65 | 9 / 56 |
| **NON-SETTLING-2** (own; chosen primary) | 6/200 | 75/100 | 26 | 21 / 5 |
| NON-SETTLING (version 1, withdrawn) (exploratory) | 22/200 | 80/100 | 5 | 5 / 0 |
| SAME-LINE-STRICT (exploratory) | 21/200 | 66/100 | 20 | 6 / 14 |
| SAME-LINE-CONTAINED (exploratory) | 23/200 | 72/100 | 12 | 4 / 8 |
| OUTCOME-MARKER-BOTH (exploratory) | 15/200 | 22/100 | 70 | 12 / 58 |
| OUTCOME-MARKER-LINE (exploratory) | 18/200 | 24/100 | 65 | 9 / 56 |
| SAME-LINE+OUTCOME-MARKER (exploratory) | 14/200 | 18/100 | 75 | 13 / 62 |

**Local pair, run 1 only, ids 001 to 160** (160 items; truth {'contradicted': 53, 'not shown': 53, 'shown': 54}; R2 says "shown" on 68: {'contradicted': 4, 'not shown': 17, 'shown': 47})

| Rule | False "shown" (of items whose truth is not shown) | True "shown" kept (of items whose truth is shown) | R2 "shown" removed | of those false / true |
|---|---|---|---|---|
| R2 (shown needs both) | 21/106 | 47/54 | - | - |
| SAME-LINE | 17/106 | 40/54 | 11 | 4 / 7 |
| OUTCOME-MARKER | 15/106 | 19/54 | 34 | 6 / 28 |
| **NON-SETTLING-2** (own; chosen primary) | 6/106 | 42/54 | 20 | 15 / 5 |
| NON-SETTLING (version 1, withdrawn) (exploratory) | 20/106 | 47/54 | 1 | 1 / 0 |
| SAME-LINE-STRICT (exploratory) | 15/106 | 38/54 | 15 | 6 / 9 |
| SAME-LINE-CONTAINED (exploratory) | 17/106 | 40/54 | 11 | 4 / 7 |
| OUTCOME-MARKER-BOTH (exploratory) | 12/106 | 17/54 | 39 | 9 / 30 |
| OUTCOME-MARKER-LINE (exploratory) | 15/106 | 19/54 | 34 | 6 / 28 |
| SAME-LINE+OUTCOME-MARKER (exploratory) | 11/106 | 14/54 | 43 | 10 / 33 |

**Local pair, ids 201 to 300** (100 items; truth {'contradicted': 34, 'not shown': 34, 'shown': 32}; R2 says "shown" on 25: {'contradicted': 1, 'not shown': 1, 'shown': 23})

| Rule | False "shown" (of items whose truth is not shown) | True "shown" kept (of items whose truth is shown) | R2 "shown" removed | of those false / true |
|---|---|---|---|---|
| R2 (shown needs both) | 2/68 | 23/32 | - | - |
| SAME-LINE | 2/68 | 22/32 | 1 | 0 / 1 |
| OUTCOME-MARKER | 0/68 | 4/32 | 21 | 2 / 19 |
| **NON-SETTLING-2** (own; chosen primary) | 0/68 | 23/32 | 2 | 2 / 0 |
| NON-SETTLING (version 1, withdrawn) (exploratory) | 1/68 | 23/32 | 1 | 1 / 0 |
| SAME-LINE-STRICT (exploratory) | 2/68 | 21/32 | 2 | 0 / 2 |
| SAME-LINE-CONTAINED (exploratory) | 2/68 | 22/32 | 1 | 0 / 1 |
| OUTCOME-MARKER-BOTH (exploratory) | 0/68 | 4/32 | 21 | 2 / 19 |
| OUTCOME-MARKER-LINE (exploratory) | 0/68 | 4/32 | 21 | 2 / 19 |
| SAME-LINE+OUTCOME-MARKER (exploratory) | 0/68 | 3/32 | 22 | 2 / 20 |

**Hosted pair, ids 201 to 300** (100 items; truth {'contradicted': 34, 'not shown': 34, 'shown': 32}; R2 says "shown" on 28: {'contradicted': 2, 'not shown': 3, 'shown': 23})

| Rule | False "shown" (of items whose truth is not shown) | True "shown" kept (of items whose truth is shown) | R2 "shown" removed | of those false / true |
|---|---|---|---|---|
| R2 (shown needs both) | 5/68 | 23/32 | - | - |
| SAME-LINE | 2/68 | 21/32 | 5 | 3 / 2 |
| OUTCOME-MARKER | 4/68 | 7/32 | 17 | 1 / 16 |
| **NON-SETTLING-2** (own; chosen primary) | 3/68 | 23/32 | 2 | 2 / 0 |
| NON-SETTLING (version 1, withdrawn) (exploratory) | 4/68 | 23/32 | 1 | 1 / 0 |
| SAME-LINE-STRICT (exploratory) | 2/68 | 21/32 | 5 | 3 / 2 |
| SAME-LINE-CONTAINED (exploratory) | 2/68 | 21/32 | 5 | 3 / 2 |
| OUTCOME-MARKER-BOTH (exploratory) | 1/68 | 6/32 | 21 | 4 / 17 |
| OUTCOME-MARKER-LINE (exploratory) | 4/68 | 7/32 | 17 | 1 / 16 |
| SAME-LINE+OUTCOME-MARKER (exploratory) | 1/68 | 6/32 | 21 | 4 / 17 |

**Where R2's false "shown" sit and which rule removes them: Local pair (A Qwen3-4B, B Gemma-4-E4B), ids 161 to 300**

| id | truth | trap | SAME-LINE | OUTCOME-MARKER | NON-SETTLING-2 |
|---|---|---|---|---|---|
| 163 | not shown | intermediate_signal | - | - | removed |
| 171 | not shown | relayed_claim | - | removed | removed |
| 185 | not shown | intermediate_signal | - | - | removed |
| 199 | not shown | other_environment | - | - | removed |
| 229 | contradicted | other_environment | - | removed | removed |
| 277 | not shown | relayed_claim | - | removed | removed |

- True "shown" removed by SAME-LINE: 1 (ids 236; traps ['retry'])
- True "shown" removed by OUTCOME-MARKER: 28 (ids 161, 167, 168, 172, 175, 179, 181, 188, 195, 202, 204, 211, 216, 220, 222, 230, 232, 237, 254, 263, 267, 273, 276, 278, 281, 289, 292, 297; traps ['example_text', 'intermediate_signal', 'narration', 'none', 'other_environment', 'relayed_claim', 'retry', 'tool_failed_to_run', 'truncated'])
- True "shown" removed by NON-SETTLING-2: 0

**Where R2's false "shown" sit and which rule removes them: Hosted pair (F-Q qwen3.5-9b, F-G gemma-4-26b), ids 161 to 300**

| id | truth | trap | SAME-LINE | OUTCOME-MARKER | NON-SETTLING-2 |
|---|---|---|---|---|---|
| 163 | not shown | intermediate_signal | - | - | removed |
| 185 | not shown | intermediate_signal | - | - | removed |
| 209 | not shown | example_text | - | removed | - |
| 238 | contradicted | other_environment | - | - | removed |
| 268 | contradicted | intermediate_signal | removed | - | - |
| 277 | not shown | relayed_claim | removed | - | removed |
| 294 | not shown | relayed_claim | removed | - | - |

- True "shown" removed by SAME-LINE: 4 (ids 179, 183, 254, 276; traps ['relayed_claim', 'retry'])
- True "shown" removed by OUTCOME-MARKER: 23 (ids 161, 167, 172, 175, 179, 181, 195, 204, 211, 220, 222, 227, 230, 232, 237, 241, 263, 267, 273, 276, 281, 289, 292; traps ['example_text', 'intermediate_signal', 'narration', 'none', 'other_environment', 'relayed_claim', 'retry', 'tool_failed_to_run', 'truncated'])
- True "shown" removed by NON-SETTLING-2: 1 (ids 179; traps ['relayed_claim'])

**Pooled local set: false "shown" by truth and what the primary removes**
- R2 false "shown" 27/200; R2's 107 "shown" answers by truth: {'contradicted': 5, 'not shown': 22, 'shown': 80}.
- SAME-LINE: false removed by truth {'contradicted': 1, 'not shown': 3}; by reason {'different_lines': 4, 'different_turn': 8, 'same_line': 95}
- OUTCOME-MARKER: false removed by truth {'contradicted': 2, 'not shown': 7}; by reason {'marker_in_a_quote': 42, 'no_marker_in_either_quote': 65}
- NON-SETTLING-2: false removed by truth {'contradicted': 5, 'not shown': 16}; by reason {'no_unclaimed_non_settling_word': 81, 'non_settling:acknowledged_not_done': 3, 'non_settling:other_environment': 21, 'non_settling:secondhand_report': 2}

**Selection (computed by dev_eval2.py)**
- Primary: NON-SETTLING-2. Rule applied: step 2: eligible candidate with the most false 'shown' removed (ties: fewer true removed, more removed on the hosted pair, simpler rule). Own-rule gate: {'NON-SETTLING-2': {'local_conditions_met': True, 'hosted_validation_met': True, 'admitted': True, 'hosted': {'r2_false_shown': 7, 'r2_true_shown': 32, 'false_removed': 4, 'true_removed': 1}}}
- SAME-LINE: false removed (local pooled) 4, true removed 8, eligible True, false removed on the hosted pair 3, separation 0.0481
- OUTCOME-MARKER: false removed (local pooled) 9, true removed 56, eligible False, false removed on the hosted pair 1, separation -0.3667
- NON-SETTLING-2: false removed (local pooled) 21, true removed 5, eligible True, false removed on the hosted pair 4, separation 0.7153
