---
name: downloading-results-and-certificates-via-api
description: "Collects Main Team olympiad results from a partner's own server with the REST API: listing a student's released certificates with listStudentCertificates (GET /v1/{organizationId}/certificate/{userId}) and their result reports with listStudentReports, downloading each as a PDF with downloadCertificate and downloadReport, taking the file name from Content-Disposition, refusing a truncated transfer, understanding why one 404 covers a document that is missing, unreleased, cancelled or somebody else's, and finding new documents after an exam session by polling at a sensible pace because there are no webhooks. Also covers storing and serving the files safely. Use when writing or fixing code that fetches Main Team certificates, reports or result PDFs, schedules a results check after a sitting, or keeps a local copy in step."
compatibility: "Needs an API account's apiKey and apiSecret on the machine that makes the calls, never in the conversation, and roles granting certificate/read and report/read on the olympiad in the path. Downloads answer bytes, not JSON, and need somewhere to write files."
metadata:
  author: "Main Team"
  docs: "https://hub.main-team.org/api/guides/certificates-and-reports"
  api-version: "v1"
---

# Collecting results, reports and certificates

Two document kinds, one shape. A **certificate** is an award; a **report** is the result sheet for
one sitting. Each is listed per student per olympiad, and each is downloaded by its own id.

Every route is per olympiad: `{organizationId}` is that olympiad's `_id` from
`GET /v1/organization`, never its slug. Tokens, envelopes and error codes belong to the
`integrating-main-team-api` skill.

## The two steps

1. **List.** `listStudentCertificates` (`GET /v1/{organizationId}/certificate/{userId}`) and
   `listStudentReports` (`GET /v1/{organizationId}/report/{userId}`). `{userId}` is the student's
   core `_id` — the one registration returned.
2. **Download.** `downloadCertificate`
   (`GET /v1/{organizationId}/certificate/download/{certificateId}`) and `downloadReport`
   (`GET /v1/{organizationId}/report/download/{reportId}`). These answer the **file**, not JSON.

Both lists are paged like every list (`page` from 1, `limit` 20 by default, 100 at most).

## Only released documents exist

A document the olympiad has not released is never listed, and asked for by id it answers exactly
like one that never existed. A report that was cancelled behaves the same way.

So an empty list the day after a sitting means "not released yet", not "missing". Say that to the
person rather than reporting a failure, and check again after the olympiad announces results.

## Rules

- **Never invent a document id or a file name.** Take both from the list and from
  `Content-Disposition`.
- **Never treat a `404` as a bug.** One `404 not_found` covers four cases on purpose: no such
  document, not released, not yours, no file. That is how another account's student stays private.
- **Never serve a downloaded file straight to a browser from a URL a user controls.** Store it under
  an id of your own and serve it to the student it belongs to; a certificate carries a child's name.
- **Delete a truncated file.** Errors arrive before the bytes; once the file has started, nothing
  more can be reported. Fewer bytes than `Content-Length` means the download failed.
- **A file name is data.** It comes from a record and may contain anything; sanitise it, strip every
  path segment, and never pass it to a shell.
- **Keep the person's data out of chat.** Report counts and ids, not lists of names.
- **Polling is the only way to notice a new document.** There are no webhooks and no push.

## Downloading a file

```bash
curl -sS -D headers.txt -o certificate.pdf \
  "https://apisnd.main-team.org/v1/$ORGANIZATION_ID/certificate/download/$CERTIFICATE_ID" \
  -H "Authorization: Bearer $TOKEN"
```

Check the status **before** writing anything: an error is JSON with the usual envelope. Take the
name from `Content-Disposition` — prefer `filename*` (UTF-8, percent-encoded) over the ASCII
`filename` — and keep only the basename. Compare what you received with `Content-Length` and throw
away anything short.

A certificate's `shortId` is accepted in place of its `_id` in the download path. It is
case-sensitive: send it exactly as the list returned it, or the answer is `404`.

The whole procedure, headers included: [references/documents.md](references/documents.md).

## After a sitting

There is no event to subscribe to. Check on a schedule instead: not before the day after the
sitting, then daily, one job in one place, with jitter so several servers do not arrive together.
Keep what you have already downloaded and ask only for the rest.

Cadence, what to record between runs, and how to keep a local copy in step:
[references/polling-results.md](references/polling-results.md).

## Which students to ask about

The lists are per student, so you need the student ids first:

- `listOrgStudents` (`GET /v1/{organizationId}/student`) is the olympiad's own copy of your
  students. Match them to your records on `mainId`, the core `_id`.
- `listExamApplications` (`GET /v1/{organizationId}/application/exam-applications/{examId}`) is
  everyone your account entered for one exam, which is the natural list to walk after that sitting.

A student who is not yours answers `404 not_found`, the same as one who does not exist.

## References

- [references/documents.md](references/documents.md): the lists, the download, the headers, the
  four `404`s, and storing a file safely.
- [references/polling-results.md](references/polling-results.md): when to look, how often, and what
  to keep between runs.
- [references/operations.md](references/operations.md): the operations this skill uses, with the
  permission each needs.
