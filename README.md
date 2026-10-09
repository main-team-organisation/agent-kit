# Main Team agent kit

Connect an AI app to your own [Main Team](https://hub.main-team.org/api/mcp) olympiad account, and teach
it to work there safely. The kit is one MCP server plus the skills that drive it.

## Who it is for

You sign in as yourself. The connection can do what **you** can do in your own panel — no more.

| You are | What the connection reaches |
|---|---|
| A student | your exam entries, fees, results, certificates, study papers, calendar and announcements |
| A teacher (supervisor) | your own students, their entries and payment state, registering new students with their exams, your invoices and certificates |
| A partner | the students and teachers of your country or region, their entries and payment links, your own payments and certificates — but not registering new students |

## Install

The one server address is `https://mcp.main-team.org/mcp`. Adding it opens
`auth.main-team.org`, where you sign in, tick the olympiads the app may reach and decide whether it
may change anything. The step-by-step pages per app are linked from
[hub.main-team.org/api/mcp](https://hub.main-team.org/api/mcp).

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
| `taking-part-in-group-challenges-as-a-student` | your group challenge: your group, its steps, submitting them |
| `managing-students-as-a-teacher` | your student list, exporting it, entering students for exams in batches, and past papers |
| `registering-new-students-as-a-teacher` | registering new students — no account yet — from a sheet, with their exams |
| `following-student-results-as-a-teacher` | sittings, results and certificates for your students |
| `handling-payments-and-invoices-as-a-teacher` | paying for a class and reading your invoices |
| `running-group-challenges-as-a-teacher` | forming, confirming and following your students' challenge groups |
| `managing-country-students-as-a-partner` | your country's students and their unpaid entries |
| `working-with-teachers-as-a-partner` | the teachers you work with, and exam changes for them |

The other skills in `skills/` are the Main Team REST API's own, for a developer or an integration
holding an API key rather than for a person's own account; they never use this server.
`SOURCES.json` names the release each half comes from.

## Safety in short

- **Nobody takes an exam here.** There is no tool for sitting, starting or answering one, and the
  skills refuse to help with exam content during a sitting.
- **No identifiers.** No username, no student or teacher code, no e-mail address, no phone number
  and no date of birth ever comes back. A student is an opaque handle such as `stu_x7k2m9p4`. A
  teacher registering new students gives their addresses; the platform e-mails each student their
  username and password, the student confirms the address at their first sign-in, and neither the
  teacher nor the assistant sees the username or the password.
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
