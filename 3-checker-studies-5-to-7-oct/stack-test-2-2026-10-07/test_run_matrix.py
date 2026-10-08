"""Unit tests of the runner's pure parts (event reading, message classes, model identity, the plan order). No model call, no network,
no tool is started. The box can run it too:  python3 test_run_matrix.py   (the order fingerprint must match the PC's)."""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_matrix as RM  # noqa: E402

ORDER_FINGERPRINT = "2a6025aa3591ff00"  # first 16 hex of order_fingerprint(plan_items(...)) on the PC, 7 Oct 2026


def lines(*events):
    return "\n".join(json.dumps(e) for e in events)


def claude(*mid, reply="{}", is_error=False, denials=None, model="claude-sonnet-5-5", extra_result=None):
    init = {"type": "system", "subtype": "init", "model": model, "tools": [], "mcp_servers": [], "apiKeySource": "none", "plugins": []}
    final = {"type": "assistant", "message": {"model": model, "content": [{"type": "text", "text": reply}], "stop_reason": "end_turn"}}
    res = {"type": "result", "subtype": "success", "is_error": is_error, "result": reply, "total_cost_usd": 0.01, "usage": {"input_tokens": 5, "output_tokens": 7},
           "modelUsage": {model: {}, "claude-haiku-4-5": {}}, "permission_denials": denials or []}
    res.update(extra_result or {})
    return lines(init, *mid, final, res)


def use(tid, name="Bash"):
    return {"type": "assistant", "message": {"model": "claude-sonnet-5-5", "content": [{"type": "tool_use", "id": tid, "name": name, "input": {}}]}}


