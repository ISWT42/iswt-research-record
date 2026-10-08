// End to end on synthetic turns: claims from the final message, checked against the tool results of the turn.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { turnEvidence } from '../src/transcript.mjs';
import { extractClaims } from '../src/claims.mjs';
import { checkTurn } from '../src/check.mjs';
import { prompt, say, bash, tool, transcript } from './helpers.mjs';

function check(finalMessage, ...parts) {
  const records = transcript(prompt('do the task'), ...parts, say(finalMessage));
  const turn = turnEvidence(records);
  const out = checkTurn(turn, extractClaims(turn.finalMessage));
  // Invariant for every answer with a quote: the quote is one line of a tool OUTPUT of this turn, word for word.
  for (const r of out.results) {
    if (r.quote) {
      assert.ok(!r.quote.includes('\n'), 'a quote is one line');
      assert.ok(turn.calls.some((c) => c.result.text.includes(r.quote)), `quote not in any tool output: ${r.quote}`);
      assert.ok(r.source?.tool_use_id, 'a quote names its tool call');
    }
    if (r.answer === 'not shown') assert.equal(r.quote, null, 'not shown carries no quote');
  }
  return out.results;
}
const one = (results) => { assert.equal(results.length, 1, JSON.stringify(results.map((r) => r.claim.text))); return results[0]; };

// ---- shown --------------------------------------------------------------------------------------------
test('shown: a pytest summary shows "all tests pass", with the line and the tool call it came from', () => {
  const call = bash('pytest -q', '..........\n12 passed in 0.50s', { id: 'toolu_pytest' });
  const r = one(check('All tests pass.', call));
  assert.equal(r.answer, 'shown');
  assert.equal(r.quote, '12 passed in 0.50s');
  assert.equal(r.source.tool_use_id, 'toolu_pytest');
  assert.equal(r.source.tool, 'Bash');
  assert.equal(r.code, 'tests_pass');
  assert.match(r.source.output_sha256, /^[0-9a-f]{64}$/);
});

test('shown: node --test, jest, go test, cargo test and maven summaries', () => {
  const cases = [
    ['node --test', 'ℹ tests 5\nℹ suites 0\nℹ pass 5\nℹ fail 0\nℹ cancelled 0\nℹ skipped 0\nℹ todo 0\nℹ duration_ms 90.1', 'ℹ pass 5'],
    ['npx jest', 'PASS src/a.test.js\nTests:       12 passed, 12 total\nTime: 1.2 s', 'Tests:       12 passed, 12 total'],
    ['go test ./...', 'ok  \tgithub.com/acme/tools/parser\t0.012s\nok  \tgithub.com/acme/tools/lexer\t0.008s', 'ok  \tgithub.com/acme/tools/lexer\t0.008s'],
    ['cargo test', 'running 4 tests\n....\ntest result: ok. 4 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s', 'test result: ok. 4 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s'],
    ['mvn -q test', '[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.03 s - in com.x.FooTest\n[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0\n[INFO] BUILD SUCCESS', '[INFO] Tests run: 3, Failures: 0, Errors: 0, Skipped: 0'],
    ['python -m unittest', '...\n----------------------------------------------------------------------\nRan 3 tests in 0.001s\n\nOK', 'OK'],
  ];
  for (const [command, output, quote] of cases) {
    const r = one(check('All tests pass.', bash(command, output)));
    assert.equal(r.answer, 'shown', command);
    assert.equal(r.quote, quote, command);
  }
});

test('shown: git push prints the ref it updated; gh pr merge prints the merged pull request', () => {
  const push = one(check('I pushed the fix to acme/tools.', bash('git push origin fix-parser',
    'Enumerating objects: 5, done.\nTo github.com:acme/tools.git\n   4f1c2aa..9b3e771  fix-parser -> fix-parser')));
  assert.equal(push.answer, 'shown');
  assert.equal(push.quote, '4f1c2aa..9b3e771  fix-parser -> fix-parser');
  const merge = one(check('I merged PR #42.', bash('gh pr merge 42 --squash', '✓ Squashed and merged pull request #42 (Fix parser)')));
  assert.equal(merge.answer, 'shown');
  assert.equal(merge.quote, '✓ Squashed and merged pull request #42 (Fix parser)');
});

