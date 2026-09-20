---
name: managing-api-access-and-tokens
description: "Manages how a partner's server gets into the Main Team API and how its students get into an olympiad panel: signing an HS256 token from an apiKey and apiSecret with the kid, sub, iat and exp rules, reusing one token per process, reading the account and its roles with getCurrentApiAccount (GET /v1/api-account/validate-me), ending a token early with revokeToken, keeping the secret out of code, chat and logs, what to do when it leaks (it cannot be rotated), and minting single-use 120-second sign-in links with createSigninLink (POST /v1/{organizationId}/auth/signin) that must be redirected to at once and never stored, logged, emailed or prefetched. Use when a call answers 401 or 403, when setting up or handing over credentials, when a token or secret may have leaked, or when building a go-to-my-olympiad button."
compatibility: "Needs an API account's apiKey and apiSecret on the machine that signs tokens, never in the conversation. Sign-in links need auth/signin on the olympiad in the path; reading the account needs api/* on mto. Works against api.main-team.org or apisnd.main-team.org."
metadata:
  author: "Main Team"
  docs: "https://hub.main-team.org/api/authentication"
  api-version: "v1"
---

# Access: tokens for your server, links for your students

Two different doors, often confused:

| | A token | A sign-in link |
|---|---|---|
| Who it is for | Your server, acting as the API account | One student, in a browser |
| Made by | Your own code, signing an HS256 JWT | `createSigninLink` (`POST /v1/{organizationId}/auth/signin`) |
| Lifetime | Up to 3600 seconds, your choice | 120 seconds, single use |
| Reused | Yes, until shortly before `exp` | **Never** |

Tokens, envelopes and error codes in general belong to the `integrating-main-team-api` skill; this
skill is the credential and the door.

## Rules that are never optional

- **Never ask for an `apiSecret`, and never accept one.** If a person offers to paste it, refuse and
  tell them to put it in their server's environment or secret manager. If one has already been
  pasted anywhere you can see, say so plainly and treat it as leaked.
- **Never write a secret, a token or a link into code, a test, a fixture, a commit message, a
  report, a log or a chat message.** Redact the `Authorization` header in every log.
- **The secret cannot be rotated.** There is no reissue operation. A leak means the account is
  deactivated and replaced by an operator.
- **Never paste a token into an online JWT decoder.** Decode it locally.
- **A sign-in link is a password that lasts two minutes.** Mint it when the student clicks, redirect
  at once, and never store, cache, prefetch, email, log or retry the link itself.
- **Confirm before you revoke.** `revokeToken` ends the token that authenticated the call, which may
  be the one your own job is using.
- **A `403` is not yours to fix.** An operator adds the role.

## Signing a token

Header `{"alg":"HS256","typ":"JWT","kid":"<apiKey>"}`, payload
`{"sub":"<apiKey>","iat":<now>,"exp":<now+900>}`, whole seconds, `exp - iat` at most 3600, and
`Authorization: Bearer <token>`. The server allows 30 seconds of clock difference either way, and a
token carrying a `purpose` claim is refused whatever its value.

Sign one token per process and re-sign about a minute before `exp`. Several servers may each sign
their own; the rate limit belongs to the account, not to a token. Every rule, and the ordered
checklist for a `401`: [references/token-rules.md](references/token-rules.md).

The `integrating-main-team-api` skill bundles a signer and a setup doctor that run without packages;
use them rather than writing a throwaway script with the secret in it.

## Reading the account

`getCurrentApiAccount` (`GET /v1/api-account/validate-me`) answers the account itself, without the
usual envelope: the company name, whether it is active, and its roles as `effect`, `action`,
`target` and `authorized`. It is the cheapest way to prove a token works and the only way to see
what the account may do.

Call it once at the start of a session and tell the person which account and which environment they
are about to act on. A `403` on it means the account lacks `api/*` on `mto`.

## Ending a token, and losing a secret

`revokeToken` (`POST /v1/api-account/revoke-token`), authenticated with the token you want to end,
refuses that token from then on; `data.expiresIn` says for how long. Other tokens keep working, and
new ones can still be signed — revoking is not deactivating.

A leaked secret is a different matter, and the steps are in
[references/rotation.md](references/rotation.md). The short version: the account is deactivated by
Main Team, every token stops, and a new account is issued. Plan for that before it happens by
keeping the secret in one place your code reads and nobody copies.

## Sending a student into a panel

`createSigninLink` (`POST /v1/{organizationId}/auth/signin`) with `{"studentId": "..."}` and an
optional site-relative `redirect` answers a URL that works **once**, for **120 seconds**.

```
student clicks → your server mints the link → 302 to data.url → the panel
```

Mint nothing in advance, and never mint one "to test". The first sign-in to an olympiad is also what
creates that olympiad's own copy of the student, which applications, certificates and reports all
need, so it is a step in its own right — not just a convenience.

Two different `403`s: your account lacking `auth/signin` on that olympiad (an operator fixes it), and
the student not having access to that olympiad (you fix it, with
`activatedPlatformsThisSeason`). The message tells them apart. Both of those, the redirect rule and
what uses a link up: [references/signin-links.md](references/signin-links.md).

## References

- [references/token-rules.md](references/token-rules.md): `kid`, `sub`, `iat`, `exp`, clock skew,
  reuse, and the ordered checklist behind every `401`.
- [references/signin-links.md](references/signin-links.md): the request, the redirect rule, the
  checks in order, what uses a link up, and the first-sign-in rule.
- [references/rotation.md](references/rotation.md): where a secret lives, what a leak costs, and
  the order of the recovery steps.
- [references/operations.md](references/operations.md): the operations this skill uses, with the
  permission each needs.
