# PREREG-1: marker list, rule definitions, choosing procedure and success bar, fixed BEFORE any development quote was opened

Written: 2026-10-06T02:33:02Z (read from `date -u` in the same command that hashes this file).

This is the first stamp. The second stamp (DESIGN.md) comes after the development evaluation. Nothing below was tuned on a development quote, because none had been opened.

## What I had read before this stamp
- The re-score of 5 Oct (DESIGN.md, REPORT.md, `rescore_common.py`, `q4_quote_decides.py`) and its seal files. These hold counts, not item text.
- Code only: `receipts_model.py` (the reader prompt, `verify`, the failure-marker list), `run_pair.py`, `run2.py`.
- `overnight-2026-10-05\E1-DESIGN.md`, only to learn the answer-file format. I also listed the top-level file names of that folder by glob (E1-ADDENDUM-1.md, E1-DESIGN.md, E2-DESIGN.md and their SHA-256 files appear) and opened none except E1-DESIGN.md. I have not opened, listed, read or hashed anything under `e1\` or its logs.
- For the two development answer files (run 2 local, run 2 hosted): the field names; the counts of arms, of `code` values and of `answer` values; and, for the first local record (arm A, id 161), its field types with its `answer`, `code` and `verdict` values printed (its quote and reply were printed only as lengths). No quote text, no reply text, no item text, no join to any truth label.
- The bank file (`completion-claims-001-300.jsonl`) has not been opened. Run 1's answer files have not been opened (only seen in a folder listing).
- Numbers quoted in E1-DESIGN.md and the re-score report (for example R2 false "shown" 6 of 94 on ids 161 to 300, local pair).

## The two named rules (apply only on items where R2 says "shown")
R2 = "shown needs both" (`run2.rule2`): the final answer is "shown" only if both models' final answers are "shown" (each already passed the reader's checks, so each has a quote found word for word in the cited turn's output). A rule can only turn such an R2 "shown" into "not shown".

- **Evidence.** For each model, the cited turn and the stripped quote are re-derived from the recorded reply text exactly as the reader's verbatim gate does (`parse_reply`, `normalize_verdict`, `normalize_turn_id`, quote found in the turn's output). A quote's **line range** is computed in the cited turn's output split with Python `str.splitlines()`: for every occurrence of the quote in that text, the index of the line holding its first character and of the line holding its last character. A one-line quote gives (i, i). A quote that spans lines gives (i, j).
- **SAME-LINE.** R2's "shown" stands only if both models cite the same turn and some occurrence of one quote and some occurrence of the other have overlapping line ranges (they share at least one output line). A multi-line quote counts for every line it covers. No requirement that one quote's text contains the other's.
- **OUTCOME-MARKER.** R2's "shown" stands only if at least one of the two verified quotes contains a generic outcome marker, a pattern from `outcome_markers.py` (written from general knowledge of tool output, tested only on invented lines, and hashed in this stamp).
- **Fail closed.** If either model's evidence cannot be re-derived, the rule removes the "shown" and the count is reported (none is expected).
- **No key.** A rule sees only the two replies' evidence and the log's turns (command and output text). It never sees truth, deciding line, trap, why or claim. `selftest.py` checks that deleting those fields changes no decision.

## Decisions made now, with reasons
1. **At least one quote, not both, must carry a marker.** R2 already needs both models to say "shown" with verified quotes. The marker list is general-knowledge and cannot be complete for every tool, and each gap costs a true "shown". Requiring a marker in both quotes would count every gap twice. At least one keeps the rule narrow: remove a "shown" whose cited evidence, as quoted by either model, states no outcome at all. "Both" is reported as a sensitivity variant only.
2. **The marker is tested on the quote text, not on the whole line.** The quote is what the model offered as its evidence; a model that quotes a fragment without the outcome words has not quoted an outcome. The whole-line version is a sensitivity variant only.
3. **"Same line" means overlapping line ranges, not identical text.** Two quotes from different parts of one line, or a one-line quote inside a two-line quote, point to the same log line. Stricter readings (identical ranges; one quote's text contained in the other's) are sensitivity variants only.
4. **Sensitivity variants are never primary:** SAME-LINE-STRICT, SAME-LINE-CONTAINED, OUTCOME-MARKER-BOTH, OUTCOME-MARKER-LINE, SAME-LINE+OUTCOME-MARKER (both rules must keep). They are in the code and are reported beside the named rules, labelled exploratory.

## Choosing the primary rule (procedure fixed before the development data was looked at)
Development data: run 2's local answers (arms A and B, ids 161 to 300, 140 items) and run 2's hosted answers (arms F-Q and F-G, same ids). The local pair is what E1 will use, so it decides; the hosted pair is a replication check and a tie-break. F and T are R2's false and true "shown" in the local set; for a rule, f is how many false and t how many true "shown" it removes.
1. A candidate is **eligible** if it keeps at least 80% of R2's true "shown" (5 * (T - t) >= 4 * T).
2. If some eligible candidate removes at least one false "shown": the primary is the eligible candidate with the largest f; a tie goes to the smaller t; then to the larger f on the hosted pair; then to the simpler rule (SAME-LINE, then OUTCOME-MARKER, then an own rule).
3. If no eligible candidate removes a false "shown": the primary is the candidate with the largest separation f/F - t/T; a tie goes to SAME-LINE.
4. Candidates are SAME-LINE, OUTCOME-MARKER and, only if added under the next paragraph, one own rule. Variants are not candidates.
5. The procedure is implemented in `dev_eval.py`, written after this stamp from this text, so that the choice is computed and not made by eye.

**An own rule** is added only if neither named rule, on the local development set, both removes at least half of R2's false "shown" and keeps at least 80% of R2's true "shown". Then I may look at the development items that R2 got wrong and add exactly one rule, built from a single stated mechanism, with no threshold fitted to the data, no word taken from a development item, and only the pre-registered marker list and the reader's own failure-marker list as vocabulary. If it does not meet both conditions on the local development set, it is dropped. If both named rules already do, no own rule is added.

Run 1's answers (ids 1 to 160) are not development data here. If I look at them it is after the primary is chosen, to report only.

## The success bar (for E1, written now, kept)
On E1's items with the local pair, F = R2's false "shown", T = R2's true "shown"; the primary rule removes f false and t true "shown".
- **Removal:** f >= F / 2 (at least half of R2's false "shown").
- **Retention:** 5 * (T - t) >= 4 * T (at least 80% of R2's true "shown" kept).
- **Verdict:** MET if both hold and F >= 4. NOT MET if F >= 4 and either fails. THIN if F < 4: R2 left too few false "shown" to test the bar; counts are reported and no verdict is claimed.
- The verdict is a decision rule, not a significance test. With F near 4 to 10 the evidence is weak either way, and the report will say so. All other rules are exploratory.
- R2's counts from `e1_apply.py` must equal R2's counts in E1's own score file; if they differ, stop and find out why before reading anything else.

## Files stamped here
`PREREG-1.md`, `outcome_markers.py`, `deciding_rules.py`, `selftest.py`. `deciding_rules.py` and `outcome_markers.py` are frozen from this stamp on. A later bug fix, if one is needed, goes in a new dated file and is named in DESIGN.md; the stamped files stay as they are.
