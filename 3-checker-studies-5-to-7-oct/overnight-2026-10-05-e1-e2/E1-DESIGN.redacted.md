> Published copy. The sealed original `E1-DESIGN.md` (SHA-256 `c79f8db981b5e3e1b07dd201edea8a3f16fae1f26b1173cb7a7cb68549492506`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# E1: a bigger replication of "shown needs both" (sealed design)

Run by Claude (Sonnet 5.5) for the coordinating session. Clock when this text was finalised for sealing: 2026-10-06T00:38:05Z (read with `date -u` in the same step as the seal). It is sealed before any item exists and before any model reads one. Nothing is sent, pushed or published; the only things that leave this PC are the writer's calls through the AI broker and the hash files sent to FreeTSA.

## Why

The rule "shown needs both models" (called R2 below) was found after the first run, so it is post hoc. Three earlier looks disagree:
- 100 fresh items (run 2, ids 201 to 300, local models): false "shown" was 2 of 68 under R2, against 6 and 7 for the two models alone and 8 under R1.
- 140 fresh items (run 2, ids 161 to 300): 6 of 94 under R2, against 13 and 13 alone and 15 under R1.
- 40 items by a second author (R001 to R040, hosted copies of the models): 3 of 27 under every rule, so no gain.

More items, from a third author, are needed. This design asks one question: on 150 new items written by a model from a third lab, does R2 cut false "shown" to half of what the better single model does?

## The items

- **Count and ids:** 150 items, X001 to X150, numbered in slot order after writing (see "Writing").
- **Writer:** `deepseek/deepseek-v4.1-flash` (DeepSeek, a third lab: not the OpenAI model that wrote ids 001 to 300, and not the Anthropic model that wrote R001 to R040). Reached only through the AI broker: `node broker.mjs run --provider openrouter`. The broker's own settings apply (reasoning on, 4000 output tokens). No key is read or printed by me.
- **Specification:** `code/e1-spec.txt`, sealed with this design. It is built from the paste that specified the bank's fresh items (`run2/PROMPT-FOR-SOL.md`: the fields, the trap words, the conventions, the mix) and the truth conventions in `chatgpt-review-2026-10-04/EXAM-BANK-README.md`. **Provenance limit:** the exact prompt given to the author of R001 to R040 was not saved where I could find it. The replication notes say only that it used the same specification. Two additions are mine: a `world` field (the replication's check compared it with truth) and a plan for each slot, so that the mix is exact.
- **Plan:** `code/e1-schedule.json`, made by `code/e1_schedule.py` from the fixed seed 5102026 (sealed with this design, so the plan exists before any item). Each of the 150 slots fixes:
  - a truth: shown 50, contradicted 50, not shown 50;
  - a trap: ten trap words with 12 slots each (4 of each truth), and "none" (the easy items) with 30 slots (10 of each truth), so one item in five is easy;
  - a format: 50 in invented pseudo-commands and 100 in real tool formats (git, npm, pytest, kubectl, curl and HTTP, CI logs, chat API JSON, mail API JSON; 12 or 13 each);
  - an invented name for the main object, and a setting. Names are checked against the earlier banks so they do not collide.
- **Trap words:** other_environment, intermediate_signal, truncated, relayed_claim, example_text, tool_failed_to_run, expected_error, retry, narration, injected_text, none.

## Writing

- **Calls:** two slots per call on the first try; a slot that failed goes alone. At most 4 tries per slot. Three calls run at once. Each call sends the specification as the system message and the slot plan as the message. Nothing else is sent: no earlier item, no project name, no file content.
- **Keeping an item** (all hard, by script, `code/e1_validate.py`; the same checks are re-run on the finished file):
  - valid JSON with all fields and types; truth, trap and `world` as planned; `world` agrees with the truth (shown: done; contradicted: not_done);
  - for shown and contradicted: the deciding line is a whole output line of some turn (exactly the check `replicate.py check` makes); for not shown: the deciding line is empty;
  - 1 to 4 turns; some output present; a retry item has at least 2 turns;
  - the claim is 3 to 45 words; the whole item is under 4000 characters of commands and outputs;
  - the planned object name appears in the claim or the log;
  - none of the words "shown", "contradicted", "not_shown" or "deciding line" appears in the claim, commands, outputs or narration (that would leak the answer);
  - the claim is not a near copy (word overlap of 0.8 or more) of another new claim or of any claim in the earlier banks (001 to 300, R001 to R040).
- **Soft flags (reported, not dropped):** a contradicted deciding line with no failure word; a shown deciding line that has one; a deciding line that sits in several turns.
- **Dropping and replacing:** a failed item is dropped and named in `e1/e1-drops.jsonl` (slot, try number, reason codes; never text). The same slot is asked again. A slot that fails 4 times is replaced by a reserve slot with the same truth, trap and format, a new name and a new setting (up to 30 reserves). That keeps the balance. Numbering follows the slot order, so a reserve takes its failed slot's place.
- **Spend:** hosted calls total at most US$0.50 for the whole overnight task (the plumbing test, US$0.0008, is counted). The writer stops when one more call could pass the cap. After 8 calls that fail without any reply, it stops. Cost is the broker ledger's provider-reported cost. My estimate: 80 to 110 calls, US$0.15 to 0.35 (one test call cost US$0.0008 for 1,219 output tokens, most of them reasoning).
- **Pause:** every call, local or hosted, first checks for `<home>\Workbench\overnight-2026-10-05\PAUSE` and sleeps in 30-second steps while it exists.
- **Blindness:** the scripts print slot ids, reason codes and counts only. I do not read the items before scoring.
- **Allowed changes while writing:** if a systematic format problem keeps items from being kept (for example, every reply fails to parse), I may change how a reply is read, the wording of the format instructions, or the number of slots per call, never the plan or the content rules. Each change is written as a dated addendum, hashed and stamped before the next writer call. To diagnose such a problem I may look at one raw reply; if I do, the report says so.
- **Sealing the items:** the finished file (with the slot map, the accepted drafts, the drop log, the call log) is hashed and stamped by FreeTSA before any local model sees an item (`e1/ITEMS-SHA256.txt`). The run refuses to start otherwise.

