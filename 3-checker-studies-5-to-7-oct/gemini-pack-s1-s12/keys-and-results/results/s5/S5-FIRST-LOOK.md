# S5, hidden content: first look (coordinator, 6 Oct 2026, scored after the results seal of 04:05:31 GMT)

**Checks:** 720 of 720 requests match the sealed build, and every quote check recomputes. Cost US$0.0806. Repeat 0 is primary. 100 logs in three views: O (original), R (private details redacted), H (private details hashed).

| Scope | Gemma right, O / R / H | Qwen right, O / R / H |
|---|---|---|
| All 100 | 88 / 89 / 87 (false shown 5 / 6 / 7) | 77 / 74 / 77 (false shown 5 / 6 / 6) |
| The 52 with hidden details | 44 / 46 / 44 | 37 / 33 / 36 |
| The 6 whose deciding line was hidden | 5 / 5 / 5 | 5 / 3 / 5 |

**Noise floor:** 8 of 120 repeats changed answer.

**Reading:**
- Hiding private details by redaction or hashing left accuracy within noise.
- Hashed views did as well as the originals for both models.
- When the deciding line itself held a hidden detail, Qwen lost 2 of 6 under redaction and none under hashing. That cell is too small to read.

[paragraph removed: forecasts are kept private by the owner's decision of 8 Oct 2026]

**Limits:**
- The redaction patterns were simple (emails, hosts, IPs, home folders, secret-looking tokens); names were not hidden.
- One author's bank; hosted models.
