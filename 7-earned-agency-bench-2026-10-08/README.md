# Bundle 7: Earned Agency Bench, real run 1 (8 October 2026)

By Joshua Bauer (ISWT42). The design, code, tests, raw run and score of one test of whether an AI agent's track record should decide how closely its work is checked. The design was sealed at 03:14:29 UTC on 8 October, before any paid call. The run took place from 04:28:18 UTC to 05:44:33 UTC. The raw run was sealed at 05:45:21 UTC. The score was written after that seal.

This bundle: 6,178 published files, 17.1 MB (6,139 of them are single raw calls in `runs/real-1/blobs/`).

## In plain words

Four small, cheap AI models worked on a bank of 40 small coding jobs. Each job had hidden tests that the model never saw. A game is one arm played for 5 rounds of 8 jobs, and there were 8 games per arm, 40 games in all. Before each job, the model wrote down how likely it was that its work would pass. Then it did the job and said "done" or not. The hidden tests then decided whether the work really passed. A "false done" is a job the agent called done and the hidden tests failed.

Five ways of handling the hand-off were compared, 8 games each:

| Arm | What happened to a finished job |
|---|---|
| A baseline | The agent's own word that it was done was accepted. |
| B ticket | Same, but the prompt carried a ticket written before the work that named the check. |
| C relay | Every finished job was checked by a second agent, from another model family. It was given the ticket, the file's fingerprint, the first agent's claim and the runner's own line from the hidden-test run, and it could not change the work. |
| D earned | Agents with the better forecasting record were checked less (5 jobs of 8 were checked). |
| E random | The same amount of checking as D, handed out at random. |

The question: do agents with a better track record deserve less checking ("earned agency")?

## What the score says

Every number is a count with its denominator, copied from `runs/real-1-score.txt`.

- **The agents were often wrong about "done".** In arm A they said done on 314 of 320 jobs. The hidden tests failed 116 of those 320 jobs (false done). Only 198 of 320 passed (0.62).
- **They did not know it.** In arm A the mean forecast was 0.92 against a pass rate of 0.62.
- **Checking every job against the record removed the false done that was handed on.** In arm C, 0 of 320 jobs handed on a false done, and 0 of 256 in rounds 2 to 5, against 93 of 256 in arm A. The second agent caught 122 of 122 failing jobs, let none through (0 of 122), raised no false alarm on passing work (0 of 197), and gave the exactly right verdict on 319 of 319 valid replies (1 reply of 320 was invalid). The test of arm C against arm B: mean difference -0.3844, p = 0.0078, Holm-adjusted p = 0.0312.
- **The ticket alone did not help.** Arm B against arm A: mean difference +0.0219, p = 0.1250, Holm-adjusted p = 0.2500.
- **Earned agency was not shown.** The primary test (false done handed on, rounds 2 to 5, earned minus random): n = 8, mean difference -0.0117, p = 0.6562. The record says this is not evidence that there is no effect.
- **Routing by record handed on more false done than checking everything.** Arm D against arm C, rounds 2 to 5: mean difference +0.1289, p = 0.0078, Holm-adjusted p = 0.0312.
- **Forecasts did not clearly get better over the rounds.** Change -0.0299, p = 0.1094 (not shown).
- **Cost.** 3,920 calls, US$0.316988 of a US$3.0 cap.

## Limits

- The record clearly settled each job here: the second agent was handed the line from the hidden-test run, a plain pass or fail. That probably made its job easy. A perfect checker is not to be expected on messy real logs. For comparison, in an earlier checker study (the deciding-line tables in bundle 3, local pair, 100 items) the rule "shown needs both" let 2 of 68 false "shown" answers through and kept 23 of 32 true ones.
- Four small, cheap models. One run of 40 games. Not replicated.
- Two of the declared secondary tests (S6 and S7, the twin pairs) were not run: their arms were not part of this run.
- Our forecasts for this run are not published (see below).

## What is in this folder

