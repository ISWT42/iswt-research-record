"""Self-test on small invented data: the statistics, the mirrored reply parsing, the quote classes (Q4),
the certainty rule (Q3) and the no-overwrite writer. Touches none of the real data.
  python selftest.py
"""
import hashlib
import json
import tempfile
from pathlib import Path

import q3_certainty as Q3
import q4_quote_decides as Q4
import rescore_common as C

FAILS, CHECKS = [], 0


def check(name, got, want):
    global CHECKS
    CHECKS += 1
    if got != want:
        FAILS.append(f"{name}: got {got!r}, wanted {want!r}")


def near(name, got, want, tol=6e-4):
    global CHECKS
    CHECKS += 1
    if got is None or abs(got - want) > tol:
        FAILS.append(f"{name}: got {got!r}, wanted about {want!r}")


# ---- statistics ----------------------------------------------------------------
lo, hi = C.wilson(5, 10)
near("wilson 5/10 lo", lo, 0.2366)
near("wilson 5/10 hi", hi, 0.7634)
lo, hi = C.wilson(0, 10)
near("wilson 0/10 lo", lo, 0.0)
near("wilson 0/10 hi", hi, 0.2775)
lo, hi = C.wilson(10, 10)
near("wilson 10/10 lo", lo, 0.7225)
near("wilson 10/10 hi", hi, 1.0)
check("wilson n=0", C.wilson(0, 0), None)
check("frac n=0", C.frac(0, 0), {"k": 0, "n": 0, "rate": None, "ci95": None})
f = C.frac(3, 12)
check("frac 3/12", (f["k"], f["n"], f["rate"]), (3, 12, 0.25))
nc = C.newcombe(56, 70, 48, 80)  # Newcombe 1998, worked example for method 10: 0.2000 (0.0524, 0.3339)
near("newcombe diff", nc["diff"], 0.2)
near("newcombe lo", nc["ci95"][0], 0.0524)
near("newcombe hi", nc["ci95"][1], 0.3339)
check("newcombe n=0", C.newcombe(1, 0, 1, 5), None)

# ---- mirrored reply parsing ----------------------------------------------------
check("parse plain", C.parse_reply('{"a": 1}')[0], {"a": 1})
check("parse fenced", C.parse_reply('```json\n{"a": 1}\n```')[0], {"a": 1})
check("parse embedded", C.parse_reply('Answer: {"a": 1} thanks')[0], {"a": 1})
check("parse junk", C.parse_reply("no json here"), (None, "unparseable_reply"))
check("parse list", C.parse_reply("[1, 2]"), (None, "invalid_reply"))
check("parse empty", C.parse_reply("   "), (None, "unparseable_reply"))
check("parse none", C.parse_reply(None), (None, "unparseable_reply"))
check("verdict not shown", C.normalize_verdict("Not Shown"), "not_shown")
check("verdict shown", C.normalize_verdict(" shown "), "shown")
check("verdict junk", C.normalize_verdict("maybe"), None)
check("verdict non-string", C.normalize_verdict(5), None)
tt = [C.Turn("T1", "x:1", "", ""), C.Turn("T2", "x:2", "", "")]
check("turn id T2", C.normalize_turn_id("T2", tt).label, "T2")
check("turn id 2", C.normalize_turn_id("2", tt).label, "T2")
check("turn id [t1]", C.normalize_turn_id("[t1]", tt).label, "T1")
check("turn id row id", C.normalize_turn_id("x:2", tt).label, "T2")
check("turn id unknown", C.normalize_turn_id("T9", tt), None)
check("turn id none", C.normalize_turn_id(None, tt), None)
check("turn id bool", C.normalize_turn_id(True, tt), None)

