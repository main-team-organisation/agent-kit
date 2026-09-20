# Errors

> **Generated** from the server's own tool catalog, version 1.0.0. Do not edit.

Every error answer means **nothing was done**. There is no half-finished change to clean up, so
the question is only what to tell the person and whether anything is worth trying again.

| Code | What the server says | What to do |
|---|---|---|
| `not_connected` | This connection is no longer active. Nothing was done; connect the app again at auth.main-team.org. | Stop. Tell the person to connect the app again at `auth.main-team.org`; nothing was done. |
| `reconsent_required` | What this connection may do has changed since it was approved. Nothing was done; approve it again at auth.main-team.org. | Stop. What the connection may do has changed; ask the person to approve it again at `auth.main-team.org`, then start over. |
| `insufficient_scope` | This connection was not approved for changes. Nothing was done; reconnect and allow changes to use this tool. | Stop changing. This connection was approved for reading only. Offer a panel link instead, or ask the person to reconnect and allow changes. |
| `brand_not_allowed` | This connection does not cover that olympiad. Nothing was done. | Use a `brand` the connection covers. `whoami` lists them; never retry with a guess. |
| `role_required` | That is not something this account can do on that olympiad. Nothing was done. | Stop. This account does not hold that role on that olympiad. Say so; do not try another olympiad to find one that works. |
| `role_changed` | This account holds a different role on that olympiad than when the connection was approved. Nothing was done; approve the connection again. | Stop. The role changed since the connection was approved; ask the person to approve it again. |
| `tenant_account_missing` | This account has no profile on that olympiad yet. Nothing was done; open the olympiad once in the panel and try again. | Stop. Ask the person to open that olympiad once in the panel, then try again. |
| `not_found` | No such record, or it is not this account’s. Nothing was done. | Do not retry and do not guess another id. Re-read the list the id came from; it may have changed or never belonged to this account. |
| `not_allowed_here` | That cannot be done through an AI client. Nothing was done. | Stop. That is not something an AI client does. Offer a panel link with `main-team:get_panel_link`. |
| `confirmation_required` | This change needs confirming first. Nothing was done yet. | Expected on the first call of a change. Show the summary, wait for a clear yes, then repeat the call with the same arguments plus the `confirmation` value. |
| `confirmation_expired` | That confirmation is no longer good. Nothing was done; ask again. | The confirmation was good for ten minutes. Call again without it, show the fresh summary and confirm again. |
| `open_in_panel` | This has to be done in the panel. Nothing was done. | Stop. Hand over the link in the answer; it is done in the panel. A change that cannot be undone answers this way too, as a plain answer rather than an error, when the app cannot put the question to the person: nothing was done. |
| `exam_not_eligible` | That exam is not one this student can be applied to. Nothing was done. | Do not retry. Re-read the eligible list; the exam is not one this student may be applied to. |
| `cannot_change` | That application can no longer be changed. Nothing was done. | Stop. That application can no longer be changed. Say why if the answer says, and offer the panel. |
| `cannot_cancel` | That application can no longer be cancelled. Nothing was done. | Stop. That application can no longer be cancelled here — a paid or sat exam usually cannot. Offer the panel. |
| `already_applied` | There is already an application for that exam. Nothing was done. | Not an error to fix: the entry already exists. Report it and move on. |
| `payment_required` | That needs paying for first. Nothing was done; the payment link opens the panel’s own screen. | The fee has to be paid first. Get a payment link and hand it over; never say it is paid until a read shows it. |
| `rate_limited` | This connection has asked for more than it may just now. Nothing was done; try again shortly. | Wait. Honour any wait the answer gives, then retry once. Do not loop, and do not split the work into more calls. |
| `writes_disabled` | Changes through an AI client are switched off for now; reading still works. Nothing was done. | Stop changing. Changes through an AI client are off just now; reading still works. Do not retry. |
| `temporarily_unavailable` | This is temporarily unavailable. Nothing was done; try again shortly. | Retry once after a short pause. If it happens again, stop and tell the person. |
| `upstream_error` | The platform could not answer that. Nothing was done; quote the request id to support. | Stop. Quote the `request_id` from the answer’s `meta` to support; do not retry the same call repeatedly. |

**One of those words is not always an error.** A change that cannot be undone answers
`open_in_panel` with a panel link as a plain answer — no error, and nothing done — when the app
cannot put the question to the person itself. Read it the same way: hand the link over and stop.

## The three rules that matter more than the table

1. **Never loop.** `writes_disabled`, `not_allowed_here`, `role_required`, `insufficient_scope`
   and `open_in_panel` will answer the same way every time. Say what happened and stop.
2. **Never widen the search after a refusal.** A `not_found` or a `role_required` is not an
   invitation to try another olympiad, another student or another id until something works.
3. **Say what did not happen.** "The entry was not created" is the useful sentence; the code by
   itself is not.
