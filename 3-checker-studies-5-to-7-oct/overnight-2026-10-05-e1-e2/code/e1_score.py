"""E1 scoring, from the sealed answers, as the sealed design says. Counts first, each with its own denominator.
  python e1_score.py score        refuses unless the items and the answers are sealed (hash line + FreeTSA reply) and match; writes the
                                  score file and prints no numbers
  python e1_score.py show         prints the latest score file, but only once it is sealed (E1-SCORE-SHA256.txt + FreeTSA reply)
Never overwrites a score file (a taken name gets the next free number). Prints counts only.
"""
import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc   # noqa: E402

r2, rp = oc.r2, oc.rp
E1 = oc.ROOT / "e1"
RES = E1 / "results"
NOANS = "no answer"            # a call with no usable reply after all tries: wrong for that model; "not shown" inside a pair rule
LABELS = ("shown", "contradicted", "not shown")


def split_measures(ans, truth, ids):
    """False 'shown' split by the two truths that are not 'shown' (the strict reading of the denominator)."""
    t = {i: oc.norm(truth[i]) for i in ids}
    out = {}
    for lab in ("contradicted", "not shown"):
        sub = [i for i in ids if t[i] == lab]
        out[f"false_shown_on_truth_{lab.replace(' ', '_')}"] = r2.frac(sum(ans[i] == "shown" for i in sub), len(sub))
    return out


