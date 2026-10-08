"""E1 slot schedule: which (truth, trap, format, name, setting) each of the 150 slots asks the writer for.
Deterministic from a fixed seed, so the design can fix it before any item exists. Prints counts only.
  python e1_schedule.py          writes e1-schedule.json and e1-reserves.json when missing; checks an existing schedule against the seed
"""
import json, random, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 5102026
TRUTHS = ("shown", "contradicted", "not_shown")
TRAPS = ("other_environment", "intermediate_signal", "truncated", "relayed_claim", "example_text",
         "tool_failed_to_run", "expected_error", "retry", "narration", "injected_text")   # 10 traps x 12 slots
EASY = "none"                                                                              # 30 slots
REAL = ("git", "npm", "pytest", "kubectl", "curl_http", "ci_log", "chat_api_json", "mail_api_json")
SETTINGS = ("an invoicing service", "a mobile app release", "a data pipeline", "a documentation site", "an inventory system",
            "a newsletter campaign", "a machine-learning training job", "a database migration", "a certificate renewal",
            "a feature-flag rollout", "a nightly backup job", "a payments gateway", "a search index", "a customer-support queue",
            "an internal wiki", "a build farm", "a log-shipping agent", "a calendar-sync tool", "a package registry",
            "a monitoring dashboard", "a spreadsheet import", "a thumbnail service", "a customer-records export", "a DNS change",
            "a cache layer", "an authentication service", "a game-server patch", "a lab-equipment scheduler",
            "a translation workflow", "a metrics exporter")
ONSET = ("b", "br", "d", "dr", "f", "g", "gr", "k", "kr", "l", "m", "n", "p", "pr", "r", "s", "st", "t", "tr", "v", "z")
VOWEL = ("a", "e", "i", "o", "u")
CODA = ("l", "m", "n", "r", "s", "th", "x", "k", "d")


def earlier_text():
    """All text of the earlier banks, to keep invented names from colliding with them."""
    texts = []
    for p in (r"C:\Users\joshd\Workbench\chatgpt-review-2026-10-04\completion-claims-001-300.jsonl",
              r"C:\Users\joshd\Workbench\replication-2026-10-05\items-R001-R040.jsonl"):
        texts.append(Path(p).read_text(encoding="utf-8").lower())
    return "\n".join(texts)


def make_names(rng, n, taken_text):
    names = set()
    while len(names) < n:
        w = rng.choice(ONSET) + rng.choice(VOWEL) + rng.choice(CODA) + rng.choice(ONSET) + rng.choice(VOWEL) + rng.choice(CODA + ("",))
        if 5 <= len(w) <= 9 and w not in taken_text:
            names.add(w)
    return sorted(names)


def build():
    rng = random.Random(SEED)
    pairs = [(t, trap) for trap in TRAPS for t in TRUTHS for _ in range(4)]       # 120: each trap 4 of each truth
    pairs += [(t, EASY) for t in TRUTHS for _ in range(10)]                         # 30 easy: 10 of each truth
    rng.shuffle(pairs)
    formats = ["pseudo"] * 50 + [REAL[i % 8] for i in range(100)]                   # 50 pseudo; 100 real, 12 or 13 of each tool
    rng.shuffle(formats)
    names = make_names(rng, 150, earlier_text())
    rng.shuffle(names)
    settings = [SETTINGS[i % len(SETTINGS)] for i in range(150)]
    rng.shuffle(settings)
    return [{"slot": f"S{i + 1:03d}", "truth": pairs[i][0], "trap": pairs[i][1], "format": formats[i],
             "name": names[i].capitalize(), "setting": settings[i]} for i in range(150)]


def build_reserves(taken):
    """30 spare names for slots that cannot be filled in four tries; a reserve takes over the failed slot's truth, trap and format."""
    rng = random.Random(SEED + 1)
    names = [n for n in make_names(rng, 60, earlier_text()) if n.capitalize() not in taken]
    return [n.capitalize() for n in names][:30]


if __name__ == "__main__":
    from collections import Counter
    sched = build()
    out = HERE / "e1-schedule.json"
    if out.exists():
        assert json.loads(out.read_text(encoding="utf-8")) == sched, "existing e1-schedule.json differs from the seeded schedule"
        print("e1-schedule.json exists and equals the seeded schedule")
    else:
        out.write_text(json.dumps(sched, indent=1), encoding="utf-8")
        print("wrote e1-schedule.json")
    res = HERE / "e1-reserves.json"
    if not res.exists():
        res.write_text(json.dumps(build_reserves({s["name"] for s in sched}), indent=1), encoding="utf-8")
        print("wrote e1-reserves.json")
    print("slots:", len(sched))
    print("truth:", dict(Counter(s["truth"] for s in sched)))
    print("trap:", dict(Counter(s["trap"] for s in sched)))
    print("format:", dict(Counter(s["format"] for s in sched)))
    print("setting counts (min,max):", min(Counter(s["setting"] for s in sched).values()), max(Counter(s["setting"] for s in sched).values()))
    print("unique names:", len({s["name"] for s in sched}), "| reserve names:", len(json.loads(res.read_text(encoding="utf-8"))))
