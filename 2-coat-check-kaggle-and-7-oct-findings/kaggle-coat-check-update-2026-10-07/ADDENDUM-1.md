# Kaggle coat-check update, Addendum 1: the push started a run on each task

**Written:** 7 Oct 2026 by the coordinating session, Claude (Opus 5.5). Its time is the time on its seal. The sealed files (FILES-SHA256.txt and everything it lists, sealed by FreeTSA at 18:11:00 UTC) are not edited.

**What happened.** Joshua said to push the two tasks (private) and to run them on the four models once the Bitcoin block confirms the seal. The push script (`push-coatcheck.sh`) says in its header that a push starts no model run. That was wrong: on Kaggle, each push with `--wait` also ran the task once on Gemini 3.7 Flash. Kaggle's own status lines:

- t6 (`receipt-triplets-t6-coat-check-do`, version 1): gemini-3.7-flash, Completed, started 2026-10-07 18:24:15, ended 18:57:01.
- t5 (`receipt-triplets-t5-coat-check-report`, version 1): gemini-3.7-flash, Completed, started 2026-10-07 18:49:52, ended 19:06:43.

Both runs started after the FreeTSA seal of the forecasts (18:11:00 UTC) and before the OpenTimestamps proof was confirmed in a Bitcoin block (still pending when this was written).

**How they count.** They used the sealed task files, unchanged, so the forecast file's counting rules apply to them as written: they are the earliest Gemini 3.7 Flash runs of each task. Nothing in the forecasts, rules or files changes. The first t5 push also failed to print on a Windows text encoding (the t6 push had finished on Kaggle's side); t5 was pushed again with UTF-8 output, and each task has exactly one version.

**What changes.** The remaining runs still wait for the block check, as Joshua asked. The push script's header comment is wrong and is corrected here, not in the sealed file.
