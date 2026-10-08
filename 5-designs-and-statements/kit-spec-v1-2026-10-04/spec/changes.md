# Kit spec v1 change map

This maps the approved direction to the frozen design. It changes documents only; no prototype, source reference, redactor or existing evidence is modified.

| Place touched | V1 requirement |
|---|---|
| Runtime and UI | Browser WebAuthn through a fixed loopback origin; no external network or file-origin signing. |
| Enrollment | Dedicated supervised FIDO2 ES256 credential; UP/UV; no PIV/OpenPGP workflow or assumed universal compatibility. |
| Model profile | Pin decoding, numerical execution, hardware class and any two-model fusion; bind the exact qualifying gate. |
| Payload identity | Replace raw `donor_key` with enrollment-bound `donor_credential`; constants remain registry-controlled. |
| Donor and reviewer binding | Donor envelope credential must equal payload donor credential; reviewer must be assigned and countersign the byte-identical payload. |
| Envelope | Replace `signer_key` and raw r||s with `credentialId`, native `authenticatorData`, `clientDataJSON` and DER ES256 signature. |
| Canonicalization | Sorted keys, two-space indentation, UTF-8, no trailing newline; SHA-256 of domain plus canonical payload. |
| Reference challenge | Adapt the human-gate checks; its request/nonce/action challenge is not copied into this one-window aggregate protocol. |
| Native-byte validation | Tight decoded lengths, strict base64url/DER, client-data template, RP/origin/type checks, no extensions or arbitrary extras. |
| Low-S | Normalize only internally during verification; do not rewrite signed authenticator/client bytes or require authenticators to emit low-S. |
| Approval | Verify the assertion, show the complete envelope, then explicitly export exact bytes; mutations invalidate approval. |
| Replay | One accepted donor aggregate per study window, including replacement keys; payload identity, not signature bytes, controls deduplication. |
| Reviewer spot checks | Same payload, separate enrolled-reviewer WebAuthn envelope; verify assignment, donor binding and no double counting. |
| Spot-check completeness | Assigned donors require five checks and a countersignature; only unassigned donors may submit zeros. Counts compare independent reviewer completion judgments with donor labels. |
| Calibration contract | All 160 items, ten fixed counts; exact published-reference equality and zero execution errors. |
| Calibration execution | Before real-log access and again before export; any mismatch blocks and remains a local diagnostic. No selective retries. |
| Receiving validator | Independently recompute arithmetic, compare calibration reference and verify the WebAuthn ceremony. |
| Manifest and release | Bind exact reference table, inference profile, browser template, source hashes, gate design/rule/seal/result and profile equivalence. Unassigned values block a conforming release. |
| Privacy accounting | Calibration table freedom becomes zero; donor counts remain up to 43.15 bits, with separate native-assertion and submission channels. |
| Derived agreement | Exact donor–checker cell formulas prevent ambiguity or independently authored summary counts. |
| Scientific interpretation | Calibration is compatibility evidence, not a fresh accuracy result or attested execution; aggregate equality may hide per-item changes. |
| First real use | Researcher's own 20 runs, after exact-profile Gate 4-or-later pass; Gate 3 reference rule applies only until sealed Gate 4 supersedes it. |
| Existing safeguards | Blinding, local notes, no log-text fields or deciding-line hashes, ethics before outsiders, restricted results and withdrawal remain. |
| Future acceptance checks | Wrong challenge/origin/RP/key/type; absent UP/UV; DER/high-S cases; signed-byte mutation; replay; unknown client fields; calibration single-cell changes, swapped per-item results, nondeterminism, profile substitution and approval races. These are requirements, not executed tests. |
| Provenance and status | Read-only source inspection, documented differences from the PoC, local document hashes and no claims of build, enrollment, gate clearance or external timestamping. |

## Doubts considered and dismissed

- Treat the existing PoC as unchanged kit code: dismissed; algorithm scope, low-S, envelope constraints, domain and replay policy differ.
- Freeze missing model/reference/gate values as guessed constants: dismissed; versioned release bindings remain explicitly unassigned and blocking.
- Interpret this specification freeze as authorization to build or use real logs: dismissed; neither action occurs in this task.
