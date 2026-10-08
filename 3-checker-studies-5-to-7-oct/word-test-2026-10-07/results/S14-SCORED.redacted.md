> Published copy. The sealed original `S14-SCORED.md` (SHA-256 `57438ea1b2bd3e895bcd2ed7dc7b4b08a15beb2213c5b8da941dc7bd9ccf84d6`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# S14, the word test: scored

Scored by `score_s14.py` (sealed before it ran). Calls file SHA-256 `6ab0daa90d6377e722900baa164d8f3f1b2833784f0c45dd82fffdda43b9b0d4`; 520 calls; 0 with a client error; 0 without a verdict. Each count sits beside its own denominator.

## The headline
- **Qwen:** 3 of 108 pairs changed verdict when only the word changed (forced 2 of 54, allowed 1 of 54); repeats agreed on 44 of 44. "The word alone changes this model's verdict": shown (at least one pair changed, and all 44 repeats agree).
- **Gemma:** 1 of 108 pairs changed verdict when only the word changed (forced 0 of 54, allowed 1 of 54); repeats agreed on 44 of 44. "The word alone changes this model's verdict": shown (at least one pair changed, and all 44 repeats agree).

## Per model
### Qwen (`Qwen3-4B-Instruct-2507-GGUF`)

| Count | cannot | can't | of | cannot only | can't only | exact McNemar p |
|---|---|---|---|---|---|---|
| Forced: breaks (anything but shown or contradicted) | 11 | 10 | 54 | 1 | 0 | 1 |
| Forced: guesses on missing logs | 16 | 17 | 27 | 0 | 1 | 1 |
| Forced: right on intact logs | 25 | 25 | 27 | 0 | 0 | 1 |
| Allowed: guesses on missing logs | 9 | 8 | 27 | 1 | 0 | 1 |
| Allowed: right on intact logs | 24 | 24 | 27 | 0 | 0 | 1 |
| Allowed: not_shown on missing logs | 18 | 19 | 27 | 0 | 1 | 1 |

Forced against allowed, both words together: guesses on missing logs 33 of 54 (forced) against 17 of 54 (allowed).

Verdicts per text (main block): forced_cannot: contradicted 24, not_shown 11, shown 19; forced_cant: contradicted 24, not_shown 10, shown 20; allowed_cannot: contradicted 18, not_shown 18, shown 18; allowed_cant: contradicted 17, not_shown 19, shown 18.

Changed pairs:

| Record | Framing | Log | Key | cannot | can't |
|---|---|---|---|---|---|
| T028 | forced | twin_missing | not_shown | contradicted | shown |
| T028 | allowed | twin_missing | not_shown | contradicted | not_shown |
| T030 | forced | twin_missing | not_shown | not_shown | contradicted |

Directions shown (exact McNemar p < 0.05): none.

### Gemma (`Gemma-4-E4B-it-GGUF`)

| Count | cannot | can't | of | cannot only | can't only | exact McNemar p |
|---|---|---|---|---|---|---|
| Forced: breaks (anything but shown or contradicted) | 4 | 4 | 54 | 0 | 0 | 1 |
| Forced: guesses on missing logs | 23 | 23 | 27 | 0 | 0 | 1 |
| Forced: right on intact logs | 25 | 25 | 27 | 0 | 0 | 1 |
| Allowed: guesses on missing logs | 13 | 14 | 27 | 0 | 1 | 1 |
| Allowed: right on intact logs | 25 | 25 | 27 | 0 | 0 | 1 |
| Allowed: not_shown on missing logs | 14 | 13 | 27 | 1 | 0 | 1 |

Forced against allowed, both words together: guesses on missing logs 46 of 54 (forced) against 27 of 54 (allowed).

Verdicts per text (main block): forced_cannot: contradicted 21, not_shown 4, shown 29; forced_cant: contradicted 21, not_shown 4, shown 29; allowed_cannot: contradicted 19, not_shown 14, shown 21; allowed_cant: contradicted 19, not_shown 13, shown 22.

Changed pairs:

| Record | Framing | Log | Key | cannot | can't |
|---|---|---|---|---|---|
| T033 | allowed | twin_missing | not_shown | not_shown | shown |

Directions shown (exact McNemar p < 0.05): none.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

## The two secondary reads (the parser audit's rule; exploratory)

- **The reference rule exactly:** 0 of 520 replies read differently from the stored verdict.
- **The full-key variant (reason, turn_id, quote, verdict):** 0 of 520 replies read differently from the stored verdict.

## Checks and notes
- Every row's text fingerprint equals the text the sealed runner builds from the sealed framings; every row's record fingerprint equals its sealed S12 record; every stored verdict equals a fresh read with the runner's own parser; the S12 key matches its 6 Oct seal; the main and repeat blocks are complete (216 and 44 calls per model).
- DESIGN.md prints allowed_cant's fingerprint as 661cb45c...6ad7; the text the sealed runner builds from the sealed framings has 661cb45c...4ad7 (full value 661cb45cd5072fc76bf790b8c65c55db99080aa0d9e536d9e32ac08e646b4ad7). Every allowed_cant call row carries the full value, so the printed part is a typo in the design, not a different text.

## What this does not settle
- Two small local models, not Claude; one sentence in one place per text; one apostrophe; one item bank written by models, whose labels no person has checked yet.
- A changed pair shows that this model's verdict moved when one word moved, at temperature 0 with a fixed seed. It does not show why, or that the same happens in other sentences or other models.
