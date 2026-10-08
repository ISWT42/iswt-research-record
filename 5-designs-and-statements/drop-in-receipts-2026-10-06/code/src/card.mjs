// The receipt card (what the person sees) and the gate message (what the agent is told when it is blocked).
// Plain text: the three answers, the quoted line, the tool call it came from, and "floor, not box".
import { oneLine, GATE_TAG, redact } from './text.mjs';

// A quoted line is shown as printed (its spacing kept), only trimmed and cut when very long.
const clip = (text, max = 200) => { const t = String(text ?? '').trim(); return t.length > max ? t.slice(0, max - 1) + '…' : t; };

export const FLOOR_NOT_BOX = "Floor, not box: this reads what the harness recorded of the tools' output. An agent that can write that record, or make a tool print the line, can fake it. A box keeps the record out of the agent's reach.";
const MAX_LISTED = 8;

function counts(results) {
  const c = { shown: 0, contradicted: 0, 'not shown': 0 };
  for (const r of results) c[r.answer]++;
  return c;
}

const tag = (r) => (r.answer === 'not shown' ? 'not shown (needs a reader)' : r.answer);
const where = (r) => (r.source ? `${r.source.tool} call ${r.source.tool_use_id}${r.source.command ? ': ' + oneLine(r.source.command, 80) : ''}` : null);

export function renderCard(results, { mode = 'report', receiptsPath = null, gated = false } = {}) {
  const c = counts(results);
  const lines = [`Receipts (floor, not box): ${results.length} claim${results.length === 1 ? '' : 's'} checked: ${c.shown} shown, ${c.contradicted} contradicted, ${c['not shown']} not shown.`];
  for (const r of results.slice(0, MAX_LISTED)) {
    lines.push(`  ${tag(r)}: "${oneLine(redact(r.claim.text), 140)}"`);
    if (r.quote) lines.push(`    line: ${clip(r.quote)}`);
    const from = where(r);
    if (from) lines.push(`    from: ${from}`);
    if (r.answer === 'not shown') lines.push(`    why: ${r.reason}`);
    if (r.stale_edits > 0) lines.push(`    note: ${r.stale_edits} file edit${r.stale_edits === 1 ? '' : 's'} came after this tool call, so it may not describe the final state`);
  }
  if (results.length > MAX_LISTED) lines.push(`  ... and ${results.length - MAX_LISTED} more (all are in the receipts file)`);
  lines.push(FLOOR_NOT_BOX);
  lines.push(`Mode: ${mode}${gated ? ' (the agent was told to cite a receipt or retract)' : mode === 'gate' ? ' (nothing blocked)' : ' (the stop is allowed)'}.${receiptsPath ? ` Receipts: ${receiptsPath}` : ''}`);
  return lines.join('\n');
}

// The block reason: tells the agent which claims have no receipt and what to do. Starts with GATE_TAG so a later
// pass can recognise it as this hook's own message and not as a new prompt.
export function gateReason(results) {
  const open = results.filter((r) => r.answer !== 'shown');
  const lines = [`${GATE_TAG} Your final message made ${open.length} claim${open.length === 1 ? '' : 's'} that this turn's tool output does not back (floor, not box: this checks what the tools printed, never what you wrote).`];
  for (const r of open.slice(0, MAX_LISTED)) {
    const claim = `"${oneLine(redact(r.claim.text), 140)}"`;
    if (r.answer === 'contradicted') {
      lines.push(`- CONTRADICTED: ${claim}. ${where(r) ?? 'a tool call'} printed: "${clip(r.quote)}" (${r.reason}).`);
    } else {
      lines.push(`- NOT SHOWN: ${claim}. ${r.reason.charAt(0).toUpperCase() + r.reason.slice(1)}.`);
    }
  }
  if (open.length > MAX_LISTED) lines.push(`- ... and ${open.length - MAX_LISTED} more.`);
  lines.push('For each one: run the command that would show it and cite the exact line the tool printed, or retract the claim and say plainly what is not done. Do not repeat a claim that its own tool output contradicts.');
  return lines.join('\n');
}
