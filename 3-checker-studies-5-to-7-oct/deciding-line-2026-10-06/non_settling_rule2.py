"""NON-SETTLING-2: version 2 of the one rule of my own (PREREG-3.md). It replaces NON-SETTLING (version 1, PREREG-2.md) in the E1 rule set.

Version 1 had three word families (acknowledged, secondhand, hypothetical). Reading run 1's 21 false "shown" showed that most of them cite a
real line from another environment (a line tagged stage, sim, preview, demo ...) for a claim about production. Version 2 adds that
family. The same mechanism: a quote that settles a claim reports the claimed outcome first-hand, finally, and in the claimed place.

Version 2 keeps R2's "shown" only if (1) version 1 keeps it (no unclaimed non-settling word in either quote), and (2) neither verified quote,
nor the command of the turn it cites, contains an ENVIRONMENT word that the claim does not itself use. Environment words are whole tokens
(letters and digits, lowercase; "atlas-rehearsal" gives the tokens atlas and rehearsal). Fail closed if either quote's evidence is missing.
Inputs: the two verified quotes, the commands of the cited turns, the claim. Never truth, deciding line, trap or why.
Written after the development sets (ids 001 to 300) were read: in-sample for them; E1 is the only out-of-sample test.
"""
import re

import non_settling_rule as V1

NAME = "NON-SETTLING-2"
ENV_WORDS = frozenset({"stage", "staging", "sandbox", "rehearsal", "sim", "simulator", "demo", "mock", "preprod", "qa", "uat",
                       "canary", "replica", "mirror", "shadow", "localhost", "preview"})


def tokens(text):
    """Lowercase alphanumeric tokens of a text (a path, host name or flag is split at every other character)."""
    return set(re.findall(r"[a-z0-9]+", str(text or "").lower()))


def unclaimed_env_words(texts, claim):
    """Environment words found in any of the texts that the claim does not itself use, sorted."""
    found = set()
    for t in texts:
        found |= tokens(t) & ENV_WORDS
    return sorted(found - tokens(claim))


def make_rule(items):
    """Rule factory: `items` maps item id -> item; only the item's claim text is read from it."""
    v1 = V1.make_rule(items)

    def rule(ctx):
        keep, why = v1(ctx)
        if not keep:
            return False, why                    # includes the fail-closed case 'unresolved'
        a, b = ctx.ev_a, ctx.ev_b
        item_id = ctx.turns[0].row_id.rsplit(":", 1)[0]
        claim = items[item_id].get("claim", "") if item_id in items else ""
        texts = [a.quote, b.quote, ctx.turns[a.turn_index].cmd, ctx.turns[b.turn_index].cmd]
        if unclaimed_env_words(texts, claim):
            return False, "non_settling:other_environment"
        return True, "no_unclaimed_non_settling_word"
    return rule
