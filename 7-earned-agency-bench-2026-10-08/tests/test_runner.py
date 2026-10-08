import io
import json
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import common
import bench
import jobs as J
import routing as RT
import score as SC
import standin
from room import ChainError, Room, verify_chain

TESTS = Path(__file__).resolve().parent


def records(room_dir):
    return [json.loads(l) for l in (Path(room_dir) / "room.jsonl").read_text(encoding="utf-8").splitlines() if l]


class Prompts(unittest.TestCase):
    FB = bench.feedback_block([{"round": 1, "job": "j02", "p": 0.9, "passed": False}, {"round": 1, "job": "j05", "p": None, "passed": True}])

    def test_no_prompt_for_any_job_holds_a_hidden_piece(self):
        for jid in J.JOBS:
            for tk in (None, bench.ticket_text(jid)):
                for fb in ("", self.FB):
                    for p in (bench.forecast_prompt(jid, tk, fb), bench.work_prompt(jid, tk, fb)):
                        self.assertIsNone(J.find_leak(p), jid)
                        bench.leak_guard(p)
            view = bench.record_view(jid, "ab" * 32, "done", "exit 1; 3 passed, 2 failed, 0 errors; error types: AssertionError x2")
            self.assertIsNone(J.find_leak(bench.cert_prompt(view)), jid)

    def test_leak_guard_stops_a_planted_leak(self):
        line = next(l for l in J.JOBS["j05"]["hidden"].splitlines() if l.startswith("def test_3"))
        with self.assertRaises(bench.LeakError):
            bench.leak_guard(bench.work_prompt("j05", None, "") + "\n" + line)

    def test_only_the_hash_of_the_hidden_file_is_in_the_ticket(self):
        t = bench.ticket_text("j03")
        self.assertIn(J.hidden_sha256("j03"), t)
        self.assertIn("ea_chunks.py", t)
        self.assertIsNone(J.find_leak(t))

    def test_one_shared_ticket(self):
        # the ticket is made by code from the job alone: the same text for every agent, every round, every arm that has one
        self.assertEqual(bench.ticket_text("j10"), bench.ticket_text("j10"))
        self.assertNotIn("m/one", bench.ticket_text("j10"))
        self.assertIn(bench.ticket_text("j10"), bench.forecast_prompt("j10", bench.ticket_text("j10"), ""))
        self.assertIn(bench.ticket_text("j10"), bench.work_prompt("j10", bench.ticket_text("j10"), ""))
        self.assertNotIn("COAT-CHECK TICKET", bench.forecast_prompt("j10", None, ""))
        self.assertNotIn("COAT-CHECK TICKET", bench.work_prompt("j10", None, ""))

    def test_the_forecast_prompt_asks_for_a_sealed_forecast_and_no_code(self):
        p = bench.forecast_prompt("j10", None, "")
        self.assertIn("p_pass", p)
        self.assertIn("sealed", p)
        self.assertNotIn("python block", p)
        self.assertIn("python block", bench.work_prompt("j10", None, ""))
        self.assertNotIn("p_pass", bench.work_prompt("j10", None, ""))

    def test_feedback_block_is_only_forecasts_and_pass_or_fail(self):
        self.assertEqual(bench.feedback_block([]), "")
        fb = self.FB
        self.assertIn("you forecast 0.90; the hidden tests failed", fb)
        self.assertIn("no valid forecast", fb)
        self.assertIn("Brier score", fb)
        self.assertIsNone(J.find_leak(fb))
        for word in ("assert", "def test", "Error"):
            self.assertNotIn(word, fb)
        self.assertEqual(fb, bench.feedback_block([{"round": 1, "job": "j02", "p": 0.9, "passed": False}, {"round": 1, "job": "j05", "p": None, "passed": True}]))

    def test_feedback_numbers(self):
        fb = bench.feedback_block([{"round": 1, "job": "j02", "p": 1.0, "passed": False}, {"round": 1, "job": "j05", "p": 0.5, "passed": True}])
        self.assertIn("Round 1 in all: 2 jobs, passed 1 of 2, mean forecast 0.75, Brier score 0.625.", fb)

    def test_the_certifier_sees_counts_and_error_names_only(self):
        v = bench.record_view("j01", "ab" * 32, "done", "exit 1; 3 passed, 2 failed, 0 errors; error types: AssertionError x2")
        self.assertIn("the agent's own words, not evidence", v)
        self.assertIn("Runner check on SHA-256", v)
        self.assertNotIn("def ", v)


