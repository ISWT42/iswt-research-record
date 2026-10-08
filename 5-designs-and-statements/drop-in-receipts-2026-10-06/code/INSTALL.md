# Install: drop-in receipts, step 1 (the Claude Code hook)

**Status: built and tested; not installed anywhere.** Adding the snippet below to a settings file is the owner's decision.

When an agent says it is finished, this hook looks at each "done" claim in its final message and checks it against what the agent's tools actually printed in that turn. Each claim gets one of three answers:

- **shown**: a line a tool printed settles it, and the card quotes that line and says which tool call printed it;
- **contradicted**: a line (or a non-zero exit code) shows it failed, quoted the same way;
- **not shown (needs a reader)**: nothing settles it. This is the answer whenever the rules cannot decide. A model that reads the wording is a later step and is off.

It never reads the agent's own summary as evidence. It uses no model and no network.

## What you need

- Node.js 18 or newer. It has no dependencies, so there is nothing to install. It has been run on Node 26.7.0 only.
- The file `stop-check.mjs` and the `src` folder next to it. On this PC they are in
  `<home>/Workbench/drop-in-receipts-2026-10-06/code/`.

## Try it first, without installing anything

From the `code` folder, on a made-up transcript (`examples/demo-transcript.jsonl`, written for this purpose):

    echo '{"transcript_path":"examples/demo-transcript.jsonl","hook_event_name":"Stop"}' | node stop-check.mjs --no-receipts --no-system-message

You should see a card like this (3 claims: one shown, one contradicted, one not shown). In PowerShell, put the JSON in single quotes and pipe it the same way. (Without `--no-system-message` the hook also prints the card once more as a line of JSON on stdout; that is how Claude Code receives it.)

    Receipts (floor, not box): 3 claims checked: 1 shown, 1 contradicted, 1 not shown.
      shown: "All tests pass."
        line: 12 passed in 0.50s
        from: Bash call toolu_demo_tests: pytest -q
      contradicted: "I pushed the fix to origin/fix-parser."
        line: ! [rejected]        fix-parser -> fix-parser (fetch first)
        from: Bash call toolu_demo_push: git push origin fix-parser
      not shown (needs a reader): "I deployed it to production."
        why: no tool call in this turn did that operation
    Floor, not box: this reads what the harness recorded of the tools' output. ...
    Mode: report (the stop is allowed).

## Report mode (the default): show the card, never stop the agent

Add this to the top-level `"hooks"` object of a Claude Code settings file. If the file already has a `"Stop"` list (this PC has one, for `rule-ask.mjs`), add the new entry **to that list** and keep what is there. Do not replace it.

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "node \"<home>/Workbench/drop-in-receipts-2026-10-06/code/stop-check.mjs\"", "timeout": 30 } ] }
    ],
    "SubagentStop": [
      { "hooks": [ { "type": "command", "command": "node \"<home>/Workbench/drop-in-receipts-2026-10-06/code/stop-check.mjs\"", "timeout": 30 } ] }
    ]
  }
}
```

Which file: `~/.claude/settings.json` covers every project; `.claude/settings.local.json` inside one project covers only that project and is not shared. Trying it in one project first is the gentler start. Claude Code reads hooks when it starts, so restart it (or open `/hooks`) after the edit.

The card goes to stderr and is also handed to Claude Code as a message to the person. The agent is never stopped.

## Gate mode: the agent must cite a receipt or retract

The same entries with `--gate` after the path:

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "node \"<home>/Workbench/drop-in-receipts-2026-10-06/code/stop-check.mjs\" --gate", "timeout": 30 } ] }
    ],
    "SubagentStop": [
      { "hooks": [ { "type": "command", "command": "node \"<home>/Workbench/drop-in-receipts-2026-10-06/code/stop-check.mjs\" --gate", "timeout": 30 } ] }
    ]
  }
}
```

When any claim is **not shown** or **contradicted**, the agent is stopped once and told which claims have no receipt. It must run the command that would show each one and cite the exact line the tool printed, or retract the claim and say what is not done. It is never stopped a second time in the same turn, so it cannot be trapped: the hook checks both the flag Claude Code sets when an agent is already continuing because of a stop hook, and its own gate message in the turn's record. If the check itself fails for any reason (no transcript path, an unreadable file, an error), the agent is allowed to stop and the person gets a one-line message saying the check did not run, so a broken hook does not look like a turn with nothing to check.

Use gate mode for anything that matters, or for an agent that might talk past a card. Start with report mode to see how often it fires.

## Floor, not box

From the spec (sealed 6 Oct 2026):

