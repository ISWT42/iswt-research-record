# Run plan for Test A and Test B

**Status:** draft for the coordinator. Nothing here has been run. Times are estimates (from the screen, S13 and the gate test) and are replaced by the probe's medians before the run seal. Money figures marked **to check** are not confirmed from any local file. No time of day is typed here.
**Design files:** [DESIGN-A.md](DESIGN-A.md), [DESIGN-B.md](DESIGN-B.md).

**Schedule set by the coordinator before sealing (7 Oct).** Joshua's weekly Claude plan meter read 81 percent used, resetting 12 Oct, and section 6 stops the Claude Code arm when 20 percent of the week is left, so the Claude Code arm cannot run before the reset. Wave 1 is the OpenAI pair (openai-ours on the PC, openai-theirs in the box). Wave 2 is the Claude pair, claude-ours and claude-theirs on one UTC date after the reset, so no twin is needed. The rows below are written to this schedule. Test B is not sealed with Test A: its trigger wording and forecasts are set and sealed before any result of the notes test is read.

## 1. What is run, and what it costs

| Arm | Where | Calls | Cash | Allowance |
|---|---|---|---|---|
| claude-ours | PC, through the broker | 576 | **to check** (see 4) | none |
| openai-ours | PC, through the broker | 576 | **to check** (see 4) | none |
| openai-theirs | box, Codex, his ChatGPT plan | 576 | none | about 576 turns; Codex adds roughly 13,000 to 16,000 input tokens per turn (the broker README's figure), mostly cached |
| claude-theirs | box, Claude Code, his Claude plan | 576 (192 per repeat) | none | **to measure** in the probe (section 6) |
| claude-ours twin (only if claude-theirs runs on a later day) | PC | 576 | **to check** | none |
| Probes and canaries | both | about 70 toy calls | small | small |
| **Test A total** | | **2,304** (2,880 with the twin) | cap US$12 | |
| Test B (conditional) | all four cells | **1,728 to 2,304** | cap US$10 | 288 to 576 calls per theirs cell, on the same plans as above |

## 2. What needs Joshua's yes (and what does not)

| # | Ask | Why it is his | When |
|---|---|---|---|
| **Y1** | The models: Claude Sonnet 5.5 and GPT-6.1 Sol; the cheap alternatives (Haiku 4.5, GPT-5.4 nano); no Fable. | Spend and plan use follow from it. | Before any paid probe. |
| **Y2** | The spend cap: **US$12 for Test A's API calls** (probes, both ours cells, the twin) and **US$10 for Test B's**, after the checked price table is shown. The caps are ceilings for his yes, not forecasts of spend. | Every spend needs his yes; list prices and an estimate come first. | Before any paid probe. |
| **Y3** | Using his ChatGPT plan for the Codex cell (576 calls today). The top item in `Workbench\FOR-JOSHUA.md` plans about 2,400 more Sol calls in the box (about 5 hours) on the same plan, so the two share the plan and the box. Suggest one after the other. | His allowance is a fixed pot; empty means stop and report. | Before wave 1. |
| **Y4** | The box start: one paste in Windows Terminal on his PC, like the stack test's. It probes, and only if the probe and canaries pass starts the runs in the background with standard input closed. It ends with a computed "Started HH:MM UTC. Status: ..." line. | Long runs in the box start with his paste. | Wave 1 and wave 2. |
| **Y5** | Claude Code in the box signed in on his Claude plan under the account that runs it (his one action, if not already done), and the yes to use the allowance: **today only if the probe shows repeat 1 is small, otherwise after the 12 Oct weekly reset.** | A sign-in is his; so is the plan's allowance. | Before wave 2. |
| **Y6** (Test B) | The notes text may leave this PC (OpenRouter and, through the tools, the makers); his go once `B-TRIGGER.json` says met. | The notes are his words; the notes test ran locally. | After the notes test is scored. |

**Needs no yes:** setting the forecasts; sealing (FreeTSA and OpenTimestamps); building the runner and scorer; the dry run; scoring; writing the findings. **Nothing is pushed, posted, sent or deployed by this plan.** A page on the site about any result would be a separate yes.

His own forecasts, if he wants to make them, go through his own sealer and nobody reads them before the results.

## 3. Order of work, and what must exist before each step

| Step | What happens | Must exist before | Time (est.) |
|---|---|---|---|
| **S0** | The coordinator sets the p column in both designs, confirms N1 to N3 against the notes test's sealed design, and seals DESIGN-A, DESIGN-B and this file. | The three files. | 15 to 20 min |
| **S1** | One question to Joshua: Y1, Y2, Y3. | S0; the price table below with checked prices (see 4). | his answer |
| **S2** | **Build** (one worker, Sonnet 5.5, the standing-rules block pasted in full into its prompt): `run_matrix.py`, `score_matrix.py`, `test_score_matrix.py`, `SETTINGS.json`, a copy of `prompts.jsonl`, `make_trigger.py` and `leak_check.py` (Test B), an adapted `collect_seal_score.sh`. Reuse: the screen's resumable runner and PAUSE file; its scorer's `read` unchanged; the broker call pattern S8b used (`node broker.mjs run ...`, the "recorded in ledger/..." line on stderr, `providerReportedCostUsd` in `run.json`); the Codex sprint's event reading; the S13 lessons (prompt through a pipe the runner owns, a real JSON parse, one parser for every cell). Paths in Python through Bash use forward slashes; check bytes before saying "fixed". | The design files. The build makes no model call, so it can start while S0 and S1 are still open; S0 must be sealed before the first probe. Needs nothing from Joshua. | 1.5 to 2.5 h |
| **S3** | **Probe and canaries.** Ours: 12 toy calls per cell (slug accepted, `reasoning.effort` low accepted, tokens, cost, upstream provider, ledger line). Codex in the box: version, model and effort as printed, the three canaries, the knob check. Claude Code (when its arm will run): `claude auth status --json` shows logged in and a subscription type, init event shows no tools and `apiKeySource` none, the three canaries, the knob check, tokens and the tool's own cost per call. Output: `PROBE-REPORT.md` and **Addendum 1** (settings as confirmed; every dropped flag named). | S1 for the paid part; Y4 for the box part (or the coordinator's session key if one is open); S2's dry run green; the tools signed in on the account that will run them (the box-hardening plan's agent account if it is in place by then, otherwise the stack test's account, with the folder and homes checked as DESIGN-A says). | 30 to 45 min (+15 for Claude Code) |
| **S4** | **Seal the run files** in `RUN-SHA256.txt`: runner, scorer, its test file, `SETTINGS.json`, Addendum 1, the probe report, the prompts SHA-256, and Test B's two scripts (`make_trigger.py`, `leak_check.py`), which must be sealed before the notes test's results are read. The scorer is sealed here, before the run. | S2 and S3 green; the broker's `verify` clean and its `ledger/index.head` copied. | 10 min |
| **S5** | **Wave 1 (the OpenAI pair).** PC: openai-ours (2 at a time). Box: openai-theirs. Same prompt order in both. After repeat 1, the **room check** (below). | S4; Y3, Y4; the cap set and the spend gate passed; no orphan processes (listed and stopped); the empty neutral folder checked; tool versions recorded. | 1 to 1.5 h |
| **S6** | **Collect, seal, score, seal.** Copy results to the PC, run the broker's `verify` (the ledger chain must be intact) and copy its `ledger/index.head`, seal the results before any count, check the scorer against its seal, run it, seal its output (the screen's `collect_seal_score.sh` pattern, with its times from the clock and the timestamp authority). | S5 ended; all rows present. | 10 to 15 min |
| **S7** | **Interim read of wave 1** ("the direction for today"): the sealed scorer's partial output only. P1, P3, P4 and P5 print "not run" until the Claude cells exist. | S6. | 15 min |
| **S8** | **Wave 2 (the Claude pair, after the 12 Oct reset):** claude-ours on the PC and claude-theirs in the box, on one UTC date. | Y5; the Claude Code probe; the meter reading. | 1 to 1.5 h |
| **S9** | **Final read** and a findings note (counts, then plain meaning). Test B decision (section 7). | S6 for wave 2. | 30 min |

