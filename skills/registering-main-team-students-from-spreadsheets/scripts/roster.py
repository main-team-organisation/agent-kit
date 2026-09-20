#!/usr/bin/env python3
"""Turn a class list into Main Team bulk registration requests. Python 3.8+, standard library only.

  roster.py normalise LIST [--out rows.json] [--problems problems.json] [--sheet NAME] [--dates dmy|mdy]
  roster.py build rows.json [--countries c.json] [--platforms stem,hilingua] [--client-reference NAME]
                            [--out-dir tasks] [--max 1000]
  roster.py fix TASK.json REJECTION.json [--out rejected.csv]
  roster.py report rows.json IMPORT.json [IMPORT.json ...] [--out report.csv]

LIST is a .csv, .tsv or .xlsx file. Nothing here talks to a server: it reads and writes local files.
"""
import argparse, csv, datetime, io, json, os, re, sys, unicodedata, zipfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ALIASES = json.load(open(os.path.join(HERE, '..', 'assets', 'column-aliases.json'), encoding='utf-8'))
REQUIRED = ['first_name', 'last_name', 'birth', 'sex', 'email', 'country', 'city', 'school', 'grade']
API_NAMES = {'first_name': 'firstName', 'last_name': 'lastName', 'birth': 'birth', 'sex': 'sex',
             'email': 'email', 'phone': 'phone', 'country': 'country', 'city': 'city',
             'school': 'school', 'grade': 'grade', 'platforms': 'activatedPlatformsThisSeason'}
PLATFORMS = ['common', 'stem', 'hilingua', 'neo', 'gmath', 'coding']
# The contract: a batch is 30 to 1000 rows, and a row names at most 6 platforms.
MIN_ROWS, MAX_ROWS, MAX_PLATFORMS = 30, 1000, 6
NOTES_ONLY = ('full_name_split', 'password_column_ignored')  # reported, but they never block a row
# ZipFile never inflates an .xlsx part past its declared size, so MAX_PART stops a zip bomb.
MAX_PART, MAX_COLUMN = 64 * 1024 * 1024, 16384
OBJECT_ID = re.compile(r'^[0-9a-fA-F]{24}$')
EMAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
FOLD = str.maketrans({'ı': 'i', 'ş': 's', 'ğ': 'g', 'ç': 'c', 'ö': 'o', 'ü': 'u', 'ł': 'l', 'ß': 'ss'})
M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

def key(text):
    """A header or value compared loosely: lower case, accents and punctuation removed."""
    text = unicodedata.normalize('NFKD', str(text).lower().translate(FOLD))
    return ''.join(c for c in text if c.isalnum() and not unicodedata.combining(c))

def fail(message): sys.exit(f'roster.py: {message}')

def read_xlsx(path, sheet):
    with zipfile.ZipFile(path) as z:
        part = lambda name: z.read(name) if z.getinfo(name).file_size <= MAX_PART else fail(f'{name} is too large')
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            for si in ET.fromstring(part('xl/sharedStrings.xml')).iter(M + 'si'):
                shared.append(''.join(t.text or '' for t in si.iter(M + 't')))
        workbook = ET.fromstring(part('xl/workbook.xml'))
        targets = {r.get('Id'): r.get('Target') for r in ET.fromstring(part('xl/_rels/workbook.xml.rels'))}
        sheets = list(workbook.iter(M + 'sheet'))
        chosen = next((s for s in sheets if sheet in (None, s.get('name'))), None)
        if chosen is None:  # the workbook names its sheets; pick one with --sheet
            fail(f'no sheet named {sheet!r}; it has {", ".join(s.get("name") for s in sheets)}')
        target = targets[chosen.get(R + 'id')]
        target = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        rows = []
        for position, row in enumerate(ET.fromstring(part(target)).iter(M + 'row'), start=1):
            cells, column = {}, 0
            for c in row.iter(M + 'c'):
                ref = re.match(r'([A-Z]{1,3})\d', c.get('r') or '')  # a cell without one follows the last
                column = sum((ord(ch) - 64) * 26 ** i for i, ch in enumerate(reversed(ref[1]))) if ref else column + 1
                if column > MAX_COLUMN:
                    continue
                v, kind = c.find(M + 'v'), c.get('t')
                inline = ''.join(t.text or '' for t in c.iter(M + 't'))
                plain = v.text if v is not None and v.text is not None else ''
                cells[column - 1] = shared[int(v.text)] if kind == 's' else inline if kind == 'inlineStr' else plain
            rows.append((int(row.get('r') or position),
                         [cells.get(i, '') for i in range(max(cells) + 1 if cells else 0)]))
        return rows, chosen.get('name')

