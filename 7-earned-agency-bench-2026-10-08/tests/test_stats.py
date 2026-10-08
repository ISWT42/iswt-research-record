import unittest

import common  # noqa: F401
import stats as ST


class Mcnemar(unittest.TestCase):
    def test_known_values(self):
        self.assertAlmostEqual(ST.mcnemar_exact(9, 0), 0.00390625)       # the relay's A vs B
        self.assertAlmostEqual(ST.mcnemar_exact(8, 3), 0.2265625)        # the relay's A vs C
        self.assertAlmostEqual(ST.mcnemar_exact(10, 3), 0.0922851562)    # the relay's A vs D
        self.assertEqual(ST.mcnemar_exact(0, 0), 1.0)
        self.assertEqual(ST.mcnemar_exact(5, 5), 1.0)

    def test_symmetric(self):
        self.assertEqual(ST.mcnemar_exact(2, 7), ST.mcnemar_exact(7, 2))


class SignFlip(unittest.TestCase):
    def test_all_same_sign(self):
        r = ST.signflip([1, 1, 1])
        self.assertAlmostEqual(r["p"], 2 / 8)
        self.assertTrue(r["exact"])
        self.assertAlmostEqual(r["min_p"], 2 / 8)

    def test_two_sided(self):
        self.assertAlmostEqual(ST.signflip([-1, -1, -1])["p"], 2 / 8)
        self.assertAlmostEqual(ST.signflip([1, -1])["p"], 1.0)

    def test_magnitude_matters(self):
        self.assertAlmostEqual(ST.signflip([4, 1, 1, -1])["p"], 8 / 16)       # sums of 5 or more: 8 of 16 sign patterns
        self.assertAlmostEqual(ST.signflip([1, 1, 1, -1])["p"], 10 / 16)      # same signs, small sizes: sums of 2 or more
        self.assertAlmostEqual(ST.signflip([3, 1, 1])["p"], 2 / 8)

    def test_six_games_can_just_reach_five_percent(self):
        self.assertLess(ST.signflip([0.1] * 6)["p"], 0.05)
        self.assertGreater(ST.signflip([0.1] * 5)["p"], 0.05)

    def test_empty_and_zero(self):
        self.assertIsNone(ST.signflip([])["p"])
        self.assertEqual(ST.signflip([0, 0, 0, 0])["p"], 1.0)

    def test_monte_carlo_above_16_and_repeatable(self):
        a = ST.signflip([0.1] * 20)
        b = ST.signflip([0.1] * 20)
        self.assertFalse(a["exact"])
        self.assertEqual(a["p"], b["p"])
        self.assertLess(a["p"], 0.001)


class Rank(unittest.TestCase):
    def test_spearman(self):
        self.assertAlmostEqual(ST.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(ST.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertAlmostEqual(ST.spearman([1, 2, 3], [1, 3, 2]), 0.5)
        self.assertIsNone(ST.spearman([1, 1, 1], [1, 2, 3]))
        self.assertIsNone(ST.spearman([1, 2], [1, 2]))

    def test_ties_use_average_ranks(self):
        self.assertAlmostEqual(ST.spearman([1, 2, 2, 4], [1, 2, 3, 4]), 0.9486832980505138)

    def test_holm(self):
        self.assertEqual(ST.holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
        self.assertEqual(ST.holm([None, 0.5]), [None, 0.5])
        self.assertEqual(ST.holm([0.5, 0.5]), [1.0, 1.0])


class Power(unittest.TestCase):
    def test_power_rises_with_effect_and_games(self):
        small = ST.power_signflip(8, -0.05, 0.1, sims=400)
        big = ST.power_signflip(8, -0.20, 0.1, sims=400)
        more = ST.power_signflip(12, -0.05, 0.1, sims=400)
        self.assertLess(small, big)
        self.assertLess(small, more)
        self.assertGreater(big, 0.8)

    def test_power_at_no_effect_is_at_most_alpha(self):
        self.assertLess(ST.power_signflip(8, 0.0, 0.1, sims=1500), 0.08)

    def test_too_few_games_have_no_power(self):
        self.assertEqual(ST.power_signflip(4, -1.0, 0.01, sims=100), 0.0)

    def test_repeatable(self):
        self.assertEqual(ST.power_signflip(8, -0.1, 0.1, sims=200), ST.power_signflip(8, -0.1, 0.1, sims=200))


if __name__ == "__main__":
    unittest.main()
