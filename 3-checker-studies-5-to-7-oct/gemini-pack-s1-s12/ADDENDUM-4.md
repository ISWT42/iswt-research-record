# Addendum 4: S8, receipt first (written 2026-10-06 04:18 UTC)

This adds `S8-RECEIPT-FIRST.md` and `inputs/s8-items.jsonl`. Everything else in the pack and in Addenda 1 to 3 stands.

- **Order:** after S7, run S8, with its own report.
- **Spend:** only after the owner's yes in this session. Stop at US$2 reported cost.
- **Models:** the S4 pair, `qwen/qwen3.5-9b` and `google/gemma-4-26b-a4b-it`, with the README's request body. The commitment call (B1 step 1) uses `max_tokens` 400.
- **B1, two calls per record and model:**
  - **Step 1:** S8's system prompt for the commitment, and the user message `CLAIM: "<claim>"`. No turns are sent.
  - **Step 2:** `request.system` and `request.user` from `receipt_pair.pair.prepare`, with S8's block inserted before the last line `Answer with JSON only.`. Fill `<receipt>` and `<failure>` with step 1's JSON fields exactly as returned. If step 1's reply is not valid JSON, use its raw text for `<receipt>` and `none` for `<failure>`, and record that.
  - Check every step 2 reply with `receipt_pair.reader.verify`, the same as B0.
- **Repeats and order** follow Addendum 2's method. The base list is records in file order, then arms (B0, then B1), then models in MODELS.json order. A drawn B1 repeat repeats both of its steps.
- **Recording:** as for S4. For B1, also record `step` (1 or 2) and the commitment text that went into step 2.

The SHA-256 of this file, the spec and the input file is in `ADDENDUM-4-SHA256.txt`, sealed by FreeTSA.
