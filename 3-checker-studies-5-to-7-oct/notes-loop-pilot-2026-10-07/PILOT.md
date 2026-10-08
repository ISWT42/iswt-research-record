# The notes-loop pilot: how to run it

Private. Everything stays in this folder (`<home>\Private\claims\2026-10-07-notes-loop-pilot`). The design is
`<home>\Private\ClaudeHandoff\specs\RSI-ONE-SESSION-PLAN-2026-10-05.md` (sections 4.2 to 4.8, 4.11, 4.12, 4.17, Appendices A and B);
this file is only the operating manual. Nothing here is evidence: the test items 161 to 280 were scored before, so every number is labelled
**PILOT, NOT FRESH**. The pilot checks the machinery, measures the noise floor, and may set four parameters (section 6). It changes nothing else.

The checker is `google/gemma-4-26b-a4b-it@Darkbloom` through the AI broker (`openrouter-plain`: temperature 0, seed 42, max_tokens 400, reasoning
off, `data_collection: deny`; every call is in the broker's ledger). The improver is the same model and pin through the new `openrouter-plain-long`
(max_tokens 1200, E1). The harness makes no call by itself except through the broker, with two exceptions that are their own routes: **section 9** runs the same pilot on the owner's
Codex subscription inside the experiment box (`--provider codex-box`), with no broker and no spend, and **section 10** runs it on a small local model served by Lemonade on this PC
(`--provider lemonade`), with no broker, no hosted model and no spend; section 10 also describes a fresh bank for the test items (`--bank`), which any route can use. Everything else in
this file is about the broker route unless it says otherwise.
Every test and rehearsal in this folder used the fake provider, a fake box, a fake Lemonade server or a loopback fake host on
127.0.0.1, with one exception: on 7 Oct a mistake in the build's own mutation testing made a test send 129 calls with toy items through the real broker (section 8). No bank item
text left this folder then, and tripwires now stop any test from reaching the real broker, the real box or the real Lemonade server.

## 1. The order

Seal, probe, A, B. Commands are run from the build folder (`cd <home>\Private\claims\2026-10-07-notes-loop-pilot`). `python` is 3.14.
A run's name is the same for all its commands (`pilot-1`); the probe has its own (`probe-1`).

| Step | Command | What must be true afterwards |
|---|---|---|
| 0a. E1: put the long mode into the broker | in `<home>\Desktop\Moonshots\ai-broker`: `git apply --check <build>\patches\E1-openrouter-plain-long.patch`, then `git apply ...`, then `node --test tests/adapters.test.mjs`, then **commit** the five patched files (see `patches\E1-NOTE.md`) | the broker's adapter tests pass; `git status` in the broker shows none of the five files |
| 0b. E3: extend the broker's `confidential-markers.txt` with the project's terms | edit the broker file (the harness never prints the phrases) | step 1 still passes E3: the Appendix A prompts, the labels of the improver's user part, every item's checker prompt and every item's case text hold no marker. An empty marker list FAILS E3 (it would prove nothing) |
| 1. Pre-flight | `python pilot.py preflight --stage seal` | E1, E2, E3, E5, E7, E8 PASS; E4 and E6 TODO. Prints READY TO SEAL |
| 2. Commit | `git add -A` and `git -c user.name=ISWT42 -c user.email=iswt42@local commit -m "..."` (no trailers) | `git status` is clean for `notesloop`, `prompts`, `data`, `pilot.py` (the seal refuses otherwise) |
| 3. Seal 1 (E6) | `python pilot.py manifest write` | prints the SHA-256 of `MANIFEST.json` (also in `MANIFEST-SHA256.txt`). Stamp it (FreeTSA, OpenTimestamps). A second `manifest write` is refused unless `--replace`, which keeps the old seal under its own hash |
| 4. Probe (E4): 5 calls | `python pilot.py probe --run probe-1` | `PROBE PASSED`: each call answered by Darkbloom, reasoning off, not cut off, right shape (if the ledger gives no token counts or finish reasons the line says which checks were NOT made); written to `runs\probe-1\probe.json` with the seal's hash. A probe made with the fake provider, without a seal, or under an earlier seal does not count for E4 |
| 5. Phase A, study run: 129 calls | `python pilot.py phase-a study --run pilot-1` | prints the Empty counts on the study pool; writes `runs\pilot-1\digest\study-empty-digest.txt` (holds item text: read it, never paste it into a prompt) |
| 6. Write the two notes files | read the digest; write `notes\model-hand.txt` (the coordinating session, labelled as a model) and `notes\filler.txt` (same format and size, restating task format facts, no advice); delete the PLACEHOLDER line in each | `python pilot.py notes-check` prints `notes check: OK` (valid through the applier, not empty, sizes, no six-word copy from any bank item). `manifest write-notes` does not repeat the copy audit: run `notes-check` first |
| 7. Seal 2 | `python pilot.py manifest write-notes --run pilot-1` | prints its SHA-256 (stamp it). Refused unless: the core seal holds, `pilot-1` is a real run with its 129 study calls in the log, both notes files load through the applier and hold notes, and the digest files exist. It records the files, the digest, the core seal's hash and whether each notes file is newer than the digest |
| 8. Phase A, fixed arms: 1,080 calls | `python pilot.py phase-a fixed --run pilot-1` | prints the arms' note sizes and the call count; no scores |
| 9. Read phase A | `python pilot.py results --run pilot-1` | the floor and pilot rule 1 (section 6). Decide whether to go on |
| 10. Phase B: One shot (361 calls) and the loops (664 to 864) | `python pilot.py phase-b --run pilot-1` (add `--wait-for-stamp` to stamp the chain heads round by round, section 5) | "phase B done"; chain files and heads under `runs\pilot-1\chain` |
| 11. Checks, results and chart | `python pilot.py chain-check --run pilot-1`, then `results --run pilot-1` and `chart --run pilot-1` | chain intact; text, JSON, `PILOT-<time>-chart.svg`, `-chart.txt`, `-table.csv`; each file's SHA-256 is printed. Files carry the UTC time in their names and are never written over |

Before step 5 you may run `python pilot.py preflight --stage run` once more (add `--skip-tests` to leave out the three minutes of unit tests, which then stay TODO):
with the probe passed under the seal in force and the seal written it prints ALL GREEN. To see the whole machine work with no hosted model:
`python pilot.py rehearse` (the fake provider, a few seconds, writes `runs\rehearsal-1`; its results and chart say REHEARSAL at the top, and it checks nothing about the pin or the seal).

Paste-ready, PowerShell, in the build folder (the numeral in `pilot-1` is the digit one):

```
python pilot.py preflight --stage seal
python pilot.py manifest write
python pilot.py probe --run probe-1
python pilot.py phase-a study --run pilot-1
python pilot.py notes-check
python pilot.py manifest write-notes --run pilot-1
python pilot.py phase-a fixed --run pilot-1
python pilot.py results --run pilot-1
python pilot.py phase-b --run pilot-1
python pilot.py chain-check --run pilot-1
python pilot.py results --run pilot-1
python pilot.py chart --run pilot-1
```

Exit codes of every command: 0 done (or the check passed), 1 a stop rule fired or a check failed (the message says whether the same command can be run again to
continue), 2 a usage problem (`error: ...`, nothing was run), 130 Ctrl+C.

## 2. Expected calls and cost (`python pilot.py counts` prints these from the plan)

| Part | Calls |
|---|---|
| probe | 5 |
| phase A, study run (Empty, 129 study items) | 129 |
| phase A, fixed arms (Empty, Filler, Model-hand, 3 repeats, 120 test items) | 1,080 |
| phase B, One shot (1 improver call, then 3 repeats on 120 items) | 361 |
| phase B, the loops (A1, A2 Own notes; S1, S2 Own notes + own method; 3 rounds; round 1 shared by each pair) | 664 to 864 (864 when every round makes an update) |
| all | 2,234 to 2,434, plus the probe |

Fifteen of them are long-mode calls (11 improver, 4 method rewrites). A checker call cost US$0.0001 to 0.00012 on 5 Oct; improver calls carry
longer prompts and cost several times that. Estimate for the whole pilot: **US$0.23 to 0.31**, cap **US$1.00** (`--cap-usd`). At the throughput of
5 Oct (0.5 to 1.5 calls per second) that is 30 to 80 minutes of calls; a phase prints a progress line every 100 calls (counts, cost and speed only).

## 3. What stops the run by itself

Every stop inside a run is written to `events.jsonl` with a short code (a refusal before the run exists, such as the broker environment variables below, only prints), prints `STOPPED: <reason>`, and (except the verdicts below) leaves the run resumable: run the same
command again and the calls already made are read from `calls.jsonl`, never repeated ("nothing is re-run to change a result").

| Code | What happened | Then |
|---|---|---|
| `halt` | a file named `HALT` (or `HALT.txt`, which is what Notepad makes when Explorer hides the extension) in `runs\<name>\` or in this folder, checked before every call, every retry and while waiting for a stamp (the kill switch; one in this folder stops every run and makes E8 fail) | delete it and run the command again |
| `cap` | the spend cap (`--cap-usd`, default US$1.00), counted from the ledger's provider-reported costs (the codex-box route spends nothing per call and has no spend cap) | raise the cap, or stop |
| `call_cap` | the call cap: `--call-cap` tries (retries included) in one command, 3,000 by default on the codex-box and lemonade routes and none on the others (sections 9 and 10) | run the same command again (the count starts from zero, the calls made are read from the log), or raise it |
| `outage` | 10 calls in a row with no answer (an outage, not a result); or, in phase B, an improver or method call that got no answer after its retries (the run stops before that step is sealed in the chain, so nothing has to be unpicked; a checker call with no answer is counted wrong, as the design says) | fix it, resume with `--rerun-no-answer` |
| `pin` | a call answered by a provider other than the pin (also: a logged call that was) | nothing is retried. Read the ledger entry named in the log; resume with `--rerun-no-answer` asks those calls again |
| `unknown_provider` | 5 answered calls in a row whose ledger entry names no provider, so the pin cannot be checked | read the ledger entries before going on |
| `gate` | the broker refused a prompt (confidentiality gate, exit 3) | a marker is in a prompt: fix the list or the prompt |
| `usage` | the broker does not know the mode (exit 2: the E1 patch is not applied), or `BROKER_CONFIG_DIR` / `BROKER_NO_KEYSTORE` is set in the environment (see below); on the codex-box route: no `ssh` program, no key file at the sealed path, a prompt codex cannot take as one argument, or `NOTESLOOP_NO_REAL_BOX` set; on the lemonade route: a vendored client that is not the recorded one, a server address that is not this PC, or `NOTESLOOP_NO_REAL_LEMONADE` set | fix it and run again |
| `seal` | the seal does not hold (checked at the start of every command, before One shot, before every round, after every wait for a stamp, after every phase, and every 100 calls counted across the whole command), or the run began under another core seal, or a seal was replaced while a command ran | `manifest check` shows what changed. A run keeps the seal it began under: after a deliberate new seal, start a new run |
| `inputs_changed` | a call is in the log with a different prompt than the one now built (code, notes or plan changed) | a verdict on the run: start a new run |
| `inputs` | the bank, the excluded-ids file or `data\pilot-blocks.json` is not the sealed one (checked before every command) | put the sealed file back |
| `invalid_improver` | phase B: more than 25% of a round's improver outputs invalid (checked when the round has at least 4 outputs) | a verdict on answers already in the log (the same command stops again at once): decide what to change, start a new run |
| `v3_gate` | phase B: three V3 lines in a row refused by the sealed word list | same |
| `chain` | the chain files do not match what a replay rebuilds (the code, the notes or the seal changed, or `--rerun-no-answer` changed an answer an earlier round had used) | a written (and perhaps stamped) chain entry is never rewritten: start a new run |
| `interrupt` | Ctrl+C: calls in flight finish and are logged, nothing queued is called | run the same command again |
| `worker_error`, `judge_error` | an unexpected error in a worker, or in reading a paid reply (the reply stays in the log) | read the message; run again after the cause is fixed |

A failed call is retried twice (after waits of 2 s and 6 s, so a rate-limited host is not hit again at once), then recorded as "no answer" and counted as wrong.
A call that the broker does not answer within 180 seconds is stopped and counts as a failed try. Not automatic: the design's "throughput under 0.4 calls per second for 30
minutes" rule, which drops the core run to its next priority (the pilot has none; the progress lines show the speed; stop with `HALT`).

**One command at a time on a run.** Each command that makes calls takes `runs\<name>\LOCK` (its process id, command and start time), keeps the file open while it runs
(Windows will not let another process delete an open file), and releases it when it ends, however it ends. A second command on the same run says
`another command is working on <run>: pid N` (exit 2), or `has just taken the lock ... wait a moment` if it arrives in the same instant. A lock whose process is gone is taken
over; `orphans` lists it as stale.

**Leftovers at the start.** A real command (not a rehearsal) looks at the process table when it starts and refuses (exit 2) while broker calls of this pilot are still running with
no command behind them: after a hard kill they finish later, reach the broker's ledger and no log, and the spend cap does not count them (design 4.11). Run
`python pilot.py orphans`, then `--stop`, then the command again. A process table that cannot be read is only a warning.

**The broker's own environment.** `BROKER_CONFIG_DIR` and `BROKER_NO_KEYSTORE` make the broker read its settings or its keys from somewhere other than its own folder, which the seal
does not cover, so a real run refuses to start with either set (`STOPPED: ... is set in the environment`). `BROKER_LEDGER_DIR` may be set: the harness reads each call's ledger entry from
it, and the run's first event records it.

If a run was killed: `python pilot.py orphans` lists this pilot's own leftovers and which are orphans (it exits 1 when it lists anything, a run that is going included); `--stop` stops the orphaned broker calls and removes stale locks and old prompt
folders; `--stop-all` also stops a run that is still going. "This pilot's own" is decided by identity, not by wording: a process whose id is in a `runs\<name>\LOCK`, whose command line holds `pilot.py` as a whole word (not
`autopilot.py`) and which was started no later than the lock was written (so a process id that Windows gave to another program after the run died is not taken for it); a `node`
process running THIS broker's `broker.mjs` with the `run` verb and a lane that starts with `nl-pilot-`; a lock that is empty, or whose process is gone, or whose id now belongs to
another program (`--stop` removes it; `--stop-all` also removes the locks of the runs it stops); a `notesloop-*` prompt folder in the temp folder older than four minutes. Nothing else is listed or stopped (not the Lemonade run, not another project's broker calls, not a script that merely names this folder), and this
command's own process, its shell and what it started are never touched.

## 4. Where things are

| Path | What |
|---|---|
| `notesloop\` | the harness. `config.py` holds every sealed constant; `instrument.py`, `prompts.py`, `validators.py` are the instrument; `codexbox.py` is the codex-box route (section 9); `lemonade.py` is the lemonade route and `lemonade_client.py` the Receipt Pair client it asks through, a byte for byte copy (section 10); `bank.py` and `plan.py` also hold the fresh bank for the test items (section 10) |
| `prompts\` | the Appendix A texts, run 3's CERTAINTY and UNSAFE, hashed byte for byte |
| `data\pilot-blocks.json` | ids only: the study pool, the three test blocks, the two loop partitions (derived from the sealed bank and seeds; checked on every run) |
| `notes\filler.txt`, `notes\model-hand.txt` | yours to fill (step 6) |
| `patches\` | the E1 broker patch and its note |
| `runs\<name>\` | one run: `calls.jsonl` (every call with its tries, reply and judgment), `events.jsonl`, `RUN.json` (provider kind, pin, newline), `LOCK` (while a command runs), `digest\`, `chain\`, `states\`, `results\`, `chart\`, `probe.json`. **Holds item text; never committed** (`.gitignore`) |
| `MANIFEST.json`, `MANIFEST-NOTES.json` | the two seals; `*-SHA256.txt` beside them; an earlier seal replaced with `--replace` is kept as `MANIFEST.<8 hex of its hash>.json` |
| `tests\` | 792 tests (`python -m unittest discover -s tests -t .`, about four minutes): 485 of the broker build, 123 for the codex-box route (`test_codexbox*.py`, `box.py`, `codexpilot.py`), 125 for the lemonade route (`test_lemonade*.py`, `lemon.py`, `lemonpilot.py`), 59 for the fresh bank (`test_bank_option.py`, `test_bank_run.py`, `freshbank.py`) |

The commands: `blocks`, `phase-a study|fixed`, `phase-b`, `notes-check`, `manifest write|write-notes|check`, `bank-join`, `counts`, `status`, `chain-check`, `results`, `chart`,
`orphans`, `smoke`, `probe`, `preflight`, `rehearse`. Every one has `--help`. A rehearsal must be named `rehearsal-...` and a real run must not be, so fake answers can never
share a log with real ones; `RUN.json` fixes a run's provider kind and its newline for its whole life.

## 5. The seals and the chain

* **Seal 1** (`manifest write`) hashes every fixed file: the harness code (every file below `notesloop\`, `prompts\`, `data\`, every top-level `.py`), the sealed bank and its
  excluded-ids file, run 3's `run3.py`, the frozen reader and its two source copies, the design file, and the broker: `broker.mjs`, every file below its `lib\` (so a new file
  there is a problem too), its marker list (hashed, never printed), and the parts of `broker.config.json` and `providers.json` that decide where a call goes and under what terms
  (the OpenRouter endpoint, the name of the key variable (never its value), the timeout, the terms of the two modes). Compiled caches (`__pycache__`) and the files the
  operating system adds (`Thumbs.db`, `desktop.ini`) are left out; a `.pyc` anywhere else is sealed, because Python imports a sourceless module from it. Tests, patches and docs
  are hashed too but only warn if they change. It refuses to seal when git cannot be asked or fixed files differ from the last commit (`--allow-dirty` overrides, and the git head is recorded), and when a seal
  already exists (`--replace`). It records the python and node versions and the newline on the wire.
* **Seal 2** (`manifest write-notes`) records the two filled notes files and the digest. It exists because the model-hand set is written from the study run's digest, so it cannot
  exist at seal 1. It is bound to one run and to the core seal it was made against.
* A mismatch stops the next step ("a mismatch stops the run", 4.2). `python pilot.py manifest check [--notes]` shows what changed. A real run records the core seal's hash in
  its first event; every later command of that run must find the same one.
* **Chain.** Each loop writes one hashed entry per round to `chain\<loop>.jsonl` (variables, edits, method text, evidence ids, the improver's reply hash and the
  hash of the entry before) and, after every round, `chain\HEADS-r<k>.txt` (`<loop> <seq> <hash>` per line; `HEADS-r0.txt` is the One shot state). The heads are
  written **before** that round's test block is run (One shot's before its evaluation calls). Stamping is yours. With `--wait-for-stamp` the run pauses after writing a
  round's heads until the file `chain\STAMPED-r<k>` exists (create it after stamping, for example `echo ok> runs\pilot-1\chain\STAMPED-r1`; `STAMPED-r0` for One shot; `STAMPED-r1.txt` works too);
  `HALT` still works while it waits, and the seal is checked again once the wait is over. Without the option the run does not wait (the pilot is not evidence; the chain still
  records every state). `chain-check` verifies every hash and link, that each line of each heads file names the entry it should, and that every sealed state has its head written
  (`HEADS-r<k>.txt` for the round-k entries, `HEADS-r0.txt` for One shot); a run that does not exist is a usage error.
* No test score ever returns to a loop (tested: `tests\test_phase_b.py`), and the progress lines carry counts, cost and speed only.

## 6. Reading the pilot, and the four rules it may set (4.17)

`results` prints counts, each with its own denominator, no item text and no item id: the three-block right counts of every fixed arm by repeat, the noise floor
f per 40-item block (the larger of 2 and the 90th percentile of the differences between repeats; for all fixed arms, and for Empty alone), secondary counts
(false "shown", true "shown" kept, false "contradicted", correct "not shown", sent to a person, no answer), settle proposals, what each loop saw on the study
side (right, false "shown", the improver's schema check, edits applied and dropped), the diagonal (each round's new notes on that round's block, against Empty's first run, with fixed and broken), the
improver's schema-valid share, the by-trap tables (right, and false "shown"), and Appendix D's table. A gain at or under f is noise (the design says "the 90th percentile" and names no definition: f is read from the interpolated one, as numpy and Excel compute it; the
nearest-rank one is printed beside it, and the two can differ by a whole count, for example 2.4 against 4). A rule read on part of a run (a study run that stopped early,
a loop that has not finished) says `PARTIAL` under the rules. Model-hand is a set written by a model, not a
person, and is labelled so everywhere. A run made with the fake provider says REHEARSAL at the top of its results text and its chart (and `provider_kind` fake in the JSON). The diagonal compares each loop's block with Empty's first run
from phase A, which was made earlier: a change in the provider between the two is not separated from the effect of the notes (the text says so).

| Rule | Condition | If it holds / if not |
|---|---|---|
| 1 | the Empty three-repeat floor per 40-item block is at most 3 | Gemma@Darkbloom stays primary / re-decide among Qwen, the local lane and pooled-only claims |
| 2 | at least 70% of improver outputs are schema-valid | keep edits as lines / switch to whole-slot replacement with the same caps and re-test one loop |
| 3 | at least 3 mistakes per study block under Empty | keep blocks of 25 and 5 rounds / use blocks of 30 and 4 rounds |
| 4 | no hash mismatch and no gate bypass | go on / stop everything |

The results script prints each condition beside its counts and says whether it holds; what to do is the coordinator's decision. "Schema-valid" is read as
the design's schema: the reply parses, has an `ops` list, and every edit has a known variable, operation, index and line. Edits dropped for content
(a trap word out of place, a digit in V4, a six-word copy, an unsafe V3 line) are counted by reason beside it, with two stricter readings (at least one
valid edit; every edit applied). The pilot's gains do not gate the core run; they only gate Part 2.

How each rule is read: **rule 1** from the repeats of Empty alone (9 differences). **Rule 3** from the study run's Empty answers (129 items; mistakes scaled to a block of 25),
with the two round-1 study blocks printed beside it. **Rule 4** from facts, not from the absence of a message: the answering provider of every call in the log's whole history
(a mismatch that was later asked again still counts), answers whose ledger entry named no provider, the seal each command ran under (every real command must have one, all the same, and
the seal must still hold when `results` is run), the stop codes `pin`, `unknown_provider`, `gate`, `seal`, `inputs_changed`, `inputs` (a bank or plan that is not the sealed one), `chain` and `usage`, every chain file and heads file, and every V3 line of
every state and edit checked against the word list again. A run folder without `RUN.json` or without `events.jsonl` cannot be read for it, and the rule is then shown as not holding
(`CANNOT BE READ`). A rehearsal prints these facts but has no seal or pin to check.

The CSV (Appendix D's table) has Appendix D's columns first, in its order, then `own_loops` and `own_sent_to_person_denominator`: `own_fixed`, `own_broken`, `own_false_shown` and
`own_sent_to_person` are sums over the `own_loops` loops (denominators accordingly), while `own_median`, `own_min` and `own_max` are per loop.

## 7. Choices the design left open (decided in the build; change one only before the seal)

1. **Digest size.** One shot and the hand-writer see the same selection rule as one round (up to 12 mistakes, false "shown" first, and up to 4 cases that were right
   and sure), over the whole study pool (`DIGEST_WRONG_MAX`, `DIGEST_RIGHT_MAX` in `config.py`).
2. **Improver output "invalid"** for the 25% rule means not schema-valid (above); the rule needs at least 4 outputs in the round (`INVALID_MIN_N`), so round 1 (two
   improver calls) cannot trip it.
3. **Floor.** The in-session floor uses every fixed arm that has at least two complete repeats of a block: Empty, Filler, Model-hand and, once phase B has run, One
   shot (36 differences). Rule 1 uses Empty alone (9 differences). Both are printed.
4. **Shared round 1.** The S loop of a pair reuses the A loop's round-1 calls (same inputs); results read its round-1 test block from the A loop's records.
5. **Pooled loop counts.** With two loops the "median" is their mean (half counts appear; the text chart draws a half count on the row above); fixed, broken, false "shown" and
   sent to a person are summed over the two loops, with the pooled denominator.
6. **Wire newline.** The sealed runs 2 and 3 wrote their prompt files with `Path.write_text` on Windows, so the broker received CR LF newlines (the ledger copies show it).
   The pilot sends the sealed texts byte for byte with LF (`WIRE_NEWLINE` in `config.py`; set it to `"\r\n"` before the seal to reproduce the sealed runs'
   on-wire bytes). The pilot's checker prompts were rebuilt for all 281 stage-1 calls of run 3 and are identical to run 3's prompts apart from that newline. Within the pilot every
   arm gets the same newlines, so the comparisons are unaffected; a comparison with run 3's absolute numbers is not claimed. The choice is recorded in the seal and in `RUN.json`.
7. **Right-and-sure cases** in an evidence packet are taken one truth at a time (shown, contradicted, not shown), lowest id first.
8. **Probe.** Five calls: three checker calls on study items, one improver call in the One shot form (up to 20 edits, so the 1200-token limit is exercised) on
   made-up evidence (the three items shown as if the checker had got them wrong), one method rewrite. It also checks reasoning tokens are zero and the replies are not cut off.
   It is its own run (`probe-1`), so its calls never mix with `pilot-1`'s.
9. **Notes seal.** The second manifest exists because of the order in the placeholders (digest first, then the model-hand set).
10. **Retries.** The design says two; it does not say how long to wait. The harness waits 2 s, then 6 s (`RETRY_BACKOFF_SECONDS`). The per-call timeout is 180 s
    (`CALL_TIMEOUT_SECONDS`); a timed-out call is killed before the broker writes its ledger entry, so it has a try in `calls.jsonl` but none in the ledger.
11. **Outage.** Ten calls in a row with no answer stop the run (`OUTAGE_STREAK`); the design names no number. Five answered calls in a row with no provider named stop it too
    (`UNKNOWN_PROVIDER_STREAK`): without the provider the pin cannot be checked.
12. **Spend cap.** US$1.00 for the pilot (the design's pilot share of the US$10 cap), counted from the ledger's provider-reported costs, with US$0.0002 assumed for a
    try that reports none.
13. **One shot is evaluated in phase B.** Its notes exist only after its improver call, so its three repeats (360 calls) are not interleaved with phase A's calls
    (4.6 asks for all arms of an item to be submitted together). If the provider drifts between phase A and phase B, One shot's counts carry that drift; the
    floor of 4.8 includes One shot's repeats (which are interleaved with each other) and is printed with and without it (all fixed arms; Empty alone). If One shot's improver call
    gives no valid edit the arm's notes are Empty and the run says so (`ONE SHOT WARNING`).
14. **The seal needs git.** It records the commit the fixed files were at and refuses to seal if git cannot be asked or the fixed files differ from it; `--allow-dirty` is for
    folders that are not repositories (the unit tests) and for a deliberate exception that the seal then records.
15. **The pre-flight cannot pass for want of anything to check.** E3 fails with an empty marker list; E4 ignores probes made with the fake provider and demands the seal in force; E1
    demands the five patched broker files committed (it says "not known" when the broker folder is not the top of its own git repository); E7 demands the scripts be listed in the seal.
16. **Time-stamped outputs.** `results` and `chart` never overwrite: each run of them writes new files named with the UTC time, so an earlier file that was hashed and stamped stays what it was.
17. **How strict the broker part of the seal is (flagged: stricter than the call path needs).** The seal hashes every one of the 30 files below the broker's `lib\`, the viewer's page and
    scripts included, and a new file there counts as a problem. A change to any of them while the pilot runs (another project editing the broker's viewer, say) stops the run with
    `the seal does not hold`. The call path is much smaller (`broker.mjs`, `lib\run.mjs`, `gate.mjs`, `config.mjs`, `ledger.mjs`, `keystore.mjs`, `scrub.mjs`, `providers\`, ...). The wide
    version was chosen because a call-relevant file missing from a narrow list would be a hole in the seal, while a false alarm costs a stop (resumable if the file is put back; if
    the change cannot be undone, a new seal and a new run). If you would rather have the narrow version, say so before the seal.
18. **An outage is not an invalid output.** An improver or method call with no answer after its retries stops phase B (code `outage`, resumable) before the step it belongs to
    is sealed. The design's "more than 25% invalid improver outputs" is read on answered outputs only; counting the unanswered ones would turn a few seconds of provider trouble
    into the verdict `invalid_improver`, and asking them again later would give entries that differ from the sealed ones.
19. **`--rerun-no-answer` leaves sealed rounds alone.** It asks again the calls with no answer (or another provider than the pin) of the step that has not been sealed and of the
    test blocks; it never asks again a call whose answer a sealed chain entry already used (a study call with no answer was counted wrong there; a new answer could only change
    the seal). The same holds for One shot's improver call. In a round that is not sealed yet, a loop whose improver call was already answered keeps the study and method answers
    that call was built from (also never asked again); an own-notes-plus-own-method loop (S1, S2) from round 2 on is kept in the same way when its method call was answered, even if
    its improver call was not (the improver prompt contains the rewritten method, and the method call was built from the study answers); and a call with no answer whose prompt has
    since changed (because an earlier call it is built from was asked again) is asked as it is built now, not stopped as "inputs changed".
20. **The percentile of rule 1.** The interpolated 90th percentile (type 7) decides f; the nearest-rank one is printed beside it.
21. **Leftover broker calls stop a start.** Design 4.11 says to list and stop leftovers before any resume; the harness does the listing for you at the start of every real command and
    refuses while orphaned broker calls of this pilot exist (a process table that cannot be read is a warning).

## 8. If something looks wrong

* `STOPPED: ... the seal does not hold` -> `python pilot.py manifest check`; a fixed file changed (or a new file appeared in `notesloop`, `prompts`, `data` or the broker's `lib`). Undo the
  change, or make a new seal (`manifest write --replace`) and start a new run.
* `STOPPED: ... Unknown provider "openrouter-plain-long"` (or exit 2) -> the E1 patch is not in the broker. Phase A does not need it; phase B does.
* `STOPPED: ... answered by X, not by its pin Darkbloom` -> the pin did not hold. Nothing is retried. Read the ledger entry named in the log before going on.
* `STOPPED: BROKER_CONFIG_DIR ... is set in the environment` -> unset it in the window you run from (`Remove-Item Env:BROKER_CONFIG_DIR` in PowerShell) and run the command again.
* 10 calls without an answer -> an outage; look at `python pilot.py status --run pilot-1`, fix it, resume with `--rerun-no-answer`.
* `error: another command is working on pilot-1` -> wait for it, or create `HALT` in `runs\pilot-1\`. If that process is not really there (a crashed run leaves its lock, and Windows may give the process id to another program), delete the `LOCK` file named in the message; `python pilot.py orphans --stop` removes it when no process has that id at all.
* `error: ... PLACEHOLDER` -> a notes file still has its PLACEHOLDER line or is empty (`python pilot.py notes-check`).
* `STOPPED: the chain files do not match` -> `python pilot.py chain-check --run pilot-1` names the entry; the run cannot go on (section 3).
* `STOPPED: NOTESLOOP_NO_REAL_BROKER is set ... never reach the real broker` -> that variable is set only by the unit tests, inside their own process, as a tripwire. If you see it in a real
  run it is set in your window: `Remove-Item Env:NOTESLOOP_NO_REAL_BROKER`.
* The broker's real ledger already holds 129 entries on lane `nl-pilot-a-study` (sequence numbers 17084 to 17212, 7 Oct 2026, 03:23 to 03:24 [a city] time, run folders `ledger\2026-10-07\0323...` and `0324...`).
  They are not part of the pilot: a mistake in the build's own mutation testing made a test call the real broker with toy items (no bank item text; provider-reported cost US$0.0076). The
  tripwire above was added because of it. The pilot's own study run will add 129 entries on the same lane; read them by the run folder named in `calls.jsonl`, not by lane alone.
* `error: 1 broker call(s) of this pilot are still running with no run behind them` -> a killed run left broker calls behind: `python pilot.py orphans`, then `python pilot.py orphans --stop`, then the command again.
* `STOPPED: NOTESLOOP_NO_REAL_BOX is set ... never reach the real box` -> the same tripwire for the codex-box route (section 9): set only by the unit tests; in a real run: `Remove-Item Env:NOTESLOOP_NO_REAL_BOX`.
* `STOPPED: NOTESLOOP_NO_REAL_LEMONADE is set ... never reach the real server` -> the same tripwire for the lemonade route (section 10): set only by the unit tests; in a real run: `Remove-Item Env:NOTESLOOP_NO_REAL_LEMONADE`.
* To stop on purpose: create `HALT` (or `HALT.txt`) in `runs\pilot-1\`, for example `New-Item runs\pilot-1\HALT -ItemType File` in PowerShell. Delete it to resume.

## 9. Running on the Codex subscription (codex-box)

The same pilot, the same plan and the same stop rules, with the checker, the improver and the method rewrite answered by **Codex (`gpt-6.1-sol`, effort `low`) running inside the experiment box**, on the owner's
subscription instead of the paid API. No broker, no ledger, no spend per call. Select it with `--provider codex-box` (the default stays `broker`). Nothing in this section has been run for real by the build: every test
used a fake box, and the first real call is the probe. The settings are constants in `config.py` (`CODEX_BOX_*`), recorded in the seal and in `RUN.json`.

**What a call is.** Four `ssh -o BatchMode=yes -o ConnectTimeout=10 -i <key path> [box login] "<command>"` runs per try: (1) the prompt goes to a fresh file in the box through ssh's standard input
(`umask 077; mkdir -p /tmp/nlbox && cat > /tmp/nlbox/<id>.prompt`); (2) `bash -lc` runs `codex exec --skip-git-repo-check --ephemeral --sandbox read-only --color never -m gpt-6.1-sol -c model_reasoning_effort="low" -o
/tmp/nlbox/<id>.reply "$p" < /dev/null`, where `p` is the prompt file read back with `$(cat file)` (a trailing newline is kept); (3) the reply file comes back between two marker lines, so that noise from the box's shell can
never be taken for a reply; (4) both files are deleted, after a failure too (not when ssh itself never connected: nothing was made). A prompt never appears in a command line, so no quote, dollar sign, backtick or newline in
it means anything to a shell (tested with a real bash and a prompt of 20 KB). The key file is never opened: the harness only checks that a file is there and gives its path to ssh, the first `ssh` program on the PATH.

**What differs from the broker route.**
* **One prompt**, not two messages: the system text, a blank line, then the user text. The broker route sends them as a system and a user message. Prompts are sent as UTF-8 with LF, whatever `WIRE_NEWLINE` says.
* **No pin by host.** There is no upstream host to pin. What answers is `gpt-6.1-sol/low`; every try records `provider_kind`, `model`, `effort`, `seconds`, `exit_code`, `reply_length` and `answered` in `calls.jsonl`, and the
  settings block that `codex exec` prints before it starts (`model:`, `reasoning effort:`) is read too: if it says another model or effort the run stops with the code `pin`, as for a wrong host ("not confirmed" when it prints none).
* **No spend**: cost 0 per call, so the spend cap never fires and no cost is "unknown". The limit is the **call cap**: `--call-cap N` tries in one command, retries included (default 3,000, `CODEX_BOX_CALL_CAP`), stop code `call_cap`.
  The same command run again starts from zero and reads the calls already made from the log.
* **Concurrency 2** (`CODEX_BOX_WORKERS`; `--workers` overrides it for one command). Codex's rate limits are not known: raise it only after a run has shown the limits are not met.
  The calls are the same 2,234 to 2,434 plus the probe (`python pilot.py counts`; its cost line is the broker route's estimate and does not apply here). Each try is four ssh runs, so the speed is whatever the probe's seconds per call say.
* **Timeouts and retries.** The `codex exec` step is stopped after 300 s (`CODEX_BOX_TIMEOUT_SECONDS`), the three short steps after 60 s each; a failed try is retried twice after 2 s and 6 s, then "no answer", exactly as on the broker.
  Ten calls in a row with no answer stop the run (`outage`); run it again with `--rerun-no-answer`. The failure codes in a try's `err`: `ssh_exit_255`, `write_exit_N`, `codex_exit_N`, `timeout`, `read_exit_N`, `read_garbled`, `empty_reply`.
  The `detail` of a try never holds prompt text: only lines of known harmless shapes (errors, ssh words) that are no line of the prompt (Codex echoes the prompt on its standard error).
* **The gate is the broker's marker list, applied by the harness**: before every call the prompt is checked against `confidential-markers.txt` (read from the broker folder, hashed in the seal, never printed); a hit is the stop
  `gate` and nothing is sent. An empty or missing list is refused. E3 checks the same list.
* **The seal is for one route.** `python pilot.py manifest write --provider codex-box` records the kind, the model, the effort, the host, the user, the key's path (never the key), the concurrency, the timeouts, the retries and
  the call cap, and covers no broker file but the marker list; a broker seal does not cover a codex-box command and the other way round (the message says which command to run). `MANIFEST.json` exists already (the
  pilot-1 seal), so the command needs `--replace`; the old seal is kept as `MANIFEST.<8 hex>.json`. A run keeps its seal and its settings for its whole life.
* **Probe and rule 4 read what applies.** The probe (E4) is five calls with exit code 0, a reply in the shape the harness reads, and the configured identity; it says it could not check how long a reply was, whether it was cut off, or
  whether reasoning was off (Codex gives no token counts or finish reasons and cannot turn reasoning off). Rule 4 reads that every answered try of the whole log carries the sealed model and effort, that no record is of another route,
  that the run's settings are the sealed ones, and that the seal in force now is the seal every command ran under. The checks of the broker route that do not apply are listed in the probe line and in the results: the Darkbloom pin,
  the ledger's token counts, finish reasons and costs, reasoning off, and the broker's own gate and ledger. The pre-flight with `--provider codex-box` shows E1 (the broker's long mode) as `N/A`.

**The commands, in order** (PowerShell, in the build folder `<home>\Private\claims\2026-10-07-notes-loop-pilot`; the numeral in `cx-pilot-1` and `cx-probe-1` is the digit one; the code must be committed first, and the first command runs the unit tests, about three minutes):

```
python pilot.py preflight --stage seal --provider codex-box
python pilot.py manifest write --provider codex-box --replace
python pilot.py probe --run cx-probe-1 --provider codex-box
python pilot.py phase-a study --run cx-pilot-1 --provider codex-box
python pilot.py notes-check
python pilot.py manifest write-notes --run cx-pilot-1 --replace
python pilot.py phase-a fixed --run cx-pilot-1 --provider codex-box
python pilot.py results --run cx-pilot-1
python pilot.py phase-b --run cx-pilot-1 --provider codex-box --wait-for-stamp
python pilot.py chain-check --run cx-pilot-1
python pilot.py results --run cx-pilot-1
python pilot.py chart --run cx-pilot-1
```

Between `phase-a study` and `notes-check`: the two notes files in `notes\` were written for the pilot-1 study digest; the design writes the model-hand set from the digest of the run it is used in, so either write new files from
`runs\cx-pilot-1\digest\study-empty-digest.txt` (step 6 of section 1) or keep these (the notes seal records whether each file is newer than the digest). Stamp the hashes the commands print (the seals; `STAMPED-r<k>` for
`--wait-for-stamp`, section 5) as before. The probe must pass before `phase-a study`: `preflight --stage run --provider codex-box` shows E4 as PASS once it has. In the first command E6 shows the pilot-1 seal as
`TODO` ("seal again"), not as a failure, because that seal predates this route and no longer matches the code; once the codex-box seal is in, E6 does not read the notes seal of the pilot-1 run (a broker run) and says so. Phase A's
fixed arms still demand the notes seal of their own run (`manifest write-notes --run cx-pilot-1 --replace`, above).

**Known limits.**
* **Codex has no temperature or seed setting, and its reasoning cannot be turned fully off** (`low` is the nearest to the broker route's "off"). Two identical calls can answer differently, so the **noise floor from the repeats matters
  more**: read every gain against it, and do not compare these counts with pilot-1's (another model, another instrument; the thresholds of the four rules were set for Gemma@Darkbloom). Results and the chart say "codex-box" at the top.
* Codex is an agent: it may run read-only commands in its sandbox before it answers, so a call takes seconds to a minute and uses subscription allowance. A usage window that runs out shows as `codex_exit_1` with "usage limit" in the
  detail; ten of those in a row stop the run (`outage`): wait, then continue with `--rerun-no-answer`.
* ssh must work with no prompt: the key at the sealed path, the box's host key already accepted (BatchMode will not ask), `[box host]` resolving, and codex logged in inside the box (the harness never touches sign-in files). If none
  of that holds, every call fails with `ssh_exit_255` and the run stops as an outage.
* A call stopped by the timeout may leave its codex running in the box until it ends: the prompt and reply files are deleted when the call ends, but a reply that codex writes after that stays in `/tmp/nlbox`. After a hard
  kill of the harness, local `ssh` processes and the files in `/tmp/nlbox` in the box can remain (private, mode 600: `rm -rf /tmp/nlbox` in the box); `python pilot.py orphans` lists broker calls only and does not see them.
* A prompt must be under 120,000 bytes, start with no dash and hold no NUL byte (a Linux process takes one argument of at most 128 KiB); the real checker prompts are 4.6 to 5.8 KB and the largest possible improver prompt about 30 KB (a test measures them from the sealed bank, sizes only). Otherwise the stop is `usage`.
* The code change that added this route changed fixed files, so the pilot-1 seal no longer matches the code (`python pilot.py manifest check` says so): that is the seal doing its job. Do not `results --run pilot-1` again: rule 4 would read the
  broken seal. The result files already written for pilot-1 stay as they were.

## 10. Running on the local models (lemonade)

The same pilot, the same plan and the same stop rules, with the checker, the improver and the method rewrite answered by **a small model served by Lemonade on this PC**
(`--model qwen` is `Qwen3-4B-Instruct-2507-GGUF`, `--model gemma` is `Gemma-4-E4B-it-GGUF`), asked through the client of Receipt Pair. No broker, no hosted model, no key, no spend, and
nothing leaves this PC. Select it with `--provider lemonade`. Nothing in this section has been run for real by the build: every test used a fake server, and the first real call is the probe.
The settings are constants in `config.py` (`LEMONADE_*`), recorded in the seal and in `RUN.json`. The section also describes a fresh bank for the test items (`--bank`), which is a
separate option that any route can use.

**The client.** `notesloop\lemonade_client.py` is a byte for byte copy of `<home>\Workbench\word-test-2026-10-07\vendor\receipt_pair\client.py` (Receipt Pair 0.1.0). The SHA-256 of the
source and of the copy is the same, `7d4b497477e5efd19a9fc56f69a8872c8daba47924963febb9139f3057755ac1`: `config.py` records both, the seal records both and holds the copy (as a file of `notesloop\`) and the source
(as a fixed file of its own), and the provider refuses to start with a copy that is not the recorded one. It uses the standard library only, uses no proxy, and refuses a server address
that is not this machine.

**What a call is.** One `LemonadeClient.chat(model, system, user)`: an OpenAI-style request to `http://localhost:13305/api/v1/chat/completions` with a system message and a user message (the
prompt texts byte for byte, LF; the improver's and the method rewrite's system part is the system message, as on the broker route). The settings are the sealed runs': temperature 0, seed 42,
`max_tokens` 400, thinking off (Gemma 4 carries `chat_template_kwargs: {enable_thinking: false}` in every request; the Qwen model is an instruct model that does not think). The improver and the
method rewrite use a second client of the same class whose settings differ in `max_tokens` only (1200): the checker's settings are not touched, and a test sends the three kinds of call and
compares the request bodies. The seal records both request settings; every try records the settings that were really sent. Before the first call that is really made in a command, the client makes
the chosen model the only one loaded (`make_only_loaded`: it reads `/health` and unloads another model if one is loaded; the first chat request then loads the model it needs). That happens once
per command, never per call, and a command that only replays its log never touches the server. The vendored client asks a failed chat request once more at once ("one retry after a failure, as
the sealed runs did"), so one try is one or two requests; the harness's own two retries (after 2 s and 6 s) come on top, exactly as on the other routes.

**What differs from the other routes.**
* **No pin by host.** What answers is the model that was asked for. Every try records `provider_kind`, `model`, `model_key`, `settings` (the request settings sent: everything but the model and the messages),
  `seconds`, `err`, `reply_length`, `answered` and `requests` (the chat requests the try made), and the numbers of the server's own speed report when it gives some (`server_stats`: read as numbers
  only, never as token counts). **Rule 4 reads** that every answered try of the whole log carries the sealed model and the sealed request settings for its kind (400 tokens for a checker
  call, 1200 for an improver or method call, nothing else different), that no record is of another route, that the run's settings are the sealed ones, and that every command ran under the seal in force
  now; **the probe reads** the same for its five calls, and E4 counts it only under the seal in force and for the model that seal names. Both say which checks **do not apply**: from the broker route the Darkbloom pin, the ledger's token counts, finish reasons and provider-reported costs, reasoning tokens, and the broker's own
  gate and ledger; from the box route ssh, the key file, Codex's own settings block and effort, and exit codes; and the marker-list gate (nothing leaves this PC, so no phrase list is applied). They say
  what this route **cannot check**: how long a reply was and whether it was cut off (the client returns no token counts or finish reasons), and whether thinking was off on the server (the request
  carries the switch and the try records what was sent, but the client cannot read the server's state back).
* **No spend**: cost 0 per call. The limit is the **call cap**: `--call-cap N` tries in one command, retries included (default 3,000, as on the codex-box route), stop code `call_cap`; run the same command
  again to go on.
* **One call at a time** (there is one Lemonade user and the server holds one model): `--workers` is 1 and any other value is refused (exit 2); the provider also holds a lock around every call. The same holds
  across commands: while a lemonade command works, `runs\LEMONADE-SERVER.LOCK` names its process (as `LOCK` does for a run), and a second command on the server, whichever run it is for (the probe in one window
  while the study runs in another), is refused at once (exit 2, `another command is working on the Lemonade server`). A lock whose process is gone is taken over, and a command that stops, however it stops,
  gives the server back.
* **Timeouts and retries.** 300 s per request (`LEMONADE_TIMEOUT_SECONDS`); a failed try is retried twice after 2 s and 6 s, then "no answer", counted as wrong. Ten calls in a row with no answer stop the run
  (`outage`): fix it, then continue with `--rerun-no-answer`. The codes in a try's `err`: `backend_error: <ExceptionName>` (the client's own: `URLError` for a server that is not there, `HTTPError` for a refusal
  or an error of the model, `KeyError` or `IndexError` or `JSONDecodeError` for a reply in another shape), `timeout` (any request that timed out), `empty_reply` (the server answered with nothing). The `detail`
  of a try never holds prompt text: a server message that quotes a line of the prompt is replaced by a sentence saying so.
