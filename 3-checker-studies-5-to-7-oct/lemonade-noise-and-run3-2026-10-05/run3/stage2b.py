"""Run 3, stage 2b: does one sentence make a checker use the receipt? Sealed design: STAGE2B-DESIGN.md.
  python stage2b.py run <bank.jsonl> <followups.jsonl>    A and B on stage 2's 62 followed-up pairs, providers pinned
  python stage2b.py score <followups.jsonl>               score into results/ (never overwrites)
Nothing here prints item text: only ids, answers and counts.
"""
import concurrent.futures as cf, copy, dataclasses, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run3 as r3  # noqa: E402
import stage2 as s2  # noqa: E402
r2, rp, v3 = r3.r2, r3.rp, r3.v3
OUT = r3.OUT
PINS = {"U-Q": "qwen/qwen3.5-9b@SiliconFlow", "U-G": "google/gemma-4-26b-a4b-it@Darkbloom"}
RECEIPT_RULE = (" A command run later to check the claim is part of the record: if its OUTPUT settles the claim, "
                "that output decides your verdict.")
CAP_USD = 3.0


def one(variant, arm, item, fu):
    item2 = copy.deepcopy(item)
    item2["turns"] = list(item2["turns"]) + [{"cmd": fu["check_cmd"], "output": fu["check_output"], "narration": ""}]
    turns = rp.turns_for(item2)
    req = v3.build_request(item2["claim"], item2["claim"], "as stated in the claim", list(turns))
    system = req.system + r3.CERTAINTY + (RECEIPT_RULE if variant == "B" else "")
    req = dataclasses.replace(req, system=system)
    model = {"arm": arm, "id": PINS[arm]}
    tries = []
    for _ in range(3):
        text, err, seconds, cost, provider, rel = r2.broker_ask(model, req)
        tries.append({"err": err, "seconds": round(seconds, 2), "cost": cost, "provider": provider, "ledger": rel})
        if not err:
            break
    outcome = v3.Outcome("not shown", err.split(":")[0]) if err else v3.verify(text, turns)
    certainty, _, _ = r3.extras(text) if not err else (None, None, None)
    return {"variant": variant, "arm": arm, "model": PINS[arm], "id": item["id"], "answer": outcome.answer, "code": outcome.code,
            "certainty": certainty, "tries": tries, "request_sha256": hashlib.sha256((req.system + "\n" + req.user).encode()).hexdigest(),
            "reply_sha256": hashlib.sha256((text or "").encode()).hexdigest(), "reply": text, "no_answer": bool(err)}


def run(bank_path, fpath, workers=6):
    items = r2.load(bank_path)
    fu = s2.read_followups(fpath)
    pairs = [(r["arm"], r["id"]) for r in r2.read_jsonl(OUT / "answers-stage2.jsonl")]
    log = OUT / "answers-stage2b.jsonl"
    done = {(r["variant"], r["arm"], r["id"]) for r in r2.read_jsonl(log)} if log.exists() else set()
    jobs = [(v, a, items[i], fu[i]) for v in ("A", "B") for (a, i) in pairs if (v, a, i) not in done]
    print(f"stage 2b: {len(jobs)} calls", flush=True)
    spent = 0.0
    with open(log, "a", encoding="utf-8") as f, cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {}
        queue = iter(jobs)
        for _ in range(workers):
            nxt = next(queue, None)
            if nxt:
                futs[ex.submit(one, *nxt)] = nxt
        while futs:
            fut = next(cf.as_completed(futs))
            futs.pop(fut)
            rec = fut.result()
            spent += sum(t.get("cost") or 0 for t in rec["tries"])
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{rec['variant']} {rec['arm']}] {rec['id']}: {rec['answer']} ({rec['code']}) spent ${spent:.4f}", flush=True)
            if spent < CAP_USD:
                nxt = next(queue, None)
                if nxt:
                    futs[ex.submit(one, *nxt)] = nxt


def score(fpath):
    fu = s2.read_followups(fpath)
    rows = r2.read_jsonl(OUT / "answers-stage2b.jsonl")
    by = {(r["variant"], r["arm"], r["id"]): r for r in rows}
    result = {"design_sha256": (HERE / "STAGE2B-DESIGN-SHA256.txt").read_text(encoding="utf-8").split()[0], "arms": {}}
    for arm in ("U-Q", "U-G"):
        ids = sorted({i for (v, a, i) in by if a == arm})
        def final(v, i):
            r = by.get((v, arm, i))
            return None if r is None else (r["answer"] if r.get("certainty") == "sure" else "not shown")
        both = [i for i in ids if final("A", i) is not None and final("B", i) is not None]
        t = {i: fu[i]["settles_as"] for i in both}
        res = {"n": len(both)}
        for v in ("A", "B"):
            fa = {i: final(v, i) for i in both}
            res[v] = {"right": r2.frac(sum(fa[i] == t[i] for i in both), len(both)),
                      "still_not_shown": sum(fa[i] == "not shown" for i in both),
                      "false_shown": sum(fa[i] == "shown" and t[i] != "shown" for i in both),
                      "false_contradicted": sum(fa[i] == "contradicted" and t[i] != "contradicted" for i in both),
                      "providers": sorted({(by[(v, arm, i)]["tries"][-1]["provider"] or "-") for i in both})}
        res["B_fixed_vs_A"] = sum(final("A", i) != t[i] and final("B", i) == t[i] for i in both)
        res["B_broke_vs_A"] = sum(final("A", i) == t[i] and final("B", i) != t[i] for i in both)
        result["arms"][arm] = res
    target, k = OUT / "score-stage2b.json", 2
    while target.exists():
        target, k = OUT / f"score-stage2b-{k}.json", k + 1
    target.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print("written:", target.name)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "run":
        run(sys.argv[2], sys.argv[3])
    elif mode == "score":
        score(sys.argv[2])
    else:
        print(__doc__)
