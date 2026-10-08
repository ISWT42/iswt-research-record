"""Routing: who gets which job, and which work is checked before it is handed on.

Pure functions, no model calls. The runner calls them; the scorer calls them again to prove that the plan
written into the room is the plan the rule gives.

AN ARM IS A PRESET OF FOUR FACTORS (the presets live in config.json; a new combination is a new config entry, no code)
  ticket    False / True   the shared coat-check ticket in the prompt
  certify   none           nothing is certified; the agent's own claim is handed on
            all            every piece of work is certified by an agent of another family (certify-only, no rewrite)
            table          a routed number of jobs per rank is certified (CHECKS_TABLED)
            fixed          the same number for every agent (CHECKS_FIXED), not tied to rank
  work      equal / table  2 jobs each, or 3, 2, 2, 1 by rank
  routing   equal          the agents' order turns by one place each round (used when nothing is routed)
            record         ranks by forecast accuracy so far (lowest mean Brier first)  - needs a random twin
            random         ranks by a seeded random order (the control)
  Routing applies only when something is routed: certify == table or work == table. Otherwise routing must be equal.

THE INVARIANTS, for ANY preset
  - Whenever checking is partial (table or fixed), every agent with work has at least MIN_CHECKS = 1 certified job every round.
  - The record of an agent is the forecasts THIS model made (the exact model name); a new model starts empty.
  - Routing by record reads only score (a), the forecast calibration.
  - A preset that routes by record has a random twin: the same factors with routing = random.

THE DEFAULT FIVE (exactly as in DESIGN.md)
  A baseline: ticket off, certify none, work equal.        B ticket: ticket on, certify none, work equal.
  C relay: ticket on, certify all, work equal.
  D earned: ticket on, certify table, work table, routing record.      E random: the same, routing random.
"""
from __future__ import annotations

import hashlib

import jobs as J

SEED = "earned-agency-bench-v1"
ROUNDS = 5
JOBS_PER_ROUND = 8
N_AGENTS = 4
EQUAL_WORK = (2, 2, 2, 2)
WORK_BY_RANK = (3, 2, 2, 1)
CHECKS_BY_RANK = (1, 1, 2, 1)       # certified jobs per rank when work is by table
CHECKS_BY_RANK_EQUAL_WORK = (1, 1, 1, 2)   # certified jobs per rank when everyone has 2 jobs (5 of 8 as well)
CHECKS_FIXED = (1, 1, 1, 1)         # one certified job for every agent, whatever its rank or record
MIN_CHECKS = 1          # no agent is ever left with no check, however good its record
MIN_RECORD = 1          # forecasts with a known result needed before an agent is ranked

WORK_TABLES = {"equal": EQUAL_WORK, "table": WORK_BY_RANK}
CHECKS_TABLED = {"table": CHECKS_BY_RANK, "equal": CHECKS_BY_RANK_EQUAL_WORK}      # keyed by the preset's work factor
FACTORS = {"ticket": (False, True), "certify": ("none", "all", "table", "fixed"), "work": ("equal", "table"),
           "routing": ("equal", "record", "random")}
PRESET_KEYS = {"name", "ticket", "certify", "work", "routing", "twin"}

assert sum(EQUAL_WORK) == sum(WORK_BY_RANK) == JOBS_PER_ROUND
for _work, _tab in CHECKS_TABLED.items():
    assert all(c >= MIN_CHECKS and c <= w for c, w in zip(_tab, WORK_TABLES[_work])), _work
assert all(c >= MIN_CHECKS and c <= min(WORK_BY_RANK) for c in CHECKS_FIXED)
assert sum(J.PER_ROUND.values()) == JOBS_PER_ROUND


# ----------------------------------------------------------------------------------------------
# Presets
# ----------------------------------------------------------------------------------------------
def is_routed(preset):
    return preset["certify"] == "table" or preset["work"] == "table"


def work_shares(preset):
    return WORK_TABLES[preset["work"]]


def check_counts(preset):
    """Certified jobs per rank (or per place in the turning order)."""
    c = preset["certify"]
    if c == "none":
        return (0, 0, 0, 0)
    if c == "all":
        return work_shares(preset)
    if c == "fixed":
        return CHECKS_FIXED
    return CHECKS_TABLED[preset["work"]]


