<!-- Generated from the Main Team API contract 1.1.1 (https://hub.main-team.org/api/openapi.json). Do not edit: it is rebuilt with every release. -->

# Operations

The 18 operations this skill uses, of the Main Team API 1.1.1. Paths are relative to
`https://api.main-team.org` (production) or `https://apisnd.main-team.org` (sandbox).
`{organizationId}` is the organization's `_id` from `GET /v1/organization`, never its slug.
Each operation name links to its full reference: fields, examples and errors.

The permission is the role action an account needs, on `mto` for the core record or on the
organization in the path.

Every operation of the API is listed in the integrating-main-team-api skill.

## Reference data

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`listCountries`](https://hub.main-team.org/api/reference/list-countries) | `GET /v1/country` | List the countries a student can be registered in | `country/read` on `mto` |
| [`getCountry`](https://hub.main-team.org/api/reference/get-country) | `GET /v1/country/{id}` | Fetch one country by its id | `country/read` on `mto` |
| [`listGrades`](https://hub.main-team.org/api/reference/list-grades) | `GET /v1/grade` | List the grades a student can be registered with | `grade/read` on `mto` |
| [`getGrade`](https://hub.main-team.org/api/reference/get-grade) | `GET /v1/grade/{id}` | Fetch one grade by its id | `grade/read` on `mto` |
| [`listOrganizations`](https://hub.main-team.org/api/reference/list-organizations) | `GET /v1/organization` | List the organizations and their ids | `organization/read` on `mto` |
| [`getOrganization`](https://hub.main-team.org/api/reference/get-organization) | `GET /v1/organization/{id}` | Fetch one organization by its id | `organization/read` on `mto` |

## Students

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`listStudents`](https://hub.main-team.org/api/reference/list-students) | `GET /v1/student` | List your students | `student/read` on `mto` |
| [`registerStudent`](https://hub.main-team.org/api/reference/register-student) | `POST /v1/student` | Register a student | `student/create` on `mto` |
| [`checkStudentRegistration`](https://hub.main-team.org/api/reference/check-student-registration) | `POST /v1/student/check` | Check a registration without registering the student | `student/create` on `mto` |
| [`createStudentImport`](https://hub.main-team.org/api/reference/create-student-import) | `POST /v1/student/import` | Register many students at once | `student/create` on `mto` |
| [`getStudentImport`](https://hub.main-team.org/api/reference/get-student-import) | `GET /v1/student/import/{importId}` | Follow a batch of students you sent | `student/create` on `mto` |
| [`getStudent`](https://hub.main-team.org/api/reference/get-student) | `GET /v1/student/{studentId}` | Fetch one of your students | `student/read` on `mto` |
| [`updateStudent`](https://hub.main-team.org/api/reference/update-student) | `PUT /v1/student/{studentId}` | Update one of your students | `student/update` on `mto` |
| [`setStudentPassword`](https://hub.main-team.org/api/reference/set-student-password) | `PUT /v1/student/{studentId}/password` | Set the sign-in password of one of your students | `auth/signin` on `mto` |
| [`listOrgStudents`](https://hub.main-team.org/api/reference/list-org-students) | `GET /v1/{organizationId}/student` | List your students who can use this organization | `student/read` on the organization in the path |
| [`getOrgStudent`](https://hub.main-team.org/api/reference/get-org-student) | `GET /v1/{organizationId}/student/{studentId}` | Fetch one of your students, if they can use this organization | `student/read` on the organization in the path |
| [`updateOrgStudent`](https://hub.main-team.org/api/reference/update-org-student) | `PUT /v1/{organizationId}/student/{studentId}` | Update one of your students and give them access to this organization | `student/update` on the organization in the path |
| [`linkStudentSupervisor`](https://hub.main-team.org/api/reference/link-student-supervisor) | `PUT /v1/{organizationId}/student/{studentId}/supervisor` | Link one of your students to a supervisor on this organization | `student/update` on the organization in the path |
