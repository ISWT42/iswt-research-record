> Published copy. The sealed original `STAGE2C-DESIGN.md` (SHA-256 `15abea85dec5ea70e3b15b99654877d2d070a58efb3f501fdc0987469eef2df6`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# Run 3, stage 2c: a narrow question about the receipt alone (sealed design, 5 Oct 2026)

Written by the coordinating Claude session from 18:27 UTC on 5 Oct 2026 (clock). Joshua's words, 18:26:45 UTC: "keep working. i know you have the context to know what to test". It is sealed before any stage 2c call.

## Why
In stages 2 and 2b, the model re-read the whole record with the check's output appended as its last turn. Gemma still answered "not_shown" (and marked itself sure) on about 15 of 39 of those items. One added sentence telling it the check decides changed that only from 16 to 14 (stage 2b, sealed 18:23:22 GMT).

**Hypothesis:** the failure is structural. The model weighs the whole record and discounts the late check. A verifier step that asks one narrow question about the receipt alone, "does this output show the claim succeeded, failed, or neither?", should let it use the receipt.

## Items and providers
- **Items:** the same 62 (arm, item) pairs as stage 2b (Qwen 23, Gemma 39), each scored against Sol's settles_as.
- **Providers:** pinned exactly as in 2b, `qwen/qwen3.5-9b@SiliconFlow` and `google/gemma-4-26b-a4b-it@Darkbloom`, through openrouter-plain (temperature 0, seed 42, reasoning off, max_tokens 400, data_collection deny).

## The narrow question (C), byte for byte as `NARROW_SYSTEM` and `narrow_user()` in `stage2c.py`
- **System:** "You check one claim against the output of one read-only command. Decide whether that OUTPUT shows the claim succeeded (shown), shows it failed (contradicted), or shows neither (not_shown). For shown or contradicted, quote one whole line copied exactly from the OUTPUT. Reply with JSON only: {\"verdict\": \"shown\" or \"contradicted\" or \"not_shown\", \"quote\": \"...\", \"certainty\": \"sure\" or \"unsure\"}."
- **User:** "CLAIM: <claim>\nCOMMAND: <check_cmd>\nOUTPUT:\n<check_output>". Nothing else from the record.

## Mechanical check (the same principle as v3's verify)
- A "shown" or "contradicted" verdict counts only if the quote, stripped, equals one whole line of the check's output. Otherwise it becomes "not shown", with code `unverified_quote`.
- Unparseable or invalid replies become "not shown".
- Policy U applies: anything not marked "sure" is "not shown".

## Comparison
Paired against stage 2b's A, the same items, providers and pinning, using the whole record with no added sentence.

## Measures (counts first)
For each arm, C against 2b-A:
- right;
- still "not shown";
- false "shown";
- false "contradicted";
- fixed and broken.

The pinned-repeat noise floor is reported beside it.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Budget
A cap of US$3; the estimate is under US$0.01. Two retries, then "no answer". Results are hashed and stamped by FreeTSA before anyone reads them.

## Honest limits
- Sol wrote the check outputs and settles_as, on purpose to settle each claim.
- A narrow question can only be as good as the check it is given.
- 62 pairs is small.
