// Finds the completion claims in an agent's final message: sentences that say something is done, passing,
// deployed, sent, merged, fixed and so on. Kept conservative on purpose: a missed claim is only a missed check, but a
// claim that was never made would be checked, and in gate mode block the agent for nothing. So a sentence is a claim
// only in a positive past, perfect or state form ("I pushed", "has been merged", "tests pass", "is live"), and is
// skipped when it is a question, an instruction, a plan, a condition, a hedge, a negation, a partial claim, or when
// it admits failures in the same breath.
//
// Code blocks and quotations are never claims (they are copies, not assertions).
import { extractObjects } from './objects.mjs';
import { BENIGN_FAILURE_WORDS, oneLine } from './text.mjs';

export const KINDS = ['tests', 'build', 'fix', 'push', 'merge', 'commit', 'deploy', 'send', 'create', 'install', 'change', 'live', 'done'];
export const MAX_CLAIMS = 24;
export const MAX_SENTENCE_CHARS = 3000;

// ---- from message to clauses -------------------------------------------------------------------------
export function stripCode(text) {
  const kept = [];
  let fence = null;
  for (const line of String(text ?? '').split('\n')) {
    const m = /^\s*(```+|~~~+)/.exec(line);
    if (fence) {
      if (m && m[1][0] === fence[0] && m[1].length >= fence.length) fence = null;
      continue;
    }
    if (m) { fence = m[1]; continue; }
    kept.push(line);
  }
  return kept.join('\n');
}

function plainLine(line) {
  return line
    .replace(/[’‘]/g, "'")
    .replace(/^\s*(?:[-*+•]|\d+[.)])\s+/, '')
    .replace(/^\s*\[[ xX]\]\s+/, '')
    .replace(/[\p{Extended_Pictographic}️✓✔✗✘]/gu, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)')
    .replace(/\*\*|__/g, '')
    .replace(/(?<![\w*])\*([^*\n]+)\*(?![\w*])/g, '$1')
    .replace(/\s+/g, ' ')
    .trim();
}

export function sentencesOf(message) {
  const sentences = [];
  for (const rawLine of stripCode(message).split('\n')) {
    const line = rawLine.trim();
    if (!line) continue;
    if (/^>/.test(line)) continue;                       // a quotation
    if (/^#{1,6}\s/.test(line)) continue;                // a heading
    if (/^\|?[\s:|-]+\|?$/.test(line) && line.includes('-')) continue; // a table rule
    let text = line;
    if (text.startsWith('|')) text = text.replace(/^\||\|$/g, '').split('|').map((c) => c.trim()).filter(Boolean).join('; ');
    const plain = plainLine(text);
    if (!plain || /:$/.test(plain)) continue;            // a lead-in to a list
    for (const part of plain.split(/(?<=[.!?])\s+(?=[A-Z0-9"'(\[`*_-])/)) {
      // A real claim sentence is short. A "sentence" of many thousands of characters is pasted data; only its start is
      // read, which keeps the work for one sentence bounded (it grows with the square of the length).
      if (part.trim()) sentences.push(part.trim().slice(0, MAX_SENTENCE_CHARS));
    }
  }
  return sentences;
}

const CLAUSE_SPLIT = /;\s+|\s+[—–]\s+|\s+-\s+|,\s+(?:but|however|although|though|while|whereas)\s+|\s+(?:but|however|although|though|whereas)\s+/i;
export const clausesOf = (sentence) => sentence.split(CLAUSE_SPLIT).map((c) => c.replace(/^(?:and|so|then|also|plus|now)\s+/i, '').trim()).filter(Boolean);

// A sentence that is not an assertion about work done.
const NOT_AN_ASSERTION = /^(?:please|run|try|use|check|make sure|ensure|remember|consider|note that|note:|let me|let's|you (?:can|may|should|could|will|need|might|must|'ll)|if you|when you|once you|before you|after you|to (?!be clear|summari[sz]e|sum up|recap|confirm|clarify|conclude)[a-z]+|next|todo|to do|follow-?ups?|still to do|remaining|want me to|would you like|do you want|shall i|should i|i can|i could|i would|i'll|i will|i'd|i should|i need to|i plan|i'm going to|i am going to)\b/i;

