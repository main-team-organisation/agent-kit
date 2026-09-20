# Every refusal, and the fix

## Contents

- [Creating](#creating)
- [Moving](#moving)
- [Withdrawing](#withdrawing)
- [Reading](#reading)
- [How to report one](#how-to-report-one)

Codes and statuses come from the contract; the messages are written for people and may change, so
branch on the status and `error.code`, and quote the message only to explain.

## Creating

`createApplication` `POST /v1/{organizationId}/application`

| Answer | What it means | What to do |
|---|---|---|
| `400 bad_request` | `studentId` or `examId` is not an id of 24 hexadecimal characters, or a field is missing | Fix the body |
| `403 forbidden` | No role grants `application/create` on this olympiad | Stop; an operator adds the role |
| `404 not_found` | The organization id is not an organization, or the student is not yours | Check the `{organizationId}` is an `_id`, not a slug, then check the student |
| `409` "has never signed in" | The olympiad holds no copy of the student yet | Send them a sign-in link and wait for them to use it |
| `409` "not open for application" | The sitting has passed, the category is retired, or applications are closed | Ask the picker again and choose from what it offers |
| `409` "not available for grade …" | The exam accepts other grades | Choose another exam; do not change the student's grade to fit |
| `409` "not available in this student's country" | The exam is restricted | Choose another exam |
| `409` "has no language set" | The exam is not offered to students | Choose another exam |
| `409` "already has an application for … on this sitting" | One category, one sitting, one exam | Move the existing entry instead of creating a second |
| `409` "Only exams returned by …/exam/available/…" | The exam is not in this student's picker | Take `examId` from the picker |
| `429 too_many_requests` | The rate limit | Sleep `Retry-After` seconds |

## Moving

`moveApplication` `PUT /v1/{organizationId}/application/{applicationId}`

| Answer | What it means | What to do |
|---|---|---|
| `404 not_found` | The application is not yours, or does not exist | Read the student's applications |
| `409` "already been started" | `participated` or `examSubmitted` is true | Nothing moves it; tell the person |
| `409` "cannot be moved to that category" | The old category does not accept the new one | Choose within the accepted categories |
| `409` "already has an application for … on this sitting" | The move collides with another entry | Withdraw or move the other one first |
| `409` "Training has already started for this AI Challenge application" | That entry is fixed | Tell the person |
| `409` "paid for at X, and that exam costs Y" | A settled payment would buy something else | Choose an exam at the same price, or have the school arrange it in the panel |

A move to the exam the application already has is not an error: it answers `200` and writes nothing.

## Withdrawing

`deleteApplication` `DELETE /v1/{organizationId}/application/{applicationId}`

| Answer | What it means | What to do |
|---|---|---|
| `404 not_found` | Already deleted, not yours, or never existed | If you know it existed, treat it as already gone |
| `409` "has been paid for and cannot be deleted" | The payment is settled | A refund is outside this API; arrange it with the olympiad |

There is no undo. Confirm each withdrawal with the person before sending it.

## Reading

| Answer | Where | What it means |
|---|---|---|
| `400 bad_request` | any id in a path | Not 24 hexadecimal characters |
| `404 not_found` | `getApplication`, `listStudentApplications` | Not yours, or no such record — the two are deliberately the same answer |
| `409 conflict` | `listStudentApplications` | The student has never signed in to this olympiad |
| `404` "Organization not found!" | any route | The `{organizationId}` is not an organization's `_id`; a slug always answers this |

## How to report one

Give the person the rule, not the raw error: "Ada cannot be entered for Science on 14 November
because her grade is not one the paper accepts (it takes 9 and 10)." Then offer what the picker
does allow.

Keep the `request_id` from the answer in your own log. Quote it to support; do not paste students'
names or addresses into a support message or into chat.

Never retry a `403`, a `404` or a `409`: nothing about the request will have changed. Only `429`
and `5xx` are worth sending again, and only after waiting.