def read_table(path, sheet):
    if path.lower().endswith('.xlsx'):
        return read_xlsx(path, sheet)
    raw = open(path, 'rb').read()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252')
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=',;\t')
    except csv.Error:
        dialect = csv.excel_tab if path.lower().endswith('.tsv') else csv.excel
    return [(i + 1, row) for i, row in enumerate(csv.reader(io.StringIO(text), dialect))], None

def map_headers(header):
    lookup = {key(alias): field for field, aliases in ALIASES['fields'].items() for alias in aliases + [field]}
    mapping, unmapped = {}, []
    for index, title in enumerate(header):
        field = lookup.get(key(title))
        if field and field not in mapping.values():
            mapping[index] = field
        elif str(title).strip():
            unmapped.append(str(title).strip())
    fields = set(mapping.values())
    if 'full_name' in fields and 'last_name' in fields and 'first_name' not in fields:
        mapping = {i: ('first_name' if f == 'full_name' else f) for i, f in mapping.items()}
    return mapping, unmapped

def clean(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip()

def parse_birth(value, order):
    value = clean(value)
    if re.fullmatch(r'\d+(\.0+)?', value) and 10000 < float(value) < 80000:  # an Excel date; 2012 is a year
        return (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(float(value)))).strftime('%d/%m/%Y')
    parts = re.split(r'[./\-\s]+', value.split('T')[0].split(' ')[0] if ':' in value else value)
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return None
    year, month, day = parts if len(parts[0]) == 4 else \
        (parts[2], parts[0], parts[1]) if order == 'mdy' else (parts[2], parts[1], parts[0])
    try:
        return datetime.date(int(year), int(month), int(day)).strftime('%d/%m/%Y')
    except ValueError:
        return None

def parse_row(raw, dates, sex_lookup):
    """One spreadsheet line as the fields of a request row, and everything wrong with it."""
    fields, notes = {}, []
    if raw.get('full_name') and not (raw.get('first_name') or raw.get('last_name')):
        first, _, last = raw['full_name'].rpartition(' ')
        raw['first_name'], raw['last_name'] = (first, last) if first else (last, '')
        notes.append('full_name_split')
    for field in ('first_name', 'last_name', 'city', 'school', 'phone'):
        if raw.get(field):
            fields[field] = raw[field]
    notes += ['password_column_ignored'] if raw.get('password') else []  # the operation refuses the field
    if raw.get('email'):
        fields['email'] = raw['email'].lower()
        if not EMAIL.match(fields['email']):
            notes.append('email_invalid')
    if raw.get('birth'):
        fields['birth'] = parse_birth(raw['birth'], dates)
        if not fields['birth']:
            notes.append('birth_unreadable')
            del fields['birth']
    if raw.get('sex'):
        if key(raw['sex']) in sex_lookup:
            fields['sex'] = sex_lookup[key(raw['sex'])]
        else:
            notes.append('sex_unreadable')
    if raw.get('grade'):
        digits = re.search(r'\d+', raw['grade'])
        if OBJECT_ID.match(raw['grade']):  # an id is accepted as well as the name 1 to 12
            fields['grade'] = raw['grade'].lower()
        elif digits and 1 <= int(digits.group()) <= 12:
            fields['grade'] = str(int(digits.group()))
        else:
            notes.append('grade_unreadable')
    if raw.get('country'):
        named = not OBJECT_ID.match(raw['country'])
        fields['country_name' if named else 'country'] = raw['country'] if named else raw['country'].lower()
    if raw.get('platforms'):
        wanted = [key(p) for p in re.split(r'[,;/\n]+', raw['platforms']) if clean(p)]
        fields['platforms'] = [p for p in wanted if p in PLATFORMS]
        notes += ['platform_unknown'] if len(fields['platforms']) != len(wanted) else []
        notes += ['too_many_platforms'] if len(fields['platforms']) > MAX_PLATFORMS else []
    return fields, notes

