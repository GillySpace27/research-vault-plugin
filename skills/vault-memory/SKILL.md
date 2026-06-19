---
name: vault-memory
description: Two-tier memory for the research vault. The vault `CLAUDE.md` is the hot cache (~30 most-used people, terms, projects). The `memory/` directory holds full storage — `glossary.md`, `people/<name>.md`, `projects/<name>.md`, `context/`. Use this skill whenever decoding shorthand, recording a new person/project/term, or deciding whether something belongs in the hot cache vs. deep storage.
---

# Vault memory

Two-tier memory makes Claude understand the user's shorthand without a re-brief
every session. The hot cache lives in the vault's `CLAUDE.md`. Deep storage
lives in `memory/`.

## Architecture

```
<vault>/
├── CLAUDE.md            ← Hot cache (~50-80 lines): top people, common
│                          terms, active projects, preferences
└── memory/
    ├── glossary.md      ← Full decoder ring (everything)
    ├── people/<name>.md ← Per-person profiles
    ├── projects/<name>.md ← Per-project context (separate from the task
    │                       file; this is *background*, not tasks)
    └── context/         ← Org-wide context, tools, processes
```

**CLAUDE.md goal:** cover 90% of daily decoding needs without a directory
walk. Keep it under ~100 lines.

**memory/ goal:** cover 100% of decoding needs, no size limit, searched
when the hot cache misses.

## Lookup flow

```
User: "ask <handle> about the cal status"

1. Check vault CLAUDE.md hot cache:
   - "<handle>" → ✓ resolved to a person in the roster
   - "cal" → ? not in hot cache

2. Check memory/glossary.md:
   - "cal" → calibration (a data-prep step)

3. If still not found → ask:
   - "What's X? I'll remember it."
```

## What goes where

| Type | Hot cache (vault CLAUDE.md) | Deep storage (memory/) |
|---|---|---|
| Person | Top ~30 frequent contacts | All people: `people/<name>.md` + glossary nickname row |
| Term/acronym | ~30 most common | All terms: `glossary.md` |
| Project | Active projects from projects.md | All: `projects/<name>.md` + glossary codename row |
| Nickname | Listed under top-30 person | All nicknames: `glossary.md` |
| Preferences | All preferences | — |
| Org-wide context | Quick reference only | `context/<org>.md`, `context/tools.md` |
| Historical / stale | Remove | Keep in `memory/` |

## Adding memory

When the user says "remember this" / "X means Y" / introduces a new
collaborator:

1. **Glossary item** (acronym, term, codename):
   - Add a row to `memory/glossary.md` under the right table.
   - If they'll use it often, also add to the hot cache in `CLAUDE.md`.

2. **Person:**
   - Create or update `memory/people/<handle>.md` (use the `#handle` form
     from vault-people skill).
   - Add to `CLAUDE.md` People table if they're in the top ~30.
   - Always capture nicknames — critical for decoding.

3. **Project background:**
   - Create or update `memory/projects/<name>.md` for project *context*
     (history, why it matters, key tradeoffs). The task spine stays in
     `<name>.md` at the vault root.
   - Add codename + filename to glossary.

4. **Preference:**
   - Add to the Preferences section of `CLAUDE.md`.

## Promotion / demotion

**Promote to hot cache when:**
- A term/person comes up frequently across sessions.
- A project moves from idea → active drafting → awarded.

**Demote to deep storage only when:**
- A project completes or goes dormant.
- A collaborator hasn't appeared in 60+ days.
- A term hasn't been used since the work it described shipped.

Run a promotion/demotion pass during `/update --comprehensive`.

## Per-person profile format (`memory/people/<handle>.md`)

```markdown
# <Full Name>

**Also known as:** <handle>, <alt-names>
**Role:** <role>
**Affiliation:** <institution>
**Email / contact:** <if known>

## Projects with the user
- <project-file.md> — what they do on it

## Communication
- <preferred channel, style notes>

## Context
- <anything useful for execution: who they report to, working hours, etc.>

## Notes
- <personal touches: shared interests, history>
```

## Per-project background format (`memory/projects/<name>.md`)

```markdown
# <Project name>

**Codename / aliases:** <if any>
**Vault file:** <name>.md
**Status:** <one line>

## Background
<Why this project exists, the funding source, the high-level goal>

## History
<Decisions made, paths not taken, prior versions>

## Key constraints
<Deadlines, dependencies, sensitivities>
```

## Bootstrapping

Run `/start` on a fresh vault to scaffold the directory and walk a recent
task list (or external sources, if MCP connectors are configured) to seed
the glossary, people, and projects deep storage.
