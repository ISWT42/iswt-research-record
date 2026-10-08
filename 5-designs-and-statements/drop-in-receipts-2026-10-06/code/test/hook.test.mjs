// The hook as Claude Code runs it: a subprocess with the hook input on stdin. Synthetic transcripts only.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { prompt, say, bash, transcript, writeTranscript, nextId, scratch } from './helpers.mjs';
import { verifyReceipts } from '../src/receipts.mjs';
import { runHook, parseArgs } from '../stop-check.mjs';
import { GATE_TAG } from '../src/text.mjs';

const hook = join(dirname(fileURLToPath(import.meta.url)), '..', 'stop-check.mjs');

function run({ records, args = [], input = {}, env = {}, receipts = true }) {
  const dir = scratch('h');
  const { path } = writeTranscript(records ?? [], dir);
  const receiptsFile = join(dir, 'receipts.jsonl');
  const hookInput = { session_id: 'sess-1', transcript_path: path, cwd: dir, hook_event_name: 'Stop', stop_hook_active: false, ...input };
  const proc = spawnSync(process.execPath, [hook, ...args], {
    input: JSON.stringify(hookInput), encoding: 'utf8',
    env: { ...process.env, DROP_IN_RECEIPTS_FILE: receiptsFile, DROP_IN_RECEIPTS_MODE: '', ...env },
  });
  const json = proc.stdout ? JSON.parse(proc.stdout) : null;
  return { status: proc.status, stdout: proc.stdout, stderr: proc.stderr, json, receiptsFile, dir };
}

const passingTests = (id = 'toolu_pass') => bash('pytest -q', '..........\n12 passed in 0.50s', { id });
const turn = (message, ...calls) => transcript(prompt('do it'), ...calls, say(message));

// ---- report mode (the default) ------------------------------------------------------------------------
test('report mode: prints the receipt card to stderr and lets the agent stop', () => {
  const r = run({ records: turn('All tests pass.', passingTests()) });
  assert.equal(r.status, 0);
  assert.match(r.stderr, /Receipts \(floor, not box\): 1 claim checked: 1 shown, 0 contradicted, 0 not shown\./);
  assert.match(r.stderr, /shown: "All tests pass\."/);
  assert.match(r.stderr, /line: 12 passed in 0\.50s/);
  assert.match(r.stderr, /from: Bash call toolu_pass: pytest -q/);
  assert.match(r.stderr, /Floor, not box:/);
  assert.match(r.stderr, /Mode: report \(the stop is allowed\)/);
  assert.equal(r.json.decision, undefined, 'report mode never blocks');
  assert.ok(r.json.systemMessage.includes('12 passed in 0.50s'), 'the card is also handed to Claude Code to show');
});

test('report mode: a contradicted claim and a claim with no receipt are shown on the card and still not blocked', () => {
  const r = run({ records: turn('I deployed to production. Pushed to origin/main.', bash('git push origin main',
    'To github.com:acme/tools.git\n ! [rejected]        main -> main (fetch first)', { exit: 1, id: 'toolu_push' })) });
  assert.equal(r.status, 0);
  assert.match(r.stderr, /2 claims checked: 0 shown, 1 contradicted, 1 not shown\./);
  assert.match(r.stderr, /contradicted: "Pushed to origin\/main\."/);
  assert.match(r.stderr, /line: ! \[rejected\]\s+main -> main \(fetch first\)/);
  assert.match(r.stderr, /not shown \(needs a reader\): "I deployed to production\."/);
  assert.equal(r.json.decision, undefined);
});

test('a message with no completion claims prints nothing and writes nothing', () => {
  const r = run({ records: turn('The parser has two bugs; the first is in the lexer.', passingTests()) });
  assert.equal(r.status, 0);
  assert.equal(r.stdout, '');
  assert.equal(r.stderr, '');
  assert.equal(existsSync(r.receiptsFile), false);
});

