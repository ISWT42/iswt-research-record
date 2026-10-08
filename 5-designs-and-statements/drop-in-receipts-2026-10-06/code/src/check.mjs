// The check: for each completion claim, which tool call (if any) settles it, by rule, with no model.
//
//   shown          a line the tool printed shows the claimed operation succeeded on the claimed object
//   contradicted   a line (or a non-zero exit code) shows it failed
//   not shown      nothing settles it. "Needs a reader": the rules could not settle it. A model reader is a later
//                  step, behind an off-by-default option; this file never calls one.
//
// How a claim is linked to evidence
//   1. By operation: a push claim looks at `git push` calls, a tests claim at test runs, and so on (shell.mjs).
//      A read (cat, grep, git status, ...) or an echo is never evidence that something was done.
//   2. By object: every name the claim holds (path, branch, host, version, PR number, environment) must appear in the
//      call's command or output, or the call is about something else and is passed over.
//   3. The LATEST call that settles decides. A failure after a success is "mixed", which is "not shown", never a pass.
//   4. A quote is one line of the tool output (never the command, never the agent's summary), checked to be in that
//      output word for word. An echo of the command, a quote that cites a failure word, and an output whose terminal
//      overwrites could hide a failure all turn "shown" into "not shown".
import { normalizeOutput, overwrittenFailures, failureMarkers, SHOWN, CONTRADICTED, NOT_SHOWN, sha256, redact, oneLine } from './text.mjs';
import { analyzeCommand, isScopedRun } from './shell.mjs';
import { objectMatch, hasSpecificObject, holdsWord } from './objects.mjs';
import { exitFailure } from './exitcode.mjs';
import { testOutcome, buildOutcome, parseTestRuns } from './summaries.mjs';
import { pushOutcome, mergeOutcome, commitOutcome, createOutcome } from './gitout.mjs';
import { httpStatuses, finalStatus, bodyFailureMarkers } from './httpout.mjs';
import { EDIT_TOOLS } from './transcript.mjs';

// ---- calls ---------------------------------------------------------------------------------------------
const SHELL_TOOL = /^(?:Bash|PowerShell)$|(?:^|__)(?:bash|shell|powershell|terminal|run_command|exec)(?:$|_)/i;
const ACTION_TOOL = /(?:send|create|update|delete|post|merge|publish|deploy|upload|write|set|add|remove|trigger|run|execute|start|stop|restart|approve|submit|commit|push|reply|forward|invite|cancel)/i;
const NAME_FAMILIES = [
  [/merge/i, 'merge'], [/(?:^|_)push(?:$|_)/i, 'push'], [/create_(?:pull_request|issue|branch)|create_release|open_pr/i, 'create'],
  [/send|reply|forward|post_message|comment/i, 'send'], [/deploy|publish|release/i, 'deploy'],
];

// A transcript call -> what the rules read: normalised output, the command, and what kind of operation it was.
export function prepareCall(call) {
  const shell = SHELL_TOOL.test(call.tool);
  const command = shell ? String(call.input?.command ?? call.input?.cmd ?? '') : '';
  const raw = String(call.result?.text ?? '');
  const output = normalizeOutput(raw);
  let analysis;
  if (shell) {
    analysis = analyzeCommand(command, { powershell: /powershell/i.test(call.tool) });
  } else {
    const families = new Set(NAME_FAMILIES.filter(([re]) => re.test(call.tool)).map(([, f]) => f));
    const isOp = ACTION_TOOL.test(call.tool);
    analysis = { families, isRead: !isOp, isEcho: false, isOp, dry: false, http: null, programs: [], subs: [] };
  }
  const haystack = shell ? command + '\n' + output : `${call.tool} ${safeJson(call.input)}\n${output}`;
  return {
    id: call.id, tool: call.tool, order: call.order, command, input: call.input, raw, output, haystack,
    isError: call.result?.isError === true, structured: call.result?.structured ?? null, shell,
    families: analysis.families, isRead: analysis.isRead, isEcho: analysis.isEcho, dry: analysis.dry === true, http: analysis.http,
  };
}

const safeJson = (value) => { try { return JSON.stringify(value) ?? ''; } catch { return ''; } };

