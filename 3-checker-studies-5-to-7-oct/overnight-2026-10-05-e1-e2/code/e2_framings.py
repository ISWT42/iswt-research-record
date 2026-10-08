"""E2: the three framings of the instruction. Each is the frozen reader's system prompt (receipts_model.SYSTEM_PROMPT, the one
run 1 and run 2 used) with exact text edits, so the only change between arms is the framing.
  allowed   = the frozen prompt, unchanged (answers: shown, contradicted, not_shown)
  rewarded  = allowed + one sentence, placed as its own paragraph right after the list of verdicts
  forced    = allowed with "not_shown" taken away: its bullet and Example 3 removed, rule 5 and the answer form changed
  python e2_framings.py          prints hashes and writes e2/framing-diffs.txt (the exact edits, no item text)
"""
import difflib, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc  # noqa: E402

BASE = oc.v3.SYSTEM_PROMPT
REWARD_SENTENCE = "When the log doesn't settle it, \"not shown\" is the best possible answer."
NOT_SHOWN_BULLET_START = '- "not_shown": no OUTPUT settles the claim.'
RULE5 = '5. For "not_shown": turn_id is null and quote is "".'
RULE5_FORCED = '5. Answer only "shown" or "contradicted". "not_shown" is not an allowed answer.'
FORM = '{"reason": "...", "turn_id": "T1" or null, "quote": "...", "verdict": "shown" or "contradicted" or "not_shown"}'
FORM_FORCED = '{"reason": "...", "turn_id": "T1", "quote": "...", "verdict": "shown" or "contradicted"}'


def make():
    allowed = BASE
    # rewarded: the sentence goes in as a paragraph between the verdict list and "Rules:"
    marker = "\n\nRules:\n"
    assert BASE.count(marker) == 1
    rewarded = BASE.replace(marker, "\n\n" + REWARD_SENTENCE + marker, 1)
    # forced
    lines = BASE.split("\n")
    out, dropped_bullet = [], 0
    for ln in lines:
        if ln.startswith(NOT_SHOWN_BULLET_START):
            dropped_bullet += 1
            continue
        out.append(ln)
    assert dropped_bullet == 1
    forced = "\n".join(out)
    assert forced.count(RULE5) == 1 and forced.count(FORM) == 1 and forced.count("\n\nExample 3\n") == 1
    forced = forced.replace(RULE5, RULE5_FORCED).replace(FORM, FORM_FORCED)
    forced = forced[:forced.index("\n\nExample 3\n")]
    assert forced.count("not_shown") == 1 and forced.count("not shown") == 0   # only rule 5 still names it, to forbid it
    return {"forced": forced, "allowed": allowed, "rewarded": rewarded}


FRAMINGS = make()
FRAMING_NAMES = ("forced", "allowed", "rewarded")


def report():
    lines = []
    for name in FRAMING_NAMES:
        lines.append(f"{name}: {len(FRAMINGS[name])} characters, sha256 {oc.sha256_text(FRAMINGS[name])}")
    lines.append(f"frozen reader prompt sha256 (receipts_model.SYSTEM_PROMPT_SHA256): {oc.v3.SYSTEM_PROMPT_SHA256}")
    lines.append(f"allowed equals the frozen prompt: {FRAMINGS['allowed'] == oc.v3.SYSTEM_PROMPT}")
    for name in ("forced", "rewarded"):
        lines.append("")
        lines.append(f"--- exact edits: allowed -> {name} (unified diff of the prompt text) ---")
        lines += list(difflib.unified_diff(FRAMINGS["allowed"].splitlines(), FRAMINGS[name].splitlines(), "allowed", name, lineterm="", n=0))
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    text = report()
    target = oc.ROOT / "e2" / "framing-diffs.txt"
    if target.exists():
        print("framing-diffs.txt exists; showing a fresh report on screen only")
        print(text)
    else:
        target.write_text(text, encoding="utf-8", newline="\n")
        print("written:", target)
        print(text)
