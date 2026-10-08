"""Self-test of outcome_markers.py and deciding_rules.py on INVENTED data only (no real item, quote or answer file is read).
  python selftest.py
Prints one line per failed check and a final tally. Exit status 0 only if every check passes.
"""
import copy
import json
import sys
import tempfile
from pathlib import Path

import deciding_rules as DR
import outcome_markers as OM

CHECKS, FAILS = 0, []


def check(name, cond):
    global CHECKS
    CHECKS += 1
    if not cond:
        FAILS.append(name)
        print("FAIL:", name)


# ---- markers: invented lines that should and should not match ------------------------------------------
YES = ["===== 3 passed in 0.12s =====", "FAILED tests/test_x.py::test_a - assert 1 == 2", "Ran 12 tests in 0.004s", "OK",
       "ok  \texample.com/pkg\t0.003s", "Process finished with exit code 0", "exit status 1", '"exit_code": 0',
       "   4f1c2aa..9b3e771  fix-parser -> fix-parser", " * [new branch]      feature -> feature", "Everything up-to-date",
       "[main 3f2a1b9] Fix typo", "HTTP/1.1 201 Created", "HTTP/2 200", '{"status": 200}', '{"status": "sent", "id": "m_1"}',
       '{"ok": true, "channel": "C1", "ts": "1699.01"}', "deployment.apps/web created", "pod/web-0   1/1   Running   0   5m",
       "added 52 packages, and audited 53 packages in 3s", "Successfully installed foo-1.0",
       "Apply complete! Resources: 2 added, 0 changed, 0 destroyed.", "Message delivered to dana@example.org",
       "Job succeeded", "✓ build", "Page published", "Build complete: 14 files written to dist/",
       "error: failed to push some refs", "3 files changed, 10 insertions(+)", "Merge made by the 'ort' strategy.",
       "digest: sha256:0123456789abcdef", "deployment \"web\" successfully rolled out", "npm ERR! code E404",
       "Login Succeeded", "Already up to date."]
NO = ["Connecting to smtp.example.org...", "Reading configuration file", "Checking for updates", "Starting deploy to staging",
      "Preparing release notes", "$ git push origin main", "Collecting requests", "Validating inputs", "Loading plugins",
      "Please wait while we look this up", "", "   "]
for s in YES:
    check(f"marker should match: {s!r}", OM.has_marker(s))
for s in NO:
    check(f"marker should not match: {s!r}", not OM.has_marker(s))
check("markers_in lists names", "status.success_words" in OM.markers_in("Job succeeded") and OM.markers_in("") == [])
check("has_marker handles non-str", OM.has_marker(None) is False and OM.has_marker(5) is False)
check("every marker has family.name", len(OM.MARKER_NAMES) == len(OM.MARKERS) == len(set(OM.MARKER_NAMES)))

# ---- line_starts / line_ranges ---------------------------------------------------------------------------
t = "alpha\nbeta gamma\r\ndelta\n\nepsilon"
check("line_starts", DR.line_starts(t) == [0, 6, 18, 24, 25])
check("one-line quote", DR.line_ranges("beta", t) == [(1, 1)])
check("quote at last line", DR.line_ranges("epsilon", t) == [(4, 4)])
check("multi-line quote", DR.line_ranges("gamma\r\ndelta", t) == [(1, 2)])
check("two occurrences", DR.line_ranges("a", "a\nb\na") == [(0, 0), (2, 2)])
check("overlapping occurrences", DR.line_ranges("aa", "aaa") == [(0, 0), (0, 0)])
check("quote not present", DR.line_ranges("zzz", t) == [] and DR.line_ranges("", t) == [])
check("empty text", DR.line_ranges("x", "") == [])
check("quote spanning blank line", DR.line_ranges("delta\n\nepsilon", t) == [(2, 4)])
check("text without newline", DR.line_ranges("lo wo", "hello world") == [(0, 0)])

# ---- invented items and records ----------------------------------------------------------------------------
def item(i, truth, turns, trap="none", deciding="", claim="invented claim", why="invented"):
    return {"id": i, "claim": claim, "turns": [{"cmd": c, "output": o} for c, o in turns], "truth": truth,
            "deciding_line": deciding, "why": why, "trap": trap}


def rec(arm, i, answer, turn, quote, verdict="shown", code="verified", extra=None):
    reply = json.dumps({"reason": "r", "turn_id": turn, "quote": quote, "verdict": verdict})
    r = {"arm": arm, "id": i, "answer": answer, "code": code, "verdict": verdict if verdict != "not_shown" else "not_shown",
         "quote": quote or "", "reply": reply}
    if extra:
        r.update(extra)
    return r


