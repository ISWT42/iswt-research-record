#!/usr/bin/env bash
# Print the SHA-256 list of the files that are reviewed and sealed before the first push (to stdout; redirect it
# to FILES-SHA256.txt, and seal that file the usual way). UPDATE-DRAFT.md is not listed: its placeholders are
# filled after the runs. Local files only; nothing here talks to Kaggle.
#
#   bash make-file-list.sh > FILES-SHA256.txt
set -u
cd "$(dirname "$0")" || exit 1
sha256sum -b \
  tasks/receipt-triplets-t5-coat-check-report.py \
  tasks/receipt-triplets-t6-coat-check-do.py \
  coatcheck.py build_coatcheck_tasks.py coatcheck_analysis.py coatcheck_dryrun.py coatcheck_fakeruns.py \
  test_coatcheck.py test_runner.py mutation_checks.py \
  coatcheck-common.sh run-coatcheck.sh push-coatcheck.sh publish-coatcheck.sh make-file-list.sh \
  PREDICTIONS.md COMMANDS.md dryrun-2026-10-07.log
