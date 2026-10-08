> Published copy. The sealed original `DESIGN.md` (SHA-256 `83505c70db3c06b2ff2b56f29f07787566286742986d777429320e8fa1f2ac9f`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# S14, the word test: does "cannot" against "can't", and nothing else, change a model's verdict?

**Written:** 7 Oct 2026 by the coordinating session (Claude, Opus 5.5), at Joshua's yes ("I'll take all of those"), before any model call. Its time is the FreeTSA time on `RUN-SHA256.txt`; no time is typed here. The design is mine.

## The question
AI in Human Words, lesson 13, says: to a person, "can't" and "cannot" are one idea; to a model they are different words, learned in different company ("cannot" more in rules and error messages, "can't" more in conversation). It also says: whether swapping one for the other, alone, changes the model's answers "is not shown yet. It's testable: the same evidence and the same claim, with only the wording changed." This is that test.

## Items
S12's 54 records, ids T001 to T054: 27 logs missing their deciding evidence, 27 intact (13 shown, 14 contradicted). The key stays on the PC (`Private/gemini-pack-keys-2026-10-06/s12-keys.jsonl`, sealed 6 Oct) and is read only by the scorer. Neither model under test was in S12.

## The four instruction texts
Built by `run_s14.py` from S12's two framings, one exact replacement each:
- **Forced:** rule 5 `Answer only "shown" or "contradicted". "not_shown" is not an allowed answer.` becomes `Answer only "shown" or "contradicted". You cannot answer "not_shown".` or the same with `can't`.
- **Allowed:** rule 5 `For "not_shown": turn_id is null and quote is "".` gains the sentence `You cannot answer "shown" or "contradicted" without a quoted OUTPUT line.` or the same with `can't`.
- Within each pair the two texts differ in that one word and nothing else (check mode asserts it). The apostrophe is the plain one (U+0027).
- Fingerprints (SHA-256): forced_cannot df6de01a...becb, forced_cant 8668f49f...3dca, allowed_cannot 498ae837...7341, allowed_cant 661cb45c...6ad7.
- The record goes in the user message, as in S12; the text goes in the system message.

## Models and settings
`Qwen3-4B-Instruct-2507-GGUF` and `Gemma-4-E4B-it-GGUF` (thinking off) on Lemonade on this PC, temperature 0, seed 42, max_tokens 400: the gate test's settings and client (`vendor/receipt_pair`, from commit b7dfbad).

## Order and calls
- Qwen, then Gemma. Records in file order; each record gets all four texts, and which word goes first alternates record by record.
- **The repeat block (the determinism check):** 11 records drawn with seed 14, all four texts again, after each model's main block.
- 2 × (54 × 4 + 11 × 4) = **520 calls**, about 2 hours. One Lemonade user at a time: the runner refuses to start until the gate test's console says it ended. PAUSE file as in the gate test.

## What is counted (by a scorer written after the results seal, sealed before it runs)
Per model, with each count beside its own denominator:
1. **Changed pairs:** of the 108 record-and-framing pairs (54 records × forced and allowed), how many get a different verdict under "cannot" than under "can't". No verdict counts as a value of its own.
2. **Forced:** "breaks" (anything other than "shown" or "contradicted") under each word; guesses on the 27 missing logs; right answers on the 27 intact logs. Paired exact McNemar, cannot against can't.
3. **Allowed:** guesses on the 27 missing logs; right answers on the 27 intact logs; McNemar as above.
4. **Repeats:** how many of the 44 repeat calls give the same verdict as the main block on the same text.
5. Forced against allowed, across both words: guesses on missing (F18 on this PC).

## How it is read (fixed now)
- **"The word alone changes this model's verdict" is shown** for a model if at least one pair changes and its 44 repeats all agree with the main block. If any repeat disagrees, the changed share (of 108) is reported beside the repeat share (of 44), and the effect is called shown only if the changed share is at least three times the repeat share.
- **A direction** (for example "cannot" is obeyed more) is shown only with exact McNemar p < 0.05 for that model.
- Verdicts are parsed with a real JSON parse that tolerates braces inside quoted strings (the S13 lesson), tested before the run on replies whose quote holds JSON.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## What this does not settle
- Lesson 13 speaks as Claude. This test uses two small local models, so it tests the general claim, not Claude. A Claude arm would cost money through the API and needs Joshua's yes.
- One sentence in one place per text; one apostrophe; one item bank written by models whose labels no person has checked yet.
- His two phrasings ("must pass but cannot" against "must pass but can't fail") differ in more than the word: that is a meaning test, for later.

## Seals
1. This design, the runner, the inputs and the vendored client, in `RUN-SHA256.txt`, before any model call (FreeTSA, OpenTimestamps).
2. The results, before any count.
3. The scorer, before it runs.
