# Chasing unpaid entries

## Contents

- Building the list
- Grouping by teacher
- The two things a partner can actually do
- Drafting a follow-up
- Removing an entry instead
- Errors

## Building the list

There is no unpaid-entries tool. The roster is the source.

1. `main-team:list_country_students` with the `brand`, paged, optionally by `grade`.
2. Keep every entry whose `paid` is false, with its `application_id`, the student's handle and name,
   and the teacher the student belongs to.
3. Stop paging when the question is answered. A count by grade rarely needs the whole country.

Totals come from the `price` and `currency` the tool returned. Do not convert currencies and do not
estimate a fee that was not read.

## Grouping by teacher

The useful shape is per teacher, because a teacher is who the partner actually talks to:

> "Unpaid on neo, grade 9 and 10: 34 entries across 9 teachers, 850.00 EUR. The largest are
> Ms Ramírez with 11 and Mr Adeyemi with 7."

Name students only when the partner asks for that teacher's detail, and then in the conversation —
not in anything to be sent on.

## The two things a partner can actually do

1. **Build a cart link.** `main-team:get_students_payment_link` with up to twenty
   `application_ids` answers a `url` that opens the partner's own cart with those entries in it. On
   `coding` the cart takes one entry at a time. Hand the link over; do not open, store or forward
   it, and never say a fee is paid until a fresh read shows `paid` true.
2. **Draft a message for the partner to send.** There is no messaging tool and no contact detail in
   any answer, so nothing here reaches a teacher, a student or a parent.

`main-team:check_discount_code` can say whether a code the partner holds is usable and what it is
worth, before any of that.

## Drafting a follow-up

Write it for the partner to send from their own account, and keep it to what the tools returned:

> "Dear Ms Ramírez, 11 entries for the 21 March sitting on neo are still unpaid — 275.00 EUR in
> total, across 9 students in grades 9 and 10. The payment page in your My Students view has them
> all. Could you let me know if any of them have withdrawn?"

Rules for a draft:

- no student names unless the partner asks for them in the message, and then only their own
  teacher's students;
- never a payment link inside a drafted message: the link belongs to whoever opens it;
- no deadline, penalty or consequence that Main Team has not stated;
- say plainly that the partner sends it — this assistant cannot and does not.

## Removing an entry instead

When a teacher confirms a student has withdrawn, `main-team:remove_unpaid_exam` removes that one
entry with its pending payment. It cannot be undone, so the partner themselves has to confirm it and
an app that cannot ask them gets `open_in_panel` with a panel link — a plain answer, not an error,
and nothing is done. A paid or sat entry cannot
be removed at all. Re-entering later is a new entry at whatever the fee then is.

One entry, one confirmation. Never a single yes over a list of thirty.

## Errors

| Answer | Meaning |
|---|---|
| `not_found` | that entry or student is outside this partner's scope, or gone |
| `cannot_cancel` | the entry is paid or already sat |
| `confirmation_expired` | more than about ten minutes passed; preview again |
| `insufficient_scope` | this app was approved for reading only |
| `writes_disabled` | changes through an AI app are off just now |
| `rate_limited` | wait; do not page the roster harder to make up for it |