**Room check (the only adaptive rule).** When repeat 1 of a family's ours cell is complete (about a third of the way through its wave), the coordinator counts BASE from repeat 1 alone, per cell (a count, no test). If a family's BASE is under 3 of 32, that family has no room at this model and setting. The coordinator then writes `PAUSE-<cell>` for that family's cells (the Codex cell included), tells Joshua, and proposes the cheap alternative for that family, all its cells run from the start; the first model's repeat 1 stays as "no room" evidence. If both families are under 3, pause everything and ask. The rule uses only the baseline count in an ours cell, never a harness or instruction difference. For the Claude Code arm the same count, taken on the finished claude-ours cell, decides before wave 2 whether the arm uses Sonnet 5.5 or Haiku 4.5.

## 4. Cost: the API arms

Prices come from `ai-broker\prices.json`, which lists only Gemini 3.8 Flash, DeepSeek Flash and Jev. **No Claude or OpenAI model is priced there, so every price below is to check** (the provider's own `usage.cost` is recorded per call by the broker and is what the cap adds up).

**Calls x tokens x price, per API arm.** Every cell is 576 calls: 192 prompts x 3 repeats. Input is 628,590 characters of prompt in all (4 versions x 48 logs x 3 repeats), so 0.157 to 0.196 M tokens at 4.0 to 3.2 characters per token. Output, reasoning included, is estimated at 300 to 800 tokens per call (measured in the probe), so 0.17 to 0.46 M; the ceiling is 2.3 M if every call used the whole 4,000-token cap, which is not expected.

| Arm | Calls | Input (M tokens) | Output, typical (M tokens) | Price per M tokens, in and out | Cost, typical |
|---|---|---|---|---|---|
| claude-ours (Sonnet 5.5) | 576 | 0.157 to 0.196 | 0.17 to 0.46 | **to check** | input x in price + output x out price |
| openai-ours (Sol) | 576 | 0.157 to 0.196 | 0.17 to 0.46 | **to check** | the same |
| claude-ours twin | 576 | the same | the same | **to check** | the same |
| Cheap: Haiku 4.5 ours | 576 | the same | the same | **to check** | the same |
| Cheap: GPT-5.4 nano ours | 576 | the same | the same | **to check** | the same |
| Extension E3: a Gemini twin, priced as Gemini 3.8 Flash (the only confirmed price in `prices.json`; 3.7 Flash is to check) | 576 | the same | the same | 0.75 in, 3.75 out (paid tier, through 2026-12-31) | about US$0.8 to 1.9 |
| Probes | about 70 | small | small | **to check** | well under US$1 |

**Illustrative price points (not quotes), typical case, per cell:**

| Input and output price per M tokens | Per cell, typical |
|---|---|
| US$0.5 and US$3 | about US$0.6 to 1.5 |
| US$3 and US$15 | about US$3.1 to 7.5 |
| US$15 and US$75 | about US$15 to 38 |

Anchors from earlier runs, not prices: the 2 Oct post reports US$0.51 for GPT-6.1 Sol's API rows on these logs (it does not give the call count); S12 capped 972 calls over nine models at US$4; S6 and S7 capped nine-model runs at US$15 and US$12.

**Test A's API total** is claude-ours + openai-ours (+ the twin) + probes. **Test B's** is 2 ours cells x (288 notes + 288 control) calls, with the notes' length added to the notes calls' input.

**The cheap alternative** (Haiku 4.5; GPT-5.4 nano): at illustrative US$1 and US$5 for the Haiku-class cell, about US$1.0 to 2.5 per cell; a nano-class cell about US$0.1. Both together with a twin stay under about US$6. Both have published counts on these 48 logs (the 2 Oct post), so the bare harness can be checked against Kaggle's.

**The spend gate (before any test-item call):** the probe's measured mean cost per call x the calls still to make x 1.25 must be at most 80 percent of the cap. Otherwise the coordinator stops and offers three choices: a higher cap (his yes), the cheap alternative, or fewer repeats for the API cells. **The runner adds up the cost each ledger record reports and stops at the cap**, the way S8b stopped at its US$2.00. HTTP 402 or a credit limit stops the run (the broker's `run` has no special code for it, so the runner reads the error text).

