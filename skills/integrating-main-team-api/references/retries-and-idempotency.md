# Retries and idempotency

## Contents

- [What each answer means](#what-each-answer-means)
- [Which writes are safe to repeat](#which-writes-are-safe-to-repeat)
- [After a timeout, per operation](#after-a-timeout-per-operation)
- [Backoff](#backoff)
- [Request ids](#request-ids)

Full page: https://hub.main-team.org/api/retries-and-idempotency

## What each answer means

| Answer | Did it change anything? | What to do |
|---|---|---|
| `2xx` | Yes, if it was a write | Store the result |
| `400`, `413`, `415`, `422` | No | Fix the request; the same one fails the same way |
| `401` | No | Sign a fresh token and send it once more; if that fails too, stop |
| `403` | No | Stop. An operator has to add the role |
| `404` | No | Stop, unless you are checking after a delete that timed out |
| `409` | No | Stop and read the message; it names the state in the way |
| `429` | No | Sleep `Retry-After` seconds, then send it again |
| `500`, `502`, `503`, `504`, a timeout, a dropped connection | Maybe | Check, or repeat if the operation is safe to repeat |

Every `4xx` is a refusal, and the API checks a request completely before it writes anything, so a
`4xx` never leaves half a change behind. A "did it happen?" check is only needed after a `5xx` or
when no answer arrived at all.

## Which writes are safe to repeat

| Operation | What a repeat does |
|---|---|
| Any `GET` | Nothing; repeat freely |
| `createStudentImport` `POST /v1/student/import` | **Idempotent for 24 hours.** The same rows answer `202` with the import you already have |
| `registerStudent` `POST /v1/student` | **Not idempotent.** A repeat answers `409 conflict`, and the message names your existing student |
| `updateStudent` `PUT /v1/student/{studentId}` | The same body, the same result |
| `updateOrgStudent` `PUT /v1/{organizationId}/student/{studentId}` | The same; the organization is added to the access list only once |
| `setStudentPassword` `PUT /v1/student/{studentId}/password` | Sets the same password again; `409` if the student confirmed their address in between |
| `linkStudentSupervisor` `PUT /v1/{organizationId}/student/{studentId}/supervisor` | Links the same supervisor again, `200` each time |
| `createSigninLink` `POST /v1/{organizationId}/auth/signin` | Mints a **new** link; the earlier one expires unused |
| `createApplication` `POST /v1/{organizationId}/application` | **Idempotent**: `201` once, then `200` with the same application |
| `moveApplication` `PUT /v1/{organizationId}/application/{applicationId}` | **Idempotent**: moving to the exam it already has writes nothing |
| `deleteApplication` `DELETE /v1/{organizationId}/application/{applicationId}` | The first call deletes; a repeat answers `404` |
| `revokeToken` `POST /v1/api-account/revoke-token` | The first call revokes; a repeat with that token answers `401` |

## After a timeout, per operation

- **`registerStudent`.** Do not send it again blindly. Either repeat it and treat a `409` naming
  your own student as success, or look first with `GET /v1/student` filtered by the address.
- **`createStudentImport`.** Send exactly the same rows again. Inside 24 hours you get the import
  you already have; `data._id` is the same id. Rows are compared with addresses lower-cased and
  trimmed, and `clientReference` is ignored, so changing one row makes it a new batch — which is
  refused with `409` while the first is still running.
- **`createApplication`.** Send it again; the answer is the same application.
- **`deleteApplication`.** Send it again; a `404` means it was already gone.
- **`createSigninLink`.** Repeat the *request*, never the link. A link works once, for 120 seconds,
  and a repeat of the request mints a fresh one. Never store, log, email or prefetch either.
- **`revokeToken`.** Send it again; a `401` means the first call worked.

## Backoff

Retry only network errors and `5xx`, and only on operations the table above allows. Wait
`1s, 2s, 4s, 8s` with jitter, at most four or five attempts, and stop rather than loop. Respect
`Retry-After` when it is present, on a `429` and on the `503` answers of `createStudentImport`;
it is an instruction, not a hint.

Never retry `403`, `409` or `422`. Nothing about the request will have changed.

## Request ids

Send your own `X-Request-Id` (1 to 256 characters; a UUID works) so your logs and Main Team's line
up. The answer carries the same header, and `error.request_id` repeats it. It does **not** make a
request idempotent: the API does not deduplicate on it.

Log method, path, status, duration and the request id. Redact the `Authorization` header, and never
log a sign-in link or a student's password.
