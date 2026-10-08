"""Score S13, the stack test, after its results seal (FreeTSA 08:09:49 GMT, 7 Oct 2026).

Written by the coordinator after the results were sealed and before this scorer was run. Only the runner's code, the row field
names, the inputs, the S12 key and S12's own scorer were read to learn the layout. (Before writing it, the coordinator had seen the
runners' raw progress lines, as CLAUDE-FORECASTS-0722.md states; no count below had been computed against the key.)

What it does:
- checks each tool's rows: 108 rows, each record and framing once, and every prompt's SHA-256 equal to the sealed construction
  (the framing text, a blank line, then the record's user text, byte for byte);
- re-parses every verdict from the raw reply with the runner's own sealed rule (the last JSON object holding a valid verdict) and
  counts differences from the runner's recorded verdict;
- counts, per tool and framing:
  - guesses ("shown" or "contradicted") on the 27 logs missing their deciding evidence;
  - right answers on the 27 intact logs (the verdict equals the key); quote-checked counts beside them, as secondary;
  - calls with no verdict, by status, by framing and by kind of log;
- gives paired exact McNemar tests, forced against allowed;
- compares each tool with its own model's S12 API run (openai/gpt-6.1-sol, google/gemini-3.8-flash), record by record and framing by
  framing.

Rules fixed here before any count was computed:
- A call with no verdict is neither a guess nor a right answer.
- "Same verdict as S12" means both calls give the same value, where "no verdict" counts as a value of its own.
- K1 to K6 are scored as worded in DESIGN.md (sealed 06:14:50 GMT). K3 and K6 hold only if they hold for both tools; K4 and K5 too.
- SA1 to SA8 are scored as worded in CLAUDE-FORECASTS-0722.md (sealed 07:23:38 GMT). SA8 pairs each evidence-missing record's forced
  call in the Sol stack with the same record's forced call in Sol's S12 API run: it holds if the stack guesses on fewer records and the
  exact McNemar p < 0.001.
"""
import collections
import hashlib
import json
import re
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
KEYS = Path("C:/Users/joshd/Private/gemini-pack-keys-2026-10-06/s12-keys.jsonl")
S12_CALLS = Path("C:/Users/joshd/Private/gemini-pack-keys-2026-10-06/results/s12/calls.jsonl")
TOOLS = {"sol": "openai/gpt-6.1-sol", "gemini": "google/gemini-3.8-flash"}
ARMS = ("forced", "allowed")
VERDICTS = ("shown", "contradicted", "not_shown")

reqs = {r["id"]: r["user"] for r in (json.loads(l) for l in open(HERE / "inputs/s12-requests.jsonl", encoding="utf-8") if l.strip())}
framings = json.load(open(HERE / "inputs/s12-framings.json", encoding="utf-8"))
keys = {k["id"]: k for k in (json.loads(l) for l in open(KEYS, encoding="utf-8") if l.strip())}
missing = [i for i in keys if keys[i]["kind"] == "twin_missing"]
present = [i for i in keys if keys[i]["kind"] == "present"]


def parse_verdict(text):
    """The runner's sealed rule: the last JSON object in the text that has a valid verdict."""
    found = None
    for m in re.finditer(r"\{[^{}]*\"verdict\"[^{}]*\}", text or "", flags=re.S):
        try:
            obj = json.loads(m.group(0))
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("verdict") in VERDICTS:
            found = obj
    return found


def quote_ok(item, quote):
    if not isinstance(quote, str) or not quote.strip():
        return False
    body = reqs[item].split("\n", 1)[1] if "\n" in reqs[item] else ""
    return quote.strip() in body


def mcnemar(pairs):
    s = sum(1 for a, b in pairs if a and not b)
    t = sum(1 for a, b in pairs if b and not a)
    n = s + t
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(min(s, t) + 1)) / 2 ** n)
    return s, t, p


# S13 rows
checks, ans, status = {}, {}, {}
for tool in TOOLS:
    rows = [json.loads(l) for l in open(HERE / f"results/{tool}.jsonl", encoding="utf-8") if l.strip()]
    seen = collections.Counter((r["id"], r["framing"]) for r in rows)
    bad_prompt = sum(1 for r in rows if r["prompt_sha256"] != hashlib.sha256((framings[r["framing"]] + "\n\n" + reqs[r["id"]]).encode("utf-8")).hexdigest())
    parse_diff = 0
    for r in rows:
        obj = parse_verdict(r.get("reply_text"))
        v = obj["verdict"] if obj else None
        parse_diff += v != r.get("verdict")
        ans[(tool, r["framing"], r["id"])] = (v, (obj or {}).get("quote"))
        status[(tool, r["framing"], r["id"])] = r.get("status")
    checks[tool] = dict(rows=len(rows), distinct=len(seen), duplicates=sum(1 for c in seen.values() if c > 1),
                        expected=len(keys) * 2, bad_prompt=bad_prompt, parse_diff=parse_diff)

