"""Q3: when does "not shown" beat answering, and is the model's own certainty usable? (run 3 answers)
Design: DESIGN.md (sealed first). Reads existing files only: no model calls, no network.
Prints status lines only (no result figures, so nothing is read before the results are sealed);
the results go to results-q3-vN.json: ids, labels, counts and rates, never item text.
  python q3_certainty.py --run-at "$(date -u +%FT%TZ)"
"""
import argparse
import json
from collections import Counter

import rescore_common as C

SCRIPT = "q3_certainty.py"
ARMS = {"U-Q": "qwen/qwen3.5-9b", "U-G": "google/gemma-4-26b-a4b-it"}
TYPES = ("shown", "contradicted", "not shown")
CATS = ("sure", "unsure", "unmarked")
REASONS = ("no_answer", "reply_not_a_json_object", "certainty_missing_or_invalid")


def category(rec):
    c = rec.get("certainty")
    return c if c in ("sure", "unsure") else "unmarked"


def unmarked_reason(rec):
    if rec.get("no_answer"):
        return "no_answer"
    value, _ = C.parse_reply(rec.get("reply"))
    if value is None:
        return "reply_not_a_json_object"
    return "certainty_missing_or_invalid"


def apply_rule(ans, cat, kind):
    """R_all: every unsure or unmarked answer becomes "not shown". R_shown: only such answers that are "shown"."""
    if kind == "R_all":
        return {i: (ans[i] if cat[i] == "sure" else "not shown") for i in ans}
    if kind == "R_shown":
        return {i: ("not shown" if (cat[i] != "sure" and ans[i] == "shown") else ans[i]) for i in ans}
    raise ValueError(kind)


def rule_effects(ans, ans2, t, ids):
    n = len(ids)
    right = {i: ans[i] == t[i] for i in ids}
    right2 = {i: ans2[i] == t[i] for i in ids}
    shown1 = [i for i in ids if ans[i] == "shown"]
    shown2 = [i for i in ids if ans2[i] == "shown"]
    ws1 = [i for i in shown1 if t[i] != "shown"]
    ws2 = [i for i in shown2 if t[i] != "shown"]
    truth_other_than_shown = [i for i in ids if t[i] != "shown"]
    truth_other_than_contradicted = [i for i in ids if t[i] != "contradicted"]
    removed = [i for i in ws1 if ans2[i] != "shown"]
    right_ids = [i for i in ids if right[i]]
    wrong_ids = [i for i in ids if not right[i]]
    given_up = [i for i in right_ids if not right2[i]]
    given_set = set(given_up)
    made_right = [i for i in wrong_ids if right2[i]]
    right_shown = [i for i in right_ids if ans[i] == "shown"]
    right_contra = [i for i in right_ids if ans[i] == "contradicted"]
    fc1 = [i for i in truth_other_than_contradicted if ans[i] == "contradicted"]
    fc2 = [i for i in truth_other_than_contradicted if ans2[i] == "contradicted"]
    return {
        "wrong_shown_of_shown_answers": {"before": C.frac(len(ws1), len(shown1)), "after": C.frac(len(ws2), len(shown2))},
        "false_shown_rate": {"denominator": "items whose truth is contradicted or not shown",
                             "before": C.frac(len(ws1), len(truth_other_than_shown)),
                             "after": C.frac(len(ws2), len(truth_other_than_shown))},
        "wrong_shown_removed": C.frac(len(removed), len(ws1)),
        "wrong_shown_removed_split": {"of_removed": len(removed),
                                      "now_right_truth_not_shown": sum(right2[i] for i in removed),
                                      "still_wrong_truth_contradicted": sum(not right2[i] for i in removed)},
        "right": {"before": C.frac(len(right_ids), n), "after": C.frac(sum(right2.values()), n)},
        "correct_given_up": C.frac(len(given_up), len(right_ids)),
        "correct_given_up_by_type": {
            "true_shown_given_up_of_right_shown": C.frac(sum(i in given_set for i in right_shown), len(right_shown)),
            "true_contradicted_given_up_of_right_contradicted": C.frac(sum(i in given_set for i in right_contra), len(right_contra))},
        "wrong_made_right": C.frac(len(made_right), len(wrong_ids)),
        "exchange": {"wrong_shown_removed": len(removed), "correct_given_up": len(given_up),
                     "given_up_per_wrong_shown_removed": (round(len(given_up) / len(removed), 3) if removed else None)},
        "false_contradicted": {"denominator": "items whose truth is shown or not shown",
                               "before": C.frac(len(fc1), len(truth_other_than_contradicted)),
                               "after": C.frac(len(fc2), len(truth_other_than_contradicted))},
        "ids": {"wrong_shown_before": ws1, "wrong_shown_after": ws2, "wrong_shown_removed": removed,
                "correct_given_up": given_up, "wrong_made_right": made_right},
    }


