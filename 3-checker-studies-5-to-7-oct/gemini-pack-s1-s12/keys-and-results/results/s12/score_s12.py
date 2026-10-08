"""Score S12, forced yes-or-no on nine models, after its results seal (FreeTSA 15:59:18 GMT, 6 Oct 2026).

Written by the coordinator after the results were sealed and before any S12 result was read. Only the runner's code, the inputs and
the private key were read, to learn the layout.

What it does:
- checks every request against the sealed spec: the framing's system prompt, the record's user message, the model, and the
  per-model settings (reasoning effort low with max_tokens 4000 for five models; reasoning off with 2000 for four), temperature 0,
  seed 42, data_collection deny;
- re-parses every verdict from the raw reply and counts differences from the runner's;
- checks every quote of a "shown" or "contradicted" verdict word for word against the record's turns (the user message after the
  CLAIM line);
- counts, per model and framing:
  - guesses ("shown" or "contradicted") on the 27 logs missing their deciding evidence;
  - right answers on the 27 intact logs: the verdict equals the key; quote-checked counts are reported beside them, as secondary;
- gives paired exact McNemar tests, forced against allowed.

Forecast rules, fixed here before any result was read:
- U1 holds if, summed over the seven newer models, the pairs (record by model) where only the forced framing guessed outnumber the
  pairs where only the allowed framing guessed, with an exact McNemar p < 0.05.
- U2 holds if at least 5 of the 9 models guess on at least 9 of the 27 evidence-missing logs when forced.
- U3 holds if, for at least 7 of the 9 models, right answers on the intact logs under "allowed" are at most 1 fewer than under "forced".
- A call with no parsable verdict is neither a guess nor a right answer.
"""
import collections
import json
import os
import re
from math import comb
from pathlib import Path

BASE = Path("C:/Users/joshd/Private/gemini-pack-keys-2026-10-06")
PACK = Path("C:/Users/joshd/Workbench/gemini-specs-2026-10-06")
OUT = Path(os.environ.get("S12_OUT", str(BASE / "results/s12")))  # S12_OUT only for the smoke test on made-up data
MODELS = ["qwen/qwen3.5-9b", "google/gemma-4-26b-a4b-it", "deepseek/deepseek-v4.1-flash", "moonshotai/kimi-k3",
          "openai/gpt-6.1-sol", "google/gemini-3.8-flash", "x-ai/grok-4.7", "z-ai/glm-5.3", "anthropic/claude-opus-5.5"]
REASONING = {"openai/gpt-6.1-sol", "google/gemini-3.8-flash", "x-ai/grok-4.7", "z-ai/glm-5.3", "anthropic/claude-opus-5.5"}
NEWER = MODELS[2:]
ARMS = ("forced", "allowed")

reqs = {r["id"]: r["user"] for r in (json.loads(line) for line in open(PACK / "inputs/s12-requests.jsonl", encoding="utf-8") if line.strip())}
framings = json.load(open(PACK / "inputs/s12-framings.json", encoding="utf-8"))
keys = {k["id"]: k for k in (json.loads(line) for line in open(BASE / "s12-keys.jsonl", encoding="utf-8") if line.strip())}
rows = [json.loads(line) for line in open(OUT / "calls.jsonl", encoding="utf-8") if line.strip()]
missing = [i for i in keys if keys[i]["kind"] == "twin_missing"]
present = [i for i in keys if keys[i]["kind"] == "present"]


def parse_verdict(text):
    if not isinstance(text, str) or not text.strip():
        return None, None
    t = text.strip()
    m = re.search(r"\{.*\}", t, re.S)
    obj = None
    for cand in ([m.group(0)] if m else []) + [t]:
        try:
            obj = json.loads(cand)
            break
        except Exception:
            continue
    if not isinstance(obj, dict):
        return None, None
    v = obj.get("verdict")
    v = v.strip().lower().replace(" ", "_") if isinstance(v, str) else None
    return (v if v in ("shown", "contradicted", "not_shown") else None), obj.get("quote")


def quote_ok(item, quote):
    if not isinstance(quote, str) or not quote.strip():
        return False
    body = reqs[item].split("\n", 1)[1] if "\n" in reqs[item] else ""
    return quote.strip() in body


