"""Run 3, stage 2e: the pair loop. Agreement for confident answers, the safe loop for the rest. Sealed design: STAGE2E-DESIGN.md.
  python stage2e.py run <bank.jsonl> <followups.jsonl>
  python stage2e.py score <bank.jsonl> <followups.jsonl>
Nothing here prints item text: only ids, answers and counts.
"""
import concurrent.futures as cf, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run3 as r3  # noqa: E402
import stage2 as s2  # noqa: E402
import stage2c as s2c  # noqa: E402
import stage2d as s2d  # noqa: E402
r2, rp, v3 = r3.r2, r3.rp, r3.v3
OUT = r3.OUT
PINS = s2c.PINS
LEFT_OUT = {"183", "278", "289"}


def final1(r):
    return r["answer"] if r.get("certainty") == "sure" else "not shown"


def turn1_final(q, g):
    if q.get("certainty") == "sure" and g.get("certainty") == "sure" and q["answer"] == g["answer"] and q["answer"] != "not shown":
        return q["answer"]
    return None


def narrow(arm, item, f):
    text, err, tries = s2d.call(arm, s2c.Req(s2c.NARROW_SYSTEM, s2c.narrow_user(item["claim"], f["check_cmd"], f["check_output"])))
    answer, code, certainty = ("not shown", err.split(":")[0], None) if err else s2c.judge(text, f["check_output"])
    return {"answer": answer if certainty == "sure" else "not shown", "raw": answer, "code": code, "certainty": certainty,
            "reply": text, "tries": tries}


def one(item, f, q, g):
    rec = {"id": item["id"]}
    proposal, source = None, None
    for arm, r in (("U-Q", q), ("U-G", g)):
        cmd = r.get("settle_cmd")
        if cmd and not r3.UNSAFE.search(cmd):
            proposal, source = cmd, f"run3:{arm}"
            break
    elicits = []
    if not proposal:
        turns = rp.turns_for(item)
        record_user = v3.build_request(item["claim"], item["claim"], "as stated in the claim", list(turns)).user
        for arm in ("U-Q", "U-G"):
            text, err, tries = s2d.call(arm, s2c.Req(s2d.ELICIT_SYSTEM, record_user))
            value, _ = v3.parse_reply(text) if not err else (None, None)
            cmd = value.get("cmd") if isinstance(value, dict) and isinstance(value.get("cmd"), str) and value.get("cmd").strip() else None
            elicits.append({"arm": arm, "proposal": cmd, "reply": text, "tries": tries})
            if cmd and not r3.UNSAFE.search(cmd):
                proposal, source = cmd, f"elicit:{arm}"
                break
    rec.update(proposal=proposal, proposal_source=source, elicits=elicits)
    if not proposal:
        rec.update(route="to_person", answer="not shown")
        return rec
    jq, jg = narrow("U-Q", item, f), narrow("U-G", item, f)
    rec.update(route="loop", judge_q=jq, judge_g=jg, answer=r2.rule3(jq["answer"], jg["answer"]))
    return rec


def run(bank_path, fpath, workers=6):
    items = r2.load(bank_path)
    fu = s2.read_followups(fpath)
    t1 = {(r["arm"], r["id"]): r for r in r2.read_jsonl(OUT / "answers-run3.jsonl")}
    log = OUT / "answers-stage2e.jsonl"
    done = {r["id"] for r in r2.read_jsonl(log)} if log.exists() else set()
    jobs = []
    with open(log, "a", encoding="utf-8") as f:
        for i in r2.FRESH:
            if i in LEFT_OUT or i in done:
                continue
            q, g = t1[("U-Q", i)], t1[("U-G", i)]
            a = turn1_final(q, g)
            if a is not None:
                f.write(json.dumps({"id": i, "route": "turn1", "answer": a}) + "\n")
            else:
                jobs.append((items[i], fu[i], q, g))
        f.flush()
        print(f"stage 2e: {len(jobs)} items to the loop", flush=True)
        with cf.ThreadPoolExecutor(max_workers=workers) as ex:
            for rec in ex.map(lambda j: one(*j), jobs):
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                print(f"{rec['id']}: {rec['route']} -> {rec['answer']}", flush=True)


def score(bank_path, fpath):
    items = r2.load(bank_path)
    fu = s2.read_followups(fpath)
    rows = {r["id"]: r for r in r2.read_jsonl(OUT / "answers-stage2e.jsonl")}
    result = {"design_sha256": (HERE / "STAGE2E-DESIGN-SHA256.txt").read_text(encoding="utf-8").split()[0], "sets": {}}
    for set_name, ids in (("primary_201_300", r2.PRIMARY), ("fresh_161_300", r2.FRESH)):
        ids_ = [i for i in ids if i in rows]
        truth = {i: (r2.norm(items[i]["truth"]) if rows[i]["route"] == "turn1" else fu[i]["settles_as"]) for i in ids_}
        ans = {i: rows[i]["answer"] for i in ids_}
        n = len(ids_)
        cost = sum((t.get("cost") or 0) for i in ids_ for part in ([rows[i].get("judge_q"), rows[i].get("judge_g")] + rows[i].get("elicits", [])) if part for t in part.get("tries", []))
        result["sets"][set_name] = {
            "n": n,
            "routes": {k: sum(rows[i]["route"] == k for i in ids_) for k in ("turn1", "loop", "to_person")},
            "right": r2.frac(sum(ans[i] == truth[i] for i in ids_), n),
            "false_shown": r2.frac(sum(ans[i] == "shown" and truth[i] != "shown" for i in ids_), sum(truth[i] != "shown" for i in ids_)),
            "false_contradicted": sum(ans[i] == "contradicted" and truth[i] != "contradicted" for i in ids_),
            "to_a_person": sum(ans[i] == "not shown" for i in ids_),
            "spent_usd": round(cost, 5),
        }
    target, k = OUT / "score-stage2e.json", 2
    while target.exists():
        target, k = OUT / f"score-stage2e-{k}.json", k + 1
    target.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print("written:", target.name)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "run":
        run(sys.argv[2], sys.argv[3])
    elif mode == "score":
        score(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
