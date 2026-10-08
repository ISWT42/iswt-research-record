# Re-score of run 2 (quotes) and run 3 (certainty): sealed design

Written: 2026-10-06T00:19:53Z (read from `date -u` in the same command that hashes this file)

## What this is
A re-analysis of answers that already exist on disk. No model calls of any kind. No network calls except the two FreeTSA timestamp requests (they send only a hash). Nothing is sent, pushed or published. It is descriptive: no hypothesis tests, no p-values, nothing tuned against the data. Item text (claims, log lines, quotes) is never printed and never written to a results file; only ids, labels, counts and rates.

Two questions, from an outside panel's research suggestions:
- **Q3.** When does "not shown" beat answering, and is a model's own certainty usable? (run 3)
- **Q4.** When does a quoted line actually decide the claim? Do "the quote is real" and "the quote settles it" come apart, and how often? (run 2, local and fast lanes)

## What I had read before sealing (disclosure)
- Code: `run2.py`, `run_pair.py`, `run3.py`, and in `receipts_model.py` the reply schema, the system prompt, `parse_reply`, `normalize_verdict`, `normalize_turn_id`, `ShownTurn.holds_quote` and `verify`. Also `EXAM-BANK-README.md` and `RUN3-DESIGN.md` (a sealed design, not a result).
- Structure only, no outcomes: the bank's keys; for ids 161 to 300 the counts of truth labels (46 shown, 47 contradicted, 47 not shown) and of trap labels; that `deciding_line` is empty exactly when the truth is "not shown"; that the deciding line is a whole output line of exactly one turn for 91 of the 93 shown/contradicted items and of two turns for two (ids 178 and 236); that the combined bank equals the sealed batches for ids 1 to 200. For the three answer files: the field names, rows per arm (140 each), no duplicate (arm, id), ids 161 to 300 all present, and the set of distinct values of `answer`, `code`, `verdict` and `certainty` (values only, not counts).
- Not read before sealing: any `score-*.json`, `RUN2-NOTES.md`, `RUN3-NOTES.md`, `RESULTS.md`; no count of answers by code or certainty; no join of any answer to its truth.
- Input hashes (below) were compared with the hashes sealed at the time of each run: all equal.

## Inputs (SHA-256; every script refuses to run if one differs)
| File | SHA-256 |
|---|---|
| chatgpt-review-2026-10-04\completion-claims-001-300.jsonl (the bank) | edb897f7b6d7df41a14eb37e4f6079ade036dabdec6d140d82dec6147199593a |
| lemonade-entry-2026-10-05\run2\results\answers-run2-local.jsonl | ba5303a247fe5a805064261c698e0958a36b20d6ec3791c69a1fb48f9c09eed5 |
| lemonade-entry-2026-10-05\run2\results\answers-run2-fast.jsonl | 7f634ad3a0ae7874bdecb81aec31096db7a2f6cbbfe4f597bd653c22092f284e |
| lemonade-entry-2026-10-05\run3\results\answers-run3.jsonl | df9a399dfd2959e30a226c96225495adc3435cd8ea2a07ccdd04eb4417eea9b4 |
| chatgpt-review-2026-10-04\JOB3-BATCH-5.jsonl (equality check only) | 468e2ff2deab7cf50cf31fee0a35e832f945a59a787a5703252619b03f19cda1 |
| lemonade-entry-2026-10-05\run3\results\score-run3.json (reconciliation only) | c9e2ad26fca75f3a55812563540999eca69393e599673175a237df44e6ee357f |
| lemonade-entry-2026-10-05\run2\results\score-run2-local.json (reconciliation only) | 944afdd9cc9d1a4ad970df47544b391cccb7cc63c4abd0dfe86266272d8cdf23 |
| lemonade-entry-2026-10-05\run2\results\score-run2-fast.json (reconciliation only) | 67f26941f3ec510cca5022accd15aab0d4f161fa150308075a12a8fb20c3505d |
| swarm-receipts-public\receipts_model.py (source of the checks being mirrored) | b0842ecd738554719443269a93665d0e8045c3244a20587e0455b82568169942 |
| lemonade-entry-2026-10-05\run2\run2.py | bd8decc1ddb4bc10ebcd2bc91ac0aab8c1a94d29dde6e001f456d0f119a1d29d |
| lemonade-entry-2026-10-05\run_pair.py | 3d8e8292ebd48b1278549988d275bac3a396ed99ccaa1e71a1df5b0d56468bdb |
| lemonade-entry-2026-10-05\run3\run3.py | 5a4d47b4f8e1ca44fdc5af3b462f914753fc17fe5a55cadf2bc1682f5a90aa33 |

