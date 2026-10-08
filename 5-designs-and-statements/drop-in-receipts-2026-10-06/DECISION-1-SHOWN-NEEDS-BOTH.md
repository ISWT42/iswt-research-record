# Drop-in receipts, decision 1: what a plain-rules "shown" counts for (7 October 2026)

Made by Claude on Joshua's delegation. His words, 7 Oct 2026, 05:59 UTC: "I would recommend you follow your logic on that one and explain if necessary with a hover over on anything." Made before anyone has looked at the answer keys for this question, and sealed before step 2 (the model reader) is built.

## The rule
1. **A plain-rules "shown" counts as one of the two agreeing checkers.**
   - "Shown" still needs two checkers to agree, and at least one of the two must be a model that read the whole log.
   - So the final answer is shown when the rules say shown and at least one model says shown, or when both models say shown.
2. **A plain-rules "contradicted" stands on its own.** A non-zero exit, a failing test summary or a rejected push is decisive, and the reader never overrides it.
3. **A plain-rules "not shown (needs a reader)" goes to the reader,** where the existing pair rule applies unchanged.

## Why
- The "shown needs both" rule exists because two models share most of their blind spots: in the sealed test they were each wrong on 34 of 100 items, and on the same 19.
- A fixed rule fails in different ways from a model. It reads exit codes and the exact confirming line, and it never "believes" a summary. A rule and a model agreeing is therefore a more independent pair than two models agreeing.
- It still never lets one checker settle "shown" alone. The rules read narrow patterns, and they can miss a later line in the log that undoes the result; a model reading the whole log can catch that.
- "Contradicted" is the safe direction. A decisive failure line needs no second opinion.

## What it changes, known before any key is read
- On S2 (90 claims) it changes exactly two claims, C055 and C060. In each, the rules said shown, one model said shown and the other said not shown. Under the rule they become shown.
- Whether that is right is for the keys to say. This note fixes the rule first.

## How it is explained to a reader (his "hover over")
Wherever the combined answer appears on a page, a hover note says in plain words how it was reached, for example:
- "Shown: the plain rules found the line that confirms it, and a model reading the whole log agreed."
- "Shown: both models found the line that confirms it."
- "Contradicted: a tool printed a failure, which settles it on its own."
- "Not shown: the checkers didn't agree that the log confirms it."

In a terminal, where there is no hover, the same sentence follows the answer on its own line.
