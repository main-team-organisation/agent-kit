#!/usr/bin/env python3
"""registration.py - check a teacher's registration sheet and build main-team:register_students calls.

    python3 scripts/registration.py normalise sheet.csv --olympiad gmath --exams exams.json --out registration.json
    python3 scripts/registration.py report registration.json answers.json --out report.md

No network call. The sheet is a UTF-8 CSV with the template's headers; a spreadsheet file is refused.
--olympiad: what a blank Olympiads cell means. --dates dmy|mdy: the order the teacher says every date
is in; without it a date whose day and month could swap (03/04/2013) is reported. exams.json: olympiad
-> grade -> exam name -> the id main-team:find_exams_for_grade gave. answers.json: the answers, one per
batch. Nothing is guessed or repaired, a row at an example address is refused, and a problem names a
row and a column, never the value. registration.json holds addresses and dates of birth: delete it
when done. Python 3.9+, standard library only.
"""

import argparse
import csv
import datetime
import json
import re
import sys
import unicodedata
from pathlib import Path

MAX_ROWS_PER_CALL, MAX_PAIRS_PER_CALL, MAX_OLYMPIADS_PER_ROW, MAX_EXAMS_PER_OLYMPIAD = 50, 100, 5, 20
CHANGES_PER_HOUR, NEW_ACCOUNTS_PER_DAY = 30, 2000  # a connection's changes a clock hour; a teacher's accounts a UTC day
FIELDS = ["first_name", "last_name", "email", "birth_date", "sex", "grade", "phone", "city", "school", "olympiads", "exam_ids"]
REQUIRED = FIELDS[:6]
HEADERS = {
    "first_name": ["first name", "given name", "forename", "ad"], "last_name": ["last name", "family name", "surname", "soyad"],
    "email": ["email", "e-mail", "email address", "e-posta"], "sex": ["sex", "gender", "cinsiyet"],
    "birth_date": ["date of birth", "birth date", "birthday", "dob", "dogum tarihi"],
    "grade": ["grade", "year", "class", "sinif"], "phone": ["phone", "telephone", "mobile", "telefon"],
    "city": ["city", "town", "sehir", "il"], "school": ["school", "okul"],
    "olympiads": ["olympiads", "olympiad", "olimpiyat", "olimpiyatlar"], "exam_ids": ["exams", "exam", "exam ids", "sinavlar"],
}
OLYMPIADS = {"stem": "stem", "stem olympiad": "stem", "hilingua": "hilingua", "hi-lingua": "hilingua", "neo": "neo",
             "neo science": "neo", "neoscience": "neo", "gmath": "gmath", "german math": "gmath", "germanmath": "gmath",
             "coding": "coding", "coding olympiad": "coding", "codingolympiad": "coding"}
SEX = {"f": "f", "female": "f", "girl": "f", "k": "f", "kiz": "f", "m": "m", "male": "m", "boy": "m", "e": "m", "erkek": "m"}
EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s.]+(\.[^@\s.]+)+$")
EXAMPLE_ADDRESS = re.compile(r"@(?:[^@]+\.)?example\.(?:com|org|net)$")
PHONE = re.compile(r"^[0-9+()\- ]+$")
OBJECT_ID = re.compile(r"^[a-f0-9]{24}$")
# What the platform refuses in a name: controls, line separators, < >, and @ or :// (it is printed into a mail).
CONTROL = re.compile("[\x00-\x1f\x7f-\x9f\u2028\u2029]")
NOT_IN_NAME = re.compile(r"[<>@]|://")
AMBIGUOUS = "could be day/month or month/day"
SPREADSHEET = (b"PK\x03\x04", b"\xd0\xcf\x11\xe0")


def fold(text):
    """Text reduced to what two spellings of it have in common: no accents, no case, one space."""
    text = unicodedata.normalize("NFKD", (text or "").replace("ı", "i"))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text).strip().casefold()


