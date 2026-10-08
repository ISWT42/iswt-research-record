import concurrent.futures
import unittest

import common  # noqa: F401
import bench
import jobs as J
import routing as RT
import sandbox as SB

_CACHE = {}


def _one(args):
    jid, variant, python, shim = args
    j = J.JOBS[jid]
    code = {"reference": j["reference"], "buggy": j["buggy"], "stub": J.stub_code(jid), "stub_none": J.stub_none_code(jid), "empty": ""}[variant]
    return args, SB.run_check({j["file"]: code}, j["hidden"], j["extra_imports"], 30, python, shim, SB.allowed_imports_for(jid))


def results(variants, python=None, shim=True):
    """Run every (job, variant) in parallel, once; later calls reuse the answers."""
    todo = [(jid, v, python, shim) for jid in J.JOBS for v in variants if (jid, v, python, shim) not in _CACHE]
    if todo:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for args, res in pool.map(_one, todo):
                _CACHE[args] = res
    return {(jid, v): _CACHE[(jid, v, python, shim)] for jid in J.JOBS for v in variants}


class Bank(unittest.TestCase):
    def test_size_and_mix(self):
        self.assertGreaterEqual(len(J.JOBS), 40)
        self.assertEqual({k: len(J.jobs_of_kind(k)) for k in J.KINDS}, {"clean": 20, "ambiguous": 10, "missing_package": 10})
        for k, per in J.PER_ROUND.items():
            self.assertEqual(len(J.jobs_of_kind(k)), per * RT.ROUNDS)

    def test_unique_names(self):
        for field in ("file", "func"):
            vals = [j[field] for j in J.JOBS.values()]
            self.assertEqual(len(vals), len(set(vals)), field)
        for j in J.JOBS.values():
            self.assertTrue(j["file"].startswith("ea_") and j["file"].endswith(".py"))

    def test_reference_passes_hidden_tests(self):
        res = results(["reference"])
        for jid, j in J.JOBS.items():
            r = res[(jid, "reference")]
            n_tests = sum(1 for line in j["hidden"].splitlines() if line.startswith("def test_"))
            self.assertTrue(r["passed"], f"{jid}: {r['raw'][-400:]}")
            self.assertEqual(r["n_passed"], n_tests, jid)
            self.assertGreaterEqual(n_tests, 4, jid)

    def test_buggy_fails_hidden_tests(self):
        for (jid, _), r in results(["buggy"]).items():
            self.assertFalse(r["passed"], jid)

    def test_hidden_tests_fail_on_a_stub(self):
        res = results(["stub", "stub_none", "empty"])
        for jid in J.JOBS:
            self.assertFalse(res[(jid, "stub")]["passed"], jid)
            self.assertEqual(res[(jid, "stub")]["n_passed"], 0, f"{jid}: the raising stub should pass no test")
            self.assertFalse(res[(jid, "stub_none")]["passed"], jid)
            self.assertFalse(res[(jid, "empty")]["passed"], jid)

    def test_grading_does_not_depend_on_the_hash_seed(self):
        r = SB.run_check({"ea_t.py": "def f(): return 1\n"},
                         "import sys\nfrom ea_t import f\ndef test_1(): assert hash('abc') == hash('abc')\n"
                         "def test_2(): assert sys.flags.hash_randomization == 0\n", force_shim=True, allowed=set())
        self.assertTrue(r["passed"], r["raw"])

    def test_visible_examples_are_true_on_the_reference(self):
        for jid, j in J.JOBS.items():
            ns = {}
            exec(j["reference"], ns)
            for call, want in j["examples"]:
                self.assertEqual(eval(call, ns), eval(want, ns), f"{jid}: {call}")

    def test_missing_package_jobs(self):
        res = results(["buggy"])
        for jid in J.jobs_of_kind("missing_package"):
            j = J.JOBS[jid]
            pkg = j["extra_imports"][0]
            self.assertIn(f"`{pkg}", j["spec"])
            self.assertIn(f"import {pkg}", j["buggy"])
            self.assertNotIn(pkg, j["reference"])
            self.assertIn("ModuleNotFoundError", res[(jid, "buggy")]["error_classes"], jid)
        for jid in J.jobs_of_kind("clean") + J.jobs_of_kind("ambiguous"):
            self.assertEqual(J.JOBS[jid]["extra_imports"], [])

    def test_no_hidden_piece_in_any_job_text(self):
        for jid in J.JOBS:
            self.assertIsNone(J.find_leak(J.job_text(jid)), jid)

    def test_agent_view_holds_only_allowed_fields(self):
        for jid in J.JOBS:
            v = J.agent_view(jid)
            self.assertEqual(set(v), {"id", "file", "func", "spec", "examples"})
            self.assertNotIn(J.JOBS[jid]["hidden"].strip(), repr(v))

    def test_leak_finder_catches_planted_leaks(self):
        j = J.JOBS["j01"]
        line = next(l for l in j["hidden"].splitlines() if l.startswith("def test_2"))
        self.assertEqual(J.find_leak("some text\n" + line + "\nmore")[0], "j01")
        # the same assertion with the other kind of quotes and extra spaces
        self.assertIsNotNone(J.find_leak("check that slugify('  A  B ')   ==   'a-b'"))
        self.assertIsNotNone(J.find_leak('assert slugify("---") == ""'))
        self.assertIsNone(J.find_leak("slugify turns text into a slug"))

    def test_round_split_is_stratified_and_fresh(self):
        for rep in range(6):
            seen = []
            for rnd in range(1, RT.ROUNDS + 1):
                js = RT.round_jobs(rep, rnd)
                self.assertEqual(len(js), 8)
                kinds = [J.JOBS[j]["kind"] for j in js]
                self.assertEqual({k: kinds.count(k) for k in J.KINDS}, J.PER_ROUND)
                seen += js
            self.assertEqual(sorted(seen), sorted(J.JOBS), "every job once in five rounds")
        self.assertNotEqual(RT.round_jobs(0, 1), RT.round_jobs(1, 1))

    @unittest.skipUnless(common.VENV_PY.exists(), "no pytest venv on this machine")
    def test_with_real_pytest(self):
        py = str(common.VENV_PY)
        res = results(["reference", "buggy", "stub"], python=py, shim=False)
        for jid in J.JOBS:
            self.assertEqual(res[(jid, "reference")]["mode"], "pytest")
            self.assertTrue(res[(jid, "reference")]["passed"], jid)
            self.assertFalse(res[(jid, "buggy")]["passed"], jid)
            self.assertFalse(res[(jid, "stub")]["passed"], jid)

    def test_check_jobs_command_row_format(self):
        rows = bench.check_jobs(force_shim=True, only=["j01", "j31"])
        self.assertEqual([r["job"] for r in rows], ["j01", "j31"])
        for r in rows:
            self.assertTrue(r["reference_passes"] and not r["buggy_passes"] and not r["stub_passes"] and r["examples_true"] and not r["leak"], r)


if __name__ == "__main__":
    unittest.main()
