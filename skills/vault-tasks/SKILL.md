---
name: vault-tasks
description: Task syntax and capture rules for the research vault. Use whenever adding, editing, completing, or referencing tasks in any vault `.md` file. Tasks are GitHub-style checkboxes with optional Obsidian Tasks-plugin emoji metadata (📅 ⏳ ✅ 🔼 🔽 #person). One file per project, with `inbox.md` as the catch-all. Capture is fast and surgical — never more than ten seconds to add a task.
---

# Vault tasks

The vault is plain markdown — read by Obsidian (Tasks plugin), Claude, or any
text editor. Tasks are the spine of every project file.

## Syntax

GitHub-style checkboxes, one task per line:

```
- [ ] thing to do
- [x] thing already done
```

Optional metadata, **used only when natural** — do not fabricate:

| Marker | Meaning | When to use |
|---|---|---|
| `📅 YYYY-MM-DD` | Due date | A real deadline was given. |
| `⏳ YYYY-MM-DD` | Scheduled / start date | The task shouldn't be acted on before this date. |
| `✅ YYYY-MM-DD` | Completion date | Added when checking the task off. |
| `#person-handle` | Person involved | Use the canonical handle (see vault-people skill). |
| `🔼` | High priority | The user flagged urgency, or it's blocking other work. |
| `🔽` | Low priority | The user explicitly deprioritized, or it's a nice-to-have. |

Examples:

```
- [ ] Send patch v3 to #collaborator 📅 2026-05-30 🔼
- [ ] Triage starred emails (one-time backlog clear)
- [x] Submit final proposal ✅ 2026-03-31
```

## Where tasks live

- **One file per project.** `<project>.md` for each line of work. The project
  manifest is `projects.md`. (See vault-projects skill.)
- **`inbox.md` is the catch-all.** Drop here when the right project is unclear
  or the task is genuinely cross-cutting.
- **`personal.md`** for non-work.
- Inside each project file, tasks live under `## Open`. Completed tasks move
  to `## Done` (or stay in place with `[x]` if context matters). Some files
  also have `## On hold` for paused work.

## Capture rules

1. **Capture, don't curate.** When the user hands you a task, put it in the
   right place and move on. Don't reformat surrounding content. Goal: under ten
   seconds from "here's a task" to written.
2. **Use surgical edits.** Append to the right `## Open` block. Don't rewrite
   files unless the structure genuinely needs it.
3. **Don't fabricate dates.** Only add `📅` if the user gave a real deadline or
   said something like "asap" / "by Friday" / "this week" → then resolve to
   absolute `YYYY-MM-DD` using today's date from the session context.
4. **Tell the user what you assumed.** If you interpreted an ambiguous
   reference (which project, which person, which deadline), say it in one line
   so they can correct it.
5. **No padding.** Brief beats thorough. Hour estimates only if asked.

## Completion

When the user says they're done with X:

1. Find the task.
2. Change `[ ]` → `[x]`.
3. Append `✅ YYYY-MM-DD` (today's date).
4. Leave it under `## Open` for the rest of the day (so the daily journal can
   reference it), or move to `## Done` if the file convention requires it.
5. Append a `- HH:MM — <project>: done — <description>` bullet to today's
   daily note (see vault-journal skill).

## What's on my plate

When the user asks "what's open" / "what's on my plate":

1. Read `dashboard.md` first — its Obsidian Tasks queries already aggregate
   across files.
2. If that's not enough, walk project files in `projects.md` order, summarizing
   `## Open` blocks.
3. Surface due/overdue items and 🔼-priority items at the top.

## Extraction from conversation

When a meeting summary, email, or chat contains commitments:

- Pull out commitments the user made ("I'll send X", "I'll review Y by Friday").
- Pull out action items assigned to them.
- Offer them grouped by project file before writing; don't auto-add without
  confirmation — but once confirmed, write all at once.
