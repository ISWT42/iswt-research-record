"""S14, the word test: the scorer. Written and sealed while the run was still going, before the results seal and before any
count was made (the only results seen were progress lines on the run's console). The design asked only that it be sealed
before it runs; sealing it earlier removes any chance that the results shaped it.

What it counts is fixed by DESIGN.md (sealed with the runner, before any model call):
  1. changed pairs: of the 108 record-and-framing pairs per model, how many get a different verdict under "cannot" than under
     "can't" (no verdict counts as a value of its own);
  2. forced texts: breaks (anything other than "shown" or "contradicted") under each word; guesses on the 27 missing logs;
     right answers on the 27 intact logs; paired exact McNemar, cannot against can't;
  3. allowed texts: guesses on the 27 missing logs; right answers on the 27 intact logs; McNemar as above;
  4. repeats: how many of the 44 repeat calls give the same verdict as the main block on the same text;
  5. forced against allowed, across both words: guesses on the missing logs.
Then the design's reading rules and the six forecasts W1 to W6, each scored held or did not hold, with its Brier score.

Verdicts: the primary count uses the verdict the runner stored (run_s14.parse_verdict, sealed with the runner). This scorer
re-reads every reply with that same function and stops if any stored verdict differs. Two secondary reads follow, as the
parser audit of 7 Oct asked (its reference rule, sealed 10:19:17 GMT): the reference rule exactly, and its full-key variant
(an object counts only if it has reason, turn_id, quote and verdict). Any disagreement is reported with its direction, and the
headline counts are shown again under each read that disagrees. They are exploratory; they do not replace the primary count.

    python score_s14.py                          the real results (results/calls.jsonl) into results/
    python score_s14.py --calls X --out DIR      any calls file (the synthetic test uses this)
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # nothing is written into the sealed folders this scorer reads from

import argparse
import hashlib
import json
import math
import random
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = Path("C:/Users/joshd/Private/claims/parser-audit-2026-10-07")
sys.path.insert(0, str(AUDIT))
from ref_rule import load_functions, reference_parse  # noqa: E402

KEYS = Path("C:/Users/joshd/Private/gemini-pack-keys-2026-10-06/s12-keys.jsonl")
KEYS_SHA256 = "c6d04350c3b8e50fd02cc2504ebbac39a00af9bbe689e21d4e71d30050e47ebb"   # KEYS-S12-SHA256.txt, sealed 6 Oct
RUN_SHA256 = "a8778e0cef6778a8b6e9aabadb1aff39b80343c29e4694ae5ebcf1e6af1a3777"    # run_s14.py in RUN-SHA256.txt
REQUESTS = HERE / "inputs" / "s12-requests.jsonl"
REQUESTS_SHA256 = "928a3b713559f01945067cb05fa7892f81fec1b83332f8a4df8049944b5e9609"
MODELS = ("qwen", "gemma")
MODEL_IDS = {"qwen": "Qwen3-4B-Instruct-2507-GGUF", "gemma": "Gemma-4-E4B-it-GGUF"}
VARIANTS = ("forced_cannot", "forced_cant", "allowed_cannot", "allowed_cant")
VERDICTS = ("shown", "contradicted", "not_shown")
ANSWERS = ("shown", "contradicted")
FRAMINGS = HERE / "inputs" / "s12-framings.json"
FRAMINGS_SHA256 = "4a6be62b38dafe1bea99cae71091dfb7d1c5f33a385cc6959b1e694ba427b2a0"
# The four texts' fingerprints as DESIGN.md prints them (first 8 and last 4 hex digits). The scorer does not trust these: it
# rebuilds each text with the sealed runner's own build_texts from the sealed framings, and checks every call row against the
# full value. Where a printed part differs from the rebuilt value, the report says so.
DESIGN_PARTS = {"forced_cannot": ("df6de01a", "becb"), "forced_cant": ("8668f49f", "3dca"),
                "allowed_cannot": ("498ae837", "7341"), "allowed_cant": ("661cb45c", "6ad7")}
REPEAT_SHARE = 11
FULL_KEYS = ("reason", "turn_id", "quote")

FORECASTS = [
    ("W1", 0.85, 'For at least one model, at least one of its 108 pairs gets a different verdict under "cannot" than under "can\'t".'),
    ("W2", 0.65, "For both models, the verdicts differ on at most 10 of 108 pairs."),
    ("W3", 0.75, "Neither model shows a direction with exact McNemar p < 0.05 (forced breaks, or allowed guesses on missing logs)."),
    ("W4", 0.75, "Each model's repeats agree with its main block on all 44 calls."),
    ("W5", 0.40, 'Summed over both models, forced breaks are fewer under "cannot" than under "can\'t".'),
    ("W6", 0.70, "For both models, across both words, the forced texts give more guesses on the 27 missing logs than the allowed texts."),
]
POINT = {"qwen": (4, 0, 12), "gemma": (3, 0, 10)}   # point forecast and 80% range for changed pairs, of 108


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mcnemar_exact(b: int, c: int) -> float:
    """Two-sided exact McNemar (binomial on the discordant pairs, p = 0.5)."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def label(v) -> str:
    return v if v is not None else "none"


