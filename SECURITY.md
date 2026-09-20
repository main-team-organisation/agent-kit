# Security

## Reporting a vulnerability

Please report security problems in the Main Team MCP server or this kit privately:

- through GitHub's **Report a vulnerability** button on this repository's Security tab, or
- by e-mail to info@main-team.org, with "Security" in the subject.

Include what you found and how to reproduce it. For a tool call that behaved unexpectedly, quote the
`request_id` from the answer's `meta` and the time in UTC. Do not include credentials, tokens or
anybody's personal data, and do not test with another person's account.

We confirm that we received your report and keep you informed until the problem is fixed.

## If a connection is not yours

Every connection sends the account holder an e-mail when it is approved. If one arrives that you did
not approve:

1. open `https://auth.main-team.org/connected-apps` and remove the connection — it stops working at
   once, in every app;
2. change the account password, which also ends connections within a minute;
3. write to info@main-team.org with the time of the e-mail.

Asking a connected assistant to disconnect does the same as step 1 for that one app. Signing out of
the website does **not** end a connection.

## Scope

This repository holds instructions and manifests only. It contains no credentials, stores nothing
and runs no server. The MCP server is operated by Main Team at `mcp.main-team.org`; sign-in and
consent happen at `auth.main-team.org`. A connection never reaches an account other than the one
that approved it, and there is no administrative connection.
