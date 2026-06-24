# Design — folder-agnostic vault + themed subfolders

**Date:** 2026-06-23
**Status:** Approved (brainstorming); pending implementation plan.

## Problem

A vault accumulates one markdown file per project at the **root**. A mature
vault (Gilly's has ~26 files) buries the handful of index/system files among
project, proposal, admin, and personal files. We want to organize content into
themed subfolders without breaking the engine (dashboard, `/status`,
`/capture`, `/triage`, `/update`) and without forcing every vault — including a
colleague's fresh, flat one — into a particular layout.

## Goals / non-goals

**Goals.** Let a vault organize project files into arbitrary subfolders; keep
every read/write path working regardless of where a file sits; preserve
backward compatibility with existing flat vaults; migrate Gilly's vault to a
chosen taxonomy.

**Non-goals.** No change to task syntax, the six-bucket status model, the
two-tier memory, or Obsidian behavior beyond making paths tolerant. No change
to where daily notes or memory files live.

## Design

### 1. Engine: folder-agnostic (the core change)

The engine stops assuming project files live at the root. It locates them by
scanning, with a skip-list, rather than by a fixed path.

- **`scripts/build_dashboard.py`** — walk the vault **recursively** instead of a
  root-only `glob("*.md")`. Group tasks by their containing folder, then file.
  Exclude, by directory: `.git/`, `.obsidian/`, `_templates/`, `memory/`,
  `daily_notes/`, and any asset dirs (e.g. `proposal-ideas/figures/`). Exclude,
  by filename (system/index files): `README.md`, `CLAUDE.md`, `projects.md`,
  `journaling.md`, `dashboard.md`. Everything else is a task-bearing project
  file. `inbox.md` continues to be scanned and keeps its own filter.
- **Commands / skills prose** (`vault-projects`, `vault-tasks`, `vault-status`,
  `vault-update`; `start`, `capture`, `status`, `triage`, `update`,
  `dashboard`) — reword "one file per project at the vault root" to "one file
  per project, which may live in a subfolder." Capture/status/triage/update
  locate files by scanning, not by assuming root. New project files default to
  `projects/` (or the subfolder matching the work), not the root.

The exact folder names are **never hardcoded** — the engine treats any
subfolder as a grouping. A flat vault (no subfolders) is just the degenerate
case and keeps working unchanged.

### 2. Taxonomy for Gilly's vault (data migration, not engine)

| Location | Files |
|---|---|
| **(root)** — system/index | `CLAUDE.md`, `README.md`, `projects.md`, `journaling.md`, `dashboard.md`, `dashboard.html`, `inbox.md`; plus `memory/`, `daily_notes/`, `_templates/` |
| **`projects/`** | punch-pulse, punch-science, punch-video-tools, rhef, sunback, solar-archive, gilly-space, ghosts, flux-fluxon, radiant-surya, aia-desaturation, dkist-waves, hfr-coronal-heating, lws-flare-ribbons, ec-lac, space-weather-solicitation |
| **`proposals/`** | proposal-solicitations, proposal-ideas |
| **`admin/`** | nwra-admin, travel |
| **`misc/`** | personal, showcase |

### 3. Dashboard display

Group the board by folder, then by file — a "projects" cluster, a "proposals"
cluster, an "admin" cluster, etc. — rather than one flat list. `inbox.md` keeps
its dedicated filter. The existing filters (overdue, this week, high, inbox,
all) are unchanged.

### 4. Two-repo handling

The engine change is made upstream in `research-vault-plugin`, then pushed to
the `gilly-vault` fork with `scripts/sync-engine.sh`. The vault migration
(section 2) touches only Gilly's vault (`research-tasks`) and is a separate
commit. This design doc lives under `docs/superpowers/specs/`; add
`docs/superpowers/` to the sync-engine excludes so internal specs stay in the
upstream dev repo and do not propagate to personal forks.

## Migration sequencing

1. Engine: recursive scan + folder-agnostic prose (upstream), sync to the fork.
2. Vault: `git mv` files into `projects/`, `proposals/`, `admin/`, `misc/`;
   update the `projects.md` manifest links to the new paths; audit
   `dashboard.md`'s Obsidian Tasks queries for any path scoping.
3. Test the read paths (see below).

## Testing

- Regenerate the dashboard against the migrated vault: tasks appear, grouped by
  folder; the inbox filter works; no stray tasks leak from `memory/` or
  `daily_notes/`.
- `/status` reads the proposal trackers in `proposals/` and each project's
  `**Status:**` line in `projects/`.
- `/capture` routes a new task into a project file in its subfolder.
- A flat vault (no subfolders) still produces a correct dashboard
  (back-compatibility).

## Risks

- **Recursion surfacing non-task checkboxes** — mitigated by the directory
  skip-list (`memory/`, `daily_notes/`, `_templates/`, assets).
- **Obsidian path-scoped queries** in `dashboard.md` — audited and updated in
  migration step 2.
- **Cross-references** — the vault refers to files as backtick text
  (`` `sunback.md` ``); Obsidian resolves wikilinks by basename regardless of
  folder, so these survive the move. Any hardcoded relative markdown links
  would need fixing, but the vault does not use them.
