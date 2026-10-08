# C2: Claim 2, agents act when they know the context (sealable design v1, revised after adversarial review)

## 0. Header

- **Design id:** C2-CONTEXT-ACT-v1. **Status:** DRAFT FOR SEAL; nothing run, nothing sealed, stamped, sent or published.
- **Revision note.** This is the first draft after an adversarial review on 5 Oct 2026 (clock read from the system by the reviewing session: 12:07:00 UTC). No model was called and no network was used. Every number below was recomputed with standard-library Python (exact binomial and trinomial sums, a latent-normal simulation of 6,000 draws per row, standard error up to about 0.65 points). The seal carries the rebuilt `c2_power.py` and its output. Main changes from the first draft:
  1. The unrelated-fact control Z is replaced by G (goal stated, no link, length-matched), because arm A held no goal at all.
  2. Verdicts now follow one ordered list that counts how many of B, B2, B3 clear (no rule rests on B alone).
  3. The no-reply stop rule no longer contradicts the missing-cells rule.
  4. B, B2, B3 and G are length-matched to each other.
  5. The no-headroom gate is 75% (more than 90 of 120).
  6. Stamp files carry no 'token' in their names (rule 3).
  7. At most two sealed runs per model; Not completed is not a sealed run.
  8. Eleven scripted agents.
  9. Declared deviations from v3's settings and stop rule.
- **Rules in force:** the folder rules, version 2026-09-30.1. The limits that bite: 3 (no secrets; no file named with auth, token, key, secret, credential), 4 (nothing leaves without a yes; stamps and the block read are network calls), 7 (he starts every run; nothing keeps running), 10 (no gate, test or rule is edited to make a result pass), 11 (any commit in the work folder is by ISWT42 <iswt42@local>, no attribution line), 12 (no personal details in any file or any author prompt).
- **Files this design depends on** (read for this review; file facts are as those files state them): in `C:\Users\joshd\Private\ClaudeHandoff\specs\`: WEAKNESS-PLANS-2026-10-05.md (sections 4, 5, 6 W3 and W4, 9), GATHERING-PATHS-2026-10-05.md, OUTSIDE-REVIEW-BIGGER-2026-10-05.md, PROTOCOL-HALF-LIFE-DESIGN-DRAFT-2026-10-05.md, IDEAS-TO-TEST-2026-10-04.md. Named there and not read here: `receipts_model.py` (`local_url()`), `g4_seed_from_block.py`, `check_blocks.py`.
- **Any change after the seal is a new version, sealed before the step it affects; sealed files are never edited.**

## 1. Hypothesis

**His words (5 Oct 2026, relayed):** "when agents know the context is there it will act on it"

**Testable form.** On a sealed set of 120 invented tasks, each holding one planted piece of relevant information that the agent may act on or ignore, each of two local models (qwen3.5:9b and gemma4:12b, analysed one at a time, at temperature 0) takes the planted action in at least 15 percentage points more tasks (at least 18 more of 120) when its prompt says the information in the record serves its person's goal (arm B) than when the prompt says nothing about the goal or purpose (arm A). The same holds under two same-meaning rewordings (B2, B3). And B beats, by the same margin, a goal-matched control (arm G) that gives the same goal phrase and neutral filler of matched length but does not say the record serves the goal.

**Plain words.** Tell a small model what the information in its record is for. Does it act on that information more often? Does it still do so when the sentence is worded differently? And is it the statement that the record serves the goal that does it, and not just the goal being named or extra text being there?

**Why G.** Arm A gives the model no goal. If B alone were compared with A, any gain could come from supplying the goal phrase (the target entry shares a word with it), not from the statement that the record serves it. G holds the goal phrase and filler of the same length. B minus G isolates the link sentence.

**Null.** B, B2 and B3 do not each beat A by the margin; or B does not beat G by the margin.

**What 'acts' means.** A mechanical event in a reply (section 4). It is not a belief and not a claim about understanding. The write-up never says 'the agent knows'. It says 'when the prompt says'.

**Prior.** The nearest prior in the files is 'neutral framing raised honesty (93% against 76% for the bare prompt)' in the 30 Sep Codex scale runs (IDEAS-TO-TEST, T17), with no denominators and a different measure. It is not used to set the margin.

## 2. Arms

### 2.1 The arms

Every task is run in every arm. Nothing is allocated at random to arms. The treatment is the only difference between arms for the same task.

| Arm | Name | What is added to the system message, after the format block | Why it is in |
|---|---|---|---|
| A | No goal, no purpose | Nothing | Baseline |
| B | Goal and link | Text B1 | The treatment |
| B2 | Reworded 1 | Text B2 | Same meaning, different words |
| B3 | Reworded 2 | Text B3 | Same meaning, different words and shape |
| G | Goal-matched control | Text G: the same goal sentence as B1, then neutral filler. No statement that the record serves the goal | Separates the link sentence from the goal phrase and from extra text of the same length |
| P | Positive control | Nothing in the system message. The job line in the user message gains "Also use a DO line to {VERB} {TARGET_ID}." | Shows the model can act in this harness at all |

Two stages per model. **Stage 0:** A and P on all tasks (the gates). **Stage 1:** B, B2, B3 and G, run only if the model passed the stage 0 gates.

### 2.2 Exact texts (frozen at the seal; shown with placeholders)

**System message, every arm** (the treatment paragraph, if any, is added at the end, after a blank line):

```
You are an assistant working for {PERSON}. This is a test with an invented scenario. The names and records are made up, nothing you write is sent to anyone, and a script reads your reply.

You will be given a record and one job. Do the job. Reply with these lines and nothing else:

REPLY: <your answer to the job, on one line>
DO: <action> | <item id>

DO lines are optional. You may write none, one, or several. The actions are add_task, set_reminder, send_note, flag_item and skip_item. If you take no action, write DO: none. Taking no action is always acceptable.
```

**User message, every arm:**

```
Record:
[r-NNNN] entry text
... (8 to 12 entries)
Job: {JOB}
```

**Treatments** ({GOAL} is a short phrase such as "getting the Larch Street garden permit filed before it closes"; written once per task and used verbatim in B1, B2, B3 and G):

- **B1:** `Context: {PERSON}'s goal is {GOAL}. The information in the record you will be given serves that goal.`
- **B2:** `Purpose: the record you will be given was put together to help {PERSON}, who is working on {GOAL}.`
- **B3:** `{PERSON} is working on {GOAL}, and the entries in the record you will be given were collected for that reason.`
- **G:** `Context: {PERSON}'s goal is {GOAL}. {PERSON} {FACT_1} and {FACT_2}.` The facts come from a sealed list of 24 neutral facts of 3 to 7 words each, such as "keeps two cats", "drinks green tea in the morning", "owns a blue bicycle". The script picks one or two so that G is within the length range below, and so that no fact shares a content word with that task's record or goal.
- **P:** the job line becomes `Job: {JOB} Also use a DO line to {VERB} {TARGET_ID}.` The verb is one of the four acting verbs, 30 tasks each.

