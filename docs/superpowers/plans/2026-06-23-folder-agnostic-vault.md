# Folder-Agnostic Vault Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a vault organize project files into arbitrary subfolders while every engine read/write path keeps working, then migrate Gilly's vault into `projects/ proposals/ admin/ misc/`.

**Architecture:** Make `build_dashboard.py` scan the vault recursively with a directory + filename skip-list and key results by relative path (folder-agnostic). Reword the skills/commands that assume project files live at the root. Migrate Gilly's vault as a separate commit. Engine changes are made upstream in `research-vault-plugin` and synced to the `gilly-vault` fork; the vault migration touches only `research-tasks`.

**Tech Stack:** Python 3.7+ (stdlib only — `pathlib`, `unittest`), Bash (rsync sync script), Markdown (skills/commands/vault files), git + gh.

## Global Constraints

- Python: stdlib only, 3.7+ floor; no new dependencies in `build_dashboard.py`.
- The dashboard stays **read-only**; no write-back.
- Folder names are **never hardcoded** in the engine — scanning is driven by a skip-list, not an allow-list of folders. A flat vault (no subfolders) must keep working unchanged.
- Engine edits land in `research-vault-plugin` first, then sync to `gilly-vault` via `scripts/sync-engine.sh`. Identity files (README, GETTING-STARTED, plugin.json, marketplace.json) are never synced.
- Dates absolute `YYYY-MM-DD`. Commit trailer: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- All engine work on branch `feat/folder-agnostic-vault` (already created, holds the spec commit).

---

## File Structure

| File | Responsibility | Change |
|---|---|---|
| `scripts/build_dashboard.py` | Scan vault, parse tasks, render dashboard.html | Modify: recursive scan, skip-dirs, path-keyed grouping |
| `tests/test_build_dashboard.py` | Unit tests for the scanner | Create |
| `skills/vault-projects/SKILL.md` | Project-file model | Modify: files may live in subfolders; new → `projects/` |
| `skills/vault-tasks/SKILL.md` | Task syntax + capture | Modify: "one file per project" wording |
| `skills/vault-memory/SKILL.md` | Memory tiers | Modify: drop the "at the vault root" path assumption |
| `commands/start.md` | Vault init/scaffold | Modify: create project files under `projects/` |
| `commands/capture.md` | Quick task capture | Modify: locate files by scan; new file → `projects/` |
| `commands/status.md`, `triage.md`, `update.md`, `dashboard.md` | Read/reconcile project files | Modify: locate by scan, not root |
| `scripts/sync-engine.sh` | Engine → fork sync | Modify: exclude `docs/superpowers/` |

Vault migration (separate repo, `~/Documents/NWRA/research-tasks`): `git mv` files into folders; update `projects.md` links; audit `dashboard.md` queries.

---

## Phase A — Engine scanner (TDD)

### Task A1: Failing test for recursive, skip-listed, path-keyed scan

**Files:**
- Create: `tests/test_build_dashboard.py`

**Interfaces:**
- Consumes: `build_dashboard.walk_vault(vault: Path) -> dict[str, list[dict]]` (existing).
- Produces: the contract that `walk_vault` keys results by **vault-relative POSIX path** and recurses, skipping system files + non-project dirs.

- [ ] **Step 1: Write the failing test**

```python
import sys, unittest, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build_dashboard as bd

def _vault(root: Path):
    (root / "projects").mkdir()
    (root / "proposals").mkdir()
    (root / "memory" / "people").mkdir(parents=True)
    (root / "daily_notes").mkdir()
    (root / "_templates").mkdir()
    (root / "projects" / "alpha.md").write_text("# Alpha\n- [ ] do alpha thing\n", encoding="utf-8")
    (root / "proposals" / "calls.md").write_text("# Calls\n- [ ] watch NSF call\n", encoding="utf-8")
    (root / "inbox.md").write_text("# Inbox\n- [ ] loose task\n", encoding="utf-8")
    (root / "CLAUDE.md").write_text("# mem\n- [ ] should be skipped\n", encoding="utf-8")
    (root / "memory" / "people" / "p.md").write_text("# P\n- [ ] not a task file\n", encoding="utf-8")
    (root / "daily_notes" / "2026-01-01.md").write_text("# day\n- [ ] journal item\n", encoding="utf-8")
    (root / "_templates" / "project.md").write_text("# tmpl\n- [ ] placeholder\n", encoding="utf-8")

class TestWalkVault(unittest.TestCase):
    def test_recurses_and_skips(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _vault(root)
            keys = set(bd.walk_vault(root).keys())
            self.assertEqual(keys, {"projects/alpha.md", "proposals/calls.md", "inbox.md"})

    def test_keys_are_sorted_folder_first(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _vault(root)
            keys = list(bd.walk_vault(root).keys())
            self.assertEqual(keys, sorted(keys))

    def test_flat_vault_still_works(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "rhef.md").write_text("# RHEF\n- [ ] flat task\n", encoding="utf-8")
            (root / "README.md").write_text("# r\n- [ ] skip me\n", encoding="utf-8")
            self.assertEqual(set(bd.walk_vault(root).keys()), {"rhef.md"})

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_build_dashboard -v` (from repo root)
Expected: FAIL — `test_recurses_and_skips` gets `{"inbox.md"}` (root-only glob misses the subfolders), keys aren't path-prefixed.

