#!/usr/bin/env bash
# Print the SHA-256 list of the files that are reviewed and sealed before the first push (to stdout; redirect it
# to FILES-SHA256.txt, and seal that file the usual way). Local files only; nothing here talks to Kaggle.
# The last three lines are files of the sealed coat-check update (t5, t6) that this folder reads and compares with
# (its coatcheck.py and its two task files); their hashes are listed so that a change there is seen by the preflight.
#
#   bash make-file-list.sh > FILES-SHA256.txt
set -u
cd "$(dirname "$0")" || exit 1
SEALED=../kaggle-coat-check-update-2026-10-07
sha256sum -b \
  tasks/receipt-triplets-t7-coat-check-blind-report.py \
  tasks/receipt-triplets-t8-coat-check-blind-do.py \
  blindcheck.py build_blind_tasks.py blindcheck_analysis.py blindcheck_dryrun.py blindcheck_fakeruns.py \
  test_blindcheck.py test_blind_runner.py \
  blindcheck-common.sh run-blindcheck.sh push-blindcheck.sh make-file-list.sh \
  PREDICTIONS.md COMMANDS.md dryrun-2026-10-07.log \
  $SEALED/coatcheck.py \
  $SEALED/tasks/receipt-triplets-t5-coat-check-report.py \
  $SEALED/tasks/receipt-triplets-t6-coat-check-do.py
