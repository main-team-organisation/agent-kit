<!-- Generated from the Main Team API contract 1.2.0 (https://hub.main-team.org/api/openapi.json). Do not edit: it is rebuilt with every release. -->

# Operations

The 10 operations this skill uses, of the Main Team API 1.2.0. Paths are relative to
`https://api.main-team.org` (production) or `https://apisnd.main-team.org` (sandbox).
`{organizationId}` is the organization's `_id` from `GET /v1/organization`, never its slug.
Each operation name links to its full reference: fields, examples and errors.

The permission is the role action an account needs, on `mto` for the core record or on the
organization in the path.

Every operation of the API is listed in the integrating-main-team-api skill.

## Sign-in links

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`createSigninLink`](https://hub.main-team.org/api/reference/create-signin-link) | `POST /v1/{organizationId}/auth/signin` | Create a single-use sign-in link for one of your students | `auth/signin` on the organization in the path |

## Group challenges

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`listGroupChallenges`](https://hub.main-team.org/api/reference/list-group-challenges) | `GET /v1/{organizationId}/group-challenge` | List the group challenges an organization runs | `group-challenge/read` on the organization in the path |
| [`getGroupChallenge`](https://hub.main-team.org/api/reference/get-group-challenge) | `GET /v1/{organizationId}/group-challenge/{challengeId}` | Fetch one group challenge | `group-challenge/read` on the organization in the path |
| [`listGroupChallengeGroups`](https://hub.main-team.org/api/reference/list-group-challenge-groups) | `GET /v1/{organizationId}/group-challenge/{challengeId}/group` | List the groups your students are in for a group challenge | `group-challenge/read` on the organization in the path |
| [`getGroupChallengeGroup`](https://hub.main-team.org/api/reference/get-group-challenge-group) | `GET /v1/{organizationId}/group-challenge/{challengeId}/group/{groupId}` | Fetch one group, with its steps and files | `group-challenge/read` on the organization in the path |
| [`listGroupChallengeActivity`](https://hub.main-team.org/api/reference/list-group-challenge-activity) | `GET /v1/{organizationId}/group-challenge/{challengeId}/group/{groupId}/activity` | List what has happened in one group | `group-challenge/read` on the organization in the path |
| [`submitGroupChallengeWork`](https://hub.main-team.org/api/reference/submit-group-challenge-work) | `POST /v1/{organizationId}/group-challenge/{challengeId}/group/{groupId}/final-submit` | Send a group’s finished work for one of your students | `group-challenge/submit` on the organization in the path |
| [`submitGroupChallengeStep`](https://hub.main-team.org/api/reference/submit-group-challenge-step) | `POST /v1/{organizationId}/group-challenge/{challengeId}/group/{groupId}/step/{stepId}/submit` | Submit one step of a group for one of your students | `group-challenge/submit` on the organization in the path |
| [`listGroupChallengeStudents`](https://hub.main-team.org/api/reference/list-group-challenge-students) | `GET /v1/{organizationId}/group-challenge/{challengeId}/student` | List your students’ eligibility and groups for a group challenge | `group-challenge/read` on the organization in the path |
| [`getGroupChallengeStudent`](https://hub.main-team.org/api/reference/get-group-challenge-student) | `GET /v1/{organizationId}/group-challenge/{challengeId}/student/{studentId}` | Fetch one of your students’ eligibility and group for a group challenge | `group-challenge/read` on the organization in the path |