// Words before a verb that make it not-a-claim: negation, modals, plans, conditions, attempts, hedges.
const NEGATION = /\b(?:not|never|nothing|none|nobody|no one|no longer|cannot|can't|couldn't|unable|failed to|fail to|didn't|don't|doesn't|won't|wouldn't|shouldn't|haven't|hasn't|hadn't|isn't|aren't|wasn't|weren't|yet to|still (?:need|needs|have|has) to|need to|needs to|have to|has to|must|should|would|could|might|may|will|'ll|going to|about to|plan(?:s|ning)? to|want(?:s)? to|ready to|able to|to be|if|once|when|whenever|after|before|until|unless|whether|so that|in order to|try(?:ing)? to|tried to|attempt(?:ed|ing)? to|get|getting|gets|make|making|makes|keep|keeping|keeps|ensure|ensuring|without|instead of|rather than|hope|hopefully|probably|presumably|likely|supposedly|seems? to|appears? to|looks? like|assum\w+|expect\w*)\b|n't\b/i;
const PARTIAL = /\b(?:except|apart from|aside from|other than|besides|but for|mostly|most of|the majority|almost|nearly|partially|partly|some of|a few of|only some|so far|up to a point)\b/i;
const DISCLOSED_FAILURE = /\b(?:\d+|some|two|three|four|five|a few|several|one|many|multiple)\s+(?:(?:pre-?existing|unrelated|known|expected|flaky|intermittent|remaining|other|other)\s+)*(?:tests?\s+|specs?\s+|checks?\s+)?(?:fail(?:ed|ing|ures?|s)?|errors?|broken|red)\b|\b(?:pre-?existing|unrelated|known|flaky|intermittent)\s+(?:test\s+)?(?:fail\w*|errors?)\b/i;

const FIRST_PERSON = /\b(?:i|we|i've|we've|i'd|we'd)\b/i;
// A passive reports an event when an adverb says so ("is now enabled", "was successfully sent"). The text before the verb
// has been trimmed, so a bare "is" or "was" ends it and does not match PASSIVE_TAIL: a bare "was posted by the client
// code" describes code, and a bare "is enabled" can describe a setting. Two bare forms are taken anyway:
//   "has been sent", "have been merged" (PERFECT_PASSIVE): the present perfect is an event, not a description;
//   "is fixed", "was resolved" with a bug-like subject (PASSIVE_STATE and FIX_SUBJECT), for the fix kind only.
const PASSIVE_TAIL = /\b(?:is|are|was|were|be|been|get|got)\s+(?:(?:now|already|successfully|finally|also|all|both|just)\s*)*$/i;
const PERFECT_PASSIVE = /\b(?:has|have|had)\s+been\s*(?:(?:now|already|successfully|finally|also|all|both|just)\s*)*$/i;
const PASSIVE_STATE = /\b(?:is|are|was|were)\s*(?:(?:now|already|successfully|finally|also|all|both|just)\s*)*$/i;
const FIX_SUBJECT = /\b(?:bugs?|issues?|problems?|errors?|crash(?:es)?|regressions?|failures?|leaks?|typos?|defects?|conflicts?|tests?|vulnerabilit(?:y|ies)|exceptions?|warnings?|flak(?:e|y|iness))\b/i;
const LEADING_ADVERBS = /^(?:(?:now|finally|successfully|also|already|just|then|both|all|and|so|plus)\s+)+/i;
const GIT_CONTEXT = /\b(?:origin|upstream|remote|branch|branches|repo|repository|github|gitlab|bitbucket|main|master|develop|trunk|commits?|prs?|pull[- ]requests?|changes?|work|fix(?:es)?|patch|it|them|everything|release|tag)\b/i;
const DEPLOY_CONTEXT = /\b(?:to|on|in|at)\s+(?:prod(?:uction)?|staging|stage|dev|qa|canary|the\s+(?:site|server|cluster|registry|store|cloud|web)|npm|pypi|crates|docker|github|vercel|netlify|heroku|aws|gcp|azure|cloudflare)\b|\bversion\b|\bv?\d+\.\d+(?:\.\d+)?\b|\b(?:site|service|app|package|release|build|image|api|page|website|worker|function|lambda|rule|dashboard|migration)\b/i;

