# C4: the rule spreads (reverse virus). Study design v1 (reviewed and corrected)

| Field | Value |
|---|---|
| Design id | C4-RULE-SPREADS |
| Version | v1 |
| Status | DRAFT FOR SEAL; nothing run, sent, searched or sealed |
| Drafted | 5 Oct 2026, for Joshua Bauer (ISWT42). Clock last read from the system: 12:04:27 UTC. Re-read from a command at the seal; never typed. |
| Private until the reveal | The control phrase text and its salt are NOT in this file. Only salted SHA-256 commitments are. The text lives in the private store. No AI tool may write a control string into any file, draft, post, message or query it can see. |

**Depends on (read for this design; none changed):**

1. `C:\Users\joshd\Private\ClaudeHandoff\specs\WEAKNESS-PLANS-2026-10-05.md` (sections 4, 5, 6 and 9)
2. `...\specs\GATHERING-PATHS-2026-10-05.md` (W4 path: tiers I0, I1, I2; W1 path: receipts and hash chains)
3. `...\specs\OUTSIDE-REVIEW-BIGGER-2026-10-05.md` (bar 5, someone else's replication; "1 star, 0 forks" when written)
4. `...\specs\PROTOCOL-HALF-LIFE-DESIGN-DRAFT-2026-10-05.md` (house format; the 38 seconds per call figure)
5. `...\specs\IDEAS-TO-TEST-2026-10-04.md`
6. `C:\Users\joshd\Workbench\launch-2026-10-05\package\` (`OPEN-TEST-PAGE.md`, `OPEN-TEST-THREAD.md`, `PRESS-KIT.md`: the phrase appears in all three; `LAUNCH-RUNBOOK-0635.md`: his channels, "no trackers and no visitor analytics", and a launch scheduled for 10:35:00 UTC on 5 Oct, which is a plan, not a log; `TAGS-AND-SETTINGS.md`)
7. `...\Workbench\sonny-test-public\README.md` and `STUDIES.md`
8. Searched for the phrase only: `swarm-receipts-public`, `receipt-desk-public`, `agent-board-v2`.

Any change after the seal is a new version, sealed before the step it affects. Sealed files are never edited.

**Reading rules.** Every count comes with its own denominator, original counts first, then rates. Times come from the clock, the FreeTSA token or the platform, never typed. Legal points are from memory, verify; not legal advice. Statistics are exact binomial and exact Poisson with margins fixed here. Every figure in sections 4 to 6 was recomputed with local Python (standard library only) when this version was written, and step H2 re-checks each as a test vector. No web search was made and no public page was checked, so I do not know which of his public pages carry the phrase. In the files I read, the words appear in three drafts.

**Folders (he names them in the work order).** Work: `C:\Users\joshd\Workbench\c4-rule-spreads-2026-10-05\`. Sealed files and ledger: `C:\Users\joshd\Private\claims\2026-10-05-c4-rule-spreads\`. Private store (salts, control text, raw contact list, strangers' snippets): [HIS PATH], outside every folder an AI tool can open. C4 reads nothing under `Data` and nothing under `D:\LIVE`. No AI tool scans any folder other than the work folder.

---

## 1. Hypothesis

**His words, relayed:** "this could be a reverse virus for artificial intelligence".

**My reading, his to correct:** a virus that spreads a safeguard, not a harm. This design tests only the first hop: do strangers pick up the phrase?

**Testable form.** Within 180 days of the seal, while he promotes the phrase "receipt, or it's not shown" (or a listed variant), the sealed search pipeline finds at least 3 independent accounts (none his, none reached by him directly, none repeating his posts) using it in their own words, and finds them in numbers an unpromoted control phrase does not reach. The claim is passed only if the exact one-sided 95% lower bound on the rate of FOUND accounts is at least 3 per 180 days (k of at least 7), with the guards in section 6.

**What a count means.** k counts accounts the pipeline finds, codes and keeps. If independence holds, found accounts are a floor for the true number, so a pass is conservative on the pass side. A low or zero k does NOT bound the true rate, because recall is unmeasured; it only says that few were found. Every bound below is a bound on the rate of found accounts.

**The control is a floor check, not a causal control.** He promotes the target and never the control, and the target has a quotation and snowclone advantage a control does not. An unpromoted control has about 0 expected matches, so beating it is easy once k is 5 or more. It guards against a leaky pipeline and chance matches. It cannot show that the rule's content, rather than his promotion, is what travels (section 4).

---

## 2. Arms

- T0: the time inside the verified FreeTSA token for Seal 1's hash. Horizon 90 is T0 plus 90 days; horizon 180 is T0 plus 180 days.
- k(h): independent accounts for the target by horizon h. c(h): the same for the control. n = k + c.
- A "use" has a platform creation time (UTC) after T0 and up to the horizon. Time unknown means not counted. For a file in a GitHub repository the time is that of the first commit that contains the phrase, if the platform returns it; if not, the use is not counted. Cap: at most 30 such lookups per round, in the sealed candidate order.

### 2.1 Arm T: the target (promoted by him)

**Normaliser N.** Unicode NFKC; lower case; delete every apostrophe and quotation mark with no space left; turn every other run of non-letters and non-digits into one space; trim. Example: `Receipt, or it's "not shown".` becomes `receipt or its not shown`.

**Eight target patterns,** matched as whole words inside N(text). Engines only find candidates; the matcher decides.

| ID | Normalised pattern |
|---|---|
| T1 | receipt or its not shown |
| T2a | receipts or its not shown |
| T2b | receipt or it is not shown |
| T2c | receipts or it is not shown |
| T2d | receipt or it isnt shown |
| T2e | receipts or it isnt shown |
| T2f | receipt or not shown |
| T2g | receipts or not shown |

English only. Paraphrases, other languages, hashtag forms and pre-existing phrases (for example "receipts or it didn't happen") are not counted.

### 2.2 Arm C: the control (never promoted by him)

**Shape rule.** A noun, a comma, "or it's not", a past participle; five words; the same eight-pattern grammar (noun or plural; "its not", "it is not", "it isnt"; and "or not"). The words come from another domain, so it is not a paraphrase of his rule. It must be equally searchable (same punctuation and short words, a rare noun and participle).

**Commitments.** Three candidates K1, K2, K3, in that order of preference, are fixed before Seal 1. This file holds only C(K1), C(K2), C(K3), each SHA-256 of (salt plus the normalised phrase), plus the hash of the salt-and-text file: [SHA-256 AT SEAL]. Text and salt are in the private store. At the reveal he publishes text and salt so anyone can check them.

**Selection rule.** Round 0 searches the target and all three candidates. The control is the first of K1, K2, K3 with 0 raw matches (any author, any date, after N) on every channel run in Round 0. If none qualifies, F7 applies. The selection script runs in his terminal and writes only the index chosen.

**Secrecy and lint.** The lint (H5) stores salted hashes of normalised 4 to 6 word windows of each candidate, not the text. The AI runs it only on the work folder and on synthetic input. He runs it himself, before every post and every round, over any other folder he chooses, and reports only the number of hits. Searching for the control is not promotion, because a query is not a public post.

### 2.3 Exploratory comparators (counted, never tested; R4 and R7 only)

- S1: show me the line, or it isn't done.
- S2: a checker that never says fail proves nothing.

They go through the same pipeline and are reported as counts. He promotes them unequally, so they cannot calibrate stickiness.

### 2.4 What is held fixed

The channels, queries and fixed chunks; the normaliser and patterns; the filters; the coders and masking; the windows; the same-sitting rule (target and control queries on a channel run interleaved, same tool, same settings, same pages per query); the dose at or above the floor (F5); the control unpromoted.

**What he may do.** Promote the phrase anywhere, in any wording, including public invitations. Every public item goes in the promotion log, whose first line records the platform time of his first public item (read from the platform). He must not ask anyone to use either phrase in private. A private ask makes that person I1 and goes in the ledger. A public call to action is allowed; a coder question flags uses that answer a request from him (secondary S13 and a sensitivity row).

**Promotion before T0.** The launch was scheduled before this seal. Uses before T0 are baseline B0: described, never counted. An account whose first use is before T0 is never counted in k. Delay between launch and T0 therefore costs counts; it never adds any.

### 2.5 Randomisation and order

None. The arms are two phrases, not units assigned at random. The control order is fixed. The only chance element is the coding order: sort all candidates for a phrase by SHA-256(Seal 1 hash + candidate ID), ascending. One fixed key for the whole study; no round-specific seed, so no one can grind it by re-running a search.

---

## 3. Population, filters, coding, calibration

**Population.** Public English text with a platform-shown creation time after T0 and up to T0 + 180 days, on six channels: posts, replies, comments, READMEs, docs, issues, pull requests, discussions, commit messages, instruction files (AGENTS.md, CLAUDE.md, GEMINI.md, rules files) and web pages. A census of what the searches return, not a random sample.

| ID | Channel | What is searched | Who runs it | Cap (fixed at the pilot, sealed) |
|---|---|---|---|---|
| X | X posts and replies | Latest tab, fixed 14-day chunks, minus his accounts | He, in his own session; pastes post IDs into a file | 200 per query chunk, equal for target and control |
| GH | GitHub | code, issues, pull requests, discussions, commit messages | He, with his own `gh` login | the platform's limit (about 1,000 per search; verify) |
| HN | Hacker News | stories and comments, public search API | One-shot script, run by him, or by Claude with his yes for that round | about 1,000 per query |
| RD | Reddit | posts and comments, sorted new, fixed chunks | He, by hand | 250 per query |
| SO | Bluesky and Mastodon | post search | He, by hand | 100 per query |
| WB | Open web | one named search engine (named at the seal), quoted queries, visible date in the window | He, by hand | top 50 per query |

Rules: Claude never opens a browser. Nothing keeps running; each round is a one-shot job he starts. No token is read by any AI tool. At most 8 query strings per phrase per channel, listed in the sealed manifest, with straight apostrophes. Pages per query are fixed in the manifest and equal for target and control; he records pages opened. If a channel reaches its cap before the window start it is marked "capped, possibly incomplete". His own sites have no visitor analytics, so site logs are not a channel.

**Per-round record, in this order.** R raw hits returned; M matches after N; X0 dropped as I0; X1 dropped as I1; XE dropped as echo; XC dropped by the credibility filter; XA moved to the agent stream; D coded candidates; then k_strict, k_lenient, k_adopt and B (containers). Kept per phrase and per channel. Read as "k of D coded, from R raw".

**Who counts as independent.**

1. **Tier.** I0: him, his accounts, his agents, anyone paid by him or co-developing. I1: reached directly before the use: (R1) he emailed, messaged or wrote to them by name; (R2) he replied to, quoted or tagged them, or they replied to, quoted or tagged him (each round he exports his own platform mention, reply and quote lists and the ledger takes them in); (R3) asked in person or by call, or in a small private group where he posted the phrase; (R4) an organisation account he emailed or tagged (not its staff); (R5) co-authors, raters and contributors to his gathering paths. I2: neither. Only I2 counts. An account whose first use came before it was reached stays I2 for that use. An account that cannot be classed is not independent. A late ledger entry needs a dated record that the contact came before the use, is logged with its date, and can only remove an author.
2. **Not an echo.** (a) repost, quote-post, boost, share or embed of an item by I0 or I1; (b) a reply to or quote of an item by I0 or I1; (c) a run of 8 or more normalised words shared with the sealed own-texts list, or a block-quote or screenshot of his text; (d) a mirror, fork, scrape or aggregator copy; (e) the phrase only inside words attributed to him. A use whose own words carry the phrase outside quoted text is not an echo even if it names or links him.
3. **Not an agent.** An account that says it is an AI agent or whose text shows it is automated goes to XA and never counts.
4. **Credible account.** Where the platform shows account age and public item count: at least 30 days old and at least 10 earlier public items at the time of the use. It does not apply to the web channel (WB), where the account is the registered domain; WB is reported separately and a sensitivity row drops it. Dropped accounts are counted in XC. This can exclude real new accounts; that is conservative.
5. **Baseline accounts.** First use before T0: never counted.
6. **One account, one count** per phrase per horizon. A salted hash of the handle string is the only merge key across channels. Containers: the repository (salted hash) for GitHub, the thread root for X, Bluesky and Mastodon, the story for Hacker News, the thread for Reddit, the registered domain for the web.

**Coding.** Two coders see the same masked snippet: at most 300 characters, the matched span replaced by [PHRASE], handles by [HANDLE], and his name, the project names, the site names and the protocol and test names by [PROJECT]. Metadata shown: channel and a reply-or-quote flag only. The naming share (S6) is computed by script before masking. Questions: Q1 are the words the author's own (yes, no, cannot tell); Q2 does the text show an agent, bot or scrape; Q3 type: **adopt** (a rule the author uses for their own or others' work, including in an instruction file), **cite** (names it as someone's rule, in praise, neutral or critique), **unrelated**, or **spam**; Q4 does the author say they are answering a request from him. Independent use: Q1 yes, Q2 no, Q3 adopt or cite. **Strict:** both coders agree. **Lenient:** either. k_adopt: strict and both say adopt. Doubt resolves to not independent. Each candidate is coded once and the decision cached by hash.

**Coders.** Coder 1 is Joshua (not blind to his project, which is why strict needs coder 2). Coder 2 is a local model (qwen3.5:9b, labelled "not an independent human") unless a human is named in the ledger before Seal 1 with no declared tie to him, not on the contact ledger, and passes the gate. Coders are fixed at Round 0 and may not change without a v2. A candidate authored by a coder is dropped.

**Where things are stored.** Files in the work and sealed folders hold only: channel, platform ID (never a URL), UTC time, salted hash of the account ID, salted hash of the container, snippet hash, flags and counts. Masked snippets live only in the private store. A scrubber (H1) removes secret-shaped strings, e-mail addresses and phone numbers before any snippet is stored; a secret that still appears is written as [secret]. Real-data runs go through a counts-only wrapper that prints only counts and hashes, so a traceback cannot put a stranger's text into an AI's context. Claude sees counts and script output, never snippets. Deleted posts: he deletes the stored snippet at the next round and the count stays as a flag. Retention: he deletes snippets 90 days after the final result. Any author who asks is dropped; the headline excludes dropped authors and with-and-without is shown beside it.

**Minimum before any analysis.** F4 passed (before Seal 1); legal read done (before Seal 1); Round 0 run and stamped; control chosen; for a horizon, its decision round run inside its grace with F3 clear; F5 clear; every candidate coded by both coders. Interim counts are descriptive and decide nothing.

**Fixed denominators.** 6 channels; 8 rounds (3 mandatory: R0, R4, R7); 8 patterns per phrase; 120 planted items (60 plus 60 mirrors; 40 not independent, 20 independent, with mirrors).

**Calibration of the search (Sonny Test for the instrument).** At Round 0 and each decision round:
- **L1, mechanics:** each channel finds one neutral known public item fixed at the pilot (1 of 1). No owner identifier in that query.
- **L2, recall on his own uses:** the list is the sealed own-uses list plus promotion-log items on that channel at least 7 days old. Run with an unwindowed query (all dates). If the list holds m of at least 10 on a channel, at least ceil(0.7 m) must be found. Below 10: "L1 only, coverage unmeasured".
- A channel is calibrated if L1 passes and, where L2 applies, L2 passes. One rerun of a failed channel is allowed only for a logged operator fault (logged out, rate limit, typo), with the sealed queries unchanged. Both runs are recorded.

---

## 4. Primary outcome and statistic

**Outcome.** k(180): distinct independent accounts (strict) whose first use of a target pattern has a platform time in (T0, T0 + 180 days]. c(180): the same for the control, same pipeline. The 90-day count is read from R4 and the 180-day count from R7; R7 also recomputes k(90) as a check.

**Statistic.** The exact conditional test for two Poisson counts with equal exposure: under no uptake beyond chance, k out of n = k + c is Binomial(n, 0.5). P-value P(Binomial(n, 0.5) at least k); with n = 0, p = 1. One-sided (the claim is directional), alpha 0.05, once, at the 180-day horizon. The 90-day look can fail or narrow but never pass, so it spends no alpha. If c is greater than k, the flag is ANOMALY (section 6).

**Rate bound (found accounts).** Garwood one-sided 95% lower bound L(k): L(3) = 0.82, L(5) = 1.97, L(6) = 2.61, L(7) = 3.29, L(9) = 4.70, L(10) = 5.43. Upper bounds U(k): U(0) = 2.996, U(1) = 4.74, U(2) = 6.30, U(3) = 7.75. The bar is 3, cleared only from k = 7.

**Nominal bound.** These bounds assume independent accounts. Accounts cluster (one thread can bring many). In a simulation (seed 20261005, 40,000 runs) with independent clusters at Poisson rate 2 (below the bar) and about 3 accounts each, the count part passes 39.5% of the time with no guard, 29.0% with at least 3 containers and 5.2% with at least 5 containers. So PASS needs at least 5 containers, and a container-level count is a sealed sensitivity row.

**Detection.** The tables treat found accounts as the process. Recall is unmeasured. Chance of PASS with control rate 0.3, at true target rates 5, 10, 15 per 180 days: detection 1.0: 23.1%, 86.2%, 99.1%; detection 0.8: 10.7%, 67.6%, 95.0%; detection 0.6: 3.2%, 38.5%, 78.3%.

**The limit of the control comparison.** A target count above the control measures promotion plus uptake. It cannot show that this phrase spreads better than any other promoted phrase, or that content rather than promotion is what travels. The sibling counts (2.3) look at this only roughly.

**Secondary outcomes (exploratory; counts and exact intervals, no p-values):** S1 raw uses and uses per account; S2 uses inside instruction files; S3 second-hand uses (reply to or quote of an I2 adopter); S4 time from T0 to first independent use; S5 independent accounts per promotion item in the 14 days before; S6 share naming him or the project (computed before masking); S7 adopt against cite; S8 T1 against T2; S9 per-channel counts; S10 agent stream and credibility drops; S11 sibling counts; S12 k_pairs (unmerged) and k_lenient; S13 uses answering a request from him.

---

## 5. Fail conditions, fixed in advance

Counts are strict unless stated. Figures are Poisson with independent found accounts, recomputed locally.

| ID | Fails if | Count threshold and denominator | What the threshold supports | What it changes |
|---|---|---|---|---|
| F1a | Day 90: few found beyond his channels and direct contacts | k(90) < 3, as k of D(90) coded from R(90) raw | k = 0 limits the 90-day rate of found accounts to under 3.0 (U = 2.996); k = 1 gives 4.74; k = 2 gives 6.30 (so "not shown"). A true 90-day rate of 1, 2, 3, 5, 7 gives a fail 92.0%, 67.7%, 42.3%, 12.5%, 3.0% of the time. If the 180-day rate is a steady 3, 5, 7, 10, k(90) < 3 happens 80.9%, 54.4%, 32.1%, 12.5% of the time | Wording only: "fewer than 3 independent accounts found by day 90". Collection continues. Superseded by the day 180 label |
| F1b | Day 180: fewer than 3 found | k(180) < 3, as k of D(180) coded from R(180) raw | Same bounds as F1a for found accounts. Recall is unmeasured, so this does not bound the true rate | **End the line.** Claim 4 retired as "not shown: fewer than 3 independent accounts found in 180 days". A new try needs a v2 with a new promotion plan. The program continues |
| F2 | Day 180: 3 or more found, but not above control | k(180) at least 3 and p > 0.05 for k of n = k + c(180). Smallest k with p at most 0.05 by c = 0 to 8: 5, 7, 9, 10, 12, 13, 15, 16, 18 (p = 0.031, 0.035, 0.033, 0.046, 0.038, 0.048, 0.039, 0.047, 0.038). At c = 0: k = 3 gives p = 0.125; k = 4 gives 0.0625 | Control rate 0.3 assumed: the count test is cleared (k at least 7 and p at most 0.05) 3.2%, 23.1%, 54.0%, 86.2%, 99.1% at true rates 3, 5, 7, 10, 15. If both rates are equal it is cleared at most 3.9% of the time (2.1% at rate 5; checked at rates 0.5 to 40; never above 5%) | Label "found k of n; control c; p = x; not significant". The line ends at day 180 as scheduled. If c > k: ANOMALY, a pipeline audit, no inference |
| F3 | A decision round could not see enough | Fewer than 4 of 6 channels calibrated, or X or GitHub not calibrated (L1 1 of 1; L2 at least ceil(0.7 m) of m, m at least 10) | At m = 10: recall 0.3, 0.5, 0.8, 0.9 passes 1.1%, 17.2%, 87.9%, 98.7%; at m = 15 (need 11): recall 0.5 passes 5.9%, 0.8 passes 83.6%; at m = 20 (need 14): 5.8%, 91.3%. X and GitHub both pass 77.3% of the time at m = 10 and recall 0.8 | "Not measurable" for that horizon; one logged operator-fault rerun inside the 7-day grace; never a pass or a fail of the claim |
| F4 | The coders and filters could not catch planted faults | Run before Seal 1 on the coders named. Strict pipeline: 0 of 40 not-independent items called independent. Each coder alone: at most 3 of 40 not-independent called independent, and at least 16 of 20 independent called independent. Mirror items (stand-in phrase, never K1 to K3): decisions differ on at most 2 of 60. Strict pipeline sensitivity at least 12 of 20 | 0 of 40 limits the strict miss rate to under 7.2% (95% one-sided); 3 of 40 to under 18.3%; 16 of 20 limits sensitivity to at least 59.9%; 12 of 20 to at least 39.4%. A coder with miss 2%, 5%, 10%, 15% passes the 3 of 40 line 99.2%, 86.2%, 42.3%, 13.0%; with sensitivity 0.95, 0.9, 0.8, 0.7 passes 16 of 20 99.7%, 95.7%, 63.0%, 23.8%; mirror discord rate 1%, 3%, 5%, 10% passes 97.8%, 73.1%, 41.7%, 5.3%. A strict pair with a joint miss rate of 0.5%, 1%, 2%, 5% passes 0 of 40 81.8%, 66.9%, 44.6%, 12.9% | No Seal 1. Rewrite the guide or filters as a v2 and run the gate on a freshly written 60-item set (never the same items). After two failed retries, stop and report. Low sensitivity only lowers k, so it is a mild line on purpose |
| F5 | Dose too low | Fewer than 6 public items by him (own words, a T1 or T2 pattern, dated after T0) by day 90, or fewer than 12 by day 180, or on fewer than 2 channels. Denominator: promotion-log items, once per UTC day per channel, each findable by a search of his own account | A fail with no promotion tells nothing about spread. The floor is low (about 2 a month) | "Not tested: dose too low." A day-90 shortfall voids only F1a. A day-180 shortfall voids F1b, F2 and PASS. The line stays open and a v2 extends the window |
| F6 | Control void | Any public use of the chosen control (or of K1 to K3 before choice) by him, his accounts, his tools or anyone at his request. His own lint over folders: 0 hits. Search of his own accounts on each channel: 0 hits. Denominator: his own public items on that channel at the round (a census; the platform search can miss) | A clean search shows no use the search can see | Control comparison abandoned. If k(180) is at least 3 the label is "not shown: control void". F1 still stands. A new control needs a v2 and its own window |
| F7 | No valid control | All 3 of K1, K2, K3 have at least 1 raw match at Round 0 (denominator 3) | A screen for rarity, not a proof | No Round 1 until a v2 with new candidates is sealed. Not a fail of the claim |
| F8 | PASS guards missing | k(180) at least the pass line for its c and p at most 0.05, but containers B < 5, or k_adopt < 3, or k below 7 | See section 6 | THIN-PASS with the missing guard named |

No C4 outcome ends the program. C4 never touches C1 to C3 or W1 to W4.

**Two guards on fail labels.** (1) The lenient reading is a sensitivity row. If it would change a label's type (fail against positive), the label is prefixed SPLIT and reads "not shown"; a third coder, only with his yes, may adjudicate. (2) The label is also computed without the web channel, without the credibility filter, with dropped authors and with containers; any change of type is reported beside the headline.

---

## 6. Precedence, labels and pass

**Precedence ladder for a horizon (first match wins; every case has one label and one consequence).**

1. Breach or harm trigger (section 7): result void; v2 sealed first.
2. F3 not clear: "not measurable". F5 not clear: "not tested: dose too low". If both, both are named. No pass, no fail.
3. k < 3: F1 (F1a at day 90, F1b at day 180).
4. F6 void (and k at least 3): "not shown: control void".
5. p > 0.05: F2 (add ANOMALY if c > k).
6. p at most 0.05, k at least the pass line (7 or more by the table), B at least 5 and k_adopt at least 3: **PASS** (day 180 only).
7. Otherwise THIN-PASS: "spread seen above a control; bound under the bar" or "breadth not shown" or "adoption not shown".

F7 stops the study before any horizon. At day 90 the labels are only "checkpoint met" (k(90) at least 3) and F1a. Neither is a pass.

**PASS** needs all of: k(180) at least 7 (L at least 3.29); p at most 0.05 against c(180); the k first uses in at least 5 distinct containers; k_adopt at least 3; F3, F4, F5, F6 clear and no breach. With c = 0 and k = 7, p = 0.0078. A pass does not show a virus (self-propagation); S3 only hints at it.

**Count regions by control count c (strict):**

| c | FAIL (k) | NOT ABOVE (F2) | THIN (count part) | PASS (count part) |
|---|---|---|---|---|
| 0 | 0 to 2 | 3 to 4 | 5 to 6 | 7 or more |
| 1 | 0 to 2 | 3 to 6 | none | 7 or more |
| 2 | 0 to 2 | 3 to 8 | none | 9 or more |
| 3 | 0 to 2 | 3 to 9 | none | 10 or more |
| 4 | 0 to 2 | 3 to 11 | none | 12 or more |
| 5 | 0 to 2 | 3 to 12 | none | 13 or more |
| 6 | 0 to 2 | 3 to 14 | none | 15 or more |

In the "PASS (count part)" column, a result that fails a guard (containers under 5 or k_adopt under 3) is labelled THIN-PASS at any c. The "none" in the THIN column means no count-only THIN; guard failures still give THIN.

**Outcome chances at day 180** (Poisson, control rate 0.3, detection 1.0, count part only):

| True target rate per 180 days | FAIL | NOT ABOVE | THIN | PASS |
|---|---|---|---|---|
| 2 | 0.677 | 0.283 | 0.036 | 0.004 |
| 3 | 0.423 | 0.432 | 0.112 | 0.032 |
| 5 | 0.125 | 0.406 | 0.238 | 0.231 |
| 7 | 0.030 | 0.226 | 0.205 | 0.540 |
| 10 | 0.003 | 0.061 | 0.075 | 0.862 |
| 15 | 0.000 | 0.004 | 0.005 | 0.991 |

The hypothesis says a rate of at least 3, but a pass needs a found rate near 10 or more. That is intended: the bar is the lower bound, the claim is large, and the project had "1 star, 0 forks" when the outside review was written. Rates between 3 and about 7 will usually give NOT ABOVE, THIN or FAIL.

---

## 7. Rounds, stop rule, no optional stopping

| Round | When (days after T0) | Purpose |
|---|---|---|
| R0 | within 14 days | Baseline (all-time target and K1 to K3), calibration, control choice. Uses after T0 found here count |
| R1 | 14 (plus or minus 3) | Interim, optional, descriptive |
| R2 | 30 (plus or minus 3) | Interim, optional |
| R3 | 60 (plus or minus 3) | Interim, optional |
| R4 | 93 to 97 (grace to 104) | Decision round for day 90; siblings counted. Mandatory |
| R5 | 120 (plus or minus 3) | Interim, optional |
| R6 | 150 (plus or minus 3) | Interim, optional |
| R7 | 183 to 187 (grace to 194) | Decision round for day 180; final analysis. Mandatory |

Each round: his yes for the search (network, carries his identifier); the clock read by script; target and control interleaved per channel; raw results saved and hashed; filters; coding in the fixed order; the record added to the hash-chained `C4-ROUNDS.jsonl`; then the stamp (a separate yes). Each round searches the whole window again. Skipping an optional interim round for his hours is logged and changes nothing.

**Collection stops at the first of:**
1. R7 complete.
2. His STOP. Before any restart, check for leftover processes.
3. Budget: 36 of his hours (then only R4, R7 and the final report run); US$25 cash if he chooses a paid search tool (default US$0).
4. Harm trigger: a stored snippet holds a secret or personal data (he purges it with a script; Claude only reports; if more than 3 in one round, stop storing text); a counted use is part of harassment or a threat; an author or platform asks us to stop or its terms bar a method (stop that channel, report); any legal complaint.
5. Breach trigger: a sealed file edited; a round run without his yes or outside its grace; unmasked snippets shown to a coder or to an AI; a late ledger entry without a dated record. The affected result is void and a new version sealed first.
6. Calendar limit: if R4 is not run by day 104 the 90-day look is "not run"; if R7 is not run by day 194 the 180-day horizon is "not run" and is never a pass.

A void control (F6) ends only the control comparison.

**Load cap.** There is no n to reach. If more than 150 coded candidates arrive for one phrase in one horizon window, the first 150 in the fixed order are coded and k is a lower bound; a lower bound at or above a pass line stands.

**No optional stopping.** Interim looks decide nothing. No one stops early because the count looks high or low. No threshold moves and no channel is added or dropped after a result is seen. A missing decision round is never a pass.

---

## 8. Budget

| Item | Amount | Assumptions |
|---|---|---|
| Cash | US$0 | Public APIs, his own sessions, his `gh` login. Optional US$25 cap for a paid web-search tool, only with his yes |
| CPU hours (one CPU-only mini PC) | about 3 expected; at most about 8 (about 11 with two gate retries) | Local second reader at about 38 s per masked snippet (qwen3.5:9b figure in the half-life draft). Gate 120 items = 1.27 h. Worst case 600 snippets (150 per phrase per horizon, both phrases, both horizons) = 6.3 h. Scripts are small. No long run |
| His hours | about 25 expected, range 18 to 36, cap 36 | Private inputs 3 h; reading design and guide 1.5 h; legal read 1 h; pilot 2 h; gate 0.7 h; three mandatory rounds at about 1.5 h plus 0.5 h each, 6 h; five optional rounds at about 1 h, 5 h; promotion log and ledger 2.5 h; final report 2 h; reveal 1 h |
| Outside people's hours | 0 by default | Optional: a human second coder, up to 5 h (about US$200 at an assumed US$40 an hour), a C4 default that needs his yes and the conditions in section 3 |

All figures are my assumptions, not measurements.

---

## 9. Decisions assumed (a v2 is sealed first if he chooses otherwise)

From WEAKNESS-PLANS section 4: 4.5 seals (yes to a batch of stamps; FreeTSA first; hash-chained ledger; the block-seed rule is not needed because nothing is drawn); 4.2 raters (see C4-10); 4.6 CPU (short jobs in gaps; he starts every job); 4.15 predictions (sealed privately by hash with probabilities set at the seal; arm results as data; no scorecard); 4.10 network and gh (each network round a separate yes; he runs gh and every manual search); 4.1 and 4.3 (not used; C4 touches no gated data).

From 9.3: 9.3.1 and 9.3.2 (no public ask, no intake host); 9.3.3 legal read before any stranger's text is stored (from memory, verify; not legal advice; platform terms, privacy law for people outside Canada, snippet use, the link list at the reveal); 9.3.4 incentives (none at all); 9.3.5 outside models (strangers' text to a local model only; Claude sees counts only); 9.3.6 custodian (none; control secrecy and the ledger rest on his word and the report says so).

