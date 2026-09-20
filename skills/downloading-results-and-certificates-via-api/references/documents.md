# Documents, downloads and files

## Contents

- [The four operations](#the-four-operations)
- [What a listed document carries](#what-a-listed-document-carries)
- [The download](#the-download)
- [One answer for every refusal](#one-answer-for-every-refusal)
- [Writing the file](#writing-the-file)
- [Serving it afterwards](#serving-it-afterwards)

## The four operations

| Operation | Path | Answers |
|---|---|---|
| `listStudentCertificates` | `GET /v1/{organizationId}/certificate/{userId}` | A paged list of released certificates |
| `downloadCertificate` | `GET /v1/{organizationId}/certificate/download/{certificateId}` | The PDF |
| `listStudentReports` | `GET /v1/{organizationId}/report/{userId}` | A paged list of released, uncancelled reports |
| `downloadReport` | `GET /v1/{organizationId}/report/download/{reportId}` | The PDF |

`{userId}` is the student's core `_id`, the one `registerStudent` returned. The lists need
`certificate/read` and `report/read` on the olympiad in the path; so do the downloads.

## What a listed document carries

The answers hold every stored field. The ones an integration uses:

| Field | Use |
|---|---|
| `_id` | The id the download takes |
| `shortId` | On a certificate: a 10-character id of upper-case letters and digits, also accepted by the download. **Case-sensitive** — a lower-cased copy answers `404` |
| the exam, session or category it belongs to | Which sitting it is for |
| the timestamps | Whether it is new since your last run |

Ignore fields you do not use, and expect more of them than any example shows.

## The download

```js
const answer = await fetch(
  `${base}/${organizationId}/certificate/download/${certificateId}`,
  { headers: { Authorization: `Bearer ${token}` } },
);
if (!answer.ok) {
  const { error } = await answer.json();   // errors are JSON, and arrive first
  throw new Error(`${answer.status} ${error.code} (${error.request_id})`);
}
```

| Header | What to do with it |
|---|---|
| `Content-Type` | `application/pdf` |
| `Content-Length` | Present when the size is known. Fewer bytes received means the download failed |
| `Content-Disposition` | The real file name, twice: `filename*` is exact (UTF-8, percent-encoded, RFC 5987) and is the one to prefer; `filename` is an ASCII fallback with accents removed |

Errors always arrive **before** the file. Once bytes have started, nothing more can be reported: if
storage fails halfway the connection simply closes, and you are left with a truncated file and no
error. Treat any transfer that ends early as a failure and delete what you wrote.

## One answer for every refusal

Four different situations answer `404 not_found` with the same message:

- no document has that id or short id;
- the document is not released, or the report was cancelled;
- it belongs to another account's student;
- it exists but has no file.

They are identical on purpose: a download never reveals whether a document exists in somebody
else's hands. When one you expected to work answers `404`, check that you are asking the olympiad
the document belongs to, and that it still appears in the student's list. Do not retry it, and do
not tell the person the document "was deleted" — you do not know that.

A student who is not yours answers `404 not_found` on the list, with `Student not found!`.

## Writing the file

- Decide the name yourself. Take `Content-Disposition` as a **suggestion**: strip every path
  segment, keep the basename only, and refuse `..`, a leading `/` or `\`, and control characters.
- Never interpolate a name from a record into a shell command or a template.
- Write to a temporary file and rename it once the byte count matches `Content-Length`, so a
  half-written PDF is never picked up as finished.
- Store under an id of your own (the document `_id` works) and keep the display name as metadata.
- These are children's personal data. Keep them where the rest of your student data lives, with the
  same retention, and delete a working copy when the job is done.

## Serving it afterwards

- Check who is asking before you hand over a file, and check it against the student that file
  belongs to. An id in a URL is not an authorisation.
- Do not put a document id in a public link, an email or a chat message.
- Do not re-upload certificates to a third-party tool to "process" them.
