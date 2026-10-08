"""Prints the development tables of DESIGN.md (markdown) from dev-results2-v1.json. Reads that file only; ids, labels and counts only.
  python make_design_tables.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
D = json.loads((HERE / "dev-results2-v1.json").read_text(encoding="utf-8"))
OWN, WITHDRAWN = "NON-SETTLING-2", "NON-SETTLING (version 1, withdrawn)"
ORDER = ["SAME-LINE", "OUTCOME-MARKER", OWN, WITHDRAWN, "SAME-LINE-STRICT", "SAME-LINE-CONTAINED", "OUTCOME-MARKER-BOTH",
         "OUTCOME-MARKER-LINE", "SAME-LINE+OUTCOME-MARKER"]
TITLES = {"local_run2_161_300": "Local pair (A Qwen3-4B, B Gemma-4-E4B), ids 161 to 300",
          "hosted_run2_161_300": "Hosted pair (F-Q qwen3.5-9b, F-G gemma-4-26b), ids 161 to 300",
          "local_pooled_001_300": "Local pair, pooled ids 001 to 300 (run 1 for 001 to 160, run 2 for 161 to 300): the set the primary was chosen on",
          "local_run1_001_160": "Local pair, run 1 only, ids 001 to 160",
          "local_run2_201_300": "Local pair, ids 201 to 300", "hosted_run2_201_300": "Hosted pair, ids 201 to 300"}


def frac(f):
    return f"{f['k']}/{f['n']}"


def table(set_name):
    r = D["sets"][set_name]
    out = [f"**{TITLES[set_name]}** ({r['n_items']} items; truth {r['truth_counts']}; R2 says \"shown\" on {r['r2_shown_items']}: "
           f"{r['R2']['shown_by_truth']})", "",
           "| Rule | False \"shown\" (of items whose truth is not shown) | True \"shown\" kept (of items whose truth is shown) | R2 \"shown\" removed | of those false / true |",
           "|---|---|---|---|---|",
           f"| R2 (shown needs both) | {frac(r['R2']['false_shown'])} | {frac(r['R2']['true_shown_kept'])} | - | - |"]
    for name in ORDER:
        e = r["rules"][name]
        label = {OWN: f"**{OWN}** (own; chosen primary)", "SAME-LINE": "SAME-LINE", "OUTCOME-MARKER": "OUTCOME-MARKER"}.get(name, f"{name} (exploratory)")
        out.append(f"| {label} | {frac(e['measures']['false_shown'])} | {frac(e['measures']['true_shown_kept'])} | {e['removed']['total']} | "
                   f"{e['removed']['false']} / {e['removed']['true']} |")
    return "\n".join(out)


def where(set_name, rules):
    r = D["sets"][set_name]
    out = [f"**Where R2's false \"shown\" sit and which rule removes them: {TITLES[set_name]}**", ""]
    removed = {n: {x[0]: x for x in r["rules"][n]["removed"]["items"]} for n in rules}
    out.append("| id | truth | trap | " + " | ".join(rules) + " |")
    out.append("|---|---|---|" + "---|" * len(rules))
    for i, t, tr in r["R2"]["false_shown_ids"]:
        out.append(f"| {i} | {t} | {tr} | " + " | ".join("removed" if i in removed[n] else "-" for n in rules) + " |")
    out.append("")
    for n in rules:
        tr_rows = [x for x in r["rules"][n]["removed"]["items"] if x[1] == "shown"]
        out.append(f"- True \"shown\" removed by {n}: {len(tr_rows)}" + (f" (ids {', '.join(x[0] for x in tr_rows)}; traps {sorted({x[2] for x in tr_rows})})" if tr_rows else ""))
    return "\n".join(out)


if __name__ == "__main__":
    for s in ("local_run2_161_300", "hosted_run2_161_300", "local_pooled_001_300", "local_run1_001_160", "local_run2_201_300", "hosted_run2_201_300"):
        print(table(s))
        print()
    for s in ("local_run2_161_300", "hosted_run2_161_300"):
        print(where(s, ["SAME-LINE", "OUTCOME-MARKER", OWN]))
        print()
    r = D["sets"]["local_pooled_001_300"]
    print("**Pooled local set: false \"shown\" by truth and what the primary removes**")
    print(f"- R2 false \"shown\" {frac(r['R2']['false_shown'])}; R2's {r['r2_shown_items']} \"shown\" answers by truth: {r['R2']['shown_by_truth']}.")
    for n in ("SAME-LINE", "OUTCOME-MARKER", OWN):
        rm = r["rules"][n]["removed"]
        print(f"- {n}: false removed by truth {rm['false_by_truth']}; by reason {r['rules'][n]['reasons']}")
    print("\n**Selection (computed by dev_eval2.py)**")
    sel = D["selection"]
    print(f"- Primary: {sel['primary']}. Rule applied: {sel['rule_applied']}. Own-rule gate: {sel['own_rule_gate']}")
    for c, v in sel["candidates"].items():
        print(f"- {c}: false removed (local pooled) {v['f_local']}, true removed {v['t_local']}, eligible {v['eligible']}, false removed on the hosted pair {v['f_hosted']}, separation {v['separation_local']}")
