#!/usr/bin/env bash
#
# sync-engine.sh — push the shared engine from this (upstream) plugin into a
# downstream personal fork, leaving the fork's per-install identity intact.
#
# research-vault-plugin is the single source of truth for the ENGINE:
# commands/, skills/, scripts/, _templates/, _examples/, .mcp.json, .gitignore.
#
# Each fork keeps its own IDENTITY (never synced):
#   .claude-plugin/plugin.json    — plugin name / description
#   .claude-plugin/marketplace.json
#   README.md                     — fork-specific docs
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
#   scripts/sync-engine.sh ~/vscode/gilly-vault-plugin --apply
#
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DST="${1:-}"
MODE="${2:-dry}"

if [[ -z "$DST" || ! -d "$DST" ]]; then
  echo "usage: $0 <path-to-fork-plugin-dir> [--apply]" >&2
  exit 1
fi
if [[ ! -f "$DST/.claude-plugin/plugin.json" ]]; then
  echo "error: $DST does not look like a plugin (no .claude-plugin/plugin.json)" >&2
  exit 1
fi

EXCLUDES=(
  --exclude='.git/'
  --exclude='.claude-plugin/plugin.json'
  --exclude='.claude-plugin/marketplace.json'
  --exclude='README.md'
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