def load_key() -> dict:
    if sha256_file(KEYS) != KEYS_SHA256:
        raise SystemExit("the S12 key does not match its sealed fingerprint")
    rows = [json.loads(line) for line in KEYS.read_text(encoding="utf-8").splitlines() if line.strip()]
    key = {r["id"]: r for r in rows}
    kinds = Counter(r["kind"] for r in rows)
    assert len(key) == 54 and kinds == Counter({"twin_missing": 27, "present": 27}), kinds
    assert all((r["kind"] == "twin_missing") == (r["truth"] == "not_shown") for r in rows)
    return key


def text_fingerprints() -> dict:
    """The four instruction texts, rebuilt with the sealed runner's build_texts from the sealed framings: variant -> SHA-256."""
    if sha256_file(FRAMINGS) != FRAMINGS_SHA256:
        raise SystemExit("the S12 framings do not match their sealed fingerprint")
    build = load_functions(HERE / "run_s14.py", ["build_texts"],
                           constants=["FORCED_OLD", "FORCED_NEW", "ALLOWED_OLD", "ALLOWED_NEW", "WORDS"])["build_texts"]
    texts = build(json.loads(FRAMINGS.read_text(encoding="utf-8")))
    return {v: hashlib.sha256(texts[v].encode("utf-8")).hexdigest() for v in VARIANTS}


def design_part_notes(fp: dict) -> list:
    notes = []
    for v, (head, tail) in DESIGN_PARTS.items():
        if not fp[v].startswith(head) or not fp[v].endswith(tail):
            notes.append(f"DESIGN.md prints {v}'s fingerprint as {head}...{tail}; the text the sealed runner builds from the "
                         f"sealed framings has {fp[v][:8]}...{fp[v][-4:]} (full value {fp[v]}). Every {v} call row carries the "
                         f"full value, so the printed part is a typo in the design, not a different text.")
    return notes


def requests() -> list:
    if sha256_file(REQUESTS) != REQUESTS_SHA256:
        raise SystemExit("the S12 requests do not match their sealed fingerprint")
    return [json.loads(line) for line in REQUESTS.read_text(encoding="utf-8").splitlines() if line.strip()]


def expected_repeat_ids() -> list:
    return sorted(random.Random(14).sample([r["id"] for r in requests()], REPEAT_SHARE))   # the runner's draw, repeated


