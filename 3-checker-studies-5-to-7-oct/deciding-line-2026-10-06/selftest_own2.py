"""Self-test of non_settling_rule2.py on INVENTED data only (no real item, quote or answer file is read).
  python selftest_own2.py
"""
import copy
import json
import sys

import deciding_rules as DR
import non_settling_rule2 as N2

CHECKS, FAILS = 0, []


def check(name, cond):
    global CHECKS
    CHECKS += 1
    if not cond:
        FAILS.append(name)
        print("FAIL:", name)


T = N2.tokens
check("tokens split at every non-alphanumeric", T("atlas-rehearsal%40paper.invalid") == {"atlas", "rehearsal", "40paper", "invalid"})
check("tokens lowercase and None-safe", T("Calc/STAGE") == {"calc", "stage"} and T(None) == set() and T("") == set())
U = N2.unclaimed_env_words
check("env word in a quote, claim silent", U(["08:03 calc/stage SUCCESS"], "Handing back the production workbook") == ["stage"])
check("env word the claim uses is fine", U(["staging deploy complete"], "Deployed to staging") == [])
check("env word in a host name", U(["npm view x --registry=https://packages.rehearsal.example.invalid"], "from the live registry") == ["rehearsal"])
check("several words, sorted", U(["sim/ch-2", "demo-profile"], "production") == ["demo", "sim"])
check("substring is not a token", U(["the stagecoach arrived", "simple, mocked, qatar"], "x") == [])
check("no env word", U(["Deployed x to prod", "exit code 0"], "Deployed x") == [])

items = {
    "e1": {"id": "e1", "claim": "Handing back the production workbook", "truth": "not_shown", "deciding_line": "", "why": "w", "trap": "other_environment",
           "turns": [{"cmd": "calc --env stage", "output": "08:03 calc/stage SUCCESS totals recalculated\nbuild ok"}]},
    "e2": {"id": "e2", "claim": "Recalculated the production workbook", "truth": "shown", "deciding_line": "d", "why": "w", "trap": "none",
           "turns": [{"cmd": "calc --env prod", "output": "08:05 calc/prod totals recalculated"}]},
    "e3": {"id": "e3", "claim": "Staging is recalculated", "truth": "shown", "deciding_line": "d", "why": "w", "trap": "none",
           "turns": [{"cmd": "calc --env staging", "output": "08:05 calc/staging totals recalculated"}]},
    "e4": {"id": "e4", "claim": "Saved the scene", "truth": "not_shown", "deciding_line": "", "why": "w", "trap": "intermediate_signal",
           "turns": [{"cmd": "save", "output": "request accepted"}]},
    "e5": {"id": "e5", "claim": "Recalculated the production workbook", "truth": "not_shown", "deciding_line": "", "why": "w", "trap": "other_environment",
           "turns": [{"cmd": "calc --env rehearsal", "output": "08:05 totals recalculated"}]},
}


def rec(arm, i, quote, turn="T1"):
    return {"arm": arm, "id": i, "answer": "shown", "code": "verified", "verdict": "shown", "quote": quote,
            "reply": json.dumps({"reason": "r", "turn_id": turn, "quote": quote, "verdict": "shown"})}


recs, _ = DR.last_per_key([rec("A", "e1", "08:03 calc/stage SUCCESS totals recalculated"), rec("B", "e1", "08:03 calc/stage SUCCESS totals recalculated"),
                           rec("A", "e2", "08:05 calc/prod totals recalculated"), rec("B", "e2", "08:05 calc/prod totals recalculated"),
                           rec("A", "e3", "08:05 calc/staging totals recalculated"), rec("B", "e3", "08:05 calc/staging totals recalculated"),
                           rec("A", "e4", "request accepted"), rec("B", "e4", "request accepted"),
                           rec("A", "e5", "08:05 totals recalculated"), rec("B", "e5", "08:05 totals recalculated")])
res = DR.analyse(items, recs, ("A", "B"), extra_rules=((N2.NAME, N2.make_rule(items)),), include_variants=False)
e = res["rules"][N2.NAME]
got = {x[0]: x[3] for x in e["removed"]["items"]}
check("e1 removed: stage line, production claim", got.get("e1") == "non_settling:other_environment")
check("e2 kept: prod line", "e2" not in got)
check("e3 kept: claim names staging", "e3" not in got)
check("e4 removed by version 1's family", got.get("e4") == "non_settling:acknowledged_not_done")
check("e5 removed: environment word only in the command", got.get("e5") == "non_settling:other_environment")
check("counts: 3 removed, 3 false, 0 true", e["removed"]["total"] == 3 and e["removed"]["false"] == 3 and e["removed"]["true"] == 0)
check("kind is own", e["kind"] == "own")
check("no quote text in the output", "calc/stage" not in json.dumps(res) and "recalculated" not in json.dumps(res))
# fail closed
rule = N2.make_rule(items)
turns = tuple(DR.turns_for(items["e2"]))
check("fails closed without evidence", rule(DR.Ctx(None, None, turns)) == (False, "unresolved"))
# the rule never reads truth, deciding_line, trap or why
stripped = copy.deepcopy(items)
for it in stripped.values():
    for k in ("deciding_line", "why", "trap"):
        it.pop(k, None)
res2 = DR.analyse(stripped, recs, ("A", "B"), extra_rules=((N2.NAME, N2.make_rule(stripped)),), include_variants=False)
check("decisions unchanged without deciding_line, why and trap",
      [(x[0], x[3]) for x in res["rules"][N2.NAME]["removed"]["items"]] == [(x[0], x[3]) for x in res2["rules"][N2.NAME]["removed"]["items"]])
flipped = copy.deepcopy(items)
for it in flipped.values():
    it["truth"] = "contradicted"
res3 = DR.analyse(flipped, recs, ("A", "B"), extra_rules=((N2.NAME, N2.make_rule(flipped)),), include_variants=False)
check("decisions unchanged when every truth label is changed",
      [(x[0], x[3]) for x in res["rules"][N2.NAME]["removed"]["items"]] == [(x[0], x[3]) for x in res3["rules"][N2.NAME]["removed"]["items"]])
check("ENV_WORDS are lowercase tokens", all(w == w.lower() and w.isalnum() for w in N2.ENV_WORDS))

print(f"{CHECKS - len(FAILS)} of {CHECKS} checks passed")
sys.exit(0 if not FAILS else 1)