# S12 API rows for the same two models (the last row wins, as in S12's scorer)
api = {}
for line in open(S12_CALLS, encoding="utf-8"):
    if not line.strip():
        continue
    r = json.loads(line)
    for tool, model in TOOLS.items():
        if r.get("model") == model:
            text = r.get("raw_reply")
            m = re.search(r"\{.*\}", text.strip(), re.S) if isinstance(text, str) and text.strip() else None
            obj = None
            for cand in ([m.group(0)] if m else []) + ([text.strip()] if isinstance(text, str) else []):
                try:
                    obj = json.loads(cand)
                    break
                except Exception:
                    continue
            v = obj.get("verdict") if isinstance(obj, dict) else None
            v = v.strip().lower().replace(" ", "_") if isinstance(v, str) else None
            api[(tool, r.get("arm"), r.get("item_id"))] = v if v in VERDICTS else None


def v_of(tool, arm, i):
    return ans.get((tool, arm, i), (None, None))[0]


def guess(tool, arm, i):
    return v_of(tool, arm, i) in ("shown", "contradicted")


def right(tool, arm, i, quoted=False):
    v, q = ans.get((tool, arm, i), (None, None))
    ok = v == keys[i]["truth"]
    if ok and quoted and v in ("shown", "contradicted"):
        ok = quote_ok(i, q)
    return ok


out = []
P = out.append
P("# S13, the stack test: first look (coordinator; scorer written after the results seal and sealed before it was run)")
P("")
for tool, c in checks.items():
    P(f"**Checks, {tool}:** {c['rows']} rows, {c['distinct']} distinct record-and-framing calls of {c['expected']}, {c['duplicates']} duplicated; "
      f"prompts not matching the sealed construction: {c['bad_prompt']}; verdicts re-parsed that differ from the runner's: {c['parse_diff']}.")
P(f"**S12 API rows found:** sol {sum(1 for k in api if k[0] == 'sol')}, gemini {sum(1 for k in api if k[0] == 'gemini')} (108 expected each).")
P("")
P(f"Records: {len(missing)} logs missing their deciding evidence, {len(present)} intact (key sealed 6 Oct 2026).")
P("")
P("| Stack | Guesses on missing, forced | allowed | Right on intact, forced | allowed | Right with the quote checked, forced | allowed | No verdict |")
P("|---|---|---|---|---|---|---|---|")
res = {}
for tool in TOOLS:
    gf, ga = (sum(guess(tool, a, i) for i in missing) for a in ARMS)
    rf, ra = (sum(right(tool, a, i) for i in present) for a in ARMS)
    qf, qa = (sum(right(tool, a, i, True) for i in present) for a in ARMS)
    nv = sum(1 for a in ARMS for i in keys if v_of(tool, a, i) is None)
    res[tool] = dict(gf=gf, ga=ga, rf=rf, ra=ra, nv=nv)
    P(f"| {tool} | {gf} of 27 | {ga} of 27 | {rf} of 27 | {ra} of 27 | {qf} of 27 | {qa} of 27 | {nv} of 108 |")
P("")
P("For comparison, the same models through the plain API in S12 (computed here from S12's sealed calls):")
P("")
P("| S12 API | Guesses on missing, forced | allowed | Right on intact, forced | allowed | No verdict |")
P("|---|---|---|---|---|---|")
for tool, model in TOOLS.items():
    gf = sum(api.get((tool, "forced", i)) in ("shown", "contradicted") for i in missing)
    ga = sum(api.get((tool, "allowed", i)) in ("shown", "contradicted") for i in missing)
    rf = sum(api.get((tool, "forced", i)) == keys[i]["truth"] for i in present)
    ra = sum(api.get((tool, "allowed", i)) == keys[i]["truth"] for i in present)
    nv = sum(1 for a in ARMS for i in keys if api.get((tool, a, i)) is None)
    res[tool].update(api_gf=gf)
    P(f"| {model} | {gf} of 27 | {ga} of 27 | {rf} of 27 | {ra} of 27 | {nv} of 108 |")
P("")
P("## Calls with no verdict")
P("")
for tool in TOOLS:
    by = collections.Counter()
    for a in ARMS:
        for i in keys:
            if v_of(tool, a, i) is None:
                by[(a, keys[i]["kind"], status.get((tool, a, i)))] += 1
    P(f"- {tool}: " + ("; ".join(f"{a}, {'missing' if k == 'twin_missing' else 'intact'}, {s}: {n}" for (a, k, s), n in sorted(by.items())) or "none"))
