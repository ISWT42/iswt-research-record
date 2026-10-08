#!/usr/bin/env node
// Drop-in receipts, step 1: a Claude Code hook for Stop and SubagentStop. When the agent says it is finished, this
// reads what its tools printed in the turn (never the agent's own summary of it) and answers each completion claim in
// the final message with one of three answers: shown (and the exact line), contradicted (and the exact line), or
// not shown. Deterministic rules only; no model, no network, nothing leaves the machine.
//
//   report mode (default)  prints a small receipt card to stderr and lets the agent stop
//   gate mode  (--gate)    also returns {"decision":"block"} once per turn when a claim is not shown or contradicted,
//                          so the agent must cite a receipt or retract (it never blocks twice in a row)
//
// It is the floor, not the box: an agent that can write the record it reads, or make a tool print a line, can fake it.
//
// Install: see INSTALL.md. Options (flags, or the environment variable beside each):
//   --gate | --report          DROP_IN_RECEIPTS_MODE=gate|report
//   --receipts <file>          DROP_IN_RECEIPTS_FILE   (default ~/.drop-in-receipts/receipts.jsonl)
//   --no-receipts              write no receipts file
//   --no-system-message        do not also hand the card to Claude Code as a systemMessage
//   --reader <name>            the model reader is step 2 and not built; anything but "off" is refused with a note
//   --verify [file]            check a receipts file instead of running as a hook: recompute every SHA-256 and the chain
//                              (exit 0 when intact, 1 when not, 2 when the file cannot be read)
import { readFileSync, realpathSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { parseJsonl, readTail, turnEvidence } from './src/transcript.mjs';
import { extractClaims } from './src/claims.mjs';
import { checkTurn } from './src/check.mjs';
import { renderCard, gateReason } from './src/card.mjs';
import { appendReceipts, buildReceipt, defaultReceiptsPath, verifyReceipts } from './src/receipts.mjs';
import { sha256 } from './src/text.mjs';

export function parseArgs(argv = [], env = {}) {
  const opts = {
    mode: env.DROP_IN_RECEIPTS_MODE === 'gate' ? 'gate' : 'report',
    receipts: env.DROP_IN_RECEIPTS_FILE || null,
    noReceipts: false,
    systemMessage: true,
    reader: env.DROP_IN_RECEIPTS_READER || 'off',
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--gate') opts.mode = 'gate';
    else if (a === '--report') opts.mode = 'report';
    else if (a === '--no-receipts') opts.noReceipts = true;
    else if (a === '--no-system-message') opts.systemMessage = false;
    else if (a === '--receipts' && argv[i + 1]) opts.receipts = argv[++i];
    else if (a.startsWith('--receipts=')) opts.receipts = a.slice('--receipts='.length);
    else if (a === '--reader' && argv[i + 1]) opts.reader = argv[++i];
    else if (a.startsWith('--reader=')) opts.reader = a.slice('--reader='.length);
  }
  return opts;
}

// Which transcript, and which records of it, belong to the agent that just stopped.
function transcriptFor(input) {
  const event = input.hook_event_name ?? 'Stop';
  if (event === 'SubagentStop') {
    if (input.agent_transcript_path) return { path: input.agent_transcript_path, scope: 'agent' };
    return { path: input.transcript_path, scope: 'sidechain-only' };
  }
  return { path: input.transcript_path, scope: 'main' };
}

// The whole hook as a function: hook input in, what to write out. {stdout, stderr}; stdout is JSON text or null.
export function runHook(input = {}, options = {}) {
  const opts = { mode: 'report', noReceipts: false, systemMessage: true, reader: 'off', ...options };
  const notes = [];
  if (opts.reader && opts.reader !== 'off') notes.push(`drop-in-receipts: the model reader is step 2 and is not built; running the deterministic rules only (asked for reader "${opts.reader}").`);

  // Something is wrong with the check itself: say so where the person sees it (stderr alone is not shown for an exit-0
  // hook), or a broken hook would look the same as a turn with nothing to check. The stop is allowed.
  const failure = (note) => {
    const message = [...notes, note].join('\n');
    return { stdout: opts.systemMessage ? JSON.stringify({ systemMessage: message }) : null, stderr: message };
  };

  const { path, scope } = transcriptFor(input);
  if (!path) return failure('drop-in-receipts: the hook input has no transcript path; nothing checked, the stop is allowed.');

  let records;
  try {
    records = parseJsonl(readTail(path));
  } catch (error) {
    return failure(`drop-in-receipts: could not read the transcript (${error.code ?? error.message}); nothing checked, the stop is allowed.`);
  }

  const turn = turnEvidence(records, { scope, lastAssistantMessage: input.last_assistant_message });
  const claims = extractClaims(turn.finalMessage);
  if (claims.length === 0) return { stdout: null, stderr: notes.length ? notes.join('\n') : null };

  const { results } = checkTurn(turn, claims);
  const receiptsPath = opts.noReceipts ? null : (opts.receipts || defaultReceiptsPath());
  const lines = [...notes];

  if (receiptsPath) {
    try {
      const context = {
        event: input.hook_event_name ?? 'Stop', session_id: input.session_id ?? null, agent_id: input.agent_id ?? null,
        mode: opts.mode, message_sha256: sha256(turn.finalMessage),
      };
      appendReceipts(receiptsPath, results.map((r) => buildReceipt(r, context)));
    } catch (error) {
      lines.push(`drop-in-receipts: could not write the receipts file (${error.code ?? error.message}); the check still ran.`);
    }
  }

  // Once per turn, by two guards: the harness says the agent is already continuing because of a stop hook, or this hook's
  // own gate message is already in the turn's record.
  const open = results.some((r) => r.answer !== 'shown');
  const block = opts.mode === 'gate' && open && input.stop_hook_active !== true && !turn.gateSeen;
  const card = renderCard(results, { mode: opts.mode, receiptsPath, gated: block });
  lines.push(card);

  const out = {};
  if (block) { out.decision = 'block'; out.reason = gateReason(results); }
  if (opts.systemMessage) out.systemMessage = lines.join('\n');          // the card, and any warning that came with it
  return { stdout: Object.keys(out).length ? JSON.stringify(out) : null, stderr: lines.join('\n') };
}

// --verify: {text, code} for a receipts file.
export function verifyText(file) {
  try {
    const result = verifyReceipts(file);
    const lines = `${result.lines} line${result.lines === 1 ? '' : 's'}`;
    if (result.ok) return { text: `receipts OK: ${lines}, every SHA-256 recomputed, the chain unbroken (${file}).`, code: 0 };
    const listed = result.problems.slice(0, 20).map((p) => `  line ${p.line}: ${p.problem}`);
    if (result.problems.length > 20) listed.push(`  ... and ${result.problems.length - 20} more`);
    return { text: [`receipts NOT OK: ${result.problems.length} problem${result.problems.length === 1 ? '' : 's'} in ${lines} (${file}).`, ...listed].join('\n'), code: 1 };
  } catch (error) {
    return { text: `drop-in-receipts: cannot read ${file} (${error.code ?? error.message})`, code: 2 };
  }
}

function main() {
  const argv = process.argv.slice(2);
  const v = argv.indexOf('--verify');
  if (v >= 0) {
    const file = argv[v + 1] && !argv[v + 1].startsWith('--') ? argv[v + 1] : (process.env.DROP_IN_RECEIPTS_FILE || defaultReceiptsPath());
    const out = verifyText(file);
    (out.code === 2 ? process.stderr : process.stdout).write(out.text + '\n');
    process.exitCode = out.code;
    return;
  }
  let input = {};
  try { input = JSON.parse(readFileSync(0, 'utf8') || '{}'); } catch { return; }
  const result = (() => {
    const options = parseArgs(process.argv.slice(2), process.env);
    try { return runHook(input, options); }
    catch (error) {
      const note = `drop-in-receipts: the check failed (${error.message}); nothing blocked, the stop is allowed.`;
      return { stdout: options.systemMessage ? JSON.stringify({ systemMessage: note }) : null, stderr: note };
    }
  })();
  if (result.stderr) process.stderr.write(result.stderr + '\n');
  if (result.stdout) process.stdout.write(result.stdout);
}

let isMain = false;
try { isMain = Boolean(process.argv[1]) && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href; } catch { isMain = false; }
if (isMain) main();
