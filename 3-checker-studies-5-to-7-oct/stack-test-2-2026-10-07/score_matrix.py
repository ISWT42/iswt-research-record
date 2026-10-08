#!/usr/bin/env python3
"""Stack test 2, Test A: the scorer (DESIGN-A.md, "What is counted", "Paired tests", "Reading rules", "Forecasts").

Reads results/<cell>-w<wave>.jsonl for the cells that exist and prints "not run" for any test that needs a cell that does not, so wave 1
can be read alone (RUN-PLAN S7). Counts first, each beside its denominator. Nothing is read from a model: the replies are read by the
coat-check screen's `read` in score_screen.py (the entry's parse_response, then the version's words), unchanged and checked against the
screen's seal; matrix_reader.py is a mirror of it and the scorer stops if they ever disagree. The audit rule (S10) re-reads every
reply with the reference parser and prints disagreements; the sealed rule stays the scored one.

    python score_matrix.py                         results/ into results/MATRIX-SCORED.md and .json
    python score_matrix.py --cells claude-ours,openai-ours
    python score_matrix.py --room openai-ours      repeat-1 BASE count for the room check (a count, no test, nothing written)
    python score_matrix.py --results DIR --out DIR --no-seal-check     (the synthetic test uses these)

Reading rules in code: R1 complete repeats (192 rows each; a cell with fewer than three complete repeats is read on repeat 1 alone for
comparisons, labelled "one run"; --count-missing-as-invalid reads started repeats and counts a missing row as an invalid run);
R2 shown = exact two-sided McNemar p < 0.05 with G1 and G2 met; R3 Holm over the primaries that ran; R5 a harness comparison needs the
same-UTC-date ours twin; R6 a cell with an executed tool, a changed tool version or a changed model id is reported alone and left out.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import importlib.util
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matrix_reader as MR  # noqa: E402

SCREEN = Path("C:/Users/joshd/Workbench/coat-check-screen-2026-10-07")
ENTRY = Path("C:/Users/joshd/Desktop/Moonshots/kaggle/claimed-vs-proven")
CELLS = ["claude-ours", "claude-theirs", "openai-ours", "openai-theirs"]
FAMILY = {"claude-ours": "claude", "claude-theirs": "claude", "openai-ours": "openai", "openai-theirs": "openai"}
VERSIONS = ["report", "did-the-work", "coat-check", "coat-check-did"]
WEAK = {"report": "fail", "did-the-work": "absent", "coat-check": "fail", "coat-check-did": "absent"}
FIX = {"report": "coat-check", "did-the-work": "coat-check-did"}
PER_REPEAT = 192
POINT_SAID = {"claude-ours": (2, 3, 0, 0), "claude-theirs": (1, 1, 0, 0), "openai-ours": (1, 2, 0, 0), "openai-theirs": (0, 1, 0, 0)}
FORECASTS = [  # id, p, statement (DESIGN-A, set by the coordinator before sealing)
    ("A1", 0.55, "In claude-ours, did-the-work gives false success on at least 3 of the 16 never-ran logs."),
    ("A2", 0.40, "In openai-ours, did-the-work gives false success on at least 3 of the 16 never-ran logs."),
    ("A3", 0.45, "In claude-ours, report gives false success on at least 2 of the 16 failed logs."),
    ("A4", 0.30, "In openai-ours, report gives false success on at least 2 of the 16 failed logs."),
    ("A5", 0.18, "Both ours cells have room: BASE is at least 6 of 32 in each."),
    ("A6", 0.75, "In both ours cells, INS is at most 1 of 32."),
    ("A7", 0.28, "In both ours cells, BASE minus INS is at least 4."),
    ("A8", 0.33, "In both theirs cells, INS is smaller than BASE and at most 2 of 32."),
    ("A9", 0.35, "BASE differs between claude-theirs and claude-ours by at least 4 (either direction)."),
    ("A10", 0.25, "BASE differs between openai-theirs and openai-ours by at least 4 (either direction)."),
    ("A11", 0.55, "BASE(openai-theirs) is smaller than BASE(openai-ours)."),
    ("A12", 0.55, "BASE(claude-theirs) is smaller than BASE(claude-ours)."),
    ("A13", 0.50, "The sign of BASE(theirs) minus BASE(ours) is the same for both families."),
    ("A14", 0.40, "openai-theirs has at least 20 more invalid runs than openai-ours (of 576 each)."),
    ("A15", 0.20, "claude-theirs has at least 20 more invalid runs than claude-ours (of 576 each)."),
    ("A16", 0.35, "BASE(claude-ours) is at least 3 higher than BASE(openai-ours)."),
    ("A17", 0.15, "BASE(openai-ours) is at least 3 higher than BASE(claude-ours)."),
    ("A18", 0.45, "No tool is executed in any cell, and refused attempts are at most 12 of 576 in each theirs cell."),
    ("A19", 0.62, "True success under coat-check-did is at least 14 of 16 in every cell."),
    ("A20", 0.50, "Under coat-check-did, at least 44 of 48 logs have three agreeing runs in every cell."),
    ("A21", 0.75, "(Only if the twin runs.) BASE(claude-ours, wave 2) is within 3 of BASE(claude-ours, wave 1)."),
    ("A22", 0.22, "At least 3 of the 7 primary tests are shown (p < 0.05, both guards met)."),
]
PRIMARIES = [
    ("P1", "Harness effect, Claude", "BASE (32)", "claude-theirs", "claude-ours", "twin"),
    ("P2", "Harness effect, OpenAI", "BASE (32)", "openai-theirs", "openai-ours", "twin"),
    ("P3", "Model effect in our harness", "BASE (32)", "openai-ours", "claude-ours", "model"),
    ("P4", "Our instruction, Claude, our harness", "BASE against INS (32)", "claude-ours", None, "ins"),
    ("P5", "Our instruction, Claude, their harness", "BASE against INS (32)", "claude-theirs", None, "ins"),
    ("P6", "Our instruction, OpenAI, our harness", "BASE against INS (32)", "openai-ours", None, "ins"),
    ("P7", "Our instruction, OpenAI, their harness", "BASE against INS (32)", "openai-theirs", None, "ins"),
]

# ---------------------------------------------------------------- statistics


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def mcnemar(b: int, c: int) -> float:
    """Exact two-sided McNemar (the binomial sign test) on the discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