def catch_and_giveup(ans, cat, t, ids):
    flagged = {i: cat[i] != "sure" for i in ids}
    right = {i: ans[i] == t[i] for i in ids}
    wrong_ids = [i for i in ids if not right[i]]
    right_ids = [i for i in ids if right[i]]
    ws = [i for i in ids if ans[i] == "shown" and t[i] != "shown"]
    rs = [i for i in ids if ans[i] == "shown" and t[i] == "shown"]
    wc = [i for i in ids if ans[i] == "contradicted" and t[i] != "contradicted"]
    rc = [i for i in ids if ans[i] == "contradicted" and t[i] == "contradicted"]

    def fl(sub):
        return C.frac(sum(flagged[i] for i in sub), len(sub))

    out = {"flagged_share_of_all": fl(ids), "wrong_flagged_of_wrong": fl(wrong_ids), "right_flagged_of_right": fl(right_ids),
           "wrong_shown_flagged_of_wrong_shown": fl(ws), "right_shown_flagged_of_right_shown": fl(rs),
           "wrong_contradicted_flagged_of_wrong_contradicted": fl(wc), "right_contradicted_flagged_of_right_contradicted": fl(rc)}
    out["catch_minus_giveup_all"] = C.diff_of(out["wrong_flagged_of_wrong"], out["right_flagged_of_right"])
    out["catch_minus_giveup_shown"] = C.diff_of(out["wrong_shown_flagged_of_wrong_shown"], out["right_shown_flagged_of_right_shown"])
    return out


def analyse(rows, truth, ids):
    """rows: id -> run 3 record for one arm. truth: id -> normalised truth."""
    ids = [i for i in ids if i in rows]
    n = len(ids)
    ans = {i: rows[i]["answer"] for i in ids}
    cat = {i: category(rows[i]) for i in ids}
    t = {i: truth[i] for i in ids}
    right = {i: ans[i] == t[i] for i in ids}
    out = {"n": n}
    out["truth_counts"] = dict(Counter(t[i] for i in ids))
    out["answer_counts"] = {ty: C.frac(sum(ans[i] == ty for i in ids), n) for ty in TYPES}
    out["constant_not_shown_right"] = C.frac(sum(t[i] == "not shown" for i in ids), n)
    out["certainty_counts"] = {c: C.frac(sum(cat[i] == c for i in ids), n) for c in CATS}
    um = [i for i in ids if cat[i] == "unmarked"]
    out["unmarked_reasons"] = {r: C.frac(sum(unmarked_reason(rows[i]) == r for i in um), len(um)) for r in REASONS}
    acc = {}
    for c in CATS:
        sub = [i for i in ids if cat[i] == c]
        acc[c] = C.frac(sum(right[i] for i in sub), len(sub))
    out["accuracy_by_certainty"] = acc
    out["sure_minus_unsure"] = C.diff_of(acc["sure"], acc["unsure"])
    cells = {}
    for ty in TYPES:
        for c in CATS:
            sub = [i for i in ids if ans[i] == ty and cat[i] == c]
            k_right = sum(right[i] for i in sub)
            k_ns = sum(t[i] == "not shown" for i in sub)
            cells[f"{ty}|{c}"] = {"n": len(sub), "right": C.frac(k_right, len(sub)), "wrong": len(sub) - k_right,
                                  "truth_not_shown": C.frac(k_ns, len(sub)),
                                  "net_if_replaced": (k_ns - k_right) if ty != "not shown" else 0}
    out["cells"] = cells
    out["rule_R_all"] = rule_effects(ans, apply_rule(ans, cat, "R_all"), t, ids)
    out["rule_R_shown"] = rule_effects(ans, apply_rule(ans, cat, "R_shown"), t, ids)
    out["catch_and_giveup"] = catch_and_giveup(ans, cat, t, ids)
    out["ids_of_unmarked"] = um
    return out