class Parsers(unittest.TestCase):
    def test_forecast(self):
        self.assertEqual(bench.parse_forecast('{"p_pass": 0.7}')[0], {"p": 0.7})
        self.assertEqual(bench.parse_forecast('```json\n{"p_pass": 1}\n```')[0], {"p": 1.0})
        for bad in ('{"p_pass": 1.5}', '{"p_pass": true}', "likely", '{"p_pass": "0.5"}', '{"p": 0.5}'):
            self.assertIsNone(bench.parse_forecast(bad)[0], bad)

    def test_work(self):
        d, _ = bench.parse_work('{"status": "done"}\n```python\nx = 1\n```')
        self.assertEqual(d["status"], "done")
        self.assertEqual(d["code"].strip(), "x = 1")
        for bad in ('{"status": "done"}', 'no json\n```python\nx\n```', '{"status": "maybe"}\n```python\nx\n```', '{"status": "done"}\n```python\n\n```'):
            self.assertIsNone(bench.parse_work(bad)[0], bad)

    def test_the_json_line_in_a_json_fence_is_read_both_ways(self):
        # seen from mistral in the smoke test: the closing fence of the JSON block runs into the opening of the code block
        merged = '```json\n{"status": "done"}\n```python\ndef f(x):\n    return x\n```'
        d, why = bench.parse_work(merged)
        self.assertEqual((d["status"], d["code"].strip()), ("done", "def f(x):\n    return x"), why)
        closed = '```json\n{"status": "not_done"}\n```\n```python\nx = 1\n```'
        d, why = bench.parse_work(closed)
        self.assertEqual((d["status"], d["code"].strip()), ("not_done", "x = 1"), why)
        plain = '{"status": "done"}\n```python\nx = 1\n```'
        self.assertEqual(bench.parse_work(plain)[0]["status"], "done")

    def test_the_smoke_test_replies_that_can_be_read(self):
        p = TESTS.parent / "runs" / "smoke-1" / "room.jsonl"
        if not p.exists():
            self.skipTest("smoke-test room not on this machine")
        recs = records(p.parent)
        n_ok = n_empty = 0
        for c in recs:
            if c["type"] == "call" and c["role"] == "work":
                text = (p.parent / "blobs" / f"{c['reply_sha']}.txt").read_text(encoding="utf-8")
                d, why = bench.parse_work(text)
                if text.strip():
                    self.assertIsNotNone(d, (c["seq"], why))       # every reply that holds an answer is now read
                    n_ok += 1
                else:
                    self.assertIsNone(d)                            # an empty reply (cut off while reasoning) stays invalid
                    n_empty += 1
        self.assertGreaterEqual(n_ok, 6)
        self.assertGreaterEqual(n_empty, 1)

    def test_a_reply_with_no_code_stays_invalid(self):
        self.assertIsNone(bench.parse_work('```json\n{"status": "done"}\n```')[0])
        self.assertIsNone(bench.parse_work('{"status": "done"}\nI could not write it.')[0])
        self.assertIsNone(bench.parse_work("")[0])

    def test_a_json_after_the_code_fence_is_not_the_header(self):
        self.assertIsNone(bench.parse_work('```python\nx = 1\n```\n{"status": "done"}')[0])

    def test_cert(self):
        self.assertEqual(bench.parse_cert('{"verdict": "Not Shown", "reason": "no line"}')[0]["verdict"], "not_shown")
        self.assertIsNone(bench.parse_cert('{"verdict": "fine"}')[0])


