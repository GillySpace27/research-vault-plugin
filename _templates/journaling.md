# Journaling

How the daily journal works in this vault. (The `vault-journal` skill enforces
these rules automatically — this file is the human-readable version.)

- **One note per calendar day** under `daily_notes/YYYY-MM-DD.md`, created from
  `_templates/daily-note.md`.
- **Stable headings:** `## Summary`, `## Work log`, `## Tasks touched`,
  `## Decisions & notes`, `## Follow-ups`. Keep the names exact.
- **Work log format:** `- HH:MM — <project/area>: <attempted|done> — <what happened>`.
- **Append, never rewrite.** Surgical edits only; don't reorder past entries.
- **Terse and factual** — these are log lines, not prose.

Append with `/journal "..."` (or just say "log this") and reconcile the day
with `/update`.
