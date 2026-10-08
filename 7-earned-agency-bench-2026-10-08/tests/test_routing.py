import random
import unittest

import common
import jobs as J
import routing as RT

P = common.PRESETS


def mp(arm, *a, **k):
    return RT.make_plan(arm, P[arm], *a, **k)


def cp(plan, agents, fam):
    return RT.check_plan(plan, P[plan["arm"]], agents, fam)


AGENTS = ["m/one", "m/two", "m/three", "m/four"]
FAM = {"m/one": "qwen", "m/two": "google", "m/three": "qwen", "m/four": "xiaomi"}


def table(**brier):
    """{agent: (n, brier)} -> a calibration table"""
    return {a: ({"n": brier[a][0], "brier": brier[a][1]} if a in brier else {"n": 0, "brier": None}) for a in AGENTS}


def empty():
    return table()


class Calibration(unittest.TestCase):
    def test_brier_is_the_mean_square_error(self):
        t = RT.calibration_table([("m/one", 0.9, 1), ("m/one", 0.5, 0), ("m/two", 1.0, 0)], AGENTS)
        self.assertAlmostEqual(t["m/one"]["brier"], (0.01 + 0.25) / 2)
        self.assertEqual(t["m/one"]["n"], 2)
        self.assertAlmostEqual(t["m/two"]["brier"], 1.0)
        self.assertIsNone(t["m/three"]["brier"])

    def test_invalid_forecasts_do_not_count(self):
        t = RT.calibration_table([("m/one", None, 1)], AGENTS)
        self.assertEqual(t["m/one"]["n"], 0)

    def test_record_resets_when_the_model_changes(self):
        old = [("m/old-model", 0.0, 1)] * 5            # a bad record made by a model that is no longer in the list
        t = RT.calibration_table(old + [("m/two", 0.9, 1)], AGENTS)
        self.assertNotIn("m/old-model", t)
        for a in AGENTS:
            if a != "m/two":
                self.assertEqual(t[a]["n"], 0)
        # a model that replaces m/three arrives with an empty record and is ranked last among the others
        agents2 = ["m/one", "m/two", "m/new", "m/four"]
        rows = [("m/one", 0.9, 1), ("m/two", 0.9, 1), ("m/three", 0.9, 1), ("m/four", 0.9, 1)]
        t2 = RT.calibration_table(rows, agents2)
        self.assertEqual(t2["m/new"]["n"], 0)
        self.assertEqual(RT.rank_agents(agents2, t2, 0, 2)[-1], "m/new")


class Ranking(unittest.TestCase):
    def test_lower_brier_ranks_first(self):
        t = table(**{"m/one": (3, 0.30), "m/two": (3, 0.05), "m/three": (3, 0.20), "m/four": (3, 0.50)})
        self.assertEqual(RT.rank_agents(AGENTS, t, 0, 2), ["m/two", "m/three", "m/one", "m/four"])

    def test_unranked_go_last_and_ties_are_seeded(self):
        t = table(**{"m/one": (2, 0.2), "m/two": (2, 0.2)})
        order = RT.rank_agents(AGENTS, t, 0, 2)
        self.assertEqual(set(order[:2]), {"m/one", "m/two"})
        self.assertEqual(set(order[2:]), {"m/three", "m/four"})
        self.assertEqual(order, RT.rank_agents(AGENTS, t, 0, 2))                 # the same every time
        tie_orders = {tuple(RT.rank_agents(AGENTS, t, rep, 2)[:2]) for rep in range(12)}
        self.assertEqual(len(tie_orders), 2, "a tie must be broken by a seeded draw, not by list order")

    def test_ranking_reads_only_score_a(self):
        t1 = table(**{"m/one": (3, 0.30), "m/two": (3, 0.05), "m/three": (3, 0.20), "m/four": (3, 0.50)})
        t2 = {a: dict(v, passes=99, done_claims=0) for a, v in t1.items()}      # extra facts about score (b) change nothing
        self.assertEqual(RT.rank_agents(AGENTS, t1, 1, 3), RT.rank_agents(AGENTS, t2, 1, 3))

    def test_round_one_has_no_record_so_d_and_e_plan_alike(self):
        for rep in range(5):
            d = mp("D", rep, 1, AGENTS, FAM, empty())
            e = mp("E", rep, 1, AGENTS, FAM, empty())
            self.assertEqual([(x["job"], x["agent"], x["checked"]) for x in d["entries"]],
                             [(x["job"], x["agent"], x["checked"]) for x in e["entries"]])


