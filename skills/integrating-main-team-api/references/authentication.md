# Authentication

## Contents

- [Credentials](#credentials)
- [The token](#the-token)
- [Signing in code](#signing-in-code)
- [Reusing and revoking tokens](#reusing-and-revoking-tokens)
- [When the API answers 401](#when-the-api-answers-401)
- [If the secret leaks](#if-the-secret-leaks)

Full guide: https://hub.main-team.org/api/authentication

## Credentials

| | `apiKey` | `apiSecret` |
|---|---|---|
| Format | `key_` and 24 characters from `A-Z a-z 0-9 _ -` | `secret_` and a long random string |
| Used as | `kid` header and `sub` claim of every token | The HMAC key that signs tokens |
| Secret | No | **Yes**: whoever holds it acts as the account |
| Recoverable | Ask the operator | No: shown once, never again, no rotation |

The sandbox and production have separate accounts. Sandbox credentials are refused by production
and the other way round.

Use the secret exactly as issued: the whole string including `secret_`, as UTF-8 bytes. A trailing
newline or quotes picked up from a configuration file make every token fail.

## The token

| Part | Field | Rule |
|---|---|---|
| Header | `alg` | `HS256`, and nothing else |
| Header | `typ` | `JWT` (not checked) |
| Header | `kid` | The `apiKey` |
| Payload | `sub` | The `apiKey`, equal to `kid` |
| Payload | `iat` | Issued-at, whole seconds since the epoch. Required. At most 30 seconds ahead of the server |
| Payload | `exp` | Expiry, whole seconds. Required. After `iat`, and at most 3600 seconds after it |
| Payload | `nbf` | Optional; checked with the same 30-second tolerance |

A token is still accepted up to 30 seconds after `exp`. Other claims are ignored, except `purpose`:
a token carrying a `purpose` claim is refused, whatever its value.

## Signing in code

Node.js, with `jsonwebtoken`:

```js
import jwt from 'jsonwebtoken';

const now = Math.floor(Date.now() / 1000);
const token = jwt.sign(
  { sub: process.env.MTO_API_KEY, iat: now, exp: now + 900 },
  process.env.MTO_API_SECRET,
  { algorithm: 'HS256', keyid: process.env.MTO_API_KEY },
);
```

PHP, with `firebase/php-jwt`:

```php
$now = time();
$token = \Firebase\JWT\JWT::encode(
    ['sub' => getenv('MTO_API_KEY'), 'iat' => $now, 'exp' => $now + 900],
    getenv('MTO_API_SECRET'),
    'HS256',
    getenv('MTO_API_KEY'),
);
```

Without packages, `scripts/sign-token.mjs` does the same with `node:crypto`. Any language works:
the signature is HMAC-SHA256 over `base64url(header) + "." + base64url(payload)`, base64url-encoded
without padding.

## Reusing and revoking tokens

- Keep one token per process and sign a new one about 60 seconds before `exp`. Several servers may
  each sign their own; the rate limit belongs to the account, not to a token.
- `POST /v1/api-account/revoke-token`, authenticated with the token to end, refuses that token from
  then on. `data.expiresIn` says how long the refusal is held. Other tokens keep working.
- `GET /v1/api-account/validate-me` returns the account itself, without the usual envelope: a cheap
  way to test a token. Both need `api/*` on `mto`.

## When the API answers 401

Every authentication failure is the same `401 unauthorized` with the same message, whatever the
cause. Check, in order:

1. The header is `Authorization: Bearer <token>`, with one space and nothing else.
2. The credentials belong to the environment of the base URL.
3. `kid` in the header and `sub` in the payload are both exactly the `apiKey`.
4. `alg` is `HS256`.
5. `iat` and `exp` are numbers of whole seconds, `exp - iat` is at most 3600, and `exp` is in the
   future.
6. The server clock is synchronized: `iat` more than 30 seconds ahead is refused. Compare with the
   `Date` header of `GET /v1/health`.
7. The secret is byte for byte what was issued.
8. The account is active, and the token has not been revoked.
9. The payload has no `purpose` claim.

`node scripts/doctor.mjs --env sandbox` runs most of these checks. When writing to support, send the
`request_id`, the time in UTC and the decoded header and payload, never the token or the secret.

## If the secret leaks

The secret cannot be rotated.

1. Email info@main-team.org from the registered contact address, give the `apiKey` (never the
   secret) and ask for the account to be deactivated. Tokens stop working within 60 seconds of that.
2. Revoke the tokens you hold if you want them cut off sooner; only deactivation stops new ones.
3. Find and fix the cause before new credentials arrive.
4. Agree the replacement with the operator. Students belong to the account that registered them, so a
   new account does not see the old account's students until that is arranged.