// ---- gate mode ------------------------------------------------------------------------------------------
test('gate mode: blocks once when a claim is not shown, telling the agent to cite a receipt or retract', () => {
  const r = run({ records: turn('I deployed the app to production.'), args: ['--gate'] });
  assert.equal(r.status, 0);
  assert.equal(r.json.decision, 'block');
  assert.ok(r.json.reason.startsWith(GATE_TAG));
  assert.match(r.json.reason, /NOT SHOWN: "I deployed the app to production\."/);
  assert.match(r.json.reason, /cite the exact line the tool printed, or retract the claim/);
  assert.match(r.stderr, /Mode: gate \(the agent was told to cite a receipt or retract\)/);
});

test('gate mode: blocks on a contradicted claim and quotes the line that contradicts it', () => {
  const r = run({ records: turn('All tests pass.', bash('pytest -q', 'F.\n1 failed, 11 passed in 0.50s', { exit: 1, id: 'toolu_f' })), args: ['--gate'] });
  assert.equal(r.json.decision, 'block');
  assert.match(r.json.reason, /CONTRADICTED: "All tests pass\."/);
  assert.match(r.json.reason, /printed: "1 failed, 11 passed in 0\.50s"/);
});

test('gate mode: does not block a second time in the same turn (stop_hook_active), and still prints the card', () => {
  const records = turn('I deployed the app to production.');
  const first = run({ records, args: ['--gate'] });
  assert.equal(first.json.decision, 'block');
  const second = run({ records, args: ['--gate'], input: { stop_hook_active: true } });
  assert.equal(second.status, 0);
  assert.equal(second.json.decision, undefined, 'once per turn');
  assert.match(second.stderr, /not shown \(needs a reader\)/);
  assert.match(second.stderr, /Mode: gate \(nothing blocked\)/);
});

test('gate mode: lets the stop through when every claim is shown', () => {
  const r = run({ records: turn('All tests pass.', passingTests()), args: ['--gate'] });
  assert.equal(r.json.decision, undefined);
  assert.match(r.stderr, /1 shown/);
});

test('gate mode via the environment variable', () => {
  const r = run({ records: turn('I deployed the app to production.'), env: { DROP_IN_RECEIPTS_MODE: 'gate' } });
  assert.equal(r.json.decision, 'block');
});

test('gate mode after the agent cites a receipt: the retry turn is checked on its own evidence and passes', () => {
  // the agent was blocked, then ran the check and said so; the gate feedback is not a new prompt, so the first call still counts
  const feedback = { type: 'user', message: { role: 'user', content: `Stop hook feedback:\n${GATE_TAG} cite a receipt` } };
  const records = transcript(prompt('do it'), say('I pushed to origin.'), feedback,
    bash('git push origin main', 'To github.com:acme/tools.git\n   1111111..2222222  main -> main', { id: 'toolu_retry' }), say('I pushed to origin; git printed the ref update.'));
  const r = run({ records, args: ['--gate'], input: { stop_hook_active: true } });
  assert.match(r.stderr, /1 shown/);
});

// ---- the hook never traps or breaks the session -----------------------------------------------------------------
test('it fails open: no transcript, an unreadable path, or bad input never block and never crash', () => {
  // a broken hook must not look like a turn with nothing to check: the problem goes to the person as a message (and never as a block)
  const noPath = spawnSync(process.execPath, [hook, '--gate'], { input: JSON.stringify({ hook_event_name: 'Stop' }), encoding: 'utf8' });
  assert.equal(noPath.status, 0);
  assert.deepEqual(Object.keys(JSON.parse(noPath.stdout)), ['systemMessage']);
  assert.match(JSON.parse(noPath.stdout).systemMessage, /no transcript path/);
  assert.match(noPath.stderr, /no transcript path/);
  const missing = spawnSync(process.execPath, [hook, '--gate'], { input: JSON.stringify({ transcript_path: join(tmpdir(), 'does-not-exist-xyz.jsonl') }), encoding: 'utf8' });
  assert.equal(missing.status, 0);
  assert.deepEqual(Object.keys(JSON.parse(missing.stdout)), ['systemMessage']);
  assert.match(JSON.parse(missing.stdout).systemMessage, /could not read the transcript/);
  assert.match(missing.stderr, /could not read the transcript/);
  // with --no-system-message it stays on stderr
  const quiet = spawnSync(process.execPath, [hook, '--gate', '--no-system-message'], { input: JSON.stringify({ hook_event_name: 'Stop' }), encoding: 'utf8' });
  assert.equal(quiet.stdout, '');
  assert.match(quiet.stderr, /no transcript path/);
  const garbage = spawnSync(process.execPath, [hook, '--gate'], { input: 'not json at all', encoding: 'utf8' });
  assert.equal(garbage.status, 0);
  assert.equal(garbage.stdout, '');
  const empty = spawnSync(process.execPath, [hook], { input: '', encoding: 'utf8' });
  assert.equal(empty.status, 0);
});

