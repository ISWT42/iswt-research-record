#!/usr/bin/env bash
# Push the two coat-check tasks to Kaggle. A push makes the task private to the account; nothing is published and
# no model runs. Needs the owner's yes for the push. Written 7 Oct 2026 for review, in the style of the entry's
# push step (go-2026-10-01.log). NOT RUN.
#
#   bash push-coatcheck.sh            both tasks, T6 then T5   (ARMS="T5" for one)
#
# Before the first push: FILES-SHA256.txt made after review and sealed the usual way, the block check passed
# (see COMMANDS.md). The script checks that the files are the listed ones, that the entry's own seal still
# verifies and that tasks/ equals a fresh build, and stops otherwise. The task slug must equal the name in the
# task's @kbench.task line, which is the file name without .py.
set -u
. "$(dirname "$0")/coatcheck-common.sh"
ARMS=${ARMS:-"T6 T5"}
LOG=$RESULTS/push-coatcheck.log
for arm in $ARMS; do [ -n "${TASK[$arm]:-}" ] || { echo "unknown task $arm (T5 or T6)"; exit 1; }; done

preflight
for arm in $ARMS; do
  task=${TASK[$arm]}
  f="$UPD/tasks/$task.py"
  [ -f "$f" ] || { say "no task file $f; stopping"; exit 1; }
  grep -q "^@kbench.task(name=\"$task\")" "$f" || { say "$f does not name the task $task; stopping"; exit 1; }
  say "push $task (sha256 $(sha256sum "$f" | cut -c1-12)... matches the list)"
  fw=$(cygpath -m "$f" 2>/dev/null || echo "$f")   # a Windows-style path for the native kaggle command; the same path elsewhere
  "$K" b t push "$task" -f "$fw" --wait 2>&1 | grep -v -i -E "token|bearer" | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  [ "$rc" -eq 0 ] || { say "push of $task failed (exit $rc); stopping"; exit 4; }
  say "pushed $task"
done
"$K" b t list --name-regex 'receipt-triplets-t[56]' --all 2>&1 | grep -v -i -E "token|bearer" | tee -a "$LOG"
for arm in $ARMS; do
  "$K" b t status "${TASK[$arm]}" 2>&1 | grep -v -i -E "token|bearer" | tee -a "$LOG"
done
say "pushed: $ARMS. Next: the canary round of run-coatcheck.sh"
