// Test-runner summaries, read by rule (no model): pytest, node --test, jest, vitest, mocha, go test, cargo test,
// maven, python unittest, rspec, dotnet test. Each summary is a line, or a few lines, a runner prints at the end.
//
// A run is
//   ok        it ran tests and none failed or errored
//   failing   some failed, errored or were cancelled
//   neither   no tests ran, or the summary does not say (never a pass)
// "0 failed" and its kind are benign zeros: they are read as the number 0, never as a failure word.
import { splitLines } from './text.mjs';

const num = (x) => Number.parseInt(x, 10);

function countsIn(text) {
  const c = {};
  for (const m of text.matchAll(/(\d+)\s+(failed|passed|skipped|todo|total|errors?|deselected|xfailed|xpassed|warnings?|rerun|failures?|pending|cancelled)\b/gi)) {
    const key = m[2].toLowerCase().replace(/^errors$/, 'error').replace(/^failures$/, 'failure').replace(/^warnings$/, 'warning');
    c[key] = (c[key] ?? 0) + num(m[1]);
  }
  return c;
}

function run(runner, at, line, { failed = 0, passed = 0, total = null, extra = {}, failLine = null }) {
  const failing = failed > 0;
  return { runner, at, line, failLine: failLine ?? line, failed, passed, total: total ?? passed + failed, failing, ok: !failing && passed > 0, ...extra };
}

const PYTEST = /^\s*(?:=+\s*)?((?:\d+\s+(?:failed|passed|skipped|deselected|xfailed|xpassed|warnings?|errors?|rerun)\b(?:\s*,\s*|\s+and\s+)?)+)\s+in\s+[\d.]+\s*s(?:\s*\([\d:]+\))?\s*(?:=+)?\s*$/i;
const PYTEST_NONE = /^\s*(?:=+\s*)?no tests (?:ran|collected)(?:\s+in\s+[\d.]+s)?\s*(?:=+)?\s*$/i;
const JEST = /^\s*Tests:\s+((?:\d+\s+(?:failed|passed|skipped|todo|total)\b(?:,\s*)?)+)\s*$/;
const VITEST = /^\s*Tests\s+((?:\d+\s+(?:failed|passed|skipped|todo)\b(?:\s*\|\s*)?)+)\s*\(\d+\)\s*$/;
// A suite or file that failed to run (an import error, a syntax error) leaves the tests line clean ("5 passed"), so the
// suite-level lines are read too. They can only add a failure: their passes are not counted, so a zero-test suite line
// cannot make a pass.
const JEST_SUITES = /^\s*Test Suites:\s+((?:\d+\s+(?:failed|passed|skipped|todo|total)\b(?:,\s*)?)+)\s*$/;
const VITEST_FILES = /^\s*Test Files\s+((?:\d+\s+(?:failed|passed|skipped|todo)\b(?:\s*\|\s*)?)+)\s*\(\d+\)\s*$/;
const MOCHA_PASS = /^\s*(\d+)\s+passing\b/;
const MOCHA_FAIL = /^\s*(\d+)\s+failing\b/;
const NODE_TEST = /^\s*(?:ℹ|#)\s+(tests|suites|pass|fail|cancelled|skipped|todo)\s+(\d+)\s*$/;
const GO_OK = /^ok\s+(\S+)\s+(?:\(cached\)|[\d.]+s)/;
const GO_FAIL_PKG = /^FAIL\s+(\S+)(?:\s+(?:[\d.]+s|\[(?:build|setup) failed\]))?\s*$/;
const GO_FAIL_TEST = /^--- FAIL: /;
const CARGO = /^test result: (ok|FAILED)\.\s+(\d+) passed;\s+(\d+) failed;/;
const MVN = /^(?:\[(?:INFO|ERROR|WARNING)\]\s*)?Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+)(?:,\s*Skipped:\s*(\d+))?(?:,\s*Time elapsed:[^-\n]*?)?(\s+-\s+in\s+\S+)?\s*$/;
const UNITTEST_RAN = /^Ran (\d+) tests? in [\d.]+s\s*$/;
const RSPEC = /^\s*(\d+) examples?, (\d+) failures?(?:, (\d+) pending)?\s*$/;
const DOTNET = /^\s*(Passed|Failed)!\s+-\s+Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)/;