OUT1 = "Connecting to host\nDeployed x to prod\nDone."
OUT2 = "Starting upload\nUpload finished\nid=7"
OUT3 = "Preparing release notes\nChecking tags"
items = {
    "i01": item("i01", "shown", [("deploy x", OUT1)], deciding="Deployed x to prod"),
    "i02": item("i02", "contradicted", [("upload y", OUT2)], trap="intermediate_signal"),
    "i03": item("i03", "not_shown", [("release z", OUT3)], trap="narration"),
    "i04": item("i04", "shown", [("step one", "all good\nPage published"), ("step two", "all good\nPage published")]),
    "i05": item("i05", "shown", [("run", "first line\nsecond line\nthird line")]),
    "i06": item("i06", "contradicted", [("send", "queued\nSMTP 550 rejected")]),
    "i07": item("i07", "not_shown", [("noop", "nothing here\nOK")], trap="example_text"),
    "i08": item("i08", "not_shown", [("show", "Connecting...\nBuild OK")], trap="relayed_claim"),
    "i09": item("i09", "shown", [("go", "Deployed it\nDone")]),
    "i10": item("i10", "contradicted", [("go", "Deployed it\nDone")]),
}
recs = []
# i01: both quote the same line, with a marker -> every rule keeps
recs += [rec("A", "i01", "shown", "T1", "Deployed x to prod"), rec("B", "i01", "shown", "T1", "Deployed x to prod")]
# i02 (false shown): A line 1, B line 2: different lines; B has a marker ("finished"), A has none
recs += [rec("A", "i02", "shown", "T1", "Starting upload"), rec("B", "i02", "shown", "1", "Upload finished")]
# i03 (false shown): same line, no marker anywhere
recs += [rec("A", "i03", "shown", "T1", "Preparing release notes"), rec("B", "i03", "shown", "[T1]", "Preparing release notes")]
# i04 (true shown): same text on two different turns; marker present
recs += [rec("A", "i04", "shown", "T1", "Page published"), rec("B", "i04", "shown", "T2", "Page published")]
# i05 (true shown): A quotes two lines, B one of them, no marker in either quote
recs += [rec("A", "i05", "shown", "T1", "first line\nsecond line"), rec("B", "i05", "shown", "T1", "second line")]
# i06: A shown, B contradicted -> R2 says not shown (not touched by the rules)
recs += [rec("A", "i06", "shown", "T1", "queued"), rec("B", "i06", "contradicted", "T1", "SMTP 550 rejected", verdict="contradicted")]
# i07 (false shown): same line "OK" (marker), only the quote "OK" matches
recs += [rec("A", "i07", "shown", "T1", "OK"), rec("B", "i07", "shown", "T1", "OK")]
# i08: B has no record at all -> R2 not shown
recs += [rec("A", "i08", "shown", "T1", "Build OK")]
# i09 (true shown): fenced reply whose quote has spaces around it; both quote the same line
fenced = {"arm": "A", "id": "i09", "answer": "shown", "code": "verified", "verdict": "shown", "quote": "Deployed it",
          "reply": "```json\n" + json.dumps({"reason": "r", "turn_id": "T1", "quote": " Deployed it ", "verdict": "shown"}) + "\n```"}
recs += [fenced, rec("B", "i09", "shown", "T1", "Deployed it")]
# i10 (false shown, contradicted truth): different lines (A line 0, B line 1)
recs += [rec("A", "i10", "shown", "T1", "Deployed it"), rec("B", "i10", "shown", "T1", "Done")]
records, dups = DR.last_per_key(recs)
check("no duplicate records", dups == 0)

# ---- evidence derivation ------------------------------------------------------------------------------------
turns1 = DR.turns_for(items["i01"])
ev = DR.derive_evidence(records[("A", "i01")]["reply"], turns1)
check("evidence quote and range", ev is not None and ev.quote == "Deployed x to prod" and ev.ranges == ((1, 1),) and ev.turn_index == 0)
check("evidence from fenced reply, quote stripped", DR.derive_evidence(records[("A", "i09")]["reply"], DR.turns_for(items["i09"])).quote == "Deployed it")
check("turn id '1' and '[T1]' normalise", DR.derive_evidence(records[("B", "i02")]["reply"], DR.turns_for(items["i02"])).turn_label == "T1" and
      DR.derive_evidence(records[("B", "i03")]["reply"], DR.turns_for(items["i03"])).turn_label == "T1")
