# One address, one student

## Contents

- [The rule](#the-rule)
- [What the check tells you first](#what-the-check-tells-you-first)
- [The 409, decided](#the-409-decided)
- [After a timeout](#after-a-timeout)
- [What never to do](#what-never-to-do)

## The rule

An email address belongs to **one student on the whole platform**, across every olympiad and every
API account. `registerStudent` (`POST /v1/student`) answers `409 conflict` when the address is
taken, whoever holds it.

The API deliberately does not tell you who holds an address that is not yours. That is not an
oversight to work around: it is how another school's roster stays private from yours.

## What the check tells you first

`checkStudentRegistration` (`POST /v1/student/check`) writes nothing and answers a `duplicate`
block:

| `duplicate.sameAccount` | `duplicate.studentId` | Meaning |
|---|---|---|
| `false` | absent | The address is free, or held by somebody outside your account |
| `true` | the student's `_id` | One of **your** students already has it |

Read it together with `valid`: a row can be invalid for a field reason and hold a duplicate at the
same time, and the check reports both in one round trip.

The check is not a reservation. A row it passes can still be refused at registration if someone
registers that address in between, so treat it as a way to find problems early, never as a lock.

## The 409, decided

```
409 conflict on POST /v1/student
│
├── Is the student one of yours?  (the check's duplicate.sameAccount, or listStudents by email)
│   │
│   ├── Yes ──► Do not register again.
│   │            getStudent (GET /v1/student/{studentId}) reads them.
│   │            updateStudent (PUT /v1/student/{studentId}) corrects the record and
│   │            adds olympiads through activatedPlatformsThisSeason.
│   │
│   └── No  ──► You cannot register this address, and you cannot find out who has it.
│                Ask the person for the address that student actually uses, or, if they
│                believe the record is theirs, have the two accounts settle it with Main
│                Team support. Nothing in the API transfers a student between accounts.
│
└── Was this a repeat of a request whose answer you never saw?  See below.
```

The message of a `409` for a student of your own carries their `_id`. Parse it only as a
convenience; `listStudents` (`GET /v1/student`) filtered by the address is the supported way to find
the record, and it is the one to use when the message shape changes.

## After a timeout

`registerStudent` is not idempotent, so an answer you never saw leaves a real question: was the
student written?

1. Ask: `GET /v1/student` filtered by that address.
2. A student in the answer means the registration worked. Keep the `_id` and move on.
3. No student means it did not. Send the registration once more.

Sending it again without asking is also defensible — the `409` tells you the same thing — but only
if you treat "409, and the student is mine" as success rather than as an error to report.

## What never to do

- **Never register the same person under a second address** to get past a `409`. Two records for
  one child split their applications, their results and their certificates, and nothing merges them
  afterwards.
- **Never loop on a `409`.** Nothing about the request will change.
- **Never guess who holds an address**, and never tell the person you work for that a particular
  school or account has it. The API did not say so.
- **Never fabricate an address** (`firstname.lastname.2@…`) to make a row register. A wrong address
  means the welcome email, the sign-in links and the results all go to someone else.
- **Never paste the address into chat** to discuss the conflict. Quote the row number.
