# Discount codes

## What the check does and does not do

`main-team:check_discount_code` answers whether a code is usable **by this account, right now**, and
what it is worth. It reserves nothing, uses nothing up and changes nothing. The code is still typed
into the payment screen, by the person, when they pay.

```jsonc
{ "brand": "stem", "code": "SPRING25" }
//  -> { "valid": true, "kind": "rate", "amount": null, "amount_display": null, "currency": null,
//       "rate": 20, "rate_display": "20%", "applies_to": [ ... ] }
{ "brand": "stem", "code": "SPRING5" }
//  -> { "valid": true, "kind": "static", "amount": 5, "amount_display": "5.00 EUR", "currency": "EUR",
//       "rate": null, "rate_display": null, "applies_to": [ ... ] }
```

`categories` is an optional argument: pass the `category_id` values of the entries the person means,
and `applies_to` comes back scoped to those. Take the ids from `main-team:list_my_exams` or from
`main-team:find_exams_for_me`; do not invent one.

## Reading the answer

| Field | Meaning |
|---|---|
| `valid` | whether this account can use it now |
| `kind` | `static`, a fixed amount off, or `rate`, a percentage off |
| `rate` | the percentage, when that is the kind: 20 is 20% off |
| `rate_display` | the same percentage as text, "20%" |
| `amount` | the fixed amount, when that is the kind, in the currency's major unit: 5 is 5.00 EUR, never cents |
| `amount_display` | the same amount as text to quote, "5.00 EUR" |
| `applies_to` | the exam categories it covers |
| `currency` | the currency of a fixed amount; `null` for a rate code, which is a percentage, not money |

Report it plainly: "That code is 20% off, and it covers the Physics and Chemistry categories. Type it
in on the payment screen."

## `valid` false is an answer, not an error

A code that is unknown, expired, used up or meant for somebody else comes back with `valid` false.
The tool did not fail, and there is nothing to retry.

- Say it is not usable on this account, and stop.
- **Do not try variations** — upper case, no spaces, last year's code with a different number. That
  is guessing at somebody else's codes, and the connection's call budget is not there for it.
- Do not ask the student for another code unless they offer one.

## What the discount is worth in money

Work it out only when the person asks, only from numbers the tools returned, and say it is an
estimate of what the payment screen will show:

> "Chemistry is 25.00 EUR and the code is 20% off, so the screen should show about 20.00 EUR. The
> exact figure is whatever the payment page says."

Never promise a final price, and never promise that two codes stack or that one applies to an entry
`applies_to` does not list.

## Where a code is actually used

On the payment screen the link from `main-team:get_payment_link` opens. Nothing in this kit applies
a code, and no tool here can. If the code is refused there, that is between the person and the
payment screen; re-checking it with this tool will keep saying the same thing.

## Errors

`brand_not_allowed`, `role_required` and `tenant_account_missing` mean the account and the olympiad
do not line up — say which olympiads the connection covers. `rate_limited` means wait. Neither is a
reason to try the code again with a different `brand`.