// The claim patterns. `verb` finds the word, `need` (optional) is a context the clause must also have.
const VERBS = [
  { kind: 'fix', verb: /\b(?:fixed|resolved|patched|solved|repaired|corrected)\b(?![- ](?:width|size|point|length|position|height|number|set|rate|price|cost|term|list|interval|delay|ip|income|cap|amount))/gi },
  { kind: 'push', verb: /\b(?:force[- ])?pushed\b/gi, context: GIT_CONTEXT },
  { kind: 'merge', verb: /\bmerged\b/gi, need: /\b(?:prs?|pull[- ]requests?|branch(?:es)?|#\d+|into|to (?:main|master|develop|trunk|dev)|main|master|develop|upstream|origin)\b/i, context: GIT_CONTEXT },
  { kind: 'commit', verb: /\bcommitted\b/gi, context: GIT_CONTEXT },
  { kind: 'deploy', verb: /\b(?:deployed|published|released|shipped|launched|rolled[- ]out|promoted)\b/gi, context: DEPLOY_CONTEXT },
  { kind: 'send', verb: /\b(?:sent|emailed|mailed|posted|submitted|uploaded|delivered|forwarded|replied|messaged|notified|dispatched)\b/gi },
  { kind: 'create', verb: /\b(?:created|opened|filed|raised|cut|tagged|drafted)\s+(?:(?:a|an|the|new|another|draft|follow-?up|tracking)\s+)*(?:pr|pull[- ]request|issue|ticket|branch|tag|release|gist|repo|repository|incident|deployment|invoice|calendar event|event|meeting|reminder)s?\b/gi },
  { kind: 'install', verb: /\b(?:installed|upgraded|downgraded)\b/gi },
  { kind: 'change', verb: /\b(?:enabled|disabled|activated|deactivated|configured|registered|provisioned|rotated|restarted|restored|reverted|rolled[- ]back|migrated|scaled|cancell?ed|revoked|renewed)\b/gi },
  { kind: 'live', verb: /\b(?:(?:is|are|now|went|goes|gone)\s+live|(?:is|are|now)\s+(?:up and running|online|reachable|serving traffic))\b/gi, noQualifier: true },
  { kind: 'live', verb: /\b(?:returns?|returned|responds?|responded|responding)\s+(?:with\s+)?(?:an?\s+)?(?:http\s+)?(?:status\s+)?(?:code\s+)?[1-5]\d\d\b(?!\s+(?:items?|rows?|records?|results?|bytes?|lines?|users?|entries|files?|objects?|elements?|tests?|errors?|ms|seconds?))/gi, noQualifier: true },
  { kind: 'done', verb: /\b(?:completed|finished|wrapped up)\b/gi, needObject: true },
];

const PASS_WORD = /\b(?:pass(?:es|ed|ing)?|green|succeed(?:s|ed)?|succeeding|clean)\b/gi;
// "pass on" and "pass in" are left out of this list on purpose: "the tests pass on main", "pass in CI" are test claims.
const PASS_NOT_PASSING = /^\s*(?:through|along|over|into|by|off|up|down|out|to|from|around|away)\b/i;
const TEST_NOUN = /\b(?:tests?|test[- ]suites?|suites?|specs?|test[- ]cases?|checks?|ci|pipelines?|workflows?|pytest|jest|vitest|mocha|junit|rspec|unittests?|e2e)\b/gi;
const BUILD_NOUN = /\b(?:builds?|compil(?:e|es|ed|er|ation)|lint(?:ing|er|s)?|type-?check(?:ing|s)?|type check(?:ing|s)?|tsc|eslint|ruff|mypy|pyright|flake8|clippy|biome|prettier)\b/gi;
const COUNT_CLAIMS = [
  /\b(\d+)\s+(?:(?:unit|integration|e2e|total)\s+)?(?:tests?|specs?|cases?)\s+(?:are\s+|now\s+|all\s+)*(?:passed|passing|pass)\b/i,
  /\b(\d+)\s*\/\s*(\d+)\s+(?:tests?\s+)?pass/i,
  /\b(?:all\s+)?(\d+)\s+(?:passed|passing)\b/i,
];
const EVERYTHING_GREEN = /\b(?:everything|all)\s+(?:is\s+|are\s+|now\s+)*(?:passing|green|passes|pass)\b/i;

function lastMatch(re, text) {
  let last = null;
  for (const m of text.matchAll(new RegExp(re.source, re.flags.includes('g') ? re.flags : re.flags + 'g'))) last = m;
  return last;
}

function qualifierOf(before, spec, clause) {
  const b = before.trim();
  if (FIRST_PERSON.test(b)) return 'first-person';
  if (b.replace(LEADING_ADVERBS, '') === '') return 'initial';
  if (PASSIVE_TAIL.test(b) || PERFECT_PASSIVE.test(b)) return 'passive';
  if (spec.kind === 'fix' && PASSIVE_STATE.test(b) && FIX_SUBJECT.test(b)) return 'passive';
  // a short status phrase like "Fix pushed to origin" or "Branch merged into main"
  if (spec.context && b.split(/\s+/).length <= 4 && spec.context.test(clause)) return 'status';
  return null;
}

function negatedBefore(before) {
  const tail = before.split(/[,:(]/).pop();   // only the part since the last comma
  return NEGATION.test(tail.slice(-90));
}

const hasDisclosedFailure = (sentence) => {
  const cleaned = sentence.replace(BENIGN_FAILURE_WORDS, ' ');
  return DISCLOSED_FAILURE.test(cleaned) || PARTIAL.test(cleaned);
};

// Hits for one clause: [{kind, index, label, counts?}]
function findHits(clause, sentence) {
  const hits = [];

  // tests and builds: "<subject> ... pass"
  for (const m of clause.matchAll(PASS_WORD)) {
    const before = clause.slice(0, m.index);
    const after = clause.slice(m.index + m[0].length);
    if (PASS_NOT_PASSING.test(after)) continue;
    const window = before.slice(-80);
    const testNoun = lastMatch(TEST_NOUN, window);
    const buildNoun = lastMatch(BUILD_NOUN, window);
    const near = (n) => n && window.slice(n.index + n[0].length).trim().split(/\s+/).filter(Boolean).length <= 6;
    let kind = null;
    let nounIndex = 0;
    if (near(buildNoun) && (!near(testNoun) || buildNoun.index > testNoun.index)) { kind = 'build'; nounIndex = before.length - window.length + buildNoun.index; }
    else if (near(testNoun)) { kind = 'tests'; nounIndex = before.length - window.length + testNoun.index; }
    if (!kind) continue;
    if (/^clean$/i.test(m[0]) && kind !== 'build') continue;
    if (negatedBefore(before.slice(nounIndex)) || negatedBefore(before)) continue;
    hits.push({ kind, index: nounIndex, end: m.index + m[0].length, label: m[0] });
  }
  for (const re of COUNT_CLAIMS) {
    const m = re.exec(clause);
    if (m && !negatedBefore(clause.slice(0, m.index))) hits.push({ kind: 'tests', index: m.index, end: m.index + m[0].length, label: m[0], counts: m.slice(1).filter(Boolean).map(Number) });
  }
  const g = EVERYTHING_GREEN.exec(clause);
  if (g && !negatedBefore(clause.slice(0, g.index))) hits.push({ kind: 'tests', index: g.index, end: g.index + g[0].length, label: g[0] });

  // verbs
  for (const spec of VERBS) {
    for (const m of clause.matchAll(spec.verb)) {
      const before = clause.slice(0, m.index);
      if (negatedBefore(before)) continue;
      if (spec.need && !spec.need.test(clause)) continue;
      const q = spec.noQualifier ? 'state' : qualifierOf(before, spec, clause);
      if (!q) continue;
      if (spec.needObject) {
        const rest = clause.slice(m.index + m[0].length).trim().split(/\s+/).filter(Boolean);
        if (rest.length < 2) continue;
      }
      hits.push({ kind: spec.kind, index: m.index, end: m.index + m[0].length, label: m[0], qualifier: q });
    }
  }
  return hits;
}

// Two hits of the same kind in one clause are one claim (the count form and the noun form of "all 14 tests pass").
function mergeHits(hits) {
  const byKind = new Map();
  for (const h of [...hits].sort((a, b) => a.index - b.index)) {
    const prev = byKind.get(h.kind);
    if (!prev) byKind.set(h.kind, { ...h });
    else {
      if (h.counts && !prev.counts) prev.counts = h.counts;
      prev.end = Math.max(prev.end, h.end);
    }
  }
  return [...byKind.values()].sort((a, b) => a.index - b.index);
}

const JOINER = /(?:,|;|\band\b|\bthen\b|\bplus\b|\balso\b)\s*/gi;

// The part of the clause that belongs to each claim. The first starts with the clause; each later one starts after the
// conjunction that comes before its own verb ("... and I fixed the bug" -> "I fixed the bug").
export function segmentsOf(clause, hits) {
  const starts = hits.map((hit, i) => {
    if (i === 0) return 0;
    const from = hits[i - 1].end;
    const joiner = [...clause.slice(from, hit.index).matchAll(JOINER)].pop();
    return joiner ? from + joiner.index + joiner[0].length : hit.index;
  });
  return hits.map((_, i) => clause.slice(starts[i], i + 1 < hits.length ? starts[i + 1] : clause.length));
}

const trimSegment = (s) => s.replace(/^[\s,;:]+/, '').replace(/(?:[\s,;]|\b(?:and|then|plus|also)\b)+$/gi, '').trim();

const FIX_STOP = new Set(['fixed', 'resolved', 'patched', 'solved', 'repaired', 'corrected', 'bug', 'bugs', 'issue', 'issues', 'error', 'errors', 'problem', 'problems',
  'crash', 'crashes', 'failure', 'failures', 'regression', 'this', 'that', 'with', 'from', 'into', 'onto', 'have', 'been', 'were', 'also', 'just', 'then', 'here',
  'there', 'but', 'not', 'some', 'more', 'another', 'other', 'which', 'what', 'when', 'where', 'because', 'after', 'before', 'first', 'second', 'again', 'still',
  'working', 'works', 'code', 'test', 'tests', 'failing', 'passing', 'edge', 'case', 'cases', 'now', 'properly', 'correctly', 'finally', 'successfully', 'already',
  'caused', 'causing', 'cause', 'problem', 'thing', 'things', 'issue', 'wrong', 'broken', 'behaviour', 'behavior']);

// The words that say WHAT was fixed ("login" in "I fixed the login bug"): used to tie a fix to a test run.
function fixWordsOf(segment) {
  const words = segment.toLowerCase().match(/[a-z][a-z0-9_]{3,}/g) ?? [];
  return [...new Set(words.filter((w) => !FIX_STOP.has(w)))];
}

// "pushed to main", "into master", "the develop branch": a branch named as the destination of a push has to appear in the
// push command or in the ref line git printed, or a push of some other branch would settle it. (A plain "main" is not an
// object elsewhere: "the main issue" is prose.) Only push claims take it; for a merge the pull request number says which.
const BRANCH_AFTER_WORD = /\b(?:to|into|onto|on|in|at|from|of)\s+(?:the\s+)?(?:remote\s+|upstream\s+|origin\s+)?(main|master|develop|trunk)\b(?![\w/-])/gi;
const BRANCH_PUSHED = /\bpush(?:ed)?\s+(main|master|develop|trunk)\b(?![\w/-])(?=\s+(?:to|into|onto|branch)\b|\s*[.,;]|\s*$)/gi;   // "pushed main to origin", not "pushed the main fix"
const BRANCH_BEFORE_NOUN = /(?<![\w./-])(main|master|develop|trunk)\s+branch\b/gi;
function withBranches(objects, segment) {
  const named = [...segment.matchAll(BRANCH_AFTER_WORD), ...segment.matchAll(BRANCH_PUSHED), ...segment.matchAll(BRANCH_BEFORE_NOUN)].map((m) => m[1].toLowerCase());
  return named.length ? { ...objects, strong: [...new Set([...objects.strong, ...named])] } : objects;
}

// The claims of one final message: [{kind, text, sentence, segment, objects, counts, subject?, fixWords?}]
export function extractClaims(message) {
  const claims = [];
  const seen = new Set();
  const sentences = sentencesOf(message);
  for (const sentence of sentences) {
    if (sentence.endsWith('?') || NOT_AN_ASSERTION.test(sentence)) continue;
    for (const clause of clausesOf(sentence)) {
      if (clause.endsWith('?') || NOT_AN_ASSERTION.test(clause)) continue;
      let hits = findHits(clause, sentence);
      // a sentence that admits failures or exceptions does not claim that everything passes or is fixed
      hits = hits.filter((h) => !(['tests', 'build', 'fix'].includes(h.kind) && hasDisclosedFailure(sentence)));
      hits = mergeHits(hits);
      if (hits.length === 0) continue;
      // each claim's segment: from just after the conjunction before its own verb to just before the next claim's
      segmentsOf(clause, hits).forEach((segment, i) => {
        const hit = hits[i];
        const key = hit.kind + '|' + segment.toLowerCase();
        if (seen.has(key)) return;
        seen.add(key);
        const objects = hit.kind === 'push' ? withBranches(extractObjects(segment), segment) : extractObjects(segment);
        const claim = { kind: hit.kind, text: oneLine(trimSegment(segment), 220), sentence: oneLine(sentence, 300), segment, objects, counts: hit.counts ?? [] };
        if (hit.kind === 'tests' || hit.kind === 'build') {
          const countHit = !hit.counts && /\b(\d+)\s+(?:\w+\s+){0,2}?(?:tests?|specs?)\b/i.exec(segment);
          if (countHit) claim.counts = [Number(countHit[1])];
          claim.subject = subjectOf(segment);
        }
        if (hit.kind === 'fix') claim.fixWords = fixWordsOf(segment);
        claims.push(claim);
      });
    }
    if (claims.length >= MAX_CLAIMS) break;
  }
  return claims.slice(0, MAX_CLAIMS);
}

const SUBJECT_STOP = new Set(['all', 'the', 'a', 'an', 'my', 'our', 'these', 'those', 'new', 'existing', 'unit', 'integration', 'e2e', 'end-to-end',
  'regression', 'smoke', 'local', 'relevant', 'full', 'whole', 'entire', 'final', 'every', 'each', 'both', 'now', 'are', 'is', 'were', 'was',
  'and', 'of', 'that', 'which', 'passing', 'failing', 'test', 'tests', 'build', 'the', 'then', 'also', 'ci', 'suite', 'suites', 'specs', 'spec',
  'i', 'we', 'added', 'wrote', 'written', 'few', 'more', 'extra', 'additional', 'related', 'other', 'python', 'node', 'rust', 'go', 'java']);

// "auth tests pass" -> auth; "tests for the parser pass" -> parser; the word that says WHICH tests or build.
function subjectOf(segment) {
  const words = [];
  const before = /([\w.-]+)\s+(?:tests?|specs?|test[- ]suite|suite)\b/i.exec(segment);
  if (before) words.push(before[1]);
  const after = /\b(?:tests?|specs?|suite)\s+(?:in|for|of|on|covering|under)\s+(?:the\s+)?([\w./-]+)/i.exec(segment);
  if (after) words.push(after[1]);
  return words.map((w) => w.toLowerCase()).filter((w) => w.length > 1 && !SUBJECT_STOP.has(w) && !/^\d+$/.test(w));
}
