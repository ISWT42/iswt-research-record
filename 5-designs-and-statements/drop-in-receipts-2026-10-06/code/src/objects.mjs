// What a claim is ABOUT, so that a tool result about something else cannot settle it.
//
// strong tokens  names that identify the object: paths, files, URLs and hosts, versions, IPs, commit ids, e-mail
//                addresses, backticked names, and hyphenated or underscored names that sit next to a word like
//                "branch" or "service". Every one must appear in the call's command or output, or the call is
//                about a different object.
// prs            pull request / issue numbers (#42, PR 42).
// env            production, staging and the like: the claimed environment must appear, not another one.
// weak tokens    capitalised names in the middle of a sentence (Trontin, Stripe) and hyphenated prose words. Used
//                only for the claim kinds that have no stricter evidence (deploy, send, create, change, live, done):
//                at least one must appear.
//
// A token is matched case-insensitively as a whole word (no letter or digit touching it).

const FILE_EXT = 'py|js|mjs|cjs|ts|tsx|jsx|json|md|yml|yaml|toml|go|rs|java|kt|c|cc|cpp|h|hpp|sh|ps1|txt|csv|html|css|sql|lock|cfg|ini|xml|rb|php|swift|zone';
const URL_RE = /\bhttps?:\/\/[^\s)>\]"'`]+/gi;
const EMAIL_RE = /\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b/g;
const FILE_RE = new RegExp(String.raw`(?<![\w@/.-])(?:[\w.-]+/)*[\w.-]*[\w-]\.(?:${FILE_EXT})(?![\w])`, 'gi');
const HOST_RE = /\b(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+(?:com|net|org|io|dev|app|ai|co|ca|uk|de|eu|internal|example|test|local|cloud|sh|xyz|tech|info|biz|us|gov|edu)\b|\blocalhost(?::\d{2,5})?\b/gi;
const PATH_RE = /(?<![\w@:.-])(?:\.{0,2}\/)?[\w.@-]+(?:\/[\w.@-]+)+(?![\w@])/g;
const IP_RE = /\b\d{1,3}(?:\.\d{1,3}){3}\b/g;
const VERSION_RE = /\b(?:v\d+(?:\.\d+)+|\d+\.\d+\.\d+)(?:-[\w.]+)?\b/gi;
const PR_RE = /(?:#|\bPRs?\s*#?|\bpull[- ]requests?\s*#?|\bissues?\s*#?)(\d+)\b/gi;
const SHA_RE = /\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b/g;
const BACKTICK_RE = /`([^`\n]{1,80})`/g;
// hyphenated or underscored words; strong only in the contexts below
const NAME_RE = /(?<![\w@/.-])[a-z][a-z0-9]*(?:[-_][a-z0-9]+)+(?![\w@/-])/g;
const NAME_CONTEXT_BEFORE = /(?:(?:pushed|merged|rebased|checked out|cherry-picked)\s+(?:the\s+)?|(?:to|into|onto|from)\s+(?:the\s+)?)$|(?:branch(?:es)?|tag|repo(?:sitory)?|service|app|package|module|project|pipeline|job|release|cluster|namespace|bucket|table|rule|zone|image|container|function|method|class|script|command|workflow|environment|env|server|host|queue|topic|stream|database|db)\s+(?:named\s+|called\s+)?$/i;
const NAME_CONTEXT_AFTER = /^\s+(?:branch|tag|repo(?:sitory)?|service|app|package|module|project|pipeline|job|release|cluster|namespace|bucket|table|rule|zone|image|container|function|script|workflow|server|queue)\b/i;

// slashed pairs of ordinary words are not paths
const SLASH_WORDS = new Set(['and/or', 'either/or', 'yes/no', 'true/false', 'input/output', 'read/write', 'client/server', 'he/she', 'his/her',
  'w/o', 'n/a', 'i/o', 'tcp/ip', 'ui/ux', 'ci/cd', 'on/off', 'pass/fail', 'up/down', 'start/stop', 'before/after', 'in/out', '24/7', 'v/s',
  'front/back', 'and/or/the']);
// framework names that look like file names
const NOT_FILES = /^(?:node|next|nuxt|vue|react|express|three|d3|chart|angular|ember|backbone|alpine|svelte|socket)\.js$/i;

export const ENV_GROUPS = [
  ['production', 'prod', 'prd'],
  ['staging', 'stage', 'stg'],
  ['development', 'dev'],
  ['qa'],
  ['canary'],
  ['preview'],
];

const WEAK_STOP = new Set(['I', 'The', 'This', 'That', 'These', 'Those', 'It', 'Its', 'All', 'Both', 'My', 'Our', 'We', 'You', 'And', 'But', 'Also',
  'Now', 'Then', 'Here', 'There', 'Yes', 'No', 'OK', 'Done', 'Note', 'Next', 'See', 'PR', 'CI', 'API', 'URL', 'HTTP', 'HTTPS', 'JSON', 'ID', 'TODO',
  'README', 'CLI', 'UI', 'UX', 'SQL', 'CSS', 'HTML', 'TLS', 'SSL', 'SSH', 'CPU', 'GPU', 'OS', 'AI', 'LLM', 'MCP', 'PDF', 'CSV', 'JS', 'TS', 'Python',
  'JavaScript', 'TypeScript', 'Node', 'Windows', 'Linux', 'Mac', 'Git', 'GitHub', 'Claude', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
  'Saturday', 'Sunday', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']);

const trimToken = (t) => t.replace(/^[("'[<]+/, '').replace(/[.,;:)\]}>"'!?]+$/, '');
const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const uniq = (list) => [...new Set(list)];

// Take every match of `re` out of `work` (leaving a space), and return [what was picked from each match, the rest].
function take(work, re, pick = (m) => m[0]) {
  const found = [];
  const rest = work.replace(re, (...args) => {
    const m = args.slice(0, -2);
    m.index = args.at(-2);
    m.input = args.at(-1);
    const picked = pick(m);
    if (picked !== undefined) found.push(picked);
    return ' ';
  });
  return [found, rest];
}

export function extractObjects(rawText) {
  const raw = String(rawText ?? '').replace(/[’‘]/g, "'");
  const strong = [];
  const weakNames = [];
  const prs = [];
  let work = raw;
  let found;

  [found, work] = take(work, BACKTICK_RE, (m) => m[1]);
  for (const f of found) { const t = trimToken(f.trim()); if (t && !/\s/.test(t) && t.length >= 2) strong.push(t); }
  [found, work] = take(work, URL_RE);
  strong.push(...found.map(trimToken));
  [found, work] = take(work, EMAIL_RE);
  strong.push(...found.map(trimToken));
  [found, work] = take(work, PR_RE, (m) => m[1]);
  prs.push(...found);
  [found, work] = take(work, FILE_RE);
  strong.push(...found.map(trimToken).filter((t) => !NOT_FILES.test(t)));
  [found, work] = take(work, HOST_RE);
  strong.push(...found.map(trimToken));
  [found, work] = take(work, PATH_RE);
  strong.push(...found.map(trimToken).filter((t) => !SLASH_WORDS.has(t.toLowerCase())));
  [found, work] = take(work, IP_RE);
  strong.push(...found);
  [found, work] = take(work, VERSION_RE);
  strong.push(...found);
  [found, work] = take(work, SHA_RE);
  strong.push(...found);

  // hyphenated or underscored names: strong with a naming context, a digit or an underscore; otherwise weak
  [found, work] = take(work, NAME_RE, (m) => {
    const before = m.input.slice(0, m.index);
    const after = m.input.slice(m.index + m[0].length);
    const named = NAME_CONTEXT_BEFORE.test(before) || NAME_CONTEXT_AFTER.test(after) || /\d/.test(m[0]) || m[0].includes('_');
    return { token: m[0], named };
  });
  for (const { token, named } of found) (named ? strong : weakNames).push(token);

  const env = [];
  for (const group of ENV_GROUPS) {
    if (group.some((word) => new RegExp(`(?<![\\w-])${word}(?![\\w])`, 'i').test(raw))) env.push(group[0]);
  }

  // Capitalised words that are not the first word of the text.
  const weak = [];
  work.split(/\s+/).filter(Boolean).forEach((word, i) => {
    const t = trimToken(word).replace(/'s$/, '');
    if (i === 0 || !t || WEAK_STOP.has(t)) return;
    if (/^[A-Z][a-z]{2,}[\w-]*$/.test(t) || /^[A-Z]{3,6}$/.test(t)) weak.push(t);
  });

  return {
    strong: uniq(strong.map((t) => t.toLowerCase())).filter(Boolean),
    prs: uniq(prs),
    env: uniq(env),
    weak: uniq([...weak, ...weakNames].map((t) => t.toLowerCase())),
  };
}

const wordRe = (token) => new RegExp(`(?<![\\w])${escapeRe(token)}(?![\\w])`, 'i');

// A strong token is found when it is literally in the haystack, or, for a/b tokens (origin/main, acme/tools), when
// every part is a word of the haystack ("git push origin main" holds origin/main).
export function holdsToken(haystack, token) {
  if (wordRe(token).test(haystack)) return true;
  if (token.includes('/') && !/^https?:/.test(token)) {
    const parts = token.split('/').filter(Boolean);
    return parts.length > 1 && parts.every((p) => wordRe(p).test(haystack));
  }
  return false;
}

// A subject word ("parser" in "the parser tests pass") is held when it stands apart from other letters and digits,
// so test_parser.py, tests/parser/ and parser-tests all hold it, but "parsers" and "reparse" do not.
export const holdsWord = (haystack, word) => new RegExp(`(?<![A-Za-z0-9])${escapeRe(word)}(?![A-Za-z0-9])`, 'i').test(haystack);

// "#42", "pull request #42", "PR 42", "pull/42", "pulls/42/merge", or a number given to a gh pr command.
export function holdsPr(haystack, number) {
  const n = escapeRe(String(number));
  const pulls = /pull|merge|(?<![a-z])pr(?![a-z])/i.test(haystack);
  return [
    new RegExp(`(?<![\\w.])#${n}(?!\\d)`),
    new RegExp(`\\b(?:pull[- ]requests?|pulls?|PR|issues?)\\s*[#/]?\\s*${n}(?!\\d)`, 'i'),
    new RegExp(`\\bgh\\s+pr\\s+\\w+\\s+(?:[^\\n]*?\\s)?${n}(?![\\w.])`, 'i'),
    // a field of a tool call or response: "pullNumber": 42, pull_number=42, "pr_number": "42", "pull_request_id": 42
    new RegExp(`\\b(?:pull[_\\s-]?(?:request[_\\s-]?)?|pr[_\\s-]?)(?:number|num|id|no)["']?\\s*[:=]\\s*["']?${n}(?!\\d)`, 'i'),
    // a plain "number": 42 counts only inside a call or output that is about pull requests or merging
    ...(pulls ? [new RegExp(`(?<![\\w])number["']?\\s*[:=]\\s*["']?${n}(?!\\d)`, 'i')] : []),
  ].some((re) => re.test(haystack));
}

export function holdsEnv(haystack, envName) {
  const group = ENV_GROUPS.find((g) => g[0] === envName) ?? [envName];
  return group.some((word) => new RegExp(`(?<![\\w])${word}(?![\\w])`, 'i').test(haystack));
}

// {ok, missing}: does the haystack (a call's command plus its output) speak about the claimed object?
//   useWeak: also ask for one capitalised name when the claim has any.
export function objectMatch(objects, haystack, { useWeak = false } = {}) {
  const missing = [];
  for (const token of objects.strong) if (!holdsToken(haystack, token)) missing.push(token);
  for (const number of objects.prs) if (!holdsPr(haystack, number)) missing.push('#' + number);
  for (const env of objects.env) if (!holdsEnv(haystack, env)) missing.push(env);
  if (useWeak && objects.weak.length > 0 && !objects.weak.some((token) => haystack.toLowerCase().includes(token))) {
    missing.push(objects.weak.join('|'));
  }
  return { ok: missing.length === 0, missing };
}

export const hasSpecificObject = (objects) => objects.strong.length > 0 || objects.prs.length > 0 || objects.env.length > 0;
