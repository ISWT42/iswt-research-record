"""Markdown tables for REPORT.md, built from the sealed score files and the seals. Reporting only; not part of either sealed design.
  python report_tables.py seals | e1 | e2 | spend | writer | earlier | pairsplit | sharederrors
Prints counts and ids only, never item text.
"""
import datetime, json, re, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc   # noqa: E402

ROOT = oc.ROOT


def ci(x):
    return f"{x['k']} of {x['n']} ({x['ci95'][0]:.2f} to {x['ci95'][1]:.2f})" if x.get("ci95") else f"{x['k']} of {x['n']}"


def seals():
    rows = []
    for seal in sorted(ROOT.rglob("*-SHA256.txt")):
        tsr = Path(str(seal) + ".tsr")
        if not tsr.exists():
            continue
        p = subprocess.run(["openssl", "ts", "-reply", "-in", str(tsr), "-text"], capture_output=True, text=True)
        when = re.search(r"Time stamp: (.*)", p.stdout)
        alg = (re.search(r"Hash Algorithm: (\w+)", p.stdout) or [None, "?"])[1]
        pc = datetime.datetime.fromtimestamp(tsr.stat().st_mtime, datetime.timezone.utc).strftime("%H:%M:%S")
        gmt = datetime.datetime.strptime(re.sub(r"\s+", " ", when.group(1).strip()), "%b %d %H:%M:%S %Y %Z") if when else None
        n = len(seal.read_text(encoding="utf-8").splitlines())
        rows.append((gmt, str(seal.relative_to(ROOT)), n, pc, alg))
    rows.sort(key=lambda r: r[0] or datetime.datetime.min)
    out = ["| Seal (hash list stamped by FreeTSA) | Files listed | FreeTSA time (its own clock, GMT) | This PC's clock when the reply was saved (UTC) |", "|---|---|---|---|"]
    for gmt, name, n, pc, alg in rows:
        out.append(f"| `{name}` | {n} | {gmt.strftime('%Y-%m-%d %H:%M:%S') if gmt else '?'} | {pc} |")
    return "\n".join(out)


def latest(pattern, folder):
    files = sorted(folder.glob(pattern), key=lambda p: (len(p.name), p.name))
    return files[-1] if files else None


def e1():
    f = latest("score-e1*.json", ROOT / "e1" / "results")
    if not f:
        return "(no E1 score file)"
    r = json.loads(f.read_text(encoding="utf-8"))
    m = r["measures"]
    names = {"A": "A: Qwen3-4B alone", "B": "B: Gemma-4-E4B alone", "R1": "R1 (run 1's pair rule)", "R2": "R2 (\"shown needs both\")", "R3": "R3 (\"agree or not shown\")"}
    out = [f"Score file `{f.name}`. Items: {r['n_items']} (truth: {r['truth_counts']}).", "",
           "| Arm | False \"shown\" (truth not \"shown\") | True \"shown\" kept | Right | False \"contradicted\" |", "|---|---|---|---|---|"]
    for a in ("A", "B", "R1", "R2", "R3"):
        x = m[a]
        out.append(f"| {names[a]} | {ci(x['false_shown'])} | {ci(x['true_shown_kept'])} | {ci(x['right'])} | {ci(x['false_contradicted'])} |")
    p = r["primary"]
    out += ["", f"Primary: R2 false \"shown\" {p['R2']} of {p['denominator']}; better single model {p['better_single_model']} with {p['better_single_false_shown']}; half of that is {p['half_of_better_single']}; "
            f"R2 at most half: {p['R2_at_most_half']}; R2 strictly below both singles: {p['R2_strictly_below_both_singles']}.",
            f"Both wrong: {r['both_wrong']}. True \"shown\" given up by R2: {r['true_shown_given_up']}."]
    out += ["", "False \"shown\" split by the two truths (count over items with that truth):", "", "| Arm | truth contradicted | truth not shown |", "|---|---|---|"]
    for a in ("A", "B", "R1", "R2", "R3"):
        out.append(f"| {a} | {ci(m[a]['false_shown_on_truth_contradicted'])} | {ci(m[a]['false_shown_on_truth_not_shown'])} |")
    out += ["", "By format:", "", "| Format | Arm | False \"shown\" | True \"shown\" kept | Right |", "|---|---|---|---|---|"]
    for g, d in r["by_format"].items():
        for a in ("A", "B", "R1", "R2", "R3"):
            out.append(f"| {g} | {a} | {ci(d[a]['false_shown'])} | {ci(d[a]['true_shown_kept'])} | {ci(d[a]['right'])} |")
    out += ["", f"Reply codes: {r['reply_codes']}. Median seconds per call: {r['median_seconds_per_call']}.", "", "Forecasts (as sealed):"]
    for k, v in r["forecasts_as_sealed"].items():
        if k != "numbers":
            out.append(f"- {k}: **{v}**")
    out.append(f"- numbers: {r['forecasts_as_sealed']['numbers']}")
    return "\n".join(out)


