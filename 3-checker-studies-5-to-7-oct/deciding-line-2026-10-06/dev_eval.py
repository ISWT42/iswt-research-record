"""Development evaluation of the key-free rules on run 2's existing answers, and the pre-registered choice of the primary rule.
(PREREG-1.md, stamped before any development quote was opened.) No model calls, no network calls.
Reads: the bank (ids 161 to 300 only are used), run 2's local answers (arms A, B) and run 2's hosted answers (arms F-Q, F-G);
each input must have the SHA-256 written in the re-score's DESIGN.md. Prints and writes counts, ids and labels only.
  python dev_eval.py --run-at "$(date -u +%FT%TZ)" [--no-write] [--own-rule-module own_rule]
"""
import argparse
import importlib
import sys
from pathlib import Path

import deciding_rules as DR

HERE = Path(__file__).resolve().parent
WORK = Path(r"C:\Users\joshd\Workbench")
BANK = WORK / "chatgpt-review-2026-10-04" / "completion-claims-001-300.jsonl"
RUN2 = WORK / "lemonade-entry-2026-10-05" / "run2" / "results"
INPUTS = {
    "bank": (BANK, "edb897f7b6d7df41a14eb37e4f6079ade036dabdec6d140d82dec6147199593a"),
    "run2_local": (RUN2 / "answers-run2-local.jsonl", "ba5303a247fe5a805064261c698e0958a36b20d6ec3791c69a1fb48f9c09eed5"),
    "run2_fast": (RUN2 / "answers-run2-fast.jsonl", "7f634ad3a0ae7874bdecb81aec31096db7a2f6cbbfe4f597bd653c22092f284e"),
}
PAIRS = {"local": ("run2_local", ("A", "B")), "hosted": ("run2_fast", ("F-Q", "F-G"))}
SETS = {"fresh_161_300": lambda i: "161" <= i <= "300", "primary_201_300": lambda i: "201" <= i <= "300"}
RANK = {"SAME-LINE": 0, "OUTCOME-MARKER": 1}   # simpler first; an own rule ranks last


def check_inputs():
    out = {}
    for key, (path, want) in INPUTS.items():
        got = DR.sha256_file(path)
        out[key] = {"sha256": got, "matches_expected": got == want}
        if got != want:
            raise SystemExit(f"STOP: {key} differs from the hash in the re-score DESIGN.md")
    return out


def choose_primary(local_res, hosted_res, candidates):
    """The pre-registered procedure (PREREG-1.md, 'Choosing the primary rule'). Returns (name, per-candidate table)."""
    rank = dict(RANK)
    for c in candidates:
        rank.setdefault(c, len(rank))
    F = local_res["rules"][candidates[0]]["bar"]["r2_false_shown"]
    T = local_res["rules"][candidates[0]]["bar"]["r2_true_shown"]
    table = {}
    for c in candidates:
        e = local_res["rules"][c]
        f, t = e["removed"]["false"], e["removed"]["true"]
        table[c] = {"f_local": f, "t_local": t, "eligible": 5 * (T - t) >= 4 * T, "f_hosted": hosted_res["rules"][c]["removed"]["false"],
                    "separation_local": (f / F - t / T) if (F and T) else float("-inf"), "rank": rank[c]}
    elig = [c for c in candidates if table[c]["eligible"] and table[c]["f_local"] >= 1]
    if elig:
        best = sorted(elig, key=lambda c: (-table[c]["f_local"], table[c]["t_local"], -table[c]["f_hosted"], table[c]["rank"]))[0]
        step = "step 2: eligible candidate with the most false 'shown' removed (ties: fewer true removed, more removed on the hosted pair, simpler rule)"
    else:
        best = sorted(candidates, key=lambda c: (-table[c]["separation_local"], table[c]["rank"]))[0]
        step = "step 3: no eligible candidate removes a false 'shown'; largest separation f/F - t/T (ties: SAME-LINE first)"
    for c in table:
        if table[c]["separation_local"] == float("-inf"):
            table[c]["separation_local"] = None
        else:
            table[c]["separation_local"] = round(table[c]["separation_local"], 4)
    return best, step, table


