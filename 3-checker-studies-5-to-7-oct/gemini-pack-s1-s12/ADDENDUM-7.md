# Addendum 7: S11 (the tuned reviewer) and S12 (forced yes-or-no on nine models) (written 2026-10-06 from 13:55 UTC)

This adds `S11-TUNED-REVIEWER.md`, `S12-FORCED-SWEEP.md`, `inputs/s12-requests.jsonl` and `inputs/s12-framings.json`. Everything else in the pack and Addenda 1 to 6 stands.

- **Owner's yes:** "Lets run a gemini in the box test" at 13:49:48 UTC, and his go to run more tests from one paste at 13:52:24 UTC.
- **Run S11, then S12**, after S9 has finished and been reported. Report each in the README's format before starting the next.
- **Code:** one runner per spec, in `runs/s11/code/` and `runs/s12/code/`, with the standard library plus the vendored `receipt_pair` where the spec uses it. Write `order.json` before the first call, and `MANIFEST.sha256` at the end.
- **Order and repeats:** follow Addendum 2's method. S11 repeats 20% of whole chains; S12 has no repeat.
- **Network:** every call goes through the proxy. The box refuses all other name lookups.
- **Key:** `OPENROUTER_API_KEY` from the environment only. Never write it anywhere.
- **Spend stops:** US$1.50 for S11 and US$4 for S12. The key's own cap stands.
- **Stop and report** if more than 5% of a spec's calls end as "no answer", if a stop is reached, or if anything is unclear (QUESTIONS.md).

The SHA-256 of this file, the two specs and the two input files is in `ADDENDUM-7-SHA256.txt`, sealed by FreeTSA.
