<!-- Generated from the Main Team API contract 1.1.1 (https://hub.main-team.org/api/openapi.json). Do not edit: it is rebuilt with every release. -->

# Columns

The fields one row of `createStudentImport` takes, and the spreadsheet headers
`scripts/roster.py` maps to each. Headers are compared in lower case, without accents, spaces
or punctuation. Anything else in the list is left out and reported.

A row is `registerStudent`'s body without `password`, with the same rules: no password
is ever read from a list, and a column called one is refused by the API. Students get a
password through a sign-in link or "forgot password".

`email2` is not in the table either: the contract refuses any value for it, so no column ever
maps to it.

## One row

| Field | Required | Format | Meaning | Headers the script recognizes |
|---|---|---|---|---|
| `birth` | yes | string, `DD/MM/YYYY` | Date of birth as `DD/MM/YYYY`, and a date that exists: `31/02/2008` is refused. An ISO date such as `2008-05-14` is refused. | birth, date of birth, birth date, birthdate, birthday, dob, geburtsdatum, date de naissance, fecha de nacimiento, dogum tarihi, data urodzenia |
| `city` | yes | string | The `_id` of a city, or its name within `country`, matched without regard to case. There is no list of cities to look one up in: send the name your records hold. One that matches no city is refused with 400; no city is ever created. | city, town, stadt, ville, ciudad, sehir, il, miasto |
| `country` | yes | string, an id of 24 hexadecimal characters | The `_id` of a country, from `listCountries` (`GET /v1/country`). An id only: a name or an ISO code is refused. Its two-letter code starts the student’s `username`. | country, country id, land, pays, pais, ulke, kraj |
| `email` | yes | string, format email | The student’s email address, stored in lower case. An address belongs to one student on the whole platform, so one already registered, by your account or another, is refused with 409. | email, e-mail, email address, mail, e posta, eposta |
| `firstName` | yes | string | The student’s first name. Printed on certificates and reports, followed by `lastName`. | first name, firstname, given name, forename, vorname, prenom, nombre, ad, isim, imie |
| `grade` | yes | string | The `_id` of a grade, from `listGrades` (`GET /v1/grade`), or its name, `1` to `12`. Either way the grade’s `_id` is what is stored. One that matches no grade is refused with 400. The grade decides which exams the student is offered. | grade, class, year, klasse, classe, curso, sinif, klasa |
| `lastName` | yes | string | The student’s surname. Printed on certificates and reports after `firstName`. It cannot be empty. | last name, lastname, surname, family name, nachname, nom, apellido, apellidos, soyad, soyadi, nazwisko |
| `school` | yes | string | The `_id` of a school, or its name within `country` and `city`, matched without regard to case. There is no list of schools to look one up in: send the name your records hold. One that matches no school is refused with 400; no school is ever created. | school, school name, schule, ecole, escuela, okul, szkola |
| `sex` | yes | one of `m`, `f`, `n` | One of `m`, `f` or `n`. | sex, gender, geschlecht, sexe, genero, sexo, cinsiyet, plec |
| `activatedPlatformsThisSeason` | no | array of `common`, `stem`, `hilingua`, `neo`, `gmath`, `coding`, 0 to 6 | The organizations the student takes part in this season, by `slug` (as `listOrganizations` gives it, except `mto`: the core record, which every student is on), or `common` for every organization. Registration sets `["common"]` when you leave it out; `null` is refused with 400. At most 6 entries. | platforms, platform, olympiads, olympiad, organizations, olimpiyat |
| `externalRef` | no | string, at most 64 characters | Your own reference for this row, echoed back when you read the import. Not stored on the student and not required to be unique. At most 64 characters. | (set by the script) |
| `phone` | no | string | A phone number, stored as you send it. No format is checked. On an update, `""` clears it. | phone, phone number, mobile, telephone, tel, telefon, telefono |

## What the script reads

A single full-name column (headers: full name, fullname, student name, name surname, ad soyad, adi soyadi, name) is split at the last space, which the
report marks. `country` must be an id: the script keeps a country name aside, and `build`
replaces it using the map written from `listCountries` (`GET /v1/country`). `birth` is
written as `DD/MM/YYYY` from `YYYY-MM-DD`, `DD.MM.YYYY`, `DD/MM/YYYY` (or `MM/DD/YYYY`
with `--dates mdy`) and Excel date numbers. `grade` is written as `1` to `12` from values
such as `5`, `5th` or `Grade 5`.

`sex` is read from these words: `m` from "m", "male", "boy", "man", "mannlich", "masculin", "masculino", "erkek", "e", "chlopiec"; `f` from "f", "female", "girl", "woman", "weiblich", "feminin", "femenino", "kiz", "kadin", "k", "dziewczynka"; `n` from "n", "x", "other", "non-binary", "nonbinary", "divers", "diger".

`externalRef` is not a column: the script writes its own reference for each row (`row 7`,
or `Sheet1!7`), the API echoes it back, and the report uses it to find the line again.
