# Certificates

## The two calls

```jsonc
main-team:list_my_certificates { "brand": "stem" }
//  -> certificates: each with certificate, title, exam, session_date

main-team:get_my_certificate   { "brand": "stem", "certificate": "crt_q4n8w2k6" }
//  -> the same detail for one, plus view_url
```

Take `certificate` from the list. It is an opaque value sealed to this connection and this
olympiad: never compose or edit one, and one from another session answers `not_found`. If the
student pastes a panel certificate link instead, the 24-character id at its end can go in as
`certificate_id` — one of the two, never both. The answer names the certificate by `certificate`
either way and never repeats the id.

`view_url` is the student's Certificates page, not one certificate: no link names a certificate.

## The official document never comes back

The official certificate file is never returned, on any olympiad, to anybody — not to the student,
not to their teacher. It carries the holder's platform ID — the username the account signs in with —
and that never goes into a chat. There is also no public verification link, because such a link is
a permanent way for anyone to fetch the document, and the page behind it shows the same ID.

Do not offer to rebuild, re-typeset, screenshot or describe the official document as a substitute,
and do not put the link anywhere but into the conversation.

## A copy made for AI use

Where the connection offers it, `main-team:get_certificate_copy` attaches a PDF **copy**:

```jsonc
main-team:get_certificate_copy { "brand": "stem", "certificate": "crt_q4n8w2k6" }
//  -> certificate, copy { layout, mime_type, size_bytes, pages, uri, file_name },
//     official: false, omitted: [...], notice, view_url — and the PDF attached
```

The copy prints the olympiad, the certificate title, the student's current first and last name, the
subject, the sitting and the date. It never prints a user ID, a student code, a QR code, a document
number or a verification link, so it is **not the official certificate and cannot be verified**.
So "send me my certificate" has two honest answers:

> "Here is a copy made for use with AI apps — your name, the exam and the date, but no user ID,
> document number or QR code, so it is not the official certificate. For the official one, open
> <view_url> while signed in."

Or, when the connection has no copy tool, only the page:

> "Here is the page that downloads it — <view_url>. Open it while you are signed in and the PDF is
> there."

Fetch a copy only when the student asked for the file, one at a time. `status: "open_in_panel"`
with `reason: "copy_unavailable"` means this one cannot be copied; hand over its `url`.

## What a student sees, and what a teacher sees

`main-team:list_my_certificates` answers the certificates **this account holds**. For a student
those are their exam certificates. A teacher or partner calling the same tool sees their own
teacher certificates, not their students' — which is why it is a shared tool with a different
meaning per role.

## When the list is empty

Usually because the season has not reached certificates yet, or because the student has no result
that earns one. Say which of the two you can tell from what you read, and say plainly when you
cannot tell:

> "There are no certificates on your account for gmath yet. They follow the published results, so
> there is nothing to do but wait."

Do not check other olympiads unprompted, and do not re-read.

## Panel pages

`main-team:get_panel_link` with the page `certificates` opens the student's own certificates page,
which is the right destination when they want to browse rather than fetch one.

## What certificates are not

- Not proof of anything this assistant can attest to. If somebody asks for verification, the answer
  is that Main Team verifies certificates, through the panel, and there is no link to hand out. A
  copy from `main-team:get_certificate_copy` proves nothing either, and must never be offered as proof.
- Not a place to take, start or answer an exam, which nothing in this kit ever does.
- Not editable. No tool changes a certificate's name, title or date; corrections go to Main Team
  through the panel.
