"""Counts only: how far each run has got, and whether the answers files are whole. Reporting only; not part of either sealed design.
  python progress.py
"""
import json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"<home>\Workbench\overnight-2026-10-05")


def count(path, want):
    if not path.exists():
        return f"{path.name}: not started"
    raw = path.read_bytes()
    whole = raw.endswith(b"\n") or not raw
    rows = [json.loads(l) for l in raw.decode("utf-8").splitlines() if l.strip()]
    by = Counter(r["arm"] for r in rows)
    codes = Counter(r["code"] for r in rows)
    bad = [c for c in codes if c in ("backend_error", "timeout")]
    dup = len(rows) - len({(r["arm"], r["id"]) for r in rows})
    return (f"{path.name}: {len(rows)} of {want} lines | by arm {dict(sorted(by.items()))} | duplicates {dup} | whole last line: {whole} | "
            f"no-answer codes: { {c: codes[c] for c in bad} } | median s/call "
            f"{sorted(r['seconds'] for r in rows)[len(rows) // 2] if rows else None}")


if __name__ == "__main__":
    print(count(ROOT / "e1" / "results" / "answers-e1-local.jsonl", 300))
    print(count(ROOT / "e2" / "results" / "answers-e2-local.jsonl", 486))
    for p in (ROOT / "PAUSE",):
        print(f"{p.name}: {'EXISTS' if p.exists() else 'no'}")
