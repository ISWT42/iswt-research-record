"""After the primary rule was chosen (dev-results-v1.json), a report-only look at run 1's local answers (arms A, B; ids 001 to 160),
which PREREG-1 declared not to be development data. None of these items was opened before the rules were written. The result
does not change the choice, the bar or any rule. No model calls, no network calls; ids, labels and counts only.
  python postchoice_look.py --run-at "$(date -u +%FT%TZ)"
"""
import argparse
import sys
from pathlib import Path

import deciding_rules as DR
import non_settling_rule as NS

HERE = Path(__file__).resolve().parent
WORK = Path(r"C:\Users\joshd\Workbench")
BANK = WORK / "chatgpt-review-2026-10-04" / "completion-claims-001-300.jsonl"
RUN1 = WORK / "lemonade-entry-2026-10-05" / "results" / "answers-run.jsonl"
WANT = {"bank": (BANK, "edb897f7b6d7df41a14eb37e4f6079ade036dabdec6d140d82dec6147199593a"),
        "run1_answers": (RUN1, "0cf9b3775d9258c7a34d30af35dccabb33248239e06bf8fb73bfbe0c34c482af")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-at", required=True)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    inputs = {}
    for k, (path, want) in WANT.items():
        got = DR.sha256_file(path)
        inputs[k] = {"sha256": got, "matches_expected": got == want}
        if got != want:
            raise SystemExit(f"STOP: {k} differs from the sealed hash")
    items = {}
    for obj in DR.read_jsonl(BANK):
        it = DR.load_item(obj)
        items[it["id"]] = it
    recs, dups = DR.last_per_key(DR.read_jsonl(RUN1))
    res = DR.analyse(items, recs, ("A", "B"), extra_rules=((NS.NAME, NS.make_rule(items)),), id_filter=lambda i: "001" <= i <= "160")
    out = {"script": "postchoice_look.py", "run_at": args.run_at, "python": sys.version.split()[0], "inputs": inputs,
           "duplicates": dups, "note": "report only; run 1 is not development data (PREREG-1)", "result": res}
    print(f"run 1 local pair (A, B), ids 001 to 160 | items {res['n_items']} | truth {res['truth_counts']} | R2 'shown' answers "
          f"{res['r2_shown_items']} (flags: {res['evidence_flags_on_r2_shown'] or 'none'}; anomalies: {res['anomalies'] or 'none'})")

    def line(label, m):
        fs, ts = m["false_shown"], m["true_shown_kept"]
        return f"  {label:<28} false shown {fs['k']:>3}/{fs['n']:<3}  true shown kept {ts['k']:>3}/{ts['n']:<3}  right {m['right']['k']:>3}/{m['right']['n']}"
    print(line("R2 (shown needs both)", res["R2"]))
    for name, e in res["rules"].items():
        r = e["removed"]
        print(line(f"{name} [{e['kind']}]", e["measures"]) + f"  removes {r['total']:>2} (false {r['false']}, true {r['true']})  bar: {e['bar']['verdict']}")
    print("R2 false 'shown' (id, truth, trap):", res["R2"]["false_shown_ids"])
    if not args.no_write:
        p = DR.write_new_json(HERE / "postchoice-run1", out)
        print("written:", p.name)


if __name__ == "__main__":
    main()
