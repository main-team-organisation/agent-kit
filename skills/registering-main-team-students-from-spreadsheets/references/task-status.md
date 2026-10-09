<!-- Generated from the Main Team API contract 1.2.0 (https://hub.main-team.org/api/openapi.json). Do not edit: it is rebuilt with every release. -->

# Import status

What `createStudentImport` (`POST /v1/student/import`) answers with, and what
`getStudentImport` (`GET /v1/student/import/{importId}`) returns while you follow it.

Branch on `status` and on each row `code`, never on a `message`.

## The import

| Field | Always there | Format | Meaning |
|---|---|---|---|
| `_id` | yes | string | The import’s `_id`. Read it with `getStudentImport`. |
| `createdAt` | yes | string, format date-time | When you sent it. |
| `expiresAt` | yes | string, format date-time | When this import stops being readable. After it, `getStudentImport` answers 404, exactly as it does for an import that never existed. The students stay registered. |
| `registered` | yes | number | How many students were registered: `total` once the import has succeeded, and 0 until then and for ever after a failure. |
| `status` | yes | one of `queued`, `running`, `succeeded`, `failed`, `cancelled` | `queued` until a server picks it up, `running` while it registers, then `succeeded` or `failed`. `cancelled` means an operator stopped it. There is no partial import: on anything but `succeeded` no student of this batch was registered. |
| `students` | yes | array of objects | One page of the rows, in the order you sent them. Page it with `page` and `limit`; `pagination.total` counts every row. Absent from the answer to `createStudentImport`, which has nothing to report yet. |
| `total` | yes | number | How many rows you sent. |
| `clientReference` | no | string | The `clientReference` you sent, if you sent one. |
| `failure` | no | object | Set once the import has failed or been cancelled. |
| `finishedAt` | no | string, format date-time | When it ended, whichever way it ended. |
| `startedAt` | no | string, format date-time | When a server picked it up. |

## One row of the import

| Field | Always there | Format | Meaning |
|---|---|---|---|
| `email` | yes | string, format email | The address you sent for this row, in lower case. |
| `row` | yes | number | The row’s position in the `students` you sent, counting from 0. |
| `status` | yes | one of `pending`, `registered`, `skipped` | `pending` until the import runs, then `registered` for every row when it succeeds, or `skipped` for every row when it does not. An import registers all of its students or none of them. |
| `error` | no | object | Why this row could not be registered, when it could not. |
| `externalRef` | no | string | The `externalRef` you sent for this row, if you sent one. |
| `studentId` | no | string | The student’s `_id`, on a `registered` row. Use it with `getStudent`, `createSigninLink` and `createApplication`. |

A row that could not be registered carries `error`:

| Field | Always there | Format | Meaning |
|---|---|---|---|
| `code` | yes | one of `invalid_field`, `unexpected_field`, `unknown_reference`, `duplicate_in_request`, `email_taken_by_your_student`, `email_unavailable` | A stable machine code: branch on this. `invalid_field` and `unexpected_field` are the row’s own rules; `unknown_reference` is a `country`, `grade`, `city` or `school` that matches nothing; `duplicate_in_request` is the same address twice in your own body; `email_taken_by_your_student` is one of your students; `email_unavailable` is an address that cannot be registered, and the answer never says who holds it. |
| `message` | yes | string | Written for a person, and may change: never branch on it. |
| `duplicateOf` | no | number | On `duplicate_in_request`: the earlier row in your own body with the same address. |
| `studentId` | no | string | On `email_taken_by_your_student`: the `_id` of the student of yours who has the address, so you can update them instead. |

## Why an import ended

| Field | Always there | Format | Meaning |
|---|---|---|---|
| `code` | yes | string | A stable machine code. `rows_rejected`: a row stopped being registrable between the check and the write, most often because its address was registered in between; the rows say which. `forbidden`: the account may no longer register students. `cancelled`: an operator stopped it. `internal_error`: something failed on our side. |
| `message` | yes | string | Written for a person, and may change: never branch on it. |

## What a refused batch answers (422)

`error.details` of the `422`. Nothing was queued and nothing was registered:

| Field | Always there | Format | Meaning |
|---|---|---|---|
| `rejected` | yes | number | How many of them cannot be registered. |
| `rows` | yes | array of objects | Every refused row, by position and property. Empty, with `rejected` still counted, when the refusal is only that addresses cannot be registered and your account has already been told which rows those were several times today. |
| `total` | yes | number | How many rows you sent. |
| `truncated` | yes | boolean | True when `rows` is shorter than `rejected`, so fix what is listed and send the batch again to see the rest. |

Each entry of `rows`:

| Field | Always there | Format | Meaning |
|---|---|---|---|
| `code` | yes | one of `invalid_field`, `unexpected_field`, `unknown_reference`, `duplicate_in_request`, `email_taken_by_your_student`, `email_unavailable` | Why the row was refused; the same codes a row carries. |
| `field` | yes | object | The property at fault, or `null` when no single property is. |
| `message` | yes | string | Written for a person, and may change: never branch on it. |
| `row` | yes | number | The row’s position in the `students` you sent, counting from 0. |
| `duplicateOf` | no | number | On `duplicate_in_request`: the earlier row with the same address. |
| `studentId` | no | string | On `email_taken_by_your_student`: the `_id` of the student of yours who has the address. |
