# Addendum 2: how repeats and order are drawn (written 2026-10-06 03:27 UTC)

This answers QUESTIONS.md question 3. The runner's current S4 code is correct, and its method is now the rule for every spec. Question 2 (the spend) is not answered here: only the owner can answer it, in the session.

**The method, every spec:**
1. **List the base calls in input order.** Items in the order of the input file. Within an item, models in the order of MODELS.json, Qwen first. In S1, arms in the order A0, A1, A2, then models. In S3, conditions in the order P0, P1, P2, P3, then models.
2. **Make one generator:** `rng = random.Random(20261006)`.
3. **Draw the repeats with it.** Take `rng.sample(range(len(base)), k)` and append a copy of each drawn call with `repeat` = 1. The k for each spec:
   - S4: 96 of 480.
   - S3: 192 of 960.
   - S5: 120 of 600.
   - S2: whole chains, 108 of the 540 base chains (item, arm, model), each chain being a reviewer call and its release-manager call (216 calls).
   - S1: no sampling. Every call is made twice; append a full copy of the base list with `repeat` = 1.
4. **Shuffle everything with the same rng instance:** `rng.shuffle(all_calls)`. In S2, shuffle whole chains, not single calls, and run S2's step 1 (the 180 receipt checks) first, in input order, before any chain.
5. **Record the order** in `runs/<spec>/order.json`, as rule 8 says.

Everything else in the pack and in Addendum 1 stands. The SHA-256 of this file is in `ADDENDUM-2-SHA256.txt`, sealed by FreeTSA.
