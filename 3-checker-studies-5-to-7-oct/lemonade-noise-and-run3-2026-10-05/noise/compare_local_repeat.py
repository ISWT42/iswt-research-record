"""Noise test 2, the local Lemonade repeat: compare it with run 2's local lane on items 201 to 240.
Sealed design: LOCAL-REPEAT-DESIGN.md (FreeTSA 18:48:02 GMT, 5 Oct 2026). Measures, per arm: identical verdicts k of 40,
identical reply text (reply SHA-256) k of 40, and seconds per item for context. Prints ids and counts only, never item text.
Writes noise/results/local-repeat-compare.json and never overwrites an earlier result."""
import json, statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN2 = HERE.parent / "run2" / "results"
IDS = [f"{i:03d}" for i in range(201, 241)]


def rows(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            out[(r["arm"], r["id"])] = r
    return out


first, again = rows(RUN2 / "answers-run2-local.jsonl"), rows(RUN2 / "answers-run2-local-repeat.jsonl")
res = {"design": "LOCAL-REPEAT-DESIGN.md", "items": "201-240", "arms": {}}
for arm in ("A", "B"):
    both = [i for i in IDS if (arm, i) in first and (arm, i) in again]
    same_v = [i for i in both if first[(arm, i)]["answer"] == again[(arm, i)]["answer"]]
    same_t = [i for i in both if first[(arm, i)]["reply_sha256"] == again[(arm, i)]["reply_sha256"]]
    res["arms"][arm] = {
        "model": again[(arm, both[0])]["model"] if both else None,
        "n": len(both),
        "identical_verdicts": len(same_v),
        "identical_reply_text": len(same_t),
        "verdict_changed_ids": [i for i in both if i not in same_v],
        "text_changed_ids": [i for i in both if i not in same_t],
        "median_seconds_first": round(st.median(first[(arm, i)]["seconds"] for i in both), 1) if both else None,
        "median_seconds_repeat": round(st.median(again[(arm, i)]["seconds"] for i in both), 1) if both else None,
        "missing": [i for i in IDS if (arm, i) not in first or (arm, i) not in again],
    }
(HERE / "results").mkdir(exist_ok=True)
target, k = HERE / "results" / "local-repeat-compare.json", 2
while target.exists():
    target, k = HERE / "results" / f"local-repeat-compare-{k}.json", k + 1
target.write_text(json.dumps(res, indent=1), encoding="utf-8")
print("written:", target.name)
for arm, m in res["arms"].items():
    print(f"arm {arm} ({m['model']}): verdicts identical {m['identical_verdicts']} of {m['n']}, reply text identical {m['identical_reply_text']} of {m['n']}; "
          f"verdict changed {m['verdict_changed_ids']}; text changed {len(m['text_changed_ids'])}; median s {m['median_seconds_first']} -> {m['median_seconds_repeat']}; missing {m['missing']}")
