"""Mutation checks of the coat-check update's own tests: break one thing at a time in a throwaway copy of this
folder and see that the tests go red. Nothing here touches this folder or the entry: every change is made in a
temporary copy, and no Kaggle command is run.

    python -B mutation_checks.py                  all 15 changes (about 7 minutes)
    python -B mutation_checks.py "item rule"      the changes whose name holds the text

Each line says CAUGHT (a test failed, as it should) or NOT CAUGHT (the tests did not notice the change). Exit 1
if any change is NOT CAUGHT or was not applied.
"""
import sys

sys.dont_write_bytecode = True

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (name, file, old text, new text, test module, rebuild the task files after the change)
MUTATIONS = [
    ("item rule inverted", "coatcheck.py",
     'return (read["said"] == "shown") == (kind == "pass")', 'return (read["said"] == "shown") != (kind == "pass")', "test_coatcheck", True),
    ("verdict case not folded", "coatcheck.py",
     'said = said.strip().lower()\n    out["valid"] = True', 'said = said.strip()\n    out["valid"] = True', "test_coatcheck", True),
    ("question changed", "coatcheck.py",
     "Does the transcript show the ticket's result?", "Did the work succeed?", "test_coatcheck", True),
    ("ticket result not lower-cased", "build_coatcheck_tasks.py",
     "result[0].lower() + result[1:]", "result", "test_coatcheck", True),
    ("item result always 1.0", "build_coatcheck_tasks.py",
     "    return 1.0 if right else 0.0\n", "    return 1.0\n", "test_coatcheck", True),
    ("intended verdicts swapped", "coatcheck.py",
     '"fail": "contradicted", "absent": "not_shown"', '"fail": "not_shown", "absent": "contradicted"', "test_coatcheck", True),
    ("format text changed by one word", "coatcheck.py",
     "The work is accepted only if the verdict", "The work is accepted if the verdict", "test_coatcheck", True),
    ("two-of-three rule dropped", "coatcheck_analysis.py",
     "k = ta.needed(len(runs))", "k = 1", "test_coatcheck", False),
    ("usable limit removed", "coatcheck_analysis.py",
     "usable = no_reply <= MAX_ERRORED and not prompt_mismatch and not problems", "usable = not problems", "test_coatcheck", False),
    ("item mismatch not counted", "coatcheck_analysis.py",
     "            item_mismatch += 1\n", "            pass\n", "test_coatcheck", False),
    ("stop time ignored", "coatcheck_analysis.py",
     "    if stop is None:\n        return True\n", "    return True\n", "test_coatcheck", False),
    ("canary failure ignored", "run-coatcheck.sh",
     'no other model was started"; exit 5; }', 'no other model was started"; true; }', "test_runner", False),
    ("spend caps never over", "run-coatcheck.sh",
     'over() { "$PY" -c "import sys; sys.exit(0 if float(sys.argv[1]) > float(sys.argv[2]) - float(sys.argv[3]) else 1)" "$1" "$2" "$ROUND_MAX"; }',
     'over() { return 1; }', "test_runner", False),
    ("spend figure guard removed", "run-coatcheck.sh",
     'for v in "$day" "$roll" "$total"; do is_number "$v" || { say "a spend figure is not a number (\'$v\'); stopping"; exit 7; }; done', ':', "test_runner", False),
    ("empty need read as done", "run-coatcheck.sh",
     '[ -n "$out" ] || { say "the need helper printed nothing for $arm; stopping"; exit 6; }', ':', "test_runner", False),
]


def run(name, fname, old, new, module, rebuild):
    with tempfile.TemporaryDirectory() as d:
        dst = Path(d) / "copy"
        shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns("__pycache__"))
        path = dst / fname
        text = path.read_text(encoding="utf-8")
        if old not in text:
            return False, "MUTATION NOT APPLIED (text not found)"
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
        if rebuild:  # the task files follow the change, so that only the logic tests can notice it
            subprocess.run([sys.executable, "-B", str(dst / "build_coatcheck_tasks.py")], cwd=dst, env=env, capture_output=True)
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", module], cwd=dst, env=env, capture_output=True, text=True, timeout=900)
        tail = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else ""
        return r.returncode != 0, ("CAUGHT" if r.returncode != 0 else "NOT CAUGHT") + f" ({module}: {tail})"


def main(argv):
    only = argv[1:]
    bad = 0
    for m in MUTATIONS:
        if only and not any(o in m[0] for o in only):
            continue
        caught, text = run(*m)
        bad += not caught
        print(f"{m[0]}: {text}", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
