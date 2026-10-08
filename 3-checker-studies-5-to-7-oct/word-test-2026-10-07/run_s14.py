"""S14, the word test: does swapping "can't" for "cannot", and nothing else, change a model's verdicts?

Design: DESIGN.md (sealed before any model call). Items: S12's 54 records (27 missing their deciding evidence, 27 intact),
whose key stays on the PC. Four instruction texts, built here from S12's two framings by one exact replacement each, so the
"cannot" and "can't" texts differ in that one word and nothing else (check mode proves it). Models: the local pair on Lemonade,
Qwen3-4B-Instruct-2507 and Gemma-4-E4B (thinking off), temperature 0, seed 42, max_tokens 400 (the gate test's settings and client,
vendored from receipt_pair at b7dfbad).

    python run_s14.py check   inputs, framings and the parser (no model calls)
    python run_s14.py dry     the whole plan against a stub server, written to dry/ (no model calls)
    python run_s14.py run     the sealed run: resumable, honours the PAUSE file, refuses to start while the gate test runs
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
from receipt_pair.client import GEMMA, QWEN, LemonadeClient  # noqa: E402  (vendored from b7dfbad, as in the gate test)

REQUESTS = HERE / "inputs" / "s12-requests.jsonl"
FRAMINGS = HERE / "inputs" / "s12-framings.json"
REQUESTS_SHA256 = "928a3b713559f01945067cb05fa7892f81fec1b83332f8a4df8049944b5e9609"
FRAMINGS_SHA256 = "4a6be62b38dafe1bea99cae71091dfb7d1c5f33a385cc6959b1e694ba427b2a0"
PAUSE = Path("C:/Users/joshd/Workbench/overnight-2026-10-05/PAUSE")
GATE_CONSOLE = Path("C:/Users/joshd/Workbench/gate-test-2026-10-07/results/run-console.txt")
MODELS = {"qwen": QWEN, "gemma": GEMMA}
VERDICTS = ("shown", "contradicted", "not_shown")
REPEAT_SHARE = 11  # records drawn with seed 14 for a full repeat of all four texts: the determinism check

# One exact replacement per text. The "cannot" and "can't" texts differ only in that word.
FORCED_OLD = '5. Answer only "shown" or "contradicted". "not_shown" is not an allowed answer.'
FORCED_NEW = '5. Answer only "shown" or "contradicted". You {W} answer "not_shown".'
ALLOWED_OLD = '5. For "not_shown": turn_id is null and quote is "".'
ALLOWED_NEW = '5. For "not_shown": turn_id is null and quote is "". You {W} answer "shown" or "contradicted" without a quoted OUTPUT line.'
WORDS = {"cannot": "cannot", "cant": "can't"}
VARIANTS = ("forced_cannot", "forced_cant", "allowed_cannot", "allowed_cant")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_inputs():
    if sha256_bytes(REQUESTS.read_bytes()) != REQUESTS_SHA256 or sha256_bytes(FRAMINGS.read_bytes()) != FRAMINGS_SHA256:
        raise SystemExit("inputs do not match their sealed fingerprints")
    records = [json.loads(line) for line in REQUESTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    framings = json.loads(FRAMINGS.read_text(encoding="utf-8"))
    return records, framings


def build_texts(framings: dict) -> dict:
    assert framings["forced"].count(FORCED_OLD) == 1 and framings["allowed"].count(ALLOWED_OLD) == 1
    texts = {}
    for key, word in WORDS.items():
        texts[f"forced_{key}"] = framings["forced"].replace(FORCED_OLD, FORCED_NEW.format(W=word))
        texts[f"allowed_{key}"] = framings["allowed"].replace(ALLOWED_OLD, ALLOWED_NEW.format(W=word))
    return texts


def parse_verdict(text):
    """A real JSON parse, robust to braces inside strings (the S13 lesson): first the text from the first "{" to the last "}"
    (S12's rule); if that fails, the last complete JSON object found by decoding from each "{". Returns (verdict, quote)."""
    if not isinstance(text, str) or not text.strip():
        return None, None
    t = text.strip()
    candidates = []
    m = re.search(r"\{.*\}", t, re.S)
    if m:
        try:
            candidates.append(json.loads(m.group(0)))
        except Exception:
            pass
    if not candidates:
        dec = json.JSONDecoder()
        for i, ch in enumerate(t):
            if ch == "{":
                try:
                    obj, _ = dec.raw_decode(t[i:])
                    candidates.append(obj)
                except Exception:
                    continue
    for obj in reversed(candidates):
        if isinstance(obj, dict) and isinstance(obj.get("verdict"), str):
            v = obj["verdict"].strip().lower().replace(" ", "_")
            if v in VERDICTS:
                return v, obj.get("quote")
    return None, None


PARSER_CASES = [
    ('{"reason": "r", "turn_id": "T2", "quote": "{\\"commit\\":\\"b71e4c9\\",\\"state\\":\\"success\\"}", "verdict": "shown"}', "shown"),
    ('{"reason": "r", "turn_id": "T1", "quote": "{\\"pr\\":218,\\"verdict\\":\\"ACCEPT\\"}", "verdict": "contradicted"}', "contradicted"),
    ('```json\n{"reason": "r", "turn_id": null, "quote": "", "verdict": "not_shown"}\n```', "not_shown"),
    ('Here you go: {"reason": "r", "turn_id": null, "quote": "", "verdict": "Not Shown"}', "not_shown"),
    ('{"reason": "No turns were provided.", "turn_id": null, "quote": null, "verdict": null}', None),
    ('no json at all', None),
    ('{"verdict": "maybe"}', None),
]


def order(records: list) -> list:
    """Model by model (Qwen, then Gemma); records in file order; the two words alternate which goes first, record by record;
    then the repeat block: REPEAT_SHARE records drawn with seed 14, all four texts again."""
    plan = []
    rng = random.Random(14)
    repeat_ids = sorted(rng.sample([r["id"] for r in records], REPEAT_SHARE))
    for m in MODELS:
        for n, r in enumerate(records):
            pair_f = ("forced_cannot", "forced_cant") if n % 2 == 0 else ("forced_cant", "forced_cannot")
            pair_a = ("allowed_cannot", "allowed_cant") if n % 2 == 0 else ("allowed_cant", "allowed_cannot")
            for v in pair_f + pair_a:
                plan.append({"model_key": m, "id": r["id"], "variant": v, "repeat": 0})
        for rid in repeat_ids:
            for v in VARIANTS:
                plan.append({"model_key": m, "id": rid, "variant": v, "repeat": 1})
    return plan


def check() -> int:
    records, framings = load_inputs()
    texts = build_texts(framings)
    for kind in ("forced", "allowed"):
        a, b = texts[f"{kind}_cannot"], texts[f"{kind}_cant"]
        assert a.replace("cannot", "can't", 1) == b and a.count("cannot") == 1 and b.count("can't") == 1, kind
        assert "cannot" not in b and "can't" not in a, kind
    for text, want in PARSER_CASES:
        got, _ = parse_verdict(text)
        assert got == want, (text, got, want)
    plan = order(records)
    assert len(plan) == 2 * (54 * 4 + REPEAT_SHARE * 4), len(plan)
    assert len({(p["model_key"], p["id"], p["variant"], p["repeat"]) for p in plan}) == len(plan)
    print(f"check ok: 54 records, 4 texts differing only in the word, parser passes {len(PARSER_CASES)} cases, {len(plan)} calls planned")
    for v in VARIANTS:
        print(f"  {v}: sha256 {sha256_bytes(texts[v].encode('utf-8'))}")
    return 0


def done_keys(path: Path) -> set:
    if not path.exists():
        return set()
    return {(r["model_key"], r["id"], r["variant"], r["repeat"]) for r in
            (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())}


def run(out_dir: Path, client: LemonadeClient, guard: bool = True) -> int:
    if guard:
        console = GATE_CONSOLE.read_text(encoding="utf-8") if GATE_CONSOLE.exists() else ""
        if "ended " not in console:
            raise SystemExit("the gate test has not ended; one Lemonade user at a time")
    records, framings = load_inputs()
    texts = build_texts(framings)
    users = {r["id"]: r["user"] for r in records}
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "calls.jsonl"
    done = done_keys(out)
    plan = order(records)
    loaded = None
    for i, step in enumerate(plan, 1):
        key = (step["model_key"], step["id"], step["variant"], step["repeat"])
        if key in done:
            continue
        while PAUSE.exists():
            print("PAUSE file found; waiting 30 s", flush=True)
            time.sleep(30)
        if loaded != step["model_key"]:
            client.make_only_loaded(MODELS[step["model_key"]].id)
            loaded = step["model_key"]
        system, user = texts[step["variant"]], users[step["id"]]
        started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        chat = client.chat(MODELS[step["model_key"]], system, user)
        verdict, quote = parse_verdict(chat.text)
        row = {**step, "model": MODELS[step["model_key"]].id, "started": started, "seconds": chat.seconds,
               "system_sha256": sha256_bytes(system.encode("utf-8")), "user_sha256": sha256_bytes(user.encode("utf-8")),
               "request": client.request_body(MODELS[step["model_key"]], "<system: see system_sha256>", "<user: see user_sha256>"),
               "reply": chat.text, "error": chat.error, "verdict": verdict, "quote": quote}
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"{started} [{i}/{len(plan)}] {step['model_key']} {step['id']} {step['variant']} r{step['repeat']}: "
              f"{verdict or ('error' if chat.error else 'no verdict')} ({chat.seconds:.1f} s)", flush=True)
    print("finished", flush=True)
    return 0


