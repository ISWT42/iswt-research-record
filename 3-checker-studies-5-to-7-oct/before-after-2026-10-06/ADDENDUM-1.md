# S8b addendum 1: the code, the hosted lane and his yes (written 2026-10-06, from 11:40 UTC)

Sealed before the first model call. The design (DESIGN.md, FreeTSA 11:34:55 GMT) stands. This adds the code and pins three details.

## His yes to spend
- 11:36:45 UTC, "On my yes". I asked whether that meant go or hold.
- 11:37:10 UTC, ":-)".
- 11:37:37 UTC, **"Yes, spend"**.

So the hosted lane runs, with a stop at US$2.00 reported cost. The estimate is about US$1.20.

## Details pinned here
1. **B1-blank's block, exact text:** 'Answer "shown" only if a line in the turns shows the claimed outcome for the claimed object, and quote that line. Answer "contradicted" only if a line shows that it failed. Otherwise answer "not shown".'
   - The design changed only "matches that receipt". "Matches the failure" had to change too, because the failure line is gone in this arm.
2. **The hosted lane:**
   - **Route:** the AI broker's `openrouter-plain` provider, which sends reasoning off, temperature 0, seed 42, `max_tokens` 400 and `data_collection` deny, the same body as the pack.
   - **Calls:** 4 at a time.
   - **Units:** 560 (280 records x 2 models), plus 112 repeated whole units drawn with `random.Random(20261006)`, then the whole list shuffled (Addendum 2's method).
   - **Phase 1** is 672 calls and **phase 2** is 3,360, so 4,032 calls in all.
3. **The local lane:** Qwen3-4B on Lemonade, 280 units with no repeat, one call at a time. It runs after the local chain test.

## Checks run before sealing (11:40 UTC)
- **Requests:** `python run_s8b.py check` rebuilt all 2,016 of S8's hosted requests byte for byte (672 commitments, 672 B0, 672 B1).
- **Input:** `inputs/s8-items.jsonl` has sha256 5310cb9b…6e9, equal to the hash sealed with Addendum 4 of the pack.

## Files sealed with this addendum
`ADDENDUM-1.md`, `run_s8b.py`, `score_s8b.py`, `inputs/s8-items.jsonl` and `vendor/receipt_pair/*.py`. Their hashes are in `ADDENDUM-1-SHA256.txt`.
