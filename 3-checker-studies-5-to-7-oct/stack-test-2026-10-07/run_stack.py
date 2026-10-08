#!/usr/bin/env python3
"""S13, the stack test: S12's 54 records, forced and allowed, through two agent command-line tools.

Design: DESIGN.md in this folder, sealed before any call. Standard library only (Python 3.10).

    python3 run_stack.py probe          one tiny call per tool (no record), to check both tools answer; prints what they report
    python3 run_stack.py sol            the 108 Sol calls (Codex command line, gpt-6.1-sol, reasoning xhigh)
    python3 run_stack.py gemini         the 108 Gemini calls (Gemini command line, gemini-3.8-flash, read-only plan mode)
    python3 run_stack.py status         how many calls each tool has recorded
    python3 run_stack.py dry            the whole plan against a stand-in tool (no real call), written to dry/

Resumable: a call already recorded is skipped. Addendum 1 (7 Oct 2026): every tool call gets an empty standard input. A PAUSE file in this folder pauses between calls; a HALT file stops after the current call.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
REQUESTS = INPUTS / "s12-requests.jsonl"
FRAMINGS = INPUTS / "s12-framings.json"
REQUESTS_SHA256 = "928a3b713559f01945067cb05fa7892f81fec1b83332f8a4df8049944b5e9609"
FRAMINGS_SHA256 = "4a6be62b38dafe1bea99cae71091dfb7d1c5f33a385cc6959b1e694ba427b2a0"
TIMEOUT_S = 600
FRAMING_ORDER = ("forced", "allowed")
VERDICTS = {"shown", "contradicted", "not_shown"}
PAUSE, HALT = HERE / "PAUSE", HERE / "HALT"

os.environ["PATH"] = str(Path.home() / ".local" / "bin") + os.pathsep + os.environ.get("PATH", "")


def utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(msg: str) -> None:
    print(f"{utc()} {msg}", flush=True)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_inputs():
    rb, fb = REQUESTS.read_bytes(), FRAMINGS.read_bytes()
    if sha256_bytes(rb) != REQUESTS_SHA256 or sha256_bytes(fb) != FRAMINGS_SHA256:
        sys.exit("STOP: the inputs differ from the sealed ones (SHA-256 mismatch). Nothing was run.")
    records = [json.loads(line) for line in rb.decode("utf-8").splitlines() if line.strip()]
    framings = json.loads(fb.decode("utf-8"))
    assert len(records) == 54 and [r["id"] for r in records] == [f"T{i:03d}" for i in range(1, 55)]
    assert set(FRAMING_ORDER) <= set(framings)
    return records, framings


def build_prompt(framings: dict, framing: str, record: dict) -> str:
    return framings[framing] + "\n\n" + record["user"]


def command(tool: str, prompt: str, reply_file: Path) -> list[str]:
    if tool == "sol":
        return ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "--sandbox", "read-only", "--color", "never",
                "-m", "gpt-6.1-sol", "-c", 'model_reasoning_effort="xhigh"', "-o", str(reply_file), prompt]
    if tool == "gemini":
        return ["gemini", "-m", "gemini-3.8-flash", "--approval-mode", "plan", "-o", "json", "-p", prompt]
    if tool == "stand-in":
        reply = '{"reason": "stand-in", "turn_id": null, "quote": "", "verdict": "not_shown"}'
        return [sys.executable, "-c", f"import sys; open(sys.argv[1], 'w').write({reply!r}); print({reply!r})", str(reply_file)]
    raise ValueError(tool)


def reply_text(tool: str, stdout: str, reply_file: Path) -> tuple[str, dict]:
    """The model's final text, and what the tool reports about itself (model name, usage)."""
    meta: dict = {}
    if tool in ("sol", "stand-in"):
        text = reply_file.read_text(encoding="utf-8", errors="replace") if reply_file.exists() else ""
        return text, meta
    try:
        data = json.loads(stdout)
    except Exception:
        return stdout, {"json_error": True}
    text = data.get("response") or data.get("text") or ""
    stats = data.get("stats") or {}
    if isinstance(stats, dict):
        meta["models"] = list((stats.get("models") or {}).keys()) if isinstance(stats.get("models"), dict) else stats.get("models")
        meta["stats"] = stats
    return text, meta


def parse_verdict(text: str) -> dict | None:
    """The last JSON object in the text that has a verdict; None when there is none."""
    found = None
    for m in re.finditer(r"\{[^{}]*\"verdict\"[^{}]*\}", text, flags=re.S):
        try:
            obj = json.loads(m.group(0))
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("verdict") in VERDICTS:
            found = obj
    return found


