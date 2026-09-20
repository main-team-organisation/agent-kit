# Exam changes on a teacher's behalf

## Contents

- When a partner should do this at all
- Eligibility, once per grade
- The batch, previewed then confirmed
- Reading the answer, and resuming
- Removing an entry
- Errors

## When a partner should do this at all

A partner can enter a teacher's students for exams. That does not mean they always should. Before
building anything, check that the partner is acting on something the teacher actually asked for, and
say what you are about to do in their words:

> "That is 28 students across two of Ms Ramírez's grades, entered for the 21 March sitting on neo.
> Is that what she asked for?"

An assistant that quietly enters a class on somebody else's behalf is the failure this skill exists
to avoid.

## Eligibility, once per grade

```jsonc
main-team:find_exams_for_student { "brand": "neo", "student": "stu_x7k2m9p4" }
//  -> exams: exam_id, category_id, session_id, session_date, language_code, price, currency
```

The list already accounts for the student's grade, the partner's country, what the student holds and
the olympiad's same-day rule. Students in the same grade get the same list, so call it **once per
grade**, not once per student.

Offer the partner a handful of options per grade, with dates and fees, and let them choose.

## The batch, previewed then confirmed

```jsonc
// 1. dry run — nothing is created
{ "brand": "neo", "items": [ { "student": "stu_x7k2m9p4", "exam_ids": ["6a1c4f2b9d07e85c3b214fa0"] } ] }
//  -> confirmation_required: how many students, how many entries, and a confirmation value

// 2. after a clear yes — the same items, plus the value
{ "brand": "neo", "items": [ ... identical ... ], "confirmation": "cfm_example1" }
```

Up to **fifty students** per call, up to **twenty exams** each. Change anything in `items` and the
confirmation value stops matching.

Do not loop one student per call to get round the batch size: that is fifty changes instead of one,
and the connection's change budget will stop it.

## Reading the answer, and resuming

Per student: `created`, `already_applied`, `refused` with a `reason`. Report all three — "26
entered, 1 already had it, 1 refused because the grade cannot take that exam" — rather than calling
the batch done.

If a call fails part way, read before retrying: `main-team:list_country_students` with the `grade`,
or `main-team:get_student` for the handles in question, and build a batch of only what is missing.
Re-sending the whole batch is usually harmless, because an existing entry comes back as
`already_applied`, but read first anyway.

## Removing an entry

`main-team:remove_unpaid_exam` takes one `student` and one `application_id`. It removes the pending
payment with the entry and cannot be undone, so the partner themselves has to confirm it: an app that
cannot ask them gets `open_in_panel` with a panel link — a plain answer, not an error — and nothing
is done.

A **paid** entry, or one already sat, cannot be removed here at all — `cannot_cancel`. Re-entering
later is a new entry at whatever the fee then is. One entry, one confirmation; never a blanket yes
over a list.

## Errors

| Answer | Meaning | Do |
|---|---|---|
| `exam_not_eligible` | the platform will not take that entry for that student | record it; do not retry |
| `not_found` | the student is outside this partner's scope | re-read the roster |
| `already_applied` | the entry exists | report it; nothing is wrong |
| `confirmation_expired` | too slow | preview again and re-confirm |
| `insufficient_scope` | approved for reading only | stop; offer a panel link |
| `writes_disabled` | changes through an AI app are off | stop; reading still works |
| `role_required` | not a partner on that olympiad | stop |
| `rate_limited` | wait, then the next batch | do not split batches to get round it |