# ---- Q4: classes on invented items ----------------------------------------------
ITEMS = {
    "901": {"id": "901", "truth": "shown", "trap": "none", "deciding_line": "deploy ok: site-a v2",
            "turns": [{"cmd": "deploy", "output": "building\ndeploy ok: site-a v2\ndone"}]},
    "902": {"id": "902", "truth": "contradicted", "trap": "retry", "deciding_line": "Error: 500",
            "turns": [{"cmd": "c1", "output": "Error: 500\nretrying"}, {"cmd": "c2", "output": "queued\nError: 500"}]},
    "903": {"id": "903", "truth": "not_shown", "trap": "narration", "deciding_line": "",
            "turns": [{"cmd": "c", "output": "ran build\nall good"}]},
    "904": {"id": "904", "truth": "shown", "trap": "none", "deciding_line": "x done",
            "turns": [{"cmd": "c1", "output": "x done"}, {"cmd": "c2", "output": "y x done z"}]},
    "905": {"id": "905", "truth": "shown", "trap": "none", "deciding_line": "result: ok",
            "turns": [{"cmd": "c", "output": "result: ok\nstatus: ok"}]},
}


def reply(turn, quote, verdict="shown"):
    return json.dumps({"reason": "r", "turn_id": turn, "quote": quote, "verdict": verdict})


def rec(i, rep, answer="shown", code="verified", verdict="shown", quote=""):
    return {"arm": "A", "id": i, "answer": answer, "code": code, "verdict": verdict, "quote": quote, "reply": rep}


RECS = {
    "1 FULL": rec("901", reply("T1", "deploy ok: site-a v2"), quote="deploy ok: site-a v2"),
    "2 PART": rec("901", reply("T1", "deploy ok"), quote="deploy ok"),
    "3 OTHER": rec("901", reply("T1", "done"), quote="done"),
    "4 PLUS": rec("901", reply("T1", "building\ndeploy ok: site-a v2"), quote="building\ndeploy ok: site-a v2"),
    "5 unverified": rec("901", reply("T1", "zzz"), answer="not shown", code="unverified_quote", quote="zzz"),
    "6 FULL T2": rec("902", reply("T2", "Error: 500", "contradicted"), answer="contradicted", verdict="contradicted", quote="Error: 500"),
    "7 FULL wrong": rec("902", reply("T1", "Error: 500"), quote="Error: 500"),
    "8 NO_D": rec("903", reply("T1", "all good"), quote="all good"),
    "9 wrong turn": rec("904", reply("T2", "x done"), quote="x done"),
    "10 PART ambiguous": rec("905", reply("T1", "ok"), quote="ok"),
    "11 failure net": rec("902", reply("T1", "Error: 500"), answer="not shown", code="shown_citing_failure", quote="Error: 500"),
    "12 spaces": rec("901", reply("T1", "  deploy ok: site-a v2  "), quote="deploy ok: site-a v2"),
    "13 bad turn": rec("905", reply("T9", "ok"), answer="not shown", code="wrong_turn", verdict="shown"),
    "14 model not shown": rec("905", reply(None, "", "not_shown"), answer="not shown", code="model_not_shown", verdict="not_shown"),
    "15 no reply": rec("905", None, answer="not shown", code="backend_error", verdict=None),
}
ROWS = {}
for name, r in RECS.items():
    row = Q4.build_row(r, ITEMS[r["id"]])
    row["lane"] = "local"
    ROWS[name] = row
