# Example vault CLAUDE.md (fictional — for shape only)

`/start` writes the real version of this file into your vault root. It is the
**hot cache** for the two-tier memory system (see the vault-memory skill): the
~30 most-used people, terms, and active projects, loaded into context every
session so Claude decodes your shorthand without a re-brief. Keep it under
~100 lines; deep storage lives in `memory/`.

---

# CLAUDE.md

This folder is a personal research-task vault driven by the **`research-vault`**
Claude Code plugin. The plugin encodes the operating manual, task syntax,
journaling rules, status grouping, and the "update the vault" convention as
slash commands and skills — they auto-activate, no need to re-read conventions
here.

**Vault path:** `~/research-vault/`

## Commands the plugin provides

- `/start` · `/update` · `/update --comprehensive` · `/status` · `/journal` ·
  `/triage` · `/capture` · `/dashboard` — see the plugin README.

## People (top ~30)

| Handle | Full name | Affiliation | Role / context |
|---|---|---|---|
| `#jordan-reyes` | Jordan Reyes | State University | PhD advisor; co-PI. |
| `#sam-okafor` | Sam Okafor | Partner Institute | Imaging-tool collaborator. |

## Active projects

See `projects.md` for the full manifest. Currently hot: Main Grant (drafting),
Imaging Tool (active).

## Preferences

- Brief over thorough. Capture in seconds, not minutes.
- Resolve all relative dates to absolute `YYYY-MM-DD` before writing.
- Surgical edits only — never reformat surrounding content.

## currentDate convention

Today's date is provided in the session context. Resolve all relative dates to
absolute `YYYY-MM-DD` before writing into the vault.
