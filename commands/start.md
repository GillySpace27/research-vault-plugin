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
- Else if the `RESEARCH_VAULT_DIR` environment variable is set
  (`echo $RESEARCH_VAULT_DIR`), use that.
- Else, if a vault `CLAUDE.md` is already loaded in context, use the
  `**Vault path:**` it records.
- Else default to `~/research-vault/`.
- If the path doesn't exist, this is **first-run** — confirm the location with
  the user ("I'll create your vault at `~/research-vault/` — ok, or somewhere
  else?"), then create it.

### 2. First-run setup (vault folder is empty or absent)

If the vault has no `projects.md`, treat it as first-run. Do this:

**a) Create the folder and skeleton.** Make the vault directory, plus
`daily_notes/`, `memory/people/`, `memory/projects/`, `memory/context/`. Then:

- Copy `_templates/project.md` and `_templates/daily-note.md` from
  `${CLAUDE_PLUGIN_ROOT}/_templates/` into the vault's own `_templates/`.
- Separately, seed `memory/glossary.md` by copying
  `${CLAUDE_PLUGIN_ROOT}/_templates/glossary.md`.

**b) Interview the user** (keep it short — 4 quick questions, accept "skip"):

```
Let's seed your vault. I'll ask a few quick things — say "skip" to any.

1. Your name + role/affiliation? (used to personalize the vault, nothing leaves
   your machine)
2. Your 3–8 most frequent collaborators — name, affiliation, what you work on
   together. I'll coin #firstname-lastname handles.
3. Your active projects — a short name + one line each. I'll make one file per
   project. Flag any that are grant proposals and their stage (idea / drafting /
   submitted / awarded) so I can also seed your proposal trackers.
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
- **Starter files copied verbatim** from `${CLAUDE_PLUGIN_ROOT}/_templates/`
  into the vault root (these ship as real templates — copy, don't improvise):
  `inbox.md`, `personal.md`, `dashboard.md`, `journaling.md`,
  `proposal-solicitations.md`, `proposal-ideas.md`, and `vault-README.md`
  (write it to the vault as `README.md`). If the user flagged any project as a
  proposal in Q3, add an entry for it to `proposal-solicitations.md` (with its
  `Status:` stage) or `proposal-ideas.md` (if idea-first), so the first
  `/status` is coherent rather than empty.
- **`memory/glossary.md`** — append the codenames/acronyms the user gave to
  the glossary already seeded in step (a).
- **`memory/people/<handle>.md`** — one per collaborator named.
- The roster lives in the vault `CLAUDE.md` hot cache (the `vault-people`
  skill is read-only and points there) — keep the People table there, not in
  the plugin.

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