- [ ] **Step 3: Commit the test**

```bash
git add tests/test_build_dashboard.py
git commit -m "test: recursive, skip-listed, path-keyed vault scan (failing)"
```

### Task A2: Implement recursive scan

**Files:**
- Modify: `scripts/build_dashboard.py` (SKIP set + `walk_vault`)

**Interfaces:**
- Produces: `walk_vault` returns a dict keyed by vault-relative POSIX path, sorted, recursing all dirs except the skip set, skipping `SKIP_FILES` by basename. `parsed["file"]` becomes the relative path.

- [ ] **Step 1: Add the directory skip-set** (after `SKIP_FILES`)

```python
SKIP_FILES = {
    "README.md", "CLAUDE.md", "dashboard.md", "journaling.md", "projects.md",
}
SKIP_DIRS = {".git", ".obsidian", "_templates", "memory", "daily_notes"}
```

- [ ] **Step 2: Replace `walk_vault`**

```python
def walk_vault(vault: Path) -> dict[str, list[dict]]:
    by_file: dict[str, list[dict]] = {}
    paths = []
    for md in vault.rglob("*.md"):
        rel = md.relative_to(vault)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        if md.name in SKIP_FILES:
            continue
        paths.append((rel.as_posix(), md))
    for key, md in sorted(paths):
        tasks: list[dict] = []
        for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            parsed = parse_task(line)
            if parsed is None:
                continue
            parsed["file"] = key
            parsed["line"] = i
            tasks.append(parsed)
        if tasks:
            by_file[key] = tasks
    return by_file
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_build_dashboard -v`
Expected: PASS (all three tests).

- [ ] **Step 4: Smoke-test against a real nested vault**

```bash
mkdir -p /tmp/fa/projects /tmp/fa/proposals
printf '# A\n- [ ] x 📅 2026-07-01 #kd\n' > /tmp/fa/projects/a.md
printf '# Calls\n- [ ] watch call\n' > /tmp/fa/proposals/c.md
printf '# Inbox\n- [ ] loose\n' > /tmp/fa/inbox.md
python3 scripts/build_dashboard.py /tmp/fa
python3 - <<'PY'
import re,json
h=open('/tmp/fa/dashboard.html').read()
d=json.loads(re.search(r'const DATA = (\{.*?\});',h,re.S).group(1).replace('\\u003c','<').replace('\\u003e','>'))
print("keys:", sorted(d))
PY
rm -rf /tmp/fa
```
Expected: `keys: ['inbox.md', 'projects/a.md', 'proposals/c.md']`

- [ ] **Step 5: Commit**

```bash
git add scripts/build_dashboard.py
git commit -m "feat(dashboard): recursive folder-agnostic vault scan, path-keyed"
```

### Task A3: Dashboard groups by folder; inbox filter intact

The JS already renders one `<section>` per `DATA` key with `<h2>${escapeHtml(file)}</h2>`; with path keys the sections now show `projects/alpha.md` and sort folder-first (sorted in `walk_vault`). Verify the inbox filter still matches and nothing regressed.

**Files:**
- Modify (only if needed): `scripts/build_dashboard.py` HTML/JS template.

- [ ] **Step 1: Confirm the inbox filter still keys on `inbox.md`**

Run: `grep -n 'file === "inbox.md"' scripts/build_dashboard.py`
Expected: one match. `inbox.md` stays at the root, so its key is exactly `inbox.md` — the filter still works. No change needed.

- [ ] **Step 2: Visually verify grouping in a browser** (preview server)

Generate against `/tmp/fa` (as in A2) and load `dashboard.html`; confirm sections appear folder-clustered (`projects/…` then `proposals/…`) and the Inbox filter shows only `inbox.md` tasks. If sections are not folder-clustered, they already are via the sorted keys — no code change. (Optional enhancement, NOT in scope: explicit folder sub-headers.)

- [ ] **Step 3: Commit only if the template changed** (otherwise skip)

