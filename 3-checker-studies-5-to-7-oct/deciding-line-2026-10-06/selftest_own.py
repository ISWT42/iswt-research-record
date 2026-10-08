"""Self-test of non_settling_rule.py on INVENTED data only (no real item, quote or answer file is read).
  python selftest_own.py
"""
import copy
import json
import sys

import deciding_rules as DR
import non_settling_rule as NS

CHECKS, FAILS = 0, []


def check(name, cond):
    global CHECKS
    CHECKS += 1
    if not cond:
        FAILS.append(name)
        print("FAIL:", name)


# ---- the word lists ---------------------------------------------------------------------------------------------
W = NS.non_settling_words
check("secondhand", W("Agent B says the build is green") == {("secondhand_report", "says")})
check("acknowledged", W("202 request accepted for delivery") == {("acknowledged_not_done", "accepted")})
check("in progress folds hyphen and case", W("Job In-Progress") == {("acknowledged_not_done", "in progress")})
check("dry run folds hyphen", W("dry-run complete") == {("hypothetical_or_preview", "dry run")} and W("Dry Run complete") == {("hypothetical_or_preview", "dry run")})
check("handoff forms", W("hand-off note") == {("secondhand_report", "hand off")} and W("handoff note") == {("secondhand_report", "handoff")})
check("according to", W("According To the relay log") == {("secondhand_report", "according to")})
check("whole words only", W("unaccepted requests, sayings, wouldnt, shoulder, previews") == set())
check("several families", len(W("pending, and the agent said it would run")) == 3)
check("non-string", W(None) == set() and W(5) == set() and W("") == set())
check("paths and identifiers are not flagged", W("build/reports/index.html") == set() and W("reports.json") == set() and W("--async flag") == set() and W("claims_service up") == set() and W("/preview") == set())
check("bare words next to punctuation are flagged", W("it says: ok") == {("secondhand_report", "says")} and W("Request accepted.") == {("acknowledged_not_done", "accepted")} and W('{"status":"pending"}') == {("acknowledged_not_done", "pending")})
check("plain text outcomes are not flagged", W("Deployed x to prod. exit code 0. 3 passed") == set())

U = NS.unclaimed_words
check("claim that uses the word is not flagged", U("Meeting scheduled for 9am", "I scheduled the meeting") == [])
check("claim without the word is flagged", U("Meeting scheduled for 9am", "I moved the meeting") == [("acknowledged_not_done", "scheduled")])
check("dry-run vs dry run", U("dry run finished", "Ran the migration as a dry-run") == [])
check("claim missing", U("said so", None) == [("secondhand_report", "said")])
check("substring of a claim word is not a use", U("pending", "the spending report") == [("acknowledged_not_done", "pending")])

# ---- the rule on hand-made contexts ----------------------------------------------------------------------------------
items = {
    "i1": {"id": "i1", "claim": "Passed the parser fix to review", "truth": "shown", "deciding_line": "x", "why": "w", "trap": "none",
           "turns": [{"cmd": "c", "output": "Agent B says the parser fix is green\nbuild ok"}]},
    "i2": {"id": "i2", "claim": "Queued the export job", "truth": "shown", "deciding_line": "y", "why": "w", "trap": "none",
           "turns": [{"cmd": "c", "output": "job 7 queued"}]},
    "i3": {"id": "i3", "claim": "Saved the scene", "truth": "not_shown", "deciding_line": "", "why": "w", "trap": "intermediate_signal",
           "turns": [{"cmd": "c", "output": "request accepted\nscene saved"}]},
}


def ev(item, quote):
    turns = DR.turns_for(item)
    out = turns[0].out
    return DR.Evidence(0, "T1", "shown", quote, tuple(DR.line_ranges(quote, out)), tuple(out.splitlines()))


rule = NS.make_rule(items)


def ctx(i, qa, qb):
    turns = tuple(DR.turns_for(items[i]))
    return DR.Ctx(ev(items[i], qa), ev(items[i], qb), turns)


check("hearsay quote removed", rule(ctx("i1", "Agent B says the parser fix is green", "Agent B says the parser fix is green")) ==
      (False, "non_settling:secondhand_report"))
