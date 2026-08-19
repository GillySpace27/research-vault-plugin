# Changelog

All notable changes to the research-vault engine. The same engine is synced
into downstream forks via `scripts/sync-engine.sh`, so bump this on every
engine change to keep forks traceable. Format follows
[Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- **Instrument files open with a `§0 Start here` document registry**: portals
  (official site, mission site, archive, search, quick-look, software, event
  catalog, local cache) plus tier 1/2/3 documents with DOIs, so the sources
  never have to be re-found. Adds a `§10 Citing and acknowledging` section and
  `homepage`/`archive`/`instrument_doi`/`bibtex_key` frontmatter. The skill now
  requires DOIs to be verified by resolving them (content negotiation) rather
  than from recall, and preprint status checked via the arXiv API.
- **`vault-instruments` skill + `instruments/` directory.** A sourced reference
  record for scientific instruments, one file per instrument, with a generic
  `_templates/instrument.md` covering identity, observable, spatial coverage,
  spectral response, cadence, data levels, calibration, conventions, gotchas,
  and access. Every factual row carries a source key resolving to an exact
  locator (chapter, table, page, or FITS keyword) plus a clickable link to that
  item, a retrieval date, and an evidence type. The skill fires whenever an
  instrument is named anywhere in context, resolves it through an alias table
  (`instruments/README.md`), and surfaces disagreements between the claim and
  the record rather than silently preferring either. Includes a source
  precedence order, a no-source-no-row rule, and a distinction between design
  facts and frame facts.
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
