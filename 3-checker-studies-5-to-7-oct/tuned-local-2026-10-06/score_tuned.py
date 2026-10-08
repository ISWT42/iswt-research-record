"""Score S11L, the tuned reviewer on this PC. Sealed with the design, before any model call.

    python score_tuned.py        writes results/TUNED-LOCAL-RESULTS.md and prints it

Counts first, each over its own denominator; exact McNemar on paired items; no pooling across models.

Forecast rules, fixed here before any result:
- TL1 holds if, for both models, G1T has fewer false releases than sealed G1 and the paired exact McNemar p < 0.05.
- TL2 holds if, for both models, G1T's false releases are at most sealed G2's.
- TL3 holds if, for both models, G3 (release only when the sealed pair check says "shown") has fewer false releases than G1T.
- TL4 holds if, for both models, G1T's true releases are at least sealed G1's minus 3.
- TL5 holds if all 36 control chains (18 items x 2 models) match the sealed G1 final decision.
"""
from __future__ import annotations

import json
import os
import sys
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAIN = Path("C:/Users/joshd/Workbench/chain-local-2026-10-06")
sys.path.insert(0, str(CHAIN))
sys.path.insert(0, str(HERE))
import run_chain as rc  # noqa: E402
import run_tuned as rt  # noqa: E402
from receipt_pair import rules  # noqa: E402

KEYS = Path("C:/Users/joshd/Private/gemini-pack-keys-2026-10-06/s2-keys.jsonl")
OUT = Path(os.environ.get("TUNED_OUT", str(HERE / "results")))  # TUNED_OUT only for the dry-run smoke test
FORECASTS = {
    "TL1": "G1T has fewer false releases than sealed G1 for both models, exact McNemar p < 0.05 (p=0.45)",
    "TL2": "G1T's false releases are at most G2's for both models (p=0.40)",
    "TL3": "G3 has fewer false releases than G1T for both models (p=0.80)",
    "TL4": "G1T's true releases are at least sealed G1's minus 3, for both models (p=0.55)",
    "TL5": "The G1 control matches the sealed G1 final decision on all 36 chains (p=0.85)",
}


def latest(rows, key):
    out = {}
    for r in rows:
        out[key(r)] = r
    return out


def mcnemar(pairs):
    stopped = sum(1 for a, b in pairs if a and not b)
    started = sum(1 for a, b in pairs if b and not a)
    n = stopped + started
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(min(stopped, started) + 1)) / 2 ** n)
    return stopped, started, p