```bash
git add scripts/build_dashboard.py && git commit -m "feat(dashboard): folder-clustered sections"
```

---

## Phase B — Folder-agnostic prose

Each task: reword the cited lines so they no longer assert project files live at the vault root, and state that new project files default to `projects/`. Verify with the grep in the final step (no remaining root-only assertions about *project* files; `daily_notes/` and `memory/` references are correct and stay).

### Task B1: Skills

**Files:**
- Modify: `skills/vault-projects/SKILL.md` (lines ~3, ~8, ~14), `skills/vault-tasks/SKILL.md` (lines ~3, ~41), `skills/vault-memory/SKILL.md` (line ~78)

- [ ] **Step 1: vault-projects** — change "Each substantive line of work gets its own file **under the vault root**" → "…its own `.md` file, in `projects/` (or another subfolder); the tools find project files anywhere in the vault, so the exact folder is your choice." Update the `description` line and the "One file per project" bullet to match. Leave `projects.md` (the manifest) at the root.
- [ ] **Step 2: vault-tasks** — reword the `description` ("One file per project, with `inbox.md` as the catch-all") and the body bullet "**One file per project.** `<project>.md`…" to "**One file per project**, in `projects/` (or any subfolder); `inbox.md` (at the root) is the catch-all."
- [ ] **Step 3: vault-memory** — line 78 "`<name>.md` at the vault root" → "the matching project `.md` (in `projects/` or wherever it lives)."
- [ ] **Step 4: Verify**

Run: `grep -rinE "under the vault root|file per project at|\.md.* at the vault root" skills/`
Expected: no matches about *project* files (a `daily_notes/ in the vault root` line in vault-journal is correct — leave it).

- [ ] **Step 5: Commit**

```bash
git add skills/ && git commit -m "docs(skills): project files may live in subfolders (folder-agnostic)"
```

### Task B2: Commands

**Files:**
- Modify: `commands/start.md`, `commands/capture.md`, `commands/status.md`, `commands/triage.md`, `commands/update.md`, `commands/dashboard.md`

- [ ] **Step 1: start.md** — in the first-run scaffold (the "One `<project>.md` per named project" step), write project files into `projects/` (create the folder); keep system/index files (`CLAUDE.md`, `README.md`, `projects.md`, `inbox.md`, `dashboard.md`, `journaling.md`) and the proposal trackers at the root for a fresh vault. In the "later runs — verify core files" table, note project files live under `projects/`.
- [ ] **Step 2: capture.md** — "drops into the most likely project file" → add: project files may be in subfolders; locate the target by scanning; if a brand-new project file is needed, create it under `projects/`. `inbox.md` (root) remains the fallback.
- [ ] **Step 3: status.md, triage.md, update.md** — where each says it reads/walks "project files," add that they may live in subfolders and are located by scanning (not assumed at the root). `proposal-solicitations.md` / `proposal-ideas.md` read by `/status` may live at the root or in `proposals/`.
- [ ] **Step 4: dashboard.md** — note the builder now scans recursively and groups by folder; no usage change.
- [ ] **Step 5: Verify + commit**

Run: `grep -rinE "vault root" commands/` → confirm only legitimate root references remain (e.g. copying system files, the default vault path).
```bash
git add commands/ && git commit -m "docs(commands): locate project files by scan; new files default to projects/"
```

---

## Phase C — Keep dev specs out of the fork

### Task C1: Exclude `docs/superpowers/` from sync

**Files:**
- Modify: `scripts/sync-engine.sh` (the `EXCLUDES` array)

- [ ] **Step 1: Add the exclude**

In the `EXCLUDES=(...)` array, add: `--exclude='docs/superpowers/'`

- [ ] **Step 2: Verify dry-run skips it**

Run: `bash scripts/sync-engine.sh ~/vscode/gilly-vault-plugin` (dry run)
Expected: the itemized list shows engine files but **not** `docs/superpowers/...`.

- [ ] **Step 3: Commit**

```bash
git add scripts/sync-engine.sh
git commit -m "chore(sync): keep docs/superpowers/ (dev specs) out of personal forks"
```

---

## Phase D — Land the engine + sync to the fork

### Task D1: PR research-vault, then sync gilly-vault

- [ ] **Step 1: Run the full test suite once more**

Run: `python3 -m unittest tests.test_build_dashboard -v`
Expected: PASS.

- [ ] **Step 2: Push + PR + squash-merge** (research-vault-plugin)

```bash
git push -u origin feat/folder-agnostic-vault
gh pr create --repo GillySpace27/research-vault-plugin --base main --head feat/folder-agnostic-vault \
  --title "feat: folder-agnostic vault (recursive scan + subfolder support)" --body "<summary + spec link>"
gh pr merge feat/folder-agnostic-vault --repo GillySpace27/research-vault-plugin --squash --delete-branch
```