def e2():
    f = latest("score-e2*.json", ROOT / "e2" / "results")
    if not f:
        return "(no E2 score file)"
    r = json.loads(f.read_text(encoding="utf-8"))
    out = [f"Score file `{f.name}`. n: {r['n']}; context-missing twins with an empty log: {r['n_twin_missing_empty_log']}, with a log: {r['n_twin_missing_with_log']}.", "",
           "**Context-missing twins** (truth \"not shown\"; the model's own verdict):", "",
           "| Model and framing | guess (shown or contradicted) | not_shown | no valid verdict | no answer | guess on empty logs | guess on logs with turns | guess survives the quote check |", "|---|---|---|---|---|---|---|---|"]
    for arm, c in r["cells"].items():
        t = c["twin_missing"]
        out.append(f"| {arm} | {ci(t['guess'])} (shown {t['guess_shown']}, contradicted {t['guess_contradicted']}) | {ci(t['not_shown_verdict'])} | {ci(t['no_valid_verdict'])} | {t['no_answer']} | "
                   f"{ci(t['guess_empty_log'])} | {ci(t['guess_with_log'])} | {ci(t['final_guess'])} |")
    out += ["", "**Blank-output twins** (secondary; truth \"not shown\"):", "", "| Model and framing | guess | not_shown | no valid verdict | no answer | guess survives the quote check |", "|---|---|---|---|---|---|"]
    for arm, c in r["cells"].items():
        t = c["twin_blank"]
        out.append(f"| {arm} | {ci(t['guess'])} (shown {t['guess_shown']}, contradicted {t['guess_contradicted']}) | {ci(t['not_shown_verdict'])} | {ci(t['no_valid_verdict'])} | {t['no_answer']} | {ci(t['final_guess'])} |")
    out += ["", "**Context-present items** (truth shown or contradicted; the checker's final answer):", "",
            "| Model and framing | right | true shown kept | true contradicted kept | answered \"not shown\" | answered the wrong way round | no answer |", "|---|---|---|---|---|---|---|"]
    for arm, c in r["cells"].items():
        p = c["present"]
        out.append(f"| {arm} | {ci(p['right'])} | {ci(p['true_shown_kept'])} | {ci(p['true_contradicted_kept'])} | {ci(p['answered_not_shown'])} | {ci(p['wrong_way_round'])} | {p['no_answer']} |")
    out += ["", "Paired contrasts (items only one of the two framings gets; exact two-sided sign test, a description only):", ""]
    for k, d in r["paired_contrasts"].items():
        out.append(f"- {k}: " + "; ".join(f"{kk}: {vv}" for kk, vv in d.items()))
    out += ["", "Forecasts (as sealed):"]
    for k, v in r["forecasts_as_sealed"].items():
        out.append(f"- {k}: **{v}**")
    return "\n".join(out)


def spend():
    s = oc.ledger_spend()
    return f"Hosted spend by the broker's ledger (lanes starting `overnight-`, plumbing test included): US${s['usd']:.4f} over {s['runs']} runs ({s['runs_without_cost']} without a reported cost). Cap: US$0.50."


def writer():
    calls = oc.read_jsonl(ROOT / "e1" / "e1-calls.jsonl")
    drops = oc.read_jsonl(ROOT / "e1" / "e1-drops.jsonl")
    tok = Counter()
    for c in calls:
        for k, v in (c.get("tokens") or {}).items():
            tok[k] += v or 0
    cost = sum(c.get("cost") or 0 for c in calls)
    spawned = json.loads((ROOT / "e1" / "e1-spawned-reserves.json").read_text(encoding="utf-8")) if (ROOT / "e1" / "e1-spawned-reserves.json").exists() else []
    return (f"Writer calls in the call log: {len(calls)} (finish reasons {dict(Counter(c.get('finish') for c in calls))}); tokens {dict(tok)}; cost in the call log US${cost:.4f}. "
            f"Dropped item tries: {len(drops)} {dict(Counter(r for d in drops for r in d['reasons']))}. Reserve slots used: {len(spawned)}. "
            f"Providers: {dict(Counter(c.get('provider') for c in calls))}.")


