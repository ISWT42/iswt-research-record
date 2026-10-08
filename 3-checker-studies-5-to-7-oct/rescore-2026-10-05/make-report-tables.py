"""Turns the sealed results JSON into markdown tables for REPORT.md (post-seal helper; reads only the two sealed results files).
Prints counts, rates and intervals only."""
import json
import sys

import rescore_common as C

sys.stdout.reconfigure(encoding="utf-8")
Q3 = json.load(open(C.HERE / "results-q3-v1.json", encoding="utf-8"))
Q4 = json.load(open(C.HERE / "results-q4-v1.json", encoding="utf-8"))
SET_LABEL = {"fresh_161_300": "161-300", "primary_201_300": "201-300"}
MODEL = {"U-Q": "qwen3.5-9b", "U-G": "gemma-4-26b", "A": "Qwen3-4B (A)", "B": "Gemma-4-E4B (B)",
         "F-Q": "qwen3.5-9b (F-Q)", "F-G": "gemma-4-26b (F-G)"}


def ci(d):
    lo, hi = max(d["ci95"][0], 0.0) + 0.0, d["ci95"][1]
    return f"{lo * 100:.0f}-{hi * 100:.0f}"


def full(d):
    return f'{d["k"]}/{d["n"]} ({d["rate"] * 100:.0f}%; {ci(d)})' if d["n"] else "0/0"


def kn(d):
    return f'{d["k"]}/{d["n"]}'


def kp(d):
    return f'{d["k"]}/{d["n"]} ({d["rate"] * 100:.0f}%)' if d["n"] else "0/0"


def pts(x):
    return f'{x["diff"] * 100:+.0f} ({x["ci95"][0] * 100:+.0f} to {x["ci95"][1] * 100:+.0f})' if x else "n/a"


print("### T1 Q3 certainty and accuracy")
print("| Model | Items | Marked sure | Marked unsure | Unmarked | Right when sure | Right when unsure | Right when unmarked |")
print("|---|---|---|---|---|---|---|---|")
for arm in ("U-Q", "U-G"):
    for s in Q3["sets"]:
        a = Q3["sets"][s][arm]
        cc, ac = a["certainty_counts"], a["accuracy_by_certainty"]
        print(f"| {MODEL[arm]} | {SET_LABEL[s]} | {kn(cc['sure'])} | {kn(cc['unsure'])} | {kn(cc['unmarked'])} | {full(ac['sure'])} | {full(ac['unsure'])} | {full(ac['unmarked'])} |")
print("\n### T1b sure minus unsure")
for arm in ("U-Q", "U-G"):
    for s in Q3["sets"]:
        print(f"{MODEL[arm]} {SET_LABEL[s]}: {pts(Q3['sets'][s][arm]['sure_minus_unsure'])}")
print("\n### T1c unmarked causes")
for arm in ("U-Q", "U-G"):
    for s in Q3["sets"]:
        u = Q3["sets"][s][arm]["unmarked_reasons"]
        print(f"{MODEL[arm]} {SET_LABEL[s]}: " + ", ".join(f"{k} {kn(v)}" for k, v in u.items()))

print("\n### T2 Q3 the rule R_all")
print("| Model | Items | Wrong 'shown' before (of 'shown' answers) | Wrong 'shown' after the rule (of 'shown' answers left) | Wrong 'shown' removed | Correct answers given up (of correct) | Wrong made right (of wrong) | Right before | Right after |")
print("|---|---|---|---|---|---|---|---|---|")
for arm in ("U-Q", "U-G"):
    for s in Q3["sets"]:
        r = Q3["sets"][s][arm]["rule_R_all"]
        print(f"| {MODEL[arm]} | {SET_LABEL[s]} | {full(r['wrong_shown_of_shown_answers']['before'])} | {full(r['wrong_shown_of_shown_answers']['after'])} | {full(r['wrong_shown_removed'])} | {full(r['correct_given_up'])} | {full(r['wrong_made_right'])} | {full(r['right']['before'])} | {full(r['right']['after'])} |")
print("\n### T2b false-shown rate (of items whose truth is contradicted or not shown), before and after; given up by type; R_shown")
for arm in ("U-Q", "U-G"):
    for s in Q3["sets"]:
        a = Q3["sets"][s][arm]
        r = a["rule_R_all"]
        g = r["correct_given_up_by_type"]
        rs = a["rule_R_shown"]
        print(f"{MODEL[arm]} {SET_LABEL[s]}: false-shown {full(r['false_shown_rate']['before'])} -> {full(r['false_shown_rate']['after'])}; given up: true-shown {kn(g['true_shown_given_up_of_right_shown'])}, true-contradicted {kn(g['true_contradicted_given_up_of_right_contradicted'])}; false-contradicted {full(r['false_contradicted']['before'])} -> {full(r['false_contradicted']['after'])}; R_shown: removed {kn(rs['wrong_shown_removed'])}, given up {kn(rs['correct_given_up'])}, right {kn(rs['right']['before'])} -> {kn(rs['right']['after'])}; split of removed {r['wrong_shown_removed_split']}")


