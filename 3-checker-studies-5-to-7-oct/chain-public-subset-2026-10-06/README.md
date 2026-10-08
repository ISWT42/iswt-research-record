# The chain-of-agents test: the public subset (6 October 2026)

What's here can be shown without opening the half that stays closed for safety: the agent prompts, the planted faults, the order of the hops, and any way around the check.

| Folder | What the fingerprint list covers | Stamp |
|---|---|---|
| `1-hosted-plan` | the test pack: specs, models, rules and item files (14 files) | FreeTSA, 03:07:46 GMT, 6 Oct 2026 |
| `2-answer-key-seal` | the answer keys: the planted truth per item, stamped before the hosted results | FreeTSA, 03:07:47 GMT |
| `3-hosted-results` | the hosted run's manifest (calls, order, runner); the manifest itself is included | FreeTSA, 04:10:43 GMT |
| `4-pc-plan` | the run on my PC: design, runner, scorer, items, the checker's code | FreeTSA, 09:08:24 GMT; Bitcoin block 970158 |
| `5-pc-results` | the PC run's three result files | FreeTSA, 13:30:22 GMT; Bitcoin block 970180 |

- **`TOKENS.txt`** prints what each FreeTSA token says. The stamped fingerprint must equal the fingerprint of the file beside it, and anyone can compare those by eye.
- **`SCORING-RULE.md`** gives the scoring rule in full.
- **`HOP-EXAMPLE.md`** is one hop, redacted: an illustration, not a receipt.

## How to check

- **FreeTSA:** download `cacert.pem` and `tsa.crt` from freetsa.org, then run:
  `openssl ts -verify -in <file>.tsr -data <file> -CAfile cacert.pem -untrusted tsa.crt`
  It should print "Verification: OK".
- **Bitcoin (folders 4 and 5):** with the stamped file beside its proof, run `ots verify <file>.ots`, or upload both at opentimestamps.org. The proof stamps the fingerprint list itself, not a later note.

## What these files show, and what they don't

- **Shown:** each fingerprint list existed, unchanged, at its stamped time, and two of them are anchored in Bitcoin. The answer key's list was stamped at 03:07:47 GMT, before the hosted results list (04:10:43 GMT); that it came before the first model call is not shown by these files.
- **Not shown by these files alone:**
  - that the lists match the closed files;
  - that the record holds 90 jobs and 60 false "done"s.

  Checking either one means opening files that hold the closed half. Each seal covers a whole file, so a redacted copy can't be checked against it.
- **The fix, from the next run on:** each record gets its own fingerprint inside the seal. Then one record can be opened and checked while the rest stay closed.