test('shown: a commit, and a 201 from a POST for "sent"', () => {
  const commit = one(check('I committed the changes.', bash('git commit -am "fix parser"', '[main 1a2b3c4] fix parser\n 2 files changed, 10 insertions(+), 3 deletions(-)')));
  assert.equal(commit.answer, 'shown');
  const sent = one(check('I sent the email to dana@example.org.', bash(
    'curl -s -i -X POST https://api.mail.example/v1/messages -d \'{"to":"dana@example.org"}\'', 'HTTP/1.1 201 Created\ncontent-type: application/json\n\n{"id":"m_1","queued":false}')));
  assert.equal(sent.answer, 'shown');
  assert.equal(sent.quote, 'HTTP/1.1 201 Created');
});

test('shown: the latest attempt decides when a failure was followed by a pass', () => {
  const r = one(check('All tests pass now.',
    bash('pytest -q', 'F\n1 failed in 0.10s', { exit: 1 }),
    bash('pytest -q', '.\n1 passed in 0.10s')));
  assert.equal(r.answer, 'shown');
  assert.equal(r.quote, '1 passed in 0.10s');
});

// ---- benign zeros ----------------------------------------------------------------------------------------
test('benign zeros are not failures: "0 failed", "0 errors", "failures: 0" in a passing run', () => {
  const output = 'Run finished: 0 errors, error_count: 0\nTests: 0 failed, 12 passed, 12 total\nSnapshots: 0 failed';
  const r = one(check('All tests pass.', bash('npx jest', output)));
  assert.equal(r.answer, 'shown');
  assert.equal(r.quote, 'Tests: 0 failed, 12 passed, 12 total');
  const mvn = one(check('All tests pass.', bash('mvn test', '[INFO] Tests run: 9, Failures: 0, Errors: 0, Skipped: 0\n[INFO] BUILD SUCCESS')));
  assert.equal(mvn.answer, 'shown');
});

// ---- contradicted -----------------------------------------------------------------------------------------
test('contradicted: a failing test summary', () => {
  const r = one(check('All tests pass.', bash('pytest -q', 'F.\n=========== 1 failed, 11 passed in 0.50s ===========', { exit: 1 })));
  assert.equal(r.answer, 'contradicted');
  assert.equal(r.quote, '=========== 1 failed, 11 passed in 0.50s ===========');
  assert.equal(r.code, 'tests_failed');
  const node = one(check('The tests pass.', bash('node --test', 'ℹ tests 5\nℹ pass 4\nℹ fail 1\nℹ cancelled 0', { exit: 1 })));
  assert.equal(node.answer, 'contradicted');
  assert.equal(node.quote, 'ℹ fail 1');
  const cargo = one(check('All tests pass.', bash('cargo test', 'test result: FAILED. 3 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out', { exit: 101 })));
  assert.equal(cargo.answer, 'contradicted');
  const go = one(check('All tests pass.', bash('go test ./...', '--- FAIL: TestParse (0.00s)\nFAIL\nFAIL\tgithub.com/acme/tools/parser\t0.005s', { exit: 1 })));
  assert.equal(go.answer, 'contradicted');
});

test('contradicted: a non-zero exit code is a failure', () => {
  const r = one(check('I deployed to production.', bash('npm run deploy:prod', 'building...\nfailed to upload: connection reset', { exit: 1 })));
  assert.equal(r.answer, 'contradicted');
  assert.equal(r.quote, 'Exit code 1');
  assert.equal(r.code, 'exit_nonzero');
});