P("")
P("## Paired, forced to allowed (only forced / only allowed, exact McNemar p)")
P("")
mc = {}
for tool in TOOLS:
    s, t, p = mcnemar([(guess(tool, "forced", i), guess(tool, "allowed", i)) for i in missing])
    s2, t2, p2 = mcnemar([(right(tool, "forced", i), right(tool, "allowed", i)) for i in present])
    mc[tool] = (s, t, p)
    P(f"- {tool}: guesses on missing {s} / {t}, p = {p:.3g}; right on intact {s2} / {t2}, p = {p2:.3g}")
P("")
P("## Against the same model's S12 API run (108 record-and-framing pairs each)")
P("")
same = {}
for tool in TOOLS:
    pairs = [(a, i) for a in ARMS for i in keys]
    same[tool] = sum(1 for a, i in pairs if v_of(tool, a, i) == api.get((tool, a, i)))
    P(f"- {tool}: same verdict on {same[tool]} of 108")
s8, t8, p8 = mcnemar([(guess("sol", "forced", i), api.get(("sol", "forced", i)) in ("shown", "contradicted")) for i in missing])
P(f"- Sol, forced, evidence-missing records: guessed in the stack only {s8}, in the API only {t8}, exact McNemar p = {p8:.3g}")
P("")
P("## Forecasts, by the rules fixed in this scorer before any count was computed")
P("")
sol_nv_forced_missing = sum(1 for i in missing if v_of("sol", "forced", i) is None)
sol_nv_intact = sum(1 for a in ARMS for i in present if v_of("sol", a, i) is None)
parseable = {t: 108 - res[t]["nv"] for t in TOOLS}
k3 = all(mc[t][0] > mc[t][1] and mc[t][2] < 0.05 for t in TOOLS)
rows = [
    ("K1 (0.70)", res["sol"]["gf"] >= 20, f"Sol stack forced guesses on missing: {res['sol']['gf']} of 27 (needs 20 or more)"),
    ("K2 (0.60)", res["gemini"]["gf"] >= 15, f"Gemini stack forced guesses on missing: {res['gemini']['gf']} of 27 (needs 15 or more)"),
    ("K3 (0.85)", k3, "; ".join(f"{t} {mc[t][0]} / {mc[t][1]}, p = {mc[t][2]:.3g}" for t in TOOLS) + " (both need forced-only above allowed-only, p < 0.05)"),
    ("K4 (0.75)", all(res[t]["ra"] >= 25 for t in TOOLS), "; ".join(f"{t} {res[t]['ra']} of 27" for t in TOOLS) + " right on intact, allowed (both need 25 or more)"),
    ("K5 (0.55)", all(same[t] >= 90 for t in TOOLS), "; ".join(f"{t} {same[t]} of 108" for t in TOOLS) + " same as S12 (both need 90 or more)"),
    ("K6 (0.70)", all(parseable[t] >= 100 for t in TOOLS), "; ".join(f"{t} {parseable[t]} of 108" for t in TOOLS) + " with a verdict (both need 100 or more)"),
    ("SA1 (0.85)", res["sol"]["gf"] <= 8, f"Sol stack forced guesses on missing: {res['sol']['gf']} of 27 (needs 8 or fewer)"),
    ("SA2 (0.70)", sol_nv_forced_missing >= 24, f"Sol no-verdict calls that are forced, on missing logs: {sol_nv_forced_missing} of {res['sol']['nv']} (needs 24 or more)"),
    ("SA3 (0.70)", sol_nv_intact <= 2, f"Sol no-verdict calls on intact logs: {sol_nv_intact} (needs 2 or fewer)"),
    ("SA4 (0.75)", res["sol"]["ra"] >= 25, f"Sol stack right on intact, allowed: {res['sol']['ra']} of 27 (needs 25 or more)"),
    ("SA5 (0.75)", res["gemini"]["ra"] >= 25, f"Gemini stack right on intact, allowed: {res['gemini']['ra']} of 27 (needs 25 or more)"),
    ("SA6 (0.75)", res["gemini"]["gf"] >= 20, f"Gemini stack forced guesses on missing: {res['gemini']['gf']} of 27 (needs 20 or more)"),
    ("SA7 (0.70)", res["gemini"]["ga"] <= 5, f"Gemini stack allowed guesses on missing: {res['gemini']['ga']} of 27 (needs 5 or fewer)"),
    ("SA8 (0.85)", s8 < t8 and p8 < 0.001, f"Sol forced, missing: stack-only {s8}, API-only {t8}, p = {p8:.3g} (needs fewer in the stack, p < 0.001)"),
]
for name, ok, why in rows:
    P(f"- **{name}:** {'holds' if ok else 'does not hold'} ({why}).")
P("")
P("One outcome scores a forecast; it does not show that a probability was right or wrong.")
(HERE / "results" / "S13-FIRST-LOOK.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("\n".join(out))
