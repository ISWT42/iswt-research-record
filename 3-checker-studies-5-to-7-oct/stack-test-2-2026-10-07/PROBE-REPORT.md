# Probe report (stack test 2, Test A)

Written by `run_matrix.py probe`; regenerated 2026-10-07T19:24:43Z. Toy items only (not among the 48 logs). Nothing here is a result.

## claude-ours: PASS

```json
{
 "cell": "claude-ours",
 "kind": "ours",
 "time": "2026-10-07T19:24:43Z",
 "model_asked": "anthropic/claude-sonnet-5.5",
 "toy_calls": 12,
 "toy_answered": 12,
 "toy_valid_replies": 12,
 "slug_accepted": true,
 "effort_accepted": true,
 "effort_sent": "low",
 "models_reported": [
  "anthropic/claude-sonnet-5.5"
 ],
 "models_reported_accepted": true,
 "upstream_providers": [
  "Claude Platform on AWS"
 ],
 "mean_input_tokens": 304.3333333333333,
 "mean_output_tokens": 68.33333333333333,
 "mean_reasoning_tokens": 0.0,
 "mean_cost_usd": 0.001292,
 "mean_seconds": 3.0233333333333334,
 "total_probe_cost_usd": 0.020774,
 "finish_reasons": [
  "stop"
 ],
 "knob_tokens_low": [
  58,
  189
 ],
 "knob_tokens_high": [
  38,
  304
 ],
 "knob_high_effort": "high",
 "effort_confirmed": true,
 "errors": [],
 "pass": true,
 "flags": [],
 "settings_sha256": "66f527c65303f492a0ecdc5855e1b9c59f35b3a0ca01282ffee2ab9f837aa0f1"
}
```

## openai-ours: PASS

```json
{
 "cell": "openai-ours",
 "kind": "ours",
 "time": "2026-10-07T19:23:52Z",
 "model_asked": "openai/gpt-6.1-sol",
 "toy_calls": 12,
 "toy_answered": 12,
 "toy_valid_replies": 12,
 "slug_accepted": true,
 "effort_accepted": true,
 "effort_sent": "low",
 "models_reported": [
  "openai/gpt-6.1-sol"
 ],
 "models_reported_accepted": true,
 "upstream_providers": [
  "OpenAI"
 ],
 "mean_input_tokens": 201.0,
 "mean_output_tokens": 39.25,
 "mean_reasoning_tokens": 0.0,
 "mean_cost_usd": 0.0007945000000000001,
 "mean_seconds": 2.9499999999999997,
 "total_probe_cost_usd": 0.014382,
 "finish_reasons": [
  "stop"
 ],
 "knob_tokens_low": [
  66,
  188
 ],
 "knob_tokens_high": [
  104,
  436
 ],
 "knob_high_effort": "high",
 "effort_confirmed": true,
 "errors": [],
 "pass": true,
 "flags": [],
 "settings_sha256": "66f527c65303f492a0ecdc5855e1b9c59f35b3a0ca01282ffee2ab9f837aa0f1"
}
```

