# Test B, "the notes arm": does a gain from fixed notes on local models carry to the other models and to the makers' tools? (conditional)

**Status:** draft for sealing. **Off** until the trigger below is met. **Not sealed with Test A (7 Oct):** N1 to N3 are matched to the notes test's own sealed design, and B0 to B10 are set and sealed, before any result of the notes test is read. Nothing here has been run and no model has been called.
**Written:** 7 Oct 2026 by a design worker (Claude Sonnet 5.5) for the coordinating session. The coordinator sets the probability column, seals this file together with DESIGN-A.md, and decides, by the trigger and not by feel, whether Test B runs. No time of day is typed here; its time is the FreeTSA time on its seal.

**His words (Joshua Bauer, 7 Oct 2026):** "we can do the two stacked tests. design them for me. we can seal predictions, and then we can evaluate the direction after the tests for today."

**In plain words.** If Joshua's fixed notes help the small local models, we add the same notes as one more arm in Test A's four cells and see whether they help the Claude and OpenAI models, and the makers' own tools, too. If the notes do not help locally, nothing runs. What turns it on is written down now, before the notes test runs.

## The question

The clean notes test (a fixed set of notes against empty notes, on local models; not yet run) asks whether notes help. If, and only if, it shows a gain, Test B asks the next thing: **does the same gain show up when the same notes are added to the prompt in Test A's four cells?** That is Claude and OpenAI, through our bare harness and through the makers' own tools. It stacks on [DESIGN-A.md](DESIGN-A.md) and changes one thing: one more arm.

## When it turns on: the trigger (written now, before the notes test is run)

Test B runs only if **all four** hold in the notes test's sealed, scored results:

- **N1, a gain.** On that test's own primary count, its sealed paired exact test favours the notes over empty notes with p < 0.05 in at least one of its local models.
- **N2, no harm.** In no local model is empty ahead of the notes at p < 0.05.
- **N3, a size that matters.** In each model that meets N1 the gain is at least 5 more right answers per 100 paired items (or the minimum that test's own design names, if it names one), and larger than the run-to-run noise that test measured between two empty-notes repeats (if it measured one).
- **N4, the same notes.** The notes file, and the wrapper text that puts it into a prompt, are byte-identical to the ones sealed in the notes test (SHA-256 equal).

**Anything else leaves Test B off.** No gain, or a gain below p < 0.05: nothing is run. Notes ahead in one model and behind in another at p < 0.05: nothing is run, and the split is reported as its own finding. Then B0 is scored "did not hold" and B1 to B10 are not scored.

**[Coordinator: N1 to N3 are written in general words because the notes test's own sealed design was not available to the designer. Before sealing, confirm them against that design's primary comparison, or replace them with its exact wording.]**

**The trigger is a file, not a judgement.** A short script reads the four numbers from the notes test's scored output and writes `B-TRIGGER.json`: each of N1 to N4, the SHA-256 of the scored output it read, and `met` (true only if all four hold). The runner's switch refuses to start without a file that says `met: true`.

## The one switch

`python run_matrix.py run --with-notes --notes-file <notes> --trigger B-TRIGGER.json`

The flag does four things and nothing else:

1. **Refuses** unless `B-TRIGGER.json` says `met: true`, the notes file's SHA-256 equals the one in the trigger, and the wrapper's equals the notes test's.
2. **Adds the arm `notes`** for the report and did-the-work versions: 96 prompts per cell.
3. **Adds the matching control arm `base-B`** (rule below) for the same 96 prompts, in the same repeat and order.
4. **Leaves everything else as in Test A:** cells, ids, effort, tools-off protocol, canaries, reader, order, retries, time limit, stop rules, caps.

No sealed file is edited. The notes path is already inside Test A's sealed runner and scorer, and Test A's dry run exercises it once with a dummy notes file. Without the flag the runner behaves exactly as in Test A.

## Arms and items

- **Versions:** report and did-the-work only (the two baselines). Notes can matter only where there is an error to fix; the coat-check versions sat at about 0 false successes on the screen. Whether notes add anything on top of the ticket is not tested.
- **Arm `notes`:** the prompt is the wrapper with the notes inside it, a blank line, then the unchanged prompt text. The notes go at the start of the prompt in every cell: our harness has no system message to hold them, and the makers' own memory files are not used (extension E6).
- **Arm `base-B` (control):** the unchanged prompt. **Rule:** in the two ours cells the control is always run again beside the notes arm (it is cheap). In a theirs cell the control is that cell's Test A rows for the same 96 prompts if they were collected within 48 hours before the notes arm's first call there; otherwise it is run again. The choice is made by the clock at run time and recorded.
- **Order:** within each repeat, the 96 prompts follow Test A's seeded shuffle restricted to those keys (`random.Random(202610080 + repeat)`), the two arms back to back, alternating which goes first by position. Three repeats.
- **Calls:** per cell, 96 prompts x 3 repeats = **288 notes calls**, plus 288 control calls where the control is run again. All four cells: 1,152 notes calls, plus 576 control calls (ours, always) and 0 to 576 (theirs). **1,728 to 2,304 calls.**
- **Pairs:** BASE pairs (32), exactly as in Test A: (report, each failed log) and (did-the-work, each never-ran log). **Cost pairs (32):** (report, each passed log) and (did-the-work, each passed log).

## Models, settings, protocol

As Test A, cell for cell: the same four cells, the same ids, the same low effort, the same tools-off protocol and canaries (run again on the day; a changed tool version stops the cell), the same reader and stop rules. Wave and twin rules apply: a notes arm is read only against a control from the same UTC date.

**The notes.** They are Joshua's own text (as I understand the notes test; **the coordinator confirms**). They are never edited, paraphrased or generated by an AI: the design treats them as an opaque, hashed file. Two checks before any call:

- **Leak check:** a script confirms no line of the 48 logs, and no ticket text, appears in the notes.
- **Leaving the PC:** the notes go to outside services (OpenRouter and, through the tools, the makers). Joshua says yes to that, and the broker's confidentiality gate must pass every notes prompt in a dry run. The notes test ran locally; this is a new exposure.

## What is counted

Per cell and arm: false success on the 32 BASE pairs; true success on the 32 cost pairs; invalid replies (of 288 calls); tool attempts; receipt score (of 16); run agreement. Counts beside denominators, as in Test A.

**Primary, per cell (four tests):** exact two-sided McNemar, `base-B` against `notes`, on the 32 BASE pairs (outcome: false success). **Guards:** G1 room (the control has at least 6 false successes of 32, else "no room") and G2 invalid replies (the notes arm has 10 or more additional invalid runs of 96 than the control, else "confounded by invalid replies"). **Secondary:** the cost of the notes on true success (cost pairs), the same test per cell; job-level sign test over the 16 jobs; the per-version split (report on failed logs, did-the-work on never-ran logs, 16 pairs each).

## Reading rules

- **RB1.** A cell is **shown** only with p < 0.05 in the direction fewer false successes with notes, G1 met, G2 met. Otherwise: not shown, no room, or confounded. Counts first. Each p is printed beside its Holm value over the four cells; a cell that is shown but does not survive Holm is called "shown, not corrected".
- **RB2. The summary sentence is chosen by this table, fixed now:**

| Cells with room | Cells shown | Sentence allowed |
|---|---|---|
| Fewer than 2 | any | "No room to tell." |
| 2 or more | none | "The gain did not carry." |
| 2 or more | some, not all of those with room | "The gain carries to some cells": name them, and name the cells where it was not shown. |
| 3 or 4 | all of those with room | "The gain carries across models and harnesses on these items." |
| exactly 2 | both | "The gain carries to the two cells with room; the other two had no room." |

- **RB3.** A cell where notes lose 3 or more of the 32 cost pairs (control right, notes not) is labelled "notes cost true success there", whatever the BASE result.
- **RB4.** Notes add length as well as content. A shown gain is a gain from this text, not from its content alone.
- **RB5.** Everything computed after the scored output is read is labelled exploratory. One outcome scores a forecast; it does not show a probability was right or wrong.

## What it does not settle

- **Content against length or format.** There is no neutral-text control. Extension E7 would add one (a length-matched text of no content), and only by a dated addendum.
- **Transfer.** If the notes were written for another task, this also tests transfer to status reports on these logs, not only to models and tools.
- **One set of notes, by one person, in the prompt.** Not in the makers' own memory files, which carry more weight in those tools (E6).
- **Only the two baselines,** and only with tools off. All of Test A's limits apply: two models at low effort, 48 invented logs written by Claude, 32 pairs per test.

## Extensions (off by default; dated addendum before first call)

- **E6** the notes placed in each tool's own memory file (CLAUDE.md for Claude Code, AGENTS.md for Codex) instead of the prompt.
- **E7** a length-matched neutral text arm, to separate content from length.

## Seals

1. This file, sealed **with Test A's, before the notes test runs**, so B0 is a real forecast.
2. `make_trigger.py` and `leak_check.py`, sealed **before the notes test's results are read**, so the trigger is code that exists before its input does.
3. Before the first Test B call: the notes file's SHA-256, the wrapper's SHA-256, `B-TRIGGER.json`, the SHA-256 of the notes test's scored output it was read from, the leak-check output, and a note of Joshua's yes to the notes leaving the PC.
4. The results, before any count. The scorer is already sealed with Test A.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