**C4's own defaults (none is in the WEAKNESS-PLANS text):**
- C4-1 T0 is the FreeTSA token time for Seal 1.
- C4-2 Horizons 90 and 180 days; bar 3 per 180 days; pass needs the lower bound at least 3 (k at least 7). A bar of 5 would need k of 10 (L(10) = 5.43).
- C4-3 Unit: distinct accounts; raw uses reported.
- C4-4 Control: K1, then K2, then K3, committed by salted hash; secret until the reveal.
- C4-5 Six channels; three mandatory rounds, five optional.
- C4-6 Dose floor 6 by day 90, 12 by day 180, on at least 2 channels.
- C4-7 Retention: snippets deleted by him 90 days after the final result. At the reveal the design text, counts and per-use hashes are published; a list of links only with his yes after the legal read, with removal on request.
- C4-8 Two sibling slogans counted, never tested.
- C4-9 The pilot is mandatory and runs before Seal 1.
- C4-10 Second coder: local model by default; a human only if named before Seal 1 under the section 3 conditions; ceiling about US$200 for 5 h. This is not a section 4.12 ceiling.
- C4-11 Caps: 150 coded candidates per phrase per horizon; 36 of his hours.
- C4-12 No public line says the rule "spreads" before the sealed 180-day result.

---

