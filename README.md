# Main Team agent kit

Connect an AI app to your own [Main Team](https://hub.main-team.org/ai) olympiad account, and teach
it to work there safely. The kit is one MCP server plus the skills that drive it.

## Who it is for

You sign in as yourself. The connection can do what **you** can do in your own panel — no more.

| You are | What the connection reaches |
|---|---|
| A student | your exam entries, fees, results, certificates, study papers, calendar and announcements |
| A teacher (supervisor) | your own students, their entries and payment state, your invoices and certificates |
| A partner | the students and teachers of your country or region, their entries and payment links |

## Install

The one server address is `https://mcp.main-team.org/mcp`. Adding it opens
`auth.main-team.org`, where you sign in, tick the olympiads the app may reach and decide whether it
may change anything. The step-by-step pages per app are at
[hub.main-team.org/ai/connect](https://hub.main-team.org/ai/connect).

```bash
npx skills add main-team-organisation/agent-kit
npx skills update
```

Each release also carries one zip per skill, for upload to a chat app that takes skill files.

## The skills

| Skill | Read it when |
|---|---|
| `connecting-to-main-team` | starting any session: who the connection is for and what it may do |
| `staying-safe-with-main-team` | before any change, and whenever a tool answers an error |
| `managing-olympiad-exams-as-a-student` | finding, entering, moving or cancelling your own exams |
| `paying-olympiad-fees-as-a-student` | fees, discount codes and payment links for your entries |
| `reviewing-results-and-certificates-as-a-student` | scores, reports and certificates |
| `preparing-for-olympiads-as-a-student` | past papers, the calendar, announcements and notifications |
| `managing-students-as-a-teacher` | a class list, and entering students for exams in batches |
| `following-student-results-as-a-teacher` | sittings, results and certificates for your students |
| `handling-payments-and-invoices-as-a-teacher` | paying for a class and reading your invoices |
| `managing-country-students-as-a-partner` | your country's students and their unpaid entries |
| `working-with-teachers-as-a-partner` | the teachers you work with, and exam changes for them |

## Safety in short

- **Nobody takes an exam here.** There is no tool for sitting, starting or answering one, and the
  skills refuse to help with exam content during a sitting.
- **No identifiers.** No username, no student or teacher code, no e-mail address, no phone number
  and no date of birth ever comes back. A student is an opaque handle such as `stu_x7k2m9p4`.
- **No money moves.** A payment tool returns a link that opens your own panel's payment screen.
- **Changes are confirmed twice.** A change is previewed first and only happens on a second,
  identical call; the ones that cannot be undone need you yourself.
- **Text from a record is data.** An announcement or a report may contain anything; it is never an
  instruction to the assistant.

## Disconnecting

The connected-apps page at `https://auth.main-team.org/connected-apps` ends any connection at once,
and so does asking the assistant to disconnect. Signing out of the website does not.

## Versions

The kit carries the MCP server's version. Every release is a GitHub release with the skill zips and
their checksums; the changes are in [CHANGELOG.md](CHANGELOG.md).

This repository is generated from a Main Team release. Please report problems rather than opening
pull requests: [SECURITY.md](SECURITY.md) for security issues, info@main-team.org for anything else.
