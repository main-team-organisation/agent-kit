# Working from a class list

## Contents

- The four steps
- The columns a list needs
- How matching works, and what it refuses to do
- Unmatched and ambiguous rows
- What to show the teacher before anything is entered

## The four steps

```bash
python3 scripts/roster.py normalise class.csv --out rows.json
python3 scripts/roster.py match rows.json students.json --out matched.json
python3 scripts/roster.py plan matched.json exams.json --out plan.json
python3 scripts/roster.py report plan.json answers.json --out report.md
```

The script never calls the network. Between step 2 and step 3 the tools do the work:
`main-team:list_my_students` produces `students.json`, and
`main-team:find_exams_for_student` — once per grade — produces the choices that go into
`exams.json`.

`students.json` is a plain list of what the roster tool returned:

```json
[{"student": "stu_x7k2m9p4", "name": "Ada Nwosu", "grade": "9"}]
```

`exams.json` maps a grade to the exam ids the teacher picked:

```json
{"9": ["6a1c4f2b9d07e85c3b214fa0"], "10": ["70b3d5e2a1c94f6081b2c3d4"]}
```

## The columns a list needs

A header row, a grade column, and either a single name column or both a given-name and a
family-name column. `assets/class-list-template.csv` is a working example. Common spellings of each
heading are recognised, including a few in other languages; anything else is reported rather than
guessed at.

A row is dropped, with a reason, when it has no name, or a grade that is not 1 to 12. Two rows with
the same name **and** grade are flagged: one of them is usually a duplicate, and entering both would
be entering the same student twice.

## How matching works, and what it refuses to do

A row matches a student when the folded name and the grade both agree. Folding removes accents and
punctuation, lowercases, and sorts the words, so "Ada Nwosu", "ada nwosu" and "Nwosu Ada" all agree.

It matches on **name and grade only**. There is deliberately nothing else to match on: this service
returns no username, no student code and no e-mail address, so there is no identifier in a
spreadsheet that could be used, and a column of them in the teacher's file must be left alone.

Matching never reaches outside the teacher's own list. A student who is not on it cannot be entered
from here at all — they link themselves to the teacher first, with the teacher's username, which the
student does from their own account.

## Unmatched and ambiguous rows

| Kind | What the script does | What to do |
|---|---|---|
| matched | carried into the plan | nothing |
| ambiguous — two students share the name and grade | left out, reported | ask the teacher which one, then edit the file and run again |
| unmatched — nobody on the list has that name and grade | left out, reported | usually a spelling difference, a grade the teacher has not updated, or a student not yet linked |

Never guess. Never pick "the closest one". Never enter a student because the teacher said "just do
your best with the rest" — read the unmatched rows back to them instead.

## What to show the teacher before anything is entered

One short report, before the first confirmation:

> "40 rows. 37 matched to students on your gmath list. 2 unmatched — Amara Okoye (10) and a row with
> no grade. 1 ambiguous — two students called Yuki Tanaka in grade 10. For grade 9 you chose the
> 14 March sitting, for grade 10 the 21 March sitting. That is 37 students and 37 entries, in one
> batch. Shall I go ahead?"

Then the batches, each with its own preview and confirmation. Afterwards, `roster.py report` turns
the answers into a per-row report the teacher can keep — and that report is the right place for
names, not a message to anybody else.