def cell_table(s):
    print("| Answer type, certainty | qwen3.5-9b: n | right | 'not shown' right | net | gemma-4-26b: n | right | 'not shown' right | net |")
    print("|---|---|---|---|---|---|---|---|---|")
    for key in Q3["sets"][s]["U-Q"]["cells"]:
        row = []
        for arm in ("U-Q", "U-G"):
            c = Q3["sets"][s][arm]["cells"][key]
            row += [str(c["n"]), kn(c["right"]), kn(c["truth_not_shown"]), f'{c["net_if_replaced"]:+d}' if c["net_if_replaced"] else "0"]
        print(f"| {key.replace('|', ', ')} | " + " | ".join(row) + " |")


def cell_table_combined():
    print("| Answer, certainty | qwen3.5-9b: answers | right | 'not shown' would be right | gemma-4-26b: answers | right | 'not shown' would be right |")
    print("|---|---|---|---|---|---|---|")
    for key in Q3["sets"]["fresh_161_300"]["U-Q"]["cells"]:
        row = []
        for arm in ("U-Q", "U-G"):
            f_, p_ = (Q3["sets"][s][arm]["cells"][key] for s in ("fresh_161_300", "primary_201_300"))
            row += [f'{f_["n"]} / {p_["n"]}', f'{kn(f_["right"])} / {kn(p_["right"])}', f'{kn(f_["truth_not_shown"])} / {kn(p_["truth_not_shown"])}']
        print(f"| {key.replace('|', ', ')} | " + " | ".join(row) + " |")


print("\n### T3 Q3 cells (items 161-300 / items 201-300)")
cell_table_combined()
print("\n### T3-old cells, items 161-300 (n; right; what 'not shown' would get right; net if replaced)")
cell_table("fresh_161_300")
print("\n### T3b same cells, items 201-300")
cell_table("primary_201_300")
print("\n### T3c catch and give-up")
for arm in ("U-Q", "U-G"):
    for s in Q3["sets"]:
        c = Q3["sets"][s][arm]["catch_and_giveup"]
        print(f"{MODEL[arm]} {SET_LABEL[s]}: flagged {full(c['flagged_share_of_all'])}; wrong flagged {full(c['wrong_flagged_of_wrong'])}; right flagged {full(c['right_flagged_of_right'])}; catch minus give-up {pts(c['catch_minus_giveup_all'])}; wrong shown flagged {full(c['wrong_shown_flagged_of_wrong_shown'])}; right shown flagged {full(c['right_shown_flagged_of_right_shown'])}")

LANE_SCOPES = [("local", "pooled", "Local, both models"), ("local", "A", MODEL["A"]), ("local", "B", MODEL["B"]),
               ("fast", "pooled", "Hosted, both models"), ("fast", "F-Q", MODEL["F-Q"]), ("fast", "F-G", MODEL["F-G"])]


def scope(s, lane, sc):
    d = Q4["sets"][s][lane]
    return d["pooled"] if sc == "pooled" else d["arms"][sc]


print("\n### T4 Q4 where the real quotes land")
print("| Lane / model | Items | Answers | Quote passes the check | On the deciding line | Another real line | No deciding line exists | Not on a deciding line (another + none) |")
print("|---|---|---|---|---|---|---|---|")
for lane, sc, label in LANE_SCOPES:
    for s in Q4["sets"]:
        a = scope(s, lane, sc)["all"]
        sh, cl = a["shares"], a["classes"]
        print(f"| {label} | {SET_LABEL[s]} | {a['n_answers']} | {a['n_pop']} | {full(sh['on_of_pop'])} | {kp(C.frac(cl.get('OTHER', 0), a['n_pop']))} | {full(sh['no_d_of_pop'])} | {full(sh['not_on_of_pop'])} |")