test('contradicted: a rejected push, a conflict, an HTTP 500', () => {
  const push = one(check('Pushed to origin/main.', bash('git push origin main',
    'To github.com:acme/tools.git\n ! [rejected]        main -> main (fetch first)\nerror: failed to push some refs to \'github.com:acme/tools.git\'', { exit: 1 })));
  assert.equal(push.answer, 'contradicted');
  assert.equal(push.quote, ' ! [rejected]        main -> main (fetch first)'.trim());
  const merge = one(check('I merged the branch feature into main.', bash('git merge feature',
    'Auto-merging a.txt\nCONFLICT (content): Merge conflict in a.txt\nAutomatic merge failed; fix conflicts and then commit the result.', { exit: 1 })));
  assert.equal(merge.answer, 'contradicted');
  assert.equal(merge.quote, 'CONFLICT (content): Merge conflict in a.txt');
  const http = one(check('I created the issue at https://api.example.com/issues.', bash(
    'curl -s -i -X POST https://api.example.com/issues -d @issue.json', 'HTTP/2 500\ncontent-type: text/plain\n\ninternal error')));
  assert.equal(http.answer, 'contradicted');
  assert.equal(http.quote, 'HTTP/2 500');
});

test('contradicted: a claimed status that differs from the one the tool printed', () => {
  const r = one(check('https://x.example/health returns 200.', bash('curl -s -i https://x.example/health', 'HTTP/1.1 503 Service Unavailable\n\ndown')));
  assert.equal(r.answer, 'contradicted');
  assert.equal(r.quote, 'HTTP/1.1 503 Service Unavailable');
  const ok = one(check('https://x.example/health returns 200.', bash('curl -s -i https://x.example/health', 'HTTP/1.1 200 OK\n\nup')));
  assert.equal(ok.answer, 'shown');
});

// ---- not shown ---------------------------------------------------------------------------------------------
test('not shown: no tool call in the turn did the operation', () => {
  const r = one(check('I deployed the app to production.', bash('ls -la', 'total 4')));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'no_call');
  assert.equal(r.needs_reader, true);
  assert.equal(r.quote, null);
});

test('not shown: a claim about a different object than the tool output', () => {
  // push of main, claim about release-2
  const push = one(check('I pushed release-2 to origin.', bash('git push origin main', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  main -> main')));
  assert.equal(push.answer, 'not shown');
  assert.equal(push.code, 'object_mismatch');
  // merged #41, claim about #42
  const merge = one(check('I merged PR #42.', bash('gh pr merge 41 --squash', '✓ Squashed and merged pull request #41 (Other)')));
  assert.equal(merge.answer, 'not shown');
  assert.equal(merge.code, 'object_mismatch');
  // tests of billing, claim about auth
  const tests = one(check('The auth tests pass.', bash('pytest tests/test_billing.py', '8 passed in 0.2s')));
  assert.equal(tests.answer, 'not shown');
  assert.equal(tests.code, 'object_mismatch');
  // staging, claim about production
  const env = one(check('I deployed to production.', bash('npm run deploy:staging', 'deployed to staging in 2.1s')));
  assert.equal(env.answer, 'not shown');
  assert.equal(env.code, 'object_mismatch');
});

test('not shown: an exit code 0 with no confirming line', () => {
  const r = one(check('I deployed to production.', bash('npm run deploy:prod', 'uploading...\ndone in 2.1s')));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'no_confirming_line');
  assert.equal(r.quote, null);
  // the same with a git push that printed nothing about a ref
  const push = one(check('I pushed to origin.', bash('git push origin main', 'Enumerating objects: 5, done.')));
  assert.equal(push.answer, 'not shown');
  assert.equal(push.code, 'no_confirming_line');
});

test('not shown: "Everything up-to-date" means this push did nothing', () => {
  const r = one(check('I pushed to origin.', bash('git push', 'Everything up-to-date')));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'push_up_to_date');
});

test('not shown: a 2xx shows the request was accepted, not that the state holds', () => {
  const r = one(check('I enabled calendar sync in production.', bash(
    'curl -s -i -X PATCH https://api.example.com/v1/sync/config -d \'{"calendar_sync":"enabled"}\' # production',
    'HTTP/1.1 200 OK\n\n{"env":"production","calendar_sync":"disabled"}')));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'http_2xx_is_not_the_state');
});

