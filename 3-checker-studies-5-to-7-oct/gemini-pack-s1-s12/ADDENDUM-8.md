# Addendum 8: S9 resumes, and the runners run in the background (written 2026-10-06 from 15:05 UTC)

Everything in the pack and Addenda 1 to 7 stands, except where this addendum says otherwise.

## What happened
- S9 started at 14:32 UTC (`runs/s9/order.json` was written first, as Addendum 6 requires).
- It stopped at **2,523 of 3,360 calls**. The last row was written at 15:03 UTC, and Antigravity exited at about 15:04 UTC.
  - The run lasted about 30 minutes, which matches a time limit on Antigravity's command tool. The runner ran inside one tool call.
  - At the stop: no errors, every row answered, and the last line of `runs/s9/calls.jsonl` complete and valid.
- No report was written, and S11 and S12 had not started. Their runners existed, written by Gemini; they had made no calls.

## The change
1. **The runners are not changed.** Their SHA-256, read in the box at 15:05:55 UTC:
   - `runs/s9/code/runner.py`: `c5ada5902517501a2d9ce8d5807a4beef9a4eaadc68108531795966fc9431765`
   - `runs/s11/code/runner.py`: `a2cec555e16410b9c5ff6889afa004ded4d2c49d0b7d5d9799a3814a8e5812dd`
   - `runs/s12/code/runner.py`: `07f3ef3bc9e28aea5b0c80146b1e6657d203008ee551c81e7fb21751e36146b6`
   - `runs/s9/order.json`: `44e26e72ff319ab328f6a57a5202d369e531956933a93b432e7679f864515978`
2. **S9 resumes with the same runner.** It reads the calls already in `calls.jsonl` and makes only the missing 837. It counts the spend already reported toward its US$2 stop.
3. **They run in the background, one after another, from Joshua's paste:**
   - S9, then S11 only if S9's runner exits cleanly, then S12 only if S11's does.
   - No tool time limit can stop them.
   - The key stays in his terminal's environment only.
   - Output goes to `runs/run-all-2026-10-06.log`.
4. **Reports come after the runs.** Addendum 7 asked for each spec's report before the next spec starts. Instead, after all three runs, Gemini writes the three reports in the README's format from the run files, with no new calls.
   - Each runner's own stop rules still apply to its spec: more than 5% "no answer", and its spend stop.
   - A stop ends the chain.

## Why this is safe for the results
- Every request is still checked by the coordinator, byte for byte against the sealed specs, before scoring. The order files are checked against Addendum 2's method.
- S9's scorer was sealed at 14:39:38 GMT, before any S9 result was read. Its forecast rules don't change.
- Resuming changes when calls happen, not what they are. At temperature 0.7 the seeds fix each sample's request, but not the hosted reply: hosted replies vary run to run (see the hosted noise floor). The coordinator will report the 837 resumed calls apart from the first 2,523, so a time effect would show.

The SHA-256 of this file is in `ADDENDUM-8-SHA256.txt`, sealed by FreeTSA.
