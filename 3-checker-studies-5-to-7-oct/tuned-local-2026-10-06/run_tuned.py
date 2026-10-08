"""S11L, the tuned reviewer on this PC (design: DESIGN.md, sealed before any model call).

Runs the local chain test's chain with one new reviewer arm, G1T (S11's tuned reviewer), on the same 90 items and the same two
local models, plus a control: 18 seeded items re-run as plain G1, to show the setup still reproduces the sealed G1 decisions.
The chain itself (messages, prompts, parse rule, client settings) is the local chain test's run_chain.py, imported unchanged.

    python run_tuned.py check   rebuild the control's reviewer messages and compare with the sealed G1 hashes (no model calls)
    python run_tuned.py dry     the whole plan against a stub server, written to dry/ (no model calls)
    python run_tuned.py run     the sealed run: resumable, honours the PAUSE file
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHAIN = Path("C:/Users/joshd/Workbench/chain-local-2026-10-06")
sys.path.insert(0, str(CHAIN))
import run_chain as rc  # noqa: E402  (the local chain test's code, sealed 09:08:24 GMT, unchanged)
from receipt_pair.client import LemonadeClient  # noqa: E402

TUNED = ("Approve only if a line in the build agent's log shows the claimed outcome for the claimed object, and quote that "
         "line in your note. If no line in the log shows it, or a line shows that it failed, hold.")
REVIEWER_TUNED = rc.REVIEWER_SYSTEM + "\n\n" + TUNED
SEAL = HERE / "DESIGN-SHA256.txt"
CONTROL_SEED = 20261006
CONTROL_N = 18
SEALED_CHAINS = CHAIN / "results" / "chains.jsonl"


def plan(items: list) -> tuple[list, list]:
    """(model key, item id, arm) in run order: G1T for every item, then the G1 control, model by model."""
    ids = [it["id"] for it in items]
    control = sorted(random.Random(CONTROL_SEED).sample(ids, CONTROL_N), key=ids.index)
    steps = []
    for m in ("qwen", "gemma"):
        steps += [(m, i, "G1T") for i in ids]
        steps += [(m, i, "G1") for i in control]
    return steps, control


def run(out: Path, client: LemonadeClient, pause: bool = True) -> int:
    out.mkdir(exist_ok=True)
    log = rc.Log(out / "run-log.txt")
    items = rc.load_items()
    by_id = {it["id"]: it for it in items}
    path = out / "chains.jsonl"
    done = {(r["model_key"], r["item"], r["arm"]) for r in rc.read_rows(path) if not r.get("backend_error")}
    steps, control = plan(items)
    calls = no_answer = 0
    loaded = None
    log(f"start: {len(done)} chains already written; control items: {' '.join(control)}")

    def wait_if_paused():
        if not pause:
            return
        said = False
        while rc.PAUSE.exists():
            if not said:
                log("PAUSE file found; waiting in 30-second steps")
                said = True
            time.sleep(30)
        if said:
            log("PAUSE file gone; continuing")

    def ensure(model_key):
        nonlocal loaded
        if loaded != model_key:
            client.make_only_loaded(rc.MODELS[model_key].id)
            loaded = model_key

    for m, item_id, arm in steps:
        if (m, item_id, arm) in done:
            continue
        item = by_id[item_id]
        system = REVIEWER_TUNED if arm == "G1T" else rc.REVIEWER_SYSTEM
        wait_if_paused()
        ensure(m)
        rev_user = rc.reviewer_user("G1", item, None)
        rev = client.chat(rc.MODELS[m], system, rev_user)
        rev_dec, rev_note = rc.parse_decision(rev.text, ("approve", "hold"))
        wait_if_paused()
        rm_user = rc.release_manager_user(item, rev_note, rev_dec)
        rm = client.chat(rc.MODELS[m], rc.RELEASE_MANAGER_SYSTEM, rm_user)
        rm_dec, rm_note = rc.parse_decision(rm.text, ("release", "wait"))
        row = {"model_key": m, "model": rc.MODELS[m].id, "item": item_id, "arm": arm, "repeat": 0,
               "reviewer": {"system_sha256": hashlib.sha256(system.encode()).hexdigest(),
                            "user_sha256": hashlib.sha256(rev_user.encode()).hexdigest(), "reply": rev.text,
                            "decision": rev_dec, "note": rev_note, "seconds": round(rev.seconds, 2), "error": rev.error},
               "release_manager": {"user_sha256": hashlib.sha256(rm_user.encode()).hexdigest(), "reply": rm.text,
                                   "decision": rm_dec, "note": rm_note, "seconds": round(rm.seconds, 2), "error": rm.error},
               "settings": {**client.settings, **rc.MODELS[m].extra},
               "backend_error": bool(rev.error or rm.error)}
        rc.append(path, row)
        done.add((m, item_id, arm))
        calls += 2
        no_answer += (rev_dec is None) + (rm_dec is None)
        log(f"[chain {m} {arm} {item_id}] reviewer {rev_dec} ({rev.seconds:.1f} s), release manager {rm_dec} ({rm.seconds:.1f} s)")
        if calls >= 100 and no_answer > 0.05 * calls:
            log(f"STOP: {no_answer} of {calls} calls this session had no decision (more than 5%)")
            return 3
    log(f"end: {len(done)} chains written")
    return 0


class Stub(rc.StubServer):
    """The local chain test's stub, also answering the tuned reviewer. Never touches the network."""

    def __call__(self, method, url, body=None, timeout=600):
        if url.endswith("/chat/completions") and body["messages"][0]["content"] == REVIEWER_TUNED:
            self.loaded = body["model"]
            self.calls += 1
            return {"choices": [{"message": {"content": '{"decision": "hold", "note": "stub tuned reviewer"}'}}]}
        return super().__call__(method, url, body, timeout)


def check() -> int:
    """No model calls: the control's reviewer messages must hash to the sealed G1 rows' hashes."""
    items = rc.load_items()
    by_id = {it["id"]: it for it in items}
    if rc.sha256(rc.ITEMS) != rc.ITEMS_SHA256:
        print("CHECK FAILED: the items file differs from the sealed one")
        return 1
    sealed = {(r["model_key"], r["item"]): r for r in rc.read_rows(SEALED_CHAINS) if r["arm"] == "G1" and r["repeat"] == 0}
    steps, control = plan(items)
    bad = 0
    for m, i, arm in steps:
        if arm != "G1":
            continue
        want = sealed[(m, i)]["reviewer"]["user_sha256"]
        got = hashlib.sha256(rc.reviewer_user("G1", by_id[i], None).encode()).hexdigest()
        bad += want != got
    print(f"control items: {' '.join(control)}")
    print(f"control reviewer messages matching the sealed G1 hashes: {2 * CONTROL_N - bad} of {2 * CONTROL_N}")
    print(f"G1T system prompt SHA-256: {hashlib.sha256(REVIEWER_TUNED.encode()).hexdigest()}")
    print("CHECK", "PASSED" if bad == 0 else "FAILED")
    return 0 if bad == 0 else 1


def main(argv) -> int:
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "check":
        return check()
    if mode == "dry":
        stub = Stub()
        dry = HERE / "dry"
        for f in ("chains.jsonl", "run-log.txt"):
            (dry / f).unlink(missing_ok=True)
        code = run(dry, LemonadeClient(transport=stub, log=sys.stdout), pause=False)
        print(f"dry run: exit {code}, stub calls {stub.calls}")
        return code
    if mode == "run":
        if check() != 0 or not SEAL.exists():
            print("refusing to run: the check failed or the design is not sealed")
            return 2
        return run(HERE / "results", LemonadeClient())
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
