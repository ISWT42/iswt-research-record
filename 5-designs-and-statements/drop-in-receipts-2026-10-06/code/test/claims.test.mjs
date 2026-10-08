import { test } from 'node:test';
import assert from 'node:assert/strict';
import { extractClaims, sentencesOf, stripCode } from '../src/claims.mjs';
import { extractObjects, objectMatch, holdsToken, holdsPr } from '../src/objects.mjs';

const kinds = (message) => extractClaims(message).map((c) => c.kind);

test('positive claims: the kinds the hook looks for', () => {
  const cases = [
    ['All tests pass.', ['tests']],
    ['All 14 tests pass.', ['tests']],
    ['The test suite passes.', ['tests']],
    ['I ran the tests and they all pass.', ['tests']],
    ['pytest passes now.', ['tests']],
    ['Tests: 14 passing', ['tests']],
    ['Everything is green.', ['tests']],
    ['✅ All tests pass', ['tests']],
    ['CI is green.', ['tests']],
    ['The build succeeds.', ['build']],
    ['Lint is clean.', ['build']],
    ['Typecheck passes.', ['build']],
    ['I fixed the login bug.', ['fix']],
    ['Fixed the crash in parser.py.', ['fix']],
    ['The bug is now fixed.', ['fix']],
    ['I pushed the branch to origin.', ['push']],
    ['Pushed to origin/main.', ['push']],
    ['The fix has been pushed to origin.', ['push']],
    ['I merged PR #42.', ['merge']],
    ['PR #42 was merged into main.', ['merge']],
    ['I committed the changes.', ['commit']],
    ['Deployed to production.', ['deploy']],
    ['I deployed the app to staging.', ['deploy']],
    ['I published v1.2.0 to npm.', ['deploy']],
    ['I sent the email to Dana.', ['send']],
    ['I created PR #43.', ['create']],
    ['I opened a pull request.', ['create']],
    ['I installed the dependencies.', ['install']],
    ['I enabled calendar sync in production.', ['change']],
    ['The site is live.', ['live']],
    ['I completed the migration.', ['done']],
    // passives that report an event, and tests that pass "on" or "in" somewhere
    ['The bug is fixed.', ['fix']],
    ['The login crash is fixed.', ['fix']],
    ['The bug was fixed in parser.js.', ['fix']],
    ['The issue has been resolved.', ['fix']],
    ['The email has been sent to Dana.', ['send']],
    ['The tests pass in CI.', ['tests']],
    ['The test suite passes on main.', ['tests']],
    ['Tests pass on Node 20.', ['tests']],
  ];
  for (const [message, expected] of cases) assert.deepEqual(kinds(message), expected, message);
});

test('passives and "pass on": the fixes do not turn descriptions of settings or code into claims', () => {
  for (const message of [
    'The sidebar width is fixed.',                                   // a bare "is fixed" needs a bug-like subject
    'The flag is enabled by default.',                               // a bare "is enabled" describes a setting
    'The message is sent to the queue by the handler.',
    'The request was posted to the endpoint by the client code.',   // a bare "was posted" describes code
    'Nothing has been deployed.',
    'None of the changes were pushed.',
    'The handler passes the request on to the next middleware.',    // "pass on" with no test or build before it
    'The value is passed on to the lexer.',
    'Logging is configured through environment variables.',
  ]) assert.deepEqual(kinds(message), [], message);
});

test('two claims in one sentence become two claims, each with its own object', () => {
  const claims = extractClaims('I fixed the bug and pushed to origin/main.');
  assert.deepEqual(claims.map((c) => c.kind), ['fix', 'push']);
  assert.deepEqual(claims[1].objects.strong, ['origin/main']);
  assert.deepEqual(claims[0].objects.strong, []);
  assert.deepEqual(kinds('The tests pass and the build succeeds.'), ['tests', 'build']);
});

