# Digest of the eight-model outside panel on "the two building blocks"

First written 2026-10-06 20:27 UTC; last edited 2026-10-06 20:31 UTC (both are system clock readings taken at the time).
Link checks ran from 19:56 UTC to about 20:13 UTC on 6 October 2026 (system clock readings taken during the work).

Read-only sources (nothing in them was changed):
- The question: [PROMPT.md](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/PROMPT.md)
- The answers, sealed before anyone read them (the run log records the stamp as "Oct 6 19:56:01 2026 GMT"): [Sol_6.1](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/answers/Sol_6.1.txt), [Gemini_3.8_Flash](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/answers/Gemini_3.8_Flash.txt), [Grok_4.7](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/answers/Grok_4.7.txt), [Kimi_K3](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/answers/Kimi_K3.txt), [GLM_5.3](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/answers/GLM_5.3.txt), [Deepseek_Flash_4.1](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/answers/Deepseek_Flash_4.1.txt), [Deepseek_R1](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/answers/Deepseek_R1.txt), [Fable_5.1](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/answers/Fable_5.1.txt)
- The run log: [RUN-LOG.txt](file:///<home>/Private/claims/2026-10-06-panel-two-blocks/answers/RUN-LOG.txt)
- Seal check [mine], at 2026-10-06 20:30 UTC: the eight answer files match ANSWERS-SHA256.txt byte for byte. RUN-LOG.txt matches too once its last two lines (the 'answers sealed' stamp line and the 'end' line, added after the hashing) are left out. I changed none of them.

Private file. Per your standing note about Gemini, its answer is quoted here for comparison only; nothing from it is a source for anything public.

## Key to names

| Short name | File and model | Words | Distinct links cited |
|---|---|---|---|
| Sol | Sol_6.1 (openai/gpt-6.1-sol:online) | 2,037 | 20 |
| Gemini | Gemini_3.8_Flash (google/gemini-3.8-flash:online) | 1,178 | 8 |
| Grok | Grok_4.7 (x-ai/grok-4.7:online) | 2,264 | 34 |
| Kimi | Kimi_K3 (moonshotai/kimi-k3:online) | 1,662 | 33 |
| GLM | GLM_5.3 (z-ai/glm-5.3:online) | 1,508 | 31 |
| DS Flash | Deepseek_Flash_4.1 (deepseek/deepseek-v4.1-flash:online) | 2,246 | 28 |
| R1 | Deepseek_R1 (deepseek/deepseek-r1-0528:online) | 600 | 7 |
| Fable | Fable_5.1 (anthropic/claude-fable-5.1:online) | 3,437 | 18 |

Every model ran once, with web search on. Counts below are "n of 8" for this run only. A repeat run could differ, so treat gaps between single models as soft.

How I worked, and the labels I use:
- I pulled out every URL (179 citations, 120 distinct URLs after dropping tracking tags) and opened each one with a fetch tool. That tool summarises a page with a small model, so for sources the conclusions lean on I asked again with different questions or read the PDF pages myself.
- I used web search only for facts the answers state without a link, and for pages that blocked the fetch tool.
- "[mine]" marks something I found that no model said.
- Check wording: "checked, exists and says it", "checked, exists but doesn't say what was claimed", "checked, not found", "not checked". The rule was strict: a link that exists but does not support the claim attached to it counts against the model that cited it.

---

## 7. One-screen summary (read this first)

Eight models answered one question once each, with web search on. Counts are n of 8.

1. **No building block is new (8 of 8); at most the discipline of using them together is (7 of 8).** All 8 say none of the building blocks is new (append-only log, commit then reveal, trusted timestamp, pre-registration, secret sharing). 7 of 8 say that whatever is distinct about using them together is a workflow or discipline, not new cryptography (Sol, Gemini, Grok, Kimi, GLM, DS Flash, Fable). R1 alone calls the combination novel, and its own "Not New" bullet says otherwise. 6 of 8 treat "digital time travel" and the Mobius picture as a metaphor or a marketing risk (Sol, Grok, Kimi, GLM, DS Flash, Fable).
2. **Close neighbours of his agent use exist: 6 of 8 found them (Grok, Kimi, GLM, DS Flash, R1, Fable); Sol and Gemini found none.** I opened all of them and every one exists. The closest are two July 2026 documents: the evidence-action draft and the Proof Packets paper. [mine] Proof Packets, which I read in full, already splits missing evidence from contradicting evidence, and the draft has the same three-verdict shape.
3. **What may still be his (models' view, unverified):** a public record of every seal so nothing is silently dropped (Kimi, Fable; Grok, Sol, GLM, DS Flash want it as a rule); every claim paired with evidence and a fixed three-word verdict (Sol, Gemini, Grok, Kimi, Fable); using it inside the agent's own "done" step (Gemini, DS Flash, Fable). GLM says the evidence that the composition adds value is thin; DS Flash notes that the belief-ledger note says no numbers exist yet.
4. **Other uses, by how many models named them:** research and trial pre-registration 7; journalism, whistleblower and source escrow 6; sealed bids 5; evidence custody and audit logs 4 (plus 2 partial); software release provenance 4; AI-evaluation integrity 4; IP and priority 4; physical supply chain 3; vulnerability disclosure 3. 6 of 8 put pre-registration of research or evaluations first. One-model ideas: key directories (Grok), cloud SLA disputes (Gemini), contract escrow (R1), threshold secret custody (DS Flash), blind scoring in hiring and grants (Fable), forecaster track records (Fable).
5. **Failure modes:** all 8 raise "sealed is not true", a log keeper who can show two histories, lost keys or salts, and timestamp misreading. 7 raise guessable unsalted hashes. 6 raise selective reveal, a permanent record versus erasure rights, and clock or anchor limits.
6. **Best paragraph: Sol's.** It calls the phrase a metaphor, lists what a record cannot do, and scopes his contribution as a workflow, not cryptography. Runner-up: Grok's. Overreach: Gemini ("We introduce", "cannot be altered, backdated"), R1 ("uniquely"), "without trusting me" (Kimi, GLM, Fable) and "before the outcome was known" (GLM, DS Flash).
7. **Experiments:** 5 of 8 test pre-commitment against selective reporting or tampering (Grok, GLM, DS Flash, R1, Fable); 2 test software release or agent "done" claims (Sol, Kimi); 1 tests vulnerability disclosure (Gemini). The common design: randomized arms where a weaker comparator (each claim timestamped alone, or prose registration) faces an append-only record with an outside checkpoint, on units with known outcomes. All 8 seal the design and failure thresholds first. Kimi tests his current use, not its own top new use.
8. **Links: 120 distinct URLs. 108 checked: 106 found, 2 not found (both Kimi's). 12 not checked (blocked, unreadable or redacted).** Of the 106 found, 103 were read: 93 say what the model claimed, 10 exist but do not (Fable 4, Grok 2, Sol 1, Gemini 1, GLM 1, DS Flash 1). Kimi has no such mismatch but has 2 dead links and one partial misquote.
9. **Careless or invented:** no invented sources found. The faults are misplaced quotes (Fable), mismatched links (Sol, Gemini, Grok, GLM, DS Flash), a wrong section number (R1), and thin or overconfident answers: R1 (600 words, self-contradicting) and Gemini (no uncertainty marked, two footnote markers with no source, a wrong description of ClinicalTrials.gov as private).

---

## 1. Other uses

Counts: 8 models gave 48 ranked uses plus 6 lower mentions (2 from Grok, 4 from DS Flash). I grouped them into 18 groups. Grouping is my judgment; partial matches are shown separately so you can regroup. Merging the closest pairs does not change the top counts: custody plus journalism is still 6 models, and pre-registration plus AI evaluation is still 7.

Each model's own first pick:

| Model | Its #1 other use |
|---|---|
| Sol | Software-release assurance and supplier security claims |
| Gemini | Coordinated vulnerability disclosure and zero-day embargoes |
| Grok | Complete reporting of pre-specified outcomes (trials) |
| Kimi | AI evaluation and deployment audit |
| GLM | Deviation-proof preregistration (trials, social science, ML evals) |
| DS Flash | Sealed, pre-registered evaluations of AI systems |
| R1 | Scientific research pre-registration |
| Fable | Pre-registered AI evaluation and benchmark claims |

Read strictly: research pre-registration first for 3 (Grok, GLM, R1), AI evaluation first for 3 (Kimi, DS Flash, Fable), software release first for 1 (Sol), vulnerability disclosure first for 1 (Gemini). Merged as "pre-registration of research or evaluations": 6 of 8.

### Ranking by number of models naming it

| Rank | Use | Named by |
|---|---|---|
| 1 | Research, clinical-trial and forecast pre-registration; complete outcome reporting | 7 of 8: Gemini, Grok, Kimi, GLM, DS Flash, R1, Fable |
| 2 | Journalism, whistleblowing, source possession and escrow | 6 of 8: Sol, Grok, Kimi, GLM, DS Flash, Fable |
| 3 | Sealed-bid procurement, auctions and sealed scoring | 5 of 8: Sol, Grok, GLM, DS Flash, Fable |
| 4 (tie) | Digital-evidence custody and tamper-evident audit logs | 4 of 8: Sol, Kimi, GLM, Fable. Partial: Grok, DS Flash |
| 4 (tie) | Software, firmware and AI-model release provenance | 4 of 8: Sol, Grok, GLM, DS Flash |
| 4 (tie) | AI evaluation and benchmark integrity | 4 of 8: Kimi, GLM, DS Flash, Fable |
| 4 (tie) | IP, priority and authorship timestamps | 4 of 8: Kimi, DS Flash, R1, Fable |
| 8 (tie) | Physical supply chain, product quality, environmental claims | 3 of 8: Sol, Gemini, R1. Weak mention: DS Flash |
| 8 (tie) | Vulnerability disclosure and bug-bounty priority | 3 of 8: Gemini, Kimi, Fable (Fable inside a bundle) |
| 10 (tie) | Elections and voting | 2 of 8: GLM, R1. Partial: Grok (election documents), DS Flash (weak mention) |
| 10 (tie) | Regulatory logging for automated decisions | 2 of 8: Kimi, Fable |
| 10 (tie) | Financial audit, proof of reserves, claim files | 2 of 8: Grok, DS Flash |
| 13 | **ONE MODEL ONLY:** forecaster and analyst track records | Fable (DS Flash folds forecasts into its research item) |
| 13 | **ONE MODEL ONLY:** key and account directories | Grok |
| 13 | **ONE MODEL ONLY:** cloud service-level disputes | Gemini |
| 13 | **ONE MODEL ONLY:** contract execution and escrow | R1 |
| 13 | **ONE MODEL ONLY:** threshold secret custody | DS Flash |
| 13 | **ONE MODEL ONLY:** blind scoring in hiring and grant review | Fable |

Lower-ranked mentions: whistleblower dossiers opened after a story breaks, and insurance photos sealed before adjustment (Grok, who calls both easier to fake with one stamp); insurance and warranty claims, tenancy and construction photo records, emissions and ESG reporting, governance balloting (DS Flash; it says balloting is weaker because a voter receipt enables coercion).

### The groups: who needs it, what it proves, what it replaces

**1. Research, trial and forecast pre-registration (7 of 8).**
- Who: journals, funders, regulators, trial sponsors, systematic reviewers, meta-analysts (Gemini, Grok, Kimi, GLM, DS Flash, R1, Fable); anyone paid for forecasts (Fable).
- Proves: the outcome list, analysis plan or prediction was fixed before the data, and a later paper is the committed set or a visible departure from it (Grok); every later change shows as a difference against a sealed original (GLM); how many forecasts were sealed versus revealed (Fable).
- Replaces: registration on ClinicalTrials.gov, OSF or AsPredicted, which rests on trust and on someone comparing registry with paper (Grok, GLM, DS Flash); prose plans that are vague or late (GLM); curated track records (Fable).
- Caveats: Kimi says he already does this himself, so the new part is running it as infrastructure for others. Fable ranks trial reporting below AI evaluation because registries already timestamp and the bottleneck is enforcement, not cryptography. Grok says silent switching stays common because the comparison is rarely done (the CASRAI and TranspariMED pages support that). Gemini calls ClinicalTrials.gov "centralized, private"; it is public and keeps a visible history of every record, though not a cryptographic one (see section 6).

**2. Journalism, whistleblowing, source possession and escrow (6 of 8).**
- Who: newsrooms, reporters, sources, NGOs, litigants, courts (Sol, Grok, Kimi, GLM, DS Flash, Fable).
- Proves: a file existed unchanged by a date without revealing it (Kimi, DS Flash, Fable); a disclosed file matches the earlier commitment (Sol); an allegation is released only when N matching reports exist (Kimi, citing Project Callisto, whose site describes a matching system and appears active).
- Replaces: notaries, lawyers' escrow, screenshots, unsupported chronology claims (Sol, DS Flash), platform clocks (Grok).
- Caveats: it does not prove the story true (Sol; the C2PA page says the same of provenance). DS Flash and Fable warn that permanence and the first-mile problem bite here. GLM says the hard part is security, not cryptography.

**3. Sealed-bid procurement, auctions and sealed scoring (5 of 8).**
- Who: public purchasers, bidders, auction houses (Sol, Grok, GLM, DS Flash); reviewers who score before seeing identities (Fable).
- Proves: each bid was committed before any was opened, the opened bid matches, and the agency did not drop or insert a bid (Grok).
- Replaces: sealed envelopes and a trusted auctioneer (Grok, GLM, DS Flash); an administrator's editable portal history (Sol).
- Caveats: the auctioneer's own record is still what you trust (DS Flash). Sol's World Bank guidance link is redacted in the saved answer, so I could not check it.

**4. Digital-evidence custody and tamper-evident audit logs (4 of 8, plus 2 partial).**
- Who: forensic labs, courts, incident responders, auditors, e-discovery teams, banks (Sol, Kimi, GLM, Fable); human-rights documenters (GLM). Grok and DS Flash cover the courts-and-records side inside other items.
- Proves: a file or log existed unaltered from seizure or decision time (Kimi, GLM); continuity of the recorded objects and documented handling, not that capture matched reality (Sol).
- Replaces: paper custody forms, mutable security logs, affidavits, custody spreadsheets, editable incident narratives (Sol, Kimi, GLM).
- Caveat: NIST already recommends hashing evidence and storing the hashes separately with custody documentation (Sol; I read section 3.2 of the report and it says so).

**5. Software, firmware and AI-model release provenance (4 of 8).**
- Who: release managers, software buyers, package ecosystems, regulators (Sol, Grok, GLM, DS Flash).
- Proves: the file everyone fetches is the file that was published, and a publisher cannot show different releases to different people (Grok); built from this source by this builder (GLM, DS Flash).
- Replaces: "trust the vendor site", signed checksums plus manual attestation, retrospective checklists.
- Caveats: all four say existing work already covers much of it (in-toto, SLSA, Sigstore, Go checksum database, SCITT). GLM: the value is "adoption and wiring, not invention". DS Flash: "incremental, not new". Sol still ranks it first because there is a clear accept or reject decision and strong comparators. Grok sees an open gap in model-weight releases.

**6. AI evaluation and benchmark integrity (4 of 8).**
- Who: labs, benchmark makers, regulators, insurers, procurement teams (Kimi, GLM, DS Flash, Fable).
- Proves: the test items, scoring rule and model identifier were fixed before the run (Kimi, DS Flash); items existed before a model's cutoff (GLM); every sealed run is accounted for, so a claimed best-ever score cannot be the survivor of twenty quiet tries (Fable).
- Replaces: self-reported benchmark tables, "we did not train on the test set", model cards (DS Flash, Fable, Kimi).
- Caveats: DS Flash chose it as its pick because both blocks do real work here, and chose it over the agent-ledger test because that test measures his current use. Fable cites a 2026 preprint arguing for pre-registration of agent experiments (checked, exists).

**7. IP, priority and authorship timestamps (4 of 8).**
- Who: inventors, artists, startups, platforms (Kimi, DS Flash, R1, Fable).
- Proves: possession of a work at a date. Replaces: notarised notebooks, "poor man's copyright", registered mail, platform timestamps.
- Caveats: Kimi says first-to-file patent law caps the value. Fable ranks it last as low differentiation and a common OpenTimestamps use already.

**8. Physical supply chain, product quality and environmental claims (3 of 8, plus a weak mention).**
- Who: manufacturers, purchasers, insurers (Sol); exporters, customs, regulators (Gemini); regulators such as the FDA and consumers (R1).
- Proves: recorded measurements met the original rules (Sol); sensor readings were paired with receipts before milestones (Gemini).
- Replaces: retrospective certificates, vendor spreadsheets, forgeable bills of lading, paper trails.
- Caveats: Sol says cryptography cannot show a sensor measured the actual goods, and GS1 EPCIS already supplies event records (I opened the GS1 guideline; it is real).

**9. Vulnerability disclosure and bug-bounty priority (3 of 8).**
- Who: security researchers and vendors (Gemini, Kimi; Fable lists "security disclosure" inside a bundle).
- Proves: a researcher held a specific report on a date without revealing it, and later whether the patch fixed that exact flaw (Gemini).
- Replaces: triage-queue timestamps, private email threads, risky full disclosure (Gemini, Kimi).

**10. Elections and voting (2 of 8, plus 2 partial).** GLM: voters and observers, proof each ballot is on the public board and the tally follows, complementing paper trails and risk-limiting audits. R1: election commissions, ballot integrity without losing anonymity. Grok covers election documents (not ballots); [mine] Guatemala's election tribunal did timestamp election documents with OpenTimestamps (found by search). DS Flash says voter receipts enable coercion.

**11. Regulatory logging for automated decisions (2 of 8).** Kimi (EU AI Act logging; banks under model-risk rules) and Fable (deployers and auditors; proof the decision record was not edited after a complaint). Fable warns this one is crowded, so the pairing and verdict words must carry the difference.

**12. Financial audit, proof of reserves, claim files (2 of 8).** Grok (depositors, auditors, insurers: obligations existed at a pinned checkpoint; "a reserves selfie that omits liabilities is not this") and DS Flash (replaces quarterly sampling and management letters).

**13 to 18. ONE MODEL ONLY.**
- Forecaster and analyst track records (Fable): shows how many forecasts were sealed versus revealed; Fable calls it the one place the ladder adds real value over a bare timestamp.
- Key and account directories (Grok): users of encrypted messaging; the key shown to you is the key shown to everyone. Grok says this is deployed already (WhatsApp, iMessage, Proton); I confirmed only WhatsApp, through Fable's cited page.
- Cloud service-level disputes (Gemini): uptime pings paired with both sides' claims; replaces competing dashboards and manual credit negotiation.
- Contract execution and escrow (R1): replaces notarisation and "centralized blockchain oracles"; R1 gives no source and no detail.
- Threshold secret custody (DS Flash): custodians, estates, break-glass access; proves no single party could reconstruct a secret and every attempt is on record. DS Flash points to verifiable secret sharing, which exists.
- Blind scoring in hiring and grant review (Fable): scores fixed before identities are known.

---

## 2. What already exists

Counts: 179 link citations (one URL counted once per model), 120 distinct URLs. 108 checked: 106 found, 2 not found. 12 not checked (4 of those confirmed to exist by another route). Of the 106 found, 103 were read, 3 are page shells that did not render. Of the 103 read, 93 say what the citing model claimed and 10 exist but do not.

Grouped below with every link. "Cited by" names the models. Where a link was cited with different claims, the note says which model's claim failed.

### A. Logs and transparency systems

| Item | Link | Cited by | Check |
|---|---|---|---|
| Haber and Stornetta 1991, "How to Time-Stamp a Digital Document" (copy on gwern.net) | https://gwern.net/doc/bitcoin/1991-haber.pdf | Sol | Checked, exists and says it. Page 1 read: back-dating or forward-dating is infeasible even if the time-stamping service colludes. |
| Same paper, Springer page | https://link.springer.com/article/10.1007/BF00196791 | Kimi, DS Flash | Not checked: redirects through a Springer cookie service, not followed. The paper is confirmed by the row above. |
| Same paper, Wayback copy of a Springer preview | https://web.archive.org/web/20180411111447im_/https:/page-one.live.cf.public.springer.com/pdf/preview/10.1007/BF00196791 | Grok | Not checked: the fetch tool cannot open web.archive.org. |
| "The First Blockchain or How to Time-Stamp a Digital Document", Ittai Abraham, 5 Jul 2020 | https://decentralizedthoughts.github.io/2020-07-05-the-first-blockchain-or-how-to-time-stamp-a-digital-document/ | Grok | Checked, exists and says it: explains the 1991 scheme as an early blockchain. |
| Certificate Transparency 2.0 (RFC 9162), rfc-editor.org | https://www.rfc-editor.org/rfc/rfc9162.html | Sol, Grok (with a chatgpt tracking tag), Kimi | Checked, exists and says it. Dec 2021, status Experimental, obsoletes RFC 6962; inclusion and consistency proofs; mechanisms so clients need not trust logs blindly (gossip) are out of scope, which supports Grok. No text making browsers enforce it. Section 1.6 holds the sentence Fable quotes (see RFC 6962 row). |
| RFC 9162, datatracker | https://datatracker.ietf.org/doc/html/rfc9162 | Gemini, GLM, DS Flash, R1 | Checked, exists and says it (title confirmed). GLM's "mandatory in browsers" is not in this RFC. |
| RFC 9162, rfc-editor.org without .html | https://www.rfc-editor.org/rfc/rfc9162 | Fable | Checked, exists and says it. |
| Certificate Transparency 1.0 (RFC 6962) | https://datatracker.ietf.org/doc/html/rfc6962 | DS Flash, Fable | Checked, exists (June 2013, Experimental). DS Flash: fine. Fable: **exists but doesn't say what was claimed.** The sentence Fable quotes as RFC 6962's ("it is necessary to treat each log as a trusted third party...") was not found in it by text search; it is in RFC 9162 section 1.6. |
| MDN, Certificate Transparency | https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Certificate_Transparency | Grok | Checked, exists and says it: public append-only logs that browsers check. |
| Russ Cox, "Transparent Logs for Skeptical Clients", 1 Mar 2019 | https://research.swtch.com/tlog | Grok, Fable | Checked, exists and says it: Merkle logs with inclusion and prefix proofs, as in Go's checksum database. |
| Trillian site | https://google.github.io/trillian/ | Grok | Checked, exists and says it. Trillian is in maintenance mode; Tessera is advised for new logs. Only Grok mentions Tessera. |
| Trillian repository | https://github.com/google/trillian | Gemini, GLM, DS Flash, Fable | Checked, exists. README says maintenance mode (none of the four say so). |
| "Tile-Based Transparency Logs" | https://transparency.dev/articles/tile-based-logs/ | Grok | Checked, exists and says it for Go checksum database, Sunlight CT, Pixel binary transparency, firmware transparency. Sigstore is not on this page (Grok cites the Safeguard blog for it). |
| transparency.dev home | https://transparency.dev | Kimi | Checked, exists. |
| Go module services (sum.golang.org) | https://sum.golang.org | Kimi, DS Flash | Checked, exists; the checksum database is among the services described. |
| Sigsum | https://www.sigsum.org | DS Flash | Checked, exists and says it: a public log of signatures so signing cannot go unnoticed. |
| Sigstore docs, Rekor logging overview | https://docs.sigstore.dev/logging/overview/ | Sol | Checked, exists. Calls Rekor a tamper-resistant ledger of supply-chain metadata; the fetch tool did not see the inclusion-proof wording Sol attaches. |
| Sigstore docs, older Rekor path | https://docs.sigstore.dev/rekor/overview/ | Gemini | Checked, exists (loads the same Rekor page). |
| Rekor repository | https://github.com/sigstore/rekor | GLM, Fable | GLM: checked, exists. Fable: **exists but doesn't say what was claimed.** Neither the README nor its raw copy has the "single-party attestation that data existed prior to a certain time" or "does not store secrets" sentences Fable quotes; a search found no source for them either. |
| Rekor specification | https://github.com/sigstore/architecture-docs/blob/main/rekor-spec.md | Sol | Checked, exists and says it: privacy section says entries can carry signer identities and monitoring reveals when artifacts are signed. |
| Sigstore home | https://www.sigstore.dev | Kimi, DS Flash | Found, page shell only ("Loading..."); content not read. |
| Safeguard.sh blog, "Sigstore Rekor Transparency Log Deep Dive 2026", 4 Feb 2026 (vendor blog) | https://safeguard.sh/resources/blog/sigstore-rekor-transparency-log-deep-dive-2026 | Grok | Checked, exists and says it: append-only Merkle log, inclusion proofs, Rekor v2 with tiles. |
| Schneier and Kelsey 1999, "Secure Audit Logs to Support Computer Forensics" | https://www.schneier.com/academic/archives/1999/05/secure_audit_logs_to.html | Sol | Checked, exists and says it: entries made before a compromise cannot be read or undetectably changed. |
| "Policy Transparency" (PolyLog), Ferraiuolo, Behjati, Santoro, Laurie, SCORED 2022 | https://storage.googleapis.com/gweb-research2023-media/pubtools/6805.pdf | Sol | Checked, exists and says it. Page 1 read: policies written as authorization logic, claims made transparent in a log. |
| Microsoft CCF | https://github.com/microsoft/ccf | GLM | Checked, exists. |
| immudb | https://immudb.io | GLM | Checked, exists. |
| IPFS | https://ipfs.tech | GLM | Checked, exists. |
| crt.sh | https://crt.sh | GLM | Checked, exists (Sectigo certificate search). Two earlier tries returned 404 and 502; the third loaded. |

### B. Key transparency

| Item | Link | Cited by | Check |
|---|---|---|---|
| CONIKS, "Bringing Key Transparency to End Users" (eprint 2014/1004) | https://eprint.iacr.org/2014/1004 | GLM | Checked, exists and says it (USENIX Security 2015). |
| CONIKS PDF | https://eprint.iacr.org/archive/2014/1004/1428180619.pdf | Grok | Not checked (403). The paper is confirmed by the abstract page above. |
| eprint 2023/1515 (PDF) | https://eprint.iacr.org/2023/1515.pdf | Grok | **Exists but doesn't say what was claimed.** It is "OPTIKS: An Optimized Key Transparency System", a scalability paper (PDF returned 403; abstract page read). Grok cites it with CONIKS for "in production at WhatsApp, iMessage, and Proton". |
| Google Key Transparency repository | https://github.com/google/keytransparency | Kimi | Checked, exists. Archived and read-only since 11 Oct 2024 (Kimi does not say). |
| Meta engineering, WhatsApp key transparency, 13 Apr 2023 | https://engineering.fb.com/2023/04/13/security/whatsapp-key-transparency/ | Fable | Checked, exists, partly says it: the append-only key directory and the public audit record are there. The "tombstoning" wording Fable quotes was not found. The page says that after account deletion the keys are removed but the fact a key existed at a point in time stays immutable, which is weaker than "history securely deleted". Counted as **doesn't say what was claimed.** |

### C. Agent receipts, SCITT and related drafts

| Item | Link | Cited by | Check |
|---|---|---|---|
| SCITT architecture, RFC 9943 | https://www.ietf.org/ietf-ftp/rfc/rfc9943.html | Grok | Checked, exists and says it. "An Architecture for Trustworthy and Transparent Digital Supply Chains", June 2026, Standards Track. A transparency service issues receipts and records a registration time. "The service's own clock unless anchored" is Grok's reading, not stated there. |
| BTW Media article on RFC 9943 (Chinese language), 1 Sep 2026 | https://btw.media/zh/shouju-xieru-zhangben-weidai-jueiding-xinren-rfc9943 | Grok | Checked, exists and says it: order in a verifiable structure is not the order in which statements were issued. Secondary source. |
| SCITT working group page | https://datatracker.ietf.org/wg/scitt/ | GLM | Checked, exists: active working group. |
| SCITT group about page | https://datatracker.ietf.org/group/scitt/about/ | DS Flash | Checked, exists: same working group. |
| SCITT about page | https://datatracker.ietf.org/wg/scitt/about/ | Fable | **Exists but doesn't say what was claimed.** The sentence Fable quotes ("authenticity of entities, evidence, policy, and artifacts ... non-repudiable, immutable, and auditable") is not on this page per the fetch. [mine] The same words appear in earlier SCITT material (a 2023 W3C list post and the working-group proposal, found by search), so the words are real but not from this page. |
| "Bitcoin-Anchored Temporal Proof for Transparency Services" (draft-fassbender-scitt-time-anchor-07) | https://www.ietf.org/archive/id/draft-fassbender-scitt-time-anchor-07.html | Grok | Checked, exists and says it. J. Fassbender (Umarise), 24 Sep 2026, individual draft, not an RFC. |
| "Evidence Layer" (draft-mih-agent-evidence-layer-00) | https://www.ietf.org/archive/id/draft-mih-agent-evidence-layer-00.html | Grok | Checked, exists and says it. Steven Mih (Action State Group), 3 Oct 2026, individual informational draft. All six points Grok attributes are there: a receipt proves inclusion only; commit time is kept apart from claimed event time; a fabricated history is possible until an outside party pins a checkpoint; a fabricated "no evidence" needs checkable non-membership; the privacy points; a signature shows key control only. |
| "Signed, Hash-Chained Action Receipts for AI Agents" (draft-sahu-agent-action-receipts-00) | https://www.ietf.org/archive/id/draft-sahu-agent-action-receipts-00.html | Grok | Checked, exists and says it. N. Sahu, 16 Aug 2026, individual draft. |
| Agent Receipts specification overview | https://agentreceipts.ai/specification/overview/ | Grok | Checked, exists and says it. v0.5.0 draft, built on W3C Verifiable Credentials, signed receipts, hash chain. "Running proxies" is not on this page. |
| "The evidence.* Family" (draft-msebenzi-evidence-action-00) | https://datatracker.ietf.org/doc/html/draft-msebenzi-evidence-action-00 | Kimi, GLM, DS Flash, R1 | Checked, exists and says it (asked four ways). Michael Msebenzi, 28 Jul 2026, individual draft. Records bind tool id, argument hash and result hash; JSON canonical form; verdicts VALID, INVALID, UNVERIFIABLE; fails closed (section 3.2); section 8 says a record makes the commitment verifiable, not the content good (GLM's quote is exact); 9.2 a key holder can produce any chain; 9.3 not equivocation-resistant, witnessing is a deployment measure; 9.5 the time field is the operator's claim and must not be used as evidence of when something happened. Two exceptions: R1 cites 9.2 for external witnessing and it is 9.3; Kimi says the draft "states the same bound" (existed no later than a time), which I did not find. |
| "Memory with Receipts: A Belief Ledger for AI Agents" | https://ai.bluecloudcyber.com/notes/belief-ledger | Kimi, GLM, DS Flash, R1 | Checked, exists and says it. Blue Cloud Cyber AI Research, 6 Sep 2026. Assertion plus evidence, session-start re-check, stale-belief diff, a proposed testbed with no results yet, an open question on how often to re-check. |
| Acta, GitHub | https://github.com/VeritasActa/acta | Kimi, GLM, DS Flash, R1 | Checked, exists and says it. Open protocol with signed receipts and hash-chained trails; typed contributions; states open, contested, superseded, resolved. |
| Veritas Acta docs | https://veritasacta.com/docs | Kimi, GLM, DS Flash, R1 | Checked, exists and says it. States are computed from the response graph, not stored; daily anchors witnessed on Bluesky. |
| "Proof Packets: A Derive-Don't-Trust Envelope for Accountable Agent Actions" | https://harperz9.github.io/papers/proof-packets.pdf | Kimi, GLM, DS Flash, R1 | Checked, exists and says it. All 5 pages read. Zain Dana Harper, July 2026 (Zenodo DOI 10.5281/zenodo.21231406). Verdicts MATCH, DRIFT, UNVERIFIABLE; missing evidence is UNVERIFIABLE, contradicting evidence is DRIFT; a packet's own claim can never raise the verdict. |
| "Preregistration for Experiments with AI Agents", arXiv 2606.11217 | https://arxiv.org/abs/2606.11217 | Fable | Checked, exists and says it. Michelle Vaccaro (MIT), ICML 2026 paper. Pages 1 to 2 read; the sentence Fable paraphrases about p-hacking, HARKing and selective outcome reporting is there. |
| "Agent Flight Recorder: Tamper-Evident Audit Trails with On-Chain Anchoring for Long-Horizon Tool-Using Agents", arXiv 2609.01931 | https://arxiv.org/abs/2609.01931 | Fable | Checked, exists and says it. Bindschaedler, Botha, Siebenbrunner, 1 Sep 2026; title matches. |
| "NovaFabric: Tamper-Evident, Replayable Evidence for Autonomous AI Agent Runs", arXiv 2609.12582 | https://arxiv.org/abs/2609.12582 | Fable | Checked, exists and says it. Seyedkazemi Ardebili, 11 Sep 2026; title matches. |
| "A Black Box for Agentic Processes: Blockchain-Anchored Evidence for AI Agent Communication, Human Oversight, and GRC Audits", arXiv 2609.04017 | https://arxiv.org/abs/2609.04017 | Fable | Checked, exists and says it. Arslan Brömme, draft dated 3 Sep 2026. Page 1 read; it calls itself a position and architecture paper with no empirical evaluation. The fetch tool first called it fictional because it treats September 2026 as the future; that was the tool's error. |
| JSON Canonicalization Scheme (RFC 8785) | https://datatracker.ietf.org/doc/html/rfc8785 | GLM | Checked, exists and says it (Informational, June 2020). |

### D. Trusted timestamping and anchoring

| Item | Link | Cited by | Check |
|---|---|---|---|
| Time-Stamp Protocol (RFC 3161), rfc-editor.org | https://www.rfc-editor.org/rfc/rfc3161.html | Sol, Kimi | Checked, exists and says it. Purpose is proof a datum existed before a particular time; a compromised TSA key means the certificate is revoked and its tokens can no longer be trusted. |
| RFC 3161, datatracker | https://datatracker.ietf.org/doc/html/rfc3161 | Gemini, GLM, DS Flash | Checked, exists and says it (title confirmed). |
| RFC 3161, rfc-editor.org without .html | https://www.rfc-editor.org/rfc/rfc3161 | Fable | Checked, exists. [mine] The definition Fable quotes beside this link ("a trusted timestamp is a timestamp issued by a Trusted Third Party...") comes from Wikipedia's "Trusted timestamping" article, not RFC 3161. |
| Evidence Record Syntax (RFC 4998) | https://www.rfc-editor.org/rfc/rfc4998.html | Sol, Kimi | Checked, exists and says it. Aug 2007, Standards Track; renewal of timestamps and hash trees. This also answers DS Flash's "unsure of its status" for the same RFC. |
| FreeTSA | https://freetsa.org | Gemini, Grok, Kimi, GLM, DS Flash | Checked, exists and says it. Free RFC 3161 time stamp authority; the page names an individual operator ("busilezas") and makes no qualified or eIDAS claim. GLM's "his own FreeTSA" is not supported; the prompt says he uses it. |
| FreeTSA with www | https://www.freetsa.org/ | Sol | Checked, exists. |
| OpenTimestamps site | https://opentimestamps.org/ | Sol, Gemini, Kimi, GLM, DS Flash, R1, Fable | Checked, exists and says it. A standard for blockchain timestamping; proof that data existed prior to some time; calendar servers; Bitcoin attestations. The page does not itself credit Peter Todd (his announcement is linked). |
| Wikipedia, OpenTimestamps | https://en.wikipedia.org/wiki/OpenTimestamps | Grok | **Exists but doesn't say what was claimed.** Says a timestamp proves data existed before a time. Does not mention elections or authorship, which Grok attaches to it. |
| YouTube video m4zDethg5e4 | https://www.youtube.com/watch?v=m4zDethg5e4 | Grok | Not checked: the fetch tool could not read the video page. [mine] The claim it supports is true: Guatemala's election tribunal timestamped election documents with OpenTimestamps (Bitcoin Magazine and Nasdaq reports, found by search). |
| OpenTimestamps client | https://github.com/opentimestamps/opentimestamps-client | Grok | Checked, exists and says it: warns that stamping many files in one command, or in quick succession, lets an adversary link them. |
| Peter Todd, OpenTimestamps announcement, 15 Sep 2016 | https://petertodd.org/2016/opentimestamps-announcement | Fable | Checked, exists and says it: trust-minimized timestamping with Bitcoin; verification needs only the proof file and Bitcoin block headers. |
| Peter Todd, "How OpenTimestamps 'Carbon Dated' (almost) The Entire Internet With One Bitcoin Transaction", 25 May 2017 (gwern copy) | https://gwern.net/doc/www/petertodd.org/8acad037d1201985b33477a574c506e74c7d9074.html | Grok | Checked, exists and says it: a timestamp is evidence of when a file existed, not that it is legitimate. |
| Bitcoin white paper | https://bitcoin.org/bitcoin.pdf | Kimi, DS Flash | Checked, exists. Page 1 read. |
| validityBase blog, "Beyond RFC-3161", Aug 2024 (vendor blog) | https://www.vbase.com/blog/beyond-rfc-3161/ | Grok | Checked, exists and says it: with RFC 3161 alone a company could stamp many predictions and reveal only the successful ones; a compromised TSA certificate invalidates earlier stamps. The vendor sells blockchain timestamps. |
| Haven blog, "Trusted Timestamping...", 26 Jun 2026 (vendor blog) | https://havenmessenger.com/blog/posts/trusted-timestamping-rfc3161-explained/ | Grok | Checked, exists and says it: if the TSA key is stolen, an attacker can forge timestamps for dates the certificate covers. |
| RightsDocket, RFC 3161 timestamps for music creators, 3 Apr 2026 | https://www.rightsdocket.com/insights/rfc-3161-timestamps-music-creators | Grok | Checked, exists and says it: a timestamp does not prove authorship. |
| RFC 3161 in Ian Duncan's RFC browser | https://www.iankduncan.com/projects/rfc-browser/3161 | Grok | Checked, exists and says it: RFC 3161 text with the purpose statement. |
| Surety | https://www.surety.com | GLM | **Exists but doesn't say what was claimed.** Enterprise product page with no mention of the New York Times. [mine] The claim is true (a weekly hash printed in the New York Times since 1995, per a Vice article found by search); Kimi states the same thing without a link. |
| Guardtime technology page | https://guardtime.com/technology | Kimi | **Checked, not found.** The domain did not resolve, with or without www. [mine] The KSI and Estonia claim itself is supported by news reports found by search. |
| Proof of Existence | https://proofofexistence.com | GLM | Found, page title only; whether it still operates is not determined (GLM said unsure). |
| eIDAS Regulation 910/2014 | https://eur-lex.europa.eu/eli/reg/2014/910/oj | Kimi, GLM | Checked, exists. The text the fetch tool saw did not show the article on qualified time stamps. [mine] Search results quoting Article 41 confirm the presumption of accurate date and time that GLM describes. |

### E. Commitments, secret sharing and time-lock

| Item | Link | Cited by | Check |
|---|---|---|---|
| Wikipedia, Commitment scheme | https://en.wikipedia.org/wiki/Commitment_scheme | Kimi, GLM, DS Flash, Fable | Checked, exists and says it: hiding and binding, Blum 1981 coin flipping, Pedersen commitments, hash-based commitments. |
| IACR Crypto 2015 paper PDF | https://www.iacr.org/archive/crypto2015/92160114/92160114.pdf | Sol | **Exists but doesn't say what was claimed.** Page 1 read: it is "Privacy with Imperfect Randomness" (Dodis and Yao), about privacy tasks under weak randomness. It is not a source for binding and hiding, hash-based commitments or Pedersen commitments, which is what Sol cites it for. |
| "Time-lock puzzles and timed-release Crypto", Rivest, Shamir, Wagner, 1996 | https://people.csail.mit.edu/rivest/pubs/RSW96.pdf | DS Flash | **Exists but doesn't say what was claimed.** Page 1 read: timed-release encryption, motivated with sealed bids. It does not say time-lock puzzles and commitments are "the same primitive", which is DS Flash's sentence. |
| Shamir, "How to Share a Secret" (MIT DSpace) | https://dspace.mit.edu/entities/publication/91c51bfc-5678-409c-80c5-44ce8fcdbadf | Sol | Checked, exists and says it. May 1979, MIT-LCS-TM-134; k pieces rebuild the data, k minus 1 reveal nothing. |
| Shamir (ACM DOI) | https://dl.acm.org/doi/10.1145/359168.359176 | Kimi | Not checked (403). [mine] A search confirms the DOI is Shamir's 1979 Communications of the ACM paper. |
| Wikipedia, Shamir's secret sharing | https://en.wikipedia.org/wiki/Shamir%27s_secret_sharing | GLM, DS Flash, Fable | Checked, exists and says it: shares below the threshold reveal nothing. |
| Wikipedia, Verifiable secret sharing | https://en.wikipedia.org/wiki/Verifiable_secret_sharing | DS Flash | Checked, exists and says it: shares can be checked as consistent without revealing the secret. |
| Wikipedia, Three-valued logic | https://en.wikipedia.org/wiki/Three-valued_logic | DS Flash | Checked, exists. |
| Wikipedia, Blind analysis | https://en.wikipedia.org/wiki/Blind_analysis | Kimi | **Checked, not found.** HTTP 404, tried twice. |
| drand | https://docs.drand.love/ | Fable | Checked, exists and says it: timelock encryption lets you encrypt toward the future so anyone can decrypt when the time comes. Fable's quote matches the page. |
| TokenToolHub guide, commit-reveal schemes | https://tokentoolhub.com/commit-reveal-schemes/ | Grok | Checked, exists and says it: the commit-reveal pattern for sealed bids, voting and randomness, with a list of implementation bugs such as weak salts. Vendor guide. |
| Shutter Network blog, 5 Jun 2025 | https://blog.shutter.network/tired-of-getting-sniped-send-your-dapps-this-commit-reveal-fix/ | Grok | Checked, exists and says it: commit-reveal against front-running. Vendor blog. |
| Prediction Arenas docs | https://docs.predictionarenas.app/how-it-works/commit-reveal | Grok | Not checked: the DNS lookup failed twice, and a search did not find the site. |

### F. Pre-registration and outcome reporting

| Item | Link | Cited by | Check |
|---|---|---|---|
| OSF Registries | https://osf.io/registries | Kimi, GLM | Found, page shell only; content not read. |
| OSF help, "Welcome to Registrations" | https://help.osf.io/article/330-welcome-to-registrations | Sol | Checked, exists and says it: a time-stamped read-only version of the plan; embargo up to four years. |
| Center for Open Science, Registered Reports | https://www.cos.io/initiatives/registered-reports | Sol, Kimi, DS Flash | Checked, exists and says it: review before data collection and in-principle acceptance. |
| Center for Open Science, preregistration | https://www.cos.io/initiatives/prereg | Gemini, DS Flash | Checked, exists and says it: preregistration of study plans on OSF. |
| Center for Open Science home | https://www.cos.io | GLM | Checked, exists. |
| AsPredicted | https://aspredicted.org | Kimi, GLM | Checked, exists and says it: time-stamped PDFs that cannot be modified once public. |
| ClinicalTrials.gov | https://clinicaltrials.gov | Kimi, GLM, DS Flash | Checked, exists (registry). [mine] It is public and keeps every earlier version of a record; see section 6 on Gemini. |
| AEA RCT Registry | https://www.socialscienceregistry.org | Kimi | Checked, exists and says it: the American Economic Association's registry for randomized trials. |
| PNAS, "The preregistration revolution" | https://www.pnas.org/doi/10.1073/pnas.1708274114 | GLM | Not checked (403). [mine] A search confirms the DOI is Nosek and others, PNAS 2018. |
| Metaculus | https://www.metaculus.com | GLM | Not checked (403). |
| COMPare | https://www.compare-trials.org/ | Fable | Checked, exists. The figures load by script and were not shown. [mine] A search gives 67 trials, 9 reported perfectly, 58 with discrepancies; that matches Fable and fits GLM's "most". |
| CASRAI guide, outcome switching and selective outcome reporting | https://casrai.org/guides/outcome-switching-and-selective-outcome-reporting | Grok | Checked, exists and says it: discrepancies are common among trials checked, and detection depends on someone doing the registry-to-publication comparison. |
| CASRAI guide, OSF preregistration | https://casrai.org/guides/osf-preregistration | Grok | Checked, exists and says it: OSF stores a snapshot that cannot be quietly altered. |
| CASRAI dictionary, pre-registration | https://casrai.org/dictionary/term/pre-registration | Grok | Checked, exists and says it: defines pre-registration. |
| TranspariMED, 12 Feb 2024 | https://www.transparimed.org/single-post/outcome-switching-research-misconduct | Grok | Checked, exists and says it: silent outcome switching remains widespread. |
| BMJ, article bmj-2025-087975 | https://www.bmj.com/content/393/bmj-2025-087975 | Grok | Not checked (403); a search could not identify the article. |
| BMJ, article bmj.j396 | https://www.bmj.com/content/356/bmj.j396 | Grok | Not checked (403); a search could not identify the article. |

### G. Standards, provenance and law

| Item | Link | Cited by | Check |
|---|---|---|---|
| in-toto, getting started | https://in-toto.io/docs/getting-started/ | Sol | Checked, exists and says it: layouts, functionaries, signed link metadata, verification. |
| in-toto home | https://in-toto.io | Kimi | Checked, exists. |
| SLSA 1.2, threats and mitigations | https://slsa.dev/spec/v1.2/threats | Sol | Checked, exists and says it: source, build and dependency threats with mitigations. |
| SLSA home | https://slsa.dev | Kimi, DS Flash | Checked, exists. |
| C2PA explainer 2.2 | https://c2pa.org/specifications/specifications/2.2/explainer/Explainer.html | Sol | Checked, exists and says it (after a redirect to spec.c2pa.org): provenance alone cannot say whether content is true. |
| C2PA home | https://c2pa.org | Kimi, DS Flash | Checked, exists. |
| W3C Verifiable Credentials 2.0 | https://www.w3.org/TR/vc-data-model-2.0/ | Kimi | Checked, exists: W3C Recommendation, 15 May 2025. |
| NIST IR 8387, Digital Evidence Preservation | https://nvlpubs.nist.gov/nistpubs/ir/2022/NIST.IR.8387.pdf | Sol | Checked, exists and says it. Cover, contents and pages 1 and 4 to 7 read; section 3.2 says to hash with an approved algorithm and store hashes separately in a secure location, with chain-of-custody documentation. |
| GS1 EPCIS and CBV Implementation Guideline | https://ref.gs1.org/guidelines/epcis-cbv/2.0.0/ | Sol | Checked, exists. Release 2.0 ratified March 2023 (title pages read). |
| ISO/IEC 27037 | https://www.iso.org/standard/44381.html | Kimi | Not checked (403). [mine] A search lists this URL as ISO/IEC 27037:2012 on digital-evidence handling. |
| EU AI Act, Regulation 2024/1689 | https://eur-lex.europa.eu/eli/reg/2024/1689/oj | Kimi | Checked, exists. The text seen mentions record-keeping duties for high-risk systems; Article 12 itself was not displayed. |
| GDPR Article 17 | https://gdpr-info.eu/art-17-gdpr/ | DS Flash | Checked, exists and says it: the right to erasure. |
| World Bank electronic-procurement document | `https://thedocs.worldbank.[REDACTED:long-token]...pdf` | Sol | Not checked: the saved answer has the link redacted. |

### H. Other

| Item | Link | Cited by | Check |
|---|---|---|---|
| Helios Voting | https://heliosvoting.org | GLM | Checked, exists (redirects to vote.heliosvoting.org): verifiable online elections. |
| ElectionGuard | https://www.electionguard.vote | GLM | Checked, exists and says it: open-source SDK for end-to-end verifiable elections; appears current (GLM was unsure). |
| Project Callisto | https://www.projectcallisto.org | Kimi | Checked, exists and says it: a matching system that links reports naming the same perpetrator; appears active (Kimi was unsure). |
| Full Fact | https://fullfact.org/ | Gemini | **Exists but doesn't say what was claimed.** The UK fact-checking charity's home page. Gemini links it as "Fact-Checking Automated Pipelines". |

### Per-model scorecard (citations, each URL counted once per model)

| Model | URLs cited | Opened, says what was claimed | Exists but doesn't say it | Not found | Not checked | Shell only |
|---|---|---|---|---|---|---|
| Sol | 20 | 18 | 1 | 0 | 1 (redacted) | 0 |
| Gemini | 8 | 7 | 1 | 0 | 0 | 0 |
| Grok | 34 | 26 | 2 | 0 | 6 | 0 |
| Kimi | 33 | 26 | 0 | 2 | 3 | 2 |
| GLM | 31 | 26 | 1 | 0 | 2 | 2 |
| DS Flash | 28 | 25 | 1 | 0 | 1 | 1 |
| R1 | 7 | 7 | 0 | 0 | 0 | 0 |
| Fable | 18 | 14 | 4 | 0 | 0 | 0 |
| Total | 179 | 149 | 10 | 2 | 13 | 5 |

Notes on the scorecard: "says what was claimed" is my judgment of the main use of each link. It still hides partial faults: R1's wrong section number and Kimi's "same bound" claim (both on the evidence-action draft); GLM's "mandatory in browsers" and "his own FreeTSA"; Fable's RFC 3161 definition that is really Wikipedia's. Gemini also has two citation markers, [1] and [2], with no source listed anywhere.

Unlinked facts I tested:
- Right: Fable's 41 percent median discrepancy between registered and published outcomes (a 2015 BMC Medicine systematic review); Fable's COMPare numbers (9 of 67 trials perfect, 58 with discrepancies); Fable's "approximately half" of preregistered studies reporting hypotheses selectively (a study of 459 preregistrations found 52 percent omitted and 57 percent added hypotheses, so "more than half" is closer); Fable's point that preregistration alone shows no meaningful drop in p-hacking (Brodeur and others, 2024, which also found complete pre-analysis plans did better); Kimi's Surety weekly New York Times hash and its KSI and Estonia claim; Grok's election-documents claim; Gemini's Blum 1981 coin flipping (the Wikipedia commitment page cites it).
- Wrong or unsupported: Gemini on ClinicalTrials.gov; GLM on "mandatory in browsers" and on "his own FreeTSA"; Fable's four misplaced quotes (Rekor, SCITT page, WhatsApp "tombstoning", RFC 6962) plus the Wikipedia sentence under RFC 3161; R1's section number; DS Flash on time-lock puzzles.

### What the models agree is distinct, and what is not

Counts: all 8 say no building block is new (they all name the append-only log, commit then reveal, trusted timestamping and pre-registration as existing). 7 of 8 say what is distinct is a workflow or discipline, not cryptography (Sol, Gemini, Grok, Kimi, GLM, DS Flash, Fable). R1 alone says the combination is novel (and in the same answer lists it as "Not New").

What each says might be distinct:
- Sol (unverified): a usable workflow that forces every claim to name exact evidence, gives shown, contradicted or not shown consistently, and keeps amendments and failed checks. A systems or human-factors contribution if an experiment shows an advantage.
- Gemini: the framing and workflow. "Done" is impossible without a receipt entry; a three-state claim and evidence schema; pre-registration and commit-reveal as runtime guardrails for software agents. Gemini names no prior art for any of it.
- Grok: the joint rule. A claim counts only as a pointer into a log the speaker cannot rewrite; claim and evidence are one committed pair; only three answers exist; a checkpoint is pinned outside the speaker before the outcome. "A discipline on top of existing parts", not a new cryptographic object. Grok is unsure whether any paper uses the exact "every rung is a pair, never closes" rule.
- Kimi: (a) a public ledger of all seals closes commit-reveal's selective-revelation hole, while commit-reveal gives the ledger privacy; (b) a minimal, dual-anchored, near-zero-cost personal discipline across research and agent work; (c) the verdict-forcing social rule. "Integration and evaluation, not invention."
- GLM: composing the pre-commitment side with the after-action evidence side in one externally anchored, fail-closed record. It calls this "modest novelty" and says evidence that it adds value is thin.
- DS Flash (all three marked unsure): (a) evidence commitment and secret share as one record type; (b) sealing the resolution rule and the evidence source, then a machine-computed three-way verdict; (c) use in a live agent loop with bulk re-check. An empirical and engineering contribution, not a new primitive.
- R1: a "unified system for incremental verification" and "efficient re-verification for dynamic AI agents". This conflicts with R1's own list, which includes the belief ledger and Acta.
- Fable: (1) the pairing rule as a schema constraint with a fixed three-way vocabulary; (2) set completeness, because numbered rungs make "how many did you seal, how many did you reveal" answerable; (3) applying it to the agent's own completion claim. Fable says the headline should be the file-drawer defence, not time travel.

Where they overlap: set completeness (Kimi, Fable, Grok; as a needed rule, Sol, GLM, DS Flash); the three-word verdict rule (Sol, Gemini, Grok, Kimi, Fable; GLM and DS Flash say it echoes existing verdict sets); in-loop use (Gemini, DS Flash, Fable).

Where they disagree on "two halves of a secret": Sol, Grok, Kimi and Fable say it is a different primitive from claim-plus-evidence pairing (confidentiality versus verifiability). DS Flash says treating them as one record type might be distinct (unsure). GLM treats the example as a split-key escrow use and does not object.

[mine] How much of the "possibly distinct" list is already written down: three-way verdicts that separate missing evidence from contradicting evidence are in Proof Packets (read in full) and have the same shape in the evidence-action draft. The Evidence Layer draft already says a self-consistent fabricated history is possible until an outside party pins a checkpoint, so the need for an outside pin is written down; and a search shows a Checkpointed Local Log draft by the same author (draft-mih-scitt-checkpointed-local-log, September 2026) on records that can be deleted or reordered unless checkpointed. I did not find an existing source for "every entry is a pair and the log never closes", or for gating the agent's own "done" on a receipt, but I did not search for them beyond the models' lists.

[mine] What this suggests, in the "claim, not anxiety" spirit: cite the near neighbours and say where each stops (for example, the evidence-action draft is explicit that witnessing is optional and that time is the operator's claim); then claim the narrow pieces with dated seals (the set-completeness rule, the missing-versus-contradicted rule on a pinned log, the in-loop gate), each stated as a discipline to be tested, not as new cryptography. If your related-work note from September 2026 does not already list the near neighbours above, they are candidates to add.

---

## 3. Failure modes

Counts: 18 failure modes after grouping. 4 are raised by all 8 models, 1 by 7, 4 by 6.

| Failure mode | Models | What they say |
|---|---|---|
| **Sealed is not true.** A false or fabricated claim seals perfectly; a timestamp can make it look more credible | 8 of 8: Sol, Gemini, Grok, Kimi, GLM, DS Flash, R1, Fable | Sol separates three checks: commitment verified, evidence authenticated, claim supported. DS Flash: a timestamped lie looks more credible. Fable: if the agent writes both claim and evidence, the receipt shows only that it said so. |
| **Whoever keeps the log can show two histories,** censor entries or rewrite storage | 8 of 8: Sol, Gemini, Grok, Kimi, GLM, DS Flash, R1, Fable | Remedies named: retained inclusion receipts, outside checkpoints and monitors (Sol, Grok, DS Flash); witness cosigning (Fable); Gemini points to gossip as in Certificate Transparency. Grok: an agent that writes its own "done" line has not met "a record the agent cannot change" unless the line was already in a log the agent does not run. Kimi, GLM and DS Flash lean on the evidence draft's own "not equivocation-resistant". |
| **Lost keys, salts, openings or receipts** | 8 of 8: Sol, Gemini, Grok, Kimi, GLM, DS Flash, R1, Fable | A lost salt or preimage makes a commitment unopenable (Sol, Grok, Fable; Fable adds: indistinguishable from hiding). Lost proof files (Grok, Fable). Stolen keys forge entries (Kimi, GLM). R1 says a lost signing key makes records unverifiable; Sol and DS Flash say past records stay verifiable. See section 6. |
| **Timestamp misread.** It shows existence by a time, not creation at that time, authorship, truth, or that the author had not seen the outcome | 8 of 8: Sol, Gemini, Grok, Kimi, GLM, DS Flash, R1, Fable | Sol is the only one to add "had not already seen the outcome". Gemini and R1 make only the simpler point that a timestamp is not correctness. |
| **Guessable hashes.** Low-entropy claims can be recovered by hashing guesses; use a random salt | 7 of 8: Sol, Gemini, Grok, Kimi, GLM, DS Flash, Fable | R1 mentions privacy leaks and suggests zero-knowledge proofs but says nothing of salts. |
| **Permanent record versus erasure rights** (GDPR) | 6 of 8: Gemini, Grok, Kimi, GLM, DS Flash, Fable | Grok: "a real conflict, not a footnote", and unsure how he would handle it. GLM is unsure how Canadian courts treat anchored hashes. Fable mentions WhatsApp-style tombstoning (its quoted wording was not found, section 2). |
| **Selective sealing and revelation:** seal many, reveal the good ones | 6 of 8: Sol, Grok, Kimi, GLM, DS Flash, Fable | Gemini touches only withheld salts. Fixes named: one authoritative commitment per scope, superseded ones kept, missed openings labelled "not shown" (Sol); the full set committed before outcomes with an outside holder of the checkpoint (Grok); a public set of seals (Kimi, Fable); all-or-nothing reveal plus independent adjudication (GLM); escrowed reveal keys, bonded stakes, mandatory-reveal registries or "void unless revealed by a deadline" (DS Flash). DS Flash says that without such a rule "the ladder actively helps the dishonest". |
| **Clock and anchor limits:** one TSA, key theft or expiry, Bitcoin block-time slack, pending proofs, ageing algorithms | 6 of 8: Sol, Grok, Kimi, GLM, DS Flash, Fable | Kimi: dual anchoring hedges, and FreeTSA is probably not eIDAS-qualified (unsure). DS Flash: a pending OpenTimestamps proof may be read as "not timestamped" (unsure). Sol, Kimi, Fable: algorithms age, so re-stamp (RFC 4998). Grok is unsure how much skew to allow for block times. |
| **Metadata leaks:** timing, volume, who sealed, checkpoint size | 5 of 8: Sol, Grok, GLM, DS Flash, Fable | GLM uses the public hostnames in Certificate Transparency as the example. |
| **Legal weight and legal exposure** (courts, regulators, subpoena) | 5 of 8: Grok, Kimi, GLM, DS Flash, Fable | Grok and Fable are unsure of Canadian case law. Kimi: FreeTSA is probably not a qualified service in the EU sense (unsure). DS Flash: a record that never closes can always be subpoenaed; a receipt does not show the committer was free. |
| **Agents or analysts gaming receipts,** or writing their own evidence (Goodhart, vacuous receipts, first-mile problem) | 4 of 8: Kimi, GLM, DS Flash, Fable. Close: Sol (valid receipt, wrong artifact or obsolete criterion), Grok (agent writes its own "done") | Kimi: receipts that verify but check nothing are "self-praise with a hash"; thousands of trivial receipts can bury contradictions. DS Flash: one agent's sealed claim becomes another's evidence, so garbage travels with a receipt. |
| **Completeness:** what never entered the record; an absence that is only asserted | 4 of 8: Sol, Grok, DS Flash, Fable | Sol: immutability preserves what was submitted, not what was omitted. Grok: "we have nothing" is not a checked absence. DS Flash: whoever controls the evidence source can manufacture "not shown". Fable: unrevealed entries should count as "not shown" by default. |
| **"Not shown" read as "false"** | 4 of 8: Sol, Grok, DS Flash, Fable | Grok adds that "contradicted" needs a committed counter-record, not a missing row. |
| **Nobody watches** | 4 of 8: Sol, Grok, DS Flash, Fable | Logs help only if someone monitors and compares checkpoints. |
| **Vague or unfalsifiable sealed claims** | 3 of 8: Kimi, GLM, Fable | Kimi: a hash of a vague prediction proves only that vague text existed. |
| **"Never closes" or "never changes" promised too strongly** | 3 of 8: Sol, Fable, GLM | Sol: say "tamper-evident under stated assumptions". Fable: say "any closing is itself logged". GLM: verification cost grows forever. |
| **Cost, staleness and link rot** | 2 of 8: DS Flash, GLM (Kimi's flooding point is close) | DS Flash: re-checking everything costs as much as re-deriving it; evidence sources die. |
| **The metaphors invite over-reading** | 6 of 8: Sol, Grok, Kimi, GLM, DS Flash, Fable | Kimi and GLM list it as a failure; the other four say it elsewhere. Fable: cryptographers will read the metaphors as marketing. |

One-model items: coercion, and what a receipt cannot show about freedom (DS Flash); time-lock encryption such as drand's tlock so a reveal does not depend on the committer being present (Fable); witness cosigning as the modern fix for split views (Fable).

---

## 4. How to say it

Counts: 8 paragraphs, from about 76 words (R1) to about 237 (DS Flash). Quotes are word for word. Only these marks changed, to follow the no-dash rule: em dashes (Kimi, GLM, DS Flash, R1, Fable) appear as a spaced hyphen; the one en dash, inside Kimi's "commit-reveal", appears as a plain hyphen; curly quotes (Sol, Grok) appear as straight quotes; and one non-breaking hyphen (Fable) appears as a normal hyphen. A script checked that each quoted line matches the answer file after those changes.

**Sol**

> I use "digital time travel" as a metaphor for checking historical commitments, not for proving past knowledge or truth. My approach combines established cryptographic commitments and timestamps with an append-only, independently checkable record: plans and claims are fixed before the relevant work, later evidence is linked to them, and each claim is assessed as shown, contradicted or not shown under explicit rules. The aim is to make retrospective changes, unsupported completion claims and missing evidence easier to detect. These records cannot make false inputs true, guarantee that every event was captured, or prove what someone understood; their reliability depends on evidence collection, record governance, cryptographic assumptions and preservation. The contribution I am testing is the usefulness of this workflow, not the invention of its underlying cryptography.

Overreach: none that I found. One gap: it names no tools, and it does not say that similar agent-receipt systems exist (Sol did not find any).

**Gemini**

> "We introduce a dual-layer cryptographic accountability protocol for autonomous processes, combining public append-only transparency logs with commit-reveal verification. By requiring an agent to bind every output claim to an immutable, timestamped evidentiary record, the system verifies temporal priority and protocol adherence across three states: shown, contradicted, or not shown. This mechanism does not verify whether an ungrounded claim is inherently true; rather, it guarantees that whatever an agent claimed, predicted, or used as evidence cannot be altered, backdated, or selectively edited after the fact."

Overreach: "We introduce" claims invention, against Gemini's own section 2 ("None of the cryptographic primitives are new"). "Verifies temporal priority and protocol adherence": a timestamp gives only an upper bound on when something existed, and says nothing about adherence. "Cannot be altered, backdated, or selectively edited after the fact" is too strong; all 7 other models raise a log keeper who can show two histories, and a timestamp does not show when content was created.

**Grok**

> Digital time travel, as used here, means a later check can show that a specific byte string was fixed before that check, and that a witnessed log was not rewritten after an outside party pinned it. A claim is entered as a pair with the evidence offered for it, in a log that only grows. The claim is sealed, then opened against what happened. The only answers are shown, contradicted, or not shown. A FreeTSA token and an OpenTimestamps proof can show that a hash existed by a time. They do not show that the text was true, who wrote it, that the set was complete, or that an event occurred at the printed minute. A log the speaker alone can checkpoint does not bind the speaker. The method replaces "trust the later story" with "check this commitment against this record." It does not replace judgment about whether the evidence was enough.

Overreach: none that I found. It claims no novelty, which is also why it says nothing about prior art. "The method replaces 'trust the later story'" is rhetoric but harmless. The tool names make it harder for a general reader.

**Kimi**

> I keep two public records. The first is an append-only, hash-chained ledger in which every entry pairs an assertion - for example, an AI agent's claim that a task is done - with the evidence that supported it; old entries cannot be altered without detection. The second is a commit-reveal step: before running a study or accepting a result, I publish a cryptographic hash of the claim or design, anchored by two independent timestamp services (an RFC 3161 authority and the Bitcoin blockchain via OpenTimestamps), and later reveal the content so anyone can check it against the seal. Together these let any third party verify, without trusting me, that a specific statement existed in a specific form no later than a specific time, and that a given evidence record has not changed since signing. They prove nothing else - not that a sealed claim was true, not that evidence was gathered honestly, and not that a "shown" verdict was correct. The primitives are decades old (linked timestamping dates to Haber and Stornetta, 1991) and similar agent-receipt systems exist; my contribution is testing whether a deliberately small, cheap composition of them measurably reduces false "done" claims by AI agents and unsupported claims in my own research.

Overreach: "without trusting me" holds only if an outside party holds an earlier checkpoint; Kimi's own failure-modes section says an operator-signed chain is tamper-evident but not equivocation-resistant. "Old entries cannot be altered without detection" has the same condition. Good: it says similar agent-receipt systems exist.

**GLM**

> "Two old cryptographic ideas, used together: an append-only ledger in which every entry pairs a claim with the evidence behind it, and a commit-then-reveal check anchored to public timestamps. Anyone holding the published record can verify, later and without trusting me, exactly two things: that the record of what was claimed - and when - has not changed since it was written, and that a given prediction was committed before its outcome was known. This is not proof of truth. A sealed statement can be false; a timestamp proves that bytes existed by a date, not who wrote them, when they were created, or whether they are correct. Verification fails closed: a record that cannot be recomputed reads as unverifiable, never as valid. What it replaces is memory and good faith about what was known when - with a diff anyone can recompute."

Overreach: "without trusting me" and "has not changed since it was written" need an outside anchor taken at seal time (GLM's own failure modes say anchoring after the fact proves only the later history). "Committed before its outcome was known" cannot be shown; a timestamp shows commitment before a date, not that the outcome was unknown to the author (Sol says this plainly). "Verification fails closed" is a property of the evidence draft, true of his system only if he built it that way.

**DS Flash**

> I build receipts for claims. When an AI agent - or a researcher, or an analyst - says something is done or true, my systems require it to point at evidence that can be re-checked later, and they answer with one of three things: shown, contradicted, or not shown. The record is append-only and hash-chained, and anything I want to commit to before I know the outcome gets sealed first and revealed later, with the seal independently timestamped. Almost none of the cryptography is mine: Merkle logs, hash commitments, RFC 3161 timestamps, Bitcoin anchoring and transparency logs have been standard for years, and claim-plus-evidence records for agents have already been proposed by others. What is genuinely unsettled is the engineering and the evidence: what such a system costs to run, how often it catches a claim that would otherwise have been believed wrongly, and how often it produces a "not shown" that a human then has to adjudicate. So I am careful about what a receipt proves. A timestamp proves a document existed by a certain time. A hash proves bytes didn't change. A sealed prediction proves what I said before I knew the answer. None of that proves the claim is true, that I am honest, or that the record's operator is independent of the claim - and I seal my methods and my falsification thresholds in advance precisely so the record, not my memory, decides what I predicted.

Overreach: "A sealed prediction proves what I said before I knew the answer" has the same problem: it proves what was said before a date, not before he knew. Good: it says plainly that almost none of the cryptography is his and that others have proposed claim-plus-evidence records for agents. It is long for one public paragraph.

**R1**

> "This work enables 'digital time travel' via two mechanisms: (1) an append-only ledger pairing claims with their supporting evidence, and (2) a commit-reveal loop that seals data for later verification. Together, they let anyone prove - at a future time - what was known or asserted earlier, with cryptographic assurance against alteration. While building on transparency logs and timestamping, our integration uniquely supports efficient re-verification for dynamic AI agents. It does not guarantee truthfulness, only immutable record-keeping and temporal anchoring."

Overreach: "enables 'digital time travel'" treats the slogan as a capability. "Prove ... what was known" claims proof of knowledge. "Uniquely supports efficient re-verification" conflicts with R1's own list of the belief ledger and Acta, which do re-verification. "Immutable" is stronger than tamper-evident. "Cryptographic assurance against alteration" ignores a log keeper who can show two histories. It is the shortest paragraph and the most overclaiming per word.

**Fable**

> Every result I publish - study designs, predictions, and the "done" claims made by AI agents I run - is first hashed and committed to an append-only log, and the log's state is timestamped by two independent mechanisms (an RFC 3161 authority and Bitcoin via OpenTimestamps) before anything is revealed. This lets a third party verify three things without trusting me: that a specific claim existed no later than a specific time, that it has not been altered since, and how many claims I sealed versus how many I later opened. It does not establish that any claim is true, that the evidence a claim points to is itself genuine, or exactly when a claim was written - only that it was fixed by the time shown. The building blocks (hash commitments, Merkle logs, trusted timestamps) are standard and decades old; what I add is a discipline for using them: every entry must pair a claim with evidence the claimant cannot change, every claim gets a verdict of shown, contradicted, or not shown, and unrevealed entries count against the record rather than disappearing from it.

Overreach: "Every result I publish" is a claim about his practice that must be true for every result. "Verify three things without trusting me", including "how many claims I sealed versus how many I later opened", holds only if the log head is witnessed outside him; Fable's own failure modes say anchoring fixes when a head existed, not that only one head was shown. "Every entry must pair a claim with evidence the claimant cannot change" is a rule to enforce, and Fable's own first-mile point says a log cannot make evidence unchangeable by itself. "Unrevealed entries count against the record" is a policy that needs enforcement. Good: it names the limits and says the building blocks are decades old.

### The best one, and why

Best: **Sol's.** Reasons: it is the only one that calls "digital time travel" a metaphor and says the records do not prove past knowledge or truth; it lists three things a record cannot do (make false inputs true, show that every event was captured, show what someone understood); it says the contribution is the usefulness of a workflow, not the invention of the cryptography; and it has no "without trusting me" or "before the outcome was known" overreach. Its weakness is that it is abstract and silent on prior art.

Runner-up: **Grok's.** It is the most exact about what a FreeTSA token or OpenTimestamps proof shows and does not show, and it carries the best single limit: a log the speaker alone can checkpoint does not bind the speaker.

Honest about prior art but each with one overreach: DS Flash, Kimi, Fable. If you want one paragraph, the cleanest merge is Sol's frame plus Grok's limit plus Kimi's or DS Flash's sentence that similar systems exist. The call is yours.

---

## 5. Experiments

Counts: 8 experiments. All 8 seal the design and the failure thresholds first. 7 give numeric failure thresholds; Grok defers to "the margin written in the sealed plan". 5 of 8 test pre-commitment against selective reporting, deviation or tampering; 2 test software release or agent "done" claims; 1 tests vulnerability disclosure. 6 of 8 target their own first-ranked use; Kimi does not, and Fable tests a mechanism rather than a use.

**The one most models converge on (5 of 8; 3 with a direct two-or-three-arm comparison):** a randomized comparison of an append-only record with an outside checkpoint against a weaker arm (each claim timestamped alone, or prose registration), on units with known outcomes, with blind raters, measuring selective reporting or deviation between what was sealed and what was reported. Grok, GLM and Fable made it; DS Flash and R1 are looser versions.

| Model | Design in two lines | Fails if | My note |
|---|---|---|---|
| Sol (software release acceptance) | Blinded, randomized, four conditions: existing signed provenance; plus a witnessed append-only history; plus timestamped commit-reveal of release criteria; both with the claim-to-evidence verdict workflow. Primary: how often reviewers accept claims the ground truth contradicts or does not support; false-but-sealed inputs as a negative control. | Under a 10 point drop in erroneous acceptance against the better single component, with a bounded rise in false rejections and time. Inconclusive if the interval is wide. Dangerous if reviewers accept more false-but-sealed claims. | Most careful, but four arms need many reviewers. Sol says sample size needs a power calculation first. |
| Gemini (vulnerability disclosure) | 50 synthetic flaws with proofs of concept. 25 sent as a hash anchored with OpenTimestamps plus a summary, with a 60-day deadline; 25 sent in full through the vendor portal. Measures disputes, leaks before 60 days, auditor time. | No significant drop in attribution disputes (p of 0.05 or higher), or more than 5 percent of commitments cannot be revealed. | 25 per arm is small for a p-value test on disputes, and it does not say who plays the vendor or how disputes arise with synthetic flaws. |
| Grok (completeness test) | Third party generates synthetic studies after the seal. Three arms: A each claim timestamped alone; B append-only log with operator-held checkpoints; C same log with an independent monitor pinning the pre-outcome checkpoint, anchored with FreeTSA and OpenTimestamps. Operator may omit, relabel or swap evidence; blind reviewers and a proof-only checker score claims and bundle completeness. | C does not cut accepted incomplete bundles against both A and B by the sealed margin; or an internally consistent but unpinned second log is accepted as often as the pinned one; or sealed false claims are marked "shown". | Best match to the "ladder plus outside witness" idea. No number for the margin. |
| Kimi (false-done trial) | About 80 software tasks with ground truth by independent re-execution; control accepts free-form "done", treatment accepts "done" only with an independently re-runnable ledger entry whose verdict is "shown". Primary: false-done rate; also overhead, vacuous receipts, time to catch. | Under a 10 point drop or an interval crossing zero; overhead above 50 percent; vacuous receipts above 10 percent. Sealed hopes: at least 50 percent relative drop, at most 25 percent overhead, at most 5 percent vacuous. | Tests his current use, not Kimi's top new use (AI evaluation). Strong on the gaming measure. |
| GLM (sealed versus prose preregistration) | 40 to 60 analysts or agent runs each make five numeric predictions resolvable at 30 days. Arm A commits plans and predictions as anchored hashes with mandatory all-or-nothing reveal; arm B files prose preregistration. Blind judges use a sealed rubric. Measures deviation, retrofit, share revealed, verification cost. | Deviation and retrofit rates indistinguishable; judges cannot adjudicate 15 percent or more; one verification costs over 30 minutes; or two inconsistent histories both pass. | Retrofit can only be detected in arm A, so that measure is not a fair comparison. |
| DS Flash (AI evaluation) | 30 to 60 evaluations of public models by at least two independent teams. Seal items, scoring script, model identifier, resolution rule, stopping rule and the analyst's predictions with FreeTSA and OpenTimestamps; run; resolve every claim shown, contradicted or not shown; an adversarial arm is paid to get claims scored "shown". | Over about 20 percent of claims need human adjudication; resolvers disagree on over about 10 percent; tamper-evidence near zero while disputes are common; cost over about 2 times; sealed claims no more accurate than unsealed. | No unsealed arm is described, yet two criteria compare with an unsealed baseline. |
| R1 (pre-registration) | Seal hypothesis, methods and analysis plan with OpenTimestamps. Measure cost to verify against manual audits, the gap between plans and published results, and auditors' success at spotting tampered evidence. | Over 10 percent of tampered records go undetected by auditors, or verification costs exceed traditional methods by over 50 percent. | No randomization or control arm. Hash checks detect tampering by machine, so measuring human auditors is an odd target. Thresholds are unexplained. |
| Fable (file-drawer test) | N forecasters or agent runs each seal K=20 claims with known outcomes. Arm A timestamps each claim separately and chooses what to reveal; arm B commits numbered entries in one append-only log whose head is timestamped, and every unrevealed entry is published as "not shown" and scored as a miss. Blind raters rate trustworthiness. Primary: accuracy of the revealed set minus accuracy of the full sealed set. | Arm B's inflation is not smaller by the sealed minimum (example: 5 points), or reveal rates are alike and ratings in B do not track full-set accuracy better. | Cleanest design, but it tests the log and the scoring rule together. |

Differences worth knowing: only Kimi tests his current use (agent "done" claims); Sol tests release acceptance, its own top new use, which sits close to it. DS Flash says outright that it avoided the agent-ledger test because that test measures his current use. Only Sol asks for a power calculation before sealing. Four include a measure of receipts being gamed or misread: Sol (reviewers mistaking a valid seal for truth), Kimi (vacuous receipts), Grok (sealed false claims marked "shown"), DS Flash (false-confidence rate).

---

## 6. Disagreements, and answers that look careless or invented

### Disagreements between the models

1. **Is the agent-receipt space occupied?** Sol and Gemini name no neighbours and treat the workflow as open. Grok, Kimi, GLM, DS Flash, R1 and Fable name close neighbours. I checked the neighbours; they exist and several share his verdict shape. Kimi counts "at least four other efforts"; GLM and DS Flash call the area crowded.
2. **Is the combination novel?** R1 yes (then no), Gemini yes in framing and workflow, GLM "modest", the other five no or only as a discipline. See section 2.
3. **Does the ladder itself close selective revelation?** Kimi and Fable say a public ledger of all seals does. Grok, Sol, GLM and DS Flash say it needs an outside holder of the checkpoint or a rule (mandatory reveal, "not shown" by default, bonded stakes). DS Flash says that without such a rule the ladder helps the dishonest.
4. **Is pre-registration a "new" use?** Kimi says he does it already; DS Flash chose AI evaluation over the agent test because the agent test is his current use; Fable ranks trial reporting below AI evaluation because registries already timestamp. Grok, GLM and R1 rank it first anyway.
5. **A lost signing key.** R1: records become unverifiable. Sol: signed public records do not need the signer's private key to be checked. DS Flash: losing the signing key stops new sealing but does not rewrite the past. GLM: it kills liveness (cannot append, cannot reveal a second half).
6. **"Two halves of a secret."** Sol, Grok, Kimi and Fable: a different primitive from claim-plus-evidence. DS Flash: maybe one record type (unsure). GLM: treated as a split-key escrow use.
7. **Time slogans.** R1's paragraph adopts "digital time travel" as a capability. Sol, Grok, Kimi, GLM, DS Flash and Fable treat it as a metaphor, and Fable says it should not be the headline. Two panel paragraphs (GLM, DS Flash) say "before the outcome was known", which Sol's answer says a timestamp cannot show.
8. **Whose FreeTSA?** GLM writes "his own FreeTSA"; Kimi and DS Flash treat it as a single outside authority; the site shows an individual operator, and the prompt says he uses it.
9. **Certificate Transparency in browsers.** GLM: "RFC 9162, mandatory in browsers". Grok: RFC 9162 "is the current spec". RFC 9162 is marked Experimental and has no browser-enforcement text. [mine, not checked here] Browser enforcement is, as far as I know, built on the older RFC 6962 style of log.
10. **What the best first use is.** Eight different first picks (see section 1). Sol and Gemini do not list pre-registration at all.

### Answers that look careless or invented

Counts: 0 invented sources found. 10 links that exist but do not support their claim, 2 dead links, 1 wrong section number, 1 answer with no uncertainty marked.

- **R1** (thinnest, 600 words). Says the combination is novel ("existing tools handle these separately") and lists it as not new. Cites the evidence draft section 9.2 for external witnessing; it is 9.3. Claims "legal contract execution" replaces "centralized blockchain oracles" with no support. Its experiment has no control arm, and measures human auditors detecting tampering that hashes detect by machine.
- **Gemini** (no uncertainty marked at all, although the question asked for it). Two footnote markers, [1] and [2], with no source. The "Fact-Checking Automated Pipelines" link goes to a fact-checking charity's home page. Calls ClinicalTrials.gov a "centralized, private" registry: [mine] it is public, and a search shows it keeps every earlier version of each record (a visible history, though not a cryptographic one). Its paragraph opens "We introduce". Its experiment uses a p-value rule with only 25 per arm, which is probably underpowered. It misses all the closest prior art.
- **Fable** (longest, 3,437 words). Candid about "own knowledge" and about reading only abstracts. But 4 of 18 links carry a quote the page does not hold (Rekor, the SCITT page, WhatsApp "tombstoning", RFC 6962), and the definition placed beside RFC 3161 is Wikipedia's. Several quotes are raw search snippets pasted in, with broken grammar ("Claims like Courts worldwide accept ..."). The words behind the misplaced quotes mostly exist elsewhere (RFC 9162, earlier SCITT texts), so I call these misplaced, not invented. Its text begins with a stray line of tool narration.
- **Sol.** Careful and hedged; one wrong citation (a paper on randomness cited for commitment definitions) and one link redacted in the saved answer. It names none of the agent-receipt neighbours, though that was the closest ground.
- **Grok.** Strong on near neighbours and on timing limits. Leans on vendor blogs, a media article in Chinese and a video; 6 links could not be checked and 2 do not support their claims (OPTIKS, the Wikipedia OpenTimestamps page). Its output starts with leftover tool narration and repeats one citation. No numeric margin in its experiment.
- **Kimi.** Strong prior-art map and an honest bottom line. Two dead links (a Wikipedia page that returns 404, and guardtime.com). One partial misquote of the evidence draft ("same bound"). Its experiment tests his current use, not its own top new use.
- **GLM.** Marks unsure items and is mostly careful. Wrong glosses: "his own FreeTSA", "mandatory in browsers". The Surety link does not carry the claim. Its experiment has a built-in imbalance. Typo "adjudiate".
- **DS Flash.** Many honest [unsure] marks and a candid "what I could not verify" list. One technical overreach: time-lock puzzles are "the same primitive" as commitments. Its experiment has no unsealed arm. Its paragraph is long.

### Open points the models flagged, and what the checks found

| Flagged by | Open point | Finding |
|---|---|---|
| Kimi | Does Project Callisto still operate? | Site loads, has a matching system and current donation notices: appears active. |
| GLM | Is ElectionGuard current? | Site loads and references recent elections: appears current. |
| DS Flash | Status of RFC 4998 | Standards Track, August 2007. |
| GLM, Fable | SCITT status | Working group active; RFC 9943 published June 2026, Standards Track. |
| GLM | Exact COMPare figure | 9 of 67 trials reported perfectly; 58 had discrepancies. |
| Kimi | Is the evidence draft past version 00? | Not determined; the page I read is version 00 (28 Jul 2026). |
| Kimi | Is FreeTSA eIDAS-qualified? | The page makes no such claim; I did not check the EU trusted list. |
| Fable | Depth of the four 2026 preprints | They exist. I read page 1 of two (one a position paper with no empirical evaluation) and pages 1 to 2 of another. Depth beyond that is unknown. |
| GLM | Does proofofexistence.com still run? | Not determined (title only). |
| Grok, GLM, Fable | Canadian court weight of a timestamp | Not resolved by anyone; I did not check. |
| DS Flash | How OpenTimestamps shows pending versus confirmed | Not checked. |

---

## 8. Doubts considered and dismissed

1. **Doubt: the fetch tool's page summaries could be wrong, so "exists and says it" could be wrong.** Set aside because, for the sources the conclusions lean on, I asked again with different questions (the evidence draft four times) or read the pages myself (Proof Packets in full; Haber and Stornetta, PolyLog, NIST, GS1, Bitcoin, IACR, RSW96, two arXiv papers), and answers were specific (titles, dates, section numbers) and consistent. *Would show I was wrong:* a person reading a full page finds a sentence I recorded as absent. The most exposed are the Rekor, SCITT-page and WhatsApp items, which rest on summaries.
2. **Doubt: a "not on the page" verdict could be a truncated fetch, not a model error.** Set aside in part. For RFC 6962 I text-searched the whole file and found the sentence in RFC 9162 section 1.6 instead; for the Rekor README I fetched the raw file and all three sentences were absent. For the SCITT and WhatsApp pages I have only summaries, so I say "not found by the fetch", not "false". *Would show I was wrong:* the words turn up on those pages. Fable's four strikes would drop to two.
3. **Doubt: blocked pages (403) hide wrong claims.** Set aside as unfair to count either way: none of the 12 "not checked" is counted against anyone, and 4 were confirmed to exist by another route (ACM DOI, ISO page, PNAS DOI, CONIKS PDF). *Would show I was wrong:* one of the other 8 (Grok's two BMJ pages are most exposed) turns out to say something different from what was claimed.
4. **Doubt: pages changed between the models' runs (19:35 to 19:56 UTC) and my checks (19:56 to 20:13 UTC).** Set aside: the gap is under an hour. Several flaky pages were retried (crt.sh needed three tries; Wikipedia "Blind_analysis", guardtime.com and Prediction Arenas failed every time). *Would show I was wrong:* a later fetch loads Wikipedia "Blind_analysis" or guardtime.com. Then Kimi's two "not found" go to zero.
5. **Doubt: my grouping of 54 uses into 18 groups could shift the top counts.** Set aside because I list every model by name and show partial matches apart, and the closest merges leave the top counts unchanged (custody plus journalism is 6 models; pre-registration plus AI evaluation is 7). *Would show I was wrong:* a reader regroups and the top three change order by more than one place.
6. **Doubt: pre-registration is too close to his current use to count as an "other use".** Set aside: the question names agents' "done" claims, sealed predictions and timestamped findings as his current use; running pre-registration for journals, trials and AI evaluations is outside that. Kimi and DS Flash raised the overlap, so I show the counts both ways. *Would show I was wrong:* you treat research pre-registration as the same as sealed predictions; then the top use becomes journalism and whistleblowing (6).
7. **Doubt: four models citing the same four sources means those are the best sources.** Set aside: it more likely means the same search returned the same top hits. They are an individual IETF draft, a blog note, a GitHub repository and an independent paper, not standards. Grok and Fable found different neighbours, so the area is wider than the shared four. *Would show I was wrong:* other papers or a working group treating those four as the standard references for agent receipts.
8. **Doubt: some near neighbours could be his own earlier public work.** Set aside: the author names I saw (Msebenzi, Harper, Sahu, Mih, Fassbender, Vaccaro and others) are not names you use publicly, and the dates (July to October 2026) are recent. I did not check handles or pen names, and I did not look at any account of yours. *Would show I was wrong:* any of those authors is an alias of yours.
9. **Doubt: an answer or a fetched page tried to steer me.** Set aside: I read all eight answers in full and saw no instruction aimed at a reader or tool; the fetched summaries showed none either. A summary could hide text in a raw page. I acted on no page text.
10. **Doubt: counting a misplaced quote as a strike is unfair when the words are real elsewhere.** Set aside under the strict rule you set. I also say where the words really come from (RFC 9162 section 1.6, earlier SCITT texts, Wikipedia). *Would show I was wrong:* you prefer to count only invented sources. Then Fable's strikes are zero and no model has an invented source.
11. **Doubt: "already has three-way verdicts" overstates Proof Packets and the evidence draft.** Set aside as "same shape", not "same": Proof Packets has MATCH (all checks pass), DRIFT (contradicting evidence or tamper) and UNVERIFIABLE (missing evidence); the draft has VALID, INVALID and UNVERIFIABLE, where UNVERIFIABLE means recomputation could not finish. They are close to, not identical with, shown, contradicted and not shown. *Would show I was wrong:* a closer reading of what the draft's INVALID covers.
12. **Doubt: the arXiv paper the fetch tool called "fictional" is not real.** Set aside: the page loaded, the PDF is on file and I read page 1 (title, author, "3 Sep 2026", position paper). The tool believed September 2026 was in the future. *Would show I was wrong:* the arXiv record is later withdrawn or shown to be fabricated.
13. **Doubt: Trillian's maintenance mode makes the models' Trillian citations wrong.** Set aside as a nuance, not an error. Several logs still run on it and none of the models claimed it was the newest. Only Grok mentions Tessera. *Would show I was wrong:* evidence that none of the cited logs still use it.
14. **Doubt: changing dashes and quote marks changed the quoted paragraphs.** Set aside: only dash marks, curly quotes and one non-breaking hyphen changed, and a script confirmed every quoted line matches the answer file after that change. *Would show I was wrong:* the script's check, which you can rerun, fails.

### Doubts I could not set aside

- One run per model: single-model facts (for example, Sol and Gemini finding no neighbours) may not repeat.
- 12 links not checked, 8 of them with no other confirmation.
- Whether the four preprints say more than their abstracts suggest.
- The legal weight of FreeTSA and OpenTimestamps proofs in Canada; nobody resolved it and I did not check.
- Whether any experiment is adequately powered: only Sol asks for a power calculation before sealing.
