#!/usr/bin/env python3
"""Mutation checks: plant one fault at a time in a COPY of the code and show the tests notice.

    python tests\\mutation_check.py

For each fault: copy the project to a temp folder, change one piece of code (the text to change must appear exactly once),
run the tests that should notice, and require that they FAIL. A control run on an unchanged copy must PASS first.
The real files are never touched. Prints one line per fault and ends with "mutation checks: N/N caught".
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (name, file, [(old, new), ...], test file, -k filter or None)
MUTATIONS = [
    ("ranking reversed: the least accurate agent gets the most agency",
     "routing.py", [('ranked.sort(key=lambda a: (table[a]["brier"], h(seed, "tie", rep, rnd, a)))',
                     'ranked.sort(key=lambda a: (-table[a]["brier"], h(seed, "tie", rep, rnd, a)))')], "test_routing.py", None),
    ("the check floor is removed: the best agent can have no check",
     "routing.py", [("CHECKS_BY_RANK = (1, 1, 2, 1)", "CHECKS_BY_RANK = (0, 1, 2, 1)"), ("MIN_CHECKS = 1          # no agent", "MIN_CHECKS = 0          # no agent")], "test_routing.py", None),
    ("the random control secretly uses the track record",
     "routing.py", [('order, how = random_order(agents, rep, rnd, "random", seed), "random"',
                     'order, how = rank_agents(agents, table, rep, rnd, seed=seed), "random"')], "test_routing.py", None),
    ("the record of a model that left the list is still counted",
     "routing.py", [('if a in t and p is not None:', 'if p is not None:')], "test_routing.py", None),
    ("every round gets the same jobs (jobs are not fresh)",
     "routing.py", [("out.extend(ids[(rnd - 1) * per: rnd * per])", "out.extend(ids[:per])")], "test_bank.py", "round_split"),
    ("the leak guard is switched off",
     "bench.py", [("    hit = J.find_leak(prompt)\n    if hit:", "    hit = None\n    if hit:")], "test_runner.py", "leak"),
    ("work that a certifier checked is handed on by the agent's own claim",
     "bench.py", [('accepted = (verdict == "shown") if entry["checked"] else (claim == "done")', 'accepted = (claim == "done")')],
     "test_runner.py", "handed_on"),
    ("the spend cap check is removed",
     "bench.py", [("if self.spent + self.reserved + worst > self.cap:", "if False:")], "test_runner.py", "cap"),
    ("the feedback carries a line of a hidden test",
     "bench.py", [("""lines.append(f"  job {h['job']}: you forecast {h['p']:.2f}; the hidden tests {res}")""",
                   """lines.append(f"  job {h['job']}: you forecast {h['p']:.2f}; the hidden tests {res} " + J.JOBS[h['job']]['hidden'].splitlines()[2])""")],
     "test_runner.py", "feedback"),
    ("the forecast is written to the room after the work, not before",
     "bench.py", [("""            self.emit(name, {"type": "forecast", "job": job, "round": rnd, "agent": agent, "p": data["p"] if data else None,
                             "valid": data is not None, "call_seq": fcall["seq"], "tier": entry["tier"]})
