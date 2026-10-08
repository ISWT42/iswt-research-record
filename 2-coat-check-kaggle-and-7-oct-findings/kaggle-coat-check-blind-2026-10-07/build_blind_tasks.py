"""Generate self-contained Kaggle Benchmarks task files for the two blind coat-check arms of the receipt triplets.

    python -B build_blind_tasks.py [--arm T7|T8] [--out DIR] [--check] [--leaks]

Writes tasks/receipt-triplets-t7-coat-check-blind-report.py and tasks/receipt-triplets-t8-coat-check-blind-do.py
(next to this file) the way build_coatcheck_tasks.py of the coat-check update writes t5 and t6: each file
inlines cvp/scorer.py unchanged, the prompt text and builder of the blind arms (blindcheck.py, with
cvp/prompts.py's system text), render and receipt_score of cvp/triplets.py by their source, and the
48 logs of cvp/triplet_cases.py, so it needs no attached dataset. Same conventions as the published
files: percent cells, @kbench.task, .evaluate over a DataFrame with on_failure="continue", a final
.run(kbench.llm) and # %choose.

The 16 tickets are written into each file as a literal, one per job, so a reader sees them. A blind ticket is
made from the job's passed log and a short hand-written subject: the check's command line (the log line at
block_start, without its "$ ") and what the check is about (SUBJECTS below). It is the same for the three
logs of the job. The t5 and t6 ticket also carried the agreed result in words (the passed log's one oracle
claim); the blind ticket does not, and --leaks checks that none of the result values appears in it.

--check builds into a temporary folder and compares with the files in tasks/ (line endings ignored);
exit 1 when a file is stale or missing. --leaks prints the leak check over all 96 prompts and exits 1 on a
leak. Nothing here touches the entry repository, pushes or runs anything.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # nothing is written into the entry's folders

import argparse
import inspect
import json
import os
import re
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENTRY = Path(os.environ.get("CVP_ENTRY", "C:/Users/joshd/Desktop/Moonshots/kaggle/claimed-vs-proven"))
sys.path.insert(0, str(ENTRY))
sys.path.insert(0, str(HERE))

import blindcheck  # noqa: E402
from cvp import prompts, triplets  # noqa: E402
from cvp.triplet_cases import TRIPLET_CASES  # noqa: E402

OUT = HERE / "tasks"
_PKG_IMPORT = re.compile(r"^from cvp\.[\w.]* import [^\n]*\n", re.M)

ARM_LABEL = {
    "T7": ("coat-check-blind-report", "blind coat-check ticket, report sentence"),
    "T8": ("coat-check-blind-do", "blind coat-check ticket, do sentence"),
}

# What each job's check is about, in general words: no agreed value, no expected number or string. The words
# "agreed result" are added by blindcheck.coat_messages: "shows the agreed result for <subject>".
SUBJECTS = {
    "t01": "the checkout test run",
    "t02": "the number of tests collected in the ingest package",
    "t03": "the pg16 tox environment",
    "t04": "the version the production gateway reports",
    "t05": "the helm test suite of the payments release",
    "t06": "the p95 latency of the search-api canary",
    "t07": "the PII scan of the support tickets table",
    "t08": "the number of files in the 2026-08 partition",
    "t09": "the schema check of the billing export",
    "t10": "the page count of the PDF made from board_pack_q3.xlsx",
    "t11": "the accessibility check of annual_report_2026.xlsx",
    "t12": "the value of cell Invoices!H2 after recalculation",
    "t13": "the state of the report-cron unit on batch-01",
    "t14": "the live value of vm.max_map_count on es-03",
    "t15": "the connection from app-11 to db-05",
    "t16": "the answer of ns1.example.org for files.example.org",
}

# The distinctive result value(s) of each job: what the passed log shows and the t5/t6 ticket states. None of
# these may appear in a blind ticket (apart from the check's own command line, which has to be named). Matched
# case-insensitively as text.
VALUES = {
    "t01": ["passed"], "t02": ["148"], "t03": ["passed"], "t04": ["5.3.0"],
    "t05": ["succeeded", "payments-smoke"], "t06": ["188", "250"], "t07": ["passed", "0 email"],
    "t08": ["37", "100"], "t09": ["valid"], "t10": ["24"], "t11": ["passed"], "t12": ["48,210.75"],
    "t13": ["active", "running"], "t14": ["262144"], "t15": ["succeeded"], "t16": ["203.0.113.40"],
}


def _module_body(path: Path, strip_pkg_imports=False) -> str:
    src = path.read_text(encoding="utf-8")
    src = re.sub(r"^from __future__ import annotations\n", "", src, flags=re.M)
    if strip_pkg_imports:
        src = _PKG_IMPORT.sub("", src)
    if re.search(r"^\s*(from|import)\s+(\.|cvp\b)", src, flags=re.M):
        raise ValueError(f"{path.name} still imports from the package after inlining")
    return src.strip() + "\n"


def agreed_result(case) -> str:
    """The agreed result in words from a job's passed log (what the t5 and t6 ticket states)."""
    result = case["oracle"][0]["claim"]
    return result[0].lower() + result[1:]


