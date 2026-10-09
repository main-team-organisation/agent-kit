# Errors

> **Generated** from the server's own tool catalog, version 2.2.2. Do not edit.

Every error answer means **nothing was done**. There is no half-finished change to clean up, so
the question is only what to tell the person and whether anything is worth trying again. The one
exception is `temporarily_unavailable` on a confirmed change: the platform may have been slow rather
than down, so read before you try again.

| Code | What the server says | What to do |
|---|---|---|
| `not_connected` | This connection is no longer active. Nothing was done; connect the app again at auth.main-team.org. | Stop. Tell the person to connect the app again at `auth.main-team.org`; nothing was done. |
| `reconsent_required` | What this connection may do has changed since it was approved. Nothing was done; approve it again at auth.main-team.org. | Stop. What the connection may do has changed; ask the person to approve it again at `auth.main-team.org`, then start over. |
| `insufficient_scope` | This connection was not approved for changes. Nothing was done; reconnect and allow changes to use this tool. | Stop changing. This connection was approved for reading only. Offer a panel link instead, or ask the person to reconnect and allow changes. |
| `brand_not_allowed` | This connection does not cover that olympiad. Nothing was done. | Use a `brand` the connection covers. `whoami` lists them; never retry with a guess. |
| `role_required` | That is not something this account can do on that olympiad. Nothing was done. | Stop. This account does not hold that role on that olympiad. Say so; do not try another olympiad to find one that works. |
| `role_changed` | This account holds a different role on that olympiad than when the connection was approved. Nothing was done; approve the connection again. | Stop. The role changed since the connection was approved; ask the person to approve it again. |
| `tenant_account_missing` | This account has no profile on that olympiad yet. Nothing was done; open the olympiad once in the panel and try again. | Stop. Ask the person to open that olympiad once in the panel, then try again. |
| `not_found` | No such record, or it is not this account’s. Nothing was done. | Do not retry and do not guess another id. Re-read the list the id came from; it may have changed or never belonged to this account. |
| `not_allowed_here` | That cannot be done through an AI client. Nothing was done. | Stop. That is not something an AI client does here. Offer a panel link with `main-team:get_panel_link`, and do not retry the same call. Two tools also answer it for a call that is too big: `main-team:get_students_payment_link` on coding, which takes one application per link, and `main-team:register_students`, for more than 100 student-olympiad pairs or rows too long to check at once — send fewer. From `main-team:register_students` it can also mean registering students is not open to this account on that olympiad, for instance because the teacher’s own profile has no country: say which. |
| `confirmation_required` | This change needs confirming first. Nothing was done yet. | Expected on the first call of a change. Show the summary, wait for a clear yes, then repeat the call with the same arguments plus the `confirmation` value. |
| `confirmation_expired` | That confirmation is no longer good. Nothing was done; ask again. | The confirmation was good for ten minutes. Call again without it, show the fresh summary and confirm again. |
| `open_in_panel` | This has to be done in the panel. Nothing was done. | Stop. Hand over the link in the answer; it is done in the panel. A change that cannot be undone answers this way too, as a plain answer rather than an error, when the app cannot put the question to the person: nothing was done. |
| `exam_not_eligible` | That exam is not one this student can be applied to. Nothing was done. | Do not retry. Re-read the eligible list; the exam is not one this student may be applied to. |
| `cannot_change` | That application can no longer be changed. Nothing was done. | Stop. That application can no longer be changed. Say why if the answer says, and offer the panel. |
| `cannot_cancel` | That application can no longer be cancelled. Nothing was done. | Stop. That application can no longer be cancelled here — a paid or sat exam usually cannot. Offer the panel. |
| `already_applied` | There is already an application for that exam. Nothing was done. | Not an error to fix: the entry already exists. Report it and move on. |
| `window_closed` | That group challenge is not open for changes right now: it is outside its dates or has been closed. Nothing was done. | Stop. The group challenge is outside its dates or closed, so nothing in it can change now. Say so; do not retry. |
| `group_limit_country` | Max group limit reached for your country for that grade group. Nothing was done. | Stop. Tell the teacher their country has reached its group limit for that grade group; the organisers decide limits. Never retry, and never try another grade group to get round it. |
| `group_limit_teacher` | You have reached the maximum number of groups for that grade group. Nothing was done. | Stop. The teacher already holds as many groups as allowed for that grade group. Say so; deleting an unused draft group frees a place. |
| `already_in_group` | A student in that request is already in another group for this challenge. Nothing was done. | Do not retry. A student in the request is already in another group of this challenge; re-read the student list and leave them out. |
| `group_size_invalid` | That would leave the group with too few or too many students for this challenge. Nothing was done. | Do not retry. The group would be too small or too big for the challenge; re-read the group and its limits first. |
| `not_eligible_grade` | A student in that request is not in this group’s grade group. Nothing was done. | Do not retry. A student is not in the group’s grade group; re-read the student list for that grade group. |
| `group_locked` | That group cannot be changed this way right now. Nothing was done; read the group to see where it stands, and an administrator can help from the panel. | Stop. The group’s status does not allow this now: it may not be confirmed yet, its work may already be sent, or it may be confirmed, paid, being paid for or have uploads. Re-read the group and say what its status allows; an organiser can help in the panel. Do not retry. |
| `step_not_open` | That step is not open: the step before it has not been submitted, or this one already was. Nothing was done. | Do not retry. Re-read the group: steps open one after another, and this one is not the open step. |
| `step_empty` | That step has no file yet. A member uploads one in the panel first. Nothing was done. | Tell the person to upload the file in the panel (`upload_url`), then submit. |
| `steps_incomplete` | Every step has to be submitted before the group’s work can be sent. Nothing was done. | Not yet: every step has to be submitted before the group’s work can be sent. Say which are left. |
| `already_submitted` | The group’s work has already been sent. Nothing was done. | Not an error to fix: the group’s work was already sent. Report it and move on. |
| `profile_incomplete` | Your profile has no country, and groups are counted per country. Set it in your profile, then try again. Nothing was done. | Stop. The teacher’s profile has no country, and groups are counted per country; they set it in their profile, then try again. |
| `payment_required` | That needs paying for first. Nothing was done; the payment link opens the panel’s own screen. | The fee has to be paid first. Get a payment link and hand it over; never say it is paid until a read shows it. |
| `rate_limited` | This connection has asked for more than it may just now. Nothing was done; try again shortly. | Wait. Honour any wait the answer gives, then retry once. Do not loop, and do not split the work into more calls: a connection makes 30 changes an hour, and a change’s preview and its confirmed call are two. The one exception is `main-team:register_students` refusing a batch as more than is left of today’s registrations (2000 new accounts a teacher a day, by the UTC day): the answer does not say how many are left, and a refused call costs no change, so send a smaller batch, and the rest tomorrow. |
| `writes_disabled` | Changes through an AI client are switched off for now; reading still works. Nothing was done. | Stop changing. Changes through an AI client are off just now; reading still works. Do not retry. |
| `temporarily_unavailable` | This is temporarily unavailable. Nothing was done; try again shortly. | After a read, retry once after a short pause. After a confirmed change, read first: a slow answer can come after the change was made, so look for it with the matching read and ask to make it again only if it is not there. If it happens again, stop and tell the person. |
| `upstream_error` | The platform could not answer that. Nothing was done; quote the request id to support. | Stop. Quote the `request_id` from the answer’s `meta` to support; do not retry the same call repeatedly. |

