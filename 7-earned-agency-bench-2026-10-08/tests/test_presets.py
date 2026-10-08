"""Arms as presets of factors: validation, the default five unchanged, the four extra presets, any combination, the scorer."""
import copy
import hashlib
import itertools
import json
import random
import tempfile
import unittest
from pathlib import Path

import common
import bench
import jobs as J
import routing as RT
import score as SC
from room import canon, verify_chain

CFG = bench.load_config()
P = CFG["presets"]
AGENTS = ["m/one", "m/two", "m/three", "m/four"]
FAM = {"m/one": "qwen", "m/two": "google", "m/three": "mistral", "m/four": "xiaomi"}


def tab(spec):
    return {a: ({"n": spec[a][0], "brier": spec[a][1]} if a in spec else {"n": 0, "brier": None}) for a in AGENTS}


T_MIXED = tab({"m/one": (3, 0.30), "m/two": (3, 0.05), "m/three": (3, 0.20), "m/four": (3, 0.50)})
T_EMPTY = tab({})


def mp(arm, rep, rnd, table, presets=None):
    pr = (presets or P)[arm]
    return RT.make_plan(arm, pr, rep, rnd, AGENTS, FAM, table)


def records(d):
    return [json.loads(l) for l in (Path(d) / "room.jsonl").read_text(encoding="utf-8").splitlines() if l]


class Validation(unittest.TestCase):
    def bad(self, f):
        presets = copy.deepcopy(P)
        f(presets)
        with self.assertRaises(ValueError):
            RT.validate_presets(presets)
        cfg = copy.deepcopy(CFG)
        cfg["presets"] = presets
        with self.assertRaises(ValueError):
            bench.validate_config(cfg)

    def test_the_shipped_presets_are_valid(self):
        self.assertTrue(RT.validate_presets(P))
        self.assertTrue(RT.validate_analysis(CFG["analysis"], P))

    def test_unknown_factor_value(self):
        self.bad(lambda p: p["A"].update(certify="sometimes"))
        self.bad(lambda p: p["A"].update(work="mostly"))
        self.bad(lambda p: p["A"].update(routing="clever"))
        self.bad(lambda p: p["A"].update(ticket="yes"))

    def test_unknown_or_missing_key(self):
        self.bad(lambda p: p["A"].update(speed="fast"))
        self.bad(lambda p: p["A"].pop("ticket"))

    def test_routed_by_record_without_a_random_twin(self):
        self.bad(lambda p: p["D"].pop("twin"))
        self.bad(lambda p: p["D"].update(twin="NOPE"))
        self.bad(lambda p: p.pop("E"))
        self.bad(lambda p: p["E"].update(work="equal"))                 # the twin must match D's factors
        self.bad(lambda p: p["E"].update(routing="record", twin="D"))   # the twin must be random
        self.bad(lambda p: p.pop("EC"))
        self.bad(lambda p: p.pop("EW"))

    def test_routing_only_where_something_is_routed(self):
        self.bad(lambda p: p["A"].update(routing="random"))
        self.bad(lambda p: p["C"].update(routing="record", twin="E"))
        self.bad(lambda p: p["E"].update(routing="equal"))
        self.bad(lambda p: p["DW"].update(routing="equal"))

    def test_a_twin_belongs_only_to_a_record_preset(self):
        self.bad(lambda p: p["E"].update(twin="D"))
        self.bad(lambda p: p["A"].update(twin="E"))

    def test_no_presets(self):
        with self.assertRaises(ValueError):
            RT.validate_presets({})

    def test_the_declared_analysis_is_checked(self):
        def bad(f):
            an = copy.deepcopy(CFG["analysis"])
            f(an)
            with self.assertRaises(ValueError):
                RT.validate_analysis(an, P)
            cfg = copy.deepcopy(CFG)
            cfg["analysis"] = an
            with self.assertRaises(ValueError):
                bench.validate_config(cfg)

        bad(lambda an: an["primary"].update(a="A"))                      # the primary pair must be a record preset ...
        bad(lambda an: an["primary"].update(b="EC"))                     # ... and its own twin
        bad(lambda an: an.update(baseline="ZZ"))
        bad(lambda an: an["validity_arms"].append("D"))                  # a routed arm cannot be a validity arm
        bad(lambda an: an["secondary"].append({"id": "T1", "a": "A", "b": "B", "field": "passed", "rounds": "all", "what": "x"}))
        bad(lambda an: an["secondary"].append({"id": "S9", "a": "A", "b": "QQ", "field": "passed", "rounds": "all", "what": "x"}))
        bad(lambda an: an["secondary"].append({"id": "S9", "a": "A", "b": "B", "field": "luck", "rounds": "all", "what": "x"}))
        bad(lambda an: an["secondary"].append(dict(an["secondary"][0])))   # a repeated id

    def test_default_arms_must_be_presets(self):
        cfg = copy.deepcopy(CFG)
        cfg["default_arms"] = ["A", "Q"]
        with self.assertRaises(ValueError):
            bench.validate_config(cfg)

    def test_the_cli_refuses_an_unknown_arm(self):
        self.assertEqual(bench.pick_arms("A,Q", CFG)[0], None)
        self.assertEqual(bench.pick_arms("A,DC", CFG)[0], ["A", "DC"])
        self.assertEqual(bench.pick_arms("all", CFG)[0], list(P))
        self.assertEqual(bench.pick_arms(None, CFG)[0], ["A", "B", "C", "D", "E"])
        d = tempfile.mkdtemp(prefix="eab-badarm-")
        with self.assertRaises(ValueError):
            common.make_runner(d).run_all(["Q"], 1, "standin")