check("cls 1", ROWS["1 FULL"]["cls"], "FULL")
check("cls 2", ROWS["2 PART"]["cls"], "PART")
check("cls 2 not ambiguous", ROWS["2 PART"]["ambiguous_part"], False)
check("cls 3", ROWS["3 OTHER"]["cls"], "OTHER")
check("cls 4", ROWS["4 PLUS"]["cls"], "PLUS")
check("gate 5 fails", ROWS["5 unverified"]["derived_gate_pass"], False)
check("cls 5 outside V", ROWS["5 unverified"]["cls"], None)
check("cls 6 (D held by both turns)", ROWS["6 FULL T2"]["cls"], "FULL")
check("cls 7", ROWS["7 FULL wrong"]["cls"], "FULL")
check("cls 8", ROWS["8 NO_D"]["cls"], "NO_D")
check("cls 9 wrong turn", (ROWS["9 wrong turn"]["cls"], ROWS["9 wrong turn"]["wrong_turn_text_match"]), ("OTHER", True))
check("cls 10", (ROWS["10 PART ambiguous"]["cls"], ROWS["10 PART ambiguous"]["ambiguous_part"]), ("PART", True))
check("cls 11 (post-gate downgrade is in V)", ROWS["11 failure net"]["cls"], "FULL")
check("cls 12 (quote is stripped)", ROWS["12 spaces"]["cls"], "FULL")
check("quote agrees with record", ROWS["12 spaces"]["quote_agrees_with_record"], True)
check("13 outside V", (ROWS["13 bad turn"]["in_V"], ROWS["13 bad turn"]["derived_gate_pass"]), (False, False))
check("14 outside V", (ROWS["14 model not shown"]["in_V"], ROWS["14 model not shown"]["derived_gate_pass"]), (False, False))
check("15 outside V", (ROWS["15 no reply"]["in_V"], ROWS["15 no reply"]["derived_gate_pass"]), (False, False))
check("15 model verdict none", ROWS["15 no reply"]["model_verdict"], None)
check("match 7", (ROWS["7 FULL wrong"]["answer_match"], ROWS["7 FULL wrong"]["verdict_match"]), (False, False))
check("match 11", (ROWS["11 failure net"]["answer_match"], ROWS["11 failure net"]["verdict_match"]), (False, False))

# summarise on rows 1..4, 6..12 except 5 and 12 is also in V: the V rows are 1,2,3,4,6,7,8,9,10,11,12
vrows = [ROWS[k] for k in ROWS]
s = Q4.summarise(vrows)
check("n_answers", s["n_answers"], 15)
check("n_pop", s["n_pop"], 11)
check("classes", s["classes"], {"FULL": 5, "NO_D": 1, "OTHER": 2, "PART": 2, "PLUS": 1})
check("ON", (s["answer_match"]["ON"]["k"], s["answer_match"]["ON"]["n"]), (6, 8))
check("FULL", (s["answer_match"]["FULL"]["k"], s["answer_match"]["FULL"]["n"]), (3, 5))
check("PART", (s["answer_match"]["PART"]["k"], s["answer_match"]["PART"]["n"]), (2, 2))
check("PLUS", (s["answer_match"]["PLUS"]["k"], s["answer_match"]["PLUS"]["n"]), (1, 1))
check("OTHER", (s["answer_match"]["OTHER"]["k"], s["answer_match"]["OTHER"]["n"]), (2, 2))
check("NO_D", (s["answer_match"]["NO_D"]["k"], s["answer_match"]["NO_D"]["n"]), (0, 1))
check("NOT_ON", (s["answer_match"]["NOT_ON"]["k"], s["answer_match"]["NOT_ON"]["n"]), (2, 3))
check("verdict ON", (s["model_verdict_match"]["ON"]["k"], s["model_verdict_match"]["ON"]["n"]), (6, 8))
check("share on", (s["shares"]["on_of_pop"]["k"], s["shares"]["on_of_pop"]["n"]), (8, 11))
check("share other", (s["shares"]["other_of_pop_on_items_with_deciding_line"]["k"],
                      s["shares"]["other_of_pop_on_items_with_deciding_line"]["n"]), (2, 10))
check("share no_d", (s["shares"]["no_d_of_pop"]["k"], s["shares"]["no_d_of_pop"]["n"]), (1, 11))
check("share not_on", (s["shares"]["not_on_of_pop"]["k"], s["shares"]["not_on_of_pop"]["n"]), (3, 11))
check("wrong shown", (s["wrong_with_real_quote"]["shown"]["final_answers"], s["wrong_with_real_quote"]["shown"]["wrong"]["k"],
                      s["wrong_with_real_quote"]["shown"]["wrong_by_group"]), (9, 2, {"NO_D": 1, "ON": 1}))
check("wrong contradicted", (s["wrong_with_real_quote"]["contradicted"]["final_answers"],
                             s["wrong_with_real_quote"]["contradicted"]["wrong"]["k"]), (1, 0))
