# E1 addendum 1: how a call with no usable reply is counted, and one slot per call

Written by Claude (Sonnet 5.5) at 2026-10-06T00:41:49Z (read with `date -u` in the same step as the seal). The design allows this kind of change ("Allowed changes while writing"); this is its dated addendum, hashed and stamped before the next writer call.

## What happened

The writer started at 00:38:23Z (its log). I stopped it myself at 00:40:06Z, before its own stop rule fired.
- 13 calls are in the call log. 9 of them gave a reply: 17 items kept, 1 dropped (reason code `deciding_line_partial`).
- 4 calls gave no usable text: 3 were cut at the 4,000-token output limit while the model was still reasoning (finish reason `length`), and 1 ended normally (finish reason `stop`) with no usable text.
- The writer counted those 4 as failed calls, not as tries. Its rule "stop after 8 calls that fail without any reply" would have fired after a few more, and the same pairs would have been asked again as pairs.
- 3 more calls were in flight when I stopped it. They are in the broker's ledger but not in the call log, so their slots will be asked again.
- Hosted spend at the time of writing, by the broker's ledger: US$0.0330 over 17 runs (the plumbing test included).

I looked at no raw reply. Everything above comes from the call log (finish reasons, token counts, reason codes).

## The change

1. A call that the model answered but that gave no usable text counts as a try for its slots, with the reason code `empty_reply` (or `truncated_reply` when cut at the limit). The 4 earlier calls of this kind are counted as tries too and named in the drop log (`e1/e1-drops.jsonl`, marked "counted by addendum 1").
2. One slot per call, from the first try (it was two). A pair needs about twice the reasoning budget, and 4 of 13 pairs ran out of it.
3. "Stop after 8 calls without any reply" now counts only calls the provider never answered.

## What does not change

The plan (`e1-schedule.json`), the specification, the keep rules, the 4 tries per slot, the reserves, the US$0.50 cap, the pause file, the model and the broker settings. The 17 kept items stay. The sealed `code/e1_generate.py` is not edited: `code/e1_generate2.py` patches it when it runs, and the sealed design still checks out.

## Files sealed with this addendum

`E1-ADDENDUM-1.md`, `code/e1_generate2.py`. Their hashes are in `E1-ADDENDUM-1-SHA256.txt`, which FreeTSA stamps. `e1_generate2.py` refuses to run unless that seal is in place and matches.
