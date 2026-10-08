"""Build S12's label-free inputs (and its private key) from E2's sealed twins, with E2's exact framings and request builder.
Opaque ids T001..T054 in a seeded shuffle, so nothing in an id tells a twin from an intact log."""
import json, random, sys, hashlib
from pathlib import Path
OVER = Path("C:/Users/joshd/Workbench/overnight-2026-10-05")
LEMON = Path("C:/Users/joshd/Workbench/lemonade-entry-2026-10-05")
PACK = Path("C:/Users/joshd/Workbench/gemini-specs-2026-10-06")
KEYS = Path("C:/Users/joshd/Private/gemini-pack-keys-2026-10-06")
sys.path.insert(0, str(OVER / "code")); sys.path.insert(0, str(LEMON)); sys.path.insert(0, str(LEMON / "run2"))
import e2_framings as fr
import run_pair as rp
twins = [json.loads(l) for l in (OVER / "e2/twins-R001-R040.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
chosen = [t for t in twins if t["kind"] in ("present", "twin_missing")]
assert len(chosen) == 54, len(chosen)
rng = random.Random(20261006)
rng.shuffle(chosen)
reqs, keys = [], []
for n, item in enumerate(chosen, 1):
    oid = f"T{n:03d}"
    req = rp.v3.build_request(item["claim"], item["claim"], "as stated in the claim", list(rp.turns_for(item)))
    reqs.append({"id": oid, "user": req.user})
    keys.append({"id": oid, "source_id": item["id"], "kind": item["kind"], "truth": item["truth"]})
(PACK / "inputs/s12-requests.jsonl").write_bytes(("\n".join(json.dumps(r, ensure_ascii=False) for r in reqs) + "\n").encode("utf-8"))
(PACK / "inputs/s12-framings.json").write_bytes(json.dumps({"forced": fr.FRAMINGS["forced"], "allowed": fr.FRAMINGS["allowed"]}, ensure_ascii=False, indent=1).encode("utf-8"))
(KEYS / "s12-keys.jsonl").write_bytes(("\n".join(json.dumps(k) for k in keys) + "\n").encode("utf-8"))
print("requests", len(reqs), "keys", len(keys), "kinds", {k: sum(1 for x in keys if x["kind"] == k) for k in ("present", "twin_missing")})
print("allowed == frozen reader prompt:", fr.FRAMINGS["allowed"] == rp.v3.SYSTEM_PROMPT)
for f in ("inputs/s12-requests.jsonl", "inputs/s12-framings.json"):
    print(f, hashlib.sha256((PACK / f).read_bytes()).hexdigest())