## 10. Order of steps

**Hard limits obeyed:** inside the named folders only; never Data or `D:\LIVE`; no key, token or cookie read by an AI; nothing leaves without his yes (each search with his identifier is a yes); nothing deleted or overwritten by an AI; no installs; nothing keeps running; Claude opens no window; no other tool's records opened; no check weakened; commits as ISWT42 with no attribution line; no private person's details in any file (strangers appear only as salted hashes).

### 10.1 In-house steps (no outsiders, no gated data, no outside model on real data)

- **H1.** Build the pipeline (standard library only): normaliser, 16 matchers, echo detector, hashed-ledger matcher, credibility filter, scrubber, counts-only wrapper, hash-chained round writer. Test on synthetic input.
- **H2.** Analysis script (exact binomial, Poisson bounds, labels from the section 6 ladder) with every number in sections 4 to 6 as a test vector.
- **H3.** 60 invented items (40 not independent: own account 5, ledger match 5, repost 5, block-quote 3, 10-word copy 3, embed 2, reply in his thread 3, agent 3, bot copy 3, search-term page 2, unrelated 3, neighbour snowclone 3; 20 independent: adopt 8, cite praise 4, cite critique 4, instruction file 4), 60 mirrors with a stand-in phrase (never K1 to K3), and a coder guide whose examples differ from the planted items. Planted answers are held by the script; he does not read them before the gate.
- **H4.** Mock round on invented files for six channels, reproducing planted counts, one in each region of section 6.
- **H5.** Control lint over the work folder and synthetic input only; he runs it elsewhere.
- **H6.** With him, his private inputs: own-accounts list, own-texts list from the launch package, ledger genesis and promotion log genesis. Salting and hashing are done by a script he runs; the AI never sees a contact name.
- **H7.** Draft the channel manifest, command sheets, data-handling statement and legal-read request. Nothing is sent.
- **H8.** Run the gate on synthetic items: his masked reading and the local model. This is F4.
- **H9.** Hash every file, build the manifest, and his envelope of probabilities.
- **H10.** Count draft items in the launch package against the dose floor. Descriptive only; drafts are not confirmed public items.

