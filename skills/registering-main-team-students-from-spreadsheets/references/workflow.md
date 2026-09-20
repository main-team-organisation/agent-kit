# The run, end to end

## Contents

- [The checklist](#the-checklist)
- [Limits](#limits)
- [Polling](#polling)
- [Resuming and timeouts](#resuming-and-timeouts)
- [Over 1000, and under 30](#over-1000-and-under-30)
- [Refusals that stop the run](#refusals-that-stop-the-run)
- [Files this skill writes](#files-this-skill-writes)

## The checklist

1. `getCurrentApiAccount` — which account, which environment, which roles.
2. Tell the person what will happen, including the welcome email. Wait for a yes.
3. `roster.py normalise` — clean the list, show the problems, fix them in the source.
4. `listCountries` — build `countries.json`.
5. `roster.py build` — write `tasks/task-NNN.json`.
6. `createStudentImport` — send one task file.
7. On `422`: `roster.py fix`, correct the source, back to step 3.
8. On `202`: keep `data._id` and poll `getStudentImport`.
9. `roster.py report` — one line per row of the original list.
10. The next task file, if there is one.

## Limits

| | Value |
|---|---|
| Rows per request | 30 to 1000 |
| Body size | 1.5 MB on this operation; 100 kB on every other |
| Requests to `createStudentImport` | 10 per hour per account |
| Unfinished imports | one per account |
| Requests to `getStudentImport` | the ordinary 100 per 60 seconds |
| An import stays readable | 30 days after it finishes |

Ten requests an hour is the whole budget for the day's mistakes as well as its work, which is why
the local checks come first. A batch refused with `422` has still cost one of the ten.

## Polling

Poll `getStudentImport` (`GET /v1/student/import/{importId}`) every 3 to 5 seconds. There are no
webhooks and nothing is pushed.

- `queued` — accepted, not started.
- `running` — being registered now.
- `succeeded` — every row registered, each with its `studentId`.
- `failed` — **no** row registered; `failure` says why.
- `cancelled` — an operator stopped it; no row registered.

Page the rows with `page` and `limit` (100 at most) to collect the ids. Stop polling after a bounded
number of attempts and come back later with the id rather than holding a process open; the import
is readable for 30 days.

## Resuming and timeouts

`createStudentImport` is the one write on this API that is safe to send again exactly as it was. The
same rows from your account inside 24 hours answer `202` with the import you already have, not a
second one, and `data._id` is the id you already had.

So an answer you never saw needs no special handling: send the same body again.

"The same rows" means the rows themselves — addresses compared without case or surrounding spaces,
`clientReference` ignored. Change one row and it is a **new** batch, which is refused with `409`
while the first is still running.

If you lost the import id, read the `409`: its message carries the id of the running import.

## Over 1000, and under 30

`roster.py build` writes as few request bodies as it can and makes them the same size, so a list of
1030 becomes two of 515 rather than one of 1000 and one of 30.

Send them **one after another**: one unfinished import per account. Wait for `succeeded` before
sending the next, and stop the run if one fails — the later batches may depend on what the person
wants to do about the failure.

Under 30 rows the operation refuses the batch with `400`. Register those students one at a time with
`registerStudent` (`POST /v1/student`), which is a different skill and a different rhythm: one
request per student, `409` on a duplicate address, 100 requests per 60 seconds.

## Refusals that stop the run

| Code | Meaning | What to do |
|---|---|---|
| `unauthorized` | The token is expired, malformed or signed with the wrong secret | Sign a fresh token once; if it fails again, stop |
| `forbidden` | No role grants `student/create` on `mto` | Stop; an operator adds it |
| `not_found` | Bulk registration is not switched on for this environment | Stop and ask support before building on it |
| `payload_too_large` | Over 1.5 MB | Send smaller batches (`--max`) |
| `unsupported_media_type` | Not UTF-8 JSON, or an encoding that is not gzip, deflate or br | Fix the client |
| `too_many_requests` | Over 10 requests this hour | Wait `Retry-After` seconds |
| `internal_error` | Something failed on the platform | Stop, keep the `request_id`, tell the person |
| `service_unavailable` | Busy, a scheduled pause, or the check took too long. **Nothing was queued** | Wait `Retry-After`, then send the same body again |

A `503` because the check took too long is the one worth reading twice: it suggests a smaller batch,
and `--max 500` is a reasonable next try.

## Files this skill writes

| File | Written by | Holds |
|---|---|---|
| `rows.json` | `roster.py normalise` | Every row, cleaned, with its reference and problems |
| `problems.json` | `roster.py normalise` | One entry per problem, for the person to fix |
| `countries.json` | you | Country names mapped to ids from `listCountries` |
| `tasks/task-NNN.json` | `roster.py build` | One whole request body |
| `rejection.json` | you | The `422` answer, saved as it arrived |
| `rejected.csv` | `roster.py fix` | One line per refused row, by spreadsheet reference |
| `import.json` | you | The last `getStudentImport` answer |
| `report.csv` | `roster.py report` | One line per row of the original list |

All of them hold children's personal data. Keep them on the person's own machine or in the session,
and delete them when the job is done.
