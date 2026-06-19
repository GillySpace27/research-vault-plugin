#!/usr/bin/env python3
"""
Build a self-contained dashboard.html for a research-task vault.

Walks every `*.md` file at the vault root (skipping README/CLAUDE/dashboard/
journaling/projects scaffolding), parses GitHub-style checkbox tasks with
Obsidian Tasks-plugin emoji metadata, and renders a single HTML page with
filters: due/overdue, this week, high priority, inbox, by-project.

Usage:
    python build_dashboard.py [vault_path]

Defaults to ~/research-vault/.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

SKIP_FILES = {
    "README.md", "CLAUDE.md", "dashboard.md", "journaling.md", "projects.md",
}
EMOJI_DUE = "\U0001f4c5"        # 📅
EMOJI_SCHED = "⏳"           # ⏳
EMOJI_DONE = "✅"            # ✅
EMOJI_HIGH = "\U0001f53c"        # 🔼
EMOJI_LOW = "\U0001f53d"         # 🔽

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
PERSON_RE = re.compile(r"#([a-z0-9][a-z0-9-]*)")
TASK_RE = re.compile(r"^\s*-\s\[([ xX])\]\s+(.*)$")


def parse_task(line: str) -> dict | None:
    m = TASK_RE.match(line)
    if not m:
        return None
    done = m.group(1).lower() == "x"
    text = m.group(2)
    out = {"done": done, "raw": text, "due": None, "sched": None,
           "completed": None, "priority": None, "people": []}
    for token, key in ((EMOJI_DUE, "due"), (EMOJI_SCHED, "sched"),
                        (EMOJI_DONE, "completed")):
        idx = text.find(token)
        if idx != -1:
            after = text[idx + len(token):].lstrip()
            dm = DATE_RE.match(after)
            if dm:
                out[key] = dm.group(1)
    if EMOJI_HIGH in text:
        out["priority"] = "high"
    elif EMOJI_LOW in text:
        out["priority"] = "low"
    out["people"] = PERSON_RE.findall(text)
    # Strip metadata for display text
    display = text
    for emo in (EMOJI_DUE, EMOJI_SCHED, EMOJI_DONE):
        display = re.sub(re.escape(emo) + r"\s*\d{4}-\d{2}-\d{2}", "", display)
    display = display.replace(EMOJI_HIGH, "").replace(EMOJI_LOW, "")
    out["display"] = display.strip()
    return out


def walk_vault(vault: Path) -> dict[str, list[dict]]:
    by_file: dict[str, list[dict]] = {}
    for md in sorted(vault.glob("*.md")):
        if md.name in SKIP_FILES:
            continue
        tasks: list[dict] = []
        for i, line in enumerate(md.read_text().splitlines(), 1):
            parsed = parse_task(line)
            if parsed is None:
                continue
            parsed["file"] = md.name
            parsed["line"] = i
            tasks.append(parsed)
        if tasks:
            by_file[md.name] = tasks
    return by_file


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Vault Dashboard</title>
<style>
  :root {{
    --bg: #fafaf8; --panel: #fff; --ink: #1a1a1a; --muted: #6b6b6b;
    --rule: #e7e5e1; --accent: #b25600; --high: #b25600; --low: #999;
    --overdue: #c0392b; --done: #6b9a4f; --today: #b25600;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg: #1a1a1a; --panel: #242424; --ink: #f0f0f0; --muted: #999;
      --rule: #333; --accent: #ff9c4a; --high: #ff9c4a;
      --overdue: #ff6b5e; --done: #8fc070; --today: #ff9c4a;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px; line-height: 1.5; }}
  header {{ padding: 1.5rem 2rem; border-bottom: 1px solid var(--rule);
    display: flex; justify-content: space-between; align-items: baseline; }}
  header h1 {{ margin: 0; font-size: 1.1rem; font-weight: 600; }}
  header .meta {{ color: var(--muted); font-size: 0.85rem; }}
  nav {{ display: flex; gap: 0.5rem; padding: 1rem 2rem; flex-wrap: wrap;
    border-bottom: 1px solid var(--rule); }}
  nav button {{ background: var(--panel); border: 1px solid var(--rule);
    color: var(--ink); padding: 0.35rem 0.75rem; border-radius: 999px;
    font-size: 0.85rem; cursor: pointer; font-family: inherit; }}
  nav button.active {{ background: var(--accent); color: white;
    border-color: var(--accent); }}
  main {{ padding: 1.5rem 2rem; max-width: 100ch; }}
  section.file {{ margin-bottom: 2rem; }}
  section.file h2 {{ font-size: 0.95rem; font-weight: 600; margin: 0 0 0.5rem;
    color: var(--muted); font-family: ui-monospace, SFMono-Regular, monospace; }}
  ul {{ list-style: none; padding: 0; margin: 0; }}
  li.task {{ padding: 0.4rem 0; border-bottom: 1px solid var(--rule);
    display: grid; grid-template-columns: 1.2rem 1fr auto; gap: 0.6rem;
    align-items: baseline; }}
  li.task input {{ accent-color: var(--accent); }}
  li.task.done .text {{ text-decoration: line-through; color: var(--muted); }}
  .badges {{ display: flex; gap: 0.4rem; font-size: 0.75rem; color: var(--muted);
    align-items: baseline; }}
  .badge {{ padding: 0.1rem 0.5rem; border-radius: 4px;
    background: var(--bg); border: 1px solid var(--rule); white-space: nowrap; }}
  .badge.high {{ color: var(--high); border-color: var(--high); }}
  .badge.low {{ color: var(--low); }}
  .badge.overdue {{ color: var(--overdue); border-color: var(--overdue);
    font-weight: 600; }}
  .badge.today {{ color: var(--today); border-color: var(--today);
    font-weight: 600; }}
  .badge.person {{ background: var(--panel); }}
  .empty {{ color: var(--muted); font-style: italic; padding: 1rem 0; }}
  footer {{ padding: 1rem 2rem; color: var(--muted); font-size: 0.75rem;
    border-top: 1px solid var(--rule); }}
  code {{ font-family: ui-monospace, SFMono-Regular, monospace; }}
</style>
</head>
<body>
<header>
  <h1>Vault Dashboard</h1>
  <div class="meta">
    {open_count} open · {done_count} done · generated {generated}
  </div>
</header>
<nav id="filters">
  <button class="active" data-filter="open">Open ({open_count})</button>
  <button data-filter="overdue">Overdue</button>
  <button data-filter="today">Today</button>
  <button data-filter="week">This week</button>
  <button data-filter="high">High pri</button>
  <button data-filter="inbox">Inbox only</button>
  <button data-filter="all">All</button>
</nav>
<main id="board"></main>
<footer>
  Read-only view. Edits go through Obsidian, your editor, or
  <code>/capture</code> / <code>/journal</code> / <code>/update</code>.
  Regenerate with <code>python scripts/build_dashboard.py</code>.
</footer>
<script>
const DATA = {data_json};
const TODAY = "{today}";

function todayCmp(d) {{
  if (!d) return null;
  if (d < TODAY) return "overdue";
  if (d === TODAY) return "today";
  const dt = new Date(d);
  const wk = new Date(TODAY);
  wk.setDate(wk.getDate() + 7);
  if (dt <= wk) return "week";
  return null;
}}

function render(filter) {{
  const board = document.getElementById("board");
  board.innerHTML = "";
  let total = 0;
  for (const [file, tasks] of Object.entries(DATA)) {{
    const shown = tasks.filter(t => {{
      if (filter === "all") return true;
      if (filter === "open") return !t.done;
      if (filter === "overdue") return !t.done && todayCmp(t.due) === "overdue";
      if (filter === "today") return !t.done && todayCmp(t.due) === "today";
      if (filter === "week") return !t.done && todayCmp(t.due) &&
        ["overdue", "today", "week"].includes(todayCmp(t.due));
      if (filter === "high") return !t.done && t.priority === "high";
      if (filter === "inbox") return !t.done && file === "inbox.md";
      return !t.done;
    }});
    if (!shown.length) continue;
    total += shown.length;
    const sec = document.createElement("section");
    sec.className = "file";
    sec.innerHTML = `<h2>${{file}}</h2>`;
    const ul = document.createElement("ul");
    for (const t of shown) {{
      const li = document.createElement("li");
      li.className = "task" + (t.done ? " done" : "");
      const dueClass = todayCmp(t.due);
      const badges = [];
      if (t.priority === "high") badges.push(`<span class="badge high">🔼</span>`);
      if (t.priority === "low") badges.push(`<span class="badge low">🔽</span>`);
      if (t.due) {{
        const cls = dueClass === "overdue" ? "badge overdue" :
                    dueClass === "today" ? "badge today" : "badge";
        badges.push(`<span class="${{cls}}">📅 ${{t.due}}</span>`);
      }}
      if (t.sched) badges.push(`<span class="badge">⏳ ${{t.sched}}</span>`);
      for (const p of t.people) badges.push(`<span class="badge person">#${{p}}</span>`);
      li.innerHTML = `
        <input type="checkbox" ${{t.done ? "checked" : ""}} disabled>
        <span class="text">${{escapeHtml(t.display)}}</span>
        <span class="badges">${{badges.join(" ")}}</span>`;
      ul.appendChild(li);
    }}
    sec.appendChild(ul);
    board.appendChild(sec);
  }}
  if (!total) {{
    board.innerHTML = '<div class="empty">No tasks match this filter.</div>';
  }}
}}

function escapeHtml(s) {{
  return s.replace(/[&<>"']/g, c => ({{
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }}[c]));
}}

document.querySelectorAll("#filters button").forEach(b => {{
  b.addEventListener("click", () => {{
    document.querySelectorAll("#filters button").forEach(x =>
      x.classList.remove("active"));
    b.classList.add("active");
    render(b.dataset.filter);
  }});
}});

render("open");
</script>
</body>
</html>
"""


def main(argv: list[str]) -> int:
    vault = Path(argv[1]) if len(argv) > 1 else Path.home() / "research-vault"
    if not vault.is_dir():
        print(f"vault not found: {vault}", file=sys.stderr)
        return 1
    by_file = walk_vault(vault)
    open_count = sum(1 for ts in by_file.values() for t in ts if not t["done"])
    done_count = sum(1 for ts in by_file.values() for t in ts if t["done"])
    out = HTML_TEMPLATE.format(
        data_json=json.dumps(by_file),
        today=dt.date.today().isoformat(),
        generated=dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        open_count=open_count,
        done_count=done_count,
    )
    target = vault / "dashboard.html"
    target.write_text(out)
    print(f"wrote {target} ({open_count} open, {done_count} done across {len(by_file)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
