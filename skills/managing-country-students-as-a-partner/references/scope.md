# What this partner may see

## Full and limited

`main-team:whoami` carries `limited`.

| | What the roster answers |
|---|---|
| a **full** partner | every registered student of their country on that olympiad |
| a **limited** partner | the students of the teachers linked to them |

The platform decides. There is no argument that widens it, no second tool that sees further, and a
record outside the scope answers `not_found` — the same answer as a record that does not exist, on
purpose.

Say which one applies before giving a figure:

> "Your connection is a limited partner view on neo, so these numbers cover the students of the
> teachers linked to you, not the whole country."

## Per olympiad

Partner status is per olympiad. The same person can be a full partner on one, a limited partner on
another, and only a teacher on a third. Work one `brand` at a time, and re-read `main-team:whoami`
rather than assuming last week's answer still holds. If the role changed since the connection was
approved, every tool answers `role_changed` and the person approves the connection again.

## What is deliberately withheld

These are not missing features. The panel withholds them from a partner too, and this connection
matches the panel.

| Not available | What to say |
|---|---|
| a student's exam result | "A partner does not see individual results, here or in the panel." |
| statistics: registrations, payments, trends, charts, past seasons | "There are no partner statistics through this connection." |
| invoices | "Partner invoices are not available here." |
| marking a fee paid without money | "Nothing here marks an entry paid. Payment happens on the panel's own screen." |
| any identifier of a person | "No username, student code, e-mail address or phone number is ever returned." |
| an official report or certificate file, or a link anyone could open | "Official documents stay in the panel." A certificate copy made for AI use is the one file there is, and only where the connection offers it. |

If a partner needs one of these, the answer is the panel, or Main Team. Do not assemble a
substitute: a "statistics report" built by paging the whole roster, or out of the whole-list
table, is exactly the thing the platform declined to give, and it puts a country's worth of other
people's data into a conversation.

## Reading no more than the question needs

- Filter with `grade` and `search` rather than pulling everything.
- For a count or a lookup, page, and stop when the question is answered. For the whole list, or an
  export the partner asked for, `main-team:export_student_list` — once, following `next_from` — and
  the rows go into the file, not the conversation.
- For "how many", read the answer's `total` instead of paging to the end: `list_country_students`
  carries the size of the whole scope, under the `grade` asked for, whenever no `search` was sent.
  With a `search` there is no `total`, and a full page only means "ask for the next one".
- Summarise in counts. A total, a per-grade breakdown, a per-teacher count — those answer most
  questions without naming anybody.
- Name students only when the partner is acting on those particular students.

## Certificates

`main-team:get_student_certificate` reads one certificate belonging to a student this partner is
responsible for, when the partner pastes the id at the end of its panel certificate link as
`certificate_id` — the roster tools do not hand certificates out. The answer names it by an opaque
`certificate` value (`crt_…`), never by the id, and its `view_url` is the Applications page, the
nearest page to it. It does not open the certificate there: the certificate buttons on that page
point to a page the panel does not have yet, so do not tell the partner the certificate opens from
the link. The official file never comes back, and there is no shareable verification link.

When the partner asks for that certificate as a file and the connection offers it,
`main-team:get_certificate_copy` with the `certificate` value attaches a PDF copy made for AI use:
the olympiad, the title, the student's name, the subject, the sitting and the date, and no user ID,
student code, QR code, document number or verification link. Say it is a copy, not the official
certificate, and that it cannot be verified. One per call, for the certificate asked about — never a
copy of every certificate in scope. `status: "open_in_panel"` with `reason: "copy_unavailable"`
means that one cannot be copied.

## When the scope and the question do not line up

A partner asking about a student who is not in their scope gets `not_found`. Say what that means and
stop:

> "That student is not in the scope this connection covers, so I cannot read anything about them.
> If they should be, their teacher's link to you is the thing to check."

Do not search the roster for a near-match, and do not try the same read on another olympiad.
