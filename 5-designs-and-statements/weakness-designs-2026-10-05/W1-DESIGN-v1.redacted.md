> Published copy. The sealed original `W1-DESIGN-v1.md` (SHA-256 `d66811f4f018b62031c21594e62fef73d9e2666f12540a2e095890890fce42c3`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: box host/account names and a city name replaced.

# W1 design v2: human ground truth for E3's labels (HGA)

## 0. Header

| | |
|---|---|
| Design id | HGA-W1-2026-10-05-v2 (replaces v1, never sealed) |
| Status | DRAFT FOR SEAL; nothing run |
| Written by | Claude (drafter) and reviewed adversarially, for Joshua Bauer (ISWT42), 5 Oct 2026. No clock time is written in this file; the stamps carry the times. |
| Rules in force | AGENTS.md rules version 2026-09-30.1, every hard limit, every step. No gated text is shown to any AI. No network without a yes. Nothing keeps running after a task ends. No file name in this work contains auth, token, key, secret or credential (the answer map is map-answers, rater logins are rater codes). |
| Seal method | SHA-256 file, FreeTSA RFC 3161 reply, OpenTimestamps proof. Each stamp waits for his yes. Only hashes leave the PC. The manifest is frozen once hashed; the first FreeTSA reply obtained for it is the one used; every stamp request is written to the ledger. Every submission goes into a hash-chained ledger. |

**Files read by the drafter and the reviewer (no file under Data was opened):** WEAKNESS-PLANS-2026-10-05.md (sections 4, 6 W1, 8, 9); GATHERING-PATHS-2026-10-05.md (W1 path); OUTSIDE-REVIEW-BIGGER-2026-10-05.md (bars 3 and 4); gate4-prep GATE4-DESIGN-DRAFT.md; swarm-receipts-public audit files (G3-DESIGN.md, LABELLER-PROMPTS.md, CORRECTIONS-2026-10-04.md, the claim-spotting label files, WRITEUP.md lines 231 and 248); launch package PRESS-KIT.md line 65. Named by the plan, not opened: the gate 2 design and capsule manifest; make_g3.py; score_g3.py; check_inputs.py; make_bundle_manifest.py; START-RULE-CHANGE-2026-10-03.md; the 4 Oct tooling; receipts_io.safe_value; receipts_model.seen_text; kaggle-v3/the-48-logs.jsonl; swarm-receipts-public/fixtures/. Their facts below are quoted from the plan and are not checked. The agent reads from a folder outside the standing list only after he names it (step 1.0).

**Any change after the seal is a new version, sealed before the step it affects; sealed files are never edited.**

### Terms

| Term | Meaning |
|---|---|
| E3 | The model-reader checker tests: gate 2, gate 3 and the claim-spotting sample. |
| Key | The sealed answer for an exam item: made by Claude Sonnet (two passes agreeing) for the 200 keyed items; by script for the 100 no-record items. |
| SHW (plan S) | Planted success receipt. Key at Q2: shown. 100 items (50 gate 3, 50 gate 2). |
| CON (plan C) | Planted failure receipt. Key at Q2: contradicted. 100 items (50 + 50). |
| NON | No-record item. Key not shown, by script. 100 items. Not rated by people. |
| UNC (plan N) | Turn the first labelling pass called unclear. One pass only. Q1 only. |
| SPL (plan D) | Turn where the two passes split. 21 items. Q1 only. |
| DEC (plan M) | Mismatch decoy: a real unused turn with an invented-object swap and a claim naming a different invented object. Answer is not shown by construction. |
| DUP | Duplicate presentation of an earlier item, for test-retest. Not used in H. |
| Q1 / Q2 | Stage 1: command and output only, success, failure or unclear. Stage 2: claim shown, shown, contradicted or not shown. |
| A, B, C | A is Joshua (author). B is the first outside rater. C is the second outside rater and adjudicator. |
| H | Final human key, formed by the rule in 4.1. |
| Seen items | The 20 gate-3 turns (10 SHW, 10 CON) already in the 4 Oct sample (sample_id d3a32a80ea4a5f53), plus 20 of the 200 claim-spotting messages. |
| Verdict kappa | Three-class Q1 kappa between A and B on the 240 core reliability pairs (phases 1 and 2); on phase 2 alone (130 pairs) if the guide was revised after phase 1. |

## 1. Hypothesis

His words that bear on it: 'The labels: the ground truth for gates 2 and 3 and the claim-spotting sample were labelled by models (Claude and Claude Sonnet), each with a blind second pass, not by humans. A blind sample for people to label is sealed. The labellers and the tools that built the checker come from one model family, so they may share blind spots.' (WRITEUP.md, line 231). Method instructions, not claim text: 10:27 UTC on 5 Oct (as quoted in the plan, section 9) and 11:35 UTC on 5 Oct (relayed): 'in parallel, we need to work on the experiments needed and the methodology to collect'. No sentence of his states the W1 claim in test form; he may add one before the seal.

**Testable form.** Blind human consensus H, formed by Joshua and two outside raters from the same command-and-output evidence the model labellers saw, agrees with E3's AI-made answer key on at least 190 of the 200 keyed planted items (100 key-shown, 100 key-contradicted; at least 90 of each 100; at most 2 of the 100 key-shown items judged contradicted), and the one checker that passed gate 3 (gemma4:12b) still passes when its sealed answers are rescored against H. Decision by the count lines in 5.5. Two secondary questions are pre-registered and reported whatever they show: lane A (do public raters and the model labelling method read logs alike; it does not check E3's key) and phase 4 (do people agree with the claim-spotting consensus).

## 2. Arms

### 2.1 Rating streams

| Stream | Who | Rates what | Blind to | Counts in H | Limits |
|---|---|---|---|---|---|
| A, author, in-house | Joshua | Every presentation of each phase, alone | Map, key, model labels, checker answers, B and C | Yes, except the 20 seen turns | Never counted as independent; every headline also reported with B alone and with B and C only. After an early map open (author-only path) A is not blind and the interim is final for this design. |
| B, outside (lane B) | First person who accepts within 14 days and passes rehearsal within 7 more | Every presentation of each phase, alone | Same, and A | Yes | Needs own approved AI Village access or the publishers' written OK. Declares any tie. |
| C, outside (lane B) | Second such person | (i) every item where A and B differ at Q1 or Q2; (ii) the 20 seen turns; (iii) 10 C-decoys, mixed in a sealed order with no label | A, B, key, map | Yes: tie-break; seen turns | Rates blind. Never discusses an item with A or B. Reads only about a fifth of the items, so the pass sentence says one outside person reads in full and a second decides disputes. |
| Extras B2, B3 | Other credentialed people who ask | Same sheet as B | Same | No: own table | Volunteers only, no pay. |
| Pilot P (4 Oct) | Joshua | The 40-item sample | Not blind to his own earlier ratings; AI-reviewed afterwards | No | Excluded from every confirmatory analysis (3.5). |
| Synthetic scripted raters | Code | Synthetic items only | n/a | No | Tool tests only: accuracy 0.95, 0.90, 0.80, oracle, identical, random. |
| Lane A streams | Anyone 18 or over, on public excerpts | 14 counted excerpts and 6 checks per set | Model labels, class, which items are checks | No | Separate line. Independent stream is primary; tied, author and agent streams count as zero toward any floor. |