export function parseTestRuns(text) {
  const lines = splitLines(text);
  const runs = [];
  const node = {};
  let nodeAt = -1;
  const goOk = [];
  const goFail = [];
  const mvnLines = [];
  let mochaPass = null;
  let mochaFail = null;
  let unittestRan = null;

  lines.forEach((raw, at) => {
    const line = raw.trimEnd();
    let m;
    if ((m = PYTEST.exec(line))) {
      const c = countsIn(m[1]);
      runs.push(run('pytest', at, line.trim(), { failed: (c.failed ?? 0) + (c.error ?? 0), passed: c.passed ?? 0, total: (c.passed ?? 0) + (c.failed ?? 0) + (c.error ?? 0) }));
    } else if (PYTEST_NONE.test(line)) {
      runs.push(run('pytest', at, line.trim(), { failed: 0, passed: 0 }));
    } else if ((m = JEST.exec(line))) {
      const c = countsIn(m[1]);
      runs.push(run('jest', at, line.trim(), { failed: c.failed ?? 0, passed: c.passed ?? 0, total: c.total ?? null }));
    } else if ((m = VITEST.exec(line))) {
      const c = countsIn(m[1]);
      runs.push(run('vitest', at, line.trim(), { failed: c.failed ?? 0, passed: c.passed ?? 0 }));
    } else if ((m = JEST_SUITES.exec(line)) || (m = VITEST_FILES.exec(line))) {
      const c = countsIn(m[1]);
      runs.push(run(JEST_SUITES.test(line) ? 'jest-suites' : 'vitest-files', at, line.trim(), { failed: c.failed ?? 0, passed: 0, total: c.total ?? null }));
    } else if ((m = MOCHA_PASS.exec(line))) {
      mochaPass = { at, line: line.trim(), n: num(m[1]) };
    } else if ((m = MOCHA_FAIL.exec(line))) {
      mochaFail = { at, line: line.trim(), n: num(m[1]) };
    } else if ((m = NODE_TEST.exec(line))) {
      node[m[1]] = { n: num(m[2]), line: line.trim(), at };
      nodeAt = at;
    } else if ((m = GO_OK.exec(line))) {
      goOk.push({ at, line: line.trim() });
    } else if ((m = GO_FAIL_PKG.exec(line))) {
      goFail.push({ at, line: line.trim() });
    } else if (GO_FAIL_TEST.test(line)) {
      goFail.push({ at, line: line.trim(), test: true });
    } else if ((m = CARGO.exec(line))) {
      runs.push(run('cargo', at, line.trim(), { failed: num(m[3]) + (m[1] === 'FAILED' && num(m[3]) === 0 ? 1 : 0), passed: num(m[2]) }));
    } else if ((m = MVN.exec(line))) {
      mvnLines.push({ at, line: line.trim(), run: num(m[1]), failures: num(m[2]), errors: num(m[3]), perClass: Boolean(m[5]) });
    } else if ((m = UNITTEST_RAN.exec(line))) {
      unittestRan = { at, line: line.trim(), n: num(m[1]) };
    } else if ((m = RSPEC.exec(line))) {
      runs.push(run('rspec', at, line.trim(), { failed: num(m[2]), passed: num(m[1]) - num(m[2]) - num(m[3] ?? 0), total: num(m[1]) }));
    } else if ((m = DOTNET.exec(line))) {
      runs.push(run('dotnet', at, line.trim(), { failed: num(m[2]), passed: num(m[3]), total: num(m[5]) }));
    } else if (unittestRan && at > unittestRan.at && at <= unittestRan.at + 4) {
      const t = line.trim();
      if (/^OK\b/.test(t)) { runs.push(run('unittest', at, t, { failed: 0, passed: unittestRan.n })); unittestRan = null; }
      else if (/^FAILED\s*\(/.test(t)) { runs.push(run('unittest', at, t, { failed: Math.max(1, countFromParens(t)), passed: 0 })); unittestRan = null; }
    }
  });

  if (mochaPass || mochaFail) {
    const at = (mochaFail ?? mochaPass).at;
    runs.push(run('mocha', at, (mochaPass ?? mochaFail).line, { failed: mochaFail?.n ?? 0, passed: mochaPass?.n ?? 0, failLine: mochaFail?.line ?? null }));
  }
  if (node.pass && node.fail) {
    const failed = node.fail.n + (node.cancelled?.n ?? 0);
    runs.push(run('node:test', nodeAt, node.pass.line, {
      failed, passed: node.pass.n, total: node.tests?.n ?? node.pass.n + node.fail.n,
      failLine: node.fail.n > 0 ? node.fail.line : node.cancelled?.n > 0 ? node.cancelled.line : null,
    }));
  }
  if (goOk.length || goFail.length) {
    const first = goFail[0];
    runs.push(run('go', (first ?? goOk.at(-1)).at, (goOk.at(-1) ?? first).line, {
      failed: goFail.length > 0 ? goFail.length : 0, passed: goOk.length, failLine: first?.line ?? null,
    }));
  }
  if (mvnLines.length) {
    const bad = mvnLines.find((l) => l.failures > 0 || l.errors > 0);
    const summary = [...mvnLines].reverse().find((l) => !l.perClass) ?? mvnLines.at(-1);
    runs.push(run('maven', summary.at, summary.line, {
      failed: bad ? bad.failures + bad.errors : 0, passed: Math.max(0, summary.run - summary.failures - summary.errors), failLine: bad?.line ?? null,
    }));
  }
  return runs.sort((a, b) => a.at - b.at);
}

function countFromParens(line) {
  const c = {};
  for (const m of line.matchAll(/(failures|errors)=(\d+)/g)) c[m[1]] = num(m[2]);
  return (c.failures ?? 0) + (c.errors ?? 0);
}

// What a call's output says about a test run: contradicted by a failing summary, shown by a passing one, else null.
export function testOutcome(text) {
  const runs = parseTestRuns(text);
  if (runs.length === 0) return null;
  const failing = runs.find((r) => r.failing);
  if (failing) return { answer: 'contradicted', quote: failing.failLine, code: 'tests_failed', run: failing };
  const best = runs.filter((r) => r.ok).sort((a, b) => b.passed - a.passed)[0];
  if (best) return { answer: 'shown', quote: best.line, code: 'tests_pass', run: best };
  return { answer: null, code: 'no_tests_ran', run: runs[0] };
}

// ---- builds: a few explicit lines; anything else rests on the exit code alone ------------------------
const BUILD_OK = [
  /^\s*(?:\[INFO\]\s*)?BUILD SUCCESS(?:FUL)?\b/,
  /\bCompiled successfully\b/i,
  /^\s*Build succeeded\b/i,
  /^\s*Finished\s+`?(?:dev|release|test|bench)\b.*\btarget\(s\)\s+in\b/,
  /\bbuilt in [\d.]+m?s\b/i,
  /\bSuccessfully (?:compiled|built)\b/i,
  /^\s*All checks passed!?\s*$/,
  /^\s*Success: no issues found in \d+ source files?\s*$/,
  /^\s*Found 0 errors\b/,
  /\b0 errors?,\s*0 warnings?\b/i,
];
const BUILD_FAIL = [
  /^\s*(?:\[(?:INFO|ERROR)\]\s*)?BUILD FAIL(?:URE|ED)\b/,
  /^\s*Build failed\b/i,
  /\bFailed to compile\b/i,
  /^\s*error: could not compile\b/,
  /^\s*Found [1-9]\d* errors?\b/,
  /\berror TS\d+:/,
];

export function buildOutcome(text) {
  const lines = splitLines(text);
  for (const line of lines) if (BUILD_FAIL.some((re) => re.test(line))) return { answer: 'contradicted', quote: line.trim(), code: 'build_failed' };
  for (const line of lines) if (BUILD_OK.some((re) => re.test(line))) return { answer: 'shown', quote: line.trim(), code: 'build_success_line' };
  return null;
}