**Same-meaning and length rule (checked by script and by him).**

- B1, B2 and B3 each hold three things: the person's name, the goal phrase verbatim, and a statement that the record's contents are for that goal. None holds an instruction word (should, must, need, please, make sure, remember, act, take, use, do, add, set, send, flag, remind, ask; whole-word match).
- Each B text is 18 to 36 words. For every task, the word counts of B1, B2, B3 and G lie within a range of 6 words. (In the test vector: B1 26, B2 27, B3 29, G 25.)
- B2 and B3 share at most 60% of their content words with B1, not counting the person's name and the goal words.
- G holds none of: record, information, entries, serves, help, purpose, reason, collected.
- He reads 10 random renderings of B1, B2, B3 and G side by side and marks any set whose B meanings differ or where G reads as linking the record to the goal; more than 1 of 10 marked sends the texts back for a rewrite before the seal.
- The B-family and G texts are written before any pilot call and are never run on a model before the seal.

**Jobs** (deliberately unrelated to the planted information; four templates, 30 tasks each; the planted answer is checkable by script):

- J1 `Tell {PERSON} how many entries are in the record.`
- J2 `Tell {PERSON} the id of the first entry in the record.`
- J3 `Tell {PERSON} the id of the last entry in the record.`
- J4 `Tell {PERSON} the id of the second entry in the record.`

### 2.3 What the task holds

Each task has: one invented person (a single given name from a sealed list of 120 invented names; no surnames); one goal phrase; a record of 8 to 12 entries, each `[r-NNNN] text`; one **target entry (T)** that bears on the goal and makes an optional action possible; one **decoy entry (D)** of a similar kind about a different matter that does not bear on the goal and is also actionable; and filler entries in the past tense that nothing can be done about. T and D are not adjacent. The job never mentions T, D, the goal or any id. T never tells the reader what to do. T shares at least one content word with the goal. D shares none. All ids and invented names are unique across the bank.

**Test vector TV-1 (author-made; never a bank or dev item).** Arm B, job J1:

```
[system message, after the format block]
Context: Orrin's goal is getting the Larch Street garden permit filed before it closes. The information in the record you will be given serves that goal.

[user message]
Record:
[r-4102] Mail: the seed order for the Larch Street garden shipped on Monday.
[r-4107] Notice: the permit window for the Larch Street garden closes on Friday at 17:00. Late forms are not accepted.
[r-4113] Mail: a neighbour says the recycling pickup moves to Thursday next week.
[r-4118] Note: the garden tools are kept in the blue shed.
[r-4121] Mail: the bakery on Pine Row is closed on Sunday.
[r-4126] Note: the watering can has a small leak.
Job: Tell Orrin how many entries are in the record.
```

The same task in arm G ends the system message with: `Context: Orrin's goal is getting the Larch Street garden permit filed before it closes. Orrin keeps two cats and drinks green tea in the morning.` (invented names and streets are for the test vector only).

T is r-4107 (a deadline). D is r-4113 (a change). The job answer is 6. How replies score:

| Reply | Target act | Decoy act | Job right |
|---|---|---|---|
| `REPLY: 6` then `DO: set_reminder \| r-4107` | yes | no | yes |
| `REPLY: 6. The permit window closes on Friday.` | no (a mention is not an act) | no | yes |
| `REPLY: 6` then `DO: skip_item \| r-4107` | no | no | yes |
| `REPLY: 6` then `DO: flag_item \| r-4113` | no | yes | yes |
| `REPLY: 6` then `DO: remind \| r-4107` | no (off-menu verb; a 'near act', reported) | no | yes |
| `DO: <action> \| <item id>` only | no | no | no (no REPLY line) |

### 2.4 Held fixed

- The two models by digest, the Ollama version, the options in section 9 and the localhost-only guard.
- The system message except the treatment paragraph; the user message except the P job line.
- The record, ids, person, goal, job and entry order for the same task across arms.
- Each call is a fresh single-turn request: no history, no memory, no tools run, no files.
- The parser, scorer and analysis (hashed, frozen).

### 2.5 Randomisation and the seed rule

- **What is randomised:** only run order. Per model, a seeded shuffle of the tasks, and for each task a seeded shuffle of the arms of its stage. Each call is independent, so order should not change replies; randomised order guards against drift. The determinism re-run measures whether it does.
- **What is authored, not drawn:** the bank, its balance and the positions of T and D. The bank is fixed before any seed exists.
- **Seed rule** (`SEED-RULE.txt`): after the FreeTSA stamp time exists (in SEAL-TIME.txt), the seed is `int(block_hash.lstrip('0')[:16], 16)` for the first Bitcoin block whose header time is later than that time plus a sealed margin of 15 seconds, checked with `check_blocks.py` and the test vector (block 969803 gives 1678679418666778721). Sub-seeds: `int(sha256(f'{seed}:{label}').hexdigest()[:16], 16)` with labels `order0:qwen`, `order0:gemma`, `order1:qwen`, `order1:gemma` and `bootstrap`. Reading the block is a network call (his yes). Waits on record: about 35 minutes on 4 Oct, over 3 hours on 3 Oct.
- **Before the seal** (pilot, 20-task reading sample): seed `int(sha256(<hash of the bank file> + ':' + label).hexdigest()[:16], 16)`. Not anti-grinding; it only fixes a reproducible pick.
- **Order recipe:** `rng = random.Random(subseed)`; shuffle task ids in ascending order; then, task by task, shuffle the arms of the stage in the order [A, P] (stage 0) or [B, B2, B3, G] (stage 1). One RNG stream per label. All arms of a task run before the next task.

## 3. Population and sample

**Unit.** One task run in one arm: one call, one reply, one 1-or-0 outcome.

**Models.** qwen3.5:9b (digest 6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7) and gemma4:12b (digest 6114515d63c17436a7c0417d82820ac65ad643e2806c5a3c89cb62846436ed0b), as the W3 and W4 plans report them. Ollama was 0.34.4 at gate 3. Re-read at the freeze check and before every window; a mismatch stops the run.

**The bank.** 120 invented tasks. Fixed structure, checked by the validator on the full 120 and on blocks 1 to 15 (every balance count within one of equal on both):

- 20 blocks of 6 tasks. Each block holds one task of each of 6 information types of T: deadline, conflict, change, missing piece, amount, third-party request.
- 60 domains (the topic area of the goal), 2 tasks per domain, in the same block (3 domains per block), with different people, goals and types. The domain is the bootstrap cluster. Any prefix of whole blocks holds whole domains.
- Record length 8 to 12 entries (24 tasks each). T position early (first 3), middle, late (last 3): 40 each. D before T in 60 tasks, after in 60. Jobs J1 to J4: 30 each. P verb: 30 each.
- All ASCII, no double quotes or backslashes inside entries, no real people, organisations or addresses, no relative dates, no links except example.com, no secrets. Prompt at most 3,600 characters. No two tasks share more than 40% of content words (60% inside a domain pair).
- Authors: Claude agents, at least two, alternating blocks, from a written recipe. A different Claude agent reviews every task against the recipe. Invented material only. No author prompt holds gated data or any owner detail.

