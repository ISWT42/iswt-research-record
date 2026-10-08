import os
import tempfile
import threading
import unittest
from pathlib import Path

import common  # noqa: F401
import room as RM
import sandbox as SB


def new_room(**kw):
    d = tempfile.mkdtemp(prefix="eab-room-")
    return RM.Room(Path(d) / "room.jsonl", fsync=False, **kw), Path(d)


class Chain(unittest.TestCase):
    def fill(self, n=6):
        r, d = new_room()
        for i in range(n):
            b = r.put_blob(f"blob {i}")
            r.append({"type": "x", "i": i, "blobs": [b]})
        return r, d

    def test_clean_chain_verifies(self):
        r, d = self.fill()
        ok, problems, n = RM.verify_chain(d / "room.jsonl")
        self.assertTrue(ok, problems)
        self.assertEqual(n, 6)

    def test_edit_is_caught(self):
        r, d = self.fill()
        p = d / "room.jsonl"
        p.write_bytes(p.read_bytes().replace(b'"i":2', b'"i":9'))
        self.assertFalse(RM.verify_chain(p)[0])

    def test_cut_off_newest_lines_is_caught(self):
        r, d = self.fill()
        p = d / "room.jsonl"
        lines = p.read_bytes().split(b"\n")
        p.write_bytes(b"\n".join(lines[:3]) + b"\n")
        self.assertFalse(RM.verify_chain(p)[0])

    def test_reordering_is_caught(self):
        r, d = self.fill()
        p = d / "room.jsonl"
        lines = p.read_bytes().split(b"\n")
        lines[1], lines[2] = lines[2], lines[1]
        p.write_bytes(b"\n".join(lines))
        self.assertFalse(RM.verify_chain(p)[0])

    def test_changed_blob_is_caught(self):
        r, d = self.fill()
        blob = next((d / "blobs").glob("*.txt"))
        blob.write_text("something else")
        ok, problems, _ = RM.verify_chain(d / "room.jsonl")
        self.assertFalse(ok)
        self.assertTrue(any("blob" in x for x in problems))

    def test_room_refuses_a_broken_file_and_reopens_a_good_one(self):
        r, d = self.fill()
        again = RM.Room(d / "room.jsonl", fsync=False)
        self.assertEqual(len(again.records()), 6)
        again.append({"type": "y"})
        self.assertTrue(RM.verify_chain(d / "room.jsonl")[0])
        p = d / "room.jsonl"
        p.write_bytes(p.read_bytes().replace(b'"i":2', b'"i":9'))
        with self.assertRaises(RM.ChainError):
            RM.Room(p, fsync=False)

    def test_a_file_the_system_refuses_for_a_moment_is_tried_again(self):
        from unittest import mock
        r, d = new_room()
        real, state = open, {"n": 0}

        def flaky(path, mode="r", *a, **k):
            if str(path).endswith("room.jsonl") and mode == "ab" and state["n"] < 2:
                state["n"] += 1
                raise PermissionError("busy")
            return real(path, mode, *a, **k)

        with mock.patch.object(RM, "open", flaky, create=True):
            r.append({"type": "x"})
        self.assertEqual(state["n"], 2)
        self.assertEqual(len(r.records()), 1)
        self.assertTrue(RM.verify_chain(d / "room.jsonl")[0])

        def always(path, mode="r", *a, **k):
            if mode == "ab":
                raise PermissionError("busy")
            return real(path, mode, *a, **k)

        with mock.patch.object(RM, "open", always, create=True):
            with self.assertRaises(PermissionError):
                r.append({"type": "y"})
        self.assertEqual(len(r.records()), 1)             # nothing half-written

    def test_many_threads_write_one_clean_chain(self):
        r, d = new_room()

        def work(k):
            for i in range(60):
                r.append({"type": "t", "run": f"g{k}", "i": i, "blobs": [r.put_blob(f"{k}-{i % 5}")]})

        ts = [threading.Thread(target=work, args=(k,)) for k in range(8)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        ok, problems, n = RM.verify_chain(d / "room.jsonl")
        self.assertTrue(ok, problems)
        self.assertEqual(n, 480)
        self.assertEqual(len(r.records_of("g3")), 60)

    def test_valid_records_keep_only_the_last_complete_attempt(self):
        recs = []

        def add(t, step=None, **kw):
            recs.append(dict(type=t, step=step, seq=len(recs) + 1, **kw))

        add("game_start")
        add("step_start", "a"); add("call", "a", n=1)           # crashed attempt of step a
        add("step_start", "a"); add("call", "a", n=2); add("step_done", "a")
        add("step_start", "b"); add("call", "b", n=3)           # never finished
        v = RM.valid_records(recs)
        self.assertEqual([r.get("n") for r in v if r["type"] == "call"], [2])
        self.assertEqual(RM.dropped_attempts(recs), 2)


class Paths(unittest.TestCase):
    def test_accepts_plain_names(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(SB.safe_join(d, "ea_a.py").name, "ea_a.py")

    def test_refuses_planted_escapes(self):
        with tempfile.TemporaryDirectory() as d:
            for bad in ["../x.py", "/abs.py", "C:\\x.py", "C:/x.py", "a\\b.py", "sub/../../x.py", ".hidden.py", "", "a//b.py", "..", "a/../b.py"]:
                with self.assertRaises(SB.SandboxError, msg=bad):
                    SB.safe_join(d, bad)

    def test_run_check_will_not_write_outside_the_sandbox(self):
        outside = Path(tempfile.gettempdir()) / "eab_evil_marker.py"
        outside.unlink(missing_ok=True)
        with self.assertRaises(SB.SandboxError):
            SB.run_check({"../eab_evil_marker.py": "x = 1\n"}, "def test_1(): assert True\n", force_shim=True)
        self.assertFalse(outside.exists())


class Screen(unittest.TestCase):
    ALLOWED = {"re", "collections"}

    def test_blocks(self):
        for code in ["import os\n", "import subprocess\n", "from os import path\n", "x = __import__('os')\n", "open('f')\n",
                     "eval('1')\n", "exec('1')\n", "().__class__.__mro__\n", "import socket\n", "from . import x\n", "import fastcount\n"]:
            ok, why = SB.screen_code(code, self.ALLOWED)
            self.assertFalse(ok, code)
            self.assertTrue(why)

    def test_allows_control(self):
        for code in ["import re\n", "from collections import Counter\n", "def f(x):\n    return {x: [x]}\n"]:
            self.assertTrue(SB.screen_code(code, self.ALLOWED)[0], code)

    def test_a_missing_package_passes_the_screen_when_the_job_lists_it(self):
        self.assertTrue(SB.screen_code("import fastcount\n", self.ALLOWED | {"fastcount"})[0])

    def test_refused_code_is_never_run(self):
        marker = Path(tempfile.gettempdir()) / "eab_screen_marker.txt"
        marker.unlink(missing_ok=True)
        code = f"import os\nopen(r'{marker}', 'w').write('ran')\n"
        r = SB.run_check({"ea_x.py": code}, "from ea_x import *\ndef test_1(): assert True\n", force_shim=True, allowed={"ea_x"})
        self.assertTrue(r["refused"])
        self.assertFalse(r["passed"])
        self.assertFalse(marker.exists())


class Run(unittest.TestCase):
    def go(self, code, hidden, **kw):
        return SB.run_check({"ea_t.py": code}, hidden, force_shim=True, allowed={"re"}, **kw)

    def test_pass_and_fail(self):
        self.assertTrue(self.go("def f(): return 1\n", "from ea_t import f\ndef test_1(): assert f() == 1\n")["passed"])
        r = self.go("def f(): return 2\n", "from ea_t import f\ndef test_1(): assert f() == 1\n")
        self.assertFalse(r["passed"])
        self.assertEqual(r["n_failed"], 1)

    def test_no_test_is_not_a_pass(self):
        self.assertFalse(self.go("x = 1\n", "from ea_t import x\n")["passed"])

    def test_timeout(self):
        r = self.go("def f():\n    while True:\n        pass\n", "from ea_t import f\ndef test_1(): f()\n", timeout=2)
        self.assertTrue(r["timed_out"])
        self.assertFalse(r["passed"])

    def test_network_is_blocked(self):
        # a refused connection is also an OSError, so the test looks for OUR message, which only the block can give
        hidden = '''
import socket
from ea_t import f
def _msg(fn, *a):
    try:
        fn(*a)
    except OSError as e:
        return str(e)
    return 'no error'
def test_1(): assert 'network disabled' in _msg(socket.create_connection, ('127.0.0.1', 9))
def test_2(): assert 'network disabled' in _msg(socket.getaddrinfo, 'localhost', 80)
def test_3(): assert 'network disabled' in _msg(socket.socket().connect, ('127.0.0.1', 9))
def test_4(): assert 'network disabled' in _msg(socket.socket().connect_ex, ('127.0.0.1', 9))
def test_5(): assert [f.__name__ for f in (socket.create_connection, socket.getaddrinfo, socket.socket.connect, socket.socket.connect_ex)] == ['_blocked'] * 4
'''
        r = self.go("def f(): return 1\n", hidden)
        self.assertTrue(r["passed"], r["raw"])

    def test_the_sandbox_does_not_inherit_our_environment(self):
        os.environ["EAB_FAKE_TEST_VALUE"] = "should-not-reach-the-sandbox"
        try:
            hidden = "import os\nfrom ea_t import f\ndef test_1(): assert 'EAB_FAKE_TEST_VALUE' not in os.environ\n"
            self.assertTrue(self.go("def f(): return 1\n", hidden)["passed"])
        finally:
            del os.environ["EAB_FAKE_TEST_VALUE"]

    def test_check_summary_never_holds_assertion_text(self):
        hidden = "from ea_t import f\ndef test_1(): assert f() == 'SECRET_EXPECTED_VALUE_123'\n"
        r = self.go("def f(): return 'no'\n", hidden)
        s = SB.summarize_check(r)
        self.assertNotIn("SECRET_EXPECTED_VALUE_123", s)
        self.assertNotIn("assert ", s)
        self.assertIn("AssertionError", s)

    def test_missing_package_shows_as_import_error(self):
        r = SB.run_check({"ea_t.py": "import fastcount\ndef f(): return 1\n"}, "from ea_t import f\ndef test_1(): assert f() == 1\n",
                         force_shim=True, allowed={"fastcount"})
        self.assertFalse(r["passed"])
        self.assertIn("ModuleNotFoundError", r["error_classes"])


if __name__ == "__main__":
    unittest.main()
