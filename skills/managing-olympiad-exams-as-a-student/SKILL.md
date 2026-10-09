---
name: managing-olympiad-exams-as-a-student
description: "Helps a student of the Main Team olympiads — stem, hilingua, neo, gmath and coding — or a parent sitting with them, run their own exam entries through the main-team MCP server: listing the exams they are entered for with dates, times and payment state, finding the exams their grade may still enter, entering one, moving an entry to another sitting, category or language, cancelling an unpaid entry, answering an invitation to somebody else's team entry, and linking or unlinking the teacher who may enter them. Explains what find_exams_for_me has already ruled out, why an entry can stop being changeable, and what already_applied, exam_not_eligible, cannot_change and cannot_cancel mean. Never helps take or answer an exam. Use when a student connected with a student account asks about entering, changing, cancelling or listing their Main Team exams."
license: Apache-2.0
metadata:
  audience: "student"
---

# Managing olympiad exams as a student

This is the student's own entries on one olympiad at a time. Start from `main-team:whoami`, pick a
`brand`, and work from a list — never from a remembered id.

Every tool here: [references/tools.md](references/tools.md).

## The four things a student asks for

### "What am I entered for?"

`main-team:list_my_exams` with the `brand`. It answers every entry — upcoming, under way and past —
with the exam, the sitting's `exam_date` with its `time_zone` and its `exam_start_time`, whether it
is `paid`, the `price` with its `price_display`, and the hints `can_change` and `can_cancel`. The
`price` is already in the currency's major unit, never cents: 25 with `currency` EUR is 25.00 EUR,
so quote `price_display` and never divide it by 100. The start time is
`exam_start_time`, not `exam_time`: that is the panel's display text, which for some sittings is a
window such as "24 Hours in GMT" rather than a time.

Read it before anything else: every other tool here needs an `application_id` from this list. The
platform does some catching up when it is read, so call it when something has actually changed
rather than over and over.

### "What else can I enter?"

`main-team:find_exams_for_me` with the `brand`. It already accounts for the student's grade and
country, what they have entered, and the olympiad's own rule about two exams on one day — so
everything it returns is something `main-team:add_exam_application` will accept.

Offer at most five options, each with the date, the time, the language and the `price_display`, and wait
for the student to choose. Do not choose for them.
[references/finding-and-adding.md](references/finding-and-adding.md).

### "Enter me for that one"

`main-team:add_exam_application` with the `exam_id` from that list.

1. Call it once. It answers `confirmation_required` with a summary and a `confirmation` value and
   changes nothing.
2. Show the summary — exam, sitting, price. Wait for a clear yes.
3. Call again with the same arguments plus `confirmation`.
4. The answer carries `application_id` and, when there is a fee, `payment_url`. Say that the fee is
   not paid until they open that link and pay. Nothing here takes money.

One exam at a time, reading the answer before the next.

### "Change it" or "cancel it"

Moving an entry keeps the same entry: `main-team:change_exam_application`, with an `exam_id` from
`main-team:find_exams_for_me` called with `for_application_id` set to that entry. Language alone, on
stem only: `main-team:list_exam_language_options` then `main-team:change_exam_language`.

Cancelling cannot be undone and the student themselves must confirm:
`main-team:cancel_exam_application`. A paid or sat entry usually cannot be cancelled here at all.
[references/changing-and-cancelling.md](references/changing-and-cancelling.md).

## Invitations and teachers

`main-team:respond_to_team_invitation` accepts or declines an invitation to join somebody else's
team entry — and accepting can remove the student's own not-yet-started entry for the same exam, so
say that first. `main-team:get_my_teacher`, `main-team:link_my_teacher` and
`main-team:unlink_my_teacher` manage the teacher who may see results and enter the student for
exams. [references/teams-and-teachers.md](references/teams-and-teachers.md).

## Rules that stop this going wrong

- **Only ids from this session.** `application_id` from `main-team:list_my_exams`, `exam_id` from
  `main-team:find_exams_for_me`. Never carry one over from an earlier conversation and never
  construct one.
- **Never take, start or answer an exam.** There is no tool for it. Refuse exam content while a
  sitting is under way; revising from published past papers beforehand is a different thing.
- **A refusal is final.** `exam_not_eligible` means the platform will not accept that entry, whatever
  a list looked like a minute ago — re-read rather than retry. `already_applied` means it is
  already done. `cannot_change` and `cannot_cancel` mean the entry has moved past that point.
- **Never guess at what a sitting costs**, when it is, or whether it is paid. Quote what the tool
  returned, with its `currency`.
- **Do not repeat the student's own details back** beyond what the task needs, and never write their
  entries into another tool or a file unless they asked for it.

## When to hand over to the panel

`main-team:get_panel_link` builds the address of one panel page — `my_exams`, `results`,
`certificates`, `profile`, `connected_apps`. Use it whenever the answer is "you will need to finish
this yourself": paying, editing personal details, or reviewing what this assistant just did.

If a tool answers `open_in_panel` — which is how a change that cannot be undone comes back when this
app cannot put the question to the student — that is the whole answer: nothing was done, so hand the
link over and stop.