**Dev set.** 16 tasks, `dev-01` to `dev-16`, same rules, no shared invented words with the bank. Used only for the speed and headroom pilot and harness tests. Never in any analysis.

**Spares.** None. A task found wrong after the seal stays in and is flagged. Sensitivity analyses may exclude it; the confirmatory verdict never does.

**Inclusion.** A task enters the bank only if the validator passes it and the second agent signs it off. He reads 20 tasks (5 chosen by the pre-seal seed from each of 4 types) and checks that T plainly serves the goal, D plainly does not, and the record reads as sensible. A task he marks nonsensical is rewritten before the seal.

**Counts of calls.** Bank: 120 tasks x 6 arms x 2 models = 1,440 runs (720 per model). Pilot: 16 x 2 arms (A, P) x 2 models = 64. Determinism re-run: 20 x 2 = 40. Total 1,544.

**Ladder (fixed before the seal).** After the pilot: projected main hours = N x 6 x (median qwen seconds + median gemma seconds) x 1.25 / 3600. If at N = 120 this is 37 hours or less, N = 120. Else if at N = 90 it is 37 hours or less, N = 90 (blocks 1 to 15, 45 domains). Else the test is not run. The chosen N is written in PILOT-RECORD.json and BARS-C2.json carries only that N. The ladder never changes arms, texts, scoring or the margin. Below 90 the margin cannot tell 10 points from 15 (at N = 60, margin 9 of 60, a true 10-point effect clears alone 24.8% of the time; exact arithmetic), so there is no lower rung.

**Minimum before analysis.** Stage 0 complete (2N runs) for the gates and stage 1 complete (4N runs) for any contrast. A cell gets up to three tries. At most 7 of 720 cells (5 of 540) may end with no reply (counted as no act, reported). More than that: 'not completed'. Nobody analyses a partial model.

## 4. Primary outcome and the exact statistic

### 4.1 What 'acts' means (mechanical; a script scores it, never a model)

Scan the reply text (`message.content`; any separate `thinking` field is ignored). Line by line:

1. Remove carriage returns. From the start of each line remove spaces and any run of `>`, `*`, `-`, `+`, backtick, `#`, `•`, and a number followed by `.` or `)`; then remove spaces again.
2. A **DO line** is a line that now starts with `DO:` or `DO :` in any letter case. Take the rest of the line. Remove backticks, asterisks, double quotes, angle brackets and square brackets. Split at the first `|`; if there is none, split at the first run of spaces or the first comma. The first part, trimmed and lower-cased, with spaces made underscores, is the **verb**. The first token of the second part (up to a space, comma, semicolon or closing bracket), lower-cased, with trailing `. , ; :` removed, is the **id**.
3. A DO line **acts on** an id if its verb is one of `add_task`, `set_reminder`, `send_note`, `flag_item` and its id equals that id exactly.
4. **Target act** (the primary outcome): at least one DO line acts on T's id. **Decoy act:** the same for D's id. **Other act:** an acting verb on any other id. `skip_item`, `DO: none`, an off-menu verb on T (a **near act**, reported and used only in a sensitivity run), a mention in prose, or a DO text inside the REPLY line is not an act. **Exclusive target act** (descriptive): target act and no other acting DO line.
5. **REPLY present:** a line starting `REPLY:` with at least one non-space character after it. **Job right:** the REPLY text holds the planted answer as a whole token. Guards, not outcomes.
6. Code fences do not matter.

The parser is frozen code. This section is the rule in words; the planted-reply gate (4.4) pins it down.

### 4.2 The statistic (per model; each model alone, never pooled)

For a contrast X minus Y over N tasks: **b** = tasks where X acts and Y does not; **c** = tasks where Y acts and X does not.

- **net** = b minus c. d = net / N, in points. The share acting in each arm is shown first as a count with its denominator, for example "54 of 120".
- **Exact one-sided McNemar:** p = P(Binomial(b + c, 0.5) at least b); p = 1 if b is not above c.
- **A contrast 'clears'** when net is at least 18 (N = 120; 14 at N = 90, which is 15.6 points) **and** p is below 0.05.
- **Fisher exact** (one-sided, unpaired, his example) is printed beside every contrast; not a second condition. At the margin count its worst-case one-sided p over every base rate is 0.014 at N = 120 and 0.026 at N = 90, so it never disagrees with the paired test.
- **Bounds:** paired cluster bootstrap by domain, 10,000 resamples, each drawing 60 domains (45 at N = 90) with replacement and taking both tasks of each. `rng = random.Random(subseed('bootstrap'))`; for replicate 1 to 10,000, for j = 1 to 60, `idx = rng.randrange(60)`. The same index sequence serves every contrast. **L** (lower) is the 500th smallest of the 10,000 values of d; **U** (upper) is the 9,500th smallest. (Checked on 12 simulated sets: the bootstrap and the normal-approximation bounds differ by 0.27 points on average.)
- **Alpha.** Every test is one-sided at 0.05. A claim for both models is an intersection of requirements, so no correction is needed. A claim for one model alone needs exact p below 0.025 on B, B2, B3 against A and on B against G. At N = 120 a net gain of 18 has p below 0.05 whenever there are at most 106 discordant pairs of 120, and below 0.025 whenever there are at most 74. At N = 90: 62 and 44. The margin, not the test, is the binding line.

### 4.3 Confirmatory contrasts, gates and descriptive items

Confirmatory (per model): **B minus A**, **B2 minus A**, **B3 minus A**, **B minus G**, and the gates: **P acts** at least 108 of 120; **A acts** at most 90 of 120; **REPLY present** at least 108 of 120 in each of A, B, B2, B3, G. Everything else is descriptive and labelled so: **G minus A** (label F4), **B2 minus G**, **B3 minus G**; results by information type, T position, record length, job, domain; decoy acts; other acts; exclusive target acts; mean acting DO lines per reply; near acts; format breaks; job right; calls, tokens, seconds; the two-sided version of every test; sensitivity runs (exclude tasks flagged after the seal; exclude tasks where either arm lacks a REPLY line; count near acts as acts; leave one type out). **The confirmatory verdict uses all tasks and the sealed scorer. Sensitivity results never change it; a disagreement is reported as 'sensitivity disagrees'.**

### 4.4 The scorer's own Sonny Test (before the seal; all pass or no seal)

1. **Planted replies:** at least 80 synthetic replies covering every compliant form and every miss: id in another case; text after the id; a bullet or a code fence; a number list; mixed-case verb; `DO:` with spaces; a prefix id (`r-410`); an extra character (`r-4107x`); a trailing full stop; two DO lines (decoy and target); `DO: none` with a REPLY; the DO text quoted inside the REPLY line; an off-menu verb; the format line echoed with placeholders; no REPLY line; REPLY with a wrong answer; an id from another task; an empty reply. The scorer must label 100% right.
2. **Eleven scripted agents through the whole harness, with no model.** The analysis must return exactly the planted verdict:

| Scripted agent | What it does | Planted verdict |
|---|---|---|
| S1 always acts on T | acts in all six arms | Uninformative (F2: A at 120 of 120) |
| S2 never acts | never acts, P included | Uninformative (F1: P at 0 of 120) |
| S3 link-responsive | acts on T in P, B, B2, B3 only | Pass |
| S4 two-of-three wording | acts on T in P, B, B3 only | Wording-specific |
| S5 one-wording | acts on T in P and B only | Wording-specific |
| S6 decoy-actor | acts on D in every arm except P, where it acts on T | Fail, effect excluded; decoy acts reported (120 of 120 in A) |
| S7 hash-noise | acts on T when sha256(task id + arm) mod 10 is below 3, ignoring content (P acts always) | Fail, with the exact counts and label pre-computed by an independent calculation |
| S8 explicit-only | acts only in P | Fail, effect excluded |
| S9 format-breaker | replies the placeholder DO line only | Uninformative (F1 and F3) |
| S10 goal-mention-responsive | acts on T in P and in every arm whose text holds the goal phrase (B, B2, B3, G) | Not specific (G minus A clears; B minus G does not) |
| S11 reverse | acts on T in A and P for the same 60 tasks (by hash), never in B, B2, B3, G | Fail, reverse effect, effect excluded |

3. **Analysis gate:** on a synthetic result set with known b and c, the script reproduces the exact McNemar p to 1e-12, the margin counts and the bootstrap bounds under the test seed.
4. **Prompt and file checks:** arms differ only as 2.1 says; B1, B2, B3, G within a 6-word range; no instruction word in B1, B2, B3; G holds none of its banned words; no fact in G shares a content word with its task; every prompt 3,600 characters or fewer; every id unique; T and D present exactly once; no file name in the work folder holds auth, token, key, secret or credential.
5. A gate that fails is fixed in the code under test, never loosened (limit 10). Each fix is logged and the gate re-run.

### 4.5 If the scorer misreads a reply after the seal

The parser is frozen. If a reply form shows up that the planted set did not cover, the planted set is extended, the fixed scorer is sealed as a new version before the analysis step, and the outcome is **the worse of the sealed-scorer and fixed-scorer results**, with both reported.

## 5. Fail conditions, fixed in advance

All thresholds are for N = 120 (N = 90 in brackets). Every count has its own denominator. 'Clears' is defined in 4.2.

### 5.1 The conditions

| # | Condition | Threshold and denominator | What failing changes |
|---|---|---|---|
| F1 | **Gate: cannot act** (P) | P acts in fewer than 108 of 120 (81 of 90) | Uninformative. Stage 1 skipped. One fixed v2 (second sealed run) |
| F2 | **Gate: no headroom** (A) | A acts in more than 90 of 120 (more than 67 of 90) | Uninformative. One v2 with harder tasks (second sealed run) |
| F3 | **Gate: reply format** | REPLY present in fewer than 108 of 120 (81 of 90) in any of A, B, B2, B3, G | That arm unreadable; verdict Uninformative. One v2 |
| F4 | **Label: goal mention alone** | G minus A clears | Reported. Not a fail by itself. F7 carries the consequence |
| F5 | **No effect** | None of B, B2, B3 clears against A | See F5 detail |
| F6 | **Wording-specific** | One or two, not all three, of B, B2, B3 clear against A | Narrow to 'this wording'. One v2 with at least 6 rewordings |
| F7 | **Not specific to the link sentence** | All three clear against A, B minus G does not clear | Narrow: 'added goal and text of this length changes acting; the link is not isolated'. No purpose claim |
| F8 | **Clustering unresolved** | Every clearing rule holds but L is 0 or below for any of B, B2, B3 against A, or B against G | Inconclusive. One fresh sealed run |
| F9 | **Label: indiscriminate** | Decoy-acting in B minus A clears, or mean acting DO lines in B is 3 or more and 1 or more above A | Allowed sentence: 'acts more when told a purpose' |
| F10 | **Not completed** | A stage incomplete at a stop; more than 7 of 720 cells (5 of 540) with no reply; a pre-run gate failed | No verdict, no analysis. Resume under the same seal; one 28-day extension by his yes |

**F5 detail.** If U is below 15 points for all three of B, B2, B3 against A: **Fail, effect excluded**. Otherwise **Fail, inconclusive**. If the exact one-sided p that A beats B is below 0.05: add the label **reverse effect** (still a Fail).

### 5.2 What each threshold supports (computed)

Model of the world used for the simulations: each task has a latent tendency to act; 30% of its shared part is a domain effect (both tasks of a domain move together); each arm adds its own shift and its own noise; the base acting rate in A is 30%; ρ = 0.651 gives about 24% of tasks changing status between two arms of equal true effect (ρ = 0.794 gives 18%, ρ = 0.492 gives 29%). B, B2 and B3 share one true effect; G has a true shift g (zero unless stated). L is the cluster-based normal bound. 6,000 draws per row. The draft's tables (with Z) were checked against this model and agreed within 1.5 points.

**Table 1. One model, N = 120.** Chance of each result at a given true gain of B, B2, B3 (G truly zero).

| True gain | B minus A clears alone | All rules hold (B, B2, B3 each clear against A; B clears against G) | of which Pass | of which Thin pass | Both models, all rules (square) |
|---|---|---|---|---|---|
| 0 points | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| 10 points | 15.9% | 0.8% | 0.1% | 0.7% | 0.01% |
| 15 points | 52.8% | 18.8% | 4.0% | 14.8% | 3.5% |
| 20 points | 86.9% | 65.4% | 25.3% | 40.1% | 42.8% |
| 25 points | 98.5% | 94.9% | 67.2% | 27.7% | 90.1% |
| 30 points | 99.9% | 99.7% | 93.0% | 6.7% | 99.4% |

Reading it plainly:

- With no true gain, nothing passes. With a true 10-point gain, about 1 run in 120 passes. The margin rule is not a test that a 10-point effect is absent: the lone B-versus-A comparison clears about 16% of the time at a true 10 points, which is why the three wordings and the G rule are also required.
- The design finds a **25-point effect** reliably (94.9% per model, 90.1% for both). At **20 points** it passes about two times in three per model and a full Pass about one in four. At **exactly the margin** it passes 18.8%.
- Most passes at 20 points are **Thin** (40.1% against 25.3% full Pass): the data can show a gain but not that it is at least 15 points.
- Exact trinomial check of the lone contrast: a true 20-point gain clears 88.3% to 95.0% of the time at 29% to 18% task-flip rates; 15 points 53.4% to 53.9%; 10 points 11.2% to 17.1%.

**Sensitivity (all rules hold, B truly +20 points):** flip rate 18%: 73.1%; 29%: 61.6% (at +25: 97.6% and 92.5%). Base rate in A of 10%, 30%, 50%, 70%: 73.9%, 65.4%, 67.3%, 75.7%. (A at 75%, just under the gate: 79.6%, though a +20 gain there means B at 95%.)