def own_rule_gate(local_res, hosted_res, name):
    """PREREG-1 (own-rule clause) and PREREG-2 (validation): the own rule is a candidate only if, on the local set, it removes at
    least half of R2's false 'shown' and keeps at least 80% of R2's true 'shown', and, on the hosted pair, it removes at least one
    false 'shown' with separation f/F - t/T >= 0 (integer cross-multiplication)."""
    e, h = local_res["rules"][name], hosted_res["rules"][name]
    Fh, Th = h["bar"]["r2_false_shown"], h["bar"]["r2_true_shown"]
    fh, th = h["removed"]["false"], h["removed"]["true"]
    local_ok = bool(e["bar"]["removal_half_met"] and e["bar"]["retention_met"])
    hosted_ok = bool(fh >= 1 and Fh > 0 and Th > 0 and fh * Th >= th * Fh)
    return {"local_conditions_met": local_ok, "hosted_validation_met": hosted_ok, "admitted": local_ok and hosted_ok,
            "hosted": {"r2_false_shown": Fh, "r2_true_shown": Th, "false_removed": fh, "true_removed": th}}


def line(label, m, base=None):
    fs, ts = m["false_shown"], m["true_shown_kept"]
    return f"  {label:<26} false shown {fs['k']:>3}/{fs['n']:<3}  true shown kept {ts['k']:>3}/{ts['n']:<3}  right {m['right']['k']:>3}/{m['right']['n']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-at", required=True, help='pass "$(date -u +%%FT%%TZ)"')
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--own-rule-module", default=None, help="module with NAME and make_rule(items); the own rule of PREREG-2.md")
    args = ap.parse_args()
    inputs = check_inputs()
    print("inputs verified against the hashes in the re-score DESIGN.md")
    extra, mod = (), None
    if args.own_rule_module:
        mod = importlib.import_module(args.own_rule_module)
    items = {}
    for obj in DR.read_jsonl(INPUTS["bank"][0]):
        it = DR.load_item(obj)
        items[it["id"]] = it
    if mod is not None:
        extra = ((mod.NAME, mod.make_rule(items)),)
        print(f"own rule loaded: {mod.NAME}")
    recs = {}
    for key in ("run2_local", "run2_fast"):
        rows = DR.read_jsonl(INPUTS[key][0])
        recs[key], dups = DR.last_per_key(rows)
        print(f"{key}: {len(rows)} records; duplicate (arm, id): {dups}")
    result = {"script": "dev_eval.py", "run_at": args.run_at, "python": sys.version.split()[0], "inputs": inputs,
              "script_sha256": DR.sha256_file(HERE / "dev_eval.py"), "rules_sha256": DR.sha256_file(HERE / "deciding_rules.py"),
              "markers_sha256": DR.sha256_file(HERE / "outcome_markers.py"), "sets": {}}
    candidates = ["SAME-LINE", "OUTCOME-MARKER"]
    for set_name, flt in SETS.items():
        result["sets"][set_name] = {}
        for pair, (key, arms) in PAIRS.items():
            res = DR.analyse(items, recs[key], arms, extra_rules=extra, id_filter=flt)
            result["sets"][set_name][pair] = res
    for set_name in SETS:
        for pair in PAIRS:
            res = result["sets"][set_name][pair]
            print(f"\n== {set_name} | {pair} pair {res['arms']} | items {res['n_items']} | truth {res['truth_counts']} | "
                  f"R2 'shown' answers {res['r2_shown_items']} (flags: {res['evidence_flags_on_r2_shown'] or 'none'}; anomalies: {res['anomalies'] or 'none'})")
            print(line("R2 (shown needs both)", res["R2"]))
            for name, e in res["rules"].items():
                r = e["removed"]
                print(line(f"{name} [{e['kind']}]", e["measures"]) + f"  removes {r['total']:>2} (false {r['false']}, true {r['true']})")
    sel_local = result["sets"]["fresh_161_300"]["local"]
    sel_hosted = result["sets"]["fresh_161_300"]["hosted"]
    gates = {}
    for n, _ in extra:
        gates[n] = own_rule_gate(sel_local, sel_hosted, n)
        print(f"\nown rule gate for {n}: {gates[n]}")
        if gates[n]["admitted"]:
            candidates.append(n)
    best, step, table = choose_primary(sel_local, sel_hosted, candidates)
    result["selection"] = {"primary": best, "rule_applied": step, "candidates": table, "own_rule_gates": gates,
                           "basis": "local pair, ids 161 to 300 (hosted pair as tie-break and, for an own rule, as validation)"}
    print("\nSELECTION (pre-registered procedure):", best, "|", step)
    for c, v in table.items():
        print(f"  {c}: {v}")
    if not args.no_write:
        p = DR.write_new_json(HERE / "dev-results", result)
        print("written:", p.name)


if __name__ == "__main__":
    main()