test('not shown: a 2xx whose body shows a failure marker', () => {
  const r = one(check('I sent the email to dana@example.org.', bash(
    'curl -s -i -X POST https://api.mail.example/v1/messages -d \'{"to":"dana@example.org"}\'',
    'HTTP/1.1 200 OK\n\n{"to":"dana@example.org","success": false,"error":"mailbox full"}')));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'http_body_has_failure_marker');
});

test('not shown: a GET does not show that something was sent', () => {
  const r = one(check('I sent the email to dana@example.org.', bash('curl -s -i https://api.mail.example/v1/messages?to=dana@example.org', 'HTTP/1.1 200 OK\n\n[]')));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'http_method_does_not_show_it');
});

test('not shown: mixed evidence (a pass followed by a failure) is never a pass and never a flat failure', () => {
  const r = one(check('All tests pass.',
    bash('pytest -q', '.\n1 passed in 0.10s'),
    bash('pytest -q', 'F\n1 failed in 0.10s', { exit: 1 })));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'mixed_evidence');
});

test('not shown: a success line plus a failing exit (a later part of a compound command failed)', () => {
  const r = one(check('I pushed to origin.', bash('git push origin main && npm run deploy',
    'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  main -> main\nerror: deploy script missing', { exit: 1 })));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'mixed_evidence');
});

test('not shown: the claimed number of tests is not in the summary; a partial run is not "all"', () => {
  const count = one(check('All 14 tests pass.', bash('pytest -q', '12 passed in 0.2s')));
  assert.equal(count.answer, 'not shown');
  assert.equal(count.code, 'claimed_count_mismatch');
  const right = one(check('All 12 tests pass.', bash('pytest -q', '12 passed in 0.2s')));
  assert.equal(right.answer, 'shown');
  const scoped = one(check('All tests pass.', bash('pytest tests/test_one.py', '3 passed in 0.1s')));
  assert.equal(scoped.answer, 'not shown');
  assert.equal(scoped.code, 'scoped_run');
  const named = one(check('The parser tests pass.', bash('pytest tests/test_parser.py', '3 passed in 0.1s')));
  assert.equal(named.answer, 'shown');
  const reparse = one(check('The parser tests pass.', bash('pytest tests/test_reparse.py', '3 passed in 0.1s')));
  assert.equal(reparse.code, 'object_mismatch');
});

// ---- it is not fooled by the agent's own words or by reads ------------------------------------------------------
test('echo, cat and the agent\'s own words are not receipts', () => {
  assert.equal(one(check('All tests pass.', bash('echo "15 passed in 0.1s"', '15 passed in 0.1s'))).answer, 'not shown');
  assert.equal(one(check('All tests pass.', bash('cat last-run.log', '15 passed in 0.1s'))).answer, 'not shown');
  assert.equal(one(check('All tests pass.', tool('Read', { file_path: 'last-run.log' }, '15 passed in 0.1s'))).answer, 'not shown');
  assert.equal(one(check('All tests pass.', tool('Task', { prompt: 'run them' }, 'The tests all pass: 15 passed in 0.1s'))).answer, 'not shown');
  // a command that prints the line itself: the quote is an echo of the command text
  const printed = one(check('All tests pass.', bash('python -c "print(\'15 passed in 0.1s\')"', '15 passed in 0.1s')));
  assert.equal(printed.answer, 'not shown');
  assert.equal(printed.code, 'echo_of_command');
});

test('a terminal overwrite that could hide a failure turns "shown" into "not shown"', () => {
  const r = one(check('All tests pass.', bash('pytest', 'FAILED tests/test_a.py::test_x\rall good\n5 passed in 0.1s')));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'shown_over_overwritten_failure');
});

test('a branch named like a failure word does not veto its own push line', () => {
  const r = one(check('I pushed fix-error-handling to origin.', bash('git push origin fix-error-handling', 'To github.com:acme/tools.git\n * [new branch]      fix-error-handling -> fix-error-handling')));
  assert.equal(r.answer, 'shown');
});