""", "            fdata = data\n"),
                  ("            # 3. the hidden tests, run by the runner",
                   """            self.emit(name, {"type": "forecast", "job": job, "round": rnd, "agent": agent, "p": fdata["p"] if fdata else None,
                             "valid": fdata is not None, "call_seq": fcall["seq"], "tier": entry["tier"]})
            # 3. the hidden tests, run by the runner""")], "test_runner.py", "sealed"),
    ("the scorer counts the agent's claim as what was handed on",
     "score.py", [('"accepted_false_done": accepted and not passed,', '"accepted_false_done": claim["status"] == "done" and not passed,')],
     "test_score.py", "OnTheDryRun"),
    ("the no-room guard is switched off",
     "score.py", [('if not guards.get("G1_baseline_false_done", {}).get("ok", False):', "if False:")], "test_score.py", "Verdict"),
    ("the scorer stops checking that the plan follows the routing rule",
     "score.py", [("if canon(again) != canon(plan):", "if False:")], "test_score.py", "BreakingRules"),
    ("the exact McNemar test returns half the p-value",
     "stats.py", [("return min(1.0, 2 * tail)", "return tail")], "test_stats.py", None),
    ("the sign-flip test becomes one-sided",
     "stats.py", [("            if abs(s) >= obs - eps:\n                hits += 1\n        p, exact = hits / total, True",
                   "            if s >= obs - eps:\n                hits += 1\n        p, exact = hits / total, True")], "test_stats.py", None),
    ("the network block in the sandbox loses one door",
     "sandbox.py", [("_s.create_connection = _blocked\n", "")], "test_room_sandbox.py", "network"),
    ("the sandbox inherits the whole environment",
     "sandbox.py", [('env = {"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}', "env = dict(os.environ)")], "test_room_sandbox.py", "environment"),
    ("the head file no longer catches cut-off lines",
     "room.py", [("if int(hs) != n or hh != prev:", "if False:")], "test_room_sandbox.py", "cut_off"),
    ("a preset that routes by record no longer needs a random twin",
     "routing.py", [("if not tw or tw not in presets:", "if False:")], "test_presets.py", "twin"),
    ("a preset may route where nothing is routed",
     "routing.py", [('elif p["routing"] != "equal":', "elif False:")], "test_presets.py", "routing_only_where"),
    ("the fixed-check preset checks by rank instead of one for everyone",
     "routing.py", [('    if c == "fixed":\n        return CHECKS_FIXED\n', '    if c == "fixed":\n        return CHECKS_TABLED[preset["work"]]\n')],
     "test_presets.py", "work_only"),
    ("the fixed checks leave one agent with no check",
     "routing.py", [("CHECKS_FIXED = (1, 1, 1, 1)", "CHECKS_FIXED = (1, 1, 1, 0)")], "test_presets.py", None),
    ("the check-only preset gives the work share by rank",
     "routing.py", [('EQUAL_WORK = (2, 2, 2, 2)\nWORK_BY_RANK', 'EQUAL_WORK = (3, 2, 2, 1)\nWORK_BY_RANK')], "test_presets.py", "check_only"),
    ("the scorer ignores the declared primary pair and uses D against E",
     "score.py", [('pa, pb = analysis["primary"]["a"], analysis["primary"]["b"]', 'pa, pb = "D", "E"')], "test_presets.py", "primary_pair"),
    ("the ticket follows the arm's letter, not its preset",
     "bench.py", [('tk = ticket_text(job) if self.preset["ticket"] else None', 'tk = ticket_text(job) if self.arm != "A" else None')],
     "test_presets.py", "new_combination"),
    ("every role is sent to the forecast route",
     "bench.py", [('"--provider", self.providers[role],', '"--provider", self.providers["forecast"],')], "test_runner.py", "own_route"),
    ("the worst case ignores the role's reply limit",
     "bench.py", [("self.max_out[role])", 'self.max_out["forecast"])')], "test_runner.py", "worst_case"),
    ("a reply with the JSON fence run into the code fence is no longer read",
     "bench.py", [("    if merged != text:\n        text = merged\n", "    if False:\n        text = merged\n")], "test_runner.py", "json_fence"),
    ("a job's hidden file gets shown in the job text",
     "jobs.py", [("""    s = v["spec"].strip("\\n")""", """    s = v["spec"].strip("\\n") + "\\n" + JOBS[job_id]["hidden"].splitlines()[2]""")], "test_bank.py", "no_hidden_piece"),
]


def copy_project(dst):
    for item in ROOT.iterdir():
        if item.name in {".git", "dryrun", "runs", "__pycache__", "mutation-report.txt"}:
            continue
        if item.is_dir():
            shutil.copytree(item, dst / item.name, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(item, dst / item.name)


def run_tests(folder, test_file, k):
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", test_file]
    if k:
        cmd += ["-k", k]
    env = {"PYTHONDONTWRITEBYTECODE": "1", "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", ""), "PATH": __import__("os").environ.get("PATH", ""),
           "TEMP": __import__("os").environ.get("TEMP", ""), "TMP": __import__("os").environ.get("TMP", "")}
    r = subprocess.run(cmd, cwd=str(folder), capture_output=True, text=True, timeout=900, env=env)
    last = [l for l in (r.stderr + r.stdout).strip().splitlines() if l.strip()][-1:]
    return r.returncode, (last[0] if last else "")


def main():
    caught = 0
    problems = []
    for name, fname, edits, test_file, k in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="eab-mut-") as d:
            d = Path(d)
            copy_project(d)
            code, last = run_tests(d, test_file, k)            # control: the unchanged copy must pass
            if code != 0:
                print(f"CONTROL FAILED for '{name}' ({test_file} -k {k}): {last}")
                problems.append(name)
                continue
            text = (d / fname).read_text(encoding="utf-8")
            for old, new in edits:
                if text.count(old) != 1:
                    print(f"CANNOT PLANT '{name}': text to change found {text.count(old)} times in {fname}")
                    problems.append(name)
                    break
                text = text.replace(old, new)
            else:
                (d / fname).write_text(text, encoding="utf-8")
                code, last = run_tests(d, test_file, k)
                if code != 0:
                    caught += 1
                    print(f"caught      {name}   [{test_file}{' -k ' + k if k else ''}: {last}]")
                else:
                    print(f"NOT CAUGHT  {name}   [{test_file}{' -k ' + k if k else ''}]")
                    problems.append(name)
    print(f"mutation checks: {caught}/{len(MUTATIONS)} caught")
    return 0 if caught == len(MUTATIONS) and not problems else 1


if __name__ == "__main__":
    sys.exit(main())
