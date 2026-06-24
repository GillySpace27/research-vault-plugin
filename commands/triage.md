---
description: Inbox triage. Walk `inbox.md`, decide for each open item — move to a project file, delete, defer, or split out a new project file. Five-minute pass; never longer.
---

# /triage

The inbox sweep (a good weekly cadence). Goal: empty (or near-empty) `## Open`
block in `inbox.md` by routing each item to its rightful home.

## Instructions

### 1. Read state

- `inbox.md` — list each open `- [ ]` item under `## Open`.
- `projects.md` — the project manifest (so candidate target files are top of mind).

### 2. For each open inbox item

Present one at a time (or batch if the user says "go fast"). For each:

1. Propose a route based on content and the vault-projects skill:
   - **Move to project file** — most common. Specify which.
   - **Delete** — if it's stale, no longer relevant, or was a one-off note
     not actually requiring action.
   - **Defer** — leave in inbox, but only if it genuinely cross-cuts and
     can't be placed.
   - **Split into a new project file** — only if it's a sustained line of
     work that fits no existing file (see vault-projects principles).

2. Wait for the user to confirm (default: yes if they don't push back). For
   batches, present the proposed routes as a table and let them override.

### 3. Execute

For each confirmed move:

- **To a project file**: append the task line under that file's `## Open`,
  preserving emoji metadata. Remove from `inbox.md`.
- **Delete**: remove from `inbox.md`. If it was checked-off (`- [x]`), leave
  it under `## Done`.
- **Defer**: leave in `inbox.md`. Log a short note next session.
- **New project**: scaffold `projects/<name>.md` from `_templates/project.md`,
  add an entry (with its path) to `projects.md`, move the task into the new file.

### 4. Surgical edits

Don't reformat `inbox.md` or the target files. Append to `## Open`; remove
the corresponding line from `inbox.md`. Section structure stays intact.

### 5. Report

```
Triaged N items:
- → <project-a>.md: 2
- → <project-b>.md: 1
- → new file <project-c>.md: 1 (added to projects.md)
- deleted: 1
- deferred: 1

Inbox.md ## Open: <count remaining>
```

## Cadence

A good convention is **weekly, five minutes max**. If `inbox.md` is empty or
near-empty, say so and stop — don't invent work.