### 2.2 Held fixed in every arm

- **Guide.** RATER-GUIDE.md v1: the pass-2 outcome definitions of LABELLER-PROMPTS.md (success, failure, unclear, with the already-in-place example), both claim readings, the no-AI-tools rule.
- **Page.** Two stages. Q1 locks before the claim appears. Stage 2 only for SHW, CON and DEC; UNC and SPL stop after Q1. At Q1 the rater picks the deciding line (the page checks it is a verbatim substring of the OUTPUT) and a confidence of low, medium or high. At Q2 the rater answers shown, contradicted or not shown. A shown answer carries a tick 'claim says more than the record shows'. A not-shown answer takes one reason from a fixed list. Optional tick 'read this log before today'. A skip button. Sessions of at most 60 items. Time per item and position are logged.
- **Claim readings.** Primary (every Q2 answer): judge the main verb and object; details count only if the OUTPUT contradicts them. Strict (derived): a shown answer with the tick is read as not shown.
- **Evidence.** Command and output as the model saw them, through safe_value and seen_text, without the 500 and 1,000 character caps. The builder prints counts of items that lost text in the model's view and items dropped as confidential.
- **Never shown to a rater:** case id, gate, group, family, stratum, model labels, checker answers, timestamps, total count, other raters' answers.
- **Returned file.** Ids, answers, fixed-list reasons, confidence, ticks, line index and a hash of the chosen line, times, positions. No item text, no free-text note.
- **Rater terms and ethics (RATER-AGREEMENT.md).** Aged 18 or over; consent in writing; told what is logged (answers, times and positions under an anonymised rater code; no IP; the page makes no network call); retention and deletion stated; alone; no AI tool, ever; hourly pay with no bonus for agreement, paid for time worked even on early stop; told that disagreeing with the labels is wanted; may stop at once or skip any item; payment details are handled outside this folder. Both claim readings are honest descriptions of the same page; nothing about the page differs between raters.
- **Code and bars.** Scorer, stats code, simulation scripts, lines and decision table are frozen at Seal 1.

### 2.3 Randomisation and the seed rule

- **Seed.** The first 16 hex digits of the SHA-256 of SEAL1-MANIFEST.txt as stamped, read as a base-16 integer (manifest frozen once hashed). Seed grinding is limited: SHW, CON and SPL are censuses; the seed chooses only the UNC and DEC draws, 5 duplicates a phase, and the orders.
- **Sub-seed.** First 16 hex digits of the SHA-256 of the text {seed}:{label}.
- **Hash-sort rule.** Every draw sorts the candidates ascending by the SHA-256 of {sub-seed}:{item key} and takes the first k. No library random generator is used.
- **Labels, in draw order:** ids; N:g3; N:g2; N:rest; M:g3; M:g2 (per gate the first 10 become DEC for A and B, the next 5 C-decoys); DUP:1, DUP:2, DUP:3; ORD:{phase}:{A|B|C}; BOOT.
- **Sheet ids.** First 12 hex digits of the SHA-256 of {ids sub-seed}:{item key}; 14 if any two collide.
- **Order.** One sealed order per rater per phase. Duplicates sit at least 15 places after their original; leak_test.py checks it.

### 2.4 Tooling arms (in-house, synthetic)

Scripted raters at accuracy 0.95, 0.90 and 0.80, an oracle, identical raters and random raters rate the synthetic exam. They count toward no bar.

### 2.5 Lane A (secondary; opens last)

Anyone 18 or over rates public log excerpts blind by the labellers' own task. Items are a seeded draw from a sealed pool of public excerpts; no item comes from, paraphrases or is modelled on AI Village text. Model labels for the bank come from two independent Claude Sonnet passes on public items, agree-only, sealed before any human rates (needs his yes). Contributed logs enter only with the contributor's consent to both public display and outside-model labelling.

| Parameter | Value |
|---|---|
| Scored items | 308 = 22 sets of 14 (5, 5, 4 per class; totals 103, 103, 102) |
| Checks | 6 per set, 2 per answer class, from a pool of 60; answers sealed |
| Ratings | Each set rated by 2 different people (44 accepted sets, 616 scored ratings, 264 check ratings); any two people share at most one set |
| Reserve | Up to 4 sets (56 third ratings, 18.2% of 308) |
| Caps | 2 sets per person planned (28 of 616 ratings, 4.5%); hard cap 3 (42 of 616, 6.8%); three fake codes at cap 2 would hold 84 of 616 (13.6%) |
| Raters needed | 24 at cap 2; 16 at cap 3; about 89 sets started if 60% finish and 90% pass the screen (48 / 0.54), both guesses until the pilot |
| Screen | Set accepted at 5 of 6 checks right, median time above the sealed floor, at most 4 of 20 skips |
| Floor | At least 20 independent passing raters and at least 154 of 308 items doubly rated, else counts only |
| Seeds and delay | Assignment seed from the manifest hash of Seal L1; per-rater shuffle seed from SHA-256 of seed, rater code and set id; second rating not issued within 48 h of the first |
| Windows and host | Open 28 days, one extension of 28 days; durations counted from the Seal L1 FreeTSA time. The intake host is his deployment with his yes at the time; he starts and stops it; the agent starts nothing |
| Agent stream | Only with the person's yes; never added to human tallies |
| Pilot | 3 to 5 invited people with no tie, before Seal L1 |

## 3. Population and sample

### 3.1 Source counts (from the plan; not checked against Data)

| Source | Count | Denominator |
|---|---|---|
| Gate 3 exam items | 150 | 50 contradicted, 50 shown, 50 no-record |
| Gate 2 exam items | 150 | 50, 50, 50 |
| Gate 3 labelled pool | 234 turns | 112 success, 59 failure, 63 unclear (first pass) |
| Gate 3 second pass | 165 agree | of 167 eligible; 2 of 167 split |
| Gate 2 second pass | 168 agree | of 187; 19 of 187 split |
| Unused eligible turns (decoy source) | gate 3: 65 | of 165; gate 2: 68 of 168 |
| Gate 3 claims with the verb replaced | 30 | of 150 |
| Gate 3 divergences between the two checkers | 17 | of 150 (gemma 9, qwen 10, 2 shared): 15 keyed items and 2 no-record items (g3-139, g3-150) |
| 4 Oct sample | 40 | 20 gate-3 turns and 20 messages |
| Claim-spotting messages | 200 | consensus 180 (92 claims, 88 not; reviewer recomputed from the public files); 20 split |
| Real record | 2,510,487 turns | |

### 3.2 Strata and presentations

| Stratum | Items | Rated how |
|---|---|---|
| SHW | 100 of 100 (census) | Q1 then Q2 |
| CON | 100 of 100 (census) | Q1 then Q2 |
| UNC | up to 100 (20 + 20 + 60) | Q1 only |
| SPL | 21 of 21 | Q1 only |
| DEC (A and B) | 20 (10 per phase 1 and 2) | Q1 then Q2 |
| C-decoys | 10 (5 per gate), C only | Q1 then Q2 |
| DUP | 15 (5 per phase) | as the original |

SHW and CON are censuses. Items on which the checkers diverged are inside the census unmarked. The 2 divergent no-record items get a non-blind look by Joshua after Seal 4-1, as a note and not a rating.

### 3.3 Phases

