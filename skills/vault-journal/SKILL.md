---
name: vault-journal
description: Daily journaling rules for the research vault — one note per calendar day under `daily_notes/YYYY-MM-DD.md`, with stable headings (Summary, Work log, Tasks touched, Decisions & notes, Follow-ups). Use whenever attempting or completing a task in the vault, and always as part of the "update the vault" convention. Append surgically; never rewrite or reorder.
---

# Vault journal

A living journal of each day's work. The point is continuity: any future
session can read recent daily notes and reconstruct what happened, what was
decided, and what's still open.

## Location & naming

- **Folder:** `daily_notes/` in the vault root.
- **Filename:** `YYYY-MM-DD.md`, one per calendar day. Today's date comes
  from the session context — resolve any relative reference ("yesterday",
  "Monday") to absolute first.
- **Template:** `_templates/daily-note.md`. If today's note doesn't exist
  when an update is needed, create it from the template first.

## Structure (stable headings)

Keep these exact heading names so both Claude and the user can parse:

- `## Summary` — one or two lines; the headline of the day.
- `## Work log` — append-only chronological bullets. Format:
  ```
  - HH:MM — <project/area>: <attempted|done> — <concise description>
  ```
  Time is optional if unknown — never fabricate a precise time. 24-hour local.
- `## Tasks touched` — vault tasks created / advanced / completed, with the
  project file named (e.g. `<project>.md`).
- `## Decisions & notes` — choices made, assumptions, things learned.
- `## Follow-ups` — open threads carried into tomorrow.

## When to update

- **Whenever a task is attempted or accomplished**, append a `## Work log`
  bullet. This is the most common trigger.
- **Always when the user says "update the vault"** — the daily note is part of
  that convention (see vault-update skill), not a separate ask.
- New things happen anyway during normal work; capture them as they occur
  rather than reconstructing later.

## How to update

- **Surgical edits only.** Append bullets under the right heading. Don't
  rewrite the file or reorder existing entries.
- **Terse and factual.** These are log lines, not published prose. Any
  personal writing-voice guide the user maintains does **not** apply here —
  code-style brevity is correct.
- **Cross-reference project files** by filename (e.g. `<project>.md`) so each
  entry links back to the task spine.
- **Resolve dates/times to absolute.** Today's date from session context.
- **Don't pad.** A single-line bullet is the right size for most events.

## What goes in the journal vs. the project file

| Belongs in daily note | Belongs in project file |
|---|---|
| "Attempted X at 14:30; ran into Y" | The open task "do X" |
| "Decided to use approach A over B" | The decision documented in `## Notes` |
| "Talked to <collaborator> re: framing" | The follow-up task or status update |
| "Tomorrow: pick up where draft v2 left off" | Tomorrow's actual task |

Daily notes are the work log. Project files are the spine. The journal
references the spine; the spine doesn't duplicate the journal.
