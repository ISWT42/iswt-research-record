// Reads a Claude Code session transcript (JSON Lines) and pulls out what the check needs from the CURRENT TURN:
//   - the final assistant message (where the completion claims are), and
//   - the tool calls with the results the harness captured for them (the record the claims are checked against).
//
// The agent's own prose is never evidence: assistant text is read only to find claims. A result counts as evidence
// only when it came back as a tool_result for a tool_use in this turn. Results of tools whose text is itself the
// agent's words (a sub-agent's report, a todo list, a plan) are left out.
//
// Record shapes (as Claude Code writes them, and as rule-ask.mjs reads them):
//   {type:'user',      message:{content:'prompt text' | [{type:'text',text}] | [{type:'tool_result',tool_use_id,content,is_error}]}, toolUseResult?}
//   {type:'assistant', message:{content:[{type:'text',text} | {type:'tool_use',id,name,input}]}}
import { openSync, readSync, fstatSync, closeSync } from 'node:fs';
import { GATE_TAG } from './text.mjs';

// Only the end of the transcript is read (the current turn is always near the end), so a long session stays fast.
export const TAIL_BYTES = 8 * 1024 * 1024;

export function readTail(path, maxBytes = TAIL_BYTES) {
  const fd = openSync(path, 'r');
  try {
    const size = fstatSync(fd).size;
    const start = Math.max(0, size - maxBytes);
    const buffer = Buffer.alloc(size - start);
    readSync(fd, buffer, 0, buffer.length, start);
    const text = buffer.toString('utf8');
    return start === 0 ? text : text.slice(text.indexOf('\n') + 1); // drop the partial first line
  } finally {
    closeSync(fd);
  }
}

export function parseJsonl(text) {
  const records = [];
  for (const line of String(text ?? '').split('\n')) {
    if (!line.trim()) continue;
    try {
      const record = JSON.parse(line);
      if (record && typeof record === 'object') records.push(record);
    } catch { /* a cut-off or damaged line is skipped */ }
  }
  return records;
}

// Tools whose result text is the agent's own words or bookkeeping, never a record of something happening.
export const NON_EVIDENCE_TOOLS = new Set([
  'Task', 'Agent', 'TodoWrite', 'ExitPlanMode', 'EnterPlanMode', 'AskUserQuestion', 'Skill', 'SlashCommand',
  'SendMessage', 'TaskCreate', 'TaskUpdate', 'TaskList', 'TaskGet', 'ToolSearch',
]);

// The tools that edit files. Not evidence for any claim in step 1, but a call after the evidence call means
// the evidence may be out of date, and the card says so.
export const EDIT_TOOLS = new Set(['Write', 'Edit', 'MultiEdit', 'NotebookEdit']);

const textOf = (blocks) => (Array.isArray(blocks) ? blocks.filter((b) => b?.type === 'text').map((b) => b.text ?? '').join('\n') : '');

// A real prompt from the person: a user record that is not a tool result, not meta text, and not this hook's own
// gate message coming back.
export function isRealPrompt(record) {
  if (record?.type !== 'user') return false;
  if (record.isMeta === true || record.isCompactSummary === true) return false;
  const content = record.message?.content;
  if (typeof content === 'string') {
    const text = content.trim();
    return text !== '' && !text.includes(GATE_TAG) && !/^Stop hook feedback/i.test(text);
  }
  if (Array.isArray(content)) {
    if (content.some((b) => b?.type === 'tool_result')) return false;
    const text = textOf(content);
    return content.some((b) => b?.type === 'text') && !text.includes(GATE_TAG) && !/^Stop hook feedback/i.test(text.trim());
  }
  return false;
}

// Everything after the last real prompt (the whole list when no prompt is in view, e.g. a very long turn read
// from the tail of the file).
export function currentTurn(records) {
  let start = 0;
  records.forEach((record, index) => { if (isRealPrompt(record)) start = index + 1; });
  return records.slice(start);
}

