"""E1 item writing. The writer is deepseek/deepseek-v4.1-flash, reached only through the AI broker (provider "openrouter").
Items are asked for slot by slot (e1-schedule.json), checked by script (e1_validate.py), and kept or dropped by name.
  python e1_generate.py run          write items until every slot is filled, or the spend cap or the try limit is reached
  python e1_generate.py status       counts only
  python e1_generate.py assemble     number the kept items X001.. in slot order and write items-X001-X150.jsonl and slot-map.json
Nothing here prints item text: only slot ids, codes and counts.
"""
import concurrent.futures as cf, json, re, subprocess, sys, tempfile, time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc  # noqa: E402
import e1_validate as val      # noqa: E402
import e1_schedule as sch      # noqa: E402

E1 = oc.ROOT / "e1"
MODEL = "deepseek/deepseek-v4.1-flash"
LANE = "overnight-e1"
CAP_USD = 0.50                 # the whole overnight hosted budget (plumbing test included)
WORST_CALL_USD = 0.0035        # 4000 output tokens at about US$0.65 per million, plus the input
WORKERS = 3
MAX_ATTEMPTS = 4
BATCH_BY_ATTEMPT = {0: 2, 1: 1, 2: 1, 3: 1}   # a slot's first request goes two slots to a call; a retried slot goes alone
MAX_TRANSPORT_FAILURES = 8

ACCEPTED, DROPS, CALLS = E1 / "drafts-accepted.jsonl", E1 / "e1-drops.jsonl", E1 / "e1-calls.jsonl"
SPAWNED = E1 / "e1-spawned-reserves.json"
GENLOG = oc.LOGS / "e1-generate-log.txt"

SPEC = (HERE / "e1-spec.txt").read_text(encoding="utf-8")
SCHED = json.loads((HERE / "e1-schedule.json").read_text(encoding="utf-8"))
RESERVE_NAMES = json.loads((HERE / "e1-reserves.json").read_text(encoding="utf-8"))

FORMAT_HINT = {
    "pseudo": "pseudo-commands: invented command-line tools with invented but plausible output (for example `shelfctl sync --tray 4`)",
    "git": "real tool format: git (commit, push, pull, merge, rebase, tag, log) with realistic git output",
    "npm": "real tool format: npm (install, test, run build, publish, audit) with realistic npm output",
    "pytest": "real tool format: pytest runs, with realistic pytest output",
    "kubectl": "real tool format: kubectl (apply, rollout status, get pods, describe) with realistic output",
    "curl_http": "real tool format: curl against an HTTP API, with realistic status lines or JSON bodies",
    "ci_log": "real tool format: a CI pipeline or job log (fetched with curl or a command-line client), with realistic stage and job lines",
    "chat_api_json": "real tool format: a chat service API (post a message, read a thread), with realistic JSON",
    "mail_api_json": "real tool format: a mail service API (send, draft, list), with realistic JSON",
}


