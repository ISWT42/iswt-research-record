# S5: Hidden content

**Question.** A log holds private details: names, email addresses, hosts, file paths, keys. If they are blacked out or replaced with a fingerprint before the checker reads the log, does the checker still give the right answer, with a quote it can back?

**Origin:** the most proposed research area on Joshua's outside panel (5 Oct, 5 of 8 models): receipts that keep their value when the log is hashed, blacked out or cut to the minimum.

**Why it matters.** Most real logs can't be shown to anyone as they are. A receipt that only works on an uncensored log stays inside the company that made it.

## Inputs

`inputs/s5-items.jsonl`: 300 records, ids H001-O to H100-H: 100 logs, each in three views. Each record has `id`, `claim`, `turns` and `view`. The coordinator made the views with a fixed script:
- **O:** the original log.
- **R:** private details replaced with `[REDACTED-1]`, `[REDACTED-2]` and so on, the same detail always getting the same number within a log.
- **H:** the same details replaced with a short fingerprint such as `h:3fa9c1d2`.

## The request

- Build it with `receipt_pair` at commit `b7dfbad`: `shown, request = receipt_pair.pair.prepare(item_id, claim, turns)`.
- Use the system prompt and user message as built.
- Check each reply with `receipt_pair.reader.verify(reply_text, shown)`, against the view the model saw. Record `answer`, `code`, `verdict`, `quote` and `turn`.

## Calls

- 300 records × 2 models = 600.
- Repeat a random 20% (`random.Random(20261006)`): 120.
- **720 calls.**

## What the coordinator will count (not you)

For each view, against O, and each model:
- **Right answers**, and in particular false "shown".
- **Verified quotes:** how many quotes pass the check.
- **Where the changes sit:** whether answers change more when the deciding line itself holds a hidden detail.
- **Prediction tested:** R and H stay within a few answers of O when the deciding line holds no hidden detail, and drop when it does.

## Stop and report if

- more than 5% of calls end as "no answer";
- the spend for S5 passes US$2;
- anything is unclear (QUESTIONS.md).