## 5. Time

| Arm | Per call (est.) | Workers | Wall-clock (est.) |
|---|---|---|---|
| claude-ours | 6 to 12 s | 2 | 30 to 60 min |
| openai-ours | 5 to 10 s | 2 | 25 to 50 min |
| openai-theirs | 6 to 10 s (S13: about 8 s at xhigh) | 2 | 30 to 50 min |
| claude-theirs | 6 to 12 s (tool start-up included) | 2 | 30 to 60 min |

Wave 1 runs its two arms side by side: about 1 to 1.5 h. From Joshua's yes to the interim read: about 4 to 5.5 h if nothing breaks, and the build runs while he decides.

## 6. The Claude Code arm: size, estimate, decision

- **Size:** 576 calls in three repeats of 192. It may stop at the end of any repeat.
- **Per-call use is unknown until the probe.** The tool reports its own token counts and a cost figure (what the tokens would cost at list price; on a plan nothing extra is billed). Cache reads and writes are input the plan pays for, so they count.
- **Estimate:** calls x the probe's mean tokens per call (system prompt and environment text, about 0.3 K of prompt, and the reply), set against the usage meter that Joshua reads. At 192 calls that is one repeat; at 576, the full arm.
- **Decision rule:** run repeat 1 (192 calls) today only if the probe's per-call figure x 192 is at most 5 percent of the allowance the meter shows for the week, and Joshua says yes. Otherwise wait for the 12 Oct reset and run all three repeats then. In either case: stop at the first plan-limit message or when the meter shows 20 percent of the week left; **never switch to an API key**, never seek another resource. An incomplete arm is read on the repeats it has (DESIGN-A, reading rule R1 and the "one run" label).
- **Twin:** if claude-theirs runs on a later UTC date, claude-ours runs again that day (576 calls), and the harness effect for Claude is read against that twin.

