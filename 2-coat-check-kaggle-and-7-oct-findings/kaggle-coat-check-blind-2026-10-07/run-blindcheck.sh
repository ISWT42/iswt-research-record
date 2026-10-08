#!/usr/bin/env bash
# Blind coat-check runs (t7, t8) on Kaggle, private. Needs the owner's yes for spending, given for this script's caps;
# written 7 Oct 2026 for review, copied from run-coatcheck.sh of the coat-check update (t5, t6) and pointed at t7 and t8. NOT RUN.
#
# Works through the run plan of blindcheck_analysis.py (PLAN): tasks in the order given by ARMS (default T8 T7);
# per task, every core model up to its planned usable runs (3), the models that still need runs going in
# parallel, one round at a time. Usable and counted come from blindcheck_analysis.py need, which applies the
# counting rules of the entry's own run plan.
# Before every round: recorded spend today (UTC) <= DAY_CAP - ROUND_MAX, last 24 h (rolling) <= ROLL_CAP - ROUND_MAX,
# total spend of these two tasks (t7, t8) <= TOTAL_CAP - ROUND_MAX, and the clock before STOP_AT. Stops on the first quota
# refusal. Nothing is published.
#
# Two changes against run-triplets.sh, both so that a broken helper stops the run instead of letting it go on:
#   - the answer of the "need" helper is read into a variable first; if the helper fails or prints nothing the
#     script stops, where an empty answer would otherwise read as "all runs done";
#   - every spend figure must be a number; if a helper prints anything else the script stops, where an
#     unreadable figure would otherwise read as "under the cap".
# The first round of the first task runs the canary model alone and checks its run (usable, Kaggle's own
# results equal to the re-score, replies read) before the other models start.
#
#   STOP_AT=YYYY-MM-DDTHH:MM:SSZ bash run-blindcheck.sh          (STOP_AT is the stop time written in the forecast file)
set -u
. "$(dirname "$0")/blindcheck-common.sh"
ARMS=${ARMS:-"T8 T7"}
DAY_CAP=${DAY_CAP:-6.00}; ROLL_CAP=${ROLL_CAP:-7.50}; TOTAL_CAP=${TOTAL_CAP:-15.00}; ROUND_MAX=${ROUND_MAX:-0.75}
EXTRA_TRIES=${EXTRA_TRIES:-3}
ROUND_SLEEP=${ROUND_SLEEP:-15}
STOP_AT=${STOP_AT:?set STOP_AT, a UTC time as YYYY-MM-DDTHH:MM:SSZ, the stop time of the sealed run plan}
CANARY_MODEL=${CANARY_MODEL-gpt-5.4-nano-2026-03-17}   # empty = no canary
LOG=$RESULTS/run-blindcheck.log
over() { "$PY" -c "import sys; sys.exit(0 if float(sys.argv[1]) > float(sys.argv[2]) - float(sys.argv[3]) else 1)" "$1" "$2" "$ROUND_MAX"; }
[[ "$STOP_AT" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$ ]] || { echo "STOP_AT must look like 2026-10-09T12:00:00Z, not: $STOP_AT"; exit 1; }
stop=$(date -u -d "$STOP_AT" +%s) || { echo "STOP_AT is not a time: $STOP_AT"; exit 1; }
for arm in $ARMS; do [ -n "${TASK[$arm]:-}" ] || { echo "unknown task $arm (T7 or T8)"; exit 1; }; done

