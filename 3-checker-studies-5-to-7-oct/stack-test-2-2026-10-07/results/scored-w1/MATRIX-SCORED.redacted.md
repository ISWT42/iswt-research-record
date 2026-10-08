> Published copy. The sealed original `MATRIX-SCORED.md` (SHA-256 `3c3e8dc5faabc9cbb3cdaaa741e1507b2a56bee60cb3494cf3fcf6149613ba89`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 2 forecast section(s) or paragraph(s) removed.

# Stack test 2, Test A: scored

Scored by `score_matrix.py` (sealed before the run). Cells read: openai-ours, openai-theirs; not run: claude-ours, claude-theirs. A log's call is the majority of its runs (2 of 3; one run when a cell has fewer than three complete repeats, labelled). Checks: every file in RUN-SHA256.txt matches (18 files; SHA-256 of the list 5b83a1fdf284); score_screen.py 9ac239c86e23 matches the screen's seal (ADDENDUM-1-SHA256.txt); cvp/scorer.py 57921ba81c3a matches the screen's seal (SCORER-SHA256.txt).

## The cells (counts beside their denominators)

- **claude-ours**: not run.
- **claude-theirs**: not run.
### openai-ours, wave 1, 2026-10-07: 576 of 576 rows; complete repeats [1, 2, 3]; read on [1, 2, 3]
Models asked ['openai/gpt-6.1-sol']; reported ['openai/gpt-6.1-sol'].

| Version | False success on its weak-spot logs | True success, passed logs | Receipt score (jobs) | Invalid runs | Three runs agree (logs) |
|---|---|---|---|---|---|
| report | 2 of 16 (fail logs) | 16 of 16 | 14 of 16 | 0 of 144 | 44 of 48 |
| did-the-work | 2 of 16 (absent logs) | 16 of 16 | 14 of 16 | 0 of 144 | 47 of 48 |
| coat-check | 0 of 16 (fail logs) | 16 of 16 | 16 of 16 | 0 of 144 | 48 of 48 |
| coat-check-did | 0 of 16 (absent logs) | 16 of 16 | 16 of 16 | 0 of 144 | 48 of 48 |

BASE 4 of 32; INS 0 of 32; invalid runs 0 of 576 (kinds none; missing runs 0); tool attempts 0, refused 0, executed 0; other-model runs 0; median 3.18 s, tokens in/out/reasoning 283.5/43.5/0.0, cost 0.001081 (ledger).

### openai-theirs, wave 1, 2026-10-07: 576 of 576 rows; complete repeats [1, 2, 3]; read on [1, 2, 3]
Models asked ['gpt-6.1-sol']; reported [].

| Version | False success on its weak-spot logs | True success, passed logs | Receipt score (jobs) | Invalid runs | Three runs agree (logs) |
|---|---|---|---|---|---|
| report | 0 of 16 (fail logs) | 16 of 16 | 16 of 16 | 0 of 144 | 45 of 48 |
| did-the-work | 1 of 16 (absent logs) | 16 of 16 | 15 of 16 | 0 of 144 | 48 of 48 |
| coat-check | 0 of 16 (fail logs) | 16 of 16 | 16 of 16 | 0 of 144 | 48 of 48 |
| coat-check-did | 0 of 16 (absent logs) | 16 of 16 | 16 of 16 | 0 of 144 | 48 of 48 |

BASE 1 of 32; INS 0 of 32; invalid runs 0 of 576 (kinds none; missing runs 0); tool attempts 0, refused 0, executed 0; other-model runs 0; median 4.98 s, tokens in/out/reasoning 9194.5/44.0/0.0, cost None (none reported).

## The seven primary tests (exact two-sided McNemar on false success; each p beside its Holm value)

Holm is taken over the 3 primaries that ran (an interim read says so).

| # | Question | Compared (first against second) | First / second false success | First only / second only | p | Holm | G1 room | G2 extra invalid in the lower set | Job-level sign test (first higher / lower jobs, p) | Reading |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 | Harness effect, Claude | claude-theirs against claude-ours | | | | | | | | **not run** |
| P2 | Harness effect, OpenAI | openai-theirs against openai-ours (three runs) | 1 of 32 / 4 of 32 | 0 / 3 | 0.25 | 0.5 | NOT met | 0 (limit 10) | 0 / 3, p 0.25 | **no room** |
| P3 | Model effect in our harness | openai-ours against claude-ours | | | | | | | | **not run** |
| P4 | Our instruction, Claude, our harness | claude-ours against claude-ours INS | | | | | | | | **not run** |
| P5 | Our instruction, Claude, their harness | claude-theirs against claude-theirs INS | | | | | | | | **not run** |
| P6 | Our instruction, OpenAI, our harness | BASE against INS (three runs) | 4 of 32 / 0 of 32 | 4 / 0 | 0.125 | 0.375 | NOT met | 0 (limit 10) | 4 / 0, p 0.125 | **no room** |
| P7 | Our instruction, OpenAI, their harness | BASE against INS (three runs) | 1 of 32 / 0 of 32 | 1 / 0 | 1 | 1 | NOT met | 0 (limit 10) | 1 / 0, p 1 | **no room** |

A direction is written only for a shown effect. "Not shown" is never "no effect". Counts first.

## Secondary tests (printed, never rescuing a primary)

- S1 openai: harness effect on INS (theirs against ours): 0 of 32 against 0 of 32; first only 0, second only 0, p = 1; job-level sign p = 1.
- S2 openai: harness effect, report on its fail logs (theirs against ours): 0 of 16 against 2 of 16; first only 0, second only 2, p = 0.5; job-level sign p = 0.5.
- S2 openai: harness effect, did-the-work on its absent logs (theirs against ours): 1 of 16 against 2 of 16; first only 0, second only 1, p = 1; job-level sign p = 1.
- S2 openai: harness effect, coat-check on its fail logs (theirs against ours): 0 of 16 against 0 of 16; first only 0, second only 0, p = 1; job-level sign p = 1.
- S2 openai: harness effect, coat-check-did on its absent logs (theirs against ours): 0 of 16 against 0 of 16; first only 0, second only 0, p = 1; job-level sign p = 1.
- S6 openai: invalid runs per log (summed over the four versions), theirs against ours (paired sign test over the 48 logs): theirs_more_invalid_logs 0, ours_more_invalid_logs 0, tied 48, p 1.0, theirs_invalid 0, ours_invalid 0, of_runs 576.
- S7 openai: receipt score, report (theirs 16 of 16, ours 14 of 16): theirs_only 2, ours_only 0, p 0.5.
- S7 openai: receipt score, did-the-work (theirs 15 of 16, ours 14 of 16): theirs_only 1, ours_only 0, p 1.0.
- S7 openai: receipt score, coat-check (theirs 16 of 16, ours 16 of 16): theirs_only 0, ours_only 0, p 1.0.
- S7 openai: receipt score, coat-check-did (theirs 16 of 16, ours 16 of 16): theirs_only 0, ours_only 0, p 1.0.
- S4 openai-ours: instruction effect, report to coat-check on its fail logs: 2 of 16 against 0 of 16; first only 2, second only 0, p = 0.5; job-level sign p = 0.5.
- S5 openai-ours: cost of the ticket, true success on passed logs: report 16 of 16, coat-check 16 of 16: baseline_only 0, fix_only 0, p 1.0.
- S4 openai-ours: instruction effect, did-the-work to coat-check-did on its absent logs: 2 of 16 against 0 of 16; first only 2, second only 0, p = 0.5; job-level sign p = 0.5.
- S5 openai-ours: cost of the ticket, true success on passed logs: did-the-work 16 of 16, coat-check-did 16 of 16: baseline_only 0, fix_only 0, p 1.0.
- S4 openai-theirs: instruction effect, report to coat-check on its fail logs: 0 of 16 against 0 of 16; first only 0, second only 0, p = 1; job-level sign p = 1.
- S5 openai-theirs: cost of the ticket, true success on passed logs: report 16 of 16, coat-check 16 of 16: baseline_only 0, fix_only 0, p 1.0.
- S4 openai-theirs: instruction effect, did-the-work to coat-check-did on its absent logs: 1 of 16 against 0 of 16; first only 1, second only 0, p = 1; job-level sign p = 1.
- S5 openai-theirs: cost of the ticket, true success on passed logs: did-the-work 16 of 16, coat-check-did 16 of 16: baseline_only 0, fix_only 0, p 1.0.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## S10: every reply re-read with the audit's reference rule

None: the sealed rule and the reference rule read every reply alike.

## What this does not settle
- Two models, one tier, one effort; tools off is not how people use these tools; the harness includes the route; 16 invented jobs; power under about 6 of 32 pairs; the coat-check is a bundle; sampling is not identical across harnesses. See DESIGN-A.md.

