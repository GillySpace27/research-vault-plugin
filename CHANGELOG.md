# Changelog

All notable changes to the research-vault engine. The same engine is synced
into downstream forks via `scripts/sync-engine.sh`, so bump this on every
engine change to keep forks traceable. Format follows
[Keep a Changelog](https://keepachangelog.com/).

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