// Which records belong to the agent being checked.
//   'main'  a session transcript: sub-agent records (isSidechain) are not this agent's tool results.
//   'agent' a sub-agent's own transcript: everything in it.
//   'sidechain-only' an old-style SubagentStop that only gave the session transcript: the sub-agent records in it.
export function scopeRecords(records, scope = 'main') {
  if (scope === 'agent') return records;
  if (scope === 'sidechain-only') return records.filter((r) => r?.isSidechain === true);
  return records.filter((r) => r?.isSidechain !== true);
}

function resultText(content) {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content.map((b) => (typeof b === 'string' ? b : b?.type === 'text' ? (b.text ?? '') : '')).filter(Boolean).join('\n');
  }
  return '';
}

// The text of a user record that is a message, not a tool result (a string, or text blocks).
function plainUserText(record) {
  const content = record?.message?.content;
  if (typeof content === 'string') return content;
  if (Array.isArray(content) && !content.some((b) => b?.type === 'tool_result')) return textOf(content);
  return '';
}

// The text of the final assistant message: the assistant records after the last user record of the turn.
export function finalAssistantText(turn) {
  const texts = [];
  for (let i = turn.length - 1; i >= 0; i--) {
    const record = turn[i];
    if (record?.type === 'user') {
      if (record.isMeta === true) continue;
      break;
    }
    if (record?.type !== 'assistant') continue;
    const content = record.message?.content;
    if (typeof content === 'string') { texts.unshift(content); continue; }
    if (!Array.isArray(content)) continue;
    const text = textOf(content);
    if (text) texts.unshift(text);
  }
  return texts.join('\n\n').trim();
}

// {finalMessage, calls, allCalls, records}. `calls` are the tool calls that have a captured result and can count as
// evidence, oldest first. Each: {id, tool, input, order, result:{text, isError, structured}}.
export function turnEvidence(records, { scope = 'main', lastAssistantMessage = null } = {}) {
  const turn = currentTurn(scopeRecords(records, scope));
  const allCalls = [];
  const byId = new Map();
  let order = 0;
  for (const record of turn) {
    const content = record?.message?.content;
    if (!Array.isArray(content)) continue;
    if (record.type === 'assistant') {
      for (const block of content) {
        if (block?.type !== 'tool_use' || !block.id) continue;
        const call = { id: block.id, tool: String(block.name ?? ''), input: block.input ?? {}, order: order++, result: null };
        allCalls.push(call);
        byId.set(block.id, call);
      }
    } else if (record.type === 'user') {
      for (const block of content) {
        if (block?.type !== 'tool_result') continue;
        const call = byId.get(block.tool_use_id);
        if (!call) continue;
        const structured = record.toolUseResult && typeof record.toolUseResult === 'object' ? record.toolUseResult : null;
        let text = resultText(block.content);
        if (!text && structured) text = [structured.stdout, structured.stderr].filter((s) => typeof s === 'string' && s).join('\n');
        call.result = { text, isError: block.is_error === true, structured };
      }
    }
  }
  // This hook's own gate message is in the record when it has already stopped the agent once in this turn. That is read
  // from the record so that "once per turn" does not depend on the harness setting stop_hook_active. Only a user message
  // counts: a tool result that happens to print the tag does not.
  const gateSeen = turn.some((r) => r?.type === 'user' && plainUserText(r).includes(GATE_TAG));
  const fromRecords = finalAssistantText(turn);
  const given = typeof lastAssistantMessage === 'string' ? lastAssistantMessage.trim() : '';
  return {
    // The harness's own copy of the last message (when it gives one) wins: the transcript can lag behind the Stop event.
    finalMessage: given || fromRecords,
    calls: allCalls.filter((c) => c.result && !NON_EVIDENCE_TOOLS.has(c.tool)),
    allCalls,
    records: turn.length,
    gateSeen,
  };
}
