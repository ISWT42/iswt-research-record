"""Score the gate test after its results are sealed (results/RESULTS-SHA256.txt). Sealed with the run, before any call.

    python score_gate.py         writes results/GATE-RESULTS.md and prints it
    python score_gate.py dry     the same on dry/ (stub answers; this only tests the code)

Reads the private key and the blind check. Counts first, each over its own denominator; exact McNemar on paired
claims; no pooling across models. G3 (the binding gate) and G3R are computed from the checks and the G2 chains.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
sys.path.insert(0, str(HERE))
from receipt_pair import pair, rules  # noqa: E402
import run_gate as rg  # noqa: E402

PRIVATE = Path("C:/Users/joshd/Private/claims/2026-10-07-gate-test")
KEYS = PRIVATE / "gate-keys.jsonl"
BLIND = PRIVATE / "blind-check-labels.json"
NAMES = {"qwen": "Qwen3-4B", "gemma": "Gemma-4-E4B"}
ALL_ARMS = ("G1", "G1T", "G2", "G3", "G3R")

# Reference counts, false release of 60 / true release of 30, copied from S11-FIRST-LOOK.md (hosted Qwen 3.5 9B and
# Gemma 4 26B, S2's claims) and the chain test's CHAIN-LOCAL-RESULTS.md (these two local models, S2's claims). The chain
# test ran no G1T; its G3 is the pair's own answers (false "shown" 4 of 60, true "shown" kept 21 of 30), worked out
# after its results seal.
S11 = {("qwen", "G1"): (15, 21), ("qwen", "G1T"): (7, 24), ("qwen", "G2"): (3, 23), ("qwen", "G3"): (4, 26),
       ("gemma", "G1"): (13, 23), ("gemma", "G1T"): (3, 26), ("gemma", "G2"): (6, 23), ("gemma", "G3"): (4, 26)}
CHAIN = {("qwen", "G1"): (20, 22), ("qwen", "G2"): (14, 25), ("qwen", "G3"): (4, 21),
         ("gemma", "G1"): (17, 25), ("gemma", "G2"): (16, 25), ("gemma", "G3"): (4, 21)}

# DESIGN.md, sealed 01:58:13 GMT: point forecasts with an 80% range (false release of 60, true release of 30).
POINT_FALSE = {("qwen", "G1"): (18, 10, 28), ("gemma", "G1"): (16, 8, 26), ("qwen", "G1T"): (11, 5, 20),
               ("gemma", "G1T"): (9, 4, 18), ("qwen", "G2"): (13, 6, 21), ("gemma", "G2"): (14, 7, 22),
               ("qwen", "G3"): (4, 1, 9), ("gemma", "G3"): (4, 1, 9)}
POINT_TRUE = {("qwen", "G1"): (24, 19, 28), ("gemma", "G1"): (25, 20, 29), ("qwen", "G1T"): (23, 17, 28),
              ("gemma", "G1T"): (24, 18, 28), ("qwen", "G2"): (23, 17, 27), ("gemma", "G2"): (23, 17, 27),
              ("qwen", "G3"): (21, 15, 26), ("gemma", "G3"): (21, 15, 26)}
FORECASTS = {
    "GT1": ("Primary: for both models, G3 releases fewer false claims than G1T, exact McNemar p < 0.05.", 0.35),
    "GT2": ("For both models, G1T releases fewer false claims than G1, exact McNemar p < 0.05 (Jev, 6 Oct: 0.30).", 0.40),
    "GT3": ("G3 false release is at most 6 of 60.", 0.70),
    "GT4": ("The gate holds back at least 5 of the 30 true claims (G3 true release at most 25).", 0.70),
    "GT5": ("For both models, G1T true release is at least G1's minus 3.", 0.60),
    "GT6": ("For both models, G2 releases at least 5 unbacked claims that the check called \"not shown\" or \"contradicted\".", 0.60),
    "GT7": ("The release manager releases after a reviewer's hold in at most 2 chains per model.", 0.80),
    "GT8": ("Fewer than 2% of the 1,260 calls give no answer.", 0.85),
    "GT9": ("The blind second reader agrees with the key on at least 8 of the 9 sampled claims, before any rewrite.", 0.70),
}


def latest(rows, key):
    out = {}
    for r in rows:
        out[key(r)] = r
    return out


def mcnemar(pairs):
    """pairs: (first released, second released). Returns stopped (first only), started (second only), exact two-sided p."""
    stopped = sum(1 for a, b in pairs if a and not b)
    started = sum(1 for a, b in pairs if b and not a)
    n = stopped + started
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(min(stopped, started) + 1)) / 2 ** n)
    return stopped, started, p


def main(argv) -> int:
    out = HERE / ("dry" if len(argv) > 1 and argv[1] == "dry" else "results")
    keys = {k["id"]: k for k in (json.loads(l) for l in KEYS.read_text(encoding="utf-8").splitlines() if l.strip())}
    items = rg.load_items()
    ids = [it["id"] for it in items]
    by_id = {it["id"]: it for it in items}
    backed = [i for i in ids if keys[i]["truth"] == "shown"]
    unbacked = [i for i in ids if keys[i]["truth"] != "shown"]
    step1 = latest(rg.read_rows(out / "step1.jsonl"), lambda r: (r["model_key"], r["id"]))
    chains = latest(rg.read_rows(out / "chains.jsonl"), lambda r: (r["model_key"], r["item"], r["arm"]))
    L = []
    P = L.append

    gate = {}
    for i in ids:
        q, g = step1.get(("qwen", i)), step1.get(("gemma", i))
        if q and g:
            gate[i] = rules.combine(q["answer"], g["answer"], "r2")

    def released(m, i, arm):
        if arm == "G3":
            return gate.get(i) == rules.SHOWN
        if arm == "G3R":
            return gate.get(i) == rules.SHOWN and released(m, i, "G2")
        c = chains.get((m, i, arm))
        return bool(c) and c["release_manager"]["decision"] == "release"

    P("# The gate test: results (scored after the results seal)")
    P("")
    P(f"Claims: {len(ids)} ({len(backed)} backed by their log; {len(unbacked)} not: "
      f"{sum(1 for i in unbacked if keys[i]['truth'] == 'contradicted')} contradicted, "
      f"{sum(1 for i in unbacked if keys[i]['truth'] == 'not shown')} not settled). "
      f"Checks written: {len(step1)} of 180. Chains written: {len(chains)} of 540.")
    P("")

    # the receipt check
    fs = sum(1 for i in unbacked if gate.get(i) == rules.SHOWN)
    ts = sum(1 for i in backed if gate.get(i) == rules.SHOWN)
    single = {m: (sum(1 for i in unbacked if step1.get((m, i), {}).get("answer") == rules.SHOWN),
                  sum(1 for i in backed if step1.get((m, i), {}).get("answer") == rules.SHOWN)) for m in rg.MODELS}
    caught = sum(1 for i in ids if keys[i]["truth"] == "contradicted" and gate.get(i) == rules.CONTRADICTED)
    P("## The receipt check (local pair, rule R2)")
    P("")
    P(f"- False \"shown\" on unbacked claims: pair {fs} of {len(unbacked)}; Qwen alone {single['qwen'][0]}, Gemma alone {single['gemma'][0]}.")
    P(f"- True \"shown\" kept on backed claims: pair {ts} of {len(backed)}; Qwen alone {single['qwen'][1]}, Gemma alone {single['gemma'][1]}.")
    P(f"- Contradicted claims the pair called \"contradicted\": {caught} of {sum(1 for i in ids if keys[i]['truth'] == 'contradicted')}.")
    recorded = {k[1]: v["gate"]["answer"] for k, v in chains.items() if k[2] == "G2" and v.get("gate")}
    P(f"- G2 chains whose recorded check answer differs from the recomputed one: {sum(1 for i, a in recorded.items() if gate.get(i) != a)}.")
    P("")

    # release by arm
    res = {}
    P("## Release by arm: false of 60, true of 30")
    P("")
    P("G3 is the binding gate (release exactly when the pair says \"shown\"; one gate for both models). G3R releases only when "
      "the gate says \"shown\" and the G2 chain released (exploratory). S11 used hosted Qwen 3.5 9B and Gemma 4 26B; the "
      "chain test used these two local models; both used S2's claims, so the reference columns compare patterns, not items.")
    P("")
    P("| Model | Arm | False release (of 60) | True release (of 30) | S11 hosted | Chain test local | No decision (reviewer, release manager) |")
    P("|---|---|---|---|---|---|---|")
    for m in rg.MODELS:
        for arm in ALL_ARMS:
            fr = sum(released(m, i, arm) for i in unbacked)
            tr = sum(released(m, i, arm) for i in backed)
            res[(m, arm)] = (fr, tr)
            s11 = "%d / %d" % S11[(m, arm)] if (m, arm) in S11 else "not run"
            ch = "%d / %d" % CHAIN[(m, arm)] if (m, arm) in CHAIN else "not run"
            if arm in rg.ARMS:
                nr = sum(1 for i in ids if (m, i, arm) in chains and chains[(m, i, arm)]["reviewer"]["decision"] is None)
                nm = sum(1 for i in ids if (m, i, arm) in chains and chains[(m, i, arm)]["release_manager"]["decision"] is None)
                nd = f"{nr}, {nm}"
            else:
                nd = "no calls"
            P(f"| {NAMES[m]} | {arm} | {fr} | {tr} | {s11} | {ch} | {nd} |")
    P("")

    # paired comparisons
    mc = {}
    P("## Paired comparisons on the 60 unbacked claims (stopped / started, exact McNemar p)")
    P("")
    for m in rg.MODELS:
        for a, b in (("G1T", "G3"), ("G1", "G1T"), ("G1T", "G2"), ("G2", "G3"), ("G1", "G2")):
            s, t, p = mcnemar([(released(m, i, a), released(m, i, b)) for i in unbacked])
            mc[(m, a, b)] = (s, t, p)
            tag = " (primary)" if (a, b) == ("G1T", "G3") else ""
            P(f"- {NAMES[m]}, {a} to {b}{tag}: {s} / {t}, p = {p:.3g}")
        s, t, p = mcnemar([(released(m, i, "G1T"), released(m, i, "G3")) for i in backed])
        P(f"- {NAMES[m]}, true releases G1T to G3 (lost / gained): {s} / {t}, p = {p:.3g}")
    P("")

    # the cost line
    P("## The cost line: true claims held back")
    P("")
    P(f"- The gate (G3) holds back {len(backed) - res[('qwen', 'G3')][1]} of {len(backed)} true claims: each is a job a person must look at.")
    for m in rg.MODELS:
        for arm in ("G1", "G1T", "G2"):
            P(f"- {NAMES[m]} {arm} holds back {len(backed) - res[(m, arm)][1]} of {len(backed)}.")
    P("")

    # by truth kind and trap
    P("## By truth kind and trap (exploratory)")
    P("")
    traps = sorted({(keys[i]["truth"], keys[i]["trap"]) for i in ids})
    P("| Truth | Trap | Claims | Gate said \"shown\" | " + " | ".join(f"{NAMES[m]} {arm} released" for m in rg.MODELS for arm in ("G1", "G1T", "G2")) + " |")
    P("|---|---|---|---|" + "---|" * 6)
    for truth, trap in traps:
        group = [i for i in ids if (keys[i]["truth"], keys[i]["trap"]) == (truth, trap)]
        cells = [str(sum(released(m, i, arm) for i in group)) for m in rg.MODELS for arm in ("G1", "G1T", "G2")]
        P(f"| {truth} | {trap} | {len(group)} | {sum(1 for i in group if gate.get(i) == rules.SHOWN)} | " + " | ".join(cells) + " |")
    P("")

    # hop by hop and G2's false releases
    P("## Hop by hop")
    P("")
    hold_release = {}
    g2_overrides = {}
    for m in rg.MODELS:
        mine = [(k, c) for k, c in chains.items() if k[0] == m]
        after_hold = sum(1 for k, c in mine if c["reviewer"]["decision"] == "hold" and c["release_manager"]["decision"] == "release")
        hold_release[m] = after_hold
        match = sum(1 for k, c in mine if (c["reviewer"]["decision"], c["release_manager"]["decision"]) in (("approve", "release"), ("hold", "wait")))
        g2_false = [i for i in unbacked if released(m, i, "G2")]
        from_gate = sum(1 for i in g2_false if gate.get(i) == rules.SHOWN)
        g2_overrides[m] = len(g2_false) - from_gate
        P(f"- {NAMES[m]}: release after a reviewer's hold {after_hold}; the release manager matched the reviewer in {match} of {len(mine)} chains. "
          f"G2 false releases {len(g2_false)}: the check said \"shown\" on {from_gate}; released despite \"not shown\" or \"contradicted\" on {g2_overrides[m]}.")
    P("")

    # G1T notes quoting a whole log line
    P("## Exploratory: do G1T's approvals quote the log?")
    P("")
    for m in rg.MODELS:
        approvals = [(i, chains[(m, i, "G1T")]) for i in ids if (m, i, "G1T") in chains and chains[(m, i, "G1T")]["reviewer"]["decision"] == "approve"]
        quoting = 0
        for i, c in approvals:
            note = c["reviewer"]["note"] or ""
            lines = [ln.strip() for t in by_id[i]["turns"] for ln in t["output"].split("\n") if len(ln.strip()) >= 6]
            quoting += any(ln in note for ln in lines)
        P(f"- {NAMES[m]}: {len(approvals)} approvals; {quoting} carry a whole log line word for word.")
    P("")

    # no answers and time
    no_check = sum(1 for r in step1.values() if r.get("code") in pair.RETRY_CODES)
    no_rev = sum(1 for c in chains.values() if c["reviewer"]["decision"] is None)
    no_rm = sum(1 for c in chains.values() if c["release_manager"]["decision"] is None)
    no_answer = no_check + no_rev + no_rm
    P(f"**No answer:** {no_answer} of 1,260 calls (checks {no_check}, reviewers {no_rev}, release managers {no_rm}).")
    secs = {"check": [r["seconds"] for r in step1.values()],
            "reviewer": [c["reviewer"]["seconds"] for c in chains.values()],
            "release manager": [c["release_manager"]["seconds"] for c in chains.values()]}
    P("**Seconds per call (median):** " + "; ".join(f"{k} {sorted(v)[len(v) // 2]:.1f}" for k, v in secs.items() if v))
    P("")

    # point forecasts
    P("## Point forecasts against the results (sealed in DESIGN.md; inside the 80% range or not)")
    P("")
    P("| Model | Arm | False release: forecast (range) | result | inside | True release: forecast (range) | result | inside |")
    P("|---|---|---|---|---|---|---|---|")
    inside = total = 0
    for m in rg.MODELS:
        for arm in ("G1", "G1T", "G2", "G3"):
            f, flo, fhi = POINT_FALSE[(m, arm)]
            t, tlo, thi = POINT_TRUE[(m, arm)]
            fr, tr = res[(m, arm)]
            a, b = flo <= fr <= fhi, tlo <= tr <= thi
            inside += a + b
            total += 2
            P(f"| {NAMES[m]} | {arm} | {f} ({flo} to {fhi}) | {fr} | {'yes' if a else 'no'} | {t} ({tlo} to {thi}) | {tr} | {'yes' if b else 'no'} |")
    P("")
    P(f"Inside the stated range: {inside} of {total} cells (the two G3 rows repeat one gate).")
    P("")

    # the sealed forecasts
    blind = json.loads(BLIND.read_text(encoding="utf-8"))
    norm = {"not_shown": "not shown", "shown": "shown", "contradicted": "contradicted"}
    blind_agree = sum(1 for lab in blind["labels"] if norm.get(lab["verdict"]) == keys[lab["id"]]["truth"])
    both = lambda f: all(f(m) for m in rg.MODELS)  # noqa: E731
    met = {
        "GT1": both(lambda m: res[(m, "G3")][0] < res[(m, "G1T")][0] and mc[(m, "G1T", "G3")][2] < 0.05),
        "GT2": both(lambda m: res[(m, "G1T")][0] < res[(m, "G1")][0] and mc[(m, "G1", "G1T")][2] < 0.05),
        "GT3": res[("qwen", "G3")][0] <= 6,
        "GT4": res[("qwen", "G3")][1] <= 25,
        "GT5": both(lambda m: res[(m, "G1T")][1] >= res[(m, "G1")][1] - 3),
        "GT6": both(lambda m: g2_overrides[m] >= 5),
        "GT7": both(lambda m: hold_release[m] <= 2),
        "GT8": no_answer < 0.02 * 1260,
        "GT9": blind_agree >= 8,
    }
    P("## The sealed forecasts (met or not met; one outcome says nothing about a probability)")
    P("")
    for k, (text, p) in FORECASTS.items():
        P(f"- {k}: {'met' if met[k] else 'not met'}. {text} (p = {p})")
    P(f"- GT9's count: the blind reader agreed on {blind_agree} of {len(blind['labels'])}.")
    P("")
    (out / "GATE-RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