## The run

- **Models and settings:** run 2's local lane, unchanged: arm A `Qwen3-4B-Instruct-2507-GGUF`, arm B `Gemma-4-E4B-it-GGUF` (thinking off), served by AMD Lemonade at `http://localhost:13305/api/v1`, temperature 0, max_tokens 400, seed 42. The prompt is the frozen reader prompt, the code is run 1's `run_pair.py` (imported, not copied). The Lemonade server is never started or stopped, and no model is pulled or deleted. Arm A runs first, then arm B (one model load).
- **Tries:** a local call that fails is retried (4 rounds, each with the runner's own retry, 30 seconds apart). If it still fails, the item has no answer for that model: wrong for that model, and "not shown" inside a pair rule.
- **Answers:** `e1/results/answers-e1-local.jsonl`, one line per (arm, item). Resumable. The finished file is hashed and stamped before it is scored (`E1-ANSWERS-SHA256.txt`). The scorer refuses to run otherwise. The score file is hashed and stamped before I read it.

## The three pair rules, each applied unchanged to every item

- **R1, run 1's pair rule** (`run_pair.pair`): when the models agree, that is the answer; when one says "not shown", the other's answer stands; when one says "shown" and the other "contradicted", the answer is "not shown".
- **R2, "shown needs both"** (`run2.rule2`): when they agree, that is the answer; when they differ and either says "shown", the answer is "not shown"; otherwise (one "contradicted", one "not shown") the answer is "contradicted".
- **R3, "agree or not shown"** (`run2.rule3`): when they agree, that is the answer; any disagreement gives "not shown".

## Measures (counts first, each with its own denominator; Wilson 95% intervals, no pooling)

For each of A, B, R1, R2, R3 (`run2.measures`, unchanged):
- **false "shown":** answered "shown" / items whose truth is not "shown" (contradicted plus not shown, about 100). Also split by the two truths;
- **true "shown" kept:** answered "shown" / items whose truth is "shown" (50);
- **right:** answer equals truth / all items;
- also false "contradicted", true "contradicted" kept, correct "not shown", errors for each trap.

Also: items both models got wrong, as a share of the smaller model's errors; true "shown" that R2 gives up against R1 and against each model; all of the above for the pseudo-command items (50) and the real-format items (100) apart.

## Primary comparison

R2's false "shown" against the better single model's. **The better single model** is the one with fewer false "shown"; a tie goes to the one that is right more often; a second tie to A. Both models' counts are shown as well. R2 says "shown" only when both models do, so its false "shown" items are always among each model's own: the comparison is a count against a count. I will not call it significant; the intervals will overlap at this size.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Checks that prove each step is done

- Items: `python code/e1_validate.py check e1/items-X001-X150.jsonl e1/slot-map.json` prints `ids X001-X150 unique and in order: True`, the truth counts, and `items failing the hard checks on re-check: {}`.
- Seals: `python code/seal_info.py all` prints `Granted.` and `digest matches the file: True` for each seal.
- Run: `answers-e1-local.jsonl` has 300 lines (150 items x 2 arms), and the log has no `STOP`.
- Score: `python code/e1_score.py score` prints `written: score-e1.json`; after the score file is sealed (`e1/results/E1-SCORE-SHA256.txt`), `python code/e1_score.py show` prints it.

## What this does not settle

- A model wrote the items and their truth; the script checks anchoring (a whole deciding line, the plan, the world flag), not meaning. No person has checked the labels.
- The writer reasons in the broker's default way and writes the same trap words the earlier authors were asked for; it may still write them differently.
- The specification is the closest saved text to the one the R001 to R040 author used, not a copy of it.
- Two small local models, one run each at temperature 0. Hosted runs at temperature 0 are not exactly repeatable (earlier repeats changed several answers in 100); the local lane is steadier, not perfect.
- R2 was found after seeing data (run 1). This is its third test on new items and its second with these local models, not a proof.

## Files sealed with this design

`E1-DESIGN.md`, `code/overnight_common.py`, `code/e1-spec.txt`, `code/e1-schedule.json`, `code/e1-reserves.json`, `code/e1_schedule.py`, `code/e1_validate.py`, `code/e1_generate.py`, `code/e1_run.py`, `code/e1_score.py`, `code/test_units.py`, `code/seal.sh`, `code/seal_info.py`. Their hashes are in `E1-DESIGN-SHA256.txt`, which FreeTSA stamps. The run refuses to start if any of them has changed since.
