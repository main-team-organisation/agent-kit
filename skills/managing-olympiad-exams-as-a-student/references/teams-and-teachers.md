# Team invitations, and the student's teacher

## Answering an invitation

Another student can invite this one into a team entry. `main-team:respond_to_team_invitation` takes
the `application_id` of that team entry and `accept` true or false.

Say this **before** the dry run, every time:

> "Accepting can remove your own entry for the same exam, because one exam cannot be sat twice. An
> entry that is already under way is left alone."

Then the usual two steps: the first call answers `confirmation_required` with a summary; the same
call with `confirmation` goes ahead.

Only answer an invitation the student has actually told you about. The roster the platform gives
this service does not list invitations, so an id has to come from the student or from their panel —
and an id from anywhere else is a guess. If they cannot find it, send them to the panel with
`main-team:get_panel_link` and the page `my_exams`.

Declining costs nothing and changes nothing else. Accepting is the one worth slowing down for.

## The teacher

A linked teacher can see this student's results and certificates and can enter them for exams. That
is worth saying out loud both when linking and when unlinking.

### Is there one?

`main-team:get_my_teacher` with the `brand` reports `linked`. The platform does not currently return
the teacher's name through this route, so a linked student may come back with nothing more than
"linked" — that is a gap, not an error. Send them to the panel to see who it is.

### Linking

`main-team:link_my_teacher` takes `teacher_username`, which the **teacher** gives the student for
exactly this purpose.

- Ask the student for it. Never guess one, and never try a second if the first is not found.
- Use it once, in the call. Do not repeat it back into the conversation and do not keep it.
- The first call answers `confirmation_required`; the same call with `confirmation` links them.
- `not_found` means no teacher holds that username on that olympiad. Say so and stop.

### Unlinking

`main-team:unlink_my_teacher` cannot be undone from here: the teacher stops seeing the student's
results at once, and re-linking needs the teacher's username again. Exam entries and payments are
untouched. The student themselves has to confirm; an app that cannot ask gets a panel link and
nothing happens.

## Where this stops

There is no tool to invite somebody into a team, to add a student to a teacher's list from the
student's side beyond the link above, or to message anybody. If the student wants any of those,
send them to the panel.
