# Rate limits

## Contents

- [The limit](#the-limit)
- [What "per operation" means](#what-per-operation-means)
- [What is counted](#what-is-counted)
- [The headers](#the-headers)
- [Handling a 429](#handling-a-429)
- [Pacing a bulk job](#pacing-a-bulk-job)

Full page: https://hub.main-team.org/api/rate-limits

## The limit

**100 requests per 60 seconds, per API account, per operation.** The same numbers apply in the
sandbox and in production.

One operation has a budget of its own: `createStudentImport` (`POST /v1/student/import`) allows
**10 requests per hour**, because one request to it registers up to 1000 students. Its
`X-RateLimit-Limit` reads `10`.

Two further limits bound that operation and are **not** rate limits:

- one unfinished import per account — a second one while the first runs is `409 conflict`, and the
  message carries the id of the running import;
- one batch being checked per server at a time — a server already checking one answers
  `503 service_unavailable` with `Retry-After`, and nothing was queued.

## What "per operation" means

Each operation has its own counter for your account.

- **Different ids share one counter.** Two reads of two applications are one operation.
- **Different organizations share one counter.** `GET /v1/{organizationId}/exam` for two olympiads
  is one operation, `listExams`, with 100 requests a minute between them, not 100 each.
- **Similar operations never share one.** `listStudents` (`GET /v1/student`) and `listOrgStudents`
  (`GET /v1/{organizationId}/student`) are two counters. So are `getStudent` and `getOrgStudent`,
  and `updateStudent` and `updateOrgStudent`.

The count belongs to the account, not to the machine. Ten containers on one account draw on one
budget, so spreading a job over more servers does not raise it.

## What is counted

A request is counted once the API knows it is yours and allowed: the token was accepted, the
organization exists, and the account holds the permission.

| Counted | Not counted |
|---|---|
| Every accepted request, file downloads included | `401 unauthorized` |
| `400 bad_request`, `404 not_found` and `409 conflict` from the operation itself | `403 forbidden` for a missing permission |
| | `404 not_found` for an unknown organization |
| | `413 payload_too_large`, `415 unsupported_media_type`, malformed JSON |
| | `getHealth` (`GET /v1/health`) |

Traffic without a valid token is limited per client address by the network in front of the API. That
refusal is a `429` **without** the JSON error envelope, and it is not part of your account's budget.

## The headers

Every counted response, errors included, carries:

| Header | Meaning |
|---|---|
| `X-RateLimit-Limit` | The limit for this operation |
| `X-RateLimit-Remaining` | Requests left in the current window, never below `0` |
| `X-RateLimit-Reset` | Seconds until the window ends, rounded up |

The window is fixed, not rolling: the first counted request to an operation opens a 60-second
window, and the next request after it closes opens a fresh one.

## Handling a 429

A refusal is status `429`, code `too_many_requests`, with a `Retry-After` header in seconds and no
`X-RateLimit-*` headers. Sleep exactly that long. A request sent sooner is refused again and does
not shorten the wait.

```js
if (response.status === 429) {
  const wait = Number(response.headers.get('retry-after') ?? 60);
  await new Promise((wake) => setTimeout(wake, wait * 1000));
  // then send the same request once more
}
```

Never loop on a `429` without sleeping, and never spread the same job over more accounts to get
around the limit.

## Pacing a bulk job

- Read `X-RateLimit-Remaining` from every answer and slow down before it reaches `0` rather than
  after: aim to leave a few requests in each window as headroom.
- Run one job per account at a time. Two jobs share one budget and can register the same person
  twice under two addresses.
- Prefer one big request to many small ones. A roster of 30 or more students is one
  `createStudentImport` rather than hundreds of `registerStudent` calls; see the
  registering-main-team-students-from-spreadsheets skill.
- Polling is requests too. Budget it with the work: see the polling reference of this skill.
- When a run is interrupted, resume from what you recorded; do not start the whole job again.
