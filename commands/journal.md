---
description: Append to today's daily note. Default appends a `## Work log` bullet; `--summary "..."` updates the headline; `--decision "..."` adds under Decisions & notes; `--followup "..."` adds under Follow-ups.
argument-hint: "[--summary|--decision|--followup] \"text\""
---

# /journal

Surgical append to today's `daily_notes/YYYY-MM-DD.md`. See the vault-journal
skill for structure and rules.

## Instructions

### 1. Locate today's note

- Compute today's date from session context.
- If `daily_notes/<today>.md` doesn't exist, create it from
  `_templates/daily-note.md` first.

### 2. Parse arguments

| Flag | Action |
|---|---|
| (none) | Append a `## Work log` bullet. Use the rest of `$ARGUMENTS` as the description. |
| `--summary "..."` | Replace the `## Summary` body (only place this command overwrites). |
| `--decision "..."` | Append a bullet under `## Decisions & notes`. |
| `--followup "..."` | Append a bullet under `## Follow-ups`. |
| `--task <file.md> "..."` | Append to `## Tasks touched`, naming the project file. |

If `$ARGUMENTS` is empty, ask the user what to append.

### 3. Format

- Work log bullet: `- HH:MM — <project/area>: <attempted|done> — <description>`
  - Default time is the current local time (24-hour).
  - If the area is obvious from the active conversation (a project file was
    being edited), use it; otherwise infer or ask.
  - "attempted" vs "done": ask once if not implicit; default to "done" only
    if a task was just checked off.
- Decisions / Follow-ups / Tasks-touched: plain bullets, terse, factual.

### 4. Voice

Terse and factual. Code-style brevity. Any personal writing-voice guide does
**not** apply here — log lines, not prose.

### 5. Report

```
Appended to daily_notes/<date>.md → <section>: <one-line preview>
```

## Notes

- Never reorder existing entries.
- Never rewrite the whole file — append only (except `--summary`).
- Resolve any relative date/time to absolute before writing.
