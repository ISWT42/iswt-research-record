# Addendum 6: S9, the wobble test (written 2026-10-06 from 13:50 UTC)

This adds `S9-WOBBLE.md`. Everything else in the pack and Addenda 1 to 5 stands.

- **Owner's yes:** "Lets run a gemini in the box test", 13:49:48 UTC.
- **Run S9 only.** S1 to S8 are finished and verified; do not run them again.
- **Code:** write the S9 runner in `runs/s9/code/`, with the standard library plus the vendored `receipt_pair` (Addendum 1), the same way as the S8 runner.
- **Order:** follow Addendum 2's method.
  - The base list is records in file order, then models in S9's order, then arms (W0, then the five W5 seeds).
  - Shuffle the whole list with one `random.Random(20261006)` instance.
  - Write the order to `runs/s9/order.json` before the first call.
- **Network:** the box now refuses every name lookup except the proxy's. Make every call through the proxy, as before; don't try to resolve names yourself.
- **Key:** `OPENROUTER_API_KEY` from the environment only. Never write it anywhere.
- **Spend stop:** US$2 for S9. The key's own cap stands.
- **Report** S9 in the README's format when it is done.

The SHA-256 of this file and `S9-WOBBLE.md` is in `ADDENDUM-6-SHA256.txt`, sealed by FreeTSA.
