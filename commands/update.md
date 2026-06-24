---
description: 'The "update the vault" convention as a command — reconcile every project file relevant to the conversation, advance/close tasks, append to today''s daily note. Add --comprehensive for a deep scan of email/calendar/chat/project tracker.'
argument-hint: "[--comprehensive]"
---

# /update

This command is the slash-command form of the "update the vault" convention.
See the vault-update skill for the full logic; this file is the entry point.

## Default mode

Run the steps in the vault-update skill, default section:

1. Identify scope — every project file the recent conversation touches
   (project files may live in subfolders such as `projects/`; locate them via
   `projects.md`, not by assuming the vault root).
2. Reconcile each affected file (status line, ## Open, ## On hold, ## Done,
   ## Notes, ## People, dates).
3. Append a `## Work log` bullet to today's `daily_notes/YYYY-MM-DD.md` for
   each meaningful action (create the daily note from
   `_templates/daily-note.md` first if missing).
4. Surgical edits only — capture, don't curate.
5. Report what landed where, with an "Assumed" section flagging ambiguous
   interpretations.

If nothing recent has touched the vault, ask the user what to reconcile.

## Comprehensive mode (`--comprehensive`)

Everything above, plus the extra steps from the vault-update skill's
comprehensive section:

- Scan Gmail, Google Calendar, Slack, Notion, and the connected project
  tracker (Asana / Linear / Atlassian / monday / ClickUp) via MCP.
- Flag missed todos — surface action items in external activity that aren't
  yet in any vault `## Open` block. Group by source.
- Suggest memory updates — new people, projects, and terms; promotion /
  demotion candidates for the hot cache.

Always interactive. Never auto-add tasks or memory entries.

## Argument parsing

- `--comprehensive` (or `-c`) anywhere in `$ARGUMENTS` → comprehensive mode.
- Anything else in `$ARGUMENTS` → treat as scope hint (e.g. `/update
  <project>` → narrow the reconciliation to that file).

## Report shape

```
Updated:
- <file>.md — <what changed in one line>
- daily_notes/<date>.md — <N bullets, M follow-ups>

Assumed:
- <ambiguous interpretation> — correct me if wrong.

(comprehensive only)
Possible missing tasks:
- <source>: "<excerpt>" → <suggested project file>?

New people / projects to capture:
- <name>: <freq + context> → add to memory?
```

## Notes

- If an MCP source isn't connected, skip it silently and mention the gap in
  the report rather than blocking.
- The full reconciliation logic lives in the vault-update skill so other
  triggers (the phrase "update the vault", etc.) get the same behavior.