| Phase | Gate | SHW | CON | DEC | UNC | SPL | DUP | Presentations per rater |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 | 50 | 50 | 10 | 20 | 0 | 5 | 135 |
| 2 | 2 | 50 | 50 | 10 | 20 | 0 | 5 | 135 |
| 3 | both | 0 | 0 | 0 | 60 (cap) | 21 | 5 | 86 |
| Total | | 100 | 100 | 20 | 100 | 21 | 15 | 356 |

Committed core: phases 1 and 2, 270 presentations. Phase 3 follows if B agrees and money allows; it is descriptive. UNC counts are caps: if a pool holds fewer unclear turns than planned the phase takes all of them and reports the shortfall. Phase 4 (optional, own yes and own US$200): the 200 claim-spotting messages, 180 consensus plus 20 split, the splits their own stratum.

### 3.4 Inclusion and exclusion

- **Items in.** Every SHW and CON item of gates 2 and 3.
- **Items out, counted and reported by gate and stratum:** items dropped as confidential; items whose text cannot be rendered. They reduce the denominator; 3.6 sets the minimum; a worst-case row counts every dropped item as a disagreement.
- **Raters in.** Aged 18 or over; own approved AI Village access or the publishers' written OK; passed the rehearsal; has not seen the model labels for these items; agrees to the rater terms; declares a tie to Joshua (none, colleague, friend, family, other). Accepted = terms agreed and access basis confirmed within 14 days of day 0; qualified = passed R1 (or R2) within 7 more days. A candidate failing both is replaced once by the next accepter; no replacement after results except under F6.
- **Raters out.** Anyone who built or labelled E3 (Joshua rates in his own stream). Anyone who would break an [workplace]'s rule or the dataset's terms. Anyone who uses an AI tool on an item.
- **Delivery route**, set by the publishers' answer and recorded in Seal 2-R. R1: the static rater page goes to an approved person. R2: render_sheet_local.py builds each item from the rater's own copy and checks it against the sealed per-item text hash. The route changes delivery only, never the items.

### 3.5 Seen items and the 4 Oct pilot

- The 20 seen turns stay in the census. Joshua's new ratings of them and his 4 Oct ratings are excluded from H, kappa and every confirmatory number. H for a seen turn is B and C agreeing; else unresolved. C rates all 20 blind.
- The 4 Oct results (messages 16 of 20 against pass 1, kappa 0.62, and 19 of 20 against pass 2, kappa 0.90; turns 19 of 20, kappa 0.91) are a disclosed prior known to the designer. 19 of 20 has Wilson 76.4% to 99.1%; 16 of 20, 58.4% to 91.9% (recomputed). They count toward no bar.
- His new ratings of the seen turns feed one exploratory test-retest with the memory caveat.
- Sensitivity row: the 20 seen turns removed (n = 180; lines 171 pooled and 81 per class of 90).

### 3.6 Minimum before any analysis

1. A phase is analysed only when A, B and C ratings files for it are sealed, or the stop rule closed the window.
2. A gate is evaluable when at least 90 of its 100 keyed items carry ratings from at least 2 valid raters.
3. The pooled verdict needs both gates evaluable, at least 180 of 200 keyed items and at least 90 of 100 per class. Lines scale as in 4.2.
4. Below these, counts only, and the line reads open.
5. At least one valid outside rater (B) for anything beyond author-checked; B and C both valid for any done.

## 4. Primary outcome and the exact statistic

### 4.1 How H is formed (per item, per stage)

1. Raters counted: A and B, and C when C rated the item. For the 20 seen turns: B and C only. A rater dropped by F6 is removed first. Duplicate presentations are never used in H (the first presentation counts).
2. If A and B give the same answer, that is H. C's rating of such an item is informational.
3. If A and B differ, C decides if C matches one of them; if C matches neither, unresolved.
4. For a seen turn, H is the answer when B and C agree, else unresolved.
5. Unresolved counts as disagreement with the key in the primary analysis; the denominator does not change. The best-case bookend counts unresolved as agreement and is used only for the kill confirmation (5.5) and the rescore.
6. Q1 and Q2 are resolved separately. The primary outcome uses Q2.
7. If only one rater is left, H is that rater's answer and the line cannot read done.

### 4.2 Primary outcome and decision lines

- **K** = number of the 200 keyed items whose H at Q2 equals the key.
- **Reported test (does not decide).** Exact one-sided binomial test of H0 true agreement rate p at most 0.90 against p above 0.90, K ~ Binomial(200, p), alpha 0.05. It rejects at K of 188 or more (P at 188 is 0.0320; at 187, 0.0566). Reported with Wilson and exact Clopper-Pearson 95% intervals and a cluster bootstrap by gate and family (descriptive; items share families, verbs and labellers, so plain binomial intervals understate uncertainty).
- **Decision lines.** Pass: K at least 190 of 200, each class at least 90 of 100, at most 2 of 100 SHW called contradicted. K of 190: Wilson 91.0% to 97.3%, exact one-sided lower bound 91.7%.
- **Scaling when items are dropped (n eligible keyed items, m per class):** pass ceil(0.95 n); kill below ceil(0.90 n); class boundary ceil(0.90 m); danger pass at most floor(0.02 m), kill at ceil(0.06 m) or more. Integer rule: ceil(0.9 n) = (9n + 9) // 10 and ceil(0.95 n) = (19n + 19) // 20. Test vectors: bar(50) 45, bar(49) 45, bar(46) 42, bar(47) 43, bar(51) 46.
- **What a pass says.** Against this sealed key, humans agreed on at least 190 of 200, so the true agreement rate is at least 91.7% (one-sided 95%). It does not say the key is 95% right.

### 4.3 Pre-registered secondary outcomes (anything else is exploratory)

| Id | Outcome | Statistic |
|---|---|---|
| S1 | Agreement per key class | SHW and CON, n = 100 each; Wilson and exact intervals; 3 x 3 table of H against key |
| S2 | Danger cells | SHW called contradicted (has a bar); SHW called not shown; CON called shown; each with n and an exact upper bound |
| S3 | Gate heterogeneity | Fisher exact two-sided (sum of probabilities not larger than observed), gate 2 against gate 3, agree against disagree. Per family and per labeller: cluster bootstrap by family (descriptive) |
| S4 | Reliability A against B | Percent agreement with Wilson 95% (primary measure); Cohen's kappa with one-sided 5th-percentile bound of 10,000 item-bootstrap resamples (BOOT seed); Krippendorff alpha (A and B only); specific agreement per class with counts; Q1 and Q2 separately; test-retest as x of 15 on DUP. Kappa with expected agreement 1 is undefined; percent agreement then decides |
| S5 | Rater validity | Decoys caught: 9 of 10 after phase 1, 18 of 20 after phase 2 per rater; not-shown use rate per rater beside accuracy on keyed items |
| S6 | Rescore | Section 4.4; McNemar exact two-sided, gemma against qwen under H (descriptive) |
| S7 | Author influence | A's key agreement minus B's on the 180 unseen keyed items |
| S8 | Sensitivity rows | B alone; B and C only; read-before items removed; verb-replaced claims removed (30 of 150 gate-3 claims); items cut in the model's view removed; strict reading; 20 seen turns removed; unresolved counted for and against; accuracy by session position (first against last third) |
| S9 | UNC and SPL | Descriptive: H against each AI pass at Q1, with counts |
| S10 | Phase 4 | Agreement of H with AI consensus out of 180; kappa A against B; the 20 split messages apart |

