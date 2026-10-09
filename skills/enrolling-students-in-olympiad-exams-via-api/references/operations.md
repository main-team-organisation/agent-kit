<!-- Generated from the Main Team API contract 1.2.0 (https://hub.main-team.org/api/openapi.json). Do not edit: it is rebuilt with every release. -->

# Operations

The 12 operations this skill uses, of the Main Team API 1.2.0. Paths are relative to
`https://api.main-team.org` (production) or `https://apisnd.main-team.org` (sandbox).
`{organizationId}` is the organization's `_id` from `GET /v1/organization`, never its slug.
Each operation name links to its full reference: fields, examples and errors.

The permission is the role action an account needs, on `mto` for the core record or on the
organization in the path.

Every operation of the API is listed in the integrating-main-team-api skill.

## Exams

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`listExams`](https://hub.main-team.org/api/reference/list-exams) | `GET /v1/{organizationId}/exam` | List the exams open for applications | `exam/read` on the organization in the path |
| [`listExamCategories`](https://hub.main-team.org/api/reference/list-exam-categories) | `GET /v1/{organizationId}/exam-category` | List an organization’s exam categories | `exam-category/read` on the organization in the path |
| [`getExamCategory`](https://hub.main-team.org/api/reference/get-exam-category) | `GET /v1/{organizationId}/exam-category/{categoryId}` | Fetch one exam category | `exam-category/read` on the organization in the path |
| [`listAvailableExams`](https://hub.main-team.org/api/reference/list-available-exams) | `GET /v1/{organizationId}/exam/available/{studentId}` | List the exams one of your students can apply to | `exam/read` on the organization in the path |
| [`getExam`](https://hub.main-team.org/api/reference/get-exam) | `GET /v1/{organizationId}/exam/{examId}` | Fetch one exam that is open for applications | `exam/read` on the organization in the path |

## Applications

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`listApplications`](https://hub.main-team.org/api/reference/list-applications) | `GET /v1/{organizationId}/application` | List your students’ applications in this organization | `application/read` on the organization in the path |
| [`createApplication`](https://hub.main-team.org/api/reference/create-application) | `POST /v1/{organizationId}/application` | Enter one of your students for an exam | `application/create` on the organization in the path |
| [`listExamApplications`](https://hub.main-team.org/api/reference/list-exam-applications) | `GET /v1/{organizationId}/application/exam-applications/{examId}` | List your students’ applications for one exam | `application/read` on the organization in the path |
| [`listStudentApplications`](https://hub.main-team.org/api/reference/list-student-applications) | `GET /v1/{organizationId}/application/student-applications/{studentId}` | List one of your students’ applications in this organization | `application/read` on the organization in the path |
| [`deleteApplication`](https://hub.main-team.org/api/reference/delete-application) | `DELETE /v1/{organizationId}/application/{applicationId}` | Withdraw one of your students from an exam | `application/delete` on the organization in the path |
| [`getApplication`](https://hub.main-team.org/api/reference/get-application) | `GET /v1/{organizationId}/application/{applicationId}` | Fetch one of your students’ applications | `application/read` on the organization in the path |
| [`moveApplication`](https://hub.main-team.org/api/reference/move-application) | `PUT /v1/{organizationId}/application/{applicationId}` | Move one of your students’ applications to another exam | `application/update` on the organization in the path |
