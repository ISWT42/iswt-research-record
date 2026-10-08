#!/usr/bin/env bash
# Publish the two coat-check tasks on Kaggle (irreversible from the CLI). Needs the owner's own word for each
# line below, quoted, as it is to be logged. Written 7 Oct 2026 for review, in the style of
# publish-tasks-2026-10-02.log. NOT RUN.
#
#   bash publish-coatcheck.sh "Publish."             publishes the two tasks, not their backing notebooks
#   bash publish-coatcheck.sh "publish notebook" notebook
#                                                    the second step: publishes the tasks' backing notebooks too
#
# Adding the tasks to the benchmark "two-kinds-of-false-done" is not a command: the CLI has no command for it
# (see COMMANDS.md); it is done on Kaggle's benchmark page, with the owner's yes.
set -u
. "$(dirname "$0")/coatcheck-common.sh"
ARMS=${ARMS:-"T6 T5"}
word=${1:?give the words the owner said, in quotes, as they are to be logged}
mode=${2:-tasks}
LOG=$RESULTS/publish-coatcheck.log
for arm in $ARMS; do [ -n "${TASK[$arm]:-}" ] || { echo "unknown task $arm (T5 or T6)"; exit 1; }; done
case "$mode" in
  tasks)    flag="--no-publish-backing-notebook"; head="publish run" ;;
  notebook) flag=""; head="notebook publish" ;;
  *) echo "mode is tasks or notebook"; exit 1 ;;
esac

echo "$head $(date -u +%Y-%m-%dT%H:%M:%SZ), owner's word: \"$word\"" | tee -a "$LOG"
for arm in $ARMS; do
  task=${TASK[$arm]}
  echo "--- $task" | tee -a "$LOG"
  "$K" b t publish "$task" $flag 2>&1 | grep -v -i -E "token|bearer" | tee -a "$LOG"
  rc=${PIPESTATUS[0]}
  [ "$rc" -eq 0 ] || { say "publish of $task failed (exit $rc); stopping"; exit 4; }
done
