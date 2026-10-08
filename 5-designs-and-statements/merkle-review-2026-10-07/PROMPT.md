# A design for AI-agent receipts that redact themselves by access

You are one of several independent reviewers. You have no tools and no web access: answer from what you know, and say plainly when you are unsure. Do not invent sources. Name a paper, standard or product only if you are confident it exists, and say in one line what it does.

## The idea, from an independent AI researcher

When an AI agent says a job is "done", he wants a receipt: a record the agent cannot change, checked with one of three answers. **Shown:** the record backs the claim. **Contradicted:** the record shows the claim is false. **Not shown:** the evidence isn't there.

His proposal for sharing those records safely:

1. Every record (each log line, each agent step, each answer) becomes a leaf: a random salt plus the record, hashed.
2. The leaves are combined in a hash tree (a Merkle tree), in layers: lines into files, files into runs, runs into a day. Only the top root is timestamped, with a public timestamp authority and in Bitcoin, before anyone reads the results.
3. Each viewer receives the records their access allows, each with its salt and the path of sibling hashes up to the root. Hidden records appear in place as hashes labelled "withheld", so nothing disappears silently.
4. Anyone can check a visible record against the timestamped root without seeing the others. A changed record no longer matches.

His words: "you can give a cascade of hashes, and my tech should allow people to auto redact what their access allows."

## Please answer under these headings

1. **Verdict in one paragraph:** is the design sound, and is it worth building?
2. **What is already established:** the closest existing systems, standards or papers, and how this differs from them, or doesn't.
3. **What is new, if anything,** in this application. State it without hype.
4. **How it can fail:** the main technical and practical risks (for example salts, record boundaries, exact byte encoding, leakage through structure or counts, lost salts or keys, revocation, who sets the access rules), with a fix for each.
5. **Threat model:** who could cheat, and how the design stops them or doesn't, including the person who builds the tree.
6. **The smallest prototype that would show it works,** and the test: what to measure, and what result would count against it.
7. **Where it is most useful first,** with one sentence each on why.
8. **What it does not prove:** the limits a reader must be told.

Keep it under 900 words. Plain words, no marketing language.
