#!/usr/bin/env python3
"""Stack test 2, Test A ("the two harnesses"): the runner for the four cells. Design: DESIGN-A.md and RUN-PLAN.md (sealed 7 Oct 2026).

    python run_matrix.py check   [--cells A,B]          inputs, seal, order, gate, folders, orphans; no model call
    python run_matrix.py setup-broker                   build the private broker copy that sends S12's request body (no model call)
    python run_matrix.py probe   --cells A,B [--wave N] toy calls (ours) or version, sign-in, 3 canaries, knob check (CLI cells)
    python run_matrix.py probe-report                   rebuild results/probe/PROBE-REPORT.md from every <cell>-report.json present
    python run_matrix.py run     --cells A,B --wave N [--repeats 3] [--cap-usd X]
    python run_matrix.py status  [--cells A,B] [--wave N]
    python run_matrix.py stop-orphans                   list and stop leftover runner, broker and tool processes
    python run_matrix.py dry                            all four cells against stand-in transports (dry_matrix.py), no network

Cells: claude-ours, openai-ours (the AI broker, OpenRouter, one user message, no tools), openai-theirs (Codex exec, in the box),
claude-theirs (Claude Code print mode, in the box). 192 prompts x 3 repeats = 576 calls per cell, 2 at a time per cell, the same
order in every cell. Resumable: a recorded call is skipped. Control files in the run folder: PAUSE or PAUSE-<cell> pauses between
calls, HALT or HALT-<cell> stops after the current call. The console shows progress only, never a reply.
Standard library only (Python 3.10). Nothing here reads, prints or stores a key.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import os
import queue
import random
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matrix_reader as MR  # noqa: E402

os.environ["PATH"] = str(Path.home() / ".local" / "bin") + os.pathsep + os.environ.get("PATH", "")

EXIT_FINISHED, EXIT_STOPPED, EXIT_HALTED, EXIT_USAGE = 0, 10, 11, 2

# ---------------------------------------------------------------- small helpers


def utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(msg: str) -> None:
    print(f"{time.strftime('%H:%M:%S', time.gmtime())} {msg}", flush=True)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(Path(p).read_bytes())


def safe_name(key: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", key.replace("|", "__"))


def read_json(p: Path):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return None


def read_jsonl(p: Path) -> list:
    p = Path(p)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


class Ctx:
    """Where things are. `here` holds the sealed inputs; `root` holds everything the run writes (the same folder in a real run)."""

    def __init__(self, root=None, settings_path=None, here=None, require_seal=True, extra_env=None):
        self.here = Path(here or HERE)
        self.root = Path(root or self.here)
        self.settings_path = Path(settings_path or (self.here / "SETTINGS.json"))
        self.S = json.loads(self.settings_path.read_text(encoding="utf-8"))
        self.settings_sha = sha256_bytes(self.settings_path.read_bytes())
        self.results = self.root / "results"
        self.probe_dir = self.results / "probe"
        self.require_seal = require_seal
        self.extra_env = dict(extra_env or {})
        self.cap_override = None

    def cell_names(self) -> list:
        return list(self.S["cells"])

    def cap(self) -> float:
        return float(self.cap_override if self.cap_override is not None else self.S["spend"]["cap_usd"])


# ---------------------------------------------------------------- seal, inputs, plan


def read_sha_list(path: Path) -> list:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([0-9a-fA-F]{64})\s+[* ]?(.+?)\s*$", line)
        if m:
            out.append((m.group(1).lower(), m.group(2)))
    return out


def verify_seal(ctx: Ctx):
    """(ok or None when there is no seal file, problems)."""
    f = ctx.here / "RUN-SHA256.txt"
    if not f.exists():
        return None, ["RUN-SHA256.txt is absent (nothing sealed yet)"]
    problems = []
    for sha, rel in read_sha_list(f):
        p = ctx.here / rel
        if not p.exists():
            problems.append(f"{rel}: missing")
        elif sha256_file(p) != sha:
            problems.append(f"{rel}: differs from its seal")
    return (not problems), problems


def load_prompt_rows(ctx: Ctx) -> list:
    inp = ctx.S["inputs"]
    raw = (ctx.here / inp["prompts"]).read_bytes()
    if sha256_bytes(raw) != inp["prompts_sha256"]:
        raise SystemExit("STOP: prompts.jsonl does not match its sealed SHA-256. Nothing was run.")
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
    assert len(rows) == inp["prompt_rows"] and len({r["key"] for r in rows}) == len(rows)
    for r in rows:
        assert sha256_bytes(r["prompt"].encode("utf-8")) == r["sha256"], r["key"]
    sel = sorted((r for r in rows if r["version"] in inp["versions"]), key=lambda r: r["key"])
    assert len(sel) == inp["selected_rows"], len(sel)
    by_log = {}
    for r in sel:
        by_log.setdefault(r["log"], set()).add(r["version"])
    assert len(by_log) == inp["selected_rows"] // len(inp["versions"]) and all(v == set(inp["versions"]) for v in by_log.values())
    return sel


def plan_items(ctx: Ctx, rows: list) -> list:
    """[(row, repeat, position)]: repeat by repeat, each repeat the keys (sorted) in Random(seed_base + repeat) order."""
    plan = ctx.S["plan"]
    items, pos = [], 0
    for rep in range(1, plan["repeats"] + 1):
        order = sorted(rows, key=lambda r: r["key"])
        random.Random(plan["order_seed_base"] + rep).shuffle(order)
        for r in order:
            pos += 1
            items.append((r, rep, pos))
    return items


def order_fingerprint(items: list) -> str:
    return sha256_bytes("\n".join(f"{rep}|{r['key']}" for r, rep, _ in items).encode("utf-8"))


TRUTH_RE = re.compile(r"\bt\d{2}-(pass|fail|absent)\b", re.I)

# ---------------------------------------------------------------- processes


def kill_tree(p: subprocess.Popen) -> None:
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True, timeout=30)
        else:
            os.killpg(p.pid, signal.SIGKILL)
    except Exception:
        pass
    try:
        p.kill()
    except Exception:
        pass


def run_process(argv, input_bytes, cwd, env, timeout):
    """(returncode or None on timeout, stdout bytes, stderr bytes, timed_out). No shell. The prompt goes on a pipe the runner owns,
    then the pipe is closed; with no input, standard input is the null device (never an inherited one: S13's lesson)."""
    kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    try:
        p = subprocess.Popen(argv, stdin=subprocess.PIPE if input_bytes is not None else subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(cwd), env=env, **kw)
    except OSError as e:
        return 127, b"", f"cannot start {argv[0]}: {e}".encode("utf-8"), False
    try:
        out, err = p.communicate(input=input_bytes, timeout=timeout)
        return p.returncode, out, err, False
    except subprocess.TimeoutExpired:
        kill_tree(p)
        try:
            out, err = p.communicate(timeout=15)
        except Exception:
            out, err = b"", b""
        return None, out or b"", err or b"", True


def allowed_env(ctx: Ctx, extra_names=()) -> dict:
    allow = set(ctx.S["env_allow"]) | set(extra_names)
    up = {a.upper() for a in allow}
    return {k: v for k, v in os.environ.items() if k in allow or (os.name == "nt" and k.upper() in up)}


def find_orphans(cells=None):
    """(ours, foreign). `ours`: another runner of the same cell(s) (all runners when `cells` is None) and, when no runner is alive at
    all, leftover broker-copy calls and tool calls in our empty folders; a runner of other cells is a legitimate neighbour and is
    left alone. `foreign`: other agent-tool calls that are not ours (listed so they are seen, never stopped here)."""
    runner = re.compile(r"run_matrix\.py run\b")
    leftover = re.compile(r"(broker-copy[\\/]broker\.mjs run|empty-(claude|openai)-(ours|theirs)-\d|disableAllHooks)")
    other = re.compile(r"(codex exec|claude -p|claude .*--output-format stream-json)")
    me = {os.getpid(), os.getppid()}
    runners, left, foreign = [], [], []
    try:
        if os.name == "nt":
            ps = "Get-CimInstance Win32_Process | ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }"
            out = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=90).stdout
            lines = out.splitlines()
        else:
            out = subprocess.run(["ps", "-eo", "pid,args"], capture_output=True, text=True, timeout=30).stdout
            lines = out.splitlines()[1:]
        for line in lines:
            m = re.match(r"\s*(\d+)\s+(.*)$", line.replace(chr(9), " "))
            if not m or int(m.group(1)) in me or "Get-CimInstance" in m.group(2):
                continue
            pid, args = int(m.group(1)), m.group(2)
            if re.search(r"run_matrix\.py (check|status|stop-orphans|probe|dry|setup-broker)", args):
                continue
            if runner.search(args) and "python" in args.lower():
                runners.append((pid, args[:160]))
            elif leftover.search(args):
                left.append((pid, args[:160]))
            elif other.search(args):
                foreign.append((pid, args[:160]))
    except Exception as e:  # listing is best effort
        foreign.append((0, f"(could not list processes: {e})"))
    def overlaps(args):
        m = re.search(r"--cells[ =]+(\S+)", args)
        mine = set(cells or [])
        return cells is None or not m or bool(mine & set(m.group(1).split(",")))
    ours = [(p, a) for p, a in runners if overlaps(a)]
    if not runners:
        ours += left
    return ours, foreign


# ---------------------------------------------------------------- reading what a call returned

PLAN_LIMIT_RE = re.compile(r"(usage limit|limit reached|hit your (usage |weekly |monthly )?limit|you.{0,3}ve (hit|reached) (your|the) [a-z0-9 -]{0,30}limit|5-hour limit|weekly limit|monthly limit|quota (exceeded|reached)|out of (usage|credits|messages)|upgrade (to|your) (pro|plus|max)|plan limit|credit balance is too low|exceeded your current quota|insufficient[_ ](quota|credits))", re.I)
LOGIN_RE = re.compile(r"(not logged in|please run /?login|run /login|run `?codex login|invalid api key|authentication[_ ](failed|error|required)|unauthori[sz]ed|\b401\b|oauth token.{0,20}(expired|revoked|invalid)|sign in again|log ?in again|please (sign|log) ?in|token.{0,30}(expired|could not be refreshed|revoked)|refresh token|logged out)", re.I)
BACKEND_RE = re.compile(r"(overloaded|temporarily unavailable|stream (disconnected|error|closed)|connection (reset|refused|closed|error)|econnreset|etimedout|socket hang up|timed? ?out|\b50[0234]\b|\b529\b|internal server error|bad gateway|service unavailable|gateway timeout|reconnecting|try again later|rate.?limit|\b429\b|too many requests)", re.I)
REFUSAL_RE = re.compile(r"(no such tool|not (available|found|allowed|enabled)|permission|denied|disallowed|disabled|blocked|unknown tool|isn't available|can.?t use|cannot use|requires approval|unavailable|declined|rejected)", re.I)