No correction for multiplicity. A pass is a conjunction of lines; the kill is a union, and its combined chance is in 5.3.

### 4.4 The decision outcome: rescore of gate 3

1. Use the sealed checker answers as they are (gemma result fingerprint efff50ac...; qwen 4896bc03...). No re-run, no change to the checker or its fail-closed rule.
2. For each of the 150 gate-3 cases the human key k is H at Q2 for SHW and CON, and not shown for no-record cases unless the widened absence check restated them.
3. Groups are re-formed from k. n_g is the group size. Bar_g = (9 n_g + 9) // 10.
4. Pass: every group meets its bar, and no case with k = contradicted has the checker answer shown.
5. Unresolved and restated cases are scored two ways. U1: they keep the sealed key. U2 (worst case): they stay in their sealed group, count as wrong, and any the checker called shown counts as a planted failure called shown. A pass holds only if it passes under both.
6. Both readings. A pass holds only if it passes under the primary reading. A pass that fails under strict is stated as depends on the reading of claim detail.
7. Two tables, equal prominence: gate 3 under the sealed key and under H. A rescored reversal is reported equally and never replaces the sealed result.
8. Worked vectors the code must reproduce (reviewer confirmed): gemma sealed 47, 45, 49 of 50 pass at bar 45; one shown-group hit overturned to not shown gives 44 of 49 against bar 45: fail. Qwen sealed 49, 42, 49 fails; it reaches 42 of 46 (bar 42) only if at least 4 of its 7 not-shown misses are overturned (at 3 it is 42 of 47 against 43).

### 4.5 Intervals and the thin or firm label

Exact one-sided 95% (Clopper-Pearson) bound against a floor F. Firm when the bound clears F; thin when the count meets the pass line but the bound does not.

| Bar | Pass line | Floor F | Count at which the bound clears F |
|---|---|---|---|
| Pooled agreement | 190 of 200 | 90% lower | 188 or more (lower bound 90.5%), so any pooled pass is firm |
| Class agreement | 90 of 100 | 90% lower | 96 or more (lower bound 91.1%; at 95 it is 89.8%), so 90 to 95 is thin |
| Danger cell | 2 or fewer of 100 | 6% upper | 1 or fewer (upper 4.7%; at 2 it is 6.2%), so 2 is thin |
| Gate alone (F11 path) | 95 of 100 | 90% lower | 96 or more |
| Kappa A against B | 0.80 | 0.60 lower (one-sided item bootstrap) | bound at least 0.60 |

## 5. Fail conditions fixed in advance

No condition here ends the program. The largest consequence is ending the AI-labelled-exam line.

### 5.1 Gates before any real item is shown

| Gate | Threshold and denominator | If it fails |
|---|---|---|
| Stats vectors | Wilson 45 of 50 = 0.786 to 0.957; Wilson 95 of 100 = 0.888 to 0.978; exact one-sided upper for 0 of 50 = 5.8% and 0 of 100 = 2.95%; kappa on the public claim-spotting files = 0.8004 on 180 of 200; vectors in 11 | No seal |
| Scorer planted-fault test | Oracle raters: 8 of 8 wrong keys flagged, 0 of 92 clean keyed items flagged; identical raters kappa 1.0; random raters within plus or minus 0.15 (null SD 0.045); rescore reproduces 47/45/49 and 49/42/49 | No seal |
| Leak test | 0 forbidden strings in the rater-facing file; duplicate distance at least 15; sessions at most 60. Run on every real sheet | No delivery |
| Input hash check | 8 of 8 listed fingerprints match | Stop; a v-next |
| Rehearsal | At least 11 of 12 on R1 per rater (A, B, C); one retake on R2; under 11 of 12 on R2 and the rater is not used. If 2 or more raters miss the same item the guide is revised and a new version sealed before any phase is rated | Rater out, or guide v-next |

### 5.2 Result conditions

See the fail_conditions list: F1 to F12, L1 to L3, P4. Key numbers, all recomputed: count-alone chances (F2) 0.12%, 4.2%, 12.2%, 44.1%, 97.5% at true 95%, 93%, 92%, 90%, 85%; class (F3) 1.1%, 9.1%, 17.6%, 41.7%; danger (F5) 0.05%, 1.5%, 8.1%, 38.4% at 1%, 2%, 3%, 5%; gemma group at 45 of 50 passes 99.6%, 96.2%, 61.6%, 21.9% at true 97%, 95%, 90%, 85%.

Interim rule. After phase 1, gate 3 alone is reported: pass at least 95 of 100 (true 97% passes 91.9%, 95% passes 61.6%, 93% 29.1%), against 90 to 94, flagged below 90. No kill acts on 100 items; kill lines act at the pooled verdict. The gate 3 rescore runs as soon as H exists for it.

### 5.3 What the thresholds support (my simulation: independent errors, key errors spread over the other two classes, 6,000 runs per cell, 20 seen turns judged by B and C only; sealed script)

Probability of each outcome by the key's true accuracy q and each rater's accuracy r. Firm = pass with every class at 96 of 100 or more and danger 1 or fewer.

| q | r | Pass | Firm pass | Against | Kill |
|---|---|---|---|---|---|
| 1.00 | 0.97 | 1.000 | 0.996 | 0.000 | 0.000 |
| 0.98 | 0.97 | 0.892 | 0.574 | 0.107 | 0.001 |
| 0.95 | 0.99 | 0.373 | 0.088 | 0.567 | 0.060 |
| 0.95 | 0.97 | 0.281 | 0.055 | 0.631 | 0.088 |
| 0.93 | 0.97 | 0.058 | 0.006 | 0.597 | 0.345 |
| 0.90 | 0.97 | 0.002 | 0.000 | 0.203 | 0.795 |
| 0.98 | 0.93 | 0.629 | 0.214 | 0.357 | 0.013 |
| 0.95 | 0.93 | 0.085 | 0.010 | 0.657 | 0.258 |

Plainly:
- A key truly 98% right passes 63% to 89%. A key truly 95% right passes 9% to 37% and is killed 6% to 26% (before the best-case confirmation, which lowers it). Counting K alone at 190 or more with a perfect H is 58.3%; class bars and the danger cell cost the rest.
- Key questioned is the most likely result for a good but not excellent key. Its consequence is mild by design.
- Real errors cluster on ambiguous items, so these figures are optimistic.

Verdict kappa, three classes (easy items at accuracy rE, unclear items at rN; 3,000 runs; items 90 success, 90 failure, 60 unclear in 240 pairs; 45, 45, 20 in 110): share reaching at least 0.80 / 0.60 to 0.79 / under 0.60.

| rE | rN | 110 pairs | 240 pairs |
|---|---|---|---|
| 0.99 | 0.90 | 1.000 / 0.000 / 0.000 | 1.000 / 0.000 / 0.000 |
| 0.97 | 0.90 | 0.943 / 0.057 / 0.000 | 0.987 / 0.013 / 0.000 |
| 0.97 | 0.80 | 0.694 / 0.306 / 0.000 | 0.508 / 0.492 / 0.000 |
| 0.95 | 0.90 | 0.683 / 0.317 / 0.000 | 0.742 / 0.258 / 0.000 |
| 0.95 | 0.80 | 0.291 / 0.709 / 0.000 | 0.109 / 0.891 / 0.000 |
| 0.93 | 0.80 | 0.097 / 0.891 / 0.013 | 0.009 / 0.989 / 0.002 |
| 0.93 | 0.70 | 0.023 / 0.905 / 0.072 | 0.000 / 0.940 / 0.060 |

