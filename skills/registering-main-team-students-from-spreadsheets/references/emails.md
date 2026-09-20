# The welcome email

## Every student in the file gets one

Each student registered by a batch receives the same welcome email `registerStudent` sends, one per
student, with the same text. Bulk registration changes nothing about it, and there is no flag that
suppresses it.

So a batch of 250 rows is 250 messages, sent to the addresses exactly as they were typed. Every
typo is a message to a stranger, and a mistyped address cannot be recalled.

## What that means before you send

- **Say it out loud.** Before the first send, tell the person how many students are in the file and
  that each will be emailed. It is the part of the job that cannot be undone, and they may want to
  check the list once more.
- **Nothing is sent while a batch is refused.** A `400`, a `422` or a `503` means nothing was
  queued, so no email went out. That is the cheap moment to find a bad address.
- **Nothing is sent when an import fails.** The batch is all or nothing; a `failed` import
  registered nobody and emailed nobody.
- **Everything is sent when it succeeds.** There is no half-way state to stop.

## Checking addresses first

For a list you are not sure of, check rows against the API before you build the batch:
`checkStudentRegistration` (`POST /v1/student/check`) runs registration's own checks on one row and
writes nothing. It is a different operation with its own budget of 100 requests per 60 seconds, so
checking a few doubtful rows is cheap — checking a thousand is a separate job with its own pacing.

Worth checking one by one:

- rows whose address looks generated (`student1@`, `class5@`) or shared between siblings;
- rows the school typed in by hand rather than exported;
- rows whose surname or school the local script had to guess at.

`roster.py normalise` already finds what can be seen without the API: malformed addresses, the same
address twice in the file, missing fields, unreadable dates.

## Addresses you did not collect

An address in a spreadsheet belongs to a child. Register only students the person you work for is
entitled to register, from a list that school or partner collected themselves.

Do not send a list of addresses gathered somewhere else to find out which of them exist. The API
answers `email_unavailable` without saying who holds an address, and repeats of that against the
same account stop being itemised at all — the refusal is counted and the list comes back empty.

If the person asks for that, say no and say why.

## What to tell the person afterwards

- How many students were registered, and where the report is.
- That the welcome mail has gone out, so a mistake now means contacting the family, not resending.
- Which rows were left out and why, by row reference rather than by name.
