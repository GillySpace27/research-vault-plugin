---
name: vault-update
description: The "update the vault" convention as a full multi-file reconciliation flow. Use whenever the user says "update the vault", "log this into the vault", "here are a few tasks, update the vault", or any variant. Triggers an audit of every project file relevant to the recent conversation — not a single append. Also covers the comprehensive-mode deep scan over Slack, Gmail, Calendar, Notion, and project trackers.
---

# Vault update

When the user says **"update the vault"** — or any natural variant ("log this
email into the vault", "update the vault with this", "here are a few tasks,
update the vault") — treat it as a request to **audit and update every project
task file relevant to the conversation**, not just append one line.

## Default mode

### 1. Identify scope

Walk the recent conversation. List every project file that any piece of it
touches. If something is a sustained new line of work that fits no existing
file, plan to create a new `<project>.md` (see vault-projects skill) and add
it to `projects.md`.

### 2. Reconcile each affected file

For each file, surgically update:

- **Status line** at the top, if the high-level state changed (e.g.
  "submitted → awaiting review").
- **`## Open`** — add new tasks, advance in-progress ones, check off
  completed ones (with `✅ YYYY-MM-DD`).
- **`## On hold`** — promote if work paused on an external trigger, demote
  back to Open if unblocked.
- **`## Done`** — move completed items if the file convention requires it.
- **`## Notes`** — append assumptions, decisions, references discussed.
- **`## People`** — add new collaborators with project-specific context;
  also update the vault-people skill if they're recurring.
- **Dates** — resolve every relative reference to absolute `YYYY-MM-DD`.

### 3. Append to today's daily note

For each meaningful action taken in this session, append a `## Work log`
bullet to `daily_notes/YYYY-MM-DD.md` (create from template if missing). See
vault-journal skill for format.

### 4. Capture, don't curate

Don't reformat surrounding content. Don't reorder. Don't make it pretty. The
point of the system is fast capture (see vault-tasks principle).

### 5. Report back

In your final message, list what landed where, organized by file. Flag any
assumptions or ambiguous references in a short "Assumed" section so the user
can correct them in one line. Example:

```
Updated:
- <proposal>.md — added 2 open tasks, marked NOI done
- <paper>.md — appended feedback to ## Notes
- daily_notes/2026-05-24.md — 3 work-log bullets, 1 follow-up
- inbox.md — 1 task (unclear project)

Assumed:
- "Sarah" meant <Sarah Lastname> (<project> context) — correct me if not.
- "by Friday" resolved to 2026-05-29.
```

## Comprehensive mode

When invoked via `/update --comprehensive` (or "do the full sweep"), run
everything above, plus:

### Extra step A — Scan external activity

Gather from available MCP sources:

- **Gmail** — search sent messages and recent threads (especially with
  collaborators in the vault-people roster).
- **Google Calendar** — list recent + upcoming events; flag meetings that
  mention vault projects with no associated open tasks.
- **Slack** — search recent messages, read DMs and project channels.
- **Notion** — list recently touched docs.
- **Project tracker** (Asana / Linear / Atlassian / monday / ClickUp) — pull
  tasks assigned to the user that aren't already in the vault.

### Extra step B — Flag missed todos

Compare external activity against vault `## Open` blocks. Surface action items
that aren't tracked, grouped by source:

```
## Possible missing tasks

From Gmail (2026-05-22):
- "I'll send the updated analysis by next week" (to: <collaborator>)
  → <project>.md?

From Calendar:
- Recurring "<project> sync" Thursdays, no open tasks in <project>.md
  → Anything needed?
```

Let the user pick which to add. Never auto-add.

### Extra step C — Suggest memory updates

Surface new people, projects, and terms not yet in `memory/` or the vault-
people roster:

```
## New people (not in memory)
| Name | Frequency | Context |
|---|---|---|
| Jamie Park | 6 emails this week | data pipeline |

## Suggested cleanup
- "<project>" — no activity in 30 days. Demote from CLAUDE.md hot cache?
```

High-confidence additions are offered directly. Low-confidence are asked about.

## Notes

- Never auto-add tasks or memories without confirmation.
- Comprehensive mode always runs interactively.
- Safe to run frequently — only updates when there's new info.
- If an MCP source isn't connected, skip it and note the gap.