check("ambiguous", s["ambiguous_part"], 1)
check("wrong turn", s["wrong_turn_text_match"], 1)
check("contrast present", s["contrast_on_minus_other"]["answer_match"]["diff"], round(6 / 8 - 2 / 2, 4))
check("matrix ON", s["answer_truth_matrix"]["ON"], {"contradicted|contradicted": 1, "not shown|contradicted": 1,
                                                    "shown|contradicted": 1, "shown|shown": 5})
sv = Q4.summarise(vrows, "verified")
check("verified-only n_pop", sv["n_pop"], 10)  # row 11 has code shown_citing_failure
cross = Q4.crosscheck(vrows)
check("crosscheck clean", cross["discrepancies"], 0)
bad = dict(ROWS["1 FULL"])
bad["in_V"], bad["derived_gate_pass"] = True, False
check("crosscheck catches", Q4.crosscheck([bad])["discrepancy_list"][0]["kind"], "recorded_in_V_but_gate_not_derived")
bad2 = dict(ROWS["5 unverified"])
bad2["derived_gate_pass"] = True
check("crosscheck catches 2", Q4.crosscheck([bad2])["discrepancy_list"][0]["kind"], "recorded_gate_failure_but_derived_pass")
unres = Q4.build_row(rec("901", reply("T1", "zzz"), code="verified", quote="zzz"), ITEMS["901"])
check("unresolved class", unres["cls"], "UNRESOLVED")
empty = Q4.summarise([])
check("empty summary", (empty["n_pop"], empty["shares"]["on_of_pop"]["rate"], empty["contrast_on_minus_other"]["answer_match"]), (0, None, None))
check("thin flag", Q4.summarise(vrows[:3])["thin"], True)

# ---- Q3: the certainty rule on 10 invented answers --------------------------------
Q3ROWS = {}
for i, (a, c) in enumerate([("shown", "sure"), ("shown", "sure"), ("shown", "unsure"), ("shown", "unsure"), ("shown", None),
                            ("contradicted", "unsure"), ("contradicted", "sure"), ("not shown", "unsure"),
                            ("not shown", "sure"), ("contradicted", None)], 1):
    Q3ROWS[f"{i:03d}"] = {"arm": "U-Q", "id": f"{i:03d}", "answer": a, "certainty": c, "no_answer": False,
                          "reply": json.dumps({"verdict": a, "certainty": c}) if c else '{"verdict": "shown"}'}
Q3ROWS["010"]["reply"] = "not json at all"
Q3ROWS["005"]["no_answer"] = True
TRUTH = dict(zip([f"{i:03d}" for i in range(1, 11)],
                 ["shown", "not shown", "not shown", "shown", "contradicted", "contradicted", "shown", "not shown", "shown", "not shown"]))
ids = sorted(Q3ROWS)
a = Q3.analyse(Q3ROWS, TRUTH, ids)
kn = lambda d: (d["k"], d["n"])  # noqa: E731
check("q3 n", a["n"], 10)
check("q3 cert counts", {c: a["certainty_counts"][c]["k"] for c in Q3.CATS}, {"sure": 4, "unsure": 4, "unmarked": 2})
check("q3 unmarked reasons", {r: a["unmarked_reasons"][r]["k"] for r in Q3.REASONS},
      {"no_answer": 1, "reply_not_a_json_object": 1, "certainty_missing_or_invalid": 0})
check("q3 acc sure", kn(a["accuracy_by_certainty"]["sure"]), (1, 4))
check("q3 acc unsure", kn(a["accuracy_by_certainty"]["unsure"]), (3, 4))
check("q3 acc unmarked", kn(a["accuracy_by_certainty"]["unmarked"]), (0, 2))
check("q3 sure-unsure", a["sure_minus_unsure"]["diff"], -0.5)
check("q3 constant not shown", kn(a["constant_not_shown_right"]), (4, 10))
R = a["rule_R_all"]
check("R wrong shown of shown", (kn(R["wrong_shown_of_shown_answers"]["before"]), kn(R["wrong_shown_of_shown_answers"]["after"])), ((3, 5), (1, 2)))
check("R false shown rate", (kn(R["false_shown_rate"]["before"]), kn(R["false_shown_rate"]["after"])), ((3, 6), (1, 6)))
check("R removed", kn(R["wrong_shown_removed"]), (2, 3))
check("R removed split", R["wrong_shown_removed_split"], {"of_removed": 2, "now_right_truth_not_shown": 1, "still_wrong_truth_contradicted": 1})
check("R right", (kn(R["right"]["before"]), kn(R["right"]["after"])), ((4, 10), (4, 10)))
check("R given up", kn(R["correct_given_up"]), (2, 4))
check("R given up by type", (kn(R["correct_given_up_by_type"]["true_shown_given_up_of_right_shown"]),
                             kn(R["correct_given_up_by_type"]["true_contradicted_given_up_of_right_contradicted"])), ((1, 2), (1, 1)))
