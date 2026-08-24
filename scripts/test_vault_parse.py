#!/usr/bin/env python3
"""python3 scripts/test_vault_parse.py

The parser every other reader now depends on. What is pinned here is the
behaviour that used to differ between copies: which lines count as tasks, what
survives into the display text, and that section offsets point at real bytes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vault_parse import iter_tasks, parse_task, sections, title_of  # noqa: E402

NOTE = """# A Project

Status: **Active**

## Open

- [ ] **Email Andy** the confirmed number 🔼 📅 2026-08-14 #andy-frahm
- [ ] 🔥 Something urgent with `code` in it
  - [ ] An indented sub-task
- [x] Done thing ✅ 2026-08-06 🔽

## Notes

- not a task, just a bullet
"""


def main():
    tasks = dict(iter_tasks(NOTE))
    assert len(tasks) == 4, f"expected 4 checkboxes, got {len(tasks)}"

    t = tasks[7]
    assert t["due"] == "2026-08-14" and t["priority"] == "high"
    assert t["people"] == ["andy-frahm"]
    assert t["heading"] == "Open"
    # Display text drops the metadata and the markup, keeps the words.
    assert "📅" not in t["display"] and "**" not in t["display"]
    assert t["display"].startswith("Email Andy the confirmed number"), t["display"]

    assert tasks[8]["urgent"] is True
    assert "`" not in tasks[8]["display"]
    # Indented sub-tasks are real tasks: a nested checkbox is still work.
    assert 9 in tasks, "indented sub-task was dropped"

    d = tasks[10]
    assert d["done"] and d["completed"] == "2026-08-06" and d["priority"] == "low"

    assert parse_task("- not a checkbox") is None
    assert parse_task("plain text") is None

    secs = sections(NOTE)
    names = [h for h, _, _ in secs]
    assert names == ["A Project", "Open", "Notes"], names
    # The offset must point at the real bytes, or a snippet windowed from it
    # quotes the wrong part of the file.
    for heading, body, off in secs:
        if body:
            # The body starts at the offset give or take the blank line that
            # follows a heading; what matters is that it is really there.
            gap = NOTE.index(body, off) - off
            assert 0 <= gap <= 4, f"{heading}: body sits {gap} chars from its offset"

    assert title_of(NOTE) == "A Project"
    assert title_of("no heading here", "fallback") == "fallback"
    print("vault_parse: 4 groups ok")


if __name__ == "__main__":
    main()
