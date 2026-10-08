#!/usr/bin/env bash
# Shared set-up of the blind coat-check scripts (run-blindcheck.sh, push-blindcheck.sh).
# Source it; do not run it. It runs nothing against Kaggle by itself.
#
# Written 7 Oct 2026 for review, copied from the scripts of the coat-check update (t5, t6) and pointed at t7 and t8. The scripts work from
# the entry's folder (REPO), as run-triplets.sh does, and keep this folder's files out of it.

UPD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO=${REPO:-"$HOME/Desktop/Moonshots/kaggle/claimed-vs-proven"}
cd "$REPO" || { echo "no entry folder at $REPO"; exit 1; }
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
K=${K:-.venv/Scripts/kaggle.exe}
PY=${PY:-.venv/Scripts/python.exe}
RESULTS=${RESULTS:-results/kaggle}
SEAL=ENTRY/SEAL-MANIFEST-2026-10-01.json
mkdir -p "$RESULTS"

# main task of each coat-check arm; a test compares these with build_blind_tasks.task_name
declare -A TASK=([T7]=receipt-triplets-t7-coat-check-blind-report [T8]=receipt-triplets-t8-coat-check-blind-do)

say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG"; }
ca() { "$PY" -B "$UPD/blindcheck_analysis.py" "$@"; }
is_number() { [[ "$1" =~ ^[0-9]+(\.[0-9]+)?$ ]]; }

# What was reviewed is what runs: the listed files unchanged, the entry's own seal unchanged, the task files
# equal to a fresh build. Any failure stops the script (exit 10).
preflight() {
  say "preflight: listed files, the entry's seal, a fresh build of the task files"
  if [ ! -f "$UPD/FILES-SHA256.txt" ]; then say "no FILES-SHA256.txt in $UPD; make it with make-file-list.sh after review"; exit 10; fi
  if grep -q '\[FILL' "$UPD/PREDICTIONS.md"; then say "PREDICTIONS.md still has [FILL] items; fill them before sealing; stopping"; exit 10; fi
  if grep -q -E '^\| B[0-9]+ \| p = \? \||^B[0-9]+ +\? ' "$UPD/PREDICTIONS.md"; then say "PREDICTIONS.md still has a probability left as ?; the coordinator sets them before sealing; stopping"; exit 10; fi
  if ! ( cd "$UPD" && sha256sum -c FILES-SHA256.txt --quiet ); then
    say "a listed file differs from FILES-SHA256.txt (changed after the list was made); stopping"; exit 10
  fi
  local out rc
  out=$("$PY" -B kaggle/seal_manifest.py verify "$SEAL" 2>&1); rc=$?
  if [ "$rc" -ne 0 ]; then say "the entry's seal does not verify; stopping"; echo "$out" | tail -5 | tee -a "$LOG"; exit 10; fi
  say "seal verifies: $(echo "$out" | grep 'items unchanged')"
  out=$("$PY" -B "$UPD/build_blind_tasks.py" --check 2>&1); rc=$?
  if [ "$rc" -ne 0 ]; then say "the task files are not a fresh build: $out; stopping"; exit 10; fi
  say "$out"
  out=$("$PY" -B "$UPD/build_blind_tasks.py" --leaks 2>&1); rc=$?
  if [ "$rc" -ne 0 ]; then say "a ticket states a result value: $out; stopping"; exit 10; fi
  say "$out"
}
