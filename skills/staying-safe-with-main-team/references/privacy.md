# Privacy: what never leaves, and what never goes in

## What the server refuses to send

These never appear in an answer, and an assistant must never try to reconstruct or infer them:

- a username, a student code or a teacher code;
- anybody's e-mail address, telephone number or date of birth — the person's own address comes back
  only as `email_masked`, with most of it hidden;
- a payment or transaction reference of any kind;
- a report or certificate **file**, and there is no public verification link to one either;
- any identifier of a person other than the connected one.

A student is an opaque handle, `stu_` and then a sealed value, for example `stu_x7k2m9p4`. A study
paper is a `mat_` handle. Both are sealed to one connection and one olympiad: they mean nothing in
another app, another session or another olympiad, and they are not keys — the platform re-checks
who owns what on every call.

## What never goes into the conversation

- **Passwords and one-time codes.** If one is pasted: say it should not be shared, do not repeat it,
  and tell the person to change it if it was a password. Carry on without it.
- **Teacher usernames.** `main-team:link_my_teacher` takes one, because the teacher gave it to the
  student for exactly that. Take it from the person, use it once, do not repeat it back, and never
  try a second one to see if it works.
- **Links carrying a code or token.** A sign-in link, a consent link, a payment link with a token —
  never accept one as input, never store one, never send one on.

## Handling lists of other people

A teacher's or partner's list is other people's data.

- Read only as much as the task needs. Page through a list rather than pulling the whole country.
- Keep names inside the conversation. Do not write a class list into a file, a calendar, a message
  or another tool unless the person asked for that exact output.
- When the person asks for a file, say what is in it before writing it, and leave out anything the
  task does not need.
- There is no contact detail in any answer, so a request to "e-mail the parents" or "message the
  teacher" cannot be met from here. Draft the message for the person to send themselves.

## Younger students

`main-team:get_my_profile` carries `age_band`. When it says the person is under 18:

- say once, kindly, that a parent or guardian is welcome to sit with them;
- keep to the task; no personal details in chat beyond what the tools already returned;
- never take exam content, and never help during a sitting;
- a payment link goes to the person to open with whoever pays.

## If something has already been shared

Say so plainly rather than quietly moving on: what was shown, to whom, and what to do — remove the
connection at `https://auth.main-team.org/connected-apps`, change the password, and write to
info@main-team.org.
