"""Score S9, the wobble test, after its results seal.

Written by the coordinator (Claude) on 6 Oct 2026, and sealed before any S9 result was copied or read. Only the field names of
one record were looked at, to read the file.

What it does:
- re-checks every request against the sealed spec (S9-WOBBLE.md with Addendum 6): the messages from receipt_pair's prepare,
  the model, temperature and seed per arm, max_tokens 400, reasoning off, data_collection deny;
- re-checks order.json against Addendum 6's method (the base list, shuffled once with random.Random(20261006));
- re-runs receipt_pair's quote check (commit b7dfbad) on every reply, and counts where it differs from the runner's;
- counts, per model, false "shown" (of 240) and true "shown" kept (of 40), for:
  - W0;
  - "all five agree" ("shown" only if all five W5 samples are verified "shown");
  - "majority of five" (at least 3 of 5);
- compares one model agreeing with itself (all five) against two models agreeing at W0 (rule r2, "shown needs both");
- counts how often the five samples split, where W0 was right against where it was wrong;
- resolves the sealed forecasts by the rules below.

Forecast rules, fixed here before any result was seen:
- P1 holds if, for both models, "all five agree" has fewer false "shown" than W0, with exact McNemar p < 0.05 (paired, on the 240).
- P2 holds if, for both models, "all five agree" keeps at least 85% of W0's true "shown" (of the 40).
- P3 holds if r2 at W0 has fewer false "shown" than "all five agree", for each model.
- P4 holds if, pooled over both models, the share of records whose samples split is higher where W0 was wrong than where it
  was right.
  - "Right" means W0's answer equals the key's truth ("shown", "contradicted" or "not_shown").
  - A record splits when its five samples don't all give the same answer.
  - A two-way version (shown against anything else) is reported too, labelled secondary.
- Jev 1 ("the wobble catches half the false passes, keeping 80% of true ones") holds if, pooled over both models, "all five
  agree" stops at least half of W0's false "shown" and keeps at least 80% of W0's true "shown".
- Jev 2 ("cross-model is the better warning") holds under P3's rule.

Run after the results are copied to this folder and sealed: python score_s9.py
"""
import collections
import json
import os
import random
import sys
from math import comb
from pathlib import Path

VENDOR = Path("C:/Users/joshd/AppData/Local/Temp/claude/C--Users-joshd-AppData-Roaming-Claude-scratch-workspaces-fd692c9b-fbaf-43f4-83e5-a4fc2af28829-304e406a-9554-4c05-9669-3eee15c68287-scratch-2026-09-28-855a22/9ade3c6b-7215-4ad7-b2c4-7ebb4abcf721/scratchpad/rp-b7dfbad")
sys.path.insert(0, str(VENDOR))
from receipt_pair import pair, reader, rules  # noqa: E402

BASE = Path("C:/Users/joshd/Private/gemini-pack-keys-2026-10-06")
PACK = Path("C:/Users/joshd/Workbench/gemini-specs-2026-10-06")
OUT = Path(os.environ.get("S9_OUT", str(BASE / "results/s9")))  # S9_OUT only for the smoke test on made-up data
MODELS = ["qwen/qwen3.5-9b", "google/gemma-4-26b-a4b-it"]
ARMS = [("W0", 0.0, 42)] + [("W5", 0.7, s) for s in (101, 102, 103, 104, 105)]
SEEDS5 = (101, 102, 103, 104, 105)


def norm(a):
    return None if a is None else a.replace(" ", "_")


def short(m):
    return m.split("/")[1]


items_list = [json.loads(line) for line in open(PACK / "inputs/s8-items.jsonl", encoding="utf-8") if line.strip()]
items = {i["id"]: i for i in items_list}
keys = {k["id"]: k for k in (json.loads(line) for line in open(BASE / "s8-keys.jsonl", encoding="utf-8") if line.strip())}
rows = [json.loads(line) for line in open(OUT / "calls.jsonl", encoding="utf-8") if line.strip()]
order = json.load(open(OUT / "order.json", encoding="utf-8"))
prepared = {i: pair.prepare(i, it["claim"], it["turns"]) for i, it in items.items()}

# Order: Addendum 6's method.
base = [(i["id"], m, arm, seed) for i in items_list for m in MODELS for (arm, _t, seed) in ARMS]
expected = list(base)
random.Random(20261006).shuffle(expected)
got = [(o.get("item_id"), o.get("model"), o.get("arm"), o.get("seed")) for o in order]
order_ok = got == expected
order_same_set = sorted(got) == sorted(base)

