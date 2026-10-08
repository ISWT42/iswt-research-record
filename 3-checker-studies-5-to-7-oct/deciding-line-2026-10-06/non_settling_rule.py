"""NON-SETTLING: the one rule of my own (PREREG-2.md). Written after I had seen the six local R2 false "shown" items and all 39
local R2 "shown" quotes of the development set, and before any hosted-pair quote was opened. It is in-sample for the local pair.

Mechanism (one): a quote that settles a claim must report the claimed outcome first-hand and finally. A quote that carries
a non-settling word reports something else: that the request was only acknowledged (accepted, queued, pending ...), that someone
else said so (says, reports, according to ...), or that the line is hypothetical (preview, would, dry run ...). The rule keeps R2's
"shown" only if neither verified quote carries such a word that the CLAIM does not itself use (a claim that says "scheduled" is
settled by "scheduled"). Words are whole words, case-insensitive. If either quote's evidence cannot be re-derived, the rule fails closed.

Inputs: the two verified quotes and the claim text. Never truth, deciding line, trap or why. Written from general knowledge of how
logs and chat hand-offs speak; the lists are fixed here and never edited after the stamp.
"""
import re

import deciding_rules as DR

I = re.IGNORECASE
# A word counts only as a whole word that is not glued to a path or identifier: not right after / \ . _ - and not right before
# one of those followed by a word character (so build/reports/x.html, reports.json, --async and claims_service are not flagged).
_BEFORE = r"(?<![/\\._-])\b"
_AFTER = r"\b(?![/\\._-]\w)"


def _fam(*alternatives):
    return re.compile("|".join(_BEFORE + "(" + a + ")" + _AFTER for a in alternatives), I)


FAMILIES = (
    ("acknowledged_not_done", _fam(r"accepted|queued|enqueued|pending|scheduled|submitted|requested|initiated|dispatched|awaiting|"
                                   r"async|asynchronous|asynchronously", r"in[ -]progress")),
    ("secondhand_report", _fam(r"says|said|reports|reported|claims|claimed|told|asserts|asserted|relayed|hand-?off", r"according to")),
    ("hypothetical_or_preview", _fam(r"preview|simulated|simulation|would|should", r"dry[ -]run", r"not yet", r"so far")),
)
NAME = "NON-SETTLING"


def _plain(text):
    """Lowercase, every run of non-alphanumeric characters becomes one space, padded so ' word ' tests whole words."""
    return " " + re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip() + " "


def non_settling_words(text):
    """Set of (family, word) found in text; the word is lowercased with spaces and hyphens folded to one space."""
    found = set()
    if not isinstance(text, str):
        return found
    for fam, pat in FAMILIES:
        for m in pat.finditer(text):
            word = next(g for g in m.groups() if g)
            found.add((fam, re.sub(r"[ -]+", " ", word.lower())))
    return found


def unclaimed_words(quote, claim):
    """Non-settling words of the quote that the claim does not itself use (whole-word test on plain text)."""
    padded = _plain(claim)
    return sorted((fam, w) for fam, w in non_settling_words(quote) if (" " + w + " ") not in padded)


def make_rule(items):
    """Rule factory: `items` maps item id -> item; only the item's claim text is read from it (never truth, deciding line, trap, why).
    The item id is read from the turns' row ids ('<id>:<n>'), as deciding_rules.turns_for builds them."""
    def rule(ctx):
        a, b = ctx.ev_a, ctx.ev_b
        if a is None or b is None or not ctx.turns:
            return False, "unresolved"
        item_id = ctx.turns[0].row_id.rsplit(":", 1)[0]
        claim = items[item_id].get("claim", "") if item_id in items else ""
        fams = sorted({fam for q in (a.quote, b.quote) for fam, _ in unclaimed_words(q, claim)})
        if fams:
            return False, "non_settling:" + "+".join(fams)
        return True, "no_unclaimed_non_settling_word"
    return rule