test('not claims: negation, plans, conditions, hedges, questions and instructions', () => {
  const notClaims = [
    'Tests did not pass.',
    "The tests don't pass yet.",
    "I haven't deployed it.",
    "I couldn't push because the remote refused.",
    'You can deploy it with `npm run deploy`.',
    'Should I push the changes?',
    "Once the tests pass I'll push.",
    'If the build passes, deploy it.',
    'Tests should pass now.',
    'This should be fixed now.',
    'Hopefully this fixes it.',
    'I will deploy tomorrow.',
    'I plan to merge the PR after review.',
    'Next, run the tests to verify.',
    'Run `pytest` and check that all tests pass.',
    'I tried to push but it was rejected.',
    'The deploy failed.',
    'Before the tests pass we need the fixture.',
    'To get the tests passing, install the dev dependencies.',
    'The build is not clean.',
    'Nothing was deployed.',
    'We still need to merge it.',
    'Do you want me to push?',
  ];
  for (const message of notClaims) assert.deepEqual(kinds(message), [], message);
});

test('not claims: partial claims and claims that admit failures in the same breath', () => {
  for (const message of [
    'All tests pass except two failures.',
    'All tests pass apart from the flaky one.',
    '28 tests pass, 2 pre-existing failures remain.',
    'Most of the tests pass.',
    'The build passes, though 3 tests fail.',
    'Fixed the parser, but 2 unrelated tests fail.',
  ]) assert.deepEqual(kinds(message).filter((k) => ['tests', 'build', 'fix'].includes(k)), [], message);
  // zero failures is not an admission
  assert.deepEqual(kinds('All tests pass with 0 failures.'), ['tests']);
  assert.deepEqual(kinds('All 12 tests pass, no errors.'), ['tests']);
});

test('not claims: describing what code does, not what the agent did', () => {
  for (const message of [
    'The handler pushed the item to the queue.',
    'The function merged the two lists.',
    'The parser passes the token through to the lexer.',
    'The request was posted to the endpoint by the client code in the example.',
  ]) assert.deepEqual(kinds(message), [], message);
});

test('code blocks, quotations, headings and table rules are never claims', () => {
  const message = [
    '## All tests pass',
    '> 5 passed in 0.1s',
    '```',
    '$ pytest',
    '14 tests passed',
    'Deployed to production.',
    '```',
    '| a | b |',
    '|---|---|',
  ].join('\n');
  assert.deepEqual(kinds(message), []);
  assert.equal(stripCode('a\n```\nb\n```\nc'), 'a\nc');
  assert.equal(stripCode('a\n```\nb'), 'a'); // an unclosed fence runs to the end
});

test('bullets, bold, links and emoji are stripped before reading', () => {
  const message = [
    '- **Tests**: all 14 pass',
    '- ✅ Pushed to [origin/main](https://github.com/acme/tools)',
    '1. I merged PR #7',
  ].join('\n');
  assert.deepEqual(kinds(message), ['tests', 'push', 'merge']);
  assert.deepEqual(sentencesOf('First one. Second one!\n\nThird?'), ['First one.', 'Second one!', 'Third?']);
});

test('a table row can carry a claim', () => {
  assert.deepEqual(kinds('| Tests | all pass |\n|---|---|'), ['tests']);
});

test('the claimed count and the subject of a test claim are kept', () => {
  const [a] = extractClaims('All 14 tests pass.');
  assert.deepEqual(a.counts, [14]);
  const [b] = extractClaims('The auth tests pass.');
  assert.deepEqual(b.subject, ['auth']);
  const [c] = extractClaims('Tests for the parser pass.');
  assert.deepEqual(c.subject, ['parser']);
  const [d] = extractClaims('All tests pass.');
  assert.deepEqual(d.subject, []);
});

test('the claim carries its text and its sentence', () => {
  const [claim] = extractClaims('I pushed the branch to origin. Then I went home.');
  assert.equal(claim.text, 'I pushed the branch to origin.');
  assert.equal(claim.kind, 'push');
});

test('no more than a few dozen claims are taken from one message', () => {
  const message = Array.from({ length: 60 }, (_, i) => `I pushed branch-${i} to origin.`).join('\n');
  assert.ok(extractClaims(message).length <= 24);
});

