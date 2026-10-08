# Probe report (stack test 2, Test A)

Written by `run_matrix.py probe`; regenerated 2026-10-07T19:16:21Z. Toy items only (not among the 48 logs). Nothing here is a result.

## claude-ours: PASS

```json
{
 "cell": "claude-ours",
 "kind": "ours",
 "time": "2026-10-07T19:16:15Z",
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
  "StandInProvider"
 ],
 "mean_input_tokens": 100.0,
 "mean_output_tokens": 40.0,
 "mean_reasoning_tokens": 10.0,
 "mean_cost_usd": 0.001,
 "mean_seconds": 0.10333333333333333,
 "total_probe_cost_usd": 0.016,
 "finish_reasons": [
  "stop"
 ],
 "knob_tokens_low": [
  50,
  50
 ],
 "knob_tokens_high": [
  350,
  350
 ],
 "knob_high_effort": "high",
 "effort_confirmed": true,
 "errors": [],
 "pass": true,
 "flags": [],
 "settings_sha256": "a5bff73d0d36213d13641dba4e4d586f017c7c61e004669bc223d00f16183108"
}
```

## claude-theirs: PASS

```json
{
 "cell": "claude-theirs",
 "kind": "claude-code",
 "time": "2026-10-07T19:16:17Z",
 "model_asked": "claude-sonnet-5-5",
 "effort_asked": "low",
 "flags": [],
 "problems": [],
 "version": "2.1.286 (Claude Code)",
 "version_planned": "2.1.286",
 "version_note": "same as planned",
 "env_names_passed": [
  "APPDATA",
  "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC",
  "COMSPEC",
  "DISABLE_AUTOUPDATER",
  "HOME",
  "LOCALAPPDATA",
  "PATH",
  "PATHEXT",
  "SHELL",
  "SYSTEMROOT",
  "TEMP",
  "TERM",
  "TMP",
  "USERPROFILE",
  "WINDIR"
 ],
 "key_like_env_names": [],
 "auth": {
  "loggedIn": true,
  "authMethod": "claude.ai",
  "subscriptionType": "max"
 },
 "required_flags_missing": [],
 "flags_dropped": [],
 "canaries": [
  {
   "sentinel": "NO_FILE_TOOL",
   "ok": true,
   "reply_head": "NO_FILE_TOOL",
   "tool_attempts": 0,
   "kind": "answered",
   "error": null,
   "answer_model": "claude-sonnet-5-5",
   "seconds": 0.14
  },
  {
   "sentinel": "NO_WEB_TOOL",
   "ok": true,
   "reply_head": "NO_WEB_TOOL",
   "tool_attempts": 0,
   "kind": "answered",
   "error": null,
   "answer_model": "claude-sonnet-5-5",
   "seconds": 0.2
  },
  {
   "sentinel": "NO_SHELL_TOOL",
   "ok": true,
   "reply_head": "NO_SHELL_TOOL",
   "tool_attempts": 0,
   "kind": "answered",
   "error": null,
   "answer_model": "claude-sonnet-5-5",
   "seconds": 0.15
  }
 ],
 "init": {
  "model": "claude-sonnet-5-5",
  "tools": [],
  "mcp_servers": [],
  "apiKeySource": "none",
  "permissionMode": "default",
  "plugins": [],
  "effort": null,
  "version": "2.1.286"
 },
 "init_lists_for_review": {
  "skills": [],
  "slash_commands": [
   "compact"
  ],
  "agents": []
 },
 "knob_tokens_low": [
  25,
  25
 ],
 "knob_tokens_high": [
  350,
  350
 ],
 "knob_high_effort": "max",
 "effort_confirmed": true,
 "mean_cost_usd_shadow": 0.0123,
 "mean_seconds": 0.14,
 "pass": true,
 "settings_reported_note": "Claude Code: the init event (above).",
 "settings_sha256": "a5bff73d0d36213d13641dba4e4d586f017c7c61e004669bc223d00f16183108"
}
```

## openai-ours: PASS

```json
{
 "cell": "openai-ours",
 "kind": "ours",
 "time": "2026-10-07T19:16:17Z",
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
  "StandInProvider"
 ],
 "mean_input_tokens": 100.0,
 "mean_output_tokens": 40.0,
 "mean_reasoning_tokens": 10.0,
 "mean_cost_usd": 0.001,
 "mean_seconds": 0.10916666666666668,
 "total_probe_cost_usd": 0.016,
 "finish_reasons": [
  "stop"
 ],
 "knob_tokens_low": [
  50,
  50
 ],
 "knob_tokens_high": [
  350,
  350
 ],
 "knob_high_effort": "high",
 "effort_confirmed": true,
 "errors": [],
 "pass": true,
 "flags": [],
 "settings_sha256": "a5bff73d0d36213d13641dba4e4d586f017c7c61e004669bc223d00f16183108"
}
```

## openai-theirs: PASS

```json
{
 "cell": "openai-theirs",
 "kind": "codex",
 "time": "2026-10-07T19:16:18Z",
 "model_asked": "gpt-6.1-sol",
 "effort_asked": "low",
 "flags": [],
 "problems": [],
 "version": "codex-cli 0.159.3",
 "version_planned": "0.159.3",
 "version_note": "same as planned",
 "env_names_passed": [
  "APPDATA",
  "COMSPEC",
  "HOME",
  "LOCALAPPDATA",
  "PATH",
  "PATHEXT",
  "SHELL",
  "SYSTEMROOT",
  "TEMP",
  "TERM",
  "TMP",
  "USERPROFILE",
  "WINDIR"
 ],
 "key_like_env_names": [],
 "auth": {
  "login_status_line": "Logged in using ChatGPT"
 },
 "required_flags_missing": [],
 "codex_features_listed": 21,
 "flags_dropped": [],
 "canaries": [
  {
   "sentinel": "NO_FILE_TOOL",
   "ok": true,
   "reply_head": "NO_FILE_TOOL",
   "tool_attempts": 0,
   "kind": "answered",
   "error": null,
   "answer_model": "gpt-6.1-sol",
   "seconds": 0.15
  },
  {
   "sentinel": "NO_WEB_TOOL",
   "ok": true,
   "reply_head": "NO_WEB_TOOL",
   "tool_attempts": 0,
   "kind": "answered",
   "error": null,
   "answer_model": "gpt-6.1-sol",
   "seconds": 0.15
  },
  {
   "sentinel": "NO_SHELL_TOOL",
   "ok": true,
   "reply_head": "NO_SHELL_TOOL",
   "tool_attempts": 0,
   "kind": "answered",
   "error": null,
   "answer_model": "gpt-6.1-sol",
   "seconds": 0.16
  }
 ],
 "knob_tokens_low": [
  25,
  25
 ],
 "knob_tokens_high": [
  350,
  350
 ],
 "knob_high_effort": "xhigh",
 "effort_confirmed": true,
 "mean_cost_usd_shadow": null,
 "mean_seconds": 0.15000000000000002,
 "pass": true,
 "settings_reported_note": "Codex: the header on stderr if it appeared with --json (see the saved stderr files); otherwise the flags as passed are the record.",
 "settings_sha256": "a5bff73d0d36213d13641dba4e4d586f017c7c61e004669bc223d00f16183108"
}
```

