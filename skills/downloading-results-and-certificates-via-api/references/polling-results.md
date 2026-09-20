# Finding new results without webhooks

## Nothing is pushed

The API never calls your server. No webhook, no callback, no stream. A certificate appears in a
list the moment the olympiad releases it, and the only way to notice is to ask.

## When to start asking

Not before the day after the sitting. Results are released by people, on their own schedule, and a
job that starts polling an hour after the paper spends its whole rate-limit budget on empty lists.

| Phase | Cadence |
|---|---|
| The sitting itself | Do not poll |
| The day after, until results are announced | Once a day |
| The week after the announcement | Once a day, until every student you expected has their documents |
| Afterwards | Weekly, or on demand when someone asks |

Add jitter of a few minutes so that several servers, or several partners, do not arrive at the same
moment. Run the job in one place: on every container it costs the number of containers and shares
one budget.

## What to keep between runs

Keep a small record per student per olympiad, so each run asks for as little as possible:

| Keep | Why |
|---|---|
| The student's core `_id` | The `{userId}` both lists take |
| The document `_id`s you already have | So you download each file once |
| The last time you looked | So you can skip students you checked today |
| A failure count per document | So one broken download does not run for ever |

Walk the students you actually entered rather than every student you have ever registered:
`listExamApplications` (`GET /v1/{organizationId}/application/exam-applications/{examId}`) is the
list of who sat that paper for you.

## The loop

1. For each student, list certificates and reports.
2. Compare against what you already hold; download only the new ids.
3. Record what you downloaded before moving on, so an interrupted run resumes instead of restarting.
4. Stop the run on `401 unauthorized` (sign a fresh token, one retry) and on `403 forbidden` (a
   missing role; only an operator fixes it).
5. On `429 too_many_requests`, sleep the seconds in `Retry-After` and continue where you were.
6. On `404 not_found` for a document that used to be there, drop it from your list: it was withdrawn
   or is no longer available to you. Do not retry it and do not report it as an error.
7. On `500 internal_error` or `503 service_unavailable`, back off and come back to the same student
   later; a list read is safe to repeat.

Each list is its own operation with 100 requests per 60 seconds for the whole account, so a run over
a thousand students is paced work, not a burst. Read `X-RateLimit-Remaining` and slow down before it
reaches zero.

## Telling the person

- An empty list is "not released yet", not a failure. Say which sitting and when you will look
  again.
- Report counts — "142 of 160 students have their report" — rather than lists of names.
- If a student is still missing documents a week after the announcement, that is a question for the
  olympiad, not something more polling will solve.