| Path | What it is |
|---|---|
| `DESIGN.redacted.md` | The design as sealed, with 4 forecast probabilities of the decision model marked as removed. |
| `config.json`, `bench.py`, `jobs.py`, `room.py`, `routing.py`, `sandbox.py`, `standin.py`, `stats.py`, `score.py`, `call_costs.py`, `relay_costs.py` | The code, the job bank (with the hidden tests), the model list and prices, the scorer and the statistics, as sealed on 8 October at 03:14:29 UTC. |
| `tests/` | The unit tests and the planted-fault checks. |
| `sources/` | His words behind the two ideas, the coordinator's amendment, and the agreed design (redacted copy). |
| `EAB-SEAL-SHA256.txt` with `.tsr`, `.tsq`, `.ots` | The pre-run seal: SHA-256 of every file above. FreeTSA 2026-10-08T03:14:29Z. The OpenTimestamps proof holds Bitcoin block 970432. |
| `runs/real-1/room.jsonl` | The raw run: every sealed forecast, work reply, certification and score record, in order, hash-chained. |
| `runs/real-1/room.jsonl.head` | The head of that chain. |
| `runs/real-1/blobs/` | One file per raw call (6,139 files), named by their SHA-256. |
| `runs-real-1-full-console.txt` | The runner's closing line. |
| `RESULTS-SEAL-SHA256.txt` with `.tsr`, `.tsq`, `.ots` | The results seal: SHA-256 of the raw run, before any count. FreeTSA 2026-10-08T05:45:21Z. The OpenTimestamps proof holds Bitcoin block 970449 (upgraded on 8 October 2026 after the first release; its Merkle root matched the block's on an independent block explorer). |
| `runs/real-1-score.txt` | The score, written by the sealed `score.py` after the results seal. SHA-256 `941462cb0e91dcaa0b611bb5a4f704dde8f61c7a71f5b639490291bf53933f04`. It is not in a seal list. |

## How to check

- Everything at once: from the top folder run `python check_public.py`.
- This bundle's two seal lists: `cd` to this folder, then `tr -d '\r' < EAB-SEAL-SHA256.txt | sha256sum -c --ignore-missing` and the same for `RESULTS-SEAL-SHA256.txt`. Files that are not published (listed below) are skipped.
- Re-count: from this folder, `python score.py runs/real-1/room.jsonl` checks the hash chain of the raw run and prints the score. Its output was checked against `runs/real-1-score.txt` on 8 October 2026 and was identical.
- FreeTSA and OpenTimestamps: as in the top README.

## What was left out, and why

- **Our forecasts.** `PREDICTIONS.md` (our statements about the result, written before the run) and `sources/CLAUDE-PREDICTIONS-R4.md` are kept private by the owner's rule. Their SHA-256 are in `EAB-SEAL-SHA256.txt`, so the seal chain still checks.
- **The decision model's forecasts.** `sources/SUMMARY-R4.txt` and `sources/STACK-3-PROPOSAL.md` (a draft that sets the two sets of forecasts side by side) are kept private with them. Where `DESIGN.md` and the agreed design quote them, a redacted copy is published, with the removed parts marked.
- **`COMMANDS.md`**: run commands with local paths and account steps.
- **Not sealed, not published:** the stand-in dry runs, the two smoke runs, `.ots` backup copies.
- `WITHHELD.json` at the top lists each withheld file with the hash its seal list gives it.

## Correction

8 October 2026, after the release with version DOI 10.5281/zenodo.23235648: that release's copy of this README said the four models "did 40 small coding jobs each, in 5 rounds". The right description is the one in "In plain words" above: a bank of 40 jobs, and 40 games (8 per arm), each game 5 rounds of 8 jobs. The score and every other file are unchanged.

8 October 2026, later: the `.ots` proof for `RESULTS-SEAL-SHA256.txt` was upgraded with the calendars' answers and now holds Bitcoin block 970449 (earlier attestations: 970464, 970467). The release with version DOI 10.5281/zenodo.23235648 carries the earlier, still-pending proof; the files it seals are unchanged.

8 October 2026, later: an outside methods review asked for corrections to wording in this README. `ADDENDUM-1-2026-10-08.md` in this folder answers it; the sealed files and the score are unchanged. In short: the design was sealed before the scored run, not before any paid call (a first smoke run came earlier); the scored record began as one repetition and was resumed to complete the predeclared 8; one unit test fails in the public package because the README, the redacted copies and the addendum are outside the original seal list (explained in the addendum and in `SEAL-NOTES.json`); "the ticket alone did not help" should read "a benefit from the ticket alone was not shown"; "caught 122 of 122" leaves out one failing job whose verdict was invalid and was blocked; "they did not know it" should read "their forecasts were overconfident in aggregate"; checking every job cost about 58% more per delivered good job.
