# PREREG-3: version 2 of my own rule, and run 1 becomes development data; fixed BEFORE version 2 was evaluated

Written: 2026-10-06T02:46:39Z (read from `date -u` in the same command that hashes this file).

Third stamp. PREREG-1 (FreeTSA 02:33:18 GMT) fixed the markers, SAME-LINE, OUTCOME-MARKER, the choosing procedure and the bar. PREREG-2 (02:41:57 GMT) fixed my own rule, NON-SETTLING (version 1), before any hosted quote was opened. This stamp records what I saw after that, one change of plan, and version 2, in the order it happened. I have not run version 2 on any data.

## What I saw after PREREG-2
1. `dev_eval.py` with version 1, ids 161 to 300. Local pair: version 1 removes 4 of R2's 39 "shown" (4 false, 0 true); hosted pair: removes 4 (3 false, 1 true). It was admitted by PREREG-2's gate and the procedure chose it as primary.
2. The ids of R2's false "shown": local (6): 163, 171, 185, 199, 229, 277; hosted (7): 163, 185, 209, 238, 268, 277, 294. Version 1 removes 163, 185, 277 on the hosted pair. Those three were among the six local items I had read when writing it, so the hosted validation passed only through items I had seen. On the four hosted-only false "shown" (209, 238, 268, 294) version 1 removes none.
3. `postchoice_look.py --no-write` on run 1's local answers (ids 001 to 160), which PREREG-1 had said I would only report: R2 false "shown" 21 of 106, true "shown" kept 47 of 54. SAME-LINE removes 11 (4 false, 7 true). OUTCOME-MARKER removes 34 (6 false, 28 true). Version 1 removes 1 (1 false, 0 true). Version 1 is nearly inert outside the items it was written from.
4. The 21 run 1 false "shown" items: claim, both quotes, line ranges, deciding line and the bank's `why` note. Most cite a real line from another environment (a line tagged stage, sim, simulator, preview or demo) for a claim about production, often after a failed first attempt.
5. Not opened: any hosted-pair quote or reply; anything of E1.

## Changes of plan
1. **Run 1 is development data from now on** (PREREG-1's sentence saying otherwise is withdrawn). Reasons: ids 161 to 300 hold only 6 local false "shown", too few to choose among rules; run 1 adds 21; and the out-of-sample check that sentence protected has now been used. After this stamp nothing except E1 is out of sample for my own rule, so every development number for it is in-sample.
2. **NON-SETTLING (version 1) is withdrawn from the E1 rule set. Version 2 (NON-SETTLING-2) is the one rule of my own** (the cap of one is kept). Version 1 stays in the record and is reported on the development sets, labelled withdrawn.
3. **Version 2 (exact: `non_settling_rule2.py`, hashed in this stamp).** Same mechanism as version 1, plus a fourth family: an environment word. R2's "shown" stands only if (a) version 1 keeps it (neither quote has a non-settling word the claim does not use), and (b) neither verified quote, nor the command of the turn each cites, contains an environment word that the claim does not itself use. Environment words, as whole lowercase alphanumeric tokens (so `atlas-rehearsal` gives atlas and rehearsal): stage, staging, sandbox, rehearsal, sim, simulator, demo, mock, preprod, qa, uat, canary, replica, mirror, shadow, localhost, preview. Fail closed if evidence is missing. Inputs: the two quotes, the cited turns' commands, the claim; never truth, deciding line, trap or why (`selftest_own2.py` checks this).
4. **Development sets.** Local pooled set: ids 001 to 300 (run 1's local answers, arms A and B, for 001 to 160, plus run 2's local answers for 161 to 300). The hosted pair (run 2, ids 161 to 300) stays the validation and tie-break. Sub-sets are reported too: run 1 alone, run 2 alone, ids 201 to 300.
5. **Admission and selection** are PREREG-1's procedure and PREREG-2's gate, unchanged in wording, applied to the pooled local set (`dev_eval2.py`, which calls the stamped `dev_eval.choose_primary` and `dev_eval.own_rule_gate`): version 2 is a candidate only if, on the pooled local set, it removes at least half of R2's false "shown" and keeps at least 80% of R2's true "shown", and, on the hosted pair, it removes at least one false "shown" with f/F - t/T >= 0. If it is not admitted it is reported as exploratory and the procedure runs on SAME-LINE and OUTCOME-MARKER. Ties rank the own rule last.
6. **The success bar and verdict categories** are PREREG-1's, unchanged.
7. **The E1 rule set:** SAME-LINE, OUTCOME-MARKER, NON-SETTLING-2, and the five sensitivity variants. Version 1 is not computed on E1.

## Files stamped here
`PREREG-3.md`, `non_settling_rule2.py`, `selftest_own2.py`, `dev_eval2.py`. The files of PREREG-1 and PREREG-2 are unchanged. `dev_eval2.py` was dry-run with status lines only (no rule counts printed) before this stamp.
