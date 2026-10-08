import { test } from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { parseJsonl, currentTurn, turnEvidence, readTail, isRealPrompt, finalAssistantText } from '../src/transcript.mjs';
import { GATE_TAG } from '../src/text.mjs';
import { prompt, say, think, bash, tool, transcript, scratch } from './helpers.mjs';

test('only the current turn counts: calls and claims from earlier prompts are left out', () => {
  const records = transcript(
    prompt('first job'), bash('pytest -q', '5 passed in 0.1s', { id: 'old' }), say('All tests pass.'),
    prompt('second job'), bash('git push origin main', 'To github.com:acme/tools.git\n   1a2b3c4..5d6e7f8  main -> main', { id: 'new' }),
    say('Pushed to main.'));
  const ev = turnEvidence(records);
  assert.equal(ev.finalMessage, 'Pushed to main.');
  assert.deepEqual(ev.calls.map((c) => c.id), ['new']);
});

test('the final message is the text after the last tool result, not the narration before it', () => {
  const records = transcript(
    prompt('go'), say('Let me run the tests.'), bash('npm test', 'ok', { id: 'a' }),
    think('hmm'), say('Everything is done.'), say('Tests pass.'));
  assert.equal(turnEvidence(records).finalMessage, 'Everything is done.\n\nTests pass.');
});

test('a tool result is paired to its call by id, and carries is_error and the text', () => {
  const records = transcript(prompt('go'), bash('make deploy', 'boom', { exit: 2, id: 'x1' }), say('Deployed.'));
  const [call] = turnEvidence(records).calls;
  assert.equal(call.tool, 'Bash');
  assert.equal(call.input.command, 'make deploy');
  assert.equal(call.result.isError, true);
  assert.equal(call.result.text, 'Exit code 2\nboom');
});

test('the agent\'s own words are not evidence: sub-agent reports and todo lists are dropped', () => {
  const records = transcript(
    prompt('go'),
    tool('Task', { prompt: 'run the tests' }, 'The sub-agent says: all 40 tests pass.', { id: 't1' }),
    tool('TodoWrite', { todos: [] }, 'Todos have been modified successfully', { id: 't2' }),
    bash('pytest -q', '3 passed in 0.1s', { id: 't3' }), say('done'));
  assert.deepEqual(turnEvidence(records).calls.map((c) => c.id), ['t3']);
});

test('a call with no captured result is not evidence', () => {
  const [use] = bash('pytest -q', 'x', { id: 'lonely' });
  const records = transcript(prompt('go'), use, say('Tests pass.'));
  assert.equal(turnEvidence(records).calls.length, 0);
  assert.equal(turnEvidence(records).allCalls.length, 1);
});

test('sub-agent (sidechain) records are not the main agent\'s evidence, but are the sub-agent\'s own', () => {
  const side = (records) => records.map((r) => ({ ...r, isSidechain: true }));
  const records = transcript(
    prompt('go'), bash('make', 'ok', { id: 'main1' }), side(bash('pytest', '9 passed in 1s', { id: 'side1' })), say('done'));
  assert.deepEqual(turnEvidence(records, { scope: 'main' }).calls.map((c) => c.id), ['main1']);
  assert.deepEqual(turnEvidence(records, { scope: 'sidechain-only' }).calls.map((c) => c.id), ['side1']);
  assert.deepEqual(turnEvidence(records, { scope: 'agent' }).calls.map((c) => c.id), ['main1', 'side1']);
});

test('this hook\'s own gate message coming back is not a new prompt, so the turn (and its evidence) carries on', () => {
  const feedback = { type: 'user', message: { role: 'user', content: `Stop hook feedback:\n${GATE_TAG} please cite a receipt` } };
  assert.equal(isRealPrompt(feedback), false);
  const records = transcript(prompt('go'), bash('pytest', '3 passed in 0.1s', { id: 'e1' }), say('Tests pass.'), feedback,
    bash('pytest -v', '3 passed in 0.1s', { id: 'e2' }), say('Tests pass, shown above.'));
  const ev = turnEvidence(records);
  assert.deepEqual(ev.calls.map((c) => c.id), ['e1', 'e2']);
  assert.equal(ev.finalMessage, 'Tests pass, shown above.');
});