So the line often reads open: reliability inconclusive. Hard unclear items drag kappa; this is the reason the choice in section 9 (kappa as bar for done) is his call.

Author-influence false alarm (exact; A and B equally accurate; 8 or more of 180): 1.0% at r 0.97, 3.3% at 0.95, 5.8% at 0.93, any key accuracy. Power for a 4-point edge 38%, 6-point edge 75%.

Rater validity chances: at 9 of 10, a rater at 97%, 95%, 90%, 85% passes 96.6%, 91.4%, 73.6%, 54.4%; at 18 of 20, 97.9%, 92.5%, 67.7%, 40.5%; rehearsal 11 of 12: 95.1%, 88.2%, 65.9%, 44.3%.

### 5.4 Precedence

1. A 5.1 gate not passed: no real item is shown.
2. A breach (7.4): stop.
3. The decision table in 5.5, first matching row.
F7 and F9 are read beside whichever result stands.

### 5.5 Decision table (first match wins; covers every result)

| Row | Condition | W1 line |
|---|---|---|
| R1 | Not evaluable (3.6), or C missing or dropped, or no valid B | counts only; no B: author-checked, not independent |
| R2 | Verdict kappa under 0.60 | open: raters unreliable; pause E3; no kill, no pass |
| R3 | A kill line (F2, F3, F5; or per gate if F11 fired) holds in the primary AND in the best-case bookend | failed |
| R3b | A kill line holds in the primary only | key questioned (kill not confirmed) |
| R4 | K from 180 to 189, or danger 3 to 5, or gemma fails the rescore under primary or either bookend | key questioned |
| R5 | Pass lines met and verdict kappa 0.60 to 0.79 | open: reliability inconclusive (all key numbers published) |
| R6 | Pass lines met, kappa 0.80 or more, every bar firm, no declared tie, F10 not fired, B and C valid | done |
| R7 | Pass lines met, kappa 0.80 or more, but any bar thin, or a tie, or F10 fired, or the pass depends on the reading | done (thin) |

Check: K 190 or more forces each class to 90 or more, so R3 to R7 partition all remaining outcomes; a class at 89 or less is a kill row.

## 6. Pass condition

**The W1 line (page text published only with his yes):** E3's labels were checked by people: read in full by the author and one outside person, with a second outside person deciding disputes. Default: not shown.

States: not shown; author-checked, not independent; open (reliability inconclusive, or raters unreliable); key questioned; done; done (thin); failed. Rules: see 5.5. Plain done also needs B and C to declare no tie; a tie, even with firm counts, gives done (thin) and says tied rater. Every table shows misses beside hits, per class with n and an interval.

What each outcome changes:
- **Done or done (thin):** W1 moves from one author-checked sample to x of 200 agree with the key, read by the author and one outside person with a second deciding disputes. E3's numbers stand with the fragility note. W2, W3, W4 untouched.
- **Key questioned:** E3 restated under H. If gemma fails under H, passed gate 3 is withdrawn in the correction note. Gate 4's key stays two humans.
- **Failed:** the AI-labelled-exam line ends; later exams are human-keyed; E3's scores are republished as agreement with a model key.
- **Open or counts only:** reported as open, with the counts.

**Hand-off to gate 4 (W3 step 0).** Phase 1 produces per-class specific agreement at Q1 (counts and bootstrap interval) and the three-class kappa on the 110 pairs. W3's own thresholds live in W3's design. A W3 pass keeps its human-review caveat until W1 reports.

**Lane A and phase 4.** Separate lines; never set done or failed on the W1 line.

## 7. Stop rule

1. **n reached.** Per phase, when A and B have each rated every presentation (135, 135, 86) and C has rated the dispute list. No item added, dropped or replaced.
2. **Calendar** (all days counted from the ledger by him; no timer or background job exists).
   - B accepted within 14 days of the publisher message (day 0) and qualified within 7 more days; else the author-only interim for phase 1, final for this design.
   - Each phase window for an outside rater is 21 days from delivery, one sealed extension of 21 days.
   - All collection stops 84 days after day 0; day 0 must fall within 30 days of Seal 1 or the design lapses. Unfinished work is reported as incomplete.
   - Lane A: open 28 days, one extension of 28 days.
3. **Budget.** A phase is released only if the remaining money covers its high estimate. Cumulative rater pay at the ceiling (US$800 for phases 1 to 3; US$200 for phase 4) stops further outside rating until a v-next and a new yes. Hours worked are always paid.
4. **Harm or breach.** Item text reaches anyone without their own access or the publishers' written OK; item text pasted into any AI tool; a rater asks to stop or reports distress; a publisher objects; a leak test fails on a released sheet; a sheet, map or answer file found in another tool's folder; the answer map opened before ratings are sealed (except the author-only path). Effect: stop that phase, dated breach note, resume only under a v-next.
5. **No optional stopping.** No real ratings are compared with any key, and no agreement figure is computed, before a phase's ratings files are sealed. n, items and raters are fixed; no rater is added or dropped after results except by F6. The only extension is one window extension. The scorer runs twice per phase and no more: reliability mode (A and B only, no key) and full mode. A bug fix is a dated correction showing both outputs. While collecting, only counts are shown.

## 8. Budget

| Line | Amount | Assumptions |
|---|---|---|
| Cash | US$0 to US$800 (phases 1 to 3) plus a separate US$200 (phase 4) | B 13.5 h and C up to 4.2 h is 17.7 h; at an assumed US$40 an hour, US$708; ceiling adds 13%. Phase 4 about 4 h, US$160. US$0 if volunteers and until access is settled. Joshua unpaid. Lane A marginal cash assumed US$0 |
| CPU, one CPU-only mini PC | At most 2 h | Absence check one streamed pass over 2,510,487 turns, one compiled pattern, guess 0.25 to 0.33 h, timed first on synthetic input, abort at 1.5 h. Other steps under 1.5 h. No model call. No long run |
| His hours | About 17 h core, about 20 h phases 1 to 3, phase 4 plus about 3.5 h, lane A up to 3 h a week | Core is about 10.3 h rating plus about 7 h seals, scoring, outreach, writing (plan). Recount at 2.5 and 1 minutes: 10.25 h core, 11.68 h three phases; rehearsal times replace these |
| Outside people | B about 11 h core, 13 h three phases, plus 0.5 h rehearsal; C 2.4 to 3.7 h plus 0.5 h; phase 4 about 4 h | Lane A: 44 accepted sets; arithmetic only, 14.7 h at 1 minute per item and 36.7 h at 2.5 |
| Elapsed (plan figures) | Author-only interim about 1 week after the clocks in 7.2; interim gate 3 result 2 to 4 weeks after the seal; all phases 4 to 6 weeks | |

## 9. Decisions assumed

Each default was used where a decision is pending. If he chooses otherwise, a v-next is sealed before the step it affects.

