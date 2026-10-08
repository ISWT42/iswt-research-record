# Amendment from the coordinator, before sealing (8 Oct 2026, after the owner's words at 02:02 UTC)

Copied word for word from the coordinator's message to the builder. DESIGN.md cites the lines as AMEND 1 to AMEND 3.

Owner's words, 8 Oct 02:02 UTC, as the coordinator gave them: "ensure we have the flexibility to test the different combinations"

AMEND 1. "Make arms composable from factors, so new combinations need only a config entry, not code. Factors: ticket (off/on); certify (none / all / routed-by-table); routing (equal / record / random) where routing only applies when certify or work share is routed; and a separate work-share switch (equal / by-table) so work share and checking can be varied apart — this answers your choice C2 (the confound). Keep A to E as named presets with exactly their current behaviour (A = ticket off, certify none, equal; B = ticket on, certify none, equal; C = ticket on, certify all; D = ticket on, routed checking + routed work share, record; E = same as D with random). Add as available presets (not in the default run): D-check-only (routed checking, equal work share, record), D-work-only (equal checking at the floor-respecting fixed table, routed work share, record), and their random twins. Keep the guardrails as invariants for ANY combination: checks never zero (MIN_CHECKS=1 per agent per round whenever certify is routed), records keyed by exact model, forecast before work. The scorer must handle any preset set; the primary test stays D vs E and is declared in config; secondary comparisons are listed per preset pair in config before the run. Validate config at load (unknown factor value or a routed preset without its random twin -> refuse)."

AMEND 2. "C3: replace "qwen/qwen3-coder-30b-a3b-instruct" with {"id": "mistralai/mistral-small-3.2-24b-instruct", "family": "mistral", "price_in_per_m": 0.09375, "price_out_per_m": 0.25} (live OpenRouter list price, read 8 Oct 02:05 UTC). Note in DESIGN.md that it has not yet been called through the broker; the smoke test covers it."

AMEND 3. "Also record in DESIGN.md my decisions: C1 = hand-off is acceptance of one finished job (no chains); C2 = resolved by the new check-only / work-only presets (available, not default); C3 = swap above."

AMEND 4. "Then: full tests, check-jobs, a stand-in dry run of the default 5 arms plus one quick dry run including the four extra presets, mutation checks (add mutations for the new invariants), refresh the cost estimate, regenerate the file list for sealing (make the list, do not stamp)."