* **E1 is N/A** (there is no broker mode to patch). E2 to E8 are made as for the codex-box route, with the lemonade seal and a lemonade probe (E4 counts one only under the seal in force and only for the model
  that seal names). E3 still reads the broker's marker list: this route does not apply it, but the pre-flight does, as a check that no prompt or item holds a confidential phrase (it covers the fresh bank's items too).
* **The seal is for one route and one model.** `manifest write --provider lemonade --model qwen` records the kind, the model, both request settings, the server, the limits and the client's SHA-256s, and covers no
  broker file (not even the marker list); it needs `--replace` while the pilot-1 seal is `MANIFEST.json`. A broker or codex-box seal does not cover a lemonade command and the other way round (the message names the
  command to run). **A run uses one model**: later commands read it from the seal (`--model` may be given and must be the sealed one), and a run keeps its model and server for its whole life. To run the other
  model, seal again with `--model gemma --replace` and start new runs.
* **Tripwires.** `NOTESLOOP_NO_REAL_LEMONADE` is set by the tests package, as the broker's and the box's are, and a guard on port 13305 in the socket module does not depend on the harness's own code. The provider
  refuses before the client does (the client takes any exception of its transport for a failed request), so a test that reached for the server would be stopped, not retried. Every test hands the provider a fake server.

