"""Stand-in for `node broker.mjs`: used only to test BrokerClient's plumbing. No network, no key."""
import sys

args = sys.argv[1:]
model = args[args.index("--model") + 1]
prompt = open(args[args.index("--prompt-file") + 1], encoding="utf-8").read()
if model == "fail/model":
    sys.stderr.write("[broker] call failed\n")
    sys.exit(1)
if model == "dash/model":
    sys.stdout.write("reply without token counts\n")
    sys.stderr.write("[broker] tokens in/out/reasoning: -/-/-; time 5 ms; cost estimate unknown\n")
    sys.exit(0)
if prompt.startswith("ECHO-PROVIDER"):
    sys.stdout.write("provider " + args[args.index("--provider") + 1] + "\n")
    sys.stderr.write("[broker] tokens in/out/reasoning: 1/1/0; time 5 ms\n")
    sys.exit(0)
sys.stdout.write("fake reply to %d chars\n" % len(prompt))
sys.stderr.write("[broker] tokens in/out/reasoning: 123/45/6; time 5 ms; cost estimate unknown\n")
