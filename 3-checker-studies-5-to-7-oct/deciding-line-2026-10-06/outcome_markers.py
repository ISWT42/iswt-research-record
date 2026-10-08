"""Generic outcome markers: the fixed list used by the OUTCOME-MARKER rule.

Written from general knowledge of what tool output looks like (test runners, exit codes, git, HTTP, CI,
package managers, kubectl, docker, terraform, mail and chat APIs, create / delete / deploy confirmations),
BEFORE any development-set quote was opened. It contains no word taken from a particular item, claim, command
or log line, and it never reads an answer key. The file is hashed and time-stamped (PREREG-1) before the
development quotes are read, and it is frozen from then on.

A "marker" is a pattern that states HOW SOMETHING WENT (a result, a status, a count of what was done, an exit
code, a ref update, a confirmation), as opposed to preparation text ("Connecting...", "Reading...", "Checking...")
or a bare command echo. A quote "carries a marker" if any pattern below matches somewhere in the quote text.

Each entry: (family, name, compiled pattern). Some patterns are case-sensitive on purpose (for example the
unittest token OK, or runner tokens in capitals).
"""
import re

I = re.IGNORECASE
M = re.IGNORECASE | re.MULTILINE

MARKERS = (
    # ---- test runners and checks --------------------------------------------------------------
    ("tests", "count_result", re.compile(r"\b\d+\s+(?:passed|failed|failing|passing|errors?|skipped|xfailed|xpassed)\b", I)),
    ("tests", "status_token_capitals", re.compile(r"\b(?:PASSED|FAILED|PASS|FAIL|ERROR|ERRORS|SKIPPED|XFAIL|XPASS)\b")),
    ("tests", "status_word", re.compile(r"\b(?:passed|failed|passing|failing)\b", I)),
    ("tests", "unittest_ran", re.compile(r"\bRan\s+\d+\s+tests?\b")),
    ("tests", "ok_token", re.compile(r"\bOK\b")),
    ("tests", "runner_summary", re.compile(r"\bTests?\s+run:\s*\d+|\btest result:\s*\w+|\bTest\s+Suites?:\s*\d+|\bTests:\s+\d+", I)),
    ("tests", "go_ok_line", re.compile(r"^\s*ok\s+\S+\s+(?:\(cached\)|[\d.]+s)", M)),
    ("tests", "check_or_cross_mark", re.compile("[✓✔✗✘✕✅❌☑☒]")),

    # ---- exit codes ----------------------------------------------------------------------------
    ("exit", "exit_code_phrase", re.compile(r"\bexit(?:ed)?(?:\s+with)?(?:\s+(?:code|status))?\s*[:=]?\s*-?\d+\b", I)),
    ("exit", "exit_code_field", re.compile(r"\b(?:exit_?code|exit_?status|return_?code|returncode|rc)[\"']?\s*[:=]\s*-?\d+\b", I)),

    # ---- git and code hosting ------------------------------------------------------------------
    ("git", "ref_arrow", re.compile(r"->")),
    ("git", "bracket_tag", re.compile(r"\[(?:new branch|new tag|new ref|rejected|up to date|deleted|forced update|remote rejected|tag update)\]", I)),
    ("git", "up_to_date", re.compile(r"\b(?:everything up-to-date|already up[ -]to[ -]date)\b", I)),
    ("git", "hash_range", re.compile(r"\b[0-9a-f]{7,40}\.\.\.?[0-9a-f]{7,40}\b")),
    ("git", "commit_line", re.compile(r"\[[\w./#-]+(?:\s+\(root-commit\))?\s+[0-9a-f]{7,40}\]")),
    ("git", "merge_and_diffstat_words", re.compile(
        r"\bfast-forward\b|\bmerge made by\b|\bautomatic merge failed\b|\bmerge conflict\b|\bCONFLICT\s*\(|"
        r"\bnothing to commit\b|\bfiles? changed\b|\b(?:create|delete) mode\b", I)),

    # ---- HTTP and API status -------------------------------------------------------------------
    ("http", "status_line", re.compile(r"\bHTTP/\d(?:\.\d)?\s+\d{3}\b", I)),
    ("http", "status_code_with_reason", re.compile(
        r"\b(?:200\s+OK|201\s+Created|202\s+Accepted|204\s+No\s+Content|30[1-8]\s+[A-Z][a-z]+|400\s+Bad\s+Request|"
        r"401\s+Unauthorized|403\s+Forbidden|404\s+Not\s+Found|405\s+Method\s+Not\s+Allowed|408\s+Request\s+Timeout|"
        r"409\s+Conflict|410\s+Gone|422\s+Unprocessable|429\s+Too\s+Many\s+Requests|500\s+Internal\s+Server\s+Error|"
        r"501\s+Not\s+Implemented|502\s+Bad\s+Gateway|503\s+Service\s+Unavailable|504\s+Gateway\s+Time-?out)\b", I)),
    ("http", "status_code_field", re.compile(
        r"\b(?:status|status_?code|statusCode|http_?status|response_?code|code)[\"']?\s*[:=]\s*[\"']?[1-5]\d\d\b", I)),
    ("api", "status_text_field", re.compile(r"\b(?:status|state|result|outcome|conclusion|phase)[\"']?\s*[:=]\s*[\"']?[A-Za-z]", I)),
    ("api", "boolean_result_field", re.compile(
        r"\b(?:ok|success|succeeded|accepted|delivered|sent|created|deleted|updated|published|merged|error|failed)"
        r"[\"']?\s*[:=]\s*(?:true|false)\b", I)),
    ("api", "error_field", re.compile(r"[\"']\s*(?:error|errors|error_?code|error_?message)\s*[\"']\s*:", I)),
    ("api", "message_receipt_id", re.compile(r"\b(?:message_?id|msg_?id|messageId)\b|[\"']ts[\"']\s*:\s*[\"']?\d", I)),

    # ---- CI and generic status words ------------------------------------------------------------
    ("status", "success_words", re.compile(r"\b(?:success|successful|successfully|succeeded|succeeds)\b", I)),
    ("status", "failure_words", re.compile(
        r"\b(?:fail|fails|failed|failing|failure|failures|errors?|errored|exception|traceback|fatal|denied|refused|"
        r"rejected|aborted|cancell?ed|timed\s*out|timeout|unauthorized|forbidden|not\s+found|crash(?:ed)?|killed)\b", I)),
    ("status", "completion_words", re.compile(r"\b(?:done|complete|completed|finished|healthy|approved|resolved)\b", I)),
    ("status", "up_to_date_words", re.compile(r"\bup to date\b|\bno changes\b|\bnothing to (?:do|update)\b|\balready (?:exists|installed|applied|satisfied)\b", I)),

    # ---- mail and chat delivery ------------------------------------------------------------------
    ("message", "delivery_words", re.compile(r"\b(?:sent|delivered|bounced|accepted|posted|replied|forwarded)\b", I)),

    # ---- create / change / delete / deploy confirmations ---------------------------------------------
    ("confirm", "change_verbs", re.compile(
        r"\b(?:created|deleted|removed|updated|deployed|published|released|uploaded|installed|uninstalled|applied|"
        r"configured|unchanged|scaled|restarted|saved|written|committed|pushed|merged|tagged|built|migrated|renamed|"
        r"moved|copied|archived|restored|revoked|enabled|disabled|registered|submitted|assigned|closed|reopened|"
        r"patched|reverted|imported|exported|generated|provisioned|destroyed|terminated|added|changed|replaced|"
        r"inserted|affected|processed|synced|synchronized|rolled\s+out|rolled\s+back)\b", I)),
    ("confirm", "kubectl_pod_status_row", re.compile(
        r"\b\d+/\d+\s+(?:Running|Pending|CrashLoopBackOff|ImagePullBackOff|ErrImagePull|Terminating|Evicted|"
        r"OOMKilled|Completed|Succeeded|Failed|NotReady|Error)\b")),
    ("confirm", "kubectl_failure_states", re.compile(r"\b(?:CrashLoopBackOff|ImagePullBackOff|ErrImagePull|OOMKilled|Evicted)\b")),
    ("confirm", "rollout_and_wait", re.compile(r"\bsuccessfully rolled out\b|\bcondition met\b", I)),
    ("confirm", "package_manager_counts", re.compile(
        r"\b(?:added|removed|changed|audited)\s+\d+\s+packages?\b|\bfound\s+\d+\s+vulnerabilit(?:y|ies)\b|\bnpm\s+ERR!", I)),
    ("confirm", "docker_acks", re.compile(r"\bdigest:\s*sha256:[0-9a-f]{8,}|\bpull complete\b|\blogin succeeded\b|\blayer already exists\b", I)),
    ("confirm", "terraform_summaries", re.compile(
        r"\bapply complete!|\bdestroy complete!|\bplan:\s*\d+\s+to\s+add|\bresources:\s*\d+\s+added", I)),
)

MARKER_NAMES = tuple(f"{fam}.{name}" for fam, name, _ in MARKERS)


def markers_in(text):
    """Names (family.name) of every marker pattern that matches somewhere in text, in list order."""
    if not isinstance(text, str) or not text:
        return []
    return [f"{fam}.{name}" for fam, name, pat in MARKERS if pat.search(text)]


def has_marker(text):
    """True if any marker pattern matches somewhere in text."""
    if not isinstance(text, str) or not text:
        return False
    return any(pat.search(text) for _, _, pat in MARKERS)
