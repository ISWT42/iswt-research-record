# Re-score of run 2 (quotes) and run 3 (certainty): report (6 Oct 2026)

**Status:** the design and scripts were sealed by FreeTSA at 2026-10-06 00:20:08 UTC, and the results at 00:20:56 UTC, before they were read. No model calls were made.
- The agent's report was returned as text, because the harness blocks report files from subagents. The coordinating session saved this summary.
- Every table regenerates from the sealed results with `python make-report-tables.py`.
- Main set: items 161 to 300 (140 items). The primary subset, items 201 to 300, is in the results files.

## The short answers

**Q3. Is a model's own certainty usable as a guard on "shown"? Not in these two models.**
- Every "shown" answer was marked "sure": qwen3.5-9b 42 of 42, gemma-4-26b 49 of 49. That includes every wrong one, 8 and 12.
- So the rule "every unsure or unmarked answer becomes not shown" removes **0 of 8** and **0 of 12** wrong "shown" answers.
- It costs almost nothing (1 of 93 and 0 of 95 correct answers given up) only because it changes almost nothing.
- "Not shown" beats answering in one small cell only: qwen "contradicted, unsure", 0 right of 3.

**Q4. Do "the quote is real" and "the quote settles it" come apart? Yes. That is where the wrong "shown" answers are.**

Quotes that pass the word-for-word check, by where they land:

| | Local pair | Hosted pair |
|---|---|---|
| Not on the item's deciding line | 83 of 228 (36%; 30 to 43) | 77 of 201 (38%; 32 to 45) |
| Right when the quote is the deciding line | 137 of 145 (94%) | 115 of 124 (93%) |
| Right when the quote is another real line | 13 of 22 (59%) | 15 of 24 (62%) |

Gap: +35 points (+17 to +56) and +30 points (+13 to +50).
- **Wrong "shown" answers that carry a real quote:**
  - local: 26 of 26 were not on the deciding line (derived);
  - hosted: 26 of 27 were not on the deciding line (derived).
- **By trap:**
  - `expected_error` is the one trap where the quote is on the deciding line and the answer is still mostly wrong (right 6 of 14 local, 3 of 10 hosted).
  - In `other_environment` and `intermediate_signal`, a real quote from another line was wrong every time: 0 of 4 and 0 of 1 local, 0 of 3 and 0 of 3 hosted.

## What it means, in plain words
- **A verbatim quote shows the line exists. It does not show the line decides the claim.** Nearly every false "shown" with a real quote cited a real line that wasn't the deciding one. This is Joshua's "a name is not the content", and the outside panel's "a record shows a check ran, not that the work was done", measured.
- **A model's "I'm sure" carried no warning** on the answers that mattered.

## What this does not show
- **It's descriptive.** No rule was tested on held-out items. A deployed checker has no answer key for the deciding line, so "check the quote is the deciding line" needs a way to find it without a key.
- **The data is limited:**
  - two models, one certainty wording, 140 items;
  - gemma marked "sure" 136 times of 140;
  - qwen's 12 unmarked answers are mostly replies that weren't JSON.
- **The bank:** it is synthetic, written and labelled by one model, and no person has checked the labels.
- **"On the deciding line" is a text test,** not a judgement of understanding. Trap cells are small, so treat them as leads.
- **Counting:** the pooled "both models" rows count each item twice, so prefer the per-model rows in the results files.
- **Repeat runs:** hosted runs at temperature 0 don't repeat exactly, and this analyses the recorded run only.