## 7. Test B steps (only after the notes test is scored)

| Step | What happens | Must exist before |
|---|---|---|
| **B1** | `make_trigger.py` reads the notes test's scored output and writes `B-TRIGGER.json` (N1 to N4, the scored output's SHA-256, `met`). If `met` is false: stop. B0 is scored, B1 to B10 are not. | The notes test's scored and sealed output. |
| **B2** | Joshua says yes to the notes leaving the PC (Y6). His notes already exist; no AI edits them. | B1 met. |
| **B3** | `leak_check.py` (no line of the 48 logs or any ticket appears in the notes); a dry run of every notes prompt through the broker's confidentiality gate; the `--with-notes` path dry-run once more. | B2. |
| **B4** | Seal: notes SHA-256, wrapper SHA-256, trigger, its source's SHA-256, the leak-check output. | B3. |
| **B5** | Run per cell with `--with-notes`: ours cells with their control run beside them; theirs cells per allowance, with the 48-hour control rule (DESIGN-B). Same stop rules and the Test B cap. | B4; Y3 and Y5 again if a tool arm runs. |
| **B6** | Score with the sealed scorer; read with DESIGN-B's summary table. | B5 sealed. |

## 8. What can go wrong, and what to do

| If | Then |
|---|---|
| A canary does not get its sentinel, or a tool item appears | Do not seal. Add the missing `--disable` or deny, run the canary again, record it in Addendum 1. If the tool cannot be turned off, report it and run that cell only as "tools denied by sandbox", labelled, with attempts counted. This answers the open question on the "Agents did what" page (No. 1) about other tools' "read-only" modes. |
| A flag is rejected by the installed tool | Drop it, name it in Addendum 1, keep the canary result as the proof. |
| The knob check shows no effect of `--effort` or `reasoning.effort` | Flag the cell "effort not confirmed" in the design's tables; do not claim matched effort for it. |
| Sonnet 5.5 is not on OpenRouter | Opus 5.5 on both routes (needs a new Y1 and Y2), or the cheap alternative. |
| The tool version changes mid-run (auto-update) | The cell stops (env switches off auto-update, but they are unverified). Re-run that repeat under one version; runs under two versions are never pooled. |
| A model change appears (Claude Code can fall back to another model near a plan limit or on a safeguard event) | The call is flagged and counted separately; three in a cell pause the cell. |
| Many invalid replies in a CLI cell | Pause and ask. It may be a mismatch (the tool answering as an agent), which is itself the finding, but the cost of continuing is his allowance. |
| A leftover process after a stop | List and stop it before any resume. |
| The broker ledger shows a call the runner did not make | Stop and identify it before anything else (a foreign process). |

## 9. After the runs

- **Interim read** (S7) and **final read** (S9) follow DESIGN-A's reading rules and its "what each pattern would mean" table. Counts first, with denominators; plain meaning after; the protocol's own wording: firm where backed, "not shown" where not.
- A findings note goes in the findings folder the same day, as the 6 Oct one did. Sending, posting or publishing any of it is his yes.
- **Fed forward.** The tools-off canary results answer the "other tools' read-only modes" item on the "Agents did what" page (No. 1, "What we don't know yet"). The Kaggle coat-check update (tasks t5 and t6, four models, three runs each, in `kaggle-coat-check-update-2026-10-07`) is the coat-check on Kaggle's harness; if the cheap alternative runs here (Haiku 4.5, GPT-5.4 nano), those ours cells are a third harness for two of those four models on the same 48 logs, to be set beside the update's counts as a descriptive comparison, not a pre-declared test.
