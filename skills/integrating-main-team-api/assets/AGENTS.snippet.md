## Main Team API

This project calls the Main Team API (https://hub.main-team.org/api). Rules for agents working here:

- The `apiSecret` is read from the environment (`MTO_API_SECRET`) or a secret manager on the server.
  Never write it into code, tests, fixtures, logs, commit messages or chat, and never ask for it.
- The base URL comes from configuration: `https://apisnd.main-team.org/v1` (sandbox) or
  `https://api.main-team.org/v1` (production). Tests and experiments use the sandbox only.
- Tokens are HS256 JWTs with `kid` = `sub` = the `apiKey`, integer `iat` and `exp`, and
  `exp - iat` at most 3600. Reuse a token until about a minute before `exp`.
- Organization paths take the organization's `_id` from `GET /v1/organization`, never its slug.
- Branch on the HTTP status and `error.code`; log `error.request_id`; never parse `error.message`.
- Never retry `POST /v1/student`: a `409` names the existing student. `POST .../application` is safe
  to repeat, and `POST /v1/student/import` answers the import you already have for 24 hours.
- Bulk registration is 30 to 1000 rows, all or nothing, 10 requests an hour, and every student in
  the batch gets a welcome email. A `422` lists every row to fix and queues nothing.
- Sign-in links work once for 120 seconds: mint on demand, redirect at once, never store or log them.
- Respect `Retry-After` on `429`; the limit is 100 requests per 60 seconds per operation per account.
- Students are matched across olympiads on `mainId`, the core `_id`.
- Students' names, addresses and ids stay out of chat, tickets and commit messages.
- Redact the `Authorization` header in every log.
