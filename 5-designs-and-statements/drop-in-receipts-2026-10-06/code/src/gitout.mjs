// What git and gh print, read by rule. Each function returns
//   {answer:'shown'|'contradicted', quote, code}   a line settles it
//   {answer:null, code}                            the output was recognised and does NOT settle it
//   null                                           nothing recognised
// "Settles" means the line itself says the operation happened (a ref updated, a merge made) or failed (rejected,
// conflict). A command that exits 0 and prints neither settles nothing.
import { splitLines } from './text.mjs';

const SHA = '[0-9a-f]{7,40}';
const PUSH_OK = [
  new RegExp(`^\\s*${SHA}\\.\\.${SHA}\\s+(\\S+)\\s+->\\s+(\\S+)`),                       //    4f1c2aa..9b3e771  fix -> fix
  new RegExp(`^\\s*\\+\\s+${SHA}\\.\\.\\.${SHA}\\s+(\\S+)\\s+->\\s+(\\S+)`),            //  + 1111111...2222222 main -> main (forced update)
  /^\s*\*\s+\[new (?:branch|tag|ref)\]\s+(\S+)\s+->\s+(\S+)/,                              //  * [new branch]  feature -> feature
  /^\s*-\s+\[deleted\]\s+(\S+)/,                                                           //  - [deleted]  old-branch
];
const PUSH_REJECTED = /^\s*!\s+\[(?:rejected|remote rejected)\]/;
const PUSH_FAILED = [
  /^error: failed to push some refs/,
  /^remote: error:/,
  /^remote: Permission to .* denied/,
  /^ERROR: Permission to .* denied/,
  /^fatal: /,
  /Permission denied \(publickey/,
];
const UP_TO_DATE = /^Everything up-to-date\s*$/;

export function pushOutcome(text) {
  const lines = splitLines(text);
  const ok = lines.filter((l) => PUSH_OK.some((re) => re.test(l)));
  const rejected = lines.find((l) => PUSH_REJECTED.test(l));
  const failed = rejected ?? lines.find((l) => PUSH_FAILED.some((re) => re.test(l)));
  if (ok.length && failed) return { answer: null, code: 'push_mixed' };
  if (failed) return { answer: 'contradicted', quote: failed.trim(), code: 'push_rejected' };
  if (ok.length) return { answer: 'shown', quote: ok[0].trim(), code: 'push_ref_updated', refs: ok.map((l) => l.trim()) };
  if (lines.some((l) => UP_TO_DATE.test(l))) return { answer: null, code: 'push_up_to_date' };
  return null;
}

const MERGE_OK = [
  /^Fast-forward\s*$/,
  /^Merge made by the '[^']+' strategy\.?\s*$/,
  /^[✓✔]\s+(?:Squashed and merged|Rebased and merged|Merged)\s+pull request\s+#\d+/,
  /^(?:Squashed and merged|Rebased and merged|Merged)\s+pull request\s+#\d+/i,
  /^\s*"merged"\s*:\s*true\b/,
  /"merged"\s*:\s*true\b/,
  /^Pull Request successfully merged\b/i,
];
const MERGE_FAIL = [
  /^CONFLICT \(/,
  /^Automatic merge failed/,
  /^fatal: refusing to merge/,
  /^error: Your local changes to the following files would be overwritten by merge/,
  /^merge: .* - not something we can merge/,
  /\bPull request #?\d+ is not mergeable\b/i,
  /GraphQL: .*not mergeable/i,
  /"merged"\s*:\s*false\b/,
  /^fatal: /,
];
const MERGE_PENDING = [
  /will be automatically merged/i,
  /^Squash commit -- not updating HEAD/,
  /^Already up to date\.?\s*$/i,
  /^Automatic merge went well; stopped before committing as requested/,
];

export function mergeOutcome(text) {
  const lines = splitLines(text);
  const fail = lines.find((l) => MERGE_FAIL.some((re) => re.test(l)));
  const ok = lines.find((l) => MERGE_OK.some((re) => re.test(l)));
  const pending = lines.find((l) => MERGE_PENDING.some((re) => re.test(l)));
  if (fail && ok) return { answer: null, code: 'merge_mixed' };
  if (fail) return { answer: 'contradicted', quote: fail.trim(), code: 'merge_failed' };
  if (pending && !ok) return { answer: null, code: 'merge_not_done', quote: pending.trim() };
  if (pending && ok && /will be automatically merged/i.test(pending)) return { answer: null, code: 'merge_not_done', quote: pending.trim() };
  if (ok) return { answer: 'shown', quote: ok.trim(), code: 'merge_done' };
  return null;
}

const COMMIT_OK = /^\[(?:detached HEAD|[^\]\s]+)(?:\s+\([^)]*\))?\s+[0-9a-f]{7,40}\]\s+\S/;
const COMMIT_FAIL = [
  /^nothing to commit\b/,
  /^no changes added to commit\b/,
  /^error: /,
  /^fatal: /,
  /^\*\*\* Please tell me who you are/,
];

export function commitOutcome(text) {
  const lines = splitLines(text);
  const ok = lines.find((l) => COMMIT_OK.test(l));
  const fail = lines.find((l) => COMMIT_FAIL.some((re) => re.test(l)));
  if (ok && fail) return { answer: null, code: 'commit_mixed' };
  if (fail) return { answer: 'contradicted', quote: fail.trim(), code: 'commit_failed' };
  if (ok) return { answer: 'shown', quote: ok.trim(), code: 'commit_made' };
  return null;
}

// ---- gh pr create / gh issue create / gh release create: the URL the command prints is the receipt ----------------------
// The claim's own object check (the pull request or issue number must appear in the call) has already tied the call to the
// claim; this says whether the call printed the address of what it made. A command that failed printed no such line and
// exited non-zero, which the exit-code rule reads.
const CREATED_URL = [
  /^\s*https:\/\/[\w.-]+\/[\w.-]+\/[\w.-]+\/(?:pull|issues)\/\d+\s*$/,
  /^\s*https:\/\/[\w.-]+\/[\w.-]+\/[\w.-]+\/releases\/tag\/\S+\s*$/,
];

export function createOutcome(text) {
  const line = splitLines(text).find((l) => CREATED_URL.some((re) => re.test(l)));
  return line ? { answer: 'shown', quote: line.trim(), code: 'created_url' } : null;
}
