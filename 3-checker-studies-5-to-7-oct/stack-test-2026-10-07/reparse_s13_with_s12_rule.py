"""Exploratory re-parse of S13 with S12's verdict rule (written 7 Oct 2026, after the sealed scorer ran and its output was read).

Why: the sealed scorer (score_s13.py, sealed 08:12:05 GMT) re-parsed verdicts with the runner's rule, which only finds a JSON object
with no braces inside it. Replies that quote a log line which is itself JSON ("quote": "{\"commit\": ...}") hold a verdict that this
rule cannot see, so they were counted as "no verdict". S12's scorer, which produced the API numbers S13 compares against, takes the
text from the first "{" to the last "}" and parses that. This script applies S12's rule to both stacks so the comparison is like for
like. It is exploratory: the sealed scorer's output stands as the scored result.
"""
import collections
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
keys = {k["id"]: k for k in (json.loads(l) for l in open(KEYS, encoding="utf-8") if l.strip())}
missing = [i for i in keys if keys[i]["kind"] == "twin_missing"]
present = [i for i in keys if keys[i]["kind"] == "present"]


def s12_rule(text):
    """S12's scorer, exactly: first '{' to last '}', else the whole text; verdict lower-cased, spaces to underscores."""
    if not isinstance(text, str) or not text.strip():
        return None
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
        return None
    v = obj.get("verdict")
    v = v.strip().lower().replace(" ", "_") if isinstance(v, str) else None
    return v if v in VERDICTS else None


def mcnemar(pairs):
    s = sum(1 for a, b in pairs if a and not b)
    t = sum(1 for a, b in pairs if b and not a)
    n = s + t
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(min(s, t) + 1)) / 2 ** n)
    return s, t, p


stack, changed = {}, collections.Counter()
for tool in TOOLS:
    for line in open(HERE / f"results/{tool}.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            v = s12_rule(r.get("reply_text"))
            stack[(tool, r["framing"], r["id"])] = v
            if v != r.get("verdict"):
                changed[(tool, "found a verdict" if r.get("verdict") is None else ("lost a verdict" if v is None else "changed"))] += 1
api = {}
for line in open(S12_CALLS, encoding="utf-8"):
    if line.strip():
        r = json.loads(line)
        for tool, model in TOOLS.items():
            if r.get("model") == model:
                api[(tool, r.get("arm"), r.get("item_id"))] = s12_rule(r.get("raw_reply"))

out = []
P = out.append
P("# S13, exploratory re-parse with S12's verdict rule (after the sealed scorer ran; not the scored result)")
P("")
P("Calls whose verdict differs from the runner's rule: " + "; ".join(f"{t} {k}: {n}" for (t, k), n in sorted(changed.items())))
P("")
P("| | Guesses on missing, forced | allowed | Right on intact, forced | allowed | No verdict |")
P("|---|---|---|---|---|---|")
res = {}
for src, d in (("stack", stack), ("API (S12)", api)):
    for tool in TOOLS:
        g = {a: sum(d.get((tool, a, i)) in ("shown", "contradicted") for i in missing) for a in ARMS}
        rt = {a: sum(d.get((tool, a, i)) == keys[i]["truth"] for i in present) for a in ARMS}
        nv = sum(1 for a in ARMS for i in keys if d.get((tool, a, i)) is None)
        res[(src, tool)] = dict(g=g, rt=rt, nv=nv)
        P(f"| {tool} {src} | {g['forced']} of 27 | {g['allowed']} of 27 | {rt['forced']} of 27 | {rt['allowed']} of 27 | {nv} of 108 |")
P("")
P("No-verdict calls left in the stacks, by framing and kind of log:")
for tool in TOOLS:
    by = collections.Counter((a, "missing" if keys[i]["kind"] == "twin_missing" else "intact") for a in ARMS for i in keys if stack.get((tool, a, i)) is None)
    P(f"- {tool}: " + ("; ".join(f"{a}, {k}: {n}" for (a, k), n in sorted(by.items())) or "none"))
P("")
P("Paired tests:")
for tool in TOOLS:
    s, t, p = mcnemar([(stack.get((tool, "forced", i)) in ("shown", "contradicted"), stack.get((tool, "allowed", i)) in ("shown", "contradicted")) for i in missing])
    P(f"- {tool} stack, forced to allowed, guesses on missing: only forced {s}, only allowed {t}, p = {p:.3g}")
    s, t, p = mcnemar([(stack.get((tool, "forced", i)) in ("shown", "contradicted"), api.get((tool, "forced", i)) in ("shown", "contradicted")) for i in missing])
    P(f"- {tool}, forced, missing, stack against API: guessed only in the stack {s}, only in the API {t}, p = {p:.3g}")
    same = sum(1 for a in ARMS for i in keys if stack.get((tool, a, i)) == api.get((tool, a, i)))
    P(f"- {tool}: same verdict as its S12 API run on {same} of 108")
(HERE / "results" / "S13-REPARSE-S12-RULE.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("\n".join(out))
