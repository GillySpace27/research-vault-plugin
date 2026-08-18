# Changelog

All notable changes to the research-vault engine. The same engine is synced
into downstream forks via `scripts/sync-engine.sh`, so bump this on every
engine change to keep forks traceable. Format follows
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- **Papers tracker** (`papers.md`), a hot-cache list of papers/manuscripts
  parallel to `proposal-solicitations.md`. Papers get their own six-bucket
  shape (Untouched → Idea Scoped → Drafting Currently → Submitted / Under
  Review → Accepted → Published), distinct from the proposal buckets: "Awarded"
  does not describe a manuscript, and a proposal and a paper on the same
  project run different clocks even when they cite each other.
- `_templates/papers.md` starter template.
- `vault-status` defines and reports both bucket sets, and asks for author
  position on papers because it changes what a bucket means: first author means
  the user's own pen is moving, co-author usually means waiting on the lead.
- `/status` gained a `papers` scope argument; `vault-projects` step 5 routes
  new paper files into `papers.md`; `/start` seeds `papers.md` on first run and
  checks for it on later runs.

## [0.1.0] — 2026-06-18

### Added
- Seven slash commands: `/start`, `/update`, `/status`, `/journal`, `/triage`,
  `/capture`, `/dashboard`.
- Seven auto-loading skills: `vault-tasks`, `vault-projects`, `vault-people`,
  `vault-journal`, `vault-update`, `vault-status`, `vault-memory`.
- First-run `/start` interview that creates the vault and seeds the user's own
  people, projects, and memory.
- `scripts/build_dashboard.py` (pure-stdlib HTML board) and
  `scripts/sync-engine.sh` (upstream → fork engine sync).
- Templates for every file `/start` scaffolds, plus fictional `_examples/`.
- `RESEARCH_VAULT_DIR` env var for vault-path resolution.
- LICENSE (MIT), CONTRIBUTING, GETTING-STARTED.
