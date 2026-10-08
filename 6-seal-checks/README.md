# Bundle 6: Seal checks

The 5 October check of Bitcoin proofs.

This bundle: 1 published files, 9 KB.

## What is in it

### `block-check-2026-10-05/`  Block check of the Bitcoin proofs (5 Oct)

A log of 82 proofs checked against real Bitcoin block headers.

1 published files, 9 KB.

| Result | Headline from the record | Seal |
|---|---|---|
| Bitcoin block check of 82 proofs (5 Oct 03:20 UTC) | 82 OK (merkle roots match real Bitcoin block headers; file hashes match), 0 FAIL. | no seal files of its own |

Left out of this folder: nothing.

## How to check

- **Everything at once:** from the top folder run `python check_public.py`. It reads only this folder. It checks every seal list, the file names, the banned strings and the sizes, and ends with `DONE CHECK: ALL PASS`.
- **One seal list:** `cd` to the folder that holds a `*-SHA256.txt` and run `sha256sum -c --ignore-missing <list>`. A listed file that is not published (for the reasons below) is skipped by `--ignore-missing`; `WITHHELD.json` at the top records the hash each skipped file had.
- **FreeTSA time stamps (`.tsr`):** download `cacert.pem` and `tsa.crt` from freetsa.org, then `openssl ts -verify -in <file>.tsr -data <file> -CAfile cacert.pem -untrusted tsa.crt`. It should print `Verification: OK`. The stamped file is the seal list, not the files it lists.
- **OpenTimestamps (`.ots`):** `ots verify <file>.ots` with the OpenTimestamps client. A file made on 7 October may still show only a calendar attestation; run `ots upgrade <file>.ots` once online and it will pick up the Bitcoin block when one exists.

## What was left out, and why

All forecasts and predictions (Claude's, Jev's, and his) are left out: forecasts kept private by the owner's decision of 8 Oct; their SHA-256 seals remain checkable. Where a sealed file carries a forecast section, the sealed original is not published and a copy named `*.redacted.*` is published instead, with the removed parts marked; a banner at the top of each such copy gives the original's SHA-256, which is the hash in its seal list.

Other reasons, in this bundle: sealed scorers whose code carries forecast probabilities are not published (their hashes are in the seal lists); drafts, run commands, box and broker scripts, console logs and dry runs are not published; images and audio are not published; the 20-item human label sample and the fresh item banks that have not run are not part of this record; no AI Village record text is included.