class TheDefaultFive(unittest.TestCase):
    def test_definitions(self):
        want = {
            "A": dict(ticket=False, certify="none", work="equal", routing="equal"),
            "B": dict(ticket=True, certify="none", work="equal", routing="equal"),
            "C": dict(ticket=True, certify="all", work="equal", routing="equal"),
            "D": dict(ticket=True, certify="table", work="table", routing="record", twin="E"),
            "E": dict(ticket=True, certify="table", work="table", routing="random"),
        }
        for k, w in want.items():
            self.assertEqual({f: P[k][f] for f in w}, w, k)
        self.assertEqual(CFG["default_arms"], ["A", "B", "C", "D", "E"])

    def test_the_plans_are_exactly_what_they_were_before_arms_became_presets(self):
        tabs = [{a: {"n": 0, "brier": None} for a in AGENTS},
                {"m/one": {"n": 3, "brier": 0.3}, "m/two": {"n": 3, "brier": 0.05}, "m/three": {"n": 2, "brier": 0.2}, "m/four": {"n": 0, "brier": None}},
                {"m/one": {"n": 3, "brier": 0.1}, "m/two": {"n": 3, "brier": 0.1}, "m/three": {"n": 2, "brier": 0.1}, "m/four": {"n": 1, "brier": 0.9}}]
        fam = {"m/one": "qwen", "m/two": "google", "m/three": "qwen", "m/four": "xiaomi"}      # the families the golden hash was made with
        plans = [RT.make_plan(arm, P[arm], rep, rnd, AGENTS, fam, t) for arm in "ABCDE" for rep in range(4) for rnd in range(1, 6) for t in tabs]
        self.assertEqual(len(plans), 300)
        self.assertEqual(hashlib.sha256(canon(plans).encode()).hexdigest(), "33cd0bc73b924a9e0e8452e49a80704db68b382adb384ab252fff63b2b18ef17")


