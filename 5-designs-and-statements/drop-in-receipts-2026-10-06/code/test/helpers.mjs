// Builds SYNTHETIC transcripts for the tests, in the record shapes Claude Code writes. No real transcript is ever read.
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

// A scratch folder for one test. Only folders made here are tracked, and exactly those are removed when the test process
// exits (node --test runs each test file in its own process), so a run leaves nothing behind in the temp folder.
const made = [];
export function scratch(label = 'test') {
  const dir = mkdtempSync(join(tmpdir(), `drop-in-receipts-${label}-`));
  made.push(dir);
  return dir;
}
process.on('exit', () => { for (const dir of made) { try { rmSync(dir, { recursive: true, force: true }); } catch { /* leave it for the system */ } } });

let counter = 0;
export const nextId = () => 'toolu_' + String(++counter).padStart(4, '0');

export const prompt = (text) => ({ type: 'user', message: { role: 'user', content: text } });
export const say = (text) => ({ type: 'assistant', message: { role: 'assistant', content: [{ type: 'text', text }] } });
export const think = (text) => ({ type: 'assistant', message: { role: 'assistant', content: [{ type: 'thinking', thinking: text }] } });

// A tool call and the result the harness captured for it: [assistant tool_use record, user tool_result record].
// A failing Bash command is how Claude Code records it: is_error true and a first line "Exit code N".
export function tool(name, input, output, { isError = false, id = nextId(), structured } = {}) {
  const use = { type: 'assistant', message: { role: 'assistant', content: [{ type: 'tool_use', id, name, input }] } };
  const result = {
    type: 'user',
    message: { role: 'user', content: [{ type: 'tool_result', tool_use_id: id, content: output, ...(isError ? { is_error: true } : {}) }] },
    ...(structured ? { toolUseResult: structured } : {}),
  };
  return [use, result];
}

export function bash(command, output, { exit = 0, id } = {}) {
  const failed = exit !== 0;
  return tool('Bash', { command }, failed ? `Exit code ${exit}\n${output}` : output, {
    isError: failed, id, structured: { stdout: output, stderr: '', interrupted: false },
  });
}

export const transcript = (...parts) => parts.flat();

export function writeTranscript(records, dir = scratch('test')) {
  const path = join(dir, 'session.jsonl');
  writeFileSync(path, records.map((r) => JSON.stringify(r)).join('\n') + '\n');
  return { path, dir };
}

// A small helper to build one finished turn: a prompt, tool calls, and the agent's final message.
export function turn(finalMessage, ...calls) {
  return transcript(prompt('please do the task'), ...calls, say(finalMessage));
}