test('meta user records and tool results are not prompts; a text-block prompt is', () => {
  assert.equal(isRealPrompt({ type: 'user', isMeta: true, message: { content: 'reminder' } }), false);
  assert.equal(isRealPrompt({ type: 'user', message: { content: [{ type: 'tool_result', tool_use_id: 'x', content: 'y' }] } }), false);
  assert.equal(isRealPrompt({ type: 'user', message: { content: [{ type: 'text', text: 'hello' }] } }), true);
  assert.equal(isRealPrompt({ type: 'assistant', message: { content: 'hello' } }), false);
});

test('the harness\'s last_assistant_message wins over the transcript, which can lag the Stop event', () => {
  const records = transcript(prompt('go'), say('Let me check.'));
  assert.equal(turnEvidence(records).finalMessage, 'Let me check.');
  assert.equal(turnEvidence(records, { lastAssistantMessage: 'All tests pass.' }).finalMessage, 'All tests pass.');
});

test('structured toolUseResult stdout is used when the tool_result text is empty', () => {
  const [use, result] = bash('echo hi', '', { id: 's1' });
  result.toolUseResult = { stdout: 'hi from stdout', stderr: 'warn', interrupted: false };
  const [call] = turnEvidence(transcript(prompt('go'), use, result, say('x'))).calls;
  assert.equal(call.result.text, 'hi from stdout\nwarn');
});

test('damaged and cut-off lines are skipped; non-objects are ignored', () => {
  const text = [JSON.stringify(prompt('a')), '{"type":"assis', '', 'null', '42', JSON.stringify(say('b'))].join('\n');
  assert.equal(parseJsonl(text).length, 2);
});

test('readTail drops the partial first line when it starts mid-file', () => {
  const dir = scratch('tail');
  const path = join(dir, 'big.jsonl');
  const lines = Array.from({ length: 400 }, (_, i) => JSON.stringify({ type: 'user', message: { content: 'line ' + i + ' ' + 'x'.repeat(100) } }));
  writeFileSync(path, lines.join('\n') + '\n');
  const tail = readTail(path, 5000);
  const records = parseJsonl(tail);
  assert.ok(records.length > 10 && records.length < 400);
  assert.match(records.at(-1).message.content, /^line 399 /);
  assert.equal(tail.split('\n').filter(Boolean).every((l) => l.startsWith('{')), true);
});

test('finalAssistantText is empty when the turn ends on a tool call', () => {
  const records = currentTurn(transcript(prompt('go'), ...bash('ls', 'a', { id: 'z' }).slice(0, 1)));
  assert.equal(finalAssistantText(records), '');
});

test('gateSeen: this hook\'s gate message among the user records of the turn, and not in a tool result', () => {
  const feedback = { type: 'user', message: { role: 'user', content: `Stop hook feedback:\n${GATE_TAG} cite a receipt` } };
  assert.equal(turnEvidence(transcript(prompt('go'), say('x'), feedback, say('y'))).gateSeen, true);
  const blocks = { type: 'user', message: { role: 'user', content: [{ type: 'text', text: `${GATE_TAG} cite a receipt` }] } };
  assert.equal(turnEvidence(transcript(prompt('go'), say('x'), blocks, say('y'))).gateSeen, true);
  assert.equal(turnEvidence(transcript(prompt('go'), say('x'))).gateSeen, false);
  assert.equal(turnEvidence(transcript(prompt('go'), bash('cat f', `${GATE_TAG} printed by a tool`), say('y'))).gateSeen, false);
  // an earlier turn's gate message does not count for this turn
  assert.equal(turnEvidence(transcript(prompt('one'), say('x'), feedback, say('y'), prompt('two'), say('z'))).gateSeen, false);
});