def validate_presets(presets):
    """Refuse a bad set of presets: an unknown key or factor value; routing where nothing is routed; a preset that routes
    by record without its random twin (same factors, routing = random)."""
    if not presets:
        raise ValueError("config: no presets")
    for pid, p in presets.items():
        extra = set(p) - PRESET_KEYS
        missing = {"name", "ticket", "certify", "work", "routing"} - set(p)
        if extra or missing:
            raise ValueError(f"preset {pid}: unknown keys {sorted(extra)} or missing keys {sorted(missing)}")
        for f, allowed in FACTORS.items():
            if p[f] not in allowed or (f == "ticket" and not isinstance(p[f], bool)):
                raise ValueError(f"preset {pid}: {f} = {p[f]!r} is not one of {allowed}")
        if is_routed(p):
            if p["routing"] not in ("record", "random"):
                raise ValueError(f"preset {pid}: something is routed, so routing must be record or random")
        elif p["routing"] != "equal":
            raise ValueError(f"preset {pid}: nothing is routed (certify is not table and work is not table), so routing must be equal")
        if p["routing"] == "record":
            tw = p.get("twin")
            if not tw or tw not in presets:
                raise ValueError(f"preset {pid}: routes by record but has no random twin in the presets")
            t = presets[tw]
            same = all(t[f] == p[f] for f in ("ticket", "certify", "work"))
            if not same or t["routing"] != "random":
                raise ValueError(f"preset {pid}: its twin {tw} must have the same ticket, certify and work and routing = random")
        elif p.get("twin") is not None:
            raise ValueError(f"preset {pid}: only a preset that routes by record has a twin")
    return True


def validate_analysis(an, presets):
    """Refuse a declared analysis that names a preset that does not exist, or a primary pair that is not a record preset
    with its own random twin, or a validity arm that routes anything."""
    known = set(presets)
    a, b = an["primary"]["a"], an["primary"]["b"]
    if a not in known or b not in known:
        raise ValueError("analysis: primary names an unknown preset")
    if presets[a]["routing"] != "record" or presets[a].get("twin") != b:
        raise ValueError("analysis: primary a must route by record and b must be its random twin")
    if an["baseline"] not in known:
        raise ValueError("analysis: baseline names an unknown preset")
    for k in ("calibration_arms", "validity_arms"):
        if not an[k] or any(x not in known for x in an[k]):
            raise ValueError(f"analysis: {k} names an unknown preset")
    for x in an["validity_arms"]:
        if is_routed(presets[x]):
            raise ValueError(f"analysis: validity arm {x} routes something")
    seen = set()
    for s in an["secondary"]:
        if s["id"] in seen or s["id"] in ("T1", "T1b", "T2", "S1", "S5"):
            raise ValueError(f"analysis: secondary id {s['id']} is repeated or reserved")
        seen.add(s["id"])
        if s["a"] not in known or s["b"] not in known or s["rounds"] not in ("all", "window"):
            raise ValueError(f"analysis: secondary {s['id']} is not valid")
        if s["field"] not in ("accepted_false_done", "claimed_false_done", "delivered_good", "passed"):
            raise ValueError(f"analysis: secondary {s['id']} names an unknown measure")
    return True