| # | Decision | Default used |
|---|---|---|
| 1 | Gate 4's answer key | Two humans; local models write claim sentences only; no Claude Sonnet on real turns without his explicit yes; no step here sends real text to any model |
| 2 | Raters B and C, publishers | Ask the publishers first; plan candidate is the organizer contact (ties declared); first accepter qualified is B, second C; 14 days then author-only |
| 3 | Counts-only Data reads | Yes, run by Joshua, folders Workbench/w1-human-audit-2026-10-05/ and Data/hga/; AI sees counts, ids, hashes |
| 5 | Seals and start rule | Batch of stamps; FreeTSA first; manifest-hash seed, manifest frozen, first reply used; hash-chained ledger |
| 6 | CPU schedule | He starts every run; one short pass |
| 7 | W1 size | Phases 1 and 2 committed; phase 3 if B agrees; phase 4 after |
| 8 | Claim-detail rule | Both readings pre-registered |
| 12 | Rater money | US$0 until access is settled; US$800 and US$200 ceilings at an assumed US$40 an hour (plan US$650 did not close) |
| 14 | Publishing and wording | Nothing out without his yes; reword the sealed sample sentence (WRITEUP lines 231 and 248, PRESS-KIT line 65); labels keyed to ids only with publishers' OK |
| 15 | Predictions | Private by hash; misses beside hits; no scorecard |
| 16 | The 4 Oct sample | Prior and pilot, 3.5 |
| G1 to G8 | Public asks, intake host, legal read, incentives, outside models, custodian, publisher wording, load caps | Lane A last; his deployment of the host with his yes; legal read before opening (from memory, verify; not legal advice); points only; local models only on contributed material; no custodian in v2; publisher message says plainly E3's labellers were Claude Sonnet sub-agents who saw the turns; caps 30 set starts and 3 h a week |

**Choices made here that the plan left open (each reversible by a v-next):**

| # | Choice | Reason |
|---|---|---|
| a | Seal 1 before the counts-only reads | His method |
| b | Phase n+1 released after A and B phase-n ratings are sealed with kappa at least 0.60 and decoys passed | Lets a guide revision happen early |
| c | C gets 10 own decoys and the 9 of 10 gate | Plan gives no count |
| d | Rehearsal retake on R2 | One careless rater should not force a re-seal |
| e | Evaluability 180 of 200 and 90 of 100 per class | No plan rule for dropped items |
| f | Thin or firm by exact bound | Needed for a labelled thin pass |
| g | Author-influence rule, threshold 8 of 180 | A falsifier needs a consequence; 10 had 18% power |
| h | Heterogeneity rule with agree and danger lines per gate | Plan gives none |
| i | Windows 21 days plus one extension; 84 days from day 0 | Plan has only 14 days |
| j | Ratings files hold line index and hash only | No dataset text leaves a rater's machine |
| k | A tie gives at most done (thin) | Plan candidate B has ties |
| l | Kappa 0.80 kept as a bar for done, as the plan table lists it. Alternative: descriptive only (plan section 5 item 12); at (0.95, 0.80) it is reached 11% of the time | His call |
| m | Phase 1 interim gives no kill | 100 items too few |
| n | Unresolved bookends U1, U2 | Plan does not define them |
| o | Extra-detail tick | Derives the strict reading from one pass |
| p | Lane A options as listed in the previous design | Gathering path leaves them to him |
| q | Verdict kappa on 240 core pairs, or phase 2 alone after a guide revision; phase 3 descriptive | Phase 3 items are hard and cannot rescue or sink |
| r | A kill needs the best-case bookend too | Unresolved items could otherwise manufacture a kill |
| s | Acceptance 14 days plus rehearsal 7 days; one replacement | Closes the clock gap |
| t | Ceilings US$800 and US$200 | 17.7 h does not fit US$650 |
| u | Author-only interim final for this design | A is not blind after the map opens |
| v | Scorer two modes, each once per phase | Plan needs a reliability run |
| w | Phase 2 release also needs decoys passed | Same as b |
| x | A rates only after B and C rehearse, or day 21 | Avoids a guide change mid phase 1 |

## 10. Order of steps

In-house means no outside person, no outside model, and no gated text in any AI's view. Joshua and his local scripts may read gated data on his PC; the AI sees counts, ids and hashes only. Each step says what yes it needs.

### Part 1. Agent builds on synthetic or public material only (no Data, no network, no model call, nothing left running)

1.0 He names any extra folder the agent may read (4 Oct tooling, kaggle-v3, receipts_io and receipts_model); otherwise the agent writes those pieces from scratch.
1.1 make_synthetic_g3.py. 1.2 stats_core.py, tests and simulation scripts. 1.3 The two-stage page and sheet, leak, input-check, absence-check, local-render tools and the counts-only wrapper (tested under Node with no browser; a source test forbids network code). 1.4 score_hga.py (two modes) and rescore_g3.py. 1.5 Synthetic end-to-end dry run. 1.6 RATER-GUIDE.md and rehearsal sets R1 and R2 written from scratch; no outside model reads them unless he says yes. 1.7 Drafts, unsent: publisher message, candidate messages, RATER-AGREEMENT.md, corrections template, predictions shell.
**SEAL 1** (his yes to the stamps).

### Part 2. After Seal 1, Joshua only on his PC

2.1 Hash check of the sealed inputs (his yes). Any mismatch: stop, v-next.
2.2 Counts-only census and widened absence check (timed first on synthetic input; abort at 1.5 CPU hours) (his yes); items restated are listed by case id and treated as unresolved in the rescore. Other-tool folder check by names and sizes. **Seal 1b.**
2.3 His rehearsal on R1.

### Part 3. Outside raters (each step needs his yes)

3.1 His send: the publisher message. Day 0.
3.2 His send, a yes per person: approach B, then C. **Seal 2-R:** anonymised roster hash, publishers' answer hash, route R1 or R2, custodian choice.
3.3 B and C rehearse on R1 (R2 for a retake). Any guide revision is sealed here, before any phase is rated.

### Part 4. Each phase (1, 2, then 3 if B agrees)

4.1 Build the sheet from Data on his PC (his yes); leak test; three-part map: map-flags, map-decoy, map-answers. **Seal 2-n** (items, order, maps; route independent).
4.2 Build the delivery file for the route chosen; check it carries the same items. **Seal 2-n-b.** His yes to deliver gated text by the publishers' route only.
4.3 A rates (after B and C have rehearsed, or day 21 with no B). **Seal 3-n-A.** B rates. **Seal 3-n-B.**
4.4 His yes to run the scorer in reliability mode once (no key): verdict kappa on A and B, dispute list as sheet ids, decoy results using map-decoy. Release gate for the next phase.
4.5 C rates the disputes, the 20 seen turns and own decoys. **Seal 3-n-C.**
4.6 Open map-answers (Joshua, or the custodian). Full scorer once: H, primary numbers, rescore, McNemar, W3 file. He opens g3-139 and g3-150 non-blind. **Seal 4-n.** Pooled verdict after phase 2: **Seal 4-P.** Phase 3 the same way; **Seal 4-F.**
4.7 Author-only path: if no qualified B by day 21, A rates phase 1, **Seal 3-1-A**, then with his yes the map opens and only A against the key is reported, labelled author-checked, not independent. Final for this design.
4.8 Phase 4 in or out (his yes and the separate US$200). Draft the correction note and proposed edits. Folder check again. His yes to publish; not before.

