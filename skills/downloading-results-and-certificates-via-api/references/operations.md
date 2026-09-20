<!-- Generated from the Main Team API contract 1.1.1 (https://hub.main-team.org/api/openapi.json). Do not edit: it is rebuilt with every release. -->

# Operations

The 4 operations this skill uses, of the Main Team API 1.1.1. Paths are relative to
`https://api.main-team.org` (production) or `https://apisnd.main-team.org` (sandbox).
`{organizationId}` is the organization's `_id` from `GET /v1/organization`, never its slug.
Each operation name links to its full reference: fields, examples and errors.

The permission is the role action an account needs, on `mto` for the core record or on the
organization in the path.

Every operation of the API is listed in the integrating-main-team-api skill.

## Documents

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`downloadCertificate`](https://hub.main-team.org/api/reference/download-certificate) | `GET /v1/{organizationId}/certificate/download/{certificateId}` | Download a certificate file | `certificate/read` on the organization in the path |
| [`listStudentCertificates`](https://hub.main-team.org/api/reference/list-student-certificates) | `GET /v1/{organizationId}/certificate/{userId}` | List one of your students’ released certificates | `certificate/read` on the organization in the path |
| [`downloadReport`](https://hub.main-team.org/api/reference/download-report) | `GET /v1/{organizationId}/report/download/{reportId}` | Download a result report file | `report/read` on the organization in the path |
| [`listStudentReports`](https://hub.main-team.org/api/reference/list-student-reports) | `GET /v1/{organizationId}/report/{userId}` | List one of your students’ released result reports | `report/read` on the organization in the path |
