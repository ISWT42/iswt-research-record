# Probe report (stack test 2, Test A)

Written by `run_matrix.py probe`; regenerated 2026-10-07T19:17:39Z. Toy items only (not among the 48 logs). Nothing here is a result.

## openai-theirs: PASS

```json
{
 "cell": "openai-theirs",
 "kind": "codex",
 "time": "2026-10-07T19:17:37Z",
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
  "STANDIN_HELP_OMIT",
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
 "codex_features_listed": 20,
 "flags_dropped": [
  "--ignore-rules",
  "--disable code_mode_host"
 ],
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
   "seconds": 0.17
  },
  {
   "sentinel": "NO_SHELL_TOOL",
   "ok": true,
   "reply_head": "NO_SHELL_TOOL",
   "tool_attempts": 0,
   "kind": "answered",
   "error": null,
   "answer_model": "gpt-6.1-sol",
   "seconds": 0.15
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
 "mean_seconds": 0.135,
 "pass": true,
 "settings_reported_note": "Codex: the header on stderr if it appeared with --json (see the saved stderr files); otherwise the flags as passed are the record.",
 "settings_sha256": "f3ad21f2097b6bba3690e4481bf7e419ed2c7b55ed6ec034b7cd478ffc0acdfc"
}
```

