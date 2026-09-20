# Moving, re-languaging and cancelling an entry

## Move an entry rather than cancelling and entering again

Moving keeps the same entry, the same fee and whatever has been paid. Cancelling and entering again
is a new entry at whatever the fee then is. Always reach for the move first.

```jsonc
// 1. what this entry may move to
main-team:find_exams_for_me
{ "brand": "stem", "for_application_id": "70b3d5e2a1c94f6081b2c3d4" }

// 2. dry run
main-team:change_exam_application
{ "brand": "stem", "application_id": "70b3d5e2a1c94f6081b2c3d4", "exam_id": "6a1c4f2b9d07e85c3b214fa0" }
//    -> confirmation_required, summary, confirmation

// 3. after a clear yes: the same call plus "confirmation"
```

`for_application_id` matters. Without it the list is "what could I enter", which includes sittings
this particular entry is not allowed to move to; with it the platform leaves those out.

`main-team:list_my_exams` carries `can_change` per entry. Treat it as a hint, not a promise: the
platform decides again at the moment of the call, and `cannot_change` is the honest answer even when
the hint said otherwise.

## Language only, and only on stem

```jsonc
main-team:list_exam_language_options { "brand": "stem", "application_id": "70b3d5e2a1c94f6081b2c3d4" }
//    -> each option with its own exam_id and language_code

main-team:change_exam_language { "brand": "stem", "application_id": "...", "exam_id": "<the option>" }
```

The sitting, the category and the fee stay the same; only the language moves. On any olympiad other
than stem both tools answer `not_allowed_here`. Say that plainly rather than trying the move tool
instead.

## Cancelling

`main-team:cancel_exam_application` is the one entry-level change that cannot be undone.

Before calling it, say all three of these:

- the entry is gone, and entering again later is a **new** entry at whatever the fee then is;
- a paid entry usually cannot be cancelled here at all — the platform decides, not this tool;
- the student themselves has to confirm; an app that cannot ask them gets a panel link and nothing
  happens.

```jsonc
main-team:cancel_exam_application { "brand": "stem", "application_id": "70b3d5e2a1c94f6081b2c3d4" }
```

| Answer | Meaning |
|---|---|
| `open_in_panel` | the app could not ask the student; not an error, nothing was done — hand over the link in the answer and stop |
| `cannot_cancel` | the platform refuses it — paid, under way or past |
| `confirmation_expired` | too slow; start again from a fresh call |
| `not_found` | that is not one of this student's entries; re-read the list |

Never offer to "just cancel and re-enter" to get round a `cannot_change`. Say what the platform
said, and offer the panel link.

## Refunds

There is no refund tool and no way to tell from here whether one is due. If a student asks, say that
cancelling does not by itself return money and that they should ask Main Team through the panel.
