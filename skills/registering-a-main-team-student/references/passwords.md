# Passwords: the last resort

## The default is a sign-in link

A student reaches their olympiad panel either through a sign-in link your server mints when they
click, or with a password. Prefer the link.

| | Sign-in link | A password you set |
|---|---|---|
| Lifetime | 120 seconds, single use | Until somebody changes it |
| Who knows it | Only the browser you redirect | You, the student, and everything the password passed through |
| Permission | `auth/signin` on the organization in the path | `auth/signin` on `mto` |
| Works after the student confirmed their address | Yes | No: `409 conflict` |
| Something to deliver to the student | No | Yes, and delivering it safely is your problem |

Sign-in links are the `managing-api-access-and-tokens` skill's subject.

## Where a password may be set

- `registerStudent` (`POST /v1/student`) takes an optional `password` at registration.
- `setStudentPassword` (`PUT /v1/student/{studentId}/password`) sets one afterwards.

Both need an allow role with action `auth/signin` (or `auth/*`, `*/signin`, `*/*`, `*`) and target
`mto` or `*`. A role granting `student/*` is not enough: an account that may register and update
students still gets `403 forbidden` on the password. The reason is plain — whoever knows a
student's password can sign in as that student, with no expiry — so it cannot need less than a
sign-in link does.

`auth/signin` on one olympiad only, say target `stem`, lets you mint links for that olympiad and
still answers `403` on the password, which lives on the core record.

## When it is refused

| Answer | Why |
|---|---|
| `403 forbidden` | No role grants `auth/signin` on `mto`. An operator adds it; retrying never helps |
| `409 conflict` | The student has confirmed their own email address. From then on the password is theirs, not yours. Send a sign-in link, or let them use "forgot password" |
| `400 bad_request` | The password breaks the rules the contract states for the field |

`setStudentPassword` is safe to repeat: the same body sets the same password again. A `409` on the
repeat means the student confirmed their address in between.

## Rules for an agent

- **Never read a password out of a spreadsheet, a ticket or a message and send it.** A class list
  never carries passwords; a column called one is a mistake to report, and bulk registration refuses
  the field outright.
- **Never invent a password and tell the person what it is in chat.** If a password is genuinely
  needed, have their own code generate it and deliver it through their own channel.
- **Never echo a password back**, into a log, a report file, a commit or a summary.
- **Never set one "to be safe"** while registering. A student with no password and a sign-in link is
  in a better position than one whose password sat in three systems.
- Ask before setting one, and say what it is for.
