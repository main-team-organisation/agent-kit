# Invoices and payment history

## Invoices

```jsonc
main-team:list_my_invoices { "brand": "gmath", "page": 1 }
//  -> invoices: student_count, amount and amount_display (major units, never cents), currency, date
```

Each row says how many students the invoice covers, what it came to and when it was issued. Quote
`amount_display` ("300.00 EUR") as it stands. That is the whole of what is available.

- **The document is not available through an AI app.** No PDF, no link to one in the answer. The
  teacher downloads it from their panel; `main-team:get_panel_link` with the page `my_students`
  gets them there.
- **Some countries have no invoices at all**, and then the list is simply empty. Say that as a
  possibility rather than treating an empty list as a fault.
- **Nothing here changes an invoice.** No address, no tax details, no re-issue. Those are panel work
  or a conversation with Main Team.

When a teacher asks for "my invoices for this season", read the pages and summarise:

> "Four invoices on gmath this season: 12 students in October (300.00 EUR), 8 in November, 15 in
> January and 6 in March. The PDFs are on your panel's page — here is the link."

## Payment history

```jsonc
main-team:list_my_payments { "brand": "gmath" }
//  -> payments: amount and amount_display (major units, never cents) or amount_hidden, currency, date, exam, session_date, category_id
```

It lists the payments **on this account**: the ones this teacher made for their students.

`amount_hidden` means somebody else paid that one — a parent, a partner — and the amount is
deliberately not shown. Report it as "paid by somebody else"; do not reconstruct the figure from the
entry's `price`, and do not imply you know who paid.

There is no payment reference, no card detail and no transaction id in any answer, and none should
ever be asked for or repeated.

## Reconciling

A teacher wanting to tie payments to students is doing arithmetic over two reads:
`main-team:list_my_students` for who is entered and `paid`, and `main-team:list_my_payments` for
what has been paid. Do it when asked, and say what it is:

> "By my count from these two lists: 22 entries for the March sitting, 18 paid by you, 2 paid by
> somebody else, 2 still unpaid. That is my arithmetic over what the tools returned, not an official
> statement of account."

Never present it as an official figure, and never write it into anything that looks like a receipt
or an invoice.

## What to do about money questions this cannot answer

Refunds, tax, a wrong amount, a payment that does not appear: none of them has a tool here. Say so,
and point at the panel and at Main Team. Do not guess at policy, and do not promise a refund, a
correction or a deadline.
