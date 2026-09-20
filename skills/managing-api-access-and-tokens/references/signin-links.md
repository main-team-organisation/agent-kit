# Sign-in links

## Contents

- [The request](#the-request)
- [The redirect rule](#the-redirect-rule)
- [What is checked, in order](#what-is-checked-in-order)
- [What uses a link up](#what-uses-a-link-up)
- [Why the first sign-in matters](#why-the-first-sign-in-matters)
- [Handling it safely](#handling-it-safely)

## The request

`createSigninLink` (`POST /v1/{organizationId}/auth/signin`), with `auth/signin` on that olympiad:

```json
{ "studentId": "652f1c9b8e4b2a0012a3c4d5", "redirect": "/dashboard" }
```

| Field | Required | Meaning |
|---|---|---|
| `studentId` | yes | One of your students, by their core `_id` |
| `redirect` | no | Where they land afterwards, as a site-relative path. Left out, they land on the olympiad's home page |

The answer carries the URL and `expiresIn`, which is always `120`. The link works **once**, for
**120 seconds** from the moment it was issued.

## The redirect rule

`redirect` must be a **site-relative path**: it starts with `/` and cannot point at another site, so
a link can never be turned into an open redirect. Anything else answers `400 bad_request` with a
message saying so.

The literal text `{userId}` inside the path is replaced, when the student lands, with that
student's id **inside that olympiad** — which is not the core id you know them by. Use it whenever a
panel path needs the student's own id. Only the first occurrence is replaced, so write it once.

## What is checked, in order

| Answer | Meaning | Who fixes it |
|---|---|---|
| `404 not_found` "Organization not found!" | The `{organizationId}` is not an organization's `_id` — a slug always lands here | You |
| `403 forbidden` "Insufficient role permissions" | Your account has no role granting `auth/signin` on that olympiad | An operator |
| `400 bad_request` | `studentId` is not a 24-character hexadecimal id, `redirect` breaks the rule, or the body has a field it should not | You |
| `404 not_found` | The student is not yours, or does not exist | You |
| `403 forbidden` "Student is not activated for organization …" | The student's access list does not include that olympiad | You: add it with `activatedPlatformsThisSeason` |

The two `403`s look alike and have different fixes. Tell them apart by the message, and say which
one it is when you report it. A refusal changes nothing.

An unconfirmed email address does **not** stop a link being issued.

## What uses a link up

The link is single use. It is spent the first time it is opened — by the student, by a link
scanner in an email gateway, by a preview in a chat app, by your own `curl`, or by a crawler
following it out of a log. That is why it is minted on the click and redirected to at once.

Once spent or expired, the browser shows an error and there is no way to revive it. The fix is
always a new link, and minting a new one is an ordinary request, safe to repeat.

Never:

- generate links in advance or in a batch;
- store one in a database, a queue, a cache or a session;
- put one in an email, an SMS, a chat message or a ticket;
- log one, or let it into an error report or an analytics event;
- open one yourself to "check that it works".

## Why the first sign-in matters

A student's registration creates the **core** record. The olympiad's own copy is created the first
time they sign in there. Until that has happened:

| Operation | Answer |
|---|---|
| `createApplication` | `409 conflict`, naming the rule and the sign-in link |
| `listStudentApplications`, `listStudentCertificates`, `listStudentReports` | the same `409 conflict` |

So "send a sign-in link" is a real step in an onboarding flow, not an optional nicety. Design for
the student actually using it: nothing you can call on their behalf replaces it.

## Handling it safely

Treat the URL as a password with a two-minute life.

- Return it as a `302` from the request the student's click made; do not render it into a page.
- Send `Cache-Control: no-store` and `Referrer-Policy: no-referrer` on that response.
- Keep it out of access logs, application logs and traces. If your framework logs redirect targets,
  redact this one by name.
- Never show it to the operator, and never paste it into chat to demonstrate a problem. The
  `request_id` is what support needs.
