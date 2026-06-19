---
name: vault-status
description: Six-bucket status grouping for the user's proposals and projects. Use whenever they ask "what is the status of my proposals/projects", "where do things stand", or any variant. Sort and group into Untouched → Proposal Idea Scoped → Drafting Currently → Submitted and Pending → Awarded → Complete (or otherwise no further work). Show every category even if empty. The live proposal list lives in `proposal-solicitations.md`.
---

# Vault status

When the user asks for the status of their proposals/projects, present a grouped
view across the six buckets. This is the default response for status questions;
the live proposal list lives in `proposal-solicitations.md`.

## The six buckets, in order

1. **Untouched** — on the radar, no work started.
2. **Proposal Idea Scoped** — concept defined, not yet drafting.
3. **Drafting Currently** — actively being written.
4. **Submitted and Pending** — submitted, awaiting outcome.
5. **Awarded** — funded; work underway.
6. **Complete or otherwise no further work**.

**Show every category, even if empty.** Mark an empty bucket `(none)`.

## How to build the report

1. Read `projects.md` to get the project list.
2. Read `proposal-solicitations.md` for the live proposal-call list.
3. Read `proposal-ideas.md` for idea-first entries (their `Status:` field
   maps to bucket 2 when they're at "Scoping solicitation" or "Promoted").
4. For each project file, look at the `**Status:**` line near the top to
   classify into a bucket.
5. Group and present.

## Format

```
**Untouched**
  (none)

**Proposal Idea Scoped**
  - <Solicitation name> (`<file>.md`) — Phase-I scoping.
  - Idea: <short title> (`proposal-ideas.md`) — Sketched.

**Drafting Currently**
  - <Proposal name> (`<file>.md`) — proposal in active drafting.
  - <Paper name> (`<file>.md`) — companion paper.

**Submitted and Pending**
  - <Proposal name> (`<file>.md`) — submitted 2026-03-31, awaiting review.

**Awarded**
  - <Project name> (`<file>.md`) — direction-setting phase.

**Complete or otherwise no further work**
  (none)
```

Keep each entry to one line: bucket-relevant note + project filename in
backticks. Include the most recent date or deadline when relevant.

## Default scope

Default scope is **everything**: proposals (drafting / submitted / awarded)
*and* other ongoing projects (papers, service, tools). If the user asks
specifically for proposals only, scope to those.
