# Addendum 1: nothing to install (written 2026-10-06 03:20 UTC)

The coordinator wrote this after the runner's first question, QUESTIONS.md question 1. It replaces every "pip install" line in the pack: S2 step 1, S3 to S5 where they name the install, and the "receipt_pair" line of MODELS.json. Everything else in the pack stands.

- **receipt_pair at commit b7dfbad is already here, as plain source files,** in `vendor/receipt_pair/`, with its MIT `LICENSE`. Nothing needs installing, so no yes is needed: this answers QUESTIONS.md question 1.
- **Run Python with `PYTHONPATH=$HOME/work/gemini-pack/vendor`.** Check it first:
  `PYTHONPATH=$HOME/work/gemini-pack/vendor python3 -c "import receipt_pair; print(receipt_pair.__file__)"`
  It must print a path inside `vendor/`.
- **Use only Python's standard library for everything else:** `urllib.request` for the HTTPS calls, `json`, `concurrent.futures` for the 4 parallel calls, `hashlib`, `random` and `datetime`. Do not install anything, and do not create a virtual environment.
- **The box's web proxy:** web traffic goes through it automatically (`https_proxy` is set in your session), and `urllib` picks it up. If the proxy refuses a call, stop and report it.
- Python here is 3.10. receipt_pair supports 3.9 and newer.

The SHA-256 of this file and of every file under `vendor/` is in `ADDENDUM-1-SHA256.txt`, sealed by FreeTSA.
