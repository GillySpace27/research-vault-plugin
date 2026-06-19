# Maintaining & contributing

## The two-repo model

This repo (`research-vault-plugin`) is the **single source of truth for the
engine** — commands, skills, scripts, templates, examples, `.mcp.json`,
`.gitignore`. A personal fork can share the exact same engine and overlay only
its own identity.

```
research-vault-plugin   ← UPSTREAM, public, the engine
        │ scripts/sync-engine.sh <fork> --apply
        ▼
<your-fork>-plugin      ← same engine, byte-identical, + identity overlay
```

**Identity files are never synced** (each fork keeps its own):

- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `README.md`
- `GETTING-STARTED.md`
- `.git/`

The per-install **vault path** is the `RESEARCH_VAULT_DIR` environment
variable, not a code diff — so the engine files stay identical across forks.

## Propagating an engine change

1. Edit the engine here (a command, skill, script, or template).
2. Bump the version in `.claude-plugin/plugin.json` and add a `CHANGELOG.md`
   entry.
3. Dry-run the sync to a fork:
   ```bash
   scripts/sync-engine.sh ~/path/to/your-fork-plugin
   ```
4. Apply it, then review:
   ```bash
   scripts/sync-engine.sh ~/path/to/your-fork-plugin --apply
   cd ~/path/to/your-fork-plugin && git diff
   ```
5. Commit both repos.

## Before committing

- Run `claude plugin validate .` — it must pass.
- If you changed `build_dashboard.py`, run it against a throwaway vault dir.
- Keep personal data out of the engine: roster, project codenames, and the
  vault path belong in the *vault* (its `CLAUDE.md` hot cache + `memory/`),
  never in the plugin.

## Prerequisites for development

- Python 3.7+ (only for `scripts/build_dashboard.py` / `/dashboard`).
- `rsync` (for `scripts/sync-engine.sh`; ships with macOS and most Linux).