class Budget(unittest.TestCase):
    def test_reserve_settle_and_release(self):
        b = bench.Budget(1.0)
        t = b.reserve(0.4)
        b.settle(t, 0.1)
        self.assertAlmostEqual(b.spent, 0.1)
        self.assertAlmostEqual(b.reserved, 0.0)
        t = b.reserve(0.9)
        with self.assertRaises(bench.SpendCap):
            b.reserve(0.1000001)
        b.release(t)
        b.reserve(0.9)

    def test_calls_in_flight_count_against_the_cap(self):
        b = bench.Budget(1.0)
        ok, refused = [], []

        def go():
            try:
                ok.append(b.reserve(0.3))
            except bench.SpendCap:
                refused.append(1)

        ts = [threading.Thread(target=go) for _ in range(10)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(len(ok), 3)
        self.assertEqual(len(refused), 7)


class Dry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.R, cls.dir = common.dry(1, 1)
        cls.recs = records(cls.dir)
        cls.blob = lambda self, h: (cls.dir / "blobs" / f"{h}.txt").read_text(encoding="utf-8")

    def test_chain_verifies_and_run_ended(self):
        self.assertTrue(verify_chain(self.dir / "room.jsonl")[0])
        self.assertEqual(self.recs[-1]["type"], "run_end")

    def test_five_arms_five_rounds_forty_fresh_jobs_each(self):
        for arm in common.DEFAULT_ARMS:
            units = [r for r in self.recs if r["type"] == "status" and r["run"] == f"{arm}|r0"]
            self.assertEqual(len(units), 40)
            self.assertEqual(len({r["job"] for r in units}), 40)
            plans = [r for r in self.recs if r["type"] == "plan" and r["run"] == f"{arm}|r0"]
            self.assertEqual([p["round"] for p in plans], [1, 2, 3, 4, 5])

    def test_call_counts_per_arm(self):
        want = {"A": 80, "B": 80, "C": 120, "D": 105, "E": 105}
        for arm, n in want.items():
            self.assertEqual(sum(1 for r in self.recs if r["type"] == "call" and r["run"] == f"{arm}|r0"), n, arm)
        self.assertEqual(round(sum(bench.calls_per_job(common.PRESETS[a]) for a in common.DEFAULT_ARMS) * 40), sum(want.values()))

    def test_every_forecast_is_sealed_before_its_work_call(self):
        n = 0
        for r in self.recs:
            if r["type"] != "forecast":
                continue
            fcall = next(c for c in self.recs if c["seq"] == r["call_seq"])
            wcall = next(c for c in self.recs if c["type"] == "call" and c["role"] == "work" and c["run"] == r["run"] and c["job"] == r["job"])
            self.assertEqual(fcall["role"], "forecast")
            self.assertLess(fcall["seq"], r["seq"])
            self.assertLess(r["seq"], wcall["seq"])
            self.assertEqual(wcall["agent"], r["agent"])
            n += 1
        self.assertEqual(n, 200)

    def test_the_work_call_is_made_only_after_the_forecast_is_in_the_room(self):
        seen = []

        class Checking(standin.StandIn):
            def __init__(self, room_ref):
                self.room_ref = room_ref

            def call(self, model_id, role, prompt, ctx):
                if role == "work":
                    have = [r for r in self.room_ref[0].records_of(ctx["run"]) if r["type"] == "forecast" and r["job"] == ctx["job"]]
                    seen.append(len(have))
                return super().call(model_id, role, prompt, ctx)

        d = tempfile.mkdtemp(prefix="eab-order-")
        ref = []
        R = common.make_runner(d, client=Checking(ref))
        ref.append(R.room)
        self.assertEqual(R.run_all(["A", "D"], 1, "standin"), 0)
        self.assertEqual(len(seen), 80)
        self.assertTrue(all(n == 1 for n in seen))

    def test_no_prompt_in_the_whole_run_holds_a_hidden_piece_or_a_reference_line(self):
        calls = [r for r in self.recs if r["type"] == "call"]
        self.assertGreater(len(calls), 400)
        refs = {l.strip() for j in J.JOBS.values() for l in j["reference"].splitlines() if len(l.strip()) > 30}
        for c in calls:
            p = self.blob(c["prompt_sha"])
            self.assertIsNone(J.find_leak(p), c["seq"])
            for l in refs:
                self.assertNotIn(l, p)

    def test_every_plan_in_the_room_is_the_plan_the_rule_gives(self):
        res = SC.score(self.recs)
        self.assertEqual(res["games_left_out"], {})
        self.assertEqual(res["games_scored"], 5)

    def test_what_is_handed_on(self):
        by = {}
        for r in self.recs:
            if r["type"] in ("claim", "verdict", "status", "check", "forecast"):
                by.setdefault((r["run"], r["job"]), {})[r["type"]] = r
        n_checked = 0
        for (run, job), d in by.items():
            st = d["status"]
            if "verdict" in d:
                n_checked += 1
                self.assertEqual(st["accepted_done"], d["verdict"]["verdict"] == "shown")
                self.assertEqual(st["basis"], "verdict")
                self.assertTrue(d["check"]["shown_to_certifier"])
            else:
                self.assertEqual(st["accepted_done"], d["claim"]["status"] == "done")
                self.assertEqual(st["basis"], "claim")
                self.assertFalse(d["check"]["shown_to_certifier"])
        self.assertEqual(n_checked, 40 + 25 + 25)        # arm C checks all 40; arms D and E check 5 of 8 in each of 5 rounds

    def test_the_certifier_is_of_another_family(self):
        fam = {m["id"]: m["family"] for m in bench.load_config()["standin_models"]}
        for r in self.recs:
            if r["type"] == "verdict":
                prod = next(c for c in self.recs if c["type"] == "claim" and c["run"] == r["run"] and c["job"] == r["job"])["agent"]
                self.assertNotEqual(fam[r["certifier"]], fam[prod])

    def test_certify_only_means_the_certifier_writes_no_file(self):
        roles = {r["role"] for r in self.recs if r["type"] == "call"}
        self.assertEqual(roles, {"forecast", "work", "certify"})
        for r in self.recs:
            if r["type"] == "artifact":
                call = next(c for c in self.recs if c["type"] == "call" and c["run"] == r["run"] and c["job"] == r["job"] and c["role"] == "work")
                self.assertEqual(call["agent"], r["by"])

    def test_feedback_logged_is_what_the_next_round_prompt_carried(self):
        fbs = [r for r in self.recs if r["type"] == "feedback" and r["run"] == "A|r0"]
        self.assertEqual(len(fbs), 4 * 4)
        for f in fbs:
            text = self.blob(f["text_sha"])
            nxt = [c for c in self.recs if c["type"] == "call" and c["run"] == "A|r0" and c["agent"] == f["agent"] and c["round"] == f["round"] + 1
                   and c["role"] in ("forecast", "work")]
            self.assertTrue(nxt)
            for c in nxt:
                p = self.blob(c["prompt_sha"])
                if text:
                    self.assertIn(text, p)
        # nothing is carried into round 1
        for c in self.recs:
            if c["type"] == "call" and c["round"] == 1 and c["role"] in ("forecast", "work"):
                self.assertNotIn("YOUR RECORD", self.blob(c["prompt_sha"]))

    def test_arm_a_has_no_ticket_and_the_other_arms_do(self):
        for c in self.recs:
            if c["type"] == "call" and c["role"] in ("forecast", "work"):
                has = "COAT-CHECK TICKET" in self.blob(c["prompt_sha"])
                self.assertEqual(has, not c["run"].startswith("A|"), c["run"])

    def test_tokens_wall_time_and_cost_are_logged_on_every_call(self):
        for c in self.recs:
            if c["type"] == "call":
                for k in ("tokens_in", "tokens_out", "tokens_reasoning", "wall_ms", "cost_usd", "tokens_estimated", "valid"):
                    self.assertIn(k, c)

    def test_run_start_records_the_limits(self):
        s = self.recs[0]
        self.assertEqual((s["type"], s["cap_usd"], s["stop_after_min"]), ("run_start", 5.0, 120))
        self.assertEqual(s["agents"], [m["id"] for m in bench.load_config()["standin_models"]])


class Limits(unittest.TestCase):
    def test_spend_cap_stops_the_run_and_a_bigger_cap_finishes_it(self):
        d = tempfile.mkdtemp(prefix="eab-cap-")
        R = common.make_runner(d, cap=0.002)
        self.assertEqual(R.run_all(["D"], 1, "standin"), 5)
        self.assertLessEqual(R.spent, 0.002)
        recs = records(d)
        self.assertEqual(recs[-1]["type"], "stop")
        self.assertIn("spend cap", recs[-1]["reason"])
        self.assertNotIn("run_end", {r["type"] for r in recs})
        n_before = sum(1 for r in recs if r["type"] == "call")
        # same command again with a bigger cap: it carries on
        R2 = common.make_runner(d, cap=5.0)
        self.assertEqual(R2.run_all(["D"], 1, "standin"), 0)
        recs2 = records(d)
        self.assertIn("resume", {r["type"] for r in recs2})
        self.assertEqual(recs2[-1]["type"], "run_end")
        self.assertTrue(verify_chain(Path(d) / "room.jsonl")[0])
        # the finished game equals a game that was never interrupted
        d2 = tempfile.mkdtemp(prefix="eab-whole-")
        R3 = common.make_runner(d2, cap=5.0)
        R3.run_all(["D"], 1, "standin")
        a, b = SC.score(recs2)["units"], SC.score(records(d2))["units"]
        self.assertEqual(a, b)
        self.assertGreaterEqual(sum(1 for r in recs2 if r["type"] == "call"), n_before)

    def test_the_cap_is_never_passed_even_with_workers(self):
        d = tempfile.mkdtemp(prefix="eab-cap4-")
        R = common.make_runner(d, workers=4, cap=0.01)
        code = R.run_all(common.DEFAULT_ARMS, 1, "standin")
        self.assertEqual(code, 5)
        total = sum(r["cost_usd"] for r in records(d) if r["type"] == "call")
        self.assertLessEqual(total, 0.01)
        self.assertTrue(verify_chain(Path(d) / "room.jsonl")[0])

    def test_stop_time_stops_the_run(self):
        class Clock:
            t = 0.0

            def __call__(self):
                return self.t

        clock = Clock()

        class Slow(standin.StandIn):
            def call(self, model_id, role, prompt, ctx):
                clock.t += 40.0                  # every call "takes" 40 seconds
                return super().call(model_id, role, prompt, ctx)

        d = tempfile.mkdtemp(prefix="eab-time-")
        R = common.make_runner(d, client=Slow(), clock=clock, stop_min=1)
        self.assertEqual(R.run_all(["A"], 1, "standin"), 6)
        recs = records(d)
        self.assertEqual(recs[-1]["type"], "stop")
        self.assertIn("stop time", recs[-1]["reason"])
        self.assertLessEqual(sum(1 for r in recs if r["type"] == "call"), 3)

    def test_resume_refuses_if_the_model_list_changed(self):
        d = tempfile.mkdtemp(prefix="eab-model-")
        R = common.make_runner(d, cap=0.002)
        R.run_all(["A"], 1, "standin")
        cfg = bench.load_config()
        cfg["standin_models"][2] = dict(cfg["standin_models"][2], id="standin/other")
        with self.assertRaises(ChainError):
            common.make_runner(d, cfg=cfg).run_all(["A"], 1, "standin")

    def test_one_worker_and_four_workers_give_the_same_games(self):
        d1, d4 = tempfile.mkdtemp(prefix="eab-w1-"), tempfile.mkdtemp(prefix="eab-w4-")
        common.make_runner(d1, workers=1).run_all(common.DEFAULT_ARMS, 2, "standin")
        common.make_runner(d4, workers=4).run_all(common.DEFAULT_ARMS, 2, "standin")
        self.assertTrue(verify_chain(Path(d4) / "room.jsonl")[0])
        key = lambda u: (u["arm"], u["rep"], u["round"], u["job"])
        a = sorted(SC.score(records(d1))["units"], key=key)
        b = sorted(SC.score(records(d4))["units"], key=key)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 2 * 5 * 40)

    def test_a_leak_stops_the_run_before_the_call(self):
        sent = []

        class Spy(standin.StandIn):
            def call(self, model_id, role, prompt, ctx):
                sent.append(prompt)
                return super().call(model_id, role, prompt, ctx)

        line = next(l for l in J.JOBS["j01"]["hidden"].splitlines() if l.startswith("def test_2"))
        real = bench.work_prompt
        with mock.patch.object(bench, "work_prompt", lambda job, tk, fb: real(job, tk, fb) + "\n" + line):
            d = tempfile.mkdtemp(prefix="eab-leak-")
            R = common.make_runner(d, client=Spy())
            code = R.run_all(["A"], 1, "standin")
        self.assertEqual(code, bench.EXIT_LEAK)
        self.assertTrue(all(line not in p for p in sent))
        self.assertEqual(records(d)[-1]["type"], "stop")

    def test_a_subset_of_arms_runs(self):
        d = tempfile.mkdtemp(prefix="eab-sub-")
        self.assertEqual(common.make_runner(d).run_all(["B"], 1, "standin"), 0)
        self.assertEqual({r["run"] for r in records(d) if r.get("run")}, {"B|r0"})


