"""Run 3, stage 2c: a narrow question about the receipt alone. Sealed design: STAGE2C-DESIGN.md.
  python stage2c.py run <bank.jsonl> <followups.jsonl>    C on stage 2's 62 followed-up pairs, providers pinned
  python stage2c.py score <followups.jsonl>               score against stage 2b's A into results/ (never overwrites)
Nothing here prints item text: only ids, answers and counts.
"""
import concurrent.futures as cf, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run3 as r3  # noqa: E402
import stage2 as s2  # noqa: E402
r2, v3 = r3.r2, r3.v3
OUT = r3.OUT
PINS = {"U-Q": "qwen/qwen3.5-9b@SiliconFlow", "U-G": "google/gemma-4-26b-a4b-it@Darkbloom"}
NARROW_SYSTEM = ("You check one claim against the output of one read-only command. Decide whether that OUTPUT shows the claim succeeded "
                 "(shown), shows it failed (contradicted), or shows neither (not_shown). For shown or contradicted, quote one whole line "
                 "copied exactly from the OUTPUT. Reply with JSON only: {\"verdict\": \"shown\" or \"contradicted\" or \"not_shown\", "
                 "\"quote\": \"...\", \"certainty\": \"sure\" or \"unsure\"}.")
CAP_USD = 3.0


def narrow_user(claim, cmd, output):
    return f"CLAIM: {claim}\nCOMMAND: {cmd}\nOUTPUT:\n{output}"


class Req:  # what r2.broker_ask needs: .system and .user
    def __init__(self, system, user):
        self.system, self.user = system, user


def judge(text, output):
    value, problem = v3.parse_reply(text)
    if value is None:
        return "not shown", problem, None
    verdict = v3.normalize_verdict(value.get("verdict"))
    c = value.get("certainty")
    certainty = c.strip().lower() if isinstance(c, str) and c.strip().lower() in ("sure", "unsure") else None
    if verdict is None:
        return "not shown", "invalid_reply", certainty
    if verdict == "not_shown":
        return "not shown", "model_not_shown", certainty
    quote = value.get("quote")
    lines = [ln.strip() for ln in str(output).splitlines()]
    if not isinstance(quote, str) or not quote.strip() or quote.strip() not in lines:
        return "not shown", "unverified_quote", certainty
    return verdict, "verified", certainty


def one(arm, item, fu):
    req = Req(NARROW_SYSTEM, narrow_user(item["claim"], fu["check_cmd"], fu["check_output"]))
    model = {"arm": arm, "id": PINS[arm]}
    tries = []
    for _ in range(3):
        text, err, seconds, cost, provider, rel = r2.broker_ask(model, req)
        tries.append({"err": err, "seconds": round(seconds, 2), "cost": cost, "provider": provider, "ledger": rel})
        if not err:
            break
    answer, code, certainty = ("not shown", err.split(":")[0], None) if err else judge(text, fu["check_output"])
    return {"variant": "C", "arm": arm, "model": PINS[arm], "id": item["id"], "answer": answer, "code": code, "certainty": certainty,
            "tries": tries, "request_sha256": hashlib.sha256((req.system + "\n" + req.user).encode()).hexdigest(),
            "reply_sha256": hashlib.sha256((text or "").encode()).hexdigest() if not err else None, "reply": None if err else text,
            "no_answer": bool(err)}


def run(bank_path, fpath, workers=6):
    items = r2.load(bank_path)
    fu = s2.read_followups(fpath)
    pairs = [(r["arm"], r["id"]) for r in r2.read_jsonl(OUT / "answers-stage2.jsonl")]
    log = OUT / "answers-stage2c.jsonl"
    done = {(r["arm"], r["id"]) for r in r2.read_jsonl(log)} if log.exists() else set()
    jobs = [(a, items[i], fu[i]) for (a, i) in pairs if (a, i) not in done]
    print(f"stage 2c: {len(jobs)} calls", flush=True)
    spent = 0.0
    with open(log, "a", encoding="utf-8") as f, cf.ThreadPoolExecutor(max_workers=workers) as ex:
        futs, queue = {}, iter(jobs)
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
            print(f"[C {rec['arm']}] {rec['id']}: {rec['answer']} ({rec['code']}) spent ${spent:.4f}", flush=True)
            if spent < CAP_USD:
                nxt = next(queue, None)
                if nxt:
                    futs[ex.submit(one, *nxt)] = nxt


def score(fpath):
    fu = s2.read_followups(fpath)
    c = {(r["arm"], r["id"]): r for r in r2.read_jsonl(OUT / "answers-stage2c.jsonl")}
    a = {(r["arm"], r["id"]): r for r in r2.read_jsonl(OUT / "answers-stage2b.jsonl") if r["variant"] == "A"}
    fin = lambda r: None if r is None else (r["answer"] if r.get("certainty") == "sure" else "not shown")
    result = {"design_sha256": (HERE / "STAGE2C-DESIGN-SHA256.txt").read_text(encoding="utf-8").split()[0], "arms": {}}
    for arm in ("U-Q", "U-G"):
        ids = sorted(i for (x, i) in c if x == arm and (arm, i) in a)
        t = {i: fu[i]["settles_as"] for i in ids}
        res = {"n": len(ids)}
        for name, src in (("A_2b", a), ("C", c)):
            fa = {i: fin(src.get((arm, i))) for i in ids}
            res[name] = {"right": r2.frac(sum(fa[i] == t[i] for i in ids), len(ids)),
                         "still_not_shown": sum(fa[i] == "not shown" for i in ids),
                         "false_shown": sum(fa[i] == "shown" and t[i] != "shown" for i in ids),
                         "false_contradicted": sum(fa[i] == "contradicted" and t[i] != "contradicted" for i in ids)}
        res["C_fixed_vs_A"] = sum(fin(a[(arm, i)]) != t[i] and fin(c[(arm, i)]) == t[i] for i in ids)
        res["C_broke_vs_A"] = sum(fin(a[(arm, i)]) == t[i] and fin(c[(arm, i)]) != t[i] for i in ids)
        result["arms"][arm] = res
    target, k = OUT / "score-stage2c.json", 2
    while target.exists():
        target, k = OUT / f"score-stage2c-{k}.json", k + 1
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
