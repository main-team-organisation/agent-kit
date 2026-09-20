# Country, grade, city and school

## Contents

- [Two kinds of reference](#two-kinds-of-reference)
- [Countries](#countries)
- [Grades](#grades)
- [Cities and schools](#cities-and-schools)
- [Organizations](#organizations)
- [When a name matches nothing](#when-a-name-matches-nothing)
- [Caching](#caching)

## Two kinds of reference

| | Has a list you can read | Field takes |
|---|---|---|
| Country | Yes: `listCountries` (`GET /v1/country`) | The `_id` only |
| Grade | Yes: `listGrades` (`GET /v1/grade`) | The `_id`, or the name `1` to `12` |
| City | **No** | The `_id`, or a name inside `country` |
| School | **No** | The `_id`, or a name inside `country` and `city` |
| Organization | Yes: `listOrganizations` (`GET /v1/organization`) | Its `_id` in the path |

The API never creates reference data. Nothing you send to any route adds a country, a grade, a city
or a school, so a value that matches nothing is refused rather than invented.

## Countries

`GET /v1/country` is paginated like every list: `page` from 1, `limit` 20 by default and 100 at
most, and it has no guaranteed order. Page through all of it once and index it yourself, by `name`
and by `iso2`.

The field takes the `_id` and nothing else. A name or an ISO code in `country` is `400 bad_request`.
`getCountry` (`GET /v1/country/{id}`) reads one when you already hold an id.

The country's two-letter code starts the student's username, which the platform generates.

## Grades

`GET /v1/grade` lists them. `grade` takes either the `_id` or the plain name `1` to `12`; either
way the grade's `_id` is stored. Anything else is `400`.

The grade decides which exams the student is offered, so it is worth getting right rather than
approximating: a student entered in the wrong grade is offered the wrong papers.

## Cities and schools

There is no directory to search. Send the name your own records hold, and the API matches it inside
the country (and, for a school, the city) you sent, without regard to case.

That has two consequences worth planning for:

- **You cannot list a country's schools**, so you cannot offer the person a picker built from the
  API. Build it from your own data.
- **A school that is not there yet has to be added by Main Team.** Ask through support with the
  country, the city and the exact name; do not work around it by putting the school in the city
  field or by registering the student under a neighbouring school.

## Organizations

`GET /v1/organization` answers the olympiads with their `_id`, `name` and `slug`. Every
`/v1/{organizationId}/…` path takes the **`_id`**. A slug such as `stem` in the path is
`404 not_found` with the message `Organization not found!`, which reads exactly like a real missing
record, so check the id first when you see it.

Slugs are what `activatedPlatformsThisSeason` takes. So the same olympiad is named two ways: by
slug in the access list, by id in the path. Keep both in the cache.

## When a name matches nothing

`checkStudentRegistration` (`POST /v1/student/check`) is the cheap way to find out. Its `problems`
name the field, and its `resolved` block shows exactly which country, grade, city and school the
API matched — worth reading even when the row is valid, because it catches the row that resolved to
the *wrong* school.

At registration the same refusal is `400 bad_request` and the message names the field. Do not retry
it: fix the value, or ask the person. Guessing a nearby name registers the child at another school.

## Caching

Countries, grades and organizations change between seasons, not between requests. Read them once
when a job starts, hold them in memory or in your own table, and refresh at most daily. Each list is
its own operation with its own budget of 100 requests per 60 seconds, and a job that re-reads the
country list per student wastes both the budget and the time.
