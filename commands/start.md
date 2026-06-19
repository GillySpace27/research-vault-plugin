---
description: Initialize or open a research-task vault — on first run, create the folder, scaffold the core files, and interview you to seed people/projects/memory. On later runs, verify files and open today's note.
argument-hint: "[vault path]"
---

# /start

Open the vault, check that everything is in place, bootstrap any missing
pieces. **On a brand-new machine the vault does not exist yet — this command
creates it and interviews you to seed it.**

## Instructions

### 1. Locate the vault

- If `$ARGUMENTS` is non-empty and a directory, treat it as the vault path.
- Else check the vault `CLAUDE.md` hot cache (if a vault was set up before) for
  a recorded path.
- Else default to `~/research-vault/`.
- If the path doesn't exist, this is **first-run** — confirm the location with
  the user ("I'll create your vault at `~/research-vault/` — ok, or somewhere
  else?"), then create it.

### 2. First-run setup (vault folder is empty or absent)

If the vault has no `projects.md`, treat it as first-run. Do this:

**a) Create the folder and skeleton.** Make the vault directory, plus
`daily_notes/`, `memory/people/`, `memory/projects/`, `memory/context/`, and
copy `_templates/project.md`, `_templates/daily-note.md`, and
`_templates/glossary.md` from `${CLAUDE_PLUGIN_ROOT}/_templates/` into the
vault's `_templates/` and `memory/glossary.md`.

**b) Interview the user** (keep it short — 4 quick questions, accept "skip"):

```
Let's seed your vault. I'll ask a few quick things — say "skip" to any.

1. Your name + role/affiliation? (used to personalize the vault, nothing leaves
   your machine)
2. Your 3–8 most frequent collaborators — name, affiliation, what you work on
   together. I'll coin #firstname-lastname handles.
3. Your active projects/proposals — a short name + one line each. I'll make one
   file per project.
4. Any codenames or acronyms you use that I should know? (e.g. "the storefront"
   = a specific app)
```

**c) Write the seed files** from the answers:

- **`CLAUDE.md`** (the vault hot cache) — a thin pointer to this plugin plus:
  a People table (top collaborators), an Active projects list, a Preferences
  section, and the recorded vault path. Use the `_examples/vault-CLAUDE.example.md`
  shape in the plugin as the model.
- **`projects.md`** — one `**NAME** (`file.md`) — one-line summary.` per project
  the user named, alphabetical.
- **One `<project>.md`** per named project, scaffolded from
  `_templates/project.md`, with the Status line and a People stub filled.
- **`inbox.md`**, **`README.md`**, **`dashboard.md`** (Obsidian Tasks queries),
  **`journaling.md`**, **`proposal-solicitations.md`**, **`proposal-ideas.md`**,
  **`personal.md`** — minimal starters. Models for each live in
  `_examples/` in the plugin.
- **`memory/glossary.md`** — add the codenames/acronyms the user gave.
- **`memory/people/<handle>.md`** — one per collaborator named.
- Also add the top collaborators to the **vault-people skill roster table** is
  NOT possible (the skill is read-only inside the plugin) — instead, the
  roster lives in the vault `CLAUDE.md` hot cache. Keep it there.

Report everything created.

### 3. Later runs — verify core files

Check for the following — list what's present and what's missing:

| Path | Purpose |
|---|---|
| `CLAUDE.md` | Vault-level hot-cache memory + plugin pointer |
| `README.md` | Human-readable vault overview |
| `projects.md` | Project manifest |
| `journaling.md` | Daily journal guidelines |
| `dashboard.md` | Obsidian Tasks queries |
| `dashboard.html` | Interactive board view (optional) |
| `inbox.md` | Capture catch-all |
| `_templates/daily-note.md` | Daily journal scaffold |
| `_templates/project.md` | New-project scaffold |
| `daily_notes/` | Daily journal folder |
| `memory/` | Two-tier memory deep storage |

Create only what's missing (from `${CLAUDE_PLUGIN_ROOT}/_templates/` or the
`_examples/` shapes). **Never overwrite an existing file.**

### 4. Open today's daily note

- Compute today's date from the session context (`YYYY-MM-DD`).
- If `daily_notes/<today>.md` doesn't exist, create it from
  `_templates/daily-note.md`, replacing `{{date:YYYY-MM-DD}}` with today.
- Don't open in a browser — just report the path. The user opens it in
  Obsidian / VS Code.

### 5. Optional comprehensive seeding (MCP-backed)

After the interview, if MCP connectors are configured, offer:

```
Want me to also scan your Gmail / Calendar / Slack / project tracker to find
collaborators and projects you didn't mention? (requires the connectors to be
authenticated) — see `/update --comprehensive` for the same logic.
```

Never auto-add — present candidates and let the user pick.

### 6. Report

```
Vault: <path>
- Project files: N
- Open tasks (from dashboard.md queries): ~X
- Today's note: daily_notes/2026-06-18.md (created | already existed)
- Memory: <bootstrapped | already populated | skipped>

Dashboard: open dashboard.md in Obsidian for the live task queries
         (or run /dashboard then open dashboard.html in a browser).

Next:
  /update              — reconcile from recent conversation
  /update --comprehensive — deep scan email/calendar/chat for missed work
  /status              — six-bucket proposal/project status
  /journal "..."       — append to today's daily note
  /triage              — inbox sweep
  /capture "..."       — quick task drop
```

## Notes

- This command is idempotent — safe to run any time. Later runs never
  re-interview unless the vault is empty.
- Never delete or overwrite vault content.
- The plugin's skills (vault-tasks, vault-projects, vault-people, vault-
  journal, vault-update, vault-status, vault-memory) load automatically when
  matching context appears; no need to invoke them explicitly.