class ExtraPresets(unittest.TestCase):
    def shares(self, plan):
        return [sum(1 for e in plan["entries"] if e["agent"] == a) for a in plan["order"]]

    def checks(self, plan):
        return [sum(e["checked"] for e in plan["entries"] if e["agent"] == a) for a in plan["order"]]

    def test_check_only_has_equal_work_and_routed_checks(self):
        for arm in ("DC", "EC"):
            p = mp(arm, 0, 3, T_MIXED)
            self.assertEqual(self.shares(p), [2, 2, 2, 2])
            self.assertEqual(self.checks(p), [1, 1, 1, 2])
            self.assertEqual(sum(self.checks(p)), 5)
        self.assertEqual(mp("DC", 0, 3, T_MIXED)["order"], ["m/two", "m/three", "m/one", "m/four"])    # by record

    def test_work_only_has_routed_work_and_the_same_one_check_for_everyone(self):
        for arm in ("DW", "EW"):
            p = mp(arm, 0, 3, T_MIXED)
            self.assertEqual(self.shares(p), [3, 2, 2, 1])
            self.assertEqual(self.checks(p), [1, 1, 1, 1])
        self.assertEqual(mp("DW", 0, 3, T_MIXED)["order"], ["m/two", "m/three", "m/one", "m/four"])

    def test_random_twins_ignore_the_record_and_record_presets_follow_it(self):
        t2 = tab({"m/one": (3, 0.01), "m/two": (3, 0.90), "m/three": (3, 0.60), "m/four": (3, 0.02)})
        for twin in ("E", "EC", "EW"):
            for rep in range(4):
                x, y = mp(twin, rep, 3, T_MIXED), mp(twin, rep, 3, t2)
                self.assertEqual((x["order"], x["entries"]), (y["order"], y["entries"]))
        for rec in ("D", "DC", "DW"):
            self.assertNotEqual(mp(rec, 0, 3, T_MIXED)["order"], mp(rec, 0, 3, t2)["order"])

    def test_twins_share_the_jobs_and_round_one_is_alike(self):
        for rec, twin in (("D", "E"), ("DC", "EC"), ("DW", "EW")):
            for rep in range(4):
                a, b = mp(rec, rep, 1, T_EMPTY), mp(twin, rep, 1, T_EMPTY)
                self.assertEqual(a["entries"], b["entries"])
                self.assertEqual([e["job"] for e in mp(rec, rep, 3, T_MIXED)["entries"]], [e["job"] for e in mp(twin, rep, 3, T_MIXED)["entries"]])

    def test_the_floor_holds_for_every_preset_and_record(self):
        rng = random.Random(11)
        perfect = tab({a: (9, 0.0) for a in AGENTS})
        for arm, pr in P.items():
            if pr["certify"] not in ("table", "fixed"):
                continue
            for rep in range(6):
                for rnd in range(2, 6):
                    t = perfect if rep % 2 else tab({a: (rng.randint(1, 8), rng.random()) for a in AGENTS if rng.random() < 0.8})
                    p = mp(arm, rep, rnd, t)
                    for a in AGENTS:
                        self.assertGreaterEqual(sum(e["checked"] for e in p["entries"] if e["agent"] == a), RT.MIN_CHECKS, (arm, a))

    def test_nothing_is_checked_for_none_and_everything_for_all(self):
        self.assertFalse(any(e["checked"] for e in mp("B", 0, 2, T_MIXED)["entries"]))
        self.assertTrue(all(e["checked"] for e in mp("C", 0, 2, T_MIXED)["entries"]))