check("R made right", kn(R["wrong_made_right"]), (2, 6))
check("R exchange", R["exchange"], {"wrong_shown_removed": 2, "correct_given_up": 2, "given_up_per_wrong_shown_removed": 1.0})
check("R false contradicted", (kn(R["false_contradicted"]["before"]), kn(R["false_contradicted"]["after"])), ((2, 8), (1, 8)))
check("R ids", (R["ids"]["wrong_shown_removed"], R["ids"]["correct_given_up"]), (["003", "005"], ["004", "006"]))
S = a["rule_R_shown"]
check("S right after", kn(S["right"]["after"]), (4, 10))
check("S given up", kn(S["correct_given_up"]), (1, 4))
check("S made right", kn(S["wrong_made_right"]), (1, 6))
check("S removed", kn(S["wrong_shown_removed"]), (2, 3))
cg = a["catch_and_giveup"]
check("flag share", kn(cg["flagged_share_of_all"]), (6, 10))
check("wrong flagged", kn(cg["wrong_flagged_of_wrong"]), (3, 6))
check("right flagged", kn(cg["right_flagged_of_right"]), (3, 4))
check("wrong shown flagged", kn(cg["wrong_shown_flagged_of_wrong_shown"]), (2, 3))
check("right shown flagged", kn(cg["right_shown_flagged_of_right_shown"]), (1, 2))
check("wrong contra flagged", kn(cg["wrong_contradicted_flagged_of_wrong_contradicted"]), (1, 2))
check("right contra flagged", kn(cg["right_contradicted_flagged_of_right_contradicted"]), (1, 1))
check("catch minus giveup", cg["catch_minus_giveup_all"]["diff"], -0.25)
cells = a["cells"]
check("cell shown|sure", (cells["shown|sure"]["n"], kn(cells["shown|sure"]["right"]), kn(cells["shown|sure"]["truth_not_shown"]), cells["shown|sure"]["net_if_replaced"]), (2, (1, 2), (1, 2), 0))
check("cell shown|unsure", (cells["shown|unsure"]["n"], kn(cells["shown|unsure"]["right"]), cells["shown|unsure"]["net_if_replaced"]), (2, (1, 2), 0))
check("cell contradicted|unsure", (cells["contradicted|unsure"]["n"], cells["contradicted|unsure"]["net_if_replaced"]), (1, -1))
check("cell contradicted|unmarked", (cells["contradicted|unmarked"]["n"], cells["contradicted|unmarked"]["net_if_replaced"]), (1, 1))
check("cell not shown|sure", (cells["not shown|sure"]["n"], cells["not shown|sure"]["net_if_replaced"]), (1, 0))
check("cell not shown|unmarked empty", cells["not shown|unmarked"]["n"], 0)
check("sub-set ids", Q3.analyse(Q3ROWS, TRUTH, ["001", "002", "999"])["n"], 2)

# ---- the writer never overwrites ----------------------------------------------------
with tempfile.TemporaryDirectory() as d:
    p1 = C.write_new_json("results-x", {"a": 1}, d)
    p2 = C.write_new_json("results-x", {"a": 2}, d)
    check("writer names", (p1.name, p2.name), ("results-x-v1.json", "results-x-v2.json"))
    check("writer keeps v1", json.loads(p1.read_text(encoding="utf-8")), {"a": 1})