### 10.2 Steps that need his yes

- **Y1.** The pilot (network, neutral phrase, no identifier) and Seal 0 hash.
- **Y2.** The legal and terms read, then the coder decision (human or model).
- **Y3.** Seal 1: SHA-256 manifest, FreeTSA, OpenTimestamps (network, hashes only), with a yes or no on each default. T0 is read from the verified token.
- **Y4.** Round 0 and calibration (network with his identifier; each channel named; X, Reddit, Bluesky and Mastodon and the web by him; GitHub through his gh; Hacker News by script). Then the control by the sealed rule.
- **Y5.** The stamp of each round record (hash only).
- **Y6.** Each later round: one yes for the search and a separate yes for its stamp.
- **Y7.** The reveal after R7 and any removal requests.

---

## 11. What is sealed

| File | Content |
|---|---|
| `C4-DESIGN-v1.md` | this document |
| `C4-PATTERNS-v1.json` | normaliser, 8 target patterns, shape rule, K1 to K3 salted commitments, S1 and S2 |
| `C4-CONTROL-PRIVATE-v1.txt` | in the private store; only its hash is sealed |
| `C4-CHANNELS-v1.json` | channels, queries, caps, chunks, pages per query, neutral items |
| `C4-OWN-ACCOUNTS-v1.sha`, `C4-OWN-TEXTS-v1.txt` | salted hashes of his account IDs; his public texts and own-uses list |
| `C4-LEDGER-GENESIS.json`, `C4-PROMOTION-LOG-GENESIS.json` | heads of the two hash chains |
| `C4-CODER-GUIDE-v1.md` | definitions with invented examples |
| `C4-PLANTED-v1.jsonl`, `C4-PLANTED-ANSWERS-v1.json` | 60 items, 60 mirrors, answers |
| `C4-PIPELINE-v1.py`, `C4-ANALYSIS-v1.py`, `C4-CONTROL-LINT-v1.py` | code and test vectors |
| Gate outputs | F4 gate (run before Seal 1), mock round, analysis vectors |
| `C4-PREDICTIONS-v1` | his envelope's hash and Claude's forecast |

