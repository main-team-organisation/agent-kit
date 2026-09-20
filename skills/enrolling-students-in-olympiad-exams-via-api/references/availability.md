# What a student may sit

## Contents

- [How an exam is put together](#how-an-exam-is-put-together)
- [What open means](#what-open-means)
- [The picker](#the-picker)
- [Why an exam is missing](#why-an-exam-is-missing)
- [The catalogue routes](#the-catalogue-routes)

## How an exam is put together

An exam has no name. It is one **category** (a subject), on one **session** (a sitting on a date),
in one **language**. Describe it to a person by those three: "Science, 14 November 2026, English".

| Part | Fields that matter |
|---|---|
| Category | `name`, `order`, `isActive`, `nonAcceptedReplacements` |
| Session | `date`, `sessionName`, `startTime`, `tz`, `relatedSession` |
| Language | `name`, `code` |
| Exam | `session`, `category`, `language`, `grades`, `countries`, `price`, `preventApplication` |

`grades` are the grades that may sit it; an empty list is offered to nobody. `countries` restricts
it, and an empty or absent list means every country. `price` is **absent** on an unpriced exam, so
read it as `price ?? 0`. A session with `relatedSession` is a make-up sitting linked to a main one.

## What open means

An exam is open when all three hold:

1. `preventApplication` is not `true`;
2. the sitting's `date` is still in the future;
3. the category is active (`isActive: true`).

Only the `date` decides; `startTime`, `tz` and `duration` never do. The list, the single read, the
picker and both writes use this one rule, so there is no way to reach a closed exam: you cannot
list it, read it, apply to it or move onto it.

The student panel stops offering a sitting an hour before its `date`; the API keeps offering it
until the `date` itself, so that the list and the write always agree. If a person has to act on
what you show them, add your own buffer — hide sittings less than a day away.

## The picker

`listAvailableExams` (`GET /v1/{organizationId}/exam/available/{studentId}`) is the panel's own
per-student picker. It is not paginated, and it answers a tree: categories, then sittings, then
languages, each leaf carrying `matchedExam` with the `_id` to apply to and the price.

Take `examId` from `matchedExam._id`. Nothing else is a supported source of an exam id.

The picker has already applied:

- the student's grade against `grades`;
- the student's country against `countries`;
- whether the exam is open;
- exams the student already has, and the categories a sitting will not take twice.

So an empty tree means "nothing is on offer for this student right now", which is an answer to
report, not a failure to retry.

## Why an exam is missing

| The person expected | Likely reason |
|---|---|
| A sitting they saw last week | Its `date` has passed, or `preventApplication` was set |
| A subject the school teaches | The category is not active on that olympiad, or has no exam on that sitting |
| A paper in another language | No exam exists for that category, sitting and language |
| Anything at all, for one student | Their grade or country is not accepted, or they already hold an entry in that category on that sitting |
| Anything at all, for every student | Check the `{organizationId}`: a slug in the path answers `404 not_found` |

Compare the picker with `listExams` (`GET /v1/{organizationId}/exam`) before telling anyone an exam
does not exist: an exam open for the olympiad and missing from one student's picker is a rule about
that student, not about the exam.

## The catalogue routes

| Operation | What it answers |
|---|---|
| `listExams` `GET /v1/{organizationId}/exam` | Every open exam of the olympiad, paged |
| `getExam` `GET /v1/{organizationId}/exam/{examId}` | One open exam |
| `listExamCategories` `GET /v1/{organizationId}/exam-category` | **Every** category, retired ones included: check `isActive` |
| `getExamCategory` `GET /v1/{organizationId}/exam-category/{categoryId}` | One category |

None of them writes anything, and none of them knows about a student. They are for building a
catalogue and for turning ids into names; the picker is for deciding what one student may sit.

The answers carry every stored field, more than any of these tables lists. Ignore what you do not
use, and never branch on a field's absence alone.