**One of those words is not always an error.** A change that cannot be undone answers
`open_in_panel` with a panel link as a plain answer — no error, and nothing done — when the app
cannot put the question to the person itself. Read it the same way: hand the link over and stop.

## Row problems

`main-team:register_students` reports a row it cannot take as a value inside its answer,
never as an error: `problems` carries them while nobody has been registered, and `not_registered`
carries the `reason` for a row or an olympiad refused after the confirmation. A problem names the
`row`, counting from 0, the `field` to correct and, when one olympiad found it, that `brand`; it never
repeats a cell’s value (only `exam_not_eligible` carries the `exam_id` the row named), so ask the
teacher rather than guess.

| Code | What it means and what to do |
|---|---|
| `already_your_student` | The student is already on this teacher’s list, so they are not registered again. `student` is their handle there: take the row out, and enter their exams on that olympiad with `main-team:add_exams_for_students`. On another olympiad of the row the student links themselves with `main-team:link_my_teacher`. The one exception is a row sent again within 24 hours of a call that stopped: an olympiad after the row’s first that the stopped call listed in `not_registered` is sent again, without the olympiads that answered `already_your_student`, and is attached. A row with every olympiad listed there failed on its first, so its account was not made or not finished: it is sent again whole, in the same order, never one olympiad at a time. |
| `duplicate_in_request` | Two rows carry the same e-mail address; `duplicate_of` is the earlier row. Ask the teacher which row is right — usually one is a copy — and send one of them. Siblings who share a parent’s address are two students: each needs an address of their own, since it is where their own password goes. |
| `email_unavailable` | Another Main Team account already uses the address, and the answer never says whose. Never guess another address. The student links themselves to the teacher with `main-team:link_my_teacher` from their own account, or the teacher gives that student’s own other address. |
| `exam_not_eligible` | The exam (`exam_id`) is not open to that row’s grade on that olympiad (`brand`). Read `main-team:find_exams_for_grade` for the grade on that olympiad again and let the teacher choose; do not swap in another exam yourself. |
| `invalid` | The cell is not in the template’s format — a date that does not exist or is not DD/MM/YYYY, a name with `<`, `>`, `@`, `://` or a control character such as a line break, a city or a school with `<`, `>` or a line break, a school written as an id, letters in a phone number. Correct it with the teacher. A `field` of null means the row as a whole. |
| `missing` | A required cell is empty, City is filled and School is not, or the platform could not place the city or the school. Ask the teacher for the value; never invent one. |
| `olympiad_not_allowed` | The row names an olympiad (`brand`) this connection does not hold as a teacher. Leave that olympiad out of the row, or the teacher connects that olympiad as a teacher first; never pick another olympiad for them. |
| `unknown_grade` | The olympiad has no such grade. Check the grade with the teacher. |

## The three rules that matter more than the table

1. **Never loop.** `writes_disabled`, `not_allowed_here`, `role_required`, `insufficient_scope`
   and `open_in_panel` will answer the same way every time. Say what happened and stop.
2. **Never widen the search after a refusal.** A `not_found` or a `role_required` is not an
   invitation to try another olympiad, another student or another id until something works.
3. **Say what did not happen.** "The entry was not created" is the useful sentence; the code by
   itself is not.
