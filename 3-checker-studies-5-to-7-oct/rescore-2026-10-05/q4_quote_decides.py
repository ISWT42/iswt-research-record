"""Q4: when does a quoted line actually decide the claim? (run 2, local and fast lanes)
Design: DESIGN.md (sealed first). Reads existing files only: no model calls, no network.
Prints status lines only (no result figures, so nothing is read before the results are sealed);
the results go to results-q4-vN.json: ids, labels, counts and rates, never item text.
  python q4_quote_decides.py --run-at "$(date -u +%FT%TZ)"
"""
import argparse
import json
from collections import Counter

import rescore_common as C

SCRIPT = "q4_quote_decides.py"
LANES = {
    "local": {"file": "run2_local", "arms": {"A": "Qwen3-4B-Instruct-2507-GGUF", "B": "Gemma-4-E4B-it-GGUF"},
              "stored": "score_run2_local", "stored_lane": "run2-local"},
    "fast": {"file": "run2_fast", "arms": {"F-Q": "qwen/qwen3.5-9b", "F-G": "google/gemma-4-26b-a4b-it"},
             "stored": "score_run2_fast", "stored_lane": "run2-fast"},
}
# Codes that receipts_model.verify() returns after turn.holds_quote(quote) has passed.
V_CODES = ("verified", "shown_citing_failure", "quote_echoes_command", "shown_over_overwritten_failure")
# Codes returned when the verbatim gate itself fails.
GATE_FAIL_CODES = ("unverified_quote", "quote_in_other_turn", "quote_from_command")
ON = ("FULL", "PART", "PLUS")
THIN = 5


def classify(gate, turns, deciding_line):
    """Class of a quote that the record says passed the verbatim check.
    NO_D: the item has no deciding line. Otherwise, if the cited turn holds the deciding line as a whole output line:
    FULL (quote equals it), PART (quote is a proper part of it), PLUS (it is a proper part of the quote); else OTHER."""
    extra = {"text_relation": None, "cited_holds_D": None, "ambiguous_part": False,
             "wrong_turn_text_match": False, "quote_agrees_with_record": None}
    if not gate.get("passed"):
        return "UNRESOLVED", extra
    quote, cited = gate["quote"], gate["turn"]
    if not deciding_line:
        return "NO_D", extra
    lines = cited.out.splitlines()
    holds = deciding_line in lines
    extra["cited_holds_D"] = holds
    if quote == deciding_line:
        rel = "equal"
    elif quote in deciding_line:
        rel = "quote_in_D"
    elif deciding_line in quote:
        rel = "D_in_quote"
    else:
        rel = "none"
    extra["text_relation"] = rel
    if rel != "none" and not holds:
        extra["wrong_turn_text_match"] = True
        return "OTHER", extra
    if rel == "equal":
        return "FULL", extra
    if rel == "quote_in_D":
        extra["ambiguous_part"] = any((quote in ln) and (ln != deciding_line) for ln in lines)
        return "PART", extra
    if rel == "D_in_quote":
        return "PLUS", extra
    return "OTHER", extra


def build_row(rec, item):
    """One answer record joined to its item: labels and booleans only, no text."""
    turns = C.turns_for(item)
    truth = C.norm_truth(item["truth"])
    deciding = item.get("deciding_line") or ""
    gate = C.verbatim_gate(rec.get("reply"), turns)
    in_v = rec["code"] in V_CODES
    row = {"arm": rec["arm"], "id": rec["id"], "trap": item.get("trap", "-"), "truth": truth,
           "answer": rec["answer"], "model_verdict": C.norm_verdict(rec.get("verdict")), "code": rec["code"],
           "in_V": in_v, "derived_gate_pass": bool(gate["passed"])}
    row["answer_match"] = rec["answer"] == truth
    row["verdict_match"] = row["model_verdict"] == truth
    row["cls"] = None
    if in_v:
        cls, extra = classify(gate, turns, deciding)
        if gate.get("passed"):
            extra["quote_agrees_with_record"] = (gate["quote"] == (rec.get("quote") or "").strip())
        row["cls"] = cls
        row.update(extra)
    return row


def groups_of(pop):
    return {"ON": [r for r in pop if r["cls"] in ON],
            "FULL": [r for r in pop if r["cls"] == "FULL"],
            "PART": [r for r in pop if r["cls"] == "PART"],
            "PLUS": [r for r in pop if r["cls"] == "PLUS"],
            "OTHER": [r for r in pop if r["cls"] == "OTHER"],
            "NO_D": [r for r in pop if r["cls"] == "NO_D"],
            "NOT_ON": [r for r in pop if r["cls"] in ("OTHER", "NO_D")]}