def load_calls(path: Path, key: dict, parse_verdict, fp: dict) -> list:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen = set()
    repeat_ids = expected_repeat_ids()
    user_sha = {r["id"]: hashlib.sha256(r["user"].encode("utf-8")).hexdigest() for r in requests()}
    for r in rows:
        k = (r["model_key"], r["id"], r["variant"], r["repeat"])
        assert k not in seen, f"duplicate call {k}"
        seen.add(k)
        assert r["model_key"] in MODELS and r["variant"] in VARIANTS and r["id"] in key, k
        assert r["model"] == MODEL_IDS[r["model_key"]], k
        assert r["system_sha256"] == fp[r["variant"]], f"text fingerprint {k}"
        assert r["user_sha256"] == user_sha[r["id"]], f"record fingerprint {k}"
        again, _ = parse_verdict(r.get("reply"))
        assert again == r.get("verdict"), f"stored verdict differs from a fresh read with the runner's parser: {k}"
    for m in MODELS:
        main = {(r["id"], r["variant"]) for r in rows if r["model_key"] == m and r["repeat"] == 0}
        rep = {(r["id"], r["variant"]) for r in rows if r["model_key"] == m and r["repeat"] == 1}
        assert main == {(i, v) for i in key for v in VARIANTS}, f"{m}: main block incomplete ({len(main)} of 216)"
        assert rep == {(i, v) for i in repeat_ids for v in VARIANTS}, f"{m}: repeat block wrong ({len(rep)} of 44)"
    assert len(rows) == 520, len(rows)
    return rows


def measures(rows: list, key: dict, read) -> dict:
    """Every count the design names, per model, with the verdict for each row given by read(row)."""
    out = {}
    missing = sorted(i for i in key if key[i]["kind"] == "twin_missing")
    intact = sorted(i for i in key if key[i]["kind"] == "present")
    for m in MODELS:
        main = {(r["id"], r["variant"]): read(r) for r in rows if r["model_key"] == m and r["repeat"] == 0}
        rep = {(r["id"], r["variant"]): read(r) for r in rows if r["model_key"] == m and r["repeat"] == 1}
        d = {"verdicts": {v: dict(Counter(label(main[(i, v)]) for i in key)) for v in VARIANTS}}
        changed = []
        for i in sorted(key):
            for fr in ("forced", "allowed"):
                a, b = main[(i, f"{fr}_cannot")], main[(i, f"{fr}_cant")]
                if a != b:
                    changed.append({"id": i, "framing": fr, "kind": key[i]["kind"], "truth": key[i]["truth"],
                                    "cannot": label(a), "cant": label(b)})
        d["changed_pairs"] = len(changed)
        d["changed_detail"] = changed
        d["changed_by_framing"] = dict(Counter(c["framing"] for c in changed))

        def tally(variant, ids, test):
            return [1 if test(main[(i, variant)], i) else 0 for i in ids]

        def pair(name, fr, ids, test):
            x = tally(f"{fr}_cannot", ids, test)
            y = tally(f"{fr}_cant", ids, test)
            b = sum(1 for p, q in zip(x, y) if p and not q)
            c = sum(1 for p, q in zip(x, y) if q and not p)
            d[name] = {"cannot": sum(x), "cant": sum(y), "of": len(ids), "cannot_only": b, "cant_only": c,
                       "mcnemar_p": mcnemar_exact(b, c)}

        everyone = sorted(key)
        pair("forced_breaks", "forced", everyone, lambda v, i: v not in ANSWERS)
        pair("forced_guesses_missing", "forced", missing, lambda v, i: v in ANSWERS)
        pair("forced_right_intact", "forced", intact, lambda v, i: v == key[i]["truth"])
        pair("allowed_guesses_missing", "allowed", missing, lambda v, i: v in ANSWERS)
        pair("allowed_right_intact", "allowed", intact, lambda v, i: v == key[i]["truth"])
        pair("allowed_right_missing", "allowed", missing, lambda v, i: v == "not_shown")
        agree = sum(1 for k, v in rep.items() if main[k] == v)
        d["repeats"] = {"agree": agree, "of": len(rep),
                        "disagree_detail": [{"id": k[0], "variant": k[1], "main": label(main[k]), "repeat": label(v)}
                                            for k, v in sorted(rep.items()) if main[k] != v]}
        fg = d["forced_guesses_missing"]["cannot"] + d["forced_guesses_missing"]["cant"]
        ag = d["allowed_guesses_missing"]["cannot"] + d["allowed_guesses_missing"]["cant"]
        d["forced_vs_allowed_guesses_missing"] = {"forced": fg, "allowed": ag, "of": 2 * len(missing)}
        # the design's reading rule for "the word alone changes this model's verdict"
        n_changed, dis = len(changed), len(rep) - agree
        changed_share, repeat_share = n_changed / 108, dis / len(rep)
        if n_changed == 0:
            reading = "not shown (no pair changed)"
        elif dis == 0:
            reading = "shown (at least one pair changed, and all 44 repeats agree)"
        elif changed_share >= 3 * repeat_share:
            reading = f"shown (changed share {n_changed} of 108 is at least three times the repeat share, {dis} of 44)"
        else:
            reading = f"not shown (changed share {n_changed} of 108 is under three times the repeat share, {dis} of 44)"
        d["word_alone"] = reading
        d["directions"] = {name: d[name]["mcnemar_p"] < 0.05 for name in
                           ("forced_breaks", "forced_guesses_missing", "forced_right_intact",
                            "allowed_guesses_missing", "allowed_right_intact")}
        out[m] = d
    return out


