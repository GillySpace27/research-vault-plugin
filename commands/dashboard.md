---
description: Regenerate the interactive `dashboard.html` from the current vault. Runs `scripts/build_dashboard.py`, which scans the vault recursively for project `.md` files (skipping README/CLAUDE/projects/journaling/dashboard scaffolding and the memory/daily_notes/_templates folders), groups them by folder, and renders a filterable board.
argument-hint: "[vault path]"
---

# /dashboard

Build (or rebuild) the static interactive dashboard for the vault.

## Instructions

1. Resolve the vault path, in order: `$ARGUMENTS` if it's a directory; else the
   `RESEARCH_VAULT_DIR` environment variable (`echo $RESEARCH_VAULT_DIR`); else
   the `**Vault path:**` recorded in a loaded vault `CLAUDE.md`; else
   `~/research-vault/`.
2. Run (use `python3`; fall back to `python` only if `python3` is absent):
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_dashboard.py" "<vault path>"
   ```
   Requires Python 3.7+. If no Python 3 is installed, tell the user the vault
   still works fully without `/dashboard` — `dashboard.md` in Obsidian is the
   live view.
3. Report the written file path and the counts the script prints (project
   files, open/done, papers/proposals, hours logged and estimated remaining).
   Relay any `warning:` lines on stderr: they flag config ambiguities, not
   crashes.
4. Tell the user to open `dashboard.html` in any browser. Don't `open` it
   yourself — that's their call.

## What the page shows

Five tabs: **Overview** (KPIs, four charts, the full table), **Papers** and
**Proposals** (six-bucket pipelines read from `papers.md` and
`proposals/proposal-solicitations.md`), **Projects** (grouped by folder), and
**Tasks** (overdue, scheduled, high-priority). Clicking any project row opens
its task list.

Effort estimates come from `scripts/timesheet.py`: hours logged per project
divided by tasks closed in the same window gives an hours-per-task rate, and
remaining = open tasks × rate, priority weighted. Projects without enough
closed tasks inherit the vault median and are marked `est`. Say plainly that
this is a planning estimate, not a promise: it assumes remaining tasks resemble
finished ones.

## Notes

- The HTML is **read-only**. Edits still happen in Obsidian / the editor /
  the plugin's `/capture`, `/journal`, `/update` commands.
- The dashboard.md (Obsidian Tasks queries) remains the live, in-Obsidian
  view. dashboard.html is for outside-Obsidian glance views (browser, phone
  via a synced folder, second monitor).
- Regenerate after any non-trivial set of vault edits — there's no
  filesystem-watcher in the static HTML.
- A future iteration could add write-back (drag-drop, checkbox toggling
  that updates the source `.md` files). That's not built yet.
