"""E1-apply: R2 and every key-free rule, on an items file and the local pair's answers file; the primary rule against the sealed bar.
Design: DESIGN.md (sealed). No model calls, no network calls. Reads two files, prints and writes ids, labels and counts only
(never claims, log lines or quotes). It refuses to run unless DESIGN-SHA256.txt exists and every file in it still has its sealed hash.

  python e1_apply.py --items <items.jsonl> --answers <answers.jsonl> --run-at "$(date -u +%FT%TZ)"
        [--arms A B] [--id-range LO HI] [--groups-json FILE] [--no-write]

Items: one JSON object per line with id, turns (cmd, output), claim and truth (shown / contradicted / not_shown), optional trap.
Answers: run_pair.py's records (arm, id, answer, code, verdict, quote, reply, ...), one per (arm, item); the last record wins.
An item with no record for an arm counts as "not shown" for that arm (E1-DESIGN.md). --groups-json: a JSON object {id: label}
to split the removals by a label of your own (for example the item format). --unsealed-dev lets the development files be run
before the seal exists, and is refused for any path under overnight-2026-10-05.
"""
import argparse
import json
import sys
from pathlib import Path

import deciding_rules as DR
import non_settling_rule2 as N2

HERE = Path(__file__).resolve().parent
SEAL_NAME = "DESIGN-SHA256.txt"
REQUIRED = ("DESIGN.md", "outcome_markers.py", "deciding_rules.py", "non_settling_rule.py", "non_settling_rule2.py", "e1_apply.py",
            "dev_eval.py", "dev_eval2.py", "dev-results2-v1.json")
PRIMARY = "NON-SETTLING-2"   # the output of the sealed choosing procedure (dev-results2-v1.json, selection.primary); checked below
FORBIDDEN_FOR_UNSEALED = "overnight-2026-10-05"


def line(label, m):
    fs, ts = m["false_shown"], m["true_shown_kept"]
    return f"  {label:<30} false shown {fs['k']:>3}/{fs['n']:<3}  true shown kept {ts['k']:>3}/{ts['n']:<3}  right {m['right']['k']:>3}/{m['right']['n']}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", required=True)
    ap.add_argument("--answers", required=True)
    ap.add_argument("--run-at", required=True, help='pass "$(date -u +%%FT%%TZ)"')
    ap.add_argument("--arms", nargs=2, default=["A", "B"])
    ap.add_argument("--id-range", nargs=2, default=None, metavar=("LO", "HI"))
    ap.add_argument("--groups-json", default=None)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--unsealed-dev", action="store_true", help="skip the seal check (development files only)")
    args = ap.parse_args()

    paths = [Path(args.items).resolve(), Path(args.answers).resolve()]
    if args.unsealed_dev:
        if any(FORBIDDEN_FOR_UNSEALED in str(p) for p in paths):
            raise SystemExit("STOP: --unsealed-dev is refused for files under " + FORBIDDEN_FOR_UNSEALED)
        seal = {"seal_file": None, "note": "unsealed development run"}
        print("UNSEALED DEVELOPMENT RUN (seal check skipped)")
    else:
        seal = DR.check_seal(HERE, SEAL_NAME, REQUIRED)
        print("seal verified: every sealed file has its sealed hash")
    dev = json.loads((HERE / "dev-results2-v1.json").read_text(encoding="utf-8"))
    if dev["selection"]["primary"] != PRIMARY:
        raise SystemExit(f"STOP: PRIMARY ({PRIMARY}) differs from the sealed development selection ({dev['selection']['primary']})")

    items = {}
    for obj in DR.read_jsonl(paths[0]):
        it = DR.load_item(obj)
        items[it["id"]] = it
    rows = DR.read_jsonl(paths[1])
    records, dups = DR.last_per_key(rows)
    groups = json.loads(Path(args.groups_json).read_text(encoding="utf-8")) if args.groups_json else None
    flt = None
    if args.id_range:
        lo, hi = args.id_range
        flt = lambda i: lo <= i <= hi   # noqa: E731  (string comparison; ids are zero-padded)
    arms = tuple(args.arms)
    res = DR.analyse(items, records, arms, extra_rules=((N2.NAME, N2.make_rule(items)),), id_filter=flt, groups=groups)
    primary = res["rules"][PRIMARY]
    bar = primary["bar"]
    out = {"script": "e1_apply.py", "run_at": args.run_at, "python": sys.version.split()[0], "seal": seal,
           "inputs": {"items": {"path_name": paths[0].name, "sha256": DR.sha256_file(paths[0]), "n_items_in_file": len(items)},
                      "answers": {"path_name": paths[1].name, "sha256": DR.sha256_file(paths[1]), "n_records": len(rows), "duplicates": dups}},
           "primary_rule": PRIMARY, "primary_bar": bar, "result": res}

    print(f"items in file {len(items)} | items analysed {res['n_items']} | answer records {len(rows)} (duplicate arm-id: {dups}) | arms {list(arms)}")
    print(f"truth {res['truth_counts']} | traps {res['trap_counts']}")
    print(f"anomalies {res['anomalies'] or 'none'} | evidence flags on R2 'shown' {res['evidence_flags_on_r2_shown'] or 'none'}")
    print(f"\nR2 ('shown needs both') answers 'shown' on {res['r2_shown_items']} items {res['R2']['shown_by_truth']}")
    print(line("R2", res["R2"]))
    for name, e in res["rules"].items():
        r = e["removed"]
        tag = "PRIMARY" if name == PRIMARY else e["kind"]
        print(line(f"{name} [{tag}]", e["measures"]) + f"  removes {r['total']:>2} (false {r['false']}, true {r['true']})")
    print(f"\nPRIMARY RULE {PRIMARY} against the sealed bar:")
    print(f"  R2 false 'shown' F = {bar['r2_false_shown']}; the rule removes {bar['false_removed']} (needs at least {bar['false_removed_needed']}): removal half met = {bar['removal_half_met']}")
    print(f"  R2 true 'shown' T = {bar['r2_true_shown']}; the rule removes {bar['true_removed']} (may remove at most {bar['true_removed_allowed']}): retention met = {bar['retention_met']}")
    print(f"  VERDICT: {bar['verdict']}" + ("  (F is below 4: the bar cannot be tested; no verdict is claimed)" if bar["verdict"] == "THIN" else ""))
    print(f"  removed by the primary (id, truth, trap, reason): {primary['removed']['items']}")
    print("\nCheck before reading further: R2's false 'shown' and true 'shown' counts above must equal R2's counts in E1's own score file.")
    if not args.no_write:
        p = DR.write_new_json(HERE / ("e1-apply" if not args.unsealed_dev else "dev-apply"), out)
        print("written:", p.name)


if __name__ == "__main__":
    main()