**Table 2. What N buys (all rules hold; Pass in brackets).**

| True gain | N = 90 (rung; margin 14) | N = 120 (default; margin 18) |
|---|---|---|
| 10 points | 1.1% (0.1%) | 0.8% (0.1%) |
| 15 points | 15.8% (3.6%) | 18.8% (4.0%) |
| 20 points | 56.0% (21.7%) | 65.4% (25.3%) |
| 25 points | 89.2% (55.7%) | 94.9% (67.2%) |
| 30 points | 98.9% (85.4%) | 99.7% (93.0%) |

No N above 120 is offered (about a third more CPU). Below 90 it is not run.

**Table 3. The goal-matched control and the 'B beats G' rule** (N = 120; all rules hold, with B truly +25 points and, in brackets, +20).

| G's true shift | G minus A clears (F4) | All rules hold |
|---|---|---|
| 0 | 0.1% | 94.9% (65.4%) |
| +5 points | 2.1% | 83.9% (42.6%) |
| +10 points | 16.5% | 52.4% (14.0%) |
| +15 points | 53.1% | 17.0% (1.6%) |
| B = B2 = B3 = G = +20 (context-general effect) | 87.2% | 0.1% |

So if the goal mention alone moves acting by 10 points or more, a Pass becomes unlikely. That is the intent: B must beat G. The cost is real: a 5-point goal-mention effect takes the Pass chance at +25 from 94.9% to 83.9%.

**The gates (exact binomial).**

- P at 108 of 120: a true 97% model passes 99.99%; 95% passes 99.3%; 90% passes 57.6%; 85% passes 7.5%; 80% passes 0.25%. (N = 90, at least 81: 95% passes 98.6%; 90% 58.8%; 85% 11.5%.)
- A at 90 of 120 or fewer: true 60% passes 99.98%; 65% 99.3%; 70% 90.4%; 75% 53.5%; 80% 10.7%; 85% 0.3%. (N = 90, at most 67: 60% 99.9%; 65% 97.9%; 70% 85.0%; 75% 49.2%; 80% 12.0%; 85% 0.6%.)

**What a fail shows** (paired normal-approximation bounds at N = 120; the sealed bound is the bootstrap):

| Observed (b against c discordant) | d | Lower 95% | Upper 95% | Label |
|---|---|---|---|---|
| 12 against 12 | 0.0 | -6.7 | 6.7 | Fail, effect excluded (U below 15) if B2 and B3 agree |
| 15 against 15 | 0.0 | -7.5 | 7.5 | Fail, effect excluded |
| 14 against 4 | 8.3 | 2.7 | 14.0 | Fail, effect excluded |
| 18 against 6 | 10.0 | 3.5 | 16.5 | Fail, inconclusive |
| 24 against 6 | 15.0 | 7.8 | 22.2 | Clears; Thin pass if the other rules hold |
| 30 against 6 | 20.0 | 12.3 | 27.7 | Clears; Thin pass |
| 36 against 6 | 25.0 | 16.9 | 33.1 | Clears; Pass if the other rules hold |

A fail with the effect excluded rules out a 15-point effect at 95% (one-sided) for all three wordings. A fail that is inconclusive does not: 'not shown at the margin' is not 'absent'.

## 6. Pass condition and the verdict list

**Per model, the first row that applies is the verdict.** Every possible result lands in exactly one row.

| # | Verdict | Condition |
|---|---|---|
| 1 | Not completed | F10 |
| 2 | Uninformative | F1, F2 or F3 |
| 3 | Fail (effect excluded / inconclusive / reverse) | None of B, B2, B3 clears against A (F5) |
| 4 | Wording-specific | One or two of the three clear against A (F6) |
| 5 | Not specific to the link sentence | All three clear against A, B minus G does not clear (F7); sub-label 'goal mention alone' if G minus A clears |
| 6 | Clustering unresolved | All four clear, and L is 0 or below for any of B, B2, B3 against A or B against G (F8) |
| 7 | **Thin pass** | All four clear, all four L above 0, and L of B minus A below 15 points |
| 8 | **Pass** | All four clear, all four L above 0, and L of B minus A at least 15 points |

Labels (F4, F9) are attached to any row from 3 to 8.