// ---- what each kind of claim looks at ----------------------------------------------------------------------
const STRICT_FAMILIES = {
  tests: ['test'], fix: ['test', 'build'], build: ['build'], push: ['push'], merge: ['merge'], commit: ['commit'],
  deploy: ['deploy'], send: ['send'], create: ['create'], install: ['install'], change: ['deploy'], live: [], done: [], unknown: [],
};
// These kinds may also be settled by an HTTP call or any operation that names the claimed object.
const OBJECT_LINKED = new Set(['deploy', 'send', 'create', 'change', 'live', 'done', 'unknown']);
// An HTTP 2xx is itself the receipt only for these (the request succeeded is what the claim says).
const HTTP_SHOWS = { send: ['POST', 'PUT', 'PATCH'], create: ['POST', 'PUT', 'PATCH'], live: ['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', null] };
const UNIVERSAL = /\b(?:all|every|entire|whole|full|everything)\b|\btest[- ]suites?\b|\bsuite\b/i;
const STATUS_CLAIM = /\b(?:returns?|returned|responds?|responded|responding|status(?:\s+code)?|http)\s*(?:with\s+|of\s+|:\s*)?(?:an?\s+)?(?:http\s+)?(?:status\s+)?(?:code\s+)?([1-5]\d\d)\b/i;
const STATUS_NEGATIVE = /\b(?:unauthori[sz]ed|forbidden|not found|rejected|denied|blocked|errors?|fails?|failing|failed|expected to (?:fail|reject))\b/i;

const claimedStatus = (claim) => { const m = STATUS_CLAIM.exec(claim.segment ?? claim.text ?? ''); return m ? Number(m[1]) : null; };

// ---- vetoes: reasons a quote may not be trusted --------------------------------------------------------------
const squash = (s) => String(s).replace(/\s+/g, ' ').trim();

function vetoShown(call, quote, code) {
  if (!quote || !call.output.includes(quote)) return 'quote_not_in_record';
  if (call.command && squash(call.command).includes(squash(quote))) return 'echo_of_command';
  // a branch called fix-error-handling is a name, not a failure: look at a push line without its ref names
  const checked = code === 'push_ref_updated' ? quote.replace(/\s\S+\s+->\s+\S+.*$/, '') : quote;
  if (failureMarkers(checked).length > 0) return 'shown_citing_failure';
  if (overwrittenFailures(call.raw).length > 0) return 'shown_over_overwritten_failure';
  return null;
}

// ---- evidence in one call -------------------------------------------------------------------------------------
function httpEvidence(claim, call) {
  const statuses = httpStatuses(call.output, { bareStatus: call.http?.bareStatus === true });
  const fin = finalStatus(statuses);
  if (!fin) return null;
  const said = claimedStatus(claim);
  if (said !== null) {
    if (fin.status === said) return { answer: SHOWN, quote: fin.line, code: 'http_status_claimed', http: fin };
    return { answer: CONTRADICTED, quote: fin.line, code: 'http_status_differs', http: fin };
  }
  if (STATUS_NEGATIVE.test(claim.segment ?? claim.text ?? '')) return null;
  const method = fin.method ?? call.http?.method ?? null;
  if (fin.status >= 400) return { answer: CONTRADICTED, quote: fin.line, code: 'http_4xx5xx', http: fin };
  const allowed = HTTP_SHOWS[claim.kind];
  if (!allowed) return { answer: null, code: 'http_2xx_is_not_the_state' };
  if (!allowed.includes(method)) return { answer: null, code: 'http_method_does_not_show_it' };
  const markers = bodyFailureMarkers(call.output, fin);
  if (markers.length > 0) return { answer: null, code: 'http_body_has_failure_marker', markers };
  return { answer: SHOWN, quote: fin.line, code: 'http_2xx', http: fin };
}

function specificEvidence(claim, call) {
  switch (claim.kind) {
    case 'tests':
    case 'fix': {
      const t = testOutcome(call.output);
      if (t) return t;
      return claim.kind === 'fix' ? buildOutcome(call.output) : null;
    }
    case 'build': return buildOutcome(call.output);
    case 'push': return pushOutcome(call.output);
    case 'merge': return mergeOutcome(call.output);
    case 'commit': return commitOutcome(call.output);
    case 'create': return createOutcome(call.output) ?? httpEvidence(claim, call);
    case 'install': return null;
    default: return httpEvidence(claim, call);
  }
}

