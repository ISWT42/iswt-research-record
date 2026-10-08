"""Key-free rules for "real but not deciding" quotes, applied ON TOP of R2 ("shown needs both").

A rule can only turn an R2 "shown" into "not shown". It never creates a "shown", never touches
"contradicted" or "not shown", and never reads an answer key: its inputs are the two models' replies
(cited turn and verified quote) and the log turns (command and output text). The item's truth, deciding
line, trap and why fields are never passed to a rule (selftest.py checks this by deleting them).

Rules defined here (exact definitions: DESIGN.md and PREREG-1.md):
  SAME-LINE       R2's "shown" stands only if the two verified quotes lie on the same line of the same turn.
  OUTCOME-MARKER  R2's "shown" stands only if at least one verified quote carries a generic outcome marker
                  (outcome_markers.py).
Sensitivity variants (exploratory only, never primary): SAME-LINE-STRICT, SAME-LINE-CONTAINED,
OUTCOME-MARKER-BOTH, OUTCOME-MARKER-LINE, SAME-LINE+OUTCOME-MARKER.

Makes no model calls and no network calls. Reports ids, labels and counts only, never item text.
"""
import hashlib
import json
import math
import re
import sys
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import outcome_markers as OM

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LABELS = ("shown", "contradicted", "not shown")


# ---- small helpers --------------------------------------------------------------------------
def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def norm_label(t):
    """Truth / answer labels: 'not_shown' and 'not shown' are the same label."""
    if not isinstance(t, str):
        return t
    t = t.strip().lower().replace("_", " ")
    return t


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def frac(k, n):
    """k out of n with its own n, the rate and the Wilson 95% interval."""
    ci = wilson(k, n)
    return {"k": k, "n": n, "rate": (round(k / n, 4) if n else None),
            "ci95": ([round(ci[0], 4), round(ci[1], 4)] if ci else None)}


def last_per_key(rows):
    """One record per (arm, id): the last one wins (as in run2.py). Returns (dict, number of duplicates)."""
    by, dups = {}, 0
    for r in rows:
        key = (r["arm"], r["id"])
        if key in by:
            dups += 1
        by[key] = r
    return by, dups


def write_new_json(path_stem, obj):
    """Write <stem>-v1.json, or the next free version. Never overwrites an existing file."""
    text = json.dumps(obj, indent=1, ensure_ascii=False)
    k = 1
    while True:
        p = Path(f"{path_stem}-v{k}.json")
        try:
            with open(p, "x", encoding="utf-8") as f:
                f.write(text)
            return p
        except FileExistsError:
            k += 1


def check_seal(folder, seal_name, required):
    """Every file named in the seal file must still have its sealed hash, and every name in `required` must be listed."""
    folder = Path(folder)
    seal = folder / seal_name
    if not seal.exists():
        raise SystemExit(f"STOP: {seal_name} not found. Seal the design before running on the real data.")
    listed = {}
    for line in seal.read_text(encoding="utf-8").splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            listed[parts[1].lstrip("*").strip()] = parts[0].lower()
    ok = {}
    for name, h in listed.items():
        p = folder / name
        ok[name] = p.exists() and sha256_file(p) == h
    missing = [n for n in required if n not in listed]
    if missing or not all(ok.values()):
        raise SystemExit(f"STOP: seal check failed. missing from the seal file: {missing}; changed or absent since the seal: "
                         f"{[n for n, good in ok.items() if not good]}")
    return {"seal_file": seal_name, "seal_file_sha256": sha256_file(seal), "files_match": ok}


# ---- the reader's checks, mirrored (receipts_model.py, sha256 b0842ecd...; as in rescore_common.py) ----
ANSWER = {"shown": "shown", "contradicted": "contradicted", "not_shown": "not shown"}


def parse_reply(text):
    """Mirror of receipts_model.parse_reply."""
    if not isinstance(text, str) or not text.strip():
        return None, "unparseable_reply"
    candidate = text.strip()
    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", candidate, re.S)
    if fence:
        candidate = fence.group(1)
    try:
        value = json.loads(candidate)
    except ValueError:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start < 0 or end <= start:
            return None, "unparseable_reply"
        try:
            value = json.loads(candidate[start:end + 1])
        except ValueError:
            return None, "unparseable_reply"
    if not isinstance(value, dict):
        return None, "invalid_reply"
    return value, ""


