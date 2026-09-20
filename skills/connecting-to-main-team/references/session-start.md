# Starting a session

## The first call, always

```text
main-team:whoami          (no arguments, changes nothing, costs almost nothing)
```

Call it even when the person's question looks simple. Every other tool needs a `brand` slug that
only `whoami` supplies, and a tool missing from what it reports is one this person's role cannot
reach — trying it anyway spends a call and answers an error.

## What to say back

One sentence, before anything else happens. Name the account by the first name the connection
carries, never by a username or any code.

- A student, changes allowed:
  > "You are connected as Lina, as a student on stem and hilingua. I can enter and change exams, and
  > I will show you each change before it happens."
- A teacher, reading only:
  > "You are connected as Mr Adeyemi, as a teacher on gmath. This app was approved for reading only,
  > so I can look at your students and their entries but cannot change anything."
- A partner with a limited view:
  > "You are connected as Sofia, as a partner on neo. Your view covers the teachers linked to you
  > rather than the whole country."

## When to stop instead of continuing

- The role is not the one the person describes. A person who says "my students" but is connected as
  a student has either the wrong account or the wrong olympiad open.
- The olympiad they are asking about is not in `brands`. Say which ones the connection covers and
  ask them to reconnect if they want another.
- `can_change` is false and the task is a change. Say so now, not after four read calls.
- `access_expires_at` is in the past or minutes away. Ask them to reconnect first.

## Their own details

`main-team:get_my_profile` reads the person's own account: grade, country, city, school, whether
the e-mail address is confirmed, that address with most of it hidden, and `age_band`. It changes
nothing, and the link it returns is where the person edits their details themselves.

Call it when a task needs the person's own grade or school — not as a matter of routine, and never
to repeat their details back to them unasked.

If `age_band` says the person is under 18, say once that a parent or guardian is welcome to sit with
them, and keep to it: no exam content, no personal details in chat, nothing shared outside the
conversation.

## Between sessions

Nothing is remembered on the server between conversations except the connection itself. Handles
(`stu_`, `mat_`) are sealed to one connection: a handle from a previous session, or from another
app, means nothing here. Always take handles from a list read in this session.
