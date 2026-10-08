// Text helpers and the receipt_pair ports. The expected values in fixtures/python-pin.json were produced by
// running receipt_pair's own Python (reader.py / rules.py) on the same inputs, so a drift in the port fails here.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { failureMarkers, overwrittenFailures, normalizeOutput, redact, BENIGN_FAILURE_WORDS, sha256, oneLine } from '../src/text.mjs';
import { r1, r2, r3, combine, normalizeAnswer, ruleKey } from '../src/pairrule.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const pin = JSON.parse(readFileSync(join(here, 'fixtures', 'python-pin.json'), 'utf8'));

test('failureMarkers gives the same answers as receipt_pair on 53 pinned lines', () => {
  assert.equal(pin.failure_markers.length, 53);
  for (const [line, expected] of pin.failure_markers) {
    assert.deepEqual(failureMarkers(line), expected, JSON.stringify(line));
  }
});

test('benign zeros are not failures: "0 failed", "failures: 0", "no errors", "error: null" and friends', () => {
  for (const line of ['5 passed, 0 failed', 'Tests: 0 failed, 12 passed, 12 total', 'ℹ fail 0',
    'test result: ok. 5 passed; 0 failed; 0 ignored', 'Tests run: 12, Failures: 0, Errors: 0, Skipped: 0',
    '12 examples, 0 failures', 'Completed without errors', 'no errors found', 'errors: []', 'error: null',
    'failed=0', 'zero failed', 'exceptions: {}', 'without any errors']) {
    assert.deepEqual(failureMarkers(line), [], line);
  }
});

test('real failures still count: "2 failed", "failures: 3", "10 failed" are not mistaken for zeros', () => {
  for (const line of ['ℹ fail 2', '3 failed, 9 passed in 0.12s', '10 failed', '100 failures', 'failed: 3', 'ERROR: apply failed: zone locked']) {
    assert.notDeepEqual(failureMarkers(line), [], line);
  }
});

test('"0" inside a larger number does not hide a failure: "10 failed" is a failure', () => {
  assert.equal(BENIGN_FAILURE_WORDS.lastIndex, 0);
  assert.deepEqual(failureMarkers('10 failed'), ['failed']);
});

test('overwrittenFailures matches receipt_pair on 7 pinned records', () => {
  for (const [text, expected] of pin.overwritten) {
    assert.deepEqual(overwrittenFailures(text), expected, JSON.stringify(text));
  }
});

test('a failure hidden behind a terminal overwrite is found', () => {
  assert.deepEqual(overwrittenFailures('error: boom\rall good'), ['error']);
  assert.deepEqual(overwrittenFailures('plain output, nothing hidden'), []);
});

test('pair rules r1, r2, r3 match rules.py on all 9 combinations', () => {
  assert.equal(pin.pair.length, 9);
  for (const [a, b, expected] of pin.pair) {
    assert.equal(r1(a, b), expected.r1, `r1 ${a} | ${b}`);
    assert.equal(r2(a, b), expected.r2, `r2 ${a} | ${b}`);
    assert.equal(r3(a, b), expected.r3, `r3 ${a} | ${b}`);
    assert.equal(combine(a, b), expected.r2, 'default rule is r2');
  }
});

test('pair rule input is checked like the original', () => {
  assert.throws(() => r2('shown', 'maybe'));
  assert.equal(normalizeAnswer('Not_Shown'), 'not shown');
  assert.equal(normalizeAnswer(' not-shown '), 'not shown');
  assert.equal(ruleKey(' R2 '), 'r2');
  assert.throws(() => ruleKey('r9'));
});

test('redact removes the same credential shapes as receipt_pair', () => {
  for (const [text, expected] of pin.safe_value) {
    assert.equal(redact(text), expected, text);
  }
  assert.equal(redact('git clone https://user:s3cret@example.com/x.git'), 'git clone https://[redacted]@example.com/x.git');
  assert.equal(redact('AKIAABCDEFGHIJKLMNOP'), '[redacted]');
});