def read_table(path):
    """The rows of a UTF-8 CSV, split on whichever of , ; tab | the header uses most."""
    with open(path, "rb") as handle:
        if handle.read(4) in SPREADSHEET or path.lower().endswith((".xlsx", ".xls", ".xlsm", ".ods", ".numbers")):
            sys.exit('normalise: %s is a spreadsheet, not a CSV. Save it as "CSV UTF-8 (Comma delimited)" (Excel: File > '
                     'Save As; Google Sheets: File > Download > CSV) and run this on that file.' % path)
    try:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            delimiter = max(",;\t|", key=handle.readline().count)
            handle.seek(0)
            return [row for row in csv.reader(handle, delimiter=delimiter) if any(cell.strip() for cell in row)]
    except UnicodeDecodeError:
        sys.exit('normalise: %s is not UTF-8 text. Save it again as "CSV UTF-8" and run this on that file.' % path)


def birth_date(text, order):
    """(DD/MM/YYYY, None), or (None, why not). `order` is the sheet's day/month order, if the teacher said."""
    text = text.strip()
    iso = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    loose = re.fullmatch(r"(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})", text)
    if iso:
        year, month, day = (int(part) for part in iso.groups())
    elif loose:
        first, second, year = (int(part) for part in loose.groups())
        if order == "mdy":
            month, day = first, second
        elif order == "dmy" or first == second or first > 12:
            day, month = first, second
        elif second > 12:
            return None, "reads as month/day/year, not DD/MM/YYYY: ask the teacher (--dates mdy if every date is month first)"
        else:
            return None, AMBIGUOUS + ": ask the teacher which order the sheet uses, then run again with --dates dmy or --dates mdy"
    else:
        return None, "is not a date in the form DD/MM/YYYY"
    try:
        when = datetime.date(year, month, day)
    except ValueError:
        return None, "is not a real day, month and year (DD/MM/YYYY)"
    if year < 1950 or when > datetime.date.today():
        return None, "is not a date from 1950 to today"
    return when.strftime("%d/%m/%Y"), None


def exam_id(token, brands, grade, names):
    """(olympiad, id) for one Exams token, or a sentence saying why there is none."""
    olympiad, _, rest = token.partition(":")
    if rest and OLYMPIADS.get(fold(olympiad)) in brands:
        brands, token = [OLYMPIADS[fold(olympiad)]], rest.strip()
    if OBJECT_ID.fullmatch(token.lower()):
        return (brands[0], token.lower()) if len(brands) == 1 else "an exam id without its olympiad; write olympiad: id"
    found = [(brand, names.get(brand, {}).get(grade, {}).get(fold(token))) for brand in brands]
    found = [one for one in found if one[1]]
    if len(found) == 1:
        return found[0]
    return "an exam two of the row's olympiads hold; write olympiad: exam" if found else "an exam that exams.json does not map for this grade on the row's olympiads"


