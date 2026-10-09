# Connecting an app, and ending a connection

## The one address

```text
https://mcp.main-team.org/mcp
```

That is the whole configuration. There is no second server, no test server and no API key to paste:
anything that asks for a Main Team key or password in order to "connect an AI app" is not this.

## What the person sees

1. The app is pointed at the address above and opens a browser window.
2. `auth.main-team.org` asks the person to sign in with their own Main Team username and password —
   the same ones they use for the panel.
3. A consent page shows: which app is asking, which olympiads they hold a role on, and whether the
   app may change anything or only read. The person ticks the olympiads they want covered.
4. A student also ticks a declaration that they are 18 or older, or that a parent or guardian
   approves and is with them.
5. The browser returns to the app, and the connection is live.
6. Main Team e-mails the account holder that a connection was approved. That mail is the safety
   net: anybody who did not approve it should follow it up at once.

An assistant takes no part in steps 2 to 4 and must never offer to. Never ask for the password,
never offer to "do the sign-in", and never accept a link that carries a code or a token.

## Per-app instructions

The install steps for each AI app are published at `https://hub.main-team.org/api/mcp`, one page
per app. Point the person there rather than guessing menu names; apps rename their settings often.

## How long it lasts

`main-team:whoami` carries `access_expires_at`. Students get the shortest connections and can
connect only apps Main Team has verified; staff connections last longer. A connection also ends
when the person changes their password, when their role changes, or when an operator stops
connections. Expect it to end at any time and say so plainly when it does — never retry around it.

## Ending it

Either of these ends it immediately, everywhere:

- `main-team:disconnect_this_app`, which asks for confirmation first and then revokes every token
  this app holds. It removes no exam entry, no payment and no account — only the connection. The
  answer carries the address for connecting again later.
- the person's own connected-apps page, `https://auth.main-team.org/connected-apps`, which lists
  every connected app and ends any of them.

Signing out of the Main Team website does **not** end a connection. Say so when somebody assumes it
does.

## If a connection looks wrong

Stop working, and tell the person to:

1. open `https://auth.main-team.org/connected-apps` and remove anything they do not recognise;
2. change their account password, which also ends connections shortly afterwards;
3. write to info@main-team.org with the time of the e-mail they received.