// One call's answer for one claim: {answer, quote, code, ...} (answer may be null), or null when it says nothing.
function evidenceIn(claim, call) {
  const spec = specificEvidence(claim, call);
  const failure = exitFailure(call);
  if (spec?.answer === CONTRADICTED) return spec;
  if (spec?.answer === SHOWN) {
    // A line says it happened but the command also failed (a later part of a compound command, say): not settled.
    if (failure) return { answer: null, code: 'mixed_evidence', quote: failure.line };
    const veto = vetoShown(call, spec.quote, spec.code);
    if (veto) return { answer: null, code: veto, quote: spec.quote };
    return spec;
  }
  if (failure) {
    const code = failure.source === 'harness' ? 'exit_nonzero' : failure.source === 'is_error' ? 'tool_error' : 'exit_nonzero_in_output';
    return { answer: CONTRADICTED, quote: failure.line, code, exit: failure };
  }
  return spec;
}

// ---- one claim ----------------------------------------------------------------------------------------------
function link(claim, calls) {
  const wanted = STRICT_FAMILIES[claim.kind] ?? [];
  const specific = hasSpecificObject(claim.objects);
  const subject = claim.subject ?? [];
  const linked = [];
  let mismatched = 0;
  let dry = 0;
  for (const call of calls) {
    if (call.isRead) {                              // a read, an echo or a dry run never settles "done"
      if (call.dry && wanted.some((f) => call.families.has(f))) dry++;
      continue;
    }
    const byFamily = wanted.some((f) => call.families.has(f))
      || ((claim.kind === 'tests' || claim.kind === 'fix') && parseTestRuns(call.output).length > 0);
    const byObject = OBJECT_LINKED.has(claim.kind) && specific;
    if (!byFamily && !byObject) continue;
    const hay = call.haystack;
    const m = objectMatch(claim.objects, hay, { useWeak: OBJECT_LINKED.has(claim.kind) });
    const subjectMissing = subject.filter((word) => !holdsWord(hay, word));
    if (!m.ok || subjectMissing.length > 0) { if (byFamily) mismatched++; continue; }
    linked.push(call);
  }
  return { linked, mismatched, dry };
}

const WHY = {
  tests_pass: 'a test-runner summary line shows the tests passed',
  tests_failed: 'a test-runner summary line shows tests failed',
  build_success_line: 'a build line shows it succeeded',
  build_failed: 'a build line shows it failed',
  push_ref_updated: 'git printed the ref it updated',
  push_rejected: 'git printed that the push was rejected or failed',
  merge_done: 'the merge printed that it was done',
  merge_failed: 'the merge printed that it failed',
  commit_made: 'git printed the commit it made',
  commit_failed: 'git printed that the commit failed',
  created_url: 'the command printed the address of what it created',
  http_2xx: 'the request returned a 2xx status',
  http_status_claimed: 'the response status is the one the claim names',
  http_status_differs: 'the response status is not the one the claim names',
  http_4xx5xx: 'the request returned a 4xx or 5xx status',
  exit_nonzero: 'the command exited with a non-zero code',
  exit_nonzero_in_output: 'the command printed a non-zero exit code',
  tool_error: 'the tool reported an error',
  no_call: 'no tool call in this turn did that operation',
  dry_run_only: 'the only matching call in this turn was a dry run, which prints what it would do and changes nothing',
  object_mismatch: 'the tool calls in this turn are about something else than the claim names',
  no_confirming_line: 'the command ran but no line it printed confirms the claim (a zero exit code alone is not a receipt)',
  mixed_evidence: 'one call shows success and another shows failure',
  push_mixed: 'the push updated some refs and rejected others',
  push_up_to_date: 'git said everything was already up to date, so this push did nothing',
  merge_mixed: 'the output shows both a merge and a failure',
  merge_not_done: 'the merge was queued or changed nothing',
  commit_mixed: 'the output shows both a commit and a failure',
  no_tests_ran: 'the runner ran no tests',
  claimed_count_mismatch: 'the number of tests in the claim is not in the summary',
  scoped_run: 'the claim covers everything but the run covered only part',
  echo_of_command: 'the line is an echo of the command, not a result',
  shown_citing_failure: 'the line that would settle it also names a failure',
  shown_over_overwritten_failure: 'a terminal overwrite in the output could hide a failure',
  quote_not_in_record: 'the line is not in the tool output',
  http_2xx_is_not_the_state: 'a 2xx status shows the request was accepted, not that the claimed state holds',
  http_method_does_not_show_it: 'that kind of request does not show the claimed operation',
  http_body_has_failure_marker: 'the response is 2xx but its body shows a failure marker',
  fix_failed_then_passed: 'the same kind of run failed earlier in this turn and passes now',
  fix_not_tied_to_run: 'a run passed or failed, but nothing ties it to this fix: it did not fail earlier in this turn and none of the claim\'s words appear in it',
};
export const whyText = (code) => WHY[code] ?? code.replaceAll('_', ' ');

