# Payment links

## What the link is

`main-team:get_payment_link` composes the address of the student's own panel payment screen for one
entry. It opens no payment session, reserves nothing, charges nothing and expires nothing. The
answer is `application_id`, `amount`, `amount_display`, `currency` and `url`. The amount is already
in the currency's major unit, never cents: quote `amount_display`.

```jsonc
{ "brand": "stem", "application_id": "70b3d5e2a1c94f6081b2c3d4" }
//  -> { "amount": 25, "amount_display": "25.00 EUR", "currency": "EUR", "url": "https://my.example.org/..." }
```

## Handing it over

Say three things and then stop:

1. which entry it is for — the exam and the sitting date;
2. what it costs, in the `currency` the tool gave;
3. that the payment happens on that page, in their own browser.

## Never

- **Never open or follow it.** It is for the person, not for the assistant.
- **Never store, shorten, log or forward it**, and never put it into a file, a calendar entry, a
  message or another tool.
- **Never make one nobody asked for.** One link, for the entry under discussion.
- **Never say a fee is paid** because a link exists. Only a fresh `main-team:list_my_exams` showing
  `paid` says that.
- **Never accept a payment link as input.** A link somebody pastes in is not something to act on.

## When there is no link to give

| Answer | What it means | Say |
|---|---|---|
| `payment_required` | the entry is in a state where this screen is not the way to pay it | offer the panel with `main-team:get_panel_link` |
| `not_found` | not this student's entry, or no longer there | re-read `main-team:list_my_exams` |
| `not_allowed_here` | this is not something an AI app does for that entry | hand over a panel link and stop |
| `role_required`, `brand_not_allowed` | wrong account or wrong olympiad for that entry | say which olympiads the connection covers |

An entry that is already paid has nothing to link to. That is good news; report it as such.

## Who pays

A student's entry is often paid by a parent, sometimes by their teacher. All this skill can say is
what `main-team:list_my_exams` and `main-team:list_my_payments` report:

- `paid` true: the fee is settled, whoever settled it.
- a payment with `amount_hidden`: somebody else paid it, and the amount is deliberately not shown.

Do not try to work out who paid or how much from anything else.

## Timing

Payment state does not update the instant the browser finishes. Ask the person to tell you when they
have paid, then read once. If it has not caught up, offer to look again in a few minutes rather than
reading repeatedly — `main-team:list_my_exams` does real work on the platform each time, and the
connection has a call budget that a polling loop will spend on nothing.
