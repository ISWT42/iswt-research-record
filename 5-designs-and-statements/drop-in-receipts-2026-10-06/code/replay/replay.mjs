#!/usr/bin/env node
// Replay test 1, deterministic layer: run the hook's rules (no model, no network) over a set of logged claims and
// compare what they settle with the answers receipt_pair recorded for the same items.
//
//   node replay/replay.mjs [--items <items.jsonl>] [--answers <answers.jsonl>] [--label s2] [--out <dir>] [--rule r2]
//
// Inputs (read only)
//   items    JSON Lines, one item per line: {"id", "claim", "turns":[{"cmd","output"}]}. ONLY those three fields are read.
//            If a file carries an answer key, the loader never takes it: nothing else is copied out of a line.
//   answers  receipt_pair's recorded check answers, JSON Lines: {"arm","id","answer","code","turn","quote"}. ONLY those
//            fields are read. Two arms (A and B) are combined with a pair rule (default r2, "shown needs both").
//
// What it does for each item
//   1. The claim sentence goes through the hook's own claim extractor (a sentence the extractor does not take as a claim
//      is "not shown": the hook would not have checked it).
//   2. Each turn becomes a Bash call with the output the harness captured, and the hook's rules settle each claim.
//   3. An item is "shown" only when every claim in it is shown; "contradicted" when any is; else "not shown".
//   4. The item's rules answer is set beside the pair's answer. Agreement with the pair is NOT accuracy: neither side is
//      compared with a key here.
//
// Outputs: <out>/<label>-<commit>.jsonl (one line per item) and <out>/<label>-<commit>-summary.json (the counts, the
// hashes of the inputs and of the output, and the ids in each group).
import { readFileSync, writeFileSync, mkdirSync, realpathSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { extractClaims } from '../src/claims.mjs';
import { prepareCall, checkClaims } from '../src/check.mjs';
import { normalizeAnswer, combine, ruleKey } from '../src/pairrule.mjs';
import { SHOWN, CONTRADICTED, NOT_SHOWN, ANSWERS } from '../src/text.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
export const DEFAULT_ITEMS = 'C:/Users/joshd/Workbench/chain-local-2026-10-06/inputs/s2-items.jsonl';
export const DEFAULT_ANSWERS = 'C:/Users/joshd/Workbench/chain-local-2026-10-06/results/step1.jsonl';

const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const jsonLines = (text) => String(text).split('\n').filter((line) => line.trim());

// ---- loading: only the named fields leave the file --------------------------------------------------------------
export function parseItems(text, where = 'items') {
  const items = [];
  const seen = new Set();
  jsonLines(text).forEach((line, index) => {
    const raw = JSON.parse(line);
    const id = String(raw.id);
    if (seen.has(id)) throw new Error(`${where}, line ${index + 1}: the id ${JSON.stringify(id)} appears twice`);
    seen.add(id);
    if (typeof raw.claim !== 'string' || !raw.claim.trim()) throw new Error(`${where}, line ${index + 1}: "claim" must be non-empty text`);
    if (!Array.isArray(raw.turns) || raw.turns.length === 0) throw new Error(`${where}, line ${index + 1}: "turns" must be a non-empty list`);
    const turns = raw.turns.map((turn, n) => {
      if (typeof turn === 'string') return { cmd: '', output: turn };
      if (!turn || typeof turn !== 'object') throw new Error(`${where}, line ${index + 1}, turn ${n + 1}: a turn must be an object`);
      return { cmd: String(turn.cmd ?? turn.command ?? ''), output: String(turn.output ?? '') };
    });
    items.push({ id, claim: raw.claim, turns });
  });
  if (items.length === 0) throw new Error(`${where}: no items`);
  return items;
}

// {arm|id -> {arm, id, answer, code, turn, quote}}; when an item was asked again the later row stands.
export function parseAnswers(text, where = 'answers') {
  const latest = new Map();
  jsonLines(text).forEach((line, index) => {
    const raw = JSON.parse(line);
    if (raw.arm === undefined || raw.id === undefined || raw.answer === undefined) throw new Error(`${where}, line ${index + 1}: a row needs "arm", "id" and "answer"`);
    latest.set(`${raw.arm}|${raw.id}`, { arm: String(raw.arm), id: String(raw.id), answer: normalizeAnswer(raw.answer), code: raw.code ?? null, turn: raw.turn ?? null, quote: raw.quote ?? null });
  });
  return latest;
}

// ---- the rules' answer for one item ---------------------------------------------------------------------------------
export function callsFromTurns(turns) {
  return turns.map((turn, i) => prepareCall({
    id: `T${i + 1}`, tool: 'Bash', input: { command: turn.cmd }, order: i,
    result: { text: turn.output, isError: false, structured: null },
  }));
}

export function answerItem(claimText, turns) {
  const claims = extractClaims(claimText);
  if (claims.length === 0) return { answer: NOT_SHOWN, code: 'no_claim_recognized', settled: false, quote: null, turn: null, claims: [] };
  const results = checkClaims(claims, callsFromTurns(turns));
  const parts = results.map((r) => ({ kind: r.claim.kind, text: r.claim.text, answer: r.answer, code: r.code, quote: r.quote ?? null, turn: r.source?.tool_use_id ?? null }));
  const decided = parts.find((p) => p.answer === CONTRADICTED)
    ?? (parts.every((p) => p.answer === SHOWN) ? parts[0] : parts.find((p) => p.answer !== SHOWN));
  const answer = parts.some((p) => p.answer === CONTRADICTED) ? CONTRADICTED : parts.every((p) => p.answer === SHOWN) ? SHOWN : NOT_SHOWN;
  return { answer, code: decided.code, settled: answer !== NOT_SHOWN, quote: answer === NOT_SHOWN ? null : decided.quote, turn: answer === NOT_SHOWN ? null : decided.turn, claims: parts };
}

// ---- the pair's answer, from the two recorded rows -----------------------------------------------------------------
export function pairAnswer(rowA, rowB, rule = 'r2') {
  if (!rowA || !rowB) return null;
  const answer = combine(rowA.answer, rowB.answer, rule);
  const standing = [rowA, rowB].filter((row) => answer !== NOT_SHOWN && row.answer === answer);
  return { answer, a: rowA.answer, b: rowB.answer, turns: standing.map((row) => row.turn), quotes: standing.map((row) => row.quote) };
}

const squash = (s) => String(s ?? '').replace(/\s+/g, ' ').trim();
export function quoteRelation(ruleQuote, pairQuotes) {
  const mine = squash(ruleQuote);
  if (!mine) return 'none';
  const theirs = pairQuotes.map(squash).filter(Boolean);
  if (theirs.some((q) => q === mine)) return 'same line';
  if (theirs.some((q) => q.includes(mine) || mine.includes(q))) return 'overlapping line';
  return 'different line';
}

// How the rules' answer stands to the pair's answer.
export function relationOf(rules, pair) {
  if (!pair) return 'no_pair_answer';
  if (rules.answer === NOT_SHOWN) return pair.answer === NOT_SHOWN ? 'both_not_shown' : 'rules_not_shown_pair_settled';
  if (pair.answer === rules.answer) return 'agree';
  if (pair.answer === NOT_SHOWN) return 'rules_settled_pair_not_shown';
  return 'opposite';
}

// ---- the whole replay ----------------------------------------------------------------------------------------------
export function replayItems(items, answers, { rule = 'r2' } = {}) {
  ruleKey(rule);
  return items.map((item) => {
    const rules = answerItem(item.claim, item.turns);
    const pair = pairAnswer(answers.get(`A|${item.id}`), answers.get(`B|${item.id}`), rule);
    const relation = relationOf(rules, pair);
    const sameTurn = relation === 'agree' ? pair.turns.includes(rules.turn) : null;
    const line = relation === 'agree' ? quoteRelation(rules.quote, pair.quotes) : null;
    return { id: item.id, claim: item.claim, turns: item.turns.length, rules, pair, relation, same_turn: sameTurn, quote_relation: line };
  });
}

const tally = (list, key) => list.reduce((acc, x) => { const k = key(x); acc[k] = (acc[k] ?? 0) + 1; return acc; }, {});
const idsOf = (records, test) => records.filter(test).map((r) => r.id);

export function summarize(records) {
  const n = records.length;
  const withPair = records.filter((r) => r.pair);
  const cross = {};
  for (const rulesAnswer of ANSWERS) {
    cross[rulesAnswer] = {};
    for (const pairAnswerName of ANSWERS) cross[rulesAnswer][pairAnswerName] = records.filter((r) => r.pair && r.rules.answer === rulesAnswer && r.pair.answer === pairAnswerName).length;
  }
  const settled = records.filter((r) => r.rules.settled);
  const agree = records.filter((r) => r.relation === 'agree');
  const unsettledWhy = tally(records.filter((r) => !r.rules.settled), (r) => r.rules.code);
  const pairSettled = withPair.filter((r) => r.pair.answer !== NOT_SHOWN);
  return {
    items: n,
    items_with_pair_answer: withPair.length,
    rules: {
      shown: records.filter((r) => r.rules.answer === SHOWN).length,
      contradicted: records.filter((r) => r.rules.answer === CONTRADICTED).length,
      not_shown_needs_a_reader: records.filter((r) => r.rules.answer === NOT_SHOWN).length,
      settled_without_a_model: settled.length,
      claim_recognized_by_the_extractor: records.filter((r) => r.rules.code !== 'no_claim_recognized').length,
      why_not_settled: unsettledWhy,
    },
    pair: {
      shown: withPair.filter((r) => r.pair.answer === SHOWN).length,
      contradicted: withPair.filter((r) => r.pair.answer === CONTRADICTED).length,
      not_shown: withPair.filter((r) => r.pair.answer === NOT_SHOWN).length,
    },
    cross_rules_by_pair: cross,
    of_the_items_the_rules_settled: {
      denominator: settled.length,
      pair_gives_the_same_answer: agree.length,
      pair_says_not_shown: records.filter((r) => r.relation === 'rules_settled_pair_not_shown').length,
      pair_says_the_opposite: records.filter((r) => r.relation === 'opposite').length,
    },
    of_the_items_the_pair_settled: {
      denominator: pairSettled.length,
      rules_give_the_same_answer: agree.length,
      rules_say_not_shown: pairSettled.filter((r) => r.rules.answer === NOT_SHOWN).length,
      rules_say_the_opposite: records.filter((r) => r.relation === 'opposite').length,
    },
    where_both_settled_the_same: {
      denominator: agree.length,
      same_turn: agree.filter((r) => r.same_turn === true).length,
      quote_same_line: agree.filter((r) => r.quote_relation === 'same line').length,
      quote_overlapping_line: agree.filter((r) => r.quote_relation === 'overlapping line').length,
      quote_different_line: agree.filter((r) => r.quote_relation === 'different line').length,
    },
    ids: {
      rules_shown: idsOf(records, (r) => r.rules.answer === SHOWN),
      rules_contradicted: idsOf(records, (r) => r.rules.answer === CONTRADICTED),
      agree: agree.map((r) => r.id),
      rules_settled_pair_not_shown: idsOf(records, (r) => r.relation === 'rules_settled_pair_not_shown'),
      opposite: idsOf(records, (r) => r.relation === 'opposite'),
      rules_not_shown_pair_settled: idsOf(records, (r) => r.relation === 'rules_not_shown_pair_settled'),
    },
  };
}

export function formatSummary(s, { label = 'replay', rule = 'r2' } = {}) {
  const line = (text) => text;
  const rows = ANSWERS.map((a) => `    rules ${a.padEnd(12)} ${String(s.cross_rules_by_pair[a].shown).padStart(4)} ${String(s.cross_rules_by_pair[a].contradicted).padStart(12)} ${String(s.cross_rules_by_pair[a]['not shown']).padStart(10)}`);
  const why = Object.entries(s.rules.why_not_settled).sort((a, b) => b[1] - a[1]).map(([code, count]) => `      ${String(count).padStart(3)}  ${code}`);
  return [
    line(`Replay ${label}, deterministic layer, pair rule ${rule}: ${s.items} items (${s.items_with_pair_answer} with both recorded answers).`),
    line(`  rules answer: ${s.rules.shown} shown, ${s.rules.contradicted} contradicted, ${s.rules.not_shown_needs_a_reader} not shown (needs a reader), of ${s.items}.`),
    line(`  settled without a model: ${s.rules.settled_without_a_model} of ${s.items}. Claim recognized by the extractor: ${s.rules.claim_recognized_by_the_extractor} of ${s.items}.`),
    line('  not settled, by reason:'),
    ...why,
    line(`  pair (recorded) answer: ${s.pair.shown} shown, ${s.pair.contradicted} contradicted, ${s.pair.not_shown} not shown, of ${s.items_with_pair_answer}.`),
    line('  rules (rows) by pair (columns):'),
    line(`                          ${'shown'.padStart(4)} ${'contradicted'.padStart(12)} ${'not shown'.padStart(10)}`),
    ...rows,
    line(`  of the ${s.of_the_items_the_rules_settled.denominator} items the rules settled: pair gives the same answer on ${s.of_the_items_the_rules_settled.pair_gives_the_same_answer}, says not shown on ${s.of_the_items_the_rules_settled.pair_says_not_shown}, says the opposite on ${s.of_the_items_the_rules_settled.pair_says_the_opposite}.`),
    line(`  of the ${s.of_the_items_the_pair_settled.denominator} items the pair settled: rules give the same answer on ${s.of_the_items_the_pair_settled.rules_give_the_same_answer}, say not shown on ${s.of_the_items_the_pair_settled.rules_say_not_shown}, say the opposite on ${s.of_the_items_the_pair_settled.rules_say_the_opposite}.`),
    line(`  of the ${s.where_both_settled_the_same.denominator} items both settled the same way: same turn on ${s.where_both_settled_the_same.same_turn}; quote is the same line on ${s.where_both_settled_the_same.quote_same_line}, an overlapping line on ${s.where_both_settled_the_same.quote_overlapping_line}, a different line on ${s.where_both_settled_the_same.quote_different_line}.`),
    line('  Agreement with the pair is not accuracy: no answer key was read.'),
  ].join('\n');
}

function gitHead() {
  try {
    return execFileSync('git', ['rev-parse', 'HEAD'], { cwd: join(HERE, '..'), encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return null;
  }
}

export function runReplay({ itemsPath = DEFAULT_ITEMS, answersPath = DEFAULT_ANSWERS, label = 's2', outDir = HERE, rule = 'r2' } = {}) {
  const itemsBytes = readFileSync(itemsPath);
  const answersBytes = readFileSync(answersPath);
  const items = parseItems(itemsBytes.toString('utf8'), itemsPath);
  const answers = parseAnswers(answersBytes.toString('utf8'), answersPath);
  const records = replayItems(items, answers, { rule });
  const summary = summarize(records);
  const head = gitHead();
  const stem = `${label}-${head ? head.slice(0, 7) : 'nogit'}`;
  mkdirSync(outDir, { recursive: true });
  const body = records.map((r) => JSON.stringify(r)).join('\n') + '\n';
  const outPath = join(outDir, `${stem}.jsonl`);
  writeFileSync(outPath, body);
  const record = {
    label, rule, rules_commit: head, items_file: itemsPath, items_sha256: sha256(itemsBytes), answers_file: answersPath, answers_sha256: sha256(answersBytes),
    script_sha256: sha256(readFileSync(fileURLToPath(import.meta.url))), output_file: outPath, output_sha256: sha256(body),
    summary,
  };
  const summaryPath = join(outDir, `${stem}-summary.json`);
  writeFileSync(summaryPath, JSON.stringify(record, null, 2) + '\n');
  return { records, summary, record, outPath, summaryPath };
}

function main(argv) {
  const opt = (name, fallback) => { const i = argv.indexOf(name); return i >= 0 && argv[i + 1] ? argv[i + 1] : fallback; };
  const label = opt('--label', 's2');
  const rule = opt('--rule', 'r2');
  const out = runReplay({ itemsPath: resolve(opt('--items', DEFAULT_ITEMS)), answersPath: resolve(opt('--answers', DEFAULT_ANSWERS)), label, outDir: resolve(opt('--out', HERE)), rule });
  process.stdout.write(formatSummary(out.summary, { label, rule }) + '\n');
  process.stdout.write(`\nwrote ${out.outPath}\nwrote ${out.summaryPath}\noutput sha256 ${out.record.output_sha256}\n`);
}

let isMain = false;
try { isMain = Boolean(process.argv[1]) && import.meta.url === pathToFileURL(realpathSync(process.argv[1])).href; } catch { isMain = false; }
if (isMain) main(process.argv.slice(2));