All paths are under `C:\Users\joshd\Workbench\`. The scripts check all twelve hashes before anything else is read. The last four rows are the code whose logic is mirrored; the score files are read only for the reconciliation step, after the analysis has been computed.

## Common definitions
- **Sets.** `fresh_161_300` = ids 161 to 300 (140 items, the main set). `primary_201_300` = ids 201 to 300 (100 items, reported beside it). Every number is given for both.
- **Bank.** The combined bank file. Truth is normalised: `not_shown` becomes "not shown". Labels: "shown", "contradicted", "not shown". `trap` and `deciding_line` are the bank's own fields. At run time the script also checks that items 161 to 200 equal `JOB3-BATCH-5.jsonl` (report only).
- **Answer.** The record's `answer` field: the checker's final answer after the mechanical quote checks (shown, contradicted or "not shown"). **Right** means the answer equals the normalised truth. The record's `verdict` field (used in Q4 only, and always labelled "model verdict") is the model's own verdict before the checks, with `not_shown` read as "not shown".
- **Unit.** One answer record = one (arm, id). If a file had a duplicate (arm, id), the last record would be used, as `run2.py` and `run3.py` do, and the number reported (none are expected).
- **Rates.** Always k out of n with its own n written beside it. Interval: Wilson 95% (z = 1.96), as in `run2.py`. A difference between two rates: Newcombe's hybrid-score interval (method 10), built from the two Wilson intervals.
- **Independence.** Intervals treat answers as independent. Within a lane (Q4) the two arms answer the same items, so a pooled interval is optimistic; per-arm numbers are always given as well.

## Q3: "not shown" against answering, and the model's own certainty (run 3)
**Data.** `answers-run3.jsonl`: arms U-Q (`qwen/qwen3.5-9b`) and U-G (`google/gemma-4-26b-a4b-it`), 140 items each. For each arm, each set.

**Certainty category** of an answer: `sure` if the `certainty` field is "sure"; `unsure` if it is "unsure"; `unmarked` otherwise (the field is null). Unmarked answers are further split by cause: `no_answer` (the record says no answer), `reply_not_a_json_object` (the reply does not parse to a JSON object by the mirrored `parse_reply`), `certainty_missing_or_invalid` (the reply parses but has no usable certainty).

**Q3.1 Counts.** n answers; how many are sure, unsure, unmarked (each out of n); the causes of unmarked (out of the unmarked count). The answer mix (shown, contradicted, not shown) out of n. Reference: the share of items whose truth is "not shown" (what a constant "not shown" would get right).

**Q3.2 Accuracy by category.** Right out of n for sure, for unsure, and for unmarked. Then sure minus unsure (difference of rates, Newcombe interval).

**Q3.3 Cell table.** For each answer type (shown, contradicted, not shown) and each category: n; right out of n; `truth_not_shown` = how many of the n have truth "not shown" (what the cell would score if its answers became "not shown"); `net_if_replaced` = `truth_not_shown` minus right (for the type "not shown" it is 0 by definition). A positive `net_if_replaced` means "not shown" would score more correct answers than answering does in that cell; this is the direct reading of "when does not shown beat answering".

**Q3.4 The rule (primary), R_all.** Every answer whose category is unsure or unmarked becomes "not shown"; sure answers are unchanged. (This is exactly policy U of `run3.py`.) Report, before the rule and after it:
- wrong "shown" answers = answers "shown" whose truth is not "shown". Counts: out of the "shown" answers (before, after), and out of the items whose truth is not "shown" (the false-shown rate, before and after);
- wrong "shown" removed = before minus after, out of before; and of those removed, how many are now right (truth "not shown") and how many are still wrong (truth "contradicted");
- right answers out of n, before and after;
- **correct answers given up** = answers that were right and are wrong after the rule: out of all right answers; and by type, true "shown" answers given up out of right "shown" answers, true "contradicted" answers given up out of right "contradicted" answers;
- wrong answers made right (wrong before, right after) out of all wrong answers;
- the exchange: wrong "shown" removed, correct answers given up, and their ratio (given up per removed);
- false "contradicted" (answers "contradicted" whose truth is not "contradicted"), before and after, out of the items whose truth is not "contradicted".

**Q3.5 Rule variant, R_shown (secondary).** Only unsure or unmarked answers that are "shown" become "not shown"; "contradicted" and "not shown" answers are left alone. Same measures as Q3.4.

**Q3.6 Catch rate and give-up rate (is the flag informative).** "Flagged" = unsure or unmarked. Report: wrong answers that were flagged out of all wrong answers (the catch rate); right answers that were flagged out of all right answers (the give-up rate); the same two for "shown" answers only (wrong "shown" flagged out of wrong "shown"; right "shown" flagged out of right "shown") and for "contradicted" answers only; and the share flagged out of n. Catch rate minus give-up rate (all answers, and "shown" only) with a Newcombe interval. If the flag carried no information, the catch and give-up rates would be about equal.

## Q4: does the real quote settle the claim? (run 2, local and fast lanes)
**Data.** `answers-run2-local.jsonl` (arms A = Qwen3-4B-Instruct-2507-GGUF, B = Gemma-4-E4B-it-GGUF) and `answers-run2-fast.jsonl` (arms F-Q = `qwen/qwen3.5-9b`, F-G = `google/gemma-4-26b-a4b-it`), 140 items each, both sets. Pooled per lane, and per arm.

**Population V: the quote passes the verbatim check.** The record's `code` is one of `verified`, `shown_citing_failure`, `quote_echoes_command`, `shown_over_overwritten_failure`. These are exactly the codes `verify()` in `receipts_model.py` returns after `turn.holds_quote(quote)` has passed (the quote is found verbatim in the cited turn's output). A nested secondary population V_verified is `code == verified` only (the answers that stand as shown or contradicted). Cross-check, report only: the script re-derives the verbatim gate from each record's `reply` and the bank's turns (mirrored `parse_reply`, `normalize_verdict`, `normalize_turn_id`; the quote must be a non-empty string found in the cited turn's output text), and counts disagreements with the recorded code. The analysis always uses the recorded code. Answers whose quote failed the check (`unverified_quote` etc.), "not shown" verdicts, unparseable replies and backend errors are outside V; their counts are reported as accounting.

**Cited turn and quote.** From the reply: the turn named by `turn_id` (turn labels T1, T2, ... in order) and the stripped quote. For a record in V that cannot be re-derived, the class is `UNRESOLVED` (counted, excluded from the class rates).

**Class of a quote in V.** Let D be the item's `deciding_line` and O the cited turn's output text. The cited turn "holds" D if D is one of `O.splitlines()`.
- `NO_D`: the item has no deciding line (D is empty; the bank has this exactly when the truth is "not shown", which the script checks).
- Otherwise, if the cited turn holds D: `FULL` if quote == D; `PART` if quote is a proper substring of D; `PLUS` if D is a proper substring of quote (the quote spans more than the line).
- Otherwise `OTHER` (some other verbatim text). Rows where the quote text relates to D but the cited turn does not hold D are classed `OTHER` and counted separately (`wrong_turn_text_match`).
- **On the deciding line** (`ON`) = FULL, PART or PLUS. The strict reading is FULL only; per-class rates are given so either can be read off. `NOT_ON` = OTHER or NO_D.
- `ambiguous_part`: PART rows whose quote also appears in another line of the cited output (reported as a count).

**Q4.1 Accounting.** Per lane, arm and set: n answers; counts by `code`; n in V; counts by class.

**Q4.2 Do they come apart.**
- Share of V on the deciding line, out of V.
- Among V on items that have a deciding line (truth shown or contradicted): share OTHER, out of ON + OTHER.
- Share of V on items with no deciding line (NO_D), out of V.
- Share NOT_ON, out of V.

**Q4.3 Does the verdict match the truth.** For each group (ON, FULL, PART, PLUS, OTHER, NO_D, NOT_ON): the count of rows, and k out of n for
- *answer match* = the final answer equals the truth (primary);
- *model verdict match* = the model's own verdict equals the truth (secondary).
Contrast, on items that have a deciding line: ON against OTHER (difference in match rate, Newcombe interval). Secondary contrast: ON against NOT_ON. Also the (answer, truth) count matrix for ON, OTHER and NO_D.

**Q4.4 Wrong answers that carry a real quote.** Among V rows whose final answer is "shown": how many are wrong (truth not "shown"), and of those how many are ON, OTHER, NO_D. The same for final answer "contradicted".

**Q4.5 By trap.** Q4.1 to Q4.4 for each trap label in the bank (none, retry, other_environment, expected_error, tool_failed_to_run, truncated, intermediate_signal, narration, example_text, relayed_claim, injected_text), pooled per lane and per arm, for both sets. A trap with fewer than 5 rows in V is marked `thin`.

## Reconciliation (report only)
Each script re-computes a few figures that earlier scoring already stored and compares them: for run 3 the certainty counts, right when sure, right when unsure, raw right, raw false "shown", policy-U right and policy-U false "shown" (from `score-run3.json`); for run 2, per arm and set, the number right, the false "shown" count and the answer mix (from `score-run2-local.json` and `score-run2-fast.json`). The comparison is written to the results as agree / differ; it does not change any analysis.

## Scripts and outputs (all in `C:\Users\joshd\Workbench\rescore-2026-10-05\`)
- `rescore_common.py`: input checks, bank and answer loading, Wilson and Newcombe, mirrored reply parsing, versioned no-overwrite writing.
- `q3_certainty.py`: Q3. Writes `results-q3-v1.json` (next free version if it exists; never overwrites).
- `q4_quote_decides.py`: Q4. Writes `results-q4-v1.json` (same rule).
- `selftest.py`: checks the helpers, the quote classes and the certainty rule against hand-worked answers on small invented data, and runs both scripts end to end on an invented copy of the whole setup in a throwaway folder (invented bank, answers and stored scores; it touches no real data). It passed 141 of 141 checks before sealing.
- Each script takes `--run-at "$(date -u +%FT%TZ)"` (the time is read in the same command), refuses to run on the real data unless `DESIGN-SHA256.txt` exists and every file listed in it still has its sealed hash, and prints status lines only: files read, row counts, integrity checks and the reconciliation tally. No result figure is printed, so none is read before the results are sealed.

## Limits declared in advance
1. The bank is synthetic; one model (Sol) wrote the items, the truth labels, the deciding lines and the trap labels, and no person has yet checked them. "The quote is the deciding line" means the bank author's line.
2. "On the deciding line" is a text-containment test, not a judgement; a short fragment can fall inside the deciding line by coincidence (hence the FULL / PART / PLUS split and the `ambiguous_part` count).
3. The two arms of a lane answered the same items; pooled intervals are optimistic. Hosted models at temperature 0 do not reproduce exactly; this analyses the recorded answers and re-runs nothing.
4. Certainty is the model's own word under one instruction wording; "unmarked" lumps several causes; run 3's prompt differs from run 2's (a certainty instruction was appended), so the two runs are different conditions and are not pooled.
5. The rule R_all is evaluated on the same answers that raised the question: no held-out test.
6. Trap cells are small; their intervals are wide.

## Procedure
1. This file is written first; then the scripts; `selftest.py` runs on invented data only.
2. In one command: the time is read with `date -u` and written into this file; then `sha256sum DESIGN.md rescore_common.py q3_certainty.py q4_quote_decides.py selftest.py > DESIGN-SHA256.txt`; then `openssl ts -query -data DESIGN-SHA256.txt -sha256 -no_nonce -cert -out DESIGN-SHA256.txt.tsq` and `curl -s -H "Content-Type: application/timestamp-query" --data-binary @DESIGN-SHA256.txt.tsq https://freetsa.org/tsr -o DESIGN-SHA256.txt.tsr`.
3. Run `q3_certainty.py` and `q4_quote_decides.py`, stdout to `run-q3-v1.log` and `run-q4-v1.log`. A results file is never overwritten.
4. `sha256sum` the two results files and the two logs into `RESULTS-SHA256.txt`; stamp it the same way, before reading any result. Each stamp's time is read from the reply with `openssl ts -reply -text`. No network call besides the timestamp request is allowed, so the reply's signature chain can only be checked against the root certificate carried inside the reply (and earlier FreeTSA replies), not against a root downloaded from freetsa.org; the report says so.
5. Then `REPORT.md`: plain words, counts first, each with its own denominator, and a "what this does not show" section.
6. If a script has to change after sealing, the original stays, the new file gets a new name, a new seal file is hashed and stamped before any re-run, and the report says so.
