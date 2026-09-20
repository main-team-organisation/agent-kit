# When a batch is refused

## Contents

- [Two different refusals](#two-different-refusals)
- [The row codes](#the-row-codes)
- [truncated and an empty list](#truncated-and-an-empty-list)
- [Fixing and sending again](#fixing-and-sending-again)
- [Problems the local script finds first](#problems-the-local-script-finds-first)
- [A row that failed after the check](#a-row-that-failed-after-the-check)

## Two different refusals

**`400 bad_request` comes first.** A row that breaks a property's own rule — a birth date that is
not a date, a missing surname, a `password` field — is refused before the batch is looked at, and
the message names the row and the property, counting rows from 0, for example
`students.4.birth birth must be a real date in DD/MM/YYYY format`. Only the first problem is
reported, so fixing one can reveal the next.

**`422 unprocessable_entity` comes second**, and lists everything at once: it is for the problems
that take a lookup to see. `error.details` carries `total`, `rejected`, `truncated` and `rows`.
Nothing was queued and nothing was registered.

Both leave the batch unsent, so neither costs anything but one of the ten requests an hour.

## The row codes

Branch on `code`, never on `message`.

| `code` | What happened | What to do |
|---|---|---|
| `invalid_field` | The row breaks one of `registerStudent`'s rules; `field` says which | Fix the value in the list |
| `unexpected_field` | The row carries a property the operation does not take, `password` among them | Remove the column |
| `unknown_reference` | The `country`, `grade`, `city` or `school` matches nothing. Nothing is ever created for you | Fix the name, or send an id. Ask the person; never substitute a similar school |
| `duplicate_in_request` | Two rows of your own body have the same address; `duplicateOf` is the earlier one | Decide which row is right. Two rows for one child is usually a copied line |
| `email_taken_by_your_student` | One of **your** students already has the address; `studentId` is theirs | Take the row out of the batch and update that student instead with `updateStudent` |
| `email_unavailable` | The address cannot be registered, and the answer never says who holds it | Take the row out and ask the person for the address that student actually uses |

`email_unavailable` is deliberately silent about the holder. Do not guess, and do not tell the
person which school or account has it — the API did not say.

## truncated and an empty list

`truncated: true` means `rows` is shorter than `rejected`: fix what is listed and send the batch
again to see the rest.

`rows` can also be **empty with `rejected` counted**. That happens when the only problem is
addresses that cannot be registered and your account has already been shown those rows several
times that day. It is a deliberate limit: a roster of addresses collected somewhere else, sent
repeatedly to learn which ones exist, is not a supported use of this API. If you see it, stop and
tell the person plainly.

## Fixing and sending again

1. Save the `422` answer as it arrived.
2. `python3 scripts/roster.py fix tasks/task-001.json rejection.json --out rejected.csv` maps each
   refused position back to its line in the spreadsheet.
3. Show the person `rejected.csv`, grouped by code, and agree what to change.
4. Correct the **source list**, not the task file, then run `normalise` and `build` again.
5. Send the whole batch again. A batch is one unit: sending only the corrected rows leaves the rest
   unregistered, and under 30 rows it is refused outright.

Changing any row makes it a new batch, so the 24-hour repeat protection does not apply to the fixed
version. That is correct — it is a different set of students.

## Problems the local script finds first

`roster.py normalise` reports these before anything is sent, so they never cost a request:

| Problem | Meaning |
|---|---|
| `birth_unreadable`, `grade_unreadable`, `sex_unreadable` | The value is not a date, a grade 1 to 12, or a sex the script recognizes |
| `email_invalid` | Not an address at all |
| `email_duplicate_of_row_N` | The same address twice in the file — `duplicate_in_request` before it is sent |
| `<field>_missing` | A required field is empty |
| `password_column_ignored` | The list has a password column; it is never sent |
| `platform_unknown`, `too_many_platforms` | A platforms cell names something that is not an olympiad slug, or more than six |
| `country_not_in_countries_map` (at `build`) | The country name is not in `countries.json` |
| `full_name_split` | One name column was split at the last space; worth checking for double surnames |

## A row that failed after the check

The batch is checked before it is queued, but the world moves on. If a row stops being registrable
between the check and the write — almost always because its address was registered in between — the
import ends `failed` with `failure.code` `rows_rejected`, and the rows carrying an `error` say
which.

Nothing was registered. Take those rows out, or fix them, and send the batch again.
