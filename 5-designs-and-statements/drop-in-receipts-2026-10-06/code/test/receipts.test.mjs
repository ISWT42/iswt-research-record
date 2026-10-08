import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { scratch } from './helpers.mjs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { appendReceipts, buildReceipt, verifyReceipts, canonicalJson, seal, lastSha, defaultReceiptsPath } from '../src/receipts.mjs';
import { sha256 } from '../src/text.mjs';
import { extractClaims } from '../src/claims.mjs';
import { settleClaim, prepareCall } from '../src/check.mjs';

const tmp = () => join(scratch('r'), 'nested', 'receipts.jsonl');

function sampleResult(text = 'All tests pass.', output = '12 passed in 0.50s', command = 'pytest -q') {
  const call = prepareCall({ id: 'toolu_x', tool: 'Bash', input: { command }, order: 0, result: { text: output, isError: false } });
  return settleClaim(extractClaims(text)[0], [call]);
}

test('a receipt line carries its own SHA-256, which anyone can recompute from the line', () => {
  const file = tmp();
  const [sealed] = appendReceipts(file, [buildReceipt(sampleResult(), { event: 'Stop', session_id: 's1', mode: 'report' })]);
  const lines = readFileSync(file, 'utf8').trim().split('\n');
  assert.equal(lines.length, 1);
  const record = JSON.parse(lines[0]);
  const { sha256: claimed, ...body } = record;
  assert.equal(claimed, sha256(canonicalJson(body)));
  assert.equal(claimed, sealed.sha256);
  assert.equal(record.prev_sha256, null);
  assert.equal(record.answer, 'shown');
  assert.equal(record.quote, '12 passed in 0.50s');
  assert.equal(record.record, 'floor');
  assert.equal(record.source.tool_use_id, 'toolu_x');
  assert.equal(record.layer, 'deterministic');
});

test('the file is append-only: later receipts are chained to earlier ones, and nothing is overwritten', () => {
  const file = tmp();
  appendReceipts(file, [buildReceipt(sampleResult(), {}), buildReceipt(sampleResult('I pushed to origin.', 'x'), {})]);
  const first = readFileSync(file, 'utf8');
  appendReceipts(file, [buildReceipt(sampleResult(), { event: 'SubagentStop' })]);
  const second = readFileSync(file, 'utf8');
  assert.ok(second.startsWith(first), 'the earlier lines are untouched');
  assert.equal(second.trim().split('\n').length, 3);
  const check = verifyReceipts(file);
  assert.deepEqual(check, { ok: true, lines: 3, problems: [] });
  const lines = second.trim().split('\n').map((l) => JSON.parse(l));
  assert.equal(lines[1].prev_sha256, lines[0].sha256);
  assert.equal(lines[2].prev_sha256, lines[1].sha256);
  assert.equal(lastSha(file), lines[2].sha256);
});

test('a changed, removed or inserted line breaks verification', () => {
  const file = tmp();
  appendReceipts(file, [0, 1, 2].map(() => buildReceipt(sampleResult(), {})));
  const original = readFileSync(file, 'utf8').trim().split('\n');
  writeFileSync(file, [original[0], original[1].replace('"shown"', '"contradicted"'), original[2]].join('\n') + '\n');
  assert.equal(verifyReceipts(file).ok, false);
  writeFileSync(file, [original[0], original[2]].join('\n') + '\n');
  assert.ok(verifyReceipts(file).problems.some((p) => p.problem.includes('prev_sha256')));
  writeFileSync(file, original.join('\n') + '\n');
  assert.equal(verifyReceipts(file).ok, true);
});

test('credentials are redacted before a receipt is written; the output itself is not stored, only its hash', () => {
  const result = sampleResult('I pushed to origin.', 'To github.com:a/b.git\n   1111111..2222222  main -> main', 'git push https://user:s3cret@github.com/a/b.git main -H "Authorization: Bearer abcdef123456"');
  const record = buildReceipt(result, {});
  const text = JSON.stringify(record);
  assert.ok(!text.includes('s3cret'));
  assert.ok(!text.includes('abcdef123456'));
  assert.match(record.source.output_sha256, /^[0-9a-f]{64}$/);
  assert.ok(!('output' in record.source));
});

