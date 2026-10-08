> Published copy. The sealed original `LOCAL-REPEAT-DESIGN.md` (SHA-256 `934d1c274483a52f5fd91685593cf81b96a11b03af2d510a74c3b6d53d28c48a`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# Noise test 2: is the local Lemonade lane reproducible? (sealed design, 5 Oct 2026)

Written by the coordinating Claude session from 18:47:47 UTC on 5 Oct 2026 (clock). Joshua is away ("act autonomously for the next 30-60 testing", 18:46:19 UTC). Sealed while run 2's local lane is still running and before this repeat starts.

## The question
Hosted models at temperature 0 changed 15 to 23 of 140 verdicts between identical runs (4 to 22 when pinned). Does AMD's Lemonade server on this PC give the same verdicts and the same reply text when run 2's local lane is repeated?

## Design
- **Items:** 201 to 240 (40 items) of the sealed bank (edb897f7...593a), all inside run 2's primary set.
- **Arms:** run 2's local lane, unchanged:
  - L-A, Qwen3-4B-Instruct-2507-GGUF;
  - L-B, Gemma-4-E4B-it-GGUF.
- **Code and settings:** the same code (`run_pair.run` through `run2.local`) and the same settings: temperature 0, max_tokens 400, seed 42, thinking off for Gemma.
- **Output:** `run2/results/answers-run2-local-repeat.jsonl`.
- **When:** the repeat starts only after run 2's local lane has finished. Nothing else heavy runs during it; Daybreak's quiet gate pauses it if needed.

## Measures
For each arm, against run 2's local lane on the same 40 items:
- identical verdicts, k of 40;
- identical reply text (reply SHA-256), k of 40.

Seconds per item are reported for context.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Honest limits
- 40 items.
- One machine.
- Lemonade's own internals (threads, batching) are not controlled beyond its defaults.
