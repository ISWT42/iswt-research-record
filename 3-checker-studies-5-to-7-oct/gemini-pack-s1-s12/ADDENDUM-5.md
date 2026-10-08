# Addendum 5: newer models that refuse "reasoning off" (written 2026-10-06 04:48 UTC)

**The fault was the coordinator's, not the runner's.** S6's first attempts showed that six newer models reject `"reasoning": {"enabled": false}` with HTTP 400, "Reasoning is mandatory for this endpoint and cannot be disabled.":
- `openai/gpt-6.1-sol`
- `anthropic/claude-fable-5.1`
- `anthropic/claude-opus-5.5`
- `z-ai/glm-5.3`
- `google/gemini-3.8-flash`
- `x-ai/grok-4.7`

This addendum changes S6 and S7 only. Everything else stands.

1. **Stop and report.** Stop the current S6 run, keep its calls file, and report S6 as partial (README rule 5).
2. **Drop Claude Fable 5.1 from S6 and S7.** With reasoning it would cost more than the cap allows. S6 and S7 now use nine models.
3. **For the five remaining reasoning-only models** (GPT-6.1 Sol, Claude Opus 5.5, GLM 5.3, Gemini 3.8 Flash, Grok 4.7):
   - Send `"reasoning": {"effort": "low"}` instead of `{"enabled": false}`, with `max_tokens` 4000.
   - Record `usage.completion_tokens_details.reasoning_tokens` when present.
   - A reply cut off by the token limit still counts as "no answer".
4. **Keep the other four models exactly as before:** Qwen 3.5 9B, Gemma 4 26B, Kimi K3 and DeepSeek V4.1 Flash, with reasoning off and `max_tokens` 2000.
5. **Resume S6.**
   - Keep every answered call already recorded for the four unchanged models.
   - Move the rejected attempts (HTTP 400) of the six models to `runs/s6/rejected-reasoning-off.jsonl`, unchanged, and leave them out of `calls.jsonl`.
   - Then make every remaining call under these settings. Repeats and order follow Addendum 2, with the base list in S6's model order minus Fable.
6. **Then S7** with the same nine models and the same per-model settings.
7. **Spend stops are unchanged:** US$15 for S6 and US$12 for S7. Expected now: about US$8 for S6 and US$6 for S7.

The SHA-256 of this file is in `ADDENDUM-5-SHA256.txt`, sealed by FreeTSA.