# Requests, replies and quote checks.
mismatch = collections.Counter()
recheck_diff = 0
dupes = 0
no_answer = 0
cost = 0.0
ans = {}
for r in rows:
    key = (r.get("item_id"), r.get("model"), r.get("arm"), r.get("seed"))
    req, resp = r.get("request") or {}, r.get("response") or {}
    if key[0] not in prepared:
        mismatch["unknown item"] += 1
        continue
    shown, request = prepared[key[0]]
    want = {"W0": (0.0, 42)}.get(key[2]) or (0.7, key[3])
    msgs = req.get("messages") or []
    temp = req.get("temperature")
    checks = {
        "messages": len(msgs) == 2 and msgs[0].get("content") == request.system and msgs[1].get("content") == request.user
        and msgs[0].get("role") == "system" and msgs[1].get("role") == "user",
        "model": req.get("model") == key[1] and key[1] in MODELS,
        "temperature": temp is not None and float(temp) == want[0],
        "seed": req.get("seed") == want[1] and (key[2] == "W0" or key[3] in SEEDS5),
        "max_tokens": req.get("max_tokens") == 400,
        "reasoning": (req.get("reasoning") or {}).get("enabled") is False,
        "provider": (req.get("provider") or {}).get("data_collection") == "deny",
    }
    for name, ok in checks.items():
        mismatch[name] += not ok
    usage = resp.get("usage") or {}
    cost += float(usage.get("cost") or 0)
    text = ((resp.get("choices") or [{}])[0].get("message") or {}).get("content")
    mine = reader.verify(text, shown).answer if text else "no answer"
    no_answer += mine == "no answer"
    rec = (r.get("verified") or {}).get("answer")
    recheck_diff += (rec is not None) and (mine != rec)
    if key in ans:
        dupes += 1
    if key not in ans or text:
        ans[key] = mine

unb = [i for i in items if keys[i]["truth"] != "shown"]
bkd = [i for i in items if keys[i]["truth"] == "shown"]


def w0(i, m):
    return ans.get((i, m, "W0", 42))


def five(i, m):
    return [ans.get((i, m, "W5", s)) for s in SEEDS5]


def all5(i, m):
    return "shown" if all(a == "shown" for a in five(i, m)) else "not all shown"


def maj(i, m):
    return "shown" if sum(a == "shown" for a in five(i, m)) >= 3 else "not majority"


def r2(i):
    a, b = w0(i, MODELS[0]), w0(i, MODELS[1])
    if a is None or b is None or "no answer" in (a, b):
        return "no answer"
    return rules.combine(a, b, "r2")


def mcn(ids, f, g):
    """Paired: s = shown under f only, t = shown under g only; exact two-sided McNemar."""
    s = sum(1 for i in ids if f(i) == "shown" and g(i) != "shown")
    t = sum(1 for i in ids if g(i) == "shown" and f(i) != "shown")
    n = s + t
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(min(s, t) + 1)) / 2 ** n)
    return s, t, p


def fisher(a, b, c, d):
    """Two-sided exact test on [[a, b], [c, d]]."""
    n1, n2, k, n = a + b, c + d, a + c, a + b + c + d

    def pr(x):
        return comb(n1, x) * comb(n2, k - x) / comb(n, k)
    obs = pr(a)
    lo, hi = max(0, k - n2), min(k, n1)
    return min(1.0, sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= obs * (1 + 1e-9)))


def count(ids, f):
    return sum(1 for i in ids if f(i) == "shown")


out = []
P = out.append
P("# S9, the wobble test: first look (coordinator; scorer sealed before the results were read)")
P("")
P(f"**Checks:** {len(rows)} rows for {len(ans)} distinct calls (duplicates {dupes}); {no_answer} without an answer. "
  f"Requests not matching the sealed spec, by check: {dict(mismatch)}. Quote checks re-run with receipt_pair b7dfbad that differ "
  f"from the runner's: {recheck_diff}. order.json: {'matches Addendum 6 exactly' if order_ok else 'does NOT match the Addendum 6 shuffle'}"
  f"{'' if order_ok else (' (same set of calls)' if order_same_set else ' (different set of calls)')}. Reported cost US${cost:.4f}.")
P("")
P(f"Records: {len(unb)} whose log doesn't back the claim, {len(bkd)} that do.")
P("")
P("## False \"shown\" (of 240) and true \"shown\" kept (of 40)")
P("")
P("| Model | W0 false | all five false | majority false | W0 kept | all five kept | majority kept |")
P("|---|---|---|---|---|---|---|")
res = {}
for m in MODELS:
    fw, fa, fm = (count(unb, lambda i, f=f: f(i, m)) for f in (w0, all5, maj))
    kw, ka, km = (count(bkd, lambda i, f=f: f(i, m)) for f in (w0, all5, maj))
    res[m] = dict(fw=fw, fa=fa, fm=fm, kw=kw, ka=ka, km=km)
    P(f"| {short(m)} | {fw} | {fa} | {fm} | {kw} | {ka} | {km} |")