**A fresh bank for the test items (`--bank PATH --bank-sha256 HEX`, any route).** The test items of the fixed arms (and of phase B's rounds) can come from a JSON Lines bank in the sealed bank's item format
instead of items 161 to 280. The study pool stays the pilot's own (129 items), and so do the first three study blocks of each loop.
* **The file.** One item per line with the sealed bank's fields: `id` (a string of digits that is not an id of the sealed bank), `claim`, `turns` (each turn with `cmd` and `output` as text; `narration` is not read), `truth`
  (`shown`, `contradicted` or `not_shown`), `deciding_line` (text, which may be empty) and `trap` (a non-empty word: the blocks are stratified by truth and trap). `why` is not read. A file written on Windows (CRLF, a
  byte order mark, no final newline) is read as it is. Its SHA-256 is checked **before** anything is read from it: a changed bank is refused. Every refusal names a file, a line and a field, never an item's text.
* **Several files.** `python pilot.py bank-join --out FILE [--hashes LIST] FILE ...` joins batch files into one file in id order (numeric), one item per line, LF, no byte order mark, a final newline, and prints
  the SHA-256 that `--bank-sha256` takes, the counts and the truth counts (no item text). For batch files that are already in order and written that way, the joined file is their concatenation. It never
  overwrites a file, writes nothing unless every file is valid and no id is in two files, and with `--hashes` (a `sha256sum`-style list such as `ITEMS-SHA256.txt`) every file must be on the list with the hash
  it has. Items 301 to 900 later: give it all the batch files and make a new seal.
* **Blocks.** A block is 40 items and the number of blocks follows the bank: 200 items are 5 blocks, 600 are 15. A bank whose number of items is not a multiple of 40 is refused with how many to remove or add.
  The blocks are stratified by truth and trap (seed `notes-loop-pilot/test-blocks-fresh/1`); the file order does not change them. The noise floor, the by-block tables and the results read as many blocks as there are.
* **What is recorded.** The seal holds the bank's path and hash, its ids in file order, its blocks and its truth counts, and holds the file as a fixed file (hashed at every check, with the seal's other files); a
  later check that finds the file changed is a seal stop. `RUN.json` keeps the bank for the run's whole life (a run cannot go on with other test items), every test call's record names its block, and the results and the
  chart say which bank ("TEST BANK <12 hex>, ... not the pilot's items 161 to 280"). The harness does not know whether the items were scored before: that is in the owner's record.
