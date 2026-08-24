#!/usr/bin/env python3
"""What a vault note IS: tasks, sections, titles. One definition, several readers.

This file exists because there were three. The dashboard generator, the search
indexer and the entity mapper each carried their own `TASK_RE` and their own
idea of which directories to skip, and they had already drifted: a task the
dashboard counted was not necessarily a task the index could find, and neither
could say which of them was wrong.

The vault format is the plugin's business, so the definition lives here, in the
generic plugin, and everything else imports it. Nothing in this module knows
about any particular dashboard, index or site.

    from vault_parse import iter_tasks, sections, title_of, iter_notes
"""
from __future__ import annotations

import re
from pathlib import Path

# Obsidian Tasks-plugin metadata.
EMOJI_DUE, EMOJI_SCHED, EMOJI_DONE = "\U0001f4c5", "⏳", "✅"      # 📅 ⏳ ✅
EMOJI_HIGH, EMOJI_LOW = "\U0001f53c", "\U0001f53d"                 # 🔼 🔽
EMOJI_URGENT = ("\U0001f525", "\U0001f6a8", "⏫", "\U0001f534")     # 🔥 🚨 ⏫ 🔴

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
PERSON_RE = re.compile(r"#([a-z0-9][a-z0-9-]*)")
TASK_RE = re.compile(r"^\s*-\s\[([ xX])\]\s+(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")

# Scaffolding and machine-written folders. A reader that wants daily notes or
# memory (the search index does) passes its own set.
SKIP_FILES = {"README.md", "CLAUDE.md", "dashboard.md", "journaling.md", "projects.md"}
SKIP_DIRS = {".git", ".obsidian", ".claude", ".smart-env", "node_modules", ".trash",
             "_templates", "memory", "daily_notes", "baseline",
             "nwra-intranet-mirror", "misc", "time_tracking"}
# The minimum any reader should skip: version control and editor state are
# never content, whatever the caller is doing.
SKIP_DIRS_MINIMAL = {".git", ".obsidian", ".claude", ".smart-env", "node_modules", ".trash"}


def parse_task(line: str) -> dict | None:
    """One checkbox line -> its metadata, or None if the line is not a task."""
    m = TASK_RE.match(line)
    if not m:
        return None
    text = m.group(2)
    out = {"done": m.group(1).lower() == "x", "raw": text,
           "due": None, "sched": None, "completed": None,
           "priority": None, "people": []}
    for token, key in ((EMOJI_DUE, "due"), (EMOJI_SCHED, "sched"), (EMOJI_DONE, "completed")):
        idx = text.find(token)
        if idx != -1:
            dm = DATE_RE.match(text[idx + len(token):].lstrip())
            if dm:
                out[key] = dm.group(1)
    if EMOJI_HIGH in text:
        out["priority"] = "high"
    elif EMOJI_LOW in text:
        out["priority"] = "low"
    out["urgent"] = any(e in text for e in EMOJI_URGENT)
    out["people"] = PERSON_RE.findall(text)

    display = text
    for emo in (EMOJI_DUE, EMOJI_SCHED, EMOJI_DONE):
        display = re.sub(re.escape(emo) + r"\s*\d{4}-\d{2}-\d{2}", "", display)
    display = display.replace(EMOJI_HIGH, "").replace(EMOJI_LOW, "")
    display = re.sub(r"\*\*(.+?)\*\*", r"\1", display)
    display = re.sub(r"`([^`]+)`", r"\1", display)
    out["display"] = re.sub(r"\s+", " ", display).strip(" :-")
    return out


def iter_tasks(text: str):
    """(line number, task) for every checkbox in a note, with its heading.

    The heading comes along because a task's location is part of reading it:
    "Open" and "Done" mean different things about the same words."""
    heading = ""
    for n, line in enumerate(text.split("\n"), 1):
        h = HEADING_RE.match(line)
        if h:
            heading = h.group(2)
            continue
        t = parse_task(line)
        if t is not None:
            t["heading"] = heading
            yield n, t


def sections(text: str):
    """(heading, body, char offset) per heading section.

    The offset is what lets a reader go back to the source and quote the part
    that actually matched, instead of the head of the block."""
    out, heading, buf, pos, start = [], "", [], 0, 0
    for line in text.split("\n"):
        if HEADING_RE.match(line):
            if buf:
                out.append((heading, "\n".join(buf).strip(), start))
            heading = HEADING_RE.match(line).group(2)
            buf, start = [], pos + len(line) + 1
        else:
            buf.append(line)
        pos += len(line) + 1
    if buf:
        out.append((heading, "\n".join(buf).strip(), start))
    return out


def title_of(text: str, fallback: str = "") -> str:
    """The first `# ` heading, which is the note's own name for itself."""
    for line in text.split("\n", 40)[:40]:
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def iter_notes(vault: Path, skip_dirs=None, skip_files=None):
    """Every markdown note worth reading, as (relative posix path, Path)."""
    skip_dirs = SKIP_DIRS if skip_dirs is None else skip_dirs
    skip_files = SKIP_FILES if skip_files is None else skip_files
    for md in sorted(Path(vault).rglob("*.md")):
        rel = md.relative_to(vault)
        if any(part in skip_dirs for part in rel.parts[:-1]):
            continue
        if md.name in skip_files:
            continue
        yield rel.as_posix(), md