// ---- object tokens ---------------------------------------------------------------------------------
test('object tokens: paths, hosts, versions, PR numbers, environments, backticks', () => {
  const o = extractObjects('Deployed v1.2.0 of `my-app` to production at api.example.com, see parser.py and src/lib/util.ts, PR #42, sha 4f1c2aa');
  assert.ok(o.strong.includes('v1.2.0'));
  assert.ok(o.strong.includes('my-app'));
  assert.ok(o.strong.includes('api.example.com'));
  assert.ok(o.strong.includes('parser.py'));
  assert.ok(o.strong.includes('src/lib/util.ts'));
  assert.ok(o.strong.includes('4f1c2aa'));
  assert.deepEqual(o.prs, ['42']);
  assert.deepEqual(o.env, ['production']);
});

test('object tokens: prose is not an object ("and/or", "pre-existing", "Node.js")', () => {
  const o = extractObjects('The pre-existing built-in handler and/or Node.js code, plus the up-to-date list.');
  assert.deepEqual(o.strong, []);
  assert.ok(o.weak.includes('pre-existing'));
});

test('object tokens: a name next to "branch" or "service" is strong, a Capitalised name is weak', () => {
  const o = extractObjects('Pushed branch fix-parser, restarted the auth-service service for Trontin.');
  assert.ok(o.strong.includes('fix-parser'));
  assert.ok(o.strong.includes('auth-service'));
  assert.ok(o.weak.includes('trontin'));
});

test('holdsToken: whole words, case-insensitive, and a/b held when both parts are words', () => {
  assert.equal(holdsToken('To github.com:acme/tools.git', 'acme/tools'), true);
  assert.equal(holdsToken('git push origin main', 'origin/main'), true);
  assert.equal(holdsToken('git push origin feature', 'origin/main'), false);
  assert.equal(holdsToken('see test_parser.py', 'parser.py'), false);
  assert.equal(holdsToken('see src/parser.py', 'parser.py'), true);
  assert.equal(holdsToken('Fix-Parser -> Fix-Parser', 'fix-parser'), true);
});

test('holdsPr: #42, pull request #42, gh pr merge 42, but not #421 or 142', () => {
  assert.equal(holdsPr('Merged pull request #42 (title)', '42'), true);
  assert.equal(holdsPr('gh pr merge 42 --squash', '42'), true);
  assert.equal(holdsPr('https://github.com/a/b/pull/42', '42'), true);
  assert.equal(holdsPr('Merged pull request #421', '42'), false);
  assert.equal(holdsPr('gh pr merge 142', '42'), false);
  assert.equal(holdsPr('Merged pull request #41', '42'), false);
});

test('holdsPr: the number as a field of a tool call or response (MCP clients), and only for the right number', () => {
  assert.equal(holdsPr('mcp__github__merge_pull_request {"owner":"acme","repo":"tools","pullNumber":42}', '42'), true);
  assert.equal(holdsPr('{"pull_number": 42, "merge_method": "squash"}', '42'), true);
  assert.equal(holdsPr('pr_number="42"', '42'), true);
  assert.equal(holdsPr('{"pull_request_id":42}', '42'), true);
  assert.equal(holdsPr('mcp__github__merge_pull_request {"number":42}', '42'), true, 'a plain number counts in a call about pull requests');
  assert.equal(holdsPr('mcp__github__merge_pull_request {"pullNumber":41}', '42'), false);
  assert.equal(holdsPr('mcp__github__merge_pull_request {"pullNumber":421}', '42'), false);
  assert.equal(holdsPr('deploy_service {"number":42}', '42'), false, 'a plain number is not a pull request in a call that is not about one');
  assert.equal(holdsPr('{"pull_number": 142}', '42'), false);
});

