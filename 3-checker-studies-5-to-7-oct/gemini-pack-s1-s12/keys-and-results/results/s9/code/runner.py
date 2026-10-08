"""Runner for Spec S9: The wobble test (temperature testing).

Standard library only (+ vendor/receipt_pair).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import threading
import time
import urllib.error
import urllib.request

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
VENDOR_DIR = BASE_DIR / "vendor"
if str(VENDOR_DIR) not in sys.path:
    sys.path.insert(0, str(VENDOR_DIR))

import receipt_pair.pair
import receipt_pair.reader

SPEC = "s9"
ITEMS_FILE = BASE_DIR / "inputs" / "s8-items.jsonl"
RUNS_DIR = BASE_DIR / "runs" / SPEC
ORDER_FILE = RUNS_DIR / "order.json"
CALLS_FILE = RUNS_DIR / "calls.jsonl"
CODE_DIR = RUNS_DIR / "code"
MANIFEST_FILE = RUNS_DIR / "MANIFEST.sha256"

MODELS = [
    "qwen/qwen3.5-9b",
    "google/gemma-4-26b-a4b-it",
]

ARMS_SPECS = [
    {"arm": "W0", "seed": 42, "temperature": 0.0},
    {"arm": "W5", "seed": 101, "temperature": 0.7},
    {"arm": "W5", "seed": 102, "temperature": 0.7},
    {"arm": "W5", "seed": 103, "temperature": 0.7},
    {"arm": "W5", "seed": 104, "temperature": 0.7},
    {"arm": "W5", "seed": 105, "temperature": 0.7},
]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_CONCURRENT_CALLS = 4
MAX_RETRIES = 4
RETRY_DELAY = 30.0
SEED = 20261006
MAX_COST_S9 = 2.00
MAX_NO_ANSWER_RATE = 0.05


def load_items() -> list[dict]:
    items = []
    with open(ITEMS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def serialize_outcome(outcome) -> dict | None:
    if outcome is None:
        return None
    if isinstance(outcome, dict):
        return outcome
    return {
        "answer": getattr(outcome, "answer", None),
        "code": getattr(outcome, "code", None),
        "verdict": getattr(outcome, "verdict", None),
        "quote": getattr(outcome, "quote", None),
        "turn": outcome.turn.label if hasattr(outcome, "turn") and outcome.turn is not None and hasattr(outcome.turn, "label") else (outcome.turn if hasattr(outcome, "turn") else None),
        "reason": getattr(outcome, "reason", None),
        "detail": getattr(outcome, "detail", None),
        "markers": list(outcome.markers) if hasattr(outcome, "markers") else [],
    }


def build_request_body(model: str, system: str, user: str, temperature: float, seed: int) -> dict:
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "seed": seed,
        "max_tokens": 400,
        "reasoning": {"enabled": False},
        "provider": {"data_collection": "deny"},
    }


def make_call(req_body: dict, api_key: str) -> tuple[dict | None, int | None, str | None, str, str]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = json.dumps(req_body).encode("utf-8")

    attempts = 0
    last_error = None
    response_body = None
    http_status = None
    started_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    finished_utc = None

    while attempts <= MAX_RETRIES:
        attempts += 1
        req = urllib.request.Request(OPENROUTER_URL, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                http_status = resp.status
                resp_bytes = resp.read()
                finished_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
                response_body = json.loads(resp_bytes.decode("utf-8"))
                break
        except urllib.error.HTTPError as e:
            http_status = e.code
            finished_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
            try:
                err_text = e.read().decode("utf-8", "replace")
            except Exception:
                err_text = ""
            last_error = f"HTTP {e.code}: {err_text[:200]}"
            if attempts <= MAX_RETRIES:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            finished_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
            last_error = f"{type(e).__name__}: {str(e)[:200]}"
            if attempts <= MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    if finished_utc is None:
        finished_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return response_body, http_status, last_error, started_utc, finished_utc


def write_manifest() -> None:
    files_to_hash = []
    if CALLS_FILE.exists():
        files_to_hash.append(CALLS_FILE)
    if ORDER_FILE.exists():
        files_to_hash.append(ORDER_FILE)
    if CODE_DIR.exists():
        for p in sorted(CODE_DIR.rglob("*")):
            if p.is_file() and p.name != "MANIFEST.sha256":
                files_to_hash.append(p)

    lines = []
    for p in files_to_hash:
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        rel = p.relative_to(RUNS_DIR)
        lines.append(f"{h} *{rel}\n")

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def build_plan(items: list[dict]) -> tuple[list[dict], dict[str, tuple]]:
    prepared = {}
    base_calls = []
    for item in items:
        item_id = item["id"]
        variant = item.get("variant", "")
        shown, req = receipt_pair.pair.prepare(item_id, item["claim"], item["turns"])
        prepared[item_id] = (shown, req)
        for model in MODELS:
            for arm_spec in ARMS_SPECS:
                base_calls.append({
                    "spec": SPEC,
                    "arm": arm_spec["arm"],
                    "seed": arm_spec["seed"],
                    "temperature": arm_spec["temperature"],
                    "item_id": item_id,
                    "variant": variant,
                    "model": model,
                    "repeat": 0,
                })

    rng = random.Random(SEED)
    rng.shuffle(base_calls)

    for i, call in enumerate(base_calls):
        call["call_index"] = i

    return base_calls, prepared


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    CODE_DIR.mkdir(parents=True, exist_ok=True)

    items = load_items()
    all_calls, prepared = build_plan(items)

    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        json.dump(all_calls, f, indent=2)
    print(f"Prepared {len(all_calls)} calls for S9.")
    print(f"Order written to {ORDER_FILE}")

    existing_calls = set()
    initial_spend = 0.0
    no_answer_count = 0
    if CALLS_FILE.exists():
        with open(CALLS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    call_key = (rec["item_id"], rec["model"], rec["arm"], rec["seed"])
                    existing_calls.add(call_key)
                    if not rec.get("answered", False):
                        no_answer_count += 1
                    if "response" in rec and rec["response"]:
                        usage = rec["response"].get("usage")
                        if usage:
                            c = usage.get("cost")
                            if c:
                                initial_spend += c

    print(f"Found {len(existing_calls)} existing calls (spend: ${initial_spend:.4f}).")

    if len(existing_calls) >= len(all_calls):
        print("All calls already completed. Writing manifest.")
        write_manifest()
        return

    pending_calls = [
        c for c in all_calls
        if (c["item_id"], c["model"], c["arm"], c["seed"]) not in existing_calls
    ]
    print(f"Pending calls to execute: {len(pending_calls)}")

    total_cost = initial_spend
    completed_count = len(existing_calls)
    write_lock = threading.Lock()
    stop_event = threading.Event()

    calls_handle = open(CALLS_FILE, "a", encoding="utf-8")

    def worker(call_info: dict) -> None:
        nonlocal total_cost, no_answer_count, completed_count
        if stop_event.is_set():
            return

        item_id = call_info["item_id"]
        model = call_info["model"]
        arm = call_info["arm"]
        seed = call_info["seed"]
        temp = call_info["temperature"]

        shown, req = prepared[item_id]
        req_body = build_request_body(model, req.system, req.user, temp, seed)

        resp, status, err, started, finished = make_call(req_body, api_key)

        reply_text = ""
        cost = None
        if resp:
            try:
                reply_text = resp["choices"][0]["message"].get("content") or ""
            except Exception:
                reply_text = ""
            usage = resp.get("usage")
            if usage:
                cost = usage.get("cost")

        outcome = None
        verified = None
        answered = False
        if resp is not None and reply_text:
            try:
                outcome = receipt_pair.reader.verify(reply_text, shown)
                verified = serialize_outcome(outcome)
                if outcome and outcome.answer != "no answer":
                    answered = True
            except Exception as e:
                verified = {"answer": "no answer", "code": "exception", "detail": str(e)}
                answered = False
        elif resp is not None:
            # Empty reply text
            verified = {"answer": "no answer", "code": "empty_reply", "detail": "Empty reply content"}
            answered = False
        else:
            answered = False

        record = {
            "spec": SPEC,
            "arm": arm,
            "seed": seed,
            "temperature": temp,
            "item_id": item_id,
            "variant": call_info.get("variant", ""),
            "model": model,
            "repeat": call_info.get("repeat", 0),
            "call_index": call_info["call_index"],
            "request": req_body,
            "response": resp,
            "started_utc": started,
            "finished_utc": finished,
            "http_status": status,
            "error": err,
            "verified": verified,
            "answered": answered,
        }

        with write_lock:
            calls_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            calls_handle.flush()
            completed_count += 1

            if not answered:
                no_answer_count += 1
                if no_answer_count / len(all_calls) > MAX_NO_ANSWER_RATE:
                    print(f"STOP: No-answer rate exceeded 5% ({no_answer_count}/{len(all_calls)}).", file=sys.stderr)
                    stop_event.set()

            if cost and cost > 0:
                total_cost += cost
                if total_cost >= MAX_COST_S9:
                    print(f"STOP: Spend for S9 reached US${MAX_COST_S9:.2f} (current: ${total_cost:.4f}).", file=sys.stderr)
                    stop_event.set()

            if completed_count % 100 == 0 or completed_count == len(all_calls):
                print(f"Progress S9: {completed_count}/{len(all_calls)} calls completed (spend: ${total_cost:.4f}, no-answer: {no_answer_count}).", flush=True)

    print(f"Starting S9 execution (max {MAX_CONCURRENT_CALLS} concurrent)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_CALLS) as executor:
        futures = [executor.submit(worker, c) for c in pending_calls]
        for f in concurrent.futures.as_completed(futures):
            if stop_event.is_set():
                executor.shutdown(wait=False, cancel_futures=True)
                break
            try:
                f.result()
            except Exception as e:
                print(f"Worker exception: {e}", file=sys.stderr)

    calls_handle.close()
    print("Execution finished. Writing MANIFEST.sha256...")
    write_manifest()
    print("S9 run complete.")


if __name__ == "__main__":
    main()
