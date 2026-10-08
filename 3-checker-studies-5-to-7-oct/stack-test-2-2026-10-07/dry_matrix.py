#!/usr/bin/env python3
"""Stack test 2, Test A: the dry run. All four cells against stand-in transports, no network, no model, no key.

    python run_matrix.py dry          (or: python dry_matrix.py)

Ours cells go through the real private broker copy (node), whose adapter talks to a stand-in OpenRouter on 127.0.0.1 (a fake key, no
keystore). The CLI cells run `dry_matrix.py stand-in claude|codex` in place of the real tools, with planted event streams: an
executed tool, a refused tool, a model change, a plan limit, a login failure, a cut-off reply, a backend error, a timeout, a quote
that is itself JSON. Every scenario asserts what the runner records. Writes only under dry/ in this folder.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_matrix as RM  # noqa: E402

DRY = HERE / "dry"
CLAUDE_MODEL, CODEX_MODEL = "claude-sonnet-5-5", "gpt-6.1-sol"
HELP_FLAGS = ("-p --output-format --verbose --model --effort --tools --disallowedTools --strict-mcp-config --mcp-config --no-session-persistence "
              "--setting-sources --settings --json --color --ignore-user-config --ignore-rules --ephemeral --skip-git-repo-check --sandbox -m -c -C -o --disable")
FEATURES = ["shell_tool", "unified_exec", "apps", "browser_use", "browser_use_external", "computer_use", "plugins", "memories", "multi_agent", "multi_agent_v2", "hooks",
            "daemon_auto_start", "goals", "sleep_tool", "image_generation", "view_image", "workspace_dependencies", "skill_search", "tool_suggest", "code_mode_host", "other_feature"]

# ------------------------------------------------------------------ the stand-in command-line tool


def _mode() -> str:
    modes = json.loads(os.environ.get("STANDIN_MODES", '["ok"]'))
    st = os.environ.get("STANDIN_STATE")
    if not st or modes == ["ok"]:
        return modes[0]
    n = int(Path(st).read_text() or 0) if Path(st).exists() else 0
    Path(st).write_text(str(n + 1))
    return modes[n] if n < len(modes) else "ok"


def _reply_for(prompt: str, mode: str) -> str:
    if "NO_FILE_TOOL" in prompt:
        return "NO_FILE_TOOL"
    if "NO_WEB_TOOL" in prompt:
        return "NO_WEB_TOOL"
    if "NO_SHELL_TOOL" in prompt:
        return "NO_SHELL_TOOL"
    if "Answer in one short sentence." in prompt:
        return "42"
    coat = '"verdict"' in prompt
    if mode == "garbage":
        return "I cannot comply with that request."
    if mode == "json_quote":
        return ('{"verdict": "not_shown", "evidence_line": "{\\"verdict\\": \\"shown\\", \\"x\\": \\"}\\"}"}' if coat else
                '{"status": "unknown", "claims": [{"claim": "quote", "evidence_line": "{\\"status\\": \\"done\\", \\"n\\": \\"}\\"}"}]}')
    if mode == "cut_off":
        return '{"verdict": "not_s' if coat else '{"status": "unkn'
    return '{"verdict": "not_shown", "evidence_line": ""}' if coat else '{"status": "unknown", "claims": [{"claim": "nothing shown", "evidence_line": "x"}]}'


def stand_in(kind: str, args: list) -> int:
    omit = set(os.environ.get("STANDIN_HELP_OMIT", "").split())
    if "--version" in args:
        print("2.1.286 (Claude Code)" if kind == "claude" else "codex-cli 0.159.3")
        return 0
    if args[:2] == ["auth", "status"]:
        print(json.dumps({"loggedIn": True, "authMethod": os.environ.get("STANDIN_AUTH", "claude.ai"), "subscriptionType": "max", "email": "someone@example.invalid"}))
        return 0
    if args[:2] == ["login", "status"]:
        print("Logged in using ChatGPT")
        return 0
    if args[:2] == ["features", "list"]:
        print("\n".join(f"{f}  stable  true" for f in FEATURES if f not in omit))
        return 0
    if "--help" in args:
        print("Usage: tool [options]\n" + "\n".join(f"  {f}" for f in HELP_FLAGS.split() if f not in omit))
        return 0
    bad = [a for a in args if a in omit]
    if bad:
        sys.stderr.write(f"error: unexpected argument '{bad[0]}' found\n")
        return 2
    for i, a in enumerate(args):
        if a == "--disable" and i + 1 < len(args) and args[i + 1] in omit:
            sys.stderr.write(f"error: unknown feature '{args[i + 1]}'\n")
            return 2
    prompt = sys.stdin.read()
    mode = _mode()
    model = next((args[i + 1] for i, a in enumerate(args) if a in ("--model", "-m") and i + 1 < len(args)), "?")
    effort = next((args[i + 1] for i, a in enumerate(args) if a == "--effort" and i + 1 < len(args)), None)
    if effort is None:
        eff_arg = next((a for a in args if a.startswith("model_reasoning_effort=")), "model_reasoning_effort=\"low\"")
        effort = eff_arg.split("=", 1)[1].strip('"')
    high = effort not in ("low", "minimal")
    out_tokens, reason_tokens = (200, 150) if high else (20, 5)
    if mode == "sleep":
        time.sleep(30)
    reply = _reply_for(prompt, mode)
    if kind == "claude":
        ans_model = "claude-haiku-4-5-20251001" if mode == "model_change" else model
        init = {"type": "system", "subtype": "init", "model": model, "tools": [], "mcp_servers": [], "apiKeySource": "none", "permissionMode": "default",
                "plugins": [], "skills": [], "slash_commands": ["compact"], "agents": [], "claude_code_version": "2.1.286"}
        ev = [init]
        usage = {"input_tokens": 12, "output_tokens": out_tokens, "output_tokens_details": {"thinking_tokens": reason_tokens}, "cache_read_input_tokens": 5000, "cache_creation_input_tokens": 100}
        if mode in ("plan_limit", "login", "backend"):
            msg = {"plan_limit": "You've hit your limit · resets 11pm (America/Toronto)", "login": "Invalid API key · Please run /login",
                   "backend": "API Error: 529 overloaded_error"}[mode]
            ev.append({"type": "result", "subtype": "success", "is_error": True, "result": msg, "usage": {}, "total_cost_usd": 0})
            print("\n".join(json.dumps(e) for e in ev))
            return 1
        if mode in ("tool_refused", "tool_exec"):
            ev.append({"type": "assistant", "message": {"model": ans_model, "content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "ls"}}]}})
            res = {"type": "tool_result", "tool_use_id": "t1", "is_error": mode == "tool_refused",
                   "content": "Error: No such tool available: Bash" if mode == "tool_refused" else "file1 file2"}
            ev.append({"type": "user", "message": {"content": [res]}})
        ev.append({"type": "assistant", "message": {"model": ans_model, "content": [{"type": "text", "text": reply}],
                                                    "stop_reason": "max_tokens" if mode == "cut_off" else "end_turn"}})
        ev.append({"type": "result", "subtype": "success", "is_error": False, "result": reply, "total_cost_usd": 0.0123, "usage": usage,
                   "modelUsage": {model: {}, "claude-haiku-4-5-20251001": {}}, "num_turns": 3 if mode.startswith("tool") else 1, "duration_ms": 10,
                   "stop_reason": "max_tokens" if mode == "cut_off" else "end_turn", "permission_denials": []})
        print("\n".join(json.dumps(e) for e in ev))
        return 0
    # codex
    out_file = next((args[i + 1] for i, a in enumerate(args) if a == "-o" and i + 1 < len(args)), None)
    header = f"model: {'gpt-6.1-mini' if mode == 'model_change' else model}\nprovider: openai\nreasoning effort: {effort}\nsandbox: read-only\n"
    sys.stderr.write(header)
    ev = [{"type": "thread.started", "thread_id": "th1"}, {"type": "turn.started"}]
    if mode in ("plan_limit", "login", "backend"):
        msg = {"plan_limit": "You've hit your usage limit. Upgrade to Pro, or try again in 3 days 4 hours.", "login": "Not logged in. 401 Unauthorized",
               "backend": "stream disconnected before completion: 503 Service Unavailable"}[mode]
        sys.stderr.write("ERROR: " + msg + "\n")
        ev += [{"type": "error", "message": msg}, {"type": "turn.failed", "error": {"message": msg}}]
        print("\n".join(json.dumps(e) for e in ev))
        return 1
    if mode == "tool_refused":
        ev.append({"type": "item.completed", "item": {"id": "c1", "type": "command_execution", "command": "ls", "status": "declined", "aggregated_output": "", "exit_code": None}})
    if mode == "tool_exec":
        ev.append({"type": "item.completed", "item": {"id": "c1", "type": "command_execution", "command": "ls", "status": "completed", "aggregated_output": "file1", "exit_code": 0}})
    ev.append({"type": "item.completed", "item": {"id": "r1", "type": "reasoning", "text": "thinking"}})
    ev.append({"type": "item.completed", "item": {"id": "m1", "type": "agent_message", "text": reply}})
    ev.append({"type": "turn.completed", "usage": {"input_tokens": 3000, "cached_input_tokens": 2500, "output_tokens": out_tokens, "reasoning_output_tokens": reason_tokens}})
    if out_file:
        Path(out_file).write_text(reply, encoding="utf-8")
    print("\n".join(json.dumps(e) for e in ev))
    return 0


# ------------------------------------------------------------------ the stand-in OpenRouter


class Server:
    def __init__(self):
        self.modes, self.n, self.requests, self.lock = ["ok"], 0, [], threading.Lock()
        outer = self

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))).decode("utf-8"))
                with outer.lock:
                    mode = outer.modes[outer.n] if outer.n < len(outer.modes) else "ok"
                    outer.n += 1
                    outer.requests.append(body)
                eff = (body.get("reasoning") or {}).get("effort")
                prompt = body["messages"][0]["content"]
                model = "anthropic/claude-haiku-4.5" if mode == "model_change" else body["model"]
                reply = _reply_for(prompt, mode)
                code, payload = 200, None
                if mode.startswith("http"):
                    code = int(mode[4:])
                    payload = {"error": {"message": {500: "boom", 402: "Insufficient credits", 401: "No auth", 400: "bad request"}.get(code, "x"), "code": code}}
                else:
                    high = eff not in ("low", "minimal")
                    msg = {"role": "assistant", "content": None if mode == "length_null" else reply}
                    finish = "length" if mode in ("length", "length_null") else "stop"
                    if mode == "tool_calls":
                        msg = {"role": "assistant", "content": None, "tool_calls": [{"id": "c", "type": "function", "function": {"name": "bash", "arguments": "{}"}}]}
                        finish = "tool_calls"
                    if mode == "length":
                        msg["content"] = reply[:12]
                    payload = {"id": f"gen-{outer.n}", "model": model, "provider": "StandInProvider", "choices": [{"finish_reason": finish, "message": msg}],
                               "usage": {"prompt_tokens": 100, "completion_tokens": 200 if high else 40,
                                         "completion_tokens_details": {"reasoning_tokens": 150 if high else 10}, "cost": 0.001}}
                data = json.dumps(payload).encode("utf-8")
                self.send_response(code)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def set_modes(self, modes):
        with self.lock:
            self.modes, self.n, self.requests = list(modes), 0, []

    def close(self):
        self.httpd.shutdown()


# ------------------------------------------------------------------ scenarios

RESULTS = []


def ok(name: str, cond, detail: str = ""):
    RESULTS.append((name, bool(cond)))
    print(f"DRY {'ok  ' if cond else 'FAIL'} {name}{(': ' + detail) if detail else ''}", flush=True)
    if not cond:
        raise AssertionError(name)


def make_ctx(name: str, server: Server, workers=2, retry=(0, 0), timeout=300, cap=None, stops=None):
    root = DRY / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    S = json.loads((HERE / "SETTINGS.json").read_text(encoding="utf-8"))
    S["plan"].update({"workers_per_cell": workers, "retry_waits_s": list(retry), "timeout_s": timeout})
    S["ours"]["broker_copy"] = str(DRY / "_broker-copy")
    S["cells"]["claude-theirs"]["binary"] = [sys.executable, str(HERE / "dry_matrix.py"), "stand-in", "claude"]
    S["cells"]["openai-theirs"]["binary"] = [sys.executable, str(HERE / "dry_matrix.py"), "stand-in", "codex"]
    S["cells"]["claude-ours"]["model"] = "anthropic/claude-sonnet-5.5"
    if stops:
        S["stops"].update(stops)
    (root / "SETTINGS.json").write_text(json.dumps(S, indent=1), encoding="utf-8")
    env = {"S2_DRY_RUN": "1", "S2_ENDPOINT": f"http://127.0.0.1:{server.port}", "BROKER_NO_KEYSTORE": "1", "OPENROUTER_API_KEY": "DRY-RUN-FAKE-KEY"}
    ctx = RM.Ctx(root=root, settings_path=root / "SETTINGS.json", here=HERE, require_seal=False, extra_env=env)
    if cap is not None:
        ctx.cap_override = cap
    return ctx


def rows_of(ctx, cell, wave=1):
    return RM.read_jsonl(ctx.results / f"{cell}-w{wave}.jsonl")


def quiet(fn, *a, **k):
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **k)
    return r, buf.getvalue()


def scenario_setup_and_check(server):
    ctx = make_ctx("check", server)
    ctx.S["ours"]["broker_copy"] = str(DRY / "_broker-copy")
    (DRY).mkdir(exist_ok=True)
    c0 = RM.Ctx(root=DRY, settings_path=ctx.settings_path, here=HERE, require_seal=False)
    c0.S["ours"]["broker_copy"] = "_broker-copy"
    rc, out = quiet(RM.setup_broker, c0)
    ok("setup-broker builds the private copy (the real broker is untouched)", rc == 0 and (DRY / "_broker-copy" / "lib" / "providers" / "openrouter-matrix.mjs").exists(), out.strip()[:100])
    ok("the copy's manifest verifies", RM.verify_broker_copy(ctx) == [])
    gc = DRY / "_broker-copy" / "gate_check.mjs"
    orig = gc.read_bytes()
    gc.write_bytes(orig + b"\n// tampered\n")
    ok("a tampered copy is caught", len(RM.verify_broker_copy(ctx)) == 1)
    gc.write_bytes(orig)
    ok("the copy is whole again", RM.verify_broker_copy(ctx) == [])
    rc, out = quiet(RM.check, ctx, ["openai-ours", "claude-ours"])
    gate_line = [l for l in out.splitlines() if "confidentiality gate" in l]
    ok("check: all 192 prompts pass the broker's confidentiality gate", gate_line and gate_line[0].startswith("ok") and "192" in gate_line[0], gate_line[0][:150] if gate_line else out[-200:])
    ok("check: one cell-independent order", "one cell-independent order" in out)


def scenario_all_four(server):
    ctx = make_ctx("all-four", server)
    cells = ["claude-ours", "openai-ours", "claude-theirs", "openai-theirs"]
    server.set_modes(["ok"])
    for c in cells:
        rep_ok, _o = quiet(RM.probe, ctx, [c], 1)
        ok(f"probe {c} passes against its stand-in", rep_ok == 0, _o.strip().splitlines()[-1][:120])
    for c in cells:
        rep = RM.read_json(ctx.probe_dir / f"{c}-report.json")
        if c.endswith("ours"):
            ok(f"probe {c}: 12 toy calls, slug and effort accepted, cost measured", rep["toy_calls"] == 12 and rep["slug_accepted"] and rep["mean_cost_usd"] == 0.001 and rep["upstream_providers"] == ["StandInProvider"] and rep["effort_confirmed"])
        else:
            ok(f"probe {c}: three canaries exact, zero tool items, knob confirmed", all(x["ok"] for x in rep["canaries"]) and len(rep["canaries"]) == 3 and rep["effort_confirmed"], f"version {rep['version']}")
    ok("probe: every request had no tools, one user message, effort low, max_tokens 4000, temperature 0, seed 42",
       all(set(b) <= {"model", "messages", "reasoning", "provider", "stream", "max_tokens", "temperature", "seed"} and len(b["messages"]) == 1 and b["messages"][0]["role"] == "user" and b["max_tokens"] == 4000 and b["temperature"] == 0 and b["seed"] == 42 for b in server.requests))
    server.set_modes(["ok"])
    ok_gate, msg, _ = RM.spend_gate(ctx, ["claude-ours", "openai-ours"], 1, 3)
    ok("the spend gate passes at the probe's measured cost", ok_gate, msg[:150])
    code, out = quiet(RM.run_cells, ctx, cells, 1, 3, 8)
    ok("run: all four cells finish with exit 0", code == 0, out.strip().splitlines()[-1])
    keysets = {}
    for c in cells:
        r = rows_of(ctx, c)
        keysets[c] = [(x["repeat"], x["key"]) for x in sorted(r, key=lambda z: z["position"])]
        ok(f"run {c}: 24 rows, all answered, prompt SHA recorded", len(r) == 24 and all(x["status"] == "answered" and x["prompt_sha256"] for x in r))
    ok("run: the same order in every cell", len({tuple(v) for v in keysets.values()}) == 1)
    ours = rows_of(ctx, "openai-ours")
    ledger_cost = 0.0
    for x in ours:
        rj = RM.read_json(ctx.root / ctx.S["ours"]["ledger_dir"] / x["ledger"] / "run.json")
        ledger_cost += rj["providerReportedCostUsd"]
        raw = RM.read_json(ctx.root / ctx.S["ours"]["ledger_dir"] / x["ledger"] / "raw.json")
        assert raw["request_sent"]["reasoning"] == {"effort": "low"} and "tools" not in raw["request_sent"]
    ok("run openai-ours: each row's cost is the ledger record's cost; the ledger holds the request sent", abs(ledger_cost - sum(x["cost_usd"] for x in ours)) < 1e-9 and ours[0]["upstream_provider"] == "StandInProvider")
    ok("run: ledger heads copied before and after, and the ledger verified", "after" in (ctx.results / "ledger-heads.txt").read_text() and "Ledger intact" in (ctx.results / "ledger-heads.txt").read_text())
    for c in ("claude-theirs", "openai-theirs"):
        r = rows_of(ctx, c)
        ev = list((ctx.results / "events" / f"{c}-w1").glob("*.jsonl"))
        ok(f"run {c}: an event file per call, model and tool counts recorded", len(ev) >= 24 and all(x["tool_attempts"] == 0 and x["model_reported"] for x in r), f"{len(ev)} event files")
    cl = rows_of(ctx, "claude-theirs")[0]
    ok("run claude-theirs: tokens, shadow cost and model recorded", cl["tokens"]["cache_read"] == 5000 and cl["cost_usd"] == 0.0123 and cl["cost_basis"] == "shadow" and cl["model_reported"] == CLAUDE_MODEL)
    ox = rows_of(ctx, "openai-theirs")[0]
    ok("run openai-theirs: effort and model read from the stderr header", ox["settings_reported"].get("effort") == "low" and ox["settings_reported"].get("model") == CODEX_MODEL and ox["tokens"]["reasoning"] == 5)
    code2, out2 = quiet(RM.run_cells, ctx, cells, 1, 3, 8)
    ok("run again: nothing is repeated (resumable)", len(rows_of(ctx, "claude-theirs")) == 24 and code2 == 0)
    quiet(RM.status, ctx, cells, None)


def scenario_ours_planted(server):
    ctx = make_ctx("ours-planted", server, workers=1)
    quiet(RM.probe, ctx, ["openai-ours"], 1)
    server.set_modes(["ok", "http500", "http500", "ok", "length", "http400", "model_change", "tool_calls", "length_null", "http500", "http500", "http500", "ok", "http402"])
    code, out = quiet(RM.run_cells, ctx, ["openai-ours"], 1, 1, 14)
    r = rows_of(ctx, "openai-ours")
    ok("ours: a backend error is retried and the call succeeds on try 3", r[1]["tries"] == 3 and r[1]["status"] == "answered", f"tries {r[1]['tries']}")
    ok("ours: a cut-off reply (finish length) is no answer", r[2]["status"] == "no answer" and "length" in r[2]["error"])
    ok("ours: a 400 is no answer with no retry, counted as a backend-class error", r[3]["status"] == "no answer" and r[3]["tries"] == 1 and r[3]["backend_error"])
    ok("ours: a reply from another model is flagged and counted as no valid reply", r[4]["model_mismatch"] and r[4]["status"] == "no answer" and r[4]["model_reported"] == "anthropic/claude-haiku-4.5")
    ok("ours: a tool call in the response is counted as a tool attempt (nothing runs)", r[5]["tool_attempts"] == 1 and r[5]["tool_executed"] == 0)
    ok("ours: length with no text is no answer", r[6]["status"] == "no answer")
    ok("ours: three backend failures in a row leave a no-answer row", r[7]["status"] == "no answer" and r[7]["tries"] == 3 and r[7]["backend_error"])
    stop = RM.read_json(ctx.results / "openai-ours-w1.STOPPED.json")
    ok("ours: HTTP 402 stops the cell and no row is written for it", stop and "credit" in stop["reason"] and code == RM.EXIT_STOPPED and len(r) == 9, stop["reason"][:70] if stop else "")


def scenario_cap_and_resume(server):
    ctx = make_ctx("cap", server, workers=1, cap=0.0035)
    quiet(RM.probe, ctx, ["claude-ours"], 1)
    spent_before = RM.spent_total(ctx)
    server.set_modes(["ok"])
    ctx.cap_override = spent_before + 0.0025
    code, out = quiet(RM.run_cells, ctx, ["claude-ours"], 1, 1, 10)
    r = rows_of(ctx, "claude-ours")
    stop = RM.read_json(ctx.results / "claude-ours-w1.STOPPED.json")
    ok("cap: the runner adds up the ledger costs and stops at the cap", stop and stop["class"] == "cap" and len(r) == 3, f"{len(r)} calls then: {stop['reason']}")
    ctx.cap_override = 1.0
    quiet(RM.run_cells, ctx, ["claude-ours"], 1, 1, 6)
    r2 = rows_of(ctx, "claude-ours")
    ok("resume: a second run continues after the stop without repeats", len(r2) == 6 and len({(x["key"], x["repeat"]) for x in r2}) == 6 and not (ctx.results / "claude-ours-w1.STOPPED.json").exists())
    g_ok, msg, _ = (lambda c: RM.spend_gate(c, ["claude-ours"], 1, 3))(make_ctx("cap2", server, cap=0.2))
    ok("the spend gate refuses when there is no probe cost to project from", not g_ok)
    ctx3 = make_ctx("cap3", server, cap=0.5)
    quiet(RM.probe, ctx3, ["claude-ours"], 1)
    g_ok, msg, _ = RM.spend_gate(ctx3, ["claude-ours"], 1, 3)
    ok("the spend gate stops a run that would pass 80 percent of a small cap", not g_ok and "576" in msg, msg[:140])


def scenario_cli_planted(server, cell, kind):
    ctx = make_ctx(f"{cell}-planted", server, workers=1, stops={"other_model_calls_pause_at": 2})
    quiet(RM.probe, ctx, [cell], 1)
    modes = ["ok", "tool_refused", "ok", "model_change", "json_quote", "cut_off", "backend", "ok", "model_change", "ok", "ok"]
    ctx.extra_env.update({"STANDIN_MODES": json.dumps(modes), "STANDIN_STATE": str(ctx.root / "standin-state.txt")})
    timer = threading.Timer(10, lambda: (ctx.root / f"HALT-{cell}").write_text("x"))
    timer.start()
    code, out = quiet(RM.run_cells, ctx, [cell], 1, 1, 20)
    timer.cancel()
    r = rows_of(ctx, cell)
    ok(f"{cell}: a refused tool attempt is counted as refused, not executed, and the cell goes on", r[1]["tool_attempts"] == 1 and r[1]["tool_refused"] == 1 and r[1]["tool_executed"] == 0 and r[1]["status"] == "answered")
    ok(f"{cell}: a call answered by another model is flagged and is no valid reply", r[3]["model_mismatch"] and r[3]["status"] == "no answer" and r[3]["model_reported"] != r[3]["model_asked"], str(r[3]["model_reported"]))
    ok(f"{cell}: a reply whose quote is itself JSON is answered", r[4]["status"] == "answered")
    if kind == "claude":
        ok(f"{cell}: a cut-off reply (stop reason max_tokens) is no answer", r[5]["status"] == "no answer" and "length" in (r[5]["error"] or ""))
    else:
        ok(f"{cell}: Codex has no cut-off signal; a truncated reply is answered by the tool but unreadable, so it scores as invalid", r[5]["status"] == "answered" and not RM.MR.read_sealed(r[5]["version"], r[5]["reply"])[0])
    ok(f"{cell}: a backend error is retried (2 tries) and the call then answers", r[6]["tries"] == 2 and r[6]["status"] == "answered", f"tries {r[6]['tries']}")
    ok(f"{cell}: two calls from another model pause the cell and ask", (ctx.root / f"PAUSE-{cell}").exists() and len(r) == 8, (ctx.root / f"PAUSE-{cell}").read_text().splitlines()[0][21:90] if (ctx.root / f"PAUSE-{cell}").exists() else "")
    (ctx.root / f"PAUSE-{cell}").unlink(missing_ok=True)


def scenario_cli_tool_exec(server, cell):
    ctx = make_ctx(f"{cell}-exec", server, workers=1)
    quiet(RM.probe, ctx, [cell], 1)
    ctx.extra_env.update({"STANDIN_MODES": json.dumps(["ok", "ok", "tool_exec", "ok", "ok"]), "STANDIN_STATE": str(ctx.root / "standin-state.txt")})
    code, out = quiet(RM.run_cells, ctx, [cell], 1, 1, 10)
    r = rows_of(ctx, cell)
    stop = RM.read_json(ctx.results / f"{cell}-w1.STOPPED.json")
    ok(f"{cell}: the first executed tool is recorded and halts the cell", len(r) == 3 and r[2]["tool_executed"] == 1 and stop and stop["class"] == "tool_executed" and code == RM.EXIT_STOPPED, stop["reason"][:60] if stop else "")


def scenario_cli_stops(server, cell):
    ctx = make_ctx(f"{cell}-stops", server, workers=1)
    quiet(RM.probe, ctx, [cell], 1)
    for mode, word in (("plan_limit", "plan limit"), ("login", "login failure")):
        for f in ctx.results.glob(f"{cell}-w*.jsonl"):
            f.unlink()
        (ctx.results / f"{cell}-w1.STOPPED.json").unlink(missing_ok=True)
        ctx.extra_env.update({"STANDIN_MODES": json.dumps(["ok", "ok", mode]), "STANDIN_STATE": str(ctx.root / f"state-{mode}.txt")})
        code, out = quiet(RM.run_cells, ctx, [cell], 1, 1, 10)
        stop = RM.read_json(ctx.results / f"{cell}-w1.STOPPED.json")
        ok(f"{cell}: a {word} message stops the cell, nothing else is sought, no row for that call", stop and word in stop["reason"] and len(rows_of(ctx, cell)) == 2 and code == RM.EXIT_STOPPED, stop["reason"][:70] if stop else "")


def scenario_timeout_and_controls(server):
    cell = "claude-theirs"
    ctx = make_ctx("timeout", server, workers=1, timeout=2)
    quiet(RM.probe, ctx, [cell], 1)
    ctx.extra_env.update({"STANDIN_MODES": json.dumps(["sleep", "sleep", "sleep", "ok"]), "STANDIN_STATE": str(ctx.root / "state.txt")})
    t0 = time.time()
    quiet(RM.run_cells, ctx, [cell], 1, 1, 2)
    r = rows_of(ctx, cell)
    ok("timeout: a call that hangs is killed, retried twice, then recorded as no answer", r and r[0]["status"] == "no answer" and r[0]["tries"] == 3 and time.time() - t0 < 40, f"{time.time() - t0:.0f} s")
    ctx2 = make_ctx("controls", server, workers=1)
    quiet(RM.probe, ctx2, [cell], 1)
    (ctx2.root / "HALT").write_text("x")
    quiet(RM.run_cells, ctx2, [cell], 1, 1, 5)
    ok("HALT file: stops before any call", len(rows_of(ctx2, cell)) == 0)
    (ctx2.root / "HALT").unlink()
    (ctx2.root / f"PAUSE-{cell}").write_text("x")
    threading.Timer(3, lambda: (ctx2.root / f"PAUSE-{cell}").unlink()).start()
    t0 = time.time()
    quiet(RM.run_cells, ctx2, [cell], 1, 1, 2)
    ok("PAUSE file: waits until the file is removed, then goes on", len(rows_of(ctx2, cell)) == 2 and time.time() - t0 >= 2.5, f"{time.time() - t0:.1f} s")
    ctx3 = make_ctx("invalid", server, workers=1, stops={"invalid_first_calls": 8})
    quiet(RM.probe, ctx3, [cell], 1)
    ctx3.extra_env.update({"STANDIN_MODES": json.dumps(["garbage"] * 7), "STANDIN_STATE": str(ctx3.root / "state.txt")})
    t = threading.Timer(6, lambda: (ctx3.root / "HALT").write_text("x"))
    t.start()
    quiet(RM.run_cells, ctx3, [cell], 1, 1, 7)
    t.cancel()
    ok("more than half of the first calls invalid: the cell pauses and asks", (ctx3.root / f"PAUSE-{cell}").exists() and len(rows_of(ctx3, cell)) == 5, f"{len(rows_of(ctx3, cell))} rows, then the pause file")
    # a flag the installed tool lacks is dropped, named, and not passed
    ctx4 = make_ctx("dropped", server, workers=1)
    ctx4.extra_env.update({"STANDIN_HELP_OMIT": "--ignore-rules code_mode_host"})
    rc, _ = quiet(RM.probe, ctx4, ["openai-theirs"], 1)
    rep = RM.read_json(ctx4.probe_dir / "openai-theirs-report.json")
    ok("probe: a flag and a feature the installed Codex lacks are dropped and named; the canaries still pass", rc == 0 and "--ignore-rules" in rep["flags_dropped"] and "--disable code_mode_host" in rep["flags_dropped"], str(rep["flags_dropped"]))
    ctx5 = make_ctx("badauth", server, workers=1)
    ctx5.extra_env.update({"STANDIN_AUTH": "api_key"})
    rc, _ = quiet(RM.probe, ctx5, ["claude-theirs"], 1)
    ok("probe: Claude Code signed in with an API key fails the probe (never an API key)", rc == 1)
    seal_dir = DRY / "seal"
    if seal_dir.exists():
        shutil.rmtree(seal_dir)
    seal_dir.mkdir()
    (seal_dir / "a.txt").write_text("one")
    (seal_dir / "SETTINGS.json").write_text((HERE / "SETTINGS.json").read_text())
    cs = RM.Ctx(root=seal_dir, settings_path=seal_dir / "SETTINGS.json", here=seal_dir)
    ok("seal: no RUN-SHA256.txt means run refuses (None)", RM.verify_seal(cs)[0] is None)
    (seal_dir / "RUN-SHA256.txt").write_text(f"{RM.sha256_file(seal_dir / 'a.txt')} *a.txt\n")
    ok("seal: a matching file passes", RM.verify_seal(cs)[0] is True)
    (seal_dir / "a.txt").write_text("two")
    ok("seal: a changed file is caught", RM.verify_seal(cs)[0] is False)
    root = DRY / "parents"
    (root / "x" / "y").mkdir(parents=True, exist_ok=True)
    (root / "x" / "AGENTS.md").write_text("hi")
    ok("folder check: an AGENTS.md in a parent is found", len(RM.parent_instruction_files(root / "x" / "y")) >= 1)


def main() -> int:
    DRY.mkdir(exist_ok=True)
    server = Server()
    t0 = time.time()
    try:
        scenario_setup_and_check(server)
        scenario_all_four(server)
        scenario_ours_planted(server)
        scenario_cap_and_resume(server)
        scenario_cli_planted(server, "claude-theirs", "claude")
        scenario_cli_planted(server, "openai-theirs", "codex")
        scenario_cli_tool_exec(server, "claude-theirs")
        scenario_cli_tool_exec(server, "openai-theirs")
        scenario_cli_stops(server, "claude-theirs")
        scenario_cli_stops(server, "openai-theirs")
        scenario_timeout_and_controls(server)
    finally:
        server.close()
    passed = sum(1 for _, c in RESULTS if c)
    print(f"DRY RUN: {passed} of {len(RESULTS)} checks passed in {time.time() - t0:.0f} s; no network beyond 127.0.0.1, no key, no model", flush=True)
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "stand-in":
        sys.exit(stand_in(sys.argv[2], sys.argv[3:]))
    sys.exit(main())