> It reads the tool output the harness captured: command results, exit codes, test reports, HTTP status. It never reads the agent's own summary of them.
> That is rung 3 of his ladder, a record outside the agent's word, as far as the harness keeps it honest.
> **It is the floor, not the box.** An agent that can write the files the check reads can still fake them. The box, with a record kept out of the agent's reach, is the full version. The card says which one the user has.

In plain words: this hook is the floor. It reads the session record that Claude Code writes, and an agent that can edit that record, or make a tool print a line, can fool it. The card says "floor, not box" every time so nobody mistakes it for the box.

## What it checks, by rule

- exit codes: non-zero is a failure; zero alone is never a success for the claimed object, so a claim still needs a line that says what happened;
- test summaries: pytest, node --test, jest, vitest, mocha, go test, cargo test, maven, unittest, rspec, dotnet, with failure counts. "0 failed", "0 errors" and similar are read as zeros, never as failures;
- HTTP status lines, git push, merge and commit output, `gh pr merge`, the address `gh pr create` / `gh issue create` prints, and a few build lines;
- the claim must be about the same thing the tool output is about: a different branch (including "pushed to main" when `feature` was pushed), pull request or issue number, environment, host, version or file means "not shown". Reads, echoes and dry runs (`cat`, `grep`, `echo`, `git status`, `git push --dry-run`, `npm publish --dry-run`) never settle a "done" claim;
- a test run whose summary says "5 passed" but whose suite or file failed to run (jest "Test Suites: 1 failed", vitest "Test Files 1 failed") is a failure.

A claim sentence is taken only in a positive past, perfect or state form ("I pushed", "has been merged", "tests pass", "is live"). Plans, questions, instructions, hedges, negations and partial claims are skipped, so a missed claim is only a missed check and nothing is blocked for a claim that was never made.

## Receipts file

Every checked claim is written as one JSON line to `~/.drop-in-receipts/receipts.jsonl` (on this PC `<home>\.drop-in-receipts\receipts.jsonl`). The file is append-only. Each line carries its own SHA-256 and the SHA-256 of the line before it, so a changed, removed or inserted line is detectable. A line keeps the claim (credentials redacted), the answer, the quoted line, the tool call it came from (the command, cut to 300 characters, credentials redacted), and the SHA-256 of that tool's output; it does not keep the output itself. The redaction catches the usual credential shapes (tokens, passwords in `NAME=value` and `--flag value` form, Authorization headers, URL passwords, private keys) but it is a filter, not a guarantee, and a quoted line can still hold a file name or a host name. The file stays on this machine; nothing sends it anywhere.

Check the file at any time:

    node stop-check.mjs --verify                 (the default file)
    node stop-check.mjs --verify path/to/receipts.jsonl

It prints "receipts OK" and exits 0, or names the first problems and exits 1.

## Options

| Flag | Environment variable | Meaning |
|---|---|---|
| `--gate` / `--report` | `DROP_IN_RECEIPTS_MODE=gate` or `report` | the mode (default report) |
| `--receipts <file>` | `DROP_IN_RECEIPTS_FILE` | where receipts go |
| `--no-receipts` | | write no receipts file |
| `--no-system-message` | | print the card to stderr only; do not also hand it to Claude Code |
| `--reader off` | `DROP_IN_RECEIPTS_READER` | the model reader is step 2 and is not built; any other value is refused with a note and the rules still run |
| `--verify [file]` | | check a receipts file instead of running as a hook |

## What it does not do yet

- It is conservative about what counts as a claim. "Done." on its own, "I updated the README", and a bare "was sent" are not taken as claims.
- The rules cover tests, builds, git, HTTP and exit codes. Anything else (a deploy through a tool it does not know, a mail sent through an unknown program) comes out as "not shown (needs a reader)". That is the honest answer, and it is also why gate mode may stop an agent whose claim was true. The model reader is step 2.
- A completed run before a later edit can go stale: the card notes when a file edit came after the tool call it relied on.
- It checks one turn at a time: a claim about something done in an earlier turn is "not shown" in this one.
- The MCP server, the GitHub Action, packaging and a one-line install are steps 2 to 4. Publishing is the owner's decision.

## Take it out

Delete the two entries from the settings file and restart Claude Code. The receipts file stays where it is; delete it if you want it gone.

## Tests

From the `code` folder: `node --test` (synthetic transcripts only; no real conversation is ever read). Node also lists two helper files in `test/` as passing no-op tests, so the count it prints is two higher than the number of real tests. The replay of test 1 on the deterministic layer is `node replay/replay.mjs`; it reads two files outside this folder and writes its results into `replay/`.
