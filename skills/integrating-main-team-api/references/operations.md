<!-- Generated from the Main Team API contract 1.1.1 (https://hub.main-team.org/api/openapi.json). Do not edit: it is rebuilt with every release. -->

# Operations

The 38 operations of the Main Team API 1.1.1. Paths are relative to
`https://api.main-team.org` (production) or `https://apisnd.main-team.org` (sandbox).
`{organizationId}` is the organization's `_id` from `GET /v1/organization`, never its slug.
Each operation name links to its full reference: fields, examples and errors.

The permission is the role action an account needs, on `mto` for the core record or on the
organization in the path.

## Health

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`getHealth`](https://hub.main-team.org/api/reference/get-health) | `GET /v1/health` | Check that the API is up | none (no token) |

## API account

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`revokeToken`](https://hub.main-team.org/api/reference/revoke-token) | `POST /v1/api-account/revoke-token` | Revoke the token you send, before it expires | `api/*` on `mto` |
| [`getCurrentApiAccount`](https://hub.main-team.org/api/reference/get-current-api-account) | `GET /v1/api-account/validate-me` | Fetch the API account your token belongs to | `api/*` on `mto` |

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

## Sign-in links

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`createSigninLink`](https://hub.main-team.org/api/reference/create-signin-link) | `POST /v1/{organizationId}/auth/signin` | Create a single-use sign-in link for one of your students | `auth/signin` on the organization in the path |

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

## Documents

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`downloadCertificate`](https://hub.main-team.org/api/reference/download-certificate) | `GET /v1/{organizationId}/certificate/download/{certificateId}` | Download a certificate file | `certificate/read` on the organization in the path |
| [`listStudentCertificates`](https://hub.main-team.org/api/reference/list-student-certificates) | `GET /v1/{organizationId}/certificate/{userId}` | List one of your students’ released certificates | `certificate/read` on the organization in the path |
| [`downloadReport`](https://hub.main-team.org/api/reference/download-report) | `GET /v1/{organizationId}/report/download/{reportId}` | Download a result report file | `report/read` on the organization in the path |
| [`listStudentReports`](https://hub.main-team.org/api/reference/list-student-reports) | `GET /v1/{organizationId}/report/{userId}` | List one of your students’ released result reports | `report/read` on the organization in the path |
