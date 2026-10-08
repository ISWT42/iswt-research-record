> Published copy. The sealed original `DESIGN.md` (SHA-256 `05294fb739dff302bdbfccc0d233d4e2b25a5b8803d297c9515e80813d03369c`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# T18: an independent checker on an independent exam (design, sealed before any run; written 4 Oct 2026 from 20:12 UTC)

**His words:** "Of course, you can naturally start agents and tasks." (agent-queue node: "An independent checker built from the public description (Sol)").

## What is tested
Sol 6.1's frozen generic checker (`receipt_checker.py --mode generic --trust-record`, from `Documents\Codex\2026-10-04\you-are-an-independent-engineer-from\outputs`). Its rules were frozen and fingerprinted by its author before this exam existed in its session. It has never seen these items.
- `receipt_checker.py` SHA-256: recorded in `CHECKER-SHA256.txt` with this seal.
- `generic_checker.py` SHA-256: recorded likewise.

## The exam
The 120 sealed bank items (`Workbench\chatgpt-review-2026-10-04\JOB3-BATCH-1..3.jsonl`, FreeTSA 19:06:56, 19:25:35 and 19:48:38 UTC). The checker gets only `id`, `claim` and `turns` (cmd, output, narration). Truth, deciding line and reason are withheld.

## Measures
- Accuracy overall, by truth class, and by batch (1: narration and traps; 2: decoys and ordering; 3: retries).
- The confusion matrix.
- **Safety-critical errors:** false `shown` (a failure or unbacked claim certified) and false `contradicted` (an accusation the record doesn't support). Each listed by id.
- Deciding-line agreement: for conclusive answers that match the truth, the share whose deciding line equals the bank's exactly.
- Batch 3 also under the alternative retry rules (v3's "a relevant failure wins" and abstention), as a sensitivity note only. The primary score uses the bank's convention.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Rules
- The checker and its inputs are fixed before the run. No reruns with changed settings.
- Counts and ids only in any public note. The bank is synthetic, so no AI Village text is involved.
- The run starts at least 15 s after the FreeTSA stamp.
- Exploratory: one model family wrote both the bank and the checker, in separate sessions.
