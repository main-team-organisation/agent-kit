# Group challenges in detail

## Contents

- [Challenges](#challenges)
- [Where a student stands](#where-a-student-stands)
- [Groups and steps](#groups-and-steps)
- [The submit checks, in order](#the-submit-checks-in-order)
- [Side effects](#side-effects)
- [Busy groups](#busy-groups)

## Challenges

A challenge is listed while it is `published`, and after it is `closed`; one that is not published
is not listed and answers `404`. `isOpen` is true only while it is `published` and now is between
`windowStart` and `windowEnd` (UTC, both inclusive). `gradeGroups` say which grades take part: every
member of a group comes from the same grade group. `minStudents` and `maxStudents` bound a group.

## Where a student stands

`listGroupChallengeStudents` lists your students activated for the olympiad and signed in to it
once; `getGroupChallengeStudent` answers one student, activated or not, and `409 conflict` for one
who has never signed in there.

| `state` | Meaning | What moves it on |
|---|---|---|
| `not_eligible` | Grade in no grade group | A corrected grade, if it was wrong |
| `not_in_group` | Eligible, in no group | The teacher adds them; `teacherLinked: false` means link a teacher first (`linkStudentSupervisor`) |
| `group_pending` | In a group the teacher is still preparing | The teacher confirms the group |
| `group_active` | In a confirmed group | The group submits every step, then the work |
| `group_completed` | The work has been sent | Nothing |

A group wins over the grade. New values may be added: treat one you do not know as "nothing to do
yet".

## Groups and steps

`listGroupChallengeGroups` lists the groups any of your students is an active member of.
A group is `awaiting_payment` or `draft` while the teacher prepares it, `finalized` once confirmed
(steps open one by one), `completed` once its work is sent. Steps exist only once `finalized`.

A step is `locked` until the one before it is submitted, `open` while the group works on it, and
`submitted` once sent. Its files are `uploading`, `draft` (uploaded) or `submitted`.

`listGroupChallengeActivity` is the history every member can read, newest first. Your own submits
show as `actor.role: partner` with `yours: true` and the student in `onBehalfOf`.

## The submit checks, in order

The first that fails decides the answer, and nothing is written for any of them.

1. The student is yours (`404 not_found`) and has signed in to the olympiad once (`409 conflict`).
2. The challenge exists and is published or closed (`404 not_found`).
3. The group belongs to the challenge, and the student is an active member (`404 not_found`).
4. Already done: `200` with `changed: false`.
5. The challenge is published (reason `challenge_closed`) and inside its dates (reason
   `window_closed`, with `windowStart` and `windowEnd` in `details`).
6. The teacher has confirmed the group (reason `payment_pending` or `group_not_confirmed`).
7. Step submit: the group has the step (`404 not_found`), it is open (reason `step_locked`), and a
   file was uploaded for it (reason `step_empty`). Final submit: every step is submitted (reason
   `steps_incomplete`, with `stepsSubmitted` and `stepCount`).

Steps 5 to 7 answer `409 conflict` with the reason in `error.details.reason`.

## Side effects

- **Step submit**: the step becomes `submitted` with its uploaded files; an upload still running for
  it is stopped; the next step opens.
- **Final submit**: the group becomes `completed`, and every member and the teacher receive an
  e-mail saying the group has sent its work. Confirm with the person first, and send it once.

## Busy groups

A group is changed by one request at a time, from the panel, the app or the API. `503 service_unavailable` with
`details.reason: busy` and `Retry-After: 1` means someone was changing it at that moment and nothing
was written. Wait the second and send the same request again; the answer then says whether it was
already done (`changed: false`).
