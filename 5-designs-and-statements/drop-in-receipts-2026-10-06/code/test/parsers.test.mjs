import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseTestRuns, testOutcome, buildOutcome } from '../src/summaries.mjs';
import { pushOutcome, mergeOutcome, commitOutcome } from '../src/gitout.mjs';
import { httpStatuses, finalStatus, bodyFailureMarkers } from '../src/httpout.mjs';
import { exitFailure } from '../src/exitcode.mjs';

const verdict = (text) => { const o = testOutcome(text); return o ? [o.answer, o.quote] : null; };

test('pytest: every summary shape, and no tests ran is never a pass', () => {
  assert.deepEqual(verdict('=========== 15 passed in 0.12s ==========='), ['shown', '=========== 15 passed in 0.12s ===========']);
  assert.deepEqual(verdict('15 passed, 2 warnings in 0.30s'), ['shown', '15 passed, 2 warnings in 0.30s']);
  assert.deepEqual(verdict('3 failed, 12 passed, 1 skipped in 0.52s'), ['contradicted', '3 failed, 12 passed, 1 skipped in 0.52s']);
  assert.deepEqual(verdict('==== 2 errors in 0.50s ===='), ['contradicted', '==== 2 errors in 0.50s ====']);
  assert.deepEqual(verdict('1 failed, 2 passed in 1.0s (0:00:01)'), ['contradicted', '1 failed, 2 passed in 1.0s (0:00:01)']);
  assert.equal(testOutcome('============ no tests ran in 0.01s ============').answer, null);
});

test('node --test: spec and TAP summaries; cancelled counts as failed', () => {
  assert.deepEqual(verdict('# tests 5\n# pass 5\n# fail 0\n# cancelled 0'), ['shown', '# pass 5']);
  assert.deepEqual(verdict('ℹ tests 5\nℹ pass 3\nℹ fail 0\nℹ cancelled 2'), ['contradicted', 'ℹ cancelled 2']);
  assert.equal(testOutcome('ℹ tests 0\nℹ pass 0\nℹ fail 0').answer, null);
});

test('jest, vitest, mocha, rspec, dotnet', () => {
  assert.deepEqual(verdict('Tests:       1 failed, 4 passed, 5 total'), ['contradicted', 'Tests:       1 failed, 4 passed, 5 total']);
  assert.deepEqual(verdict('Tests:       4 passed, 4 total'), ['shown', 'Tests:       4 passed, 4 total']);
  const vt = testOutcome(' Test Files  3 passed (3)\n      Tests  12 passed (12)');
  assert.equal(vt.answer, 'shown');
  assert.equal(vt.quote, 'Tests  12 passed (12)');
  assert.equal(verdict('      Tests  1 failed | 11 passed (12)')[0], 'contradicted');
  assert.deepEqual(verdict('  12 passing (45ms)'), ['shown', '12 passing (45ms)']);
  assert.deepEqual(verdict('  10 passing (45ms)\n  2 failing'), ['contradicted', '2 failing']);
  assert.deepEqual(verdict('12 examples, 0 failures'), ['shown', '12 examples, 0 failures']);
  assert.deepEqual(verdict('12 examples, 2 failures'), ['contradicted', '12 examples, 2 failures']);
  assert.deepEqual(verdict('Passed!  - Failed:     0, Passed:    12, Skipped:     0, Total:    12, Duration: 25 ms'), ['shown', 'Passed!  - Failed:     0, Passed:    12, Skipped:     0, Total:    12, Duration: 25 ms']);
  assert.equal(verdict('Failed!  - Failed:     1, Passed:    11, Skipped:     0, Total:    12')[0], 'contradicted');
});

test('a suite or file that failed to run is a failure even when the tests line is clean; suite lines never make a pass', () => {
  // vitest: the file that could not be imported does not appear in the tests line
  const vt = testOutcome(' FAIL  src/b.test.ts [ src/b.test.ts ]\nError: Failed to resolve import\n Test Files  1 failed | 2 passed (3)\n      Tests  5 passed (5)');
  assert.equal(vt.answer, 'contradicted');
  assert.equal(vt.quote, 'Test Files  1 failed | 2 passed (3)'.trim());
  // jest: the same, with the suites line
  const jest = testOutcome('Test Suites: 1 failed, 1 passed, 2 total\nTests:       3 passed, 3 total');
  assert.equal(jest.answer, 'contradicted');
  assert.equal(jest.quote, 'Test Suites: 1 failed, 1 passed, 2 total');
  // all suites passed: the answer is the tests line, as before
  assert.deepEqual(verdict('Test Suites: 2 passed, 2 total\nTests:       3 passed, 3 total'), ['shown', 'Tests:       3 passed, 3 total']);
  // a suites line alone, or with no tests, is not a pass
  assert.equal(testOutcome('Test Suites: 1 passed, 1 total').answer, null);
  assert.equal(testOutcome('Test Suites: 1 passed, 1 total\nTests:       0 total').answer, null);
  assert.equal(testOutcome(' Test Files  1 passed (1)').answer, null);
});

