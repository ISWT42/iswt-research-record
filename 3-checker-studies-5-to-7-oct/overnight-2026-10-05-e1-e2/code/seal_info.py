"""Read a FreeTSA reply: print its own time stamp and whether its digest is the SHA-256 of the sealed hash file.
  python seal_info.py <seal.txt>      one seal      |      python seal_info.py all     every seal under the overnight folder
Needs only `openssl ts -reply -text` (no CA file); the reply's signature chain is not checked here.
"""
import hashlib, re, subprocess, sys
from pathlib import Path

ROOT = Path(r"C:\Users\joshd\Workbench\overnight-2026-10-05")


def info(seal):
    seal = Path(seal)
    tsr = Path(str(seal) + ".tsr")
    p = subprocess.run(["openssl", "ts", "-reply", "-in", str(tsr), "-text"], capture_output=True, text=True)
    text = p.stdout
    status = re.search(r"Status: (.*)", text)
    when = re.search(r"Time stamp: (.*)", text)
    hexes = re.findall(r"^\s+[0-9a-f]{4} - ((?:[0-9a-f]{2}[ -]){1,16})", text.split("Message data:")[1].split("Serial number")[0] if "Message data:" in text else "", re.M)
    digest = "".join(h.replace(" ", "").replace("-", "") for h in hexes)
    alg = (re.search(r"Hash Algorithm: (\w+)", text) or [None, "sha256"])[1].lower()
    mine = hashlib.new(alg, seal.read_bytes()).hexdigest()
    return {"seal": seal.name, "hash_algorithm": alg, "status": status.group(1).strip() if status else None, "freetsa_time": when.group(1).strip() if when else None,
            "digest_matches_file": digest == mine, "file_sha256": mine}


if __name__ == "__main__":
    targets = sorted(ROOT.rglob("*-SHA256.txt")) if sys.argv[1:] == ["all"] else [Path(a) for a in sys.argv[1:]]
    for t in targets:
        if Path(str(t) + ".tsr").exists():
            r = info(t)
            print(f"{r['seal']}: {r['status']} | FreeTSA time {r['freetsa_time']} | {r['hash_algorithm']} digest matches the file: {r['digest_matches_file']} | {r['hash_algorithm']} {r['file_sha256'][:16]}...")
        else:
            print(f"{t.name}: no .tsr")
