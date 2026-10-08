"""Runner for Spec S12: Forced yes-or-no on nine models.

Standard library only.
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
import re
import sys
import threading
import time
import urllib.error
import urllib.request

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
SPEC = "s12"
REQUESTS_FILE = BASE_DIR / "inputs" / "s12-requests.jsonl"
FRAMINGS_FILE = BASE_DIR / "inputs" / "s12-framings.json"
RUNS_DIR = BASE_DIR / "runs" / SPEC
ORDER_FILE = RUNS_DIR / "order.json"
CALLS_FILE = RUNS_DIR / "calls.jsonl"
CODE_DIR = RUNS_DIR / "code"
MANIFEST_FILE = RUNS_DIR / "MANIFEST.sha256"

MODELS = [
    "qwen/qwen3.5-9b",
    "google/gemma-4-26b-a4b-it",
    "deepseek/deepseek-v4.1-flash",
    "moonshotai/kimi-k3",
    "openai/gpt-6.1-sol",
    "google/gemini-3.8-flash",
    "x-ai/grok-4.7",
    "z-ai/glm-5.3",
    "anthropic/claude-opus-5.5",
]

REASONING_MODELS = {
    "openai/gpt-6.1-sol",
    "google/gemini-3.8-flash",
    "x-ai/grok-4.7",
    "z-ai/glm-5.3",
    "anthropic/claude-opus-5.5",
}

ARMS = ["forced", "allowed"]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_CONCURRENT_CALLS = 4
MAX_RETRIES = 4
RETRY_DELAY = 30.0
SEED = 20261006
MAX_COST_S12 = 4.00
MAX_NO_ANSWER_RATE = 0.05


def load_requests() -> list[dict]:
    items = []
    with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_framings() -> dict[str, str]:
    with open(FRAMINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_request_body(model: str, system_prompt: str, user_message: str) -> dict:
    if model in REASONING_MODELS:
        return {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0,
            "seed": 42,
            "max_tokens": 4000,
            "reasoning": {"effort": "low"},
            "provider": {"data_collection": "deny"},
        }
    else:
        return {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0,
            "seed": 42,
            "max_tokens": 2000,
            "reasoning": {"enabled": False},
            "provider": {"data_collection": "deny"},
        }


def parse_reply(reply_text: str) -> tuple[dict | None, str | None]:
    if not isinstance(reply_text, str) or not reply_text.strip():
        return None, None

    candidate = reply_text.strip()
    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", candidate, re.S)
    if fence:
        candidate = fence.group(1).strip()

    parsed = None
    try:
        parsed = json.loads(candidate)
    except Exception:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(candidate[start:end + 1])
            except Exception:
                parsed = None

    if not isinstance(parsed, dict):
        return None, None

    raw_verdict = parsed.get("verdict")
    verdict = None
    if isinstance(raw_verdict, str):
        v = raw_verdict.strip().lower()
        if v in ("shown", "contradicted", "not_shown"):
            verdict = v

    return parsed, verdict


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


def build_plan(requests: list[dict]) -> list[dict]:
    base_calls = []
    for req in requests:
        req_id = req["id"]
        for arm in ARMS:
            for model in MODELS:
                base_calls.append({
                    "spec": SPEC,
                    "arm": arm,
                    "item_id": req_id,
                    "model": model,
                    "repeat": 0,
                })

    rng = random.Random(SEED)
    rng.shuffle(base_calls)

    for i, c in enumerate(base_calls):
        c["call_index"] = i

    return base_calls


def main():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    CODE_DIR.mkdir(parents=True, exist_ok=True)

    requests = load_requests()
    req_map = {r["id"]: r["user"] for r in requests}
    framings = load_framings()

    all_calls = build_plan(requests)
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        json.dump(all_calls, f, indent=2)
    print(f"Order written to {ORDER_FILE}")

    existing_calls = set()
    total_cost = 0.0
    no_answer_count = 0
    if CALLS_FILE.exists():
        with open(CALLS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    existing_calls.add((rec["item_id"], rec["arm"], rec["model"]))
                    if not rec.get("answered", False):
                        no_answer_count += 1
                    resp = rec.get("response") or {}
                    usage = resp.get("usage") or {}
                    c = usage.get("cost") or 0.0
                    total_cost += c

    pending_calls = [
        c for c in all_calls
        if (c["item_id"], c["arm"], c["model"]) not in existing_calls
    ]
    print(f"Pending calls for S12: {len(pending_calls)} out of {len(all_calls)}")

    if not pending_calls:
        print("All calls already completed. Writing manifest.")
        write_manifest()
        return

    write_lock = threading.Lock()
    stop_event = threading.Event()
    completed_count = len(existing_calls)

    calls_handle = open(CALLS_FILE, "a", encoding="utf-8")

    def worker(call_info: dict) -> None:
        nonlocal total_cost, no_answer_count, completed_count
        if stop_event.is_set():
            return

        item_id = call_info["item_id"]
        arm = call_info["arm"]
        model = call_info["model"]

        system_prompt = framings[arm]
        user_message = req_map[item_id]

        req_body = build_request_body(model, system_prompt, user_message)
        resp, status, err, started, finished = make_call(req_body, api_key)

        reply_text = ""
        cost = None
        if resp:
            choices = resp.get("choices") or [{}]
            finish_reason = choices[0].get("finish_reason")
            if finish_reason == "length":
                err = "token limit cut off (finish_reason: length)"
            else:
                reply_text = choices[0].get("message", {}).get("content") or ""
            usage = resp.get("usage") or {}
            cost = usage.get("cost")

        parsed_json, verdict = parse_reply(reply_text)
        answered = bool(resp is not None and reply_text and verdict is not None)

        record = {
            "spec": SPEC,
            "arm": arm,
            "item_id": item_id,
            "model": model,
            "repeat": 0,
            "call_index": call_info["call_index"],
            "request": req_body,
            "response": resp,
            "started_utc": started,
            "finished_utc": finished,
            "http_status": status,
            "error": err,
            "raw_reply": reply_text,
            "parsed": parsed_json,
            "verdict": verdict,
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
                if total_cost >= MAX_COST_S12:
                    print(f"STOP: Spend for S12 reached US${MAX_COST_S12:.2f} (current: ${total_cost:.4f}).", file=sys.stderr)
                    stop_event.set()

            if completed_count % 50 == 0 or completed_count == len(all_calls):
                print(f"Progress S12: {completed_count}/{len(all_calls)} calls completed (spend: ${total_cost:.4f}, no-answer: {no_answer_count}).", flush=True)

    print(f"Starting S12 execution (max {MAX_CONCURRENT_CALLS} concurrent)...")
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
    print("Writing MANIFEST.sha256...")
    write_manifest()
    print("S12 run complete.")


if __name__ == "__main__":
    main()