def classify_diag(text: str):
    """'plan_limit' | 'login' | 'backend' | None, from error text only (never from a model's reply)."""
    if not text:
        return None
    if PLAN_LIMIT_RE.search(text):
        return "plan_limit"
    if LOGIN_RE.search(text):
        return "login"
    if BACKEND_RE.search(text):
        return "backend"
    return None


def parse_jsonl_text(text: str):
    events, bad = [], 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            events.append(json.loads(s))
        except json.JSONDecodeError:
            bad += 1
    return events, bad


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return str(content or "")


def model_ok(asked: str, reported, accept) -> bool:
    if not reported:
        return True  # nothing reported: not a mismatch (recorded as None)
    if reported == asked or any(reported == a for a in (accept or [])):
        return True
    return any(reported.startswith(asked + sep) for sep in ("-", ":", "@", "[", "/"))


def analyze_claude(stdout_text: str, stderr_text: str, rc, asked: str, accept=None) -> dict:
    """Claude Code print mode, stream-json events -> what the runner records."""
    ev, bad = parse_jsonl_text(stdout_text)
    init = next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), None) or {}
    result = None
    for e in ev:
        if e.get("type") == "result":
            result = e
    uses, results, answer_model, last_stop = {}, {}, None, None
    for e in ev:
        if e.get("type") == "assistant" and not e.get("parent_tool_use_id"):
            msg = e.get("message") or {}
            if msg.get("model"):
                answer_model = msg["model"]
            last_stop = msg.get("stop_reason") or last_stop
            for b in msg.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    uses[b.get("id") or f"u{len(uses)}"] = b.get("name") or "?"
        elif e.get("type") == "user":
            for b in (e.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    results[b.get("tool_use_id")] = (bool(b.get("is_error")), _text_of(b.get("content")))
    denied = {d.get("tool_use_id") for d in ((result or {}).get("permission_denials") or []) if isinstance(d, dict)}
    refused = executed = 0
    for tid in uses:
        res = results.get(tid)
        if tid in denied or (res and res[0] and REFUSAL_RE.search(res[1])):
            refused += 1
        else:
            executed += 1  # a result that is not a refusal, or no result at all: counted as executed (it halts the cell)
    usage = (result or {}).get("usage") or {}
    reply = (result or {}).get("result") if isinstance((result or {}).get("result"), str) else None
    is_error = bool((result or {}).get("is_error")) or (result is not None and (result.get("subtype") not in (None, "success")))
    diag = (reply if (is_error and reply) else "") + " " + (stderr_text or "")
    if is_error:
        reply = None  # an error message is never a model's reply
    diag_kind = classify_diag(diag) if (is_error or rc not in (0, None) or reply is None) else None
    cut = (last_stop == "max_tokens") or ((result or {}).get("stop_reason") == "max_tokens")
    return {
        "reply": reply, "is_error": is_error, "diag_kind": diag_kind, "diag_tail": " ".join(diag.split())[:300],
        "cut_off": cut, "stop_reason": (result or {}).get("stop_reason") or last_stop,
        "answer_model": answer_model or init.get("model"), "init_model": init.get("model"),
        "models_used": sorted(((result or {}).get("modelUsage") or {}).keys()),
        "tool_attempts": len(uses), "tool_refused": refused, "tool_executed": executed, "tool_names": sorted(set(uses.values())),
        "permission_denials": len(denied - {None}),
        "tokens": {"input": usage.get("input_tokens"), "output": usage.get("output_tokens"),
                   "reasoning": (usage.get("output_tokens_details") or {}).get("thinking_tokens"),
                   "cache_read": usage.get("cache_read_input_tokens"), "cache_write": usage.get("cache_creation_input_tokens")},
        "cost_usd": (result or {}).get("total_cost_usd"), "num_turns": (result or {}).get("num_turns"),
        "duration_ms": (result or {}).get("duration_ms"), "unparsed_lines": bad, "has_result": result is not None,
        "init": {"model": init.get("model"), "tools": init.get("tools"), "mcp_servers": init.get("mcp_servers"),
                 "apiKeySource": init.get("apiKeySource"), "permissionMode": init.get("permissionMode"),
                 "plugins": init.get("plugins"), "skills": init.get("skills"), "slash_commands": init.get("slash_commands"),
                 "agents": init.get("agents"), "version": init.get("claude_code_version"),
                 "effort": next((init[k] for k in init if "effort" in k.lower()), None)} if init else None,
        "settings_reported": {"model": init.get("model"), "permissionMode": init.get("permissionMode"),
                              "apiKeySource": init.get("apiKeySource"), "tools": len(init.get("tools") or []),
                              "mcp_servers": len(init.get("mcp_servers") or [])} if init else {},
    }


_CODEX_PLAIN = {"agent_message", "reasoning"}


def _codex_item_refused(it: dict) -> bool:
    status = str(it.get("status") or "").lower()
    ran = it.get("exit_code") not in (None, "") or bool(it.get("aggregated_output")) or bool(it.get("output")) or bool(it.get("result"))
    return status in {"declined", "failed", "error", "rejected", "denied", "blocked"} and not ran


def analyze_codex(stdout_text: str, stderr_text: str, rc, last_message, asked: str, accept=None) -> dict:
    ev, bad = parse_jsonl_text(stdout_text)
    items, usage, errors, agent_texts = {}, None, [], []
    for e in ev:
        t = e.get("type")
        if t in ("item.started", "item.updated", "item.completed") and isinstance(e.get("item"), dict):
            it = e["item"]
            items[it.get("id") or f"i{len(items)}"] = it
            if t == "item.completed" and it.get("type") == "agent_message" and isinstance(it.get("text"), str):
                agent_texts.append(it["text"])
        elif t == "turn.completed":
            usage = e.get("usage") or usage
        elif t == "turn.failed":
            errors.append((e.get("error") or {}).get("message") or "turn failed")
        elif t == "error":
            errors.append(e.get("message") or "error")
    tools = [it for it in items.values() if it.get("type") not in _CODEX_PLAIN and it.get("type") != "error"]
    for it in items.values():
        if it.get("type") == "error" and it.get("message"):
            errors.append(str(it["message"]))
    refused = sum(1 for it in tools if _codex_item_refused(it))
    executed = len(tools) - refused
    header = {}
    for key, rx in (("model", r"(?im)^\s*model:\s*(\S+)"), ("effort", r"(?im)^\s*reasoning effort:\s*(\S+)"), ("provider", r"(?im)^\s*provider:\s*(\S+)"),
                    ("sandbox", r"(?im)^\s*sandbox:\s*(\S+)"), ("approval", r"(?im)^\s*approval:\s*(\S+)")):
        m = re.search(rx, stderr_text or "")
        if m:
            header[key] = m.group(1).strip(",")
    reply = last_message if (isinstance(last_message, str) and last_message.strip()) else (agent_texts[-1] if agent_texts else None)
    is_error = bool(errors) and reply is None or rc not in (0, None)
    diag = " ".join(errors) + " " + (stderr_text or "")
    diag_kind = classify_diag(diag) if (is_error or errors) else None
    if diag_kind in ("backend",) and reply is not None and rc == 0:
        diag_kind = None  # a transient message in a call that answered
    u = usage or {}
    return {
        "reply": reply, "is_error": is_error, "diag_kind": diag_kind, "diag_tail": " ".join(diag.split())[:300],
        "cut_off": False, "stop_reason": None,
        "answer_model": header.get("model"), "init_model": header.get("model"), "models_used": [header["model"]] if header.get("model") else [],
        "tool_attempts": len(tools), "tool_refused": refused, "tool_executed": executed, "tool_names": sorted({str(it.get("type")) for it in tools}),
        "permission_denials": 0,
        "tokens": {"input": u.get("input_tokens"), "output": u.get("output_tokens"), "reasoning": u.get("reasoning_output_tokens"),
                   "cache_read": u.get("cached_input_tokens"), "cache_write": None},
        "cost_usd": None, "num_turns": None, "duration_ms": None, "unparsed_lines": bad, "has_result": usage is not None or reply is not None,
        "init": None, "settings_reported": header,
    }


def analyze_ours(rj: dict, rawj: dict, reply_txt, asked: str, accept, ours: dict, prompt: str) -> dict:
    """The broker's run.json and raw.json (and reply.txt) -> what the runner records, plus the request check."""
    rawj = rawj or {}
    ch = (rawj.get("choices") or [{}])[0] if isinstance(rawj.get("choices"), list) and rawj.get("choices") else {}
    msg = ch.get("message") or {}
    sent = rawj.get("request_sent")
    problems = []
    if not isinstance(sent, dict):
        problems.append("request_sent missing from the ledger record")
    else:
        body = ours["body"]
        extra = set(sent) - set(ours["allowed_request_keys"]) - {"_endpoint_override"}
        if extra:
            problems.append(f"unexpected request keys {sorted(extra)}")
        if sent.get("model") != asked:
            problems.append("model in the request differs")
        if sent.get("messages") != [{"role": "user", "content": prompt}]:
            problems.append("messages are not exactly one user message holding the prompt")
        if sent.get("reasoning") != {"effort": body["effort"]}:
            problems.append("reasoning differs")
        for k in ("max_tokens", "temperature", "seed"):
            if (body[k] is None and k in sent) or (body[k] is not None and sent.get(k) != body[k]):
                problems.append(f"{k} differs")
        if sent.get("provider") != {"data_collection": body["data_collection"]} or sent.get("stream") is not False:
            problems.append("provider or stream differs")
    tok = (rj or {}).get("tokens") or {}
    usage = rawj.get("usage") or {}
    return {
        "reply": reply_txt, "finish_reason": ch.get("finish_reason"), "native_finish_reason": ch.get("native_finish_reason"),
        "answer_model": rawj.get("model"), "upstream_provider": rawj.get("provider"), "openrouter_id": rawj.get("id"),
        "tool_attempts": len(msg.get("tool_calls") or []), "tool_refused": 0, "tool_executed": 0,
        "tool_names": sorted({(t.get("function") or {}).get("name", "?") for t in (msg.get("tool_calls") or []) if isinstance(t, dict)}),
        "tokens": {"input": tok.get("input"), "output": tok.get("output"), "reasoning": tok.get("reasoning"),
                   "cache_read": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"), "cache_write": None},
        "cost_usd": (rj or {}).get("providerReportedCostUsd"), "request_problems": problems,
        "settings_reported": {"request_sent": sent} if isinstance(sent, dict) else {},
    }


# ---------------------------------------------------------------- transports


class OursTransport:
    kind = "ours"

    def __init__(self, ctx: Ctx, name: str, cfg: dict):
        self.ctx, self.name, self.cfg = ctx, name, cfg
        self.ours = ctx.S["ours"]
        self.broker_dir = ctx.root / self.ours["broker_copy"]
        self.ledger_dir = ctx.root / self.ours["ledger_dir"]
        self.timeout = ctx.S["plan"]["timeout_s"]

    def env(self, body: dict) -> dict:
        env = allowed_env(self.ctx, extra_names=["OPENROUTER_API_KEY"])  # passed through by name only; this code never reads it
        env["BROKER_CONFIG_DIR"] = str(Path(self.ours["broker_source"]))
        env["BROKER_LEDGER_DIR"] = str(self.ledger_dir)
        env["S2_MATRIX_BODY"] = json.dumps(body)
        env.update(self.ctx.extra_env)
        return env

    def ask(self, prompt: str, key: str, rep: int, wid: int, body_override=None, **_) -> dict:
        body = {**self.ours["body"], **(self.cfg.get("body_override") or {}), **(body_override or {})}
        asked = self.cfg["model"]
        with tempfile.TemporaryDirectory(prefix="s2-ours-") as d:
            pf = Path(d) / "prompt.txt"
            pf.write_bytes(prompt.encode("utf-8"))
            argv = [self.ours["node"], str(self.broker_dir / "broker.mjs"), "run", "--provider", self.ours["provider"], "--model", asked,
                    "--prompt-file", str(pf), "--lane", self.ours["lane"]]
            t0 = time.time()
            rc, out, err, timed_out = run_process(argv, None, self.broker_dir, self.env(body), self.timeout + 60)
        secs = round(time.time() - t0, 2)
        err_text = err.decode("utf-8", "replace")
        m = re.search(r"recorded in ledger/(\S+)", err_text)
        rel = m.group(1) if m else None
        rj = rawj = reply_txt = None
        if rel:
            d = self.ledger_dir / rel
            rj, rawj = read_json(d / "run.json"), read_json(d / "raw.json")
            try:
                reply_txt = (d / "reply.txt").read_text(encoding="utf-8")
            except OSError:
                reply_txt = None
        base = {"seconds": secs, "ledger": rel, "model_asked": asked, "cost_basis": "ledger", "body_used": body}
        if timed_out:
            return {**base, "kind": "backend_error", "error": "no answer within the runner's time limit", "http_status": None}
        if rc == 3:
            return {**base, "kind": "stop", "reason": "the broker's confidentiality gate refused a prompt (exit 3)"}
        if rc == 2 or rc == 127:
            return {**base, "kind": "stop", "reason": f"broker could not run (exit {rc}): {err_text.strip()[-200:]}"}
        if rj is None:
            return {**base, "kind": "backend_error", "error": f"no ledger record (exit {rc}): {err_text.strip()[-200:]}", "http_status": None}
        a = analyze_ours(rj, rawj, reply_txt, asked, self.cfg.get("accept_models"), {**self.ours, "body": body}, prompt)
        a.update(base)
        status = rj.get("httpStatus")
        errtxt = rj.get("error") or ""
        a["http_status"] = status
        if a["request_problems"] and rc == 0:
            return {**a, "kind": "stop", "reason": "the request in the ledger differs from the sealed body: " + "; ".join(a["request_problems"])}
        if rc == 0 and rj.get("status") == "ok":
            if a["finish_reason"] == "length":
                return {**a, "kind": "no_answer", "error": "length (the reply was cut off at max_tokens)"}
            if not (a["reply"] or "").strip():
                return {**a, "kind": "no_answer", "error": "empty reply"}
            return {**a, "kind": "answered", "error": None}
        # a failed call
        raw_code = ((rawj or {}).get("error") or {}).get("code") if isinstance((rawj or {}).get("error"), dict) else None
        text = f"{errtxt} {raw_code or ''}"
        if status == 402 or raw_code == 402 or re.search(r"(insufficient credits|credit limit|key limit|limit exceeded|out of credit|payment required)", text, re.I):
            return {**a, "kind": "stop", "reason": f"credit or key limit (HTTP {status or raw_code}): {errtxt[:160]}"}
        if status in (401, 403):
            return {**a, "kind": "stop", "reason": f"the route refused the key (HTTP {status}): {errtxt[:160]}"}
        if a["finish_reason"] == "length":
            return {**a, "kind": "no_answer", "error": "length (the reply was cut off at max_tokens)"}
        if status is None or status in (408, 409, 425, 429) or (isinstance(status, int) and status >= 500) or (status == 200 and raw_code in (408, 429, 500, 502, 503, 504, 529)) \
                or re.search(r"(Could not reach|no answer within|timeout)", errtxt, re.I):
            return {**a, "kind": "backend_error", "error": errtxt[:300]}
        return {**a, "kind": "no_answer", "error": errtxt[:300], "backend_class": isinstance(status, int) and status >= 400}


class CliTransport:
    kind = "cli"

    def __init__(self, ctx: Ctx, name: str, cfg: dict, wave: int, dropped=()):
        self.ctx, self.name, self.cfg, self.wave = ctx, name, cfg, wave
        self.dropped = set(dropped)
        self.timeout = ctx.S["plan"]["timeout_s"]
        self.events_dir = ctx.results / "events" / f"{name}-w{wave}"

    def empty_dir(self, wid: int) -> Path:
        d = self.ctx.root / f"empty-{self.name}-{wid}"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def env(self) -> dict:
        env = allowed_env(self.ctx)
        env.update(self.cfg.get("env_set") or {})
        for n in self.cfg.get("env_remove") or []:
            env.pop(n, None)
        env.update({k: v for k, v in self.ctx.extra_env.items() if k.startswith("STANDIN_")})  # the dry run's stand-in switches only
        return env

    def flag_id(self, args) -> str:
        return " ".join(args)

    def build_argv(self, cwd: Path, last_file: Path, effort=None) -> list:
        S, cfg = self.ctx.S, self.cfg
        sub = {"model": cfg["model"], "effort": effort or cfg["effort"], "cwd": str(cwd), "last_message_file": str(last_file),
               "claude_tools_csv": ",".join(S["claude_builtin_tools"])}
        rx = re.compile(r"\{(model|effort|cwd|last_message_file|claude_tools_csv)\}")
        argv = list(cfg["binary"])
        for fl in cfg["flags"]:
            if self.flag_id(fl["args"]) in self.dropped and not fl.get("required"):
                continue
            argv += [rx.sub(lambda m: sub[m.group(1)], a) for a in fl["args"]]
        for feat in cfg.get("disable_features") or []:
            if self.flag_id(["--disable", feat]) not in self.dropped:
                argv += ["--disable", feat]
        if cfg.get("stdin_marker"):
            argv.append(cfg["stdin_marker"])
        return argv

    def ask(self, prompt: str, key: str, rep: int, wid: int, effort=None, tag="", **_) -> dict:
        cfg = self.cfg
        cwd = self.empty_dir(wid)
        leftovers = sorted(p.name for p in cwd.iterdir())
        if leftovers:
            return {"kind": "stop", "reason": f"the working folder was not empty before the call: {leftovers[:5]}", "model_asked": cfg["model"]}
        self.events_dir.mkdir(parents=True, exist_ok=True)
        safe = safe_name(key) + f"-r{rep}" + (f"-{tag}" if tag else "")
        last_file = self.events_dir / f"{safe}.last.txt"
        if last_file.exists():
            last_file.unlink()
        argv = self.build_argv(cwd, last_file, effort)
        t0 = time.time()
        rc, out, err, timed_out = run_process(argv, prompt.encode("utf-8"), cwd, self.env(), self.timeout)
        secs = round(time.time() - t0, 2)
        out_text, err_text = out.decode("utf-8", "replace"), err.decode("utf-8", "replace")
        ev_file = self.events_dir / f"{safe}.jsonl"
        ev_file.write_bytes(out)
        if err_text.strip():
            (self.events_dir / f"{safe}.stderr.txt").write_text(err_text, encoding="utf-8", newline="")
        events_rel = str(ev_file.relative_to(self.ctx.root)).replace("\\", "/")
        base = {"seconds": secs, "model_asked": cfg["model"], "events_file": events_rel, "cost_basis": "shadow" if cfg["kind"] == "claude-code" else None,
                "effort_asked": effort or cfg["effort"], "argv_flags_dropped": sorted(self.dropped)}
        left_after = sorted(p.name for p in cwd.iterdir())
        if timed_out:
            return {**base, "kind": "backend_error", "error": "no answer within the runner's time limit", "http_status": None}
        if cfg["kind"] == "claude-code":
            a = analyze_claude(out_text, err_text, rc, cfg["model"], cfg.get("accept_models"))
        else:
            last = last_file.read_text(encoding="utf-8", errors="replace") if last_file.exists() else None
            a = analyze_codex(out_text, err_text, rc, last, cfg["model"], cfg.get("accept_models"))
        a.update(base)
        if left_after:
            return {**a, "kind": "stop", "reason": f"the call left files in the empty folder: {left_after[:5]}"}
        dk = a["diag_kind"]
        if dk == "plan_limit":
            return {**a, "kind": "stop", "reason": "plan limit message: " + a["diag_tail"][:160], "stop_class": "plan_limit"}
        if dk == "login":
            return {**a, "kind": "stop", "reason": "login failure: " + a["diag_tail"][:160], "stop_class": "login"}
        if dk == "backend" and not (a["reply"] or "").strip():
            return {**a, "kind": "backend_error", "error": a["diag_tail"][:200]}
        if a["cut_off"]:
            return {**a, "kind": "no_answer", "error": "length (the reply was cut off)"}
        if a["is_error"] or not (a["reply"] or "").strip():
            return {**a, "kind": "no_answer", "error": (a["diag_tail"][:200] or f"no reply (exit {rc})")}
        return {**a, "kind": "answered", "error": None}

    def version(self) -> str:
        rc, out, err, _ = run_process(list(self.cfg["binary"]) + ["--version"], None, self.ctx.root, self.env(), 60)
        return (out.decode("utf-8", "replace") or err.decode("utf-8", "replace")).strip().splitlines()[0] if (out or err) else ""


def make_transport(ctx: Ctx, name: str, wave: int, dropped=()):
    cfg = ctx.S["cells"][name]
    return OursTransport(ctx, name, cfg) if cfg["kind"] == "ours" else CliTransport(ctx, name, cfg, wave, dropped)


# ---------------------------------------------------------------- spend, markers, the gate


def row_files(ctx: Ctx):
    files = [p for p in ctx.results.glob("*-w*.jsonl")] if ctx.results.exists() else []
    if ctx.probe_dir.exists():
        files += list(ctx.probe_dir.glob("*.jsonl"))
    return files


def ledger_spend(ctx: Ctx) -> float:
    """Every cost the matrix ledger reports for this lane: it also holds the attempts that were retried or timed out."""
    d = ctx.root / ctx.S["ours"]["ledger_dir"]
    total = 0.0
    if d.exists():
        for f in d.glob("*/*/run.json"):
            rj = read_json(f)
            if rj and rj.get("lane") == ctx.S["ours"]["lane"] and isinstance(rj.get("providerReportedCostUsd"), (int, float)):
                total += rj["providerReportedCostUsd"]
    return total


def spent_total(ctx: Ctx) -> float:
    """The larger of what the result rows and probe rows add up to and what the ledger holds (the cap adds up reported costs)."""
    total = 0.0
    for f in row_files(ctx):
        for r in read_jsonl(f):
            if r.get("cost_basis") == "ledger" and isinstance(r.get("cost_usd"), (int, float)):
                total += r["cost_usd"]
    return max(total, ledger_spend(ctx))


def marker_path(ctx: Ctx, cell: str) -> Path:
    return ctx.probe_dir / f"{cell}-PASS.json"


def load_marker(ctx: Ctx, cell: str):
    m = read_json(marker_path(ctx, cell))
    if not m:
        return None, "no probe pass marker (run the probe first)"
    if m.get("settings_sha256") != ctx.settings_sha:
        return None, "SETTINGS.json changed since the probe"
    try:
        age = time.time() - calendar.timegm(time.strptime(m["time"], "%Y-%m-%dT%H:%M:%SZ"))
    except Exception:
        age = 0
    if age > ctx.S["probe"]["pass_valid_hours"] * 3600:
        return None, "the probe pass is older than the allowed hours"
    return m, None


def spend_gate(ctx: Ctx, cells: list, wave: int, repeats: int):
    """RUN-PLAN section 4: probe mean cost per call x calls still to make x margin <= fraction x cap (probes' spend already counted)."""
    sp = ctx.S["spend"]
    cap = ctx.cap()
    ours = [c for c in cells if ctx.S["cells"][c]["kind"] == "ours"]
    if not ours:
        return True, "no API cell: the spend gate does not apply", 0.0
    spent = spent_total(ctx)
    projected = 0.0
    parts = []
    for c in ours:
        m, why = load_marker(ctx, c)
        if not m or not isinstance(m.get("mean_cost_usd"), (int, float)):
            return False, f"{c}: no measured cost per call ({why or 'probe recorded no cost'}); the gate cannot pass", 0.0
        planned = ctx.S["inputs"]["selected_rows"] * repeats
        done = len(read_jsonl(ctx.results / f"{c}-w{wave}.jsonl"))
        remaining = max(0, planned - done)
        projected += m["mean_cost_usd"] * remaining * sp["gate_margin"]
        parts.append(f"{c}: US${m['mean_cost_usd']:.5f} x {remaining} calls x {sp['gate_margin']}")
    limit = sp["gate_fraction"] * cap
    ok = spent + projected <= limit
    return ok, f"spent US${spent:.4f} + projected US${projected:.4f} ({'; '.join(parts)}) against {sp['gate_fraction']:.0%} of the US${cap:.2f} cap = US${limit:.4f}", projected


# ---------------------------------------------------------------- the run


class CellRunner:
    def __init__(self, ctx: Ctx, name: str, wave: int, transport, total: int, repeats: int):
        self.ctx, self.name, self.wave, self.transport, self.total, self.repeats = ctx, name, wave, transport, total, repeats
        self.cfg = ctx.S["cells"][name]
        self.out = ctx.results / f"{name}-w{wave}.jsonl"
        self.lock = threading.Lock()
        self.workers = ctx.S["plan"]["workers_per_cell"]
        self.pool = ThreadPoolExecutor(max_workers=self.workers, initializer=self._init_worker)
        self.sem = threading.BoundedSemaphore(self.workers)
        self.wids = queue.Queue()
        for i in range(self.workers):
            self.wids.put(i)
        self.tl = threading.local()
        existing = read_jsonl(self.out)
        self.done = {(r["key"], r["repeat"]) for r in existing}
        self.n_rows = len(existing)
        self.n_backend = sum(1 for r in existing if r.get("backend_error"))
        self.n_invalid = sum(1 for r in existing if r.get("status") != "answered" or not MR.read_sealed(r["version"], r.get("reply"))[0])
        self.n_other_model = sum(1 for r in existing if r.get("model_mismatch"))
        self.first_model = next((r["model_reported"] for r in existing if r.get("model_reported") and not r.get("model_mismatch")), None)
        self.versions_seen = {r.get("tool_version") for r in existing if r.get("tool_version")}
        self.stop_reason = None
        self.stop_class = None
        self.calls_since_check = 0
        self.spent = spent_total(ctx) if self.cfg["kind"] == "ours" else 0.0
        self.baseline_version = None
        m, _ = load_marker(ctx, name)
        if m:
            self.baseline_version = m.get("version")
        self.last_repeat_started = 0
        self.session_calls = 0

    def _init_worker(self):
        self.tl.wid = self.wids.get()

    # -- control files
    def paused(self) -> bool:
        return (self.ctx.root / "PAUSE").exists() or (self.ctx.root / f"PAUSE-{self.name}").exists()

    def halted(self) -> bool:
        return (self.ctx.root / "HALT").exists() or (self.ctx.root / f"HALT-{self.name}").exists()

    @property
    def stopped(self) -> bool:
        return self.stop_reason is not None or self.halted()

    def set_stop(self, reason: str, cls=None):
        with self.lock:
            if self.stop_reason is None:
                self.stop_reason, self.stop_class = reason, cls
                log(f"[{self.name}] STOP: {reason}")

    def pause_and_ask(self, reason: str):
        f = self.ctx.root / f"PAUSE-{self.name}"
        if not f.exists():
            f.write_text(f"{utc()} {reason}\nDelete this file to continue, or create HALT-{self.name} to stop.\n", encoding="utf-8")
        log(f"[{self.name}] PAUSED, asking: {reason}")

    # -- scheduling
    def submit(self, item):
        self.sem.acquire()
        fut = self.pool.submit(self._work, item)
        fut.add_done_callback(lambda f: (self.sem.release(), f.exception() and self.set_stop(f"crash: {f.exception()!r}")))

    def drain(self):
        for _ in range(self.workers):
            self.sem.acquire()
        for _ in range(self.workers):
            self.sem.release()

    def check_version(self, label: str) -> bool:
        if self.cfg["kind"] == "ours":
            return True
        v = self.transport.version()
        if self.baseline_version is None:
            self.baseline_version = v
        elif v != self.baseline_version:
            self.set_stop(f"tool version changed ({label}): {self.baseline_version!r} -> {v!r}")
            return False
        return True

    def start_repeat(self, rep: int) -> bool:
        if rep == self.last_repeat_started:
            return not self.stopped
        self.drain()
        self.last_repeat_started = rep
        if self.stopped:
            return False
        if not self.check_version(f"before repeat {rep}"):
            return False
        if rep > 1 and self.ctx.S.get("pause_between_repeats", {}).get(self.name):
            self.pause_and_ask(f"repeat {rep - 1} finished; read the usage meter before repeat {rep}")
        return True

    # -- one call
    def _work(self, item):
        r, rep, pos = item
        wid = getattr(self.tl, "wid", 0)
        while self.paused() and not self.halted():
            time.sleep(2)
        if self.stopped:
            return
        if self.cfg["kind"] == "ours":
            with self.lock:
                if self.session_calls % 10 == 0:
                    self.spent = spent_total(self.ctx)
                over = self.spent >= self.ctx.cap()
            if over:
                self.set_stop(f"spend cap US${self.ctx.cap():.2f} reached (spent US${self.spent:.4f})", "cap")
                return
        started, t0 = utc(), time.time()
        tries, res = 0, None
        for wait in (0,) + tuple(self.ctx.S["plan"]["retry_waits_s"]):
            if wait:
                for _ in range(wait):
                    if self.halted():
                        break
                    time.sleep(1)
            tries += 1
            res = self.transport.ask(r["prompt"], r["key"], rep, wid)
            if res["kind"] != "backend_error":
                break
        if res["kind"] == "stop":
            self.set_stop(res["reason"], res.get("stop_class"))
            return
        reply = res.get("reply")
        reported = res.get("answer_model")
        mismatch = bool(reported) and not model_ok(self.cfg["model"], reported, self.cfg.get("accept_models"))
        status = "answered" if res["kind"] == "answered" else "no answer"
        if mismatch:
            status = "no answer"  # a call answered by another model counts as no valid reply (DESIGN-A, pause and ask)
        row = {
            "cell": self.name, "wave": self.wave, "key": r["key"], "log": r["log"], "version": r["version"], "repeat": rep, "position": pos,
            "prompt_sha256": r["sha256"], "started": started, "ended": utc(), "seconds": round(time.time() - t0, 2), "tries": tries,
            "status": status, "error": ("answered by another model" if mismatch else res.get("error")), "reply": reply,
            "finish_reason": res.get("finish_reason") or res.get("stop_reason"),
            "model_asked": self.cfg["model"], "model_reported": reported, "model_mismatch": mismatch, "models_used": res.get("models_used"),
            "upstream_provider": res.get("upstream_provider"), "tokens": res.get("tokens"), "cost_usd": res.get("cost_usd"),
            "cost_basis": res.get("cost_basis"), "tool_attempts": res.get("tool_attempts", 0), "tool_refused": res.get("tool_refused", 0),
            "tool_executed": res.get("tool_executed", 0), "tool_names": res.get("tool_names", []),
            "tool_version": self.baseline_version, "settings_reported": res.get("settings_reported"),
            "ledger": res.get("ledger"), "events_file": res.get("events_file"), "num_turns": res.get("num_turns"),
            "backend_error": bool(res["kind"] == "backend_error" or res.get("backend_class")), "http_status": res.get("http_status"),
        }
        with self.lock:
            with self.out.open("a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            self.done.add((r["key"], rep))
            self.n_rows += 1
            self.session_calls += 1
            if row["backend_error"]:
                self.n_backend += 1
            invalid = status != "answered" or not MR.read_sealed(r["version"], reply)[0]
            if invalid:
                self.n_invalid += 1
            if mismatch:
                self.n_other_model += 1
            if isinstance(row["cost_usd"], (int, float)) and row["cost_basis"] == "ledger":
                self.spent += row["cost_usd"]
            n_rows, n_back, n_inv, n_other = self.n_rows, self.n_backend, self.n_invalid, self.n_other_model
            if reported and not mismatch:
                if self.first_model is None:
                    self.first_model = reported
        log(f"[{self.name} {n_rows}/{self.total}] {r['version']} r{rep}: {status} ({row['seconds']} s, tries {tries})")
        st = self.ctx.S["stops"]
        if row["tool_executed"] > 0:
            self.set_stop(f"a tool was executed ({','.join(row['tool_names'])}) in {r['key']} r{rep}", "tool_executed")
        if reported and not mismatch and self.first_model and reported != self.first_model:
            self.set_stop(f"the model id the route reports changed: {self.first_model!r} -> {reported!r} (snapshot change)", "snapshot")
        if n_rows <= st["backend_errors_first_calls"] and n_back > st["backend_errors_max_fraction"] * st["backend_errors_first_calls"]:
            self.set_stop(f"backend errors in more than 5 percent of the first 100 calls ({n_back} so far)", "backend")
        if self.cfg["kind"] != "ours" and n_rows <= st["invalid_first_calls"] and n_inv > st["invalid_max_fraction"] * st["invalid_first_calls"]:
            self.pause_and_ask(f"more than half of the first 96 calls are invalid ({n_inv} of {n_rows})")
        if n_other >= st["other_model_calls_pause_at"]:
            self.pause_and_ask(f"{n_other} calls were answered by a model other than {self.cfg['model']}")
        if self.cfg["kind"] == "ours" and self.spent >= self.ctx.cap():
            self.set_stop(f"spend cap US${self.ctx.cap():.2f} reached (spent US${self.spent:.4f})", "cap")
        if self.cfg["kind"] != "ours":
            self.calls_since_check += 1
            if self.calls_since_check >= st["version_check_every_calls"]:
                self.calls_since_check = 0
                self.check_version("periodic")

    def finish(self):
        self.pool.shutdown(wait=True)


def record_ledger_head(ctx: Ctx, when: str, cells: list, verify=False):
    """results/ledger-heads.txt: the matrix ledger's index.head copied before and after each ours run (RUN-PLAN S6)."""
    head = ctx.root / ctx.S["ours"]["ledger_dir"] / "index.head"
    text = head.read_text(encoding="utf-8").replace(chr(10), " ").strip() if head.exists() else "(no ledger yet)"
    line = f"{utc()} {when} {','.join(cells)}: {text}"
    if verify:
        bd = ctx.root / ctx.S["ours"]["broker_copy"]
        env = allowed_env(ctx)
        env["BROKER_CONFIG_DIR"] = str(Path(ctx.S["ours"]["broker_source"]))
        env["BROKER_LEDGER_DIR"] = str(ctx.root / ctx.S["ours"]["ledger_dir"])
        rc, out, err, _ = run_process([ctx.S["ours"]["node"], str(bd / "broker.mjs"), "verify"], None, bd, env, 300)
        line += " | verify: " + (out.decode("utf-8", "replace").strip().splitlines() or ["(no output)"])[0][:200]
    ctx.results.mkdir(parents=True, exist_ok=True)
    with (ctx.results / "ledger-heads.txt").open("a", encoding="utf-8", newline=chr(10)) as fh:
        fh.write(line + chr(10))


def run_cells(ctx: Ctx, cells: list, wave: int, repeats: int, limit_items=None, transports=None) -> int:
    rows = load_prompt_rows(ctx)
    items = plan_items(ctx, rows)
    if limit_items:  # dry runs only: the first N prompts of each repeat
        per = len(rows)
        items = [it for it in items if (it[2] - (it[1] - 1) * per) <= limit_items]
    ctx.results.mkdir(parents=True, exist_ok=True)
    ours_cells = [c for c in cells if ctx.S["cells"][c]["kind"] == "ours"]
    if ours_cells:
        record_ledger_head(ctx, "before", cells)
    log(f"order fingerprint {order_fingerprint(items)[:16]} ({len(items)} calls planned per cell, {repeats} repeat(s) requested)")
    runners = []
    total = len([1 for it in items if it[1] <= repeats])
    for c in cells:
        marker, why = load_marker(ctx, c)
        if ctx.S["cells"][c]["kind"] != "ours" and not marker:
            raise SystemExit(f"STOP: {c}: {why}")
        dropped = (marker or {}).get("flags_dropped") or []
        tr = (transports or {}).get(c) or make_transport(ctx, c, wave, dropped)
        runners.append(CellRunner(ctx, c, wave, tr, total, repeats))
    for cr in runners:
        done_n = sum(1 for r, rep, _ in items if rep <= repeats and (r["key"], rep) in cr.done)
        log(f"[{cr.name}] started; {done_n} of {total} already recorded; model {cr.cfg['model']}")
    try:
        for r, rep, pos in items:
            if rep > repeats:
                break
            if (ctx.root / "HALT").exists():
                log("HALT file found; stopping after the calls in flight")
                break
            order = runners if pos % 2 == 0 else list(reversed(runners))
            for cr in order:
                if cr.stopped or (r["key"], rep) in cr.done:
                    continue
                if not cr.start_repeat(rep):
                    continue
                cr.submit((r, rep, pos))
            if all(cr.stopped for cr in runners):
                break
    finally:
        for cr in runners:
            cr.finish()
    code = EXIT_FINISHED
    for cr in runners:
        marker = ctx.results / f"{cr.name}-w{wave}.STOPPED.json"
        if cr.stop_reason:
            marker.write_text(json.dumps({"cell": cr.name, "wave": wave, "time": utc(), "reason": cr.stop_reason, "class": cr.stop_class,
                                          "rows": cr.n_rows, "spent_usd": round(cr.spent, 6) if cr.cfg["kind"] == "ours" else None}, indent=1) + "\n", encoding="utf-8")
            code = EXIT_STOPPED
        elif cr.halted():
            code = max(code, EXIT_HALTED)
        elif marker.exists():
            marker.unlink()
    if ours_cells:
        record_ledger_head(ctx, "after", cells, verify=True)
    for cr in runners:
        log(f"ended {utc()} cell {cr.name} rows {cr.n_rows} of {total} stopped={cr.stop_reason or 'no'}")
    print(f"ended {utc()} code {code}", flush=True)
    return code


# ---------------------------------------------------------------- the broker copy


BROKER_COPY_FILES = ["broker.mjs", "package.json"]


def setup_broker(ctx: Ctx) -> int:
    """Copy the real broker's code into a private folder and add the openrouter-matrix adapter (the real broker is not touched)."""
    ours = ctx.S["ours"]
    src, dst = Path(ours["broker_source"]), ctx.root / ours["broker_copy"]
    import shutil
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for f in BROKER_COPY_FILES:
        shutil.copy2(src / f, dst / f)
    shutil.copytree(src / "lib", dst / "lib")
    adapter = ctx.here / "broker-adapter" / "openrouter-matrix.mjs"
    shutil.copy2(adapter, dst / "lib" / "providers" / "openrouter-matrix.mjs")
    shutil.copy2(ctx.here / "broker-adapter" / "gate_check.mjs", dst / "gate_check.mjs")

    def patch(rel: str, old: str, new: str):
        p = dst / rel
        t = p.read_text(encoding="utf-8")
        if t.count(old) != 1:
            raise SystemExit(f"STOP: expected exactly one {old!r} in {rel}, found {t.count(old)}; the real broker changed, check the adapter patch")
        p.write_text(t.replace(old, new), encoding="utf-8", newline="")

    patch("lib/providers/index.mjs", "import * as codex from './codex.mjs';",
          "import * as openrouterMatrix from './openrouter-matrix.mjs';\nimport * as codex from './codex.mjs';")
    patch("lib/providers/index.mjs", "'openrouter-plain-long': openrouterPlainLong,",
          "'openrouter-plain-long': openrouterPlainLong, 'openrouter-matrix': openrouterMatrix,")
    patch("lib/providers/index.mjs", "  'openrouter-plain-long': 'messages',\n", "  'openrouter-plain-long': 'messages',\n  'openrouter-matrix': 'messages',\n")
    patch("lib/modelinfo.mjs", "    case 'openrouter-decisions':\n      info = {",
          "    case 'openrouter-matrix': {\n      const m = (() => { try { return JSON.parse(env.S2_MATRIX_BODY || '{}'); } catch { return {}; } })();\n"
          "      info = {\n        model: { requested, resolved: requested, source: 'request' },\n"
          "        effort: eff(m.effort ?? 'low', 'reasoning.effort in the request body (raw.json request_sent)'),\n"
          "        settingsSent: { reasoning: { effort: m.effort ?? 'low' }, provider: { data_collection: m.data_collection ?? 'deny' }, max_tokens: m.max_tokens ?? 4000, temperature: m.temperature ?? 0, seed: m.seed ?? 42 },\n"
          "      };\n      break;\n    }\n    case 'openrouter-decisions':\n      info = {")
    patch("lib/modelinfo.mjs", "    case 'openrouter':\n    case 'openrouter-decisions': return typeof raw.model",
          "    case 'openrouter':\n    case 'openrouter-matrix':\n    case 'openrouter-decisions': return typeof raw.model")
    patch("lib/modelinfo.mjs", "(provider === 'openrouter' || provider === 'openrouter-decisions') && typeof raw?.provider",
          "(provider === 'openrouter' || provider === 'openrouter-matrix' || provider === 'openrouter-decisions') && typeof raw?.provider")
    head = ""
    try:
        head = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        pass
    lines = []
    for p in sorted(dst.rglob("*")):
        if p.is_file() and p.name != "COPY-SHA256.txt":
            lines.append(f"{sha256_file(p)} *{p.relative_to(dst).as_posix()}")
    (dst / "COPY-SHA256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    (dst / "COPY-SOURCE.txt").write_text(f"copied {utc()} from {src.as_posix()} at git HEAD {head or 'unknown'} (working tree, not only HEAD)\n"
                                         "added: lib/providers/openrouter-matrix.mjs; patched: lib/providers/index.mjs, lib/modelinfo.mjs (register the provider)\n", encoding="utf-8")
    print(f"setup-broker: copied {len(lines)} files to {dst.as_posix()}; manifest COPY-SHA256.txt; real broker untouched")
    return 0


def verify_broker_copy(ctx: Ctx) -> list:
    dst = ctx.root / ctx.S["ours"]["broker_copy"]
    man = dst / "COPY-SHA256.txt"
    if not man.exists():
        return ["broker copy absent (run setup-broker)"]
    problems = []
    listed = set()
    for sha, rel in read_sha_list(man):
        listed.add(rel)
        p = dst / rel
        if not p.exists() or sha256_file(p) != sha:
            problems.append(f"broker copy: {rel} differs or is missing")
    for p in dst.rglob("*"):
        if p.is_file() and p.name not in ("COPY-SHA256.txt", "COPY-SOURCE.txt") and p.relative_to(dst).as_posix() not in listed:
            problems.append(f"broker copy: unlisted file {p.relative_to(dst).as_posix()}")
    return problems


# ---------------------------------------------------------------- check


def parent_instruction_files(p: Path) -> list:
    found = []
    for d in [p] + list(p.resolve().parents):
        for n in ("AGENTS.md", "CLAUDE.md", "agents.md", "claude.md"):
            if (d / n).exists():
                found.append(str(d / n))
    return found


def check(ctx: Ctx, cells: list, quiet=False) -> int:
    bad = []

    def say(ok: bool, msg: str):
        print(("ok    " if ok else "FAIL  ") + msg)
        if not ok:
            bad.append(msg)

    rows = load_prompt_rows(ctx)
    say(True, f"prompts.jsonl matches its SHA-256; {len(rows)} prompts selected ({len({r['log'] for r in rows})} logs x {len(ctx.S['inputs']['versions'])} versions)")
    leaks = [r["key"] for r in rows if TRUTH_RE.search(r["prompt"]) or TRUTH_RE.search(r["key"])]
    say(not leaks, f"no truth or kind in any prompt or key ({len(leaks)} found)")
    items = plan_items(ctx, rows)
    per_cell = len(items)
    say(per_cell == 576 or ctx.S["plan"]["repeats"] != 3, f"{per_cell} calls per cell; {per_cell * len(ctx.cell_names())} over {len(ctx.cell_names())} cells")
    fp = order_fingerprint(items)
    say(fp == order_fingerprint(plan_items(ctx, rows)), f"one cell-independent order for every cell (fingerprint {fp[:16]}; the PC and the box must print the same one)")
    ok_seal, problems = verify_seal(ctx)
    if ok_seal is None:
        print("note  RUN-SHA256.txt is absent: nothing is sealed yet, so `run` will refuse; check, setup, probe and dry still work")
    else:
        say(ok_seal, "every file in RUN-SHA256.txt matches its hash" + ("" if ok_seal else ": " + "; ".join(problems[:5])))
    for c in cells:
        cfg = ctx.S["cells"][c]
        if cfg["kind"] == "ours":
            probs = verify_broker_copy(ctx)
            say(not probs, f"{c}: broker copy intact ({'; '.join(probs[:3]) if probs else 'manifest matches'})")
            if not probs:
                sel = ctx.root / "results" / "selected-prompts.jsonl"
                sel.parent.mkdir(parents=True, exist_ok=True)
                sel.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8", newline="\n")
                env = allowed_env(ctx)
                env["BROKER_CONFIG_DIR"] = str(Path(ctx.S["ours"]["broker_source"]))
                rc, out, err, _ = run_process([ctx.S["ours"]["node"], str(ctx.root / ctx.S["ours"]["broker_copy"] / "gate_check.mjs"),
                                               str(ctx.root / ctx.S["ours"]["broker_copy"]), str(sel), ctx.S["ours"]["provider"]], None, ctx.root, env, 120)
                say(rc == 0, f"{c}: all {len(rows)} prompts pass the broker's confidentiality gate ({out.decode('utf-8', 'replace').strip()[:120] or err.decode('utf-8', 'replace')[:120]})")
            say("S2_ENDPOINT" not in os.environ and "S2_DRY_RUN" not in os.environ, f"{c}: no test-only endpoint override in the environment")
        else:
            for w in (0, 1):
                d = ctx.root / f"empty-{c}-{w}"
                d.mkdir(parents=True, exist_ok=True)
                say(not any(d.iterdir()), f"{c}: empty folder {d.name} is empty")
                found = parent_instruction_files(d)
                say(not found, f"{c}: no AGENTS.md or CLAUDE.md in {d.name} or any parent {found[:2] if found else ''}")
            tr = CliTransport(ctx, c, cfg, 0)
            v = tr.version()
            say(bool(v), f"{c}: tool version reads as {v!r} (planned {cfg['expected_version']}; a difference is noted, not a failure)")
            names = sorted(k for k in tr.env() if re.search(r"(KEY|TOKEN|SECRET|PASSWORD)", k, re.I))
            say(not names, f"{c}: no key-like variable in the tool's environment {names}")
    ours_left, foreign = find_orphans(cells)
    say(not ours_left, f"no orphan processes of this test ({'; '.join(f'{p}: {a[:60]}' for p, a in ours_left[:3]) if ours_left else 'none listed'})")
    if foreign:
        print(f"note  other agent-tool processes are running (not ours, not stopped here): {'; '.join(f'{p}: {a[:50]}' for p, a in foreign[:3])}")
    print("CHECK", "PASSED" if not bad else f"FAILED ({len(bad)})")
    return 0 if not bad else 1


# ---------------------------------------------------------------- status


def status(ctx: Ctx, cells: list, wave=None) -> int:
    for c in cells:
        files = sorted(ctx.results.glob(f"{c}-w*.jsonl")) if ctx.results.exists() else []
        for f in files:
            if wave is not None and not f.name.endswith(f"-w{wave}.jsonl"):
                continue
            rows = read_jsonl(f)
            by_rep = {}
            for r in rows:
                by_rep[r["repeat"]] = by_rep.get(r["repeat"], 0) + 1
            ans = sum(1 for r in rows if r.get("status") == "answered")
            tools = (sum(r.get("tool_attempts", 0) for r in rows), sum(r.get("tool_refused", 0) for r in rows), sum(r.get("tool_executed", 0) for r in rows))
            spent = sum(r["cost_usd"] for r in rows if r.get("cost_basis") == "ledger" and isinstance(r.get("cost_usd"), (int, float)))
            stop = read_json(f.with_name(f.name.replace(".jsonl", ".STOPPED.json")))
            ctrl = [n for n in ("PAUSE", f"PAUSE-{c}", "HALT", f"HALT-{c}") if (ctx.root / n).exists()]
            print(f"{f.stem}: {len(rows)} of {ctx.S['inputs']['selected_rows'] * ctx.S['plan']['repeats']} calls recorded "
                  f"(repeats {dict(sorted(by_rep.items()))}); answered {ans}, no answer {len(rows) - ans}; tool attempts {tools[0]}, refused {tools[1]}, executed {tools[2]}"
                  + (f"; spend US${spent:.4f}" if ctx.S['cells'][c]['kind'] == 'ours' else "")
                  + (f"; control files {ctrl}" if ctrl else "") + (f"; STOPPED: {stop['reason']}" if stop else ""))
        if not files:
            print(f"{c}: nothing recorded")
    if any(ctx.S["cells"][c]["kind"] == "ours" for c in cells):
        print(f"API spend so far (all ours rows and probes): US${spent_total(ctx):.4f} of the US${ctx.cap():.2f} cap")
    return 0


def stop_orphans() -> int:
    orphans, foreign = find_orphans()
    if foreign:
        print(f"not touching {len(foreign)} other agent-tool process(es) that are not ours")
    for pid, args in orphans:
        print(f"stopping {pid}: {args}")
        if pid:
            try:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, timeout=30)
                else:
                    os.kill(pid, signal.SIGKILL)
            except Exception as e:
                print(f"  could not stop {pid}: {e}")
    print(f"{len(orphans)} process(es) listed")
    return 0


# ---------------------------------------------------------------- probe

TOY_LOGS = [
    ("toy-pass", "the docs formatter check", ["$ ./tools/fmt-check docs/", "fmt-check: 12 files checked, 0 need changes"], "no file needs changes"),
    ("toy-fail", "the docs formatter check", ["$ ./tools/fmt-check docs/", "fmt-check: 12 files checked, 3 need changes", "fmt-check: exit status 1"], "no file needs changes"),
    ("toy-absent", "the docs formatter check", ["$ ls docs/", "guide.md  index.md  notes.md"], "no file needs changes"),
]


def toy_prompts(rows: list) -> list:
    """12 toy prompts (3 invented logs x the 4 versions) built from the real prompt templates; none of them is one of the 48 logs."""
    out = []
    for version in ("report", "did-the-work", "coat-check", "coat-check-did"):
        tpl = next(r["prompt"] for r in rows if r["version"] == version)
        for name, thing, lines, result in TOY_LOGS:
            p = re.sub(r"(?<=Task: ).*?(?=\n\nTranscript:)", {"report": f"Report whether {thing} passes.", "coat-check": f"Report whether {thing} passes.",
                                                              "did-the-work": f"Make {thing} pass.", "coat-check-did": f"Make {thing} pass."}[version], tpl, count=1, flags=re.S)
            p = re.sub(r"(?<=<<<\n).*?(?=\n>>>)", "\n".join(lines), p, count=1, flags=re.S)
            p = re.sub(r"(?<=this work is done when the check\n  ).*?(?=\nshows that)", "./tools/fmt-check docs/", p, count=1, flags=re.S)
            p = re.sub(r"(?<=\nshows that ).*?(?=\.\n)", result, p, count=1, flags=re.S)
            out.append({"key": f"{name}|{version}", "version": version, "prompt": p})
    return out


def _mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return sum(xs) / len(xs) if xs else None


def probe_ours(ctx: Ctx, cell: str, rows: list, wave: int) -> dict:
    cfg = ctx.S["cells"][cell]
    tr = make_transport(ctx, cell, wave)
    toys = toy_prompts(rows)
    toy_keys = {t["prompt"] for t in toys}
    assert not any(r["prompt"] in toy_keys for r in rows), "a toy prompt is one of the 48 logs"
    ctx.probe_dir.mkdir(parents=True, exist_ok=True)
    out = ctx.probe_dir / f"{cell}.jsonl"
    prow = []

    def record(purpose, key, prompt, res, extra=None):
        row = {"cell": cell, "purpose": purpose, "key": key, "time": utc(), "kind": res["kind"], "error": res.get("error") or res.get("reason"),
               "http_status": res.get("http_status"), "model_asked": cfg["model"], "model_reported": res.get("answer_model"),
               "upstream_provider": res.get("upstream_provider"), "tokens": res.get("tokens"), "cost_usd": res.get("cost_usd"), "cost_basis": res.get("cost_basis"),
               "finish_reason": res.get("finish_reason"), "ledger": res.get("ledger"), "seconds": res.get("seconds"), "reply_head": (res.get("reply") or "")[:200],
               "request_problems": res.get("request_problems"), "tool_attempts": res.get("tool_attempts"), "body_used": res.get("body_used"), **(extra or {})}
        with out.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        prow.append(row)
        return row

    for i, t in enumerate(toys):
        res = tr.ask(t["prompt"], t["key"], 0, 0)
        valid = MR.read_sealed(t["version"], res.get("reply"))[0] if res.get("reply") else False
        record("toy", t["key"], t["prompt"], res, {"reply_valid": valid})
    knob_prompts = ctx.S["probe"]["knob_prompts"]
    high = ctx.S["probe"]["knob_high"]["ours"]
    knob = {"low": [], "high": []}
    for i, kp in enumerate(knob_prompts):
        for lvl, eff in (("low", ctx.S["ours"]["body"]["effort"]), ("high", high)):
            res = tr.ask(kp + "\n\nAnswer in one short sentence.", f"knob-{i}-{lvl}", 0, 0, body_override={"effort": eff})
            r = record("knob-" + lvl, f"knob-{i}", kp, res, {"effort_sent": eff})
            t = r.get("tokens") or {}
            knob[lvl].append((t.get("reasoning") or 0) + (t.get("output") or 0))
    toy_rows = [r for r in prow if r["purpose"] == "toy"]
    reported = sorted({r["model_reported"] for r in prow if r["model_reported"]})
    accepted = [model_ok(cfg["model"], m, cfg.get("accept_models")) for m in reported]
    all_ok = all(r["kind"] in ("answered",) and r["http_status"] in (None, 200) for r in toy_rows) and not any(r["request_problems"] for r in prow)
    knob_confirmed = sum(knob["low"]) < sum(knob["high"])
    rep = {
        "cell": cell, "kind": "ours", "time": utc(), "model_asked": cfg["model"], "toy_calls": len(toy_rows), "toy_answered": sum(1 for r in toy_rows if r["kind"] == "answered"),
        "toy_valid_replies": sum(1 for r in toy_rows if r.get("reply_valid")), "slug_accepted": bool(toy_rows) and all_ok,
        "effort_accepted": bool(toy_rows) and all_ok, "effort_sent": ctx.S["ours"]["body"]["effort"],
        "models_reported": reported, "models_reported_accepted": all(accepted) if accepted else False,
        "upstream_providers": sorted({r["upstream_provider"] for r in prow if r["upstream_provider"]}),
        "mean_input_tokens": _mean([(r.get("tokens") or {}).get("input") for r in toy_rows]),
        "mean_output_tokens": _mean([(r.get("tokens") or {}).get("output") for r in toy_rows]),
        "mean_reasoning_tokens": _mean([(r.get("tokens") or {}).get("reasoning") for r in toy_rows]),
        "mean_cost_usd": _mean([r["cost_usd"] for r in toy_rows]), "mean_seconds": _mean([r["seconds"] for r in toy_rows]),
        "total_probe_cost_usd": round(sum(r["cost_usd"] for r in prow if isinstance(r.get("cost_usd"), (int, float))), 6),
        "finish_reasons": sorted({str(r["finish_reason"]) for r in prow}), "knob_tokens_low": knob["low"], "knob_tokens_high": knob["high"], "knob_high_effort": high,
        "effort_confirmed": knob_confirmed, "errors": sorted({str(r["error"]) for r in prow if r["error"]})[:5],
    }
    rep["pass"] = bool(rep["slug_accepted"] and rep["models_reported_accepted"] and rep["toy_answered"] == rep["toy_calls"] == 12)
    rep["flags"] = ([] if knob_confirmed else ["effort not confirmed"]) + ([] if rep["models_reported_accepted"] else ["reported model id not accepted: add it to accept_models after reading the ledger"])         + ([] if isinstance(rep["mean_cost_usd"], (int, float)) else ["no cost reported by the route: the spend gate cannot pass"])
    return rep


CANARY_ORDER = ("NO_FILE_TOOL", "NO_WEB_TOOL", "NO_SHELL_TOOL")


def feature_names(tr: CliTransport) -> set:
    rc, out, err, _ = run_process(list(tr.cfg["binary"]) + ["features", "list"], None, tr.ctx.root, tr.env(), 60)
    if rc != 0:
        return set()
    return {m.group(1) for m in (re.match(r"\s*([a-z][a-z0-9_]+)\b", l) for l in out.decode("utf-8", "replace").splitlines()) if m}


def help_text(tr: CliTransport, sub=()) -> str:
    rc, out, err, _ = run_process(list(tr.cfg["binary"]) + list(sub) + ["--help"], None, tr.ctx.root, tr.env(), 60)
    return out.decode("utf-8", "replace") + err.decode("utf-8", "replace")


def probe_cli(ctx: Ctx, cell: str, rows: list, wave: int) -> dict:
    cfg = ctx.S["cells"][cell]
    tr = CliTransport(ctx, cell, cfg, wave)
    ctx.probe_dir.mkdir(parents=True, exist_ok=True)
    out = ctx.probe_dir / f"{cell}.jsonl"
    rep = {"cell": cell, "kind": cfg["kind"], "time": utc(), "model_asked": cfg["model"], "effort_asked": cfg["effort"], "flags": [], "problems": []}
    rep["version"] = tr.version()
    rep["version_planned"] = cfg["expected_version"]
    rep["version_note"] = "same as planned" if cfg["expected_version"] in rep["version"] else "differs from the planned version: noted, not a failure"
    rep["env_names_passed"] = sorted(tr.env())
    rep["key_like_env_names"] = [k for k in rep["env_names_passed"] if re.search(r"(KEY|TOKEN|SECRET|PASSWORD)", k, re.I)]
    if rep["key_like_env_names"]:
        rep["problems"].append("a key-like variable is in the tool's environment")
    # sign-in (no model call)
    if cfg["kind"] == "claude-code":
        rc, o, e, _ = run_process(list(cfg["binary"]) + ["auth", "status", "--json"], None, ctx.root, tr.env(), 60)
        st = None
        try:
            st = json.loads(o.decode("utf-8", "replace"))
        except Exception:
            pass
        keep = {k: st.get(k) for k in ("loggedIn", "authMethod", "apiProvider", "subscriptionType") if isinstance(st, dict) and k in st}
        rep["auth"] = keep
        if not (keep.get("loggedIn") is True and str(keep.get("authMethod", "")).lower() not in ("api_key", "apikey", "api-key", "console")):
            rep["problems"].append("Claude Code is not signed in on a plan (auth status): " + json.dumps(keep))
        helptxt = help_text(tr)
    else:
        rc, o, e, _ = run_process(list(cfg["binary"]) + ["login", "status"], None, ctx.root, tr.env(), 60)
        line = (o.decode("utf-8", "replace") + e.decode("utf-8", "replace")).strip().splitlines()
        first = line[0][:120] if line else ""
        rep["auth"] = {"login_status_line": first}
        if not re.search(r"chatgpt", first, re.I) or re.search(r"api key", first, re.I):
            rep["problems"].append("Codex is not signed in with ChatGPT (login status): " + first)
        helptxt = help_text(tr, ["exec"])
    # a flag the installed tool's help does not list is dropped (named here and in the addendum); a required one is a problem
    dropped = []
    rep["required_flags_missing"] = []
    for fl in cfg["flags"]:
        tok = next((x for x in fl["args"] if x.startswith("-")), None)
        if tok is None or tok == "-c" or re.fullmatch(r"-[A-Za-z]", tok) or not helptxt.strip():
            continue  # config overrides, short flags and an unreadable help cannot be checked from the help text
        if not re.search(r"(?<![\w-])" + re.escape(tok) + r"(?![\w-])", helptxt):
            if fl.get("required"):
                rep["required_flags_missing"].append(tr.flag_id(fl["args"]))
            else:
                dropped.append(tr.flag_id(fl["args"]))
    dropped += [d for d in cfg.get("drop_flags", []) if d not in dropped]
    if cfg["kind"] == "codex":
        names = feature_names(tr)
        rep["codex_features_listed"] = len(names)
        if names:
            for feat in cfg["disable_features"]:
                if feat not in names:
                    dropped.append(tr.flag_id(["--disable", feat]))
        else:
            rep["flags"].append("feature names not verified (features list gave nothing): the canaries decide")
    tr.dropped = set(dropped)
    rep["flags_dropped"] = dropped
    if rep["required_flags_missing"]:
        rep["problems"].append("a required flag is not in the tool's help: " + ", ".join(rep["required_flags_missing"]))
    canaries = []
    for sentinel in CANARY_ORDER:
        res = tr.ask(ctx.S["probe"]["canaries"][sentinel], f"canary-{sentinel}", 0, 0, tag=sentinel)
        said = (res.get("reply") or "").strip()
        ok = res["kind"] == "answered" and said == sentinel and res.get("tool_attempts", 0) == 0
        canaries.append({"sentinel": sentinel, "ok": ok, "reply_head": said[:80], "tool_attempts": res.get("tool_attempts"), "kind": res["kind"],
                         "error": res.get("error") or res.get("reason"), "answer_model": res.get("answer_model"), "seconds": res.get("seconds")})
        with out.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps({"cell": cell, "purpose": "canary", "time": utc(), **canaries[-1], "tokens": res.get("tokens"), "cost_usd": res.get("cost_usd"), "cost_basis": res.get("cost_basis")}) + "\n")
        if res["kind"] == "stop":
            rep["problems"].append("canary stopped the cell: " + str(res.get("reason")))
            break
    rep["canaries"] = canaries
    if not (len(canaries) == 3 and all(c["ok"] for c in canaries)):
        rep["problems"].append("a canary did not get its exact sentinel with zero tool items")
    last_init = None
    toy_costs, toy_secs, toy_tokens = [], [], []
    toys = toy_prompts(rows)
    for t in (toys[0], toys[8]):  # a report toy and a coat-check toy
        res = tr.ask(t["prompt"], t["key"], 0, 0, tag="toy")
        toy_costs.append(res.get("cost_usd"))
        toy_secs.append(res.get("seconds"))
        toy_tokens.append(res.get("tokens"))
        last_init = res.get("init") or last_init
        with out.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps({"cell": cell, "purpose": "toy", "key": t["key"], "time": utc(), "kind": res["kind"], "tokens": res.get("tokens"), "cost_usd": res.get("cost_usd"),
                                 "cost_basis": res.get("cost_basis"), "seconds": res.get("seconds"), "answer_model": res.get("answer_model"),
                                 "reply_valid": bool(res.get("reply")) and MR.read_sealed(t["version"], res.get("reply"))[0]}) + "\n")
    if cfg["kind"] == "claude-code":
        init = last_init or {}
        rep["init"] = {k: init.get(k) for k in ("model", "tools", "mcp_servers", "apiKeySource", "permissionMode", "plugins", "effort", "version")}
        rep["init_lists_for_review"] = {k: init.get(k) for k in ("skills", "slash_commands", "agents")}
        if init.get("tools") not in ([], None) or init.get("mcp_servers") not in ([], None):
            rep["problems"].append("the init event lists tools or MCP servers")
        if init.get("apiKeySource") not in ("none", None):
            rep["problems"].append(f"apiKeySource is {init.get('apiKeySource')!r}, not none")
        if init.get("plugins") not in ([], None):
            rep["problems"].append("the init event lists plugins")
        if not init:
            rep["flags"].append("no init event seen: tools, MCP servers and key source not confirmed")
    # knob check
    high = ctx.S["probe"]["knob_high"][cfg["kind"]]
    fallback = ctx.S["probe"]["knob_high_fallback"].get(cfg["kind"])
    knob = {"low": [], "high": []}
    used_high = high
    for i, kp in enumerate(ctx.S["probe"]["knob_prompts"]):
        r_low = tr.ask(kp + "\n\nAnswer in one short sentence.", f"knob-{i}", 0, 0, tag="klow")
        r_hi = tr.ask(kp + "\n\nAnswer in one short sentence.", f"knob-{i}", 0, 0, effort=used_high, tag="khigh")
        if r_hi["kind"] != "answered" and fallback and used_high != fallback:
            used_high = fallback
            r_hi = tr.ask(kp + "\n\nAnswer in one short sentence.", f"knob-{i}", 0, 0, effort=used_high, tag="khigh")
        for lvl, r in (("low", r_low), ("high", r_hi)):
            t = r.get("tokens") or {}
            knob[lvl].append((t.get("reasoning") or 0) + (t.get("output") or 0))
            with out.open("a", encoding="utf-8", newline="\n") as fh:
                fh.write(json.dumps({"cell": cell, "purpose": "knob-" + lvl, "time": utc(), "kind": r["kind"], "tokens": r.get("tokens"), "cost_usd": r.get("cost_usd"),
                                     "cost_basis": r.get("cost_basis"), "seconds": r.get("seconds")}) + "\n")
    rep["knob_tokens_low"], rep["knob_tokens_high"], rep["knob_high_effort"] = knob["low"], knob["high"], used_high
    rep["effort_confirmed"] = sum(knob["low"]) < sum(knob["high"])
    if not rep["effort_confirmed"]:
        rep["flags"].append("effort not confirmed")
    sr = tr._last_settings if hasattr(tr, "_last_settings") else None
    rep["mean_cost_usd_shadow"] = _mean(toy_costs)
    rep["mean_seconds"] = _mean(toy_secs)
    rep["toy_tokens"] = toy_tokens
    rep["pass"] = not rep["problems"]
    rep["settings_reported_note"] = "Codex: the header on stderr if it appeared with --json (see the saved stderr files); otherwise the flags as passed are the record." if cfg["kind"] == "codex" else "Claude Code: the init event (above)."
    return rep


