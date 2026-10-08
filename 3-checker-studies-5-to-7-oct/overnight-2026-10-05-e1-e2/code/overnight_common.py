"""Shared helpers for the two overnight experiments (5-6 Oct 2026). Nothing here prints item text.

  - paths, the clock, hashing, JSON Lines
  - run 1's runner (run_pair) and run 2's measures (run2), imported unchanged
  - the PAUSE file: every call to the Lemonade server (and every hosted call) waits while
    C:\\Users\\joshd\\Workbench\\overnight-2026-10-05\\PAUSE exists, sleeping in 30-second steps
  - a few extra tries for a local call that fails (the design says so)
"""
import hashlib, json, os, sys, time, datetime
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"   # never write .pyc files into other people's folders
sys.dont_write_bytecode = True

ROOT = Path(r"C:\Users\joshd\Workbench\overnight-2026-10-05")
LEMON = Path(r"C:\Users\joshd\Workbench\lemonade-entry-2026-10-05")
REPL = Path(r"C:\Users\joshd\Workbench\replication-2026-10-05")
BROKER = Path(r"C:\Users\joshd\Desktop\Moonshots\ai-broker")
PAUSE = ROOT / "PAUSE"
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

sys.path.insert(0, str(LEMON))
sys.path.insert(0, str(LEMON / "run2"))
import run_pair as rp          # noqa: E402  run 1's runner: Lemonade calls, frozen reader (rp.v3), the pair rule
import run2 as r2              # noqa: E402  run 2's measures, Wilson intervals, rules R2 and R3
v3 = rp.v3

LABELS = ("shown", "contradicted", "not shown")


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(path, msg):
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{utc_now()} {msg}\n")


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sha256_text(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def read_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def write_jsonl(p, rows):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def norm(t):
    return "not shown" if t == "not_shown" else t


# ---------------------------------------------------------------- the PAUSE file
def wait_if_paused(who="run"):
    """Block while the PAUSE file exists; sleep in 30-second steps. Called before every model call."""
    if not PAUSE.exists():
        return 0
    t0 = time.time()
    log(LOGS / "pause-log.txt", f"{who}: PAUSE file found; waiting in 30-second steps")
    print(f"[{utc_now()}] PAUSE file found; waiting", flush=True)
    while PAUSE.exists():
        time.sleep(30)
    waited = int(time.time() - t0)
    log(LOGS / "pause-log.txt", f"{who}: PAUSE file gone after {waited} s; continuing")
    print(f"[{utc_now()}] PAUSE gone after {waited} s; continuing", flush=True)
    return waited


def install_local_patches(who="run"):
    """Make run_pair's server calls pause-aware, and give a failed local call more tries (30 s apart)."""
    orig_http, orig_ask = rp.http, rp.ask
    if getattr(rp, "_overnight_patched", False):
        return

    def paused_http(method, url, body=None, timeout=600):
        wait_if_paused(who)
        return orig_http(method, url, body, timeout)

    def ask_with_tries(model, request):
        text = err = seconds = stats = None
        waited_for_server = False
        for round_no in (1, 2):
            for attempt in range(1, 5):          # run_pair.ask already retries once inside each of these
                wait_if_paused(who)
                text, err, seconds, stats = orig_ask(model, request)
                if err is None:
                    return text, err, seconds, stats
                log(LOGS / "local-errors.txt", f"{who}: {model['arm']} call failed ({err}), try {attempt} of 4, round {round_no}")
                time.sleep(30)
            if round_no == 2:
                break
            # Four tries failed. If the server itself is gone, wait for it (up to an hour) and try once more in a second round.
            for _ in range(60):
                try:
                    orig_http("GET", rp.LEMONADE + "/health", None, 30)
                    break
                except Exception:
                    waited_for_server = True
                    log(LOGS / "local-errors.txt", f"{who}: the Lemonade server does not answer; waiting 60 s")
                    wait_if_paused(who)
                    time.sleep(60)
            if not waited_for_server:
                break                             # the server is up and this one request keeps failing: record it as no answer
        return text, err, seconds, stats

    rp.http, rp.ask = paused_http, ask_with_tries
    rp._overnight_patched = True


# ---------------------------------------------------------------- the two local arms
def local_arms():
    """Arms A (Qwen3-4B-Instruct-2507-GGUF) and B (Gemma-4-E4B-it-GGUF), exactly as run 2's local lane."""
    return [dict(m) for m in rp.MODELS if m["arm"] in ("A", "B")]


# ---------------------------------------------------------------- hosted spend, from the broker's ledger
def ledger_spend(prefix="overnight-", since="2026-10-05"):
    """Sum providerReportedCostUsd over every ledger run whose lane starts with `prefix` (authoritative spend)."""
    total, n, missing = 0.0, 0, 0
    for day in (BROKER / "ledger").glob("20*"):
        if not day.is_dir() or day.name < since:
            continue
        for run in day.iterdir():
            rj = run / "run.json"
            if not rj.exists():
                continue
            try:
                j = json.loads(rj.read_text(encoding="utf-8"))
            except Exception:
                continue
            if str(j.get("lane", "")).startswith(prefix):
                n += 1
                c = j.get("providerReportedCostUsd")
                if c is None:
                    missing += 1
                else:
                    total += c
    return {"usd": round(total, 6), "runs": n, "runs_without_cost": missing}


# ---------------------------------------------------------------- seals
def sealed_ok(seal_file, name):
    """The file `name` (beside `seal_file`) must equal the hash listed in `seal_file`, and a FreeTSA reply must exist for the seal file."""
    seal_file = Path(seal_file)
    tsr = Path(str(seal_file) + ".tsr")
    if not seal_file.exists() or not tsr.exists() or tsr.stat().st_size < 100:
        return False
    for line in seal_file.read_text(encoding="utf-8").splitlines():
        h, _, f = line.partition(" *")
        if f.strip() == name:
            return h == sha256_file(seal_file.parent / name)
    return False


def design_seal_ok(label):
    """E1-DESIGN-SHA256.txt / E2-DESIGN-SHA256.txt: every file it lists must still have its sealed hash, and the FreeTSA reply must exist."""
    seal = ROOT / f"{label}-DESIGN-SHA256.txt"
    tsr = Path(str(seal) + ".tsr")
    if not seal.exists() or not tsr.exists() or tsr.stat().st_size < 100:
        return False, "no sealed design (hash line + FreeTSA reply)"
    for line in seal.read_text(encoding="utf-8").splitlines():
        h, _, f = line.partition(" *")
        if sha256_file(ROOT / f.strip()) != h:
            return False, f"{f.strip()} changed after the design was sealed"
    return True, "ok"
