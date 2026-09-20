# Sittings, and planning around them

## The call

```jsonc
main-team:list_exam_sessions { "brand": "gmath" }
//  -> sessions, grouped by category and session: date, count, exam_ids
```

It covers the sittings **this teacher's students are booked into** — not the olympiad's whole
programme, which is `main-team:get_calendar`, and not one student's entries, which is
`main-team:get_student`.

## Which question, which tool

| The teacher asks | Read |
|---|---|
| "what is coming up for my class?" | `main-team:list_exam_sessions` |
| "when are the rounds this year?" | `main-team:get_calendar` |
| "who is entered for the March sitting?" | `main-team:list_my_students`, filtered by grade |
| "what is Ada entered for?" | `main-team:get_student` |
| "what did the olympiad announce?" | `main-team:list_announcements` |

Answering the wrong one wastes a call and gives a confident wrong answer. Ask which they mean if it
is genuinely ambiguous.

## Turning it into something useful

A season plan is two reads and some arithmetic the teacher can check:

1. `main-team:list_exam_sessions` — the dates.
2. `main-team:list_my_students`, per grade — who is entered and who has paid.
3. Say it back plainly:

> "Two sittings ahead on gmath. 14 March, junior category: 18 of your students, 4 unpaid.
> 21 March, senior: 22 students, all paid. The unpaid four are all in grade 9."

Fees are `handling-payments-and-invoices-as-a-teacher`; entering more students is
`managing-students-as-a-teacher`. This skill reads.

## Time zones and dates

Dates come from the platform as the platform holds them. Quote them as given. Do not convert to the
teacher's local time unless they ask, and if they do, say which time zone you converted from and
that the panel is the authority.

## Reminders

There is nothing here to subscribe to, and no tool that sends anything. If a teacher wants a
reminder, the honest answer is that they can put the dates in their own calendar — and only if they
ask for that, since a class calendar entry carries their students' business into another system.

## Errors

| Answer | Meaning |
|---|---|
| an empty list | no student of this teacher is booked into any sitting on that olympiad |
| `role_required` | this account is not a teacher on that olympiad |
| `brand_not_allowed` | the connection does not cover that olympiad |
| `tenant_account_missing` | this account has no profile on that olympiad yet |
| `rate_limited` | wait; this is not a tool to poll |

None of them is a reason to try the other olympiads until one answers.