All hashes: [SHA-256 AT SEAL]. Then FreeTSA, then OpenTimestamps. Only hashes and proofs leave the PC before the reveal. `C4-ROUNDS.jsonl` is hash-chained from Seal 1's hash.

**Predictions (private; no public scorecard).** P1 k(90) at least 3; P2 k(180) at least 3; P3 day 180 label is PASS; P4 c(180) = 0; P5 at least 1 independent use in an instruction file; P6 at least 1 second-hand use; P7 first independent use within 30 days of T0; P8 X gives more than half; P9 more than half are "cite"; P10 dose floor met; P11 the pre-T0 baseline at Round 0 is 0 accounts. His probability for each: [HIS PROBABILITY].

---

## 12. What this design cannot show

- That he caused it, or that the phrase has pull. Promotion plus uptake only.
- That anyone follows the rule, or that AI systems took it up. Instruction-file uses are written by people.
- Anything in private places, or his own sites' visitors.
- That zero means none. Recall is unknown. Counts are a floor of what the pipeline finds. L1 checks mechanics and L2 checks only recall on his own uses, which is optimistic.
- That independence is true. It is attested by absence from his ledger, which rests on his word. Hidden ties, sockpuppets and AI-assisted posts cannot be seen.
- That the control is clean. Its secrecy rests on his word and tools. On the open web his indexed pages may help the target and not the control; the sensitivity row without the web channel shows how much.
- Spread past 180 days, or beyond English.
- That timestamps are right. Platform and commit dates can be forged; a missing time means not counted.
- That the rule is good. A bad rule can spread.
- That nobody looked early. A seal shows a plan existed by its time. He has seen launch-day replies. That part rests on his word.