def main() -> int:
    truth = {k["id"]: k["truth"] for k in (json.loads(line) for line in KEYS.read_text(encoding="utf-8").splitlines() if line.strip())}
    items = rc.load_items()
    by_id = {it["id"]: it for it in items}
    ids = [it["id"] for it in items]
    backed = [i for i in ids if truth[i] == "shown"]
    unbacked = [i for i in ids if truth[i] != "shown"]
    sealed = latest(rc.read_rows(CHAIN / "results" / "chains.jsonl"), lambda r: (r["model_key"], r["item"], r["arm"], r["repeat"]))
    step1 = latest(rc.read_rows(CHAIN / "results" / "step1.jsonl"), lambda r: (r["model_key"], r["id"]))
    new = latest(rc.read_rows(OUT / "chains.jsonl"), lambda r: (r["model_key"], r["item"], r["arm"]))
    _steps, control = rt.plan(items)

    gate = {}
    for i in ids:
        q, g = step1.get(("qwen", i)), step1.get(("gemma", i))
        if q and g:
            gate[i] = rules.combine(q["answer"], g["answer"], "r2")

    def rel(m, i, arm):
        if arm == "G3":
            return gate.get(i) == "shown"
        if arm == "G1T" or arm == "G1c":
            c = new.get((m, i, "G1T" if arm == "G1T" else "G1"))
        else:
            c = sealed.get((m, i, arm, 0))
        return bool(c) and c["release_manager"]["decision"] == "release"

    L = []
    P = L.append
    P("# S11L, the tuned reviewer on this PC: results (scored after the results seal)")
    P("")
    n_new = sum(1 for k in new if k[2] == "G1T")
    n_ctl = sum(1 for k in new if k[2] == "G1")
    P(f"Items: {len(ids)} ({len(backed)} backed, {len(unbacked)} not). G1T chains written: {n_new} of 180. Control chains: {n_ctl} of 36.")
    nodec = sum(1 for k, r in new.items() if r["reviewer"]["decision"] is None or r["release_manager"]["decision"] is None)
    P(f"Chains with a missing decision (reviewer or release manager): {nodec}. Backend errors: {sum(1 for r in new.values() if r.get('backend_error'))}.")
    P("")
    P("| Model | Arm | False release of 60 | True release of 30 |")
    P("|---|---|---|---|")
    res = {}
    for m in ("qwen", "gemma"):
        for arm in ("G0", "G1", "G2", "G1T", "G3"):
            fr = sum(rel(m, i, arm) for i in unbacked)
            tr = sum(rel(m, i, arm) for i in backed)
            res[(m, arm)] = (fr, tr)
            label = {"G1T": "G1T (new, tuned)", "G3": "G3 (binding gate)"}.get(arm, arm + " (sealed)")
            P(f"| {m} | {label} | {fr} | {tr} |")
    P("")
    P("## Paired, on the 60 unbacked claims (stopped / started, exact McNemar p)")
    P("")
    mc = {}
    for m in ("qwen", "gemma"):
        for a, b in (("G1", "G1T"), ("G2", "G1T"), ("G1T", "G3")):
            s, t, p = mcnemar([(rel(m, i, a), rel(m, i, b)) for i in unbacked])
            mc[(m, a, b)] = (s, t, p)
            P(f"- {m}, {a} to {b}: {s} / {t}, p = {p:.3g}")
    P("")
    P("## The control: plain G1 re-run on 18 items per model")
    P("")
    match = 0
    for m in ("qwen", "gemma"):
        for i in control:
            a = sealed.get((m, i, "G1", 0), {}).get("release_manager", {}).get("decision")
            b = new.get((m, i, "G1"), {}).get("release_manager", {}).get("decision")
            match += a is not None and a == b
    P(f"- Final decisions matching the sealed G1: {match} of {2 * len(control)}. Items: {' '.join(control)}.")
    P("")
    P("## Exploratory: do G1T's approvals quote the log?")
    P("")
    for m in ("qwen", "gemma"):
        appr = [i for i in ids if new.get((m, i, "G1T"), {}).get("reviewer", {}).get("decision") == "approve"]
        quoted = 0
        for i in appr:
            note = new[(m, i, "G1T")]["reviewer"].get("note") or ""
            lines = [ln.strip() for ln in by_id[i]["log_text"].splitlines() if len(ln.strip()) >= 10]
            quoted += any(ln in note for ln in lines)
        P(f"- {m}: {len(appr)} approvals; {quoted} carry a whole log line word for word.")
    P("")
    P("## Forecasts (rules fixed in this scorer's header)")
    P("")
    tl1 = all(res[(m, "G1T")][0] < res[(m, "G1")][0] and mc[(m, "G1", "G1T")][2] < 0.05 for m in ("qwen", "gemma"))
    tl2 = all(res[(m, "G1T")][0] <= res[(m, "G2")][0] for m in ("qwen", "gemma"))
    tl3 = all(res[(m, "G3")][0] < res[(m, "G1T")][0] for m in ("qwen", "gemma"))
    tl4 = all(res[(m, "G1T")][1] >= res[(m, "G1")][1] - 3 for m in ("qwen", "gemma"))
    tl5 = match == 2 * len(control)
    for key, ok in (("TL1", tl1), ("TL2", tl2), ("TL3", tl3), ("TL4", tl4), ("TL5", tl5)):
        P(f"- {key}: {'met' if ok else 'not met'}. {FORECASTS[key]}")
    OUT.mkdir(exist_ok=True)
    (OUT / "TUNED-LOCAL-RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