class AnyCombination(unittest.TestCase):
    def all_valid_presets(self):
        out = {}
        for tk, ce, wk, ro in itertools.product(RT.FACTORS["ticket"], RT.FACTORS["certify"], RT.FACTORS["work"], RT.FACTORS["routing"]):
            pid = f"{int(tk)}-{ce}-{wk}-{ro}"
            p = dict(name=pid, ticket=tk, certify=ce, work=wk, routing=ro)
            routed = ce == "table" or wk == "table"
            if routed != (ro != "equal"):
                continue
            if ro == "record":
                p["twin"] = f"{int(tk)}-{ce}-{wk}-random"
            out[pid] = p
        return out

    def test_every_valid_combination_makes_rule_following_plans(self):
        presets = self.all_valid_presets()
        self.assertTrue(RT.validate_presets(presets))
        self.assertGreater(len(presets), 20)
        for pid in presets:
            for rep in range(2):
                for rnd in (1, 3, 5):
                    p = mp(pid, rep, rnd, T_MIXED if rnd > 1 else T_EMPTY, presets)
                    self.assertTrue(RT.check_plan(p, presets[pid], AGENTS, FAM))
                    if presets[pid]["certify"] in ("table", "fixed"):
                        self.assertTrue(all(sum(e["checked"] for e in p["entries"] if e["agent"] == a) >= 1 for a in AGENTS), pid)

    def test_a_new_combination_is_only_a_config_entry(self):
        cfg = copy.deepcopy(CFG)
        cfg["presets"]["X"] = {"name": "ticket-and-fixed-checks", "ticket": True, "certify": "fixed", "work": "equal", "routing": "equal"}
        cfg["presets"]["Y"] = {"name": "relay-with-routed-work", "ticket": True, "certify": "all", "work": "table", "routing": "record", "twin": "Z"}
        cfg["presets"]["Z"] = {"name": "relay-with-random-work", "ticket": True, "certify": "all", "work": "table", "routing": "random"}
        cfg["presets"]["N"] = {"name": "certified-without-a-ticket", "ticket": False, "certify": "all", "work": "equal", "routing": "equal"}
        bench.validate_config(cfg)
        d = tempfile.mkdtemp(prefix="eab-newcombo-")
        R = common.make_runner(d, workers=2, cfg=cfg)
        self.assertEqual(R.run_all(["A", "X", "Y", "Z", "N"], 1, "standin"), 0)
        recs = records(d)
        for arm, has in (("A", False), ("N", False), ("X", True), ("Y", True)):          # the ticket follows the preset, not the letter
            calls = [c for c in recs if c["type"] == "call" and c["run"] == f"{arm}|r0" and c["role"] in ("forecast", "work")]
            self.assertTrue(calls)
            for c in calls:
                text = (Path(d) / "blobs" / f"{c['prompt_sha']}.txt").read_text(encoding="utf-8")
                self.assertEqual("COAT-CHECK TICKET" in text, has, arm)
        self.assertTrue(verify_chain(Path(d) / "room.jsonl")[0])
        res = SC.score(recs)
        self.assertEqual(res["games_left_out"], {})
        self.assertEqual(sorted(res["per_arm"]), ["A", "N", "X", "Y", "Z"])
        self.assertEqual(res["per_arm"]["N"]["all_rounds"]["checked_share"]["num"], 40)
        self.assertEqual(res["per_arm"]["X"]["all_rounds"]["checked_share"]["num"], 20)     # 4 checks of 8, five rounds
        self.assertEqual(res["per_arm"]["Z"]["all_rounds"]["checked_share"]["num"], 40)     # all of them
        self.assertEqual(res["per_arm"]["Y"]["name"], "relay-with-routed-work")


