"""Read the recorded calls of a room (read only) and print, per model and per role, the mean tokens, seconds and cost.

    python call_costs.py runs\\smoke-1\\room.jsonl [--json]

Cost is recomputed from the tokens and the prices in config.json: in x price_in + out x price_out. The broker's out count
already holds the reasoning tokens, so reasoning is not added.
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_prices():
    cfg = json.loads((HERE / "config.json").read_text(encoding="utf-8"))
    return {m["id"]: (m["price_in_per_m"], m["price_out_per_m"]) for m in cfg["models"]}


def summarize(recs, prices=None):
    prices = prices or load_prices()
    calls = [r for r in recs if r["type"] == "call"]
    groups = collections.defaultdict(list)
    for c in calls:
        groups[(c["agent"], c["role"])].append(c)
    out = {}
    for (agent, role), cs in sorted(groups.items()):
        pin, pout = prices[agent.split("@")[0]]
        n = len(cs)
        cost = [(c["tokens_in"] * pin + c["tokens_out"] * pout) / 1e6 for c in cs]
        out[f"{agent}|{role}"] = {
            "calls": n, "invalid": sum(1 for c in cs if not c["valid"]),
            "tokens_in": sum(c["tokens_in"] for c in cs) / n, "tokens_out": sum(c["tokens_out"] for c in cs) / n,
            "tokens_reasoning": sum(c.get("tokens_reasoning") or 0 for c in cs) / n,
            "seconds": sum((c.get("wall_ms") or 0) for c in cs) / n / 1000, "cost_usd": sum(cost) / n,
            "at_out_cap": sum(1 for c in cs if c["tokens_out"] >= 4000),
        }
    by_role = {}
    for role in sorted({c["role"] for c in calls}):
        cs = [c for c in calls if c["role"] == role]
        n = len(cs)
        by_role[role] = {"calls": n, "tokens_in": sum(c["tokens_in"] for c in cs) / n, "tokens_out": sum(c["tokens_out"] for c in cs) / n,
                         "seconds": sum((c.get("wall_ms") or 0) for c in cs) / n / 1000,
                         "cost_usd": sum((c["tokens_in"] * prices[c["agent"].split("@")[0]][0] + c["tokens_out"] * prices[c["agent"].split("@")[0]][1]) / 1e6 for c in cs) / n}
    return {"calls": len(calls), "by_model_role": out, "by_role": by_role}


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    recs = [json.loads(l) for l in Path(args[0]).read_text(encoding="utf-8").splitlines() if l]
    s = summarize(recs)
    if "--json" in argv:
        print(json.dumps(s, indent=2))
        return 0
    print(f"{s['calls']} calls")
    for k, v in s["by_model_role"].items():
        print(f"  {k}: {v['calls']} calls, {v['invalid']} invalid; in {v['tokens_in']:.0f}, out {v['tokens_out']:.0f} (reasoning {v['tokens_reasoning']:.0f}); "
              f"{v['seconds']:.1f} s; US${v['cost_usd']:.6f} a call; {v['at_out_cap']} at the 4000 cap")
    for k, v in s["by_role"].items():
        print(f"  all models, {k}: in {v['tokens_in']:.0f}, out {v['tokens_out']:.0f}; {v['seconds']:.1f} s; US${v['cost_usd']:.6f} a call")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