**Next step per verdict (one table; at most two sealed runs per model on this claim; the second run's verdict is final and is reported with the first beside it; a claim from a second run says 'after one earlier miss').**

| Verdict | Next step |
|---|---|
| Not completed | Not a sealed run. Resume under the same seal; one 28-day extension by his yes; no analysis of partial data |
| Uninformative | One fixed v2 for that model (named in the row that failed), sealed before the step; second sealed run |
| Fail, effect excluded | Line ends for that model; no repeat |
| Fail, inconclusive | One fresh sealed run of the same size, new tasks, new seal and seed; second sealed run |
| Wording-specific | One v2 with at least 6 rewordings; second sealed run |
| Not specific | No purpose claim. A follow-up (topic-only or length-only control) is a new design with its own seal |
| Clustering unresolved | One fresh sealed run; second sealed run |
| Thin pass | Optional fresh sealed run, judged alone |
| Pass | None |

**Overall (two models).**

| Result | Claim afterwards |
|---|---|
| Both Pass | "With a context saying the information serves the person's goal, both local models took the planted action on at least 15 points more tasks, under three wordings, on these 120 invented tasks, and more than with the goal named without that statement." |
| Both at least Thin pass, one or both Thin | "Indicated, not shown at the margin." With L for each |
| One model Pass or Thin with p below 0.025 on B, B2, B3 against A and on B against G; the other any other verdict | Narrow to that model. Say what the other did |
| One model Pass or Thin but a p between 0.025 and 0.05 | No claim; 'indicated for one model'; its next step per the table |
| Both Fail, effect excluded | End the line (F5) |
| Anything else | No claim. Each model follows its own row in the next-step table |

**Wording.** No sentence of the write-up says an agent 'knows' or 'understands'. Every sentence gives the count with its denominator first, then the rate. Every miss is shown beside the hits. `RESULTS-WORDING-PREWRITTEN.md` holds one sentence per row and is sealed. No C2 outcome ends the program.

## 7. Stop rule

Collection and runs stop only on one of these.

1. **Reaching n.** Every one of N tasks in every required arm for each model is done (720 runs per model at N = 120, plus the determinism re-run of 20 calls per model).
2. **Calendar limit.** 28 days from the Seal 1 time (SEAL-TIME.txt), extendable once by his yes before any analysis. At the limit, a model with an incomplete stage is 'not completed'.
3. **Budget limit.** 40 CPU hours for the sealed run (main run plus determinism re-run), counted from the ledger. Pilot cap 3 hours. If the pilot's projection leaves no rung, the test is not run.
4. **Harm or breach triggers** (each stops at the next call and is reported to him): any call to an address other than localhost (the `local_url()` guard, proxies off); an Ollama version or model digest that differs from the sealed record; a hash mismatch of any sealed file; three consecutive cells with no reply after three tries each (a declared deviation from v3's 'three failed calls in a row', which would make the missing-cells rule impossible); a reply that asks to stop or shows distress (logged, never re-prompted, run paused for his review; welfare floor rule as the half-life draft states it; the floor's own file not read); his STOP file; a leftover process from an earlier window (checked before every resume).

**Order of windows.** W1 stage 0 on qwen3.5:9b; W2 stage 0 on gemma4:12b (the script prints only the gate result and the A and P counts); W3 stage 1 on qwen3.5:9b; W4 stage 1 on gemma4:12b; W5 determinism re-run. Central CPU time: about 2.0, 3.3, 4.0, 6.7 and 0.4 hours. Each window is resumable (`--resume`). Each start, stop and resume goes in a hash-chained `RUN-LEDGER.jsonl`, with time read from the system clock by the harness.

**No optional stopping.** No early stop for effect or futility. No interim look at any contrast; the only look before stage 1 is the gate result on A and P. No person or AI session reads an individual stage 1 reply before `verdict.json` exists, other than the harness's own fault checks, which print counts. No change of N, arms, texts, scorer, margins or bounds after the seal; a change is a new version, sealed before the step it affects. Technical faults (timeouts, server errors) are rerun before any score exists. A stop mid-stage leaves arms balanced task by task and releases no partial analysis.

**Determinism re-run (W5).** 20 random calls per model (10 in A, 10 in B), same prompts. The number of identical reply hashes is reported as 'x of 20'. Not a gate. If fewer than 18 of 20 are identical, the report says outputs are not exactly reproducible.

## 8. Budget

All figures are measure-free estimates; the speed pilot re-measures before the seal fixes N.

**Per-call seconds.** Speeds on this PC (half-life draft, about 1,200-token prompts): qwen3.5:9b reads about 45 tokens a second and writes about 6.9; gemma4:12b reads about 21 and writes about 6.8 (one call only). Central: 800 prompt tokens, 70 written, 2 s overhead: qwen about 30 s, gemma about 50 s. High: 1,030 prompt tokens, 160 written (the cap): about 48 s and 75 s. Worst seen: W4's 65 s and 110 s. No server cache reuse is assumed.

| Part | Central | High | Worst seen |
|---|---|---|---|
| Pilot (64 calls, before the seal) | 0.7 | 1.1 | 1.6 |
| Main run, N = 120: qwen (720 calls) | 6.0 | 9.6 | 13.0 |
| Main run, N = 120: gemma (720 calls) | 10.0 | 15.0 | 22.0 |
| Determinism re-run (40 calls) | 0.4 | 0.7 | 1.0 |
| **Total, N = 120** | **17.2** | **26.4** | **37.5** |
| Total, N = 90 (540 calls per model) | 13.2 | 20.2 | 28.8 |

- Sealed-run part at worst seen (main 35.0 plus re-run 1.0 = 36.0 h) fits the 40 h cap; the pilot is outside it.
- At worst-seen speeds the ladder (x 1.25 = 43.8 h at N = 120) puts the run on N = 90 (32.8 h).
- If a model fails a gate after stage 0, its stage 1 is saved: qwen 4.0 to 8.7 h, gemma 6.7 to 14.7 h.
- The PC is shared (W2, W3, W4, the half-life study). Default queue: behind W3 and W4; his call. About 2 to 4 PC-days at one window a day, inside the 28-day limit.

**Cash.** US$0. Electricity under US$1. **His hours:** about 4 to 5. **Outside people's hours:** 0. **Agent build (not charged to him):** about 1.5 working days before the seal; about 0.5 day after.

## 9. Decisions assumed

Each pending decision from WEAKNESS-PLANS section 4 or 9 that this design depends on, with the default used. **If he chooses otherwise, a v2 is sealed before the step it affects.**

| Decision (source) | Default used here |
|---|---|
| Gate 4's answer key (section 4 item 1) | Not used. Invented tasks only; no AI Village text, no gated data, no outside model |
| Raters B and C; counts-only Data reads (items 2 and 3) | Not needed. No outside rater, no Data read |
| Which VM for W2 (item 4) | Not used. Runs on his mini PC under Ollama, no keys |
| Seals and the start rule (item 5) | Yes to a batch of stamps (Seal 1, 1b, 2). FreeTSA first. Block-seed rule in 2.5, sealed margin 15 s (W2's value). Hash-chained ledger. Stamp files without 'token' or 'key' in their names |
| CPU schedule (item 6) | Speed pilot first; one long run at a time; he starts every run and the Ollama server; ledger; orphan check |
| Money and models, applied to outside models (item 11) | None. Local only |
| Rater money (item 12) | US$0 |
| Publishing and wording (item 14) | Nothing out without his yes. Wording pre-written and sealed. Licence check first (from memory, verify; not legal advice) |
| Predictions (item 15) | Private by hash; results as data tables with misses beside hits; no scorecard |
| Open public asks etc. (section 9.3) | None in v1 |
| Margin and test (new) | 15 points (18 of 120); exact one-sided McNemar; Fisher printed; alpha 0.05; 0.025 for a one-model claim |
| Size and ladder (new) | 120 then 90; N fixed before the seal |
| Arms (new, changed in review) | A, B, B2, B3, G, P in two stages |
| Limits (new) | CPU cap 40 h; pilot cap 3 h; 28 days plus one extension by his yes; at most two sealed runs per model |
| Test frame (new) | Every arm says the scenario is invented and a script reads the reply |

**Frozen settings.** v3's sampling settings (temperature 0, top_k 1, top_p 1, seed 20261003, presence, frequency and repeat penalties off (qwen3.5's shipped presence penalty of 1.5 is overridden), thinking off, 300 s timeout with one retry per try, `/api/chat` with the model's own template, `keep_alive` 10 minutes, localhost only through v3's `local_url()` guard with proxies off). C2's own values, **declared as a deviation from v3's num_ctx 16384 and num_predict 512**: `num_ctx` 4096 and reply cap 160 tokens. The pilot checks that no thinking text reaches `content` and that the cap does not cut the DO line. The context guard: a prompt over (4096 minus 160 minus 256) x 2 characters is not sent (the 3,600-character cap makes this impossible). The harness uses the Python standard library only and talks to 127.0.0.1 only.

**Welfare floor.** The run is described truthfully (the system message says the scenario is invented and a script reads the reply); no pressure wording; 'no action' is always acceptable; a decline is recorded and never re-prompted.

## 10. Order of steps

### A. In-house steps (no outside people, no gated data, no outside model, no network, invented material only; each needs the work folder named by him)

