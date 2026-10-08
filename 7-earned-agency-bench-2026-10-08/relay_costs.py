"""Read the coat-check relay's recorded calls (read only) and print the per-call cost basis used by `bench.py estimate`.

    python relay_costs.py ..\\coat-check-relay-2026-10-07\\runs\\real-1\\room.jsonl

Uses only the `call` records of that room: role, agent, tokens_in, tokens_out, cost_usd, and the time between the
first and last record (the relay ran one call at a time).
"""
import collections
import datetime as dt
import json
import sys


def load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def summarize(recs):
    calls = [r for r in recs if r["type"] == "call"]
    by_role, by_model = collections.defaultdict(list), collections.defaultdict(list)
    for c in calls:
        by_role[c["role"]].append(c)
        by_model[c["agent"]].append(c)

    def agg(cs):
        n = len(cs)
        return {"calls": n, "tokens_in": sum(c["tokens_in"] for c in cs) / n, "tokens_out": sum(c["tokens_out"] for c in cs) / n,
                "cost_usd": sum(c["cost_usd"] for c in cs) / n, "at_out_cap": sum(1 for c in cs if c["tokens_out"] >= 4000),
                "invalid": sum(1 for c in cs if not c["valid"])}

    t0 = dt.datetime.strptime(recs[0]["ts"], "%Y-%m-%dT%H:%M:%SZ")
    t1 = dt.datetime.strptime(recs[-1]["ts"], "%Y-%m-%dT%H:%M:%SZ")
    return {"calls": len(calls), "total_cost_usd": sum(c["cost_usd"] for c in calls),
            "seconds_per_call": (t1 - t0).total_seconds() / len(calls),
            "by_role": {k: agg(v) for k, v in by_role.items()}, "by_model": {k: agg(v) for k, v in by_model.items()}}


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    s = summarize(load(argv[0]))
    print(json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