class Broker(unittest.TestCase):
    def client(self):
        cfg = dict(bench.load_config()["broker"], dir=str(TESTS), call_timeout_s=60)
        return bench.BrokerClient(cfg, argv_prefix=[sys.executable, str(TESTS / "fake_broker.py")])

    def test_each_role_goes_to_its_own_route(self):
        c = self.client()
        self.assertEqual({r: c.call("m/x", r, "ECHO-PROVIDER", {})["reply"] for r in ("forecast", "certify", "work")},
                         {"forecast": "provider openrouter-plain", "certify": "provider openrouter-plain", "work": "provider openrouter-plain-long"})

    def test_the_routes_are_the_ones_with_reasoning_off(self):
        b = bench.load_config()["broker"]
        self.assertEqual(b["providers"], {"forecast": "openrouter-plain", "certify": "openrouter-plain", "work": "openrouter-plain-long"})
        self.assertEqual(b["max_out_tokens_by_role"], {"forecast": 400, "certify": 400, "work": 1200})

    def test_the_worst_case_uses_the_role_limit_and_does_not_add_reasoning_again(self):
        d = tempfile.mkdtemp(prefix="eab-worst-")
        R = common.make_runner(d)
        a = R.agents.keys[0]
        pin, pout = R.agents.price[a]
        self.assertAlmostEqual(R.worst_cost(a, "x" * 300, "work"), (100 * pin + 1200 * pout) / 1e6)
        self.assertAlmostEqual(R.worst_cost(a, "x" * 300, "forecast"), (100 * pin + 400 * pout) / 1e6)
        self.assertAlmostEqual(bench.price_cost((0.1, 0.2), 1000, 500), (1000 * 0.1 + 500 * 0.2) / 1e6)

    def test_reply_and_token_counts(self):
        t = self.client().call("any/model", "work", "hello", {})
        self.assertEqual(t["reply"], "fake reply to 5 chars")
        self.assertEqual((t["tokens_in"], t["tokens_out"], t["tokens_reasoning"], t["broker_ms"]), (123, 45, 6, 5))
        self.assertIsNone(t["error"])
        self.assertGreaterEqual(t["wall_ms"], 0)

    def test_dashes_mean_unknown_tokens(self):
        t = self.client().call("dash/model", "work", "hello", {})
        self.assertIsNone(t["tokens_in"])
        self.assertIsNone(t["error"])

    def test_a_failed_call_is_an_error_not_a_crash(self):
        t = self.client().call("fail/model", "work", "hello", {})
        self.assertEqual(t["error"], "broker exit 1")
        self.assertEqual(t["reply"], "")

    def test_a_missing_broker_is_an_error_not_a_crash(self):
        c = bench.BrokerClient(dict(bench.load_config()["broker"], dir=str(TESTS)), argv_prefix=["no-such-program-xyz"])
        self.assertIn("did not run", c.call("m", "work", "x", {})["error"])

    def test_a_dash_call_is_priced_from_estimated_tokens_in_a_run(self):
        d = tempfile.mkdtemp(prefix="eab-dash-")

        class Dash:
            def call(self, model_id, role, prompt, ctx):
                return {"reply": "garbled", "tokens_in": None, "tokens_out": None, "tokens_reasoning": None, "broker_ms": None,
                        "wall_ms": 3, "error": None, "timed_out": False}

        R = common.make_runner(d, client=Dash(), cap=0.003)
        R.run_all(["A"], 1, "standin")
        calls = [r for r in records(d) if r["type"] == "call"]
        self.assertTrue(calls and all(c["tokens_estimated"] and not c["valid"] for c in calls))
        for c in calls:
            prompt = (Path(d) / "blobs" / f"{c['prompt_sha']}.txt").read_text(encoding="utf-8")
            self.assertEqual(c["tokens_in"], len(prompt) // 4)

    def test_a_timed_out_call_is_charged_its_worst_case(self):
        d = tempfile.mkdtemp(prefix="eab-timeout-")

        class TimesOut:
            def call(self, model_id, role, prompt, ctx):
                return {"reply": "", "tokens_in": None, "tokens_out": None, "tokens_reasoning": None, "broker_ms": None,
                        "wall_ms": 600000, "error": "broker call timed out", "timed_out": True}

        R = common.make_runner(d, client=TimesOut(), cap=0.05)
        R.run_all(["A"], 1, "standin")
        calls = [r for r in records(d) if r["type"] == "call"]
        self.assertTrue(calls)
        first = calls[0]
        prompt = (Path(d) / "blobs" / f"{first['prompt_sha']}.txt").read_text(encoding="utf-8")
        self.assertAlmostEqual(first["cost_usd"], R.worst_cost(first["agent"], prompt, first["role"]), places=7)    # charged as if it ran to the limit
        self.assertGreater(first["cost_usd"], first["tokens_in"] * 0)       # not zero


class Cli(unittest.TestCase):
    def test_real_run_needs_the_flag(self):
        d = tempfile.mkdtemp(prefix="eab-cli-")
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = bench.main(["run", "--out", d, "--cap", "1", "--stop-after-min", "5"])
        self.assertEqual(code, 2)
        self.assertIn("--real", buf.getvalue())
        self.assertFalse((Path(d) / "room.jsonl").exists())

    def test_real_run_needs_a_cap_and_a_stop_time(self):
        for argv in (["run", "--out", "x", "--real"], ["run", "--out", "x", "--real", "--cap", "1"]):
            with self.assertRaises(SystemExit):
                with mock.patch("sys.stderr", io.StringIO()):
                    bench.main(argv)

    def test_dry_run_refuses_an_old_folder(self):
        d = tempfile.mkdtemp(prefix="eab-old-")
        common.make_runner(d, cap=0.001).run_all(["A"], 1, "standin")
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(bench.main(["dry-run", "--out", d, "--reps", "1"]), 2)

    def test_estimate_matches_the_call_counts_and_the_cap(self):
        e = bench.estimate(bench.load_config(), reps=8, workers=4)
        self.assertEqual({k: v["calls"] for k, v in e["arms"].items()}, {"A": 640, "B": 640, "C": 960, "D": 840, "E": 840})
        self.assertEqual(e["total"]["calls"], 3920)
        cap = bench.load_config()["run"]["cap_usd"]
        self.assertLess(e["total"]["cost_expected_usd"], e["total"]["cost_worst_usd"])
        self.assertLess(e["total"]["cost_expected_usd"], e["total"]["cost_upper_usd"])
        self.assertLess(e["total"]["cost_upper_usd"], 2.40)            # even priced as the smoke test saw it (reasoning on)
        self.assertLess(e["total"]["cost_worst_usd"], cap)             # reply limits per role keep even the worst case under the cap
        self.assertAlmostEqual(e["total"]["wall_hours_with_workers"] * 4, e["total"]["wall_hours_one_at_a_time"], delta=0.2)
        self.assertGreater(e["total"]["wall_hours_with_workers_if_reasoning_stayed_on"], 5 * e["total"]["wall_hours_with_workers"])

    def test_the_reasoning_on_reference_is_what_the_smoke_test_recorded(self):
        import call_costs
        p = TESTS.parent / "runs" / "smoke-1" / "room.jsonl"
        if not p.exists():
            self.skipTest("smoke-test room not on this machine")
        s = call_costs.summarize(records(p.parent))
        ref = bench.load_config()["estimate_basis"]["reasoning_on_reference"]
        for role in ("forecast", "work"):
            per_model = [v["cost_usd"] for k, v in s["by_model_role"].items() if k.endswith("|" + role)]
            self.assertEqual(len(per_model), 4)
            self.assertAlmostEqual(sum(per_model) / 4, ref["cost_per_call_usd"][role], places=5)
        for m, (f, w) in ref["by_model_forecast_work_usd"].items():
            self.assertAlmostEqual(s["by_model_role"][m + "|forecast"]["cost_usd"], f, places=5)
            self.assertAlmostEqual(s["by_model_role"][m + "|work"]["cost_usd"], w, places=5)

    def test_config_is_checked(self):
        cfg = bench.load_config()
        bench.validate_config(cfg)
        bad = json.loads(json.dumps(cfg))
        bad["models"][1]["family"] = "qwen"
        bad["models"][3]["family"] = "qwen"
        bad["models"][0]["family"] = "qwen"
        bad["models"][2]["family"] = "qwen"                  # all one family: nobody can be certified by another family
        with self.assertRaises(ValueError):
            bench.validate_config(bad)
        bad = json.loads(json.dumps(cfg))
        bad["models"].pop()
        with self.assertRaises(ValueError):
            bench.validate_config(bad)
        for key in ("providers", "max_out_tokens_by_role"):
            bad = json.loads(json.dumps(cfg))
            bad["broker"][key].pop("work")
            with self.assertRaises(ValueError):
                bench.validate_config(bad)
        bad = json.loads(json.dumps(cfg))
        bad["broker"]["max_out_tokens_by_role"]["work"] = 0
        with self.assertRaises(ValueError):
            bench.validate_config(bad)

    def test_no_model_name_is_written_into_the_protocol_code(self):
        names = [m["id"].split("/")[1] for m in bench.load_config()["models"]]
        for f in ("routing.py", "bench.py", "score.py", "jobs.py", "stats.py", "room.py", "sandbox.py"):
            text = (TESTS.parent / f).read_text(encoding="utf-8")
            for n in names:
                self.assertNotIn(n, text, f"{n} appears in {f}")

    def test_manifest_lists_files_that_exist(self):
        m = bench.manifest()
        for f in m:
            self.assertTrue((TESTS.parent / f).exists())
        self.assertIn("score.py", m)
        self.assertIn("config.json", m)

    def test_every_design_code_and_source_file_is_in_the_seal_list(self):
        root = TESTS.parent
        found = {p.relative_to(root).as_posix() for pat in ("*.py", "*.md", "*.json", "tests/*.py", "sources/*") for p in root.glob(pat)}
        missing = sorted(found - set(bench.FILES_TO_SEAL))
        self.assertEqual(missing, [], "files that would not be sealed")


if __name__ == "__main__":
    unittest.main()
