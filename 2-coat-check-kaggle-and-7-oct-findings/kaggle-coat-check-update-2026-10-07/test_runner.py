"""The three Kaggle scripts (run, push, publish) run against a fake `kaggle` command in a sandbox. Nothing here
talks to Kaggle: the fake command records its arguments and writes run files made by coatcheck_fakeruns.py;
the sandbox holds copies of the entry's spend scripts and a stand-in for its seal check, so no real run
folder, seal or credential is touched.

    cd <this folder> && python -B -m unittest -v test_runner

What this shows: the gates (day, rolling, total, stop time, quota, canary), the stops when a helper breaks,
the refusal when a listed file changed, and the exact lines the scripts send to the kaggle command.
It does not show that the real command prints the same lines the fake one does.
"""
import sys

sys.dont_write_bytecode = True

import os
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENTRY = Path(os.environ.get("CVP_ENTRY", "C:/Users/joshd/Desktop/Moonshots/kaggle/claimed-vs-proven"))
sys.path.insert(0, str(ENTRY))
sys.path.insert(0, str(ENTRY / "kaggle"))
sys.path.insert(0, str(HERE))

import build_coatcheck_tasks as bct  # noqa: E402

CORE = ("gemini-3.8-flash", "gemini-3.7-flash", "claude-haiku-4-5-20251001", "gpt-5.4-nano-2026-03-17")
T5, T6 = "receipt-triplets-t5-coat-check-report", "receipt-triplets-t6-coat-check-do"

FAKE_KAGGLE = """#!/usr/bin/env bash
# a stand-in for the kaggle command: it records the call and answers in the lines the scripts read
echo "$*" >> "$FAKE_CALLS"
case "$1 $2 $3" in
  "b t run")
    shift 4
    while [ $# -gt 0 ]; do case "$1" in -m) echo "  $2: COMPLETED"; shift 2;; *) shift;; esac; done ;;
  "b t download")
    task=$4; shift 4; out=""; m=""
    while [ $# -gt 0 ]; do case "$1" in -o) out=$2; shift 2;; -m) m=$2; shift 2;; *) shift;; esac; done
    n=$(( $(cat "$FAKE_COUNTER" 2>/dev/null || echo 0) + 1 )); echo $n > "$FAKE_COUNTER"
    "$FAKE_PY" -B "$FAKE_UPD/coatcheck_fakeruns.py" write "$out" "$task" "$m" --answerer "${FAKE_ANSWERER:-perfect}" \\
      --start "$(date -u -d "+$n seconds" +%Y-%m-%dT%H:%M:%SZ)" --run-id "$((7000000 + n))" --cost "${FAKE_COST:-1000000}" \\
      --errored "${FAKE_ERRORED:-0}" >/dev/null ;;
  "b t push")
    [ -n "${FAKE_PUSH_FAILS:-}" ] && { echo "push refused" >&2; exit 3; }
    echo "Next step:"; echo "   \\$ kaggle b t run $4" ;;
  "b t list") echo "receipt-triplets-t6-coat-check-do   Completed   2026-10-08 09:00:00" ;;
  "b t status") echo "Task:     $4"; echo "Version:  1"; echo "Status:   Completed"; echo "Public:   False" ;;
  "b t publish") echo "Task '$4' published successfully."; echo "Task URL: https://example.invalid/$4" ;;
  *) echo "unexpected call: $*" >&2; exit 2 ;;
esac
"""


