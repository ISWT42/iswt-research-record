"""E1 addendum 1 (E1-ADDENDUM-1.md): the writer, with two changes made at run time. The sealed e1_generate.py is not edited.
  1. A call that the model answered but that gave no usable text (empty, or cut at the 4000-token output limit while the model was still
     reasoning) counts as a try for its slots. Before, it was counted as a failed call, which would have stopped the writer after 8.
  2. One slot per call, from the first try (it was two).
  python e1_generate2.py run
Prints slot ids, reason codes and counts only.
"""
import json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc   # noqa: E402
import e1_generate as g         # noqa: E402

ADDENDUM = oc.ROOT / "E1-ADDENDUM-1-SHA256.txt"
STATE = {"real_failures": 0}
orig_handle, orig_read_state = g.handle, g.read_state


def addendum_ok():
    tsr = Path(str(ADDENDUM) + ".tsr")
    if not ADDENDUM.exists() or not tsr.exists() or tsr.stat().st_size < 100:
        return False, "addendum 1 is not sealed (hash line + FreeTSA reply)"
    for line in ADDENDUM.read_text(encoding="utf-8").splitlines():
        h, _, f = line.partition(" *")
        if oc.sha256_file(oc.ROOT / f.strip()) != h:
            return False, f"{f.strip()} changed after addendum 1 was sealed"
    return True, "ok"


def read_state():
    accepted, calls, attempts, spawned = orig_read_state()
    attempts = Counter(s for c in calls if (c.get("counted") or c.get("finish") is not None) for s in c["slots"])
    return accepted, calls, attempts, spawned


def handle(group, text, info, call_no):
    if text is None and info.get("finish") is not None:
        text = ""        # the model answered, but there is no usable text: a try that gave nothing
    rec = orig_handle(group, text, info, call_no)
    if text is None:     # the provider never answered
        STATE["real_failures"] += 1
        if STATE["real_failures"] >= 8:
            g.say("STOP: 8 calls got no answer from the provider; stopping")
            raise SystemExit(3)
    return rec


def backfill():
    """The four calls before the addendum that gave no usable text now count as tries; name their slots in the drop log, once."""
    marker = oc.ROOT / "e1" / "addendum1-backfill-done.txt"
    if marker.exists():
        return
    n = 0
    with open(g.DROPS, "a", encoding="utf-8") as f:
        for c in oc.read_jsonl(g.CALLS):
            if not c.get("counted") and c.get("finish") is not None:
                for s in c["slots"]:
                    f.write(json.dumps({"call": c["call"], "slot": s, "attempt": 1, "note": "counted by addendum 1",
                                        "reasons": ["truncated_reply" if c["finish"] == "length" else "empty_reply"]}) + "\n")
                    n += 1
    marker.write_text(f"{oc.utc_now()} backfilled {n} slot tries\n", encoding="utf-8")
    g.say(f"addendum 1: {n} slot tries from earlier calls without usable text added to the drop log")


if __name__ == "__main__":
    if sys.argv[1:] == ["run"]:
        ok, why = addendum_ok()
        if not ok:
            sys.exit(f"STOP: {why}")
        g.handle, g.read_state = handle, read_state
        g.BATCH_BY_ATTEMPT = {0: 1, 1: 1, 2: 1, 3: 1}
        g.MAX_TRANSPORT_FAILURES = 10 ** 9      # real failures are counted in handle() above
        backfill()
        g.run()
    else:
        print(__doc__)
