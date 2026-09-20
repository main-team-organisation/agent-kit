# The token, exactly

## Contents

- [Credentials](#credentials)
- [Every claim](#every-claim)
- [Signing it](#signing-it)
- [Reuse](#reuse)
- [The 401 checklist](#the-401-checklist)
- [The 403 is a different problem](#the-403-is-a-different-problem)

## Credentials

| | `apiKey` | `apiSecret` |
|---|---|---|
| Format | `key_` and 24 characters from `A-Z a-z 0-9 _ -` | `secret_` and a long random string |
| Used as | The `kid` header and the `sub` claim | The HMAC key |
| Secret | No | **Yes**: whoever holds it is the account |
| Recoverable | Ask the operator | No: shown once, never again, never rotated |

The sandbox and production have separate accounts. Each environment refuses the other's
credentials, and the answer is the same `401` as any other failure.

Use the secret exactly as issued: the whole string including `secret_`, as UTF-8 bytes. A trailing
newline or a pair of quotes picked up from a configuration file makes every token fail, and nothing
in the answer says so.

## Every claim

| Part | Field | Rule |
|---|---|---|
| Header | `alg` | `HS256`, and nothing else |
| Header | `typ` | `JWT` (not checked) |
| Header | `kid` | The `apiKey` |
| Payload | `sub` | The `apiKey`, equal to `kid` |
| Payload | `iat` | Whole seconds since the epoch. Required. At most 30 seconds ahead of the server |
| Payload | `exp` | Whole seconds. Required. After `iat`, at most 3600 seconds after it |
| Payload | `nbf` | Optional; checked with the same 30-second tolerance |
| Payload | `purpose` | **Refused**, whatever its value |

A token is still accepted up to 30 seconds after `exp`. Other claims are ignored.

## Signing it

Node.js, with `jsonwebtoken`:

```js
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

Any language works: the signature is HMAC-SHA256 over
`base64url(header) + "." + base64url(payload)`, base64url-encoded without padding.

Read the secret from the environment or a secret manager. Never from a command-line argument, where
every process on the machine can read it, and never from a file committed to a repository.

## Reuse

Keep one token per process and re-sign about 60 seconds before `exp`. A 900-second lifetime is a
reasonable default: short enough that a stolen token expires, long enough not to re-sign on every
call. Never sign a token per request.

Several servers may sign their own tokens at the same time. The rate limit belongs to the account,
so more tokens buy no more requests.

## The 401 checklist

Every authentication failure answers the same `401 unauthorized` with the same message, whatever
the cause, and the answer never says which check failed. Work through these in order:

1. The header is `Authorization: Bearer <token>`, one space, nothing else.
2. The credentials belong to the environment the base URL points at.
3. `kid` in the header and `sub` in the payload are both exactly the `apiKey`.
4. `alg` is `HS256`.
5. `iat` and `exp` are whole seconds, `exp - iat` is at most 3600, and `exp` is in the future.
6. The clock is synchronised: an `iat` more than 30 seconds ahead is refused. Compare with the
   `Date` header of `GET /v1/health`.
7. The secret is byte for byte what was issued, with no surrounding whitespace or quotes.
8. The account is active and the token has not been revoked.
9. The payload carries no `purpose` claim.

When you write to support, send the `request_id`, the time in UTC and the decoded header and
payload. Never send the token, and never send the secret.

## The 403 is a different problem

A `403 forbidden` means the token was accepted and the account may not do that. Signing a new token
changes nothing. `getCurrentApiAccount` (`GET /v1/api-account/validate-me`) lists the roles; the
operations reference of each skill names the action a route needs. An operator adds the role.
