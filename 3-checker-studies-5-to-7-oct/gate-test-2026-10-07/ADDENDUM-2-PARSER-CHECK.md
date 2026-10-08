# The gate test, dated addendum 2: every reply re-read with the parser audit's reference rule (7 October 2026)

Written by the coordinating session after the results seal (09:45:44 GMT), the scoring (09:46:16 GMT) and the parser audit's seal (10:19:17 GMT). Its time is the FreeTSA time on its seal file. Nothing sealed is changed.

- **Why:** the parser audit found that the reader rule shared by most studies fails closed on some reply shapes (two objects, a stray brace). The audit could not open these results before they were sealed, so it checked this runner's parser on invented replies only.
- **What was done:** `reparse_gate_reference.py` reads all 180 checker replies (field "verdict") and all 1,080 reviewer and release-manager replies (field "decision") with the audit's reference rule (`Private/claims/parser-audit-2026-10-07/ref_rule.py`).
- **Result:** 0 disagreements. Checks 180 of 180, reviewers 540 of 540, release managers 540 of 540 read the same as the sealed run.
- **What it means:** the gate test's counts carry no parsing caveat.
