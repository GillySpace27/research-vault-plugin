# research-vault

A Claude Code plugin that turns a folder of plain-markdown files into a
research-task vault: **one file per project**, GitHub-style checkbox tasks with
Obsidian Tasks-plugin emoji metadata, a daily journal, a six-bucket
proposal/project status view, and a two-tier memory of your people, projects,
and shorthand.

It mirrors the capabilities of Anthropic's official `productivity` plugin
(`/start`, `/update`, `/update --comprehensive`, memory tiering, MCP-backed
external sync, an HTML dashboard) but keeps the per-project markdown shape, the
emoji task syntax, the daily journal, and the proposal status groupings —
none of which fit the single-`TASKS.md` model.

**Bring your own everything.** The plugin ships *conventions*, not anyone's
data. `/start` creates the vault and interviews you to seed your own people,
projects, and memory.

## Install

```
/plugin marketplace add GillySpace27/research-vault-plugin
/plugin install research-vault@research-vault-local
```

(Or point the marketplace at a local clone:
`/plugin marketplace add /path/to/research-vault-plugin`.)

Then, in any Claude Code session:

```
/start
```

On first run, `/start` asks where the vault should live (default
`~/research-vault/`), creates the folder, scaffolds the core files, and runs a
short interview to seed your roster, projects, and glossary. Nothing leaves
your machine.

## Commands

| Command | What it does |
|---|---|
| `/start` | First run: create the vault + interview to seed it. Later: verify files, open today's note. |
| `/update` | "Update the vault": reconcile every project file relevant to the recent conversation, advance/close tasks, append to today's daily note. |
| `/update --comprehensive` | Plus deep scan: Slack/Gmail/Calendar/Notion/project-tracker for missed tasks, status changes, new people. |
| `/status` | Six-bucket proposal/project status report (Untouched → Complete). |
| `/journal` | Append a `## Work log` line (or fuller entry) to today's daily note. |
| `/triage` | Inbox triage: walk `inbox.md`, decide a route, move surgically. |
| `/capture <text>` | Drop a one-line task into the most likely project file (or `inbox.md` if ambiguous). 10-second rule. |
| `/dashboard` | Regenerate the interactive `dashboard.html` from the vault. |

## Skills

Loaded automatically when you're working in the vault — they encode the
conventions so future sessions don't need to be re-briefed.

| Skill | Role |
|---|---|
| `vault-tasks` | Task syntax (checkboxes + emoji metadata), capture rules. |
| `vault-projects` | Project manifest, when to make a new file, operating principles. |
| `vault-people` | Roster decoder for handles like `#firstname-lastname`. Your roster lives in the vault `CLAUDE.md` hot cache. |
| `vault-journal` | Daily journal location, structure, when/how to update. |
| `vault-update` | The "update the vault" multi-step reconciliation flow. |
| `vault-status` | Six-bucket status grouping for proposals/projects. |
| `vault-memory` | Two-tier memory (vault `CLAUDE.md` hot cache + `memory/` deep storage). |

## Vault layout created

```
<vault>/
├── CLAUDE.md            ← hot-cache memory (your people/projects/prefs) + plugin pointer
├── README.md            ← human-readable vault overview
├── dashboard.md         ← Obsidian Tasks queries
├── dashboard.html       ← (optional) interactive board view, via /dashboard
├── projects.md          ← project manifest
├── journaling.md        ← daily journal guidelines
├── inbox.md             ← capture catch-all
├── <project>.md         ← one per project
├── daily_notes/YYYY-MM-DD.md
├── memory/              ← two-tier memory (hot cache lives in CLAUDE.md)
│   ├── glossary.md
│   ├── people/<name>.md
│   ├── projects/<name>.md
│   └── context/
└── _templates/          ← project.md, daily-note.md
```

The `_examples/` folder in the plugin shows the intended shape of a filled-in
roster, manifest, and hot cache (using fictional names) — read them for
orientation; `/start` writes your real versions.

## MCP connectors

Pre-configured in `.mcp.json` (same set as the Anthropic productivity plugin):
Slack, Gmail, Google Calendar, Notion, Asana, Linear, Atlassian, monday,
ClickUp, Microsoft 365. Each requires you to authenticate the corresponding
MCP endpoint. They're optional — the vault works fully offline; the connectors
only power `/update --comprehensive`.

## Obsidian (optional)

The vault is plain markdown, so it opens in any editor. If you use Obsidian
with the Tasks plugin, the emoji metadata (📅 ⏳ ✅ 🔼 🔽) renders as real
task properties and `dashboard.md`'s queries become a live board.
