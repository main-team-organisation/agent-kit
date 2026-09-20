# Changelog

The agent kit carries the Main Team MCP server’s version. Every release is listed at
https://hub.main-team.org/ai.

## 1.0.0 - 2026-09-18

The first release of the Main Team MCP server. Everything below is new, so nothing in it can break
anything a client could already do; from here on this file carries only what changed.

### Added

- **The server.** `https://mcp.main-team.org/mcp`, MCP over HTTP, for a student's, a teacher's or a
  partner's own AI client. One connection belongs to one person: there is no account, key or secret to
  obtain, and nobody can connect on someone else's behalf.
- **Signing in.** The client sends the person to `auth.main-team.org`, where they sign in the same way they
  sign in to the panel and then read a consent screen that names the application, the brands it will reach,
  what it may read, what it may change and what it can never do. A student additionally confirms that they
  are 18 or that a parent approved, and may connect only an application whose publisher Main Team has
  verified. Every connection sends the person an e-mail.
- **OAuth 2.1**, discoverable at `/.well-known/oauth-authorization-server` (RFC 8414) and
  `/.well-known/oauth-protected-resource` (RFC 9728), with `/oauth/authorize`, `/oauth/token`,
  `/oauth/revoke` (RFC 7009) and `/oauth/register` (RFC 7591). PKCE is S256 or nothing, `resource` is
  required and is `https://mcp.main-team.org/mcp`, and the issuer comes back per RFC 9207. The scopes are
  `mcp:read` and `mcp:write`; there is no `offline_access`.
- **Tokens.** An access token good for 15 minutes and bound to this server, and a refresh token that rotates
  on every use — reusing an old one ends the whole connection. A teacher's or partner's connection lasts 30
  days idle and 90 days in all; a student's 14 and 30. The person ends it whenever they like, from Connected
  apps in the panel or with `disconnect_this_app`; changing their password ends it too.
- **41 tools** — 30 that only read, 7 that change something, and 4 that cannot be undone. A tool that
  changes something answers first with a summary and a single-use confirmation handle, and does the work only
  when it is called again with that handle. A tool that cannot be undone asks the person directly, and where
  the client cannot ask, it returns a panel link and does nothing. Each skill's `references/tools.md` lists
  the tools of its audience with their arguments; `references/errors.md` lists every code a call can answer.
- **What a student can do**: see their exams, find the exams they are eligible for, add one, change or
  cancel one, answer a team invitation, get the link to pay in the panel, read study material, the calendar,
  announcements and notifications, read their own results and certificates, and connect or disconnect their
  teacher.
- **What a teacher can do**: work their own student list, look a student up, find the exams a student is
  eligible for, add exams for up to 50 students at a time, remove an unpaid entry, remove a student from
  their list, read a student's result or certificate, list exam sessions, hand over one payment link for many
  students, and read their own invoices. Removing an unpaid entry and removing a student from the list are
  both changes that cannot be undone, so both ask the teacher themselves.
- **What a partner can do**: the same over the students of their country, plus their teachers. A partner
  whose account is limited to certain teachers sees exactly those teachers' students and nothing beyond them.
- **Paying happens in the panel.** The payment tools return a link that opens the person's own cart; no
  payment is ever started from a chat.
- **What never leaves the server.** No username, no student or teacher code, no reference code, no other
  person's e-mail, telephone number or date of birth, no payment or transaction identifier, no file address,
  no certificate verification link, and no result or certificate document. Text a person typed into a record
  comes back marked as data, trimmed, and is never an instruction for the model.
- **The agent kit**: eleven skills — `connecting-to-main-team` and `staying-safe-with-main-team` for
  everybody, four for a student, three for a teacher, two for a partner — with the tool and error references
  generated from the catalogue, and ten client manifests.

### Changed

- **BREAKING — `remove_unpaid_exam` is a tool that cannot be undone.** It was going to ask through the same
  two-step confirmation as an ordinary change; it now asks the person themselves, like cancelling an entry or
  removing a student from a list, and an application that cannot put the question to them gets a panel link
  and does nothing. It deletes the entry, the payment waiting on it and everything recorded against it, which
  is exactly what a student's own cancellation does — and that has always been in the stricter class. An
  application that expected a confirmation handle back from the first call gets
  `{"status": "open_in_panel", "url": …}` instead — a plain answer, not an error, with nothing done.

### Not included, deliberately

- Sitting an exam, and everything near one.
- Uploads, AI Lab, Grand Final, exam bucks, messaging and bulk downloads.
- Changing a password, an e-mail address or a profile, and minting any kind of credential.
- Result and certificate documents, and the public verification link.
- Anything administrative: a connection acts for the person who approved it and for nobody else.

### Known limits

- `get_student_result` and `get_student_certificate` need the record's id, which the person reads from the
  panel: the roster tools do not answer one yet.
