# Polling: there are no webhooks

## Contents

- [The rule](#the-rule)
- [What is worth polling, and how often](#what-is-worth-polling-and-how-often)
- [A poll loop](#a-poll-loop)
- [What never to poll](#what-never-to-poll)

## The rule

The Main Team API sends nothing to your server. It answers requests, and that is all. There is no
webhook, no callback URL, no server-sent stream and no queue you can subscribe to. Anything you
want to notice, you ask for.

That makes cadence a design decision, and a budgeted one: every poll is a request against the rate
limit for that operation — 100 per 60 seconds for most, 10 an hour for `createStudentImport`.
Reading an import is `getStudentImport`, an ordinary operation with the ordinary 100 a minute.

## What is worth polling, and how often

| You are waiting for | Ask | Cadence |
|---|---|---|
| A bulk import to finish | `getStudentImport` `GET /v1/student/import/{importId}` | Every 3 to 5 seconds. A thousand students take seconds, not minutes, once it starts |
| A certificate or report after an exam session | `listStudentCertificates` `GET /v1/{organizationId}/certificate/{userId}` and `listStudentReports` `GET /v1/{organizationId}/report/{userId}` | Not before the day after the sitting, then daily |
| A fee to be settled | `listApplications` `GET /v1/{organizationId}/application` | Hourly at most; payment happens in the panel, at the family's pace |
| A student's first sign-in to an olympiad | `listOrgStudents` `GET /v1/{organizationId}/student` | Only when you are about to need it, such as before entering them for an exam |
| Reference data: countries, grades, organizations | `listCountries`, `listGrades`, `listOrganizations` | Once a day at most; cache the ids |

Add jitter. Several servers that poll on the same schedule arrive together and spend the whole
window at once; a random fraction of the interval spreads them.

Poll from one place. A job that runs on every container multiplies the cost by the number of
containers and shares one budget.

## A poll loop

```js
async function waitForImport(importId, token) {
  for (let attempt = 0; attempt < 120; attempt += 1) {
    const answer = await fetch(
      `https://api.main-team.org/v1/student/import/${importId}?limit=100`,
      { headers: { Authorization: `Bearer ${token}` } },
    );
    if (answer.status === 429) {
      const wait = Number(answer.headers.get('retry-after') ?? 60);
      await new Promise((wake) => setTimeout(wake, wait * 1000));
      continue;
    }
    const { data } = await answer.json();
    if (data.status !== 'queued' && data.status !== 'running') return data;
    await new Promise((wake) => setTimeout(wake, 3000 + Math.random() * 1000));
  }
  throw new Error('the import did not finish in time; read it again later');
}
```

Points that matter in any language: a bounded number of attempts, a sleep between them, honouring
`Retry-After` instead of counting the attempt, and returning the record rather than a boolean, so
the caller can read `status` and `failure`.

For a long wait, record the id and come back later rather than holding a process open. An import is
readable for 30 days after it finishes; after that it answers `404` and the students stay
registered.

## What never to poll

- **A sign-in link.** It works once, for 120 seconds. Mint it when the student clicks, redirect at
  once, and never prefetch, cache or check one.
- **`getHealth` (`GET /v1/health`)** as a keep-alive. It is there for a one-off reachability check,
  not for a monitor loop against someone else's service.
- **An operation you already know the answer to.** Cache country, grade and organization ids; they
  change between seasons, not between requests.
- **Anything at all after a `403`.** The account lacks a role, and nothing but an operator changes
  that.