test('canonicalJson sorts keys and drops undefined', () => {
  assert.equal(canonicalJson({ b: 1, a: { d: [3, { y: 1, x: 2 }], c: undefined } }), '{"a":{"d":[3,{"x":2,"y":1}]},"b":1}');
  assert.equal(seal({ a: 1 }, 'abc').prev_sha256, 'abc');
});

test('the default receipts file is local, in the home folder, unless the environment says otherwise', () => {
  assert.match(defaultReceiptsPath({}), /\.drop-in-receipts[\\/]receipts\.jsonl$/);
  assert.equal(defaultReceiptsPath({ DROP_IN_RECEIPTS_FILE: 'x.jsonl' }), 'x.jsonl');
  assert.equal(existsSync(tmp()), false);
});

// ---- the lock: two hooks stopping together must not fork the chain ------------------------------------------------
import { mkdirSync, utimesSync, readdirSync, statSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { withLock, QUOTE_MAX } from '../src/receipts.mjs';

const writer = fileURLToPath(new URL('./fixtures/append-writer.mjs', import.meta.url));
const runWriter = (file, who, count) => new Promise((resolve, reject) => {
  const child = spawn(process.execPath, [writer, file, who, String(count)], { stdio: 'ignore' });
  child.on('error', reject);
  child.on('exit', (code) => (code === 0 ? resolve() : reject(new Error(`writer ${who} exited ${code}`))));
});

test('eight hooks writing at once: every line is written, the chain verifies, and no lock is left behind', async () => {
  const file = tmp();
  mkdirSync(join(file, '..'), { recursive: true });
  await Promise.all(Array.from({ length: 8 }, (_, i) => runWriter(file, `w${i}`, 12)));
  const check = verifyReceipts(file);
  assert.deepEqual({ ok: check.ok, lines: check.lines }, { ok: true, lines: 96 }, JSON.stringify(check.problems.slice(0, 3)));
  const sessions = readFileSync(file, 'utf8').trim().split('\n').map((l) => JSON.parse(l).session_id);
  assert.equal(new Set(sessions).size, 96, 'no line was lost or written twice');
  assert.equal(existsSync(file + '.lock'), false);
});

test('withLock: a lock left by a dead process is removed once it is old; a lock that stays is waited for, then the write goes ahead', () => {
  const file = tmp();
  mkdirSync(join(file, '..'), { recursive: true });
  // a stale lock (older than staleMs)
  mkdirSync(file + '.lock');
  const old = new Date(Date.now() - 60000);
  utimesSync(file + '.lock', old, old);
  let ran = 0;
  withLock(file, () => { ran++; }, { waitMs: 2000, staleMs: 15000 });
  assert.equal(ran, 1);
  assert.equal(existsSync(file + '.lock'), false, 'the stale lock was cleared and then released');
  // a fresh lock that never goes away: wait the (short) limit, then write anyway, and leave the other holder's lock alone
  mkdirSync(file + '.lock');
  const started = Date.now();
  appendReceipts(file, [buildReceipt(sampleResult(), {})], { waitMs: 150, staleMs: 60000 });
  assert.ok(Date.now() - started >= 140, 'it waited for the lock');
  assert.ok(Date.now() - started < 3000, 'it did not wait long');
  assert.equal(readFileSync(file, 'utf8').trim().split('\n').length, 1, 'the receipt was written anyway');
  assert.equal(existsSync(file + '.lock'), true, 'a lock held by someone else is not removed');
});

test('withLock: a folder that cannot take a lock does not stop the write', () => {
  // the lock path's parent does not exist, so mkdir fails with ENOENT, not EEXIST: carry on without a lock
  let ran = 0;
  withLock(join(tmpdir(), 'drop-in-receipts-no-such-folder-xyz', 'r.jsonl'), () => { ran++; });
  assert.equal(ran, 1);
});

test('object tokens in a receipt are redacted like the claim text, and capped', () => {
  const result = sampleResult();
  result.claim = { ...result.claim, text: 'I pushed it.', objects: { strong: ['https://user:s3cret@github.com/a/b.git', 'ghp_' + 'a'.repeat(30), ...Array.from({ length: 40 }, (_, i) => `file${i}.js`)], prs: ['42'], env: ['production'] } };
  const record = buildReceipt(result, {});
  const text = JSON.stringify(record);
  assert.ok(!text.includes('s3cret'));
  assert.ok(!text.includes('ghp_' + 'a'.repeat(30)));
  assert.equal(record.claim.objects.strong.length, 20);
  assert.deepEqual(record.claim.objects.prs, ['42']);
});

test('a very long quote is cut to a word-for-word prefix and the receipt says so; the chain still reads the last line back', () => {
  const file = tmp();
  const long = 'x'.repeat(QUOTE_MAX * 100);
  const result = sampleResult();
  result.quote = long;
  const record = buildReceipt(result, {});
  assert.equal(record.quote.length, QUOTE_MAX);
  assert.equal(record.quote_truncated, true);
  assert.equal(record.quote_chars, long.length);
  assert.ok(long.startsWith(record.quote));
  appendReceipts(file, [record, buildReceipt(sampleResult(), {})]);
  appendReceipts(file, [buildReceipt(sampleResult(), {})]);
  assert.deepEqual(verifyReceipts(file), { ok: true, lines: 3, problems: [] });
  assert.equal(buildReceipt(sampleResult(), {}).quote_truncated, undefined);
});

test('lastSha reads a last line that is longer than the first window (files written by other tools)', () => {
  const file = tmp();
  mkdirSync(join(file, '..'), { recursive: true });
  const big = JSON.stringify({ sha256: 'f'.repeat(64), pad: 'p'.repeat(300000) });
  writeFileSync(file, JSON.stringify({ sha256: 'a'.repeat(64) }) + '\n' + big + '\n');
  assert.equal(lastSha(file), 'f'.repeat(64));
  void readdirSync; void statSync;
});

// ---- Windows: a lock directory pending deletion fails with EPERM, not EEXIST ----------------------------------------
const fail = (code) => Object.assign(new Error(code), { code });

test('withLock: EPERM, EACCES and EBUSY mean "busy, try again", so the lock is still taken once it clears', () => {
  const file = tmp();
  const calls = [];
  let busyLeft = 3;
  const mkdir = (path) => { calls.push('mkdir'); if (busyLeft-- > 0) throw fail(['EPERM', 'EACCES', 'EBUSY'][busyLeft % 3]); };
  const rmdir = () => { calls.push('rmdir'); };
  let inside = null;
  withLock(file, () => { inside = calls.slice(); }, { mkdir, rmdir, stat: () => { throw fail('ENOENT'); }, transientMs: 2000 });
  assert.deepEqual(inside, ['mkdir', 'mkdir', 'mkdir', 'mkdir'], 'three busy answers, then the lock; the work ran only after it');
  assert.deepEqual(calls.slice(4), ['rmdir'], 'and it was released');
});

test('withLock: a folder that always answers EPERM is given up on after transientMs, and the work still runs', () => {
  const file = tmp();
  let ran = 0;
  const started = Date.now();
  withLock(file, () => { ran++; }, { mkdir: () => { throw fail('EPERM'); }, rmdir: () => { throw new Error('nothing was locked, nothing to release'); }, transientMs: 120 });
  assert.equal(ran, 1);
  assert.ok(Date.now() - started >= 110 && Date.now() - started < 3000);
});

test('withLock: letting go is tried again when a handle is still open, and an answer of ENOENT ends it', () => {
  const file = tmp();
  let rmdirCalls = 0;
  withLock(file, () => {}, { mkdir: () => {}, rmdir: () => { rmdirCalls++; if (rmdirCalls < 3) throw fail('EPERM'); } });
  assert.equal(rmdirCalls, 3);
  let gone = 0;
  withLock(file, () => {}, { mkdir: () => {}, rmdir: () => { gone++; throw fail('ENOENT'); } });
  assert.equal(gone, 1);
});

test('withLock: a lock that is EEXIST and cannot be looked at (pending deletion) is waited for, then the lock is taken', () => {
  const file = tmp();
  let exists = 4;
  let ran = 0;
  withLock(file, () => { ran++; }, {
    mkdir: () => { if (exists-- > 0) throw fail('EEXIST'); },
    stat: () => { throw fail('EPERM'); }, rmdir: () => {}, waitMs: 3000,
  });
  assert.equal(ran, 1);
  assert.equal(exists, -1, 'it kept trying until mkdir worked');
});