class Stub:
    """A stand-in for Lemonade in dry mode: answers in shapes the real models use, including a quote that holds JSON."""

    def __init__(self):
        self.loaded = None
        self.n = 0

    def __call__(self, method, url, body=None, timeout=600):
        if url.endswith("/health"):
            return {"model_loaded": self.loaded}
        if url.endswith("/unload"):
            self.loaded = None
            return {}
        if url.endswith("/load"):
            self.loaded = (body or {}).get("model_name") or (body or {}).get("model")
            return {}
        if url.endswith("/stats"):
            return {"tokens_per_second": 0}
        if url.endswith("/chat/completions"):
            self.loaded = body["model"]
            self.n += 1
            reply = PARSER_CASES[self.n % 4][0]
            return {"choices": [{"message": {"content": reply}}]}
        return {}


def main(argv) -> int:
    mode = argv[1] if len(argv) > 1 else "check"
    if mode == "check":
        return check()
    if mode == "dry":
        check()
        dry = HERE / "dry"
        if (dry / "calls.jsonl").exists():
            (dry / "calls.jsonl").unlink()
        run(dry, LemonadeClient(transport=Stub()), guard=False)
        rows = [json.loads(l) for l in (dry / "calls.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
        print(f"dry ok: {len(rows)} rows; verdicts {sorted({str(r['verdict']) for r in rows})}")
        return 0
    if mode == "run":
        return run(HERE / "results", LemonadeClient())
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
