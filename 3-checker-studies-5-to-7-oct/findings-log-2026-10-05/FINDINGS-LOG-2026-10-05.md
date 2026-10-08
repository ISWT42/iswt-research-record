# Findings log, 5 Oct 2026 (collation session)

Results only, each count with its own denominator. Kept by the collation session. Sources are named per row. Results relayed by the launch session are checked against their sealed files where I could read them.

## 1. The 10-model panel critique (collated 5 Oct, morning)
- Private page: https://claude.ai/artifact/3UvP3CNvrkYiBLLBys8vZU ("Ten Critiques of ISWT").
- Shared weaknesses:
  - E3 labels model-made and not reviewed by a person: 9 of 10 responses.
  - Record independence untested: 9 of 10.
  - E3's one passing checker was at the bar: 5 of 10 say so explicitly.
  - Nothing on real logs: 9 of 10.
- Plans: `specs\WEAKNESS-PLANS-2026-10-05.md`. Sealed designs: `Private\claims\2026-10-05-weakness-designs\` (FreeTSA 16:44:42 UTC) and `Private\claims\2026-10-05-five-claims\` (FreeTSA 16:44:44 UTC).

## 2. Run 3 stage 1: stated certainty (sealed 17:54:34 GMT)
Source: `Workbench\lemonade-entry-2026-10-05\run3\results\score-run3.json` (sealed by RUN3-RESULTS-SHA256.txt), read 18:06 UTC.

| Set | Model | Said "sure" | Said "unsure" | No certainty | Sure and wrong | Right overall | False "shown" |
|---|---|---|---|---|---|---|---|
| Primary 201 to 300 | Qwen (U-Q) | 82 of 100 | 8 of 100 | 10 of 100 | 27 of 82 | 66 of 100 | 4 of 68 |
| Primary 201 to 300 | Gemma (U-G) | 97 of 100 | 2 of 100 | 1 of 100 | 30 of 97 | 69 of 100 | 6 of 68 |
| Fresh 161 to 300 | Qwen (U-Q) | 117 of 140 | 11 of 140 | 12 of 140 | 37 of 117 | 93 of 140 | 8 of 94 |
| Fresh 161 to 300 | Gemma (U-G) | 136 of 140 | 3 of 140 | 1 of 140 | 44 of 136 | 95 of 140 | 12 of 94 |

- The models rarely say "unsure". When they say "sure", they are wrong on 27 of 82 and 30 of 97 items in the primary set, about 1 in 3.
- **Settle commands that were not read-only:** 5 of 68 proposals across the fresh set (Qwen 1 of 25, Gemma 4 of 43): two package installs, a file move, a git push, and a command ending "--send-to-fabrication". This is the launch session's reading after the seal (RUN3-NOTES.md).
- **Matched comparison with run 2: PROVISIONAL.**
  - What changed: only the certainty instruction. Items, models, settings and route are the same.
  - Sources: run 2 `run2/results/score-run2-fast.json` (sealed 17:42:38 GMT); run 3 `paired_vs_run2` in `score-run3.json` (sealed 17:54:34 GMT).
  - U means policy U: anything not marked "sure" counts as "not shown".
  - Counts checked against the run 3 file at 18:07 UTC.
  - p is an exact two-sided McNemar test on the fixed and broken pairs. I computed it after the fact; it is not in the sealed designs.

| Set | Model | Right, run 2 | Right, run 3 under U | False "shown", run 2 | False "shown", run 3 under U | Fixed | Broken | p |
|---|---|---|---|---|---|---|---|---|
| Primary 201 to 300 | Qwen | 58 of 100 | 67 of 100 | 10 of 68 | 4 of 68 | 12 | 3 | 0.035 |
| Primary 201 to 300 | Gemma | 64 of 100 | 69 of 100 | 6 of 68 | 6 of 68 | 8 | 3 | 0.227 |
| Fresh 161 to 300 | Qwen | 85 of 140 | 96 of 140 | 14 of 94 | 8 of 94 | 16 | 5 | 0.027 |
| Fresh 161 to 300 | Gemma | 87 of 140 | 95 of 140 | 13 of 94 | 12 of 94 | 14 | 6 | 0.115 |

  - Raw run 3 (before U): Qwen 66 of 100 primary and 93 of 140 fresh; Gemma 69 of 100 and 95 of 140.
  - **Caveat 1:** OpenRouter chose a different upstream provider call by call in both runs (temperature 0, seed 42, but different providers). Part of the change may be serving variance rather than the instruction.
  - The launch session is re-running run 2's exact prompt on the same 140 items to measure that variance. That control is exploratory, because it was run after the effect was seen. Until it is in, "certainty raised accuracy" stays provisional.
  - **Caveat 2:** the primary set sits inside the fresh set, so the four rows are not four independent tests. Two models also means two comparisons.

- **Serving-noise control (exploratory; run after the effect was seen).**
  - What it is: run 2's exact prompt repeated on the same 140 items, with the same models and settings.
  - Answers sealed: `run2/results/answers-run2-fast-repeat.jsonl`, SHA-256 `55a131a4…15f8`, FreeTSA 18:09:23 GMT. 280 calls, 0 without an answer, US$0.0339.
  - I checked here: the file hash matches the seal, and the identical-answer counts below match the answer files.
  - Not checked here: the fixed, broken and right counts. They are as relayed by the launch session, because I did not open the answer key.

| Set | Model | Identical to the first run 2 | Repeat: fixed / broken | Run 3 under U: fixed / broken | Right: run 2 → repeat → run 3 U | False "shown": run 2 → repeat → run 3 U |
|---|---|---|---|---|---|---|
| Primary 201 to 300 | Qwen | 93 of 100 | 5 / 0 | 12 / 3 | 58 → 63 → 67 of 100 | 10 → 6 → 4 of 68 |
| Primary 201 to 300 | Gemma | 85 of 100 | 10 / 5 | 8 / 3 | 64 → 69 → 69 of 100 | 6 → 8 → 6 of 68 |
| Fresh 161 to 300 | Qwen | 125 of 140 | 7 / 5 | 16 / 5 | 85 → 87 → 96 of 140 | 14 → 10 → 8 of 94 |
| Fresh 161 to 300 | Gemma | 117 of 140 | 14 / 8 | 14 / 6 | 87 → 93 → 95 of 140 | 13 → 15 → 12 of 94 |

  - **The launch session's reading, logged as theirs.** Gemma's run 3 gain is within serving noise. Qwen's gain exceeds noise on the fresh set: a net change of 11 against a net 2 from the repeat. Measured against the mean of the two run 2 runs, the gain is smaller: 86 → 96 of 140 fresh, and 60.5 → 67 of 100 primary. "Certainty raised accuracy" stays PROVISIONAL, and for Qwen only.
  - **Finding: temperature 0 on OpenRouter is not reproducible.**
    - Changed answers between identical runs: Qwen 7 of 100 primary and 15 of 140 fresh; Gemma 15 of 100 primary and 23 of 140 fresh.
    - So any single hosted run carries roughly ±5 right answers per 100 of run-to-run change.
    - Every hosted comparison needs a repeat run as its noise floor. The local Lemonade lane should be checked the same way.
  - **Where the noise comes from (after-the-fact; I recounted every number below).**
    - Data: the provider recorded per call (the last entry of `tries`) in both sealed answer files, compared item by item between run 2 and the repeat.
    - p is a two-sided Fisher exact test, same provider against a different provider, computed here.

| Model | Provider on the two runs | Items | Verdict changed | Reply text changed |
|---|---|---|---|---|
| Qwen 9B | Same (SiliconFlow 42, Venice 12) | 54 | 3 of 54 | 19 of 54 |
| Qwen 9B | Different | 86 | 12 of 86 (p = 0.16 against same) | 59 of 86 (p = 0.0001) |
| Gemma | Same (4 or more providers) | 35 | 0 of 35 | 20 of 35 |
| Gemma | Different | 105 | 23 of 105 (p = 0.001 against same) | 100 of 105 (p < 0.000001) |

    - Reading: switching provider goes with most verdict changes. This is clear for Gemma; for Qwen it isn't significant. Temperature 0 is also not deterministic on one provider: the reply text changed in 19 of 54 and 20 of 35 same-provider pairs, and Qwen's verdict changed 3 times in 54.
    - Limits: we didn't assign the routing at random, and "same provider" doesn't mean the same hardware.
    - Next, as planned by the launch session: repeat with one provider pinned (a broker change, made with a test), and repeat part of the local Lemonade lane (expected zero changes). The local repeat waits until the local lane finishes.

## 2b. Run 2 local lane (Lemonade, 4B pair), sealed 19:26:53 GMT
- Source: `run2/results/LOCAL-RESULTS-SHA256.txt`.
- Checked here at 19:28 UTC: both file hashes match the seal, the FreeTSA time is 19:26:53 GMT, and the counts below come from `score-run2-local.json`.
- Primary set 201 to 300.

| Arm or rule | False "shown" | False "contradicted" |
|---|---|---|
| Model A alone | 6 of 68 | 22 of 66 |
| Model B alone | 7 of 68 | 14 of 66 |
| Pair, R1 (run 1 rule) | 8 of 68 | 21 of 66 |
| Pair, R2 "shown needs both" (pre-registered) | 2 of 68 | 21 of 66 |
| Pair, R3 (sealed in the addendum before any local result) | 2 of 68 | 13 of 66 |

- Pre-registered headline: R2 cut false "shown" from 8 of 68 to 2 of 68 against R1, with no change in false "contradicted" (21 of 66 under both). R3 kept the 2 of 68 and also cut false "contradicted" to 13 of 66.
- Both run 2 lanes are now sealed (fast 17:42:38 GMT, local 19:26:53 GMT). That meets the HC-S release gate's condition. HC-S itself still waits on its own seal and Joshua's open calls.
- The local determinism repeat (40 items, 2 local models) is running. Its design is sealed in `noise/LOCAL-REPEAT-DESIGN.md`.

## 3. Human-check method (afternoon)
- Rater B methodology: `specs\RATER-B-METHODOLOGY-2026-10-05.md`. Tool spec v0: `specs\HUMAN-CHECK-TOOL-SPEC-2026-10-05.md`. HC-S design draft: `specs\HC-S-DESIGN-v1-DRAFT.md`.
- 242 invented practice, decoy and qualification items (`human-check-items-2026-10-05\`).
  - A second agent's blind label matched on 242 of 242.
  - The deciding line appears verbatim on 184 of 184.
  - The same deciding line was picked on 181 of 184. The 3 that differ (QB-058, QB-062, QB-111) each have two valid lines and need fixing.
  - Both agents are Claude: a person's spot-check is still needed.
