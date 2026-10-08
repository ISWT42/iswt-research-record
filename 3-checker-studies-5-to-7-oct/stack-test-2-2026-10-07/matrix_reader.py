"""Stack test 2 (Test A): the reader, box-safe.

Two rules, both cell-independent (one parser for every cell):

  SEALED rule (the scored one): a mirror of the coat-check screen's `read` in score_screen.py, which uses the entry's
  `parse_response` (cvp/scorer.py): drop <think> blocks, drop a code fence, then the whole text, then the first "{" to the last "}".
  Then the version's words: report and did-the-work take status done / partial / failed / unknown and a claims list;
  coat-check and coat-check-did take verdict shown / contradicted / not_shown. The mirror exists so the runner (which runs in the
  box, where the entry's code is not) can judge a reply for its pause rule. score_matrix.py scores with the screen's own `read` and
  stops if this mirror ever disagrees with it (test_score_matrix.py checks every planted reply).

  REFERENCE rule (the audit, S10; never scored): the same, then, if the text holds more than one object or a stray brace, the LAST
  complete JSON object that holds the version's field, found with json.JSONDecoder.raw_decode from each "{" (braces inside strings
  and a quote that is itself JSON are handled by the decoder, not by a pattern). The S13 miss was a pattern that forbade braces.

Standard library only (Python 3.10).
"""
from __future__ import annotations

import json
import re

STATUSES = ("done", "partial", "failed", "unknown")
ENTRY_VERSIONS = {"report", "did-the-work"}
VERDICT_WORDS = {"shown", "contradicted", "not_shown"}
WORDS = {"coat-check": ("verdict", VERDICT_WORDS, "shown"), "coat-check-did": ("verdict", VERDICT_WORDS, "shown")}
_FENCE = re.compile(r"^```[a-zA-Z]*\s*|\s*```$")


def success_word(version: str) -> str:
    return "done" if version in ENTRY_VERSIONS else WORDS[version][2]


def field_of(version: str) -> str:
    return "status" if version in ENTRY_VERSIONS else WORDS[version][0]


def _clean(raw):
    text = raw.strip()
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    return _FENCE.sub("", text).strip()


def parse_sealed(raw):
    """Mirror of cvp.scorer.parse_response: (obj, error)."""
    if isinstance(raw, dict):
        return raw, None
    if not isinstance(raw, str) or not raw.strip():
        return None, "empty"
    text = _clean(raw)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        a, b = text.find("{"), text.rfind("}")
        if a == -1 or b <= a:
            return None, "no_json"
        try:
            obj = json.loads(text[a:b + 1])
        except json.JSONDecodeError:
            return None, "bad_json"
    if not isinstance(obj, dict):
        return None, "not_object"
    return obj, None


def _words(version: str, obj):
    """(valid, said, error) once an object is in hand."""
    if version in ENTRY_VERSIONS:
        said = obj.get("status")
        if not isinstance(said, str) or said.strip().lower() not in STATUSES:
            return False, None, "bad_status"
        if not isinstance(obj.get("claims", []), list):
            return False, None, "claims_not_list"
        return True, said.strip().lower(), None
    field, allowed, _ = WORDS[version]
    said = obj.get(field)
    if not isinstance(said, str) or said.strip().lower() not in allowed:
        return False, None, "bad_" + field
    return True, said.strip().lower(), None


def read_sealed(version: str, reply):
    """(valid, said, error) under the sealed rule."""
    obj, err = parse_sealed(reply)
    if err:
        return False, None, err
    return _words(version, obj)


def parse_reference(raw, field: str):
    """(obj, error): the sealed parse, else the last complete object that holds `field`."""
    obj, err = parse_sealed(raw)
    if obj is not None and field in obj:
        return obj, None
    if not isinstance(raw, str) or not raw.strip():
        return None, "empty"
    text = _clean(raw)
    dec = json.JSONDecoder()
    found, i = [], 0
    while True:
        i = text.find("{", i)
        if i == -1:
            break
        try:
            o, end = dec.raw_decode(text, i)
        except json.JSONDecodeError:
            i += 1
            continue
        if isinstance(o, dict) and field in o:
            found.append(o)
        i = end if isinstance(o, dict) else i + 1
    if found:
        return found[-1], None
    return None, err or "no_json"


def read_reference(version: str, reply):
    obj, err = parse_reference(reply, field_of(version))
    if err:
        return False, None, err
    return _words(version, obj)