class Plans(unittest.TestCase):
    def random_table(self, rng):
        return table(**{a: (rng.randint(1, 8), rng.random()) for a in AGENTS if rng.random() < 0.8})

    def test_every_plan_obeys_every_rule(self):
        rng = random.Random(5)
        for arm in common.DEFAULT_ARMS:
            for rep in range(6):
                for rnd in range(1, 6):
                    t = self.random_table(rng) if rnd > 1 else empty()
                    plan = mp(arm, rep, rnd, AGENTS, FAM, t)
                    self.assertTrue(cp(plan, AGENTS, FAM))
                    jobs = [e["job"] for e in plan["entries"]]
                    self.assertEqual(jobs, RT.round_jobs(rep, rnd))

    def test_shares_and_checks_by_arm(self):
        t = table(**{"m/one": (3, 0.30), "m/two": (3, 0.05), "m/three": (3, 0.20), "m/four": (3, 0.50)})
        for arm in ("A", "B"):
            p = mp(arm, 0, 2, AGENTS, FAM, t)
            self.assertEqual([sum(1 for e in p["entries"] if e["agent"] == a) for a in AGENTS], [2, 2, 2, 2])
            self.assertFalse(any(e["checked"] for e in p["entries"]))
        p = mp("C", 0, 2, AGENTS, FAM, t)
        self.assertTrue(all(e["checked"] for e in p["entries"]))
        for arm in ("D", "E"):
            p = mp(arm, 0, 2, AGENTS, FAM, t)
            by_tier = {}
            for e in p["entries"]:
                by_tier.setdefault(e["tier"], []).append(e)
            self.assertEqual([len(by_tier[k]) for k in range(4)], [3, 2, 2, 1])
            self.assertEqual([sum(e["checked"] for e in by_tier[k]) for k in range(4)], [1, 1, 2, 1])
            self.assertEqual(sum(e["checked"] for e in p["entries"]), 5)

    def test_earned_arm_gives_the_best_record_the_most_work_and_the_fewest_checks_per_job(self):
        t = table(**{"m/one": (3, 0.30), "m/two": (3, 0.05), "m/three": (3, 0.20), "m/four": (3, 0.50)})
        p = mp("D", 0, 3, AGENTS, FAM, t)
        self.assertEqual(p["order"], ["m/two", "m/three", "m/one", "m/four"])
        best = [e for e in p["entries"] if e["agent"] == "m/two"]
        worst = [e for e in p["entries"] if e["agent"] == "m/four"]
        self.assertEqual(len(best), 3)
        self.assertEqual(sum(e["checked"] for e in best) / len(best), 1 / 3)
        self.assertEqual(sum(e["checked"] for e in worst) / len(worst), 1.0)

    def test_random_arm_ignores_the_record(self):
        t1 = table(**{"m/one": (3, 0.30), "m/two": (3, 0.05), "m/three": (3, 0.20), "m/four": (3, 0.50)})
        t2 = table(**{"m/one": (3, 0.01), "m/two": (3, 0.90), "m/three": (3, 0.60), "m/four": (3, 0.02)})
        for rep in range(5):
            a = mp("E", rep, 3, AGENTS, FAM, t1)
            b = mp("E", rep, 3, AGENTS, FAM, t2)
            self.assertEqual([(e["job"], e["agent"], e["checked"]) for e in a["entries"]],
                             [(e["job"], e["agent"], e["checked"]) for e in b["entries"]])
        orders = {tuple(mp("E", rep, 3, AGENTS, FAM, t1)["order"]) for rep in range(30)}
        self.assertGreater(len(orders), 8, "random routing should shuffle the ranks")

    def test_same_tiers_in_d_and_e(self):
        t = table(**{"m/one": (3, 0.30), "m/two": (3, 0.05), "m/three": (3, 0.20), "m/four": (3, 0.50)})
        d = mp("D", 2, 3, AGENTS, FAM, t)
        e = mp("E", 2, 3, AGENTS, FAM, t)
        self.assertEqual(sorted((x["tier"], x["checked"]) for x in d["entries"]).count((0, True)), sorted((x["tier"], x["checked"]) for x in e["entries"]).count((0, True)))
        self.assertEqual([x["job"] for x in d["entries"]], [x["job"] for x in e["entries"]])

    def test_no_agent_is_ever_left_without_a_check_whatever_its_record(self):
        perfect = table(**{a: (9, 0.0) for a in AGENTS})
        for rep in range(8):
            for rnd in range(2, 6):
                p = mp("D", rep, rnd, AGENTS, FAM, perfect)
                for a in AGENTS:
                    mine = [e for e in p["entries"] if e["agent"] == a]
                    self.assertGreaterEqual(sum(e["checked"] for e in mine), RT.MIN_CHECKS, (a, rep, rnd))
                self.assertGreaterEqual(min(sum(e["checked"] for e in p["entries"] if e["agent"] == a) for a in AGENTS), 1)

    def test_check_plan_rejects_broken_plans(self):
        t = empty()
        base = mp("D", 0, 2, AGENTS, FAM, t)

        def broken(f):
            import copy
            p = copy.deepcopy(base)
            f(p)
            with self.assertRaises(AssertionError):
                cp(p, AGENTS, FAM)

        def uncheck_all_of_the_best(p):
            for e in p["entries"]:
                if e["tier"] == 0:
                    e["checked"], e["certifier"] = False, None

        def same_family_certifier(p):
            e = next(e for e in p["entries"] if e["checked"])
            e["certifier"] = next(a for a in AGENTS if FAM[a] == FAM[e["agent"]] and a != e["agent"]) if FAM[e["agent"]] == "qwen" else e["agent"]

        def move_a_job(p):
            p["entries"][0]["agent"] = next(a for a in AGENTS if a != p["entries"][0]["agent"])

        def repeat_a_job(p):
            p["entries"][1]["job"] = p["entries"][0]["job"]

        for f in (uncheck_all_of_the_best, same_family_certifier, move_a_job, repeat_a_job):
            broken(f)

    def test_certifier_is_of_another_family(self):
        for a in AGENTS:
            self.assertNotEqual(FAM[RT.certifier_for(a, AGENTS, FAM)], FAM[a])
        with self.assertRaises(ValueError):
            RT.certifier_for("m/one", AGENTS, {a: "same" for a in AGENTS})

    def test_arms_a_to_c_turn_the_order_each_round(self):
        orders = [mp("A", 0, r, AGENTS, FAM, empty())["order"] for r in range(1, 5)]
        self.assertEqual(len({o[0] for o in orders}), 4)

    def test_arms_paired_by_job_in_a_rep(self):
        for rnd in range(1, 6):
            lists = [[e["job"] for e in mp(arm, 3, rnd, AGENTS, FAM, empty())["entries"]] for arm in common.DEFAULT_ARMS]
            self.assertTrue(all(l == lists[0] for l in lists))

    def test_tables_in_the_rule_are_what_the_design_says(self):
        self.assertEqual((RT.WORK_BY_RANK, RT.CHECKS_BY_RANK, RT.EQUAL_WORK), ((3, 2, 2, 1), (1, 1, 2, 1), (2, 2, 2, 2)))
        self.assertEqual((RT.ROUNDS, RT.JOBS_PER_ROUND, RT.MIN_CHECKS), (5, 8, 1))
        self.assertEqual(RT.ROUNDS * RT.JOBS_PER_ROUND, len(J.JOBS))


if __name__ == "__main__":
    unittest.main()
