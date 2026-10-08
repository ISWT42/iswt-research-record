"""T19: replies to the T13b claim sample, split by responder type (agent or human), on the raw chat export. Implements DESIGN.md. Counts only."""
import gzip, hashlib, json, random, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAIMS_DIR = HERE.parent
sys.path.insert(0, str(CLAIMS_DIR / "2026-10-04-t13-propagation"))
import t13_propagation as t13  # noqa: E402

RAW = Path(r"C:\Users\joshd\Data\ai-village\chat_messages.jsonl.gz")
AGENTS = {json.loads(l)["id"]: json.loads(l)["name"] for l in gzip.open(r"C:\Users\joshd\Data\ai-village\agents.jsonl.gz", "rt", encoding="utf-8")}


def main():
    lines = sorted({int(l.split("\t")[1]) for l in open(CLAIMS_DIR / "2026-10-04-agent-run" / "universe-chat.tsv", encoding="utf-8")})
    seed = int(hashlib.sha256((CLAIMS_DIR / "2026-10-04-t13-propagation" / "T13-RESULT.json").read_bytes()).hexdigest()[:16], 16)
    pick = sorted(random.Random(seed).sample(lines, 2000))

    raw = []
    with gzip.open(RAW, "rt", encoding="utf-8") as f:
        for l in f:
            m = json.loads(l)
            t = t13.ts(m.get("created_at"))
            human = m.get("speaker_type") == "user"
            who = "HUMAN:" + str(m.get("user_speaker_id")) if human else AGENTS.get(m.get("agent_speaker_id"), "?")
            raw.append({"t": t, "human": human, "who": who, "text": m.get("content") or ""})
    agent_idx = [i for i, r in enumerate(raw) if not r["human"]]  # k-th agent message in file order <-> mapped line k (1-based)

    mapped = {int(r["row_id"].rsplit(":", 1)[1]): r for r in t13.iter_source(t13.MAPPED, "chat_messages", t13.load_field_map())}
    mism = sum(1 for k in pick[:50] if (mapped[k].get("text") or "").strip() != raw[agent_idx[k - 1]]["text"].strip())
    if mism:
        sys.exit(f"line map spot check failed: {mism} of 50 differ")

    order = sorted(range(len(raw)), key=lambda i: (raw[i]["t"] is None, raw[i]["t"] or 0, i))
    pos = {i: p for p, i in enumerate(order)}
    replies = []
    per_claim = []
    for k in pick:
        ci = agent_idx[k - 1]; c = raw[ci]
        if c["t"] is None:
            continue
        kw = set(t13.keywords(c["text"])); name = c["who"]
        rx = re.compile(r"(?<![\w.-])" + re.escape(name.lower()) + r"(?![\w-])") if name and name != "?" else None
        n, j, flags = 0, pos[ci] + 1, {"human_vc": False, "agent_vc": False}
        while j < len(order) and n < 10:
            o = raw[order[j]]
            if o["t"] is None or o["t"] > c["t"] + 1800:
                break
            if o["who"] != name:
                n += 1
                txt = o["text"]
                if (rx and rx.search(txt.lower())) or len(kw & set(t13.keywords(txt))) >= 2:
                    cls = t13.classify(txt)
                    replies.append({"human": o["human"], "cls": cls})
                    if cls in ("verify", "challenge"):
                        flags["human_vc" if o["human"] else "agent_vc"] = True
            j += 1
        per_claim.append(flags)

    def summ(g):
        n = len(g); cnt = Counter(x["cls"] for x in g)
        return {"n": n, **{k: {"k": cnt[k], "share": round(cnt[k] / n, 3) if n else None, "wilson95": t13.wilson(cnt[k], n)} for k in ("challenge", "verify", "accept", "other")}}
    H = [x for x in replies if x["human"]]; A = [x for x in replies if not x["human"]]
    out = {"seed": seed, "claims": len(per_claim), "engaged_replies": len(replies), "human": summ(H), "agent": summ(A)}
    for c in ("verify", "challenge"):
        a = out["human"][c]["k"]; b = len(H) - a; cc = out["agent"][c]["k"]; d = len(A) - cc
        out[f"fisher_{c}_human_vs_agent"] = t13.fisher(a, b, cc, d)
    vc = [x for x in replies if x["cls"] in ("verify", "challenge")]
    hs_all = len(H) / len(replies) if replies else None
    hs_vc = sum(1 for x in vc if x["human"]) / len(vc) if vc else None
    out["human_share_of_engaged"] = round(hs_all, 4) if hs_all is not None else None
    out["human_share_of_verify_or_challenge"] = round(hs_vc, 4) if hs_vc is not None else None
    out["over_representation_ratio"] = round(hs_vc / hs_all, 2) if hs_all else None
    out["claims_with_human_verify_or_challenge"] = sum(f["human_vc"] for f in per_claim)
    out["claims_with_agent_verify_or_challenge"] = sum(f["agent_vc"] for f in per_claim)
    (HERE / "T19-RESULT.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