def score():
    if not oc.sealed_ok(E1 / "ITEMS-SHA256.txt", "items-X001-X150.jsonl"):
        sys.exit("STOP: the items are not sealed or do not match their seal")
    if not oc.sealed_ok(RES / "E1-ANSWERS-SHA256.txt", "answers-e1-local.jsonl"):
        sys.exit("STOP: the answers must be sealed (hash line + FreeTSA reply) before they are scored")
    items = {r["id"]: r for r in oc.read_jsonl(E1 / "items-X001-X150.jsonl")}
    ids = sorted(items)
    truth = {i: items[i]["truth"] for i in ids}
    trap = {i: items[i]["trap"] for i in ids}
    fmt = {i: ("pseudo" if items[i]["format"] == "pseudo" else "real") for i in ids}
    recs = oc.read_jsonl(RES / "answers-e1-local.jsonl")
    single, codes, secs = {}, {}, {}
    for a in ("A", "B"):
        by = {r["id"]: r for r in recs if r["arm"] == a}
        single[a] = {i: (NOANS if (i not in by or by[i]["code"] in ("backend_error", "timeout")) else by[i]["answer"]) for i in ids}
        codes[a] = dict(Counter((by[i]["code"] if i in by else "missing") for i in ids))
        secs[a] = sorted(by[i]["seconds"] for i in ids if i in by)
    as_rule = lambda v: "not shown" if v == NOANS else v   # noqa: E731
    A, B = single["A"], single["B"]
    arms = {"A": A, "B": B,
            "R1": {i: rp.pair(as_rule(A[i]), as_rule(B[i])) for i in ids},
            "R2": {i: r2.rule2(as_rule(A[i]), as_rule(B[i])) for i in ids},
            "R3": {i: r2.rule3(as_rule(A[i]), as_rule(B[i])) for i in ids}}
    res = {"items_sha256": oc.sha256_file(E1 / "items-X001-X150.jsonl"), "answers_sha256": oc.sha256_file(RES / "answers-e1-local.jsonl"),
           "design_sha256_file": (oc.ROOT / "E1-DESIGN-SHA256.txt").read_text(encoding="utf-8").strip().splitlines(),
           "n_items": len(ids), "truth_counts": dict(Counter(oc.norm(truth[i]) for i in ids)),
           "reply_codes": codes, "median_seconds_per_call": {a: (s[len(s) // 2] if s else None) for a, s in secs.items()}}
    m = {k: r2.measures(v, truth, trap, ids) for k, v in arms.items()}
    for k in m:
        m[k].update(split_measures(arms[k], truth, ids))
    res["measures"] = m
    # by format (pseudo-commands against real tool formats)
    byfmt = {}
    for g in ("pseudo", "real"):
        sub = [i for i in ids if fmt[i] == g]
        byfmt[g] = {k: {kk: r2.measures(v, truth, trap, sub)[kk] for kk in ("right", "false_shown", "true_shown_kept")} for k, v in arms.items()}
    res["by_format"] = byfmt
    # both models wrong
    wa = {i for i in ids if A[i] != oc.norm(truth[i])}
    wb = {i for i in ids if B[i] != oc.norm(truth[i])}
    small = min(len(wa), len(wb))
    res["both_wrong"] = {"A_wrong": len(wa), "B_wrong": len(wb), "both_wrong": len(wa & wb), "of_the_smaller_models_errors": f"{len(wa & wb)} of {small}"}
    given_up = lambda x, y: sum(1 for i in ids if oc.norm(truth[i]) == "shown" and arms[x][i] == "shown" and arms[y][i] != "shown")   # noqa: E731
    res["true_shown_given_up"] = {"R2_against_R1": given_up("R1", "R2"), "R2_against_A": given_up("A", "R2"), "R2_against_B": given_up("B", "R2")}
    # the primary comparison: R2 against the better single model on false "shown"
    fs = {a: m[a]["false_shown"]["k"] for a in arms}
    rt = {a: m[a]["right"]["k"] for a in arms}
    best = min(("A", "B"), key=lambda a: (fs[a], -rt[a], a))     # fewer false "shown"; then more right; then A
    n_ns = m["A"]["false_shown"]["n"]
    res["primary"] = {"measure": "false 'shown' over items whose truth is not 'shown'", "denominator": n_ns,
                      "A": fs["A"], "B": fs["B"], "R1": fs["R1"], "R2": fs["R2"], "R3": fs["R3"],
                      "better_single_model": best, "better_single_false_shown": fs[best],
                      "half_of_better_single": fs[best] / 2, "R2_at_most_half": fs["R2"] <= fs[best] / 2,
                      "R2_strictly_below_both_singles": fs["R2"] < fs["A"] and fs["R2"] < fs["B"]}
    fc = {a: m[a]["false_contradicted"]["k"] for a in arms}
    both_share = (len(wa & wb) / small) if small else None
    res["forecasts_as_sealed"] = {
        "F1_R2_false_shown_at_most_half_of_better_single (p 0.45)": res["primary"]["R2_at_most_half"],
        "F2_R2_false_shown_strictly_below_both_singles (p 0.85)": res["primary"]["R2_strictly_below_both_singles"],
        "F3_both_wrong_at_least_half_of_smaller_models_errors (p 0.70)": (both_share is not None and both_share >= 0.5),
        "F4_R3_false_contradicted_below_R1 (p 0.95)": fc["R3"] < fc["R1"],
        "numbers": {"both_wrong_share_of_smaller": both_share, "false_contradicted": fc},
    }
    name, k = "score-e1.json", 2
    target = RES / name
    while target.exists():
        target, k = RES / f"score-e1-{k}.json", k + 1
    target.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("written:", target.name, "| sha256", oc.sha256_file(target), "| seal it before reading it (show prints it)")


def latest_score():
    files = sorted(RES.glob("score-e1*.json"), key=lambda p: (len(p.name), p.name))
    return files[-1] if files else None


def show(path=None):
    path = Path(path) if path else latest_score()
    if not oc.sealed_ok(RES / "E1-SCORE-SHA256.txt", path.name):
        sys.exit("STOP: the score file is not sealed (hash line + FreeTSA reply) or does not match its seal; seal it before reading it")
    res = json.loads(path.read_text(encoding="utf-8"))
    m = res["measures"]
    print(f"{path.name}: items {res['n_items']}; truth {res['truth_counts']}; reply codes {res['reply_codes']}")
    for a in m:
        x = m[a]
        print(f"{a:3s} right {x['right']['k']}/{x['right']['n']} {x['right']['ci95']}  false_shown {x['false_shown']['k']}/{x['false_shown']['n']} {x['false_shown']['ci95']}  "
              f"true_shown_kept {x['true_shown_kept']['k']}/{x['true_shown_kept']['n']} {x['true_shown_kept']['ci95']}  "
              f"false_contradicted {x['false_contradicted']['k']}/{x['false_contradicted']['n']}")
    print("primary:", res["primary"])
    print("both wrong:", res["both_wrong"])
    print("true shown given up:", res["true_shown_given_up"])
    print("forecasts:", json.dumps(res["forecasts_as_sealed"], indent=1))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "score":
        score()
    elif len(sys.argv) > 1 and sys.argv[1] == "show":
        show(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print(__doc__)
