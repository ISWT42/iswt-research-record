// Receipts: an append-only local file, one JSON line per claim checked, each line carrying its own SHA-256.
//
// Each line is written with its keys in sorted order. Its "sha256" is the SHA-256 of that same JSON without the
// "sha256" field (and with "prev_sha256": the SHA-256 of the line before it, null for the first). So anyone can
// recompute every hash from the file alone, and a line that was changed, removed or inserted breaks the chain.
//
// The file is local. Nothing here touches the network. Credentials are redacted before anything is written, and the
// receipt keeps the SHA-256 of the tool output it relied on, not the output itself.
import { appendFileSync, mkdirSync, rmdirSync, statSync, openSync, readSync, fstatSync, closeSync, readFileSync, existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { sha256, redact, oneLine } from './text.mjs';

export const RECEIPT_VERSION = 1;
// A quote longer than this is cut to its first QUOTE_MAX characters (still a word-for-word piece of the line) and the
// receipt says so, so that one receipt line stays small enough for the chain to read the last line back.
export const QUOTE_MAX = 2000;
const TOKENS_MAX = 20;

export function defaultReceiptsPath(env = process.env) {
  return env.DROP_IN_RECEIPTS_FILE || join(homedir(), '.drop-in-receipts', 'receipts.jsonl');
}

export function canonicalJson(value) {
  if (Array.isArray(value)) return '[' + value.map(canonicalJson).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().filter((k) => value[k] !== undefined).map((k) => JSON.stringify(k) + ':' + canonicalJson(value[k])).join(',') + '}';
  }
  return JSON.stringify(value) ?? 'null';
}

// The receipt for one checked claim. `result` is a settleClaim() result; `context` says where and when.
const tokensOf = (list) => (Array.isArray(list) ? list : []).slice(0, TOKENS_MAX).map((token) => redact(String(token)));

export function buildReceipt(result, context) {
  const { claim } = result;
  const quote = result.quote == null ? null : String(result.quote);
  const clipped = quote !== null && quote.length > QUOTE_MAX;
  return {
    v: RECEIPT_VERSION,
    ts: context.ts ?? new Date().toISOString(),
    event: context.event ?? 'Stop',
    session_id: context.session_id ?? null,
    agent_id: context.agent_id ?? null,
    mode: context.mode ?? 'report',
    layer: result.layer ?? 'deterministic',
    record: 'floor',
    message_sha256: context.message_sha256 ?? null,
    claim: {
      kind: claim.kind,
      text: redact(claim.text),
      objects: { strong: tokensOf(claim.objects?.strong), prs: tokensOf(claim.objects?.prs), env: tokensOf(claim.objects?.env) },
    },
    answer: result.answer,
    code: result.code,
    reason: result.reason,
    needs_reader: result.needs_reader === true,
    quote: clipped ? quote.slice(0, QUOTE_MAX) : quote,
    ...(clipped ? { quote_truncated: true, quote_chars: quote.length } : {}),
    source: result.source ? { ...result.source, command: redact(result.source.command) } : null,
    stale_edits: result.stale_edits ?? 0,
  };
}

// The last line of the file. The tail is read in growing windows until a whole line is inside it (a line cut off at
// the start of the window is never taken for the last line).
function lastLine(path) {
  if (!existsSync(path)) return null;
  const fd = openSync(path, 'r');
  try {
    const size = fstatSync(fd).size;
    if (size === 0) return null;
    for (let window = 65536; ; window *= 4) {
      const start = Math.max(0, size - window);
      const buffer = Buffer.alloc(size - start);
      readSync(fd, buffer, 0, buffer.length, start);
      const pieces = buffer.toString('utf8').split('\n');
      const whole = start === 0 ? pieces : pieces.slice(1);        // when the window starts mid-file, its first piece may be cut off
      const last = whole.filter((l) => l.trim()).at(-1);
      if (last !== undefined) return last;
      if (start === 0 || window >= 64 * 1024 * 1024) return null;
    }
  } finally {
    closeSync(fd);
  }
}

