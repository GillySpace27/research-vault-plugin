---
description: Regenerate the interactive `dashboard.html` from the current vault. Runs `scripts/build_dashboard.py`, which parses every project `.md` file (skipping README/CLAUDE/projects/journaling/dashboard scaffolding) and renders a filterable board.
---

# /dashboard

Build (or rebuild) the static interactive dashboard for the vault.

## Instructions

1. Resolve the vault path: if `$ARGUMENTS` is non-empty and a directory, use
   that. Otherwise read the vault path recorded in the vault `CLAUDE.md` hot
   cache (set at `/start`), falling back to `~/research-vault/`.
2. Run:
   ```bash
   python "${CLAUDE_PLUGIN_ROOT}/scripts/build_dashboard.py" "<vault path>"
   ```
3. Report the written file path and the open/done/file counts the script
   prints.
4. Tell the user to open `dashboard.html` in any browser. Don't `open` it
   yourself — that's their call.

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
