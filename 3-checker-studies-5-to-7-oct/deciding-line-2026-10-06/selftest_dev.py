"""Self-test of dev_eval.choose_primary and dev_eval.own_rule_gate on INVENTED counts only (no real file is read).
  python selftest_dev.py
"""
import sys

import deciding_rules as DR
import dev_eval as DE

CHECKS, FAILS = 0, []


def check(name, cond):
    global CHECKS
    CHECKS += 1
    if not cond:
        FAILS.append(name)
        print("FAIL:", name)


def res(F, T, removed):
    """A minimal analysis result: removed = {rule: (false_removed, true_removed)}."""
    rules = {}
    for name, (f, t) in removed.items():
        rules[name] = {"bar": DR.bar_verdict(F, f, T, t), "removed": {"false": f, "true": t}}
    return {"rules": rules}


# step 2: eligible candidates; most false removed wins
loc = res(6, 30, {"SAME-LINE": (3, 1), "OUTCOME-MARKER": (2, 0)})
hos = res(7, 30, {"SAME-LINE": (0, 0), "OUTCOME-MARKER": (5, 0)})
best, step, table = DE.choose_primary(loc, hos, ["SAME-LINE", "OUTCOME-MARKER"])
check("step 2: most false removed", best == "SAME-LINE" and step.startswith("step 2") and table["SAME-LINE"]["eligible"])
# a candidate that loses too many true 'shown' is not eligible even if it removes more false
loc = res(6, 30, {"SAME-LINE": (1, 0), "OUTCOME-MARKER": (5, 7)})
best, step, table = DE.choose_primary(loc, hos, ["SAME-LINE", "OUTCOME-MARKER"])
check("ineligible candidate loses (7 of 30 true removed is below 80% kept)", best == "SAME-LINE" and not table["OUTCOME-MARKER"]["eligible"])
check("exactly 80% kept is eligible", DE.choose_primary(res(6, 30, {"SAME-LINE": (1, 0), "OUTCOME-MARKER": (4, 6)}), hos, ["SAME-LINE", "OUTCOME-MARKER"])[0] == "OUTCOME-MARKER")
# ties: fewer true removed, then more removed on the hosted pair, then the simpler rule
loc = res(6, 30, {"SAME-LINE": (2, 2), "OUTCOME-MARKER": (2, 1)})
check("tie on f: fewer true removed", DE.choose_primary(loc, hos, ["SAME-LINE", "OUTCOME-MARKER"])[0] == "OUTCOME-MARKER")
loc = res(6, 30, {"SAME-LINE": (2, 1), "OUTCOME-MARKER": (2, 1)})
hos2 = res(7, 30, {"SAME-LINE": (1, 0), "OUTCOME-MARKER": (3, 0)})
check("tie on f and t: more removed on hosted", DE.choose_primary(loc, hos2, ["SAME-LINE", "OUTCOME-MARKER"])[0] == "OUTCOME-MARKER")
hos3 = res(7, 30, {"SAME-LINE": (2, 0), "OUTCOME-MARKER": (2, 0)})
check("tie everywhere: the simpler rule (SAME-LINE)", DE.choose_primary(loc, hos3, ["SAME-LINE", "OUTCOME-MARKER"])[0] == "SAME-LINE")
# step 3: no eligible candidate removes a false 'shown'
loc = res(6, 33, {"SAME-LINE": (0, 1), "OUTCOME-MARKER": (3, 28)})
best, step, table = DE.choose_primary(loc, hos, ["SAME-LINE", "OUTCOME-MARKER"])
check("step 3: largest separation", best == "SAME-LINE" and step.startswith("step 3") and table["OUTCOME-MARKER"]["separation_local"] < table["SAME-LINE"]["separation_local"])
loc = res(6, 33, {"SAME-LINE": (0, 0), "OUTCOME-MARKER": (0, 0)})
check("step 3 tie goes to SAME-LINE", DE.choose_primary(loc, hos, ["SAME-LINE", "OUTCOME-MARKER"])[0] == "SAME-LINE")
# an own rule ranks last on ties
loc = res(6, 30, {"SAME-LINE": (2, 1), "OUTCOME-MARKER": (0, 9), "OWN": (2, 1)})
check("own rule loses a complete tie", DE.choose_primary(loc, hos3 | {"rules": {**hos3["rules"], "OWN": {"bar": hos3["rules"]["SAME-LINE"]["bar"], "removed": {"false": 2, "true": 0}}}},
                                                       ["SAME-LINE", "OUTCOME-MARKER", "OWN"])[0] == "SAME-LINE")
loc = res(6, 30, {"SAME-LINE": (1, 1), "OUTCOME-MARKER": (0, 9), "OWN": (4, 1)})
hos4 = res(7, 30, {"SAME-LINE": (1, 0), "OUTCOME-MARKER": (0, 9), "OWN": (3, 0)})
check("own rule wins when it removes most false 'shown' and is eligible", DE.choose_primary(loc, hos4, ["SAME-LINE", "OUTCOME-MARKER", "OWN"])[0] == "OWN")

# own-rule gate: local conditions and hosted validation
loc = res(6, 30, {"OWN": (3, 6)})
hos = res(7, 30, {"OWN": (1, 0)})
g = DE.own_rule_gate(loc, hos, "OWN")
check("gate admits: half removed, 80% kept, hosted ok", g["admitted"] and g["local_conditions_met"] and g["hosted_validation_met"])
check("gate: 2 of 6 is not half", not DE.own_rule_gate(res(6, 30, {"OWN": (2, 0)}), hos, "OWN")["local_conditions_met"])
check("gate: 7 of 30 true removed fails retention", not DE.own_rule_gate(res(6, 30, {"OWN": (4, 7)}), hos, "OWN")["local_conditions_met"])
check("gate: hosted removes no false 'shown'", not DE.own_rule_gate(loc, res(7, 30, {"OWN": (0, 0)}), "OWN")["hosted_validation_met"])
check("gate: hosted separation below zero", not DE.own_rule_gate(loc, res(7, 30, {"OWN": (1, 5)}), "OWN")["hosted_validation_met"])
check("gate: hosted separation exactly zero passes", DE.own_rule_gate(loc, res(7, 28, {"OWN": (1, 4)}), "OWN")["hosted_validation_met"])
check("gate: not admitted if local fails", not DE.own_rule_gate(res(6, 30, {"OWN": (2, 0)}), hos, "OWN")["admitted"])

print(f"{CHECKS - len(FAILS)} of {CHECKS} checks passed")
sys.exit(0 if not FAILS else 1)