def done_keys(out: Path) -> set:
    keys = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                keys.add((row["id"], row["framing"]))
    return keys


def run_tool(tool: str, out_dir: Path, records, framings) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    cwd = out_dir / f"{tool}-empty-folder"
    cwd.mkdir(exist_ok=True)
    out = out_dir / f"{tool}.jsonl"
    done = done_keys(out)
    plan = [(r, f) for r in records for f in FRAMING_ORDER]
    log(f"{tool}: {len(plan)} calls planned, {len(done)} already recorded")
    for i, (record, framing) in enumerate(plan, 1):
        if (record["id"], framing) in done:
            continue
        while PAUSE.exists():
            log("PAUSE file found; waiting in 30-second steps")
            time.sleep(30)
        if HALT.exists():
            log("HALT file found; stopping")
            return
        prompt = build_prompt(framings, framing, record)
        reply_file = cwd.parent / f"{tool}-last-reply.txt"
        if reply_file.exists():
            reply_file.unlink()
        started, t0 = utc(), time.time()
        row = {"tool": tool, "id": record["id"], "framing": framing, "prompt_sha256": sha256_bytes(prompt.encode("utf-8")),
               "started": started}
        try:
            proc = subprocess.run(command(tool, prompt, reply_file), cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                                  encoding="utf-8", errors="replace", timeout=TIMEOUT_S)
            text, meta = reply_text(tool, proc.stdout, reply_file)
            verdict = parse_verdict(text)
            row.update({"exit_code": proc.returncode, "status": "answered" if verdict else "no_verdict",
                        "verdict": verdict["verdict"] if verdict else None, "parsed": verdict, "reply_text": text,
                        "stdout": proc.stdout[-20000:], "stderr": proc.stderr[-4000:], "tool_report": meta})
        except subprocess.TimeoutExpired:
            row.update({"exit_code": None, "status": "timeout", "verdict": None, "parsed": None, "reply_text": "",
                        "stdout": "", "stderr": "", "tool_report": {}})
        except Exception as exc:  # recorded, never dropped
            row.update({"exit_code": None, "status": "error", "verdict": None, "parsed": None, "reply_text": "",
                        "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"[:4000], "tool_report": {}})
        row.update({"ended": utc(), "seconds": round(time.time() - t0, 2)})
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        log(f"[{tool} {i}/{len(plan)}] {record['id']} {framing}: {row['status']} {row['verdict'] or ''} ({row['seconds']} s)")
    log(f"{tool}: finished")


def probe() -> None:
    prompt = 'Reply with this JSON and nothing else: {"reason": "probe", "turn_id": null, "quote": "", "verdict": "not_shown"}'
    cwd = HERE / "results" / "probe-empty-folder"
    cwd.mkdir(parents=True, exist_ok=True)
    for tool in ("sol", "gemini"):
        reply_file = cwd.parent / f"probe-{tool}-reply.txt"
        t0 = time.time()
        try:
            proc = subprocess.run(command(tool, prompt, reply_file), cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                                  encoding="utf-8", errors="replace", timeout=300)
            text, meta = reply_text(tool, proc.stdout, reply_file)
            print(json.dumps({"tool": tool, "exit_code": proc.returncode, "verdict": (parse_verdict(text) or {}).get("verdict"),
                              "seconds": round(time.time() - t0, 1), "tool_report": {k: v for k, v in meta.items() if k != "stats"},
                              "stderr_tail": proc.stderr[-400:]}, ensure_ascii=False), flush=True)
        except Exception as exc:
            print(json.dumps({"tool": tool, "error": f"{type(exc).__name__}: {exc}"}), flush=True)


def status() -> None:
    for tool in ("sol", "gemini"):
        out = HERE / "results" / f"{tool}.jsonl"
        rows = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()] if out.exists() else []
        by = {}
        for r in rows:
            by[r["status"]] = by.get(r["status"], 0) + 1
        print(f"{tool}: {len(rows)} of 108 recorded {by}")


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "probe":
        probe()
        return 0
    if mode == "status":
        status()
        return 0
    records, framings = load_inputs()
    if mode in ("sol", "gemini"):
        run_tool(mode, HERE / "results", records, framings)
        return 0
    if mode == "dry":
        run_tool("stand-in", HERE / "dry", records, framings)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
