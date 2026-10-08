import json, collections, sys
sys.stdout.reconfigure(encoding="utf-8")
W = r"C:\Users\joshd\Workbench"
bank = {}
for l in open(W + r"\chatgpt-review-2026-10-04\completion-claims-001-300.jsonl", encoding="utf-8"):
    if l.strip():
        o = json.loads(l); bank[o["id"]] = o
rows = [json.loads(l) for l in open(W + r"\lemonade-entry-2026-10-05\run3\results\answers-run3.jsonl", encoding="utf-8") if l.strip()]
for arm in ("U-Q", "U-G"):
    for name, lo in (("fresh", 161), ("primary", 201)):
        rs = [r for r in rows if r["arm"] == arm and int(r["id"]) >= lo]
        t = lambda r: "not shown" if bank[r["id"]]["truth"] == "not_shown" else bank[r["id"]]["truth"]
        shown = [r for r in rs if r["answer"] == "shown"]
        by_cert = collections.Counter(str(r["certainty"]) for r in shown)
        wrong_shown = [r for r in shown if t(r) != "shown"]
        wrong_cert = collections.Counter(str(r["certainty"]) for r in wrong_shown)
        flagged = [r for r in rs if r["certainty"] != "sure"]
        flagged_types = collections.Counter(r["answer"] for r in flagged)
        print(f"{arm} {name}: n={len(rs)} shown answers={len(shown)} by certainty={dict(by_cert)} | wrong shown={len(wrong_shown)} by certainty={dict(wrong_cert)} | flagged (unsure/unmarked)={len(flagged)} by answer type={dict(flagged_types)}")
