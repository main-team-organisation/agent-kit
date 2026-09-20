# Where a credential lives, and what a leak costs

## There is no rotation

The `apiSecret` is shown once, when the account is issued, and never again. There is no operation
that reissues it, changes it or shows it. That single fact decides everything else on this page:
the only answer to a leak is a new account.

`revokeToken` (`POST /v1/api-account/revoke-token`) is not rotation. It ends **one token**, the one
that authenticated the call, and `data.expiresIn` says how long the refusal is held. New tokens
signed with the same secret still work.

## Where it should live

| Good | Why |
|---|---|
| The server's environment, set by the deployment | Nothing to commit, nothing to copy |
| A secret manager the process reads at start-up | Auditable, and replaceable in one place |
| A file outside the repository, mode `600`, read once | Acceptable when there is nothing better |

| Never | Why |
|---|---|
| In the repository, even in an example or a test fixture | It is published the moment the repository is |
| In a command-line argument | Every process on the machine can read the argument list |
| In a browser, a mobile app or anything a user can open | The API is server to server; there are no CORS headers on production |
| In a chat message, a ticket, a screenshot or a commit message | All of them are copied and searched |
| In a log, a trace or an error report | Redact `Authorization` everywhere |

Keep the `apiKey` where you like: it is not secret. It is the `kid`, and it identifies the account.

## If it has leaked

Assume a leak whenever the secret has been in a place from the "never" list, including a chat you
are reading. Do not weigh how likely it is that anyone saw it.

1. **Tell the person you work for, plainly.** They own the decision, and the clock matters.
2. **Email Main Team from the account's registered address**, quoting the `apiKey` — never the
   secret — and ask for the account to be deactivated. Tokens stop working within about a minute of
   that.
3. **Revoke the tokens you hold** with `revokeToken` if you want them cut off sooner. That does not
   replace step 2.
4. **Find and fix the cause** before the replacement arrives: the commit, the log line, the copied
   configuration file. A new secret in the same place leaks the same way.
5. **Agree the replacement with the operator.** Students belong to the account that registered them,
   so a new account does not see the old account's students until that is arranged. Say so early;
   it is the part that takes time.

## Handing an account over

- Two environments, two accounts. Sandbox credentials are refused by production and the other way
  round, and the answer is an ordinary `401`, so a mixed-up pair looks like a broken token.
- One account per system, not one per person. Roles are attached to the account, and
  `getCurrentApiAccount` (`GET /v1/api-account/validate-me`) is how anyone sees what it may do.
- When someone leaves, the question is whether they had the secret, not whether they had an account.
  If they did, it is a leak.
- Write down which environment each deployment points at. Most "it works on staging" reports are a
  base URL and a credential that disagree.