class ScorerAndExtendedRun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = Path(tempfile.mkdtemp(prefix="eab-all9-"))
        R = common.make_runner(cls.dir, workers=4)
        assert R.run_all(list(P), 1, "standin") == 0
        cls.recs = records(cls.dir)
        cls.res = SC.score(cls.recs)

    def test_all_nine_presets_run_and_score(self):
        self.assertTrue(verify_chain(self.dir / "room.jsonl")[0])
        self.assertEqual(self.res["games_scored"], 9)
        self.assertEqual(self.res["games_left_out"], {})
        self.assertEqual(list(self.res["per_arm"]), list(P))
        self.assertEqual(len(self.res["units"]), 9 * 40)

    def test_calls_per_arm(self):
        n = {a: sum(1 for r in self.recs if r["type"] == "call" and r["run"] == f"{a}|r0") for a in P}
        self.assertEqual(n, {"A": 80, "B": 80, "C": 120, "D": 105, "E": 105, "DC": 105, "EC": 105, "DW": 100, "EW": 100})

    def test_the_declared_analysis_travels_in_the_room(self):
        rs = self.recs[0]
        self.assertEqual(rs["type"], "run_start")
        self.assertEqual(rs["analysis"], CFG["analysis"])
        self.assertEqual(rs["presets"], P)
        gs = [r for r in self.recs if r["type"] == "game_start"]
        self.assertTrue(all(g["preset"] == P[g["arm"]] for g in gs))

    def test_secondary_pairs_declared_in_the_config_are_scored_when_their_arms_ran(self):
        for k in ("S2", "S3", "S4", "S6", "S7", "S5"):
            self.assertIn(k, self.res["tests"])
        self.assertEqual(self.res["tests"]["S6"]["a"], "DC")
        self.assertEqual(self.res["tests"]["S7"]["b"], "EW")
        self.assertEqual(self.res["tests"]["S6"]["n"], 1)

    def test_calibration_uses_only_the_declared_arms(self):
        self.assertEqual(self.res["tests"]["T2"]["n"], 1)
        with_all = SC.calibration_improvement({k: g for k, g in SC.build_games(self.recs)[0].items()}, None)
        only = SC.calibration_improvement(SC.build_games(self.recs)[0], CFG["analysis"]["calibration_arms"])
        self.assertNotEqual(with_all["diffs"], only["diffs"])
        self.assertEqual(only["diffs"], self.res["tests"]["T2"]["diffs"])

    def test_a_secondary_pair_whose_arms_did_not_run_is_reported_as_not_run(self):
        d = tempfile.mkdtemp(prefix="eab-five-")
        common.make_runner(d).run_all(common.DEFAULT_ARMS, 1, "standin")
        res = SC.score(records(d))
        self.assertEqual(res["tests"]["S6"]["n"], 0)
        self.assertIsNone(res["tests"]["S6"]["p"])
        self.assertEqual(res["games_scored"], 5)
        self.assertIn("S6 [secondary] n = 0, mean difference n/a, p = n/a  (not run: its arms are not in this run)", SC.report(res))

    def test_the_primary_pair_is_read_from_the_declared_analysis(self):
        an = copy.deepcopy(CFG["analysis"])
        an["primary"] = {"a": "DC", "b": "EC"}
        res = SC.score(self.recs, analysis=an)
        self.assertEqual((res["tests"]["T1"]["a"], res["tests"]["T1"]["b"]), ("DC", "EC"))
        self.assertEqual((res["tests"]["T1b"]["a"], res["tests"]["T1b"]["b"]), ("DC", "EC"))
        an["primary"] = {"a": "DW", "b": "EW"}
        self.assertEqual(SC.score(self.recs, analysis=an)["tests"]["T1"]["a"], "DW")
        self.assertEqual(self.res["tests"]["T1"]["a"], "D")

    def test_the_guards_read_the_declared_baseline_and_control(self):
        an = copy.deepcopy(CFG["analysis"])
        an["baseline"], an["primary"] = "B", {"a": "DC", "b": "EC"}
        res = SC.score(self.recs, analysis=an)
        b = res["per_arm"]["B"]["all_rounds"]["claimed_false_done_per_job"]["rate"]
        self.assertEqual(res["guards"]["G1_baseline_false_done"]["value"], b)
        c = res["per_arm"]["EC"]["rounds_2_to_5"]["accepted_false_done_per_job"]["rate"]
        self.assertEqual(res["guards"]["G2_control_false_done"]["value"], c)

    def test_a_game_whose_preset_differs_from_the_declared_one_is_left_out(self):
        recs = copy.deepcopy(self.recs)
        g = next(r for r in recs if r["type"] == "game_start" and r["arm"] == "D")
        g["preset"] = dict(g["preset"], certify="none")
        res = SC.score(recs)
        self.assertIn("D|r0", res["games_left_out"])

    def test_a_room_without_the_declared_analysis_is_refused(self):
        recs = [r for r in copy.deepcopy(self.recs)]
        del recs[0]["analysis"]
        with self.assertRaises(SystemExit):
            SC.score(recs)

    def test_certifier_measures_appear_exactly_for_arms_that_certify(self):
        for a, p in P.items():
            self.assertEqual("certifier" in self.res["per_arm"][a], p["certify"] != "none", a)


if __name__ == "__main__":
    unittest.main()
