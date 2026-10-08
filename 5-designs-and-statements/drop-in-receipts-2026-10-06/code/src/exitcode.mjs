// Exit codes. Non-zero is a failure. Zero is NOT a success for the claimed object: it only means the command did not
// fail, so a claim still needs a line that says what happened (the rules for tests, push, merge, HTTP and so on).
//
// Claude Code records a failing command as is_error with a first line "Exit code N". A successful command carries
// no exit line at all, so "no failure found" means "exit 0 or unknown", never "succeeded".
import { splitLines } from './text.mjs';

const HARNESS_EXIT = /^Exit code (-?\d+)\s*$/;
const TEXT_EXIT = [
  /^\s*(?:error:\s*)?(?:process|command|script|job|task|step)\b[^\n]*?\bexited with (?:non-zero )?(?:exit )?(?:code|status)\s*[:=]?\s*(-?[1-9]\d*)\b/i,
  /^exit status (-?[1-9]\d*)\s*$/,
  /returned non-zero exit status (-?[1-9]\d*)/i,
  /^\s*(?:EXIT|exit|rc|RC|returncode|exit_code|exitcode|exit code|status)\s*[:=]\s*(-?[1-9]\d*)\s*$/,
  /^make(?:\[\d+\])?: \*\*\* \[[^\]]*\] Error (-?[1-9]\d*)\s*$/,
];

// {code, line, source}: source is 'harness' (the "Exit code N" line the harness wrote), 'is_error' (the harness flagged
// a failure and gave no number) or 'text' (a line the command itself printed). The line is always a line of the
// output, so it can be quoted. null when nothing says it failed.
export function exitFailure(call) {
  const text = call.output ?? '';
  const lines = splitLines(text);
  for (const line of lines.slice(0, 3)) {
    const m = HARNESS_EXIT.exec(line.trim());
    if (m && Number(m[1]) !== 0) return { code: Number(m[1]), line: line.trim(), source: 'harness' };
  }
  if (call.isError) {
    const first = lines.map((l) => l.trim()).find(Boolean);
    if (first) return { code: null, line: first, source: 'is_error' };
  }
  for (const line of lines) {
    for (const pattern of TEXT_EXIT) {
      const m = pattern.exec(line);
      if (m) return { code: Number(m[1]), line: line.trim(), source: 'text' };
    }
  }
  return null;
}

// True when the harness itself says the command failed (a stronger statement than a line in the command's own output).
export const harnessFailed = (failure) => failure && (failure.source === 'harness' || failure.source === 'is_error');