def forecasts(s: dict) -> list:
    q, g = s["qwen"], s["gemma"]
    held = {
        "W1": q["changed_pairs"] >= 1 or g["changed_pairs"] >= 1,
        "W2": q["changed_pairs"] <= 10 and g["changed_pairs"] <= 10,
        "W3": all(x["forced_breaks"]["mcnemar_p"] >= 0.05 and x["allowed_guesses_missing"]["mcnemar_p"] >= 0.05 for x in (q, g)),
        "W4": all(x["repeats"]["agree"] == x["repeats"]["of"] == 44 for x in (q, g)),
        "W5": q["forced_breaks"]["cannot"] + g["forced_breaks"]["cannot"] < q["forced_breaks"]["cant"] + g["forced_breaks"]["cant"],
        "W6": all(x["forced_vs_allowed_guesses_missing"]["forced"] > x["forced_vs_allowed_guesses_missing"]["allowed"] for x in (q, g)),
    }
    return [{"id": w, "p": p, "statement": text, "held": held[w], "brier": round((p - (1.0 if held[w] else 0.0)) ** 2, 4)}
            for w, p, text in FORECASTS]


def secondary(rows: list) -> dict:
    """The parser audit's reference rule, exactly and with the full-key variant, against the stored verdict."""
    out = {}
    for name, required in (("reference", ()), ("full_key", FULL_KEYS)):
        reads, dirs, examples = {}, Counter(), []
        for r in rows:
            v, _ = reference_parse(r.get("reply"), "verdict", VERDICTS, required=required)
            k = (r["model_key"], r["id"], r["variant"], r["repeat"])
            reads[k] = v
            own = r.get("verdict")
            if v == own:
                continue
            direction = "stored none, this read found" if own is None else ("stored found, this read none" if v is None else "different")
            dirs[direction] += 1
            if len(examples) < 12:
                examples.append({"call": [k[0], k[1], k[2], "repeat block" if k[3] else "main block"], "stored": label(own), "this_read": label(v),
                                 "reply_start": (r.get("reply") or "")[:160].replace("\n", " ")})
        out[name] = {"disagreements": sum(dirs.values()), "by_direction": dict(dirs), "examples": examples, "reads": reads}
    return out


TITLES = {"forced_breaks": "Forced: breaks (anything but shown or contradicted)",
          "forced_guesses_missing": "Forced: guesses on missing logs",
          "forced_right_intact": "Forced: right on intact logs",
          "allowed_guesses_missing": "Allowed: guesses on missing logs",
          "allowed_right_intact": "Allowed: right on intact logs",
          "allowed_right_missing": "Allowed: not_shown on missing logs"}


def pct(x, n):
    return f"{x} of {n}"


