// The replay of test 1 (deterministic layer), on SYNTHETIC items and answers. No real log or answer file is read here.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { writeFileSync, readFileSync } from 'node:fs';
import { scratch } from './helpers.mjs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import {
  parseItems, parseAnswers, answerItem, pairAnswer, relationOf, quoteRelation, replayItems, summarize, formatSummary, runReplay,
} from '../replay/replay.mjs';

const turnsOf = (...pairs) => pairs.map(([cmd, output]) => ({ cmd, output }));
const item = (id, claim, ...pairs) => ({ id, claim, turns: turnsOf(...pairs) });
const row = (arm, id, answer, turn = null, quote = null) => ({ arm, id, answer, code: answer === 'not shown' ? 'model_not_shown' : 'verified', turn, quote });
const answersOf = (...rows) => new Map(rows.map((r) => [`${r.arm}|${r.id}`, r]));

const PUSH = 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  fix-parser -> fix-parser';

test('answerItem: shown, with the line and the turn it came from', () => {
  const r = answerItem('I pushed the parser fix to acme/tools.', turnsOf(['git status', 'On branch fix-parser'], ['git push origin fix-parser', PUSH]));
  assert.equal(r.answer, 'shown');
  assert.equal(r.settled, true);
  assert.equal(r.turn, 'T2');
  assert.equal(r.quote, '4f1c2aa..9b3e771  fix-parser -> fix-parser');
});

