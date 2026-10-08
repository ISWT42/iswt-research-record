// Text helpers shared by every rule: output normalising, credential redaction, and the failure-word logic.
//
// The failure-word logic is a JavaScript port of receipt_pair (reader version 3.0, MIT, same author):
// BENIGN_FAILURE_WORDS, SAFETY_MARKERS, BARE_HTTP_STATUS, the terminal-overwrite check and the credential
// redaction patterns. Python `re` became JavaScript `RegExp`; the patterns and their meaning are unchanged.
// test/text.test.mjs pins the port against answers that the Python original gave.
//
// One known difference, in the safe direction: Python's \b counts a non-ASCII letter (é, テ) as a word character and
// JavaScript's does not, so a failure word glued to such a letter ("éfailed", "テストfailed") is a marker here and not
// there. The port can therefore only add a veto against "shown", never drop one. Checked on 941 output lines and 194 raw
// outputs of a real set (0 differences, all ASCII) and on 40 constructed non-ASCII lines (6 differences, all of this kind).
import { createHash } from 'node:crypto';

export const sha256 = (text) => createHash('sha256').update(String(text), 'utf8').digest('hex');

// Terminal colour and cursor codes are not text.
export const ANSI_CODES = /\x1b\[[0-?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[@-Z\\-_]/g;
const CONTROL = /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/g; // keeps tab and newline

// What the rules read: the tool output with colour codes and control characters removed and line ends made "\n".
// A quote is always taken from this text, and is checked to be in this text.
export function normalizeOutput(raw) {
  return String(raw ?? '')
    .replace(ANSI_CODES, '')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .replace(CONTROL, '');
}

export const splitLines = (text) => String(text ?? '').split('\n');

// ---- credentials never reach a receipt or a card ----------------------------------------------------
const SENSITIVE_TEXT = /\b((?:api[_-]?key|access[_-]?token|refresh[_-]?token|auth[_-]?token|password|passwd|client[_-]?secret|authorization|token)\s*[:=]\s*)(?:"[^"]*"|'[^']*'|[^\s,;}]+)/gi;
const BEARER = /\bBearer\s+[^\s"'<>]+/gi;
const PRIVATE_KEY = /-----BEGIN [A-Z ]{0,30}PRIVATE KEY-----[\s\S]{0,20000}?-----END [A-Z ]{0,30}PRIVATE KEY-----/g;   // a key block is a few KB; unbounded, a megabyte of unterminated BEGIN lines took 5.5 s
const TOKEN_SHAPES = /\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|(?:AKIA|ASIA)[0-9A-Z]{16}|xox[abprs]-[A-Za-z0-9-]{10,}|npm_[A-Za-z0-9]{30,}|glpat-[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}|[sr]k_(?:live|test)_[0-9A-Za-z]{10,}|AIza[0-9A-Za-z_-]{30,}|ya29\.[0-9A-Za-z_-]{20,}|hf_[A-Za-z0-9]{30,}|gsk_[A-Za-z0-9]{20,}|SG\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,})\b/g;
// Every quantifier below that could run along an unbroken string is bounded. An unbounded run scanned from every start
// position makes the time grow with the square (or worse) of the length: 10 KB of "token_" repeated took 14 s.
const URL_CREDENTIALS = /\b([a-z][a-z0-9+.-]{0,15}:\/\/)[^\s/:@]+:[^\s/@]+@/gi;   // any scheme: https, postgres, mongodb+srv, redis, ftp ...
const LOGIN_PASSWORD = /(\b(?:docker|podman)\s+login\b[^\n|;&]{0,300}?\s(?:-p|--password)(?:\s+|=))\S+|(\bsshpass\b[^\n|;&]{0,300}?\s-p(?:\s+|=))\S+/gi;
// Beyond receipt_pair's patterns. A command is kept in a receipt, and commands carry credentials in more shapes than
// "token: value":
//   an Authorization header whose scheme is followed by the credential ("Basic dXNlcjpwYXNz"): receipt_pair's pattern
//   takes only the first word, so the scheme goes and the credential stays; it is removed after that step (AUTH_TAIL);
//   a name that holds a secret word after an underscore (DB_PASSWORD=..., "password": "x"), where \b does not fire;
//   "tokens" (max_tokens=400) is a count, not a secret;
//   "set <secret name> <value>" (aws configure set aws_secret_access_key abc), command-line flags (--password hunter2,
//   --token=abc) and curl's -u user:password.
const AUTH_TAIL = /(\bauthorization\s*[:=]\s*["']?\[redacted\])\s+(?!\[redacted\])[^\s"']+/gi;
const SECRET_WORDS = String.raw`(?:secret|passw(?:or)?d|passwd|pwd|passphrase|token(?!s)|(?:api|access|private|signing|encryption|license|master|auth|ssh)[_-]?key|credentials?)`;
// Only the value is replaced, so the name in front of the secret word is left in place and need not be matched.
const NAME_ASSIGN = new RegExp(String.raw`(${SECRET_WORDS}[A-Za-z0-9_.-]{0,40}["']?\s*[:=]\s*)(?:"[^"]*"|'[^']*'|[^\s,;}&]+)`, 'gi');
const SET_SECRET = new RegExp(String.raw`(\bset\s+[A-Za-z0-9_.:/-]{0,60}${SECRET_WORDS}[A-Za-z0-9_.:/-]{0,60}\s+)(?:"[^"]*"|'[^']*'|[^\s=]+)(?=\s|$)`, 'gi');
const FLAG_SECRET = /(\s--?(?:password|passwd|pwd|passphrase|token|secret|api-?key|access-?key|auth-?token|client-?secret)(?:=|\s+))(?:"[^"]*"|'[^']*'|\S+)/gi;
const CURL_USER = /(\bcurl\b[^\n|;&]{0,300}?\s(?:-u|--user)(?:\s+|=))[^\s:@]+:\S+/gi;

export function redact(text) {
  return String(text ?? '')
    .replace(PRIVATE_KEY, '[redacted]')
    .replace(BEARER, 'Bearer [redacted]')
    .replace(SENSITIVE_TEXT, (_match, head) => head + '[redacted]')
    .replace(AUTH_TAIL, '$1')
    .replace(NAME_ASSIGN, '$1[redacted]')
    .replace(SET_SECRET, '$1[redacted]')
    .replace(FLAG_SECRET, '$1[redacted]')
    .replace(CURL_USER, '$1[redacted]')
    .replace(LOGIN_PASSWORD, (_m, a, b) => (a ?? b) + '[redacted]')
    .replace(URL_CREDENTIALS, '$1[redacted]@')
    .replace(TOKEN_SHAPES, '[redacted]');
}

// ---- failure words, and the benign zeros that must not count -------------------------------------------
// Counts and empty values that report the absence of failures ("0 errors", "failed=0", "error: null",
// "without errors") are removed first.
export const BENIGN_FAILURE_WORDS = new RegExp(
  String.raw`\b(?:0|zero|no|without(?:\s+any)?)\s+(?:errors?|failures?|failed|failing|exceptions?)\b|` +
  String.raw`\b(?:errors?|failures?|failed|failing|fail|exceptions?)\s*["']?\s*[:=]?\s*["']?` +
  String.raw`(?:0|false|null|none|\[\]|\{\})(?![\w.])|` +
  String.raw`\b(?:errors?|failures?|exceptions?)["']?\s*[:=]\s*(?:""|'')`,
  'gi');

export const SAFETY_MARKERS = [
  ['non-zero exit', new RegExp(
    String.raw`\bexit(?:ed)?(?:\s+with)?(?:\s+(?:code|status))?\s*[:=]?\s*-?[1-9]\d*\b|` +
    String.raw`\b(?:exit_?code|exit_?status|return_?code|returncode|rc)\s*["']?\s*[:=]\s*-?[1-9]\d*\b|` +
    String.raw`\bnon-?zero\s+(?:exit|return)`, 'i')],
  ['http 4xx/5xx', new RegExp(
    String.raw`\b(?:HTTP(?:/\d(?:\.\d)?)?|status(?:[_ ]?code)?|response(?:[_ ]?code)?)\s*["']?\s*[:=]?\s*` +
    String.raw`["']?[45]\d\d\b`, 'i')],
  ['error', /\berrors?\b/i],
  ['failed', /\bfail(?:s|ed|ure|ures|ing)?\b/i],
  ['denied', /\bdenied\b/i],
  ['fatal', /\bfatal\b/i],
  ['rejected', /\brejected\b/i],
  ['refused', /\brefused\b/i],
  ['traceback', /\btraceback\b/i],
  ['exception', /\bexception\b/i],
  ['aborted', /\baborted\b/i],
  ['killed / out of memory', /\bkilled\b|\bout\s+of\s+memory\b|\boom(?:[-_ ]?kill(?:ed|er)?)?\b/i],
  ['crash signal', /\bSIG(?:KILL|SEGV|ABRT|BUS)\b|\bsignal\s+(?:6|9|11)\b|\bsegmentation\s+fault\b|\bcore\s+dumped\b/i],
  ['no space left', /\bno\s+space\s+left\s+on\s+device\b/i],
  ['timed out', /\btimed\s+out\b|\bhandshake\s+timeout\b|\bdeadline\s+exceeded\b/i],
  ['success: false', /\b(?:success|ok)\s*["']?\s*[:=]\s*["']?false\b/i],
];

// An unlabelled status is recognisable when it stands alone or precedes an HTTP reason phrase.
// A count such as '422 rows exported' is not a status.
export const BARE_HTTP_STATUS = new RegExp(
  String.raw`^\s*([1-5]\d\d)(?:\s*$|\s+(?:OK|Created|Accepted|No\s+Content|` +
  String.raw`Unauthorized|Forbidden|Not\s+Found|Conflict|Unprocessable(?:\s+Entity|\s+Content)?|` +
  String.raw`Too\s+Many\s+Requests|Internal\s+Server\s+Error|Not\s+Implemented|` +
  String.raw`Bad\s+Gateway|Service\s+Unavailable|Gateway\s+Timeout)\b)`, 'i');

// Names of the failure markers present in a line of text, after the benign zeros are taken out.
export function failureMarkers(text) {
  const cleaned = String(text ?? '').replace(BENIGN_FAILURE_WORDS, ' ');
  const found = SAFETY_MARKERS.filter(([, pattern]) => pattern.test(cleaned)).map(([name]) => name);
  const status = BARE_HTTP_STATUS.exec(cleaned);
  if (status && Number(status[1]) >= 400 && !found.includes('http 4xx/5xx')) found.push('http 4xx/5xx');
  return found;
}

// A terminal overwrite can hide a line from a person reading the terminal: a carriage return, a backspace,
// cursor-back, column or erase-in-line codes on the same line; cursor movement or erase-display codes across lines.
const INLINE_OVERWRITE = /\r(?!\n)|\x08|\x1b\[[0-9;?]*[DGK]/;
const CROSSLINE_OVERWRITE = /\x1b\[[0-9;?]*[ABEFHJSTdfsu]|\x1b[78]/;

// Failure markers in raw output text that a terminal overwrite would hide. Checked on the raw record,
// where the overwrite codes are still present.
export function overwrittenFailures(rawOutput) {
  const text = String(rawOutput ?? '').replace(/\r\n/g, '\n');
  const crossline = CROSSLINE_OVERWRITE.test(text);
  const found = new Set();
  for (const line of text.split('\n')) {
    const pieces = line.replace(/\r+$/, '').split(INLINE_OVERWRITE);
    for (const piece of crossline ? pieces : pieces.slice(0, -1)) {
      for (const name of failureMarkers(piece.replace(ANSI_CODES, '').replace(CONTROL, ''))) found.add(name);
    }
  }
  return [...found].sort();
}

// The answers every part of the program uses.
export const SHOWN = 'shown';
export const CONTRADICTED = 'contradicted';
export const NOT_SHOWN = 'not shown';
export const ANSWERS = [SHOWN, CONTRADICTED, NOT_SHOWN];

// Marks the hook's own gate message, so a later pass can tell it from a person's prompt.
export const GATE_TAG = '[drop-in-receipts gate]';

export function oneLine(text, max = 160) {
  const flat = String(text ?? '').replace(/\s+/g, ' ').trim();
  return flat.length > max ? flat.slice(0, max - 1) + '…' : flat;
}