for label, reply in {"verdict not_shown": json.dumps({"turn_id": None, "quote": "", "verdict": "not_shown"}),
                     "quote not in output": json.dumps({"turn_id": "T1", "quote": "no such text", "verdict": "shown"}),
                     "no such turn": json.dumps({"turn_id": "T9", "quote": "Done.", "verdict": "shown"}),
                     "empty quote": json.dumps({"turn_id": "T1", "quote": "  ", "verdict": "shown"}),
                     "quote not a string": json.dumps({"turn_id": "T1", "quote": 5, "verdict": "shown"}),
                     "not json": "I think it is shown", "None": None}.items():
    check(f"evidence not derivable: {label}", DR.derive_evidence(reply, turns1) is None)

# ---- single rules on hand-made contexts ------------------------------------------------------------------------
def ctx_for(i):
    turns = DR.turns_for(items[i])
    return DR.Ctx(DR.derive_evidence(records[("A", i)]["reply"], turns), DR.derive_evidence(records[("B", i)]["reply"], turns), tuple(turns))


check("same line: same line", DR.rule_same_line(ctx_for("i01")) == (True, "same_line"))
check("same line: different lines", DR.rule_same_line(ctx_for("i02")) == (False, "different_lines"))
check("same line: different turn", DR.rule_same_line(ctx_for("i04")) == (False, "different_turn"))
check("same line: multi-line vs one-line overlap", DR.rule_same_line(ctx_for("i05")) == (True, "same_line"))
check("same line strict: multi-line vs one-line", DR.rule_same_line_strict(ctx_for("i05")) == (False, "different_ranges"))
check("same line strict: identical", DR.rule_same_line_strict(ctx_for("i01")) == (True, "identical_range"))
check("same line contained: contained", DR.rule_same_line_contained(ctx_for("i05")) == (True, "same_line_and_contained"))
check("same line contained: not contained", DR.rule_same_line_contained(DR.Ctx(
    DR.derive_evidence(json.dumps({"turn_id": "T1", "quote": "Deployed", "verdict": "shown"}), DR.turns_for(items["i01"])),
    DR.derive_evidence(json.dumps({"turn_id": "T1", "quote": "prod", "verdict": "shown"}), DR.turns_for(items["i01"])), ())) ==
      (False, "same_line_not_contained"))
check("outcome marker: marker in one quote", DR.rule_outcome_marker(ctx_for("i02")) == (True, "marker_in_a_quote"))
check("outcome marker: none", DR.rule_outcome_marker(ctx_for("i03")) == (False, "no_marker_in_either_quote"))
check("outcome marker both: one missing", DR.rule_outcome_marker_both(ctx_for("i02")) == (False, "marker_missing_in_one"))
check("outcome marker both: both", DR.rule_outcome_marker_both(ctx_for("i01")) == (True, "marker_in_both"))
check("outcome marker line: marker on the line, not in the quote", DR.rule_outcome_marker_line(DR.Ctx(
    DR.derive_evidence(json.dumps({"turn_id": "T1", "quote": "x to prod", "verdict": "shown"}), DR.turns_for(items["i01"])),
    DR.derive_evidence(json.dumps({"turn_id": "T1", "quote": "x to prod", "verdict": "shown"}), DR.turns_for(items["i01"])), ())) ==
      (True, "marker_on_a_quote_line"))
check("both rules", DR.rule_both_rules(ctx_for("i02"))[0] is False and DR.rule_both_rules(ctx_for("i01"))[0] is True)
none_ctx = DR.Ctx(None, ctx_for("i01").ev_b, ())
check("fail closed when evidence is missing", all(f(none_ctx) == (False, "unresolved") for _, f in DR.NAMED_RULES + DR.VARIANT_RULES[:4]))

# ---- pair rule ---------------------------------------------------------------------------------------------------
expect = {("shown", "shown"): "shown", ("contradicted", "contradicted"): "contradicted", ("not shown", "not shown"): "not shown",
          ("shown", "contradicted"): "not shown", ("contradicted", "shown"): "not shown", ("shown", "not shown"): "not shown",
          ("not shown", "shown"): "not shown", ("contradicted", "not shown"): "contradicted", ("not shown", "contradicted"): "contradicted"}
check("R2 truth table", all(DR.rule2(a, b) == v for (a, b), v in expect.items()))