def normalize_verdict(value):
    """Mirror of receipts_model.normalize_verdict."""
    if not isinstance(value, str):
        return None
    verdict = re.sub(r"[\s-]+", "_", value.strip().lower())
    return verdict if verdict in ANSWER else None


class Turn:
    """Stand-in for receipts_model.ShownTurn: what the verbatim gate and the rules use."""
    __slots__ = ("label", "row_id", "cmd", "out")

    def __init__(self, label, row_id, cmd, out):
        self.label, self.row_id, self.cmd, self.out = label, row_id, cmd, out


def turns_for(item):
    """Mirror of run_pair.turns_for: labels T1, T2, ...; the output is the whole output text."""
    res = []
    for i, t in enumerate(item["turns"], 1):
        res.append(Turn(f"T{i}", f"{item['id']}:{i}", str(t.get("cmd") or ""), str(t.get("output") or "")))
    return res


def normalize_turn_id(value, turns):
    """Mirror of receipts_model.normalize_turn_id."""
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip().strip("[]()").strip()
    if re.fullmatch(r"\d{1,3}", text):
        text = "T" + text
    elif re.fullmatch(r"[tT]\d{1,3}", text):
        text = text.upper()
    for turn in turns:
        if text in (turn.label, turn.row_id):
            return turn
    return None


# ---- evidence: the cited turn and the verified quote, with where they sit ----------------------
def line_starts(text):
    """Character offset at which each line of text.splitlines() starts (line terminators belong to their line)."""
    starts, pos = [], 0
    for ln in text.splitlines(keepends=True):
        starts.append(pos)
        pos += len(ln)
    return starts


def line_ranges(quote, text):
    """Every (first_line, last_line) pair, 0-based, of the occurrences of quote in text (overlapping occurrences included).
    A one-line quote gives (i, i); a quote that spans lines gives (i, j) with j > i. Empty if the quote is not in text."""
    if not quote:
        return []
    starts = line_starts(text)
    found, pos = [], text.find(quote)
    while pos != -1:
        last_char = pos + len(quote) - 1
        found.append((bisect_right(starts, pos) - 1, bisect_right(starts, last_char) - 1))
        pos = text.find(quote, pos + 1)
    return found


@dataclass(frozen=True)
class Evidence:
    turn_index: int      # 0-based position of the cited turn in the log
    turn_label: str      # T1, T2, ...
    verdict: str         # the model's verdict (shown / contradicted)
    quote: str           # stripped quote, verbatim in the cited turn's output
    ranges: tuple        # ((first_line, last_line), ...) for every occurrence of the quote in that output
    lines: tuple         # the output's lines (str.splitlines())

    def line_text(self):
        """Text of the whole output lines the quote lies on (every occurrence, joined by newlines)."""
        return "\n".join("\n".join(self.lines[i:j + 1]) for i, j in self.ranges)


def derive_evidence(reply_text, turns):
    """Re-derive the verified evidence of one reply from its text: the cited turn and the stripped quote, if the quote
    is found verbatim in that turn's output (the verbatim gate of receipts_model.verify). None if it cannot be derived."""
    value, _ = parse_reply(reply_text)
    if value is None:
        return None
    verdict = normalize_verdict(value.get("verdict"))
    if verdict not in ("shown", "contradicted"):
        return None
    turn = normalize_turn_id(value.get("turn_id"), turns)
    if turn is None:
        return None
    quote = value.get("quote")
    if not isinstance(quote, str):
        return None
    quote = quote.strip()
    if not quote or quote not in turn.out:
        return None
    ranges = tuple(line_ranges(quote, turn.out))
    return Evidence(turn_index=turns.index(turn), turn_label=turn.label, verdict=verdict, quote=quote,
                    ranges=ranges, lines=tuple(turn.out.splitlines()))


@dataclass(frozen=True)
class Ctx:
    """What a rule may see: the two verified pieces of evidence (None if not derivable) and the log's turns."""
    ev_a: object
    ev_b: object
    turns: tuple


