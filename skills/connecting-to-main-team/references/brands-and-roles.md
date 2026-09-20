# Olympiads and roles

## The five olympiads

Every tool that acts on one olympiad takes `brand`, one of these slugs:

| Slug | The olympiad |
|---|---|
| `stem` | the science and mathematics olympiad |
| `hilingua` | the languages olympiad |
| `neo` | the natural sciences olympiad |
| `gmath` | the mathematics olympiad |
| `coding` | the programming olympiad |

`brand` may be left out only when the connection covers exactly one of them. Otherwise pass it, and
pass a slug `main-team:whoami` returned: a slug outside the connection answers `brand_not_allowed`
and nothing happens.

## One person, different roles

A role is per olympiad. The same person can be a student on one and a teacher on another, and a
partner is a teacher with a wider view on the olympiads where they hold it. So:

- do not carry an assumption from one olympiad to the next;
- when a task spans two olympiads, do each one in turn and say which one you are in;
- when a tool answers `role_required`, that account does not hold the needed role **on that
  olympiad**. Do not try the other olympiads to find one where it works.

## What differs between them

These are the platform's own rules, not this app's. They show up as refusals, so it is worth knowing
them before promising anything.

- **Languages.** Only `stem` offers the same exam in more than one language, so
  `main-team:list_exam_language_options` and `main-team:change_exam_language` answer
  `not_allowed_here` anywhere else.
- **Paying for several entries at once.** On `coding` the panel's cart takes one entry at a time;
  the other four take up to twenty. `main-team:get_students_payment_link` follows that rule.
- **Study materials.** Some olympiads publish none, and then
  `main-team:list_study_materials` simply answers an empty list. That is not an error.
- **Prices and currency.** Each olympiad prices in its own currency; the fee comes back with the
  exam, so quote what the tool returned rather than converting anything.

## The identity, and what it is not

The account itself lives across all five olympiads, which is why one sign-in covers the ones the
person ticked. There is no sixth olympiad slug for the account itself, and no tool takes one: the
account is reached through `main-team:whoami` and `main-team:get_my_profile`, which take no `brand`.

## A role that changes mid-connection

If the person is promoted, moved between schools or has their partner scope changed, the tools
answer `role_changed` from then on. Nothing was done. The person approves the connection again at
`auth.main-team.org`, and the work starts over from a fresh `main-team:whoami`.
