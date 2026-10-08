# Public research record, 8 October 2026

By Joshua Bauer (ISWT42). This is the public copy of the sealed studies from 3 to 8 October 2026, made so that anyone can check the counts against the files that were sealed before the runs. First published 8 October 2026 (bundles 1 to 6; archived on Zenodo, DOI 10.5281/zenodo.23227858). Bundle 7, the Earned Agency Bench, was added later on 8 October 2026 (this release has its own version DOI on Zenodo, under the same concept DOI 10.5281/zenodo.23227857). There are 101 OpenTimestamps proofs in this record. 100 carry a Bitcoin block. The one still waiting is the proof for the bench's results seal (bundle 7).

## In plain words

Can an AI agent's "done" be trusted? The studies here ask when it can, when it cannot, and what a checker has to look at before it says so. Small models and a few large ones are given invented logs and claims. Every study was written down and sealed before it ran. The numbers are counts with their denominators, misses sit beside hits, and what was learned later is marked as exploratory.

## The method, in five lines

1. Write the test down first: design, inputs, scorer, the checks. Seal it: a SHA-256 list, a FreeTSA time stamp and an OpenTimestamps (Bitcoin) proof.
2. Run it and keep every raw call.
3. Seal the raw results (and the scorer, if it was not sealed already) before anything is counted.
4. Count with the sealed scorer. Report counts with denominators; show misses beside hits; label anything worked out afterwards as exploratory. Corrections are dated addenda; sealed files are never edited.
5. An agent's own report is never evidence. Only a record the agent could not change counts, and a claim is "shown" only when a line in that record shows it, quoted word for word. The other answers are "contradicted" and "not shown".

## What is here

| Bundle | What it is | Headline from the record | Seal |
|---|---|---|---|
| [1-coat-check-receipts](1-coat-check-receipts/) | The coat-check screen and relay tests (7 Oct). Not copied: already public on Kaggle. | Relay: false "done" at the end, "A self-report 16, B ticket and self-fix 7" of 36 per arm, p = 0.0039 | FreeTSA 2026-10-07T21:29:16Z to 23:46:01Z |
| [2-coat-check-kaggle-and-7-oct-findings](2-coat-check-kaggle-and-7-oct-findings/) | Kaggle tasks t5 to t8 and the 7 Oct findings note | Never-ran logs called "shown" with a ticket that names only the check: 0, 0, 0, 0 of 16, against 11, 5, 10, 16 under the do sentence | FreeTSA stamps 2026-10-07T18:11:00Z to 2026-10-07T23:47:51Z; Bitcoin blocks 970376 to 970397 where confirmed in the file |
| [3-checker-studies-5-to-7-oct](3-checker-studies-5-to-7-oct/) | Studies S1 to S12 with answer keys and results, and the follow-up runs and findings records | S9: "Qwen 3.5 9B: one call 39 false "shown" and 35 true kept; all five agree 13 and 28" | FreeTSA stamps 2026-10-05T17:49:32Z to 2026-10-07T20:18:43Z; Bitcoin blocks 969745 to 970191 where confirmed in the file |
| [4-ai-village-counts](4-ai-village-counts/) | T13c, T18, T19 and the model scorecard: counts from the gated AI Village record | T19: humans were 303 of 15,030 engaged replies (2.0%); the instrument was built for agent language | FreeTSA stamps 2026-10-04T16:14:15Z to 2026-10-04T20:16:31Z; Bitcoin blocks 969871 to 969871 where confirmed in the file |
| [5-designs-and-statements](5-designs-and-statements/) | Designs sealed before they ran, and statements in his words | See the folder READMEs | FreeTSA stamps 2026-10-04T04:45:10Z to 2026-10-07T21:36:06Z; Bitcoin blocks 969781 to 970196 where confirmed in the file |
| [6-seal-checks](6-seal-checks/) | The 5 Oct check of Bitcoin proofs | "82 OK (merkle roots match real Bitcoin block headers; file hashes match), 0 FAIL" | checked 2026-10-05T03:20:59Z |
| [7-earned-agency-bench-2026-10-08](7-earned-agency-bench-2026-10-08/) | The Earned Agency Bench, real run 1 (8 Oct): four small models, 40 games, 5 ways of handing on finished work | Arm A said done on 314 of 320 jobs and 116 of 320 were false done; checking every job against the record handed on 0 of 320 (arm C); earned routing NOT SHOWN (T1 -0.0117, p = 0.6562) | Design FreeTSA 2026-10-08T03:14:29Z (Bitcoin block 970432); results FreeTSA 2026-10-08T05:45:21Z (Bitcoin proof pending) |

Each bundle folder has its own README with the counts, the seal times and what was left out.

## Already public

- Kaggle benchmark: https://www.kaggle.com/benchmarks/iswt42/two-kinds-of-false-done (DOI https://doi.org/10.34740/kaggle/w/116515) and its evidence dataset https://www.kaggle.com/datasets/iswt42/it-quoted-the-failure-evidence
- Kaggle tasks t5 to t8: https://www.kaggle.com/benchmarks/tasks/iswt42/receipt-triplets-t5-coat-check-report/1 , .../receipt-triplets-t6-coat-check-do/1 , .../receipt-triplets-t7-coat-check-blind-report/1 , .../receipt-triplets-t8-coat-check-blind-do/1
- Coat-check receipts dataset (bundle 1): https://www.kaggle.com/datasets/iswt42/coat-check-receipts-2026-10-07
- DEV posts: https://dev.to/iswt42/it-quoted-the-failure-two-kinds-of-false-done-1ago and https://dev.to/iswt42/every-done-needs-a-receipt-3n19
- Code: https://github.com/ISWT42/swarm-receipts , https://github.com/ISWT42/receipt-pair , https://github.com/ISWT42/receipt-desk
- Pages on iswt.ca: https://iswt.ca/results/ , https://iswt.ca/projects/ , https://iswt.ca/runs/ , https://iswt.ca/entries/ , https://iswt.ca/ledger/ , https://iswt.ca/sonny-test/ , https://iswt.ca/human-words/ , https://iswt.ca/check/chain/
- Zenodo DOIs: method https://doi.org/10.5281/zenodo.23117476 ; Receipt Desk https://doi.org/10.5281/zenodo.23116560 ; swarm-receipts https://doi.org/10.5281/zenodo.23147283 ; "Every done needs a receipt" https://doi.org/10.5281/zenodo.23162835
- Demo video: https://youtu.be/Iqgn11NWwDA

## What is not here, and why

- **Forecasts and predictions** (Claude's, the decision model's, and his): kept private by the owner's decision of 8 October. Their SHA-256 seals are still in the seal lists, so the seal chain still verifies. Where a sealed design, scorer or result note held a forecast section, the sealed original is not published and a marked, redacted copy is.
- **Items not yet run or not yet labelled:** the fresh item banks, and the 20-item human-label sample (publishing them early would spoil the tests).
- **AI Village record text:** gated by its publishers. Only counts are published.
- **Personal, financial, confidential or security-sensitive items,** and items that name other people.
- **Run records that are withheld for safety,** as the public chain page says.

The full account for each folder is in the bundle READMEs, and `WITHHELD.json` lists each withheld file that a seal list names, with its hash.

## Licence

Text and data: CC BY 4.0 ([LICENSE-docs](LICENSE-docs)). Code: MIT ([LICENSE](LICENSE)). The same terms as the public swarm-receipts repository.

Contact: joshua@iswt.ca