test('objectMatch: every strong token, the environment, and one weak name when asked', () => {
  const objects = extractObjects('Deployed v2.0.1 to production for Trontin.');
  assert.deepEqual(objectMatch(objects, 'deploy v2.0.1 --env=prod Trontin ok').ok, true);
  assert.deepEqual(objectMatch(objects, 'deploy v2.0.1 --env=staging').missing, ['production']);
  assert.deepEqual(objectMatch(objects, 'deploy v2.0.0 --env=prod').missing, ['v2.0.1']);
  assert.equal(objectMatch(objects, 'deploy v2.0.1 --env=prod', { useWeak: true }).ok, false);
  assert.deepEqual(objectMatch(objects, 'deploy v2.0.1 --env=prod', { useWeak: true }).missing, ['trontin']);
  assert.equal(objectMatch(objects, 'deploy v2.0.1 --env=prod', { useWeak: false }).ok, true);
});

test('a branch name after "pushed", "to" or "into" is strong, so a push of another branch cannot stand in for it', () => {
  assert.ok(extractObjects('pushed fix-parser to origin').strong.includes('fix-parser'));
  assert.ok(extractObjects('merged into release-2').strong.includes('release-2'));
  assert.deepEqual(extractObjects('I fixed the off-by-one error').strong, []);
});

test('each claim in a sentence shows only its own part, and a fix carries the words that say what was fixed', () => {
  const claims = extractClaims('I deployed to production and I fixed the login bug.');
  assert.deepEqual(claims.map((c) => [c.kind, c.text]), [['deploy', 'I deployed to production'], ['fix', 'I fixed the login bug.']]);
  assert.deepEqual(claims[1].fixWords, ['login']);
  assert.deepEqual(claims[0].objects.env, ['production']);
  assert.deepEqual(claims[1].objects.env, []);
});

test('the count form and the noun form of "all 14 tests pass" are one claim with the whole sentence as its segment', () => {
  const claims = extractClaims('All 14 tests pass.');
  assert.equal(claims.length, 1);
  assert.equal(claims[0].segment, 'All 14 tests pass.');
  assert.deepEqual(claims[0].counts, [14]);
});

test('"returns 200" is a claim about a status; "returns 200 items" is not', () => {
  assert.deepEqual(kinds('The endpoint returns 200.'), ['live']);
  assert.deepEqual(kinds('https://x.example/health responds with HTTP 200.'), ['live']);
  assert.deepEqual(kinds('The query returns 200 items.'), []);
});

test('a sentence of many thousands of characters is read only at its start, so a huge pasted line cannot stall the hook', () => {
  const huge = 'All tests pass and ' + 'x '.repeat(1000000) + 'I pushed it to origin/main.';
  const started = Date.now();
  const claims = extractClaims(huge);
  // without the cap the time grows with the square of the length (about a minute for this message); with it, well under a second
  assert.ok(Date.now() - started < 5000, 'finished in time');
  assert.deepEqual(claims.map((c) => c.kind), ['tests'], 'the claim at the start is kept, the one past the cut is not');
  assert.ok(claims[0].sentence.length <= 300 && claims[0].text.length <= 220);
});

test('a main-style branch named as the destination of a push becomes an object; the word "main" elsewhere does not', () => {
  const strong = (message) => extractClaims(message)[0].objects.strong;
  assert.deepEqual(strong('I pushed to main.'), ['main']);
  assert.deepEqual(strong('I pushed the fix to master.'), ['master']);
  assert.deepEqual(strong('Pushed the changes into the develop branch.'), ['develop']);
  assert.deepEqual(strong('I pushed main to origin.'), ['main']);
  assert.deepEqual(strong('I pushed the trunk branch.'), ['trunk']);
  assert.deepEqual(strong('I pushed the main fix to origin.'), []);
  assert.deepEqual(strong('I pushed to origin/main.'), ['origin/main']);
  assert.deepEqual(extractClaims('I merged PR #42 into main.')[0].objects.strong, [], 'a merge is identified by its pull request, not by its base branch');
});

test('holdsPr: an issue number is read like a pull request number (issue #9, /issues/9), and only that number', () => {
  assert.equal(holdsPr('https://github.com/acme/tools/issues/9', '9'), true);
  assert.equal(holdsPr('Created issue #9', '9'), true);
  assert.equal(holdsPr('https://github.com/acme/tools/issues/91', '9'), false);
  assert.equal(holdsPr('https://github.com/acme/tools/issues/19', '9'), false);
});
