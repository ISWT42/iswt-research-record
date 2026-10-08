# C1: Do people act on purpose context? Design v1, reviewed revision r1

## 0. Header

- Design id: C1-PURPOSE-CONTEXT
- Version: v1 (reviewed revision r1; replaces the first draft)
- Status: DRAFT FOR SEAL; nothing run
- Drafted: 5 Oct 2026
- Owner: Joshua Bauer (ISWT42). Nothing in this design goes up, is sent, is posted or is stamped without his yes. One yes covers one action unless he names a batch in chat.
- Labels used: P = the version that states the purpose. N = the same ask without the purpose paragraph. X = how many of the first 100 counted submissions carry P.
- Legal points are from memory, verify; not legal advice.
- Files this design depends on (read, not changed): WEAKNESS-PLANS-2026-10-05.md (sections 4 and 9.3; 1 to 3, 5, 7, 8); GATHERING-PATHS-2026-10-05.md (the W3 path for the ask, notice, receipt, caps, near-duplicate rule and embargo; the W1 path for notice and receipt patterns); OUTSIDE-REVIEW-BIGGER-2026-10-05.md (read; one figure cited, see 2.2); IDEAS-TO-TEST (searched only); PROTOCOL-HALF-LIFE draft (not used).
- Read-scope disclosure: the first drafting run's folder-wide search returned a few lines from two files not on the task list (the RECORD-LAUNDERING draft and rooms-review-template.html). Nothing from them is used. He should be told.
- Any change after the seal is a new version, sealed before the step it affects; sealed files are never edited.

## 1. Hypothesis

His words, as relayed in the task text (not found in any readable file): 'humans will act on it if they contextually know that the information they have could potentially result in their desired ending.'

Testable form: when the same honest ask is shown at random in two versions, the version that states how the contribution could lead to the end state (P) gets more than half of the first 100 counted submissions, meaning 59 or more of 100 (exact one-sided binomial, alpha 0.05). The hypothesis is directional and one-sided; a result of 59 supports only 'some effect' (exact lower bound 0.503, relative response 1.01). Every verdict prints the exact lower bound and relative response.

Terms fixed here:

- **Act** means sending one counted submission (3.3).
- **Purpose context** means Block P (2.2). It is the only text that says why the exam exists, what passing or failing could mean, and what could follow. Both versions say what happens to the item (immediate use: it may be a question in a test of an AI checker). Only P says why that matters.
- **Share** is the fraction of counted submissions that carry P. **Relative response** is share divided by (1 minus share). Share 0.60 means P gets 1.5 times as many submissions per visitor; 0.667 means 2 times.

## 2. Arms

### 2.1 The ask (fixed, the same in both arms)

The smallest ask of the W3 gathering path: write one invented exam item in about 10 minutes (a made-up record of 4 to 40 lines, a one-sentence 'done' claim, the right answer shown, contradicted or not shown, and the proving lines). Everything is invented. No real person, company, account, key or token. Nothing from the AI Village data. This ask brings no gated or personal data by design, is first in the default order of WEAKNESS-PLANS 9.3-1, and the purpose in Block P is real.

### 2.2 The page blocks (drafts; final bytes are sealed at Seal 2)

**Block T (title; also the page title and link-preview text, both arms):** Write one made-up test item (about 10 minutes)

**Block A (the ask, both arms):**

I am looking for short, invented records to use as questions in a test of an AI checker.

What you write:
1. A record you invent: 4 to 40 lines of plain text, such as a tool output, a CI log, a deploy log, a ticket history or a chat thread.
2. One sentence that someone says 'done' about. The thing it names has an invented name. Shape: 'I uploaded the <invented name> archive.' Make up your own name; do not reuse this shape's words.
3. The right answer: shown (the record proves the claim), contradicted (the record disproves it) or not shown (the record does not say either way).
4. The line number or numbers that prove or disprove it.

Rules: invent everything; do not copy a real log, even with the names changed. No real people, companies, accounts, addresses, keys or tokens. Use only example.com for links and addresses. Plain text only; no code meant to be run. The answer must follow from the record alone.

What you get: a receipt that shows what you sent and when, and credit under a pseudonym, your name or nothing, as you choose.

**Block P (version P only; 127 words in this draft; cap 130):**

Why this matters. An AI agent that says 'done' is sometimes wrong. I am testing a checker that reads a record and says whether such a claim is shown, contradicted or not shown. So far one checker has passed one exam, at the bar, and a second checker missed it. I wrote both the exam and its planted faults, so that result is weak. If your item goes into a sealed exam, the checker is tested on something I did not write. If it holds up, people would have a better reason to trust a 'done' report that comes with a checkable record. If it fails, I will publish that too. Your item cannot decide the result. It could be one small step toward an answer.

Honesty checklist for Block P (by hand before Seal 2, and by the pilot readers):

- 'One checker passed one exam, at the bar, a second missed it' traces to the W3 plan (141 of 150 for gemma4:12b with 45 of 50 exactly at the bar; 140 of 150 for qwen3.5:9b, shown 42 of 50). 'I wrote both the exam and its planted faults' traces to the same plan.
- 'Sometimes wrong' traces to the Kaggle result (for example two models said 'done' in 35 of 96 failed-check replies under the plain prompt). OUTSIDE-REVIEW-BIGGER says that figure is not readable by script. He confirms it by hand from his own output before Seal 2, or the sentence becomes 'can be wrong'.
- Every sentence about the future uses 'if' or 'could'. It states the failure case and a promise to publish it [HIS CALL: this commits him].
- No number, name, deadline, crowd, story or guilt line is added. The phrase 'a record the agent can't change' is not used (held until W2 reports).

