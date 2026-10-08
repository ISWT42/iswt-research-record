# Sealable designs: his five claims of 5 Oct 2026, 10:27 to 10:31 UTC (relayed), each with its fail condition fixed before data

Written by the collation session (Claude), read-only on his data, between 11:39 and 12:25 UTC on 5 Oct 2026. This README was written at 2026-10-05 12:26:56 UTC (from the clock).

**Status: manifest built offline; NOT stamped.** Stamping sends only the manifest's SHA-256 to FreeTSA and the OpenTimestamps calendars. It waits for Joshua's yes (AGENTS.md rule 4; seal-envelope.py stamps "only when you decide").

## Files
- C1-DESIGN-v1.md (people act on purpose context)
- C2-DESIGN-v1.md (agents act when they know the context)
- C3-DESIGN-v1.md (published rules shape later model behaviour)
- C4-DESIGN-v1.md (the rule spreads)
- C5-DESIGN-v1.md (only interaction can prove it)
- MANIFEST-SHA256.txt: every file above with its SHA-256 (built with Workbench\gathering-kit-2026-10-05, `python -m receiptkit manifest <folder>`).

Each design was drafted by one agent and then checked by an adversarial reviewer before this folder was written. The reviewer's high-severity problems and their fixes are listed at the end of each design.

## Placeholders
Slots marked [HIS PROBABILITY] (and similar [HIS ...] slots) are his predictions. They are not part of this seal. He sets them in a separate predictions file, sealed before the step it predicts, so this design seal does not wait on them.

## Note on C5
C5's design says it is not fully sealable until claim 3's question file exists, because it reuses C3's sealed questions and needs their hashes. This seal fixes C5's hypothesis, arms and fail conditions only. A C5 v2 that carries those hashes is sealed before any C5 step. The joint manifest already pins C3's design text.

## To stamp (owner runs, after his yes; from inside this folder)
    openssl ts -query -data MANIFEST-SHA256.txt -sha256 -no_nonce -cert -out MANIFEST-SHA256.txt.tsq
    curl -s -H "Content-Type: application/timestamp-query" --data-binary "@MANIFEST-SHA256.txt.tsq" https://freetsa.org/tsr -o MANIFEST-SHA256.txt.tsr
    C:\Users\joshd\Desktop\Moonshots\tools\ots\.venv\Scripts\ots.exe stamp MANIFEST-SHA256.txt
Then record it in Private\claims\SEALED-RECORD-INDEX-ADDENDUM-2026-10-05.md (the earlier index files are never edited).

Any change after the stamp is a new version, sealed before the step it affects. Sealed files are never edited.
