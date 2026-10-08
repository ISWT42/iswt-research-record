# PREREG-2: one rule of my own (NON-SETTLING), fixed after the local development quotes were read and BEFORE any hosted-pair quote was opened

Written: 2026-10-06T02:41:42Z (read from `date -u` in the same command that hashes this file).

Second stamp. The first (PREREG-1, FreeTSA 02:33:18 GMT) fixed the marker list, SAME-LINE, OUTCOME-MARKER, the choosing procedure and the success bar before any development quote was opened. This stamp records what I did next, and one deviation from PREREG-1, in the order it happened.

## What I looked at between PREREG-1 and this stamp
1. Ran `dev_eval.py --no-write` on run 2's local and hosted answers (counts only). It printed, for both pairs and both sets (ids 161 to 300 and 201 to 300), R2's and every rule's false and true "shown" and how many each rule removes. So I have seen the hosted pair's counts for the named rules and the variants, and no hosted id, reply or quote.
2. For the local pair only (arms A, B): printed all 39 R2 "shown" items (id, truth, trap, line ranges, the first 110 characters of each model's quote, marker names, the deciding line), and, for the six local R2 false "shown" (ids 163, 171, 185, 199, 229, 277), the claim, the commands, the output lines, the deciding line and the bank's `why` note.
3. Not opened: any hosted-pair reply or quote; which items the hosted pair's R2 "shown" or false "shown" are; run 1's data; anything of E1.

## What the local development set showed (ids 161 to 300, 140 items; R2 "shown" on 39 items: 6 false, 33 true)
- SAME-LINE removes 1 of the 39 (0 false, 1 true). Both small models almost always quote the same line, including in all six false "shown".
- OUTCOME-MARKER removes 31 of the 39 (3 false, 28 true). The bank's "shown" lines are mostly observations of state (a value, a header, a flag), not outcome words, so the pre-registered marker list does not fit this bank.
- Neither named rule meets the bar's two conditions on the local pair. Under PREREG-1's procedure no candidate is eligible and removes a false "shown", so step 3 would choose SAME-LINE with separation about -0.03: no demonstrated effect.
- The six false "shown" are quotes that are real, on the line both models chose, and not deciding: three carry the word "accepted" (a queue acknowledgement or a verification status), two are one agent repeating another's statement (says, reports), one is the other environment's value.

## Deviation from PREREG-1, stated openly
PREREG-1 allowed one own rule, built only from the pre-registered marker list and the reader's failure-marker list, with no word taken from a development item. Under that clause no own rule can address these failures (the markers do not fit the bank). I set the vocabulary clause aside and wrote one rule with a new word list and the claim text as a second input. Its local numbers are **in-sample**: I chose the families after reading the six items, and "accepted", "says" and "reports" are in the list. E1 is the only out-of-sample test. The hosted pair, whose quotes I have not opened, is used as a weak validation (it covers the same 140 items, with different models, so it is not independent for items that both pairs get wrong).

## The rule NON-SETTLING (exact: `non_settling_rule.py`, hashed in this stamp)
Mechanism, one: a quote that settles a claim reports the claimed outcome first-hand and finally. A quote that carries a non-settling word reports something else: the request was only acknowledged, someone else said so, or the line is hypothetical.
- Three word families, case-insensitive whole words, not glued to a path or identifier (not right after `/ \ . _ -`, and not right before one of them followed by a word character): acknowledged_not_done (accepted, queued, enqueued, pending, scheduled, submitted, requested, initiated, dispatched, awaiting, async, asynchronous, asynchronously, in progress); secondhand_report (says, said, reports, reported, claims, claimed, told, asserts, asserted, relayed, hand-off, handoff, according to); hypothetical_or_preview (preview, simulated, simulation, would, should, dry run, not yet, so far).
- R2's "shown" stands only if **neither verified quote contains a non-settling word that the claim itself does not use** (a claim that says "scheduled" is settled by "scheduled"). Claim and quote are compared as plain lowercase words.
- If either model's evidence cannot be re-derived, the rule removes the "shown" (fail closed).
- Inputs: the two verified quotes and the claim text. Never truth, deciding line, trap or why (`selftest_own.py` checks that deleting those fields, or changing every truth label, changes no decision). The claim is not an answer key; a deployed checker has it.

## Admission and selection (all computed by `dev_eval.py`, hashed in this stamp)
NON-SETTLING is a candidate for primary only if both hold:
1. **Local conditions (PREREG-1's own-rule clause, unchanged):** on the local pair, ids 161 to 300, it removes at least half of R2's false "shown" and keeps at least 80% of R2's true "shown".
2. **Hosted validation:** on the hosted pair, ids 161 to 300, it removes at least one false "shown", and f/F - t/T >= 0 (it removes false "shown" at a rate at least equal to the rate at which it removes true "shown").

If both hold, it joins SAME-LINE and OUTCOME-MARKER and PREREG-1's procedure (steps 1 to 4) picks the primary among the three, with the own rule last on ties. If either fails, it is reported as exploratory and the procedure runs on the two named rules. The success bar and the verdict categories are exactly PREREG-1's. The sensitivity variants stay non-candidates.

## Files stamped here
`PREREG-2.md`, `non_settling_rule.py`, `selftest_own.py`, `dev_eval.py`, `selftest_dev.py`. The PREREG-1 files are unchanged (the hashes in PREREG-1-SHA256.txt still hold). From this stamp on these files are frozen; a later bug fix goes in a new dated file and is named in DESIGN.md.