fr2, kr2 = count(unb, r2), count(bkd, r2)
P(f"| both at W0 (r2) | {fr2} | | | {kr2} | | |")
P("")
P("## Paired comparisons (stopped / started, exact McNemar p)")
P("")
mc = {}
for m in MODELS:
    s, t, p = mcn(unb, lambda i: w0(i, m), lambda i: all5(i, m))
    s2, t2, p2 = mcn(bkd, lambda i: w0(i, m), lambda i: all5(i, m))
    s3, t3, p3 = mcn(unb, lambda i: w0(i, m), lambda i: maj(i, m))
    s4, t4, p4 = mcn(unb, lambda i: all5(i, m), lambda i: r2(i))
    mc[m] = dict(p_all5=p, s_all5=s, t_all5=t)
    P(f"- {short(m)}: W0 to all five, false \"shown\" {s} / {t}, p = {p:.3g}; true \"shown\" lost / gained {s2} / {t2}, p = {p2:.3g}. "
      f"W0 to majority, false \"shown\" {s3} / {t3}, p = {p3:.3g}. All five to r2, false \"shown\" {s4} / {t4}, p = {p4:.3g}.")
P("")
P("## The wobble: records whose five samples split")
P("")
pool = collections.Counter()
for m in MODELS:
    c = collections.Counter()
    c2 = collections.Counter()
    for i in items:
        a0 = w0(i, m)
        sp = len(set(five(i, m))) > 1
        right = norm(a0) == keys[i]["truth"]
        c[(right, sp)] += 1
        right2 = (a0 == "shown") == (keys[i]["truth"] == "shown")
        c2[(right2, sp)] += 1
    pool.update(c)
    pr_, pw_ = c[(True, True)], c[(False, True)]
    nr, nw = c[(True, True)] + c[(True, False)], c[(False, True)] + c[(False, False)]
    p = fisher(c[(False, True)], c[(False, False)], c[(True, True)], c[(True, False)])
    s2r, s2w = c2[(True, True)], c2[(False, True)]
    n2r, n2w = s2r + c2[(True, False)], s2w + c2[(False, False)]
    P(f"- {short(m)}: split on {pw_} of {nw} records where W0 was wrong, and {pr_} of {nr} where it was right (exact p = {p:.3g}). "
      f"Secondary, two-way: {s2w} of {n2w} against {s2r} of {n2r}.")
pw_all = pool[(False, True)]
nw_all = pool[(False, True)] + pool[(False, False)]
pr_all = pool[(True, True)]
nr_all = pool[(True, True)] + pool[(True, False)]
P(f"- Pooled: split on {pw_all} of {nw_all} where W0 was wrong, and {pr_all} of {nr_all} where it was right "
  f"(exact p = {fisher(pool[(False, True)], pool[(False, False)], pool[(True, True)], pool[(True, False)]):.3g}).")
P("")
P("## Forecasts, by the rules fixed in this scorer before the results")
P("")
p1 = all(res[m]["fa"] < res[m]["fw"] and mc[m]["p_all5"] < 0.05 for m in MODELS)
p2 = all(res[m]["ka"] >= 0.85 * res[m]["kw"] for m in MODELS)
p3 = all(fr2 < res[m]["fa"] for m in MODELS)
rate_w = pw_all / nw_all if nw_all else 0.0
rate_r = pr_all / nr_all if nr_all else 0.0
p4 = rate_w > rate_r
fw_sum = sum(res[m]["fw"] for m in MODELS)
stopped = sum(mcn(unb, lambda i, m=m: w0(i, m), lambda i, m=m: all5(i, m))[0] for m in MODELS)
kw_sum = sum(res[m]["kw"] for m in MODELS)
ka_sum = sum(res[m]["ka"] for m in MODELS)
j1 = fw_sum > 0 and stopped >= 0.5 * fw_sum and ka_sum >= 0.8 * kw_sum
for name, ok, why in (
    ("P1", p1, "all five cuts false \"shown\" for both models, p < 0.05"),
    ("P2", p2, "all five keeps at least 85% of W0's true \"shown\", both models"),
    ("P3", p3, "r2 at W0 has fewer false \"shown\" than all five, each model"),
    ("P4", p4, f"pooled split rate, W0 wrong {rate_w:.3f} against right {rate_r:.3f}"),
    ("Jev 1", j1, f"pooled: stopped {stopped} of {fw_sum} W0 false \"shown\"; kept {ka_sum} of {kw_sum} true"),
    ("Jev 2", p3, "same rule as P3"),
):
    P(f"- **{name}:** {'holds' if ok else 'does not hold'} ({why}).")
(OUT / "S9-FIRST-LOOK.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