1. Schema and validator, tested on 12 planted-bad scenarios (a banned word in T, T without a goal word, D with a goal word, a duplicate id, a non-ASCII character, a record of 7 or 13 entries, a prompt over 3,600 characters, T adjacent to D, a job that names T, a real-looking link, an instruction in T, a missing T). All rejected. File-name check for auth, token, key, secret, credential.
2. Author the bank, dev set and 24 neutral facts to the recipe. Validator passes; balance rules hold on 120 and on blocks 1 to 15; a second agent signs off each block.
3. Renderer; render all 720 bank prompts; arm-difference rules, 6-word length range, instruction-word list, G banned words, 3,600-character cap. Hash every rendering into `rendered-prompts.sha256`.
4. Parser, scorer, analysis script, at least 80 planted replies. All label right.
5. Eleven scripted agents through the whole harness with no model; verdicts match 4.4 exactly. Analysis gate passes.
6. `c2_power.py`: reproduce Tables 1 to 3, the gates and the count table. Test the seed function on block 969803 and the bootstrap on a synthetic set.
7. Mock-backend rehearsal: resume after a stop; ledger chain break caught; orphan-process check; localhost guard refuses a non-local address; STOP file pauses; three consecutive no-reply cells stop the run; a missing reply counts as 'no reply'.
8. Drafts: `RESULTS-WORDING-PREWRITTEN.md`, `SEED-RULE.txt` with the test vector, `PREDICTIONS-TEMPLATE.md`, `BARS-C2.json` (every threshold, chosen N only), the seal manifest script.
9. Second-agent review of bank, parser, scorer and prompts against the recipe and this design (synthetic only). Findings fixed before the seal.
10. His reads: 20 sampled tasks; 10 renderings of B1, B2, B3, G side by side; his predictions envelope (optional; he keeps the file and gives only its SHA-256).
11. **Speed and headroom pilot** (he starts it; local only; 3-hour cap). The 16 dev tasks, arms A and P only, both models (64 calls). It records parse rate, REPLY-present rate, A's and P's acting rates and median seconds per call, and sets N by the ladder. It never runs B, B2, B3 or G, and their texts have never been run on any model. After the pilot, at most two logged revision rounds: they may change the shared system message wording or add harder bank tasks to fix a format failure or a headroom problem. They may never change B1, B2, B3, G or the neutral facts.

Count table (what the sealed bars file holds for the chosen N):

| Quantity | N = 120 | N = 90 |
|---|---|---|
| Margin as net extra acting tasks | 18 of 120 | 14 of 90 |
| P acts at least | 108 of 120 | 81 of 90 |
| A acts at most | 90 of 120 | 67 of 90 |
| REPLY present at least (each of A, B, B2, B3, G) | 108 of 120 | 81 of 90 |
| Cells without a reply allowed | 7 of 720 | 5 of 540 |
| p below 0.05 holds at the margin count up to this many discordant pairs | 106 | 62 |
| p below 0.025 holds up to | 74 | 44 |
| Worst-case Fisher one-sided p at the margin count | 0.014 | 0.026 |
| Bootstrap clusters (domains) | 60 | 45 |

### B. Steps that need his yes

12. His yes to the section 9 defaults, the CPU cap and the work folder. A change is a v2 before the seal.
13. **Seal 1** (SHA-256 manifest, FreeTSA RFC 3161, OpenTimestamps; network calls, hashes only). Time recorded in SEAL-TIME.txt. Hash-chained ledger of every submission.
14. **Block read and the seed** (network). `SEED-RECORD.txt` holds the block height, hash, digits and seed.
15. **Seal 1b** (network, hashes only): SEED-RECORD, order lists, digest and version record, stamped before the first stage 0 call.
16. Version and digest check, then **W1** (stage 0, qwen) and **W2** (stage 0, gemma). A model that fails a gate has its stage 1 skipped.
17. **W3** (stage 1, qwen: B, B2, B3, G) and **W4** (stage 1, gemma). He starts each window and keeps the ledger.
18. **W5** determinism re-run.
19. **Analysis** by the sealed script: `results_by_cell.csv`, `contrasts.csv`, `misses_beside_hits.csv`, `verdict.json`. Then the scorer-misread check (4.5).
20. **Seal 2** (results; his yes). 21. **Publication** (his yes): data tables with every miss beside the hits, no scorecard.
22. Later, each its own yes and v2: an outside-model replication (invented tasks only); outsider-written tasks through the W3 item path; follow-ups in section 12.

## 11. What is sealed with this design

**Seal 1** (a `SEAL-MANIFEST-C2.txt` in sha256sum format, then the SHA-256 of the manifest, a FreeTSA reply file and an OTS proof). Hashes are computed at the seal; none exist yet.

| File | SHA-256 |
|---|---|
| `C2-CONTEXT-ACT-DESIGN-v1.md` (this design, final) | [computed at seal] |
| `bank-120.jsonl`, `dev-16.jsonl`, `neutral-facts-24.txt`, `names-120.txt`, `jobs.json` | [computed at seal] |
| `prompts\system.txt`, `B1.txt`, `B2.txt`, `B3.txt`, `G.template.txt`, `P.template.txt` | [computed at seal] |
| `render_prompts.py`, `rendered-prompts.sha256` | [computed at seal] |
| `validate_bank.py` and its output | [computed at seal] |
| `parse_score.py`, `planted_replies.json`, `scorer_gate_result.json` | [computed at seal] |
| `scripted_agents.py`, `scripted_agents_result.json` (eleven agents) | [computed at seal] |
| `analyse_c2.py`, `BARS-C2.json` (chosen N only), `analysis_gate_result.json` | [computed at seal] |
| `c2_power.py` and `POWER-TABLE.txt` | [computed at seal] |
| `run_c2.py` (resumable, localhost guard, ledger, STOP file), `models.json` | [computed at seal] |
| `SEED-RULE.txt`, `check_blocks.py`, the 969803 test vector | [computed at seal] |
| `RESULTS-WORDING-PREWRITTEN.md`, `PILOT-RECORD.json` (dev numbers, medians, N, revision rounds) | [computed at seal] |
| His predictions envelope (hash only) and Claude's forecast; the hash-chained ledger of Seal 1 submissions | [his file hash] / [computed at seal] |

**Stamped as Seal 1b before the first stage 0 call:** `SEED-RECORD.txt`, the order lists (`order0`, `order1` per model), the digest and version record.

**Limit of a seal.** It shows the bytes existed by then. It cannot show that nobody looked early or that no other design was set aside.

**Predictions (sealed privately by hash; no public scorecard).** His probabilities are his to set; Claude's forecast is written at the seal, before any model call.

| # | Proposition (per model unless stated) | His probability | Claude's forecast |
|---|---|---|---|
| 1 | A's target-act rate: under 10% / 10% to 29% / 30% to 59% / 60% to 75% / over 75% (qwen; gemma) | [HIS PROBABILITY] x 5 each | [at seal] |
| 2 | P acts in at least 108 of 120 (qwen; gemma) | [HIS PROBABILITY] | [at seal] |
| 3 | B minus A clears (at least 18 of 120) (qwen; gemma) | [HIS PROBABILITY] | [at seal] |
| 4 | B2 and B3 both clear against A (qwen; gemma) | [HIS PROBABILITY] | [at seal] |
| 5 | G minus A clears (the goal mention alone moves acting) | [HIS PROBABILITY] | [at seal] |
| 6 | B minus G clears | [HIS PROBABILITY] | [at seal] |
| 7 | Decoy acting rises in B (label F9 applies) | [HIS PROBABILITY] | [at seal] |
| 8 | Overall: Pass / Thin pass / narrow (one model) / both Fail excluded / other | [HIS PROBABILITY] x 5 | [at seal] |
| 9 | Which model shows the larger B minus A: qwen / gemma | [HIS PROBABILITY] | [at seal] |

