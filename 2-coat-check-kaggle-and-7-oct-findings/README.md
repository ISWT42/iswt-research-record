# Bundle 2: Coat-check runs on Kaggle, and the 7 October findings

Two update runs on the public Kaggle benchmark tasks (t5 to t8) and the dated findings note. The relay and screen tests of the same night are in bundle 1 (already public).

This bundle: 61 published files, 0.62 MB.

## What is in it

### `kaggle-coat-check-update-2026-10-07/`  Kaggle coat-check update: tasks t5 and t6

The same small models as the earlier Kaggle benchmark, but now each is handed a ticket written before the work (the check, and what "done" means) and must quote the line that settles it. Four models, three counted runs each. The runner, the analysis code, the sealed task files and the seals are here.

36 published files, 0.31 MB.

| Result | Headline from the record | Seal |
|---|---|---|
| Kaggle coat-check update: tasks t5 and t6 on four models | Never-ran logs called "done" after the do sentence (T3): Gemini 3.7 Flash 11 of 16, Gemini 3.8 Flash 5, Claude Haiku 4.5 10, GPT-5.4 nano 16; with a coat-check ticket (t6): 0, 0, 0 and 1. | FreeTSA: 4 stamps, earliest 2026-10-07T18:11:00Z, latest 2026-10-07T20:19:19Z; OpenTimestamps: 4 files, 1 with a Bitcoin block in the file (blocks 970376 to 970376), 3 still pending |

Limit in the record: the ticket states the expected value, which makes the question easier. The blind version is in the next folder.

Left out of this folder: 9 left out by the plan (drafts, box and broker files, logs, working files); 8 images, audio and caches; 1 OpenTimestamps backup copies (the .ots beside each is kept); 1 forecast and prediction files (owner's decision of 8 Oct).

### `kaggle-coat-check-blind-2026-10-07/`  Blind coat-check: tasks t7 and t8

The same test with a ticket that names only the check, not the answer.

24 published files, 0.30 MB; 1 redacted copies.

| Result | Headline from the record | Seal |
|---|---|---|
| Blind coat-check: tasks t7 and t8 (the ticket names only the check) | Never-ran logs called "shown" with a ticket that names only the check (t8): Gemini 3.7 Flash 0, Gemini 3.8 Flash 0, Claude Haiku 4.5 0, GPT-5.4 nano 0; mean receipt score 1.000 for all four models on both blind tasks. | FreeTSA: 3 stamps, earliest 2026-10-07T20:54:59Z, latest 2026-10-07T23:47:51Z; OpenTimestamps: 3 files, 1 with a Bitcoin block in the file (blocks 970397 to 970397), 2 still pending |

Limit in the record: the job sentence still states the target in 10 of the 16 jobs; one set of 48 known logs; four small models.

Left out of this folder: 6 left out by the plan (drafts, box and broker files, logs, working files); 1 sealed originals replaced by a redacted copy; 1 OpenTimestamps backup copies (the .ots beside each is kept); 1 forecast and prediction files (owner's decision of 8 Oct).

### `findings-2026-10-07/`  Findings of 7 October (sections 1, 2, 4, 5)

The dated findings note for the coat-check family: the update, the OpenAI harness pair, the relay test and the blind test. Counts first, plain meaning after. The anecdote section (3) is not published, and the forecast scorecard lines are removed.

1 published files, 5 KB.

| Result | Headline from the record | Seal |
|---|---|---|
| Findings, 7 October 2026 (coat-check family) | The ticket does not need to hand over the answer: blind-ticket never-ran "shown" 0, 0, 0, 0 against 11, 5, 10, 16 under the do sentence. | no seal files of its own |

This note is a working record, not sealed; every count in it names the sealed record it rests on.

Left out of this folder: nothing.

## How to check

- **Everything at once:** from the top folder run `python check_public.py`. It reads only this folder. It checks every seal list, the file names, the banned strings and the sizes, and ends with `DONE CHECK: ALL PASS`.
- **One seal list:** `cd` to the folder that holds a `*-SHA256.txt` and run `sha256sum -c --ignore-missing <list>`. A listed file that is not published (for the reasons below) is skipped by `--ignore-missing`; `WITHHELD.json` at the top records the hash each skipped file had.
- **FreeTSA time stamps (`.tsr`):** download `cacert.pem` and `tsa.crt` from freetsa.org, then `openssl ts -verify -in <file>.tsr -data <file> -CAfile cacert.pem -untrusted tsa.crt`. It should print `Verification: OK`. The stamped file is the seal list, not the files it lists.
- **OpenTimestamps (`.ots`):** `ots verify <file>.ots` with the OpenTimestamps client. A file made on 7 October may still show only a calendar attestation; run `ots upgrade <file>.ots` once online and it will pick up the Bitcoin block when one exists.

## What was left out, and why

All forecasts and predictions (Claude's, Jev's, and his) are left out: forecasts kept private by the owner's decision of 8 Oct; their SHA-256 seals remain checkable. Where a sealed file carries a forecast section, the sealed original is not published and a copy named `*.redacted.*` is published instead, with the removed parts marked; a banner at the top of each such copy gives the original's SHA-256, which is the hash in its seal list.

Other reasons, in this bundle: sealed scorers whose code carries forecast probabilities are not published (their hashes are in the seal lists); drafts, run commands, box and broker scripts, console logs and dry runs are not published; images and audio are not published; the 20-item human label sample and the fresh item banks that have not run are not part of this record; no AI Village record text is included.
