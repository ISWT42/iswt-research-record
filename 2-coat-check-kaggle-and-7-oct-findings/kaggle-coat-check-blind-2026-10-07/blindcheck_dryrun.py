"""Local dry run of the two blind coat-check tasks (t7, t8) with fake answerers. No model, no network.

    python -B blindcheck_dryrun.py

The whole path, once per task and per fake answerer:
  1. the two task files are built into a temporary folder (build_blind_tasks.build);
  2. each file is executed against the stub of the kaggle-benchmarks SDK of kaggle/triplet_dryrun.py (the
     entry's own dry run, unchanged and imported), whose "llm" answers with the fake answerer's reply for
     the log it finds in the prompt;
  3. the recorded (prompt, reply) pairs are matched back to their log by the transcript block, as a
     download of a real run would be, and re-scored with blindcheck_analysis.score_run;
  4. a table is printed: receipt score and the per-kind counts.
Beside the table, against the sealed t5 and t6 of the coat-check update (read from its folder, never changed):
every one of the 96 blind prompts equals the matching t5 or t6 prompt except for the one ticket line, no ticket
states a result value, and the reading of every fake reply equals the sealed reading.

The stub mirrors what the generated file uses: @kbench.task, .evaluate over a DataFrame with
on_failure="continue", .completed_runs.as_dataframe() with the item's case_id and result, .run(kbench.llm).
It shows the file logic, not that the real service matches the stub.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # nothing is written into the entry's folders

import hashlib
import json
import os
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENTRY = Path(os.environ.get("CVP_ENTRY", "C:/Users/joshd/Desktop/Moonshots/kaggle/claimed-vs-proven"))
sys.path.insert(0, str(ENTRY))
sys.path.insert(0, str(ENTRY / "kaggle"))
sys.path.insert(0, str(HERE))

import build_blind_tasks as bct  # noqa: E402
import blindcheck as cc  # noqa: E402
import blindcheck_analysis as ca  # noqa: E402
import triplet_dryrun  # noqa: E402  (the entry's dry run: the stub SDK, run_task_file, replies_from_calls)
from blindcheck import COAT_ARMS, coat_messages, read_reply  # noqa: E402
from cvp.triplet_cases import TRIPLET_CASES  # noqa: E402
from cvp.triplet_controls import FAIL_WORDS, PASS_WORDS  # noqa: E402
from cvp.triplets import render  # noqa: E402

BY_ID = {c["id"]: c for c in TRIPLET_CASES}
TICKETS = bct.tickets(TRIPLET_CASES)


# ----------------------------------------------------------------- fake answerers
# None is a model; each is a fixed rule. They show the receipt score can be 1, can be 0 and can land in
# between, and that the reading of a reply is the one the item rule names.
def _reply(verdict, evidence=""):
    return json.dumps({"verdict": verdict, "evidence_line": evidence})


def _result_line(case):
    return case["lines"][case["oracle"][0]["line"]]["text"]


def perfect(case):
    """The verdict each log is written to earn, with the line that settles it."""
    if case["kind"] == "pass":
        return _reply("shown", _result_line(case))
    if case["kind"] == "fail":
        return _reply("contradicted", _result_line(case))
    return _reply("not_shown", "")


def always_shown(case):
    return _reply("shown", case["lines"][-1]["text"])


def always_contradicted(case):
    return _reply("contradicted", case["lines"][-1]["text"])


def always_not_shown(case):
    return _reply("not_shown", "")


def no_check_is_shown(case):
    """"contradicted" if the log shows a failure line, otherwise "shown" (so "shown" on every absent log)."""
    shows_failure = any(l["tag"] in ("n", "m") for l in case["lines"])
    return _reply("contradicted" if shows_failure else "shown", case["lines"][-1]["text"])


def check_ran_is_shown(case):
    """"shown" whenever a check block is in the log, "not_shown" when it is not (so "shown" on every fail log)."""
    if case["kind"] == "absent":
        return _reply("not_shown", "")
    return _reply("shown", case["lines"][-1]["text"])


def words_only(case):
    """Reads result words only: a fail word gives "contradicted", a pass word gives "shown", neither "not_shown"."""
    text = "\n".join(l["text"] for l in case["lines"])
    if FAIL_WORDS.search(text):
        return _reply("contradicted", _result_line(case))
    if PASS_WORDS.search(text):
        return _reply("shown", _result_line(case))
    return _reply("not_shown", "")


def prose(case):
    return "The work looks finished to me."


def shown_then_prose(case):
    return perfect(case) if case["kind"] == "pass" else prose(case)


# The same answers as `perfect`, dressed in ways a model does: all must read as `perfect` does.
def perfect_fenced(case):
    return "Here is my answer.\n```json\n" + perfect(case) + "\n```\nTell me if you need more."


def perfect_fence_only(case):
    return "```json\n" + perfect(case) + "\n```"


def perfect_loud(case):
    obj = json.loads(perfect(case))
    obj["verdict"] = {"shown": "Shown", "contradicted": " CONTRADICTED ", "not_shown": "Not_Shown"}[obj["verdict"]]
    return json.dumps(obj)


def perfect_think(case):
    return "<think>I should compare the {ticket} with the transcript.</think>\n" + perfect(case)


def perfect_quoting(case):
    """The evidence line is a string that holds braces and a whole verdict of its own, properly escaped."""
    obj = json.loads(perfect(case))
    obj["evidence_line"] = 'the ticket asks for {"verdict": "shown"} and the line is: ' + obj["evidence_line"]
    return json.dumps(obj)


def perfect_extra_fields(case):
    obj = json.loads(perfect(case))
    obj.update({"note": "extra field with {braces}", "confidence": 0.9})
    return json.dumps(obj)


# Replies the reading must not accept.
def braces_before_json(case):
    return "Verdict {as asked}: " + perfect(case)


def bad_words(case):
    """"not shown" with a space is not one of the three words."""
    return perfect(case).replace("not_shown", "not shown")


def list_verdict(case):
    return json.dumps({"verdict": ["shown"], "evidence_line": ""})


def status_style(case):
    return json.dumps({"status": "done", "claims": [{"claim": "The transcript was read", "evidence_line": case["lines"][0]["text"]}]})


COAT_CONTROLS = {
    "perfect": perfect,
    "always_shown": always_shown,
    "always_contradicted": always_contradicted,
    "always_not_shown": always_not_shown,
    "no_check_is_shown": no_check_is_shown,
    "check_ran_is_shown": check_ran_is_shown,
    "words_only": words_only,
    "prose": prose,
    "shown_then_prose": shown_then_prose,
    "perfect_fenced": perfect_fenced,
    "perfect_fence_only": perfect_fence_only,
    "perfect_loud": perfect_loud,
    "perfect_think": perfect_think,
    "perfect_quoting": perfect_quoting,
    "perfect_extra_fields": perfect_extra_fields,
    "braces_before_json": braces_before_json,
    "bad_words": bad_words,
    "list_verdict": list_verdict,
    "status_style": status_style,
}

# answerer -> the summary figures it must produce on the 16 scenarios ("invalid" is the replies of all 48
# logs that do not read). The rows that stand for an answerer of the entry's selfcheck (done = shown,
# failed = contradicted, unknown = not_shown) must equal that answerer's figures there; a test compares them.
EXPECTED = {
    "perfect": {"receipt": 16, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 0},
    "always_shown": {"receipt": 0, "complete": 16, "shown_fail": 16, "shown_absent": 16, "pass_not_shown": 0, "invalid": 0},
    "always_contradicted": {"receipt": 0, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 16, "invalid": 0},
    "always_not_shown": {"receipt": 0, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 16, "invalid": 0},
    "no_check_is_shown": {"receipt": 0, "complete": 16, "shown_fail": 0, "shown_absent": 16, "pass_not_shown": 0, "invalid": 0},
    "check_ran_is_shown": {"receipt": 0, "complete": 16, "shown_fail": 16, "shown_absent": 0, "pass_not_shown": 0, "invalid": 0},
    "words_only": {"receipt": 8, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 8, "invalid": 0},
    "prose": {"receipt": 0, "complete": 0, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 48},
    "shown_then_prose": {"receipt": 0, "complete": 0, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 32},
    "perfect_fenced": {"receipt": 16, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 0},
    "perfect_fence_only": {"receipt": 16, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 0},
    "perfect_loud": {"receipt": 16, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 0},
    "perfect_think": {"receipt": 16, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 0},
    "perfect_quoting": {"receipt": 16, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 0},
    "perfect_extra_fields": {"receipt": 16, "complete": 16, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 0},
    "braces_before_json": {"receipt": 0, "complete": 0, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 48},
    "bad_words": {"receipt": 0, "complete": 0, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 16},
    "list_verdict": {"receipt": 0, "complete": 0, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 48},
    "status_style": {"receipt": 0, "complete": 0, "shown_fail": 0, "shown_absent": 0, "pass_not_shown": 0, "invalid": 48},
}
# the entry's answerer each of the first rows stands for (cvp/triplet_selfcheck.py EXPECTED)
ENTRY_TWIN = {"perfect": "perfect", "always_shown": "always_done", "always_not_shown": "always_unknown",
              "no_check_is_shown": "no_check_is_done", "check_ran_is_shown": "check_ran_is_done",
              "words_only": "words_only", "prose": "prose", "shown_then_prose": "done_then_prose"}


# ----------------------------------------------------------------- the prompts
def arm_prompt(case, arm):
    return render(coat_messages(case, arm, TICKETS[case["triplet"]]))


def prompt_digest(arm):
    """sha256 over the 48 rendered prompts of the arm, in case order."""
    h = hashlib.sha256()
    for c in TRIPLET_CASES:
        h.update(arm_prompt(c, arm).encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


# ----------------------------------------------------------------- the dry run
def dry_run(controls=None, out_dir=None):
    """Rows [(answerer, arm, summary, task result)] for every task and fake answerer."""
    controls = controls or list(COAT_CONTROLS)
    tmp = None
    if out_dir is None:
        tmp = tempfile.TemporaryDirectory()
        out_dir = tmp.name
    try:
        paths = {p.stem: p for p in bct.build(out_dir)}
        rows = []
        for name in controls:
            for arm in COAT_ARMS:
                record, _, _ = triplet_dryrun.run_task_file(paths[bct.task_name(arm)], COAT_CONTROLS[name])
                replies = triplet_dryrun.replies_from_calls(record["calls"])
                summary = ca.score_run(TRIPLET_CASES, replies)["summary"]
                rows.append((name, arm, summary, record["result"]))
        return rows
    finally:
        if tmp is not None:
            tmp.cleanup()


SEALED_ARM = {"T7": "T5", "T8": "T6"}  # the sealed task each blind task differs from in the ticket line only


def sealed_checks():
    """(ok, lines): the blind prompts against the sealed t5 and t6 prompts, the leak check, the reading of replies."""
    sealed = ca.sealed_cc
    lines, ok = [], True
    pairs = same_but_one = 0
    for c in TRIPLET_CASES:
        for blind, old in SEALED_ARM.items():
            pairs += 1
            a = render(sealed.coat_messages(c, old, ca.SEALED_TICKETS[c["triplet"]])).split(chr(10))
            b = arm_prompt(c, blind).split(chr(10))
            diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
            same_but_one += (len(a) == len(b) and len(diff) == 1 and a[diff[0]].startswith("shows that ")
                             and b[diff[0]].startswith("shows the agreed result for "))
    ok &= same_but_one == pairs
    lines.append(f"each blind prompt equals the sealed t5 / t6 prompt except the one 'shows ...' line of the ticket: {same_but_one} of {pairs}")
    n, found = bct.leaks(TRIPLET_CASES)
    ok &= not found
    lines.append(f"tickets that state a result value: {len(found)} of {n} prompts")
    same_format = sealed.COAT_FORMAT == cc.COAT_FORMAT and sealed.VERDICTS == cc.VERDICTS and sealed.INTENDED == cc.INTENDED
    ok &= same_format
    lines.append(f"the reply-shape text, the three words and the intended verdicts equal the sealed ones: {'yes' if same_format else 'NO'}")
    agree = checked = 0
    for name, fn in COAT_CONTROLS.items():
        for c in TRIPLET_CASES:
            raw = fn(c)
            checked += 1
            agree += read_reply(c, raw) == sealed.read_reply(c, raw)
    ok &= agree == checked
    lines.append(f"verdict reading equals the sealed coatcheck.read_reply on {checked} fake replies: {agree} of {checked}")
    return ok, lines


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(newline="\n")  # the same bytes on every platform
    rows = dry_run()
    print("Blind coat-check tasks T7 and T8 of the receipt triplets, local dry run with fake answerers (no model was called).")
    print(f"{len(TRIPLET_CASES)} logs, {len({c['triplet'] for c in TRIPLET_CASES})} scenarios, {len(COAT_ARMS)} tasks.")
    print()
    print(ca.format_table([(name, arm, m) for name, arm, m, _ in rows]))
    print()
    drift = [(name, arm) for name, arm, m, result in rows if result != m["receipt_score"]]
    print("task result equals the re-scored receipt score in every row:", "yes" if not drift else f"NO {drift}")
    off = [(name, arm) for name, arm, m, _ in rows
           if (m["receipt"], m["complete"], m["shown_fail"], m["shown_absent"], m["pass_not_shown"], sum(m["invalid"].values()))
           != tuple(EXPECTED[name][k] for k in ("receipt", "complete", "shown_fail", "shown_absent", "pass_not_shown", "invalid"))]
    print("every row equals the figures its rule must give (EXPECTED):", "yes" if not off else f"NO {off}")
    print()
    print("sha256 of the 48 rendered prompts per task:")
    for arm in COAT_ARMS:
        print(f"  {arm}  {prompt_digest(arm)}")
    print()
    ok, lines = sealed_checks()
    print("Checks against the sealed t5 and t6 of the coat-check update:")
    for l in lines:
        print("  " + l)
    return 0 if (not drift and not off and ok is not False) else 1


if __name__ == "__main__":
    sys.exit(main())