* **Which command takes it.** `manifest write ... --bank FILE --bank-sha256 HEX` records it. The commands after that read it from the seal, and the pair on a later command (`phase-a`, `phase-b`, `probe`) may be given
  again and must be the same bank (an error says so); `results` and `chart` read the bank from the run's own `RUN.json` (and refuse another one). `--bank` alone keeps the meaning it always had (the sealed bank
  at another place, held to the sealed hash). `counts`, `preflight`, `notes-check` and `rehearse` take the pair too: `notes-check` covers the fresh items in its six-word copy audit (so the notes cannot copy a test item), and the
  pre-flight's E3 checks their prompts against the marker list (item ids only).
* **Phase B.** One round per block, and each round needs a block of 25 study items of its own for every loop: the study pool has room for 5 rounds, so phase B runs on a bank of up to 200 items (5 blocks: 3,726 to 4,126
  calls in all, and the probe's 5). A bigger bank is refused by `phase-b` (exit 2, before any call, with the number to use); phase A's fixed arms take any size that is a multiple of 40.

**The commands, in order** (PowerShell, in the build folder `<home>\Private\claims\2026-10-07-notes-loop-pilot`, with the code committed; "lm" is a lower-case L and a lower-case M and the numeral in
`lm-probe-1` and `lm-pilot-1` is the digit one; the pre-flight runs the unit tests, about four minutes). A fixed-arms run on the first fresh bank (items 301 to 500, 200 items, 5 blocks of 40):

```
cd <home>\Private\claims\2026-10-07-notes-loop-pilot
$items = "<home>\Private\claims\2026-10-07-rsi-items-301-500"
python pilot.py bank-join --out "$items\bank-301-500.jsonl" --hashes "$items\ITEMS-SHA256.txt" "$items\batch-301-340.jsonl" "$items\batch-341-380.jsonl" "$items\batch-381-420.jsonl" "$items\batch-421-460.jsonl" "$items\batch-461-500.jsonl"
$bank = "$items\bank-301-500.jsonl"
$sha = "PASTE-THE-64-CHARACTERS-THAT-bank-join-PRINTED-AFTER-sha256"
python pilot.py counts --bank $bank --bank-sha256 $sha
python pilot.py preflight --stage seal --provider lemonade --model qwen --bank $bank --bank-sha256 $sha
python pilot.py manifest write --provider lemonade --model qwen --bank $bank --bank-sha256 $sha --replace
python pilot.py probe --run lm-probe-1 --provider lemonade
python pilot.py phase-a study --run lm-pilot-1 --provider lemonade
python pilot.py notes-check
python pilot.py manifest write-notes --run lm-pilot-1 --replace
python pilot.py phase-a fixed --run lm-pilot-1 --provider lemonade --bank $bank --bank-sha256 $sha
python pilot.py results --run lm-pilot-1
python pilot.py chart --run lm-pilot-1
```

What each step is: `bank-join` checks each batch against `ITEMS-SHA256.txt`, writes the joined file and prints its hash (stamp it); `counts` shows 200 items in 5 blocks and 1,800 calls for the fixed arms; the pre-flight
at the seal stage prints READY TO SEAL when E1 is N/A, E2, E3, E5, E7 and E8 pass and E4 and E6 are still to do (E6 shows the pilot-1 seal as `TODO`, "seal again", not as a failure); the seal prints its SHA-256 (stamp
it: FreeTSA and OpenTimestamps) and the bank's line; the probe is five calls (3 checker, 1 improver in the One shot form, 1 method rewrite) and prints `PROBE PASSED` or says what failed (`preflight --stage run
--provider lemonade --model qwen --skip-tests` then shows E4 as PASS); the study run is 129 calls and writes the digest; the notes step is as in section 9 (write `notes\model-hand.txt` and `notes\filler.txt` from
`runs\lm-pilot-1\digest\study-empty-digest.txt`, or keep the files that are there: `manifest write-notes` records whether each is newer than the digest); the fixed arms are 1,800 calls (3 arms x 3 repeats x 200
items), and naming the bank again on that command is a check that it is the one in the seal; `results` prints the floor over 5 blocks (15 differences from Empty's repeats, so rule 1 is read on a complete set)
and rule 4 for this route. Phase B, if the bank is 200 items or fewer: `python pilot.py phase-b --run lm-pilot-1 --provider lemonade` (add `--wait-for-stamp` to stamp the chain heads round by round, section 5),
then `chain-check`, `results` and `chart`. Call counts for 200 items: probe 5, study 129, fixed arms 1,800, One shot 601, the loops 1,196 to 1,596; 3,726 to 4,126 in all, 27 of them long-mode calls (19 improver, 8 method).
Stops, resuming and `HALT` are as in section 3.

**Known limits.**
* **Nothing has been run against the real server.** The speed (seconds per call), whether Lemonade answers `/health` and `/chat/completions` as the vendored client expects, whether the model answers in the shape the
  harness reads, and how long the first call takes (it includes loading the model) are unknown until the probe. If `/health` does not answer, the model check is skipped and said so (`prepare_note` of the first try);
  the chat requests then show whether the server is there. A server that is not there fails at once (`backend_error: URLError`) and ten such calls stop the run as an outage; a server that hangs is the slow case
  (up to two requests of 300 s per try, three tries per call): stop it with `HALT` rather than wait for ten of those.
* **The context window is not set by the harness.** The real checker prompts are 4.6 to 5.8 KB and the largest possible improver prompt about 30 KB (roughly 8,000 tokens); a model loaded with a smaller context
  can refuse or cut the long ones. The probe's improver call is the One shot form on three cases, smaller than the largest, so a pass does not show that the largest fits: a refusal shows as `backend_error: HTTPError`
  and, in phase B, stops the run as an outage before the step is sealed (resumable).
* **No token counts, no finish reasons.** A reply cut off at 400 tokens is read like any other reply (one that does not parse is a call with no verdict, counted wrong). The probe and the results say that this is not
  checked. If the Lemonade version ignores the thinking switch the harness cannot tell.
* **Greedy decoding with a seed does not promise identical repeats** on a local server (threads, batching, the backend). The noise floor from the repeats says how much it differs: read every gain against it, and do not
  compare these counts with pilot-1's (Gemma 26B at Darkbloom) or with the codex-box route's: the thresholds of the four rules were set for Gemma@Darkbloom.
* **One user, one model.** At the start of every command that makes a call the client unloads any other model on the server: do not use Lemonade for anything else while a command runs. The address
  (`http://localhost:13305/api/v1`) is a constant of `config.py`; another port is a code change and a new seal, and the environment is never read for it.
* **A fresh bank** needs a multiple of 40 items, ids that are digits and not the sealed bank's, and a `trap` on every item; phase B runs on at most 200 items; `bank-join` writes one joined file per call and the
  study pool stays the pilot's 129 items (a fresh study pool would be another design). Whether the items are fresh is for the owner's record.
* The code change that added this route and the fresh bank changed fixed files, so the pilot-1 seal no longer matches the code (as in section 9): do not `results --run pilot-1` again, and expect E6 to say
  `TODO`, "seal again", at the seal stage.