test('answerItem: contradicted by a failing test summary; a different object is not shown', () => {
  const failing = answerItem('All tests pass.', turnsOf(['pytest -q', 'F.\n=========== 1 failed, 11 passed in 0.50s ===========']));
  assert.equal(failing.answer, 'contradicted');
  assert.equal(failing.turn, 'T1');
  const other = answerItem('I pushed release-2 to origin.', turnsOf(['git push origin main', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  main -> main']));
  assert.equal(other.answer, 'not shown');
  assert.equal(other.code, 'object_mismatch');
  assert.equal(other.settled, false);
  assert.equal(other.quote, null);
});

test('answerItem: a sentence the extractor does not take as a claim is not shown, and says so', () => {
  const r = answerItem('The queue looks healthy.', turnsOf(['kubectl get pods', 'ok']));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'no_claim_recognized');
  assert.deepEqual(r.claims, []);
});

test('answerItem: with two claims in one sentence, shown needs both and any contradiction wins', () => {
  const bothShown = answerItem('All tests pass and I pushed to origin/main.', turnsOf(['pytest -q', '3 passed in 0.1s'], ['git push origin main', 'To github.com:a/b.git\n   1111111..2222222  main -> main']));
  assert.equal(bothShown.answer, 'shown');
  const oneMissing = answerItem('All tests pass and I pushed to origin/main.', turnsOf(['pytest -q', '3 passed in 0.1s']));
  assert.equal(oneMissing.answer, 'not shown');
  assert.equal(oneMissing.code, 'no_call');
  const oneFailing = answerItem('All tests pass and I pushed to origin/main.', turnsOf(['pytest -q', '1 failed in 0.1s'], ['git push origin main', 'To github.com:a/b.git\n   1111111..2222222  main -> main']));
  assert.equal(oneFailing.answer, 'contradicted');
  assert.equal(oneFailing.code, 'tests_failed');
});

test('pairAnswer follows rules.py r2: shown needs both', () => {
  const a = (answer, turn = 'T1', quote = 'q') => row('A', 'x', answer, turn, quote);
  const b = (answer, turn = 'T1', quote = 'q') => row('B', 'x', answer, turn, quote);
  assert.equal(pairAnswer(a('shown'), b('shown')).answer, 'shown');
  assert.equal(pairAnswer(a('shown'), b('not shown')).answer, 'not shown');
  assert.equal(pairAnswer(a('contradicted'), b('not shown')).answer, 'contradicted');
  assert.equal(pairAnswer(a('shown'), b('contradicted')).answer, 'not shown');
  assert.deepEqual(pairAnswer(a('shown', 'T2', 'one'), b('shown', 'T3', 'two')).turns, ['T2', 'T3']);
  assert.deepEqual(pairAnswer(a('contradicted', 'T2', 'one'), b('not shown')).turns, ['T2']);
  assert.equal(pairAnswer(undefined, b('shown')), null);
});

test('relationOf and quoteRelation', () => {
  const settled = (answer) => ({ answer, settled: answer !== 'not shown' });
  const pair = (answer) => ({ answer });
  assert.equal(relationOf(settled('shown'), pair('shown')), 'agree');
  assert.equal(relationOf(settled('shown'), pair('not shown')), 'rules_settled_pair_not_shown');
  assert.equal(relationOf(settled('shown'), pair('contradicted')), 'opposite');
  assert.equal(relationOf(settled('not shown'), pair('shown')), 'rules_not_shown_pair_settled');
  assert.equal(relationOf(settled('not shown'), pair('not shown')), 'both_not_shown');
  assert.equal(relationOf(settled('shown'), null), 'no_pair_answer');
  assert.equal(quoteRelation('12 passed in 0.5s', ['12  passed in 0.5s']), 'same line');
  assert.equal(quoteRelation('12 passed', ['=== 12 passed in 0.5s ===']), 'overlapping line');
  assert.equal(quoteRelation('a', ['b']), 'different line');
  assert.equal(quoteRelation('', ['b']), 'none');
});

// Six items, every cell of the table used at least once.
function sixItems() {
  const items = [
    item('S1', 'I pushed the parser fix to acme/tools.', ['git push origin fix-parser', PUSH]),                       // rules shown
    item('S2', 'All tests pass.', ['pytest -q', '1 failed, 11 passed in 0.50s']),                                      // rules contradicted
    item('S3', 'I deployed the app to production.', ['ls', 'total 4']),                                               // rules not shown (no call)
    item('S4', 'I pushed the parser fix to acme/tools.', ['git push origin fix-parser', PUSH]),                       // rules shown, pair not shown
    item('S5', 'I deployed the app to production.', ['ls', 'total 4']),                                               // rules not shown, pair shown
    item('S6', 'I pushed the parser fix to acme/tools.', ['git push origin fix-parser', PUSH]),                       // rules shown, pair contradicted
  ];
  const answers = answersOf(
    row('A', 'S1', 'shown', 'T1', '4f1c2aa..9b3e771  fix-parser -> fix-parser'), row('B', 'S1', 'shown', 'T1', 'fix-parser -> fix-parser'),
    row('A', 'S2', 'contradicted', 'T1', '=== 1 failed, 11 passed in 0.50s ==='), row('B', 'S2', 'contradicted', 'T1', '=== 1 failed, 11 passed in 0.50s ==='),
    row('A', 'S3', 'not shown'), row('B', 'S3', 'not shown'),
    row('A', 'S4', 'shown', 'T1', 'x'), row('B', 'S4', 'not shown'),
    row('A', 'S5', 'shown', 'T1', 'y'), row('B', 'S5', 'shown', 'T1', 'y'),
    row('A', 'S6', 'contradicted', 'T1', 'z'), row('B', 'S6', 'contradicted', 'T1', 'z'),
  );
  return { items, answers };
}

test('replayItems and summarize: counts with denominators, and the ids in each group', () => {
  const { items, answers } = sixItems();
  const records = replayItems(items, answers);
  assert.deepEqual(records.map((r) => r.relation), ['agree', 'agree', 'both_not_shown', 'rules_settled_pair_not_shown', 'rules_not_shown_pair_settled', 'opposite']);
  const s = summarize(records);
  assert.equal(s.items, 6);
  assert.equal(s.rules.settled_without_a_model, 4);
  assert.deepEqual([s.rules.shown, s.rules.contradicted, s.rules.not_shown_needs_a_reader], [3, 1, 2]);
  assert.deepEqual(s.pair, { shown: 2, contradicted: 2, not_shown: 2 });
  assert.deepEqual(s.of_the_items_the_rules_settled, { denominator: 4, pair_gives_the_same_answer: 2, pair_says_not_shown: 1, pair_says_the_opposite: 1 });
  assert.deepEqual(s.of_the_items_the_pair_settled, { denominator: 4, rules_give_the_same_answer: 2, rules_say_not_shown: 1, rules_say_the_opposite: 1 });
  assert.equal(s.cross_rules_by_pair.shown.shown, 1);
  assert.equal(s.cross_rules_by_pair.shown['not shown'], 1);
  assert.equal(s.cross_rules_by_pair.shown.contradicted, 1);
  assert.equal(s.cross_rules_by_pair.contradicted.contradicted, 1);
  assert.equal(s.cross_rules_by_pair['not shown'].shown, 1);
  assert.equal(s.cross_rules_by_pair['not shown']['not shown'], 1);
  assert.deepEqual(s.where_both_settled_the_same, { denominator: 2, same_turn: 2, quote_same_line: 1, quote_overlapping_line: 1, quote_different_line: 0 });
  assert.deepEqual(s.ids.opposite, ['S6']);
  assert.deepEqual(s.ids.rules_settled_pair_not_shown, ['S4']);
  assert.deepEqual(s.ids.rules_not_shown_pair_settled, ['S5']);
  assert.deepEqual(s.rules.why_not_settled, { no_call: 2 });
  assert.match(formatSummary(s), /settled without a model: 4 of 6/);
});

test('an item with no recorded pair answer is counted apart, never as agreement', () => {
  const records = replayItems([item('Z', 'I pushed to origin.', ['git push origin main', 'To github.com:a/b.git\n   1111111..2222222  main -> main'])], answersOf(row('A', 'Z', 'shown', 'T1', 'q')));
  assert.equal(records[0].relation, 'no_pair_answer');
  const s = summarize(records);
  assert.equal(s.items_with_pair_answer, 0);
  assert.equal(s.of_the_items_the_rules_settled.pair_gives_the_same_answer, 0);
});

test('loaders take only the named fields: an answer key or any other field in a line never comes out', () => {
  const text = [
    JSON.stringify({ id: 'K1', claim: 'I pushed to origin.', turns: [{ cmd: 'git push', output: 'x', secret_note: 'n' }], truth: 'shown', key: 'contradicted', log_text: 'flat copy' }),
    JSON.stringify({ id: 'K2', claim: 'All tests pass.', turns: [{ command: 'pytest', output: '1 passed in 0.1s' }], truth: 'not shown' }),
  ].join('\n');
  const items = parseItems(text);
  assert.deepEqual(items.map((x) => Object.keys(x)), [['id', 'claim', 'turns'], ['id', 'claim', 'turns']]);
  assert.deepEqual(Object.keys(items[0].turns[0]), ['cmd', 'output']);
  assert.equal(items[1].turns[0].cmd, 'pytest');
  assert.ok(!JSON.stringify(items).includes('contradicted') && !JSON.stringify(items).includes('shown'));
  const answers = parseAnswers([
    JSON.stringify({ arm: 'A', id: 'K1', answer: 'not_shown', reply: 'the model said a lot', truth: 'shown', turn: null, quote: '' }),
    JSON.stringify({ arm: 'A', id: 'K1', answer: 'Shown', code: 'verified', turn: 'T1', quote: 'x', reply: 'second ask' }),
  ].join('\n'));
  assert.deepEqual(Object.keys(answers.get('A|K1')), ['arm', 'id', 'answer', 'code', 'turn', 'quote']);
  assert.equal(answers.get('A|K1').answer, 'shown', 'the later row stands, and answers are normalised');
  assert.throws(() => parseItems(JSON.stringify({ id: 'a', claim: 'x', turns: [] })), /non-empty list/);
  assert.throws(() => parseItems([JSON.stringify({ id: 'a', claim: 'x', turns: ['o'] }), JSON.stringify({ id: 'a', claim: 'x', turns: ['o'] })].join('\n')), /appears twice/);
  assert.throws(() => parseAnswers(JSON.stringify({ arm: 'A', id: 'x', answer: 'maybe' })), /must be one of/);
});

test('runReplay writes the per-item lines and a summary with the hashes of its inputs and its output', () => {
  const dir = scratch('replay');
  const { items, answers } = sixItems();
  const itemsPath = join(dir, 'items.jsonl');
  const answersPath = join(dir, 'answers.jsonl');
  writeFileSync(itemsPath, items.map((i) => JSON.stringify({ ...i, truth: 'shown', log_text: 'flat' })).join('\n') + '\n');
  writeFileSync(answersPath, [...answers.values()].map((r) => JSON.stringify({ ...r, reply: 'text' })).join('\n') + '\n');
  const out = runReplay({ itemsPath, answersPath, label: 'syn', outDir: join(dir, 'out') });
  const lines = readFileSync(out.outPath, 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  assert.equal(lines.length, 6);
  assert.ok(!readFileSync(out.outPath, 'utf8').includes('"truth"') && !readFileSync(out.outPath, 'utf8').includes('log_text'));
  const record = JSON.parse(readFileSync(out.summaryPath, 'utf8'));
  assert.match(record.items_sha256, /^[0-9a-f]{64}$/);
  assert.match(record.answers_sha256, /^[0-9a-f]{64}$/);
  assert.match(record.output_sha256, /^[0-9a-f]{64}$/);
  assert.match(record.script_sha256, /^[0-9a-f]{64}$/);
  assert.equal(record.summary.items, 6);
});

test('the command line runs offline and prints counts with their denominators', () => {
  const dir = scratch('replay-cli');
  const { items, answers } = sixItems();
  writeFileSync(join(dir, 'items.jsonl'), items.map((i) => JSON.stringify(i)).join('\n') + '\n');
  writeFileSync(join(dir, 'answers.jsonl'), [...answers.values()].map((r) => JSON.stringify(r)).join('\n') + '\n');
  const script = fileURLToPath(new URL('../replay/replay.mjs', import.meta.url));
  const proc = spawnSync(process.execPath, [script, '--items', join(dir, 'items.jsonl'), '--answers', join(dir, 'answers.jsonl'), '--label', 'cli', '--out', join(dir, 'out')], { encoding: 'utf8' });
  assert.equal(proc.status, 0, proc.stderr);
  assert.match(proc.stdout, /Replay cli, deterministic layer, pair rule r2: 6 items/);
  assert.match(proc.stdout, /settled without a model: 4 of 6/);
  assert.match(proc.stdout, /no answer key was read/);
});