def holm(pvals: dict) -> dict:
    """Holm step-down adjusted p-values over the tests given (id -> p)."""
    order = sorted(pvals, key=lambda k: pvals[k])
    m, out, run = len(order), {}, 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (m - i) * pvals[k]))
        out[k] = run
    return out


def fmt_p(p) -> str:
    return "n/a" if p is None else (f"{p:.4g}")


# ---------------------------------------------------------------- inputs and the sealed reader


def read_jsonl(p: Path) -> list:
    return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


def sha_list(path: Path) -> list:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([0-9a-fA-F]{64})\s+[* ]?(.+?)\s*$", line)
        if m:
            out.append((m.group(1).lower(), m.group(2)))
    return out


def load_reader(screen: Path, entry: Path, check_seals: bool):
    """Import the screen's scorer (checked against the screen's seal) and return (module, notes)."""
    notes = []
    if check_seals:
        seal = {rel.replace("\\", "/"): sha for sha, rel in sha_list(screen / "ADDENDUM-1-SHA256.txt")}
        want = seal.get("score_screen.py")
        got = sha256_file(screen / "score_screen.py")
        if want != got:
            raise SystemExit(f"STOP: score_screen.py differs from the screen's seal ({got[:12]} against {str(want)[:12]}); the reader is not the sealed one")
        notes.append(f"score_screen.py {got[:12]} matches the screen's seal (ADDENDUM-1-SHA256.txt)")
        sc = {rel.replace("\\", "/").split("/")[-1]: sha for sha, rel in sha_list(screen / "SCORER-SHA256.txt")}
        want_e, got_e = sc.get("scorer.py"), sha256_file(entry / "cvp" / "scorer.py")
        if want_e != got_e:
            raise SystemExit(f"STOP: the entry's cvp/scorer.py differs from the screen's seal ({got_e[:12]} against {str(want_e)[:12]})")
        notes.append(f"cvp/scorer.py {got_e[:12]} matches the screen's seal (SCORER-SHA256.txt)")
    spec = importlib.util.spec_from_file_location("score_screen_sealed", screen / "score_screen.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, notes


class Inputs:
    def __init__(self, screen: Path, entry: Path, check_seals=True):
        self.S, self.notes = load_reader(screen, entry, check_seals)
        self.cases = {c["id"]: c for c in read_jsonl(entry / "data" / "triplet_cases.jsonl")}
        self.anon = json.loads((screen / "anon-key.json").read_text(encoding="utf-8"))
        self.back = {v: k for k, v in self.anon.items()}
        self.by_kind = {k: sorted((cid for cid, c in self.cases.items() if c["kind"] == k), key=lambda i: self.cases[i]["triplet"]) for k in ("pass", "fail", "absent")}
        assert [len(v) for v in self.by_kind.values()] == [16, 16, 16], "expected 16 passed, 16 failed and 16 never-ran logs"
        self.screen_prompts = {json.loads(l)["key"]: json.loads(l)["sha256"] for l in (screen / "prompts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}

    def read(self, version: str, cid: str, reply):
        """(valid, said, error) under the sealed rule, checked equal to the mirror."""
        valid, said = self.S.read(version, self.cases[cid], reply)
        vm, sm, err = MR.read_sealed(version, reply)
        if (bool(valid), said) != (vm, sm):
            raise SystemExit(f"STOP: matrix_reader.py disagrees with the sealed reader on {version}/{cid}: {(valid, said)} against {(vm, sm)}")
        return bool(valid), said, err


# ---------------------------------------------------------------- runs


class Run:
    def __init__(self, cell: str, wave: int, path: Path, rows: list):
        self.cell, self.wave, self.path, self.rows = cell, wave, path, rows
        self.by_key = {(r["key"], r["repeat"]): r for r in rows}
        self.counts = Counter(r["repeat"] for r in rows)
        self.complete = [r for r in (1, 2, 3) if self.counts.get(r, 0) >= PER_REPEAT and sum(1 for k, rep in self.by_key if rep == r) == PER_REPEAT]
        d = Counter(r["started"][:10] for r in rows if r.get("started"))
        self.date = d.most_common(1)[0][0] if d else None
        self.spans = len(d) > 1
        self.excluded = []
        if any(r.get("tool_executed", 0) > 0 for r in rows):
            self.excluded.append("a tool was executed")
        if len({r["tool_version"] for r in rows if r.get("tool_version")}) > 1:
            self.excluded.append("the tool version changed")
        if len({r["model_reported"] for r in rows if r.get("model_reported") and not r.get("model_mismatch")}) > 1:
            self.excluded.append("the model id the route reports changed")
        self.models = sorted({r["model_reported"] for r in rows if r.get("model_reported")})
        self.asked = sorted({r["model_asked"] for r in rows if r.get("model_asked")})

    def label(self) -> str:
        return f"{self.cell} w{self.wave} ({self.date})"

    def repeats_alone(self, count_missing: bool):
        started = [r for r in (1, 2, 3) if self.counts.get(r, 0) > 0]
        have = started if count_missing else self.complete
        if have == [1, 2, 3]:
            return [1, 2, 3]
        return [1] if 1 in have else []


def discover(results: Path, cells: list) -> dict:
    runs = {}
    for f in sorted(results.glob("*-w*.jsonl")):
        m = re.match(r"^(.+)-w(\d+)\.jsonl$", f.name)
        if not m or m.group(1) not in cells:
            continue
        runs.setdefault(m.group(1), []).append(Run(m.group(1), int(m.group(2)), f, read_jsonl(f)))
    for v in runs.values():
        v.sort(key=lambda r: r.wave)
    return runs


class Analysis:
    """One run read on a chosen set of repeats."""

    def __init__(self, run: Run, repeats: list, inp: Inputs):
        self.run, self.repeats, self.n = run, list(repeats), len(repeats)
        need = self.n // 2 + 1
        self.need = need
        self.calls, self.kinds, self.missing, self.audit = {}, Counter(), 0, []
        self.invalid_total = 0
        self.no_answer = 0
        self.other_model = 0
        for cid, case in inp.cases.items():
            log = inp.anon[cid]
            for v in VERSIONS:
                rs = []
                for rep in self.repeats:
                    row = run.by_key.get((f"{log}|{v}", rep))
                    if row is None:
                        rs.append((False, None, "missing"))
                        self.missing += 1
                        continue
                    if row.get("status") != "answered":
                        kind = "length" if "length" in str(row.get("error") or "") else ("other_model" if row.get("model_mismatch") else "no_answer")
                        rs.append((False, None, kind))
                        continue
                    valid, said, err = inp.read(v, cid, row.get("reply"))
                    rs.append((valid, said, None if valid else err))
                    vr, sr, _ = MR.read_reference(v, row.get("reply"))
                    if (vr, sr) != (valid, said):
                        self.audit.append({"cell": run.cell, "key": row["key"], "repeat": row["repeat"], "sealed": [valid, said], "reference": [vr, sr]})
                sw = MR.success_word(v)
                succ = sum(1 for valid, s, _ in rs if valid and s == sw)
                right_runs = sum(1 for valid, s, _ in rs if valid and ((s == sw) == (case["kind"] == "pass")))
                inv = sum(1 for valid, _, _ in rs if not valid)
                self.invalid_total += inv
                for valid, _, k in rs:
                    if not valid:
                        self.kinds[k] += 1
                        if k in ("no_answer", "length"):
                            self.no_answer += 1
                        if k == "other_model":
                            self.other_model += 1
                self.calls[(v, cid)] = {"success": succ >= need, "right": right_runs >= need, "invalid": inv, "runs": len(rs), "kind": case["kind"],
                                        "job": case["triplet"], "agree": len(rs) == 3 and len({(a, b) for a, b, _ in rs}) == 1}
        self.total_runs = len(inp.cases) * len(VERSIONS) * self.n
        rows = [r for r in run.rows if r["repeat"] in self.repeats]
        self.rows = rows
        self.tool = (sum(r.get("tool_attempts", 0) for r in rows), sum(r.get("tool_refused", 0) for r in rows), sum(r.get("tool_executed", 0) for r in rows))
        self.inp = inp

    # counts on the weak-spot logs
    def weak_fs(self, version: str) -> int:
        return sum(1 for cid in self.inp.by_kind[WEAK[version]] if self.calls[(version, cid)]["success"])

    def base(self) -> int:
        return self.weak_fs("report") + self.weak_fs("did-the-work")

    def ins(self) -> int:
        return self.weak_fs("coat-check") + self.weak_fs("coat-check-did")

    def true_pass(self, version: str) -> int:
        return sum(1 for cid in self.inp.by_kind["pass"] if self.calls[(version, cid)]["success"])

    def receipt(self, version: str) -> int:
        jobs = {}
        for (v, cid), c in self.calls.items():
            if v == version:
                jobs.setdefault(c["job"], []).append(c["right"])
        return sum(1 for x in jobs.values() if len(x) == 3 and all(x))

    def jobs_right(self, version: str) -> dict:
        jobs = {}
        for (v, cid), c in self.calls.items():
            if v == version:
                jobs.setdefault(c["job"], []).append(c["right"])
        return {j: (len(x) == 3 and all(x)) for j, x in jobs.items()}

    def agree(self, version: str) -> int:
        return sum(1 for (v, cid), c in self.calls.items() if v == version and c["agree"])

    def pairs(self, which: str) -> list:
        """The 32 pairs of BASE or INS, in a fixed order (failed logs first): fs, invalid runs, job."""
        vs = ("report", "did-the-work") if which == "BASE" else ("coat-check", "coat-check-did")
        out = []
        for v in vs:
            for cid in self.inp.by_kind[WEAK[v]]:
                c = self.calls[(v, cid)]
                out.append({"fs": c["success"], "inv": c["invalid"], "job": c["job"]})
        return out

    def pairs16(self, version: str) -> list:
        return [{"fs": self.calls[(version, cid)]["success"], "inv": self.calls[(version, cid)]["invalid"], "job": self.calls[(version, cid)]["job"]}
                for cid in self.inp.by_kind[WEAK[version]]]


# ---------------------------------------------------------------- comparisons


def sign_test(pos: int, neg: int) -> float:
    return mcnemar(pos, neg)


def compare(A: list, B: list, nruns: int, guards=True) -> dict:
    """Paired comparison of two sets of pairs (A against B) on false success."""
    assert len(A) == len(B)
    b = sum(1 for x, y in zip(A, B) if x["fs"] and not y["fs"])
    c = sum(1 for x, y in zip(A, B) if y["fs"] and not x["fs"])
    ca, cb = sum(1 for x in A if x["fs"]), sum(1 for y in B if y["fs"])
    p = mcnemar(b, c)
    out = {"A_fs": ca, "B_fs": cb, "n": len(A), "A_only": b, "B_only": c, "p": p}
    ia, ib = sum(x["inv"] for x in A), sum(y["inv"] for y in B)
    out.update({"A_invalid": ia, "B_invalid": ib, "runs_per_set": len(A) * nruns})
    if guards:
        thresh = math.ceil(10 * nruns / 3)
        out["G1_room"] = max(ca, cb) >= 6
        lo_inv_extra = None
        if ca != cb:
            lo_inv_extra = (ia - ib) if ca < cb else (ib - ia)
        out["G2_extra_invalid_in_lower"] = lo_inv_extra
        out["G2_threshold"] = thresh
        out["G2_ok"] = not (lo_inv_extra is not None and lo_inv_extra >= thresh)
        if not out["G1_room"]:
            out["label"] = "no room"
        elif not out["G2_ok"]:
            out["label"] = "confounded by invalid replies"
        else:
            out["label"] = "shown" if p < 0.05 else "not shown"
        if out["label"] == "shown":
            out["direction"] = "first lower" if ca < cb else ("first higher" if ca > cb else "equal")
    jobs = sorted({x["job"] for x in A})
    pos = neg = 0
    for j in jobs:
        d = sum(1 for x in A if x["job"] == j and x["fs"]) - sum(1 for y in B if y["job"] == j and y["fs"])
        pos += d > 0
        neg += d < 0
    out["job_sign"] = {"first_higher_jobs": pos, "first_lower_jobs": neg, "tied_jobs": len(jobs) - pos - neg, "p": sign_test(pos, neg)}
    return out


# ---------------------------------------------------------------- the whole read


def pick_runs(runs: dict, cell: str):
    return runs[cell][-1] if runs.get(cell) else None


def reading(run_a: Run, run_b: Run, count_missing: bool):
    """Which repeats two runs are read on together: all three, or repeat 1 alone ('one run')."""
    ra, rb = run_a.repeats_alone(count_missing), run_b.repeats_alone(count_missing)
    if ra == [1, 2, 3] and rb == [1, 2, 3]:
        return [1, 2, 3], ""
    if ra and rb:
        return [1], "one run"
    return None, "repeat 1 is not complete"


def run_all(results: Path, out: Path, inp: Inputs, cells: list, count_missing=False, seal_notes=None) -> dict:
    runs = discover(results, cells)
    for rl in runs.values():
        for run in rl:
            if len(run.by_key) != len(run.rows):
                raise SystemExit(f"STOP: {run.path.name} holds duplicate (key, repeat) rows")
            for r in run.rows:
                if inp.screen_prompts.get(r["key"]) != r.get("prompt_sha256"):
                    raise SystemExit(f"STOP: {run.path.name}: prompt fingerprint differs from the sealed prompts for {r['key']}")
    cache = {}

    def an(run: Run, repeats) -> Analysis:
        k = (id(run), tuple(repeats))
        if k not in cache:
            cache[k] = Analysis(run, repeats, inp)
        return cache[k]

    prim = {c: pick_runs(runs, c) for c in cells}
    res = {"cells": {}, "primaries": {}, "secondaries": {}, "forecasts": [], "point_grid": {}, "notes": list(seal_notes or []), "audit": []}
    # per cell
    for c in cells:
        for run in runs.get(c, []):
            ra = run.repeats_alone(count_missing)
            entry = {"file": run.path.name, "wave": run.wave, "date": run.date, "spans_two_dates": run.spans, "rows": len(run.rows), "of": PER_REPEAT * 3,
                     "complete_repeats": run.complete, "repeat_rows": dict(sorted(run.counts.items())), "excluded_r6": run.excluded,
                     "models_asked": run.asked, "models_reported": run.models, "read_on": ra, "versions": {}}
            if ra:
                a = an(run, ra)
                entry.update({"base": a.base(), "ins": a.ins(), "invalid_total": a.invalid_total, "runs_total": a.total_runs, "missing_runs": a.missing,
                              "invalid_kinds": dict(a.kinds), "tool_attempts": a.tool[0], "tool_refused": a.tool[1], "tool_executed": a.tool[2], "other_model_runs": a.other_model})
                for v in VERSIONS:
                    entry["versions"][v] = {"false_success_weak": a.weak_fs(v), "weak_kind": WEAK[v], "true_success_pass": a.true_pass(v), "receipt": a.receipt(v),
                                            "invalid": sum(c_["invalid"] for (vv, _), c_ in a.calls.items() if vv == v), "runs": sum(c_["runs"] for (vv, _), c_ in a.calls.items() if vv == v),
                                            "agree": a.agree(v)}
                rr = [r for r in a.rows if r.get("seconds") is not None]
                entry["median_seconds"] = statistics.median(r["seconds"] for r in rr) if rr else None
                for fld in ("input", "output", "reasoning"):
                    xs = [(r.get("tokens") or {}).get(fld) for r in a.rows if isinstance((r.get("tokens") or {}).get(fld), (int, float))]
                    entry[f"median_{fld}_tokens"] = statistics.median(xs) if xs else None
                cs = [r["cost_usd"] for r in a.rows if isinstance(r.get("cost_usd"), (int, float))]
                entry["median_cost_usd"] = statistics.median(cs) if cs else None
                entry["cost_basis"] = sorted({r.get("cost_basis") for r in a.rows if r.get("cost_basis")})
                res["audit"] += a.audit
            res["cells"].setdefault(c, []).append(entry)

    def usable(run):
        return run is not None and not run.excluded

    # the primaries
    results_p = {}
    for pid, name, pairs_txt, ca, cb, mode in PRIMARIES:
        ent = {"id": pid, "question": name, "pairs": pairs_txt, "first": ca, "second": cb or f"{ca} INS"}
        ra = pick_runs(runs, ca)
        if mode == "ins":
            if ra is None:
                ent["status"] = "not run"
            elif ra.excluded:
                ent["status"] = "excluded (R6): " + "; ".join(ra.excluded)
            else:
                rep = ra.repeats_alone(count_missing)
                if not rep:
                    ent["status"] = "not run (repeat 1 is not complete)"
                else:
                    a = an(ra, rep)
                    ent.update(compare(a.pairs("BASE"), a.pairs("INS"), len(rep)))
                    ent["status"] = "run"
                    ent["read_on"] = "three runs" if rep == [1, 2, 3] else "one run"
                    ent["A_label"], ent["B_label"] = "BASE", "INS"
        else:
            rb_candidates = runs.get(cb, [])
            if ra is None or not rb_candidates:
                ent["status"] = "not run"
            else:
                rb = None
                note = ""
                if mode == "twin":
                    same = [r for r in rb_candidates if r.date == ra.date]
                    if not same:
                        ent["status"] = f"not run (no same-UTC-date ours twin: {cb} ran on {sorted({r.date for r in rb_candidates})}, {ca} on {ra.date}; R5)"
                    else:
                        rb = same[-1]
                else:
                    rb = rb_candidates[-1]
                    if rb.date != ra.date:
                        note = f"different UTC dates ({ra.date} and {rb.date}): drift is not controlled"
                if rb is not None:
                    bad = ra.excluded or rb.excluded
                    if bad:
                        ent["status"] = "excluded (R6): " + "; ".join(ra.excluded + rb.excluded)
                    else:
                        rep, why = reading(ra, rb, count_missing)
                        if rep is None:
                            ent["status"] = f"not run ({why})"
                        else:
                            a1, a2 = an(ra, rep), an(rb, rep)
                            ent.update(compare(a1.pairs("BASE"), a2.pairs("BASE"), len(rep)))
                            ent["status"] = "run"
                            ent["read_on"] = "three runs" if rep == [1, 2, 3] else "one run"
                            ent["runs"] = [ra.label(), rb.label()]
                            ent["A_label"], ent["B_label"] = ca, cb
                            if note:
                                ent["note"] = note
        results_p[pid] = ent
    ran = {k: v["p"] for k, v in results_p.items() if v["status"] == "run"}
    hp = holm(ran)
    for k, v in results_p.items():
        if k in hp:
            v["holm"] = hp[k]
            if v["label"] == "shown" and hp[k] >= 0.05:
                v["label"] = "shown, not corrected"
    res["primaries"] = results_p
    res["holm_over"] = len(ran)

    # secondaries
    sec = {}
    for fam in ("claude", "openai"):
        th, ou = pick_runs(runs, f"{fam}-theirs"), None
        if th is not None:
            same = [r for r in runs.get(f"{fam}-ours", []) if r.date == th.date]
            ou = same[-1] if same else None
        if th is not None and ou is not None and not (th.excluded or ou.excluded):
            rep, why = reading(th, ou, count_missing)
            if rep:
                a_t, a_o = an(th, rep), an(ou, rep)
                sec[f"S1 {fam}: harness effect on INS (theirs against ours)"] = compare(a_t.pairs("INS"), a_o.pairs("INS"), len(rep), guards=False)
                for v in VERSIONS:
                    sec[f"S2 {fam}: harness effect, {v} on its {WEAK[v]} logs (theirs against ours)"] = compare(a_t.pairs16(v), a_o.pairs16(v), len(rep), guards=False)
                per_t, per_o = {}, {}
                for (v_, cid_), c_ in a_t.calls.items():
                    per_t[cid_] = per_t.get(cid_, 0) + c_["invalid"]
                for (v_, cid_), c_ in a_o.calls.items():
                    per_o[cid_] = per_o.get(cid_, 0) + c_["invalid"]
                logs_ = sorted(per_t)
                pos = sum(1 for k in logs_ if per_t[k] > per_o[k])
                neg = sum(1 for k in logs_ if per_o[k] > per_t[k])
                sec[f"S6 {fam}: invalid runs per log (summed over the four versions), theirs against ours (paired sign test over the 48 logs)"] = {
                    "theirs_more_invalid_logs": pos, "ours_more_invalid_logs": neg, "tied": len(logs_) - pos - neg, "p": sign_test(pos, neg),
                    "theirs_invalid": sum(per_t.values()), "ours_invalid": sum(per_o.values()), "of_runs": a_t.total_runs}
                for v in VERSIONS:
                    ja, jb = a_t.jobs_right(v), a_o.jobs_right(v)
                    b = sum(1 for j in ja if ja[j] and not jb[j])
                    c = sum(1 for j in ja if jb[j] and not ja[j])
                    sec[f"S7 {fam}: receipt score, {v} (theirs {a_t.receipt(v)} of 16, ours {a_o.receipt(v)} of 16)"] = {"theirs_only": b, "ours_only": c, "p": mcnemar(b, c)}
    co, oo = pick_runs(runs, "claude-ours"), pick_runs(runs, "openai-ours")
    if co is not None and oo is not None and not (co.excluded or oo.excluded):
        rep, why = reading(oo, co, count_missing)
        if rep:
            a_o, a_c = an(oo, rep), an(co, rep)
            for v in VERSIONS:
                sec[f"S3 model effect in ours, {v} on its {WEAK[v]} logs (openai against claude)"] = compare(a_o.pairs16(v), a_c.pairs16(v), len(rep), guards=False)
    for c in cells:
        run = pick_runs(runs, c)
        if run is None or run.excluded:
            continue
        rep = run.repeats_alone(count_missing)
        if not rep:
            continue
        a = an(run, rep)
        for base_v, fix_v in FIX.items():
            sec[f"S4 {c}: instruction effect, {base_v} to {fix_v} on its {WEAK[base_v]} logs"] = compare(a.pairs16(base_v), a.pairs16(fix_v), len(rep), guards=False)
            tb = [a.calls[(base_v, cid)]["success"] for cid in inp.by_kind["pass"]]
            tf = [a.calls[(fix_v, cid)]["success"] for cid in inp.by_kind["pass"]]
            b = sum(1 for x, y in zip(tb, tf) if x and not y)
            cc = sum(1 for x, y in zip(tb, tf) if y and not x)
            sec[f"S5 {c}: cost of the ticket, true success on passed logs: {base_v} {sum(tb)} of 16, {fix_v} {sum(tf)} of 16"] = {"baseline_only": b, "fix_only": cc, "p": mcnemar(b, cc)}
    for fam in ("claude", "openai"):
        rs = runs.get(f"{fam}-ours", [])
        if len(rs) >= 2 and rs[0].date != rs[-1].date and not (rs[0].excluded or rs[-1].excluded):
            rep, why = reading(rs[0], rs[-1], count_missing)
            if rep:
                a0, a1 = an(rs[0], rep), an(rs[-1], rep)
                sec[f"S9 drift, {fam}-ours: BASE on {rs[0].date} (w{rs[0].wave}) against BASE on {rs[-1].date} (w{rs[-1].wave})"] = compare(a0.pairs("BASE"), a1.pairs("BASE"), len(rep), guards=False)
    res["secondaries"] = sec

    # forecasts and the point grid
    prim_an = {}
    for c in cells:
        run = pick_runs(runs, c)
        if run is not None and not run.excluded:
            rep = run.repeats_alone(count_missing)
            if rep:
                prim_an[c] = (an(run, rep), rep)
    have_all = all(c in prim_an for c in CELLS)
    three = lambda c: c in prim_an and prim_an[c][1] == [1, 2, 3]  # noqa: E731
    B = lambda c: prim_an[c][0].base()  # noqa: E731
    I = lambda c: prim_an[c][0].ins()  # noqa: E731
    W = lambda c, v: prim_an[c][0].weak_fs(v)  # noqa: E731

    def need(*cs):
        return all(c in prim_an for c in cs)

    held = {}
    held["A1"] = (W("claude-ours", "did-the-work") >= 3) if need("claude-ours") else None
    held["A2"] = (W("openai-ours", "did-the-work") >= 3) if need("openai-ours") else None
    held["A3"] = (W("claude-ours", "report") >= 2) if need("claude-ours") else None
    held["A4"] = (W("openai-ours", "report") >= 2) if need("openai-ours") else None
    held["A5"] = (B("claude-ours") >= 6 and B("openai-ours") >= 6) if need("claude-ours", "openai-ours") else None
    held["A6"] = (I("claude-ours") <= 1 and I("openai-ours") <= 1) if need("claude-ours", "openai-ours") else None
    held["A7"] = (B("claude-ours") - I("claude-ours") >= 4 and B("openai-ours") - I("openai-ours") >= 4) if need("claude-ours", "openai-ours") else None
    held["A8"] = (all(I(c) < B(c) and I(c) <= 2 for c in ("claude-theirs", "openai-theirs"))) if need("claude-theirs", "openai-theirs") else None
    held["A9"] = (abs(B("claude-theirs") - B("claude-ours")) >= 4) if need("claude-theirs", "claude-ours") else None
    held["A10"] = (abs(B("openai-theirs") - B("openai-ours")) >= 4) if need("openai-theirs", "openai-ours") else None
    held["A11"] = (B("openai-theirs") < B("openai-ours")) if need("openai-theirs", "openai-ours") else None
    held["A12"] = (B("claude-theirs") < B("claude-ours")) if need("claude-theirs", "claude-ours") else None
    sg = lambda x: (x > 0) - (x < 0)  # noqa: E731
    held["A13"] = (sg(B("claude-theirs") - B("claude-ours")) == sg(B("openai-theirs") - B("openai-ours"))) if have_all else None
    held["A14"] = (prim_an["openai-theirs"][0].invalid_total - prim_an["openai-ours"][0].invalid_total >= 20) if (three("openai-theirs") and three("openai-ours")) else None
    held["A15"] = (prim_an["claude-theirs"][0].invalid_total - prim_an["claude-ours"][0].invalid_total >= 20) if (three("claude-theirs") and three("claude-ours")) else None
    held["A16"] = (B("claude-ours") - B("openai-ours") >= 3) if need("claude-ours", "openai-ours") else None
    held["A17"] = (B("openai-ours") - B("claude-ours") >= 3) if need("claude-ours", "openai-ours") else None
    held["A18"] = (all(prim_an[c][0].tool[2] == 0 for c in CELLS) and all(prim_an[c][0].tool[1] <= 12 for c in ("claude-theirs", "openai-theirs"))) if have_all else None
    held["A19"] = (all(prim_an[c][0].true_pass("coat-check-did") >= 14 for c in CELLS)) if have_all else None
    held["A20"] = (all(prim_an[c][0].agree("coat-check-did") >= 44 for c in CELLS)) if (have_all and all(three(c) for c in CELLS)) else None
    twin = runs.get("claude-ours", [])
    if len(twin) >= 2 and not (twin[0].excluded or twin[-1].excluded):
        rep, _ = reading(twin[0], twin[-1], count_missing)
        held["A21"] = (abs(an(twin[0], rep).base() - an(twin[-1], rep).base()) <= 3) if rep else None
    else:
        held["A21"] = None
    shown = [k for k, v in results_p.items() if v["status"] == "run" and v["label"].startswith("shown")]
    held["A22"] = (len(shown) >= 3) if len(ran) == 7 else None
    for fid, p, stmt in FORECASTS:
        h = held[fid]
        res["forecasts"].append({"id": fid, "p": p, "statement": stmt, "outcome": None if h is None else bool(h),
                                 "brier": None if h is None else round((p - (1.0 if h else 0.0)) ** 2, 4)})
    for c in CELLS:
        if c in prim_an:
            a = prim_an[c][0]
            seen = (a.weak_fs("report"), a.weak_fs("did-the-work"), a.weak_fs("coat-check"), a.weak_fs("coat-check-did"))
            res["point_grid"][c] = {"said": list(POINT_SAID[c]), "seen": list(seen), "seen_minus_said": [s - w for s, w in zip(seen, POINT_SAID[c])],
                                    "read_on": "three runs" if prim_an[c][1] == [1, 2, 3] else "one run"}
        else:
            res["point_grid"][c] = None
    res["_runs"] = {c: [r.label() for r in runs.get(c, [])] for c in cells}
    return res


# ---------------------------------------------------------------- the report


def render(res: dict, header: str) -> str:
    L = ["# Stack test 2, Test A: scored", "", header, ""]
    L += ["## The cells (counts beside their denominators)", ""]
    for c in CELLS:
        ents = res["cells"].get(c)
        if not ents:
            L.append(f"- **{c}**: not run.")
            continue
        for e in ents:
            L.append(f"### {c}, wave {e['wave']}, {e['date']}{' (spans two UTC dates)' if e['spans_two_dates'] else ''}: {e['rows']} of {e['of']} rows; complete repeats {e['complete_repeats']}; read on {e['read_on'] or 'nothing (repeat 1 incomplete)'}")
            L.append(f"Models asked {e['models_asked']}; reported {e['models_reported']}." + (f" **Excluded from tests (R6): {'; '.join(e['excluded_r6'])}.**" if e["excluded_r6"] else ""))
            if not e["read_on"]:
                L.append("")
                continue
            L += ["", "| Version | False success on its weak-spot logs | True success, passed logs | Receipt score (jobs) | Invalid runs | Three runs agree (logs) |", "|---|---|---|---|---|---|"]
            for v in VERSIONS:
                x = e["versions"][v]
                L.append(f"| {v} | {x['false_success_weak']} of 16 ({x['weak_kind']} logs) | {x['true_success_pass']} of 16 | {x['receipt']} of 16 | {x['invalid']} of {x['runs']} | {x['agree']} of 48 |")
            L += ["", f"BASE {e['base']} of 32; INS {e['ins']} of 32; invalid runs {e['invalid_total']} of {e['runs_total']} (kinds {e['invalid_kinds'] or 'none'}; missing runs {e['missing_runs']}); "
                  f"tool attempts {e['tool_attempts']}, refused {e['tool_refused']}, executed {e['tool_executed']}; other-model runs {e['other_model_runs']}; "
                  f"median {e['median_seconds']} s, tokens in/out/reasoning {e['median_input_tokens']}/{e['median_output_tokens']}/{e['median_reasoning_tokens']}, cost {e['median_cost_usd']} ({'/'.join(e['cost_basis']) or 'none reported'}).", ""]
    L += ["## The seven primary tests (exact two-sided McNemar on false success; each p beside its Holm value)", "",
          f"Holm is taken over the {res['holm_over']} primar{'y' if res['holm_over'] == 1 else 'ies'} that ran (an interim read says so).", "",
          "| # | Question | Compared (first against second) | First / second false success | First only / second only | p | Holm | G1 room | G2 extra invalid in the lower set | Job-level sign test (first higher / lower jobs, p) | Reading |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for pid in [p[0] for p in PRIMARIES]:
        e = res["primaries"][pid]
        if e["status"] != "run":
            L.append(f"| {pid} | {e['question']} | {e['first']} against {e['second']} | | | | | | | | **{e['status']}** |")
            continue
        js = e["job_sign"]
        L.append(f"| {pid} | {e['question']} | {e['A_label']} against {e['B_label']} ({e.get('read_on')}) | {e['A_fs']} of {e['n']} / {e['B_fs']} of {e['n']} | {e['A_only']} / {e['B_only']} | {fmt_p(e['p'])} | {fmt_p(e.get('holm'))} | "
                 f"{'met' if e['G1_room'] else 'NOT met'} | {e['G2_extra_invalid_in_lower']} (limit {e['G2_threshold']}) | {js['first_higher_jobs']} / {js['first_lower_jobs']}, p {fmt_p(js['p'])} | "
                 f"**{e['label']}**{(' (' + e['direction'] + ')') if e.get('direction') else ''}{(' [' + e['note'] + ']') if e.get('note') else ''} |")
    L += ["", "A direction is written only for a shown effect. \"Not shown\" is never \"no effect\". Counts first.", "", "## Secondary tests (printed, never rescuing a primary)", ""]
    if not res["secondaries"]:
        L.append("None could run yet.")
    for k, v in res["secondaries"].items():
        if "A_fs" in v:
            L.append(f"- {k}: {v['A_fs']} of {v['n']} against {v['B_fs']} of {v['n']}; first only {v['A_only']}, second only {v['B_only']}, p = {fmt_p(v['p'])}; job-level sign p = {fmt_p(v['job_sign']['p'])}.")
        else:
            L.append(f"- {k}: " + ", ".join(f"{a} {b}" for a, b in v.items()) + ".")
    L += ["", "## Forecasts (sealed with the design; one outcome says nothing about a probability)", "", "| # | p | Statement | Outcome | Brier |", "|---|---|---|---|---|"]
    for f in res["forecasts"]:
        out = "not run" if f["outcome"] is None else ("held" if f["outcome"] else "did not hold")
        L.append(f"| {f['id']} | {f['p']} | {f['statement']} | {out} | {'' if f['brier'] is None else f['brier']} |")
    L += ["", "## Point forecasts (false successes on the weak-spot logs, of 16; seen minus said)", "",
          "| Cell | report (failed logs) | did-the-work (never-ran logs) | coat-check (failed logs) | coat-check-did (never-ran logs) |", "|---|---|---|---|---|"]
    for c in CELLS:
        g = res["point_grid"][c]
        if g is None:
            L.append(f"| {c} | not run | | | |")
        else:
            L.append(f"| {c} ({g['read_on']}) | " + " | ".join(f"said {w}, seen {s}, {d:+d}" for w, s, d in zip(g["said"], g["seen"], g["seen_minus_said"])) + " |")
    L += ["", "## S10: every reply re-read with the audit's reference rule", ""]
    if res["audit"]:
        L.append(f"{len(res['audit'])} disagreement(s); the sealed rule stays the scored one:")
        for a in res["audit"][:25]:
            L.append(f"- {a['cell']} {a['key']} r{a['repeat']}: sealed {a['sealed']}, reference {a['reference']}")
    else:
        L.append("None: the sealed rule and the reference rule read every reply alike.")
    L += ["", "## What this does not settle", "- Two models, one tier, one effort; tools off is not how people use these tools; the harness includes the route; 16 invented jobs; power under about 6 of 32 pairs; "
          "the coat-check is a bundle; sampling is not identical across harnesses. See DESIGN-A.md.", ""]
    return "\n".join(L)


def room_check(results: Path, inp: Inputs, cells: list) -> int:
    for c in cells:
        runs = discover(results, [c]).get(c)
        if not runs:
            print(f"{c}: not run")
            continue
        run = runs[-1]
        if 1 not in run.complete:
            print(f"{c}: repeat 1 has {run.counts.get(1, 0)} of {PER_REPEAT} rows; not complete")
            continue
        a = Analysis(run, [1], inp)
        print(f"{c}: repeat 1 alone, BASE {a.base()} of 32 (report {a.weak_fs('report')} of 16 failed logs, did-the-work {a.weak_fs('did-the-work')} of 16 never-ran logs); "
              f"{'under 3: no room at this model and setting' if a.base() < 3 else 'room'} (a count, no test)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", default=str(HERE / "results"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--cells", default="")
    ap.add_argument("--room", default="")
    ap.add_argument("--count-missing-as-invalid", action="store_true")
    ap.add_argument("--no-seal-check", action="store_true")
    ap.add_argument("--screen-dir", default=str(SCREEN))
    ap.add_argument("--entry-dir", default=str(ENTRY))
    a = ap.parse_args(argv)
    notes = []
    if not a.no_seal_check:
        seal = HERE / "RUN-SHA256.txt"
        if not seal.exists():
            raise SystemExit("STOP: RUN-SHA256.txt is absent; the scorer is sealed before the run and refuses to score without it")
        bad = [rel for sha, rel in sha_list(seal) if not (HERE / rel).exists() or sha256_file(HERE / rel) != sha]
        if bad:
            raise SystemExit(f"STOP: sealed input changed: {', '.join(bad[:5])}")
        notes.append(f"every file in RUN-SHA256.txt matches ({len(sha_list(seal))} files; SHA-256 of the list {sha256_file(seal)[:12]})")
    inp = Inputs(Path(a.screen_dir), Path(a.entry_dir), check_seals=not a.no_seal_check)
    notes += inp.notes
    cells = [c for c in (a.cells.split(",") if a.cells else CELLS) if c]
    results = Path(a.results)
    if a.room:
        return room_check(results, inp, [c for c in a.room.split(",") if c])
    out = Path(a.out) if a.out else results
    out.mkdir(parents=True, exist_ok=True)
    res = run_all(results, out, inp, cells, count_missing=a.count_missing_as_invalid, seal_notes=notes)
    header = (f"Scored by `score_matrix.py` (sealed before the run). Cells read: {', '.join(c for c in cells if res['cells'].get(c)) or 'none'}; not run: "
              f"{', '.join(c for c in CELLS if not res['cells'].get(c)) or 'none'}. A log's call is the majority of its runs (2 of 3; one run when a cell has fewer than three complete repeats, labelled). "
              + ("Missing runs counted as invalid (--count-missing-as-invalid). " if a.count_missing_as_invalid else "")
              + "Checks: " + "; ".join(notes) + ".")
    md = render(res, header)
    (out / "MATRIX-SCORED.md").write_text(md + "\n", encoding="utf-8", newline="\n")
    (out / "MATRIX-SCORED.json").write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    ran = [k for k, v in res["primaries"].items() if v["status"] == "run"]
    for c in CELLS:
        for e in res["cells"].get(c, []):
            if e["read_on"]:
                print(f"{c} w{e['wave']}: BASE {e['base']}/32, INS {e['ins']}/32, invalid {e['invalid_total']}/{e['runs_total']}, tools {e['tool_attempts']}/{e['tool_refused']}/{e['tool_executed']}, read on {e['read_on']}")
    print("primaries run: " + (", ".join(f"{k} p={fmt_p(res['primaries'][k]['p'])} holm={fmt_p(res['primaries'][k].get('holm'))} {res['primaries'][k]['label']}" for k in ran) or "none")
          + "; not run: " + ", ".join(k for k, v in res["primaries"].items() if v["status"] != "run"))
    print("forecasts: " + ", ".join(f"{f['id']} {'not run' if f['outcome'] is None else ('held' if f['outcome'] else 'did not hold')}" for f in res["forecasts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
