---
name: vault-status
description: Six-bucket status grouping for the user's proposals, papers, and projects. Use whenever the user asks "what is the status of my proposals/papers/projects", "where do things stand", or any variant. Proposals sort into Untouched → Proposal Idea Scoped → Drafting Currently → Submitted and Pending → Awarded → Complete; papers sort into the parallel Untouched → Idea Scoped → Drafting Currently → Submitted / Under Review → Accepted → Published. Show every category even if empty. The live proposal list lives in `proposal-solicitations.md`; the live papers list lives in `papers.md`.
---

# Vault status

When the user asks for the status of their proposals, papers or projects,
present a grouped view across six buckets. This is the default response for
status questions; the live proposal list lives in `proposal-solicitations.md`,
the live papers list in `papers.md`.

Proposals and papers use the **same six-stage shape** (idea → drafting →
under-review → funded-or-accepted → done), but papers get their own bucket
labels since "Awarded" and "Proposal Idea Scoped" do not fit a manuscript.
Do not collapse the two trackers into one list: a proposal and a paper on the
same project are different objects with different clocks, even when they cite
each other.

## The six buckets, in order

**Proposals:**

1. **Untouched** — on the radar, no work started.
2. **Proposal Idea Scoped** — concept defined, not yet drafting.
3. **Drafting Currently** — actively being written.
4. **Submitted and Pending** — submitted, awaiting outcome.
5. **Awarded** — funded; work underway.
6. **Complete or otherwise no further work**.

**Papers:**

1. **Untouched** — an idea noted, not yet scoped.
2. **Idea Scoped** — narrative/venue identified, not yet drafting.
3. **Drafting Currently** — actively being written.
4. **Submitted / Under Review** — sent to a journal, awaiting referee action.
5. **Accepted** — accepted or in revision post-acceptance; not yet formally
   published (no volume/page/DOI resolved).
6. **Published / Complete** — final citation resolved, or shelved.

**Show every category, even if empty.** Mark an empty bucket `(none)`.

## How to build the report

1. Read `projects.md` to get the project list.
2. Read `proposal-solicitations.md` for the live proposal-call list.
3. Read `proposal-ideas.md` for idea-first entries (their `Status:` field
   maps to bucket 2 when they're at "Scoping solicitation" or "Promoted").
4. Read `papers.md` for the live papers list. A project can appear in neither
   tracker, one, or both.
5. For each project file, look at the `**Status:**` line near the top to
   classify into a bucket, using the proposal bucket set or the paper bucket
   set depending on which tracker the file belongs to.
6. Group and present, proposals and papers as separate blocks.

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

Default scope is **everything**: proposals (drafting / submitted / awarded),
papers (drafting / submitted / accepted / published), *and* other ongoing
projects (service, tools). If the user asks specifically for proposals only or
papers only, scope to those.

For papers, include the **author position** (first author / co-author): it
changes what a bucket means. "Drafting Currently" on a first-author paper means
the user's own pen is moving; on a co-authored paper it usually means waiting
on the lead author.
