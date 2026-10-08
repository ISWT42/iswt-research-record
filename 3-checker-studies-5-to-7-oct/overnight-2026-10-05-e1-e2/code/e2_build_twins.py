"""E2: build the context-present items and their two kinds of twin, by script, from the replication's 40 items (R001-R040).
  present      an R item whose truth is shown or contradicted (27 of 40), unchanged
  twin_missing the present item with its deciding turn removed (id "R003-M"); truth becomes not_shown
  twin_blank   the present item with its deciding turn's OUTPUT blanked, command kept (id "R003-O"); truth becomes not_shown
The deciding turn is every turn whose output holds the deciding line as a whole line. A reviewer's note (twin-review.json, written before
any model sees a twin) may add turns that still settle the claim without it; those are removed, or blanked, too.
  python e2_build_twins.py build [--review FILE] [--out FILE]     writes twins-R001-R040.jsonl (never overwrites)
Every twin is checked: its deciding line must be absent. Prints counts and ids only.
"""
import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc  # noqa: E402

E2 = oc.ROOT / "e2"
SRC = oc.REPL / "items-R001-R040.jsonl"


def lines(turn):
    return str(turn.get("output") or "").splitlines()


def source_ok():
    for line in (oc.REPL / "ITEMS-SHA256.txt").read_text(encoding="utf-8").splitlines():
        h, _, f = line.partition(" *")
        if f.strip() == "items-R001-R040.jsonl":
            return h == oc.sha256_file(SRC), h
    return False, None


def build(review_path, out_path):
    sealed, why = oc.design_seal_ok("E2")
    if not sealed:
        sys.exit(f"STOP: {why}")          # no twin is built before the design is sealed
    ok, h = source_ok()
    if not ok:
        sys.exit("STOP: items-R001-R040.jsonl does not match the hash the replication sealed")
    print("source items sha256 matches the replication's seal:", h)
    items = oc.read_jsonl(SRC)
    present = [r for r in items if oc.norm(r["truth"]) in ("shown", "contradicted")]
    print("items:", len(items), "| present (shown or contradicted):", len(present), "| truth:", dict(Counter(oc.norm(r["truth"]) for r in present)))
    review = json.loads(Path(review_path).read_text(encoding="utf-8")) if Path(review_path).exists() else None
    if review is None:
        sys.exit(f"STOP: no review file at {review_path}; the multi-turn items must be reviewed first")
    rows, dropped, problems = [], [], []
    for r in present:
        turns = r["turns"]
        decide = [k for k, t in enumerate(turns) if r["deciding_line"] in lines(t)]
        rv = review.get(r["id"])
        if len(turns) > 1 and rv is None:
            sys.exit(f"STOP: multi-turn item {r['id']} has no entry in the review file")
        rv = rv or {"decision": "keep", "also_remove": []}
        if rv["decision"] == "drop":
            dropped.append(r["id"])
            continue
        extra = [k - 1 for k in rv.get("also_remove", [])]
        removed = sorted(set(decide) | set(extra))
        if not decide:
            problems.append(f"{r['id']}: deciding line is in no turn")
            continue
        base = {"claim": r["claim"], "trap": r["trap"], "source": r["id"], "n_turns_original": len(turns), "removed_turns": [k + 1 for k in removed],
                "review": rv["decision"], "review_code": rv.get("code", "single_turn" if len(turns) == 1 else None)}
        rows.append({"id": r["id"], "turns": turns, "truth": r["truth"], "deciding_line": r["deciding_line"], "kind": "present", **base})
        a_turns = [t for k, t in enumerate(turns) if k not in removed]
        rows.append({"id": r["id"] + "-M", "turns": a_turns, "truth": "not_shown", "deciding_line": "", "kind": "twin_missing",
                     "empty_log": len(a_turns) == 0, "n_turns_left": len(a_turns), **base})
        b_turns = [dict(t, output="") if k in removed else t for k, t in enumerate(turns)]
        rows.append({"id": r["id"] + "-O", "turns": b_turns, "truth": "not_shown", "deciding_line": "", "kind": "twin_blank",
                     "empty_log": False, "n_turns_left": len(b_turns), **base})
    # checks: the deciding line must be absent from every twin
    by_id = {r["id"]: r for r in present}
    for row in rows:
        if row["kind"] == "present":
            continue
        dl = by_id[row["source"]]["deciding_line"]
        outs = [str(t.get("output") or "") for t in row["turns"]]
        if any(dl in o for o in outs):
            problems.append(f"{row['id']}: deciding line still in an output")
        if any(dl in o for o in [str(t.get("cmd") or "") for t in row["turns"]]):
            problems.append(f"{row['id']}: deciding line appears in a command (reported)")
        if row["kind"] == "twin_missing" and len(row["turns"]) != row["n_turns_original"] - len(row["removed_turns"]):
            problems.append(f"{row['id']}: wrong turn count")
        if row["kind"] == "twin_blank" and (len(row["turns"]) != row["n_turns_original"] or any(row["turns"][k - 1]["output"] != "" for k in row["removed_turns"])):
            problems.append(f"{row['id']}: blank twin wrong")
        if oc.norm(row["truth"]) != "not shown" or row["deciding_line"] != "" or row["claim"] != by_id[row["source"]]["claim"]:
            problems.append(f"{row['id']}: truth, deciding line or claim wrong")
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids")
    kinds = Counter(r["kind"] for r in rows)
    print("rows:", dict(kinds), "| dropped by review:", dropped)
    print("twin_missing with an empty log:", sum(1 for r in rows if r["kind"] == "twin_missing" and r["empty_log"]),
          "| with at least one turn left:", sum(1 for r in rows if r["kind"] == "twin_missing" and not r["empty_log"]))
    print("review decisions:", dict(Counter(r["review"] for r in rows if r["kind"] == "present")))
    print("problems:", problems)
    hard = [p for p in problems if "(reported)" not in p]
    if hard:
        sys.exit("STOP: problems found; nothing written")
    out = Path(out_path)
    if out.exists():
        sys.exit(f"{out} exists; not overwriting")
    oc.write_jsonl(out, rows)
    print("written:", out, "| sha256", oc.sha256_file(out))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "build":
        rv = args[args.index("--review") + 1] if "--review" in args else str(E2 / "twin-review.json")
        ot = args[args.index("--out") + 1] if "--out" in args else str(E2 / "twins-R001-R040.jsonl")
        build(rv, ot)
    else:
        print(__doc__)
