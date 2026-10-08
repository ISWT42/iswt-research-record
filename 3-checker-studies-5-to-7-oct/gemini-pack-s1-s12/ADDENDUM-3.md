# Addendum 3: two more specs, S6 and S7 (written 2026-10-06 03:55 UTC)

This adds `S6-TOLD-OR-FELT.md`, `S7-REMINDER-AT-DECISION.md` and `inputs/s6-items.jsonl`, which both use. Everything else in the pack, Addendum 1 and Addendum 2 stands.

- **Order:** after S2, run S6, then S7, each with its own report.
- **Spend:** only after the owner's yes in this session. Stop at US$15 reported cost for S6 and US$12 for S7. The key's own cap is US$30 for everything.
- **Models:** the ten listed in S6, in that order, with `max_tokens` 2000. The request body is otherwise as in the README. If a reply carries reasoning anyway, keep it in the record.
- **S6 requests:**
  - The system prompt is S1's sealed text for the arm's prompt (A0, A1 or A2, as S6's table says).
  - The user message is S1's user template, with `<goal>` filled in and the arm's log text (`log_text` or `log_text_felt`) in place of `<log_text>`.
- **S7 requests:**
  - The system prompt is S1 A0.
  - The user message is S1's user template with `log_text`. For R1 to R3, add a blank line and then the reminder block exactly as S7 gives it. R0 has no block.
- **Repeats and order** follow Addendum 2's method. The base list is items in file order, then arms in table order, then models in the order S6 lists them.
- **Recording:** as for S1. Record `status` (and `line` where the arm asks for it) parsed from the reply, plus OpenRouter's `id`, `provider` and `usage` for every call.

The SHA-256 of this file, the two specs and the input file is in `ADDENDUM-3-SHA256.txt`, sealed by FreeTSA.