# ---- the rules: each returns (keep, reason). keep=False turns R2's "shown" into "not shown" ----------
def _overlap(r1, r2):
    return r1[0] <= r2[1] and r2[0] <= r1[1]


def rule_same_line(ctx):
    """SAME-LINE: keep only if both verified quotes are on the same line of the same turn.
    'Same line' = the same cited turn, and some occurrence of one quote and some occurrence of the other have
    overlapping line ranges (a multi-line quote counts for every line it covers, so a one-line quote inside a
    multi-line quote, or two quotes that cover a common line, agree). Fail closed if either evidence is missing."""
    a, b = ctx.ev_a, ctx.ev_b
    if a is None or b is None:
        return False, "unresolved"
    if a.turn_index != b.turn_index:
        return False, "different_turn"
    if any(_overlap(ra, rb) for ra in a.ranges for rb in b.ranges):
        return True, "same_line"
    return False, "different_lines"


def rule_outcome_marker(ctx):
    """OUTCOME-MARKER: keep only if at least one of the two verified quotes carries a generic outcome marker
    (outcome_markers.has_marker on the quote text). Fail closed if either evidence is missing."""
    a, b = ctx.ev_a, ctx.ev_b
    if a is None or b is None:
        return False, "unresolved"
    if OM.has_marker(a.quote) or OM.has_marker(b.quote):
        return True, "marker_in_a_quote"
    return False, "no_marker_in_either_quote"


# sensitivity variants (exploratory only; written before the development quotes were read)
def rule_same_line_strict(ctx):
    """SAME-LINE-STRICT: the same turn and an occurrence of each quote with identical line ranges."""
    a, b = ctx.ev_a, ctx.ev_b
    if a is None or b is None:
        return False, "unresolved"
    if a.turn_index != b.turn_index:
        return False, "different_turn"
    if set(a.ranges) & set(b.ranges):
        return True, "identical_range"
    return False, "different_ranges"


def rule_same_line_contained(ctx):
    """SAME-LINE-CONTAINED: SAME-LINE and one quote equals or is contained in the other as text."""
    a, b = ctx.ev_a, ctx.ev_b
    keep, reason = rule_same_line(ctx)
    if not keep:
        return False, reason
    if a.quote in b.quote or b.quote in a.quote:
        return True, "same_line_and_contained"
    return False, "same_line_not_contained"


def rule_outcome_marker_both(ctx):
    """OUTCOME-MARKER-BOTH: keep only if both verified quotes carry a marker."""
    a, b = ctx.ev_a, ctx.ev_b
    if a is None or b is None:
        return False, "unresolved"
    if OM.has_marker(a.quote) and OM.has_marker(b.quote):
        return True, "marker_in_both"
    return False, "marker_missing_in_one"


def rule_outcome_marker_line(ctx):
    """OUTCOME-MARKER-LINE: keep only if the whole output line(s) of at least one quote carry a marker."""
    a, b = ctx.ev_a, ctx.ev_b
    if a is None or b is None:
        return False, "unresolved"
    if OM.has_marker(a.line_text()) or OM.has_marker(b.line_text()):
        return True, "marker_on_a_quote_line"
    return False, "no_marker_on_either_line"


def rule_both_rules(ctx):
    """SAME-LINE+OUTCOME-MARKER: keep only if SAME-LINE and OUTCOME-MARKER both keep."""
    k1, r1 = rule_same_line(ctx)
    k2, r2 = rule_outcome_marker(ctx)
    return (k1 and k2), f"{r1}|{r2}"


NAMED_RULES = (("SAME-LINE", rule_same_line), ("OUTCOME-MARKER", rule_outcome_marker))
VARIANT_RULES = (("SAME-LINE-STRICT", rule_same_line_strict), ("SAME-LINE-CONTAINED", rule_same_line_contained),
                 ("OUTCOME-MARKER-BOTH", rule_outcome_marker_both), ("OUTCOME-MARKER-LINE", rule_outcome_marker_line),
                 ("SAME-LINE+OUTCOME-MARKER", rule_both_rules))


# ---- pair rules and measures (run2.py, unchanged) ------------------------------------------------
def rule2(a, b):
    """'Shown needs both' (run2.rule2): agree -> that answer; differ and either says shown -> not shown;
    otherwise (one contradicted, one not shown) -> contradicted."""
    if a == b:
        return a
    if "shown" in (a, b):
        return "not shown"
    return "contradicted" if "contradicted" in (a, b) else "not shown"


