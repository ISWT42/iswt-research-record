"""Build the gate test's claims file and its private key from the private source (7 Oct 2026).

    python build_items.py

Reads Private/claims/2026-10-07-gate-test/claims_src.py (truth included) and writes:
  inputs/gate-items.jsonl                                    what the models see: id, claim, turns, log_text (S2's layout)
  Private/claims/2026-10-07-gate-test/gate-keys.jsonl        the truth per id, with trap, format and deciding line
  Private/claims/2026-10-07-gate-test/blind-sample.json      the seeded tenth for the blind second reader (no truth)
Checks the trap mix against DESIGN.md, every deciding line against its output, the S2 log layout, lengths, and names.
"""
from __future__ import annotations

import collections
import hashlib
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIVATE = Path("C:/Users/joshd/Private/claims/2026-10-07-gate-test")
S2_ITEMS = Path("C:/Users/joshd/Workbench/chain-local-2026-10-06/inputs/s2-items.jsonl")
SHUFFLE_SEED = 20261007
SAMPLE_SEED = 42

MIX = {  # fixed in DESIGN.md before any claim existed
    "shown": {"plain": 10, "noise": 6, "retry": 5, "verify_step": 5, "long_output": 4},
    "contradicted": {"plain": 10, "late_fail": 6, "partial": 5, "wrong_value": 5, "rollback": 4},
    "not shown": {"never_ran": 7, "other_target": 7, "cut_off": 6, "example_text": 5, "over_claim": 5},
}


def render_log(turns: list) -> str:
    """S2's log_text layout (an empty output reads "(no output recorded)", as in S2's C070)."""
    n = len(turns)
    return "\n\n".join(f"[T{i}] step {i} of {n}\nCOMMAND:\n{t['cmd']}\nOUTPUT of T{i}:\n{t['output'] or '(no output recorded)'}"
                       for i, t in enumerate(turns, 1))


def main() -> int:
    sys.path.insert(0, str(PRIVATE))
    import claims_src  # noqa: E402

    items = claims_src.ITEMS
    problems = []

    # the S2 layout, proved on S2's own items
    s2 = [json.loads(line) for line in S2_ITEMS.read_text(encoding="utf-8").splitlines() if line.strip()]
    same = sum(render_log(it["turns"]) == it["log_text"] for it in s2)
    print(f"S2 layout check: renderer reproduces {same} of {len(s2)} S2 logs byte for byte")
    if same != len(s2):
        problems.append("renderer does not match S2")

    # the mix
    mix = collections.defaultdict(collections.Counter)
    for it in items:
        mix[it["truth"]][it["trap"]] += 1
    for truth, want in MIX.items():
        if dict(mix[truth]) != want:
            problems.append(f"mix for {truth}: {dict(mix[truth])} != {want}")
    print("mix:", {t: dict(c) for t, c in mix.items()})

    # each item
    claims_seen = set()
    for n, it in enumerate(items):
        tag = f"#{n} {it['claim'][:50]}"
        text = it["claim"] + " " + " ".join(t["cmd"] + " " + t["output"] for t in it["turns"])
        if chr(92) in text or "\t" in text or "\r" in text:
            problems.append(f"{tag}: backslash, tab or carriage return")
        if not it["claim"].endswith("."):
            problems.append(f"{tag}: claim does not end with a full stop")
        if it["claim"] in claims_seen:
            problems.append(f"{tag}: duplicate claim")
        claims_seen.add(it["claim"])
        if not 1 <= len(it["turns"]) <= 4:
            problems.append(f"{tag}: {len(it['turns'])} turns")
        for t in it["turns"]:
            if len(t["output"]) >= 1500 or len(t["cmd"]) >= 600:
                problems.append(f"{tag}: output or command too long for the checker's caps")
        if it["truth"] == "not shown":
            if it["deciding_turn"] is not None:
                problems.append(f"{tag}: not shown with a deciding line")
        else:
            k = it["deciding_turn"]
            lines = it["turns"][k - 1]["output"].split("\n") if k and k <= len(it["turns"]) else []
            if it["deciding_line"] not in lines:
                problems.append(f"{tag}: deciding line not found as a whole line in T{k}")
        if re.search(r"\b(?:shown|contradicted)\b", text, re.I):
            problems.append(f"{tag}: the words shown or contradicted appear in the record")

    # names against S2's invented names
    def names(text):
        return set(re.findall(r"\b[A-Z][a-z]{3,}\b", text))
    s2_names = set().union(*(names(it["claim"] + " " + it["log_text"]) for it in s2))
    mine = set().union(*(names(it["claim"] + " " + render_log(it["turns"])) for it in items))
    shared = sorted(mine & s2_names)
    print(f"capitalised words shared with S2 ({len(shared)}): {', '.join(shared)}")

    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(" -", p)
        return 1

    # shuffle, number, write
    order = list(range(len(items)))
    random.Random(SHUFFLE_SEED).shuffle(order)
    out_items, keys = [], []
    for pos, src in enumerate(order, 1):
        it = items[src]
        gid = f"G{pos:03d}"
        out_items.append({"id": gid, "claim": it["claim"], "turns": it["turns"], "log_text": render_log(it["turns"])})
        keys.append({"id": gid, "truth": it["truth"], "trap": it["trap"], "format": it["format"],
                     "deciding_turn": it["deciding_turn"], "deciding_line": it["deciding_line"], "why": it["why"],
                     "source_index": src})
    (HERE / "inputs").mkdir(exist_ok=True)
    items_path = HERE / "inputs" / "gate-items.jsonl"
    items_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out_items), encoding="utf-8", newline="\n")
    keys_path = PRIVATE / "gate-keys.jsonl"
    keys_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in keys), encoding="utf-8", newline="\n")

    sample_ids = sorted(random.Random(SAMPLE_SEED).sample([r["id"] for r in out_items], 9))
    by_id = {r["id"]: r for r in out_items}
    (PRIVATE / "blind-sample.json").write_text(json.dumps(
        {"seed": SAMPLE_SEED, "ids": sample_ids,
         "items": [{"id": i, "claim": by_id[i]["claim"], "log_text": by_id[i]["log_text"]} for i in sample_ids]},
        ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")

    fmts = collections.Counter(k["format"] for k in keys)
    turns = collections.Counter(len(r["turns"]) for r in out_items)
    log_len = [len(r["log_text"]) for r in out_items]
    first30 = collections.Counter(k["truth"] for k in keys[:30])
    print(f"wrote {len(out_items)} items, sha256 {hashlib.sha256(items_path.read_bytes()).hexdigest()}")
    print(f"formats: {len(fmts)} kinds; turns per item {dict(sorted(turns.items()))}; "
          f"log_text chars min {min(log_len)}, mean {sum(log_len) // len(log_len)}, max {max(log_len)}")
    print(f"truth among the first 30 ids (shuffle check): {dict(first30)}")
    print(f"blind sample (seed {SAMPLE_SEED}): {', '.join(sample_ids)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
