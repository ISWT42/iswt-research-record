"""Re-read every gate-test reply with the parser audit's reference rule (7 Oct 2026, after the results seal and the scoring).

Exploratory, not a re-scoring. The audit (Private/claims/parser-audit-2026-10-07, sealed 10:19:17 GMT) could not open these results
before they were sealed; this fills that gap. Checks: step1 verdicts (field "verdict"); reviewer and release-manager decisions
(field "decision"). Prints the disagreements by direction.
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, "C:/Users/joshd/Private/claims/parser-audit-2026-10-07")
from ref_rule import reference_parse  # noqa: E402

HERE = Path(__file__).resolve().parent
rows1 = [json.loads(l) for l in (HERE / "results/step1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
rows2 = [json.loads(l) for l in (HERE / "results/chains.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
out = Counter()
examples = []


def compare(kind, own, text, field, allowed, ident):
    ref, _ = reference_parse(text, field, allowed)
    own_n = own.strip().lower().replace(" ", "_") if isinstance(own, str) else None
    if own_n == ref:
        out[(kind, "same")] += 1
        return
    direction = "own none, reference found" if own_n in (None, "", "none") else ("own found, reference none" if ref is None else "different values")
    out[(kind, direction)] += 1
    if len(examples) < 20:
        examples.append((kind, ident, own_n, ref, (text or "")[:160].replace("\n", " ")))


for r in rows1:
    compare("check", r.get("verdict"), r.get("reply"), "verdict", ("shown", "contradicted", "not_shown"), (r.get("model_key"), r.get("id")))
for r in rows2:
    for hop, allowed in (("reviewer", ("approve", "hold")), ("release_manager", ("release", "wait"))):
        h = r.get(hop) or {}
        if isinstance(h, dict) and "reply" in h:
            compare(hop, h.get("decision"), h.get("reply"), "decision", allowed, (r.get("model_key"), r.get("item"), r.get("arm")))
for k, v in sorted(out.items()):
    print(k, v)
for e in examples:
    print(e)
