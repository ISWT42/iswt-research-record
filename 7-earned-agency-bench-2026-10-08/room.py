"""The room: an append-only, hash-chained record (JSONL), plus a folder of blobs.

Reused from the coat-check relay (7 Oct 2026) with three changes: a lock so several games can write at once,
an index of records by game, and an option to skip fsync for tests.

Each record holds a sequence number, the SHA-256 of the line before it, and a UTC time from the runner's clock.
A `.head` file holds the count and hash of the last line, so cutting off the newest lines is caught.
Large texts (prompts, replies, files, raw test output) live in `blobs/<sha256>.txt` and are named by hash.
Only the runner writes. A model only returns text.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import threading
import time
from pathlib import Path

GENESIS = "0" * 64


def utcnow():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canon(rec):
    return json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class ChainError(Exception):
    pass


def _retry(fn, tries=8, wait=0.05):
    """Windows sometimes refuses a file for a moment (a scanner has it open). Try again a few times, then give up loudly."""
    for i in range(tries):
        try:
            return fn()
        except PermissionError:
            if i == tries - 1:
                raise
            time.sleep(wait * (i + 1))


def verify_chain(path):
    """Return (ok, problems, n_records). Checks canonical form, seq, prev hash, blobs, head file."""
    path = Path(path)
    problems = []
    n = 0
    if not path.exists():
        return True, [], 0
    prev = GENESIS
    blobs = path.parent / "blobs"
    data = path.read_bytes()
    lines = data.split(b"\n")
    if lines and lines[-1] == b"":
        lines.pop()
    elif data:
        problems.append("file does not end with a newline (cut-off last line)")
    for i, raw in enumerate(lines):
        n += 1
        try:
            line = raw.decode("utf-8")
            rec = json.loads(line)
        except ValueError:
            problems.append(f"line {i + 1}: not valid JSON")
            break
        if canon(rec) != line:
            problems.append(f"line {i + 1}: not in canonical form (edited?)")
        if rec.get("seq") != i + 1:
            problems.append(f"line {i + 1}: seq is {rec.get('seq')}, expected {i + 1}")
        if rec.get("prev") != prev:
            problems.append(f"line {i + 1}: prev hash does not match the line before")
        for b in rec.get("blobs", []):
            bp = blobs / f"{b}.txt"
            if not bp.exists():
                problems.append(f"line {i + 1}: blob {b[:12]} missing")
            elif hashlib.sha256(bp.read_bytes()).hexdigest() != b:
                problems.append(f"line {i + 1}: blob {b[:12]} does not match its hash")
        prev = sha(line)
    head = Path(str(path) + ".head")
    if not head.exists():
        if n:
            problems.append("head file missing")
    else:
        try:
            hs, hh = head.read_text().split()
            if int(hs) != n or hh != prev:
                problems.append(f"head file says {hs} records, last hash {hh[:12]}; file has {n}, last hash {prev[:12]} (cut off or edited)")
        except ValueError:
            problems.append("head file unreadable")
    return (not problems), problems, n


class Room:
    def __init__(self, path, clock=utcnow, fsync=True):
        self.path = Path(path)
        self.dir = self.path.parent
        self.dir.mkdir(parents=True, exist_ok=True)
        self.blobs = self.dir / "blobs"
        self.blobs.mkdir(exist_ok=True)
        self.head = Path(str(self.path) + ".head")
        self.clock = clock
        self.fsync = fsync
        self._lock = threading.RLock()
        self._blob_lock = threading.Lock()
        self._records = []
        self._by_run = {}
        self._last = GENESIS
        if self.path.exists() and self.path.stat().st_size:
            ok, problems, _ = verify_chain(self.path)
            if not ok:
                raise ChainError("room does not verify: " + "; ".join(problems))
            for raw in self.path.read_bytes().split(b"\n"):
                if raw:
                    rec = json.loads(raw)
                    self._remember(rec)
                    self._last = sha(raw.decode("utf-8"))

    def _remember(self, rec):
        self._records.append(rec)
        if rec.get("run") is not None:
            self._by_run.setdefault(rec["run"], []).append(rec)

    def records(self):
        with self._lock:
            return list(self._records)

    def records_of(self, run):
        with self._lock:
            return list(self._by_run.get(run, []))

    def append(self, rec):
        with self._lock:
            rec = dict(rec)
            rec["seq"] = len(self._records) + 1
            rec["prev"] = self._last
            rec["ts"] = self.clock()
            line = canon(rec)
            f = _retry(lambda: open(self.path, "ab"))        # nothing is written until the open works
            with f:
                f.write(line.encode("utf-8") + b"\n")
                f.flush()
                if self.fsync:
                    os.fsync(f.fileno())
            self._last = sha(line)
            self._remember(rec)
            text = f"{rec['seq']} {self._last}\n"
            _retry(lambda: self.head.write_text(text))
            return rec

    def put_blob(self, text):
        h = sha(text)
        p = self.blobs / f"{h}.txt"
        with self._blob_lock:
            if not p.exists():
                _retry(lambda: p.write_bytes(text.encode("utf-8")))
        return h

    def get_blob(self, h):
        return (self.blobs / f"{h}.txt").read_text(encoding="utf-8")


def valid_records(recs):
    """Records of one game that count: those outside any step, plus the records of the LAST attempt of each step
    that reached step_done. A crashed attempt (a step_start with no step_done) is dropped, even if the step was run
    again later. Dropped attempts stay in the room, and their calls still count in cost."""
    blocks, done, out = {}, set(), []
    for r in recs:
        t, st = r["type"], r.get("step")
        if st is None:
            out.append(r)
        elif t == "step_start":
            blocks[st] = []
        elif t == "step_done":
            done.add(st)
        else:
            blocks.setdefault(st, []).append(r)
    for st in done:
        out.extend(blocks.get(st, []))
    return sorted(out, key=lambda r: r["seq"])


def dropped_attempts(recs):
    """How many step attempts were dropped (a step_start with no step_done after it) in one game's records."""
    open_steps, n = {}, 0
    for r in recs:
        t, st = r["type"], r.get("step")
        if st is None:
            continue
        if t == "step_start":
            if st in open_steps:
                n += 1
            open_steps[st] = True
        elif t == "step_done":
            open_steps.pop(st, None)
    return n + len(open_steps)