test('go test, cargo test, maven, unittest: failures', () => {
  const go = testOutcome('--- FAIL: TestX (0.00s)\nFAIL\nFAIL\tgithub.com/a/b\t0.004s');
  assert.equal(go.answer, 'contradicted');
  assert.equal(go.quote, '--- FAIL: TestX (0.00s)');
  assert.equal(verdict('FAIL\tgithub.com/a/b [build failed]')[0], 'contradicted');
  assert.equal(verdict('?   \tgithub.com/a/b\t[no test files]'), null);
  assert.equal(verdict('ok  \tgithub.com/a/b\t(cached)')[0], 'shown');
  assert.equal(verdict('test result: ok. 2 passed; 0 failed; 0 ignored\ntest result: FAILED. 1 passed; 1 failed; 0 ignored')[0], 'contradicted');
  assert.equal(verdict('[ERROR] Tests run: 12, Failures: 1, Errors: 0, Skipped: 0')[0], 'contradicted');
  assert.equal(verdict('[ERROR] Tests run: 4, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.1 s <<< ERROR! - in com.x.A\n[INFO] Tests run: 12, Failures: 0, Errors: 1, Skipped: 0')[0], 'contradicted');
  assert.deepEqual(verdict('Ran 3 tests in 0.002s\n\nFAILED (failures=1)'), ['contradicted', 'FAILED (failures=1)']);
  assert.deepEqual(verdict('Ran 3 tests in 0.002s\n\nOK'), ['shown', 'OK']);
  assert.equal(parseTestRuns('Ran 3 tests in 0.002s\n\n\n\n\n\nOK').length, 0, 'an OK far from the Ran line is not its summary');
});

test('a line in prose is not a summary', () => {
  assert.equal(testOutcome('we saw 5 passed in the last run, 0 failed'), null);
  assert.equal(testOutcome('Tests: three failed'), null);
});

test('build lines', () => {
  assert.equal(buildOutcome('[INFO] BUILD SUCCESS')?.answer, 'shown');
  assert.equal(buildOutcome('[INFO] BUILD FAILURE')?.answer, 'contradicted');
  assert.equal(buildOutcome('Compiled successfully in 1.2s')?.answer, 'shown');
  assert.equal(buildOutcome('Found 0 errors. Watching for file changes.')?.answer, 'shown');
  assert.equal(buildOutcome('Found 3 errors.')?.answer, 'contradicted');
  assert.equal(buildOutcome('src/a.ts(3,1): error TS2322: Type string is not assignable')?.answer, 'contradicted');
  assert.equal(buildOutcome('All checks passed!')?.answer, 'shown');
  assert.equal(buildOutcome('Success: no issues found in 12 source files')?.answer, 'shown');
  assert.equal(buildOutcome('Finished `release` profile [optimized] target(s) in 3.2s')?.answer, 'shown');
  assert.equal(buildOutcome('done'), null);
});

test('git push: new branch, forced update, deleted, rejected, fatal, up to date', () => {
  assert.equal(pushOutcome(' * [new branch]      feature -> feature').answer, 'shown');
  assert.equal(pushOutcome(' + 1111111...2222222 main -> main (forced update)').answer, 'shown');
  assert.equal(pushOutcome(' - [deleted]         old-branch').answer, 'shown');
  assert.equal(pushOutcome(' ! [remote rejected] main -> main (protected branch hook declined)').answer, 'contradicted');
  assert.equal(pushOutcome("fatal: The current branch x has no upstream branch.").answer, 'contradicted');
  assert.equal(pushOutcome('git@github.com: Permission denied (publickey).\nfatal: Could not read from remote repository.').answer, 'contradicted');
  assert.equal(pushOutcome('Everything up-to-date').answer, null);
  assert.equal(pushOutcome('   abc1234..def5678  a -> a\n ! [rejected]        b -> b (non-fast-forward)').code, 'push_mixed');
  assert.equal(pushOutcome('Enumerating objects: 5, done.'), null);
});