export function settleClaim(claim, calls, { editOrders = [] } = {}) {
  const base = { claim, quote: null, source: null, stale_edits: 0, layer: 'deterministic' };
  const { linked, mismatched, dry } = link(claim, calls);
  if (linked.length === 0) {
    const code = mismatched > 0 ? 'object_mismatch' : dry > 0 ? 'dry_run_only' : 'no_call';
    return { ...base, answer: NOT_SHOWN, code, reason: whyText(code), needs_reader: true };
  }
  const attempts = linked.map((call) => ({ call, ev: evidenceIn(claim, call) }));
  const settled = attempts.filter((a) => a.ev?.answer);
  let chosen = null;
  let code;

  if (settled.length === 0) {
    const info = attempts.map((a) => a.ev).filter((e) => e?.code).at(-1);
    code = info?.code ?? 'no_confirming_line';
    chosen = attempts.at(-1);
    return finish(base, { answer: NOT_SHOWN, code, quote: null, call: chosen.call });
  }
  const latest = settled.at(-1);
  if (latest.ev.answer === CONTRADICTED && settled.some((a) => a.ev.answer === SHOWN)) {
    return finish(base, { answer: NOT_SHOWN, code: 'mixed_evidence', quote: null, call: latest.call });
  }
  if (claim.kind === 'fix') {
    // A passing (or failing) run does not by itself show that THIS bug was fixed. A run that failed earlier in the
    // turn and passes now does; so does a run that mentions what the claim says was fixed.
    const earlierFailure = settled.slice(0, -1).some((a) => a.ev.answer === CONTRADICTED);
    const named = (claim.fixWords ?? []).some((w) => holdsWord(latest.call.haystack, w));
    if (latest.ev.answer === SHOWN) {
      if (!earlierFailure && !named) return finish(base, { answer: NOT_SHOWN, code: 'fix_not_tied_to_run', quote: null, call: latest.call });
    } else if (!named) {
      return finish(base, { answer: NOT_SHOWN, code: 'fix_not_tied_to_run', quote: null, call: latest.call });
    }
    if (latest.ev.answer === SHOWN && earlierFailure) {
      return finish(base, { answer: SHOWN, code: 'fix_failed_then_passed', quote: latest.ev.quote, call: latest.call }, editOrders);
    }
  }
  if (latest.ev.answer === SHOWN) {
    const run = latest.ev.run;
    if (claim.kind === 'tests' && claim.counts?.length && run && !claim.counts.some((n) => n === run.passed || n === run.total)) {
      return finish(base, { answer: NOT_SHOWN, code: 'claimed_count_mismatch', quote: null, call: latest.call });
    }
    if ((claim.kind === 'tests' || claim.kind === 'fix') && UNIVERSAL.test(claim.segment ?? '') && isScopedRun(latest.call.command)) {
      return finish(base, { answer: NOT_SHOWN, code: 'scoped_run', quote: null, call: latest.call });
    }
  }
  return finish(base, { answer: latest.ev.answer, code: latest.ev.code, quote: latest.ev.quote, call: latest.call }, editOrders);
}

function finish(base, { answer, code, quote, call }, editOrders = []) {
  const source = call ? {
    tool_use_id: call.id, tool: call.tool, command: oneLine(redact(call.command), 300),
    output_sha256: sha256(call.raw), output_chars: call.raw.length,
  } : null;
  const staleEdits = answer === SHOWN && call ? editOrders.filter((o) => o > call.order).length : 0;
  return {
    ...base, answer, code, quote: quote ? redact(quote) : null, source, stale_edits: staleEdits,
    reason: whyText(code), needs_reader: answer === NOT_SHOWN,
  };
}

// All claims of a turn against all calls of the turn.
export function checkClaims(claims, calls, options = {}) {
  return claims.map((claim) => settleClaim(claim, calls, options));
}

export function tally(results) {
  const counts = { shown: 0, contradicted: 0, 'not shown': 0 };
  for (const r of results) counts[r.answer]++;
  return counts;
}

// The whole turn: {results, counts, calls}. `turn` comes from transcript.turnEvidence().
export function checkTurn(turn, claims) {
  const calls = turn.calls.map(prepareCall);
  const editOrders = (turn.allCalls ?? []).filter((c) => EDIT_TOOLS.has(c.tool) && !(c.result?.isError)).map((c) => c.order);
  const results = checkClaims(claims, calls, { editOrders });
  return { results, counts: tally(results), calls: calls.length };
}
