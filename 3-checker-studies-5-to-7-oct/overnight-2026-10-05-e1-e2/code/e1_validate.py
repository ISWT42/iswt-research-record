"""E1 item checks, in the way replicate.py `check` works: by script, counts and ids only, never item text.
Hard checks decide whether an item is kept. Soft flags are only reported.
  python e1_validate.py check <items.jsonl> [slot-map.json]
"""
import hashlib, json, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc  # noqa: E402

TRUTHS = ("shown", "contradicted", "not_shown")
TRAPS = ("other_environment", "intermediate_signal", "truncated", "relayed_claim", "example_text", "tool_failed_to_run",
         "expected_error", "retry", "narration", "injected_text", "none")
WORLDS = ("done", "not_done")
REQUIRED = ("id", "claim", "turns", "truth", "deciding_line", "why", "trap", "world")
LEAK = re.compile(r"\b(?:shown|contradicted|not[_ ]shown|deciding[_ ]line)\b", re.I)
CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MAX_CHARS = 4000        # commands plus outputs of one item
JACCARD_LIMIT = 0.8

_EARLIER = None


def tokens(s):
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def earlier_claims():
    global _EARLIER
    if _EARLIER is None:
        rows = oc.read_jsonl(r"C:\Users\joshd\Workbench\chatgpt-review-2026-10-04\completion-claims-001-300.jsonl")
        rows += oc.read_jsonl(r"C:\Users\joshd\Workbench\replication-2026-10-05\items-R001-R040.jsonl")
        _EARLIER = [tokens(str(r.get("claim", ""))) for r in rows]
    return _EARLIER


def norm_truth(t):
    t = str(t).strip().lower().replace(" ", "_")
    return t


def output_lines(turns):
    return [ln for t in turns for ln in str(t.get("output") or "").splitlines()]


def validate_item(obj, slot, accepted_claim_tokens=()):
    """Hard checks. Returns a list of failure codes (empty = the item is kept). `slot` is the schedule entry."""
    bad = []
    if not isinstance(obj, dict):
        return ["not_object"]
    for k in REQUIRED:
        if k not in obj:
            bad.append(f"missing_key:{k}")
    if bad:
        return bad
    for k in ("id", "claim", "truth", "deciding_line", "why", "trap", "world"):
        if not isinstance(obj[k], str):
            bad.append(f"bad_type:{k}")
    if not isinstance(obj["turns"], list):
        bad.append("bad_type:turns")
    if bad:
        return bad
    turns = obj["turns"]
    if not (1 <= len(turns) <= 4):
        bad.append("turn_count")
    for t in turns:
        if not isinstance(t, dict) or not isinstance(t.get("cmd"), str) or not isinstance(t.get("output"), str) \
                or not isinstance(t.get("narration", ""), str):
            bad.append("turn_fields")
            break
    if bad:
        return bad
    truth = norm_truth(obj["truth"])
    if truth != slot["truth"]:
        bad.append("truth_mismatch")
    if obj["trap"].strip() != slot["trap"]:
        bad.append("trap_mismatch")
    if obj["world"] not in WORLDS:
        bad.append("world_bad")
    elif (slot["truth"] == "shown" and obj["world"] != "done") or (slot["truth"] == "contradicted" and obj["world"] != "not_done"):
        bad.append("world_disagrees")
    if slot["trap"] == "retry" and len(turns) < 2:
        bad.append("retry_needs_two_turns")
    if not any(t["output"].strip() for t in turns):
        bad.append("no_output")
    lines = output_lines(turns)
    dl = obj["deciding_line"]
    if slot["truth"] in ("shown", "contradicted"):
        if not dl.strip():
            bad.append("deciding_line_empty")
        elif dl not in lines:
            bad.append("deciding_line_partial" if any(dl in str(t["output"]) for t in turns) else "deciding_line_absent")
    elif dl != "":
        bad.append("deciding_line_not_empty")
    words = len(obj["claim"].split())
    if not (3 <= words <= 45):
        bad.append("claim_length")
    texts = [obj["claim"]] + [x for t in turns for x in (t["cmd"], t["output"], t.get("narration", ""))]
    if any(LEAK.search(x) for x in texts):
        bad.append("leak_word")
    if any(CONTROL.search(x) for x in texts + [obj["why"], dl]):
        bad.append("control_chars")
    if sum(len(t["cmd"]) + len(t["output"]) for t in turns) > MAX_CHARS:
        bad.append("too_long")
    if slot["name"].lower() not in "\n".join(texts).lower():
        bad.append("name_missing")
    ct = tokens(obj["claim"])
    if any(jaccard(ct, a) >= JACCARD_LIMIT for a in accepted_claim_tokens):
        bad.append("duplicate_claim")
    if any(jaccard(ct, a) >= JACCARD_LIMIT for a in earlier_claims()):
        bad.append("duplicate_of_earlier_bank")
    return bad


