# Finding an exam, and entering it

## What the list has already decided

`main-team:find_exams_for_me` is not a catalogue of everything the olympiad runs. The platform has
already removed:

- exams for other grades — it uses the student's own grade;
- exams not offered in their country;
- categories they have already entered;
- sittings that would put two exams on one day, where that olympiad forbids it;
- sittings that have closed.

So anything it returns is something `main-team:add_exam_application` will accept. If a student
insists an exam is missing, the answer is that the platform does not offer it to them — not that
the list is wrong. Do not go looking for the exam id another way.

Each row carries `exam_id`, `category_id`, `session_id`, `session_date`, `language_code`, `price`,
`price_display` and `currency`. `price` is already in the currency's major unit, never cents (25 is
25.00 EUR); `price_display` is the text to quote.

`session_date` is the sitting's calendar day, such as `2026-03-14`, with no start time and no time
zone. A sitting run over two days, which its name shows, gives its **last** day here. Once the
student has entered, `main-team:list_my_exams` gives the same sitting's **first** day as
`exam_date`, with `time_zone`, so the two can differ by a day and both are right. The moment the
sitting starts is its `exam_start_time`; its `exam_time` is the panel's display text, a start time
for some sittings and a window such as "24 Hours in GMT" for others, so never read a start time
out of it.

## Offering the options

Five at most, in the student's own words:

> "Three sittings are open for you on stem:
>  1. Physics, senior — 14 March, English — 25.00 EUR
>  2. Physics, senior — 21 March, English — 25.00 EUR
>  3. Chemistry, senior — 21 March, English — 25.00 EUR
>  Which one?"

Sort by date. Give the day only: this list has no start time, so do not invent one. If the student
asks when it starts, say `main-team:list_my_exams` shows the time and its time zone once they have
entered, and the panel shows it too. Do not recommend one unless asked, and if asked, say what it is
based on — the date, the fee — rather than inventing difficulty or prestige.

## Entering

```jsonc
// 1. dry run — changes nothing
{ "brand": "stem", "exam_id": "6a1c4f2b9d07e85c3b214fa0" }
//    -> confirmation_required, with a summary and a confirmation value

// 2. after a clear yes — identical arguments, plus the value
{ "brand": "stem", "exam_id": "6a1c4f2b9d07e85c3b214fa0", "confirmation": "cfm_example1" }
//    -> application_id, payment_required, amount, currency, payment_url, next_step
```

Then say, in one sentence: what they are entered for, what it costs, and that it is not paid until
they open the link and pay.

## One at a time

Enter one exam, read the answer, then the next. Not because of a limit, but because each entry can
change what the next one is allowed to be — the same-day rule is the usual reason a second entry is
refused after a first one succeeded.

## What can still go wrong

| Answer | What it means | What to do |
|---|---|---|
| `exam_not_eligible` | the platform refuses this entry for this student | re-read the list; do not retry the same id |
| `already_applied` | there is already an entry for that exam | say so and move on; nothing is wrong |
| `tenant_account_missing` | this student has no profile on that olympiad yet | ask them to open that olympiad once in the panel |
| `writes_disabled` | changes through an AI app are off just now | say so; reading still works; do not retry |
| `insufficient_scope` | this app was approved for reading only | offer a panel link |
| `rate_limited` | too many calls just now | wait, then one more try |

## After entering

The fee is handled by `paying-olympiad-fees-as-a-student`: the link from
`main-team:get_payment_link`, a discount code checked with `main-team:check_discount_code`, and a
later read of `main-team:list_my_exams` to see `paid` turn true. Never tell a student a fee is paid
before that read says so.
