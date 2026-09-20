---
name: connecting-to-main-team
description: "Opens and steers every session against the Main Team MCP server (main-team), through which a signed-in student, teacher (supervisor) or partner of the Main Team olympiads — stem, hilingua, neo, gmath and coding — lets an AI app act with exactly the rights of their own panel. Covers calling main-team:whoami first, telling the person which account, which olympiads and whether changes were approved, choosing the brand slug every other tool needs, routing to the right task skill for their role, adding the server at mcp.main-team.org and signing in at auth.main-team.org, how long a connection lasts, and how it is ended. Use at the start of any Main Team task done through the MCP server, when an app asks the person to sign in again, when a tool answers not_connected, reconsent_required, role_changed, insufficient_scope or brand_not_allowed, and when somebody asks what this assistant may or may not do on their Main Team account."
license: Apache-2.0
metadata:
  audience: "student, supervisor, partner"
---

# Connecting to Main Team

The Main Team MCP server acts for **one signed-in person**, with exactly the rights of their own
panel. It is the olympiad platform behind stem, hilingua, neo, gmath and coding. There is no
administrative connection, no service account and no way to reach anybody else's account.

Load the skill `staying-safe-with-main-team` as well before changing anything.

## 1. Start every session with `whoami`

Call `main-team:whoami` before any other tool. In most apps the tool appears as
`mcp__main-team__whoami` or `mcp__plugin_main-team_main-team__whoami`; the name after the last
underscores is the one written here.

It answers:

| Field | What it decides |
|---|---|
| `principal` | student, or staff (a teacher or a partner) — which task skill applies |
| `brands` | the olympiad slugs this connection covers, and the role held on each |
| `scopes` | whether changes were approved at all |
| `can_change` | whether this app may change anything now |
| `limited` | for a partner: whether their view is the whole country or only linked teachers |
| `access_expires_at` | when the person will have to reconnect |

Then say one sentence back to the person: whose account, which olympiads, and whether this app may
change anything. If any of it is not what they expect, stop and ask before going further.

Details and the exact opening lines: [references/session-start.md](references/session-start.md).

## 2. Pick the brand, never guess it

Almost every tool takes `brand`: one of `coding`, `gmath`, `hilingua`, `neo`, `stem`. Use a slug
`whoami` returned. It may be left out only when the connection covers exactly one olympiad.

A person's role can differ per olympiad — a teacher on one, a student on another. Work one olympiad
at a time and say which one you are in. See
[references/brands-and-roles.md](references/brands-and-roles.md).

## 3. Route to the task skill

| The person is | Their task | Skill |
|---|---|---|
| a student | entering, moving or cancelling exams | `managing-olympiad-exams-as-a-student` |
| a student | fees, discount codes, payment links | `paying-olympiad-fees-as-a-student` |
| a student | scores, reports, certificates | `reviewing-results-and-certificates-as-a-student` |
| a student | past papers, calendar, announcements | `preparing-for-olympiads-as-a-student` |
| a teacher | their student list and exam entries | `managing-students-as-a-teacher` |
| a teacher | sittings, results, certificates | `following-student-results-as-a-teacher` |
| a teacher | paying for a class, invoices | `handling-payments-and-invoices-as-a-teacher` |
| a partner | their country's students and unpaid entries | `managing-country-students-as-a-partner` |
| a partner | the teachers they work with | `working-with-teachers-as-a-partner` |

Every one of them assumes `whoami` has already been called.

## 4. What this connection will never do

Say so plainly when asked, and never look for a way round it:

- It will never **take, start or answer an exam**, or help with exam content while one is under
  way. No tool exists for it, on purpose.
- It never returns a username, a student or teacher code, an e-mail address, a phone number or a
  date of birth. A student is an opaque handle such as `stu_x7k2m9p4`, a study paper a handle such
  as `mat_q4w8e1r5`.
- It never returns a report or certificate file, and there is no shareable verification link.
- It never moves money. A payment tool answers a link that opens the person's own panel.
- It never changes a password, an e-mail address or profile details.
- It never acts for anybody but the person who approved it.

## 5. Connecting, reconnecting and disconnecting

The one server address is `https://mcp.main-team.org/mcp`. Adding it opens
`auth.main-team.org`, where the person signs in, ticks the olympiads and decides whether the app
may change anything. Step-by-step per app:
[references/connecting-an-app.md](references/connecting-an-app.md).

- `not_connected` or an app asking to sign in again: the connection ended. Tell the person to
  connect again at `auth.main-team.org`; do not retry the tool.
- `reconsent_required` or `role_changed`: something about the account changed since it was
  approved. The person approves again; then start the task over.
- `insufficient_scope`: reading was approved, changing was not. Offer a panel link instead, or ask
  them to reconnect and allow changes. Do not retry.
- To disconnect: `main-team:disconnect_this_app`, or the person's own connected-apps page at
  `https://auth.main-team.org/connected-apps`. Signing out of the website does not end a
  connection.

Every error code and what to do about it: [references/errors.md](references/errors.md). Every tool
this connection may hold: [references/tools.md](references/tools.md).

## 6. Pace

The server allows about sixty calls a minute and a few thousand a day per connection, and far fewer
changes. That is generous for real work and tight for a loop. Read a list once and work from it;
do not poll, and do not re-read something after every single change.