def soft_flags(obj):
    """Reported only. polarity: the deciding line's failure words against its label; deciding_turns: how many turns hold it."""
    flags = []
    dl = obj.get("deciding_line", "")
    if dl:
        marked = bool(oc.v3.failure_markers(dl))
        if obj["truth"] == "contradicted" and not marked:
            flags.append("contradicted_line_without_failure_word")
        if obj["truth"] == "shown" and marked:
            flags.append("shown_line_with_failure_word")
        if sum(dl in output_lines([t]) for t in obj["turns"]) > 1:
            flags.append("deciding_line_in_several_turns")
    return flags


def check(items_path, slotmap_path=None):
    """The counts-only check of the finished items file (the analogue of replicate.py `check`)."""
    p = Path(items_path)
    raw = p.read_bytes()
    rows = oc.read_jsonl(p)
    print("file sha256:", hashlib.sha256(raw).hexdigest(), "| bytes:", len(raw), "| lines:", len(rows))
    ids = [r.get("id") for r in rows]
    want = [f"X{i:03d}" for i in range(1, 151)]
    print("ids X001-X150 unique and in order:", ids == want, "| unique:", len(set(ids)), "| missing:", sorted(set(want) - set(ids))[:10])
    print("truth:", dict(Counter(norm_truth(r.get("truth")) for r in rows)))
    print("trap:", dict(Counter(r.get("trap") for r in rows)))
    print("format:", dict(Counter(r.get("format") for r in rows)))
    print("turns per item:", dict(sorted(Counter(len(r.get("turns", [])) for r in rows).items())))
    need = {"id", "claim", "turns", "truth", "deciding_line", "why", "trap", "world", "format"}
    print("rows missing a field:", [r.get("id") for r in rows if not need <= set(r)][:10])
    bad_line = []
    for r in rows:
        if norm_truth(r.get("truth")) in ("shown", "contradicted") and r.get("deciding_line") not in output_lines(r.get("turns", [])):
            bad_line.append(r.get("id"))
    print("shown/contradicted rows whose deciding line is not a whole output line:", bad_line)
    print("not_shown rows with a deciding line:", [r["id"] for r in rows if norm_truth(r.get("truth")) == "not_shown" and r.get("deciding_line")])
    wb = [r["id"] for r in rows if (norm_truth(r["truth"]) == "shown" and r.get("world") != "done")
          or (norm_truth(r["truth"]) == "contradicted" and r.get("world") != "not_done")]
    print("world disagrees with truth:", wb)
    # hard re-check of every kept item against its slot, when the slot map is given
    if slotmap_path:
        sm = json.loads(Path(slotmap_path).read_text(encoding="utf-8"))
        sched = {s["slot"]: s for s in json.loads((HERE / "e1-schedule.json").read_text(encoding="utf-8"))}
        spawned = oc.ROOT / "e1" / "e1-spawned-reserves.json"      # reserves that took over slots which could not be filled
        if spawned.exists():
            sched.update({s["slot"]: s for s in json.loads(spawned.read_text(encoding="utf-8"))})
        fails, seen = {}, []
        for r in rows:
            slot = sched[sm[r["id"]]["slot"]]
            probe = dict(r)
            probe["id"] = slot["slot"]
            codes = validate_item(probe, slot, seen)
            if codes:
                fails[r["id"]] = codes
            seen.append(tokens(r["claim"]))
        print("items failing the hard checks on re-check:", fails)
    flags = Counter(f for r in rows for f in soft_flags(r))
    print("soft flags (reported, not dropped):", dict(flags))
    size = sorted(sum(len(t["cmd"]) + len(t["output"]) for t in r["turns"]) for r in rows)
    print("chars per item (min, median, max):", size[0], size[len(size) // 2], size[-1])


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "check":
        check(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        print(__doc__)