### Part 5. Lane A (last; each step his yes)

L.1 Legal and ethics read of the notice (from memory, verify; not legal advice). L.2 Intake host off the mini PC (his deployment). L.3 Public item bank. L.4 Two Claude Sonnet passes on public items (his yes). L.5 Seal L0 and pilot. L.6 Seal L1, open. L.7 Close, run the sealed script once, Seal L2.

## 11. What is sealed with this design

**Seal 1 manifest (SEAL1-MANIFEST.txt):** this document; RATER-GUIDE.md v1; stats_core.py, score_hga.py, rescore_g3.py, simulation scripts and tests; the page, make_sheet.py, leak_test.py, check_inputs.py, check_none_absent.py, render_sheet_local.py, the wrapper; make_synthetic_g3.py and dry-run outputs; rehearsal sets R1, R2 with answers; HGA-PREDICTIONS-v1.md (hash only; private). Hashes are computed at the seal.

**Already-sealed input fingerprints that check_inputs.py must match (from the plan; not verified here):**

| Input | SHA-256 |
|---|---|
| Gate 3 truth.json | 6b2b49f491370297e46e497e6fbf0eace1769590421fe41ab4460e3b0d29128a |
| Gate 3 planted_rows.json | e311003e6d4997baccb562a5f3fc0df6d1d98f43e47c4df737adc1e9a8b8b120 |
| Gate 3 pool.json | 69ae3ed96c7222876f867c5ebef81d95ddf5d43c77d4b37b9f69912c7a178933 |
| Gate 2 truth.json | 295a86f52680b6e6c50f62358cc7031399b95b12b350576b14d1e4028763121c |
| Gate 2 planted_rows.json | b3d5e6fb3df483e46e2327fbb0041527e3dcc3416891e5c74e0ace7b93c56930 |
| Gemma gate 3 result | efff50ace23564ec9f28e6b04df23ee437f2ae4a3e82f505e3cc2d34d7962243 |
| Qwen gate 3 result | 4896bc03e34cf03e9e2cfd994989e2fe9784c283f3fa82736b856155949605fd |
| 4 Oct pass-1 labels | 6bca4dc7a098be74cd46d4c0a74e64e7dd64879b9fbfa352da8988317f5a25d4 |

**Test vectors (recomputed with local Python):** Wilson 45/50 0.786 to 0.957; 95/100 0.888 to 0.978; 190/200 0.910 to 0.973; 96/100 0.902 to 0.984; 18/20 0.699 to 0.972. Exact one-sided 95% lower: 190/200 0.9167; 188/200 0.9046; 96/100 0.9108; 95/100 0.8977; 45/50 0.8012. Upper: 0, 1, 2 of 100 = 0.0295, 0.0466, 0.0616; 0 of 50 = 0.0582. Binomial: P(X>=188|200,0.90) 0.0320; P(X>=187) 0.0566; P(X>=190|200,0.95) 0.583; P(X<=179|200,0.95) 0.0012. Decoys: P(>=18/20|0.95) 0.9245; (|0.90) 0.6769; P(>=9/10|0.95) 0.9139. Kappa on public claim-spotting labels 0.8004 (180 of 200; consensus 92 and 88). Integer bars 45, 45, 42, 43, 46. Fisher: gate at 95 of 100 is significant against 85 of 100 or lower; at 97, against 89 or lower.

**Predictions (his probabilities go in the private file; hash only is sealed):** P1 K at least 190 of 200; P2 each class at least 90 of 100; P3 at most 2 of 100 SHW called contradicted; P4 gemma's gate 3 pass holds under H; P5 at least 1 of gemma's 45 hits overturned; P6 phase 1 kappa at least 0.80; P7 verdict kappa at least 0.80; P8 a B is named and qualified within 21 days; P9 gates do not differ (Fisher p at least 0.05); P10 the author-influence rule does not fire; P11 the strict reading changes at least one gate 3 group result. Each [HIS PROBABILITY].

**Sealed later:** Seals 1b, 2-R, 2-n, 2-n-b, 3-n-A/B/C, 4-n, 4-P, 4-F, and L0, L1, L2. Each stamp needs his yes. No file under Data is published; only fingerprints leave the PC.

## 12. What this design cannot show

- W2, W3, W4 (record independence, margin on fresh exams, real logs, plain baseline).
- That the key is right in the world. Two people agreeing is not truth; people and the AI read the same text and may share a misreading.
- That a pass means 95%. At 190 of 200 the supported claim is at least 91.7%; a 90% floor cannot be certified in a class below 96 of 100; the danger cell cannot be certified under 2% below 149 items. A key truly 95% right passes 9% to 37% of the time, so plain done is hard to reach.
- Which wrong labels the filter removed (E3 kept a turn only when both passes agreed).
- Whether the checker is good on real claims, or the retrieval behind the 100 no-record items, or extraction recall.
- The faults, which are still his generator's. The planted text is not the original turn.
- Gate 1 keys and the agent run's 130 sampled answers.
- Independence of raters: B and C are few, self-selected, may have ties (self-reported); no AI use is verified. Joshua has seen part of the sample.
- Prior effect: only about 9% of claim items are not shown, so raters may expect planted items and agree with the key more; reported through not-shown use rate and decoy accuracy.
- Item dependence: items share 8 families, verbs and labellers; binomial intervals understate uncertainty; the cluster bootstrap is descriptive.
- Blindness rests partly on honour: he does not open map-answers early, and no custodian is named in v2. A stamp shows a file existed by a time, not that nobody looked early.
- Author influence: the F10 rule has 38% power for a 4-point edge.
- Public re-rating (the text is gated). Whether Sonnet labels fit other data. Lane A does not check E3's key. Legal points are from memory, verify; not legal advice; the dataset's terms were not read.

## 13. Doubts considered and dismissed

1. A different model family as the key: set aside, gated text may not go to a model. Wrong if a different family agrees with two humans on at least 95% of gate 3's 100 receipt turns.
2. Joshua is the author: set aside, not ignored; sealed before the map opens; seen turns excluded; every headline also with B alone. Wrong if F10 fires.
3. Rating planted text is not rating real turns: set aside, the exam as scored is the planted text. Wrong if more than half of at least 4 overturned keyed items have an invented word on the cited deciding line.
4. 100 per class is too few: accepted in part, 4.5 and 5.3 say what each count supports.
5. Fatigue: sessions of at most 60, position logged, 15 duplicates. Wrong if key agreement in the last third of positions falls more than 5 points below the first third (about 60 keyed presentations in each).
6. A 90% kill fires by chance: accepted; chances in 5.3; a kill needs the best-case bookend; no kill acts on phase 1 alone.
7. Let raters discuss disagreements: set aside; C rates blind.
8. Audit gate 4's labels instead: set aside for gate 3; gemma's pass sits on the bar.
9. The 4 Oct 19 of 20 already answers W1: set aside; one rater, not blind, AI-reviewed, Wilson 76.4% to 99.1%.
10. Have C rate everything: set aside on cost (about 13 more outside hours, about US$520). Wrong if unresolved items exceed 10 of 200; the bookends are shown for that reason.
11. Pay per item or bonus for agreeing: set aside; it would bend answers.
12. Open the public ask first: set aside; lane A cannot check E3's key.
13. Crowd platform: set aside for lane B; gated text cannot go to people without access.

