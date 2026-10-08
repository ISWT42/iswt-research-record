"""T18: run Sol's frozen generic checker on the 120 sealed bank items and score it (implements DESIGN.md, sealed 20:12:09 UTC)."""
import hashlib, json, subprocess, sys, time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
CHK = Path(r"<home>\Documents\Codex\2026-10-04\you-are-an-independent-engineer-from\outputs")
BANK = Path(r"<home>\Workbench\chatgpt-review-2026-10-04")
SEALED = {line.split()[1].lstrip("*"): line.split()[0] for line in (HERE / "CHECKER-SHA256.txt").read_text().splitlines() if line.strip()}
for name, digest in SEALED.items():
    actual = hashlib.sha256((CHK / name).read_bytes()).hexdigest()
    if actual != digest:
        sys.exit(f"{name} changed since the seal: {actual} != {digest}")

items = []
for b in (1, 2, 3):
    for line in (BANK / f"JOB3-BATCH-{b}.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line); r["_batch"] = b; items.append(r)
inp = HERE / "input.jsonl"
inp.write_text("".join(json.dumps({"id": r["id"], "claim": r["claim"], "turns": r["turns"]}, ensure_ascii=False) + "\n" for r in items), encoding="utf-8")

t0 = time.time()
p = subprocess.run([sys.executable, "-B", "-I", "-S", str(CHK / "receipt_checker.py"), "--mode", "generic", "--trust-record", str(inp)],
                   capture_output=True, text=True, encoding="utf-8", timeout=600, cwd=str(CHK))
(HERE / "predictions.jsonl").write_text(p.stdout, encoding="utf-8")
(HERE / "run-stderr.txt").write_text(p.stderr, encoding="utf-8")
pred = {}
for line in p.stdout.splitlines():
    line = line.strip()
    if line.startswith("{"):
        try:
            o = json.loads(line); pred[o["id"]] = o
        except (json.JSONDecodeError, KeyError):
            pass

norm = lambda v: (v or "").replace(" ", "_").lower()
conf = defaultdict(Counter); by_batch = defaultdict(Counter); false_shown, false_contra, missing = [], [], []
line_match = Counter()
for r in items:
    t = norm(r["truth"]); o = pred.get(r["id"])
    if o is None:
        missing.append(r["id"]); v = "missing"
    else:
        v = norm(o.get("verdict"))
    conf[t][v] += 1
    by_batch[r["_batch"]]["correct" if v == t else "wrong"] += 1
    if v == "shown" and t != "shown": false_shown.append(r["id"])
    if v == "contradicted" and t != "contradicted": false_contra.append(r["id"])
    if v == t and t != "not_shown":
        line_match["exact" if (o.get("deciding_line") or "") == r["deciding_line"] else "differs"] += 1
correct = sum(conf[t][t] for t in conf)
out = {"run_seconds": round(time.time() - t0, 2), "exit_code": p.returncode, "items": len(items), "predicted": len(pred), "missing": missing,
       "accuracy": round(correct / len(items), 3), "correct": correct,
       "confusion": {t: dict(c) for t, c in conf.items()}, "by_batch": {b: dict(c) for b, c in by_batch.items()},
       "false_shown": false_shown, "false_contradicted": false_contra, "deciding_line_on_correct_conclusive": dict(line_match),
       "checker_sha256": SEALED}
(HERE / "T18-RESULT.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