print("\n### T4b class split and the other-line share on items that have a deciding line")
for lane, sc, label in LANE_SCOPES:
    for s in Q4["sets"]:
        a = scope(s, lane, sc)["all"]
        cl = a["classes"]
        print(f"{label} {SET_LABEL[s]}: FULL {cl.get('FULL', 0)}, PART {cl.get('PART', 0)}, PLUS {cl.get('PLUS', 0)}, OTHER {cl.get('OTHER', 0)}, NO_D {cl.get('NO_D', 0)}, UNRESOLVED {cl.get('UNRESOLVED', 0)}; other-line share on items with a deciding line {full(a['shares']['other_of_pop_on_items_with_deciding_line'])}; codes {a['codes']}; ambiguous_part {a['ambiguous_part']}; wrong_turn_text_match {a['wrong_turn_text_match']}")

print("\n### T5 Q4 does the answer match the truth")
print("| Lane / model | Items | Right when on the deciding line | Right when another real line | Difference, on minus other (points; Newcombe 95%) | Right when no deciding line exists | Model's own verdict right: on / other |")
print("|---|---|---|---|---|---|---|")
for lane, sc, label in LANE_SCOPES:
    for s in Q4["sets"]:
        a = scope(s, lane, sc)["all"]
        am, vm = a["answer_match"], a["model_verdict_match"]
        print(f"| {label} | {SET_LABEL[s]} | {full(am['ON'])} | {full(am['OTHER'])} | {pts(a['contrast_on_minus_other']['answer_match'])} | {kp(am['NO_D'])} | {kp(vm['ON'])} / {kp(vm['OTHER'])} |")
print("\n### T5b strict reading (FULL only) and verified-code-only population, pooled lanes")
for lane in ("local", "fast"):
    for s in Q4["sets"]:
        a = Q4["sets"][s][lane]["pooled"]["all"]
        v = Q4["sets"][s][lane]["pooled"]["all_verified_code_only"]
        print(f"{lane} {SET_LABEL[s]}: FULL only right {full(a['answer_match']['FULL'])}, FULL is {a['classes'].get('FULL', 0)} of {a['n_pop']} quotes; PART {kp(a['answer_match']['PART'])}; PLUS {kp(a['answer_match']['PLUS'])}; verified-code-only (n {v['n_pop']}): on {full(v['answer_match']['ON'])}, other {full(v['answer_match']['OTHER'])}")

print("\n### T6 Q4 wrong answers that carry a real quote")
print("| Lane | Items | Final answer | Wrong (of final answers of that kind) | Quote on the deciding line | Quote on another line | No deciding line exists |")
print("|---|---|---|---|---|---|---|")
for lane, label in (("local", "Local"), ("fast", "Hosted")):
    for s in Q4["sets"]:
        for fa in ("shown", "contradicted"):
            w = Q4["sets"][s][lane]["pooled"]["all"]["wrong_with_real_quote"][fa]
            g = w["wrong_by_group"]
            print(f"| {label} | {SET_LABEL[s]} | {fa} | {kp(w['wrong'])} | {g.get('ON', 0)} | {g.get('OTHER', 0)} | {g.get('NO_D', 0)} |")


def trap_table(s):
    print(f"\n### T7 by trap, items {SET_LABEL[s]} (both models of a lane pooled; quotes that pass the check)")
    print("| Trap | Local: quotes (on / other / none) | Local: right on the line | Local: right on another line | Hosted: quotes (on / other / none) | Hosted: right on the line | Hosted: right on another line |")
    print("|---|---|---|---|---|---|---|")
    for tr in Q4["traps"]:
        cells = []
        for lane in ("local", "fast"):
            a = Q4["sets"][s][lane]["pooled"]["by_trap"][tr]
            cl = a["classes"]
            on = cl.get("FULL", 0) + cl.get("PART", 0) + cl.get("PLUS", 0)
            am = a["answer_match"]
            cells += [f"{a['n_pop']} ({on} / {cl.get('OTHER', 0)} / {cl.get('NO_D', 0)})", kn(am["ON"]), kn(am["OTHER"]) if am["OTHER"]["n"] else "-"]
        print(f"| {tr} | " + " | ".join(cells) + " |")


trap_table("fresh_161_300")
trap_table("primary_201_300")
print("\n### T7b wrong 'shown' with a real quote, by trap (final 'shown' answers; wrong; groups)")
for s in Q4["sets"]:
    for lane in ("local", "fast"):
        parts = []
        for tr in Q4["traps"]:
            w = Q4["sets"][s][lane]["pooled"]["by_trap"][tr]["wrong_with_real_quote"]["shown"]
            if w["wrong"]["k"]:
                parts.append(f"{tr} {w['wrong']['k']}/{w['final_answers']} {w['wrong_by_group']}")
        print(f"{SET_LABEL[s]} {lane}: " + "; ".join(parts))
