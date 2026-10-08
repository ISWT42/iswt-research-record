# Bundle 1: coat-check receipts (already public on Kaggle)

This bundle is **not copied here**. It is the Kaggle dataset **Coat-check receipts, 7 Oct 2026**:

https://www.kaggle.com/datasets/iswt42/coat-check-receipts-2026-10-07

It holds the sealed designs, the raw calls, the scorers and the seals of two tests run on 7 October 2026:

- `screen/`: the coat-check screen. Eight ways of asking one model (Gemini 3.7 Flash through its command line, every tool denied) to report on the 48 public logs of the Kaggle benchmark, 1,152 calls. Headline in the record: on never-ran logs the coat-check wording against the did-the-work wording, "first only 0, second only 6, p = 0.03125".
- `relay/`: the coat-check relay. Twelve real coding jobs with hidden tests, four small models, four arms, 36 jobs per arm. Headline in the record: false "done" left at the end, "A self-report 16, B ticket and self-fix 7, C certify-before-work 11, D work-then-certify 9; A against B 9 against 0, p = 0.0039".

Seals (from the record): screen, FreeTSA stamps from 2026-10-07T15:35:33Z to 2026-10-07T16:43:10Z; relay, FreeTSA stamps from 2026-10-07T21:29:16Z to 2026-10-07T23:46:01Z. The OpenTimestamps proofs for both were pending a Bitcoin block when this record was first staged; they have since been upgraded (see the dataset copy).

To check it, download the dataset and run `sha256sum -c SHA256SUMS.txt` in its top folder, then `sha256sum -c` on each `*-SHA256.txt` inside `screen/` and `relay/`.

The forecasts of these two tests are in the dataset's sealed files; this record does not republish them.
