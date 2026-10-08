# Bundle 4: Counts from the AI Village record

Four result sets computed from the gated AI Village data. Counts only; no record text is included, because the data is gated by its publishers.

This bundle: 46 published files, 0.19 MB.

## What is in it

### `t13c-2026-10-04/`  T13c: do newer models check claims more?

Counts only; no AI Village text.

12 published files, 0.03 MB; 1 redacted copies.

| Result | Headline from the record | Seal |
|---|---|---|
| T13c: do newer models check claims more? | Newest against oldest third: verify p = 0.15, accept p = 0.48; verify runs from 2.2% (Gemini 2.5 Pro) to 8.8% (Claude Opus 4.5). | FreeTSA: 2 stamps, earliest 2026-10-04T16:14:15Z, latest 2026-10-04T16:15:13Z; OpenTimestamps: 1 file, 1 with a Bitcoin block in the file (blocks 969871 to 969871) |

Left out of this folder: 1 sealed originals replaced by a redacted copy; 1 OpenTimestamps backup copies (the .ots beside each is kept).

### `t18-sol-on-bank-2026-10-04/`  T18: a frozen generic checker on 120 invented items

Synthetic bank, so no AI Village text is involved.

13 published files, 0.10 MB; 2 redacted copies.

| Result | Headline from the record | Seal |
|---|---|---|
| T18: Sol's frozen generic checker on the 120 sealed bank items | "Accuracy: 40 of 120 (33.3%)." It answered "not shown" on every item; safety-critical errors none. | FreeTSA: 2 stamps, earliest 2026-10-04T20:12:09Z, latest 2026-10-04T20:14:03Z |

The file of the model's per-item outputs has a name that matches the forecast filter and is not published; its hash is in the seal list.

Left out of this folder: 2 sealed originals replaced by a redacted copy; 1 forecast and prediction files (owner's decision of 8 Oct).

### `t19-whistle-2026-10-04/`  T19: who blows the whistle, agents or humans?

Counts only; no AI Village text.

10 published files, 0.02 MB; 2 redacted copies.

| Result | Headline from the record | Seal |
|---|---|---|
| T19: who blows the whistle, agents or humans? | Humans were 303 of 15,030 engaged replies (2.0%); verify 1.3% against 5.8% for agents (p = 0.0002); the instrument was built for agent language. | FreeTSA: 2 stamps, earliest 2026-10-04T20:15:05Z, latest 2026-10-04T20:16:31Z |

The record says the instrument was built for agent wording, so humans are probably undercounted.

Left out of this folder: 2 sealed originals replaced by a redacted copy.

### `model-scorecard-2026-10-04/`  Per-model scorecard of the AI Village results

Counts per model, from the sealed results.

11 published files, 0.04 MB.

| Result | Headline from the record | Seal |
|---|---|---|
| Per-model scorecard from the sealed AI Village results | Claude 3.7 Sonnet: 44% of 3,685 claims made blind; Gemini 2.5 Pro 48% of 3,213; DeepSeek-V3.2 0% of 1,795. | FreeTSA: 2 stamps, earliest 2026-10-04T17:32:31Z, latest 2026-10-04T17:33:27Z |

Left out of this folder: nothing.

## How to check

- **Everything at once:** from the top folder run `python check_public.py`. It reads only this folder. It checks every seal list, the file names, the banned strings and the sizes, and ends with `DONE CHECK: ALL PASS`.
- **One seal list:** `cd` to the folder that holds a `*-SHA256.txt` and run `sha256sum -c --ignore-missing <list>`. A listed file that is not published (for the reasons below) is skipped by `--ignore-missing`; `WITHHELD.json` at the top records the hash each skipped file had.
- **FreeTSA time stamps (`.tsr`):** download `cacert.pem` and `tsa.crt` from freetsa.org, then `openssl ts -verify -in <file>.tsr -data <file> -CAfile cacert.pem -untrusted tsa.crt`. It should print `Verification: OK`. The stamped file is the seal list, not the files it lists.
- **OpenTimestamps (`.ots`):** `ots verify <file>.ots` with the OpenTimestamps client. A file made on 7 October may still show only a calendar attestation; run `ots upgrade <file>.ots` once online and it will pick up the Bitcoin block when one exists.

## What was left out, and why

All forecasts and predictions (Claude's, Jev's, and his) are left out: forecasts kept private by the owner's decision of 8 Oct; their SHA-256 seals remain checkable. Where a sealed file carries a forecast section, the sealed original is not published and a copy named `*.redacted.*` is published instead, with the removed parts marked; a banner at the top of each such copy gives the original's SHA-256, which is the hash in its seal list.

Other reasons, in this bundle: sealed scorers whose code carries forecast probabilities are not published (their hashes are in the seal lists); drafts, run commands, box and broker scripts, console logs and dry runs are not published; images and audio are not published; the 20-item human label sample and the fresh item banks that have not run are not part of this record; no AI Village record text is included.