export function lastSha(path) {
  const line = lastLine(path);
  if (!line) return null;
  try { return JSON.parse(line).sha256 ?? null; } catch { return null; }
}

export function seal(record, prev) {
  const body = { ...record, prev_sha256: prev ?? null };
  return { ...body, sha256: sha256(canonicalJson(body)) };
}

const sleepSync = (ms) => {
  try { Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms); } catch { const end = Date.now() + ms; while (Date.now() < end) { /* wait */ } }
};

// Reading the last hash and appending must be one step, or two hooks stopping together (parallel sub-agents) chain to
// the same line and fork the chain. The lock is a directory next to the file: creating one is atomic. A lock older than
// staleMs belongs to a process that died and is removed. If the lock cannot be had within waitMs, or cannot be made at
// all (a read-only folder), the receipts are written anyway: a receipt is never lost and the agent never waits long. In
// that rare case the chain can fork, and verifyReceipts says so.
//
// Windows: a lock directory that another process has just removed can still be "pending deletion", and creating or
// looking at it then fails with EPERM, EACCES or EBUSY instead of EEXIST (seen under load: one writer in a set of eight
// went on without the lock and forked the chain). Those errors mean "busy, try again", for up to transientMs; only after
// that is the folder taken to be one that cannot be written to.
const BUSY_CODES = new Set(['EPERM', 'EACCES', 'EBUSY']);

export function withLock(path, fn, options = {}) {
  const { waitMs = 5000, staleMs = 15000, transientMs = 2000, mkdir = mkdirSync, rmdir = rmdirSync, stat = statSync } = options;
  const lock = path + '.lock';
  const start = Date.now();
  const pause = () => sleepSync(8 + Math.floor(Math.random() * 16));
  let held = false;
  for (;;) {
    try { mkdir(lock); held = true; break; } catch (error) {
      const waited = Date.now() - start;
      if (BUSY_CODES.has(error.code)) {
        if (waited >= transientMs) break;
        pause();
        continue;
      }
      if (error.code !== 'EEXIST') break;
      let age = null;
      try { age = Date.now() - stat(lock).mtimeMs; } catch { /* its owner just let go, or it is pending deletion: look again */ }
      if (age !== null && age > staleMs) { try { rmdir(lock); } catch { /* someone else removed it */ } continue; }
      if (waited >= waitMs) break;
      pause();
    }
  }
  try {
    return fn();
  } finally {
    if (held) {
      // letting go can meet a handle that is still open (a scanner, another process): try a few times
      for (let i = 0; i < 30; i++) {
        try { rmdir(lock); break; } catch (error) { if (error.code === 'ENOENT') break; sleepSync(10); }
      }
    }
  }
}

// Append the receipts, chained to whatever is already in the file. Returns the sealed records.
export function appendReceipts(path, records, lockOptions) {
  mkdirSync(dirname(path), { recursive: true });
  return withLock(path, () => {
    let prev = lastSha(path);
    const sealed = [];
    for (const record of records) {
      const line = seal(record, prev);
      appendFileSync(path, canonicalJson(line) + '\n', { flag: 'a' });
      prev = line.sha256;
      sealed.push(line);
    }
    return sealed;
  }, lockOptions);
}

// Recompute every hash and the chain. {ok, lines, problems:[{line, problem}]}
export function verifyReceipts(path) {
  const problems = [];
  let lines = 0;
  let prev = null;
  const text = readFileSync(path, 'utf8');
  text.split('\n').forEach((raw, i) => {
    if (!raw.trim()) return;
    lines++;
    let record;
    try { record = JSON.parse(raw); } catch { problems.push({ line: i + 1, problem: 'not valid JSON' }); return; }
    const { sha256: claimed, ...body } = record;
    if (sha256(canonicalJson(body)) !== claimed) problems.push({ line: i + 1, problem: 'sha256 does not match the line' });
    if ((record.prev_sha256 ?? null) !== prev) problems.push({ line: i + 1, problem: 'prev_sha256 does not match the line before' });
    prev = claimed ?? null;
  });
  return { ok: problems.length === 0, lines, problems };
}

export const shortId = (id) => oneLine(id ?? '', 20);
