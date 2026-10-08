> Published copy. The sealed original `SPEC.md` (SHA-256 `2f3fe412d2d6841677d41ffc7c55362a5078b6487c4da1e77c771a9166337bd1`) is not published; its hash is in the seal list beside it.
> This copy differs from it only where marked or listed here: 1 forecast section(s) or paragraph(s) removed.

# Drop-in receipts: a "done" check any agent setup can install in one line (design; Claude, 6 Oct 2026)

**His go:** "of course. you can do that" (15:41 UTC), after his "it is a future that can be 100% real if it is adopted by others" (15:40 UTC). The aim is adoption: the ISWT Protocol running inside tools people already use, at no cost to them.

## What it does
When an agent reports a task finished, the check reads what the agent's tools actually printed and gives one of three answers:
- **shown**, quoting the exact line that settles it;
- **contradicted**, quoting the line that shows it failed;
- **not shown**, when nothing settles it.

The person sees a small receipt card. In gate mode, the next step can't run without "shown".

## The record it reads, and why that matters
- It reads the tool output the harness captured: command results, exit codes, test reports, HTTP status. It never reads the agent's own summary of them.
- That is rung 3 of his ladder, a record outside the agent's word, as far as the harness keeps it honest.
- **It is the floor, not the box.** An agent that can write the files the check reads can still fake them. The box, with a record kept out of the agent's reach, is the full version. The card says which one the user has.

## Where it plugs in (in order of reach)
1. **A Claude Code hook.** It runs on `Stop` and `SubagentStop`. It takes the turn's completion claims from the final message and checks each against the tool results in the session record, then prints a receipt card.
   - Gate mode returns the "block" signal when a claim is "not shown" or "contradicted", so the agent must cite a receipt or retract.
   - Precedent: this very session already runs a hook that records doubts.
2. **An MCP server.** It offers a `check_done(claim, evidence)` tool that any agent framework can call, and a `receipts` resource listing past checks. One config line adds it to Claude Code, Cursor and other clients.
3. **A GitHub Action.** When a pull request says "tests pass" or "done", it checks that against the CI logs and posts the receipt as a check run.
4. **The library:** `receipt_pair` as a pip package. It already exists, standard library only, MIT.

## How it checks: the findings, used as defaults
- **Deterministic first.** Exit codes, test summaries, HTTP status and hashes are decided by rules, with no model call. That costs microseconds instead of a model call (his logic-gate point, 14:55 UTC).
- **A model only where wording must be read.** Two small local models (Lemonade, or any OpenAI-compatible endpoint), each required to quote the exact line. A quote not word for word in the record becomes "not shown" (F1, F5).
- **Name the receipt first.** Before reading, write down the line that would settle the claim (F11, F14: false "shown" fell from 44 to 25 of 240).
- **Never force a yes or no.** "Not shown" is always allowed (F13).
- **Pair rule:** "shown" needs both checkers (F12).
- **Optional unanimity:** ask several times and pass only a unanimous "shown" (F16).
- **The told rule for reviewers:** "approve only if a line shows it, and quote it" (F17).
- **The gate**, for anything that matters or anyone who might talk past it (F15).

## Rules it keeps
- Local-first. No telemetry, accounts or network calls beyond the model endpoint the user chooses.
- Receipts are written to a local append-only file with each record's SHA-256. Optional FreeTSA or OpenTimestamps sealing of a session's receipts.
- Plain output: the three answers, the quoted line, the source (which tool call), and "floor, not box".

## How we'll know it works (to be sealed before it runs)
1. **Replay:** feed the sealed logs of S2, S4 and S8 through it and count false "shown" and true "shown" against the keys. It must match receipt_pair's sealed results.
2. **Live:** the same coding tasks with and without the hook. Count false "done" reaching the user, true "done" blocked, and minutes and tokens.
   - [forecast bullet removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
3. **Cost:** tokens spent on checking with deterministic-first against model-first. **Forecast:** deterministic rules settle at least half of claims with no model call.

## Order of work
1. The hook and the deterministic rules, then replay test 1.
2. The MCP server.
3. The Action.
4. Packaging, an install line, and a README in plain words with the floor-and-box ladder.

**Publishing it is his yes.**
