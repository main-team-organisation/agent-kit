# Certificates

## The two calls

```jsonc
main-team:list_my_certificates { "brand": "stem" }
//  -> certificates: each with certificate_id, title, exam, session_date

main-team:get_my_certificate   { "brand": "stem", "certificate_id": "91d4a7c3e0b28f6512ab7e40" }
//  -> the same detail for one, plus view_url
```

Take `certificate_id` from the list. A guessed id answers `not_found`, and that is the server
refusing rather than a nudge to try another.

## The document never comes back

No certificate file is ever returned, on any olympiad, to anybody — not to the student, not to their
teacher. There is also no public verification link, because such a link is a permanent way for
anyone to fetch the document.

So the answer to "send me my certificate" is always the same shape:

> "Here is the page that downloads it — <view_url>. Open it while you are signed in and the PDF is
> there."

Do not offer to rebuild, re-typeset, screenshot or describe the document as a substitute, and do not
put the link anywhere but into the conversation.

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
  is that Main Team verifies certificates, through the panel, and there is no link to hand out.
- Not a place to take, start or answer an exam, which nothing in this kit ever does.
- Not editable. No tool changes a certificate's name, title or date; corrections go to Main Team
  through the panel.
