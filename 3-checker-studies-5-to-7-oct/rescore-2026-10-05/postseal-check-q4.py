# Independent re-implementation (different style, no import of the sealed helpers) to cross-check the sealed Q4 classes.
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
W = r"C:\Users\joshd\Workbench"
bank = {}
for l in open(W + r"\chatgpt-review-2026-10-04\completion-claims-001-300.jsonl", encoding="utf-8"):
    if l.strip():
        o = json.loads(l); bank[o["id"]] = o
res = json.load(open(W + r"\rescore-2026-10-05\results-q4-v1.json", encoding="utf-8"))
mine = {(r["lane"], r["arm"], r["id"]): r for r in res["rows"]}
V = {"verified", "shown_citing_failure", "quote_echoes_command", "shown_over_overwritten_failure"}
def get_obj(txt):
    if not isinstance(txt, str): return None
    t = txt.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", t, re.S)
    if m: t = m.group(1)
    try: o = json.loads(t)
    except Exception:
        a, b = t.find("{"), t.rfind("}")
        if a < 0 or b <= a: return None
        try: o = json.loads(t[a:b+1])
        except Exception: return None
    return o if isinstance(o, dict) else None
diff = []; n = 0; counts = {}
for lane, fn in (("local", "run2_local"), ("fast", "run2_fast")):
    path = W + r"\lemonade-entry-2026-10-05\run2\results\answers-run2-%s.jsonl" % ("local" if lane == "local" else "fast")
    for l in open(path, encoding="utf-8"):
        if not l.strip(): continue
        r = json.loads(l)
        it = bank[r["id"]]
        key = (lane, r["arm"], r["id"])
        ours = mine[key]
        if r["code"] not in V:
            if ours["cls"] is not None: diff.append((key, "non-V got class", ours["cls"]))
            continue
        o = get_obj(r["reply"])
        tid = str(o["turn_id"]).strip().strip("[]()").strip()
        if re.fullmatch(r"\d{1,3}", tid): tid = "T" + tid
        idx = int(tid[1:]) - 1 if re.fullmatch(r"[tT]\d{1,3}", tid) else None
        outs = [str(t.get("output") or "") for t in it["turns"]]
        q = o["quote"].strip()
        assert q in outs[idx], key
        D = it["deciding_line"]
        if not D:
            cls = "NO_D"
        else:
            holder_idx = [i for i, out in enumerate(outs) if D in out.split("\n")]  # whole-line test via split (equivalent here)
            # use splitlines for exactness with the bank check
            holder_idx = [i for i, out in enumerate(outs) if D in out.splitlines()]
            text_rel = (q == D) or (q in D) or (D in q)
            if not text_rel or idx not in holder_idx:
                cls = "OTHER"
            elif q == D: cls = "FULL"
            elif q in D: cls = "PART"
            else: cls = "PLUS"
        n += 1
        counts[cls] = counts.get(cls, 0) + 1
        if ours["cls"] != cls: diff.append((key, ours["cls"], cls))
        am = (r["answer"] == ("not shown" if it["truth"] == "not_shown" else it["truth"]))
        if am != ours["answer_match"]: diff.append((key, "answer_match", ours["answer_match"], am))
print("V rows re-derived:", n, "class counts (both lanes, both arms, fresh):", counts)
print("disagreements with sealed rows:", len(diff), diff[:10])
