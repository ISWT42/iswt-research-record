# Offline evaluation kit spec v1

Frozen design only. No kit build, enrollment, model run, network service or real-log access is authorized. Redactors v1–v3 remain unchanged and paused. Source observations and unresolved release bindings accompany this specification.

## First use and release authority

The first real use is the researcher's own 20 eligible runs, only after the kit's exact model profile passes a fresh, sealed swarm-receipts bench gate, Gate 4 or later. Record its design, rule, input and instrument seals, result reference and profile binding in the kit manifest. Fresh turns must exclude earlier gates. A paired profile must pass with its exact two-model combination and fusion rule; a component's pass does not qualify the pair.

Until Gate 4's design is sealed, require at least 90% correct in each group: 45/50, or ceil(0.9 × n) for a smaller nonempty group, and zero planted failures called `shown`. A subsequently sealed Gate 4 rule governs. Gate 3's narrow pass and post-hoc cross-check are insufficient. No Gate 4 design, result or seal is claimed here. [Sources](sources.json).

Existing deadline/site-launch/checker-retest build prerequisites remain; no build now. Outside donors still require independent ethics review and an approved pilot. Reduced funding means fewer reviewed batches.

## Local workflow

Freeze 20 consecutively eligible runs before scoring. Donor completion labels are `done/not_done/cant_tell`; original assertions are `completion/noncompletion/no_clear_assertion`. Evidence-basis choices and optional explanations stay local. Fix task scope/cutoff first; lock donor answers before revealing checker verdicts. Checker inputs exclude donor labels and calibration answers. Its proposition is “the specified task was completed”; outputs are `shown/contradicted/not_shown`. Execution errors remain separate.

Bundle local inference, disable external networking, tools, telemetry and cloud fallback. Use fresh isolated contexts per item/run; calibration answers never enter inference. Isolate a log-blind exporter receiving only typed counters and approved enrollment/profile values; never serialize model prose, logs, paths, diagnostics or notes. Local memory, swap and backups remain risks.

## Result contract

[The closed JSON schema](result-envelope.schema.json) defines one WebAuthn envelope. Required payload fields: `schema`, `study`, `kit`, `model_profile` (each approved constant 1), `donor_credential`, `counts[27]`, `errors`, `agreement[4]`, `calibration[10]`, `spot_checks[3]`. No donor-defined extensions or version strings.

`counts[9a+3h+c]` uses the assertion, donor and checker orders above. Every cell is 0–20; sum(counts)+errors=20. Donor–checker agreement sums across a=0,1,2: cells (9a,9a+4); disagreement: (9a+1,9a+3); both uncertain: (9a+8); exactly one uncertain: (9a+2,9a+5,9a+6,9a+7). The four totals sum to sum(counts); uncertainty is not correctness. Calibration cells 0–8 use reference/checker order `shown/contradicted/not_shown`, row-major; cell 9 is execution errors. Spot checks count reviewer agreement, disagreement and unverifiability, totaling zero (unassigned) or five (assigned).

Top-level fields are exactly `payload`, `credentialId`, `authenticatorData`, `clientDataJSON`, `signature`. Credential identifiers must exactly match enrollment, not arbitrary strings. No supplied public key is trusted. Binary fields use canonical unpadded base64url. Decoded bounds: credential IDs 1–1023 bytes, authenticator data exactly 37, client data at most 512, DER signature 8–72. Entire canonical envelope: at most 8192 UTF-8 bytes. Reject duplicate/extra keys, fractions, negative zero, alternate numeric spellings, invalid encodings and trailing data.

## Browser signing and verification

Use a packaged loopback service: RP ID `localhost`, exact origin `http://localhost:5361`, loopback binding only, strict Host/Origin and frame restrictions. Offline means no external network; `file://` is not the signing origin. Do not run the reference server or reuse its enrollment store. Local origin impersonation remains a compromised-host risk.

Enroll a dedicated study FIDO2 credential using ES256 only (algorithm −7), cross-platform selection and required user verification; supervise hardware enrollment without exporting attestation identifiers. No PIV/OpenPGP setup. Compatibility requires ES256, UV and an approved browser—not every FIDO2/browser combination is promised.

Canonical payload bytes use recursively sorted object keys, preserved array order, two-space JSON indentation, UTF-8 and no trailing newline. The challenge is SHA-256 of UTF-8 `offline-evaluation-kit/v1\n` followed by those bytes; `\n` means one LF byte. The browser recomputes it from the displayed payload. `navigator.credentials.get` requests the enrolled credential with `userVerification: required`.