# ----------------------------------------------------------------------------------------------
# Jobs, records, ranks
# ----------------------------------------------------------------------------------------------
def h(*parts):
    """A number in [0, 1) from the parts: the same on every machine, no random state."""
    d = hashlib.sha256("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return int(d[:12], 16) / 16 ** 12


def round_jobs(rep, rnd, seed=SEED):
    """The 8 jobs of one round of one game, in play order. Same for every arm of the same rep (so arms are paired).
    Stratified: every round gets the same mix of kinds. Every job appears once in the 5 rounds."""
    assert 1 <= rnd <= ROUNDS
    out = []
    for kind, per in J.PER_ROUND.items():
        ids = sorted(J.jobs_of_kind(kind), key=lambda j: h(seed, "bank", rep, kind, j))
        assert len(ids) == per * ROUNDS, (kind, len(ids))
        out.extend(ids[(rnd - 1) * per: rnd * per])
    return sorted(out, key=lambda j: h(seed, "order", rep, rnd, j))


def calibration_table(rows, agents):
    """Score (a), 'knows itself'. rows = [(agent, p, outcome)] from finished rounds of this game.
    Only forecasts by the exact agents in `agents` count: a model that is not in the list has no say, and a new
    model starts empty (its record is reset). Returns {agent: {"n", "brier"}} (brier is None with no forecast)."""
    t = {a: {"n": 0, "sum": 0.0} for a in agents}
    for a, p, o in rows:
        if a in t and p is not None:
            t[a]["n"] += 1
            t[a]["sum"] += (p - o) ** 2
    return {a: {"n": v["n"], "brier": (v["sum"] / v["n"] if v["n"] else None)} for a, v in t.items()}


def random_order(agents, rep, rnd, tag="random", seed=SEED):
    return sorted(agents, key=lambda a: h(seed, tag, rep, rnd, a))


def rank_agents(agents, table, rep, rnd, min_record=MIN_RECORD, seed=SEED):
    """Best first. Reads ONLY the calibration table (score a). Ranked agents by mean Brier (lower is better, ties by a
    seeded draw), then the unranked in a seeded random order."""
    ranked = [a for a in agents if table[a]["n"] >= min_record]
    unranked = [a for a in agents if table[a]["n"] < min_record]
    ranked.sort(key=lambda a: (table[a]["brier"], h(seed, "tie", rep, rnd, a)))
    return ranked + random_order(unranked, rep, rnd, "random", seed)      # the same draw random routing uses, so round 1 is alike


def certifier_for(agent, agents, families):
    """The next agent in the config order whose family differs from the producer's."""
    i = agents.index(agent)
    for k in range(1, len(agents)):
        c = agents[(i + k) % len(agents)]
        if families[c] != families[agent]:
            return c
    raise ValueError(f"no agent of another family than {agent}")


# ----------------------------------------------------------------------------------------------
# The plan of one round
# ----------------------------------------------------------------------------------------------
def make_plan(arm, preset, rep, rnd, agents, families, table, seed=SEED):
    """The plan of one round of one game. `arm` is the preset's id, `preset` its factors, `agents` the config order,
    `table` score (a) from finished rounds."""
    assert len(agents) == N_AGENTS
    jobs = round_jobs(rep, rnd, seed)
    if preset["routing"] == "record":
        order, how = rank_agents(agents, table, rep, rnd, seed=seed), "record"
    elif preset["routing"] == "random":
        order, how = random_order(agents, rep, rnd, "random", seed), "random"
    else:
        k = (rep + rnd - 1) % N_AGENTS
        order, how = list(agents[k:]) + list(agents[:k]), "rotation"
    shares, checks = work_shares(preset), check_counts(preset)
    entries, i = [], 0
    for tier, (agent, w, c) in enumerate(zip(order, shares, checks)):
        mine = jobs[i:i + w]
        i += w
        picked = set(sorted(mine, key=lambda j: h(seed, "check", rep, rnd, j))[:c])
        for j in mine:
            checked = (preset["certify"] == "all") or (j in picked)
            entries.append({"job": j, "agent": agent, "tier": tier, "checked": checked,
                            "certifier": certifier_for(agent, agents, families) if checked else None})
    entries.sort(key=lambda e: jobs.index(e["job"]))
    plan = {"arm": arm, "rep": rep, "round": rnd, "order": order, "ranked_by": how,
            "table": {a: table[a] for a in agents}, "entries": entries}
    check_plan(plan, preset, agents, families)
    return plan


def check_plan(plan, preset, agents, families):
    """Raise AssertionError if a plan breaks a rule. Used when the plan is made, and again by the scorer."""
    es = plan["entries"]
    assert [e["job"] for e in es] == round_jobs(plan["rep"], plan["round"]), "jobs or their order do not match the round"
    assert len({e["job"] for e in es}) == JOBS_PER_ROUND, "a job is missing or repeated"
    assert set(plan["order"]) == set(agents), "order must hold every agent once"
    shares, checks = work_shares(preset), check_counts(preset)
    for tier, a in enumerate(plan["order"]):
        mine = [e for e in es if e["agent"] == a]
        assert len(mine) == shares[tier], f"{a} has {len(mine)} jobs, place {tier + 1} should have {shares[tier]}"
        n_checked = sum(e["checked"] for e in mine)
        assert n_checked == checks[tier], f"{a}: {n_checked} checks, place {tier + 1} should have {checks[tier]}"
        if preset["certify"] in ("table", "fixed"):
            assert n_checked >= MIN_CHECKS, f"{a} would have no check"
    for e in es:
        if e["checked"]:
            assert e["certifier"] and families[e["certifier"]] != families[e["agent"]], "certifier must be of another family"
        else:
            assert e["certifier"] is None
    return True
