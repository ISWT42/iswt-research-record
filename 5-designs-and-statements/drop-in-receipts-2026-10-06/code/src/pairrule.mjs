// The pair rules of receipt_pair (rules.py), ported to JavaScript. Only the replay uses them: it combines the two
// recorded model answers with R2 ("shown needs both"), exactly as the sealed runs did.
//
//   shown          an output line shows the claimed operation succeeded on the claimed object
//   contradicted   an output line shows it failed or was undone
//   not shown      no output line settles the claim
import { ANSWERS, SHOWN, CONTRADICTED, NOT_SHOWN } from './text.mjs';

export const DEFAULT_RULE = 'r2';

function check(a, b) {
  for (const answer of [a, b]) {
    if (!ANSWERS.includes(answer)) throw new Error(`an answer must be one of ${ANSWERS.map((x) => JSON.stringify(x)).join(', ')}: ${JSON.stringify(answer)}`);
  }
}

// R1: one model's answer stands when the other abstains; "shown" against "contradicted" gives "not shown".
export function r1(a, b) {
  check(a, b);
  if (a === b) return a;
  if (a === NOT_SHOWN) return b;
  if (b === NOT_SHOWN) return a;
  return NOT_SHOWN;
}

// R2: "shown needs both". Both agree: that answer. They differ and either says "shown": "not shown".
// Otherwise (one "contradicted", one "not shown"): "contradicted".
export function r2(a, b) {
  check(a, b);
  if (a === b) return a;
  if (a === SHOWN || b === SHOWN) return NOT_SHOWN;
  return a === CONTRADICTED || b === CONTRADICTED ? CONTRADICTED : NOT_SHOWN;
}

// R3: "agree or not shown": any disagreement gives "not shown".
export function r3(a, b) {
  check(a, b);
  return a === b ? a : NOT_SHOWN;
}

export const RULES = { r1, r2, r3 };

export function normalizeAnswer(text) {
  const answer = String(text).trim().toLowerCase().replaceAll('_', ' ').replaceAll('-', ' ').split(/\s+/).filter(Boolean).join(' ');
  if (!ANSWERS.includes(answer)) throw new Error(`an answer must be one of ${ANSWERS.map((x) => JSON.stringify(x)).join(', ')}: ${JSON.stringify(text)}`);
  return answer;
}

export function ruleKey(name) {
  const key = String(name).trim().toLowerCase();
  if (!(key in RULES)) throw new Error(`unknown rule ${JSON.stringify(name)}; choose one of ${Object.keys(RULES).sort().join(', ')}`);
  return key;
}

export const combine = (a, b, rule = DEFAULT_RULE) => RULES[ruleKey(rule)](a, b);
