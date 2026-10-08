# T13c result: do newer models check claims more? (his hypothesis, 4 Oct 2026)

- Design sealed by FreeTSA at 16:14:15 UTC.
- Ran from 16:14:30 on the PC clock.
- Results sealed by FreeTSA at 16:15:13 UTC.

**Data:** 15,278 engaged replies from dated agents, on T13b's 2,000 claims. Only 8 replies were left out (fine-tuned "leader" agents).

| Responder's release third | Replies | Accept | Verify | Challenge |
|---|---|---|---|---|
| Oldest | 9,271 | 20.5% | 5.6% | 14.9% |
| Middle | 5,259 | 20.9% | 6.0% | 14.8% |
| Newest | 748 | 19.4% | 4.3% | 6.8% |

**Newest against oldest:** verify p = 0.15, accept p = 0.48.

**But the models differ a lot one by one:**
- verify runs from 2.2% (Gemini 2.5 Pro) to 8.8% (Claude Opus 4.5);
- accept runs from 7.7% (o3) to 30.2% (DeepSeek-V3.2).

## What it means
- **"Multi distribution": yes.** Each model has its own reply habits.
- **"Based on agent intelligence": not by release date.** Newer models don't check more; if anything, slightly less (not significant).
- Checking stays rare, between 2 and 9% of replies, for every model.

## Limits
- Release date is a rough proxy for capability.
- The newest third has few replies.
- The reply classes are fixed patterns.

[section removed: forecasts are kept private by the owner's decision of 8 Oct 2026]
