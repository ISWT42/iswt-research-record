> Published copy. The sealed original `DESIGN.md` (SHA-256 `a463e29d69661df1e0ff67abad5d77ca61642d445c37057d6e771d8cce04b42e`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# S13, the stack test: Sol and Gemini through their own agent tools, as the models under test (7 October 2026)

Designed by Claude, the coordinator, for Joshua Bauer. Sealed before any call. His words, 7 Oct 2026, 02:45 UTC: "we should run a stack test + red team. we can give SOL 6.1 Max + Gemini 3.8 Flash Max first, before using openrouter". At 02:59 UTC: "Lets do models under test first then operators after."

## The question
S12 (sealed 6 Oct 2026) asked nine models through the plain API, at low reasoning, to judge 54 agent logs. Twice: once **forced** to answer "shown" or "contradicted", and once **allowed** to answer "not shown". Through the API:
- GPT-6.1 Sol guessed on 27 of 27 logs missing their deciding evidence when forced, and on 2 of 27 when allowed. It was right on 26 and 25 of 27 intact logs.
- Gemini 3.8 Flash guessed on 20 and 3 of 27, and was right on 27 and 26 of 27. It gave no verdict in 7 of its 108 calls.

**S13 asks:** do the same two models show the same pattern when used the way people use them, through their own agent tools at the top settings those tools offer?
- **Sol:** OpenAI's Codex command line (codex-cli 0.159.3) with GPT-6.1 Sol at reasoning effort "xhigh".
- **Gemini:** Google's Gemini command line (0.62.0) with Gemini 3.8 Flash. The tool has no setting for thinking, so it runs at its default, and the runner records what the tool reports.

## Inputs (label-free, unchanged)
- `inputs/s12-requests.jsonl`: S12's 54 records, each `{"id", "user"}`, ids T001 to T054 in S12's seeded shuffle. Some logs are intact, and others had their deciding evidence removed. Nothing in a record says which.
- `inputs/s12-framings.json`: S12's two instruction texts, `forced` and `allowed`.
- **The answer key stays on Joshua's PC and never enters the box:** `Private\gemini-pack-keys-2026-10-06\s12-keys.jsonl`, sealed 6 Oct 2026.

## Calls
- **The size:** 2 tools × 54 records × 2 framings = **216 calls**, no repeats. Each call is a fresh, non-interactive session in an empty folder.
- **The prompt** is the framing text, a blank line, then the record's `user` text, byte for byte. S12 sent the framing as the system message; these tools take one prompt, so the framing leads the prompt. This is part of what "the stack" means here, and it's a stated difference from S12.
- **Sol:** `codex exec --skip-git-repo-check --ephemeral --sandbox read-only --color never -m gpt-6.1-sol -c model_reasoning_effort="xhigh" -o <reply file> "<prompt>"`.
- **Gemini:** `gemini -m gemini-3.8-flash --approval-mode plan -o json -p "<prompt>"`.
- **Order:** record by record, forced then allowed. The two tools run side by side as two background processes.
- **Time limit:** 600 seconds per call. A call that runs out of time, or fails, is recorded with no verdict, never dropped.
- **Kept for every call:** the tool, record id, framing, the prompt's SHA-256, start and end times, exit code, the raw reply, the verdict parsed from it, and whatever model name and usage the tool reports.
- **Pausing:** a `PAUSE` file in the run folder pauses between calls. A `HALT` file stops after the current call.
- **Cost:** no cash spend is expected. Both tools run on Joshua's own sign-ins in the box (his ChatGPT plan for Codex, his Google sign-in for Gemini). If the Gemini tool turns out to bill an API key, the $30 cap set on 6 Oct applies.

## What the coordinator counts afterwards (not the runner)
The results are sealed first, then scored on the PC against the sealed key.
- **For each tool and framing:** guesses ("shown" or "contradicted") on the 27 logs missing their evidence, and right answers on the 27 intact logs. Each count has its own denominator, and calls with no verdict are counted separately.
- **Paired, forced against allowed:** exact McNemar tests, counts first.
- **Against S12:** the same model's verdict on the same record and framing, through the API.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## Limits, stated before the run
- One run each, no repeats. The hosted noise floor (6 Oct) says temperature-0 calls are not exactly repeatable, and these tools don't let us set temperature at all.
- The framing sits in the prompt, not in a system message, and each tool adds instructions of its own. That is the point of a stack test, and it is also why it can't isolate the model.
- The logs and their labels were written by a model, and no person has checked the labels yet.
- Operators come later. Here the two models are the ones being tested, and Claude runs nothing in their sessions.