**Block F (form, both arms):**

Your item: [record box] [claim box] [answer: shown / contradicted / not shown] [proof line numbers]

Four short questions (all required):
1. Did an AI help write this item? (No / An AI helped me and I edited it / An AI agent wrote it for me, and I am sending it with my own yes)
2. Where did you find this page? (A post or thread / A link on a website or README / A person told me / A search or something else / Joshua asked me directly)
3. Before today, have you had private contact with the author, or been asked by him to do this? (No / Yes)
4. Have you seen this page before with different wording? (No / Yes / Not sure)

Pseudonym: [made for you; you may change it]. Credit: [pseudonym / my name: ____ / none; default none]. Email (optional, only if you want your receipt re-sent or a reply): [ ]

Tick boxes (all required except the last): I am 18 or over. I made this item up; it holds nothing real or confidential. I have read the notice below, and I understand that this page has two wordings and that which one I saw is recorded with my item. I allow my item to be used and published as the notice describes, under CC BY 4.0 (proposed). (Optional) If no exam uses my item within 12 months, publish it anyway.

[hidden field, left empty by people] [Send item]

**Block C (notice, byte-identical in both arms):**

**Who I am.** ISWT42 (Joshua Bauer), an independent researcher in Canada [HIS CALL: name shown]. This is not paid work. No ethics board reviewed it. You can stop at any time and nothing happens to you. You must be 18 or over.

**Two wordings.** This page has two wordings. One is shown to each visitor at random. I do not track who visits, so I do not count visitors. If you send an item, I record which wording you saw, with your consent, sealed so that I cannot read it until the study closes, so I can compare how many people send an item after each wording. Both wordings are honest. I will publish both after the study closes.

**What I collect.** Your item (record, claim, answer, proof lines). A pseudonym and your credit choice. Which wording you saw (sealed). Seconds spent editing (screens out automated submissions). Your answers to the four short questions. Optional: an email address. A random receipt number and salt, and a random device number, made in your browser.