---

## 13. Doubts considered and dismissed

- **"An unpromoted control is always 0, so the comparison is empty."** Accepted in part; stated in section 1. It still catches a leaky pipeline and chance matches. Wrong if c is 1 or more.
- **"Use another of his slogans as a promoted control."** Dismissed for the primary; kept as exploratory siblings.
- **"Count reposts as spread."** Dismissed: they measure his reach.
- **"Count raw uses."** Dismissed: one prolific person could carry the test.
- **"Three is too low a bar."** Accepted in part: 3 is the fail line, and the pass needs the lower bound at least 3.
- **"A one-sided test is too kind."** Kept: the claim is directional and the pass count of 7 already sits above the c = 0 line of 5.
- **"Wait a year."** Dismissed; a longer horizon is a v2.
- **"Ask friends to use it."** Dismissed: it is promotion and those uses are I1.
- **"Let an outside model code the snippets."** Dismissed: strangers' text goes to local models and people only.
- **"Merge accounts by looking at profiles."** Dismissed: it compiles personal information across sources; a shared handle string hash is the only merge.
- **"Ask the public to report uses."** Dismissed: a public ask and an intake duty; not in v1.
- **"The author codes his own project."** Accepted: strict needs the second coder, snippets are masked and the lenient reading is shown.

---