test('the harness\'s last_assistant_message is used when the transcript has not caught up', () => {
  const r = run({ records: transcript(prompt('do it'), passingTests(), say('Let me check one more thing.')), input: { last_assistant_message: 'All tests pass.' } });
  assert.match(r.stderr, /shown: "All tests pass\."/);
});

test('SubagentStop reads the sub-agent\'s own transcript, not the session\'s', () => {
  const session = writeTranscript(turn('All tests pass.', bash('pytest -q', '1 failed in 0.1s', { exit: 1 })));
  const agent = writeTranscript(turn('All tests pass.', passingTests('toolu_sub')));
  const receiptsFile = join(agent.dir, 'r.jsonl');
  const proc = spawnSync(process.execPath, [hook, '--gate'], {
    input: JSON.stringify({ hook_event_name: 'SubagentStop', session_id: 's', transcript_path: session.path, agent_transcript_path: agent.path, agent_id: 'agent-7', stop_hook_active: false }),
    encoding: 'utf8', env: { ...process.env, DROP_IN_RECEIPTS_FILE: receiptsFile },
  });
  assert.equal(proc.status, 0);
  assert.match(proc.stderr, /1 shown/);
  assert.equal(proc.stdout.includes('"decision"'), false);
  const record = JSON.parse(readFileSync(receiptsFile, 'utf8').trim());
  assert.equal(record.event, 'SubagentStop');
  assert.equal(record.agent_id, 'agent-7');
  assert.equal(record.source.tool_use_id, 'toolu_sub');
});

test('the model reader is a later step: asking for it is refused with a note, and the rules still run', () => {
  const r = run({ records: turn('All tests pass.', passingTests()), args: ['--reader', 'lemonade'] });
  assert.match(r.stderr, /the model reader is step 2 and is not built/);
  assert.match(r.stderr, /1 shown/);
  assert.equal(parseArgs(['--reader=off']).reader, 'off');
});

