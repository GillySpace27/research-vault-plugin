# Getting started with research-vault

A short walkthrough for your first hour. The vault is a folder of plain-markdown
files — one per project — that Claude Code reads and writes through a handful of
slash commands. You own the files; the plugin just knows the conventions.

## Before you start

Only the first item is required.

- **Claude Code** — the plugin runs as a Claude Code plugin. *(required)*
- **Python 3.7+** — only for `/dashboard`, which renders an HTML board. The
  vault itself works without it. *(optional)*
- **Obsidian** — the vault is plain markdown and opens in any editor. If you use
  Obsidian with the **Tasks** plugin, the emoji metadata (📅 ⏳ ✅ 🔼 🔽) renders
  as real task properties and `dashboard.md`'s queries become a live board.
  *(optional)*
- **MCP connectors** (Gmail, Calendar, Slack, Notion, a project tracker) — only
  needed for `/update --comprehensive`, which scans those for tasks you forgot to
  capture. Everything else works fully offline. *(optional)*

## 1. Install

In any Claude Code session:

```
/plugin marketplace add GillySpace27/research-vault-plugin
/plugin install research-vault@research-vault-local
```

## 2. Create your vault — `/start`

```
/start
```

On the first run this does four things:

1. Asks where the vault should live (default `~/research-vault/`) and creates it.
2. Scaffolds the folder structure and templates.
3. Runs a **short interview** — four questions, and you can say "skip" to any:
   - your name + role,
   - your 3–8 most frequent collaborators (it coins `#firstname-lastname` handles),
   - your active projects/proposals (one file each),
   - any codenames or acronyms you use.
4. Writes *your* `CLAUDE.md` hot cache, `projects.md`, a file per project, and a
   `memory/` folder — seeded with your answers.

It takes about five minutes. **Nothing leaves your machine** — the interview just
populates local markdown files.

## 3. Use it day to day

| Command | What it does |
|---|---|
| `/capture "email Sam the draft by Friday"` | Drop a one-line task into the right project file (10-second rule). |
| `/update` | Reconcile the recent conversation into the vault — advance/close tasks, log the day. |
| `/status` | Six-bucket proposal/project status view. |
| `/journal "..."` | Append to today's daily note. |
| `/triage` | Weekly sweep of `inbox.md` — route each loose item to its project. |
| `/dashboard` | Regenerate the interactive `dashboard.html` (needs Python 3). |

You can also just *talk* — "add a task to the main grant", "what's open?", "I
finished the figure" — and the skills route it to the right file. You don't have
to memorize the commands.

## What to expect — good to know

- **It's shaped for research work.** The model assumes proposals, papers, service
  committees, and grant admin. The task list, daily journal, and memory transfer
  to any kind of work, but the proposal-status buckets in `/status` (Scoped →
  Drafting → Submitted → Awarded) only mean something if you write proposals. If
  you don't, ignore `/status` — nothing else depends on it.
- **The files are yours.** Plain markdown, no database, no lock-in. Edit them in
  any editor, diff them in git, read them in ten years. The plugin is just a
  convention layer on top.
- **Back up the vault.** It's a normal folder — `git init` it (or drop it in a
  synced folder) so your tasks and notes are versioned. The vault is *separate*
  from the plugin; losing the plugin never loses your data.
- **`/start` is safe to re-run.** It never overwrites existing files — later runs
  just verify the structure and open today's note. It only interviews you when the
  vault is empty.
- **Moving the vault?** Pass a path (`/start /path/to/vault`) or set the
  `RESEARCH_VAULT_DIR` environment variable so `/start` and `/dashboard` find it
  without asking.

## If something looks off

- Re-run `/start` — it's idempotent and will report what's present vs missing.
- Not sure where your vault is? Check the `**Vault path:**` line near the top of
  your vault's `CLAUDE.md`.
- A task landed in the wrong file? Tell Claude — "move that to the imaging-tool
  project" — or run `/triage`.

That's the whole system: capture in seconds, let `/update` keep the files honest,
and glance at `/status` or the dashboard when you need the big picture.
