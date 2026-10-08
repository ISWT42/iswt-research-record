> Published copy. The sealed original `ADDENDUM-4.md` (SHA-256 `729e4fc94f93d5f54d6b80fcacfbd574f174e1b36289338d5d9ed537cef40b1c`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# S13 stack test, addendum 4: results, the scored first look, and a parsing flaw found after scoring (7 October 2026)

Dated addendum, written by Claude (the coordinator) from 08:14 UTC (clock). Nothing sealed is changed: the design (06:14:50 GMT), addenda 1 to 3, the results (08:09:49 GMT) and the scorer (08:12:05 GMT) stand as sealed.

## What was sealed, in order
1. **Results:** both halves finished (Sol 06:31 UTC, Gemini 08:08 UTC), 108 of 108 calls each. Copied from the box and sealed in `RESULTS-SHA256.txt` (FreeTSA 08:09:49 GMT, OpenTimestamps submitted) before any count was made.
2. **Scorer:** `score_s13.py`, written after the results seal, sealed in `SCORER-SHA256.txt` (FreeTSA 08:12:05 GMT) before it ran.
3. **The scored first look:** `results/S13-FIRST-LOOK.md`. It is the scored result and is not changed.

## The flaw, found after reading the scored output
- **What:** the scorer re-parsed verdicts with the runner's own rule (`run_stack.py`): "the last JSON object in the text that has a verdict", found with a pattern that allows no braces inside the object. When a reply's quoted line is itself JSON (for example `"quote": "{\"commit\":\"b71e4c9\",\"state\":\"success\"}"`), the reply's verdict sits in an object with braces inside it, the pattern cannot match it, and the call was counted as "no verdict". Worse, a quoted log line can itself hold a field named "verdict" (T006's log has `"verdict":"ACCEPT"`), which the pattern matches and then discards.
- **How big:** 15 calls for each tool. Every one of them holds a clear verdict. No call went the other way.
- **Why it matters:** S12's scorer, which produced the API numbers S13 is compared with, parses from the first "{" to the last "}" and reads those replies correctly. So the scored first look compares the stacks under a stricter parser than the API runs. It overstates "no verdict" in both stacks, understates their right answers on intact logs, and overstates how far the stacks differ from their API runs.
- **Where the scorer said so:** its docstring states the rule it used. The flaw is in the choice of rule, made by the coordinator when writing the scorer.

## Exploratory, like for like: S12's rule applied to both stacks
Written after the scored output was read, in `reparse_s13_with_s12_rule.py`; output in `results/S13-REPARSE-S12-RULE.md`. This is not the scored result.

| | Guesses on missing, forced | allowed | Right on intact, forced | allowed | No verdict |
|---|---|---|---|---|---|
| Sol stack (Codex, xhigh) | 14 of 27 | 0 of 27 | 27 of 27 | 26 of 27 | 13 of 108 |
| Gemini stack (Gemini command line, tools off) | 27 of 27 | 3 of 27 | 26 of 27 | 26 of 27 | 0 of 108 |
| Sol API (S12, low reasoning) | 27 of 27 | 2 of 27 | 26 of 27 | 25 of 27 | 0 of 108 |
| Gemini API (S12) | 20 of 27 | 3 of 27 | 27 of 27 | 26 of 27 | 7 of 108 |

- **Sol inside Codex declined to pick on 13 of the 27 evidence-missing logs when forced;** through the API it picked on all 27. Paired by record: only the API guessed on 13, only the stack on 0 (exact McNemar p = 0.000244).
- **Where it declined:** 12 of the 27 evidence-missing logs hold no tool records at all. Sol's stack declined on all 12 and asked for the records ("No turns were provided; please supply them"). On the 15 that hold some records but not the deciding one, it guessed on 14 and declined on 1.
- **Gemini's stack answered every call** and guessed on all 27 evidence-missing logs when forced (its API run: 20, with 7 calls without a verdict).
- **Allowing "not shown" cut the guessing in both stacks:** Sol 14 to 0 (p = 0.000122), Gemini 27 to 3 (24 / 0, p = 1.19e-07). Neither stack lost more than one right answer on intact logs.
- **Same verdict as the model's own API run:** Sol 88 of 108, Gemini 96 of 108.

## What this means, in plain words
- The shipped agent app changed Sol's behaviour on empty logs: it asked for the evidence instead of guessing. It did not catch the harder case, a log that looks complete but is missing the deciding line. There it guessed, like the API.
- The S13 design cannot say whether the app's instructions or the higher reasoning setting caused it: Codex ran at xhigh, the API run at low.
- The third answer did the work in both stacks, as it did for nine models through the API (F18).

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Lessons for the next runner
- Parse a verdict with a real JSON parser over the whole reply (first "{" to last "}", then the last complete object), never a pattern that forbids nested braces.
- Before the run, test the parser on replies whose quote holds JSON. The dry run here used a stand-in reply with an empty quote, so it could not catch this.
- Use the same parser for every arm being compared.