def reconcile(sets_result, stored):
    """Compare a few recomputed figures with what score-run3.json stored. Report only."""
    out, agree, total = {}, 0, 0
    for set_name, arms in sets_result.items():
        for arm, res in arms.items():
            key = f"{set_name}|{arm}"
            st = C.get(stored, "sets", set_name, arm)
            if st is None:
                out[key] = {"note": "arm not found in score-run3.json"}
                continue

            def kn(d):
                return [d["k"], d["n"]]

            try:
                cert = st["certainty"]
                R = res["rule_R_all"]
                acc = res["accuracy_by_certainty"]
                chk = {
                    "n_sure": C.compare(res["certainty_counts"]["sure"]["k"], cert.get("sure", 0)),
                    "n_unsure": C.compare(res["certainty_counts"]["unsure"]["k"], cert.get("unsure", 0)),
                    "n_unmarked": C.compare(res["certainty_counts"]["unmarked"]["k"], cert.get("None", 0)),
                    "right_when_sure": C.compare(kn(acc["sure"]), kn(st["right_when_sure"])),
                    "right_when_unsure": C.compare(kn(acc["unsure"]), kn(st["right_when_unsure"])),
                    "raw_right": C.compare(kn(R["right"]["before"]), kn(st["raw"]["right"])),
                    "raw_false_shown": C.compare(kn(R["false_shown_rate"]["before"]), kn(st["raw"]["false_shown"])),
                    "policy_U_right": C.compare(kn(R["right"]["after"]), kn(st["policy_U"]["right"])),
                    "policy_U_false_shown": C.compare(kn(R["false_shown_rate"]["after"]), kn(st["policy_U"]["false_shown"])),
                }
            except (KeyError, TypeError) as e:
                chk = {"note": f"could not compare: {type(e).__name__}: {e}"}
            for v in chk.values():
                if isinstance(v, dict) and "agree" in v:
                    total += 1
                    agree += bool(v["agree"])
            out[key] = chk
    out["tally"] = {"checks": total, "agree": agree, "differ": total - agree}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-at", required=True, help='pass "$(date -u +%%FT%%TZ)"')
    ap.add_argument("--seal-file", default="DESIGN-SHA256.txt")
    args = ap.parse_args()
    seal = C.check_seal(args.seal_file)
    inputs = C.check_inputs()
    print("seal verified; inputs verified against the design hashes")
    items = C.load_bank()
    truth = {i: C.norm_truth(it["truth"]) for i, it in items.items()}
    raw_rows = C.read_jsonl(C.PATHS["run3"])
    by, dups = C.last_per_key(raw_rows)
    arms = {a: {i: r for (arm, i), r in by.items() if arm == a} for a in ARMS}
    print(f"run 3 records read: {len(raw_rows)}; duplicates: {dups}")
    result = {"meta": C.meta(SCRIPT, args.run_at, seal, inputs), "question": "Q3",
              "checks": {"records": len(raw_rows), "duplicate_arm_id": dups,
                         "arms_found": sorted({a for a, _ in by}),
                         "ids_missing_by_arm": {a: sorted(set(C.FRESH) - set(arms[a])) for a in ARMS}},
              "sets": {}}
    for set_name, ids in C.SETS.items():
        result["sets"][set_name] = {a: analyse(arms[a], truth, ids) for a in ARMS}
    try:
        stored = json.loads(C.PATHS["score_run3"].read_text(encoding="utf-8"))
        result["reconciliation_with_score_run3"] = reconcile(result["sets"], stored)
    except Exception as e:  # report-only step
        result["reconciliation_with_score_run3"] = {"note": f"not done: {type(e).__name__}: {e}"}
    path = C.write_new_json("results-q3", result)
    print("written:", path.name)
    tally = result["reconciliation_with_score_run3"].get("tally")
    if tally:
        print(f"reconciliation with the stored run 3 score: {tally['checks']} figures compared, {tally['agree']} agree")


if __name__ == "__main__":
    main()
