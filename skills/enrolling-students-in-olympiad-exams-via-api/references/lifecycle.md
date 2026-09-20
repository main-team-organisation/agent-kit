# The life of an application

## Contents

- [Create](#create)
- [What a new application contains](#what-a-new-application-contains)
- [Payments](#payments)
- [Move](#move)
- [Withdraw](#withdraw)
- [Safe to repeat, precisely](#safe-to-repeat-precisely)

## Create

`createApplication` (`POST /v1/{organizationId}/application`) takes
`{"studentId": "...", "examId": "..."}` and nothing else.

```bash
curl -sS -X POST "https://apisnd.main-team.org/v1/$ORGANIZATION_ID/application" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -H "X-Request-Id: $(uuidgen)" \
  -d '{"studentId":"652f1c9b8e4b2a0012a3c4d5","examId":"64a1f0b2c9d8e7f600112233"}'
```

`201` created it. `200` with "Application already exists." means it was already there, and the body
is that application. Both are success; branch on the status if you are counting new entries.

The checks run in a fixed order, and each refusal names its rule. The ones worth designing around:
the student must be yours, the olympiad must hold a copy of them (their first sign-in there), the
exam must be open, the grade and country must be accepted, and the student must not already hold
another exam in that category on that sitting.

## What a new application contains

The answer is the stored application, with more fields than you need. The ones to keep:

| Field | Use |
|---|---|
| `_id` | The `{applicationId}` for a move, a delete or a single read |
| `exam` | The exam it is for |
| `user` | The olympiad's copy of the student, not the core `_id` |
| `payment` | The payment record; read it for `status` and `amount` |
| `participated`, `examSubmitted` | Whether the student has started or handed in the paper |

Match a student across olympiads on `mainId`, the core record's `_id`, not on `user`.

## Payments

The API records what an entry costs and whether it was paid. It **never takes, charges or refunds
money.** Payment happens in the olympiad panel.

| `price` on the exam | The new application's payment |
|---|---|
| absent or `0` | `amount: 0`, `status: "paid"` — free, and settled from the start |
| a number above 0 | `amount: <price>`, `status: "pending"` |

**Settled** means `status` is `paid` **and** `amount` is above `0`: somebody actually paid. A free
exam's settled-looking payment is not settled, so it never blocks a move or a delete.

Never tell a person a fee is paid until a read shows it. Never offer a refund: there is no operation
that makes one.

## Move

`moveApplication` (`PUT /v1/{organizationId}/application/{applicationId}`) with `{"examId": "..."}`
changes which exam an entry is for — another language, another sitting, another category.

| Situation | What happens to the payment |
|---|---|
| Not settled | Rewritten to the new exam's price; `paid` if that is `0`, `pending` otherwise |
| Settled, same price | Only the exam changes; the amount paid stays as it was |
| Settled, different price | **Refused with `409`**: the API can neither charge the difference nor refund it |

So a paid application is not frozen — changing the language of a paid exam at the same price is an
ordinary move — but a move that would change what the money bought is refused.

Moving from a free exam to a priced one leaves the student owing the new price: their payment goes
from `paid, amount 0` to `pending`. Say so before you make that move.

A started exam (`participated` or `examSubmitted`) can no longer be moved.

## Withdraw

`deleteApplication` (`DELETE /v1/{organizationId}/application/{applicationId}`) removes the entry
**for good**. There is no undo and no archive.

It is refused with `409` when the payment is settled, because deleting refunds nothing and would
leave money that bought something nobody can find. Cancelling a paid sitting is a refund, and
refunds happen outside this API.

Before deleting, read `participated` and `examSubmitted`, and get a clear yes from the person for
each entry you are about to remove. Deleting a class's entries is not a batch operation to run
first and report afterwards.

## Safe to repeat, precisely

- `createApplication` never creates a second entry for the same student and exam. But the exam
  checks run **before** the "already exists" check, so a repeat answers `200` only while the exam is
  still offered to that student. After the sitting, or after the student's grade changed, the same
  request answers `409` — and the existing application is untouched either way.
- `moveApplication` to the exam the application already has answers `200` and writes nothing.
- `deleteApplication` deletes once; a repeat answers `404 not_found`. Treat that `404` as "already
  gone" only when you know the application existed.

After any `409` on a retry, list the student's applications
(`GET /v1/{organizationId}/application/student-applications/{studentId}`) and read the state from
the API rather than inferring it.
