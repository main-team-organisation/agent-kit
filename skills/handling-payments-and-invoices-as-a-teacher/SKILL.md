---
name: handling-payments-and-invoices-as-a-teacher
description: "Helps a teacher (supervisor account) on a Main Team olympiad — stem, hilingua, neo, gmath or coding — deal with their class's exam fees through the main-team MCP server: finding which of their students' entries are unpaid and what each costs, checking whether a discount code is usable and what it is worth, building one panel cart link that covers up to twenty entries at once, removing an unpaid entry that is not going to be paid, reading the payments already made, and listing the teacher's own invoices. Explains that no money moves through an AI app and no tool marks anything paid, that the coding olympiad's cart takes one entry at a time while the others take twenty, that an amount somebody else paid comes back hidden, that invoice documents are downloaded in the panel and some countries have none, and what payment_required and not_allowed_here mean. Use when a teacher asks who still owes, how to pay for a class, whether a code works, or where an invoice is."
license: Apache-2.0
metadata:
  audience: "supervisor"
---

# Handling payments and invoices as a teacher

**No money moves here.** These tools read, and one of them builds a link into the teacher's own
panel cart. The teacher pays there, in their browser.

Every tool this skill uses: [references/tools.md](references/tools.md).

## Who still owes

There is no "unpaid entries" tool. Build the list from the roster:

1. `main-team:list_my_students` with the `brand`, paged, optionally by `grade`. Each student's
   entries carry `paid` and `application_id`.
2. Collect the entries where `paid` is false.
3. `main-team:get_student` for one student when the teacher wants the detail of just that one.

Report it as a summary and offer the detail:

> "Grade 9 on gmath: 6 unpaid entries across 5 students, 150.00 EUR in total. Shall I list them?"

Add up only the amounts the tool returned, in the `currency` it gave. Never convert, never estimate,
never guess a fee that was not read.

## Paying for several at once

`main-team:get_students_payment_link` takes `application_ids` — up to **twenty** — and answers a
`url` that opens the teacher's own cart with those entries in it, plus a `count`.

**The coding olympiad's cart takes one entry at a time.** Every other olympiad takes up to twenty.
Plan for that before promising a single link.

Hand the link over with what it covers and what it costs, and then stop. Do not open it, store it,
shorten it, forward it or put it in a file.
[references/carts-and-links.md](references/carts-and-links.md).

## Discount codes

`main-team:check_discount_code` with the `brand` and the `code` says whether it is usable by **this
account** and what it is worth — `valid`, `kind`, `rate` or `amount`, `applies_to`. Pass
`categories` to scope the answer to the categories the class is entered for.

It reserves nothing and uses nothing up; the code is typed in on the payment screen. `valid` false
is an answer, not a failure — report it and do not try variations of the code.

## Entries that will not be paid

`main-team:remove_unpaid_exam` removes one unpaid entry from one student, with its pending payment.
A paid or sat entry cannot be removed here at all. It cannot be undone, so the teacher themselves has
to confirm it and an app that cannot ask them gets a panel link; re-entering later is a new entry at
whatever the fee then is. One entry, one confirmation — never a blanket yes over a list.

## Confirming and recording

- Only a fresh read shows a fee paid: `main-team:list_my_students` or `main-team:get_student` with
  `paid` true. A link having been created means nothing.
- `main-team:list_my_payments` lists what this teacher has paid, and for whom. An amount somebody
  else paid comes back as `amount_hidden` — say "paid by somebody else" rather than guessing a
  number.
- `main-team:list_my_invoices` lists this teacher's invoices: `student_count`, `amount`, `currency`
  and `date`. The document itself is not available through an AI app, and some countries have no
  invoices at all, so an empty list is a normal answer.
  [references/invoices.md](references/invoices.md).

## Rules

- No tool here takes a payment, opens a card screen or marks anything paid. A request to "just mark
  it paid" cannot be met; say so.
- Never say a fee is paid before a read shows it.
- No card, bank or payment reference belongs in the conversation. If one is pasted, say so and do
  not repeat it.
- Money figures are other people's business: keep a per-student breakdown in the conversation or in
  a file the teacher asked for, not in a message to anybody else.
- Never take, start or answer an exam.
- Anything that has to be finished by hand: `main-team:get_panel_link`, page `my_students`.