say "start: tasks $ARMS; caps day \$$DAY_CAP, rolling 24 h \$$ROLL_CAP, total \$$TOTAL_CAP, round reserve \$$ROUND_MAX; stop $STOP_AT"
preflight
first_round=1
for arm in $ARMS; do
  declare -A tries=()
  while :; do
    out=$(ca need "$arm" --results "$RESULTS" --stop "$STOP_AT") || { say "the need helper failed for $arm; stopping"; exit 6; }
    [ -n "$out" ] || { say "the need helper printed nothing for $arm; stopping"; exit 6; }
    need=(); task=""; gave_up=0
    while read -r t m usable planned all; do
      task=$t
      [ "$usable" -ge "$planned" ] && continue
      if [ "${tries[$m]:-0}" -ge $((planned + EXTRA_TRIES)) ]; then
        say "GAVE UP $arm $m at $usable/$planned usable after ${tries[$m]} tries"; gave_up=$((gave_up + 1)); continue
      fi
      need+=("$m")
    done <<< "$out"
    [ "$task" = "${TASK[$arm]}" ] || { say "the need helper named $task, not ${TASK[$arm]}; stopping"; exit 6; }
    if [ "${#need[@]}" -eq 0 ]; then
      [ "$gave_up" -gt 0 ] && { say "$arm NOT done: gave up on $gave_up model(s)"; exit 8; }
      say "$arm done"; break
    fi
    now=$(date -u +%s)
    [ "$now" -ge "$stop" ] && { say "STOP TIME reached; no new run"; exit 4; }
    day=$("$PY" kaggle/day_spend.py)
    roll=$("$PY" results/probe-2026-10-01/spend_windows.py | grep 'last 24 hours' | sed 's/.*\$//')
    total=$(ca spend --results "$RESULTS")
    for v in "$day" "$roll" "$total"; do is_number "$v" || { say "a spend figure is not a number ('$v'); stopping"; exit 7; }; done
    if over "$day" "$DAY_CAP"; then say "DAY CAP: \$$day today; resume after 00:00 UTC"; exit 2; fi
    if over "$roll" "$ROLL_CAP"; then say "ROLLING CAP: \$$roll in the last 24 h; resume later"; exit 2; fi
    if over "$total" "$TOTAL_CAP"; then say "TOTAL CAP: \$$total for the blind coat-check tasks"; exit 2; fi
    canary=0
    if [ "$first_round" -eq 1 ] && [ -n "$CANARY_MODEL" ]; then
      for m in "${need[@]}"; do [ "$m" = "$CANARY_MODEL" ] && canary=1; done
      [ "$canary" -eq 1 ] && need=("$CANARY_MODEL")
    fi
    margs=(); for m in "${need[@]}"; do margs+=(-m "$m"); tries[$m]=$(( ${tries[$m]:-0} + 1 )); done
    say "run $task ($arm) on ${need[*]} (spend today \$$day, 24 h \$$roll, total \$$total)"
    timeout 5400 "$K" b t run "$task" "${margs[@]}" --wait 5000 2>&1 | grep -v -i -E "token|bearer" | grep -E "COMPLETED|ERRORED|rror" | tail -8 >> "$LOG"
    for m in "${need[@]}"; do "$K" b t download "$task" -o "$RESULTS" -m "$m" >/dev/null 2>&1 || say "  download failed: $m"; done
    if grep -l -r "exceeds your available quota" "$RESULTS"/"$task" --include='*.run.json' -q 2>/dev/null; then
      newest=$(grep -l -r "exceeds your available quota" "$RESULTS"/"$task" --include='*.run.json' | xargs ls -t | head -1)
      [ -n "$newest" ] && [ "$(find "$newest" -mmin -30 | wc -l)" -gt 0 ] && { say "QUOTA refusal in $newest; stopping"; exit 3; }
    fi
    if [ "$canary" -eq 1 ]; then
      out=$(ca check "$arm" "$CANARY_MODEL" --results "$RESULTS"); rc=$?
      echo "$out" | tee -a "$LOG"
      [ "$rc" -eq 0 ] || { say "CANARY FAILED on $CANARY_MODEL ($task); no other model was started"; exit 5; }
      say "canary passed on $CANARY_MODEL"
    fi
    first_round=0
    ca need "$arm" --results "$RESULTS" --stop "$STOP_AT" | sed 's/^/  usable: /' | tee -a "$LOG"
    sleep "$ROUND_SLEEP"
  done
done
say "all tasks done"
analysis="$RESULTS/analysis-blindcheck-$(date -u +%Y-%m-%d).txt"
if ca report --results "$RESULTS" --stop "$STOP_AT" --predictions "$UPD/PREDICTIONS.md" > "$analysis"; then
  say "analysis written to $analysis"
else
  say "the analysis helper failed; run it by hand: blindcheck_analysis.py report"; exit 9
fi
