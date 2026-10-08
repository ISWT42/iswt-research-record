"""Run 3, stage 2d: when a checker flags doubt but names no check, ask it for one. Sealed design: STAGE2D-DESIGN.md.
  python stage2d.py run <bank.jsonl> <followups.jsonl>
  python stage2d.py score <followups.jsonl>
Nothing here prints item text: only ids, answers and counts.
"""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run3 as r3  # noqa: E402
import stage2 as s2  # noqa: E402
import stage2c as s2c  # noqa: E402
r2, rp, v3 = r3.r2, r3.rp, r3.v3
OUT = r3.OUT
PINS = s2c.PINS
ELICIT_SYSTEM = ("You could not settle the claim from this record. Name the one read-only command that would settle it: it must not "
                 "change, send, install, move or delete anything. Also give the output line you would expect if the claim were true. "
                 "Reply with JSON only: {\"cmd\": \"...\", \"expect\": \"...\"}.")
LEFT_OUT = {"183", "278", "289"}


def call(arm, req):
    model = {"arm": arm, "id": PINS[arm]}
    tries = []
    text = err = None
    for _ in range(3):
        text, err, seconds, cost, provider, rel = r2.broker_ask(model, req)
        tries.append({"err": err, "seconds": round(seconds, 2), "cost": cost, "provider": provider, "ledger": rel})
        if not err:
            break
    return text, err, tries


def run(bank_path, fpath):
    items = r2.load(bank_path)
    fu = s2.read_followups(fpath)
    turn1 = r2.read_jsonl(OUT / "answers-run3.jsonl")
    pairs = [(r["arm"], r["id"]) for r in turn1 if r["id"] not in LEFT_OUT and s2.plan(r["arm"], r)[0] == "no_proposal"]
    log = OUT / "answers-stage2d.jsonl"
    done = {(r["arm"], r["id"]) for r in r2.read_jsonl(log)} if log.exists() else set()
    print(f"stage 2d: {len(pairs)} pairs", flush=True)
    with open(log, "a", encoding="utf-8") as f:
        for arm, i in pairs:
            if (arm, i) in done:
                continue
            item = items[i]
            turns = rp.turns_for(item)
            record_user = v3.build_request(item["claim"], item["claim"], "as stated in the claim", list(turns)).user
            text, err, tries = call(arm, s2c.Req(ELICIT_SYSTEM, record_user))
            value, _ = v3.parse_reply(text) if not err else (None, None)
            cmd = value.get("cmd") if isinstance(value, dict) and isinstance(value.get("cmd"), str) and value.get("cmd").strip() else None
            rec = {"arm": arm, "id": i, "elicit_reply_sha256": hashlib.sha256((text or "").encode()).hexdigest(), "elicit_reply": text,
                   "proposal": cmd, "elicit_tries": tries}
            if not cmd:
                rec.update(route="no_proposal", answer="not shown")
            elif r3.UNSAFE.search(cmd):
                rec.update(route="refused", answer="not shown")
            else:
                f2 = fu[i]
                text2, err2, tries2 = call(arm, s2c.Req(s2c.NARROW_SYSTEM, s2c.narrow_user(item["claim"], f2["check_cmd"], f2["check_output"])))
                answer, code, certainty = ("not shown", err2.split(":")[0], None) if err2 else s2c.judge(text2, f2["check_output"])
                rec.update(route="judged", answer=answer if certainty == "sure" else "not shown", raw_answer=answer, code=code,
                           certainty=certainty, judge_reply=text2, judge_tries=tries2)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{arm}] {i}: {rec['route']} -> {rec['answer']}", flush=True)


def score(fpath):
    fu = s2.read_followups(fpath)
    rows = r2.read_jsonl(OUT / "answers-stage2d.jsonl")
    result = {"design_sha256": (HERE / "STAGE2D-DESIGN-SHA256.txt").read_text(encoding="utf-8").split()[0], "arms": {}}
    for arm in ("U-Q", "U-G"):
        rs = [r for r in rows if r["arm"] == arm]
        n = len(rs)
        t = {r["id"]: fu[r["id"]]["settles_as"] for r in rs}
        result["arms"][arm] = {
            "n": n,
            "proposals": r2.frac(sum(1 for r in rs if r["proposal"]), n),
            "refused": sum(r["route"] == "refused" for r in rs),
            "right": r2.frac(sum(r["answer"] == t[r["id"]] for r in rs), n),
            "false_shown": sum(r["answer"] == "shown" and t[r["id"]] != "shown" for r in rs),
            "false_contradicted": sum(r["answer"] == "contradicted" and t[r["id"]] != "contradicted" for r in rs),
            "to_a_person": sum(r["answer"] == "not shown" for r in rs),
            "spent": round(sum((x.get("cost") or 0) for r in rs for x in r["elicit_tries"] + r.get("judge_tries", [])), 5),
        }
    target, k = OUT / "score-stage2d.json", 2
    while target.exists():
        target, k = OUT / f"score-stage2d-{k}.json", k + 1
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
