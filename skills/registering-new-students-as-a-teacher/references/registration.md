# Registering new students

## Contents

- Who can be registered, and who cannot
- The sheet
- From the sheet to the calls
- The limits
- The two-call shape
- Reading `needs_changes`
- Reading the result
- Paying for the new entries
- After a stop or a timeout
- When it is done
- What never happens

## Who can be registered, and who cannot

A teacher registers **new** students of their own, on one olympiad or on up to five at once. Each
student gets one Main Team account, linked to the teacher on every olympiad the row names, and can
be entered for exams on each in the same step.

- **Only a teacher.** `main-team:register_students` is a teacher's tool. A partner's connection does
  not have it, on any olympiad: a partner's students are registered by their own teacher.
- **Every olympiad a row names must be one this connection works on as a teacher.** Any other is
  the problem `olympiad_not_allowed`; leave it out of the row, never swap in another.
- **A student who already has an account is not registered again.** They link themselves to the
  teacher from their own account, with the student tool `link_my_teacher` and the teacher's
  username. The answer marks such a row `email_unavailable` and never says whose the address is.
- **A student already on this teacher's list** comes back as `already_your_student`, with their
  `student` handle on that olympiad. The rule is one: **take the row out**. Enter their exams there
  with `main-team:add_exams_for_students`, using that handle. On any other olympiad of the row the
  student links themselves with `link_my_teacher`; sent again, the row would answer
  `email_unavailable` there. The one exception is a row sent again within 24 hours of a stopped call
  (below): an olympiad after the row's first that the stopped call listed in `not_registered` is
  sent again, without the olympiads that answered `already_your_student`, and is attached.
- The country is always the teacher's. City and school are the teacher's unless a row names others;
  a city or a school the platform does not know yet is added. A teacher whose own profile has no
  country cannot register students: the call answers `not_allowed_here`.

## The sheet

`main-team:get_student_registration_template` answers the sheet: `columns` in order, each with its
header `name`, the argument `field` it fills, whether it is `required`, its `format`, an `example`
and `notes`; two invented `example_rows`; the `rules`; and `max_rows_per_call`, which is 50.
`assets/student-registration-template.csv` is the same sheet as a file.

Offer it when the teacher asks for a template or which columns to use. Write it out with exactly
these headers. **The example rows are not students**: delete them from anything sent. Their
addresses are at `example.com`, and the script refuses any row at an example address, so a
template filled in below its examples is caught before anybody is registered.

| Header | Argument | Required | Format |
|---|---|---|---|
| First name | `first_name` | yes | 1 to 60 characters, without `<`, `>`, `@`, `://` or a line break |
| Last name | `last_name` | yes | the same |
| Email | `email` | yes | the student's own address; one per student |
| Date of birth | `birth_date` | yes | DD/MM/YYYY, from 1950 to today |
| Sex | `sex` | yes | F or M, sent as `f` or `m` |
| Grade | `grade` | yes | 1 to 12, one grade per student: "Year 7" is 7, "1/2" is refused |
| Phone | `phone` | no | up to 30 characters, digits and + ( ) - and spaces |
| City | `city` | no | blank means the teacher's city; no `<`, `>` or line break |
| School | `school` | no | blank means the teacher's school; needed when City is filled; a name, not an id |
| Olympiads | `olympiads` | no | slugs or names separated by `;`; blank means the olympiad the teacher works on |
| Exams | `exam_ids` | no | exams on those olympiads for that grade, separated by `;` |

**An Excel file is converted first.** The script reads a UTF-8 CSV and refuses an `.xlsx`, `.xls`,
`.ods` or `.numbers` file, and a CSV in any other encoding, with the reason. Ask the teacher to save
the sheet as "CSV UTF-8 (Comma delimited)" (Excel: File, Save As; Google Sheets: File, Download,
CSV), or convert it yourself where you can read the workbook — one sheet, the header row first,
every cell as text, the dates exactly as typed rather than as the spreadsheet's date numbers.
Never retype the cells by hand.

## From the sheet to the calls

1. **Read the sheet locally.** `scripts/registration.py normalise` checks every cell against the
   format above and repairs nothing into what the teacher did not write. A sex it cannot read, a
   grade cell holding two numbers (1/2, 1-2), an olympiad it does not know, a second row with the
   same address and an example row are reported by sheet row and column. `--olympiad` names the olympiad a blank Olympiads cell means. It makes
   no network call.