def rate(rs, key):
    return C.frac(sum(1 for r in rs if r[key]), len(rs))


def summarise(rows, population="V"):
    """population 'V' = quote passes the verbatim check; 'verified' = code verified only (nested)."""
    pop = [r for r in rows if r["in_V"] and (population == "V" or r["code"] == "verified")]
    g = groups_of(pop)
    n_pop = len(pop)
    am = {k: rate(v, "answer_match") for k, v in g.items()}
    vm = {k: rate(v, "verdict_match") for k, v in g.items()}

    def group_name(r):
        return "ON" if r["cls"] in ON else r["cls"]

    wrong_with_real_quote = {}
    for fa in ("shown", "contradicted"):
        fin = [r for r in pop if r["answer"] == fa]
        wrong = [r for r in fin if not r["answer_match"]]
        wrong_with_real_quote[fa] = {"final_answers": len(fin), "wrong": C.frac(len(wrong), len(fin)),
                                     "wrong_by_group": dict(sorted(Counter(group_name(r) for r in wrong).items()))}
    return {
        "population": population,
        "n_answers": len(rows),
        "codes": dict(sorted(Counter(r["code"] for r in rows).items())),
        "n_pop": n_pop,
        "thin": n_pop < THIN,
        "classes": dict(sorted(Counter(r["cls"] for r in pop).items())),
        "shares": {
            "on_of_pop": C.frac(len(g["ON"]), n_pop),
            "other_of_pop_on_items_with_deciding_line": C.frac(len(g["OTHER"]), len(g["ON"]) + len(g["OTHER"])),
            "no_d_of_pop": C.frac(len(g["NO_D"]), n_pop),
            "not_on_of_pop": C.frac(len(g["NOT_ON"]), n_pop),
        },
        "answer_match": am,
        "model_verdict_match": vm,
        "contrast_on_minus_other": {"answer_match": C.diff_of(am["ON"], am["OTHER"]),
                                    "model_verdict_match": C.diff_of(vm["ON"], vm["OTHER"])},
        "contrast_on_minus_not_on": {"answer_match": C.diff_of(am["ON"], am["NOT_ON"]),
                                     "model_verdict_match": C.diff_of(vm["ON"], vm["NOT_ON"])},
        "answer_truth_matrix": {k: dict(sorted(Counter(f"{r['answer']}|{r['truth']}" for r in g[k]).items()))
                                for k in ("ON", "OTHER", "NO_D")},
        "wrong_with_real_quote": wrong_with_real_quote,
        "ambiguous_part": sum(1 for r in g["PART"] if r.get("ambiguous_part")),
        "wrong_turn_text_match": sum(1 for r in pop if r.get("wrong_turn_text_match")),
    }


def stratum(rows, traps):
    return {"all": summarise(rows, "V"),
            "all_verified_code_only": summarise(rows, "verified"),
            "by_trap": {tr: summarise([r for r in rows if r["trap"] == tr], "V") for tr in traps}}


def crosscheck(rows_all):
    """Compare the recorded code with a fresh derivation of the verbatim gate. Report only."""
    tally, disc = Counter(), []
    for r in rows_all:
        tally[f"recorded_in_V={r['in_V']}|derived_gate_pass={r['derived_gate_pass']}"] += 1
        kind = None
        if r["in_V"] and not r["derived_gate_pass"]:
            kind = "recorded_in_V_but_gate_not_derived"
        elif (not r["in_V"]) and r["code"] in GATE_FAIL_CODES and r["derived_gate_pass"]:
            kind = "recorded_gate_failure_but_derived_pass"
        elif (not r["in_V"]) and r["derived_gate_pass"] and r["code"] not in GATE_FAIL_CODES:
            kind = "other_code_but_derived_pass"
        elif r["in_V"] and r["derived_gate_pass"] and r.get("quote_agrees_with_record") is False:
            kind = "derived_quote_differs_from_record"
        if kind:
            disc.append({"lane": r["lane"], "arm": r["arm"], "id": r["id"], "code": r["code"], "kind": kind})
    return {"tally": dict(sorted(tally.items())), "discrepancies": len(disc), "discrepancy_list": disc}