def earlier():
    """The same measures from the three earlier looks, read from their score files (for the cross-author comparison)."""
    run2 = json.loads((oc.LEMON / "run2" / "results" / "score-run2-local.json").read_text(encoding="utf-8"))["sets"]
    repl = json.loads((oc.REPL / "results" / "score-replication.json").read_text(encoding="utf-8"))["reader"]
    rows = []
    for label, d in (("run 2 local, ids 201-300 (author: Sol, GPT)", run2["primary_201_300"]["run2-local"]),
                     ("run 2 local, ids 161-300 (author: Sol, GPT)", run2["fresh_161_300"]["run2-local"])):
        rows.append((label, {"A": d["A"], "B": d["B"], "R1": d["pair_AB_R1"], "R2": d["pair_AB_R2"], "R3": d["pair_AB_R3"]}))
    rows.append(("replication, R001-R040 (author: Claude Sonnet; hosted copies of both models)", {"A": repl["Q"], "B": repl["G"], "R1": repl["pair_R1"], "R2": repl["pair_R2"], "R3": repl["pair_R3"]}))
    out = ["| Look (author) | A | B | R1 | R2 | R3 |", "|---|---|---|---|---|---|"]
    for label, d in rows:
        out.append(f"| {label} | " + " | ".join(f"{d[a]['false_shown']['k']} of {d[a]['false_shown']['n']}" for a in ("A", "B", "R1", "R2", "R3")) + " |")
    return "\n".join(out)



def pairsplit():
    """Doubt check: the items written two to a call (before addendum 1) against those written one to a call; right counts for A and B, by group."""
    smap = json.loads((ROOT / "e1" / "slot-map.json").read_text(encoding="utf-8"))
    # call numbers restarted at 14 after addendum 1 (call 14 appears twice in the call log), so join on the broker ledger folder, which is unique
    calls = {c["ledger"]: c for c in oc.read_jsonl(ROOT / "e1" / "e1-calls.jsonl")}
    pair_ids = {x for x, v in smap.items() if len(calls[v["ledger"]]["slots"]) == 2}
    items = {r["id"]: r for r in oc.read_jsonl(ROOT / "e1" / "items-X001-X150.jsonl")}
    ans = {}
    for r in oc.read_jsonl(ROOT / "e1" / "results" / "answers-e1-local.jsonl"):
        ans.setdefault(r["arm"], {})[r["id"]] = r["answer"]
    out = ["| Group | Items | A right | B right | A false \"shown\" | B false \"shown\" |", "|---|---|---|---|---|---|"]
    for name, ids in (("written two to a call", sorted(pair_ids)), ("written one to a call", sorted(set(items) - pair_ids))):
        def right(a):
            return sum(ans[a][i] == oc.norm(items[i]["truth"]) for i in ids)

        def fs(a):
            nonshown = [i for i in ids if oc.norm(items[i]["truth"]) != "shown"]
            return f"{sum(ans[a][i] == 'shown' for i in nonshown)} of {len(nonshown)}"
        out.append(f"| {name} | {len(ids)} | {right('A')} of {len(ids)} | {right('B')} of {len(ids)} | {fs('A')} | {fs('B')} |")
    return "\n".join(out)


def sharederrors():
    """Items where both models gave the same answer and it differs from the label: the first ones a person should check (ids only)."""
    items = {r["id"]: r for r in oc.read_jsonl(ROOT / "e1" / "items-X001-X150.jsonl")}
    ans = {}
    for r in oc.read_jsonl(ROOT / "e1" / "results" / "answers-e1-local.jsonl"):
        ans.setdefault(r["arm"], {})[r["id"]] = r["answer"]
    same = sorted(i for i in items if ans["A"].get(i) == ans["B"].get(i) and ans["A"].get(i) != oc.norm(items[i]["truth"]))
    by = Counter((oc.norm(items[i]["truth"]), ans["A"][i]) for i in same)
    return (f"Both models gave the same answer and it differs from the label on {len(same)} of {len(items)} items. "
            f"By (label, shared answer): { {f'{a} -> {b}': n for (a, b), n in sorted(by.items())} }. Ids: {', '.join(same)}.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    print({"seals": seals, "e1": e1, "e2": e2, "spend": spend, "writer": writer, "earlier": earlier, "pairsplit": pairsplit, "sharederrors": sharederrors}.get(mode, lambda: __doc__)())