2. **Settle the dates.** A date such as 03/04/2013 could be 3 April or 4 March. The script reads
   such a date neither way: it reports it until the teacher says which order the whole sheet uses,
   and then runs with `--dates dmy` (day first, the template's order) or `--dates mdy`. A date that
   can only be month first, such as 03/14/2013, is reported too: the template is day first. Ask the
   teacher once for the whole sheet, never per row, and never decide it yourself.
3. **Turn exam names into ids**, once per grade and olympiad on the sheet:
   `main-team:find_exams_for_grade` with that `brand` and `grade`. Show the teacher the options
   with dates and fees, and write the names they chose, with the `exam_id` each one has, into
   `exams.json`, by olympiad and grade:

   ```json
   {"gmath": {"7": {"Mathematics": "6a1c4f2b9d07e85c3b214fa0"}}}
   ```

   An Exams cell may name `olympiad: exam` where two of the row's olympiads hold an exam of the same
   name, or hold the ids themselves when the row names one olympiad. A name the file does not map is
   reported, never guessed.
4. **Run the script again** with `--exams exams.json` until it reports no problem. It writes the
   rows as `register_students` arguments, in batches of at most 50 rows and 100 student-olympiad
   pairs, and says when the batches need more than one hour's changes or more than one day's new
   accounts (below).
5. **Call** `main-team:register_students` once per batch.

## The limits

| Limit | What it means |
|---|---|
| 50 rows, 100 student-olympiad pairs, 5 olympiads a row, 20 exams an olympiad | one call; the script batches to them |
| 2000 new accounts a teacher a day | counted per UTC day, across every connection the teacher holds; linking a new student to a further olympiad of the same row does not count |
| 30 changes an hour for this connection | the first call of a batch and its confirmed call are two, and each `needs_changes` round is one more |
| about 25 seconds of rows a call | a long call stops in time to answer and says where (below) |

**The daily limit is checked before anything is registered.** A batch with more rows than are left
today answers `rate_limited` and registers nobody. This is the one place where sending **fewer rows**
is the answer rather than waiting. The answer does not say how many are left, but a refused call
changed nothing and costs no change from the hour's budget, so a smaller batch — half, say — spends
calls and no changes; send the rest tomorrow. Every other `rate_limited` means wait, and splitting
the work into more calls only spends the hour sooner.

**The hourly budget is the tighter one in practice.** At two changes a batch, one connection
registers at most fifteen batches of fifty — 750 students — in an hour, and fewer for every round
spent on `needs_changes`. So correct the rows locally first rather than sending them to find out,
and send full batches.

A call can also be refused as too big for one call — more than 100 student-olympiad pairs, or rows
too long for the platform to check at once: `not_allowed_here`, and the answer says which. Send
fewer rows a call; that is not a retry of the same call.

## The two-call shape

```jsonc
// 1. every row is checked on every olympiad; nothing is registered
{ "students": [ { "first_name": "Maya", "last_name": "Okafor",
    "email": "maya.okafor@example.com", "birth_date": "14/03/2013", "sex": "f", "grade": "7",
    "olympiads": [ { "brand": "gmath", "exam_ids": ["6a1c4f2b9d07e85c3b214fa0"] },
                   { "brand": "stem" } ] } ] }
//  -> needs_changes, or confirmation_required with a summary of counts and a confirmation value

// 2. after a clear yes — the same students, plus the value
{ "students": [ ... exactly the same ... ], "confirmation": "cfm_example1" }
```

The account is made on the first olympiad of a row and linked to the teacher on each of the others.
The summary says how many students, how many rows per grade, how many students and exam entries per
olympiad, and that each student gets their username and a generated password by e-mail and confirms
the address the first time they sign in. Show it, and wait for a clear yes. The confirmed call
checks every row again, so a row that became a problem in between stops it before anybody is
registered.

In an app that can ask the person itself, the question may come from the app instead of a summary
and a confirmation value; a "no" there registers nobody.

## Reading `needs_changes`

`problems` lists each problem with the `row` (its place in `students`, counting from 0), the
`field` to correct, the `code`, and the `brand` of the olympiad that found it; `problem_count`
counts them. **Nobody is registered while any row has one.** A problem names the cell, never its
value — only `exam_not_eligible` carries the `exam_id` the row named — so read the row from the
sheet.

- `already_your_student` carries `student`; `duplicate_in_request` carries `duplicate_of`, the
  earlier row; `exam_not_eligible` carries `exam_id`.
- `duplicate_in_request`: usually one row is a copy. Siblings who share a parent's address are two
  students, and each needs an address of their own: it is where their own password goes.
- `email_unavailable`: never guess another address, and never try variants to see which one works.
  Ask the teacher; if the student already has an account, they link themselves instead.
- Every code, and what to do about it: the "Row problems" table of the skill
  `staying-safe-with-main-team`, in its error reference.

Correct the sheet with the teacher, run the script again, and send the whole batch again.

## Reading the result

`status` is `done`, or `stopped` with `stopped_at`. `registered` counts the students and
`exam_entries` the entries made. Per student, `students` gives the `row`, the name, the `grade` and
`olympiads`: for each, the `brand`, the `student` handle there, whether it was `resumed`, and
`exams` with the exam ids `created`, those `already_applied` and whether the exams were `refused`
with a `reason`. `not_registered` lists each olympiad of a row that was not registered, with its
`brand` and `reason`: every olympiad of a row whose account could not be made, or one further
olympiad that refused.

Report it by name and in counts: "28 registered, 27 of them entered for the March sitting on gmath,
12 on stem as well; Ada's stem entry was refused; one address was already in use." Never read out
an address. Say that each student's e-mail comes from the first olympiad of their row, so the
students know which one to look for.

## Paying for the new entries

Every exam entry made here is an unpaid application, and nothing here charges anything. The answer
carries exam ids, **not application ids**, and the payment link takes application ids only, so read
them first:

1. `main-team:list_my_students` on that olympiad, with the `grade`, or `main-team:get_student`
   with each new `student` handle: each entry carries its `application_id` and `paid`.
2. `main-team:get_students_payment_link` with those `application_ids`: up to **twenty** in one
   link, and on `coding` **one** per link. Build as many links as that takes, per olympiad.
3. Hand the links over with what they cover; the cart shows what is due. Never say a fee is paid
   until a read shows `paid` true. The rest is the skill `handling-payments-and-invoices-as-a-teacher`.

## After a stop or a timeout

**Do not simply send the same batch again.** A call stops when the platform stops answering, when
changes are switched off, or when it runs out of time, and says so. Send only what is left, reading
`not_registered` row by row against the olympiads each row named:

- **The rows from `stopped_at` on** were not tried: send them as they were.
- **A row with every one of its olympiads in `not_registered`** failed on its first olympiad, so its
  account was not made, or not finished. Send that row again **whole**, with the same olympiads in
  the same order. Never send its olympiads one at a time: the first, sent alone, makes an account
  on that olympiad only, and every other one then answers `email_unavailable`.
- **A row with only some of its olympiads in `not_registered`** has its account, made on the first.
  Send only those further olympiads, now as the row's only ones.

**That works for 24 hours.** For a day after this teacher's call made a student's account, the
platform attaches it to an olympiad the same row named, when that row is sent again — the answer
marks it `resumed` — so nobody is ever registered twice. After 24 hours the same row answers
`email_unavailable` instead, and the student links themselves to the teacher there with
`link_my_teacher`. So resume the same day.

A row sent again on an olympiad it already went through answers `already_your_student`, which costs
a round: take that olympiad out, enter its exams with `main-team:add_exams_for_students`, and send
the rest of the row. For a row sent again whole, that means its account was made after all. After a
timeout with no answer at all, read `main-team:list_my_students` on each olympiad with the `grade`
first and take out the students already there.

## When it is done

`registration.json` holds the sheet's addresses, dates of birth and phone numbers, and the saved
answers hold the new students' names and handles. They stay on the teacher's machine, are never
pasted into the chat or another tool, and are **deleted once the report is written**, as the script
says. `report.md` names sheet rows and olympiads only and is the teacher's to keep. The teacher's own
sheet stays where they put it.

## What never happens

- No username, no password, no address and no date of birth ever comes back. The platform e-mails
  each new student their username and a password and the student confirms the address at their
  first sign-in; neither the teacher nor the assistant sees the username or the password.
- No draft students: every student registered here has a full account.
- There is no tool to undo a registration. A wrong row is a real account with a real e-mail sent,
  which is why every row is checked before the first call.
- Never collect a student's password, and never ask for one to "check" a registration.
