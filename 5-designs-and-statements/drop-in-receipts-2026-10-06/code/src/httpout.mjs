// HTTP status lines, read by rule. Statuses come from lines a tool printed: curl -i / -v response lines,
// "Status: 200", "<Response [404]>", "gh: Not Found (HTTP 404)", "curl: (22) ... returned error: 404", a lone
// number from curl -w '%{http_code}', and "PUT /path -> 202 Accepted".
//
//   2xx  the request was accepted: a receipt for "the request succeeded", "created", "sent", "posted"
//   4xx / 5xx  the request failed: contradicts any claim that rests on it
//   1xx / 3xx  say nothing (a redirect is followed by the status that counts)
// A 2xx whose body shows a failure marker ("success": false, "error", ...) settles nothing. A claim that is about the
// STATE a change produced ("is enabled", "is active") is not settled by a 2xx either: that needs a reader.
import { splitLines, failureMarkers, BARE_HTTP_STATUS } from './text.mjs';

const REASON = '(?:OK|Created|Accepted|No\\s+Content|Unauthorized|Forbidden|Not\\s+Found|Conflict|Unprocessable(?:\\s+Entity|\\s+Content)?|Too\\s+Many\\s+Requests|Internal\\s+Server\\s+Error|Not\\s+Implemented|Bad\\s+Gateway|Service\\s+Unavailable|Gateway\\s+Timeout|Bad\\s+Request|Method\\s+Not\\s+Allowed|Moved\\s+Permanently|Found|Not\\s+Modified)';
const STATUS_LINES = [
  { re: /^\s*(?:<\s*)?HTTP\/\d(?:\.\d)?\s+([1-5]\d\d)\b/i, method: null },
  { re: /^\s*(?:HTTP\/\d(?:\.\d)?\s+)?(?:Response\s+)?Status(?:\s+Code)?\s*[:=]\s*([1-5]\d\d)\b/i, method: null },
  { re: /^\s*<Response \[([1-5]\d\d)\]>/, method: null },
  { re: /\(HTTP ([1-5]\d\d)\)/, method: null },
  { re: /returned error:\s*([1-5]\d\d)\b/i, method: null },
  { re: new RegExp(`^\\s*(?:(GET|POST|PUT|PATCH|DELETE|HEAD)\\s+\\S+\\s+)?->\\s*([1-5]\\d\\d)\\s+${REASON}\\b`, 'i'), method: 1, group: 2 },
  { re: new RegExp(`^\\s*(GET|POST|PUT|PATCH|DELETE|HEAD)\\s+\\S+\\s+(?:->|=>|:)\\s*([1-5]\\d\\d)\\b`, 'i'), method: 1, group: 2 },
];

// [{status, line, method, at}] in output order.
export function httpStatuses(text, { bareStatus = false } = {}) {
  const found = [];
  splitLines(text).forEach((raw, at) => {
    const line = raw.trim();
    if (!line) return;
    for (const spec of STATUS_LINES) {
      const m = spec.re.exec(line);
      if (m) {
        const status = Number(m[spec.group ?? 1]);
        found.push({ status, line, method: spec.method ? (m[spec.method] ?? null)?.toUpperCase() ?? null : null, at });
        return;
      }
    }
    if (bareStatus) {
      const m = BARE_HTTP_STATUS.exec(line);
      if (m && /^\s*[1-5]\d\d\s*$/.test(line)) found.push({ status: Number(m[1]), line, method: null, at });
    }
  });
  return found;
}

// The status that counts is the last non-1xx, non-redirect one (a 301 then a 200 is a 200).
export function finalStatus(statuses) {
  const real = statuses.filter((s) => s.status >= 200);
  const settled = real.filter((s) => s.status < 300 || s.status >= 400);
  return settled.at(-1) ?? null;
}

// The response BODY is everything after the last status line: used to veto a 2xx that carries a failure.
export function bodyAfter(text, status) {
  const lines = splitLines(text);
  return lines.slice(status.at + 1).join('\n');
}

export function bodyFailureMarkers(text, status) {
  return failureMarkers(bodyAfter(text, status));
}
