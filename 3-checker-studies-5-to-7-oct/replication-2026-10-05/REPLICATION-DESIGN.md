# Replication on a second author's items (sealed design, 5 Oct 2026)

Written by the coordinating Claude session from 18:52 UTC on 5 Oct 2026 (clock), while Joshua is away ("act autonomously for the next 30-60 testing", 18:46:19 UTC). Sealed before the items exist: a separate Claude agent (Sonnet) is writing them now, blind to Sol's bank.

## Why
Every finding today rests on 140 items written by one model (Sol, GPT). This design checks whether the main findings point the same way on 40 items written blind by a different model family (Claude), using the same specification.

## Items
- **The items:** `items-R001-R040.jsonl`, plus `followups-R001-R040.jsonl` for the loop.
- **Before any model call:** both files are hashed and stamped by FreeTSA, then checked by script (counts only):
  - 40 lines each, matching ids;
  - truth about 13 each way;
  - every deciding line a whole output line;
  - world consistent with truth;
  - no check command flagged by `run3.UNSAFE`.

  An item with any problem is left out and named.

## Arms
Pinned providers through openrouter-plain: `qwen/qwen3.5-9b@SiliconFlow` and `google/gemma-4-26b-a4b-it@Darkbloom`.
1. **Reader (run 2's prompt):** each model alone; the pair under R1, R2 and R3.
2. **Certainty (run 3's prompt and CERTAINTY instruction):** calibration, and settle proposals with the gate.
3. **The pair loop:** stage 2e's pipeline, unchanged, on the certainty answers, with the replication follow-ups.

## Replication criteria (directions, stated before the run)

| # | Criterion | My p that it holds |
|---|---|---|
| F1 | The pair under R3 gives fewer false "shown" than under R1. | 0.75 |
| F2 | Each model marks "unsure" on at most 4 of 40. | 0.7 |
| F3 | Each model is wrong on at least 20% of its "sure" answers. | 0.5 |
| F4 | At least 1 settle proposal across both models is flagged by the gate. | 0.6 |
| F5 | The pair loop is right on at least as many items as each model alone with run 2's prompt. | 0.6 |
| F6 | The pair loop's false "shown" is at most each model's own with run 2's prompt. | 0.7 |

**Scoring the replication.** A finding counts as replicated when its criterion holds. With 40 items this is a check on direction, not on size, and every count is reported.

## Budget
A cap of US$3; the estimate is under US$0.05. Two retries, then "no answer". Every results file is hashed and stamped by FreeTSA before anyone reads it.

## Honest limits
- 40 items.
- A Claude agent wrote them, so they are not human-written.
- The pinned-provider noise (Qwen changed 22 of 140 verdicts between identical pinned runs) is large compared with 40 items.