def measures(final, truth, ids):
    """Counts with their own denominators (as run2.measures)."""
    ids = list(ids)
    return {
        "right": frac(sum(final[i] == truth[i] for i in ids), len(ids)),
        "false_shown": frac(sum(final[i] == "shown" and truth[i] != "shown" for i in ids), sum(truth[i] != "shown" for i in ids)),
        "true_shown_kept": frac(sum(final[i] == "shown" and truth[i] == "shown" for i in ids), sum(truth[i] == "shown" for i in ids)),
        "false_contradicted": frac(sum(final[i] == "contradicted" and truth[i] != "contradicted" for i in ids),
                                   sum(truth[i] != "contradicted" for i in ids)),
        "answers": dict(sorted(Counter(final[i] for i in ids).items())),
    }


# ---- the success bar (written before the development data was looked at; DESIGN.md) ------------------
BAR_MIN_FALSE_SHOWN = 4          # fewer R2 false "shown" than this: the bar cannot be tested (THIN)
BAR_REMOVE_AT_LEAST = (1, 2)     # remove at least 1/2 of R2's false "shown"
BAR_KEEP_AT_LEAST = (4, 5)       # keep at least 4/5 of R2's true "shown"


def bar_verdict(F, f_removed, T, t_removed):
    """F, T: R2's false and true 'shown'; f_removed, t_removed: how many of each the rule removes.
    Integer arithmetic only. Verdict: MET, NOT MET, or THIN (F below BAR_MIN_FALSE_SHOWN: not testable)."""
    half_ok = f_removed * BAR_REMOVE_AT_LEAST[1] >= F * BAR_REMOVE_AT_LEAST[0] and F > 0
    keep_ok = (T - t_removed) * BAR_KEEP_AT_LEAST[1] >= T * BAR_KEEP_AT_LEAST[0]
    if F < BAR_MIN_FALSE_SHOWN:
        verdict = "THIN"
    else:
        verdict = "MET" if (half_ok and keep_ok) else "NOT MET"
    return {"verdict": verdict, "r2_false_shown": F, "false_removed": f_removed, "removal_half_met": bool(half_ok),
            "r2_true_shown": T, "true_removed": t_removed, "retention_met": bool(keep_ok),
            "false_removed_needed": (F * BAR_REMOVE_AT_LEAST[0] + BAR_REMOVE_AT_LEAST[1] - 1) // BAR_REMOVE_AT_LEAST[1],
            "true_removed_allowed": T - (T * BAR_KEEP_AT_LEAST[0] + BAR_KEEP_AT_LEAST[1] - 1) // BAR_KEEP_AT_LEAST[1]}


# ---- the analysis -----------------------------------------------------------------------------------
def load_item(obj):
    """Accept an item line as in the bank (id, claim, turns, truth, ...); unwrap {'item': {...}} if present."""
    if "turns" not in obj and isinstance(obj.get("item"), dict):
        obj = obj["item"]
    for key in ("id", "turns", "truth"):
        if key not in obj:
            raise SystemExit(f"STOP: an item line has no '{key}' field (fields seen: {sorted(obj)[:12]})")
    return obj


def analyse(items, records, arms, extra_rules=(), id_filter=None, groups=None, include_variants=True):
    """items: id -> item; records: (arm, id) -> answer record; arms: (first, second).
    Rules in `extra_rules` are reported with group 'own'. Returns counts and ids only, never text."""
    a_arm, b_arm = arms
    universe = [i for i in sorted(items) if ((a_arm, i) in records or (b_arm, i) in records)]
    if id_filter is not None:
        universe = [i for i in universe if id_filter(i)]
    truth = {i: norm_label(items[i]["truth"]) for i in universe}
    trap = {i: items[i].get("trap", "-") for i in universe}
    bad_truth = [i for i in universe if truth[i] not in LABELS]
    if bad_truth:
        raise SystemExit(f"STOP: truth label not shown/contradicted/not shown for ids {bad_truth[:5]}")
    ans = {a_arm: {}, b_arm: {}}
    anomalies = Counter()
    for arm in arms:
        for i in universe:
            rec = records.get((arm, i))
            if rec is None:
                ans[arm][i] = "not shown"
                anomalies[f"{arm}_no_record"] += 1
                continue
            a = norm_label(rec.get("answer"))
            if a not in LABELS:
                anomalies[f"{arm}_unknown_answer_value"] += 1
                a = "not shown"
            ans[arm][i] = a
    r2 = {i: rule2(ans[a_arm][i], ans[b_arm][i]) for i in universe}
    r2_shown = [i for i in universe if r2[i] == "shown"]
    F = sum(1 for i in r2_shown if truth[i] != "shown")
    T = sum(1 for i in r2_shown if truth[i] == "shown")

    # evidence for every R2 "shown" item
    ctxs, evidence_flags = {}, Counter()
    for i in r2_shown:
        turns = turns_for(items[i])
        ev = []
        for arm in arms:
            rec = records[(arm, i)]
            e = derive_evidence(rec.get("reply"), turns)
            if e is None:
                evidence_flags[f"{arm}_evidence_not_derivable"] += 1
            else:
                if e.verdict != "shown":
                    evidence_flags[f"{arm}_derived_verdict_not_shown"] += 1
                if e.quote != (rec.get("quote") or "").strip():
                    evidence_flags[f"{arm}_derived_quote_differs_from_recorded"] += 1
            ev.append(e)
        ctxs[i] = Ctx(ev[0], ev[1], tuple(turns))

    def apply(rule):
        keep, reasons = {}, {}
        for i in r2_shown:
            k, why = rule(ctxs[i])
            keep[i], reasons[i] = bool(k), why
        return keep, reasons

    out = {"arms": list(arms), "n_items": len(universe), "truth_counts": dict(sorted(Counter(truth.values()).items())),
           "trap_counts": dict(sorted(Counter(trap.values()).items())), "anomalies": dict(anomalies),
           "evidence_flags_on_r2_shown": dict(evidence_flags), "r2_shown_items": len(r2_shown),
           "R2": measures(r2, truth, universe), "rules": {}}
    out["R2"]["shown_by_truth"] = dict(sorted(Counter(truth[i] for i in r2_shown).items()))
    out["R2"]["false_shown_ids"] = [(i, truth[i], trap[i]) for i in r2_shown if truth[i] != "shown"]
    rule_list = [(n, f, "named") for n, f in NAMED_RULES] + [(n, f, "own") for n, f in extra_rules]
    if include_variants:
        rule_list += [(n, f, "variant") for n, f in VARIANT_RULES]
    for name, fn, kind in rule_list:
        keep, reasons = apply(fn)
        final = dict(r2)
        for i in r2_shown:
            if not keep[i]:
                final[i] = "not shown"
        removed = [i for i in r2_shown if not keep[i]]
        rf = [i for i in removed if truth[i] != "shown"]
        rt = [i for i in removed if truth[i] == "shown"]
        entry = {"kind": kind, "measures": measures(final, truth, universe),
                 "removed": {"total": len(removed), "false": len(rf), "true": len(rt),
                             "false_by_truth": dict(sorted(Counter(truth[i] for i in rf).items())),
                             "by_truth_and_trap": dict(sorted(Counter(f"{truth[i]}|{trap[i]}" for i in removed).items())),
                             "items": [(i, truth[i], trap[i], reasons[i]) for i in removed]},
                 "of_r2": {"false_removed": frac(len(rf), F), "true_removed": frac(len(rt), T),
                           "separation": (round(len(rf) / F - len(rt) / T, 4) if F and T else None)},
                 "reasons": dict(sorted(Counter(reasons.values()).items())),
                 "bar": bar_verdict(F, len(rf), T, len(rt))}
        if groups is not None:
            entry["removed"]["by_group"] = dict(sorted(Counter(groups.get(i, "-") for i in removed).items()))
        out["rules"][name] = entry
    if groups is not None:
        out["R2"]["false_shown_by_group"] = dict(sorted(Counter(groups.get(i, "-") for i in r2_shown if truth[i] != "shown").items()))
        out["R2"]["shown_by_group"] = dict(sorted(Counter(groups.get(i, "-") for i in r2_shown).items()))
    return out
