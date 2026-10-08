> Published copy. The sealed original `S9-WOBBLE.md` (SHA-256 `319321fda833120a1613850df1c063c885816812137db95b8f93be388894daa1`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: forecast or prediction lines removed; 1 forecast section(s) or paragraph(s) removed.

# S9: The wobble test (sealed with Addendum 6; it runs only after the owner's yes in the session)

**Question.** When a checker is asked the same question several times at a higher temperature, do its answers wobble more when its usual answer is wrong? If "shown" counts only when every sample agrees, how many false passes does that stop, and how many true passes does it cost? And is one model disagreeing with itself as good a warning as two different models disagreeing with each other?

**Origin:** Joshua named it at 12:56 UTC on 6 Oct 2026: "temperature testing is important, we can call it the wobble test." His go: "Lets run a gemini in the box test", 13:49:48 UTC.

## Inputs
`inputs/s8-items.jsonl`: S8's 280 label-free records. These are 60 logs that don't back their claim, each in four versions (V0 to V3), plus 40 logs that do (V0). Each record has `id`, `claim`, `turns` and `variant`.

## Models and request body
`qwen/qwen3.5-9b` and `google/gemma-4-26b-a4b-it`, the S4 pair. The request body is the README's, with only `temperature` and `seed` changing by arm:
`{"model", "messages", "temperature", "seed", "max_tokens": 400, "reasoning": {"enabled": false}, "provider": {"data_collection": "deny"}}`

## The request (the same in every arm)
- Build the request with `receipt_pair.pair.prepare(item_id, claim, turns)` (vendored at `b7dfbad`).
- Send `request.system` and `request.user` unchanged.
- Check every reply with `receipt_pair.reader.verify(reply_text, shown)`.

## Arms (per record, per model)
- **W0, the usual answer:** one call at `temperature` 0, `seed` 42. This is S8's B0, asked again.
- **W5, five samples:** five calls at `temperature` 0.7, with seeds 101, 102, 103, 104 and 105.

That is 6 calls per record and model.

## Calls and spend
- 280 records × 2 models × 6 calls = **3,360 calls**. There is no separate repeat; the five samples are the repetition.
- **Stop at US$2 reported cost.** The estimate is under US$1.

## Recording
- Record every call as in S1 to S8: the request, the response, OpenRouter's `id`, `provider` and `usage`.
- Record the `verify` outcome (answer, code, quote) and the arm, seed and temperature.
- Write `runs/s9/calls.jsonl`, `runs/s9/order.json` and `runs/s9/MANIFEST.sha256`.

## What the coordinator will count (not the runner)
- **Per model:** false "shown" (of 240) and true "shown" kept (of 40) for each rule:
  - W0;
  - **all five agree** ("shown" only if all five samples are verified "shown");
  - a **majority** of five (at least 3).
- **Self against cross:** "all five agree" for one model, against the two models agreeing at W0 (rule R2, "shown needs both").
- **The wobble itself:** how often the five samples split, on records where W0 was right against where it was wrong. Exact tests, counts first.

[paragraph removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Stop and report if
- more than 5% of calls end as "no answer";
- the S9 spend passes US$2;
- anything in this spec is unclear (write it in QUESTIONS.md).
