> Published copy. The sealed original `S12-FORCED-SWEEP.md` (SHA-256 `4c2f44916e273f7aa5a6457de8da9681c0b13bfcd37564a04a2d24af3106f64e`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# S12: Forced yes-or-no, on nine models (sealed with Addendum 7)

**Question.** In E2, two small local models guessed far more often when they were forced to answer "shown" or "contradicted" on a log missing its deciding evidence. When "not shown" was allowed, the guessing fell, and right answers on intact logs did not change. Does the same hold for large, recent models?

**Origin:** Joshua's "un-forcing the human-forced errors" and "don't force the binary". E2 measured it on small local models (F13). This repeats it on the nine models of S6.

## Inputs (built by the coordinator, label-free)
- `inputs/s12-requests.jsonl`: 54 records, each `{"id", "user"}`. `user` is the exact user message E2 sent (the claim and the log's turns).
  - Some logs are intact. Others had their deciding evidence removed.
  - The ids are opaque (T001 to T054, in a seeded shuffle), so nothing in a record tells which kind it is.
- `inputs/s12-framings.json`: the two system prompts, exactly as E2 used them:
  - `allowed`: the frozen reader prompt, where "not_shown" is allowed;
  - `forced`: the same prompt with "not_shown" taken away.

## Arms
- **forced:** system prompt `framings.forced`, user message `user`.
- **allowed:** system prompt `framings.allowed`, user message `user`.

Send them exactly as given, with no other text.

## Models and settings
The nine models and per-model settings of S6 after Addendum 5:
- `qwen/qwen3.5-9b`, `google/gemma-4-26b-a4b-it`, `deepseek/deepseek-v4.1-flash` and `moonshotai/kimi-k3`: reasoning off, `max_tokens` 2000.
- `openai/gpt-6.1-sol`, `google/gemini-3.8-flash`, `x-ai/grok-4.7`, `z-ai/glm-5.3` and `anthropic/claude-opus-5.5`: `"reasoning": {"effort": "low"}`, `max_tokens` 4000.
- Otherwise the README's request body: temperature 0, seed 42, data_collection deny.

## Calls and spend
- 54 records × 2 framings × 9 models = **972 calls**. No repeat.
- **Stop at US$4 reported cost.**

## Recording
- Record every call as in S6: the request, the response, OpenRouter's `id`, `provider` and `usage`.
- Parse `verdict` from the JSON reply. Keep the raw text whatever happens.
- The coordinator checks every quote afterwards against the source logs. The runner does not need `receipt_pair` for S12.

## What the coordinator will count (not the runner)
- **Per model and framing:** guesses ("shown" or "contradicted") on the logs missing their evidence (of 27), and right answers on the intact logs (of 27).
- **Paired comparisons:** forced against allowed, exact tests, counts first.

[paragraph removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