def result_of(tid, text, err):
    return {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": tid, "is_error": err, "content": text}]}}


class ClaudeEvents(unittest.TestCase):
    def test_plain_answer_and_helper_models_are_not_flagged(self):
        a = RM.analyze_claude(claude(reply='{"a": 1}'), "", 0, "claude-sonnet-5-5")
        self.assertEqual((a["reply"], a["tool_attempts"], a["tool_executed"], a["answer_model"]), ('{"a": 1}', 0, 0, "claude-sonnet-5-5"))
        self.assertEqual(a["models_used"], ["claude-haiku-4-5", "claude-sonnet-5-5"])   # recorded, and the answering model is the main one
        self.assertTrue(RM.model_ok("claude-sonnet-5-5", a["answer_model"], []))
        self.assertEqual(a["init"]["apiKeySource"], "none")
        self.assertEqual(a["tokens"]["output"], 7)

    def test_refused_executed_and_unanswered_tool_requests(self):
        refused = RM.analyze_claude(claude(use("t1"), result_of("t1", "Error: No such tool available: Bash", True)), "", 0, "x")
        self.assertEqual((refused["tool_attempts"], refused["tool_refused"], refused["tool_executed"]), (1, 1, 0))
        ran = RM.analyze_claude(claude(use("t1"), result_of("t1", "file1 file2", False)), "", 0, "x")
        self.assertEqual((ran["tool_refused"], ran["tool_executed"]), (0, 1))
        none = RM.analyze_claude(claude(use("t1")), "", 0, "x")
        self.assertEqual((none["tool_refused"], none["tool_executed"]), (0, 1))          # no result at all: counted as executed (halts the cell)
        denied = RM.analyze_claude(claude(use("t9"), extra_result={}, denials=[{"tool_use_id": "t9", "tool_name": "Bash"}]), "", 0, "x")
        self.assertEqual((denied["tool_refused"], denied["tool_executed"], denied["permission_denials"]), (1, 0, 1))
        errored_but_ran = RM.analyze_claude(claude(use("t1"), result_of("t1", "command exited with status 2", True)), "", 0, "x")
        self.assertEqual(errored_but_ran["tool_executed"], 1)                             # an error that is not a refusal: something ran

    def test_other_model_and_error_results(self):
        other = RM.analyze_claude(claude(model="claude-haiku-4-5"), "", 0, "claude-sonnet-5-5")
        self.assertFalse(RM.model_ok("claude-sonnet-5-5", other["answer_model"], []))
        lim = RM.analyze_claude(claude(reply="You've hit your limit · resets 11pm", is_error=True), "", 1, "x")
        self.assertEqual((lim["reply"], lim["diag_kind"]), (None, "plan_limit"))
        login = RM.analyze_claude(claude(reply="Invalid API key · Please run /login", is_error=True), "", 1, "x")
        self.assertEqual(login["diag_kind"], "login")
        be = RM.analyze_claude(claude(reply="API Error: 529 overloaded_error", is_error=True), "", 1, "x")
        self.assertEqual(be["diag_kind"], "backend")
        cut = RM.analyze_claude(claude(reply='{"a"'), "", 0, "x")
        self.assertFalse(cut["cut_off"])
        mt = lines({"type": "system", "subtype": "init", "model": "m"}, {"type": "assistant", "message": {"model": "m", "content": [{"type": "text", "text": "{"}], "stop_reason": "max_tokens"}},
                   {"type": "result", "subtype": "success", "is_error": False, "result": "{", "usage": {}})
        self.assertTrue(RM.analyze_claude(mt, "", 0, "m")["cut_off"])
        self.assertEqual(RM.analyze_claude("", "boom", 1, "m")["reply"], None)

    def test_a_model_reply_that_mentions_a_limit_is_not_a_stop(self):
        a = RM.analyze_claude(claude(reply="the usage limit was reached in the log, error 401"), "", 0, "x")
        self.assertIsNone(a["diag_kind"])


class CodexEvents(unittest.TestCase):
    def codex(self, *items, reply="ok", errors=(), usage=True):
        ev = [{"type": "thread.started"}, {"type": "turn.started"}]
        ev += [{"type": "item.completed", "item": i} for i in items]
        ev += [{"type": "item.completed", "item": {"id": "m", "type": "agent_message", "text": reply}}]
        ev += [{"type": "error", "message": e} for e in errors]
        if usage:
            ev.append({"type": "turn.completed", "usage": {"input_tokens": 9, "cached_input_tokens": 3, "output_tokens": 4, "reasoning_output_tokens": 2}})
        return lines(*ev)

    def test_tool_items_refused_and_executed(self):
        a = RM.analyze_codex(self.codex({"id": "c", "type": "command_execution", "status": "declined", "aggregated_output": "", "exit_code": None}), "", 0, "ok", "gpt-6.1-sol")
        self.assertEqual((a["tool_attempts"], a["tool_refused"], a["tool_executed"]), (1, 1, 0))
        b = RM.analyze_codex(self.codex({"id": "c", "type": "command_execution", "status": "completed", "aggregated_output": "x", "exit_code": 0}), "", 0, "ok", "x")
        self.assertEqual((b["tool_refused"], b["tool_executed"]), (0, 1))
        w = RM.analyze_codex(self.codex({"id": "w", "type": "web_search", "query": "q"}), "", 0, "ok", "x")
        self.assertEqual(w["tool_executed"], 1)
        mcp = RM.analyze_codex(self.codex({"id": "m1", "type": "mcp_tool_call", "status": "failed", "error": "no server"}), "", 0, "ok", "x")
        self.assertEqual((mcp["tool_refused"], mcp["tool_executed"]), (1, 0))
        unk = RM.analyze_codex(self.codex({"id": "u", "type": "something_new"}), "", 0, "ok", "x")
        self.assertEqual(unk["tool_executed"], 1)                                          # an unknown item type counts as executed
        e = RM.analyze_codex(self.codex({"id": "e", "type": "error", "message": "stream hiccup"}), "", 0, "ok", "x")
        self.assertEqual(e["tool_attempts"], 0)                                            # an error item is not a tool request

    def test_header_tokens_reply_and_messages(self):
        hdr = "model: gpt-6.1-sol\nprovider: openai\nreasoning effort: low\nsandbox: read-only\n"
        a = RM.analyze_codex(self.codex(), hdr, 0, "last message", "gpt-6.1-sol")
        self.assertEqual(a["reply"], "last message")
        self.assertEqual(a["settings_reported"], {"model": "gpt-6.1-sol", "effort": "low", "provider": "openai", "sandbox": "read-only"})
        self.assertEqual((a["tokens"]["input"], a["tokens"]["cache_read"], a["tokens"]["reasoning"]), (9, 3, 2))
        self.assertEqual(RM.analyze_codex(self.codex(), "", 0, None, "x")["reply"], "ok")      # falls back to the last agent message
        lim = RM.analyze_codex(lines({"type": "error", "message": "You've hit your usage limit. Try again in 3 days."}, {"type": "turn.failed", "error": {"message": "x"}}), "", 1, None, "x")
        self.assertEqual((lim["reply"], lim["diag_kind"]), (None, "plan_limit"))
        login = RM.analyze_codex("", "ERROR: Not logged in. 401 Unauthorized", 1, None, "x")
        self.assertEqual(login["diag_kind"], "login")
        transient = RM.analyze_codex(self.codex(errors=["stream disconnected before completion: reconnecting 1/5"]), "", 0, "ok", "x")
        self.assertIsNone(transient["diag_kind"])                                           # a transient message in a call that answered


class Helpers(unittest.TestCase):
    def test_model_identity(self):
        self.assertTrue(RM.model_ok("anthropic/claude-sonnet-5.5", "anthropic/claude-sonnet-5.5", []))
        self.assertTrue(RM.model_ok("anthropic/claude-sonnet-5.5", "anthropic/claude-sonnet-5.5-20261001", []))
        self.assertFalse(RM.model_ok("anthropic/claude-sonnet-5.5", "anthropic/claude-sonnet-5.55", []))
        self.assertFalse(RM.model_ok("claude-sonnet-5-5", "claude-haiku-4-5", []))
        self.assertTrue(RM.model_ok("a", "b", ["b"]))
        self.assertTrue(RM.model_ok("a", None, []))

    def test_plan_order_is_cell_independent_and_matches_the_pc(self):
        ctx = RM.Ctx()
        rows = RM.load_prompt_rows(ctx)
        items = RM.plan_items(ctx, rows)
        self.assertEqual(len(items), 576)
        self.assertEqual([it[2] for it in items], list(range(1, 577)))
        self.assertTrue(all(len({r["key"] for r, rep, _ in items if rep == k}) == 192 for k in (1, 2, 3)))
        self.assertNotEqual([r["key"] for r, rep, _ in items if rep == 1], [r["key"] for r, rep, _ in items if rep == 2])
        self.assertEqual(RM.order_fingerprint(items)[:16], ORDER_FINGERPRINT)

    def test_toy_prompts_are_not_among_the_48_logs(self):
        rows = RM.load_prompt_rows(RM.Ctx())
        toys = RM.toy_prompts(rows)
        self.assertEqual(len(toys), 12)
        real = {r["prompt"] for r in rows}
        self.assertFalse(any(t["prompt"] in real for t in toys))
        self.assertFalse(any(RM.TRUTH_RE.search(t["prompt"]) for t in toys))

    def test_argv_for_the_two_tools_follows_the_design(self):
        ctx = RM.Ctx()
        c = RM.CliTransport(ctx, "claude-theirs", ctx.S["cells"]["claude-theirs"], 1)
        argv = c.build_argv(Path("/e"), Path("/l"))
        self.assertEqual(argv[:6], ["claude", "-p", "--output-format", "stream-json", "--verbose", "--model"])
        self.assertIn("--tools", argv)
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertEqual(argv[argv.index("--effort") + 1], "low")
        self.assertEqual(argv[argv.index("--mcp-config") + 1], '{"mcpServers":{}}')
        self.assertEqual(argv[argv.index("--settings") + 1], '{"disableAllHooks": true}')
        self.assertTrue(set(ctx.S["claude_builtin_tools"]) == set(argv[argv.index("--disallowedTools") + 1].split(",")))
        self.assertNotIn("--system-prompt", argv)
        self.assertNotIn("--append-system-prompt", argv)
        x = RM.CliTransport(ctx, "openai-theirs", ctx.S["cells"]["openai-theirs"], 1)
        av = x.build_argv(Path("/e"), Path("/l.txt"))
        self.assertEqual(av[:3], ["codex", "exec", "--json"])
        self.assertEqual(av[-1], "-")
        self.assertEqual(av[av.index("-m") + 1], "gpt-6.1-sol")
        self.assertIn('model_reasoning_effort="low"', av)
        self.assertEqual(sum(1 for a in av if a == "--disable"), 20)
        self.assertEqual(av[av.index("-C") + 1], str(Path("/e")))
        for banned in ("--search", "--oss", "--add-dir", "--profile", "--dangerously-bypass-approvals-and-sandbox"):
            self.assertNotIn(banned, av)
        self.assertNotIn("ANTHROPIC_API_KEY", c.env())
        x.dropped = {"--ignore-rules", "--disable shell_tool"}
        av2 = x.build_argv(Path("/e"), Path("/l.txt"))
        self.assertNotIn("--ignore-rules", av2)
        self.assertEqual(sum(1 for a in av2 if a == "--disable"), 19)


if __name__ == "__main__":
    unittest.main(verbosity=1)
