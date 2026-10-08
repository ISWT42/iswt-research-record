> Published copy. The sealed original `PINNED-REPEAT-DESIGN.md` (SHA-256 `9316c85d818bd9142d70a61d45f8818c93cf3259f129244521cf21a93337c75f`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# Noise test: pinned-provider repeat (sealed design, 5 Oct 2026)

Written by the coordinating Claude session from 18:13:37 UTC on 5 Oct 2026 (clock), after Joshua's "that is a finding for sure" (18:11:12 UTC) and "Please do all of the above" (18:13:16 UTC).

## The question
When one upstream provider is pinned, does an identical re-run at temperature 0 give the same verdicts and the same reply text?

## Why this test
Unpinned, an identical re-run changed the verdict on 15 of 140 items for Qwen and 23 of 140 for Gemma. Most of the changes went with a switch of provider, but even on the same provider the reply text changed in 19 of 54 pairs for Qwen and 20 of 35 for Gemma.

## Design
- **Items:** the same 140 fresh items, 161 to 300, of the sealed bank (SHA-256 edb897f7...593a).
- **Prompt and settings:** run 2's exact prompt and settings, through the AI broker's openrouter-plain mode (temperature 0, seed 42, reasoning off, max_tokens 400, data_collection deny).
- **Pins** (broker commit 927061a):
  - P-Q = `qwen/qwen3.5-9b@SiliconFlow`;
  - P-G = `google/gemma-4-26b-a4b-it@Darkbloom`.

  Each was the most frequent provider for its model in both earlier runs. allow_fallbacks is false, so a call fails rather than reach another provider.
- **Two runs, one after the other:** pinned-1, then pinned-2.

## Measures (counts first, with denominators)
For each arm:
- identical verdicts, pinned-1 against pinned-2 (k of 140);
- identical reply text (k of 140);
- calls answered by a provider other than the pin (should be 0);
- calls that failed.

Compared with the unpinned run against its repeat: verdicts 125 of 140 identical for Qwen and 117 of 140 for Gemma. Right / n for each run is reported as well.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Budget
A cap of US$3 in total; the estimate is about US$0.07. A failed call is retried twice, then recorded as no answer.
