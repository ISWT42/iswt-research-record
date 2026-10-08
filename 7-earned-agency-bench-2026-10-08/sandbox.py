"""Where the runner (and only the runner) executes code from a model.

Reused from the coat-check relay (7 Oct 2026). One fresh temp folder per check, then it is removed. No shell.
A timeout per check. A minimal environment (no API keys). File names come from the job table, never from a model
reply, and every write goes through a path guard. A static screen refuses files that import anything off a short
allowlist or use open, exec, eval and a few similar names; a refused file is never run and counts as a failed check.
The network is blocked inside the test process (best effort).

This is a screen and a best-effort block, not a security boundary: Windows has no cheap way here to cut the network
at the operating-system level. The jobs are tiny and the models are cheap, but do not treat it as proof against a
determined hostile file.
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import jobs as J


class SandboxError(Exception):
    pass


_NAME = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*(/[A-Za-z0-9_][A-Za-z0-9_.\-]*)*")


def safe_join(base, rel):
    """Join rel under base, or raise. Refuses absolute paths, drive letters, backslashes, '..', symlinks."""
    base = Path(base).resolve()
    if not isinstance(rel, str) or not _NAME.fullmatch(rel):
        raise SandboxError(f"refused job file path: {rel!r}")
    p = (base / rel).resolve()
    if base != p and base not in p.parents:
        raise SandboxError(f"refused job file path outside the sandbox: {rel!r}")
    if p.is_symlink():
        raise SandboxError(f"refused symlink: {rel!r}")
    return p


PRELUDE = r'''
import socket as _s
def _blocked(*a, **k):
    raise OSError("network disabled in the bench sandbox")
_s.socket.connect = _blocked
_s.socket.connect_ex = _blocked
_s.create_connection = _blocked
_s.getaddrinfo = _blocked
'''
CONFTEST = "import os, sys\nsys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n" + PRELUDE
SHIM_PYTEST = r'''
class _Raises:
    def __init__(self, exc):
        self.exc = exc
    def __enter__(self):
        return self
    def __exit__(self, t, v, tb):
        if t is None:
            raise AssertionError("DID NOT RAISE")
        return issubclass(t, self.exc)
def raises(exc):
    return _Raises(exc)
'''
SHIM_RUNNER = r'''
import os, sys, importlib
d = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, d)
exec(open(os.path.join(d, "_prelude.py")).read())
try:
    mod = importlib.import_module("test_hidden")
except BaseException as e:
    print("ERROR test_hidden.py - %s: %s" % (type(e).__name__, e))
    print("1 error in 0.01s")
    sys.exit(2)
names = [n for n in list(vars(mod)) if n.startswith("test_") and callable(getattr(mod, n))]
np_ = nf = 0
for n in names:
    try:
        getattr(mod, n)()
        np_ += 1
    except BaseException as e:
        nf += 1
        print("FAILED test_hidden.py::%s - %s: %s" % (n, type(e).__name__, e))
print("%d failed, %d passed in 0.01s" % (nf, np_) if nf else "%d passed in 0.01s" % np_)
sys.exit(1 if nf else 0)
'''

_BANNED_CALLS = {"open", "exec", "eval", "compile", "__import__", "input", "breakpoint", "globals", "locals"}
_BANNED_ATTRS = {"__subclasses__", "__globals__", "__builtins__", "__code__", "__mro__", "__bases__"}
_PYTEST_CACHE = {}


def allowed_imports_for(job_id):
    return set(J.ALLOWED_IMPORTS) | set(J.JOBS[job_id]["extra_imports"])


def screen_code(code, allowed):
    """Cheap static screen. A screen, not a security boundary. Returns (ok, reason)."""
    if len(code) > 20000:
        return False, "file larger than 20000 characters"
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return True, ""  # cannot run anyway; the interpreter reports it
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in allowed:
                    return False, f"import of {a.name} is not on the allowlist"
        elif isinstance(node, ast.ImportFrom):
            if node.level or (node.module or "").split(".")[0] not in allowed:
                return False, f"import from {node.module} is not on the allowlist"
        elif isinstance(node, ast.Name) and node.id in _BANNED_CALLS:
            return False, f"use of {node.id} is not allowed"
        elif isinstance(node, ast.Attribute) and node.attr in _BANNED_ATTRS:
            return False, f"use of {node.attr} is not allowed"
    return True, ""


def probe_pytest(python):
    if python not in _PYTEST_CACHE:
        try:
            r = subprocess.run([python, "-I", "-c", "import pytest"], capture_output=True, timeout=30, stdin=subprocess.DEVNULL)
            _PYTEST_CACHE[python] = r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            _PYTEST_CACHE[python] = False
    return _PYTEST_CACHE[python]


def _minimal_env():
    env = {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}    # a fixed hash seed: set order cannot change a grade
    for k in ("SYSTEMROOT", "SYSTEMDRIVE", "TEMP", "TMP", "PATH", "COMSPEC", "PATHEXT"):
        if k in os.environ:
            env[k] = os.environ[k]
    return env


def run_check(files, hidden, extra_imports=(), timeout=20, python=None, force_shim=False, allowed=None):
    """Run the hidden test file against `files` ({filename: code}) in a fresh temp sandbox."""
    python = python or sys.executable
    mode = "shim" if (force_shim or not probe_pytest(python)) else "pytest"
    res = {"mode": mode, "refused": False, "refused_reason": "", "exit_code": None, "timed_out": False,
           "n_passed": 0, "n_failed": 0, "n_error": 0, "error_classes": {}, "import_messages": [], "raw": ""}
    allowed = set(allowed) if allowed is not None else set(J.ALLOWED_IMPORTS) | set(extra_imports)
    for name, code in files.items():
        ok, why = screen_code(code, allowed)
        if not ok:
            res.update(refused=True, refused_reason=f"{name}: {why}", passed=False)
            return res
    sbx = Path(tempfile.mkdtemp(prefix="eab-sbx-")).resolve()
    try:
        for name, code in files.items():
            safe_join(sbx, name).write_text(code, encoding="utf-8")
        safe_join(sbx, "test_hidden.py").write_text(hidden, encoding="utf-8")
        # "-s" keeps user site-packages out. It is not "-I", because isolated mode would also drop PYTHONHASHSEED=0,
        # and a grade must not depend on the order of a set.
        if mode == "pytest":
            safe_join(sbx, "conftest.py").write_text(CONFTEST, encoding="utf-8")
            cmd = [python, "-s", "-m", "pytest", "-q", "--tb=no", "-rfE", "-p", "no:cacheprovider", "test_hidden.py"]
        else:
            safe_join(sbx, "pytest.py").write_text(SHIM_PYTEST, encoding="utf-8")
            safe_join(sbx, "_prelude.py").write_text(PRELUDE, encoding="utf-8")
            safe_join(sbx, "run_shim.py").write_text(SHIM_RUNNER, encoding="utf-8")
            cmd = [python, "-s", "run_shim.py"]
        try:
            r = subprocess.run(cmd, cwd=str(sbx), env=_minimal_env(), capture_output=True, timeout=timeout,
                               stdin=subprocess.DEVNULL, shell=False)
            res["exit_code"] = r.returncode
            out = (r.stdout + b"\n" + r.stderr).decode("utf-8", "replace")
        except subprocess.TimeoutExpired as e:
            res["timed_out"] = True
            out = ((e.stdout or b"") + b"\n" + (e.stderr or b"")).decode("utf-8", "replace")
        res["raw"] = out[-20000:]
    finally:
        shutil.rmtree(sbx, ignore_errors=True)
    _parse_output(res)
    res["passed"] = bool(res["exit_code"] == 0 and not res["timed_out"] and res["n_passed"] > 0
                         and res["n_failed"] == 0 and res["n_error"] == 0)
    return res


def _parse_output(res):
    out = res["raw"]
    for key, pat in (("n_passed", r"(\d+) passed"), ("n_failed", r"(\d+) failed"), ("n_error", r"(\d+) errors?\b")):
        m = re.findall(pat, out)
        res[key] = int(m[-1]) if m else 0
    classes = {}
    msgs = []
    for line in out.splitlines():
        m = re.match(r"(?:FAILED|ERROR) \S+(?: - )(\w+)(?::\s?(.*))?$", line.strip())
        if m:
            cls = m.group(1)
            classes[cls] = classes.get(cls, 0) + 1
            if cls in ("ModuleNotFoundError", "ImportError") and m.group(2):
                msgs.append(m.group(2)[:80])
    res["error_classes"] = classes
    res["import_messages"] = sorted(set(msgs))


def summarize_check(res):
    """The only view of a check that any agent ever sees: counts and error class names, no assertion text.
    (In this bench only the certifier sees it, and only for work that was picked for a check.)"""
    if res["refused"]:
        return f"refused before running: {res['refused_reason']}"
    if res["timed_out"]:
        return "timed out; no result"
    s = f"exit {res['exit_code']}; {res['n_passed']} passed, {res['n_failed']} failed, {res['n_error']} errors"
    if res["error_classes"]:
        s += "; error types: " + ", ".join(f"{k} x{v}" for k, v in sorted(res["error_classes"].items()))
    if res["import_messages"]:
        s += "; import messages: " + " | ".join(res["import_messages"])
    return s