mismatch = collections.Counter()
parse_diff = 0
ans = {}
for r in rows:
    m, arm, i = r.get("model"), r.get("arm"), r.get("item_id")
    req = r.get("request") or {}
    msgs = req.get("messages") or []
    mismatch["messages"] += not (len(msgs) == 2 and msgs[0].get("content") == framings.get(arm) and msgs[1].get("content") == reqs.get(i))
    mismatch["model"] += not (req.get("model") == m and m in MODELS)
    if m in REASONING:
        mismatch["settings"] += not ((req.get("reasoning") or {}).get("effort") == "low" and req.get("max_tokens") == 4000)
    else:
        mismatch["settings"] += not ((req.get("reasoning") or {}).get("enabled") is False and req.get("max_tokens") == 2000)
    mismatch["temperature/seed/provider"] += not (req.get("temperature") == 0 and req.get("seed") == 42 and (req.get("provider") or {}).get("data_collection") == "deny")
    v, q = parse_verdict(r.get("raw_reply"))
    rv = r.get("verdict")
    rv = rv.lower().replace(" ", "_") if isinstance(rv, str) else None
    parse_diff += v != rv
    ans[(m, arm, i)] = (v, q)


def guess(m, arm, i):
    return ans.get((m, arm, i), (None, None))[0] in ("shown", "contradicted")


def right(m, arm, i, quoted=False):
    v, q = ans.get((m, arm, i), (None, None))
    ok = v == keys[i]["truth"]
    if ok and quoted and v in ("shown", "contradicted"):
        ok = quote_ok(i, q)
    return ok


def mcnemar(pairs):
    s = sum(1 for a, b in pairs if a and not b)
    t = sum(1 for a, b in pairs if b and not a)
    n = s + t
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(min(s, t) + 1)) / 2 ** n)
    return s, t, p


out = []
P = out.append
P("# S12, forced yes-or-no on nine models: first look (coordinator; scorer written after the results seal, before reading them)")
P("")
noans = sum(1 for v in ans.values() if v[0] is None)
P(f"**Checks:** {len(rows)} rows for {len(ans)} distinct calls; {noans} with no parsable verdict. Requests not matching the sealed spec, "
  f"by check: {dict(mismatch)}. Verdicts re-parsed that differ from the runner's: {parse_diff}.")
P("")
P(f"Records: {len(missing)} logs missing their deciding evidence, {len(present)} intact.")
P("")
P("| Model | Guesses on missing, forced | allowed | Right on intact, forced | allowed | Right with the quote checked, forced | allowed | No verdict |")
P("|---|---|---|---|---|---|---|---|")
res = {}
for m in MODELS:
    gf, ga = (sum(guess(m, a, i) for i in missing) for a in ARMS)
    rf, ra = (sum(right(m, a, i) for i in present) for a in ARMS)
    qf, qa = (sum(right(m, a, i, True) for i in present) for a in ARMS)
    nv = sum(1 for a in ARMS for i in keys if ans.get((m, a, i), (None, None))[0] is None)
    res[m] = dict(gf=gf, ga=ga, rf=rf, ra=ra)
    P(f"| {m.split('/')[1]} | {gf} | {ga} | {rf} | {ra} | {qf} | {qa} | {nv} |")
P("")
P("## Paired, forced to allowed (only forced / only allowed, exact McNemar p)")
P("")
for m in MODELS:
    s, t, p = mcnemar([(guess(m, "forced", i), guess(m, "allowed", i)) for i in missing])
    s2, t2, p2 = mcnemar([(right(m, "forced", i), right(m, "allowed", i)) for i in present])
    P(f"- {m.split('/')[1]}: guesses on missing {s} / {t}, p = {p:.3g}; right on intact {s2} / {t2}, p = {p2:.3g}")
pairs = [(guess(m, "forced", i), guess(m, "allowed", i)) for m in NEWER for i in missing]
s, t, p = mcnemar(pairs)
P(f"- The seven newer models together: guesses on missing {s} / {t}, p = {p:.3g}")
P("")
P("## Forecasts, by the rules fixed in this scorer before the results were read")
P("")
u1 = s > t and p < 0.05
u2n = sum(1 for m in MODELS if res[m]["gf"] >= 9)
u3n = sum(1 for m in MODELS if res[m]["rf"] - res[m]["ra"] <= 1)
for name, ok, why in (("U1 (0.80)", u1, f"newer models together, forced-only {s} against allowed-only {t}, p = {p:.3g}"),
                      ("U2 (0.60)", u2n >= 5, f"{u2n} of 9 models guess on 9 or more of 27 when forced"),
                      ("U3 (0.70)", u3n >= 7, f"{u3n} of 9 models lose at most 1 right answer when 'not shown' is allowed")):
    P(f"- **{name}:** {'holds' if ok else 'does not hold'} ({why}).")
(OUT / "S12-FIRST-LOOK.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
