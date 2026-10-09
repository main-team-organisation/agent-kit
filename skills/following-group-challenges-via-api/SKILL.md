---
name: following-group-challenges-via-api
description: "Follows a partner's own students through Main Team group challenges with the REST API: listing an olympiad's challenges with listGroupChallenges (GET /v1/{organizationId}/group-challenge), reading where each student stands with listGroupChallengeStudents and getGroupChallengeStudent, reading their groups, steps and files with listGroupChallengeGroups and getGroupChallengeGroup and the group's history with listGroupChallengeActivity, and submitting a step or a group's finished work for one of the partner's students with submitGroupChallengeStep and submitGroupChallengeWork. Explains that teachers form groups and members upload in the panel or the app, that only the partner's own students are named, which 409 reasons wait on the members, why a repeat answers changed false, and what a 503 busy means. Use when writing or fixing code that tracks group challenge progress, sends a student to a challenge page, or submits group challenge work for a student."
compatibility: "Needs an API account's apiKey and apiSecret on the machine that makes the calls, never in the conversation, and roles granting group-challenge/read, and group-challenge/submit for the submits, on the olympiad in the path. Group challenges answer 404 on an olympiad where they are not switched on."
metadata:
  author: "Main Team"
  docs: "https://hub.main-team.org/api/guides/group-challenges"
  api-version: "v1"
---

# Following students through group challenges

A **group challenge** is a project students do in small groups between two dates. A teacher forms
each group in the panel from their own students; the group works through the challenge's **steps**
in order, uploading its work for each step in the panel or the app, then sends its finished work.

Every route is per olympiad: `{organizationId}` is that olympiad's `_id` from
`GET /v1/organization`, never its slug. Tokens, envelopes and error codes belong to the
`integrating-main-team-api` skill.

## What the API does, and what it does not

- **Reads**: the challenges, where each of your students stands, the groups they are in, each step
  with its files, and what happened in a group.
- **Two writes**, for one of your students who is an active member of the group: submit the open
  step (`submitGroupChallengeStep`) and send the finished work (`submitGroupChallengeWork`).
- **Never**: create a group, add a student to one, or upload a file. Those stay with the teacher and
  the students. When a person asks for any of them, say so and offer the sign-in link instead.

## Read before you write

1. `listGroupChallenges` (`GET /v1/{organizationId}/group-challenge`): `isOpen` says whether a
   challenge takes work now; nothing is submitted outside `windowStart`–`windowEnd`.
2. `listGroupChallengeStudents` (`GET /v1/{organizationId}/group-challenge/{challengeId}/student`):
   each student's `state` (`not_eligible`, `not_in_group`, `group_pending`, `group_active`,
   `group_completed`), `teacherLinked`, their `group`, and `panelPath`.
3. `getGroupChallengeGroup`
   (`GET /v1/{organizationId}/group-challenge/{challengeId}/group/{groupId}`): each step's `state`
   and files, `canSubmit` per step and `canFinalSubmit` for the group. These are the answers a
   submit would get right now.

Only submit what `canSubmit` or `canFinalSubmit` says is ready.

## Submitting for a student

```bash
curl -sS -X POST \
  "https://apisnd.main-team.org/v1/$ORGANIZATION_ID/group-challenge/$CHALLENGE_ID/group/$GROUP_ID/step/$STEP_ID/submit" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{ "studentId": "'"$STUDENT_ID"'" }'
```

The body names the student you act for. The group's history records your account (`partner`,
`yours: true`) acting for them.

| Answer | Meaning | Do |
|---|---|---|
| `200`, `changed: true` | Submitted now | Read `nextStep`, if any |
| `200`, `changed: false` | It was already submitted, by anyone | Nothing; it is done |
| `409 conflict`, reason `step_empty` or `steps_incomplete` | The members' work is not there yet | Stop. Tell the person; never retry in a loop |
| `409 conflict`, any other reason | The challenge or the group is not ready, or closed | Stop. Nothing you send changes it |
| `404 not_found` | Not your student, not in this group, or no such step | Re-read the group; never guess ids |
| `503 service_unavailable`, reason `busy` | Someone is changing the group right now; nothing was written | Wait `Retry-After` (1 second), send it again once or twice |

Branch on `error.details.reason`, never on the message. Sending the finished work
(`POST .../group/{groupId}/final-submit`) **e-mails every member and the teacher**: confirm with the
person before you send it, and send it once.

Every reason, the order of the checks and what each side effect is:
[references/group-challenges.md](references/group-challenges.md).

## People you do not own

A group mixes your students with other schools' students and a teacher. Only your own students
come back named; everyone else is `{ "role": "student", "studentId": null, "name": null, "yours":
false }`, and a file's `name` is `null` unless your student uploaded it. Never try to work out who
they are, and keep names out of chat: report counts and states.

## Sending a student to the challenge

A student uploads in the panel or the app. To take them there, mint a sign-in link with
`createSigninLink` (`POST /v1/{organizationId}/auth/signin`) and pass the student's `panelPath` as
`redirect`, unchanged: `{userId}` in it is filled in by the link.

## Rules

- **Never upload, create groups or add members**: there is no operation for it.
- **Never loop on a 409.** `step_empty` and `steps_incomplete` wait on people.
- **Repeat safely.** After a timeout, send the same submit again and read `changed`.
- **Never submit for a student who is not yours**; the answer is `404`, as for an unknown id.
- **A `404 not_found` on every route of a running olympiad** means group challenges are not switched
  on there.

## References

- [references/group-challenges.md](references/group-challenges.md): the states, the order of the
  submit checks, every `details.reason`, the side effects, and the e-mail.
- [references/operations.md](references/operations.md): the operations this skill uses, with the
  permission each needs.
