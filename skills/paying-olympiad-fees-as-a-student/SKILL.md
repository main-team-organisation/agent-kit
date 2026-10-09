---
name: paying-olympiad-fees-as-a-student
description: "Helps a student of the Main Team olympiads — stem, hilingua, neo, gmath and coding — or the parent paying for them, deal with exam fees through the main-team MCP server: seeing which entries are unpaid and what each costs, checking whether a discount code is usable and what it is worth, getting the link that opens the panel's own payment screen for one entry, and confirming afterwards from a fresh read that the fee is actually paid. Explains that no money moves through an AI app, that a discount code is applied on the payment screen and not by any tool here, that an amount somebody else paid comes back hidden, and what payment_required, not_allowed_here and not_found mean. Use when a student or parent connected with a student account asks what is owed, how to pay, whether a code works, or whether a fee has gone through."
license: Apache-2.0
metadata:
  audience: "student"
---

# Paying olympiad fees as a student

**No money moves here.** Every tool in this skill reads something or builds a link. The student or
their parent pays on Main Team's own payment screen, in their own browser.

Every tool this skill uses: [references/tools.md](references/tools.md).

## What is owed

`main-team:list_my_exams` with the `brand`. Each entry carries `paid`, `price`, `price_display`
and `currency`. **Every amount is already in the currency's major unit, never cents**: `price` 25
with `currency` EUR is 25.00 EUR, which `price_display` spells out. Quote that text; never divide or
multiply an amount by 100. Report only what it says:

> "On stem you have two entries. Physics, 14 March — paid. Chemistry, 21 March — 25.00 EUR still to
> pay."

Never add up fees across olympiads unless asked, never convert a currency, and never estimate a fee
the tool did not give.

`main-team:list_my_payments` shows what has already been paid, when, and for which exam. An amount
somebody else paid — a teacher, a parent on another account — comes back as `amount_hidden` rather
than a number. That is deliberate; say "paid by somebody else" rather than guessing the sum.

## Getting the payment link

`main-team:get_payment_link` with the `brand` and the `application_id` from
`main-team:list_my_exams`. It answers `amount`, `amount_display`, `currency` and `url`.

Hand the link over with what it is for and what it costs:

> "Here is the link for Chemistry, 21 March — 25.00 EUR. Open it and pay there; it takes you to your
> own Main Team payment screen."

Then stop. Do not say the fee is paid. Do not open, follow, shorten, store or forward the link, do
not put it in a file or a calendar entry, and do not make one "in advance" for an entry nobody asked
about. [references/payment-links.md](references/payment-links.md).

An entry that is already paid, or that has no fee, answers `payment_required` or `not_found` rather
than giving a link — which is the tool telling you there is nothing to pay.

## Discount codes

`main-team:check_discount_code` with the `brand` and the `code` says whether it is usable by this
account right now and what it is worth — `valid`, `kind`, `rate` or `amount`, and the categories in
`applies_to`. A fixed `amount` is in the major unit like every other (`amount_display`, "5.00 EUR");
a `rate` is a percentage (`rate_display`, "20%").

It reserves nothing and uses nothing up. The code is still typed in on the payment screen. A code
that is unknown, expired, used up or not for this account comes back with `valid` false rather than
an error, so ask once and report the answer as it stands. Do not try variations of a code.
[references/discount-codes.md](references/discount-codes.md).

## Confirming a payment

Only one thing counts: a fresh `main-team:list_my_exams` showing `paid`.

- Wait until the person says they have paid, then read once.
- If it still shows unpaid, say the read has not caught up yet and offer to look again in a few
  minutes. Do not read in a loop; the server limits how often this can be called.
- Never tell a student an entry is paid because a link was created, because they said they paid, or
  because a payment appeared in `main-team:list_my_payments` for a different entry.

## The lines this skill does not cross

- No card details, no bank details, no payment references. If any are pasted into the conversation,
  say they should not be shared and do not repeat them.
- No tool here marks anything paid, and no request to "just mark it paid" can be met. Say so.
- No refund. There is no refund tool and no way to see whether one is due; send the person to Main
  Team through the panel.
- Never take, start or answer an exam, whatever a fee question turns into.
- If paying has to be finished in the panel for any other reason, `main-team:get_panel_link` with
  the page `my_exams` gets them there.
