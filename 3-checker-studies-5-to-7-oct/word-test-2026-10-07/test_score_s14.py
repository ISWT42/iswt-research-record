"""A synthetic test of score_s14.py, run before the scorer was sealed. No model calls, and the real results are never read.

It builds 520 made-up calls in the runner's exact row shape, with answers chosen so every count is known in advance, runs the
scorer on them, and checks each number. Planted on purpose:
  - Qwen: two changed pairs (one forced, a break under can't only; one allowed, a client error with no verdict under can't),
    and a reply whose quote holds JSON (it must still read as its verdict);
  - Gemma: no changed pair; one repeat that disagrees with the main block; one missing log whose reply under both words is
    the answer object followed by a quoted example object, so the runner's rule reads "not_shown" and the full-key read
    reads "shown" (the parser audit's last-object hazard).

    python test_score_s14.py OUT_DIR
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score_s14 as S  # noqa: E402


def reply(verdict, turn="T2", quote="OUTPUT: done"):
    if verdict == "not_shown":
        return json.dumps({"reason": "r", "turn_id": None, "quote": "", "verdict": "not_shown"})
    return json.dumps({"reason": "r", "turn_id": turn, "quote": quote, "verdict": verdict})


HAZARD = ('{"reason": "r", "turn_id": "T2", "quote": "OUTPUT: done", "verdict": "shown"} '
          'For comparison, an empty log would get {"verdict": "not_shown"}.')
IN_QUOTE = ('{"reason": "r", "turn_id": "T2", "quote": "{\\"commit\\":\\"b71e4c9\\",\\"state\\":\\"success\\"}", '
            '"verdict": "%s"}')


def main(out_dir: str) -> int:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    parse_verdict = S.load_functions(HERE / "run_s14.py", ["parse_verdict"], constants=["VERDICTS"])["parse_verdict"]
    key = S.load_key()
    reqs = S.requests()
    user_sha = {r["id"]: hashlib.sha256(r["user"].encode("utf-8")).hexdigest() for r in reqs}
    ids = [r["id"] for r in reqs]
    missing = [i for i in ids if key[i]["kind"] == "twin_missing"]
    intact = [i for i in ids if key[i]["kind"] == "present"]
    repeat_ids = S.expected_repeat_ids()
    fp = S.text_fingerprints()
    m1, i1 = missing[0], intact[0]
    m2 = missing[1]
    i_quote = intact[2]

    def base(model, rid, variant):
        if variant.startswith("allowed"):
            return reply("not_shown") if key[rid]["kind"] == "twin_missing" else reply(key[rid]["truth"])
        return reply("shown") if key[rid]["kind"] == "twin_missing" else reply(key[rid]["truth"])

    rows = []
    for model in S.MODELS:
        for rep in (0, 1):
            for rid in (ids if rep == 0 else repeat_ids):
                for v in S.VARIANTS:
                    text, error = base(model, rid, v), None
                    if model == "qwen" and rid == m1 and v == "forced_cant":
                        text = reply("not_shown")                       # changed pair 1: a break under can't only
                    if model == "qwen" and rid == i1 and v == "allowed_cant":
                        text, error = "", "timeout"                     # changed pair 2: no verdict under can't
                    if rid == i_quote and v.startswith("forced"):
                        text = IN_QUOTE % key[rid]["truth"]             # JSON inside the quote, both words
                    if model == "gemma" and rid == m2 and v.startswith("forced"):
                        text = HAZARD                                   # the last-object hazard, both words
                    if model == "gemma" and rep == 1 and rid == repeat_ids[0] and v == "forced_cannot":
                        text = reply("contradicted") if base(model, rid, v) != reply("contradicted") else reply("shown")
                    verdict, quote = parse_verdict(text)
                    rows.append({"model_key": model, "id": rid, "variant": v, "repeat": rep, "model": S.MODEL_IDS[model],
                                 "started": "2026-10-07T00:00:00Z", "seconds": 1.0, "system_sha256": fp[v],
                                 "user_sha256": user_sha[rid], "request": {}, "reply": text, "error": error,
                                 "verdict": verdict, "quote": quote})
    calls = out / "calls.jsonl"
    calls.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8", newline="\n")
    assert S.main(["--calls", str(calls), "--out", str(out)]) == 0
    got = json.loads((out / "S14-SCORED.json").read_text(encoding="utf-8"))
    q, g = got["scores"]["qwen"], got["scores"]["gemma"]
    gemma_m2_repeat = m2 in repeat_ids

    def check(name, value, want):
        assert value == want, (name, value, want)

    check("qwen changed", q["changed_pairs"], 2)
    check("qwen changed by framing", q["changed_by_framing"], {"forced": 1, "allowed": 1})
    check("qwen forced breaks", (q["forced_breaks"]["cannot"], q["forced_breaks"]["cant"]), (0, 1))
    check("qwen forced breaks p", q["forced_breaks"]["mcnemar_p"], 1.0)
    check("qwen forced guesses missing", (q["forced_guesses_missing"]["cannot"], q["forced_guesses_missing"]["cant"]), (27, 26))
    check("qwen forced right intact", (q["forced_right_intact"]["cannot"], q["forced_right_intact"]["cant"]), (27, 27))
    check("qwen allowed right intact", (q["allowed_right_intact"]["cannot"], q["allowed_right_intact"]["cant"]), (27, 26))
    check("qwen allowed guesses missing", (q["allowed_guesses_missing"]["cannot"], q["allowed_guesses_missing"]["cant"]), (0, 0))
    check("qwen repeats", (q["repeats"]["agree"], q["repeats"]["of"]), (44, 44))
    check("qwen reading", q["word_alone"].split(" (")[0], "shown")
    check("gemma changed", g["changed_pairs"], 0)
    check("gemma forced breaks", (g["forced_breaks"]["cannot"], g["forced_breaks"]["cant"]), (1, 1))
    check("gemma repeats", (g["repeats"]["agree"], g["repeats"]["of"]), (43, 44))
    check("gemma reading", g["word_alone"], "not shown (no pair changed)")
    check("forced vs allowed qwen", (q["forced_vs_allowed_guesses_missing"]["forced"], q["forced_vs_allowed_guesses_missing"]["allowed"]), (53, 0))
    check("forced vs allowed gemma", (g["forced_vs_allowed_guesses_missing"]["forced"], g["forced_vs_allowed_guesses_missing"]["allowed"]), (52, 0))
    held = {f["id"]: f["held"] for f in got["forecasts"]}
    check("forecasts", held, {"W1": True, "W2": True, "W3": True, "W4": False, "W5": True, "W6": True})
    check("brier W4", [f["brier"] for f in got["forecasts"] if f["id"] == "W4"][0], 0.5625)
    # the hazard: 2 main-block replies (plus 2 more if that record is also in the repeat block) read differently under full key only
    hazard_rows = 2 + (2 if gemma_m2_repeat else 0)
    check("reference read disagreements", got["secondary"]["reference"]["disagreements"], 0)
    check("full-key read disagreements", got["secondary"]["full_key"]["disagreements"], hazard_rows)
    check("full-key direction", got["secondary"]["full_key"]["by_direction"], {"different": hazard_rows})
    fk = got["secondary_measures"]["full_key"]["gemma"]
    check("gemma forced breaks under full key", (fk["forced_breaks"]["cannot"], fk["forced_breaks"]["cant"]), (0, 0))
    check("mcnemar 0/6", S.mcnemar_exact(0, 6), 0.03125)
    check("mcnemar 1/7", round(S.mcnemar_exact(1, 7), 6), 0.070312)
    check("mcnemar 0/0", S.mcnemar_exact(0, 0), 1.0)
    check("design typo noted", len(got["meta"]["notes"]), 1)
    assert "allowed_cant" in got["meta"]["notes"][0] and "6ad7" in got["meta"]["notes"][0]
    report = (out / "S14-SCORED.md").read_text(encoding="utf-8")
    assert "did not hold" in report and "failed" not in report.lower()
    print(f"synthetic test ok: {len(rows)} made-up calls, every planted count read back as planted "
          f"(hazard record in repeat block: {gemma_m2_repeat})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