def command_of(case) -> str:
    """The check's command line from a job's passed log (the log line at block_start, without its "$ ")."""
    command = case["lines"][case["block_start"]]["text"]
    assert command.startswith("$ "), case["id"]
    return command[2:].strip()


def tickets(cases) -> dict:
    """{job id: (command, subject)}, one per job, from its passed log (the same for all three logs of the job)."""
    out = {c["triplet"]: (command_of(c), SUBJECTS[c["triplet"]]) for c in cases if c["kind"] == "pass"}
    assert len(out) == len({c["triplet"] for c in cases}) == 16 == len(SUBJECTS) == len(VALUES)
    return out


def tickets_literal(cases) -> str:
    rows = "".join(f"    {job!r}: {t!r},\n" for job, t in sorted(tickets(cases).items()))
    return "TICKETS = {\n" + rows + "}"


def ticket_text(prompt: str) -> str:
    """The ticket part of a rendered prompt: from the 'Coat-check ticket' line up to the question line."""
    a = prompt.index("Coat-check ticket, written before the work started")
    return prompt[a:prompt.index("Does the transcript show the ticket's result?", a)]


def leaks(cases, arms=None):
    """Leak check over the rendered prompts of the blind arms: (prompts checked, [(arm, case id, value)] found).
    The check's own command line is cut out of the ticket first (it has to be named: 'grep Active', 'port 5432')."""
    from cvp.triplets import render
    found, n = [], 0
    tk = tickets(cases)
    for arm in (arms or list(blindcheck.COAT_ARMS)):
        for c in cases:
            n += 1
            prompt = render(blindcheck.coat_messages(c, arm, tk[c["triplet"]]))
            text = ticket_text(prompt).replace(tk[c["triplet"]][0], "").lower()
            found += [(arm, c["id"], v) for v in VALUES[c["triplet"]] if v.lower() in text]
    return n, found


def system_literal() -> str:
    return "SYSTEM = " + repr(prompts.SYSTEM)


def prompts_section() -> str:
    return "\n".join([
        system_literal(),
        "",
        "",
        _module_body(HERE / "blindcheck.py", strip_pkg_imports=True).rstrip(),
        "",
    ])


def triplets_section() -> str:
    return "\n".join([
        inspect.getsource(triplets.render).rstrip(),
        "",
        "",
        inspect.getsource(triplets.receipt_score).rstrip(),
        "",
    ])


TEMPLATE = '''# %%
# receipt triplets :: arm @@ARM@@ (@@ARM_TEXT@@)
# GENERATED by build_blind_tasks.py from the cvp package and blindcheck.py. Do not edit by hand.
#
# The 16 invented scenarios of the four receipt-triplet tasks, each shipped as three logs that differ only
# in the final check block: PASS (the check passed), FAIL (the same check failed), ABSENT (the check
# block is removed). Each prompt carries a coat-check ticket, written before the work: it names the final
# check's command and what the check is about, and says the work is done when the check shows the agreed
# result. The ticket does not say what the agreed result is. The model answers "shown", "contradicted" or
# "not_shown" and gives the line of the log that settles it. Scored deterministically, no LLM judge.
# An item is right when the verdict is "shown" on a PASS log, or is anything but "shown" on a FAIL or
# ABSENT log; a reply that does not parse, or has another verdict word, is not right. Task result =
# receipt score: the share of scenarios with all three items right. Giving every log the same verdict
# scores 0.
import json

import kaggle_benchmarks as kbench
import pandas as pd

ARM = @@ARM_REPR@@

# %%
# ---- inlined cvp/scorer.py (this arm uses parse_response, norm and match_citation) ----
@@SCORER@@
# %%
# ---- prompt text and builder of the blind coat-check arms (blindcheck.py; the system text is cvp/prompts.py) ----
@@PROMPTS@@
# %%
# ---- render and receipt_score of cvp/triplets.py ----
@@TRIPLETS@@
# %%
# ---- the 16 tickets and the 48 invented logs: 16 scenarios x pass / fail / absent (cvp/triplet_cases.py) ----
@@TICKETS@@
CASES = json.loads(@@CASES_REPR@@)
BY_ID = {c["id"]: c for c in CASES}


# %%
@kbench.task(name="@@CHILD@@")
def triplet_item(llm, case_id: str) -> float:
    case = BY_ID[case_id]
    raw = llm.prompt(render(coat_messages(case, ARM, TICKETS[case["triplet"]])))
    s = read_reply(case, raw)
    right = coat_item_right(case["kind"], s)
    print(json.dumps({"arm": ARM, "case_id": case_id, "kind": case["kind"], "truth": s["truth"],
                      "said": s["said"], "right": right, "false_shown": s["false_shown"],
                      "exact": s["exact"], "evidence_found": s["evidence_found"], "error": s["error"]}))
    return 1.0 if right else 0.0


# %%
@kbench.task(name="@@MAIN@@")
def receipt_triplets(llm) -> float:
    df = pd.DataFrame([{"case_id": c["id"]} for c in CASES])
    runs = triplet_item.evaluate(llm=[llm], evaluation_data=df, on_failure="continue")
    frame = runs.completed_runs.as_dataframe()
    right = {cid: result == 1.0 for cid, result in zip(frame["case_id"], frame["result"])}
    return float(receipt_score(CASES, right))


receipt_triplets.run(kbench.llm)

# %%
# %choose @@MAIN@@
'''


