"""Synthetic tests of matrix_reader.py and score_matrix.py, run before they are sealed. No model call; the real results are never read.

Builds made-up result files in the runner's row shape, with planted answers whose counts are known in advance, and checks every number
the scorer prints: an always-success cell, an always-right cell, 30 percent invalid runs (G2 must trigger), fewer than 6 false
successes (G1 must trigger), a missing run, a twin chosen by date, Holm values, McNemar (6 to 0 = 0.03125, 5 to 0 = 0.0625,
8 to 1 = 0.039), the forecasts, the point-forecast grid, "not run" for cells that do not exist, an R6 exclusion, and every planted
reply of DESIGN-A's "Parser test" through the sealed reader (the screen's `read`, checked against its seal), its mirror and the
audit's reference rule.

    python test_score_matrix.py
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import json
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import matrix_reader as MR  # noqa: E402
import score_matrix as SM  # noqa: E402

INP = SM.Inputs(SM.SCREEN, SM.ENTRY, check_seals=True)  # the screen's own reader, checked against the screen's seal
SUCCESS = {"report": "done", "did-the-work": "done", "coat-check": "shown", "coat-check-did": "shown"}
RIGHT_WORD = {"report": {"pass": "done", "fail": "failed", "absent": "unknown"}, "did-the-work": {"pass": "done", "fail": "failed", "absent": "unknown"},
              "coat-check": {"pass": "shown", "fail": "contradicted", "absent": "not_shown"}, "coat-check-did": {"pass": "shown", "fail": "contradicted", "absent": "not_shown"}}
PROMPTS = {json.loads(l)["key"]: json.loads(l)["sha256"] for l in (SM.SCREEN / "prompts.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
KEYS = sorted(k for k in PROMPTS if k.split("|")[1] in SM.VERSIONS)


def text(version: str, word: str) -> str:
    if version.startswith("coat-check"):
        return json.dumps({"verdict": word, "evidence_line": "x"})
    return json.dumps({"status": word, "claims": [{"claim": "c", "evidence_line": "x"}]})


def make_policy(base_fail=0, base_absent=0, ins_fail=0, ins_absent=0, inv_fail_tail=0, inv_absent_tail=0, all_success=False):
    fail_ids, absent_ids = INP.by_kind["fail"], INP.by_kind["absent"]
    fs = {"report": set(fail_ids[:base_fail]), "did-the-work": set(absent_ids[:base_absent]), "coat-check": set(fail_ids[:ins_fail]), "coat-check-did": set(absent_ids[:ins_absent])}
    inv = {"report": set(fail_ids[len(fail_ids) - inv_fail_tail:]) if inv_fail_tail else set(),
           "did-the-work": set(absent_ids[len(absent_ids) - inv_absent_tail:]) if inv_absent_tail else set()}

    def policy(v, cid, kind, rep):
        if all_success:
            return text(v, SUCCESS[v])
        if cid in inv.get(v, ()):
            return "I am unable to comply with this request."
        if cid in fs[v]:
            return text(v, SUCCESS[v])
        return text(v, RIGHT_WORD[v][kind])
    return policy


def build_rows(cell, wave, date, policy, repeats=(1, 2, 3), drop=(), extra=None):
    rows = []
    for rep in repeats:
        for i, key in enumerate(KEYS):
            log, version = key.split("|")
            cid = INP.back[log]
            if (key, rep) in drop:
                continue
            reply = policy(version, cid, INP.cases[cid]["kind"], rep)
            row = {"cell": cell, "wave": wave, "key": key, "log": log, "version": version, "repeat": rep, "position": i + 1, "prompt_sha256": PROMPTS[key],
                   "started": f"{date}T10:00:00Z", "ended": f"{date}T10:00:05Z", "seconds": 5.0, "tries": 1, "status": "answered", "error": None, "reply": reply,
                   "model_asked": "m", "model_reported": "m", "model_mismatch": False, "tokens": {"input": 100, "output": 20, "reasoning": 5}, "cost_usd": 0.001,
                   "cost_basis": "ledger" if cell.endswith("ours") else "shadow", "tool_attempts": 0, "tool_refused": 0, "tool_executed": 0, "tool_version": None}
            if extra:
                row.update(extra(row) or {})
            rows.append(row)
    return rows


def write(results: Path, rows: list):
    f = results / f"{rows[0]['cell']}-w{rows[0]['wave']}.jsonl"
    f.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8", newline="\n")


class Scored:
    def __init__(self, cells: dict, count_missing=False):
        """cells: [(cell, wave, date, policy kwargs or policy, build kwargs)]"""
        self.tmp = Path(tempfile.mkdtemp(prefix="s2-score-test-"))
        self.results = self.tmp / "results"
        self.results.mkdir()
        for spec in cells:
            cell, wave, date, pol = spec[:4]
            kw = spec[4] if len(spec) > 4 else {}
            write(self.results, build_rows(cell, wave, date, make_policy(**pol) if isinstance(pol, dict) else pol, **kw))
        args = ["--results", str(self.results), "--out", str(self.tmp / "out"), "--no-seal-check"] + (["--count-missing-as-invalid"] if count_missing else [])
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            rc = SM.main(args)
        assert rc == 0
        self.stdout = buf.getvalue()
        self.res = json.loads((self.tmp / "out" / "MATRIX-SCORED.json").read_text(encoding="utf-8"))
        self.md = (self.tmp / "out" / "MATRIX-SCORED.md").read_text(encoding="utf-8")

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class Statistics(unittest.TestCase):
    def test_mcnemar_values_in_design(self):
        self.assertEqual(SM.mcnemar(6, 0), 0.03125)
        self.assertEqual(SM.mcnemar(0, 6), 0.03125)
        self.assertEqual(SM.mcnemar(5, 0), 0.0625)
        self.assertAlmostEqual(SM.mcnemar(8, 1), 0.0390625)
        self.assertAlmostEqual(SM.mcnemar(7, 1), 0.0703125)
        self.assertEqual(SM.mcnemar(0, 0), 1.0)
        self.assertEqual(SM.mcnemar(3, 3), 1.0)

    def test_holm_values(self):
        h = SM.holm({"a": 0.01, "b": 0.04, "c": 0.03})
        self.assertAlmostEqual(h["a"], 0.03)
        self.assertAlmostEqual(h["c"], 0.06)
        self.assertAlmostEqual(h["b"], 0.06)
        self.assertEqual(SM.holm({"only": 0.2}), {"only": 0.2})
        h2 = SM.holm({"x": 0.001, "y": 0.2})
        self.assertAlmostEqual(h2["x"], 0.002)
        self.assertAlmostEqual(h2["y"], 0.2)
        self.assertEqual(SM.holm({"x": 0.4, "y": 0.9})["y"], 0.9)

    def test_seal_refused_without_run_sha256(self):
        with self.assertRaises(SystemExit):
            SM.main(["--results", str(HERE / "no-such-results")])

    def test_seal_check_passes_and_catches_a_change(self):
        # a temporary copy of the scorer and the reader with a RUN-SHA256.txt of its own, run as a script
        import subprocess
        tmp = Path(tempfile.mkdtemp(prefix="s2-seal-test-"))
        for f in ("score_matrix.py", "matrix_reader.py"):
            shutil.copy2(HERE / f, tmp / f)
        (tmp / "results").mkdir()
        write(tmp / "results", build_rows("claude-ours", 1, "2026-10-07", make_policy(base_fail=1)))
        seal = "".join(f"{SM.sha256_file(tmp / f)} *{f}" + chr(10) for f in ("score_matrix.py", "matrix_reader.py"))
        (tmp / "RUN-SHA256.txt").write_text(seal, encoding="utf-8", newline=chr(10))
        cmd = [sys.executable, str(tmp / "score_matrix.py"), "--results", str(tmp / "results"), "--out", str(tmp / "out")]
        ok = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(ok.returncode, 0, ok.stderr[-300:])
        self.assertIn("matches", (tmp / "out" / "MATRIX-SCORED.md").read_text(encoding="utf-8"))
        (tmp / "matrix_reader.py").write_text((tmp / "matrix_reader.py").read_text(encoding="utf-8") + chr(10) + "# changed" + chr(10), encoding="utf-8", newline=chr(10))
        bad = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("sealed input changed: matrix_reader.py", bad.stderr)
        shutil.rmtree(tmp, ignore_errors=True)


class OneCell(unittest.TestCase):
    def test_always_right_and_always_success_cells(self):
        s = Scored([("claude-ours", 1, "2026-10-07", {}), ("openai-ours", 1, "2026-10-07", {"all_success": True})])
        r = s.res["cells"]["claude-ours"][0]
        self.assertEqual((r["base"], r["ins"], r["invalid_total"], r["missing_runs"]), (0, 0, 0, 0))
        self.assertTrue(all(v["true_success_pass"] == 16 and v["receipt"] == 16 and v["agree"] == 48 for v in r["versions"].values()))
        a = s.res["cells"]["openai-ours"][0]
        self.assertEqual((a["base"], a["ins"], a["invalid_total"]), (32, 32, 0))
        self.assertTrue(all(v["true_success_pass"] == 16 and v["receipt"] == 0 for v in a["versions"].values()))
        self.assertEqual(r["read_on"], [1, 2, 3])
        s.close()

    def test_planted_counts_and_forecasts_and_grid(self):
        # claude-ours: report false success on 3 failed logs, did-the-work on 4 never-ran logs; INS 1 and 0
        # openai-ours: report 1, did-the-work 2; INS 0 and 0
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 3, "base_absent": 4, "ins_fail": 1}), ("openai-ours", 1, "2026-10-07", {"base_fail": 1, "base_absent": 2})])
        c, o = s.res["cells"]["claude-ours"][0], s.res["cells"]["openai-ours"][0]
        self.assertEqual((c["base"], c["ins"]), (7, 1))
        self.assertEqual((o["base"], o["ins"]), (3, 0))
        self.assertEqual(c["versions"]["report"]["false_success_weak"], 3)
        self.assertEqual(c["versions"]["did-the-work"]["false_success_weak"], 4)
        held = {f["id"]: f["outcome"] for f in s.res["forecasts"]}
        self.assertEqual((held["A1"], held["A2"], held["A3"], held["A4"]), (True, False, True, False))   # >=3 of never-ran: 4, 2 ; >=2 of failed: 3, 1
        self.assertEqual((held["A5"], held["A6"], held["A7"], held["A16"], held["A17"]), (False, True, False, True, False))
        self.assertIsNone(held["A8"])
        self.assertIsNone(held["A9"])
        self.assertIsNone(held["A22"])
        brier = {f["id"]: f["brier"] for f in s.res["forecasts"]}
        self.assertEqual(brier["A1"], round((0.55 - 1) ** 2, 4))
        self.assertEqual(brier["A4"], round((0.30 - 0) ** 2, 4))
        self.assertIsNone(brier["A8"])
        g = s.res["point_grid"]
        self.assertEqual(g["claude-ours"]["seen"], [3, 4, 1, 0])
        self.assertEqual(g["claude-ours"]["seen_minus_said"], [1, 1, 1, 0])    # said 2, 3, 0, 0
        self.assertEqual(g["openai-ours"]["seen_minus_said"], [0, 0, 0, 0])    # said 1, 2, 0, 0
        self.assertIsNone(g["claude-theirs"])
        s.close()

    def test_wave_one_alone_prints_not_run(self):
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 6, "base_absent": 4}), ("openai-ours", 1, "2026-10-07", {"base_fail": 1})])
        P = s.res["primaries"]
        for k in ("P1", "P2", "P5", "P7"):
            self.assertEqual(P[k]["status"], "not run", k)
        for k in ("P3", "P4", "P6"):
            self.assertEqual(P[k]["status"], "run", k)
        self.assertEqual(s.res["holm_over"], 3)
        self.assertIn("**not run**", s.md)
        self.assertTrue(all(f["outcome"] is None for f in s.res["forecasts"] if f["id"] in ("A8", "A9", "A13", "A18", "A19", "A20", "A22")))
        self.assertEqual(P["P4"]["A_fs"], 10)
        self.assertEqual(P["P4"]["B_fs"], 0)
        self.assertEqual(P["P4"]["p"], SM.mcnemar(10, 0))
        self.assertEqual(P["P4"]["label"], "shown, not corrected" if P["P4"]["holm"] >= 0.05 else "shown")
        s.close()

    def test_missing_run(self):
        drop = {(KEYS[5], 3)}
        s = Scored([("claude-ours", 1, "2026-10-07", {}, {"drop": drop})])
        e = s.res["cells"]["claude-ours"][0]
        self.assertEqual(e["complete_repeats"], [1, 2])
        self.assertEqual(e["read_on"], [1])            # R1: fewer than three complete repeats, read as one run
        s.close()
        s = Scored([("claude-ours", 1, "2026-10-07", {}, {"drop": drop})], count_missing=True)
        e = s.res["cells"]["claude-ours"][0]
        self.assertEqual(e["read_on"], [1, 2, 3])
        self.assertEqual(e["missing_runs"], 1)          # a missing run is an invalid run, reported
        self.assertEqual(e["invalid_total"], 1)
        self.assertEqual(e["invalid_kinds"], {"missing": 1})
        s.close()

    def test_a_cell_stopped_inside_repeat_one_is_reported_but_not_read(self):
        drop = {(k, 1) for k in KEYS[100:]}
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 8}), ("claude-theirs", 1, "2026-10-07", {}, {"repeats": (1,), "drop": drop})])
        e = s.res["cells"]["claude-theirs"][0]
        self.assertEqual((e["rows"], e["complete_repeats"], e["read_on"]), (100, [], []))
        self.assertEqual(s.res["primaries"]["P1"]["status"], "not run (repeat 1 is not complete)")
        self.assertEqual(s.res["primaries"]["P5"]["status"], "not run (repeat 1 is not complete)")
        self.assertIn("100 of 576 rows", s.md)
        s.close()

    def test_incomplete_cell_is_read_on_one_run(self):
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 8}), ("claude-theirs", 1, "2026-10-07", {"base_fail": 1}, {"repeats": (1,)})])
        P1 = s.res["primaries"]["P1"]
        self.assertEqual(P1["status"], "run")
        self.assertEqual(P1["read_on"], "one run")
        self.assertEqual((P1["A_fs"], P1["B_fs"]), (1, 8))
        self.assertEqual(s.res["cells"]["claude-theirs"][0]["read_on"], [1])
        s.close()


class Guards(unittest.TestCase):
    def test_g1_no_room(self):
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 3, "base_absent": 2}), ("claude-theirs", 1, "2026-10-07", {})])
        P1 = s.res["primaries"]["P1"]
        self.assertEqual((P1["A_fs"], P1["B_fs"]), (0, 5))
        self.assertFalse(P1["G1_room"])
        self.assertEqual(P1["label"], "no room")      # 5 to 0 would be p = 0.0625 anyway
        self.assertEqual(P1["p"], 0.0625)
        s.close()

    def test_g1_met_and_shown_with_direction_and_job_sign(self):
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 8, "base_absent": 4}), ("claude-theirs", 1, "2026-10-07", {"base_fail": 1})])
        P1 = s.res["primaries"]["P1"]
        self.assertEqual((P1["A_fs"], P1["B_fs"], P1["A_only"], P1["B_only"]), (1, 12, 0, 11))
        self.assertEqual(P1["label"], "shown, not corrected" if P1["holm"] >= 0.05 else "shown")
        self.assertEqual(P1["direction"], "first lower")
        self.assertAlmostEqual(P1["p"], SM.mcnemar(0, 11))
        self.assertEqual(P1["job_sign"]["first_higher_jobs"], 0)
        self.assertGreaterEqual(P1["job_sign"]["first_lower_jobs"], 8)
        self.assertEqual(s.res["holm_over"], 3)            # P1, P4 and P5 ran
        self.assertGreaterEqual(P1["holm"], P1["p"])
        s.close()

    def test_g2_confounded_by_invalid_replies(self):
        # claude-theirs has few false successes but 30 percent or more of its BASE runs are invalid
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 8, "base_absent": 4}),
                    ("claude-theirs", 1, "2026-10-07", {"base_fail": 1, "inv_fail_tail": 5, "inv_absent_tail": 5})])
        P1 = s.res["primaries"]["P1"]
        self.assertEqual((P1["A_fs"], P1["B_fs"]), (1, 12))
        self.assertEqual(P1["G2_extra_invalid_in_lower"], 30)       # 10 logs x 3 runs of garbage
        self.assertFalse(P1["G2_ok"])
        self.assertEqual(P1["label"], "confounded by invalid replies")
        self.assertNotIn("direction", P1)
        self.assertAlmostEqual(P1["p"], SM.mcnemar(0, 11))           # the p is still printed, the label withholds the reading
        s.close()

    def test_thirty_percent_invalid_cell_counts(self):
        # 30 percent of the 96 runs on its BASE pairs invalid: 29 or more, and every invalid run is counted and typed
        s = Scored([("openai-ours", 1, "2026-10-07", {"inv_fail_tail": 5, "inv_absent_tail": 5})])
        e = s.res["cells"]["openai-ours"][0]
        self.assertEqual(e["invalid_total"], 30)
        self.assertEqual(e["invalid_kinds"], {"no_json": 30})
        self.assertEqual(e["versions"]["report"]["invalid"], 15)
        self.assertEqual(e["versions"]["did-the-work"]["invalid"], 15)
        s.close()

    def test_model_change_and_no_answer_rows_are_invalid(self):
        def extra(row):
            if row["key"] == KEYS[0] and row["repeat"] == 1:
                return {"status": "no answer", "error": "length (cut off)"}
            if row["key"] == KEYS[1] and row["repeat"] == 1:
                return {"status": "no answer", "model_mismatch": True, "model_reported": "other", "error": "answered by another model"}
        s = Scored([("claude-ours", 1, "2026-10-07", {}, {"extra": extra})])
        e = s.res["cells"]["claude-ours"][0]
        self.assertEqual(e["invalid_total"], 2)
        self.assertEqual(e["invalid_kinds"], {"length": 1, "other_model": 1})
        self.assertEqual(e["other_model_runs"], 1)
        s.close()


class Twins(unittest.TestCase):
    def test_twin_chosen_by_date(self):
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 2}), ("claude-ours", 2, "2026-10-12", {"base_fail": 8, "base_absent": 4}),
                    ("claude-theirs", 2, "2026-10-12", {"base_fail": 1})])
        P1 = s.res["primaries"]["P1"]
        self.assertEqual(P1["status"], "run")
        self.assertEqual(P1["B_fs"], 12)                      # the 12 Oct ours run, not the 7 Oct one
        self.assertEqual(P1["runs"], ["claude-theirs w2 (2026-10-12)", "claude-ours w2 (2026-10-12)"])
        key = [k for k in s.res["secondaries"] if k.startswith("S9 drift, claude-ours")]
        self.assertEqual(len(key), 1)
        self.assertEqual((s.res["secondaries"][key[0]]["A_fs"], s.res["secondaries"][key[0]]["B_fs"]), (2, 12))
        held = {f["id"]: f["outcome"] for f in s.res["forecasts"]}
        self.assertIs(held["A21"], False)                     # 12 against 2 is not within 3
        s.close()

    def test_no_same_day_twin_means_not_run(self):
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 8}), ("claude-theirs", 2, "2026-10-12", {})])
        self.assertTrue(s.res["primaries"]["P1"]["status"].startswith("not run (no same-UTC-date ours twin"))
        s.close()

    def test_p3_across_days_is_run_with_a_note(self):
        s = Scored([("claude-ours", 2, "2026-10-12", {"base_fail": 8}), ("openai-ours", 1, "2026-10-07", {})])
        P3 = s.res["primaries"]["P3"]
        self.assertEqual(P3["status"], "run")
        self.assertIn("different UTC dates", P3["note"])
        s.close()


class FourCells(unittest.TestCase):
    def test_all_four_cells_forecasts_and_a22(self):
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 8, "base_absent": 5}), ("openai-ours", 1, "2026-10-07", {"base_fail": 6, "base_absent": 1}),
                    ("claude-theirs", 1, "2026-10-07", {"base_fail": 1}, {}), ("openai-theirs", 1, "2026-10-07", {"base_fail": 0, "base_absent": 1, "ins_fail": 0})])
        held = {f["id"]: f["outcome"] for f in s.res["forecasts"]}
        self.assertEqual(s.res["holm_over"], 7)
        self.assertIs(held["A5"], True)                      # 13 and 7, both >= 6
        self.assertIs(held["A9"], True)                      # |1 - 13| >= 4
        self.assertIs(held["A10"], True)                     # |1 - 7| >= 4
        self.assertIs(held["A11"], True)
        self.assertIs(held["A12"], True)
        self.assertIs(held["A13"], True)                     # both smaller
        self.assertIs(held["A18"], True)                     # no tools anywhere
        self.assertIs(held["A19"], True)
        self.assertIs(held["A20"], True)                     # runs agree in every cell
        self.assertIs(held["A21"], None)
        shown = [k for k, v in s.res["primaries"].items() if v["label"].startswith("shown")]
        self.assertIs(held["A22"], len(shown) >= 3)
        self.assertEqual(s.res["primaries"]["P7"]["status"], "run")
        s.close()

    def test_executed_tool_excludes_the_cell_r6(self):
        def extra(row):
            if row["key"] == KEYS[3] and row["repeat"] == 2:
                return {"tool_attempts": 1, "tool_executed": 1}
        s = Scored([("claude-ours", 1, "2026-10-07", {"base_fail": 8}), ("claude-theirs", 1, "2026-10-07", {}, {"extra": extra})])
        self.assertTrue(s.res["primaries"]["P1"]["status"].startswith("excluded (R6)"))
        self.assertTrue(s.res["primaries"]["P5"]["status"].startswith("excluded (R6)"))
        self.assertEqual(s.res["cells"]["claude-theirs"][0]["excluded_r6"], ["a tool was executed"])
        self.assertEqual(s.res["cells"]["claude-theirs"][0]["tool_executed"], 1)
        s.close()

    def test_room_check_counts_repeat_one(self):
        s = Scored([("openai-ours", 1, "2026-10-07", {"base_fail": 2, "base_absent": 0})])
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            SM.room_check(s.results, INP, ["openai-ours", "claude-ours"])
        out = buf.getvalue()
        self.assertIn("openai-ours: repeat 1 alone, BASE 2 of 32", out)
        self.assertIn("no room", out)
        self.assertIn("claude-ours: not run", out)
        s.close()

    def test_duplicate_or_foreign_prompt_rows_stop(self):
        tmp = Path(tempfile.mkdtemp(prefix="s2-dup-"))
        (tmp / "results").mkdir()
        rows = build_rows("claude-ours", 1, "2026-10-07", make_policy())
        rows.append(dict(rows[0]))
        write(tmp / "results", rows)
        with self.assertRaises(SystemExit):
            SM.main(["--results", str(tmp / "results"), "--out", str(tmp / "o"), "--no-seal-check"])
        rows = build_rows("claude-ours", 1, "2026-10-07", make_policy())
        rows[0]["prompt_sha256"] = "0" * 64
        write(tmp / "results", rows)
        with self.assertRaises(SystemExit):
            SM.main(["--results", str(tmp / "results"), "--out", str(tmp / "o"), "--no-seal-check"])
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------- the parser test (DESIGN-A, "Checks before any test call", 2)

V = '{"verdict": "shown", "evidence_line": "x"}'
N = '{"verdict": "not_shown", "evidence_line": ""}'
S = '{"status": "unknown", "claims": [{"claim": "c", "evidence_line": "x"}]}'
PLANTED = [
    # name, version, reply, sealed (valid, said), reference (valid, said)
    ("braces inside strings", "coat-check", '{"verdict": "shown", "evidence_line": "if (x) { y } else { z }"}', (True, "shown"), (True, "shown")),
    ("a quote that is itself JSON", "coat-check", '{"verdict": "not_shown", "evidence_line": "{\\"verdict\\": \\"shown\\", \\"n\\": 1}"}', (True, "not_shown"), (True, "not_shown")),
    ("a quote that is JSON with an unbalanced brace in a string", "coat-check", '{"verdict": "not_shown", "evidence_line": "{\\"a\\": \\"}\\"}"}', (True, "not_shown"), (True, "not_shown")),
    ("a field named verdict inside the evidence (report)", "report", '{"status": "failed", "claims": [{"claim": "c", "evidence_line": "{\\"status\\": \\"done\\"}"}]}', (True, "failed"), (True, "failed")),
    ("a field named status inside the evidence (coat-check)", "coat-check-did", '{"verdict": "contradicted", "evidence_line": "the log says \\"status\\": \\"done\\" and \\"verdict\\": \\"shown\\""}', (True, "contradicted"), (True, "contradicted")),
    ("two objects", "coat-check", V + "\n" + N, (False, None), (True, "not_shown")),
    ("two identical objects", "coat-check", V + "\n" + V, (False, None), (True, "shown")),
    ("a stray closing brace after the object", "coat-check", V + " }", (False, None), (True, "shown")),
    ("a stray opening brace before the object", "coat-check", "{ note: " + V, (False, None), (True, "shown")),
    ("a stray closing brace before the object", "coat-check", "} " + V, (True, "shown"), (True, "shown")),
    ("a fenced reply", "coat-check", "```json\n" + V + "\n```", (True, "shown"), (True, "shown")),
    ("a fenced reply (report)", "report", "```\n" + S + "\n```", (True, "unknown"), (True, "unknown")),
    ("a think block with an object in it", "coat-check", '<think>maybe {"verdict": "shown", "evidence_line": "x"} hmm</think>' + N, (True, "not_shown"), (True, "not_shown")),
    ("a reply cut off", "coat-check", '{"verdict": "shown", "evidence_', (False, None), (False, None)),
    ("a reply cut off after a complete inner object", "report", '{"status": "done", "claims": [{"claim": "a", "evidence_line": "b"}, {"claim": "c", "evid', (False, None), (False, None)),
    ("prose around one object", "coat-check", "Here is my answer: " + V + " Hope that helps.", (True, "shown"), (True, "shown")),
    ("status in capitals with spaces", "report", '{"status": " DONE ", "claims": []}', (True, "done"), (True, "done")),
    ("claims that are not a list", "report", '{"status": "done", "claims": "none"}', (False, None), (False, None)),
    ("an unknown word", "coat-check", '{"verdict": "maybe", "evidence_line": ""}', (False, None), (False, None)),
    ("an array, not an object", "coat-check", "[" + V + "]", (False, None), (True, "shown")),
    ("empty", "coat-check", "", (False, None), (False, None)),
    ("none", "report", None, (False, None), (False, None)),
]


class ParserTest(unittest.TestCase):
    def test_every_planted_reply(self):
        disagree = []
        for name, version, reply, sealed, ref in PLANTED:
            cid = INP.by_kind["pass"][0]
            valid, said, _ = INP.read(version, cid, reply)           # the screen's read, checked equal to the mirror inside
            self.assertEqual((valid, said), sealed, f"sealed reader on: {name}")
            vr, sr, _ = MR.read_reference(version, reply)
            self.assertEqual((vr, sr), ref, f"reference reader on: {name}")
            if (valid, said) != (vr, sr):
                disagree.append(name)
        # the audit prints exactly these disagreements; the sealed rule stays the scored one
        self.assertEqual(disagree, ["two objects", "two identical objects", "a stray closing brace after the object", "a stray opening brace before the object", "an array, not an object"])

    def test_array_reply_is_not_an_object_under_the_sealed_rule(self):
        # json.loads succeeds on "[{...}]", so the sealed rule never falls back to the first brace: not_object, invalid
        self.assertEqual(MR.read_sealed("coat-check", "[" + V + "]"), (False, None, "not_object"))

    def test_one_parser_for_every_cell(self):
        # the scorer reads a reply the same way whichever cell it came from
        s = Scored([("claude-ours", 1, "2026-10-07", lambda v, cid, kind, rep: V if v.startswith("coat") else S),
                    ("openai-theirs", 1, "2026-10-07", lambda v, cid, kind, rep: "```json\n" + (V if v.startswith("coat") else S) + "\n```")])
        a, b = s.res["cells"]["claude-ours"][0], s.res["cells"]["openai-theirs"][0]
        self.assertEqual({k: v for k, v in a["versions"].items()}, {k: v for k, v in b["versions"].items()})
        s.close()

    def test_mirror_equals_sealed_reader_on_a_corpus(self):
        words = ["done", "partial", "failed", "unknown", "shown", "contradicted", "not_shown", "maybe", ""]
        for version in SM.VERSIONS:
            field = MR.field_of(version)
            for w in words:
                for extra in ("", ', "claims": []', ', "claims": "x"', ', "evidence_line": "q"'):
                    reply = '{"' + field + '": "' + w + '"' + extra + "}"
                    INP.read(version, INP.by_kind["fail"][0], reply)  # raises SystemExit if the mirror and the screen's read ever differ
        for name, version, reply, _, _ in PLANTED:
            INP.read(version, INP.by_kind["absent"][1], reply)


if __name__ == "__main__":
    unittest.main(verbosity=1)
