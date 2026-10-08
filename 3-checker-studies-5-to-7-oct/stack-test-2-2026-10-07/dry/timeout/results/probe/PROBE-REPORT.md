# Probe report (stack test 2, Test A)

Written by `run_matrix.py probe`; regenerated 2026-10-07T19:17:15Z. Toy items only (not among the 48 logs). Nothing here is a result.

## claude-theirs: PASS

```json
{
 "cell": "claude-theirs",
 "kind": "claude-code",
 "time": "2026-10-07T19:17:13Z",
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
   "seconds": 0.16
  },
  {
   "sentinel": "NO_SHELL_TOOL",
   "ok": true,
   "reply_head": "NO_SHELL_TOOL",
   "tool_attempts": 0,
   "kind": "answered",
   "error": null,
   "answer_model": "claude-sonnet-5-5",
   "seconds": 0.17
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
 "mean_seconds": 0.13,
 "pass": true,
 "settings_reported_note": "Claude Code: the init event (above).",
 "settings_sha256": "4e068c00590936e5a9e0293e1851313378c7c4ab087a24aff52d9973a32bba67"
}
```

