# Outside review of his Merkle-cascade idea, run 2: digest (Claude, 7 Oct 2026, from 02:57 UTC)

**The run.**
- **Prompt:** the sealed PROMPT.md (FreeTSA 00:45:58 GMT on 7 Oct), unchanged. No web, no tools.
- **Models:** five, through the AI broker on OpenRouter. Gemini was left out (private material never goes to it); Fable was left out (his "no on fable 5.1").
- **Run 1** failed on the key limit and stays sealed as it was.
- **Answers:** Sol 6.1, Grok 4.7, Kimi K3 and Deepseek V4.1 Flash answered, sealed at 02:53:50 GMT (`ANSWERS-RUN2-SHA256.txt`). GLM 5.3 spent its 6,000-token allowance on reasoning and returned nothing; its retry, at a 16,000 cap, answered and was sealed apart at 02:56:26 GMT (`GLM-RETRY-RUN2-SHA256.txt`).
- **Cost:** US$0.152 for run 2, plus the GLM retry.

These counts are Claude's coding of five answers. They are not a vote on the truth.

| Point | Answers making it (of 5) |
|---|---|
| Sound for the narrow job: a shown record matches what was sealed by a time, without revealing the hidden ones | 5 |
| No new cryptography; the new part is the use (agent receipts, withheld records left visible, the three answers) | 5 |
| Guessable hidden records: salts stop precomputation, not a dictionary of likely texts | 5 |
| Lost salts mean a record can never be opened | 5 |
| One fixed byte encoding (RFC 8785 named by 2) | 5 |
| Structure leaks (counts, positions, timing); pad or say so | 5 |
| Forked roots: one public root per period, consistency proofs, viewers compare | 5 |
| Omission or fabrication before sealing is not stopped; the record is only as good as its capture | 5 |
| Encrypt what must stay secret, or encrypt to each permitted reader (hashing binds, it does not hide) | 4 |
| "Contradicted" needs a rule fixed in advance; a hash interprets nothing | 4 |
| Domain separation between leaves and inner nodes | 3 |
| Salts derived from a key he holds (HKDF per run: Kimi; HMAC of a master key and the leaf id: GLM) | 2 |
| Junk "withheld" leaves can't be told from real ones; commit a type byte, or number the steps | 2 |
| Anchor per run, not per day (OpenTimestamps makes it free) | 1 (GLM) |
| Non-inclusion proofs by sorted or sparse trees, so "not there" can be shown | 1 (GLM) |
| Destroying unreleased salts is the only practical revocation | 1 (Grok) |

**Where first:**
- agent test and CI runs (Sol, Deepseek);
- audits (all five);
- benchmark integrity: "anchoring before grading stops retrofitted results" (Kimi; GLM likewise).


**Read together:**
- The idea holds, as a commitment and disclosure layer.
- Its limits are the capture (what is never recorded leaves no trace) and the meaning of "contradicted".
- His question about a user-controlled salt is answered the same way by two outside models and by Claude: salts derived from a key he holds, in layers.
- The prototype the answers converge on:
  - one canonical run log;
  - salted, domain-separated leaves;
  - a run root anchored before results are read;
  - three viewer bundles;
  - tamper, reorder, fork and dictionary-guess tests.