// ---- receipts ------------------------------------------------------------------------------------------------
test('every checked claim is written to the receipts file; the chain verifies; a second run appends', () => {
  const r = run({ records: turn('All tests pass. I deployed to production.', passingTests()) });
  const lines = readFileSync(r.receiptsFile, 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  assert.equal(lines.length, 2);
  assert.deepEqual(lines.map((l) => l.answer), ['shown', 'not shown']);
  assert.equal(lines[0].session_id, 'sess-1');
  assert.match(lines[0].message_sha256, /^[0-9a-f]{64}$/);
  assert.equal(verifyReceipts(r.receiptsFile).ok, true);
  // run again into the same file
  const again = spawnSync(process.execPath, [hook], {
    input: JSON.stringify({ transcript_path: join(r.dir, 'session.jsonl'), session_id: 'sess-2' }), encoding: 'utf8', env: { ...process.env, DROP_IN_RECEIPTS_FILE: r.receiptsFile },
  });
  assert.equal(again.status, 0);
  assert.equal(verifyReceipts(r.receiptsFile).lines, 4);
});

test('--no-receipts writes no file; --receipts <path> chooses the file', () => {
  const none = run({ records: turn('All tests pass.', passingTests()), args: ['--no-receipts'] });
  assert.equal(existsSync(none.receiptsFile), false);
  const dir = scratch('c');
  const chosen = join(dir, 'mine', 'r.jsonl');
  const r = run({ records: turn('All tests pass.', passingTests()), args: ['--receipts', chosen] });
  assert.equal(existsSync(chosen), true);
  assert.equal(existsSync(r.receiptsFile), false);
});

test('a receipts file that cannot be written does not stop the check', () => {
  const dir = scratch('w');
  const blocker = join(dir, 'file');
  writeFileSync(blocker, 'x');
  const r = run({ records: turn('All tests pass.', passingTests()), args: ['--receipts', join(blocker, 'sub', 'r.jsonl')] });
  assert.equal(r.status, 0);
  assert.match(r.stderr, /could not write the receipts file/);
  assert.match(r.stderr, /1 shown/);
});

test('runHook is a plain function: the same answers without a subprocess', () => {
  const { path } = writeTranscript(turn('All tests pass.', passingTests()));
  const out = runHook({ transcript_path: path, session_id: 'x' }, { mode: 'report', noReceipts: true });
  assert.match(out.stderr, /1 shown/);
  assert.equal(JSON.parse(out.stdout).decision, undefined);
  void nextId;
});

// ---- --verify ---------------------------------------------------------------------------------------------------------
test('--verify checks a receipts file: intact exits 0, a changed line exits 1 and names it, an unreadable file exits 2', () => {
  const r = run({ records: turn('All tests pass. I deployed to production.', passingTests()) });
  const ok = spawnSync(process.execPath, [hook, '--verify', r.receiptsFile], { encoding: 'utf8' });
  assert.equal(ok.status, 0);
  assert.match(ok.stdout, /receipts OK: 2 lines, every SHA-256 recomputed, the chain unbroken/);
  const lines = readFileSync(r.receiptsFile, 'utf8').trim().split('\n');
  writeFileSync(r.receiptsFile, [lines[0].replace('"shown"', '"contradicted"'), lines[1]].join('\n') + '\n');
  const bad = spawnSync(process.execPath, [hook, '--verify', r.receiptsFile], { encoding: 'utf8' });
  assert.equal(bad.status, 1);
  assert.match(bad.stdout, /receipts NOT OK: \d+ problems? in 2 lines/);
  assert.match(bad.stdout, /line 1: sha256 does not match the line/);
  const missing = spawnSync(process.execPath, [hook, '--verify', join(r.dir, 'nope.jsonl')], { encoding: 'utf8' });
  assert.equal(missing.status, 2);
  assert.match(missing.stderr, /cannot read/);
  // with no file named it reads the file the environment names
  const viaEnv = spawnSync(process.execPath, [hook, '--verify'], { encoding: 'utf8', env: { ...process.env, DROP_IN_RECEIPTS_FILE: join(r.dir, 'nope.jsonl') } });
  assert.equal(viaEnv.status, 2);
});

// ---- once per turn, from the record as well as from the flag ---------------------------------------------------------
test('gate mode: this hook\'s own gate message already in the turn means no second block, even when stop_hook_active is not set', () => {
  const feedback = { type: 'user', message: { role: 'user', content: `Stop hook feedback:\n${GATE_TAG} cite a receipt` } };
  const records = transcript(prompt('do it'), say('I deployed it to production.'), feedback, say('I deployed it to production, honestly.'));
  const r = run({ records, args: ['--gate'], input: { stop_hook_active: false } });
  assert.equal(r.json.decision, undefined, 'the record says it has already stopped the agent once');
  assert.match(r.stderr, /Mode: gate \(nothing blocked\)/);
  assert.match(r.stderr, /not shown \(needs a reader\)/);
  // the same turn without the gate message does block
  const first = run({ records: transcript(prompt('do it'), say('I deployed it to production.')), args: ['--gate'], input: { stop_hook_active: false } });
  assert.equal(first.json.decision, 'block');
  // a tool result that merely prints the tag is not the gate message
  const printed = transcript(prompt('do it'), bash('cat notes.txt', `${GATE_TAG} is the tag`), say('I deployed it to production.'));
  assert.equal(run({ records: printed, args: ['--gate'] }).json.decision, 'block');
  // and a new prompt starts a new turn, in which it can block again
  const later = transcript(prompt('do it'), say('x'), feedback, say('y'), prompt('now deploy'), say('I deployed it to production.'));
  assert.equal(run({ records: later, args: ['--gate'] }).json.decision, 'block');
});

test('the card is the system message, with any warning that came with it', () => {
  const r = run({ records: turn('All tests pass.', passingTests()), args: ['--reader', 'lemonade'] });
  assert.match(r.json.systemMessage, /the model reader is step 2 and is not built/);
  assert.match(r.json.systemMessage, /1 shown/);
});