def write_report(path: Path, s: dict, fc: list, sec: dict, sec_measures: dict, meta: dict) -> None:
    L = []
    L.append("# S14, the word test: scored")
    L.append("")
    L.append(f"Scored by `score_s14.py` (sealed before it ran). Calls file SHA-256 `{meta['calls_sha256']}`; {meta['rows']} calls; "
             f"{meta['errors']} with a client error; {meta['no_verdict']} without a verdict. Each count sits beside its own denominator.")
    L.append("")
    L.append("## The headline")
    for m in MODELS:
        d = s[m]
        L.append(f"- **{m.capitalize()}:** {d['changed_pairs']} of 108 pairs changed verdict when only the word changed "
                 f"(forced {d['changed_by_framing'].get('forced', 0)} of 54, allowed {d['changed_by_framing'].get('allowed', 0)} of 54); "
                 f"repeats agreed on {pct(d['repeats']['agree'], d['repeats']['of'])}. \"The word alone changes this model's verdict\": {d['word_alone']}.")
    L.append("")
    L.append("## Per model")
    for m in MODELS:
        d = s[m]
        L.append(f"### {m.capitalize()} (`{MODEL_IDS[m]}`)")
        L.append("")
        L.append("| Count | cannot | can't | of | cannot only | can't only | exact McNemar p |")
        L.append("|---|---|---|---|---|---|---|")
        for name, title in TITLES.items():
            x = d[name]
            L.append(f"| {title} | {x['cannot']} | {x['cant']} | {x['of']} | {x['cannot_only']} | {x['cant_only']} | {x['mcnemar_p']:.4g} |")
        fva = d["forced_vs_allowed_guesses_missing"]
        L.append("")
        L.append(f"Forced against allowed, both words together: guesses on missing logs {fva['forced']} of {fva['of']} (forced) "
                 f"against {fva['allowed']} of {fva['of']} (allowed).")
        L.append("")
        L.append("Verdicts per text (main block): " + "; ".join(
            f"{v}: " + ", ".join(f"{k} {n}" for k, n in sorted(d['verdicts'][v].items())) for v in VARIANTS) + ".")
        L.append("")
        if d["changed_detail"]:
            L.append("Changed pairs:")
            L.append("")
            L.append("| Record | Framing | Log | Key | cannot | can't |")
            L.append("|---|---|---|---|---|---|")
            for c in d["changed_detail"]:
                L.append(f"| {c['id']} | {c['framing']} | {c['kind']} | {c['truth']} | {c['cannot']} | {c['cant']} |")
            L.append("")
        if d["repeats"]["disagree_detail"]:
            L.append("Repeats that disagreed with the main block: " + "; ".join(
                f"{x['id']} {x['variant']} (main {x['main']}, repeat {x['repeat']})" for x in d["repeats"]["disagree_detail"]) + ".")
            L.append("")
        dirs = [TITLES[k] for k, v in d["directions"].items() if v]
        L.append("Directions shown (exact McNemar p < 0.05): " + (", ".join(dirs) if dirs else "none") + ".")
        L.append("")
    L.append("## Forecasts (sealed with the design; one outcome says nothing about a probability)")
    L.append("")
    L.append("| # | p | Statement | Outcome | Brier |")
    L.append("|---|---|---|---|---|")
    for f in fc:
        L.append(f"| {f['id']} | {f['p']} | {f['statement']} | {'held' if f['held'] else 'did not hold'} | {f['brier']} |")
    mean_brier = sum(f["brier"] for f in fc) / len(fc)
    L.append("")
    L.append(f"Mean Brier over the six: {mean_brier:.4f}. Point forecasts for changed pairs: " + "; ".join(
        f"{m.capitalize()} {POINT[m][0]} (80% range {POINT[m][1]} to {POINT[m][2]}), result {s[m]['changed_pairs']}, "
        f"{'inside' if POINT[m][1] <= s[m]['changed_pairs'] <= POINT[m][2] else 'outside'} the range" for m in MODELS) + ".")
    L.append("")
    L.append("## The two secondary reads (the parser audit's rule; exploratory)")
    L.append("")
    for name, title in (("reference", "The reference rule exactly"), ("full_key", "The full-key variant (reason, turn_id, quote, verdict)")):
        x = sec[name]
        L.append(f"- **{title}:** {x['disagreements']} of {meta['rows']} replies read differently from the stored verdict"
                 + (f" ({', '.join(f'{k}: {v}' for k, v in sorted(x['by_direction'].items()))})." if x['disagreements'] else "."))
        if x["disagreements"]:
            for e in x["examples"]:
                L.append(f"  - {' '.join(str(c) for c in e['call'])}: stored {e['stored']}, this read {e['this_read']}; reply starts `{e['reply_start']}`")
            sm = sec_measures[name]
            L.append("  - Under this read: " + "; ".join(
                f"{m.capitalize()} changed pairs {sm[m]['changed_pairs']} of 108, forced breaks {sm[m]['forced_breaks']['cannot']} and "
                f"{sm[m]['forced_breaks']['cant']} of 54, allowed guesses on missing {sm[m]['allowed_guesses_missing']['cannot']} and "
                f"{sm[m]['allowed_guesses_missing']['cant']} of 27, repeats agree {sm[m]['repeats']['agree']} of 44" for m in MODELS) + ".")
    L.append("")
    L.append("## Checks and notes")
    L.append("- Every row's text fingerprint equals the text the sealed runner builds from the sealed framings; every row's record "
             "fingerprint equals its sealed S12 record; every stored verdict equals a fresh read with the runner's own parser; "
             "the S12 key matches its 6 Oct seal; the main and repeat blocks are complete (216 and 44 calls per model).")
    for n in meta["notes"]:
        L.append(f"- {n}")
    L.append("")
    L.append("## What this does not settle")
    L.append("- Two small local models, not Claude; one sentence in one place per text; one apostrophe; one item bank written by models, "
             "whose labels no person has checked yet.")
    L.append("- A changed pair shows that this model's verdict moved when one word moved, at temperature 0 with a fixed seed. "
             "It does not show why, or that the same happens in other sentences or other models.")
    path.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--calls", default=str(HERE / "results" / "calls.jsonl"))
    ap.add_argument("--out", default=str(HERE / "results"))
    a = ap.parse_args(argv)
    if sha256_file(HERE / "run_s14.py") != RUN_SHA256:
        raise SystemExit("run_s14.py does not match its sealed fingerprint")
    parse_verdict = load_functions(HERE / "run_s14.py", ["parse_verdict"], constants=["VERDICTS"])["parse_verdict"]
    key = load_key()
    fp = text_fingerprints()
    calls = Path(a.calls)
    rows = load_calls(calls, key, parse_verdict, fp)
    s = measures(rows, key, lambda r: r.get("verdict"))
    fc = forecasts(s)
    sec = secondary(rows)
    sec_measures = {}
    for name in sec:
        if sec[name]["disagreements"]:
            reads = sec[name]["reads"]
            sec_measures[name] = measures(rows, key, lambda r, reads=reads: reads[(r["model_key"], r["id"], r["variant"], r["repeat"])])
    meta = {"calls_sha256": sha256_file(calls), "rows": len(rows), "errors": sum(1 for r in rows if r.get("error")),
            "no_verdict": sum(1 for r in rows if r.get("verdict") is None), "text_fingerprints": fp,
            "notes": design_part_notes(fp)}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {"meta": meta, "scores": s, "forecasts": fc,
               "secondary": {k: {kk: vv for kk, vv in v.items() if kk != "reads"} for k, v in sec.items()},
               "secondary_measures": sec_measures}
    (out / "S14-SCORED.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    write_report(out / "S14-SCORED.md", s, fc, sec, sec_measures, meta)
    for m in MODELS:
        print(f"{m}: changed {s[m]['changed_pairs']}/108, repeats {s[m]['repeats']['agree']}/44; {s[m]['word_alone']}")
    print("forecasts: " + ", ".join(f"{f['id']} {'held' if f['held'] else 'did not hold'}" for f in fc))
    print(f"secondary reads: reference {sec['reference']['disagreements']}, full key {sec['full_key']['disagreements']} disagreements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
