> Published copy. The sealed original `STAGE2E-DESIGN.md` (SHA-256 `bef0273c06f427bad0378451126a2c59de48ca038ff03e8f8e6c943ba89b317e`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# Run 3, stage 2e: the pair loop. Agreement for confident answers, the safe loop for the rest (sealed design, 5 Oct 2026)

Written by the coordinating Claude session from 18:47 UTC on 5 Oct 2026 (clock), while Joshua is away. His words, 18:46:19 UTC: "act autonomously for the next 30-60 testing". It is sealed before any stage 2e call.

## Why
In the single-model safe loop (stages 2, 2c and 2d, combined after the fact), the remaining false "shown" came from turn-1 answers marked "sure" that skip the loop. Run 2 showed that "agree or not shown" (R3) halves false "shown". This stage combines the two.

## Items
The 137 fresh items, 161 to 300, without 183, 278 and 289. Primary set: 201 to 300, without 278 and 289 (98 items).

## The pipeline, for each item
1. **Turn 1.** Run 3's sealed answers for both models (`answers-run3.jsonl`; no new call). If both are marked "sure" and agree on "shown" or "contradicted", that is final, scored against the bank's truth.
2. **Otherwise the loop:**
   - **(a) Proposal.** Take the first check that passes the gate, in this order: Qwen's run 3 settle command, then Gemma's. If neither passes, elicit one from Qwen, then from Gemma, with stage 2d's `ELICIT_SYSTEM` unchanged. If there is still no proposal, or the gate refuses it, the item is final "not shown", for a person. The gate is `run3.UNSAFE`, unchanged.
   - **(b) Receipt.** Sol's canonical read-only check for the item: its command and output. The model's command is not run.
   - **(c) Judge.** BOTH models answer stage 2c's narrow question (`NARROW_SYSTEM` and `narrow_user`, unchanged), with the whole-line quote check and policy U. The final answer is R3, "agree or not shown", scored against settles_as.
3. **Providers:** pinned as in 2b to 2d: `qwen/qwen3.5-9b@SiliconFlow` and `google/gemma-4-26b-a4b-it@Darkbloom`, through openrouter-plain.

## Measures (counts first)
For the primary set and the fresh set:
- right / n;
- false "shown" / items whose truth is not "shown";
- false "contradicted";
- sent to a person;
- how many items ended at turn 1, at the loop, and with no usable proposal.

**Reported beside them:**
- the single-model safe loops, combined after the fact from sealed parts: primary right Qwen 70 and Gemma 72 of 98; false "shown" 4 and 6 of 59;
- run 2's single models: primary right 57 and 62 of 98; false "shown" 10 and 6.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Budget
A cap of US$3; the estimate is about US$0.02. Two retries, then "no answer", counted as wrong. Results are hashed and stamped by FreeTSA before anyone reads them.

## Honest limits
- Loop items are scored against Sol's settles_as, the world truth once the receipt exists, and turn-1 items against the bank's truth.
- Sol wrote both the items and the checks.
- The gate is a word list.
- Hosted noise even when pinned: Qwen changed 22 of 140 verdicts between identical pinned runs.