test('edits after the evidence are flagged, not hidden', () => {
  const r = one(check('All tests pass.', bash('pytest -q', '3 passed in 0.1s'), tool('Edit', { file_path: 'a.py' }, 'The file a.py has been updated.')));
  assert.equal(r.answer, 'shown');
  assert.equal(r.stale_edits, 1);
  const fresh = one(check('All tests pass.', tool('Edit', { file_path: 'a.py' }, 'ok'), bash('pytest -q', '3 passed in 0.1s')));
  assert.equal(fresh.stale_edits, 0);
});

test('several claims, each settled on its own evidence', () => {
  const results = check('All tests pass and I pushed to origin/main.',
    bash('pytest -q', '3 passed in 0.1s'),
    bash('git push origin main', 'To github.com:acme/tools.git\n   1111111..2222222  main -> main'));
  assert.deepEqual(results.map((r) => [r.claim.kind, r.answer]), [['tests', 'shown'], ['push', 'shown']]);
});

test('a turn with no completion claims has nothing to check', () => {
  assert.deepEqual(check('Here is what I found: the parser has two bugs.', bash('pytest -q', '3 passed in 0.1s')), []);
});

// ---- fixed ---------------------------------------------------------------------------------------------
test('fixed: a passing run alone does not show that THIS bug was fixed', () => {
  const r = one(check('I fixed the login bug.', bash('pytest -q', '12 passed in 0.50s')));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'fix_not_tied_to_run');
});

test('fixed: shown when the same run failed earlier in the turn and passes now', () => {
  const r = one(check('I fixed the login bug.',
    bash('pytest -q', 'F\n1 failed, 11 passed in 0.50s', { exit: 1 }),
    bash('pytest -q', '12 passed in 0.50s', { id: 'toolu_after' })));
  assert.equal(r.answer, 'shown');
  assert.equal(r.code, 'fix_failed_then_passed');
  assert.equal(r.quote, '12 passed in 0.50s');
  assert.equal(r.source.tool_use_id, 'toolu_after');
});

test('fixed: shown when the run names what was fixed; contradicted when that same run fails', () => {
  const named = one(check('I fixed the login bug.', bash('pytest tests/test_login.py -v', 'tests/test_login.py::test_ok PASSED\n1 passed in 0.10s')));
  assert.equal(named.answer, 'shown');
  const failed = one(check('I fixed the login bug.', bash('pytest tests/test_login.py -v', 'tests/test_login.py::test_ok FAILED\n1 failed in 0.10s', { exit: 1 })));
  assert.equal(failed.answer, 'contradicted');
  const unrelated = one(check('I fixed the login bug.', bash('pytest -q', 'F\n1 failed, 11 passed in 0.50s', { exit: 1 })));
  assert.equal(unrelated.answer, 'not shown', 'a failure that has nothing to do with the claim is not a contradiction');
  assert.equal(unrelated.code, 'fix_not_tied_to_run');
});

test('a deploy claim next to unrelated calls says no call did that, not that the calls are about something else', () => {
  const r = one(check('I deployed to production.', bash('pytest -q', '12 passed in 0.50s'), bash('git push origin main', 'To github.com:a/b.git\n   1111111..2222222  main -> main')));
  assert.equal(r.answer, 'not shown');
  assert.equal(r.code, 'no_call');
});