## 14. Changes from v1 (review)

Decision table and kappa rules added (5.5, 4.3); kill confirmation by bookend; F10 recomputed and re-set; F1 and kappa tables corrected and scripts sealed; kappa for done restated as his call; steps and file names brought inside the owner's rules; budget ceilings fixed; ordering fixed (rehearsal before rating, delivery file after route, early map open final); acceptance and replacement rules; ethics and consent text; clocks, grant line removed.

---

## Appendix: adversarial review before the seal (verdict: sealable with fixes)

17 problems were found; every fix is already in the text above. High-severity ones:

- **Undefined result regions. (1) Kappa under 0.60 had a consequence (pause E3) but no W1 line state and no rule for how it meets a kill or a pass. (2) After a guide revision the pooled 240-pair kappa mixes two guides, and phase 3 was an extension that could not change any bar. (3) K of 188 or 189 rejects the exact test (H0 p at most 0.90) yet was labelled against. (4) When F11 fires, the per-gate rule had no danger-cell rule. (5) Rater A or C dropped by the decoy gate had no state, and a dropped C leaves disputes unresolved, which count as disagreement and could manufacture a kill. (6) P4 had one consequence for two lines.**
  Fix: One ordered decision table (section 5.5) now partitions every result. Verdict kappa is defined (240 core pairs; phase 2 alone if the guide was revised); phase 3 is descriptive and cannot move it. Kappa under 0.60 gives 'open: raters unreliable' and blocks both kill and pass. The exact test is reported, the count lines decide. F11 has agree and danger lines per gate. A dropped or missing C means counts only. P4 has a full table.
- **Unresolved items can drive a kill. My simulation of the design (independent errors, 6,000 runs per cell) shows a key that is truly 95% right is killed 9% (rater accuracy 0.97) to 26% (0.93) of the time, mostly through the class line and the danger cell. The count-alone figures quoted for F2 (0.12% at true 95%) assume H equals the truth.**
  Fix: A kill is acted on only if it also holds in the best-case bookend (unresolved counted as agreement); otherwise the line reads key questioned (kill not confirmed). Simulated false-kill rates are printed beside the kill lines and F2 now says its count-alone figures assume perfect raters.
- **Figures that did not recompute. (a) F10 false-alarm numbers (0.2%, 1.0%, 3.1%, 4.5%, 5.8%) came from a naive model (agreement = key accuracy times rater accuracy). A wrong key makes both raters disagree with it together. Exact convolution gives 0.2% at rater accuracy 0.97 for any key accuracy and 1.0% at 0.95. At the old threshold of 10 the rule had only 18% power against an author 4 points better than B. (b) F1 said a key truly 95% right lands in K 180 to 189 57% to 68% of the time; my runs give 47%, 61%, 82% at rater accuracy 0.99, 0.97, 0.93 (57%, 63%, 66% is the whole against region). (c) The kappa table could not be reproduced: my runs with a stated item mix differ by up to 0.4 in the share reaching 0.80. All other quoted numbers recomputed: Wilson, exact one-sided bounds, binomial tails, decoy and rehearsal pass chances, Fisher power, 0.8004 kappa vector on the public files (180 of 200, consensus 92 and 88), integer bars 45, 45, 42, 43, 46.**
  Fix: F10 threshold moved to 8 or more of 180 (false alarm 1.0% at r 0.97, 3.3% at 0.95, 5.8% at 0.93; power 38% for a 4-point author edge and 75% for a 6-point edge), with the corrected numbers. F1 figures corrected. Kappa table replaced with a stated model and the simulation scripts (kappa, bars, F10) are sealed in Seal 1 so every simulated figure is reproducible; simulated figures are descriptive, not bars.
- **Kappa at least 0.80 was made a requirement for done, but the plan (section 5, item 12; the W1 table) calls it a descriptive target. At plausible rater accuracy (0.95 easy, 0.80 unclear items) the chance of reaching 0.80 on 240 pairs is only about 11% in my run, so done was nearly unreachable for a reason unrelated to the key.**
  Fix: Kept as the owner's call (choice l) but made explicit: kappa 0.80 or more is needed for done, 0.60 to 0.79 reads open: reliability inconclusive with every key number still published, under 0.60 reads open: raters unreliable. The reach chances are restated from my run.
- **Rule breaches in the step list. (1) Step 1.6 had an optional Claude Sonnet read of the guide listed among steps needing no yes; that is an outside model call and a send. (2) The design names a file map-key and per-rater tokens; hard limit 3 forbids an AI opening any file whose name contains key or token, so the agent could not even be asked to handle them safely. (3) Step 1.3 extends label-template.html and the 4 Oct tooling, and 1.1 and 1.6 use kaggle-v3 and receipts_io and receipts_model; none of these folders is in the standing read list (limit 1). (4) Two clock times (11:39:56 and 12:00:00) appear; the second is not shown to come from a command. (5) The cost line says grant status not checked: that is the owner's money. (6) Lane A runs an intake host for 28 days, which is a persistent outside service (limit 7) and a deploy (limit 4).**
  Fix: 1.6 Sonnet read removed (needs his yes, default off). map-key renamed map-answers; per-rater tokens renamed rater codes; a naming rule added (no file name with auth, token, key, secret, credential). New step 1.0: he names every folder the agent may read beyond the standing list before steps 1.1 to 1.5, else the agent writes those tools from scratch. All clock lines removed. Grant line removed. Lane A host is stated as his deployment, with his yes at that time, started and stopped by him; the agent starts nothing and no timer runs: day counts are read from the ledger by him.
- **Budget does not close. B 13 h plus C 3 h is 16 h, but rehearsals (0.5 h each) are listed as extra and C can take 3.7 h: 13.5 + 4.2 = 17.7 h, US$708 at US$40 an hour, over the US$650 ceiling. Phase 4 (about 4 outside hours, US$160) has no money line. Stop rule 3 would then stop pay mid-phase and leave a half-rated phase with no analysis rule.**
  Fix: Ceiling US$800 for phases 1 to 3 (US$708 plus 13% margin) and a separate US$200 for phase 4, each on his yes at the first pay. A phase is released only if the remaining money covers its high estimate; pay for hours worked is always honoured. The ceiling figure is a change from the plan default and needs his yes at the seal.
- **Order and contamination. (1) Joshua rates phase 1 before B and C rehearse, so a guide revision found in their rehearsal would split phase 1 from the rest. (2) The author-only path opens the answer map before B exists; his later ratings are then not blind. (3) Seal 2-1 seals the rater-facing file before the delivery route (R1 static page or R2 local render) is chosen in Seal 2-R. (4) The 84-day cap starts at Seal 1, so waiting for his send eats the window. (5) Scorer is said to run once per phase, yet the plan has a reliability run and a full run.**
  Fix: A rates phase 1 only after B and C have passed rehearsal, or at day 21 (14 days to accept plus 7 to rehearse) if no B. After an early map open the author-only interim is final for this design; any later outside rating needs a v-next. Seal 2-n now seals items, order and maps (route independent); the delivery file is built after Seal 2-R and sealed as Seal 2-n-b with a check that its item set matches. The cap runs 84 days from day 0 (publisher message); day 0 must fall within 30 days of Seal 1 or the design lapses. The scorer has two named modes (reliability, full), each once per phase.