## Appendix: adversarial review before the seal (verdict: sealable with fixes)

17 problems were found; every fix is already in the text above. High-severity ones:

- **The control-void lint and several in-house steps (F6, H5, H10) scan 'all his local folders'. If an AI runs or writes that scan it reaches D:\LIVE, Data, other AI tools' folders and anything outside the named work folder. That breaks hard limits 1, 2 and 9. Also H10 counts 'drafts and logs' as promotion items although drafts are not public posts.**
  Fix: The AI-run lint scans only the named work folder. He runs a second lint himself over any other folder he chooses and reports only the hit count. The lint stores salted hashes of normalised 4 to 6 word windows, never the control text. H10 counts drafts in the launch package only and says plainly they are not confirmed public items.
- **The sealed design file prints the three control candidates in plain text, inside a folder AI tools read, while the same file says the control is secret and that no AI may write a control string anywhere. Every AI that opens the folder becomes a leak path (F6). Mirror planted items also 'swap in the control phrase', which would put the real control into planted files.**
  Fix: The design holds only salted SHA-256 commitments for K1 to K3 and the shape rule. Plaintext and salt live in the private store, outside every AI-readable folder. Mirror items use a stand-in phrase of the same shape that is never K1 to K3. Selection runs by script in his terminal and the log records only the index chosen.
