#!/usr/bin/env python3
"""roster.py - turn a teacher's class list into Main Team exam entries, safely.

Four steps, each writing a file the next one reads. The script makes no network call: the MCP
tools do that, and this only prepares and checks what goes into them.

    python3 scripts/roster.py normalise class.csv --out rows.json
    python3 scripts/roster.py match rows.json students.json --out matched.json
    python3 scripts/roster.py plan matched.json exams.json --out plan.json
    python3 scripts/roster.py report plan.json answers.json --out report.md

`students.json` is written from what main-team:list_my_students returned:
    [{"student": "stu_x7k2m9p4", "name": "Ada Nwosu", "grade": "9"}, ...]
`exams.json` maps a grade to the exam ids the teacher chose from main-team:find_exams_for_student:
    {"9": ["6a1c4f2b9d07e85c3b214fa0"], "10": ["70b3d5e2a1c94f6081b2c3d4"]}

Nothing is ever guessed. A row that matches no student, or more than one, is reported and left out.
Python 3.9+, standard library only.
"""

import argparse
import csv
import json
import re
import sys
import unicodedata
from collections import defaultdict

MAX_STUDENTS_PER_CALL = 50
MAX_EXAMS_PER_STUDENT = 20
GRADES = [str(n) for n in range(1, 13)]
ALIASES = {
    "name": ["name", "full name", "student", "student name", "pupil", "ad soyad", "isim"],
    "given": ["given name", "first name", "forename", "first", "ad"],
    "family": ["family name", "last name", "surname", "last", "soyad"],
    "grade": ["grade", "year", "class", "form", "sinif", "sınıf"],
    "note": ["note", "notes", "comment", "remark"],
}


def fold(text):
    """A name reduced to what two spellings of it have in common."""
    stripped = unicodedata.normalize("NFKD", text or "")
    stripped = "".join(ch for ch in stripped if not unicodedata.combining(ch))
    stripped = re.sub(r"[^\w\s'-]", " ", stripped, flags=re.UNICODE)
    return re.sub(r"\s+", " ", stripped).strip().casefold()


def sorted_fold(text):
    """The same, with the words in order, so "Ada Nwosu" and "Nwosu Ada" agree."""
    return " ".join(sorted(fold(text).split()))