class Sandbox:
    def __init__(self, root):
        self.root = Path(root)
        self.repo, self.upd = self.root / "repo", self.root / "upd"
        self.calls, self.counter = self.root / "calls.txt", self.root / "counter.txt"
        self.kaggle = self.root / "fake-kaggle.sh"
        for d in (self.repo / "kaggle", self.repo / "results" / "kaggle", self.repo / "results" / "probe-2026-10-01", self.repo / "ENTRY"):
            d.mkdir(parents=True)
        for name in ("day_spend.py", "cost_per_honest.py", "good_runs.py"):
            shutil.copy(ENTRY / "kaggle" / name, self.repo / "kaggle" / name)
        shutil.copy(ENTRY / "results" / "probe-2026-10-01" / "spend_windows.py", self.repo / "results" / "probe-2026-10-01" / "spend_windows.py")
        (self.repo / "kaggle" / "seal_manifest.py").write_text("print('32 of 32 items unchanged')\n", encoding="utf-8")  # stands in for the entry's check
        (self.repo / "ENTRY" / "SEAL-MANIFEST-2026-10-01.json").write_text("{}", encoding="utf-8")
        self.upd.mkdir()
        (self.upd / "tasks").mkdir()
        for f in list(HERE.glob("*.py")) + list(HERE.glob("*.sh")):
            shutil.copy(f, self.upd / f.name)
        for f in (HERE / "tasks").glob("*.py"):
            shutil.copy(f, self.upd / "tasks" / f.name)
        for name in ("PREDICTIONS.md", "COMMANDS.md", "dryrun-2026-10-07.log"):
            if (HERE / name).exists():
                text = (HERE / name).read_text(encoding="utf-8").replace("[FILL]", "(set for the sandbox)")
                (self.upd / name).write_text(text, encoding="utf-8", newline="\n")
            else:
                (self.upd / name).write_text(f"stand-in for {name}\n", encoding="utf-8")
        self.kaggle.write_text(FAKE_KAGGLE, encoding="utf-8", newline="\n")
        os.chmod(self.kaggle, 0o755)
        self.make_list()

    def make_list(self):
        r = subprocess.run(["bash", "make-file-list.sh"], cwd=self.upd, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        (self.upd / "FILES-SHA256.txt").write_text(r.stdout, encoding="utf-8", newline="\n")

    def env(self, **extra):
        env = dict(os.environ)
        env.update({"REPO": self.repo.as_posix(), "K": self.kaggle.as_posix(), "PY": Path(sys.executable).as_posix(),
                    "FAKE_CALLS": self.calls.as_posix(), "FAKE_COUNTER": self.counter.as_posix(),
                    "FAKE_PY": Path(sys.executable).as_posix(), "FAKE_UPD": self.upd.as_posix(),
                    "ROUND_SLEEP": "0", "PYTHONDONTWRITEBYTECODE": "1"})
        env.update({k: str(v) for k, v in extra.items()})
        return env

    def run(self, script, *args, **env):
        return subprocess.run(["bash", (self.upd / script).as_posix(), *args], cwd=self.root, env=self.env(**env),
                              capture_output=True, text=True, timeout=600)

    def kaggle_calls(self):
        return self.calls.read_text(encoding="utf-8").splitlines() if self.calls.exists() else []

    def log(self, name):
        p = self.repo / "results" / "kaggle" / name
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def run_files(self, task):
        return sorted((self.repo / "results" / "kaggle" / task).glob("*/*/*/*.run.json"))


def stop_in(days):
    return (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


class RunnerInASandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.sb = Sandbox(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_full_run_canary_first_three_runs_per_model_and_an_analysis(self):
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1))
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 0, out)
        runs = [c for c in self.sb.kaggle_calls() if c.startswith("b t run")]
        # T6: the canary round (nano alone), a round of all four, a round of all four, a last round of the three that need one
        self.assertEqual(runs[0], f"b t run {T6} -m gpt-5.4-nano-2026-03-17 --wait 5000")
        self.assertEqual(len(runs), 4 + 3)
        self.assertTrue(all(c.startswith(f"b t run {T6}") for c in runs[:4]))
        self.assertTrue(all(c.startswith(f"b t run {T5}") for c in runs[4:]))
        self.assertEqual(sum(c.count(" -m ") for c in runs[:4]), 1 + 4 + 4 + 3)
        for task in (T6, T5):
            files = self.sb.run_files(task)
            self.assertEqual(len(files), 12, task)
            for m in CORE:
                self.assertEqual(sum(f"/{m}/" in f.as_posix() for f in files), 3, (task, m))
        log = self.sb.log("run-coatcheck.log")
        for line in ("preflight:", "seal verifies: 32 of 32 items unchanged", "canary passed on gpt-5.4-nano-2026-03-17",
                     "T6 done", "T5 done", "all tasks done", "analysis written to"):
            self.assertIn(line, log)
        analysis = list((self.sb.repo / "results" / "kaggle").glob("analysis-coatcheck-*.txt"))
        self.assertEqual(len(analysis), 1)
        text = analysis[0].read_text(encoding="utf-8")
        self.assertIn("## Numbers for the update draft", text)
        self.assertIn("## Receipt score", text)
        self.assertNotIn("not tested", text.split("## Scenarios counted per measure")[1].split("## What each model said")[0])

    def test_downloads_go_where_the_entrys_own_scripts_look(self):
        self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1), ARMS="T5", FAKE_COST=10_000_000)
        dl = [c for c in self.sb.kaggle_calls() if c.startswith("b t download")]
        self.assertTrue(dl)
        self.assertTrue(all(f"-o results/kaggle -m " in c for c in dl), dl[:2])
        out = subprocess.run([Path(sys.executable).as_posix(), "-B", "kaggle/day_spend.py"], cwd=self.sb.repo,
                             capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, f"{12 * 0.48:.2f}")  # twelve runs of 48 calls at $0.01

    def test_the_day_cap_stops_the_run_before_the_money_is_spent(self):
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1), FAKE_COST=10_000_000, DAY_CAP="1.50")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("DAY CAP", self.sb.log("run-coatcheck.log"))
        runs = [c for c in self.sb.kaggle_calls() if c.startswith("b t run")]
        self.assertEqual(len(runs), 2)  # the canary round and one round of four; the next round is refused
        self.assertEqual(len(self.sb.run_files(T6)), 5)

    def test_the_total_cap_and_the_rolling_cap(self):
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1), FAKE_COST=10_000_000, TOTAL_CAP="1.50")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("TOTAL CAP", self.sb.log("run-coatcheck.log"))
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1), FAKE_COST=10_000_000, ROLL_CAP="1.50", TOTAL_CAP="15.00", DAY_CAP="6.00")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("ROLLING CAP", self.sb.log("run-coatcheck.log"))

    def test_a_bad_canary_stops_before_the_other_models_start(self):
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1), FAKE_ANSWERER="prose")
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        runs = [c for c in self.sb.kaggle_calls() if c.startswith("b t run")]
        self.assertEqual(runs, [f"b t run {T6} -m gpt-5.4-nano-2026-03-17 --wait 5000"])
        self.assertIn("CANARY FAILED", self.sb.log("run-coatcheck.log"))

    def test_no_canary_when_asked_not_to(self):
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1), ARMS="T5", CANARY_MODEL="")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        runs = [c for c in self.sb.kaggle_calls() if c.startswith("b t run")]
        self.assertEqual(sum(c.count(" -m ") for c in runs), 12)
        self.assertEqual(runs[0].count(" -m "), 4)

    def test_the_stop_time_is_kept(self):
        r = self.sb.run("run-coatcheck.sh", STOP_AT="2020-01-01T00:00:00Z")
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertIn("STOP TIME reached", self.sb.log("run-coatcheck.log"))
        self.assertEqual([c for c in self.sb.kaggle_calls() if c.startswith("b t run")], [])
        for bad in ("not a time", "tomorrow", "2026-10-09 12:00:00", "2026-10-09T12:00:00+00:00"):
            r = self.sb.run("run-coatcheck.sh", STOP_AT=bad)
            self.assertEqual(r.returncode, 1, bad)  # only the form the analysis reads is accepted
        r = self.sb.run("run-coatcheck.sh")
        self.assertNotEqual(r.returncode, 0)  # STOP_AT is required
        self.assertEqual(self.sb.kaggle_calls(), [])

    def test_a_quota_refusal_stops_the_run(self):
        q = self.sb.repo / "results" / "kaggle" / T6 / "1" / "gemini-3.8-flash" / "1" / "q.run.json"
        q.parent.mkdir(parents=True)
        q.write_text('{"subruns": [{"state": "BENCHMARK_TASK_RUN_STATE_ERRORED", "error": "exceeds your available quota"}]}', encoding="utf-8")
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1), CANARY_MODEL="")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("QUOTA refusal", self.sb.log("run-coatcheck.log"))
        self.assertEqual(len([c for c in self.sb.kaggle_calls() if c.startswith("b t run")]), 1)

    def test_a_broken_need_helper_is_not_read_as_done(self):
        bad = self.sb.repo / "results" / "kaggle" / T6 / "1" / "gemini-3.8-flash" / "1" / "broken.run.json"
        bad.parent.mkdir(parents=True)
        bad.write_text("{this is not json", encoding="utf-8")
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1))
        self.assertEqual(r.returncode, 6, r.stdout + r.stderr)
        self.assertNotIn("T6 done", self.sb.log("run-coatcheck.log"))
        self.assertIn("the need helper failed for T6", self.sb.log("run-coatcheck.log"))
        self.assertEqual([c for c in self.sb.kaggle_calls() if c.startswith("b t run")], [])

    def test_a_need_helper_that_prints_nothing_is_not_read_as_done(self):
        (self.sb.upd / "coatcheck_analysis.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")  # succeeds, prints nothing
        self.sb.make_list()
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1))
        self.assertEqual(r.returncode, 6, r.stdout + r.stderr)
        log = self.sb.log("run-coatcheck.log")
        self.assertIn("the need helper printed nothing for T6", log)
        self.assertNotIn("T6 done", log)
        self.assertEqual([c for c in self.sb.kaggle_calls() if c.startswith("b t run")], [])

    def test_an_unreadable_spend_figure_stops_the_run(self):
        (self.sb.repo / "kaggle" / "day_spend.py").write_text("print('oops')\n", encoding="utf-8")
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1))
        self.assertEqual(r.returncode, 7, r.stdout + r.stderr)
        self.assertEqual([c for c in self.sb.kaggle_calls() if c.startswith("b t run")], [])

    def test_a_model_that_never_gets_a_usable_run_is_given_up_on_and_the_run_does_not_say_done(self):
        # every run the fake command writes has 10 logs without a reply: not usable (the limit is 3)
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1), ARMS="T5", EXTRA_TRIES="1", FAKE_ERRORED="10", CANARY_MODEL="")
        self.assertEqual(r.returncode, 8, r.stdout + r.stderr)
        log = self.sb.log("run-coatcheck.log")
        self.assertIn("T5 NOT done: gave up on 4 model(s)", log)
        self.assertNotIn("T5 done", log)
        self.assertEqual(len([c for c in self.sb.kaggle_calls() if c.startswith("b t run")]), 3 + 1)  # planned 3 + 1 extra try

    def test_an_unfilled_forecast_file_stops_the_run(self):
        p = self.sb.upd / "PREDICTIONS.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nStop time (UTC): [FILL]\n", encoding="utf-8", newline="\n")
        self.sb.make_list()
        r = self.sb.run("push-coatcheck.sh")
        self.assertEqual(r.returncode, 10, r.stdout + r.stderr)
        self.assertIn("[FILL] items", self.sb.log("push-coatcheck.log"))
        self.assertEqual(self.sb.kaggle_calls(), [])

    def test_a_changed_file_stops_the_run_before_anything_is_sent(self):
        with open(self.sb.upd / "coatcheck.py", "a", encoding="utf-8") as fh:
            fh.write("\n# changed after the list was made\n")
        for script in ("run-coatcheck.sh", "push-coatcheck.sh"):
            r = self.sb.run(script, STOP_AT=stop_in(1))
            self.assertEqual(r.returncode, 10, script + r.stdout + r.stderr)
        self.assertEqual(self.sb.kaggle_calls(), [])

    def test_a_stale_task_file_stops_the_run(self):
        f = self.sb.upd / "tasks" / f"{T5}.py"
        f.write_text(f.read_text(encoding="utf-8").replace("Does the transcript show", "Does the transcript prove"), encoding="utf-8", newline="\n")
        self.sb.make_list()  # the list is remade, so the hash check passes and the fresh-build check is the one that stops it
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1))
        self.assertEqual(r.returncode, 10, r.stdout + r.stderr)
        self.assertIn("not a fresh build", self.sb.log("run-coatcheck.log"))
        self.assertEqual(self.sb.kaggle_calls(), [])

    def test_a_failing_seal_check_stops_the_run(self):
        (self.sb.repo / "kaggle" / "seal_manifest.py").write_text("print('1 of 32 items changed')\nraise SystemExit(1)\n", encoding="utf-8")
        r = self.sb.run("run-coatcheck.sh", STOP_AT=stop_in(1))
        self.assertEqual(r.returncode, 10, r.stdout + r.stderr)
        self.assertEqual(self.sb.kaggle_calls(), [])

    def test_no_file_list_no_run(self):
        (self.sb.upd / "FILES-SHA256.txt").unlink()
        r = self.sb.run("push-coatcheck.sh")
        self.assertEqual(r.returncode, 10, r.stdout + r.stderr)

    def test_push_sends_the_two_files_and_lists_them(self):
        r = self.sb.run("push-coatcheck.sh")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        calls = self.sb.kaggle_calls()
        up = self.sb.upd.as_posix()
        self.assertEqual(calls[0], f"b t push {T6} -f {up}/tasks/{T6}.py --wait")
        self.assertEqual(calls[1], f"b t push {T5} -f {up}/tasks/{T5}.py --wait")
        self.assertEqual(calls[2], "b t list --name-regex receipt-triplets-t[56] --all")
        self.assertEqual(calls[3:], [f"b t status {T6}", f"b t status {T5}"])
        self.assertEqual(len(calls), 5)
        log = self.sb.log("push-coatcheck.log")
        self.assertIn(f"push {T6} (sha256 ", log)
        self.assertIn(f"pushed {T5}", log)

    def test_a_refused_push_stops(self):
        r = self.sb.run("push-coatcheck.sh", FAKE_PUSH_FAILS="1")
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertEqual(len([c for c in self.sb.kaggle_calls() if c.startswith("b t push")]), 1)

    def test_publish_needs_the_owners_word_and_logs_it(self):
        r = self.sb.run("publish-coatcheck.sh")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.sb.kaggle_calls(), [])
        r = self.sb.run("publish-coatcheck.sh", "Publish.")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.sb.kaggle_calls(), [f"b t publish {T6} --no-publish-backing-notebook",
                                                  f"b t publish {T5} --no-publish-backing-notebook"])
        log = self.sb.log("publish-coatcheck.log")
        self.assertRegex(log, r"publish run \d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ, owner's word: \"Publish\.\"")
        self.assertIn(f"--- {T6}\nTask '{T6}' published successfully.", log)
        r = self.sb.run("publish-coatcheck.sh", "publish notebook", "notebook")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.sb.kaggle_calls()[-2:], [f"b t publish {T6}", f"b t publish {T5}"])
        self.assertIn("notebook publish ", self.sb.log("publish-coatcheck.log"))
        r = self.sb.run("publish-coatcheck.sh", "word", "nonsense")
        self.assertNotEqual(r.returncode, 0)

    def test_task_names_in_the_scripts_equal_the_builders(self):
        text = (HERE / "coatcheck-common.sh").read_text(encoding="utf-8")
        self.assertIn(f"[T5]={bct.task_name('T5')}", text)
        self.assertIn(f"[T6]={bct.task_name('T6')}", text)

    def test_the_scripts_never_call_the_kaggle_command_by_any_name_but_k(self):
        for s in HERE.glob("*.sh"):
            text = s.read_text(encoding="utf-8")
            code = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
            self.assertNotRegex(code, r"(?<![\w$\"{.])kaggle(\.exe)?\s+b\b", s.name)  # only "$K b ..." talks to Kaggle
            self.assertNotIn("curl", code, s.name)
            self.assertNotIn("wget", code, s.name)


if __name__ == "__main__":
    unittest.main()