Verify against the enrolled ES256 key: exact `webauthn.get` type, challenge, origin and non-cross-origin ceremony; RP-ID hash; valid ES256 signature over original authenticatorData concatenated with SHA-256(original clientDataJSON); then authenticated UP and UV flags. These flags establish neither reader comprehension nor civil identity.

Strictly parse DER, require 1≤r,s<n, and internally normalize s to min(s,n−s) before verification. Preserve original assertion bytes. Never rewrite signed client/authenticator data. Accept only the profile's pinned browser-produced client-data byte template with fixed fields/values; unexpected fields, whitespace variants or extension data block export. The template permits no log-derived free string besides the payload-derived challenge. Assertion flags must reject AT/ED/reserved bits and inconsistent backup flags; retain the native counter without treating it as execution proof.

## Exact calibration gate

Run all 160 calibration items before real-log access in that session and again before export. Every observed cell must equal the kit's published reference table exactly; require reference execution-errors=0. Any difference blocks real-log access/export as applicable and flags `KIT_MODEL_RUNTIME_MISMATCH` locally. Preserve diagnostics locally; never retry selectively, substitute reference counts or export an error message.

Pin weights, quantization, prompts, seed, sampler, tokenizer, runtime, numerical kernels, precision, hardware class and threading. Temperature zero alone is insufficient. Check signed-manifest hashes before and after execution. The reference is published and manifest-bound before donor evaluation; changing it requires a new reviewed release. Reference values and the qualifying profile remain unassigned release bindings—not invented here.

Under the previous sum-only schema, the ten calibration counts had C(169,9) possible vectors: at most 47.83 bits. One required vector reduces that table's data-dependent capacity to zero for a fixed profile. The 27 donor cells plus errors still allow C(47,20) vectors, up to 43.15 bits. Derived agreement adds none. These are representational bounds, not measured leakage. Spot counts, identifiers, native counters, signatures and submission/withholding remain channels. Calibration equality can hide per-item swaps; a modified kit can copy the public table. Equality is compatibility evidence under honest execution, not attestation.

## Approval and verification limits

Preview the readable tables and exact canonical payload; sign; verify locally; then preview the complete envelope and explicitly export those immutable bytes. Any change cancels approval and requires new verification/signing. No automatic transmission. A separate receiver repeats schema, arithmetic, reference-table and WebAuthn checks, retaining no malformed body or diagnostic text.

Accept one aggregate per enrolled donor per study window, across replacement credentials. Identical payloads intentionally have identical challenges; replay protection is the acceptance ledger, not a fresh challenge or raw-signature identity. Normalize low-S only internally; it removes a malleability choice, not signature randomness.

The donor envelope must satisfy credentialId=payload.donor_credential. Randomly selected donors receive five independent, on-device spot checks without copying logs. Reviewers label before seeing donor/checker answers: when both reviewer and donor are decisive, matching labels count as agreement and different labels as disagreement; if either is `cant_tell`, count unverifiable. The reviewer checks placement/procedure, then signs the byte-identical donor payload in a second envelope using their assigned enrolled credential. The acceptance ledger requires assigned donors to have five checks plus that countersignature; unassigned donors must have zero. Count only the donor submission. No counter proves attendance.

A sealed kit identifies reviewed bytes; signatures prove enrolled-credential approval, not honest execution, true labels or confidentiality. Study credentials remain linkable pseudonyms. Omit deciding-line hashes, timestamps, user handles, attestation objects and free-text labels from exports.

## Research scope

Retain agreement, abstention and donor-reported false-done rates, with decisive-label denominators and donor-cluster analysis. The investigator's first batch is self-unblinded. These are not population accuracy or independently proven truth. Calibration is a fixed compatibility check, not a fresh blind performance result. No central rerunning, textual cause analysis or independent full-case adjudication is possible without renewed local participation.

## Doubts considered and dismissed

- Universal key/browser support: dismissed; required ES256/UV and strict templates bound compatibility.
- Exact calibration closes all covert channels: dismissed; donor counts and native assertion data remain variable.
- Gate 3 licenses this kit: dismissed; the exact profile needs the specified fresh sealed gate.
- Approval proves truthful execution: dismissed; sealing, signatures and spot checks establish narrower evidence.
