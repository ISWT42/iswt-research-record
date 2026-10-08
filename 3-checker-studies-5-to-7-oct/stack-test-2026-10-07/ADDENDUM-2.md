# S13 stack test, addendum 2: the Gemini tool's web search turned off (7 October 2026)

Dated addendum. The sealed design (FreeTSA 06:14:50 GMT) and addendum 1 (06:19:25 GMT) stand; the forecasts stand as sealed.

## What happened
- **The Gemini half restarted at 06:19:26 UTC** with the fixed runner from addendum 1. Its first call (T001, forced) did not crash.
- **But it searched the web.** The Gemini command line called its built-in `google_web_search` tool again and again, on phrases from the prompt. Four searches ran between 06:19:58 and 06:23:28 UTC, each taking one to two minutes. The tool's own session log in the box shows this.
- **Claude stopped the Gemini half at about 06:25 UTC,** before that call finished. Nothing was recorded for it.
- **The Sol half was not touched.** Its calls take seconds, and Codex's web search is not turned on in the box's Codex settings.

## The change
- **The setting:** a settings file in the Gemini run folder only, `results/gemini-empty-folder/.gemini/settings.json`, holding `{"tools": {"exclude": ["google_web_search", "web_fetch"]}}`. This is the tool's documented `tools.exclude` setting. Joshua's own Gemini settings are untouched.
- **The check, before the restart:** one call with a prompt that was not a test record ("Search the web for the phrase ISWT Protocol ... If you have no web search tool available, reply with exactly: NO_WEB_TOOL"). Gemini answered "NO_WEB_TOOL" and made 0 tool calls.
- **No other change.** The runner (SHA-256 6ed665ba...78a6), the prompts, the order, the time limit and the parsing are as in addendum 1.

## Why
- Joshua's standing rule since 7 Oct 2026 is web search off unless he asks for it.
- S12, the comparison, sent the same prompts with no tools at all.
- With web search on, each call ran into the 600-second limit, so the half could not finish.
- The test asks how the models judge the log they are given. Searching the web for an invented log's phrases cannot settle that.

## For the reader
This is now a stack test with the tools' web search off: the agent tool's own instructions and harness, without browsing. The Sol stack had no web search either, so the two halves match.
