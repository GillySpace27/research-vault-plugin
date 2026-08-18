---
description: Six-bucket status report for proposals, papers, and projects. Proposals go Untouched → Proposal Idea Scoped → Drafting Currently → Submitted and Pending → Awarded → Complete; papers go Untouched → Idea Scoped → Drafting Currently → Submitted / Under Review → Accepted → Published. Show every category even if empty.
argument-hint: "[proposals|papers|projects|all]"
---

# /status

Render the six-bucket status grouping defined by the vault-status skill.

## Scope

- `$ARGUMENTS` empty or `all` → everything: proposals (drafting / submitted /
  awarded), papers (drafting / submitted / accepted / published), plus other
  ongoing projects (service, tools).
- `proposals` → only entries from `proposal-solicitations.md` and
  `proposal-ideas.md`, plus proposal-bearing project files.
- `papers` → only entries from `papers.md`, plus paper-bearing project files.
- `projects` → only the non-proposal, non-paper project files.

## Instructions

1. Read `projects.md` for the project list (it records each file's path, which
   may be in a subfolder such as `projects/` or `proposals/`).
2. Read `proposal-solicitations.md` and `proposal-ideas.md` (at the vault root,
   or under `proposals/` — use the path from `projects.md`).
3. Read `papers.md` (at the vault root, or wherever `projects.md` points).
4. Read the `**Status:**` line at the top of each project file, wherever it lives.
5. Classify each into a bucket using the heuristics in the vault-status skill —
   proposals use the proposal bucket set, papers use the paper bucket set.
6. Render every bucket — `(none)` for empty ones — in the order defined by
   the skill, proposals and papers as separate blocks.
7. One line per entry: bucket-relevant note + project filename in backticks.
   Include the most recent date or deadline when relevant; for papers, also the
   author position (first author / co-author).

## Output shape

See the vault-status skill for the canonical format. Keep it scannable, not
prose.