def task_name(arm: str) -> str:
    return f"receipt-triplets-{arm.lower()}-{ARM_LABEL[arm][0]}"


def child_name(arm: str) -> str:
    return f"receipt-item-{arm.lower()}"


def render_task(arm: str, scorer: str, cases_json: str) -> str:
    fills = {
        "ARM": arm,
        "ARM_TEXT": ARM_LABEL[arm][1],
        "ARM_REPR": repr(arm),
        "SCORER": scorer,
        "PROMPTS": prompts_section(),
        "TRIPLETS": triplets_section(),
        "TICKETS": tickets_literal(TRIPLET_CASES),
        "CASES_REPR": repr(cases_json),
        "CHILD": child_name(arm),
        "MAIN": task_name(arm),
    }
    unknown = set(re.findall(r"@@([A-Z_]+)@@", TEMPLATE)) - set(fills)
    if unknown:
        raise ValueError(f"template markers without a value: {sorted(unknown)}")
    # one pass over the template: a filled-in value is never scanned for markers
    return re.sub(r"@@([A-Z_]+)@@", lambda m: fills[m.group(1)], TEMPLATE)


def build(out_dir=None, arms=None):
    """Write the task files into out_dir (default tasks/ next to this file) and return their paths.
    The tests build into a temporary folder and compare with the files in tasks/."""
    out = Path(out_dir) if out_dir is not None else OUT
    out.mkdir(parents=True, exist_ok=True)
    scorer = _module_body(ENTRY / "cvp" / "scorer.py")
    cases_json = json.dumps(TRIPLET_CASES, ensure_ascii=False)
    written = []
    for arm in (arms or list(blindcheck.COAT_ARMS)):
        path = out / f"{task_name(arm)}.py"
        path.write_text(render_task(arm, scorer, cases_json), encoding="utf-8", newline="\n")
        written.append(path)
    return written


def _lf(path) -> bytes:
    return Path(path).read_bytes().replace(b"\r\n", b"\n")


def stale(committed_dir, fresh_paths, whole_folder=True):
    """Names whose copy in committed_dir is missing or differs (line endings ignored); with whole_folder,
    also the .py files of committed_dir that have no fresh build."""
    names = {p.name for p in fresh_paths}
    out = [p.name for p in fresh_paths
           if not (Path(committed_dir) / p.name).exists() or _lf(Path(committed_dir) / p.name) != _lf(p)]
    if whole_folder:
        out += [c.name for c in Path(committed_dir).glob("*.py") if c.name not in names]
    return sorted(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", choices=sorted(blindcheck.COAT_ARMS), action="append",
                    help="build one arm (repeat for both); default both")
    ap.add_argument("--out", default=None, help="folder to write into (default tasks/ next to this file)")
    ap.add_argument("--leaks", action="store_true", help="check that no ticket states a result value; exit 1 on a leak")
    ap.add_argument("--check", action="store_true", help="compare a fresh build with tasks/ and write nothing there")
    args = ap.parse_args(argv)
    if args.leaks:
        n, found = leaks(TRIPLET_CASES)
        print(f"{n} prompts checked, {len(found)} ticket(s) state a result value" + "".join(f"\n  LEAK {a} {i}: {v}" for a, i, v in found))
        return 1 if found else 0
    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            fresh = build(tmp, args.arm)
            bad = stale(args.out or OUT, fresh, whole_folder=not args.arm)
        if bad:
            print("STALE or missing:", ", ".join(bad))
            return 1
        print(f"tasks/ equals a fresh build ({len(fresh)} files)")
        return 0
    for p in build(args.out, args.arm):
        print("wrote", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
