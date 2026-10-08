"""E2 local run: the two local models (arms A and B) x three framings of the instruction, on the context-present items and their twins.
Run 1's code, user prompt and settings are unchanged; only the system prompt differs between arms (e2_framings.py).
Resumable, pause-aware. Arm names are "A-forced", "A-allowed", "A-rewarded", "B-forced", ...
  python e2_run.py smoke          run 1's three toy items through all six arms, into logs/smoke-e2 (plumbing only, not scored)
  python e2_run.py run [p1|p2]    p1 = present items and context-missing twins; p2 = blank-output twins; default both, p1 first
The real run refuses unless the design seal matches the files it names and the twins file is sealed. Prints ids, answers and counts only.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc   # noqa: E402
import e2_framings as fr        # noqa: E402
from e1_run import TOY      # noqa: E402

E2 = oc.ROOT / "e2"


def arms():
    out = []
    for m in oc.local_arms():
        for name in fr.FRAMING_NAMES:
            out.append({"arm": f"{m['arm']}-{name}", "id": m["id"], "extra": m["extra"], "system": fr.FRAMINGS[name]})
    return out


def main(mode, phase):
    oc.install_local_patches("e2-run")
    oc.rp.MODELS = arms()
    health = oc.rp.http("GET", oc.rp.LEMONADE + "/health", None, 30)
    oc.log(oc.LOGS / "e2-run-log.txt", f"{mode} {phase}: Lemonade {health.get('version')} status {health.get('status')}; arms "
           f"{[a['arm'] for a in oc.rp.MODELS]}; settings {oc.rp.SETTINGS}")
    if mode == "smoke":
        out = oc.LOGS / "smoke-e2"
        out.mkdir(exist_ok=True)
        oc.rp.OUT = out
        oc.rp.run(TOY, "smoke")
        return
    ok, why = oc.design_seal_ok("E2")
    if not ok:
        sys.exit(f"STOP: {why}")
    if not oc.sealed_ok(E2 / "TWINS-SHA256.txt", "twins-R001-R040.jsonl"):
        sys.exit("STOP: the twins file is not sealed or does not match its seal")
    rows = oc.read_jsonl(E2 / "twins-R001-R040.jsonl")
    oc.rp.OUT = E2 / "results"
    phases = {"p1": ("present", "twin_missing"), "p2": ("twin_blank",)}
    for ph in (["p1", "p2"] if phase == "all" else [phase]):
        items = [r for r in rows if r["kind"] in phases[ph]]
        oc.log(oc.LOGS / "e2-run-log.txt", f"phase {ph} starts: {len(items)} items x {len(oc.rp.MODELS)} arms; twins sha256 {oc.sha256_file(E2 / 'twins-R001-R040.jsonl')}")
        oc.rp.run(items, "e2-local")
        oc.log(oc.LOGS / "e2-run-log.txt", f"phase {ph} ends")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "smoke":
        main("smoke", "p1")
    elif a and a[0] == "run":
        main("run", a[1] if len(a) > 1 else "all")
    else:
        print(__doc__)