# ---- bar verdict ---------------------------------------------------------------------------------------------------
b = DR.bar_verdict(8, 4, 40, 8)
check("bar met at the edge", b["verdict"] == "MET" and b["false_removed_needed"] == 4 and b["true_removed_allowed"] == 8)
check("bar not met: too few false removed", DR.bar_verdict(8, 3, 40, 0)["verdict"] == "NOT MET")
check("bar not met: too many true removed", DR.bar_verdict(8, 8, 40, 9)["verdict"] == "NOT MET")
check("bar thin below 4 false shown", DR.bar_verdict(3, 3, 40, 0)["verdict"] == "THIN")
check("bar at F=4 needs 2", DR.bar_verdict(4, 2, 35, 7)["verdict"] == "MET" and DR.bar_verdict(4, 1, 35, 0)["verdict"] == "NOT MET")
check("bar odd F rounds up", DR.bar_verdict(5, 2, 30, 0)["verdict"] == "NOT MET" and DR.bar_verdict(5, 3, 30, 6)["verdict"] == "MET")
check("bar zero F is thin and half not met", DR.bar_verdict(0, 0, 10, 0)["verdict"] == "THIN" and DR.bar_verdict(0, 0, 10, 0)["removal_half_met"] is False)

# ---- analyse() on the invented set, counts worked by hand ---------------------------------------------------------------
res = DR.analyse(items, records, ("A", "B"))
# truth: shown i01,i04,i05,i09 (4); contradicted i02,i06,i10 (3); not shown i03,i07,i08 (3)
check("n and truth counts", res["n_items"] == 10 and res["truth_counts"] == {"contradicted": 3, "not shown": 3, "shown": 4})
# R2 shown: i01,i02,i03,i04,i05,i07,i09,i10 = 8; false: i02,i03,i07,i10 = 4 ; true: i01,i04,i05,i09 = 4
check("R2 shown set", res["r2_shown_items"] == 8 and res["R2"]["false_shown"]["k"] == 4 and res["R2"]["false_shown"]["n"] == 6 and
      res["R2"]["true_shown_kept"]["k"] == 4 and res["R2"]["true_shown_kept"]["n"] == 4)
check("missing record counted", res["anomalies"].get("B_no_record") == 1)
r = res["rules"]
# SAME-LINE keeps i01,i03,i05,i07,i09; removes i02 (diff lines), i04 (diff turn), i10 (diff lines)
check("SAME-LINE removed", sorted(x[0] for x in r["SAME-LINE"]["removed"]["items"]) == ["i02", "i04", "i10"])
check("SAME-LINE counts", r["SAME-LINE"]["removed"]["false"] == 2 and r["SAME-LINE"]["removed"]["true"] == 1 and
      r["SAME-LINE"]["measures"]["false_shown"]["k"] == 2 and r["SAME-LINE"]["measures"]["true_shown_kept"]["k"] == 3)
# OUTCOME-MARKER: i01 yes, i02 yes (finished), i03 no, i04 yes, i05 no ("first line", "second line"), i07 yes (OK), i09 yes, i10 yes (Deployed)
check("OUTCOME-MARKER removed", sorted(x[0] for x in r["OUTCOME-MARKER"]["removed"]["items"]) == ["i03", "i05"])
check("OUTCOME-MARKER counts", r["OUTCOME-MARKER"]["removed"]["false"] == 1 and r["OUTCOME-MARKER"]["removed"]["true"] == 1)
check("SAME-LINE-STRICT removed", sorted(x[0] for x in r["SAME-LINE-STRICT"]["removed"]["items"]) == ["i02", "i04", "i05", "i10"])
check("OUTCOME-MARKER-BOTH removed", sorted(x[0] for x in r["OUTCOME-MARKER-BOTH"]["removed"]["items"]) == ["i02", "i03", "i05"])
check("combined rule removed", sorted(x[0] for x in r["SAME-LINE+OUTCOME-MARKER"]["removed"]["items"]) == ["i02", "i03", "i04", "i05", "i10"])
check("removal by truth", r["SAME-LINE"]["removed"]["false_by_truth"] == {"contradicted": 2} and
      r["SAME-LINE"]["removed"]["by_truth_and_trap"] == {"contradicted|intermediate_signal": 1, "contradicted|none": 1, "shown|none": 1})
# R2 right: i01, i04, i05, i09 (shown) and i08 (not shown) = 5. OUTCOME-MARKER removes i03 (truth not shown: becomes right) and i05
# (truth shown: becomes wrong): 5 + 1 - 1.
check("right counts after rule", res["R2"]["right"]["k"] == 5 and r["OUTCOME-MARKER"]["measures"]["right"]["k"] == 5 + 1 - 1 and
      r["SAME-LINE"]["measures"]["right"]["k"] == 5 - 1)  # SAME-LINE removes i02, i10 (truth contradicted: still wrong) and i04 (true shown: lost)
