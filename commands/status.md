---
description: Six-bucket proposal/project status report — Untouched → Proposal Idea Scoped → Drafting Currently → Submitted and Pending → Awarded → Complete. Show every category even if empty.
argument-hint: "[proposals|projects|all]"
---

# /status

Render the six-bucket status grouping defined by the vault-status skill.

## Scope

- `$ARGUMENTS` empty or `all` → everything: proposals (drafting / submitted /
  awarded) plus other ongoing projects (papers, service, tools).
- `proposals` → only entries from `proposal-solicitations.md` and
  `proposal-ideas.md`, plus proposal-bearing project files.
- `projects` → only the non-proposal project files.

## Instructions

1. Read `projects.md` for the project list (it records each file's path, which
   may be in a subfolder such as `projects/` or `proposals/`).
2. Read `proposal-solicitations.md` and `proposal-ideas.md` (at the vault root,
   or under `proposals/` — use the path from `projects.md`).
3. Read the `**Status:**` line at the top of each project file, wherever it lives.
4. Classify each into a bucket using the heuristics in the vault-status skill.
5. Render every bucket — `(none)` for empty ones — in the order defined by
   the skill.
6. One line per entry: bucket-relevant note + project filename in backticks.
   Include the most recent date or deadline when relevant.

## Output shape

See the vault-status skill for the canonical format. Keep it scannable, not
prose.
