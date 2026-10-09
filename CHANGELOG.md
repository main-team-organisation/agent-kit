# Changelog

The agent kit carries the Main Team MCP server’s version. Every release is a GitHub release of
this repository; the server itself is described at https://hub.main-team.org/api/mcp.

## 2.2.2 - 2026-10-10

**No tool changes in this release.** The server's tools, their arguments and their answers are those of
2.2.1; what changes is the agent kit. The kit published until now is 1.0.0, so this section says first what is
different for somebody upgrading from it, and then what 2.2.2 itself corrects.

### Since kit 1.0.0, in short

- **New in the server.** A copy of a certificate or of a result as a PDF file, made for use with an AI app and
  not the official document (`get_certificate_copy`, `get_result_copy`); a teacher's or a partner's whole
  student list in one call (`export_student_list`); online group challenges for students and teachers,
  seventeen tools; and a teacher registering new students, with their exams, on up to five olympiads at once
  (`get_student_registration_template`, `find_exams_for_grade`, `register_students`).
- **Four changes break code written against 1.0.0** (2.0.0): a certificate is named by an opaque
  `certificate` value rather than `certificate_id`; every exam date is a calendar day (`YYYY-MM-DD`), not a
  timestamp; `duration_minutes` is how long a sitting lasts, with the start window in `window_hours`; and a
  past paper's `year` is a number.
- **Every amount a server tool answers is in the currency's major unit** (2.2.1): `price: 20` with
  `currency: "EUR"` is 20.00 EUR, never cents, with `price_display` or `amount_display` beside it to quote.
  Amounts on neo are USD. The REST API is unchanged and answers the stored figure in cents (`price: 2000` is
  20.00); `AGENTS.md` and `GEMINI.md` now say which is which.
- **The consent screen moved from version 1 to version 4**, so every connection has been approved again at
  least once; an app that is asked to sign in again simply reconnects.
- **Three new skills**, fourteen in all for the server: `taking-part-in-group-challenges-as-a-student`,
  `running-group-challenges-as-a-teacher` and, in this release, `registering-new-students-as-a-teacher`.
  The REST API skills beside them come from that API's release 1.2.0.

### Added

- **The skill `registering-new-students-as-a-teacher`.** Registering students who have no account yet now
  has a skill of its own, with the registration script, the template and its own evals, taken out of
  `managing-students-as-a-teacher`. Its description says when it applies — new students or accounts from a
  class list, an Excel or CSV sheet or the template — and when it does not: entering students already on the
  list, adding students to a challenge group, or an integration holding an API key, for which the REST API's
  `registering-main-team-students-from-spreadsheets` is the skill.
- **The limits a registration runs into**: 2000 new accounts a teacher a day, counted by the UTC day; 30
  changes an hour for a connection, where a change's preview and its confirmed call count as two, so one
  connection registers at most about 750 students an hour; and 24 hours in which a stopped call can be
  resumed, after which a student links themselves to the teacher instead. A batch refused for the daily limit
  is the one case where sending fewer rows, rather than waiting, is the answer.
- **Paying for newly registered students.** The registration answer carries exam ids, and a payment link takes
  application ids: the kit now reads them from the student list first, then builds links of up to twenty
  entries, one on coding.
- **What a partner cannot do**, said in both partner skills, in the routing table and in an eval: a partner
  registers no new students, and the students' own teacher does it.
- **A partner's own payments and certificates, and past papers for teachers and partners**, which no skill
  explained before: `list_my_payments`, `list_my_certificates`, `get_my_certificate` for a partner, and
  `list_study_materials` with `get_study_material` for a teacher and a partner.
- The registration and password rules, and "do not loop", in `GEMINI.md` as well as `AGENTS.md`.

### Changed

- `registration.py` and `roster.py` refuse an Excel or other spreadsheet file, and a CSV that is not UTF-8,
  and say how to save the sheet as "CSV UTF-8". The skills say the same.
- `registration.py` no longer reads a date such as 03/04/2013 one way: a date whose day and month could be
  swapped is reported until the teacher says which order the whole sheet uses (`--dates dmy` or
  `--dates mdy`).
- `registration.py` checks names as the platform does — no `<`, `>`, `@`, `://` or control characters — and
  cities and schools for `<`, `>` and line breaks, and refuses a row at an example address, so the template's
  two example rows cannot be registered by mistake.
- `registration.py` accepts a grade only when the cell holds one number from 1 to 12 ("Year 7" is 7, "07" is 7):
  a cell such as "1/2" or "1-2" was read as grade 12 without a word, and is now reported. It reports a phone
  number over 30 characters once rather than twice, and says when the batches need more than one hour's changes
  or more than one day's new accounts.
- The privacy rules make room for registration: a teacher gives their new students' addresses, dates of birth
  and phone numbers for that one tool, the local file the script writes stays on the teacher's machine, and it
  is deleted, with the saved answers, once the registration is done.
- `managing-students-as-a-teacher` is now about the students already on the list, including exporting it, and
  sends anybody without an account to the new skill. `registering-new-students-as-a-teacher` says to read the
  list first when "register my class for a sitting" may mean students who already have accounts, and names both
  REST API registration skills as not its business.
- Routing: the partner skill's description and the routing table say a partner exports their student list
  there; the teacher list skill's description says entering is adding a class for exams; "the math exam" or
  "the science exam" on two connected olympiads is asked about, never picked; and `connecting-to-main-team`
  says that a "partner" in the REST API skills is an organisation holding an API account, not this role.
- A batch refused for today's registration limit is answered with a smaller batch: the answer does not say how
  many are left, and a refused call costs no change. A row problem is said to name the cell, never its value,
  rather than "never repeats what was typed" (`exam_not_eligible` carries the exam id the row named).

### Fixed

- The kit sent a new student's handle to `get_students_payment_link`, which takes application ids only.
- `already_your_student` had two different instructions in two places; there is now one: take the row out,
  enter the student's exams with `add_exams_for_students`, and on the row's other olympiads the student links
  themselves — except within 24 hours of a stopped call, when an olympiad after the row's first that is in its
  `not_registered` is sent again and attaches. A row with every one of its olympiads in `not_registered` failed
  on its first, so it is sent again whole, in the same order: sent one olympiad at a time, it would get an
  account on the first alone and `email_unavailable` on every other.
- A partner's unpaid entries were to be reported with money totals that no tool answers; they are counted.
  The teacher payments skill no longer promises "what each costs", and says instead where one exam's fee comes
  from (`find_exams_for_student`, `find_exams_for_grade`). `staying-safe-with-main-team` no longer tells the
  assistant to say what every payment link costs: a teacher's or a partner's cart link carries no amount, so
  the cart shows the total and nobody adds one up.
- A partner was described as "a teacher with a wider view"; a partner sees more students but has fewer tools.
- An eval asked for a registration to be made before the details it needed had been given; it now expects
  the assistant to ask and register nobody.
- The links to the Main Team pages for AI apps went to addresses that no longer exist; the kit now links the
  AI connections page and the agent skills page.
- The number of tools that cannot be undone (nine, not four) and the hourly change budget were out of date.
- `AGENTS.md` and `GEMINI.md` forbade accepting a teacher's username, which `link_my_teacher` needs and the
  kit sends students to; they now say it is taken from the student once, for that call, and never repeated.
