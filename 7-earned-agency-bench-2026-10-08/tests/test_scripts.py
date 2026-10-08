"""Script tests: run the command-line tools the way COMMANDS.md says, as separate processes, and read their last lines."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(*args, timeout=600):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, *args], cwd=str(ROOT), capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, (r.stdout + r.stderr)


class Scripts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="eab-script-"))
        cls.code, cls.out = run("bench.py", "dry-run", "--out", str(cls.tmp / "dr"), "--reps", "1", "--workers", "2", "--shim")

    def test_dry_run_ends_with_a_clean_chain(self):
        self.assertEqual(self.code, 0, self.out)
        lines = self.out.strip().splitlines()
        self.assertTrue(lines[-2].startswith("dry run finished (exit 0); "), lines)
        self.assertEqual(lines[-1], "chain verifies")

    def test_dry_run_will_not_overwrite(self):
        code, out = run("bench.py", "dry-run", "--out", str(self.tmp / "dr"), "--reps", "1", "--shim")
        self.assertEqual(code, 2)
        self.assertIn("already exists", out)

    def test_verify_chain_and_a_cut_room(self):
        room = self.tmp / "dr" / "room.jsonl"
        code, out = run("bench.py", "verify-chain", str(room))
        self.assertEqual(code, 0)
        self.assertRegex(out.strip(), r"^chain verifies: \d+ records, hash links, canonical form, blobs and head file all match$")
        cut = self.tmp / "cut"
        (cut).mkdir()
        data = room.read_bytes().split(b"\n")
        (cut / "room.jsonl").write_bytes(b"\n".join(data[:200]) + b"\n")
        (cut / "room.jsonl.head").write_text((room.parent / "room.jsonl.head").read_text())
        code, out = run("bench.py", "verify-chain", str(cut / "room.jsonl"))
        self.assertEqual(code, 4)
        self.assertIn("CHAIN PROBLEMS", out)
        code, out = run("score.py", str(cut / "room.jsonl"))
        self.assertNotEqual(code, 0)
        self.assertIn("refusing to score", out)

    def test_score_prints_the_verdict_and_writes_json(self):
        js = self.tmp / "score.json"
        code, out = run("score.py", str(self.tmp / "dr" / "room.jsonl"), "--json", str(js))
        self.assertEqual(code, 0, out)
        self.assertIn("VERDICT ON EARNED AGENCY: NOT SHOWN (TOO FEW GAMES)", out)
        self.assertIn("games scored: 5; unfinished: 0; left out for breaking a rule: 0", out)
        d = json.loads(js.read_text(encoding="utf-8"))
        self.assertEqual(d["games_scored"], 5)
        self.assertEqual(len(d["units"]), 200)

    def test_estimate_prints_json(self):
        code, out = run("bench.py", "estimate", "--reps", "8", "--workers", "4")
        self.assertEqual(code, 0)
        e = json.loads(out)
        self.assertEqual(e["total"]["calls"], 3920)

    def test_manifest_lines(self):
        code, out = run("bench.py", "manifest")
        self.assertEqual(code, 0)
        lines = out.strip().splitlines()
        self.assertGreaterEqual(len(lines), 20)
        for l in lines:
            self.assertRegex(l, r"^[0-9a-f]{64} \*[\w./-]+$")

    def test_real_run_is_refused_without_the_flag(self):
        code, out = run("bench.py", "run", "--out", str(self.tmp / "nope"), "--cap", "1", "--stop-after-min", "5")
        self.assertEqual(code, 2)
        self.assertFalse((self.tmp / "nope").exists())

    def test_stats_power_and_usage(self):
        code, out = run("stats.py")
        self.assertEqual(code, 2)
        self.assertIn("usage", out)

    def test_check_jobs_ends_consistent(self):
        code, out = run("bench.py", "check-jobs", "--shim")
        self.assertEqual(code, 0, out[-600:])
        self.assertEqual(out.strip().splitlines()[-1], "jobs self-check: all consistent")
        self.assertEqual(sum(1 for l in out.splitlines() if re.search(r"\bok$", l)), 40)


if __name__ == "__main__":
    unittest.main()