**What I do not collect.** No real name (unless you choose it for credit), no location, no device fingerprint, no analytics, no cookies, no visitor count. I do not store IP addresses. The host that serves this page may log network data for security and may count requests per address for a short time to stop floods: [HOST FACT: fill in only after checking the host's real settings].

**Stored on your device.** This page keeps four things in your browser's own storage: which wording you saw, the random device number, your pseudonym, and an unsent draft with the seconds spent. They stay on your device and are sent only when you send an item (the wording is sent sealed). Clear your browser storage to remove them.

**Why.** Your item may be used as one question in a sealed exam for an AI checker. The exam is run once and its results are published. The other data compare the two wordings and screen out automated or duplicate submissions.

**How it is used.** The comparison is one analysis, fixed before this page opened and run once by a script on my own computer. No hosted AI model reads your item, your answers or your email. When an exam is run, AI models on my own computer read the items. AI assistants help me write and test my scripts; they never read items, answers or emails, and before the study closes they see only counts and script output. I read some items myself while the study runs, to check they are genuine.

**Who sees it.** Before the exam is run: me, and the host that serves this page. After the exam has run, your item is published with your credit choice. After the study closes I publish the number of items sent after each wording and a table with only a row number, the wording and whether the row counted. Your row number is on your receipt. I never publish your email or your seconds.

**How long I keep it.** Your item: until its exam has run and been published, then it stays public. If no exam uses it within 12 months, it is deleted unless you ticked 'publish anyway'. Email: 90 days after the study results are posted. Seconds, device number and your answers to the four questions: 12 months after the results. The counts and the row table stay as long as the study is public.

**How to withdraw.** Use the withdrawal code on your receipt (I store only its hash) on the withdrawal page, or write to the address on iswt.ca with your receipt number and salt. Before the study closes I delete your item, your answers and your email, and your row leaves the analysis. After that I delete the same things, re-run the numbers without you, and post a dated correction that shows both results. I keep one anonymous tally of how many people withdrew after each wording.

**What withdrawal cannot undo.** A hash already stamped in the public record (it cannot be linked back to you once your random number is deleted), copies of anything already published, and the anonymous tally.

Notes to Joshua, not public, to settle before Seal 2:

- [HOST FACT] must come from the host's real settings. Do not promise 'we store nothing' unless true.
- [LEGAL READ, from memory, verify; not legal advice] PIPEDA may not cover a non-commercial independent study; I follow its spirit. GDPR may apply to people in the EU or UK. Quebec law may apply. Storing a value on the device (sticky version, device number) may need consent in the EU even with no tracking. Age of majority differs by province; 18 is the floor used.
- The notice says assistants never read items and see only counts. Keep that true: weekly checks and the validator are run by him, and the review viewer shows no version.

### 2.3 The two arms, exactly

| Arm | Page = these blocks, in this order | Words added by the arm |
|---|---|---|
| N (no purpose paragraph) | T, A, F, C | none |
| P (purpose paragraph) | T, A, P, F, C | Block P, 127 words in this draft, 130 at most |

Version P is version N with Block P inserted between Block A and Block F. `diff_pages.py` proves it on the final bytes. `purpose_lint.py` proves the rendered N text holds none of the P-only phrases ('Why this matters', 'sometimes wrong', 'weak', 'holds up', 'trust', 'decide the result', 'second checker', 'at the bar', 'toward an answer'). The page source holds Block P in an inert template for N visitors, so a person who reads the source or a crawler that does not run scripts can see it; this is stated in section 12.

### 2.4 Held fixed

The ask, the form fields and order, the button text, the tick boxes, the notice, the incentives (receipt and credit choice only), the URL, the host, the style sheet, the page title and link preview, the channel texts, the validator, the window, the analysis and the person who runs it. Channel texts, title and link preview say only the ask and the incentives, never the purpose. The page has no outbound link to a purpose page in either arm. Not held fixed, and said so: P is about 640 characters longer (under 1 KB). That difference is part of what the test measures (section 12).

### 2.5 Randomisation, blinding and its seed rule

- **Unit:** one device (browser storage). **Probability:** exactly 1/2 each. The coin is `crypto.getRandomValues` (one byte, lowest bit; 0 gives N, 1 gives P; 256 is even, so no bias). If it or WebCrypto is missing, the page shows the ask text without the form and assigns no version. It never falls back to `Math.random`. A visitor without scripts sees the ask text and a line that the form needs scripts; they cannot submit.
- **Where:** in the visitor's browser from one static page. Block P sits in an inert template and is inserted only for P. No second fetch (a second fetch would count P exposures at the host).
- **Sticky version and device number:** the page stores the version (with the design tag 'c1v1') and a random 128-bit device number in one local-storage key, so a reload or return visit from the same browser keeps the same version. A stored version that is not 'P' or 'N' is discarded and a new coin drawn once. If storage is blocked, a fresh coin is drawn per load and the submission has no device number (row R6).
- **Blinding:** the browser encrypts the version (WebCrypto RSA-OAEP, a public key sealed at Seal 2) and sends only the ciphertext. The private key is made offline by him in a file named c1_lockbox.pem and is used only by the Y7 decrypt script after Seal 3b. No assistant opens it. This blocks accidents and assistants; he could decrypt at any time, so F5 still rests on his word, but any decrypt before Y7 is a logged breach.
- **Seed rule:** no seed for the live coin (an unseeded CSPRNG cannot be ground). The seed (first 16 hex digits of the Seal 1 manifest SHA-256) is used only for the sticky-logic stub test.
- **No exposure count.** No visitor is tracked, so exposures are not counted. Random assignment makes expected exposures equal; the submission share estimates the relative response.

### 2.6 What must hold for share to mean relative response

1. Each device gets an independent fair coin (G1).
2. The recorded version is the version shown (reported by the visitor's own browser; someone determined can forge it, section 12).
3. Equal traffic in expectation: same URL, same weight within 1 KB, same host, no caching by version.
4. The counted set is decided without the version (validator, scanner, review and stop rule never see it; G3).
5. Each counted submission comes from a different device (rule 6 of 3.3), and a person saw one version, not both (3.7 handles the rest).

Under the sharp null (version changes nobody's decision to send), the versions of the counted senders are independent fair coins, and X is exactly Binomial(100, 1/2), even if people arrive in bursts. This holds only while rule 5 holds; 3.7 gives the cost when it does not.

## 3. Population and sample

### 3.1 Population

Adults (18 or over) who open the page from the sealed channels and choose to send a counted submission. Self-selected. English only. Not a sample of people in general (section 12).

### 3.2 Channels (named and sealed at Seal 2)

One thread post and one site or README link, named exactly in the Seal 2 file. Posts are mandatory on day 0 and day 28, and on day 56 only if the extension applies; each post needs his yes. Texts are ask-only. Draft text (204 characters with the placeholder; re-count with check_posts.py): Write one made-up test item for an AI checker: a short invented log, a one-line 'done' claim, and the right answer. About 10 minutes. You get a sealed receipt, and credit if you want it. [C1 PAGE ADDRESS]. Not used: the to-agents page (this test is about people), and pages that state the purpose (they would hand N visitors purpose context). Direct asks to people he knows go to the tied stream (3.3).

### 3.3 What counts (every rule is evaluated without the version)

A submission is **counted** only if all hold:

1. The hidden field is empty.
2. All required ticks are present.
3. Editing seconds are at least the floor: 0.5 times the fastest pilot human completion, not under 30 and not over 90 seconds; fixed at Seal 2.
4. The item passes validator v1: 4 to 40 plain-text lines; a claim; an answer in the set; proof lines inside the record; links and addresses only at example.com; no control, zero-width or bidirectional characters; no encoded blobs; no formula starters; at most 8 KB; and the secret and personal-data scanner finds nothing (non-example.com emails, phone patterns, key-like strings, private-key headers, long high-entropy strings). Scanner hits are quarantined unread, deleted at close, and counted for F6.
5. It is not a near-duplicate of an earlier received valid item: equal normalised SHA-256, more than 60% shared 5-word shingles, or the same invented object name (aligned to the W3 rule).
6. It is the first counted item for its device number, its pseudonym and (if given) its email. Later items are 'extra items': kept for the W3 pool, not counted. Items with no device number are counted on pseudonym and email only and are marked for row R6.
7. Question 1 is not 'An AI agent wrote it for me' (those go to an agent stream, reported apart).
8. Question 3 is 'No' and question 2 is not 'Joshua asked me directly' (others go to a tied stream, reported apart).
9. It is not burst-held, or it was burst-held and passed review. A burst hold: any 60-second window with 6 or more received items holds every item in that window. Only burst-held items are manually reviewed, by him with the version unavailable, with one question: is this a distinct, genuine attempt? Items beyond his 40-item reading cap stay uncounted.
10. It was not withdrawn before lock.

Sequence number = receipt order at the intake. 'First 100' always means the first 100 counted by sequence number, even if a held item is approved late.

### 3.4 Counts reported, each with its own denominator

R = received (cap 300). Then each as 'n of R', and by arm only after lock: honeypot filled; too fast; invalid item; scanner hit; near-duplicate; extra item; agent-written; tied; burst-held and rejected on review; withdrawn. Then provisionally counted c (the form closes at 110) and the analysed set (100). Before lock only totals are shown, never an arm count.

### 3.5 Minimum before any analysis

100 counted. No analysis, test or split look at any smaller count. The public counter shows only 'counted c of 100' and 'received r of 300', updated at weekly checks.

### 3.6 Bots and automated submissions

In order: hidden field, time floor, validator and scanner, near-duplicate rule, one counted item per device, pseudonym and email, the burst hold, host flood limits (not stored in the data). No third-party CAPTCHA and no tracking. Declared agent items go to a separate stream. After lock, with the version still sealed, he reads the 100 counted items once and marks 'genuine attempt' or 'not genuine' (rubric sealed: a record, a claim and an answer that someone made an effort to write for this ask, even if poor; not genuine means random text, boilerplate repeated across items, text copied from elsewhere, or off topic). j = number not genuine. The marks are sealed (Seal 3b) before the decrypt. Bound: if m of the 100 were forged P votes and the rest fair coins, the chance of reaching 59 is 4.43% (m=0), 5.4% (1), 6.5% (2), 7.7% (3), 10.9% (5), 17.4% (8), 23.0% (10), 41.4% (15). A bot that writes valid, distinct, plausible items passes all of this (section 12).

### 3.7 Repeat visitors, same-person repeats and what each does to size and power

- Prevention: the sticky version and device number (2.5) and rule 6 of 3.3.
- Not prevented: another device or browser, cleared storage, a private window, a shared computer. Question 4 is asked in both arms; the primary keeps everyone (question 4 is answered after exposure), and row R2 drops 'Yes' and 'Not sure'.
- Random labels dilute. Suppose a share f of counted items come from people whose label is a fair coin whatever they read. Power of the 59-of-100 rule:

| True P share | f = 0 | f = 0.1 | f = 0.2 | f = 0.3 | f = 0.4 |
|---|---|---|---|---|---|
| 0.600 (relative response 1.5) | 62.3% | 54.3% | 46.2% | 38.3% | 30.8% |
| 0.667 (relative response 2) | 95.7% | 91.2% | 84.2% | 74.4% | 62.3% |
| 0.700 | 99.3% | 97.7% | 94.2% | 87.4% | 76.6% |

Random-label contamination lowers power and does not raise the false-pass rate.

- Same-coin repeats do raise it. If k pairs of the 100 counted items share one coin (one person, two items, no device-number break), the false-pass chance under no effect is 4.43% (k=0), 5.23% (k=5), 6.02% (k=10), 7.55% (k=20), 10.13% (k=50). This is why rule 6 and row R6 exist. The residual (a person with two devices or cleared storage) gets two independent coins and does not raise size.

### 3.8 Channel mix

Question 2 records the channel (same options in both arms). A table of channel by version (counts with denominators), no per-channel test, descriptive only. Validity does not need an equal mix: the coin is per device. If one channel supplies 60 or more of the 100 counted, the result is labelled 'single channel' and the claim is stated for that channel only, whichever way the test goes. Row R4 drops the largest channel.

## 4. Primary outcome and the exact statistic

- **Outcome:** X = number of the first 100 counted submissions carrying P. N count = 100 minus X.
- **Test:** exact one-sided binomial. H0: share is 0.5 or less. H1: more than 0.5. Alpha 0.05, one-sided, a single primary test. p = sum over i from X to 100 of C(100, i) / 2^100, by integer arithmetic (math.comb), cross-checked by Pascal's rule and Monte Carlo (200,000 fair-coin runs gave 4.45% against exact 4.43%).
- **Decision count:** the smallest count with tail at most 0.05 is **59 of 100**. P(X at least 59) = 0.0443. P(X at least 58) = 0.0666.
- **Reported beside it:** point share; relative response X/(100 minus X); exact one-sided 95% lower bound (above 0.5 exactly when X is 59 or more); exact two-sided 95% Clopper-Pearson interval; Wilson interval for display. Lower bounds: X=59 gives 0.503 (relative response 1.01); 60: 0.513; 65: 0.564 (1.29); 68: 0.595 (1.47); 69: 0.605 (1.53); 75: 0.669. A lower bound at relative response 1.5 or more needs X of 69 or more.
- **Why exact:** no z-approximation, no continuity correction; n = 100 is small.
- **Family:** the reversed test (F1r) is a second one-sided test at the same count, so under no effect the chance of some strong verdict is 8.86%. Stated, not corrected: each direction is its own pre-registered claim.
- **Not primary (exploratory, no verdict, no correction):** share among all received before validation; validator pass rate by arm (Fisher exact, two-sided); median editing seconds by arm; share answering Yes or Not sure to question 4, by arm; share giving an email, by arm; channel table; agent and tied streams.
- **Two-sided note:** a two-sided test at 0.05 would need 61 of 100 (P(X at least 61) = 1.76%; at least 60 = 2.84%). The claim is directional.

## 5. Fail conditions, fixed in advance

Counts first, then rates; each with its own denominator. None ends the program: C1 tests a gathering method, not the Sonny Test.

| # | Fail condition | Threshold and denominator | What it supports | What failing changes |
|---|---|---|---|---|
| F1 | P does not clearly get more than half | X under 59 of the first 100 counted | Size 4.43%. Primary-rule power: true share 0.55: 24.1%; 0.60: 62.3%; 0.667: 95.7%; 0.70: 99.3%. Joint 'shown' chance with all rows (simulated): 4.2% at 0.50; 61.2% at 0.60; 95.0% at 0.667. Upper bounds: X=50: 0.586 (1.42); 54: 0.625 (1.67); 58: 0.664 (1.97); 45: 0.537 (1.16); 40: 0.487 | Claim 1 stays 'not shown', never 'no effect' (a true 1.5 still fails 37.7% of the time). Gathering paths keep plain honest notices and do not cite C1 |
| F1 label | X from 55 to 58 of 100 | Chance under no effect 14.0%; at true 0.55, 30.0%; at 0.60, 24.6%; at 0.667, 3.8% | Label 'not shown, leans P'. No decision depends on the label | Same as F1. A larger v2 is optional |
| F1r | N clearly ahead | X at most 41 of 100, and the N-side removal check holds | 4.43% under no effect; 0.3% at true 0.55; 0.01% at 0.60 | 'Contradicted in this test'; purpose paragraph dropped from gathering asks until a v2 |
| F2 | Minimum never reached | Fewer than 100 counted at the close date (rules in section 7) | Constant rate: 67 at day 56 reaches 100 by day 84 | 'Not tested'; counts only; no split analysis; end the line for this ask and channel set |
| G1 | Assignment broken | Real-RNG 1,000,000 draws outside 500,000 plus or minus 2,000; page function 10,000 draws outside 5,000 plus or minus 200; sticky stub 5 of 5 | 4 SE; false alarm 0.006%; finds 0.3 points 97.7%, 0.2 points 50%; a 0.2-point bias moves false-pass to 4.82%, 0.5 to 5.45%; the 10,000-draw test finds 3 points 97.7% | Page does not open; no rerun without a code change and new seal |
| G2 | Honesty gate | 0 flags among 3 to 5 pilot readers after the fix round | 0 of 4 bounds flaggers under 52.7% (3: 63.2%; 5: 45.1%); catches obvious problems only | Page does not open |
| G3 | Blinding gate | 0 of 100 synthetic exports show a readable version; 100 of 100 decrypt | Mechanism check, not a proof against the author | Page does not open |
| F3 | Not-genuine items and removals | r = j + post-lock withdrawals; r of 11 or more of 100 void; r of 1 to 10 uses the sealed count table | False-pass if all r were forged P: 5.4% (r=1), 10.9% (5), 23.0% (10) | Void, or 'not shown (does not survive removal of not-genuine items)' |
| F4 | Primary clears but a row does not | Any of R1 to R6 with 30 or more items has P share 0.5 or less | Rows are descriptive guards against one source driving the result | 'Not shown (primary cleared, does not survive row Rk)' |
| F5 | Split seen before lock | 1 of 1 looks or decrypts before Y7 | Counts-only looks without arm are allowed and logged | Breach: 'not shown (split seen before lock)'; collection stops; a new data set needs a v2 |
| F6 | Harm or breach | Scanner hits in 3 or more of the first 100 received; any exposure of contact data, ledger or lockbox; any complaint | 3 of 100 is a 3% leak rate into a no-personal-data ask | Close or pause; notify; no verdict until a v2 |

Sealed counts for m counted after removals: m=90: 54; 91: 54; 92: 55; 93: 55; 94: 56; 95: 57; 96: 57; 97: 58; 98: 58; 99: 59; 100: 59. Beyond 10 removals: void, no table.

### Alternatives not chosen (his call; any other n is a v2)

| n counted | Count needed (exact, one-sided 0.05) | Power at true share 0.60 | Power at true share 0.667 |
|---|---|---|---|
| 60 | 37 | 45.1% | 83.2% |
| 80 | 48 | 54.8% | 91.5% |
| **100 (sealed)** | **59** | **62.3%** | **95.7%** |
| 120 | 70 | 68.1% | 97.8% |
| 150 | 86 | 77.4% | 99.3% |
| 200 | 113 | 86.0% | 99.9% |
| 300 | 165 | 96.6% | 100% |

80% power at share 0.60 takes n=158 (count 90); 90% takes n=213 (count 119). At share 0.667, 80% takes n=58 (count 36); 90% takes n=78 (count 47). At share 0.55, 80% takes n=620 (count 331). So n=100 sees a large effect (relative response 2) and a moderate one (1.5) about 6 times in 10.

## 6. Pass condition and every region

Let r = j + post-lock withdrawals and m = 100 minus r. Order of checks, applied once:

1. If any of F5, F6, G1, G2 or G3 failed, or the counted-ids file was not sealed before the decrypt, or the analysis script's planted-fault test did not pass before the run: no verdict ('not shown' with the reason).
2. If fewer than 100 counted: 'not tested'.
3. If r is 11 or more: void (no verdict).
4. Otherwise by X (the P count among the 100):
   - X of 59 or more: candidate pass. 'Shown once' only if (a) the P count among the m remaining items meets the sealed count for m, and (b) rows R1 to R6 with 30 or more items each have P share above 0.5 (rows under 30 are 'not evaluable' and do not block). Otherwise 'not shown (primary cleared, does not survive ...)'.
   - X of 55 to 58: 'not shown, leans P'.
   - X of 42 to 54: 'not shown'.
   - X of 41 or fewer: candidate 'contradicted'. It stands only if the N count among the m remaining items meets the sealed count for m. Otherwise 'not shown (does not survive removal of not-genuine items)'.

The 'leans P' label is a pre-registered description, not a decision: it is the smallest split called 'more than half' in plain words, and 18.4% of no-effect runs reach 55 or more. Nothing in the gathering paths changes on it.

**Status line (same format for every outcome):** 'Claim 1 (people act on purpose context): [shown once / not shown, leans P / not shown / contradicted in this test / not tested / void]. X of 100 counted submissions saw the purpose version (exact one-sided p = ...; exact lower bound ...; relative response ...). One ask, one pair of texts, these channels. Misses beside hits: the full P and N counts, every exclusion count and every sensitivity row are published.'

**What the claim line cites (Sonny Test applied to this design):** (1) a line from a record neither he nor an assistant can change after the fact: the sealed counted-ids file, the hash-chained ledger and the stamps; (2) a checker that has first caught planted faults: analyse_c1.py, whose planted-fault test (B5) is sealed before the run.

## 7. Stop rule

- **Weekly checks (counts only, no arm):** he runs the validator on all received items and records provisionally counted c and received r. No other look. Posts follow the section 3.2 schedule.
- **Close:** at the first weekly check with c of 110 or more; or at the calendar limit: day 56, or day 84 if the extension applies. The extension applies automatically if c is 67 to 99 at the day-56 check; there is no other extension. If c is 100 to 109 at day 56, close at day 56. The intake closes itself at 300 received.
- **Lock:** fixed at 7 days after close. In those 7 days withdrawals are processed; a withdrawn counted item is replaced by the next counted item in sequence; if none exists the result is 'not tested'. No reopening. Then the counted-ids file (ids only, no version) is hashed and stamped (Seal 3), the blind genuine-read is done and sealed (Seal 3b), he runs the decrypt (Y7), and analyse_c1.py runs once in his terminal, refusing to run before the LOCK file exists. Result sealed (Seal 4).
- **Budget limit:** cash is US$0. Stop if he has read 40 burst-held items or his logged hours pass 30; the shortfall is the result.
- **Harm or breach:** F6 closes or pauses intake at once. F5 stops collection.
- **Withdrawals after lock:** removed; re-run with the sealed counts for m of 90 to 100; a dated correction shows both results; the anonymous tally by wording gives row R5.
- **No optional stopping.** No look at the P and N split before lock, no weekly 'is it winning' check, no extra week, no extra post, no new channel, no second extension, no top-up after a result. A shortfall is reported, not fixed.
- **If 100 is never reached:** 'not tested'; counts only; no verdict; no split analysis.

## 8. Budget and feasibility

| Item | Plan | Assumptions |
|---|---|---|
| Cash | US$0 | Page, write-only intake and ledger on his Cloudflare stack at no new cost (he checks free-tier limits before Seal 2). No paid promotion or prizes. A paid legal read is possible, not estimated |
| CPU hours (one CPU-only mini PC) | Under 1 in total | Tests, tables, a 200,000-trial Monte Carlo, dry run and once-only analysis are seconds to minutes. Intake runs off the mini PC. No long run. To be measured in H1 |
| His hours | About 23 (25 with the extension); hard stop at 30 | Design and texts 2.0; Seal 1 1.0; lockbox ceremony 0.5; legal-read arrangement 1.0; host and intake review 1.5; pilot 2.5; Seal 2 1.0; open and posts 1.0; weekly checks 4.0 (+2.0 and +0.5 if extended); held-item reading up to 2.0; withdrawals 1.0; genuine-read 1.7; lock, decrypt, Seals 3 and 4, analysis 1.5; write-up and publish 2.0. Assistant build time is not counted |
| Outside people's hours | Planned 3 to 7; contributors about 17 | Pilot 2.3 to 3.8; legal read 1 to 3; contributors volunteer 100 x about 10 minutes = about 17 hours (up to about 50 if all 300 received were written) |

**Feasibility, stated plainly.** Nothing here estimates turnout, and nothing in the rules lets him raise it after opening. A cold audience reaching 100 counted submissions of a 10-minute creative task from one thread post, one link and 3 posts in 56 (or 84) days is not assured. 'Not tested' after about 23 hours is a likely outcome. [HIS CALL] before Seal 2: keep the channel list as is, or widen the sealed list. His probability that 100 are counted by day 56 and by day 84 goes in the Seal 2 predictions file.

## 9. Decisions assumed

**From WEAKNESS-PLANS section 4 or 9.3:** 4.5 (stamps: yes, FreeTSA first, hash-chained ledger; no block-seed rule; each yes covers one action unless he names a batch); 4.6 (one run at a time, he starts each run); 4.14 (nothing out without his yes; held wording not used); 4.15 (predictions sealed by hash in a separate file); 9.3-1 (open asks, W3 ask first, pilot first); 9.3-2 (write-only intake off the mini PC; item text only in a scratch folder outside Data and sealed folders); 9.3-3 (legal read before anything goes up; 18 or over; CC BY 4.0 items, MIT scripts, proposed); 9.3-4 (receipt and credit only); 9.3-5 (no model reads any submission; local frozen models only at a W3 exam run); 9.3-6 (no custodian; lockbox key held by him); 9.3-8 (sealed caps: 300 received, 110 provisionally counted, 40 items read). Not depended on: section 4 items 1 to 4, 7 to 13 and 16.

**Choices made in this design [HIS CALL on each]:** n = 100 and alpha 0.05 one-sided (count 59); the W3 smallest ask; what N contains (no filler); sticky version plus random device number; browser-sealed version with a lockbox key; 56-day window with automatic 28-day extension; channels (widen or not); time floor 0.5 x fastest pilot, 30 to 90 seconds; withdrawal tally; name shown in the notice; Block P's promise to publish a failure; the W3 pool rule for C1 items (author-read tag, accepted only if the W3 plan lists C1). If he chooses otherwise on any row, a v2 is sealed before the step it affects.

## 10. Order of steps

Nothing reads anything under Data or D:\LIVE. No step uses a model on submissions. No step touches the network until a step below says so. Each network or outward step needs his own yes.

### A. In-house builds on synthetic material (before the seal; no yes needed)

B1 c1_stats.py and tests; B2 assign.js and test_assign.js (vm sandbox); B3 make_pages.py, diff_pages.py, purpose_lint.py; B4 validate_c1.py with scanner, and planted-fault and blindness tests; B5 make_synthetic_c1.py, analyse_c1.py and its planted-fault self-test; B6 simulate_c1.py; B7 receipt tooling and ledger; B8 drafts (pilot protocol, honesty checklist, channel texts, notice, check_posts.py); B9 make_manifest.py; B10 lockbox keygen and decrypt scripts (throwaway synthetic key only).

### B. The seal (needs his yes)

S1 Seal 1: SHA-256 manifest, FreeTSA RFC 3161 token, OpenTimestamps proof.

### C. In-house after Seal 1 (no outsiders, no network, no gated data)

H1 freeze check; H2 real-RNG and sticky-logic tests; H3 synthetic end-to-end dry run with G3.

### D. Steps that need his yes (each named)

- Y1 Legal and ethics read of the notice (a message he sends; outside hours).
- Y2 Host choice, write-only intake and ledger off the mini PC; host facts verified; free-tier limits checked.
- Y3 Pilot with 3 to 5 invited people (his sends). Each reads both texts, labels hidden and order randomised, answering: is anything untrue or misleading; is anything unclear; does either text pressure you; which asks for more of your time. Each tries the form on a staging copy with made-up items (time sets the floor). One scripted-bot run on the staging intake: hidden-field, too-fast, duplicate and burst bots must all be rejected (4 of 4). Pilot people are tied, never counted, and see both versions. The pilot measures no response.
- Y4 Lockbox key ceremony: he makes c1_lockbox.pem offline, gives only the public half to Seal 2.
- Y5 Seal 2 (his yes): final page bytes, final notice with host facts, public key, floor, dates, channel names, intake build hash, ledger genesis, predictions file, pilot counts (no text), legal-read outcome by hash, G1, G2 and G3 results.
- Y6 He opens the final page himself for a visual check, then opens intake and posts (one yes per post).
- Y7 Weekly check by him (counts only; validator; read burst-held items with no version; withdrawals; stamp the ledger head). At lock: Seal 3, blind genuine-read, Seal 3b, decrypt.
- Y8 Run analyse_c1.py once in his terminal. Seal 4.
- Y9 Publish counts and every sensitivity row (his yes), and any wording change to the claim line.

## 11. What is sealed with this design

**Seal 1 (design):** SHA-256 of each item in one manifest (hashes are computed in the manifest, never inside the design text), then FreeTSA and OpenTimestamps.

1. C1-DESIGN-v1-r1.md (this file).
2. Block files block_T.txt, block_A.txt, block_P.txt, block_F.txt, block_C.txt (drafts) and the channel texts.
3. Code as fingerprints: c1_stats.py, assign.js, test_assign.js, make_pages.py, diff_pages.py, purpose_lint.py, validate_c1.py (with scanner), make_synthetic_c1.py, analyse_c1.py, simulate_c1.py, check_posts.py, make_manifest.py, lockbox scripts, receipt tools, all tests.
4. test_vectors.json: the k_crit table (n=40 to 300), the clustering table, the planted-fault cases.
5. Dry-run output hashes, the honesty checklist, the pilot protocol, the genuine-read rubric, the permitted-edit rule.

Predictions are not in Seal 1. They are a separate file sealed at Seal 2 with his probabilities: 100 counted by day 56; by day 84; X of 59 or more given reached; X of 55 to 58; X of 54 or fewer; X of 41 or fewer; one channel supplying 60 or more of 100; r of 1 or more; r of 11 or more; his best guess of the true relative response.

**Permitted edits between Seal 1 and Seal 2 (everything else is a new design version):** (a) fill the host fact, dates, floor, public key, channel names and page address; (b) fix wording that a pilot reader or the legal read flags as untrue, misleading or unclear in either text, if the fix adds no new fact, reason, number, name, story or appeal; Block P may only be softened or shortened and stays 130 words or fewer; (c) nothing that changes n, alpha, thresholds, counted rules, stop rule, the one-block difference or the ask.

**Seal 3 and 3b (at lock, before the decrypt):** the counted-ids file; the genuine-read file. **Seal 4:** the version-joined data hash, the result file (counts and intervals only) and the claim line. Nothing is published by sealing; only fingerprints leave the PC.

## 12. What this design cannot show

- That a person's 'desired ending' moved them. It shows only whether this one paragraph changed how many people sent a counted item.
- Purpose context in general: one ask, one P text, one N text, English, one set of channels. A 'shown' is one test, not a law.
- Purpose versus extra text. P is about 127 words longer than N; the test cannot separate purpose from 'more text' or reassurance. A length-matched third arm is a v2 needing about 1.5 times the sample.
- A conversion rate. Visitors are not counted; the share is a relative response.
- That N visitors lack purpose context. They may know the program from elsewhere. Block P also sits in the page source and in an inert template, so a reader of the source or a script-less crawler can see it.
- Who anyone is. The version is reported by the visitor's browser (sealed, but forgeable). One counted item is not proven to be one person. Age, tie and agent status are self-reported. A bot with plausible distinct items passes. Forged P votes and same-coin repeats raise the false-pass chance (3.6, 3.7). The notice itself tells visitors there are two wordings, which may prompt some to look for the other.
- Item quality. Validator pass rate by arm is exploratory.
- That nobody looked early. Stamps show a file existed. The lockbox stops accidents and assistants, not the author.
- Other kinds of ask. Sharing a private log, rating gated text and red-teaming have other costs and risks.
- That the program's main claims hold. C1 says nothing about the Sonny Test, E3 labels, record independence, fresh exams or real logs.
- Agents. The primary is people. Agent items are a separate stream.
- Why people did not send. Non-response is not observed.

## 13. Doubts considered and dismissed

- 'Add a filler paragraph of the same length to N.' Set aside for v1: filler carries its own information. Kept as a stated limit and a v2 option. I am wrong if a length-matched v2 shows the gain vanishes.
- 'Count visitors so you can give rates.' Set aside: his no-tracking rule.
- 'Use a server-signed version token.' Set aside: needs a secret and a server step, and does not stop reload-shopping. The browser-sealed version covers accidents.
- 'Make it two-sided.' Set aside: directional claim; a two-sided 0.05 needs 61 of 100; F1r covers the other tail.
- 'n of 100 is too small.' Accepted in part (62.3% power at 1.5; n=150 needs 86 and gives 77.4%). His call; any change is a v2.
- 'Peek weekly.' Set aside: optional stopping. Weekly checks are counts only, no arm.
- 'Alternate versions by day or by channel.' Set aside: a coin per device balances every hour and channel.
- 'Show each person both versions.' Set aside: carry-over, and it reveals the manipulation.
- 'Make P more persuasive.' Set aside: it would stop being honest.
- 'Pay people or run a prize.' Set aside: changes the question and brings contest rules (from memory, verify; not legal advice).
- 'Use AI agents as respondents.' Set aside: the claim is about humans.
- 'Sticky storage needs consent in the EU.' Possibly (from memory, verify). The legal read decides; fallback is no stickiness plus question 4 and rows R2 and R6.
- 'Use a CAPTCHA.' Set aside: third-party tracking; the hidden field is used.
- 'Skip the pilot.' Set aside: it catches dishonest or unclear wording and sets the time floor.
- 'Claim no effect on a fail.' Set aside: 62.3% power at 1.5 cannot show it.

## 14. Changes from the first draft (review r1)

Browser-sealed version and lockbox key (blinding, G3); random device number and one counted item per device (independence, row R6, clustering table); real-RNG test in a vm sandbox, no browser; weekly counts-only closing, automatic extension, no reopening, fixed lock date, mandatory posts; every region of X and combined removals r defined, contradicted side symmetric; burst hold and review defined; Q2 direct ask joins the tied stream; predictions moved to Seal 2; Block P adds the second checker, example name removed from Block A; W3 rules aligned (duplicates, author-read tag); scanner for secrets and personal data; turnout stated; joint power added; one yes per action; read-scope slip and unverifiable clock range removed. All numeric thresholds, bounds and power figures of the first draft recomputed and kept.

---

## Appendix: adversarial review before the seal (verdict: sealable with fixes)

15 problems were found; every fix is already in the text above. High-severity ones:

- **The version (P or N) is not actually blinded. The design says weekly checks, flagged-item reading and F5 ('no look at the split') rest on his word, and the blindness test only covers the validator. Ledger rows, exports and the review view carry the version in the clear, so he or any assistant can see the split by accident, and F5 cannot be audited.**
  Fix: The browser seals the version to a public key (WebCrypto RSA-OAEP) before sending. The private half is made offline by him in a file named c1_lockbox.pem (a name that holds none of the words the rules ban, and no AI opens it). Only the Y7 decrypt script, run by him after Seal 3b, reads it. By-arm counts are produced only after lock. New gate G3 tests that 0 of 100 synthetic exports show a readable version. F5 stays as a rule but is now backed by a mechanism.
- **Exact-binomial size assumes each counted item has its own independent coin. Pseudonyms can be changed in the form, so one person can send several counted items from one device with the same sticky version. I computed exact false-pass rates: 5 same-coin pairs in the 100 give 5.23%, 10 pairs 6.02%, 20 pairs 7.55%, 50 pairs 10.13%. The text said contamination 'only dilutes', which is true for random labels but false for repeat items.**
  Fix: Added a random per-device id (disclosed in the notice, stored with the version key, sent only on submit). One counted item per device id, per pseudonym and per email. New row R6 drops items with no device id. Section 3.7 now states the clustering inflation table and corrects the 'only dilutes' sentence.
- **G1 offline test mixes a seed with crypto.getRandomValues, which cannot be seeded, so the 'manifest-hash seed' test does not test the live coin. The page-function test (10,000 draws) needs a browser, which house rule 8 forbids for assistants. No rule said what happens on a G1 fail by chance (6e-5) or whether a rerun is allowed.**
  Fix: test_assign.js runs the real page script in a Node vm sandbox with stubbed window, localStorage and crypto (Node's own webcrypto for the real-RNG run, unseeded). A seeded stub run tests sticky logic only. Results are hashed. No rerun without a code change and a new seal. He opens the final page himself for a visual check; no assistant opens a window.
- **Stop rule is not operable and has a loophole. 'Form closes at 110 provisionally counted' needs real-time counting, but intake is write-only and the validator runs offline. The 28-day extension was 'allowed' (optional, so a fork). 'Form reopens once for up to 7 days' contradicts 'no second extension' and the calendar limit. The day-0/28/56 posts and the channels were not named. Lock had no fixed date, so withdrawal timing was open.**
  Fix: Weekly counts-only checks decide closing: close at the first check with 110 or more provisionally counted, or at the calendar limit. Extension is automatic (not optional) when 67 to 99 are provisionally counted at day 56. Reopening is deleted. If pre-lock withdrawals leave fewer than 100 and no later counted item exists, the result is 'not tested'. Lock is fixed at close plus 7 days. Posts are mandatory on the fixed days. The exact channel names are sealed at Seal 2.
