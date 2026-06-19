#!/usr/bin/env bash
#
# sync-engine.sh — push the shared engine from this (upstream) plugin into a
# downstream personal fork, leaving the fork's per-install identity intact.
#
# research-vault-plugin is the single source of truth for the ENGINE:
# commands/, skills/, scripts/, _templates/, _examples/, .mcp.json, .gitignore.
#
# Each fork keeps its own IDENTITY (never synced):
#   .claude-plugin/plugin.json    — plugin name / description / author
#   .claude-plugin/marketplace.json
#   README.md                     — fork-specific docs
#   GETTING-STARTED.md            — fork-specific onboarding (install URLs differ)
#   .git/                         — its own history
#
# Per-install vault path is an env var (RESEARCH_VAULT_DIR), not a code diff,
# so the engine files are byte-identical across forks.
#
# Usage:
#   scripts/sync-engine.sh <path-to-fork>            # dry-run (shows changes)
#   scripts/sync-engine.sh <path-to-fork> --apply    # actually sync
#
# Example:
#   scripts/sync-engine.sh ~/path/to/your-fork-plugin --apply
#
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DST="${1:-}"
MODE="${2:-}"

if [[ -z "$DST" || ! -d "$DST" ]]; then
  echo "usage: $0 <path-to-fork-plugin-dir> [--apply]" >&2
  exit 1
fi
if [[ ! -f "$DST/.claude-plugin/plugin.json" ]]; then
  echo "error: $DST does not look like a plugin (no .claude-plugin/plugin.json)" >&2
  exit 1
fi
# Only an explicit --apply syncs; reject anything else so a typo can't silently
# no-op (e.g. "--aply" must error, not pretend to dry-run a real sync).
if [[ -n "$MODE" && "$MODE" != "--apply" && "$MODE" != "--dry-run" ]]; then
  echo "error: unknown option '$MODE' (use --apply, or omit for a dry run)" >&2
  exit 1
fi
if ! command -v rsync >/dev/null 2>&1; then
  echo "error: rsync not found on PATH" >&2
  exit 1
fi

EXCLUDES=(
  --exclude='.git/'
  --exclude='.claude-plugin/plugin.json'
  --exclude='.claude-plugin/marketplace.json'
  --exclude='README.md'
  --exclude='GETTING-STARTED.md'
  --exclude='.DS_Store'
  --exclude='__pycache__/'
)

RSYNC_FLAGS=(-a --delete --itemize-changes "${EXCLUDES[@]}")

if [[ "$MODE" == "--apply" ]]; then
  echo "Syncing engine: $SRC/  ->  $DST/  (identity files preserved)"
  rsync "${RSYNC_FLAGS[@]}" "$SRC/" "$DST/"
  echo "Done. Review with: cd '$DST' && git diff"
else
  echo "DRY RUN — engine changes that would land in $DST (no files written):"
  echo "  (run again with --apply to sync)"
  echo
  rsync --dry-run "${RSYNC_FLAGS[@]}" "$SRC/" "$DST/"
fi
