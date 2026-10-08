"""The tests decided in advance, written with the standard library only (no scipy here).

  mcnemar_exact   two-sided exact McNemar from the two discordant counts (binomial, p = 0.5)
  signflip        paired sign-flip permutation test on a list of paired differences, mean as the statistic.
                  Exact (all 2^n sign patterns) up to n = 16; above that, a fixed-seed Monte Carlo of 200,000 draws.
  spearman        rank correlation with average ranks for ties
  holm            Holm step-down adjustment
  power_signflip  chance that signflip reaches p < alpha when the true mean difference is `delta` and each
                  difference has standard deviation `sd` (normal), by simulation with a fixed seed
"""
from __future__ import annotations

import math
import random
import sys

EXACT_MAX_N = 16
MC_DRAWS = 200_000


def mcnemar_exact(b, c):
    """Two-sided exact McNemar p from the discordant counts b and c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def signflip(diffs, seed=20261008):
    """Two-sided p that a mean this far from 0 arises if the sign of each paired difference were a coin flip.
    Returns dict(n, mean, p, exact, min_p)."""
    d = [float(x) for x in diffs]
    n = len(d)
    if n == 0:
        return {"n": 0, "mean": None, "p": None, "exact": True, "min_p": None}
    obs = abs(sum(d))
    eps = 1e-12
    if n <= EXACT_MAX_N:
        total, hits = 2 ** n, 0
        for mask in range(total):
            s = 0.0
            for i in range(n):
                s += d[i] if (mask >> i) & 1 else -d[i]
            if abs(s) >= obs - eps:
                hits += 1
        p, exact = hits / total, True
        min_p = 2 / total
    else:
        rng = random.Random(seed)
        hits = 0
        for _ in range(MC_DRAWS):
            s = 0.0
            for x in d:
                s += x if rng.random() < 0.5 else -x
            if abs(s) >= obs - eps:
                hits += 1
        p, exact = (hits + 1) / (MC_DRAWS + 1), False
        min_p = 2 / 2 ** n
    return {"n": n, "mean": sum(d) / n, "p": p, "exact": exact, "min_p": min_p}


def _ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def spearman(xs, ys):
    """Spearman rank correlation, or None when it is not defined (fewer than 3 pairs, or no spread in x or y)."""
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx, ry = _ranks(xs), _ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sx = sum((a - mx) ** 2 for a in rx)
    sy = sum((b - my) ** 2 for b in ry)
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / math.sqrt(sx * sy)


def holm(pvals):
    """Holm step-down adjusted p-values, same order as the input. None stays None."""
    idx = [i for i, p in enumerate(pvals) if p is not None]
    order = sorted(idx, key=lambda i: pvals[i])
    adj = [None] * len(pvals)
    m = len(order)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj


def power_signflip(n, delta, sd, alpha=0.05, sims=2000, seed=7):
    rng = random.Random(seed)
    hit = 0
    for _ in range(sims):
        d = [rng.gauss(delta, sd) for _ in range(n)]
        if signflip(d)["p"] < alpha:
            hit += 1
    return hit / sims


def power_table(n_games, base_rate, jobs_per_game, deltas, inflate=(1.0, 1.5), sims=1000):
    """Rows of (delta, sd-inflation, power) for a difference of two rates, each over `jobs_per_game` jobs per game.
    The binomial sd of one game's difference is sqrt(2 q (1 - q) / m); `inflate` widens it for the extra spread
    between models and between games."""
    sd0 = math.sqrt(2 * base_rate * (1 - base_rate) / jobs_per_game)
    return [(d, f, power_signflip(n_games, -abs(d), sd0 * f, sims=sims)) for f in inflate for d in deltas]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["power"]:
        print("power of the primary test T1 (sign-flip over games, two-sided, alpha 0.05)")
        print("rate in the control arm E: 0.15 and 0.25; 32 jobs per game (rounds 2-5)")
        for q in (0.15, 0.25):
            for n in (6, 8, 12):
                print(f"\ncontrol rate {q}, {n} games")
                for d, f, pw in power_table(n, q, 32, (0.05, 0.10, 0.15, 0.20)):
                    print(f"  true drop {d:.2f}, spread x{f:.1f}: power {pw:.2f}")
        return 0
    print("usage: python stats.py power")
    return 2


if __name__ == "__main__":
    sys.exit(main())
