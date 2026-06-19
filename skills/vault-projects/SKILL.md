---
name: vault-projects
description: Project model for the research vault — one `.md` file per project, listed in `projects.md`. Use whenever a task or new line of work needs routing to (or creating as) a project file, or when the user refers to a project by a short codename or acronym. The user's actual project list and codenames live in `projects.md` and the vault `CLAUDE.md` hot cache — read those for the live roster.
---

# Vault projects

Each substantive line of work gets its own file under the vault root. The
canonical list — with one-line descriptions of each — lives in `projects.md`.
Read that file first when you need to know what exists.

## Operating principles

1. **One file per project.** Grants, papers, ongoing projects each get their
   own `.md` file. Tasks live inside the project they belong to.
2. **`inbox.md` is the catch-all** for capture and triage.
3. **Standard sections:** `## Open`, `## Done`, `## Notes`. Some files also
   have `## On hold`, `## Open questions`, `## People`. Keep section names
   stable so queries and skills can rely on them.
4. **Tasks are the spine.** Notes and context belong in `## Notes`, but the
   primary structure of each file is its open task list.
5. **Don't pad.** Brief is better than thorough. The point of this system is
   that capture takes seconds.
6. **Don't reformat unprompted.** Surgical edits only.

## When to create a new project file

Only when the work is sustained — a one-off task goes into `inbox.md` or an
existing project. Create a new `<project>.md` when:

- It's a grant proposal the user is drafting or has been awarded.
- It's a paper in progress.
- It's an ongoing service obligation (committee, group meetings).
- It's a tool/codebase that generates recurring tasks.
- It's a recurring administrative bucket (e.g. `admin.md`).

Process for a new file:

1. Scaffold from `_templates/project.md`.
2. Pick a lowercase-hyphen filename matching the project's natural name
   (`coronal-heating.md`, `flare-ribbons.md`).
3. Add an entry to `projects.md` under the alphabetical project list — a
   one-line description matching the existing style (`**NAME** (`file.md`) —
   summary.`).
4. If it's a proposal, also add it to `proposal-solicitations.md` (if matched
   to a call) or `proposal-ideas.md` (if idea-first).

## Project codenames

The user often refers to projects by short codenames or acronyms rather than
filenames. The live mapping lives in two places — read them, don't guess:

- **`projects.md`** — the authoritative one-line description of every project
  file.
- The **vault `CLAUDE.md` hot cache** and `memory/glossary.md` — codename →
  filename rows (see vault-memory skill).

When you meet an unfamiliar codename, check those, then ask the user in one
line if it's still unclear. `_examples/projects.example.md` in the plugin shows
the intended shape of a filled-in manifest — read it for orientation only, not
as real projects.

## When in doubt about placement

When unsure which file something belongs to: **ask in one line**, or drop it in
`inbox.md` and note the assumption.

## When the user says "update the vault"

See the vault-update skill — that phrase triggers a multi-file reconciliation,
not a single append.
