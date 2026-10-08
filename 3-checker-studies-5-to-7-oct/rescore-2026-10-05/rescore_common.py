"""Shared helpers for the 2026-10-05 re-score: Q3 (run 3 certainty) and Q4 (run 2 quotes).
Design: DESIGN.md, sealed (SHA-256 file stamped by FreeTSA) before any result is computed.
Reads files that already exist. Makes no model calls and no network calls.
Prints and writes ids, labels, counts and rates only, never item text (claims, log lines, quotes).
"""
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
WORK = Path(r"C:\Users\joshd\Workbench")
SEALED = WORK / "chatgpt-review-2026-10-04"
LEM = WORK / "lemonade-entry-2026-10-05"

PATHS = {
    "bank": SEALED / "completion-claims-001-300.jsonl",
    "batch5": SEALED / "JOB3-BATCH-5.jsonl",
    "run2_local": LEM / "run2" / "results" / "answers-run2-local.jsonl",
    "run2_fast": LEM / "run2" / "results" / "answers-run2-fast.jsonl",
    "run3": LEM / "run3" / "results" / "answers-run3.jsonl",
    "score_run3": LEM / "run3" / "results" / "score-run3.json",
    "score_run2_local": LEM / "run2" / "results" / "score-run2-local.json",
    "score_run2_fast": LEM / "run2" / "results" / "score-run2-fast.json",
    "src_receipts_model": WORK / "swarm-receipts-public" / "receipts_model.py",
    "src_run2": LEM / "run2" / "run2.py",
    "src_run_pair": LEM / "run_pair.py",
    "src_run3": LEM / "run3" / "run3.py",
}
EXPECTED_SHA256 = {
    "bank": "edb897f7b6d7df41a14eb37e4f6079ade036dabdec6d140d82dec6147199593a",
    "batch5": "468e2ff2deab7cf50cf31fee0a35e832f945a59a787a5703252619b03f19cda1",
    "run2_local": "ba5303a247fe5a805064261c698e0958a36b20d6ec3791c69a1fb48f9c09eed5",
    "run2_fast": "7f634ad3a0ae7874bdecb81aec31096db7a2f6cbbfe4f597bd653c22092f284e",
    "run3": "df9a399dfd2959e30a226c96225495adc3435cd8ea2a07ccdd04eb4417eea9b4",
    "score_run3": "c9e2ad26fca75f3a55812563540999eca69393e599673175a237df44e6ee357f",
    "score_run2_local": "944afdd9cc9d1a4ad970df47544b391cccb7cc63c4abd0dfe86266272d8cdf23",
    "score_run2_fast": "67f26941f3ec510cca5022accd15aab0d4f161fa150308075a12a8fb20c3505d",
    "src_receipts_model": "b0842ecd738554719443269a93665d0e8045c3244a20587e0455b82568169942",
    "src_run2": "bd8decc1ddb4bc10ebcd2bc91ac0aab8c1a94d29dde6e001f456d0f119a1d29d",
    "src_run_pair": "3d8e8292ebd48b1278549988d275bac3a396ed99ccaa1e71a1df5b0d56468bdb",
    "src_run3": "5a4d47b4f8e1ca44fdc5af3b462f914753fc17fe5a55cadf2bc1682f5a90aa33",
}
SEAL_FILES = ("DESIGN.md", "rescore_common.py", "q3_certainty.py", "q4_quote_decides.py", "selftest.py")

FRESH = [f"{i:03d}" for i in range(161, 301)]
PRIMARY = [f"{i:03d}" for i in range(201, 301)]
SETS = {"fresh_161_300": FRESH, "primary_201_300": PRIMARY}


# ---- integrity ---------------------------------------------------------------
def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def check_inputs():
    """Every input must still have the hash written in DESIGN.md; otherwise stop."""
    out, bad = {}, []
    for key, want in EXPECTED_SHA256.items():
        got = sha256_file(PATHS[key])
        out[key] = {"sha256": got, "matches_design": got == want}
        if got != want:
            bad.append(key)
    if bad:
        raise SystemExit("STOP: input hash differs from DESIGN.md for: " + ", ".join(bad))
    return out


def check_seal(seal_name="DESIGN-SHA256.txt"):
    """The design and the scripts must be sealed, and unchanged since the seal."""
    seal = HERE / seal_name
    if not seal.exists():
        raise SystemExit(f"STOP: {seal_name} not found. Seal the design before running on the real data.")
    listed = {}
    for line in seal.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            listed[parts[1].lstrip("*").strip()] = parts[0].lower()
    files = {name: (sha256_file(HERE / name) == h) for name, h in listed.items()}
    missing = [n for n in SEAL_FILES if n not in listed]
    if missing or not all(files.values()):
        raise SystemExit(f"STOP: seal check failed. missing from seal file: {missing}; changed since seal: "
                         f"{[n for n, ok in files.items() if not ok]}")
    return {"seal_file": seal_name, "seal_file_sha256": sha256_file(seal), "files_match": files}


# ---- reading -----------------------------------------------------------------
def read_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def norm_truth(t):
    return "not shown" if t == "not_shown" else t


def norm_verdict(v):
    if v is None:
        return None
    return "not shown" if v == "not_shown" else v


def load_bank():
    return {it["id"]: it for it in read_jsonl(PATHS["bank"])}


def last_per_key(rows):
    """One record per (arm, id): the last one wins, as in run2.py and run3.py. Returns (dict, number of duplicates)."""
    by, dups = {}, 0
    for r in rows:
        key = (r["arm"], r["id"])
        if key in by:
            dups += 1
        by[key] = r
    return by, dups


