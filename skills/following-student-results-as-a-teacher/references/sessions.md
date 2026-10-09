# Sittings, and planning around them

## The call

```jsonc
main-team:list_exam_sessions { "brand": "gmath" }
//  -> sessions, grouped by category and session: date, exam_ids; and a count of them
```

It covers **every sitting on the olympiad** from July 2025 on, past and upcoming, newest first —
the same list every teacher sees on the panel's Archive page. It says nothing about who is entered:
it is **not** the sittings this teacher's students are booked into, however the question is put.
It is not the olympiad's published calendar of rounds and events either, which is
`main-team:get_calendar`, and not one student's entries, which is `main-team:get_student`.

## Which question, which tool

| The teacher asks | Read |
|---|---|
| "what is coming up for my class?" | `main-team:list_exam_sessions` for the dates, then `main-team:list_my_students` for who is entered |
| "when are the rounds this year?" | `main-team:get_calendar` |
| "who is entered for the March sitting?" | `main-team:list_my_students`, filtered by grade |
| "what is Ada entered for?" | `main-team:get_student` |
| "what did the olympiad announce?" | `main-team:list_announcements` |

Answering the wrong one wastes a call and gives a confident wrong answer. Ask which they mean if it
is genuinely ambiguous.

## Turning it into something useful

A season plan is two reads and some arithmetic the teacher can check:

1. `main-team:list_exam_sessions` — the dates. Keep the ones still ahead; the list runs back to
   July 2025 as well.
2. `main-team:list_my_students`, per grade — who is entered and who has paid. The first list
   cannot say that; it is the same for every teacher on the olympiad.
3. Say it back plainly:

> "Two sittings ahead on gmath. 14 March, junior category: 18 of your students, 4 unpaid.
> 21 March, senior: 22 students, all paid. The unpaid four are all in grade 9."

Fees are `handling-payments-and-invoices-as-a-teacher`; entering more students is
`managing-students-as-a-teacher`. This skill reads.

## Time zones and dates

Each `date` is the sitting's calendar day, such as `2026-11-21`: a day, with no time of day and no
time zone, so there is nothing to convert. Quote it as the day. The panel names each sitting rather
than dating it, so when the teacher asks what the panel says, the sitting's name is what they will
see there. A sitting that runs over two days says so in its name, such as "19-20 December 2026", and
its `date` is the last of them. The start time is not in this list; the panel is the authority on it.

## Reminders

There is nothing here to subscribe to, and no tool that sends anything. If a teacher wants a
reminder, the honest answer is that they can put the dates in their own calendar — and only if they
ask for that, since a class calendar entry carries their students' business into another system.

## Errors

| Answer | Meaning |
|---|---|
| an empty list | the olympiad has no sitting on record from July 2025 on — it says nothing about this teacher's class |
| `role_required` | this account is not a teacher on that olympiad |
| `brand_not_allowed` | the connection does not cover that olympiad |
| `tenant_account_missing` | this account has no profile on that olympiad yet |
| `rate_limited` | wait; this is not a tool to poll |

None of them is a reason to try the other olympiads until one answers.
