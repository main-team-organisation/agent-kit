# Cart links for a class

## The call

```jsonc
main-team:get_students_payment_link
{
  "brand": "gmath",
  "application_ids": ["70b3d5e2a1c94f6081b2c3d4", "aa11bb22cc33dd44ee55ff66"]
}
//  -> { "count": 2, "application_ids": [...], "url": "https://my.example.org/..." }
```

The ids are `application_id` values out of `main-team:list_my_students`,
`main-team:get_student` or the answer to `main-team:add_exams_for_students`. Never a handle,
never an `exam_id`, never something carried over from an earlier session.

## The limits, which differ per olympiad

| Olympiad | Entries per cart link |
|---|---|
| `coding` | **one** — the panel's cart takes one entry at a time |
| `stem`, `hilingua`, `neo`, `gmath` | up to twenty |

So a class of thirty on gmath is two links; the same class on coding is thirty. Say that before
offering to "do it in one go", and offer the panel instead when thirty links is plainly the wrong
answer:

> "On coding the cart takes one entry at a time, so paying for 30 students here would be 30 separate
> links. Your My Students page handles it in one pass — shall I give you that link instead?"

## Handing a link over

Say what it covers and that the payment happens on that page, where the total is shown — no tool
answers what the entries cost, so do not put a figure on it:

> "This link opens your cart with 12 entries for grade 9; the cart shows the total. Open it and pay
> there."

Then stop.

- **Never open or follow it.** It is for the teacher.
- **Never store, shorten, log or forward it.** Not into a file, a calendar entry, a message or
  another tool.
- **Never build one nobody asked for**, and never one covering students the teacher has not seen
  listed.
- **Never say the fees are paid** because a link was made.

## When there is no link

| Answer | Meaning | Say |
|---|---|---|
| `not_found` | one of the ids is not this account's, or no longer there | re-read the roster and rebuild the list |
| `not_allowed_here` | the cart cannot be built this way for those entries | offer `main-team:get_panel_link`, page `my_students` |
| `role_required` | this account is not a teacher on that olympiad | stop |
| `brand_not_allowed` | the connection does not cover that olympiad | say which ones it does |
| `rate_limited` | too many calls | wait; do not split the cart further to get round it |

## Afterwards

Wait until the teacher says they have paid, then read **once**:
`main-team:list_my_students` with the grade, or `main-team:get_student` for the few that mattered.
`paid` true is the only thing that counts.

If it has not caught up, offer to look again in a few minutes. Do not poll: each read does real work
on the platform, and the connection's budget will run out on nothing.

## Who is paying

A class's fees may be paid by the teacher, by parents individually, or by a partner. All that can be
said from here is what the tools return: `paid`, and in `main-team:list_my_payments` either an
amount this teacher paid, with its `amount_display` to quote, or `amount_hidden` where somebody else
did. Do not infer who paid, and do
not chase a parent — there are no contact details in any answer, and no tool sends anything.
