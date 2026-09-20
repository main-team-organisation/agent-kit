<!-- Generated from the Main Team API contract 1.1.1 (https://hub.main-team.org/api/openapi.json). Do not edit: it is rebuilt with every release. -->

# Operations

The 3 operations this skill uses, of the Main Team API 1.1.1. Paths are relative to
`https://api.main-team.org` (production) or `https://apisnd.main-team.org` (sandbox).
`{organizationId}` is the organization's `_id` from `GET /v1/organization`, never its slug.
Each operation name links to its full reference: fields, examples and errors.

The permission is the role action an account needs, on `mto` for the core record or on the
organization in the path.

Every operation of the API is listed in the integrating-main-team-api skill.

## API account

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`revokeToken`](https://hub.main-team.org/api/reference/revoke-token) | `POST /v1/api-account/revoke-token` | Revoke the token you send, before it expires | `api/*` on `mto` |
| [`getCurrentApiAccount`](https://hub.main-team.org/api/reference/get-current-api-account) | `GET /v1/api-account/validate-me` | Fetch the API account your token belongs to | `api/*` on `mto` |

## Sign-in links

| Operation | Method and path | What it does | Permission |
|---|---|---|---|
| [`createSigninLink`](https://hub.main-team.org/api/reference/create-signin-link) | `POST /v1/{organizationId}/auth/signin` | Create a single-use sign-in link for one of your students | `auth/signin` on the organization in the path |