- [ ] **Step 3: Sync local main + push engine to gilly-vault**

```bash
git checkout main && git pull --ff-only origin main
bash scripts/sync-engine.sh ~/vscode/gilly-vault-plugin            # dry run, confirm scope
bash scripts/sync-engine.sh ~/vscode/gilly-vault-plugin --apply
```
Then in `~/vscode/gilly-vault-plugin`: branch, commit, push, PR, squash-merge, sync local main (same flow as prior doc syncs). Confirm `build_dashboard.py` is byte-identical across both repos.

---

## Phase E — Migrate Gilly's vault

Repo: `~/Documents/NWRA/research-tasks` (work on a branch; the live `main` may carry unrelated uncommitted work — stage only migration files).

### Task E1: Move files into folders

- [ ] **Step 1: Create folders + move** (run from the vault root)

```bash
mkdir -p projects proposals admin misc
git mv punch-pulse.md punch-science.md punch-video-tools.md rhef.md sunback.md \
  solar-archive.md gilly-space.md ghosts.md flux-fluxon.md radiant-surya.md \
  aia-desaturation.md dkist-waves.md hfr-coronal-heating.md lws-flare-ribbons.md \
  ec-lac.md space-weather-solicitation.md projects/
git mv proposal-solicitations.md proposal-ideas.md proposals/
git mv nwra-admin.md travel.md admin/
git mv personal.md showcase.md misc/
```

- [ ] **Step 2: Verify root is now just system/index files**

Run: `ls *.md`
Expected: `CLAUDE.md README.md projects.md journaling.md dashboard.md inbox.md` only.

### Task E2: Update the manifest + audit Obsidian queries

- [ ] **Step 1: Update `projects.md` links** to the new paths (e.g. `` (`punch-pulse.md`) `` → `` (`projects/punch-pulse.md`) ``; trackers → `proposals/…`; admin → `admin/…`). Edit each manifest bullet to match where its file now lives.
- [ ] **Step 2: Audit `dashboard.md`** for Obsidian Tasks queries scoped by `path`. If any restrict to the root or a specific folder, broaden them (or remove the path filter) so subfolders are included. If there are none, no change.
- [ ] **Step 3: Regenerate + verify the dashboard**

```bash
RESEARCH_VAULT_DIR="$PWD" python3 ~/vscode/gilly-vault-plugin/scripts/build_dashboard.py "$PWD"
```
Expected: open/done counts non-zero; sections appear folder-clustered (`projects/…`, `proposals/…`, `admin/…`, `misc/…`); Inbox filter shows `inbox.md` only.

- [ ] **Step 4: Commit + push** (stage only migration files; leave any unrelated uncommitted work alone)

```bash
git add projects/ proposals/ admin/ misc/ projects.md dashboard.md
git commit -m "vault: nest project files into projects/ proposals/ admin/ misc/"
git push origin <branch>   # then merge to main per the worktree flow
```

---

## Phase F — Final verification

- [ ] **Step 1: `/status`** — run it; confirm the six buckets populate from `proposals/proposal-solicitations.md` and each project's `**Status:**` line under `projects/`. No "(no Status line)" regressions for files that have one.
- [ ] **Step 2: `/capture`** — capture a test task; confirm it lands in the correct file under `projects/` (not at the root), then delete it.
- [ ] **Step 3: Flat-vault back-compat** — `python3 -m unittest tests.test_build_dashboard -v` (the `test_flat_vault_still_works` case) passes, proving a colleague's flat vault is unaffected.
- [ ] **Step 4: Confirm engines in sync** — `diff` `build_dashboard.py` and `scripts/sync-engine.sh` across both plugin repos; identical.

---

## Self-Review

- **Spec coverage:** folder-agnostic engine (A1–A3), prose (B1–B2), sync-exclude for specs (C1), two-repo sync (D1), vault taxonomy migration (E1–E2), dashboard-by-folder (A3), tests incl. flat back-compat (A1/F3) — all mapped.
- **Placeholder scan:** PR `--body` in D1 left as `<summary + spec link>` (fill at execution — it is human prose, not code) and the manifest/dashboard edits in E2 are per-line ("edit each bullet to match") rather than verbatim, because the exact set depends on the live file contents at migration time; the *rule* is explicit. No code-step placeholders.
- **Type consistency:** `walk_vault` signature unchanged; `parsed["file"]` now a relative path used by the JS `file` key and the `inbox.md` filter — consistent across A2/A3.