def get(d, *keys):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


# ---- statistics --------------------------------------------------------------
def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def frac(k, n):
    """k out of n with its own n, and the Wilson 95% interval."""
    ci = wilson(k, n)
    return {"k": k, "n": n, "rate": (round(k / n, 4) if n else None),
            "ci95": ([round(ci[0], 4), round(ci[1], 4)] if ci else None)}


def newcombe(k1, n1, k2, n2, z=1.96):
    """Difference p1 - p2 with Newcombe's hybrid-score interval (method 10)."""
    if n1 == 0 or n2 == 0:
        return None
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1, z)
    l2, u2 = wilson(k2, n2, z)
    d = p1 - p2
    lo = d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return {"k1": k1, "n1": n1, "k2": k2, "n2": n2, "diff": round(d, 4), "ci95": [round(lo, 4), round(hi, 4)]}


def diff_of(a, b):
    """Newcombe difference between two frac() dicts, a minus b."""
    return newcombe(a["k"], a["n"], b["k"], b["n"])


# ---- the reader's checks, mirrored (receipts_model.py, sha256 b0842ecd...) -----
ANSWER = {"shown": "shown", "contradicted": "contradicted", "not_shown": "not shown"}


def parse_reply(text):
    """Mirror of receipts_model.parse_reply."""
    if not isinstance(text, str) or not text.strip():
        return None, "unparseable_reply"
    candidate = text.strip()
    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", candidate, re.S)
    if fence:
        candidate = fence.group(1)
    try:
        value = json.loads(candidate)
    except ValueError:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start < 0 or end <= start:
            return None, "unparseable_reply"
        try:
            value = json.loads(candidate[start:end + 1])
        except ValueError:
            return None, "unparseable_reply"
    if not isinstance(value, dict):
        return None, "invalid_reply"
    return value, ""


def normalize_verdict(value):
    """Mirror of receipts_model.normalize_verdict."""
    if not isinstance(value, str):
        return None
    verdict = re.sub(r"[\s-]+", "_", value.strip().lower())
    return verdict if verdict in ANSWER else None


class Turn:
    """Stand-in for receipts_model.ShownTurn: only what the verbatim gate uses."""
    __slots__ = ("label", "row_id", "cmd", "out")

    def __init__(self, label, row_id, cmd, out):
        self.label, self.row_id, self.cmd, self.out = label, row_id, cmd, out


def turns_for(item):
    """Mirror of run_pair.turns_for: labels T1, T2, ...; the output is the whole output text."""
    res = []
    for i, t in enumerate(item["turns"], 1):
        res.append(Turn(f"T{i}", f"{item['id']}:{i}", str(t.get("cmd") or ""), str(t.get("output") or "")))
    return res


def normalize_turn_id(value, turns):
    """Mirror of receipts_model.normalize_turn_id."""
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip().strip("[]()").strip()
    if re.fullmatch(r"\d{1,3}", text):
        text = "T" + text
    elif re.fullmatch(r"[tT]\d{1,3}", text):
        text = text.upper()
    for turn in turns:
        if text in (turn.label, turn.row_id):
            return turn
    return None


def verbatim_gate(reply_text, turns):
    """Re-derive the verbatim gate of receipts_model.verify from the reply text alone.
    passed = valid shown/contradicted verdict, a cited turn that exists, a non-empty string quote,
    and the stripped quote found in that turn's output text. (The reader-instruction test that
    verify() runs just before the gate is not mirrored; any resulting disagreement is reported.)"""
    value, _ = parse_reply(reply_text)
    if value is None:
        return {"stage": "parse", "passed": False}
    verdict = normalize_verdict(value.get("verdict"))
    if verdict is None:
        return {"stage": "verdict", "passed": False}
    if verdict == "not_shown":
        return {"stage": "model_not_shown", "passed": False, "verdict": verdict}
    turn = normalize_turn_id(value.get("turn_id"), turns)
    if turn is None:
        return {"stage": "turn", "passed": False, "verdict": verdict}
    quote = value.get("quote")
    if not isinstance(quote, str):
        return {"stage": "quote_type", "passed": False, "verdict": verdict, "turn": turn}
    quote = quote.strip()
    if not quote:
        return {"stage": "empty_quote", "passed": False, "verdict": verdict, "turn": turn}
    return {"stage": "verbatim", "passed": quote in turn.out, "verdict": verdict, "turn": turn, "quote": quote}


# ---- writing -----------------------------------------------------------------
def write_new_json(stem, obj, folder=None):
    """Write <stem>-v1.json, or the next free version. Never overwrites an existing file."""
    folder = Path(folder) if folder else HERE
    text = json.dumps(obj, indent=1, ensure_ascii=False)
    k = 1
    while True:
        p = folder / f"{stem}-v{k}.json"
        try:
            with open(p, "x", encoding="utf-8") as f:
                f.write(text)
            return p
        except FileExistsError:
            k += 1


def meta(script_name, run_at, seal_info, inputs_info):
    return {"script": script_name, "script_sha256": sha256_file(HERE / script_name),
            "common_sha256": sha256_file(HERE / "rescore_common.py"),
            "design_sha256": sha256_file(HERE / "DESIGN.md"), "run_at": run_at,
            "python": sys.version.split()[0], "platform": sys.platform, "seal": seal_info, "inputs": inputs_info}


def compare(mine, stored):
    return {"mine": mine, "stored": stored, "agree": mine == stored}
