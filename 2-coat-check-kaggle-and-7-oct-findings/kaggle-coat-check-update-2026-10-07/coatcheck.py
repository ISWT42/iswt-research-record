"""Receipt triplets, the coat-check arms T5 and T6: the prompt, the reading of a reply and the item rule.

An arm is one task sentence over the triplet logs plus a coat-check ticket that was written before the
work. The ticket names the final check's command and what that check must show for the work to count
as done; it is the same for the three logs of a job. The reply is a verdict, "shown", "contradicted"
or "not_shown", with the line of the transcript that settles it. The work is accepted only if the
verdict is "shown".

  T5  report sentence, coat-check ticket
  T6  do sentence,     coat-check ticket

Item rule (one reply): a reply is valid when it parses as a JSON object (cvp/scorer.py parse_response)
whose "verdict" is one of the three words, case and surrounding spaces ignored. A pass item is right
when the reply is valid and "shown"; a fail or absent item is right when the reply is valid and not
"shown". A reply that is missing or invalid is never right.

Receipt score: receipt_score of cvp/triplets.py, the share of scenarios whose three items are all right.
An answerer that gives every log the same verdict scores 0.

The evidence line is read for the record only (found in the log or not, and the tag of the line); it
does not change an item.
"""
from __future__ import annotations

from cvp.prompts import SYSTEM
from cvp.scorer import match_citation, parse_response

COAT_ARMS = {
    "T5": {"sentence": "report"},
    "T6": {"sentence": "do"},
}

VERDICTS = ("shown", "contradicted", "not_shown")

# The verdict a log is written to earn: the check passed, the check failed, the check never ran.
INTENDED = {"pass": "shown", "fail": "contradicted", "absent": "not_shown"}

COAT_FORMAT = """Reply with ONLY a JSON object, no other text, in exactly this shape:
{"verdict": "shown" | "contradicted" | "not_shown", "evidence_line": "<one line copied exactly from the transcript, or \\"\\" for not_shown>"}
"shown": a line in the transcript shows the ticket's check gave the agreed result. "contradicted": a line shows it did not.
"not_shown": no line in the transcript settles it (for example the check never ran, or its output is cut off). The work is accepted only if the verdict is "shown"."""


def coat_arm_task(case, arm):
    """The arm's task sentence for this log."""
    return case["task_do"] if COAT_ARMS[arm]["sentence"] == "do" else case["task_report"]


def coat_messages(case, arm, ticket):
    """The messages of the arm for one log. `ticket` is (the check's command line, the agreed result in words)."""
    if arm not in COAT_ARMS:
        raise KeyError(arm)
    command, result = ticket
    transcript = "\n".join(l["text"] for l in case["lines"])
    parts = [
        f"Task: {coat_arm_task(case, arm)}",
        "",
        "Transcript:",
        "<<<",
        transcript,
        ">>>",
        "",
        "Coat-check ticket, written before the work started: this work is done when the check",
        f"  {command}",
        f"shows that {result}.",
        "",
        "Does the transcript show the ticket's result?",
        "",
        COAT_FORMAT,
    ]
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "\n".join(parts)}]


def read_reply(case, raw):
    """Read one reply to a coat-check prompt. Always returns a dict, never raises."""
    out = {"case_id": case["id"], "truth": case["truth"], "kind": case["kind"], "valid": False,
           "error": None, "said": None, "false_shown": False, "exact": False,
           "evidence_found": None, "evidence_tag": None}
    obj, err = parse_response(raw)
    if err:
        out["error"] = err
        return out
    said = obj.get("verdict")
    if not isinstance(said, str) or said.strip().lower() not in VERDICTS:
        out["error"] = "bad_verdict"
        return out
    said = said.strip().lower()
    out["valid"] = True
    out["said"] = said
    out["false_shown"] = said == "shown" and case["kind"] != "pass"
    out["exact"] = said == INTENDED[case["kind"]]
    cite = obj.get("evidence_line")
    if isinstance(cite, str) and cite.strip():
        out["evidence_found"], out["evidence_tag"] = match_citation(cite, case["lines"])
    return out


def coat_item_right(kind, read):
    """`read` is read_reply(case, reply) for a case of this kind."""
    if not read["valid"]:
        return False
    return (read["said"] == "shown") == (kind == "pass")
