# The teachers a partner works with

## Listing them

```jsonc
main-team:list_supervisors { "brand": "neo", "page": 1, "limit": 50 }
//  -> supervisors: name, school, city, joined_at
```

A `search` narrows it, and it matches **names**. A limited partner sees only the teachers linked to
them; a full partner sees their country's. `main-team:whoami` says which, in `limited`.

## No contact details, anywhere

The answer carries no e-mail address, no phone number, no username and no code — for the teacher or
for anybody else. So:

- nothing in this kit can e-mail, message or call a teacher;
- a request to "send them a reminder" cannot be met, however it is phrased;
- do not try to reconstruct an address from a name and a school, and do not look one up elsewhere on
  the partner's behalf without being asked to;
- the useful answer is a **draft** the partner sends themselves, from their own account.

> "I can write the message for you to send. There are no contact details in what this connection
> returns, so nothing here can send it."

## Finding a teacher's class

There is no teacher id to filter by. `main-team:list_country_students` names, on each student row,
the teacher that student belongs to — so a teacher's class comes from the roster:

1. `main-team:list_supervisors` with a `search` to confirm the name as the platform spells it;
2. `main-team:list_country_students`, paged, optionally by `grade`;
3. group the rows by the teacher named on each.

For one student in full, `main-team:get_student` with their handle.

Page rather than pulling everything. A partner asking "how is Ms Ramírez doing" wants counts —
students, entries, how many unpaid — not a list of children.

## What `joined_at` is good for

It is when the teacher joined, and it answers "who is new this season" without reading anybody's
students:

> "Four teachers joined neo since September: two in Lagos, one in Ibadan, one in Kano."

Do not infer activity, quality or effort from it, and do not rank teachers.

## What cannot be done from here

- add a teacher, remove one, or link or unlink one to this partner;
- change what a teacher may do, or their scope;
- see a teacher's invoices, their own certificates, or anything of their account beyond the list
  above;
- see a student's exam result — a partner does not get those, here or in the panel.

All of it is panel work or a conversation with Main Team. Say so plainly rather than looking for
another tool.

## Errors

| Answer | Meaning |
|---|---|
| an empty list | no teacher is in this partner's scope on that olympiad |
| `role_required` | this account is not a partner on that olympiad |
| `brand_not_allowed` | the connection does not cover that olympiad |
| `tenant_account_missing` | this account has no profile on that olympiad yet |
| `rate_limited` | wait; do not page faster |