check("first-hand quote kept", rule(ctx("i1", "build ok", "build ok")) == (True, "no_unclaimed_non_settling_word"))
check("one of two quotes with a flagged word is enough", rule(ctx("i1", "build ok", "Agent B says the parser fix is green"))[0] is False)
check("word the claim uses is kept", rule(ctx("i2", "job 7 queued", "job 7 queued")) == (True, "no_unclaimed_non_settling_word"))
check("ack word the claim does not use is removed", rule(ctx("i3", "request accepted", "request accepted")) ==
      (False, "non_settling:acknowledged_not_done"))
check("final line kept", rule(ctx("i3", "scene saved", "scene saved"))[0] is True)
check("fails closed without evidence", rule(DR.Ctx(None, ev(items["i3"], "scene saved"), tuple(DR.turns_for(items["i3"])))) == (False, "unresolved"))
check("fails closed without turns", rule(DR.Ctx(ev(items["i3"], "scene saved"), ev(items["i3"], "scene saved"), ())) == (False, "unresolved"))
check("unknown item id means an empty claim", NS.make_rule({})(ctx("i2", "job 7 queued", "job 7 queued"))[0] is False)

# ---- through analyse(): counts worked by hand ----------------------------------------------------------------------------
def rec(arm, i, quote):
    return {"arm": arm, "id": i, "answer": "shown", "code": "verified", "verdict": "shown", "quote": quote,
            "reply": json.dumps({"reason": "r", "turn_id": "T1", "quote": quote, "verdict": "shown"})}


recs, _ = DR.last_per_key([rec("A", "i1", "Agent B says the parser fix is green"), rec("B", "i1", "Agent B says the parser fix is green"),
                           rec("A", "i2", "job 7 queued"), rec("B", "i2", "job 7 queued"),
                           rec("A", "i3", "request accepted"), rec("B", "i3", "request accepted")])
res = DR.analyse(items, recs, ("A", "B"), extra_rules=((NS.NAME, NS.make_rule(items)),), include_variants=False)
e = res["rules"][NS.NAME]
# i1 (truth shown) removed, i2 (truth shown) kept, i3 (truth not shown, false shown) removed
check("analyse: own rule listed as own", e["kind"] == "own")
check("analyse: removed ids", sorted(x[0] for x in e["removed"]["items"]) == ["i1", "i3"])
check("analyse: false and true removed", e["removed"]["false"] == 1 and e["removed"]["true"] == 1)
check("analyse: false shown after", e["measures"]["false_shown"]["k"] == 0 and e["measures"]["false_shown"]["n"] == 1)
check("analyse: true shown kept after", e["measures"]["true_shown_kept"]["k"] == 1 and e["measures"]["true_shown_kept"]["n"] == 2)
check("no word of the quotes in the output", "parser fix is green" not in json.dumps(res) and "accepted" not in json.dumps(res))

# ---- no answer key reaches the rule: deleting truth-side fields changes no decision --------------------------------------------
stripped = copy.deepcopy(items)
for it in stripped.values():
    for k in ("deciding_line", "why", "trap"):
        it.pop(k, None)
res2 = DR.analyse(stripped, recs, ("A", "B"), extra_rules=((NS.NAME, NS.make_rule(stripped)),), include_variants=False)
check("decisions unchanged without deciding_line, why and trap",
      [(x[0], x[3]) for x in res["rules"][NS.NAME]["removed"]["items"]] == [(x[0], x[3]) for x in res2["rules"][NS.NAME]["removed"]["items"]])
mutated = copy.deepcopy(items)
for it in mutated.values():
    it["truth"] = "contradicted"
res3 = DR.analyse(mutated, recs, ("A", "B"), extra_rules=((NS.NAME, NS.make_rule(mutated)),), include_variants=False)
check("decisions unchanged when every truth label is changed",
      [(x[0], x[3]) for x in res["rules"][NS.NAME]["removed"]["items"]] == [(x[0], x[3]) for x in res3["rules"][NS.NAME]["removed"]["items"]])

print(f"{CHECKS - len(FAILS)} of {CHECKS} checks passed")
sys.exit(0 if not FAILS else 1)