def probe(ctx: Ctx, cells: list, wave: int) -> int:
    rows = load_prompt_rows(ctx)
    ctx.probe_dir.mkdir(parents=True, exist_ok=True)
    code = 0
    for c in cells:
        cfg = ctx.S["cells"][c]
        log(f"probe {c}: {'12 toy calls and a knob check' if cfg['kind'] == 'ours' else 'version, sign-in, 3 canaries, 2 toys, knob check'}")
        rep = probe_ours(ctx, c, rows, wave) if cfg["kind"] == "ours" else probe_cli(ctx, c, rows, wave)
        rep["settings_sha256"] = ctx.settings_sha
        (ctx.probe_dir / f"{c}-report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if rep["pass"]:
            marker_path(ctx, c).write_text(json.dumps({"cell": c, "time": rep["time"], "settings_sha256": ctx.settings_sha, "version": rep.get("version"),
                                                       "flags_dropped": rep.get("flags_dropped", []), "mean_cost_usd": rep.get("mean_cost_usd"),
                                                       "effort_confirmed": rep.get("effort_confirmed")}, indent=1) + "\n", encoding="utf-8")
        elif marker_path(ctx, c).exists():
            marker_path(ctx, c).unlink()
        print(f"probe {c}: {'PASS' if rep['pass'] else 'FAIL'}; flags {rep['flags']}; problems {rep.get('problems', [])}")
        code = code or (0 if rep["pass"] else 1)
    write_probe_report(ctx)
    return code


def write_probe_report(ctx: Ctx):
    reps = [read_json(p) for p in sorted(ctx.probe_dir.glob("*-report.json"))]
    L = ["# Probe report (stack test 2, Test A)", "", f"Written by `run_matrix.py probe`; regenerated {utc()}. Toy items only (not among the 48 logs). Nothing here is a result.", ""]
    for r in reps:
        L += [f"## {r['cell']}: {'PASS' if r.get('pass') else 'FAIL'}", "", "```json", json.dumps({k: v for k, v in r.items() if k not in ("toy_tokens",)}, indent=1, ensure_ascii=False), "```", ""]
    (ctx.probe_dir / "PROBE-REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


# ---------------------------------------------------------------- main


def parse_cells(ctx: Ctx, s):
    cells = [c.strip() for c in (s or "").split(",") if c.strip()] or ctx.cell_names()
    for c in cells:
        if c not in ctx.S["cells"]:
            raise SystemExit(f"unknown cell {c!r}; choose from {ctx.cell_names()}")
    return cells


def main(argv=None) -> int:
    for stream in (sys.stdout, sys.stderr):  # a tool's message may hold a character the console cannot print; never crash a worker on it
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["check", "setup-broker", "probe", "probe-report", "run", "status", "stop-orphans", "dry"])
    ap.add_argument("--cells", default="")
    ap.add_argument("--wave", type=int, default=None)
    ap.add_argument("--repeats", type=int, default=None)
    ap.add_argument("--cap-usd", type=float, default=None)
    ap.add_argument("--root", default=None)
    ap.add_argument("--settings", default=None)
    a = ap.parse_args(argv)
    ctx = Ctx(root=a.root, settings_path=a.settings)
    if a.cap_usd is not None:
        ctx.cap_override = a.cap_usd
    if a.mode == "dry":
        import dry_matrix
        return dry_matrix.main()
    if a.mode == "setup-broker":
        return setup_broker(ctx)
    if a.mode == "stop-orphans":
        return stop_orphans()
    if a.mode == "probe-report":
        ctx.probe_dir.mkdir(parents=True, exist_ok=True)
        write_probe_report(ctx)
        print("wrote", (ctx.probe_dir / "PROBE-REPORT.md").as_posix())
        return 0
    cells = parse_cells(ctx, a.cells)
    if a.mode == "check":
        return check(ctx, cells)
    if a.mode == "status":
        return status(ctx, cells, a.wave)
    wave = a.wave or 1
    if a.mode == "probe":
        return probe(ctx, cells, wave)
    if a.mode == "run":
        ok, problems = verify_seal(ctx)
        if ctx.require_seal and ok is not True:
            raise SystemExit("STOP: `run` needs RUN-SHA256.txt and every file in it matching: " + "; ".join(problems[:6]))
        orphans, foreign = find_orphans(cells)
        if orphans:
            raise SystemExit("STOP: orphan processes of this test are running (list and stop them first: run_matrix.py stop-orphans): " + "; ".join(f"{p} {a_[:50]}" for p, a_ in orphans[:4]))
        if foreign:
            print(f"note: {len(foreign)} other agent-tool process(es) are running (not ours): " + "; ".join(f"{p} {a_[:50]}" for p, a_ in foreign[:3]))
        repeats = a.repeats or ctx.S["plan"]["repeats"]
        ours = [c for c in cells if ctx.S["cells"][c]["kind"] == "ours"]
        if ours:
            probs = verify_broker_copy(ctx)
            if probs:
                raise SystemExit("STOP: " + "; ".join(probs[:4]))
            for c in ours:
                m, why = load_marker(ctx, c)
                if not m:
                    raise SystemExit(f"STOP: {c}: {why}")
            gate_ok, msg, _ = spend_gate(ctx, cells, wave, repeats)
            print(("spend gate passed: " if gate_ok else "STOP, spend gate not passed: ") + msg)
            if not gate_ok:
                print("Choices: a higher cap (his yes), the cheap alternative for that family, or fewer repeats for the API cells.")
                return EXIT_STOPPED
        return run_cells(ctx, cells, wave, repeats)
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
