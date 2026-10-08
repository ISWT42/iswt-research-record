"""Run files in the shape of a downloaded Kaggle run, made from fake answerers. For tests and the dry run of the runner.

    python -B blindcheck_fakeruns.py write RESULTS_DIR TASK MODEL [--answerer NAME] [--start TIME] [--errored N]

writes one run file under RESULTS_DIR/TASK/1/MODEL/<run id>/ (the layout `kaggle b t download -o RESULTS_DIR`
makes) whose replies come from a fake answerer of blindcheck_dryrun.py. The shape follows the entry's own
downloaded runs: a run record with 48 subruns, each holding its conversation (the user prompt, the
assistant reply, the request's cost fields) and the item's result; Kaggle leaves a 0.0 result empty.
Nothing here talks to Kaggle.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENTRY = Path(os.environ.get("CVP_ENTRY", "C:/Users/joshd/Desktop/Moonshots/kaggle/claimed-vs-proven"))
sys.path.insert(0, str(ENTRY))
sys.path.insert(0, str(ENTRY / "kaggle"))
sys.path.insert(0, str(HERE))

import blindcheck_analysis as ca  # noqa: E402
import blindcheck_dryrun as dr  # noqa: E402
from blindcheck import COAT_ARMS, coat_item_right, read_reply  # noqa: E402
from cvp.triplet_cases import TRIPLET_CASES  # noqa: E402
from cvp.triplets import receipt_score  # noqa: E402

SLUG = {"gemini-3.8-flash": "google/gemini-3.8-flash", "gemini-3.7-flash": "google/gemini-3.7-flash",
        "claude-haiku-4-5-20251001": "anthropic/claude-haiku-4-5@20251001", "gpt-5.4-nano-2026-03-17": "openai/gpt-5.4-nano@2026-03-17"}


def _stamp(t):
    return t.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


def fake_run_json(arm, model, replies, start, errored=(), cost_per_call_nd=1_000_000, flip=(), prompt_edit=None,
                  run_value=None):
    """A run record. `replies` maps case id -> raw reply; `errored` is the case ids whose call errored (no reply);
    `flip` the case ids whose item result is written wrong; `prompt_edit` a function applied to every prompt;
    `run_value` overrides the run's own result."""
    task, child = ca.TASK[arm], f"receipt-item-{arm.lower()}"
    slug = SLUG.get(model, model)
    t0 = start
    subruns, rights = [], {}
    for i, c in enumerate(TRIPLET_CASES):
        t1 = t0 + timedelta(seconds=i)
        prompt = ca.expected_prompt(c["id"], arm)  # t5 and t6 too: the sealed prompt
        if prompt_edit:
            prompt = prompt_edit(prompt)
        contents = [{"parts": [{"text": prompt}], "role": "CONTENT_ROLE_USER", "senderName": "User"}]
        sub = {"taskVersion": {"versionNumber": 1, "name": child}, "modelVersion": {"slug": slug},
               "startTime": _stamp(t1), "endTime": _stamp(t1 + timedelta(milliseconds=900)), "pyRunId": f"{child}-Run #{i + 1}"}
        if c["id"] in errored or c["id"] not in replies:
            sub["state"] = "BENCHMARK_TASK_RUN_STATE_ERRORED"
            sub["conversations"] = [{"id": f"{child}-{i}", "requests": [{"contents": contents}]}]
            subruns.append(sub)
            rights[c["id"]] = False
            continue
        contents.append({"parts": [{"text": replies[c["id"]]}], "role": "CONTENT_ROLE_ASSISTANT", "senderName": slug})
        right = coat_item_right(c["kind"], read_reply(c, replies[c["id"]]))
        rights[c["id"]] = right
        shown_right = (not right) if c["id"] in flip else right
        metrics = {"inputTokens": 300, "outputTokens": 100, "inputTokensCostNanodollars": str(cost_per_call_nd // 2),
                   "outputTokensCostNanodollars": str(cost_per_call_nd - cost_per_call_nd // 2), "totalBackendLatencyMs": "900"}
        sub["state"] = "BENCHMARK_TASK_RUN_STATE_COMPLETED"
        sub["conversations"] = [{"id": f"{child}-{i}", "requests": [{"contents": contents, "metrics": metrics, "id": f"{child}-{i}-req-1"}],
                                 "metrics": metrics}]
        sub["results"] = [{"type": "AGGREGATED", "numericResult": ({"value": 1.0} if shown_right else {})}]
        subruns.append(sub)
    receipt = receipt_score(TRIPLET_CASES, rights)
    value = receipt if run_value is None else run_value
    return {"taskVersion": {"versionNumber": 1, "name": task}, "modelVersion": {"slug": slug},
            "state": "BENCHMARK_TASK_RUN_STATE_COMPLETED", "startTime": _stamp(t0),
            "endTime": _stamp(t0 + timedelta(seconds=len(TRIPLET_CASES) + 1)),
            "conversations": [{"id": f"{task}-0", "metrics": {}}],
            "results": [{"type": "AGGREGATED", "numericResult": ({"value": value} if value else {})}],
            "subruns": subruns, "pyRunId": f"{task}-Run #1"}


def write_fake_run(results, arm, model, answerer="perfect", start=None, run_id=None, **kw):
    """Write one run file and return its path. `answerer` is a name of blindcheck_dryrun.COAT_CONTROLS or a function."""
    fn = dr.COAT_CONTROLS[answerer] if isinstance(answerer, str) else answerer
    start = start or datetime(2026, 10, 8, 9, 0, 0, tzinfo=timezone.utc)
    replies = {c["id"]: fn(c) for c in TRIPLET_CASES}
    run = fake_run_json(arm, model, replies, start, **kw)
    task = ca.TASK[arm]
    run_id = run_id or str(int(start.timestamp()))[-7:]
    folder = Path(results) / task / "1" / model / run_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{task}-run_id_Run_1_{SLUG.get(model, model).replace('/', '_').replace('@', '')}.run.json"
    path.write_text(json.dumps(run, indent=1), encoding="utf-8", newline="\n")
    return path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("write")
    w.add_argument("results")
    w.add_argument("task")
    w.add_argument("model")
    w.add_argument("--answerer", default="perfect", choices=sorted(dr.COAT_CONTROLS))
    w.add_argument("--start", default=None, help="ISO time of the run's start (default 2026-10-08T09:00:00Z)")
    w.add_argument("--errored", type=int, default=0, help="how many of the first logs get no reply")
    w.add_argument("--run-id", default=None, help="name of the run's folder (default: from the start time)")
    w.add_argument("--cost", type=int, default=1_000_000, help="recorded cost of one call, in nanodollars")
    a = ap.parse_args(argv)
    arm = next(k for k, v in ca.TASK.items() if v == a.task)
    start = datetime.fromisoformat(a.start.replace("Z", "+00:00")) if a.start else None
    errored = {c["id"] for c in TRIPLET_CASES[:a.errored]}
    print(write_fake_run(a.results, arm, a.model, a.answerer, start=start, errored=errored, run_id=a.run_id,
                         cost_per_call_nd=a.cost))
    return 0


if __name__ == "__main__":
    sys.exit(main())
