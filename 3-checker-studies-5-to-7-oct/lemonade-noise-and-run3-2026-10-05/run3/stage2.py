"""Run 3, stage 2: get the receipt, safely, then judge again. Sealed design: STAGE2-DESIGN.md.
  python stage2.py check <followups.jsonl>             counts-only checks of Sol's follow-up file
  python stage2.py run <bank.jsonl> <followups.jsonl>    the loop for both arms (OpenRouter through the AI broker)
  python stage2.py score <bank.jsonl> <followups.jsonl>  score into results/ (never overwrites a score file)
Nothing here prints item text: only ids, answers and counts.
"""
import concurrent.futures as cf, copy, dataclasses, hashlib, json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run3 as r3  # noqa: E402  ARMS, CERTAINTY, UNSAFE, extras; r3.r2 is run 2's module
r2, rp, v3 = r3.r2, r3.rp, r3.v3
OUT = r3.OUT
CAP_USD = 3.0


def read_followups(p):
    return {r["id"]: r for r in r2.read_jsonl(p)}


def check(fpath, bank_path=None):
    raw = Path(fpath).read_bytes()
    fu = read_followups(fpath)
    print("file sha256:", hashlib.sha256(raw).hexdigest(), "| bytes:", len(raw), "| rows:", len(fu))
    print("ids 161-300 exactly:", sorted(fu) == r2.FRESH, "| missing:", [i for i in r2.FRESH if i not in fu][:10])
    need = {"id", "world", "check_cmd", "check_output", "settles_as", "deciding_line"}
    print("rows missing a field:", [i for i, r in fu.items() if not need <= set(r)][:10])
    if bank_path:
        items = r2.load(bank_path)
        bad_world = [i for i, r in fu.items() if i in items and ((r2.norm(items[i]["truth"]) == "shown" and r.get("world") != "done") or (r2.norm(items[i]["truth"]) == "contradicted" and r.get("world") != "not_done"))]
        ns = [i for i in fu if i in items and r2.norm(items[i]["truth"]) == "not shown"]
        print("world disagrees with truth (shown/contradicted items):", len(bad_world), bad_world[:10])
        print("not_shown items by world:", dict(Counter(fu[i].get("world") for i in ns)))
    bad_settle = [i for i, r in fu.items() if (r.get("world") == "done") != (r.get("settles_as") == "shown") or r.get("settles_as") not in ("shown", "contradicted")]
    bad_line = [i for i, r in fu.items() if r.get("deciding_line") not in str(r.get("check_output") or "").splitlines()]
    unsafe = [i for i, r in fu.items() if r3.UNSAFE.search(str(r.get("check_cmd") or ""))]
    print("settles_as disagrees with world:", len(bad_settle), bad_settle[:10], "| deciding line not a whole output line:", len(bad_line), bad_line[:10],
          "| check_cmd not read-only:", len(unsafe), unsafe[:10])
    return set(bad_settle) | set(bad_line) | set(unsafe) | ({i for i in fu if not need <= set(fu[i])})


def plan(arm, rec):
    """Turn 1 under policy U, then the gate."""
    pol = rec["answer"] if rec.get("certainty") == "sure" else "not shown"
    if pol != "not shown":
        return "turn1", pol
    cmd = rec.get("settle_cmd")
    if not cmd:
        return "no_proposal", "not shown"
    if r3.UNSAFE.search(cmd):
        return "refused", "not shown"
    return "follow_up", None


def one(model, item, fu):
    item2 = copy.deepcopy(item)
    item2["turns"] = list(item2["turns"]) + [{"cmd": fu["check_cmd"], "output": fu["check_output"], "narration": ""}]
    turns = rp.turns_for(item2)
    req = v3.build_request(item2["claim"], item2["claim"], "as stated in the claim", list(turns))
    req = dataclasses.replace(req, system=req.system + r3.CERTAINTY)
    tries = []
    for _ in range(3):
        text, err, seconds, cost, provider, rel = r2.broker_ask(model, req)
        tries.append({"err": err, "seconds": round(seconds, 2), "cost": cost, "provider": provider, "ledger": rel})
        if not err:
            break
    outcome = v3.Outcome("not shown", err.split(":")[0]) if err else v3.verify(text, turns)
    certainty, cmd, expect = r3.extras(text) if not err else (None, None, None)
    return {"arm": model["arm"], "model": model["id"], "id": item["id"], "answer2": outcome.answer, "code2": outcome.code,
            "certainty2": certainty, "tries": tries, "request_sha256": hashlib.sha256((req.system + "\n" + req.user).encode()).hexdigest(),
            "reply_sha256": hashlib.sha256((text or "").encode()).hexdigest(), "reply": text, "no_answer": bool(err)}