test('redact also removes the credential shapes receipt_pair does not know, and leaves ordinary text alone', () => {
  const removed = [
    ['export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY', 'export AWS_SECRET_ACCESS_KEY=[redacted]'],
    ['aws configure set aws_secret_access_key abcdef123456', 'aws configure set aws_secret_access_key [redacted]'],
    ['mysql --password hunter2 -h db', 'mysql --password [redacted] -h db'],
    ['mysql --password=hunter2 -h db', 'mysql --password=[redacted] -h db'],
    ['curl -u admin:hunter2 https://x.example/api', 'curl -u [redacted] https://x.example/api'],
    ['curl -s -X POST --user admin:hunter2 https://x.example', 'curl -s -X POST --user [redacted] https://x.example'],
    ['DB_PASSWORD=hunter2 npm run migrate', 'DB_PASSWORD=[redacted] npm run migrate'],
    ['Authorization: Basic dXNlcjpwYXNz', 'Authorization: [redacted]'],
    ['curl -H "Authorization: Basic dXNlcjpwYXNz" https://x', 'curl -H "Authorization: [redacted]" https://x'],
    ['eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dBjftJeZ4CVPmB92K27uhbUJU1p1r_wW1gFWFOEjXk', '[redacted]'],
    ['{"password": "hunter2", "user": "a"}', '{"password": [redacted], "user": "a"}'],
    ['docker login -u me -p hunter2', 'docker login -u me -p [redacted]'],
    ['postgres://app:hunter2@db.internal:5432/app', 'postgres://[redacted]@db.internal:5432/app'],
    ['heroku config:set SECRET_KEY_BASE=abc123 -a app', 'heroku config:set SECRET_KEY_BASE=[redacted] -a app'],
    ['sk_live_abcdefghijklmnop', '[redacted]'],
  ];
  for (const [text, expected] of removed) assert.equal(redact(text), expected, text);
  const untouched = [
    'max_tokens=400', 'Total tokens: 3000', 'git push -u origin main', 'docker run -u 1000:1000 img', 'author=John', 'primary_key=id',
    'aws configure set region us-east-1', '12 passed in 0.5s', 'git config user.name Josh', 'set PATH=C:/bin', 'ssh://git@github.com/a/b.git',
    'To github.com:acme/tools.git', '   4f1c2aa..9b3e771  fix-parser -> fix-parser',
  ];
  for (const text of untouched) assert.equal(redact(text), text, text);
});

test('normalizeOutput drops colour codes, makes line ends "\\n", and keeps tabs and newlines', () => {
  assert.equal(normalizeOutput('\x1b[32m5 passed\x1b[0m in 0.1s\r\nnext\tline\r'), '5 passed in 0.1s\nnext\tline\n');
  assert.equal(normalizeOutput(null), '');
});

test('sha256 and oneLine', () => {
  assert.equal(sha256('abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  assert.equal(oneLine('  a\n  b   c '), 'a b c');
  assert.equal(oneLine('x'.repeat(300), 10).length, 10);
});

test('redact stays fast on long unbroken strings (every run it scans is bounded)', () => {
  // These each took seconds before the quantifiers were bounded: 10 KB of "token_" repeated took 14 s.
  const cases = [
    'token_'.repeat(20000), 'a_'.repeat(60000), 'a-b.c_'.repeat(30000), 'set a_secret_'.repeat(10000), 'curl '.repeat(40000),
    '-----BEGIN PRIVATE KEY-----\n'.repeat(20000), 'password="'.repeat(20000), 'a.b://'.repeat(40000),
  ];
  const started = Date.now();
  for (const text of cases) redact(text);
  assert.ok(Date.now() - started < 5000, `took ${Date.now() - started} ms`);
  // and a real private key block is still removed
  assert.equal(redact('x -----BEGIN RSA PRIVATE KEY-----\nMIIabc\n-----END RSA PRIVATE KEY----- y'), 'x [redacted] y');
});

test('a known difference from the Python original, in the safe direction: a failure word glued to a non-ASCII letter is still a marker', () => {
  // Python's \b counts é, テ and İ as word characters, so receipt_pair finds nothing in these lines; JavaScript's \b does not,
  // so the port finds the marker. That can only add a veto against "shown". Do not "fix" it to match Python.
  for (const [line, marker] of [['éfailed', 'failed'], ['テストfailed', 'failed'], ['İerror', 'error'], ['deniedé', 'denied'], ['killedé', 'killed / out of memory']]) {
    assert.deepEqual(failureMarkers(line), [marker], line);
  }
  // everywhere else the two agree, including non-ASCII text that has no failure word glued to it
  assert.deepEqual(failureMarkers('テスト failed 失敗'), ['failed']);
  assert.deepEqual(failureMarkers('résultat: échec'), []);
  assert.deepEqual(failureMarkers('0 件のエラー'), []);
});