test('merge and commit lines', () => {
  assert.equal(mergeOutcome('Updating abc1234..def5678\nFast-forward\n a.txt | 1 +').answer, 'shown');
  assert.equal(mergeOutcome("Merge made by the 'ort' strategy.").answer, 'shown');
  assert.equal(mergeOutcome('Already up to date.').answer, null);
  assert.equal(mergeOutcome('✓ Pull request #12 will be automatically merged when all requirements are met').answer, null);
  assert.equal(mergeOutcome('X Pull request #12 is not mergeable: the merge commit cannot be cleanly created.').answer, 'contradicted');
  assert.equal(mergeOutcome('{"sha":"abc","merged":true,"message":"Pull Request successfully merged"}').answer, 'shown');
  assert.equal(mergeOutcome('{"message":"Pull Request is not mergeable","merged":false}').answer, 'contradicted');
  assert.equal(commitOutcome('[feature/x (root-commit) 1a2b3c4] first\n 1 file changed').answer, 'shown');
  assert.equal(commitOutcome('[detached HEAD 1a2b3c4] msg').answer, 'shown');
  assert.equal(commitOutcome('On branch main\nnothing to commit, working tree clean').answer, 'contradicted');
  assert.equal(commitOutcome('*** Please tell me who you are.').answer, 'contradicted');
});

test('HTTP status lines in all the forms tools print them', () => {
  const lines = (text, opts) => httpStatuses(text, opts).map((s) => s.status);
  assert.deepEqual(lines('HTTP/1.1 200 OK\ncontent-type: x'), [200]);
  assert.deepEqual(lines('< HTTP/2 404'), [404]);
  assert.deepEqual(lines('Status: 201'), [201]);
  assert.deepEqual(lines('<Response [503]>'), [503]);
  assert.deepEqual(lines('gh: Not Found (HTTP 404)'), [404]);
  assert.deepEqual(lines('curl: (22) The requested URL returned error: 403'), [403]);
  assert.deepEqual(lines('PUT /boards/ops/rules/r-1 -> 202 Accepted'), [202]);
  assert.equal(httpStatuses('PUT /boards/ops/rules/r-1 -> 202 Accepted')[0].method, 'PUT');
  assert.deepEqual(lines('200', { bareStatus: true }), [200]);
  assert.deepEqual(lines('200', { bareStatus: false }), []);
  assert.deepEqual(lines('422 rows exported'), []);
  assert.deepEqual(lines('the server said HTTP is great'), []);
  // a redirect then the real answer: the last real status counts
  assert.equal(finalStatus(httpStatuses('HTTP/1.1 301 Moved Permanently\nHTTP/1.1 200 OK\n\nbody')).status, 200);
  assert.equal(finalStatus(httpStatuses('HTTP/1.1 100 Continue\nHTTP/1.1 201 Created')).status, 201);
  assert.equal(finalStatus(httpStatuses('HTTP/1.1 302 Found')), null);
  const text = 'HTTP/1.1 200 OK\n\n{"error": null, "errors": [], "failed": 0}';
  assert.deepEqual(bodyFailureMarkers(text, httpStatuses(text)[0]), [], 'benign zeros in a body are not failures');
  const bad = 'HTTP/1.1 200 OK\n\n{"success": false}';
  assert.deepEqual(bodyFailureMarkers(bad, httpStatuses(bad)[0]), ['success: false']);
});

test('exit failures: the harness line, a flagged error, and printed exit codes', () => {
  const call = (output, extra = {}) => ({ output, isError: false, ...extra });
  assert.deepEqual(exitFailure(call('Exit code 2\nboom', { isError: true })), { code: 2, line: 'Exit code 2', source: 'harness' });
  assert.equal(exitFailure(call('Exit code 0\nok')), null);
  assert.deepEqual(exitFailure(call('<tool_use_error>File does not exist.</tool_use_error>', { isError: true })), { code: null, line: '<tool_use_error>File does not exist.</tool_use_error>', source: 'is_error' });
  assert.equal(exitFailure(call('exit status 1\nFAIL')).code, 1);
  assert.equal(exitFailure(call("subprocess.CalledProcessError: Command 'x' returned non-zero exit status 3.")).code, 3);
  assert.equal(exitFailure(call('Process exited with code 137')).code, 137);
  assert.equal(exitFailure(call('make: *** [Makefile:5: test] Error 2')).code, 2);
  assert.equal(exitFailure(call('exit code: 0')), null, 'a zero is not a failure');
  assert.equal(exitFailure(call('npm run build\nbuilt in 2s')), null);
  assert.equal(exitFailure(call('the exit code is documented as 1 in the README')), null);
});
