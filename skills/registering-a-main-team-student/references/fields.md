<!-- Generated from the Main Team API contract 1.1.1 (https://hub.main-team.org/api/openapi.json). Do not edit: it is rebuilt with every release. -->

# Fields

The bodies one student goes through, exactly as the contract checks them. A field the
operation does not list is refused with `400`, so send documented fields only.

`country` and `grade` are looked up once and cached; `city` and `school` are matched by name
inside the country you send, and a name that matches nothing is refused. Nothing is ever
created for you.

## Contents

- [registerStudent (POST /v1/student)](#registerstudent-post-v1student)
- [checkStudentRegistration (POST /v1/student/check)](#checkstudentregistration-post-v1studentcheck)
- [updateStudent (PUT /v1/student/{studentId})](#updatestudent-put-v1studentstudentid)
- [setStudentPassword (PUT /v1/student/{studentId}/password)](#setstudentpassword-put-v1studentstudentidpassword)
- [What the check answers](#what-the-check-answers)

## registerStudent (POST /v1/student)

The registration itself. `201` answers with the student; keep `data._id`.

| Field | Required | Format | Meaning |
|---|---|---|---|
| `birth` | yes | string, `DD/MM/YYYY` | Date of birth as `DD/MM/YYYY`, and a date that exists: `31/02/2008` is refused. An ISO date such as `2008-05-14` is refused. |
| `city` | yes | string | The `_id` of a city, or its name within `country`, matched without regard to case. There is no list of cities to look one up in: send the name your records hold. One that matches no city is refused with 400; no city is ever created. |
| `country` | yes | string, an id of 24 hexadecimal characters | The `_id` of a country, from `listCountries` (`GET /v1/country`). An id only: a name or an ISO code is refused. Its two-letter code starts the student’s `username`. |
| `email` | yes | string, format email | The student’s email address, stored in lower case. An address belongs to one student on the whole platform, so one already registered, by your account or another, is refused with 409. |
| `firstName` | yes | string | The student’s first name. Printed on certificates and reports, followed by `lastName`. |
| `grade` | yes | string | The `_id` of a grade, from `listGrades` (`GET /v1/grade`), or its name, `1` to `12`. Either way the grade’s `_id` is what is stored. One that matches no grade is refused with 400. The grade decides which exams the student is offered. |
| `lastName` | yes | string | The student’s surname. Printed on certificates and reports after `firstName`. It cannot be empty. |
| `school` | yes | string | The `_id` of a school, or its name within `country` and `city`, matched without regard to case. There is no list of schools to look one up in: send the name your records hold. One that matches no school is refused with 400; no school is ever created. |
| `sex` | yes | one of `m`, `f`, `n` | One of `m`, `f` or `n`. |
| `activatedPlatformsThisSeason` | no | array of `common`, `stem`, `hilingua`, `neo`, `gmath`, `coding`, 0 to 6 | The organizations the student takes part in this season, by `slug` (as `listOrganizations` gives it, except `mto`: the core record, which every student is on), or `common` for every organization. Registration sets `["common"]` when you leave it out; `null` is refused with 400. At most 6 entries. |
| `email2` | no | string | Leave this out. Any value but an empty one is refused with 400. |
| `password` | no | string, at least 5 characters | The student’s sign-in password. Accepted only from an account that holds `auth/signin` on `mto`; from any other the registration is refused with 403. At least 5 characters, the minimum the sign-up form applies, and at most 72 bytes, and not containing the student’s own name or email address. Stored hashed, and never returned by any operation. Omit it to register the student without one. |
| `phone` | no | string | A phone number, stored as you send it. No format is checked. On an update, `""` clears it. |

## checkStudentRegistration (POST /v1/student/check)

The same body without `password`. It writes nothing and answers what registration would
refuse, the ids it resolved, and whether one of your own students already has the address.

| Field | Required | Format | Meaning |
|---|---|---|---|
| `birth` | yes | string, `DD/MM/YYYY` | Date of birth as `DD/MM/YYYY`, and a date that exists: `31/02/2008` is refused. An ISO date such as `2008-05-14` is refused. |
| `city` | yes | string | The `_id` of a city, or its name within `country`, matched without regard to case. There is no list of cities to look one up in: send the name your records hold. One that matches no city is refused with 400; no city is ever created. |
| `country` | yes | string, an id of 24 hexadecimal characters | The `_id` of a country, from `listCountries` (`GET /v1/country`). An id only: a name or an ISO code is refused. Its two-letter code starts the student’s `username`. |
| `email` | yes | string, format email | The student’s email address, stored in lower case. An address belongs to one student on the whole platform, so one already registered, by your account or another, is refused with 409. |
| `firstName` | yes | string | The student’s first name. Printed on certificates and reports, followed by `lastName`. |
| `grade` | yes | string | The `_id` of a grade, from `listGrades` (`GET /v1/grade`), or its name, `1` to `12`. Either way the grade’s `_id` is what is stored. One that matches no grade is refused with 400. The grade decides which exams the student is offered. |
| `lastName` | yes | string | The student’s surname. Printed on certificates and reports after `firstName`. It cannot be empty. |
| `school` | yes | string | The `_id` of a school, or its name within `country` and `city`, matched without regard to case. There is no list of schools to look one up in: send the name your records hold. One that matches no school is refused with 400; no school is ever created. |
| `sex` | yes | one of `m`, `f`, `n` | One of `m`, `f` or `n`. |
| `activatedPlatformsThisSeason` | no | array of `common`, `stem`, `hilingua`, `neo`, `gmath`, `coding`, 0 to 6 | The organizations the student takes part in this season, by `slug` (as `listOrganizations` gives it, except `mto`: the core record, which every student is on), or `common` for every organization. Registration sets `["common"]` when you leave it out; `null` is refused with 400. At most 6 entries. |
| `email2` | no | string | Leave this out. Any value but an empty one is refused with 400. |
| `phone` | no | string | A phone number, stored as you send it. No format is checked. On an update, `""` clears it. |

## updateStudent (PUT /v1/student/{studentId})

Every field is optional: send only what changes. An empty body changes nothing.

| Field | Required | Format | Meaning |
|---|---|---|---|
| `activatedPlatformsThisSeason` | no | array of `common`, `stem`, `hilingua`, `neo`, `gmath`, `coding`, 0 to 6 | Organization slugs, or 'common' for every organization, to add to the student's list. Nothing is ever removed: a value the list already holds is not added twice, and `[]` adds nothing. Leave it out and the list stays as it is. |
| `birth` | no | string, `DD/MM/YYYY` | Date of birth as `DD/MM/YYYY`, and a date that exists: `31/02/2008` is refused. An ISO date such as `2008-05-14` is refused. |
| `city` | no | string | The `_id` of a city, or its name within `country`, matched without regard to case. There is no list of cities to look one up in: send the name your records hold. One that matches no city is refused with 400; no city is ever created. |
| `country` | no | string, an id of 24 hexadecimal characters | The `_id` of a country, from `listCountries` (`GET /v1/country`). An id only: a name or an ISO code is refused. Its two-letter code starts the student’s `username`. |
| `email` | no | string, format email | The student’s email address, stored in lower case. An address belongs to one student on the whole platform, so one already registered, by your account or another, is refused with 409. |
| `email2` | no | string | Leave this out. Any value but an empty one is refused with 400. |
| `firstName` | no | string | The student’s first name. Printed on certificates and reports, followed by `lastName`. |
| `grade` | no | string | The `_id` of a grade, from `listGrades` (`GET /v1/grade`), or its name, `1` to `12`. Either way the grade’s `_id` is what is stored. One that matches no grade is refused with 400. The grade decides which exams the student is offered. |
| `lastName` | no | string | The student’s surname. Printed on certificates and reports after `firstName`. It cannot be empty. |
| `phone` | no | string | A phone number, stored as you send it. No format is checked. On an update, `""` clears it. |
| `school` | no | string | The `_id` of a school, or its name within `country` and `city`, matched without regard to case. There is no list of schools to look one up in: send the name your records hold. One that matches no school is refused with 400; no school is ever created. |
| `sex` | no | one of `m`, `f`, `n` | One of `m`, `f` or `n`. |

## setStudentPassword (PUT /v1/student/{studentId}/password)

Needs `auth/signin` on `mto`, not `student/update`. Prefer a sign-in link.

| Field | Required | Format | Meaning |
|---|---|---|---|
| `password` | yes | string, at least 5 characters | The student’s new sign-in password. At least 5 characters and at most 72 bytes, and not containing the student’s own first name, surname, username or email address, whatever the case. Stored hashed, and never returned by any operation. |

## What the check answers

The body of `checkStudentRegistration`’s `200`:

| Field | Required | Format | Meaning |
|---|---|---|---|
| `duplicate` | yes | object | Whether one of your students already has the address. |
| `problems` | yes | array of objects | Every reference field that matched nothing, in the order `country`, `grade`, `city`, `school`, and the country again when its students cannot be given a username. A city or school name inside a country or city that matched nothing is not looked up, so not listed. Empty when the email address is one of your students’. |
| `resolved` | yes | object | The `_id` each reference resolved to. All four are `null` when the email address is one of your students’: nothing is looked up then. |
| `valid` | yes | boolean | `true` when no student of yours has the email address and every reference resolved: `duplicate.sameAccount` is `false` and `problems` is empty. |

`problems` is a list of these:

| Field | Required | Format | Meaning |
|---|---|---|---|
| `field` | yes | one of `country`, `grade`, `city`, `school` | The field: `country`, `grade`, `city` or `school`. |
| `message` | yes | string | The message `registerStudent` answers `400 bad_request` with for this field. |

`duplicate` is this:

| Field | Required | Format | Meaning |
|---|---|---|---|
| `sameAccount` | yes | boolean | `true` when one of your students already has this email address, so `registerStudent` would answer `409 conflict`. |
| `studentId` | no | string | That student’s `_id`, only when `sameAccount` is `true`: the student to use instead of registering a second one. |
