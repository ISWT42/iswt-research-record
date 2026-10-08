// INSTALL.md is part of the product: its settings snippets must be valid JSON that point at the hook, and its dry run must work.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const install = readFileSync(join(root, 'INSTALL.md'), 'utf8');
const snippets = [...install.matchAll(/```json\n([\s\S]*?)```/g)].map((m) => JSON.parse(m[1]));

test('INSTALL.md has two settings snippets (report, gate), each valid JSON with Stop and SubagentStop', () => {
  assert.equal(snippets.length, 2);
  for (const snippet of snippets) {
    for (const event of ['Stop', 'SubagentStop']) {
      const hooks = snippet.hooks[event][0].hooks;
      assert.equal(hooks.length, 1);
      assert.equal(hooks[0].type, 'command');
      assert.match(hooks[0].command, /^node "[^"]+\/code\/stop-check\.mjs"/);
      assert.equal(typeof hooks[0].timeout, 'number');
    }
  }
});

test('the report snippet has no --gate and the gate snippet has it, on both events', () => {
  const [report, gate] = snippets;
  for (const event of ['Stop', 'SubagentStop']) {
    assert.ok(!report.hooks[event][0].hooks[0].command.includes('--gate'));
    assert.ok(gate.hooks[event][0].hooks[0].command.endsWith('stop-check.mjs" --gate'));
  }
});

test('the hook file the snippets name exists in this repository, and "floor, not box" is quoted from the spec', () => {
  assert.ok(existsSync(join(root, 'stop-check.mjs')));
  assert.ok(existsSync(join(root, 'examples', 'demo-transcript.jsonl')));
  assert.ok(install.includes('**It is the floor, not the box.** An agent that can write the files the check reads can still fake them. The box, with a record kept out of the agent\'s reach, is the full version. The card says which one the user has.'));
  assert.ok(install.includes('That is rung 3 of his ladder, a record outside the agent\'s word, as far as the harness keeps it honest.'));
});

test('the dry run in INSTALL.md gives the card it shows: 3 claims, one of each answer', () => {
  const proc = spawnSync(process.execPath, ['stop-check.mjs', '--no-receipts', '--no-system-message'], {
    cwd: root, input: JSON.stringify({ transcript_path: 'examples/demo-transcript.jsonl', hook_event_name: 'Stop' }), encoding: 'utf8',
  });
  assert.equal(proc.status, 0);
  assert.equal(proc.stdout, '');
  assert.match(proc.stderr, /3 claims checked: 1 shown, 1 contradicted, 1 not shown\./);
  for (const line of [
    '  shown: "All tests pass."',
    '    line: 12 passed in 0.50s',
    '    from: Bash call toolu_demo_tests: pytest -q',
    '  contradicted: "I pushed the fix to origin/fix-parser."',
    '    line: ! [rejected]        fix-parser -> fix-parser (fetch first)',
    '  not shown (needs a reader): "I deployed it to production."',
    '    why: no tool call in this turn did that operation',
  ]) assert.ok(proc.stderr.includes(line + '\n'), line);
  // and INSTALL.md shows those same lines
  for (const line of ['shown: "All tests pass."', 'line: 12 passed in 0.50s', 'line: ! [rejected]        fix-parser -> fix-parser (fetch first)', 'why: no tool call in this turn did that operation']) assert.ok(install.includes(line), line);
});
