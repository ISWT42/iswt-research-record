// A child process for the concurrency test: appends N receipts to one file, one at a time, as a hook would.
//   node append-writer.mjs <receipts file> <who> <how many>
import { appendReceipts, buildReceipt } from '../../src/receipts.mjs';

const [file, who, count] = process.argv.slice(2);
const result = {
  claim: { kind: 'tests', text: 'All tests pass.', objects: { strong: [], prs: [], env: [] } },
  answer: 'shown', code: 'tests_pass', reason: 'a test-runner summary line shows the tests passed', quote: '12 passed in 0.50s', source: null, stale_edits: 0, needs_reader: false,
};
for (let i = 0; i < Number(count); i++) appendReceipts(file, [buildReceipt(result, { session_id: `${who}-${i}` })]);
