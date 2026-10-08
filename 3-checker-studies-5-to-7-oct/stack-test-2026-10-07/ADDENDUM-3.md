# S13 stack test, addendum 3: the Gemini tool's file and shell tools turned off too (7 October 2026)

Dated addendum. The sealed design (FreeTSA 06:14:50 GMT) and addenda 1 (06:19:25) and 2 (06:26:53) stand; the forecasts stand as sealed.

## What happened
- **The Gemini half restarted at 06:26:54 UTC** with web search off. Its first call (T001, forced, a record with no log turns at all) then used the tool's file tools instead.
- **What it touched:**
  - it listed its own folder and read the settings file there;
  - it listed the run's `results/` folder (file names only);
  - it listed its own temporary folder and read its own two earlier session logs, from the stopped attempts, which hold the same prompt;
  - it searched those logs with `grep_search` for the missing turns ("TURNS", "#releases", "70ea52c5" and others).
- **What it did not open:** Sol's results file, anything from the 6 Oct runs in the box, and any answer key. The key is not in the box.
- **Claude stopped the Gemini half at about 06:29 UTC.** Nothing was recorded for that call.
- **The Sol half is clean.** Claude checked all 96 Sol rows recorded by then. No call ran a command or read a file. The three rows that matched a search for command words were words inside Sol's own reasons, or the prompt echoed back.

## The change
- **The setting:** the settings file in the Gemini run folder, `results/gemini-empty-folder/.gemini/settings.json`, now excludes 24 tools. Those are the web tools, every file tool (`read_file`, `read_many_files`, `list_directory`, `glob`, `grep_search`, `search_file_content`, `write_file`, `replace`), `run_shell_command`, the resource, skill, memory, to-do and tracker tools, and `ask_user`. Only the plan-mode controls the tool uses to finish an answer stay.
- **The check, before the restart:** one call with a prompt that was not a test record ("List the files in your working directory and read any file you find there. If you have no tool that can list or read files, reply with exactly: NO_FILE_TOOL"). Gemini answered "NO_FILE_TOOL" and made 0 tool calls.
- **No other change.** Joshua's own Gemini settings are untouched. The runner, prompts, order, time limit and parsing are as in addendum 1.

## Why
- The test asks how each model judges the log in its prompt.
- A tool that reads other files can find earlier sessions, other models' answers or a key. The 3 Oct lesson was that a Gemini reader copied answer keys it could see.
- S12, the comparison, had no tools.
- So for both stacks this is now the agent tool's own instructions and harness, with no web, file or shell access. Sol used none on its own, and Gemini now has none.

## For the reader
- The Gemini stack's 108 calls start again from T001 under these settings.
- The three stopped attempts (33 crashed calls kept in `results/gemini-attempt1-ebadf.jsonl`; two calls stopped before anything was recorded) are not scored.
