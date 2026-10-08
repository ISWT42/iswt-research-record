"""E1 local run: both local models (arms A and B, run 2's local lane) on every item of items-X001-X150.jsonl,
with run 1's code, prompts and settings unchanged (temperature 0, max_tokens 400, seed 42, thinking off for Gemma).
Resumable (run_pair.run skips every (arm, id) pair already written), pause-aware (the PAUSE file).
  python e1_run.py smoke    run 1's three toy items through both arms, into logs/smoke-e1 (plumbing only, not scored)
  python e1_run.py run      the real run; refuses unless the items file matches its sealed hash and has a FreeTSA reply
Prints ids, answers and counts only.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import overnight_common as oc  # noqa: E402

E1 = oc.ROOT / "e1"
TOY = [{"id": "toy1", "claim": "I pushed the parser fix to acme/tools.", "truth": "shown",
        "turns": [{"cmd": "git push origin fix-parser", "output": "To github.com:acme/tools.git\n   4f1c2aa..9b3e771  fix-parser -> fix-parser"}]},
       {"id": "toy2", "claim": "Sent the March invoice to Dana.", "truth": "contradicted",
        "turns": [{"cmd": "python send_invoice.py --month march --to dana@example.org",
                   "output": "Connecting to smtp.example.org...\nsmtplib.SMTPAuthenticationError: (535, 'Authentication failed')"}]},
       {"id": "toy3", "claim": "The dashboard is deployed.", "truth": "not_shown",
        "turns": [{"cmd": "npm run build", "output": "Build complete: 14 files written to dist/"}]}]


def main(mode):
    oc.install_local_patches("e1-run")
    oc.rp.MODELS = oc.local_arms()
    health = oc.rp.http("GET", oc.rp.LEMONADE + "/health", None, 30)
    oc.log(oc.LOGS / "e1-run-log.txt", f"{mode}: Lemonade {health.get('version')} status {health.get('status')}; arms "
           f"{[(m['arm'], m['id']) for m in oc.rp.MODELS]}; settings {oc.rp.SETTINGS}")
    if mode == "smoke":
        out = oc.LOGS / "smoke-e1"
        out.mkdir(exist_ok=True)
        oc.rp.OUT = out
        oc.rp.run(TOY, "smoke")
        return
    ok, why = oc.design_seal_ok("E1")
    if not ok:
        sys.exit(f"STOP: {why}")
    items_path = E1 / "items-X001-X150.jsonl"
    if not oc.sealed_ok(E1 / "ITEMS-SHA256.txt", "items-X001-X150.jsonl"):
        sys.exit("STOP: the items file is not sealed (hash line + FreeTSA reply) or does not match its seal")
    items = oc.read_jsonl(items_path)
    oc.rp.OUT = E1 / "results"
    oc.log(oc.LOGS / "e1-run-log.txt", f"run starts: {len(items)} items, items sha256 {oc.sha256_file(items_path)}")
    oc.rp.run(items, "e1-local")
    oc.log(oc.LOGS / "e1-run-log.txt", "run ends")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("smoke", "run"):
        main(sys.argv[1])
    else:
        print(__doc__)
