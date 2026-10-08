"""Replication on a second author's items. Sealed design: REPLICATION-DESIGN.md.
  python replicate.py check                  counts-only checks of the two files
  python replicate.py run                    reader, certainty, pair loop (OpenRouter through the AI broker, pinned)
  python replicate.py score                  score into results/ (never overwrites)
Nothing here prints item text.
"""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN3 = Path(r"C:\Users\joshd\Workbench\lemonade-entry-2026-10-05\run3")
sys.path.insert(0, str(RUN3))
import run3 as r3  # noqa: E402
import stage2 as s2  # noqa: E402
import stage2e as s2e  # noqa: E402
r2, rp = r3.r2, r3.rp
ITEMS = HERE / "items-R001-R040.jsonl"
FOLLOW = HERE / "followups-R001-R040.jsonl"
OUT = HERE / "results"
OUT.mkdir(exist_ok=True)
IDS = [f"R{i:03d}" for i in range(1, 41)]
PIN = {"Q": "qwen/qwen3.5-9b@SiliconFlow", "G": "google/gemma-4-26b-a4b-it@Darkbloom"}

# Point the shared modules at this study's files and ids.
r2.OUT = r3.OUT = s2e.OUT = OUT
r2.FRESH = r2.PRIMARY = IDS
r2.FAST = [{"arm": "F-Q", "id": PIN["Q"]}, {"arm": "F-G", "id": PIN["G"]}]
r3.ARMS = [{"arm": "U-Q", "id": PIN["Q"], "run2": "F-Q"}, {"arm": "U-G", "id": PIN["G"], "run2": "F-G"}]
s2e.LEFT_OUT = set()


def items():
    return {r["id"]: r for r in r2.read_jsonl(ITEMS)}


def check():
    it, fu = items(), s2.read_followups(FOLLOW)
    for p in (ITEMS, FOLLOW):
        print(p.name, "sha256", hashlib.sha256(p.read_bytes()).hexdigest())
    print("ids ok:", sorted(it) == IDS and sorted(fu) == IDS)
    from collections import Counter
    print("truth:", dict(Counter(r2.norm(r["truth"]) for r in it.values())), "| trap:", dict(Counter(r.get("trap") for r in it.values())))
    bad = []
    for i, r in it.items():
        if r2.norm(r["truth"]) in ("shown", "contradicted"):
            outs = [ln for t in r["turns"] for ln in str(t.get("output") or "").splitlines()]
            if r["deciding_line"] not in outs:
                bad.append(i)
    print("item deciding line not a whole output line:", bad)
    skip = s2.check(str(FOLLOW), None)
    wb = [i for i in IDS if (r2.norm(it[i]["truth"]) == "shown" and fu[i]["world"] != "done") or (r2.norm(it[i]["truth"]) == "contradicted" and fu[i]["world"] != "not_done")]
    print("world disagrees with truth:", wb)
    return set(bad) | set(wb) | set(skip)


def run():
    skip = check()
    it = items()
    use = [it[i] for i in IDS if i not in skip]
    print("left out:", sorted(skip), "| items used:", len(use), flush=True)
    r2.fast(use, tag="repl-run2")
    r3.run(use, "run3")
    s2e.LEFT_OUT = set(skip)
    s2e.run(str(ITEMS), str(FOLLOW))


def score():
    it, fu = items(), s2.read_followups(FOLLOW)
    truth = {i: r2.norm(it[i]["truth"]) for i in it}
    trap = {i: it[i].get("trap", "-") for i in it}
    a2 = {}
    for r in r2.read_jsonl(OUT / "answers-repl-run2.jsonl"):
        a2.setdefault(r["arm"], {})[r["id"]] = r["answer"]
    ids = [i for i in IDS if i in a2.get("F-Q", {}) and i in a2.get("F-G", {})]
    res = {"design_sha256": (HERE / "REPLICATION-DESIGN-SHA256.txt").read_text(encoding="utf-8").split()[0], "n": len(ids)}
    q, g = a2["F-Q"], a2["F-G"]
    res["reader"] = {"Q": r2.measures(q, truth, trap, ids), "G": r2.measures(g, truth, trap, ids),
                     "pair_R1": r2.measures({i: rp.pair(q[i], g[i]) for i in ids}, truth, trap, ids),
                     "pair_R2": r2.measures({i: r2.rule2(q[i], g[i]) for i in ids}, truth, trap, ids),
                     "pair_R3": r2.measures({i: r2.rule3(q[i], g[i]) for i in ids}, truth, trap, ids)}
    c = {}
    for r in r2.read_jsonl(OUT / "answers-run3.jsonl"):
        c.setdefault(r["arm"], {})[r["id"]] = r
    cert = {}
    for arm in ("U-Q", "U-G"):
        a = c.get(arm, {})
        ids_a = [i for i in ids if i in a]
        sure = [i for i in ids_a if a[i]["certainty"] == "sure"]
        unsure = [i for i in ids_a if a[i]["certainty"] == "unsure"]
        props = [i for i in ids_a if a[i]["settle_cmd"]]
        cert[arm] = {"sure": len(sure), "unsure": len(unsure), "none": len(ids_a) - len(sure) - len(unsure),
                     "wrong_when_sure": r2.frac(sum(a[i]["answer"] != truth[i] for i in sure), len(sure)),
                     "proposals": len(props), "gate_flagged": [i for i in props if r3.UNSAFE.search(a[i]["settle_cmd"])]}
    res["certainty"] = cert
    rows = {r["id"]: r for r in r2.read_jsonl(OUT / "answers-stage2e.jsonl")}
    ids_l = [i for i in ids if i in rows]
    tl = {i: (truth[i] if rows[i]["route"] == "turn1" else fu[i]["settles_as"]) for i in ids_l}
    al = {i: rows[i]["answer"] for i in ids_l}
    res["pair_loop"] = {"n": len(ids_l), "routes": {k: sum(rows[i]["route"] == k for i in ids_l) for k in ("turn1", "loop", "to_person")},
                        "right": r2.frac(sum(al[i] == tl[i] for i in ids_l), len(ids_l)),
                        "false_shown": r2.frac(sum(al[i] == "shown" and tl[i] != "shown" for i in ids_l), sum(tl[i] != "shown" for i in ids_l)),
                        "to_a_person": sum(al[i] == "not shown" for i in ids_l)}
    target, k = OUT / "score-replication.json", 2
    while target.exists():
        target, k = OUT / f"score-replication-{k}.json", k + 1
    target.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("written:", target.name)


if __name__ == "__main__":
    {"check": check, "run": run, "score": score}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: print(__doc__))()
