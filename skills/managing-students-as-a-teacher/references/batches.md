# Entering a class in batches

## Contents

- The limits
- The two-call shape
- Reading the answer
- Resuming after a failure
- What each refusal means
- Removing entries again

## The limits

`main-team:add_exams_for_students` takes `items`: up to **fifty students** in one call, up to
**twenty exams** each. `roster.py plan` builds batches of fifty by default; `--chunk` makes them
smaller, which is worth doing on a first run.

The connection also has its own budget: sixty calls a minute, and **30 changes an hour**. A batch
costs two changes — its first call and the confirmed one — whatever its size, so fifty students in
one batch is two changes, while fifty one-student batches would be a hundred and run into
`rate_limited` within the hour. Batch properly rather than looping per student, and when
`rate_limited` comes, wait rather than splitting the work into more calls.

## The two-call shape

```jsonc
// 1. the dry run — nothing is created
{
  "brand": "gmath",
  "items": [
    { "student": "stu_x7k2m9p4", "exam_ids": ["6a1c4f2b9d07e85c3b214fa0"] },
    { "student": "stu_b3n6v2c8", "exam_ids": ["6a1c4f2b9d07e85c3b214fa0"] }
  ]
}
//  -> confirmation_required: how many students, how many entries, and a confirmation value

// 2. after a clear yes — the same items, plus the value
{ "brand": "gmath", "items": [ ... exactly the same ... ], "confirmation": "cfm_example1" }
```

Change one student, one exam id or the order and the value stops matching. If the teacher wants a
change after seeing the summary, build the new batch and preview it again.

## Reading the answer

Per student: `created`, `already_applied`, `refused` with a `reason`. The call also carries
`applications_created` and, if it stopped part way, `stopped_at`.

A batch is not all-or-nothing: some students can be entered while others are refused. Report it that
way — "34 entered, 2 already had it, 1 refused because that grade cannot take that exam" — and never
report a batch as fully done without reading the per-student results.

## Resuming after a failure

If a call times out or the connection drops, **do not simply send it again**. Read first:

1. `main-team:list_my_students` with the `grade` filter, or `main-team:get_student` for a few
   handles, and see which entries exist now.
2. Build a batch of only the students still missing the entry.
3. Preview and confirm that one.

Sending the same batch again is usually harmless — an entry that already exists comes back as
`already_applied` rather than being duplicated — but "usually" is not a reason to skip the read.

## What each refusal means

| Answer | Meaning | Do |
|---|---|---|
| `exam_not_eligible` | the platform will not take that entry for that student | record it, move on; do not retry |
| `not_found` | that handle is not on this account's list any more | re-read the list |
| `already_applied` | the entry exists | not an error; report it |
| `confirmation_expired` | more than about ten minutes passed | preview again and re-confirm |
| `insufficient_scope` | this app was approved for reading only | stop; offer a panel link |
| `writes_disabled` | changes through an AI app are off just now | stop; say reading still works |
| `rate_limited` | too much, too fast | wait, then continue with the next batch |
| `role_required` | this account is not a teacher on that olympiad | stop |

## Removing entries again

`main-team:remove_unpaid_exam` takes one `student` and one `application_id`. It removes the pending
payment with the entry and cannot be undone, so the teacher themselves has to confirm it: an app that
cannot ask them gets `open_in_panel` with a panel link — a plain answer, not an error — and nothing
is done. A **paid** entry, or
one already sat, cannot be removed here at all — the platform refuses it, and the answer is
`cannot_cancel`.

One entry, one confirmation. Do not offer to "clear all the unpaid ones" as a single yes: read the
list, show exactly which entries and which students, and confirm each removal.
