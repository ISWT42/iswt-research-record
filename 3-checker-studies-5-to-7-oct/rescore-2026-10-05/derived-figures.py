"""Figures derived AFTER sealing from the sealed counts in results-q3-v1.json and results-q4-v1.json (same Wilson / Newcombe helpers).
Not part of the sealed design; nothing here reads the raw answers. Prints counts, rates and intervals only."""
import json
import sys
import rescore_common as C

sys.stdout.reconfigure(encoding="utf-8")
Q3 = json.load(open(C.HERE / "results-q3-v1.json", encoding="utf-8"))
Q4 = json.load(open(C.HERE / "results-q4-v1.json", encoding="utf-8"))


def show(d):
    ci = d["ci95"]
    return f'{d["k"]}/{d["n"]} ({d["rate"]*100:.1f}%; {max(ci[0], 0)*100:.0f}-{ci[1]*100:.0f}%)' if d["n"] else "0/0"


print("D1/D4  Q3: flagged (unsure + unmarked) against sure; contradicted answers flagged against sure")
for sname, arms in Q3["sets"].items():
    for arm, a in arms.items():
        acc, cells = a["accuracy_by_certainty"], a["cells"]
        fk = acc["unsure"]["k"] + acc["unmarked"]["k"]
        fn = acc["unsure"]["n"] + acc["unmarked"]["n"]
        flagged, sure = C.frac(fk, fn), acc["sure"]
        ck = cells["contradicted|unsure"]["right"]["k"] + cells["contradicted|unmarked"]["right"]["k"]
        cn = cells["contradicted|unsure"]["n"] + cells["contradicted|unmarked"]["n"]
        cs = cells["contradicted|sure"]["right"]
        print(f"  {sname} {arm}: right when flagged {show(flagged)} | right when sure {show(sure)} | diff sure-flagged {C.diff_of(sure, flagged)}")
        print(f"      contradicted answers: right when flagged {show(C.frac(ck, cn))} | right when sure {show(cs)}")
print("\nD3  Q3: what dropping every 'shown' answer would cost (every 'shown' answer was marked sure)")
for sname, arms in Q3["sets"].items():
    for arm, a in arms.items():
        cell = a["cells"]["shown|sure"]
        right, n = cell["right"]["k"], cell["n"]
        print(f"  {sname} {arm}: shown answers {n}; wrong {n - right}; correct {right}; give up {right} correct to remove {n - right} wrong ({right / (n - right):.2f} per wrong)")
print("\nD2  Q4: wrong final answers that carry a real (verbatim) quote: how many are NOT on the deciding line")
for sname, lanes in Q4["sets"].items():
    for lane, d in lanes.items():
        for fa in ("shown", "contradicted"):
            w = d["pooled"]["all"]["wrong_with_real_quote"][fa]
            tot, on = w["wrong"]["k"], w["wrong_by_group"].get("ON", 0)
            print(f"  {sname} {lane} final '{fa}': wrong {tot} of {w['final_answers']}; of the wrong, not on the deciding line {show(C.frac(tot - on, tot))}; by group {w['wrong_by_group']}")