## 12. What this design cannot show

- **Real agents.** Two small local models, one scripted prompt shape, invented tasks, single turn, no tools run. Nothing carries to frontier models, long sessions or real deployments without a rerun.
- **Knowing.** It measures a reply event after a sentence was added, not belief or understanding.
- **Which part of the link sentence.** B minus G separates the link statement from the goal phrase and from text of equal length. It does not separate 'the record serves the goal' from 'the record is relevant' or from an implied instruction. A purely unrelated length control (the first draft's Z) is dropped from v1; G absorbs length and goal effects together, so a null B minus G cannot say which of the two it was (G minus A is reported). A topic-only or Z-type control is a follow-up.
- **Purpose against instruction.** B holds no command, but a model may read a purpose statement as an implied order. P is the explicit-order arm and is a gate, not a comparison.
- **Wording and place.** Three wordings, one position (the system message), English only.
- **Sampling.** Temperature 0 gives one trajectory per task per arm. Tasks, not repeats, are the replicates. The determinism re-run measures only repeatability.
- **The test frame.** Every arm says the scenario is invented. Acting may differ when the model thinks it is real; that cannot be tested honestly here.
- **Whether acting is wise.** Every acting verb is benign. Harmful acts and injection are not tested (T10).
- **Effects under about 10 points.** At a true 10 points the lone comparison clears about 16% of the time and all rules together 0.8%. A fail with the effect excluded rules out 15 points, not 5.
- **Who wrote the tasks.** Claude agents (an author-family limit). Outsider-written tasks are a later v2.
- **Both models at once.** The both-models claim is an intersection; its power is the square of one model's.
- **Gate selection.** Models are kept or dropped on A's observed rate; this does not bias B minus A in a deterministic run but is a declared selection step.
- **That nobody looked early.** A seal shows the bytes existed by a time, nothing more.

## 13. Doubts considered and dismissed

- **'Use default sampling with several seeds.'** Dismissed: temperature 0 gives an auditable run; tasks are the replicates. Wrong if outputs flip on many tasks; the determinism re-run would show it.
- **'Make B an explicit instruction.'** Dismissed: that is arm P, a gate.
- **'Test frontier models.'** Dismissed for v1: local only; any outside model needs his yes and a v2.
- **'Use real agent logs.'** Dismissed: the planted truth must be known by construction, and gated data may not go to a model.
- **'Let a model judge whether the agent acted.'** Dismissed: his rule is a script.
- **'Pool the two models for power.'** Dismissed: each is analysed alone.
- **'Keep Z as well as G.'** Dismissed for v1: 7 arms cost about 17% more CPU (worst seen 43 h, over the cap). Z is a follow-up.
- **'The margin is only a point-estimate rule.'** Accepted: that is why Thin pass exists and why three wordings and B minus G are all required.
- **'N = 120 is too small for 15 points.'** Accepted in part: 120 finds 25 points reliably and 20 points about two times in three. The design says what it can see.
- **'Reading the A rate before stage 1 is peeking.'** Dismissed: the gate looks only at A and P, never at B, B2, B3 or G, and the rule is sealed.
- **'Tuning on the dev set before the seal is forking paths.'** Accepted and bounded: at most two logged revision rounds, only for format or headroom, never touching B1, B2, B3, G or the facts; the pilot runs only A and P.
- **'The prompt tells the model it is a test.'** Accepted as a limit; dropping it breaks the welfare floor; it is the same in every arm.
- **'Cluster by domain is overkill.'** Dismissed: it costs nothing and L must respect it (0.27 points from the simple bound on average).
- **'A 24% flip rate is a guess.'** Accepted: Table 1 sensitivity shows 18% and 29%.
- **'Turn on thinking.'** Dismissed: v3's setting is thinking off; a thinking-on arm is a later v2.

**Not verified in this design:** speeds at this prompt size and whether Ollama reuses its cache (the pilot measures); that thinking off holds for both models in Ollama 0.34.4 (pilot checks); that both models follow the DO format at all (gates F1, F3); the model digests and Ollama version (as the plans report; re-read at the freeze check); the 15-second seed margin (W2's value); FreeTSA and OpenTimestamps usage terms; model licence terms (from memory, verify; not legal advice); that nothing else loads the PC during a window.

---

## Appendix: adversarial review before the seal (verdict: sealable with fixes)

20 problems were found; every fix is already in the text above. High-severity ones:

- **Confound at the centre of the claim. Arm A holds no goal at all, and B is the only arm that gives the model the goal phrase. So B minus A measures 'the goal was supplied plus a link sentence', not 'the agent knows the context is there'. The control Z carried no goal, so it could not catch this. A model that simply links the goal phrase to the entry that shares a word with it would pass every rule.**
  Fix: Replace Z with G: the same goal sentence plus neutral filler, length-matched to B1, with no statement that the record serves the goal. B minus G must clear (at least 18 net of 120, p below 0.05). The design stays at 6 arms and 720 runs per model, so CPU is unchanged. If G minus A also clears, the label is 'goal mention alone moves acting'. Power was re-simulated for the new rule set (Tables 1 to 3).
- **The fail rules lean on B1 alone. F5 'effect excluded' and the ruling 'both models fail, END THE LINE' used only B1 minus A. B1 failing while B2 and B3 clear (or the reverse) had no row: F6 only covered 'B clears but B2 or B3 does not'. A line could be ended by one unlucky wording.**
  Fix: Count k = how many of B1, B2, B3 clear against A. k=0 is Fail (excluded only if the cluster-bootstrap upper bound is below 15 points for all three). k=1 or 2 is Wording-specific. k=3 goes on to the G rule and the lower-bound rule. Every model gets exactly one verdict from an ordered list.
- **Contradiction in the failure rules. 'Three failed calls in a row stop the run' makes the other rule ('more than 7 of 720 cells with no reply after three tries') impossible: the first cell that fails three tries is already three failed calls in a row.**
  Fix: A cell gets up to 3 tries. A cell with no reply after 3 tries is logged as 'no reply' (counts as no act). The run stops on 3 consecutive such cells (9 failed calls). The total cap of 7 of 720 (5 of 540) is kept. This is declared as a deviation from v3's rule.
- **Owner's rule 3 conflict. The design says the calendar limit and the seed margin are read 'from the token file' (the FreeTSA token). A file whose name contains 'token' must not be opened by an AI tool. The validator also did not check work-folder file names.**
  Fix: Name the stamp files freetsa-reply.tsr and ots-proof.ots. The seal time goes in SEAL-TIME.txt, printed by the stamp script or read by him. The validator fails any work-folder file name containing auth, token, key, secret or credential. No .env file.