def check_bank(items):
    batch5 = {it["id"]: it for it in C.read_jsonl(C.PATHS["batch5"])}
    fresh = [items[i] for i in C.FRESH]
    primary = [items[i] for i in C.PRIMARY]
    holders = Counter()
    for it in fresh:
        d = it.get("deciding_line") or ""
        if d:
            holders[sum(1 for t in C.turns_for(it) if d in t.out.splitlines())] += 1
    return {"batch5_items": len(batch5),
            "batch5_equal_to_bank": all(items.get(i) == b for i, b in batch5.items()),
            "deciding_line_empty_iff_truth_not_shown": all(
                (not (it.get("deciding_line") or "")) == (C.norm_truth(it["truth"]) == "not shown") for it in fresh),
            "turns_holding_deciding_line_as_whole_line": dict(sorted(holders.items())),
            "truth_counts_fresh": dict(sorted(Counter(C.norm_truth(it["truth"]) for it in fresh).items())),
            "truth_counts_primary": dict(sorted(Counter(C.norm_truth(it["truth"]) for it in primary).items())),
            "trap_counts_fresh": dict(sorted(Counter(it.get("trap", "-") for it in fresh).items())),
            "trap_counts_primary": dict(sorted(Counter(it.get("trap", "-") for it in primary).items()))}


def reconcile(rows_all, stored_by_lane):
    """Recompute right / false 'shown' / answer mix per arm and compare with the stored run 2 scores. Report only."""
    out, agree, total = {}, 0, 0
    for set_name, ids in C.SETS.items():
        idset = set(ids)
        for lane, cfg in LANES.items():
            for arm in cfg["arms"]:
                rs = [r for r in rows_all if r["lane"] == lane and r["arm"] == arm and r["id"] in idset]
                key = f"{set_name}|{lane}|{arm}"
                st = C.get(stored_by_lane.get(lane), "sets", set_name, cfg["stored_lane"], arm)
                if st is None:
                    out[key] = {"note": "arm not found in the stored score"}
                    continue
                try:
                    other = [r for r in rs if r["truth"] != "shown"]
                    chk = {
                        "right": C.compare([sum(r["answer_match"] for r in rs), len(rs)], [st["right"]["k"], st["right"]["n"]]),
                        "false_shown": C.compare([sum(1 for r in other if r["answer"] == "shown"), len(other)],
                                                 [st["false_shown"]["k"], st["false_shown"]["n"]]),
                        "answer_mix": C.compare(dict(sorted(Counter(r["answer"] for r in rs).items())), dict(sorted(st["answers"].items()))),
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
    bank_checks = check_bank(items)
    traps = sorted({items[i].get("trap", "-") for i in C.FRESH})
    rows_all, file_info = [], {}
    for lane, cfg in LANES.items():
        raw = C.read_jsonl(C.PATHS[cfg["file"]])
        by, dups = C.last_per_key(raw)
        missing = []
        for arm in cfg["arms"]:
            for i in C.FRESH:
                rec = by.get((arm, i))
                if rec is None:
                    missing.append(f"{arm}:{i}")
                    continue
                row = build_row(rec, items[i])
                row["lane"] = lane
                rows_all.append(row)
        file_info[lane] = {"records": len(raw), "duplicate_arm_id": dups, "arms_found": sorted({a for a, _ in by}),
                           "missing_arm_id": missing}
        print(f"{lane}: {len(raw)} records read; duplicates: {dups}; missing: {len(missing)}")
    print(f"answer rows built: {len(rows_all)}")
    cross = crosscheck(rows_all)
    print(f"verbatim-gate cross-check: {cross['discrepancies']} disagreements with the recorded codes")
    result = {"meta": C.meta(SCRIPT, args.run_at, seal, inputs), "question": "Q4",
              "checks": {"files": file_info, "bank": bank_checks, "gate_crosscheck": cross},
              "traps": traps, "sets": {}}
    for set_name, ids in C.SETS.items():
        idset = set(ids)
        result["sets"][set_name] = {}
        for lane, cfg in LANES.items():
            lane_rows = [r for r in rows_all if r["lane"] == lane and r["id"] in idset]
            result["sets"][set_name][lane] = {
                "pooled": stratum(lane_rows, traps),
                "arms": {arm: stratum([r for r in lane_rows if r["arm"] == arm], traps) for arm in cfg["arms"]}}
    stored = {}
    for lane, cfg in LANES.items():
        try:
            stored[lane] = json.loads(C.PATHS[cfg["stored"]].read_text(encoding="utf-8"))
        except Exception as e:  # report-only step
            stored[lane] = None
            print(f"stored score for {lane} not read: {type(e).__name__}")
    result["reconciliation_with_stored_run2_scores"] = reconcile(rows_all, stored)
    result["rows"] = rows_all
    path = C.write_new_json("results-q4", result)
    print("written:", path.name)
    tally = result["reconciliation_with_stored_run2_scores"]["tally"]
    print(f"reconciliation with the stored run 2 scores: {tally['checks']} figures compared, {tally['agree']} agree")


if __name__ == "__main__":
    main()