- **The bounds are stated as bounds on the TRUE rate ('k = 0 shows the rate is under 3.0') but k counts only accounts the searches find, after coder strictness and the credibility filter. Recall is unmeasured, and the section 12 line 'k = 0 limits the rate to under 3.0, no further' contradicts the unknown-recall caveat. At a detection fraction of 0.6 the chance of PASS at a true rate of 10 falls from 86.2% to 38.5%, so the power table overstates what the design can do.**
  Fix: All bounds are restated as bounds on the rate of accounts the sealed pipeline can find. The PASS side stays conservative (found accounts are a floor, if independence holds). The FAIL side becomes 'not found', and the true-rate bound is the found bound divided by an unmeasured recall. A detection-adjusted power table (0.8 and 0.6) was recomputed and is added.
- **The container guard (at least 3 containers) is too weak. With independent clusters at a Poisson rate of 2 (below the bar) and about 3 accounts per cluster, the count part passes 39.5% of the time with no guard, 29.0% with 3 containers and 5.2% with 5 containers (simulation, seed 20261005, 40,000 runs). The Poisson lower bound L(7) = 3.29 assumes independent accounts.**
  Fix: PASS needs at least 5 distinct containers. The headline bound is labelled nominal, and a container-level count is a sealed sensitivity row.
- **Regions are not fully defined. THIN-PASS text covers k >= 7 with too few containers or adopters at any control count, but the region table says THIN is 'none' for c >= 1. F1b says 'end the line' with no rule for what happens when F3 or F5 is unclear (F1a has one, F1b does not). There is no precedence between F3, F5, F6 and the count labels, and c > k is called 'anomaly' with no consequence. A day-90 dose shortfall is not tied to the day-180 result.**
  Fix: A single precedence ladder is added (section 6) with one label and one consequence for every combination. The region table is rebuilt so that guard failures give THIN at every c. The anomaly flag triggers a pipeline audit and never a pass. A day-90 dose shortfall voids only F1a.
- **F3 (instrument blind) uses L2 recall of at least ceil(0.8 m) of his own uses with m >= 5. A good channel at recall 0.8 passes only 73.7% (m = 5) or 67.8% (m = 10). X and GitHub must both pass, so a healthy instrument voids a decision round about half the time (0.678 squared = 46%). 'Repair and rerun' with no limits is also a retry-until-pass fork. In addition the L2 list is sealed before T0 but the searches only cover (T0, horizon], so the pre-T0 uses cannot be found by a windowed search.**
  Fix: L2 applies only when m >= 10, needs at least ceil(0.7 m) found, and is run with an unwindowed query on the sealed list plus promotion-log items at least 7 days old. Recomputed: at m = 10 recall 0.5 passes 17.2%, recall 0.8 passes 87.9%, so X and GitHub both pass 77.3% of the time. One rerun is allowed only for a logged operator fault with the sealed queries unchanged.
- **F4 (coding gate) is too strict to be usable and is badly placed. 0 of 40 plus 18 of 20 plus 60 of 60 mirror agreement passes a coder with 5% miss and 90% sensitivity only about 20% of the time. The mirror rule of 60 of 60 is brittle for a 9B model. Retrying after a rewrite on the same planted items trains on the test. The gate is sealed pre-seal (section 11) yet written as a post-seal fail with a second coder chosen post-seal. Joshua is coder 1 and also reads the planted set, so he may know the answers.**
  Fix: The gate runs before Seal 1 on the coders actually named. Thresholds are set per stage: strict pipeline 0 of 40 not-independent called independent; each coder alone at most 3 of 40 and at least 16 of 20; mirror decisions differ on at most 2 of 60. Every retry uses a freshly written 60-item set. He does not read the answers file before the gate. Pass chances were recomputed and are listed.
- **No-handle rule is contradicted. The design says no handle or name is written to any file, but it stores 'URL or ID' per hit, and X, Mastodon and GitHub URLs contain handles. Masked snippets can contain other people's names and secrets (instruction files), yet snippets are said to be stored per round record. Rule 12 and rule 3 are at risk. A traceback from a real-data run could print snippet text into an AI's context.**
  Fix: Only platform IDs and salted hashes appear in files in the work folder. Snippets live only in the private store. A scrubber removes secret-shaped strings, e-mails and phone numbers before any snippet is stored. Real-data runs go through a counts-only wrapper (as in the W1 and W3 plans). Repository names are stored as salted hashes. Links are rebuilt only for a published list at the reveal, with his yes.
