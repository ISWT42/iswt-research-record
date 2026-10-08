# Overnight run, 5 to 6 Oct 2026: E1 and E2 (report)

**Who wrote it:** saved by the coordinating session (Claude, Opus 5.5) at about 09:42 UTC on 6 Oct, from the overnight agent's final reply. The agent could not write this file itself, because its tools refuse report files.
**Rebuild the numbers:** every table can be rebuilt from the sealed score files with `python code\report_tables.py seals | e1 | e2 | spend | writer | earlier | pairsplit | sharederrors`.

## Status
- E1 is done, and so is E2.
- **Lemonade use:** the last call returned at 09:35:50Z (E2's runner exited 0). Nothing of the agent's is running.
- **Spend:** US$0.2893 by the broker ledger (177 hosted writer runs), against a US$0.50 cap. Local runs cost nothing.

## E1: "shown needs both" (R2) on 150 new items written by DeepSeek (50 shown, 50 contradicted, 50 not shown)

| Arm | False "shown" (of 100) | True "shown" kept (of 50) | Right (of 150) | False "contradicted" (of 100) |
|---|---|---|---|---|
| A, Qwen3-4B alone | 15 | 38 | 98 | 14 |
| B, Gemma-4-E4B alone | 18 | 45 | 116 | 10 |
| R1 | 19 | 45 | 108 | 16 |
| **R2** | **11** | 37 | 108 | 16 |
| R3 | 11 | 37 | 105 | 6 |

- R2 was below both single models. It was not at most half of the better model's 15. Without the 17 items written two to a call, it is 10 against 12, with the same answer.
- Both models were wrong together on 24 of the smaller model's 34 errors. R3's false "contradicted" was below R1's, 6 against 16.
- **For a human check first:** 21 ids where both models agree against the label. These are X004, X006, X012, X023, X044, X045, X047, X061, X093, X094, X103, X104, X105, X108, X113, X114, X119, X124, X136, X142, X145. The 11 behind R2's false "shown" are X006, X023, X047, X093, X094, X103, X113, X114, X124, X142, X145.
- **The deciding-line rule** (NON-SETTLING-2, sealed separately) was applied by the coordinator at 08:48 UTC. It is not met: it removed 1 false "shown", where the bar needed 6. See `Workbench\deciding-line-2026-10-06\e1-apply-v1.json`.

## E2: the human-forced error test (2 models x 3 framings)
- **Items:** 27 present items (13 shown, 14 contradicted). Each has a context-missing twin (12 of those are empty logs) and a blank-output twin.

**Guesses (shown or contradicted) on the 27 context-missing twins:**

| Model and framing | Guess | not shown | Guesses on the 12 empty logs | Guesses that survive the quote check |
|---|---|---|---|---|
| Qwen, forced | 15 | 12 | 0 | 13 |
| Qwen, allowed | 10 | 17 | 0 | 9 |
| Qwen, rewarded | 9 | 18 | 0 | 8 |
| Gemma, forced | 22 | 5 | 11 | 11 |
| Gemma, allowed | 15 | 12 | 5 | 10 |
| Gemma, rewarded | 15 | 12 | 5 | 10 |

- **Present items, right in all three framings:** Qwen 20 of 27, Gemma 23 of 27.
- **Blank-output twins, guesses:** Qwen 27 forced (24 of them "contradicted"), 7 allowed, 6 rewarded. Gemma 9, 6 and 5.
- **Paired, forced only against allowed only:** Qwen context-missing 5 against 0 (p=0.0625); Gemma context-missing 7 against 0 (p=0.0156); Qwen blank-output 20 against 0 (p<0.001).
- [forecast bullet removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Seals (FreeTSA, GMT, 6 Oct)
- E1 design 00:38:21
- E2 design 00:38:27
- E1 addendum 1 00:42:04
- E2 twins 00:42:39
- E1 items 01:02:45
- E1 answers 04:02:25
- E1 score 04:02:44
- E2 answers 09:36:05
- E2 score 09:36:10

## What changed from the designs, and slips
- **E1 writer, addendum 1:** an empty or truncated reply counts as a try, and one item is written per call.
- **E2 started early by mistake** at 00:46:43Z, while the run guards were being tested. The agent stopped it after 18 answers; it resumed later, and no answer changed.
- **The exit-127 lines** in the logs are the agent's own forced stops, not crashes.
- **Pauses** for the gate demo and the s10 quiet gates were 01:58 to 02:16, 02:40 to 03:12, 05:34 to 08:40 and 08:51 to 09:07Z. The runners waited each time.
- **After the fourth pause,** three Gemma calls failed (the server held no model). One manual probe of 12 tokens loaded Gemma, and the retries succeeded. The probe is not part of any answer.
- **Shared-load window:** 09:24:38 to 09:28:40Z, when the s10 gate's final pass ran. About 9 E2 answers fall in it. Timings only; the answers are unaffected.
- **AGENTS.md slip:** the agent opened the broker's `lib\keystore.mjs` (a file whose name contains "key"). It is code, and it read or printed no key value.

## What this does not show
- Models wrote the items, labels and twins, and no person has checked them.
- At most 27 items per E2 cell.
- Two small local models, one run each.
- The FreeTSA signature chain was not verified (no CA file was downloaded).
