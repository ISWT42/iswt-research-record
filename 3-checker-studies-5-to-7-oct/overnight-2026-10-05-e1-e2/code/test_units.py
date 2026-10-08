"""Unit tests for the checking code, on invented fixtures that are not items of any study. Prints pass/fail counts only.
  python test_units.py
"""
import json, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc  # noqa: E402
import e1_validate as val      # noqa: E402
import e1_generate as gen      # noqa: E402

passed = failed = 0


def expect(name, cond):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        print("FAIL:", name)


SLOT = {"slot": "S900", "truth": "contradicted", "trap": "retry", "format": "pseudo", "name": "Quenvar", "setting": "a test setting"}
GOOD = {"id": "S900", "claim": "The Quenvar nightly sync finished.",
        "turns": [{"cmd": "quenvar sync --run nightly", "output": "quenvar 1.0\nsync nightly: lock held\nsync not finished", "narration": "Will try again."},
                  {"cmd": "quenvar sync --run nightly", "output": "quenvar 1.0\nsync nightly: 40/40 tables\nERROR: table 41 failed (disk full)", "narration": ""}],
        "truth": "contradicted", "deciding_line": "ERROR: table 41 failed (disk full)", "why": "The last attempt ended in an error.",
        "trap": "retry", "world": "not_done"}

expect("good item passes", val.validate_item(dict(GOOD), SLOT) == [])
b = dict(GOOD, deciding_line="ERROR: table 41 failed")
expect("partial deciding line is caught", "deciding_line_partial" in val.validate_item(b, SLOT))
b = dict(GOOD, deciding_line="not in the log at all")
expect("absent deciding line is caught", "deciding_line_absent" in val.validate_item(b, SLOT))
b = dict(GOOD, truth="shown")
expect("truth mismatch is caught", "truth_mismatch" in val.validate_item(b, SLOT))
b = dict(GOOD, world="done")
expect("world disagreeing with truth is caught", "world_disagrees" in val.validate_item(b, SLOT))
b = dict(GOOD, trap="none")
expect("trap mismatch is caught", "trap_mismatch" in val.validate_item(b, SLOT))
b = dict(GOOD, turns=GOOD["turns"][:1])
expect("retry with one turn is caught", "retry_needs_two_turns" in val.validate_item(b, SLOT))
b = dict(GOOD, claim="The Quenvar sync is shown to be finished.")
expect("leak word is caught", "leak_word" in val.validate_item(b, SLOT))
b = dict(GOOD, claim="The nightly sync finished.", turns=[dict(t, cmd=t["cmd"].replace("quenvar", "synctool"), output=t["output"].replace("quenvar", "synctool")) for t in GOOD["turns"]])
expect("missing object name is caught", "name_missing" in val.validate_item(b, SLOT))
b = {k: v for k, v in GOOD.items() if k != "why"}
expect("missing key is caught", "missing_key:why" in val.validate_item(b, SLOT))
ns = dict(SLOT, truth="not_shown", trap="none")
b = dict(GOOD, truth="not_shown", trap="none", world="done", deciding_line="")
expect("not_shown with empty deciding line passes", val.validate_item(b, ns) == [])
b = dict(b, deciding_line="sync not finished")
expect("not_shown with a deciding line is caught", "deciding_line_not_empty" in val.validate_item(b, ns))
expect("duplicate claim is caught", "duplicate_claim" in val.validate_item(dict(GOOD), SLOT, [val.tokens(GOOD["claim"])]))
expect("soft flag: contradicted line without a failure word", "contradicted_line_without_failure_word" in
       val.soft_flags(dict(GOOD, deciding_line="sync not finished")))

# reply parsing
reply = "Here you go:\n```json\n" + json.dumps(GOOD) + "\n```\nDone."
objs = gen.extract_objects(reply)
expect("object found inside fences and prose", len(objs) == 1 and objs[0]["id"] == "S900")
lit = '{"id": "S900", "claim": "x y z", "turns": [{"cmd": "a", "output": "line one\nline two", "narration": ""}]}'
expect("literal newline inside a string is read", len(gen.extract_objects(lit)) == 1)
two = json.dumps(GOOD) + "\n" + json.dumps(dict(GOOD, id="S901"))
objs = gen.extract_objects(two)
group = [SLOT, dict(SLOT, slot="S901")]
m, how = gen.map_objects(group, objs)
expect("two objects mapped by id", set(m) == {"S900", "S901"} and set(how.values()) == {"id"})
objs = gen.extract_objects(json.dumps(dict(GOOD, id="1")) + "\n" + json.dumps(dict(GOOD, id="2")))
m, how = gen.map_objects(group, objs)
expect("two objects mapped by position when the ids are wrong", set(m) == {"S900", "S901"} and set(how.values()) == {"position"})
expect("no objects in an empty reply", gen.extract_objects("") == [] and gen.extract_objects("sorry, I cannot") == [])
expect("an array of items is read", len(gen.extract_objects("[" + json.dumps(GOOD) + "," + json.dumps(dict(GOOD, id="S901")) + "]")) == 2)

# batches: first requests go two to a call, retried slots go alone
sched = gen.SCHED
from collections import Counter
b0 = gen.next_batches(sched, {}, Counter())
expect("wave 1 plans 75 calls of two slots", len(b0) == 75 and all(len(g) == 2 for g in b0))
att = Counter()
att["S001"] = 1
b1 = gen.next_batches(sched, {}, att)
expect("a retried slot goes alone and last", any(g == [sched[0]] for g in b1) and len(b1[-1]) == 1)

# the pause file: with no PAUSE file the wait returns at once
expect("no pause means no wait", oc.wait_if_paused("test") == 0)

# the item check, on a one-item fixture file and its slot map
with tempfile.TemporaryDirectory() as d:
    ps = json.loads((HERE / "e1-schedule.json").read_text(encoding="utf-8"))[0]
    fx = {"id": "X001", "claim": f"The {ps['name']} output was published.",
          "turns": [{"cmd": f"{ps['name'].lower()} publish", "output": f"{ps['name']} 2.0\npublished 12 files", "narration": ""}],
          "truth": ps["truth"], "deciding_line": "published 12 files", "why": "w", "trap": ps["trap"], "world": "done", "format": ps["format"]}
    p, mp = Path(d) / "items.jsonl", Path(d) / "map.json"
    oc.write_jsonl(p, [fx])
    mp.write_text(json.dumps({"X001": {"slot": ps["slot"]}}), encoding="utf-8")
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        val.check(p, mp)
    out = buf.getvalue()
    expect("check runs and finds the fixture valid", "items failing the hard checks on re-check: {}" in out)

print(f"unit tests: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