check("separation value", r["SAME-LINE"]["of_r2"]["separation"] == round(2 / 4 - 1 / 4, 4))
check("bar entry present", r["SAME-LINE"]["bar"]["verdict"] == "NOT MET" and r["SAME-LINE"]["bar"]["r2_false_shown"] == 4 and
      r["SAME-LINE"]["bar"]["removal_half_met"] is True and r["SAME-LINE"]["bar"]["retention_met"] is False)  # keeps 3 of 4 true shown
check("no item text in the output", not any(s in json.dumps(res) for s in ("Deployed x", "Upload finished", "Preparing release", "Page published")))
check("variants can be switched off", set(DR.analyse(items, records, ("A", "B"), include_variants=False)["rules"]) == {"SAME-LINE", "OUTCOME-MARKER"})
check("id filter", DR.analyse(items, records, ("A", "B"), id_filter=lambda i: i <= "i03")["n_items"] == 3)
extra = DR.analyse(items, records, ("A", "B"), extra_rules=(("DEMO", lambda c: (False, "demo")),))
check("extra rule reported as own", extra["rules"]["DEMO"]["kind"] == "own" and extra["rules"]["DEMO"]["removed"]["total"] == 8)
grp = DR.analyse(items, records, ("A", "B"), groups={"i02": "g1", "i03": "g1"})
check("groups reported", grp["rules"]["SAME-LINE"]["removed"]["by_group"] == {"-": 2, "g1": 1})

# ---- no answer key reaches a rule: the decisions do not change when the key-like fields are deleted -------------------------------
stripped = copy.deepcopy(items)
for it in stripped.values():
    for k in ("claim", "deciding_line", "why", "trap"):
        it.pop(k, None)
res2 = DR.analyse(stripped, records, ("A", "B"))
same = all([(x[0], x[3]) for x in res["rules"][n]["removed"]["items"]] ==
           [(x[0], x[3]) for x in res2["rules"][n]["removed"]["items"]] for n in res["rules"])
check("rules ignore claim, deciding_line, why and trap", same)
check("rules do not read truth either (only the scoring does)", True)  # structural: Ctx has no truth field
check("Ctx fields", set(DR.Ctx.__dataclass_fields__) == {"ev_a", "ev_b", "turns"})

# ---- helpers ------------------------------------------------------------------------------------------------------------------------
check("wilson bounds", DR.wilson(0, 0) is None and 0 < DR.wilson(1, 10)[0] < 0.1 < DR.wilson(1, 10)[1] < 0.5)
check("frac fields", DR.frac(3, 10)["rate"] == 0.3 and DR.frac(0, 0)["rate"] is None)
check("norm_label", DR.norm_label("not_shown") == "not shown" and DR.norm_label("Shown") == "shown")
check("load_item unwraps", DR.load_item({"item": {"id": "x", "turns": [], "truth": "shown"}})["id"] == "x")
try:
    DR.load_item({"id": "x"})
    check("load_item stops on missing field", False)
except SystemExit:
    check("load_item stops on missing field", True)

with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    (d / "a.py").write_text("print(1)\n", encoding="utf-8")
    (d / "b.md").write_text("design\n", encoding="utf-8")
    (d / "SEAL.txt").write_text(f"{DR.sha256_file(d / 'a.py')} *a.py\n{DR.sha256_file(d / 'b.md')} *b.md\n", encoding="utf-8")
    check("seal ok", DR.check_seal(d, "SEAL.txt", ["a.py", "b.md"])["files_match"] == {"a.py": True, "b.md": True})
    (d / "b.md").write_text("changed\n", encoding="utf-8")
    try:
        DR.check_seal(d, "SEAL.txt", ["a.py", "b.md"])
        check("seal detects change", False)
    except SystemExit:
        check("seal detects change", True)
    try:
        DR.check_seal(d, "SEAL.txt", ["a.py", "c.py"])
        check("seal detects missing required", False)
    except SystemExit:
        check("seal detects missing required", True)
    try:
        DR.check_seal(d, "NOPE.txt", [])
        check("seal detects missing seal file", False)
    except SystemExit:
        check("seal detects missing seal file", True)
    p1 = DR.write_new_json(d / "out", {"a": 1})
    p2 = DR.write_new_json(d / "out", {"a": 2})
    check("write_new_json never overwrites", p1.name == "out-v1.json" and p2.name == "out-v2.json" and json.loads(p1.read_text())["a"] == 1)

print(f"{CHECKS - len(FAILS)} of {CHECKS} checks passed")
sys.exit(0 if not FAILS else 1)