def read_table(path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            dialect = csv.excel
        return [row for row in csv.reader(handle, dialect) if any(cell.strip() for cell in row)]


def header_map(header):
    found = {}
    for index, cell in enumerate(header):
        key = fold(cell)
        for field, names in ALIASES.items():
            if key in [fold(name) for name in names] and field not in found:
                found[field] = index
    return found


def cmd_normalise(args):
    table = read_table(args.source)
    if not table:
        sys.exit("normalise: the file has no rows")
    columns = header_map(table[0])
    if "grade" not in columns or not ({"name"} & set(columns) or {"given", "family"} <= set(columns)):
        sys.exit(
            "normalise: could not find the columns. A header row needs a grade column and either a "
            "name column or both a given-name and a family-name column. See assets/class-list-template.csv."
        )
    rows, problems = [], []
    for number, raw in enumerate(table[1:], start=2):
        def cell(field):
            index = columns.get(field)
            return (raw[index].strip() if index is not None and index < len(raw) else "")

        name = cell("name") or " ".join(part for part in (cell("given"), cell("family")) if part)
        grade = re.sub(r"[^0-9]", "", cell("grade"))
        if not name:
            problems.append({"row": number, "problem": "no name"})
            continue
        if grade not in GRADES:
            problems.append({"row": number, "problem": "grade %r is not 1-12" % cell("grade")})
            continue
        rows.append({
            "row": number,
            "name": name,
            "key": sorted_fold(name),
            "grade": grade,
            "note": cell("note"),
        })
    seen = defaultdict(list)
    for row in rows:
        seen[(row["key"], row["grade"])].append(row["row"])
    for (key, grade), numbers in seen.items():
        if len(numbers) > 1:
            problems.append({"row": numbers[0], "problem": "the same name and grade is on rows %s" % numbers})
    write(args.out, {"rows": rows, "problems": problems})
    print("normalise: %d row(s) ready, %d problem(s)" % (len(rows), len(problems)))
    return 1 if problems else 0


def cmd_match(args):
    rows = load(args.rows)["rows"]
    students = load(args.students)
    if not isinstance(students, list):
        sys.exit("match: students.json is the list main-team:list_my_students returned")
    index = defaultdict(list)
    for student in students:
        handle, name = student.get("student"), student.get("name", "")
        if not handle or not str(handle).startswith("stu_"):
            sys.exit("match: every entry needs a student handle from main-team:list_my_students")
        index[(sorted_fold(name), re.sub(r"[^0-9]", "", str(student.get("grade", ""))))].append(student)
    matched, ambiguous, unmatched = [], [], []
    for row in rows:
        found = index.get((row["key"], row["grade"]), [])
        if len(found) == 1:
            matched.append({"row": row["row"], "name": row["name"], "grade": row["grade"], "student": found[0]["student"]})
        elif len(found) > 1:
            ambiguous.append({"row": row["row"], "name": row["name"], "grade": row["grade"], "count": len(found)})
        else:
            unmatched.append({"row": row["row"], "name": row["name"], "grade": row["grade"]})
    write(args.out, {"matched": matched, "ambiguous": ambiguous, "unmatched": unmatched})
    print("match: %d matched, %d ambiguous, %d unmatched" % (len(matched), len(ambiguous), len(unmatched)))
    return 1 if ambiguous or unmatched else 0


def cmd_plan(args):
    matched = load(args.matched)["matched"]
    exams = load(args.exams)
    if not isinstance(exams, dict) or not exams:
        sys.exit("plan: exams.json maps a grade to the exam ids chosen for it")
    for grade, ids in exams.items():
        if not isinstance(ids, list) or not all(re.fullmatch(r"[a-f0-9]{24}", str(one)) for one in ids):
            sys.exit("plan: grade %s must list exam ids from main-team:find_exams_for_student" % grade)
        if len(ids) > MAX_EXAMS_PER_STUDENT:
            sys.exit("plan: grade %s lists %d exams; at most %d per student" % (grade, len(ids), MAX_EXAMS_PER_STUDENT))
    items, skipped = [], []
    for one in matched:
        ids = exams.get(one["grade"])
        if not ids:
            skipped.append(one)
            continue
        items.append({"student": one["student"], "exam_ids": list(ids), "row": one["row"], "name": one["name"], "grade": one["grade"]})
    size = max(1, min(args.chunk, MAX_STUDENTS_PER_CALL))
    batches = [items[at:at + size] for at in range(0, len(items), size)]
    write(args.out, {
        "batches": [
            {"batch": number, "items": [{"student": item["student"], "exam_ids": item["exam_ids"]} for item in batch],
             "rows": [{"row": item["row"], "name": item["name"], "grade": item["grade"], "student": item["student"]} for item in batch]}
            for number, batch in enumerate(batches, start=1)
        ],
        "skipped": skipped,
    })
    print("plan: %d student(s) in %d batch(es) of at most %d; %d skipped (no exam chosen for that grade)"
          % (len(items), len(batches), size, len(skipped)))
    return 0


def cmd_report(args):
    plan = load(args.plan)
    answers = load(args.answers)
    if not isinstance(answers, list):
        answers = [answers]
    by_handle = {}
    for answer in answers:
        for result in answer.get("results", []) or []:
            by_handle.setdefault(result.get("student"), []).append(result)
    lines = ["# Class list report", ""]
    done = refused = missing = 0
    for batch in plan.get("batches", []):
        lines.append("## Batch %d" % batch["batch"])
        lines.append("")
        lines.append("| Row | Student | Grade | Outcome |")
        lines.append("|---|---|---|---|")
        for row in batch["rows"]:
            results = by_handle.get(row["student"])
            if not results:
                outcome, missing = "no answer recorded", missing + 1
            else:
                created = sum(len(one.get("created", []) or []) for one in results)
                held = sum(len(one.get("already_applied", []) or []) for one in results)
                refusals = [one.get("reason", "refused") for one in results for _ in (one.get("refused", []) or [])]
                done += created
                refused += len(refusals)
                parts = ["%d created" % created] if created else []
                if held:
                    parts.append("%d already held" % held)
                if refusals:
                    parts.append("refused: %s" % ", ".join(sorted(set(refusals))))
                outcome = "; ".join(parts) or "nothing to do"
            lines.append("| %d | %s | %s | %s |" % (row["row"], row["name"], row["grade"], outcome))
        lines.append("")
    for title, rows in (("Skipped", plan.get("skipped", [])),):
        if rows:
            lines.append("## %s" % title)
            lines.append("")
            for row in rows:
                lines.append("- row %s, %s (grade %s)" % (row.get("row"), row.get("name"), row.get("grade")))
            lines.append("")
    lines.append("%d entry/entries created, %d refused, %d student(s) with no answer recorded." % (done, refused, missing))
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print("report: written to %s" % args.out)
    return 0


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def write(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Prepare a class list for Main Team exam entries.")
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("normalise", help="clean a CSV class list")
    one.add_argument("source")
    one.add_argument("--out", default="rows.json")
    one.set_defaults(run=cmd_normalise)
    two = sub.add_parser("match", help="match rows to students already on the teacher's list")
    two.add_argument("rows")
    two.add_argument("students")
    two.add_argument("--out", default="matched.json")
    two.set_defaults(run=cmd_match)
    three = sub.add_parser("plan", help="build confirmable batches")
    three.add_argument("matched")
    three.add_argument("exams")
    three.add_argument("--out", default="plan.json")
    three.add_argument("--chunk", type=int, default=MAX_STUDENTS_PER_CALL)
    three.set_defaults(run=cmd_plan)
    four = sub.add_parser("report", help="turn the tool answers into a report")
    four.add_argument("plan")
    four.add_argument("answers")
    four.add_argument("--out", default="report.md")
    four.set_defaults(run=cmd_report)
    args = parser.parse_args()
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
