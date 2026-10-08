# S13 stack test, addendum 1: the Gemini half crashed before any model call (7 October 2026)

Dated addendum. The sealed design (SEAL-SHA256.txt, FreeTSA 06:14:50 GMT) is unchanged; the forecasts stand as sealed.

## What happened
- **The start:** Joshua started both runs at about 06:16 UTC with his paste. Both probes had passed.
- **The Gemini half's first attempt:** 33 calls (T001 forced to T017 forced), each ending in about 1.5 seconds with the Gemini command line's own crash: "An unexpected critical error occurred: Error: EBADF: bad file descriptor, read".
- **The cause:** under `nohup`, standard input is an unreadable descriptor, and the Gemini command line always reads standard input (its `-p` prompt is "appended to input on stdin"). The probe passed only because it ran in the foreground.
- **No model answer was produced.** These 33 rows say nothing about Gemini.
- **Claude stopped the Gemini half at about 06:18 UTC.** The Sol half was not touched.

## The fix
- The runner now gives every tool call an empty standard input (`stdin=subprocess.DEVNULL`). Nothing else changed: the prompts, commands, order, time limit, parsing and recording are as sealed.
- **The runners:**
  - sealed runner: `run_stack.py` SHA-256 783ba0d0...cd, kept in the box as `run_stack.sealed-0614.py`;
  - fixed runner: SHA-256 6ed665baea95659001f9c427c794e8a1b1610a97a16ce37284ac41da3fb378a6.

## What is kept, and what happens now
- **The 33 failed rows** move to `results/gemini-attempt1-ebadf.jsonl`, with their log as `gemini-attempt1.log`. They are kept and are not scored.
- **The Gemini half restarts from T001** with the fixed runner, on the same sealed inputs.
- **The Sol half keeps running** in its own process, started at 06:16 UTC with the sealed runner. The Codex command line takes its prompt from its arguments and its calls answer normally, so it is not restarted. Its rows count as recorded.
- **Who restarted it:** Claude, over the box's session key, continuing the run Joshua started with his paste. No new sign-in was made.

## Seen so far (raw, not scored)
In Sol's first calls, two forced records got no verdict. The model's reply named the reason: "No TURNS were provided; please supply them so I can choose a supported verdict." Those records contain no log turns at all. Under the design, a reply with no verdict is counted separately, never dropped. Nothing is scored before the results are sealed.