def normalise(args):
    table, sheet = read_table(args.list, args.sheet)
    table = [(n, row) for n, row in table if any(clean(c) for c in row)]
    if not table: fail('the list is empty')
    mapping, unmapped = map_headers(table[0][1])
    sex_lookup = {key(v): s for s, values in ALIASES['sex_values'].items() for v in values}
    rows, problems, seen = [], [], {}
    for number, cells in table[1:]:
        raw = {field: clean(cells[i]) if i < len(cells) else '' for i, field in mapping.items()}
        fields, notes = parse_row(raw, args.dates, sex_lookup)
        if fields.get('email') and 'email_invalid' not in notes:
            if fields['email'] in seen:
                notes.append(f'email_duplicate_of_row_{seen[fields["email"]]}')
            else:
                seen[fields['email']] = number
        notes += [f'{f}_missing' for f in REQUIRED if not fields.get(f) and not (f == 'country' and fields.get('country_name'))]
        ref = (f'{sheet}!{number}' if sheet else f'row {number}')[:64]
        rows.append({'row': number, 'external_ref': ref, 'fields': fields, 'problems': notes})
        problems += [{'row': number, 'external_ref': ref, 'problem': n} for n in notes if n != 'full_name_split']
    result = {'source': os.path.basename(args.list), 'sheet': sheet,
              'columns': {str(i): f for i, f in mapping.items()}, 'unmapped_columns': unmapped, 'rows': rows}
    json.dump(result, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(problems, open(args.problems, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    blocked = len({p['row'] for p in problems})
    print(f'{len(rows)} rows, {len(rows) - blocked} ready, {blocked} with problems -> {args.out}, {args.problems}')
    if unmapped:
        print('columns not used: ' + ', '.join(unmapped))

def sizes(total, most):  # as few requests as possible, all alike, so none falls under the minimum
    n = -(-total // most) if total else 0
    return [total // n + (1 if i < total % n else 0) for i in range(n)]

def build(args):
    data = json.load(open(args.rows, encoding='utf-8'))
    countries = {key(n): v for n, v in json.load(open(args.countries, encoding='utf-8')).items()} \
        if args.countries else {}
    default = [p for p in (clean(x) for x in (args.platforms or '').split(',')) if p]
    ready, skipped = [], []
    for row in data['rows']:
        fields = dict(row['fields'])
        problems = [p for p in row['problems'] if p not in NOTES_ONLY]
        if 'country' not in fields and fields.get('country_name'):
            fields['country'] = countries.get(key(fields['country_name']))
            if not fields['country']:
                problems.append('country_not_in_countries_map')
        if default and not fields.get('platforms'):
            fields['platforms'] = default
        if problems:
            skipped.append(row['external_ref'])
            continue
        item = {API_NAMES[k]: v for k, v in fields.items() if k in API_NAMES}
        item['externalRef'] = row['external_ref']
        ready.append(item)
    if len(ready) < MIN_ROWS:
        print(f'{len(ready)} rows ready: fewer than {MIN_ROWS}, which bulk registration refuses. Register these '
              'one at a time with registerStudent (POST /v1/student).')
    os.makedirs(args.out_dir, exist_ok=True)
    start, written = 0, []
    for number, size in enumerate(sizes(len(ready), min(args.max, MAX_ROWS)), start=1):
        body = {'students': ready[start:start + size]}
        if args.client_reference:
            body['clientReference'] = f'{args.client_reference}-{number:03d}'[:64]
        json.dump(body, open(os.path.join(args.out_dir, f'task-{number:03d}.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=2)
        written.append(f'task-{number:03d}.json ({size})')
        start += size
    print(f'{len(ready)} rows in {len(written)} request(s) -> {", ".join(written)}' if written else 'nothing to send')
    if skipped:
        print(f'{len(skipped)} rows left out (fix them first): ' + ', '.join(skipped))

def write_csv(path, header, rows):
    # A leading quote makes a spreadsheet app show the value as text, never run it as a formula.
    safe = lambda v: "'" + str(v) if str(v or '')[:1] in ('=', '+', '-', '@', '\t', '\r') else str(v or '')
    with open(path, 'w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows([safe(v) for v in row] for row in rows)

def fix(args):
    students = json.load(open(args.task, encoding='utf-8')).get('students', [])
    details = json.load(open(args.rejection, encoding='utf-8')).get('error', {}).get('details', {})
    out = []
    for bad in details.get('rows', []):
        at = bad.get('row')
        sent = students[at] if isinstance(at, int) and 0 <= at < len(students) else {}
        out.append([sent.get('externalRef', at), bad.get('code', ''), bad.get('field') or '', sent.get('email', ''),
                    bad.get('message', ''), bad.get('studentId') or bad.get('duplicateOf') or ''])
    write_csv(args.out, ['row', 'code', 'field', 'email', 'message', 'other'], out)
    print(f'{details.get("rejected", len(out))} of {details.get("total", len(students))} rows refused, '
          f'{len(out)} listed -> {args.out}')
    if details.get('truncated'):
        print('the list was shortened: fix these, send the batch again, and read the next answer')

def report(args):
    data = json.load(open(args.rows, encoding='utf-8'))
    outcome, failures = {}, []
    for path in args.imports:
        job = json.load(open(path, encoding='utf-8'))
        job = job.get('data', job)
        if job.get('failure'):
            failures.append(f'{os.path.basename(path)}: {job["failure"].get("code")} {job["failure"].get("message", "")}')
        outcome.update({r['externalRef']: r for r in job.get('students', []) if r.get('externalRef')})
    rows = []
    for row in data['rows']:
        got, notes = outcome.get(row['external_ref'], {}), [p for p in row['problems'] if p not in NOTES_ONLY]
        error = got.get('error') or {}
        rows.append((row['external_ref'], row['fields'].get('first_name', ''),
                     row['fields'].get('last_name', ''),
                     got.get('status') or ('not_sent: ' + ', '.join(notes) if notes else 'not_sent'),
                     got.get('studentId', ''),
                     f'{error.get("code", "")} {error.get("message", "")}'.strip()))
    write_csv(args.out, ['row', 'first_name', 'last_name', 'status', 'student_id', 'details'], rows)
    print(f'{len(data["rows"])} rows, {len(outcome)} with a result -> {args.out}')
    for failure in failures:
        print(failure)

COMMANDS = {
    'normalise': [('list', {}), ('--out', {'default': 'rows.json'}), ('--problems', {'default': 'problems.json'}),
                  ('--sheet', {}), ('--dates', {'choices': ['dmy', 'mdy'], 'default': 'dmy'})],
    'build': [('rows', {}), ('--countries', {'help': 'JSON object: country name -> _id from listCountries'}),
              ('--platforms', {'help': 'comma-separated slugs for rows without a platforms column'}),
              ('--client-reference', {'dest': 'client_reference'}), ('--out-dir', {'default': 'tasks'}),
              ('--max', {'type': int, 'default': MAX_ROWS})],
    'fix': [('task', {}), ('rejection', {}), ('--out', {'default': 'rejected.csv'})],
    'report': [('rows', {}), ('imports', {'nargs': '+'}), ('--out', {'default': 'report.csv'})],
}

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    for name, options in COMMANDS.items():
        command = sub.add_parser(name)
        for flag, settings in options:
            command.add_argument(flag, **settings)
    args = parser.parse_args()
    try:
        {'normalise': normalise, 'build': build, 'fix': fix, 'report': report}[args.command](args)
    except (OSError, ValueError, LookupError, TypeError, AttributeError, zipfile.BadZipFile, ET.ParseError) as error:
        fail(f'{args.command} failed: {error}')

if __name__ == '__main__':
    main()
