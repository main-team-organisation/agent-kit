# Confirmations, worked through

## Class W: preview, then the same call again

The first call is a dry run. It changes nothing and comes back as `confirmation_required`, carrying
a summary built from ids, counts and prices the platform returned — never from text somebody typed.

```jsonc
// 1. the dry run
{ "brand": "stem", "exam_id": "6a1c4f2b9d07e85c3b214fa0" }

// answer: confirmation_required
//   summary: "Physics, senior, sitting of 14 March 2027, 09:00, 25.00 EUR"
//   confirmation: "cfm_example1"
```

Show the summary. Wait for a clear yes. Then:

```jsonc
// 2. the real call — identical, plus the value
{ "brand": "stem", "exam_id": "6a1c4f2b9d07e85c3b214fa0", "confirmation": "cfm_example1" }
```

Rules that are easy to get wrong:

- **Identical means identical.** Add, drop or change any other argument and the value stops
  matching; the tool will answer `confirmation_required` again with a new one.
- **One value, one use.** It cannot be reused for a second entry, a second student or a retry.
- **About ten minutes.** After that it answers `confirmation_expired`. Call again without it, show
  the fresh summary, and confirm again — do not assume the answer is still yes.
- **Never invent one.** A value that was not returned by this same tool in this session is a guess,
  and the server refuses it.
- **A batch is one confirmation.** `main-team:add_exams_for_students` previews the whole batch and
  confirms the whole batch. Show how many students and how many entries before confirming.

## Class D: the person, or nothing

Four tools cannot be undone: `main-team:cancel_exam_application`,
`main-team:unlink_my_teacher`, `main-team:remove_student_from_my_list` and
`main-team:remove_unpaid_exam`.

The app itself must put the question to the person. Where the app cannot, the tool comes back with a
plain answer — `status` `open_in_panel` and a panel link, not an error — and **nothing happens**:

```jsonc
// answer to a class D call from an app that cannot ask the person
{ "status": "open_in_panel", "url": "https://my.example.org/..." }
```

Hand the link over; do not look for another tool that would do the same thing without asking, and do
not retry the call with a `confirmation` value — the same answer comes back.

Before any of the four, say what does not come back:

- a cancelled entry is gone, and entering again later is a new entry at whatever the fee then is;
- an unlinked teacher stops seeing the student's results at once, and re-linking needs the
  teacher's username again;
- a student removed from a list keeps their account, entries, payments and results — only the link
  to that teacher goes, and the student has to link again themselves;
- an unpaid entry taken back goes with its pending payment and everything recorded against it, and
  entering that student again later is a new entry at whatever the fee then is.

## What a refusal means

- `confirmation_required` on a call that already carried a value: the arguments changed, or the
  value was for a different call. Start the dance again.
- `confirmation_expired`: too slow. Start again.
- `open_in_panel`: this app cannot ask the person. Not an error, and nothing was done. Stop and hand
  over the link.
- `cannot_cancel`, `cannot_change`: the platform refuses it regardless of confirmation — a paid or
  sat exam, usually. Say so and offer the panel.

## Never batch a yes

One yes covers one change, or one batch that was previewed as a batch. "Yes, do all of that" over a
plan of six separate changes is worth reading back once before the first call, and each change is
still its own preview and its own confirmation.
