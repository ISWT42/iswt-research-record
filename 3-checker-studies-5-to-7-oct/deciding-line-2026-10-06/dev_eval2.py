"""Development evaluation, round 2 (PREREG-3.md): the local development set is now ids 001 to 300 (run 1's local answers for 001 to 160
plus run 2's local answers for 161 to 300); the hosted pair (run 2, ids 161 to 300) is the validation and tie-break. The own rule is
NON-SETTLING-2; version 1 (NON-SETTLING) is evaluated as 'withdrawn' for the record and is not a candidate. The choosing procedure and
the own-rule gate are those of PREREG-1 and PREREG-2 (dev_eval.choose_primary and dev_eval.own_rule_gate, unchanged), applied to the
pooled local set. No model calls, no network calls. Prints and writes counts, ids and labels only, never item text.
By default only status lines are printed; --show prints the tables.
  python dev_eval2.py --run-at "$(date -u +%FT%TZ)" [--show] [--no-write]
"""
import argparse
import sys
from pathlib import Path

import deciding_rules as DR
import dev_eval as DE
import non_settling_rule as V1
import non_settling_rule2 as V2

HERE = Path(__file__).resolve().parent
WORK = Path(r"C:\Users\joshd\Workbench")
RUN1 = WORK / "lemonade-entry-2026-10-05" / "results" / "answers-run.jsonl"
RUN1_SHA = "0cf9b3775d9258c7a34d30af35dccabb33248239e06bf8fb73bfbe0c34c482af"
WITHDRAWN = "NON-SETTLING (version 1, withdrawn)"
SETS = {"local_pooled_001_300": ("local", lambda i: "001" <= i <= "300"),
        "local_run1_001_160": ("local", lambda i: "001" <= i <= "160"),
        "local_run2_161_300": ("local", lambda i: "161" <= i <= "300"),
        "local_run2_201_300": ("local", lambda i: "201" <= i <= "300"),
        "hosted_run2_161_300": ("hosted", lambda i: "161" <= i <= "300"),
        "hosted_run2_201_300": ("hosted", lambda i: "201" <= i <= "300")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-at", required=True, help='pass "$(date -u +%%FT%%TZ)"')
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--show", action="store_true", help="print the tables (otherwise status lines only)")
    args = ap.parse_args()
    inputs = DE.check_inputs()
    got = DR.sha256_file(RUN1)
    inputs["run1_answers"] = {"sha256": got, "matches_expected": got == RUN1_SHA}
    if got != RUN1_SHA:
        raise SystemExit("STOP: run 1's answer file differs from its sealed hash")
    print("inputs verified against the sealed hashes")
    items = {}
    for obj in DR.read_jsonl(DE.INPUTS["bank"][0]):
        it = DR.load_item(obj)
        items[it["id"]] = it
    recs = {}
    for key in ("run2_local", "run2_fast"):
        recs[key], dups = DR.last_per_key(DR.read_jsonl(DE.INPUTS[key][0]))
        print(f"{key}: {len(recs[key])} records; duplicates: {dups}")
    run1, dups1 = DR.last_per_key(DR.read_jsonl(RUN1))
    run1_ab = {k: v for k, v in run1.items() if k[0] in ("A", "B")}
    print(f"run 1: {len(run1)} records (arms A, B, C); duplicates: {dups1}; kept for arms A and B: {len(run1_ab)}")
    pooled_local = {**run1_ab, **recs["run2_local"]}
    if len(pooled_local) != len(run1_ab) + len(recs["run2_local"]):
        raise SystemExit("STOP: run 1 and run 2 local records overlap")
    extra = ((V2.NAME, V2.make_rule(items)), (WITHDRAWN, V1.make_rule(items)))
    result = {"script": "dev_eval2.py", "run_at": args.run_at, "python": sys.version.split()[0], "inputs": inputs,
              "script_sha256": DR.sha256_file(HERE / "dev_eval2.py"), "rules_sha256": DR.sha256_file(HERE / "deciding_rules.py"),
              "markers_sha256": DR.sha256_file(HERE / "outcome_markers.py"), "own_rule_sha256": DR.sha256_file(HERE / "non_settling_rule2.py"),
              "withdrawn_rule_sha256": DR.sha256_file(HERE / "non_settling_rule.py"), "sets": {}}
    for set_name, (pair, flt) in SETS.items():
        key, arms = DE.PAIRS[pair]
        records = pooled_local if pair == "local" else recs[key]
        result["sets"][set_name] = DR.analyse(items, records, arms, extra_rules=extra, id_filter=flt)
        res = result["sets"][set_name]
        print(f"{set_name}: items {res['n_items']}, R2 'shown' {res['r2_shown_items']}, evidence flags {res['evidence_flags_on_r2_shown'] or 'none'}, "
              f"anomalies {res['anomalies'] or 'none'}")
        if args.show:
            print(f"== {set_name} | truth {res['truth_counts']} | arms {res['arms']}")
            print(DE.line("R2 (shown needs both)", res["R2"]))
            for name, e in res["rules"].items():
                r = e["removed"]
                print(DE.line(f"{name} [{e['kind']}]", e["measures"]) + f"  removes {r['total']:>2} (false {r['false']}, true {r['true']})")
    pooled, hosted = result["sets"]["local_pooled_001_300"], result["sets"]["hosted_run2_161_300"]
    candidates = ["SAME-LINE", "OUTCOME-MARKER"]
    gate = DE.own_rule_gate(pooled, hosted, V2.NAME)
    if gate["admitted"]:
        candidates.append(V2.NAME)
    best, step, table = DE.choose_primary(pooled, hosted, candidates)
    result["selection"] = {"primary": best, "rule_applied": step, "candidates": table, "own_rule_gate": {V2.NAME: gate},
                           "basis": "pooled local set, ids 001 to 300 (hosted pair, ids 161 to 300, as tie-break and, for the own rule, validation)"}
    print("selection computed by the pre-registered procedure")
    if args.show:
        print("\nOWN RULE GATE:", gate)
        print("SELECTION:", best, "|", step)
        for c, v in table.items():
            print(f"  {c}: {v}")
    if not args.no_write:
        p = DR.write_new_json(HERE / "dev-results2", result)
        print("written:", p.name)


if __name__ == "__main__":
    main()