# ---- the seal check (on a throwaway folder) -----------------------------------------
with tempfile.TemporaryDirectory() as d:
    old_here = C.HERE
    C.HERE = Path(d)
    try:
        lines = []
        for k, name in enumerate(C.SEAL_FILES):
            (Path(d) / name).write_text(f"file {name}", encoding="utf-8")
            h = hashlib.sha256((Path(d) / name).read_bytes()).hexdigest()
            lines.append(f"{h} *{name}" if k % 2 else f"{h}  {name}")
        (Path(d) / "DESIGN-SHA256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        ok = C.check_seal()
        check("seal passes", all(ok["files_match"].values()), True)
        (Path(d) / "q3_certainty.py").write_text("changed", encoding="utf-8")
        try:
            C.check_seal()
            check("seal catches a change", "no error", "SystemExit")
        except SystemExit:
            check("seal catches a change", True, True)
        (Path(d) / "DESIGN-SHA256.txt").unlink()
        try:
            C.check_seal()
            check("seal missing", "no error", "SystemExit")
        except SystemExit:
            check("seal missing", True, True)
    finally:
        C.HERE = old_here

# ---- both scripts end to end on a made-up copy of the whole setup (no real data is touched) ------------
def synth_item(n):
    truth = ("shown", "contradicted", "not_shown")[n % 3]
    deciding = {"shown": f"result {n}: OK", "contradicted": f"status {n}: FAIL", "not_shown": ""}[truth]
    return {"id": f"{n:03d}", "claim": f"claim {n}", "truth": truth, "trap": ("none", "retry", "narration", "truncated")[n % 4],
            "deciding_line": deciding, "why": "w",
            "turns": [{"cmd": "c1", "output": f"prep {n}\nresult {n}: OK\nend {n}", "narration": ""},
                      {"cmd": "c2", "output": f"noise {n}\nstatus {n}: FAIL", "narration": ""}]}


def synth_q4(arm, model, item, variant):
    n, truth, d = int(item["id"]), item["truth"], item["deciding_line"]
    mode = (n + variant) % 6
    turn = "T1" if truth == "shown" else "T2"
    base = {"arm": arm, "model": model, "id": item["id"]}
    if n % 17 == 0:
        return {**base, "answer": "not shown", "code": "backend_error", "verdict": None, "quote": "", "reply": None}
    verdict, quote, code, answer, t_id = "shown", "", "verified", None, turn
    if mode == 0 and d:
        quote, verdict = d, truth
    elif mode == 1 and d:
        quote, verdict = d[:6], truth
    elif mode == 2:
        quote, t_id = f"prep {n}", "T1"
    elif mode == 3:
        quote, code = "not in the log", "unverified_quote"
    elif mode == 4:
        return {**base, "answer": "not shown", "code": "model_not_shown", "verdict": "not_shown", "quote": "",
                "reply": json.dumps({"reason": "r", "turn_id": None, "quote": "", "verdict": "not_shown"})}
    else:
        quote, t_id, code = f"status {n}: FAIL", "T2", "shown_citing_failure"
    answer = "not shown" if code != "verified" else verdict
    return {**base, "answer": answer, "code": code, "verdict": verdict, "quote": quote,
            "reply": json.dumps({"reason": "r", "turn_id": t_id, "quote": quote, "verdict": verdict})}


def synth_q3(arm, model, item, variant):
    n = int(item["id"])
    answer = ("shown", "contradicted", "not shown")[(n + variant) % 3]
    cert = (None, "sure", "unsure", "sure")[n % 4]
    body = {"verdict": answer.replace(" ", "_"), "certainty": cert} if cert else {"verdict": answer.replace(" ", "_")}
    return {"arm": arm, "model": model, "id": item["id"], "answer": answer, "code": "verified", "certainty": cert,
            "settle_cmd": None, "settle_expect": None, "no_answer": False, "reply": json.dumps(body)}


def integration():
    import shutil
    import sys
    tmp = Path(tempfile.mkdtemp(prefix="rescore-selftest-"))
    work, data = tmp / "work", tmp / "data"
    work.mkdir()
    data.mkdir()
    saved = (C.HERE, dict(C.PATHS), dict(C.EXPECTED_SHA256), sys.argv)
    try:
        for name in C.SEAL_FILES:
            shutil.copy(saved[0] / name, work / name)
        bank = [synth_item(n) for n in range(1, 301)]
        files = {"bank": bank, "batch5": [it for it in bank if 161 <= int(it["id"]) <= 200]}
        by_id = {it["id"]: it for it in bank}
        fresh = [by_id[i] for i in C.FRESH]
        files["run2_local"] = [synth_q4(a, m, it, v) for v, (a, m) in enumerate([("A", "qa"), ("B", "qb")]) for it in fresh]
        files["run2_fast"] = [synth_q4(a, m, it, v + 2) for v, (a, m) in enumerate([("F-Q", "qc"), ("F-G", "qd")]) for it in fresh]
        files["run3"] = [synth_q3(a, m, it, v) for v, (a, m) in enumerate([("U-Q", "qc"), ("U-G", "qd")]) for it in fresh]
        paths = dict(saved[1])
        for key, rows in files.items():
            paths[key] = data / f"{key}.jsonl"
            paths[key].write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        for key in ("score_run3", "score_run2_local", "score_run2_fast"):
            paths[key] = data / f"{key}.json"
        for key in ("src_receipts_model", "src_run2", "src_run_pair", "src_run3"):
            paths[key] = data / f"{key}.txt"
            paths[key].write_text("x", encoding="utf-8")
        C.HERE = work
        # first pass: no stored scores exist (the report-only steps must degrade, not crash)
        paths["score_run3"].write_text("{}", encoding="utf-8")
        paths["score_run2_local"].write_text("{}", encoding="utf-8")
        paths["score_run2_fast"].write_text("{}", encoding="utf-8")
        C.PATHS.clear()
        C.PATHS.update(paths)
        C.EXPECTED_SHA256.clear()
        C.EXPECTED_SHA256.update({k: C.sha256_file(p) for k, p in paths.items() if k in saved[2]})
        lines = [f"{C.sha256_file(work / n)} *{n}" for n in C.SEAL_FILES]
        (work / "DESIGN-SHA256.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        for mod, script in ((Q3, "q3_certainty.py"), (Q4, "q4_quote_decides.py")):
            sys.argv = [script, "--run-at", "2000-01-01T00:00:00Z"]
            mod.main()
        r3 = json.loads((work / "results-q3-v1.json").read_text(encoding="utf-8"))
        r4 = json.loads((work / "results-q4-v1.json").read_text(encoding="utf-8"))
        a = r3["sets"]["fresh_161_300"]["U-Q"]
        check("int q3 n", a["n"], 140)
        check("int q3 cert sums", sum(a["certainty_counts"][c]["k"] for c in Q3.CATS), 140)
        check("int q3 primary n", r3["sets"]["primary_201_300"]["U-G"]["n"], 100)
        check("int q3 reconciliation degrades", r3["reconciliation_with_score_run3"]["tally"]["checks"], 0)
        check("int q4 rows", len(r4["rows"]), 560)
        check("int q4 crosscheck", r4["checks"]["gate_crosscheck"]["discrepancies"], 0)
        check("int q4 bank checks", (r4["checks"]["bank"]["batch5_equal_to_bank"], r4["checks"]["bank"]["deciding_line_empty_iff_truth_not_shown"]), (True, True))
        loc = r4["sets"]["fresh_161_300"]["local"]
        check("int q4 pooled answers", loc["pooled"]["all"]["n_answers"], 280)
        check("int q4 arm answers", loc["arms"]["A"]["all"]["n_answers"], 140)
        check("int q4 pooled = sum of arms", loc["pooled"]["all"]["n_pop"], loc["arms"]["A"]["all"]["n_pop"] + loc["arms"]["B"]["all"]["n_pop"])
        check("int q4 trap keys", sorted(loc["pooled"]["by_trap"]), sorted(r4["traps"]))
        check("int q4 trap rows add up", sum(loc["pooled"]["by_trap"][t]["n_answers"] for t in r4["traps"]), 280)
        check("int q4 classes add up", sum(loc["pooled"]["all"]["classes"].values()), loc["pooled"]["all"]["n_pop"])
        check("int q4 reconciliation degrades", r4["reconciliation_with_stored_run2_scores"]["tally"]["checks"], 0)
        # second pass: stored scores built from the first pass, to exercise the "agree" path
        st3 = {"sets": {}}
        for s_name, arms in r3["sets"].items():
            st3["sets"][s_name] = {}
            for arm, res in arms.items():
                R = res["rule_R_all"]
                cc = res["certainty_counts"]
                st3["sets"][s_name][arm] = {
                    "certainty": {"sure": cc["sure"]["k"], "unsure": cc["unsure"]["k"], "None": cc["unmarked"]["k"]},
                    "right_when_sure": res["accuracy_by_certainty"]["sure"], "right_when_unsure": res["accuracy_by_certainty"]["unsure"],
                    "raw": {"right": R["right"]["before"], "false_shown": R["false_shown_rate"]["before"]},
                    "policy_U": {"right": R["right"]["after"], "false_shown": R["false_shown_rate"]["after"]}}
        paths["score_run3"].write_text(json.dumps(st3), encoding="utf-8")
        for lane, key in (("local", "score_run2_local"), ("fast", "score_run2_fast")):
            st = {"sets": {}}
            for s_name, ids in C.SETS.items():
                idset = set(ids)
                st["sets"][s_name] = {f"run2-{lane}": {}}
                for arm in Q4.LANES[lane]["arms"]:
                    rs = [r for r in r4["rows"] if r["lane"] == lane and r["arm"] == arm and r["id"] in idset]
                    other = [r for r in rs if r["truth"] != "shown"]
                    st["sets"][s_name][f"run2-{lane}"][arm] = {
                        "right": C.frac(sum(r["answer_match"] for r in rs), len(rs)),
                        "false_shown": C.frac(sum(1 for r in other if r["answer"] == "shown"), len(other)),
                        "answers": {k: sum(1 for r in rs if r["answer"] == k) for k in sorted({r["answer"] for r in rs})}}
            paths[key].write_text(json.dumps(st), encoding="utf-8")
        C.EXPECTED_SHA256.update({k: C.sha256_file(p) for k, p in paths.items() if k in saved[2]})
        for mod, script in ((Q3, "q3_certainty.py"), (Q4, "q4_quote_decides.py")):
            sys.argv = [script, "--run-at", "2000-01-01T00:00:01Z"]
            mod.main()
        r3b = json.loads((work / "results-q3-v2.json").read_text(encoding="utf-8"))
        r4b = json.loads((work / "results-q4-v2.json").read_text(encoding="utf-8"))
        check("int q3 reconciliation agrees", r3b["reconciliation_with_score_run3"]["tally"], {"checks": 36, "agree": 36, "differ": 0})
        check("int q4 reconciliation agrees", r4b["reconciliation_with_stored_run2_scores"]["tally"], {"checks": 24, "agree": 24, "differ": 0})
        check("int first results untouched", json.loads((work / "results-q3-v1.json").read_text(encoding="utf-8"))["meta"]["run_at"], "2000-01-01T00:00:00Z")
        # an input that changed must stop the run
        paths["run3"].write_text("changed\n", encoding="utf-8")
        try:
            sys.argv = ["q3_certainty.py", "--run-at", "2000-01-01T00:00:02Z"]
            Q3.main()
            check("int stops on changed input", "no error", "SystemExit")
        except SystemExit:
            check("int stops on changed input", True, True)
    finally:
        C.HERE = saved[0]
        C.PATHS.clear()
        C.PATHS.update(saved[1])
        C.EXPECTED_SHA256.clear()
        C.EXPECTED_SHA256.update(saved[2])
        sys.argv = saved[3]
        shutil.rmtree(tmp, ignore_errors=True)


integration()

if FAILS:
    print(f"SELFTEST FAILED: {len(FAILS)} of {CHECKS} checks")
    for f_ in FAILS:
        print("  -", f_)
    raise SystemExit(1)
print(f"SELFTEST OK: {CHECKS} checks passed")