def cmd_normalise(args):
    table = read_table(args.source)
    if not table:
        sys.exit("normalise: the file has no rows")
    columns = {}
    for index, header in enumerate(table[0]):
        for field in [field for field, names in HEADERS.items() if fold(header) in names]:
            columns.setdefault(field, index)
    lacking = [field for field in REQUIRED if field not in columns]
    if lacking:
        sys.exit("normalise: no column for %s. Use the headers of assets/student-registration-template.csv." % ", ".join(lacking))
    exams = load(args.exams) if args.exams else {}
    names = {OLYMPIADS.get(fold(brand), brand): {grade: {fold(name): one for name, one in mapping.items()}
                                                 for grade, mapping in grades.items()} for brand, grades in exams.items()}
    header = {field: table[0][index] for field, index in columns.items()}
    rows, problems, seen = [], [], {}
    for number, raw in enumerate(table[1:], start=2):
        def cell(field):
            index = columns.get(field)
            return raw[index].strip() if index is not None and index < len(raw) else ""
        found = []

        def problem(field, text):
            if text:
                found.append({"row": number, "column": header.get(field, field), "problem": text})

        student = {}
        for field in ("first_name", "last_name"):
            value = re.sub(r" +", " ", cell(field))
            if not value or len(value) > 60 or NOT_IN_NAME.search(value) or CONTROL.search(value):
                problem(field, "needs 1 to 60 characters, without < > @ :// or a line break")
            student[field] = value
        email = cell("email").lower()
        if not EMAIL.fullmatch(email) or len(email) > 254:
            problem("email", "is not an e-mail address; ask the teacher for the student's own")
        elif EXAMPLE_ADDRESS.search(email):
            problem("email", "is an example address: the template's example rows are not students; delete them")
        elif email in seen:
            problem("email", "is the same address as row %d; every student needs their own" % seen[email])
        seen.setdefault(email, number)
        student["email"] = email
        student["birth_date"], why = birth_date(cell("birth_date"), args.dates)
        problem("birth_date", why)
        student["sex"] = SEX.get(fold(cell("sex")), "")
        if not student["sex"]:
            problem("sex", "is F or M")
        digits = re.findall(r"[0-9]+", cell("grade"))  # "Year 7" is 7; "1/2" and "1-2" are two grades, not 12
        student["grade"] = grade = str(int(digits[0])) if len(digits) == 1 and 1 <= int(digits[0]) <= 12 else ""
        if not grade:
            problem("grade", "is 1 to 12; one grade per student")
        if cell("phone") and not PHONE.fullmatch(cell("phone")):
            problem("phone", "takes only digits, + ( ) - and spaces")
        for field, limit in (("phone", 30), ("city", 80), ("school", 120)):
            value = cell(field)
            if len(value) > limit:
                problem(field, "is longer than %d characters" % limit)
            elif field != "phone" and (CONTROL.search(value) or re.search(r"[<>]", value)):
                problem(field, "takes no < > or line break")
            elif field == "school" and OBJECT_ID.fullmatch(value.lower()):
                problem(field, "looks like an id, not a school's name")
            elif value:
                student[field] = value
        if cell("city") and not cell("school"):
            problem("school", "is needed when the city is filled")
        named = [part.strip() for part in cell("olympiads").split(";") if part.strip()]
        brands = []
        for name in named or ([args.olympiad] if args.olympiad else []):
            brand = OLYMPIADS.get(fold(name))
            if not brand:
                problem("olympiads", "names an olympiad that is not stem, hilingua, neo, gmath or coding")
            elif brand in brands:
                problem("olympiads", "names the same olympiad twice")
            else:
                brands.append(brand)
        if not named and not args.olympiad:
            problem("olympiads", "is blank, and no --olympiad says which olympiad that means")
        if len(brands) > MAX_OLYMPIADS_PER_ROW:
            problem("olympiads", "names more than %d olympiads" % MAX_OLYMPIADS_PER_ROW)
        ids = {brand: [] for brand in brands}
        for token in [part.strip() for part in cell("exam_ids").split(";") if part.strip()]:
            answer = exam_id(token, brands, grade, names) if brands else "has no olympiad to go to"
            if isinstance(answer, str):
                problem("exam_ids", "names " + answer if answer.startswith("an") else answer)
            elif answer[1] not in ids[answer[0]]:
                ids[answer[0]].append(answer[1])
        if any(len(one) > MAX_EXAMS_PER_OLYMPIAD for one in ids.values()):
            problem("exam_ids", "lists more than %d exams on one olympiad" % MAX_EXAMS_PER_OLYMPIAD)
        student["olympiads"] = [dict(brand=brand, **({"exam_ids": ids[brand]} if ids[brand] else {})) for brand in brands]
        problems.extend(found)
        if not found:
            rows.append({"row": number, "student": student})

    batches, batch, pairs = [], [], 0
    size = max(1, min(args.chunk, MAX_ROWS_PER_CALL))
    for one in rows if not problems else []:
        count = len(one["student"]["olympiads"])
        if batch and (len(batch) >= size or pairs + count > MAX_PAIRS_PER_CALL):
            batches.append(batch)
            batch, pairs = [], 0
        batch.append(one)
        pairs += count
    batches += [batch] if batch else []
    plan = {"problems": problems, "batches": [
        {"batch": n, "rows": [one["row"] for one in batch], "students": [one["student"] for one in batch]}
        for n, batch in enumerate(batches, start=1)]}
    Path(args.out).write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if problems:
        print("normalise: %d problem(s) on %d row(s); nothing is ready to send until they are corrected"
              % (len(problems), len({one["row"] for one in problems})))
        either = sum(1 for one in problems if one["problem"].startswith(AMBIGUOUS))
        if either:
            print("normalise: %d date(s) could be read either way; ask the teacher once which order the sheet uses, "
                  "then run again with --dates dmy (or --dates mdy)" % either)
        return 1
    print("normalise: %d student(s) in %d batch(es) of at most %d rows and %d pairs. %s holds their addresses and dates "
          "of birth: never paste it, and delete it when done" % (len(rows), len(batches), size, MAX_PAIRS_PER_CALL, args.out))
    hours, days = -(-2 * len(batches) // CHANGES_PER_HOUR), -(-len(rows) // NEW_ACCOUNTS_PER_DAY)
    if hours > 1 or days > 1:
        print("normalise: at two changes a batch and %d a clock hour these need %d hour(s) or more, and at %d new accounts "
              "a UTC day, %d day(s): send them in turn, never faster" % (CHANGES_PER_HOUR, hours, NEW_ACCOUNTS_PER_DAY, days))
    return 0


def cmd_report(args):
    plan = load(args.plan)
    answers = load(args.answers)
    answers = answers if isinstance(answers, list) else [answers]
    lines, registered = ["# Registration report", ""], 0
    for batch, answer in zip(plan.get("batches", []), answers):
        sheet = batch["rows"]

        def line(index):
            return sheet[index] if isinstance(index, int) and 0 <= index < len(sheet) else "?"
        lines += ["## Batch %d: %s" % (batch["batch"], answer.get("status", "no answer")), ""]
        for one in answer.get("problems", []) or []:
            lines.append("- sheet row %s, %s%s: %s" % (line(one.get("row")), one.get("field") or "the row", " on "
                                                      + one["brand"] if one.get("brand") else "", one.get("code")))
        for one in answer.get("students", []) or []:
            for olympiad in one.get("olympiads", []) or []:
                exams = olympiad.get("exams") or {}
                refused = exams.get("refused")
                lines.append("- sheet row %s: registered on %s%s; %d exam(s) entered%s" % (
                    line(one.get("row")), olympiad.get("brand"), " (linked)" if olympiad.get("resumed") else "",
                    len(exams.get("created") or []), "; exams refused: %s" % refused.get("reason") if refused else ""))
        registered += len(answer.get("students", []) or [])
        for one in answer.get("not_registered", []) or []:
            lines.append("- sheet row %s: not registered on %s (%s)" % (line(one.get("row")), one.get("brand"), one.get("reason")))
        if answer.get("stopped_at") is not None:
            lines.append("- stopped before sheet row %s; send the rows from there again" % line(answer["stopped_at"]))
        lines.append("")
    lines.append("%d student(s) registered. Each one is e-mailed their username and a password, and confirms the address at "
                 "their first sign-in. Every exam entry is unpaid until it is paid in the panel." % registered)
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("report: written to %s. Delete %s and %s now: they hold the addresses, dates of birth and handles"
          % (args.out, args.plan, args.answers))
    return 0


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Prepare a registration sheet for Main Team.")
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("normalise", help="check the sheet and build batches")
    one.add_argument("source")
    one.add_argument("--olympiad", choices=sorted(set(OLYMPIADS.values())), help="the olympiad a blank Olympiads cell means")
    one.add_argument("--exams", help="olympiad -> grade -> exam name -> exam id, from find_exams_for_grade")
    one.add_argument("--dates", choices=["dmy", "mdy"], help="the order the teacher says every date is written in")
    one.add_argument("--out", default="registration.json")
    one.add_argument("--chunk", type=int, default=MAX_ROWS_PER_CALL)
    one.set_defaults(run=cmd_normalise)
    two = sub.add_parser("report", help="turn the answers into a report by sheet row")
    for name in ("plan", "answers"):
        two.add_argument(name)
    two.add_argument("--out", default="report.md")
    two.set_defaults(run=cmd_report)
    args = parser.parse_args()
    return args.run(args)


if __name__ == "__main__":
    sys.exit(main())