def run(bank_path, fpath, workers=6):
    items = r2.load(bank_path)
    fu = read_followups(fpath)
    skip = check(fpath, bank_path)
    turn1 = {(r["arm"], r["id"]): r for r in r2.read_jsonl(OUT / "answers-run3.jsonl")}
    log = OUT / "answers-stage2.jsonl"
    done = {(r["arm"], r["id"]) for r in r2.read_jsonl(log)} if log.exists() else set()
    jobs = []
    for m in r3.ARMS:
        for i in r2.FRESH:
            rec = turn1.get((m["arm"], i))
            if rec is None or i in skip or i not in fu:
                continue
            route, _ = plan(m["arm"], rec)
            if route == "follow_up" and (m["arm"], i) not in done:
                jobs.append((m, items[i], fu[i]))
    print(f"stage 2: {len(jobs)} follow-up calls", flush=True)
    spent, stop = 0.0, False
    with open(log, "a", encoding="utf-8") as f, cf.ThreadPoolExecutor(max_workers=workers) as ex:
        pending, queue = {}, iter(jobs)
        for _ in range(workers):
            nxt = next(queue, None)
            if nxt:
                pending[ex.submit(one, *nxt)] = nxt
        while pending:
            fut = next(cf.as_completed(pending))
            m, it, _ = pending.pop(fut)
            rec = fut.result()
            spent += sum(t.get("cost") or 0 for t in rec["tries"])
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{m['arm']}] {it['id']}: {rec['answer2']} ({rec['code2']}, {rec['certainty2']}) spent ${spent:.4f}", flush=True)
            if spent >= CAP_USD:
                stop = True
            if not stop:
                nxt = next(queue, None)
                if nxt:
                    pending[ex.submit(one, *nxt)] = nxt


def score(bank_path, fpath):
    items = r2.load(bank_path)
    fu = read_followups(fpath)
    skip = check(fpath, bank_path)
    truth1 = {i: r2.norm(it["truth"]) for i, it in items.items()}
    turn1 = {(r["arm"], r["id"]): r for r in r2.read_jsonl(OUT / "answers-run3.jsonl")}
    t2 = {(r["arm"], r["id"]): r for r in r2.read_jsonl(OUT / "answers-stage2.jsonl")}
    result = {"design_sha256": (HERE / "STAGE2-DESIGN-SHA256.txt").read_text(encoding="utf-8").split()[0],
              "followups_sha256": hashlib.sha256(Path(fpath).read_bytes()).hexdigest(), "left_out": sorted(skip), "sets": {}}
    for set_name, ids in (("primary_201_300", r2.PRIMARY), ("fresh_161_300", r2.FRESH)):
        out, finals = {}, {}
        for m in r3.ARMS:
            routes, final, truth = Counter(), {}, {}
            fol = []
            for i in ids:
                rec = turn1.get((m["arm"], i))
                if rec is None or i in skip:
                    continue
                route, ans = plan(m["arm"], rec)
                routes[route] += 1
                if route == "follow_up":
                    r = t2.get((m["arm"], i))
                    if r is None:
                        routes["follow_up_missing"] += 1
                        continue
                    a2 = r["answer2"] if r.get("certainty2") == "sure" else "not shown"
                    final[i], truth[i] = a2, fu[i]["settles_as"]
                    fol.append((i, r, a2))
                else:
                    final[i], truth[i] = ans, truth1[i]
            n = len(fol)
            out[m["arm"]] = {
                "routes": dict(routes),
                "followed_up": {"n": n,
                                "right": r2.frac(sum(a2 == fu[i]["settles_as"] for i, _, a2 in fol), n),
                                "right_raw_turn2": r2.frac(sum(r["answer2"] == fu[i]["settles_as"] for i, r, _ in fol), n),
                                "sure": r2.frac(sum(r.get("certainty2") == "sure" for _, r, _ in fol), n),
                                "false_shown": sum(a2 == "shown" and fu[i]["settles_as"] != "shown" for i, _, a2 in fol),
                                "still_not_shown": sum(a2 == "not shown" for _, _, a2 in fol)},
                "system": {"right": r2.frac(sum(final[i] == truth[i] for i in final), len(final)),
                           "false_shown": r2.frac(sum(final[i] == "shown" and truth[i] != "shown" for i in final), sum(truth[i] != "shown" for i in final)),
                           "to_a_person": sum(final[i] == "not shown" for i in final),
                           "run3_policy_U_not_shown": sum(1 for i in ids if (m["arm"], i) in turn1 and i not in skip and plan(m["arm"], turn1[(m["arm"], i)])[0] != "turn1")},
            }
            finals[m["arm"]] = (final, truth)
        (fx, tx), (fy, ty) = finals[r3.ARMS[0]["arm"]], finals[r3.ARMS[1]["arm"]]
        common = [i for i in fx if i in fy]
        pair = {i: r2.rule3(fx[i], fy[i]) for i in common}
        # The system's truth after the loop: once either arm fetched the receipt, the record holds it (settles_as); else the bank's truth.
        tp = {i: (fu[i]["settles_as"] if (tx[i] != truth1[i] or ty[i] != truth1[i] or
                                          any(t2.get((m["arm"], i)) for m in r3.ARMS)) and i in fu else truth1[i]) for i in common}
        out["pair_final_R3"] = {"n": len(common),
                                "right": r2.frac(sum(pair[i] == tp[i] for i in common), len(common)),
                                "false_shown": r2.frac(sum(pair[i] == "shown" and tp[i] != "shown" for i in common), sum(tp[i] != "shown" for i in common)),
                                "to_a_person": sum(pair[i] == "not shown" for i in common),
                                "answers": dict(Counter(pair.values()))}
        result["sets"][set_name] = out
    target, k = OUT / "score-stage2.json", 2
    while target.exists():
        target, k = OUT / f"score-stage2-{k}.json", k + 1
    target.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print("written:", target.name)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "check":
        check(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif mode == "run":
        run(sys.argv[2], sys.argv[3])
    elif mode == "score":
        score(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
