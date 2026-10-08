"""T13c: reply classes by responder model age third, on T13b's sample. Implements DESIGN.md; reuses T13's classifier. Counts only."""
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLAIMS_DIR = HERE.parent
sys.path.insert(0, str(CLAIMS_DIR / "2026-10-04-t13-propagation"))
import t13_propagation as t13  # noqa: E402

DATES = json.load(open(r"C:\Users\joshd\Data\results\p3_dates.json", encoding="utf-8"))
THIRD = {d["agent"]: d["third"] for d in DATES}


def main():
    lines = sorted({int(l.split("\t")[1]) for l in open(CLAIMS_DIR / "2026-10-04-agent-run" / "universe-chat.tsv", encoding="utf-8")})
    seed = int(hashlib.sha256((CLAIMS_DIR / "2026-10-04-t13-propagation" / "T13-RESULT.json").read_bytes()).hexdigest()[:16], 16)
    pick = set(random.Random(seed).sample(lines, 2000))
    rows = [r for r in t13.iter_source(t13.MAPPED, "chat_messages", t13.load_field_map())]
    for r in rows:
        r["_t"] = t13.ts(r.get("time"))
    rows = [r for r in rows if r["_t"] is not None]
    rows.sort(key=lambda r: r["_t"])
    pos = {int(r["row_id"].rsplit(":", 1)[1]): i for i, r in enumerate(rows)}
    replies, unknown = [], Counter()
    for ln in sorted(pick):
        i = pos.get(ln)
        if i is None:
            continue
        m = rows[i]; who = m.get("agent") or ""; kw = set(t13.keywords(m.get("text") or ""))
        rx = re.compile(r"(?<![\w.-])" + re.escape(who.lower()) + r"(?![\w-])") if who else None
        n, j = 0, i + 1
        while j < len(rows) and rows[j]["_t"] <= m["_t"] + 1800 and n < 10:
            o = rows[j]; ow = o.get("agent") or ""
            if ow != who:
                n += 1
                txt = o.get("text") or ""
                if bool(rx and rx.search(txt.lower())) or len(kw & set(t13.keywords(txt))) >= 2:
                    if ow in THIRD:
                        replies.append({"responder": ow, "third": THIRD[ow], "cls": t13.classify(txt)})
                    else:
                        unknown[ow] += 1
            j += 1

    def summ(g):
        n = len(g); c = Counter(x["cls"] for x in g)
        return {"n": n, **{k: {"k": c[k], "share": round(c[k] / n, 3) if n else None, "wilson95": t13.wilson(c[k], n)} for k in ("accept", "verify", "challenge", "other")}}
    out = {"seed": seed, "engaged_replies_with_dated_responder": len(replies), "left_out_responders": dict(unknown.most_common(10)), "left_out_total": sum(unknown.values())}
    for th in ("oldest", "middle", "newest"):
        out[th] = summ([x for x in replies if x["third"] == th])
    for c in ("verify", "accept"):
        a = out["newest"][c]["k"]; b = out["newest"]["n"] - a; cc = out["oldest"][c]["k"]; d = out["oldest"]["n"] - cc
        out[f"fisher_{c}_newest_vs_oldest"] = t13.fisher(a, b, cc, d)
    top = Counter(x["responder"] for x in replies).most_common(10)
    out["top_responders"] = {r: {"third": THIRD[r], **summ([x for x in replies if x["responder"] == r])} for r, _ in top}
    (HERE / "T13C-RESULT.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "top_responders"}, indent=1))
    print("top responders:", {r: (v["third"], v["n"], v["verify"]["share"], v["accept"]["share"]) for r, v in out["top_responders"].items()})


if __name__ == "__main__":
    main()
