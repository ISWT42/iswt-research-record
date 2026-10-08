> Published copy. The sealed original `AGREED-DESIGN-from-the-7-oct-handoff.md` (SHA-256 `16d8dc38f5803eb89bf326b718a6bce27e3fa7cbdab1a1be51bd6464272baa1d`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 4 forecast probabilities removed (marked "[forecast removed]"); 1 local folder path shortened (marked "[work folder]"); nothing else changed.

# The agreed design, as the coordinator handed it to the builder (8 Oct 2026, 00:24 UTC by the session clock)

Copied word for word from the builder's task message. DESIGN.md cites the lines as AGREED D1 to D8 and DELIV 1 to DELIV 8.

The owner's instruction that night (8 Oct 2026, 00:24 UTC): "Yes, earned agency bench. Make sure to translate the design properly."

"Translate means: turn his idea (sources/IDEA-2-earned-agency-his-words.md, his exact words) plus the agreed design below into a precise, testable protocol, where every design element is traced to its source line, and every place where translating required a choice is listed with the choice and why. Do not add features nobody asked for; do not drop any listed element. Use plain words and short sentences (he wants simple names for people; "the coat-check" is HIS name for the handoff check: a ticket written before the work names the check and what done means; at pickup it is matched: shown, contradicted, not shown)."

## AGREED DESIGN (from the 7 Oct handoff; this is the spec to translate)

D1. Jobs: hidden-test coding jobs (the agent never sees the tests that grade it). Jev round 4 leaned toward this [forecast removed].

D2. Models: 4 cheap model families via OpenRouter; never hard-code model names in the protocol (they go in a config file).

D3. 5 rounds. In each round every agent seals a forecast (probability its work passes the hidden tests) BEFORE working; after the round it gets feedback (its pass/fail and its calibration).

D4. Arms: (1) plain baseline (self-report); (2) one shared coat-check ticket (Jev: [forecast removed]); (3) relay v2 certify-only: a second agent certifies the first agent's work against the ticket and does NOT rewrite it (last night's relay showed certifiers caught 16/16 false done but their rewrites added errors; Jev [forecast removed]); (4) routing by track record (agents whose sealed forecasts have been more accurate get more agency at handoff, i.e., are routed more work / less checking) against (5) random routing as its control.

D5. Guardrails the coordinator set when sealing his idea: two separate scores (a) knows itself = forecast calibration, (b) record shows its done = hidden tests pass; checks are never reduced to zero for anyone, however good its record; records reset when the model changes.

D6. Measures: forecast calibration over rounds (Brier, and whether it improves round to round), pass rate, false "done" (agent says done, hidden tests fail), tokens, wall time, cost per passing job.

D7. Budget for the eventual run: about US$1 to 3 total, with a hard cap enforced in code (default US$3.00) and a per-run stop time.

D8. The biggest unknown named by Jev: whether earned agency is real [forecast removed]. The design must be able to say "not shown" honestly; include the no-room guard (if baseline false-done is near zero there's nothing to improve, say so).

## REUSE (from the task message)

"REUSE: [work folder]\coat-check-relay-2026-10-07 (relay.py, jobs.py, score_relay.py, standin.py, tests, DESIGN.md, COMMANDS.md) already runs 12 real coding jobs on 4 cheap models through OpenRouter with a cost cap. Read how it calls models (do not open any key file; the runner reads keys itself). Its result (sealed): false done at end of 36: self-report 16, coat-check+self-fix 7, relay certify-before-work 11, time-travel 9; self-forecasts overconfident (0.85-1.00 stated vs 0.31-0.74 pass)."

## DELIVERABLES (from the task message; the lines the design depends on)

DELIV 1. "TASK: Build the Earned Agency Bench, ready to seal and run, with NO spend and NO network calls to any model."

DELIV 2. "A job bank with hidden tests. Enough jobs for 5 rounds with fresh jobs each round (suggest at least 40 jobs; reuse/adapt the 12 relay jobs and write new ones). Each job: a prompt the agent sees, visible example tests (optional), hidden tests it never sees, a reference solution that passes the hidden tests (proven by a test), and a check that the hidden tests fail on a stub. Keep the hidden tests out of anything sent to a model (a test proves no hidden test text reaches any prompt)."

DELIV 3. "The runner (reuse relay.py patterns): arms, rounds, sealed forecasts per agent per job written to an append-only record before the work, feedback between rounds, routing by track record vs random, certify-only relay, cost cap, stop time, token/time logging, model list from config."

DELIV 4. "A scorer, sealed before results: computes every measure and the pre-decided tests."

DELIV 5. "A stand-in model (no network) and a full dry run of all arms and 5 rounds through it; save the log."

DELIV 6. "Tests (unit + script) and a few mutation checks showing the tests catch planted faults."

DELIV 7. "PREDICTIONS.md: the forecast statements for the coordinator to fill, with every probability left as "p = ?" (the coordinator sets them, not you)."

DELIV 8. "DESIGN.md: the translated design (question, arms, jobs, rounds, routing rule exactly, feedback exactly, measures, primary and secondary comparisons with their statistical tests decided in advance, sample size and power reasoning, no-room guard, what would count as "earned agency is real", limits). A "Translation table" section: each element, its source (quote), how it was made testable, any choice made."