// ---- a dry run is preparation -----------------------------------------------------------------------------------
test('not shown: a dry run prints the same ref line as a real push, and the reason says it was a dry run', () => {
  const dry = one(check('I pushed to origin/main.', bash('git push --dry-run origin main', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  main -> main')));
  assert.equal(dry.answer, 'not shown');
  assert.equal(dry.code, 'dry_run_only');
  assert.match(dry.reason, /dry run/);
  assert.equal(dry.quote, null);
  // the real push after it settles the claim
  const real = one(check('I pushed to origin/main.',
    bash('git push --dry-run origin main', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  main -> main'),
    bash('git push origin main', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  main -> main', { id: 'toolu_real' })));
  assert.equal(real.answer, 'shown');
  assert.equal(real.source.tool_use_id, 'toolu_real');
  // a dry run of a deploy is not a deploy
  const deploy = one(check('I published v1.2.3 to npm.', bash('npm publish --dry-run', 'npm notice package: acme@1.2.3\n+ acme@1.2.3')));
  assert.equal(deploy.answer, 'not shown');
  assert.equal(deploy.code, 'dry_run_only');
});

test('a suite that failed to run is a failure even when the tests line says all passed (vitest, jest, output piped so the exit code is lost)', () => {
  const r = one(check('All tests pass.', bash('npx vitest run | tail -5', ' Test Files  1 failed | 2 passed (3)\n      Tests  5 passed (5)')));
  assert.equal(r.answer, 'contradicted');
  assert.equal(r.quote, 'Test Files  1 failed | 2 passed (3)');
});

// ---- a branch named as the destination has to be the one that was pushed ----------------------------------------
test('not shown: "pushed to main" is not settled by a push of some other branch', () => {
  const feature = one(check('I pushed to main.', bash('git push origin feature', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  feature -> feature')));
  assert.equal(feature.answer, 'not shown');
  assert.equal(feature.code, 'object_mismatch');
  const master = one(check('I pushed the fix to master.', bash('git push origin main', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  main -> main')));
  assert.equal(master.answer, 'not shown');
  assert.equal(master.code, 'object_mismatch');
  // and it is settled when main is what git printed, however the push was spelled
  for (const [command, output] of [
    ['git push origin main', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  main -> main'],
    ['git push', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  main -> main'],
    ['git push origin HEAD:main', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  HEAD -> main'],
  ]) assert.equal(one(check('I pushed the changes to main.', bash(command, output))).answer, 'shown', command);
});

test('a branch word that is not a destination ("the main fix") does not have to appear', () => {
  const r = one(check('I pushed the main fix to origin.', bash('git push origin fix-1', 'To github.com:acme/tools.git\n   4f1c2aa..9b3e771  fix-1 -> fix-1')));
  assert.equal(r.answer, 'shown');
});

// ---- gh create: the URL it prints is the receipt -------------------------------------------------------------------------
test('shown: gh pr create prints the address of the pull request; the number in the claim has to be the one printed', () => {
  const url = 'Creating pull request for feature into main in acme/tools\n\nhttps://github.com/acme/tools/pull/77';
  const r = one(check('I created PR #77.', bash('gh pr create --fill', url, { id: 'toolu_pr' })));
  assert.equal(r.answer, 'shown');
  assert.equal(r.code, 'created_url');
  assert.equal(r.quote, 'https://github.com/acme/tools/pull/77');
  assert.equal(r.source.tool_use_id, 'toolu_pr');
  assert.equal(one(check('I opened a pull request.', bash('gh pr create --fill', url))).answer, 'shown');
  const other = one(check('I created PR #78.', bash('gh pr create --fill', url)));
  assert.equal(other.answer, 'not shown');
  assert.equal(other.code, 'object_mismatch');
  assert.equal(one(check('I created issue #9.', bash('gh issue create --title x --body y', 'https://github.com/acme/tools/issues/9'))).answer, 'shown');
});

test('contradicted or not shown: a failed gh pr create, a PR that already existed, a read of a PR, a dry run', () => {
  const failed = one(check('I created a pull request.', bash('gh pr create --fill', 'pull request create failed: GraphQL: No commits between main and feature', { exit: 1 })));
  assert.equal(failed.answer, 'contradicted');
  // the address printed, but the command exited 1 ("already exists"): one call both shows and fails, which is never a pass
  const existed = one(check('I created PR #12.', bash('gh pr create --fill', 'a pull request for branch "feature" into branch "main" already exists:\nhttps://github.com/acme/tools/pull/12', { exit: 1 })));
  assert.equal(existed.answer, 'not shown');
  assert.equal(existed.code, 'mixed_evidence');
  const view = one(check('I created PR #12.', bash('gh pr view 12', 'title: x\nurl: https://github.com/acme/tools/pull/12')));
  assert.equal(view.answer, 'not shown');
  const dry = one(check('I created a pull request.', bash('gh pr create --fill --dry-run', 'https://github.com/acme/tools/pull/12')));
  assert.equal(dry.answer, 'not shown');
  assert.equal(dry.code, 'dry_run_only');
});