def say(msg):
    line = f"{oc.utc_now()} {msg}"
    print(line, flush=True)
    with open(GENLOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ------------------------------------------------------------------ state
def read_state():
    accepted = {r["slot"]: r for r in oc.read_jsonl(ACCEPTED)} if ACCEPTED.exists() else {}
    calls = oc.read_jsonl(CALLS) if CALLS.exists() else []
    attempts = Counter(s for c in calls if c.get("counted") for s in c["slots"])
    spawned = json.loads(SPAWNED.read_text(encoding="utf-8")) if SPAWNED.exists() else []
    return accepted, calls, attempts, spawned


def spawn_reserves(accepted, attempts, spawned):
    """A slot that used all its tries without success is replaced by a reserve with the same truth, trap and format."""
    universe = SCHED + spawned
    have = {r["after"] for r in spawned}          # slots that already have a reserve behind them
    changed = False
    for s in universe:
        if s["slot"] not in accepted and attempts[s["slot"]] >= MAX_ATTEMPTS and s["slot"] not in have and len(spawned) < len(RESERVE_NAMES):
            k = len(spawned)
            base = s["slot"] if "replaces" not in s else s["replaces"]
            new = {"slot": f"S{151 + k:03d}", "truth": s["truth"], "trap": s["trap"], "format": s["format"],
                   "name": RESERVE_NAMES[k], "setting": sch.SETTINGS[(k * 7 + 3) % len(sch.SETTINGS)], "replaces": base, "after": s["slot"]}
            spawned.append(new)
            have.add(s["slot"])
            changed = True
            say(f"slot {s['slot']} used {MAX_ATTEMPTS} tries without a kept item; reserve {new['slot']} takes its place ({s['truth']}, {s['trap']})")
    if changed:
        SPAWNED.write_text(json.dumps(spawned, indent=1), encoding="utf-8")
    return SCHED + spawned


def next_batches(universe, accepted, attempts):
    pending = [s for s in universe if s["slot"] not in accepted and attempts[s["slot"]] < MAX_ATTEMPTS]
    pending.sort(key=lambda s: (attempts[s["slot"]], s["slot"]))
    batches, i = [], 0
    while i < len(pending):
        a = attempts[pending[i]["slot"]]
        size = BATCH_BY_ATTEMPT.get(a, 1)
        group, j = [pending[i]], i + 1
        while j < len(pending) and len(group) < size and attempts[pending[j]["slot"]] == a:
            group.append(pending[j])
            j += 1
        batches.append(group)
        i = j
    return batches


# ------------------------------------------------------------------ the call
def slot_block(s):
    return (f"Slot {s['slot']}\n- truth: {s['truth']}\n- trap: {s['trap']}\n- format: {FORMAT_HINT[s['format']]}\n"
            f"- main object name to use: {s['name']}\n- setting: {s['setting']}")


def build_prompt(group):
    n = len(group)
    head = (f"Write {n} item{'s' if n > 1 else ''}, one for each slot below, in this order. Each item's \"id\" is its slot id. "
            "Think briefly, then write the JSON Lines directly.\n\n")
    return head + "\n\n".join(slot_block(s) for s in group) + "\n"


def broker_call(system, prompt):
    """One call through the AI broker (recorded in its ledger). Returns (reply text or None, info)."""
    oc.wait_if_paused("e1-generate")
    t0 = time.time()
    with tempfile.TemporaryDirectory(prefix="e1-") as d:
        sp, up = Path(d) / "system.txt", Path(d) / "user.txt"
        sp.write_text(system, encoding="utf-8")
        up.write_text(prompt, encoding="utf-8")
        try:
            p = subprocess.run(["node", str(oc.BROKER / "broker.mjs"), "run", "--provider", "openrouter", "--model", MODEL,
                                "--prompt-file", str(up), "--system-file", str(sp), "--lane", LANE],
                               cwd=str(oc.BROKER), capture_output=True, text=True, encoding="utf-8", timeout=900)
        except subprocess.TimeoutExpired:
            return None, {"ledger": None, "exit": "timeout", "seconds": round(time.time() - t0, 1)}
    m = re.search(r"recorded in ledger/(\S+)", p.stderr or "")
    rel = m.group(1) if m else None
    info = {"ledger": rel, "exit": p.returncode, "seconds": round(time.time() - t0, 1), "cost": None, "tokens": None, "finish": None,
            "provider": None}
    if rel:
        try:
            rj = json.loads((oc.BROKER / "ledger" / rel / "run.json").read_text(encoding="utf-8"))
            info["cost"], info["tokens"] = rj.get("providerReportedCostUsd"), rj.get("tokens")
        except Exception:
            pass
        try:
            raw = json.loads((oc.BROKER / "ledger" / rel / "raw.json").read_text(encoding="utf-8")) or {}
            info["finish"] = (raw.get("choices") or [{}])[0].get("finish_reason")
            info["provider"] = raw.get("provider")
        except Exception:
            pass
    if p.returncode != 0:
        return None, info
    return p.stdout, info


# ------------------------------------------------------------------ reading the reply
def extract_objects(text):
    """Every JSON object in the reply that looks like an item (has "id" or "claim"). Fences and prose around them are ignored."""
    dec = json.JSONDecoder(strict=False)
    objs, i, n = [], 0, len(text)
    while i < n:
        j = text.find("{", i)
        if j < 0:
            break
        try:
            obj, end = dec.raw_decode(text, j)
        except ValueError:
            i = j + 1
            continue
        if isinstance(obj, dict) and ("id" in obj or "claim" in obj):
            objs.append(obj)
        i = end
    return objs


def map_objects(group, objs):
    """Match the reply's objects to the slots by id; if no ids match but the counts agree, match by position."""
    ids = [s["slot"] for s in group]
    mapped, how, leftover = {}, {}, []
    for o in objs:
        sid = o.get("id")
        if sid in ids and sid not in mapped:
            mapped[sid], how[sid] = o, "id"
        else:
            leftover.append(o)
    free = [s for s in ids if s not in mapped]
    if free and len(leftover) == len(free):
        for sid, o in zip(free, leftover):
            mapped[sid], how[sid] = o, "position"
    return mapped, how


def normalise(obj, slot):
    return {"id": slot["slot"], "claim": obj["claim"].strip(),
            "turns": [{"cmd": t["cmd"], "output": t["output"], "narration": t.get("narration", "")} for t in obj["turns"]],
            "truth": slot["truth"], "deciding_line": obj["deciding_line"], "why": obj["why"].strip(), "trap": slot["trap"],
            "world": obj["world"], "format": slot["format"]}


# ------------------------------------------------------------------ the loop
def handle(group, text, info, call_no):
    accepted, calls, attempts, spawned = read_state()
    counted = text is not None
    objs = extract_objects(text) if text else []
    mapped, how = map_objects(group, objs)
    kept = dropped = 0
    drop_codes = Counter()
    tokens = [val.tokens(r["item"]["claim"]) for r in accepted.values()]
    for s in group:
        attempt_no = attempts[s["slot"]] + 1
        obj = mapped.get(s["slot"])
        if not counted:
            continue
        if obj is None:
            reasons = ["truncated_reply" if info.get("finish") == "length" else ("empty_reply" if not (text or "").strip() else "missing_from_reply")]
        else:
            if how.get(s["slot"]) == "position":
                obj = dict(obj, id=s["slot"])
            reasons = val.validate_item(obj, s, tokens)
        if reasons:
            dropped += 1
            drop_codes.update(reasons)
            with open(DROPS, "a", encoding="utf-8") as f:
                f.write(json.dumps({"call": call_no, "slot": s["slot"], "attempt": attempt_no, "reasons": reasons}) + "\n")
        else:
            kept += 1
            item = normalise(obj, s)
            tokens.append(val.tokens(item["claim"]))
            with open(ACCEPTED, "a", encoding="utf-8") as f:
                f.write(json.dumps({"slot": s["slot"], "attempt": attempt_no, "call": call_no, "ledger": info.get("ledger"),
                                    "matched_by": how.get(s["slot"]), "item": item}, ensure_ascii=False) + "\n")
    rec = {"call": call_no, "slots": [s["slot"] for s in group], "counted": counted, "ledger": info.get("ledger"), "exit": info.get("exit"),
           "seconds": info.get("seconds"), "cost": info.get("cost"), "tokens": info.get("tokens"), "finish": info.get("finish"),
           "provider": info.get("provider"), "objects_found": len(objs), "kept": kept, "dropped": dropped, "drop_codes": dict(drop_codes)}
    with open(CALLS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def run():
    ok, why = oc.design_seal_ok("E1")
    if not ok:
        sys.exit(f"STOP: {why}")          # no item is written before the design is sealed
    E1.mkdir(exist_ok=True)
    base = oc.ledger_spend()
    spent = base["usd"]
    say(f"start: spend so far {spent:.6f} USD (cap {CAP_USD}); ledger runs counted {base['runs']}")
    transport_failures = 0
    stop = False
    while not stop:
        accepted, calls, attempts, spawned = read_state()
        universe = spawn_reserves(accepted, attempts, spawned)
        batches = next_batches(universe, accepted, attempts)
        say(f"wave: {len(accepted)} kept, {sum(1 for s in universe if s['slot'] not in accepted and attempts[s['slot']] < MAX_ATTEMPTS)} still to write, {len(batches)} calls planned")
        if not batches:
            break
        call_base = len(calls)
        with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
            inflight, queue, n_sent = {}, iter(enumerate(batches, 1)), 0

            def submit():
                nonlocal n_sent
                nxt = next(queue, None)
                if nxt is None:
                    return False
                k, group = nxt
                if spent + WORST_CALL_USD * (len(inflight) + 1) > CAP_USD:
                    say(f"STOP: one more call could pass the US${CAP_USD} cap (spent {spent:.4f}); no new calls")
                    return "cap"
                inflight[ex.submit(broker_call, SPEC, build_prompt(group))] = (call_base + k, group)
                n_sent += 1
                return True

            for _ in range(WORKERS):
                r = submit()
                if r == "cap":
                    stop = True
                    break
            while inflight:
                fut = next(cf.as_completed(inflight))
                call_no, group = inflight.pop(fut)
                text, info = fut.result()
                spent += info["cost"] if info.get("cost") is not None else (WORST_CALL_USD if info.get("ledger") else 0)
                rec = handle(group, text, info, call_no)
                if text is None:
                    transport_failures += 1
                say(f"call {call_no} slots {','.join(rec['slots'])}: kept {rec['kept']}, dropped {rec['dropped']} {rec['drop_codes']} "
                    f"| finish {rec['finish']} tokens {rec['tokens']} cost {rec['cost']} | spent {spent:.4f}")
                if transport_failures >= MAX_TRANSPORT_FAILURES:
                    say(f"STOP: {transport_failures} calls failed without a reply; stopping")
                    stop = True
                if not stop:
                    r = submit()
                    if r == "cap":
                        stop = True
        if stop:
            break
    accepted, calls, attempts, spawned = read_state()
    final = oc.ledger_spend()
    say(f"end: {len(accepted)} kept; hosted spend by the broker's ledger {final['usd']:.6f} USD over {final['runs']} runs ({final['runs_without_cost']} without a cost)")


def status():
    accepted, calls, attempts, spawned = read_state()
    universe = SCHED + spawned
    print("kept:", len(accepted), "| slots:", len(universe), "| reserves spawned:", len(spawned))
    print("kept by truth:", dict(Counter(r["item"]["truth"] for r in accepted.values())))
    print("kept by trap:", dict(Counter(r["item"]["trap"] for r in accepted.values())))
    print("calls:", len(calls), "| counted:", sum(1 for c in calls if c.get("counted")), "| finish:", dict(Counter(c.get("finish") for c in calls)))
    drops = oc.read_jsonl(DROPS) if DROPS.exists() else []
    print("drops:", len(drops), dict(Counter(r for d in drops for r in d["reasons"])))
    print("attempts used by slot:", dict(Counter(attempts[s["slot"]] for s in universe)))
    print("not yet kept:", [s["slot"] for s in universe if s["slot"] not in accepted and attempts[s["slot"]] >= MAX_ATTEMPTS])
    print("spend:", oc.ledger_spend())


def assemble():
    accepted, calls, attempts, spawned = read_state()
    order = []
    for s in SCHED:                       # a slot's place in the order is kept by its reserve, if it needed one
        chain = [s["slot"]] + [r["slot"] for r in spawned if r["replaces"] == s["slot"]]
        kept = [c for c in chain if c in accepted]
        if kept:
            order.append(kept[0])
        else:
            say(f"slot {s['slot']} has no kept item (not filled)")
    out, mapfile = E1 / "items-X001-X150.jsonl", E1 / "slot-map.json"
    if out.exists() or mapfile.exists():
        sys.exit("items-X001-X150.jsonl or slot-map.json exists; not overwriting")
    rows, smap = [], {}
    for k, sid in enumerate(order, 1):
        item = dict(accepted[sid]["item"])
        xid = f"X{k:03d}"
        item["id"] = xid
        rows.append(item)
        smap[xid] = {"slot": sid, "attempt": accepted[sid]["attempt"], "call": accepted[sid]["call"], "ledger": accepted[sid]["ledger"]}
    oc.write_jsonl(out, rows)
    mapfile.write_text(json.dumps(smap, indent=1), encoding="utf-8")
    print("items written:", len(rows), "| truth:", dict(Counter(r["truth"] for r in rows)), "| trap:", dict(Counter(r["trap"] for r in rows)))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "run":
        run()
    elif mode == "status":
        status()
    elif mode == "assemble":
        assemble()
    else:
        print(__doc__)
