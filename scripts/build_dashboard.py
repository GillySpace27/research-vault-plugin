#!/usr/bin/env python3
"""
Build a self-contained dashboard.html for a research-task vault.

Three tracks, one page:

  * **Papers** and **Proposals** come from the two index files that already
    carry the six-bucket pipeline shape (`papers.md`,
    `proposals/proposal-solicitations.md`), so the dashboard inherits the
    vault's own classification instead of guessing from filenames.
  * **Projects** are every other task-bearing `.md`, keyed by vault-relative
    path so subfolders cluster.

Hours come from `timesheet.py` (session transcripts + the off-session event
ledger) when `time_tracking/config.json` exists; without it the effort columns
are simply omitted rather than faked.

Usage:
    python build_dashboard.py [vault_path]

Vault path resolution: explicit arg, else $RESEARCH_VAULT_DIR, else ~/research-vault/.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

SKIP_FILES = {"README.md", "CLAUDE.md", "dashboard.md", "journaling.md", "projects.md"}
SKIP_DIRS = {".git", ".obsidian", "_templates", "memory", "daily_notes", ".claude",
             "baseline", "nwra-intranet-mirror", "misc", "time_tracking"}
PAPERS_FILE = "papers.md"
PROPOSALS_FILE = "proposals/proposal-solicitations.md"

EMOJI_DUE, EMOJI_SCHED, EMOJI_DONE = "\U0001f4c5", "⏳", "✅"
EMOJI_HIGH, EMOJI_LOW = "\U0001f53c", "\U0001f53d"
EMOJI_URGENT = ("\U0001f525", "\U0001f6a8", "⏫", "\U0001f534")  # 🔥 🚨 ⏫ 🔴

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
PERSON_RE = re.compile(r"#([a-z0-9][a-z0-9-]*)")
TASK_RE = re.compile(r"^\s*-\s\[([ xX])\]\s+(.*)$")
BUCKET_RE = re.compile(r"^###\s+(.*?)\s*$")
ENTRY_RE = re.compile(r"^-\s\[([ xX])\]\s+(.*)$")   # top-level only: sub-bullets are indented
LINKED_FILE_RE = re.compile(r"`([a-z0-9\-/]+\.md)`|\[\[([a-z0-9\-]+)\]\]")

# Effort model. Rate = measured hours per closed task inside the window; the
# bounds stop one freak task (or one mis-mapped session) from dominating.
WINDOW_DAYS = 45
RATE_MIN, RATE_MAX = 0.5, 20.0
MIN_CLOSED_FOR_RATE = 3
PRIORITY_WEIGHT = {"high": 1.5, None: 1.0, "low": 0.5}


# ------------------------------------------------------------------ parsing


def parse_task(line: str) -> dict | None:
    m = TASK_RE.match(line)
    if not m:
        return None
    text = m.group(2)
    out = {"done": m.group(1).lower() == "x", "due": None,
           "sched": None, "completed": None, "priority": None, "people": []}
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


def walk_vault(vault: Path) -> dict[str, list[dict]]:
    by_file: dict[str, list[dict]] = {}
    for md in sorted(vault.rglob("*.md")):
        rel = md.relative_to(vault)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]) or md.name in SKIP_FILES:
            continue
        key = rel.as_posix()
        tasks = []
        for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            parsed = parse_task(line)
            if parsed is not None:
                parsed["file"], parsed["line"] = key, i
                tasks.append(parsed)
        if tasks:
            by_file[key] = tasks
    return by_file


def parse_index(vault: Path, rel: str, kind: str) -> list[dict]:
    """Parse a six-bucket index file (papers.md / proposal-solicitations.md).

    Entries are `- [ ] **Title** ...` lines under a `### Bucket` heading. The
    indented body is scanned for a `project.md` reference so an entry can
    borrow that project's measured hours.
    """
    path = vault / rel
    if not path.exists():
        return []
    out: list[dict] = []
    bucket, current = None, None
    for line in path.read_text(encoding="utf-8").splitlines():
        bm = BUCKET_RE.match(line)
        if bm:
            bucket = bm.group(1)
            continue
        em = ENTRY_RE.match(line)
        if em and bucket:
            current = {"kind": kind, "title": entry_title(em.group(2)), "bucket": bucket,
                       "done": em.group(1).lower() == "x", "files": []}
            out.append(current)
            continue
        if current is not None and line.startswith(("  ", "\t")):
            for a, b in LINKED_FILE_RE.findall(line):
                name = a or (b + ".md" if b else "")
                if name:
                    current["files"].append(name.split("/")[-1])
        elif line.strip() and not line.startswith(" "):
            current = None
    for e in out:
        e["files"] = list(dict.fromkeys(e["files"]))
    return out


def entry_title(text: str) -> str:
    """Title of an index entry: the bold run if there is one, else the lead clause."""
    bold = re.search(r"\*\*(.+?)\*\*", text)
    title = bold.group(1) if bold else re.split(r"(?<=[a-z0-9\)])[:.]\s", text, maxsplit=1)[0]
    title = re.sub(r"[\U0001f300-\U0001faff\u2190-\u2b55]", "", title)
    title = re.sub(r"`([^`]+)`", r"\1", title)
    return re.sub(r"\s+", " ", title).strip(" *:-")[:110]


def git_last_touched(vault: Path) -> dict[str, str]:
    try:
        raw = subprocess.run(
            ["git", "-C", str(vault), "log", "--name-only", "--format=%x00%ad",
             "--date=short", "-n", "600"],
            capture_output=True, text=True, timeout=25).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    out: dict[str, str] = {}
    date = None
    for line in raw.splitlines():
        if line.startswith("\x00"):
            date = line[1:].strip()
        elif line.strip() and date:
            out.setdefault(line.strip(), date)
    return out


def first_status(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines()[:40]:
            if re.match(r"^\*?\*?Status:?\*?\*?[:\s]", line, re.I):
                s = re.sub(r"^\*?\*?Status:?\*?\*?[:\s]+", "", line).strip()
                return re.sub(r"\*\*(.+?)\*\*", r"\1", s)[:160]
    except OSError:
        pass
    return ""


# -------------------------------------------------------------------- hours


def load_timesheet(vault: Path):
    """Import timesheet.py as a sibling module; returns (module, cfg) or (None, None)."""
    script = Path(__file__).with_name("timesheet.py")
    if not script.exists() or not (vault / "time_tracking" / "config.json").exists():
        return None, None
    os.environ.setdefault("RESEARCH_VAULT_DIR", str(vault))
    spec = importlib.util.spec_from_file_location("timesheet", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.VAULT = str(vault)
    return mod, mod.load_config()


def hours_by_label(mod, cfg, lo: dt.datetime, hi: dt.datetime) -> dict[str, dict]:
    """{project label: {'hours', 'charge', 'billable'}} over [lo, hi)."""
    intervals = mod.scan_transcripts(cfg, lo, hi) + mod.load_events(cfg, lo, hi)
    norm, _, _ = mod.allocate(intervals, lo, hi)
    out: dict[str, dict] = {}
    for key, mins in norm.items():
        label, charge, billable = mod.resolve(cfg, key)
        row = out.setdefault(label, {"hours": 0.0, "charge": charge, "billable": billable})
        row["hours"] += mins / 60.0
    return out


def weekly_series(mod, cfg, by_file, weeks: int, today: dt.date) -> list[dict]:
    start = today - dt.timedelta(days=today.weekday() + 7 * (weeks - 1))
    closed_by_day: dict[str, int] = defaultdict(int)
    for tasks in by_file.values():
        for t in tasks:
            if t["completed"]:
                closed_by_day[t["completed"]] += 1
    out = []
    for w in range(weeks):
        wk_start = start + dt.timedelta(days=7 * w)
        wk_end = wk_start + dt.timedelta(days=7)
        billable = free = 0.0
        if mod is not None:
            lo = dt.datetime.combine(wk_start, dt.time())
            hi = dt.datetime.combine(wk_end, dt.time())
            for label, row in hours_by_label(mod, cfg, lo, hi).items():
                if label == cfg.get("leave_label"):
                    continue
                if row["billable"]:
                    billable += row["hours"]
                else:
                    free += row["hours"]
        closed = sum(n for d, n in closed_by_day.items()
                     if wk_start.isoformat() <= d < wk_end.isoformat())
        out.append({"week": wk_start.isoformat(), "billable": round(billable, 2),
                    "free": round(free, 2), "closed": closed})
    return out


def assign_labels(cfg, labels: list[str], files: list[str]) -> dict[str, str]:
    """One timesheet label per vault file, and never the same label twice.

    An explicit `"file"` on a config entry wins. Everything else is matched by
    word overlap, greedily, best score first: without the one-to-one rule two
    files that share a word (solar-archive / heliograph-live) would each claim
    the same hours and the totals would double-count.
    """
    out: dict[str, str] = {}
    taken: set[str] = set()
    for entry in (cfg or {}).get("projects", {}).values():
        target, label = entry.get("file"), entry.get("project")
        if target and label in labels and target in files and target not in out:
            out[target] = label
            taken.add(label)
    pairs = []
    for rel in files:
        if rel in out:
            continue
        words = {w for w in re.split(r"[-_]", rel.split("/")[-1][:-3]) if len(w) > 2}
        for label in labels:
            lw = {w for w in re.split(r"[^a-z0-9]+", label.lower()) if len(w) > 2}
            score = len(words & lw)
            if score:
                pairs.append((score, len(words & lw) / max(len(lw), 1), rel, label))
    for _, _, rel, label in sorted(pairs, key=lambda t: (-t[0], -t[1], t[2])):
        if rel not in out and label not in taken:
            out[rel] = label
            taken.add(label)
    return out


# --------------------------------------------------------------- assembling


def build(vault: Path) -> dict:
    today = dt.date.today()
    by_file = walk_vault(vault)
    touched = git_last_touched(vault)
    mod, cfg = load_timesheet(vault)

    window_start = today - dt.timedelta(days=WINDOW_DAYS)
    hours = {}
    if mod is not None:
        hours = hours_by_label(mod, cfg,
                               dt.datetime.combine(window_start, dt.time()),
                               dt.datetime.combine(today + dt.timedelta(days=1), dt.time()))
    labels = list(hours)
    mapping = assign_labels(cfg, labels, list(by_file)) if labels else {}

    projects = []
    for rel, tasks in by_file.items():
        open_tasks = [t for t in tasks if not t["done"]]
        closed_window = [t for t in tasks if t["done"] and t["completed"]
                         and t["completed"] >= window_start.isoformat()]
        due = sorted(t["due"] for t in open_tasks if t["due"])
        label = mapping.get(rel)
        row = hours.get(label, {}) if label else {}
        projects.append({
            "file": rel,
            "name": rel.split("/")[-1][:-3],
            "folder": rel.split("/")[0] if "/" in rel else "root",
            "status": first_status(vault / rel),
            "open": len(open_tasks),
            "done": len(tasks) - len(open_tasks),
            "high": sum(1 for t in open_tasks if t["priority"] == "high"),
            "urgent": sum(1 for t in open_tasks if t["urgent"]),
            "overdue": sum(1 for t in open_tasks if t["due"] and t["due"] < today.isoformat()),
            "next_due": due[0] if due else None,
            "closed_window": len(closed_window),
            "label": label,
            "charge": row.get("charge", ""),
            "billable": row.get("billable", True),
            "hours": round(row.get("hours", 0.0), 2),
            "last_touched": touched.get(rel),
        })

    # Effort model: measured hours per closed task, with a vault-wide fallback.
    rates = [p["hours"] / p["closed_window"] for p in projects
             if p["closed_window"] >= MIN_CLOSED_FOR_RATE and p["hours"] > 0]
    fallback = min(max(statistics.median(rates), RATE_MIN), RATE_MAX) if rates else 0.0
    for p in projects:
        measured = p["closed_window"] >= MIN_CLOSED_FOR_RATE and p["hours"] > 0
        rate = (p["hours"] / p["closed_window"]) if measured else fallback
        rate = min(max(rate, RATE_MIN), RATE_MAX) if rate else 0.0
        weighted = sum(PRIORITY_WEIGHT.get(t["priority"], 1.0)
                       for t in by_file[p["file"]] if not t["done"])
        p["rate"] = round(rate, 2)
        p["measured"] = measured
        p["remaining"] = round(weighted * rate, 1)

    tracks = {"papers": parse_index(vault, PAPERS_FILE, "paper"),
              "proposals": parse_index(vault, PROPOSALS_FILE, "proposal")}
    by_name = {p["file"].split("/")[-1]: p for p in projects}
    claims: dict[str, int] = defaultdict(int)
    for entries in tracks.values():
        for e in entries:
            for f in e["files"]:
                if f in by_name:
                    claims[f] += 1
    for entries in tracks.values():
        for e in entries:
            mapped = [by_name[f] for f in e["files"] if f in by_name]
            e["open"] = sum(m["open"] for m in mapped)
            e["hours"] = round(sum(m["hours"] for m in mapped), 1)
            e["remaining"] = round(sum(m["remaining"] for m in mapped), 1)
            e["measured"] = any(m["measured"] for m in mapped)
            e["mapped"] = [m["file"] for m in mapped]
            # A paper mapped to a broad project file inherits that whole file.
            e["shared"] = any(claims[f] > 1 for f in e["files"] if f in by_name)

    # One project label with two different charge codes resolves arbitrarily,
    # here and in timesheet.py. Say so rather than showing a coin flip.
    seen: dict[str, set] = defaultdict(set)
    for entry in (cfg or {}).get("projects", {}).values():
        seen[entry.get("project", "")].add((entry.get("charge", ""), entry.get("billable", True)))
    warnings = [f"label '{lbl}' has {len(v)} different charge/billable settings in "
                f"time_tracking/config.json; whichever entry is found first wins"
                for lbl, v in sorted(seen.items()) if lbl and len(v) > 1]

    mapped_labels = set(mapping.values())
    unmapped = {lbl: row for lbl, row in hours.items() if lbl not in mapped_labels}

    return {
        "generated": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "today": today.isoformat(),
        "window_days": WINDOW_DAYS,
        "has_hours": bool(hours),
        "fallback_rate": round(fallback, 2),
        "projects": projects,
        "tracks": tracks,
        "tasks": by_file,
        "weekly": weekly_series(mod, cfg, by_file, 8, today),
        "target_hours_per_week": (cfg or {}).get("target_hours_per_week", 0),
        "warnings": warnings,
        "unmapped": sorted(({"label": k, "hours": round(v["hours"], 1)}
                            for k, v in unmapped.items() if v["hours"] >= 0.25),
                           key=lambda r: -r["hours"]),
    }


# ----------------------------------------------------------------- template

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Vault Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1" integrity="sha384-jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ" crossorigin="anonymous"></script>
<style>
:root{--bg:#faf9f7;--panel:#fff;--ink:#1a1a1a;--muted:#6b6b6b;--rule:#e7e5e1;
  --accent:#b25600;--high:#b25600;--overdue:#c0392b;--done:#5b8f3f;--free:#8a7fb5;
  --grid:rgba(0,0,0,.07);}
@media (prefers-color-scheme:dark){:root{--bg:#171717;--panel:#212121;--ink:#ededed;
  --muted:#9a9a9a;--rule:#333;--accent:#ff9c4a;--high:#ff9c4a;--overdue:#ff6b5e;
  --done:#8fc070;--free:#a99ede;--grid:rgba(255,255,255,.08);}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-size:14px;line-height:1.5;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
header{padding:1.2rem 2rem .8rem;border-bottom:1px solid var(--rule);display:flex;
  justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:.5rem}
header h1{margin:0;font-size:1.05rem;font-weight:600}
header .meta{color:var(--muted);font-size:.8rem}
nav{display:flex;gap:.4rem;padding:.8rem 2rem;flex-wrap:wrap;border-bottom:1px solid var(--rule)}
nav button{background:var(--panel);border:1px solid var(--rule);color:var(--ink);
  padding:.3rem .8rem;border-radius:999px;font-size:.83rem;cursor:pointer;font-family:inherit}
nav button.active{background:var(--accent);color:#fff;border-color:var(--accent)}
main{padding:1.2rem 2rem 3rem;max-width:1500px;margin:0 auto}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:.8rem;margin-bottom:1.1rem}
.kpi{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:.85rem 1rem}
.kpi .l{font-size:.7rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.kpi .v{font-size:1.7rem;font-weight:700;line-height:1.25}
.kpi .s{font-size:.75rem;color:var(--muted)}
.kpi.warn .v{color:var(--overdue)}
.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(370px,1fr));gap:.8rem;margin-bottom:1.1rem}
.card{background:var(--panel);border:1px solid var(--rule);border-radius:8px;padding:.9rem 1.1rem;
  margin-bottom:.8rem;overflow-x:auto}
.card h3{margin:0 0 .1rem;font-size:.85rem;font-weight:600}
.card .sub{color:var(--muted);font-size:.72rem;margin-bottom:.6rem}
.card canvas{max-height:260px}
table{width:100%;border-collapse:collapse;font-size:.83rem}
th{text-align:left;padding:.45rem .5rem;border-bottom:2px solid var(--rule);color:var(--muted);
  font-size:.7rem;text-transform:uppercase;letter-spacing:.04em;cursor:pointer;white-space:nowrap;user-select:none}
td{padding:.45rem .5rem;border-bottom:1px solid var(--rule);vertical-align:top}
tr.row{cursor:pointer}
tr.row:hover td{background:var(--bg)}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.pill{display:inline-block;padding:.05rem .45rem;border-radius:4px;border:1px solid var(--rule);
  font-size:.7rem;color:var(--muted);white-space:nowrap}
.pill.high{color:var(--high);border-color:var(--high)}
.pill.overdue{color:var(--overdue);border-color:var(--overdue);font-weight:600}
.pill.est{color:var(--muted);font-style:italic}
.bucket{font-weight:600;font-size:.78rem;margin:1.1rem 0 .3rem;color:var(--accent)}
ul{list-style:none;padding:0;margin:0}
li.task{padding:.32rem 0;border-bottom:1px solid var(--rule);display:grid;
  grid-template-columns:1rem 1fr auto;gap:.55rem;align-items:baseline}
li.task.done .text{text-decoration:line-through;color:var(--muted)}
.badges{display:flex;gap:.3rem;flex-wrap:wrap;justify-content:flex-end}
.detail .close{float:right;cursor:pointer;color:var(--muted);border:none;background:none;font-size:1.1rem}
.detail h2{margin:0 0 .1rem;font-size:1rem}
.muted{color:var(--muted)}
.small{font-size:.72rem}
.note{color:var(--muted);font-size:.75rem;margin:.6rem 0 0}
footer{padding:1rem 2rem 2rem;color:var(--muted);font-size:.72rem;border-top:1px solid var(--rule);
  max-width:1500px;margin:0 auto}
code{font-family:ui-monospace,SFMono-Regular,monospace}
@media (max-width:700px){main,header,nav,footer{padding-left:1rem;padding-right:1rem}}
</style>
</head>
<body>
<header>
  <h1>Vault Dashboard</h1>
  <div class="meta" id="meta"></div>
</header>
<nav id="tabs">
  <button class="active" data-tab="overview">Overview</button>
  <button data-tab="papers">Papers</button>
  <button data-tab="proposals">Proposals</button>
  <button data-tab="projects">Projects</button>
  <button data-tab="tasks">Tasks</button>
</nav>
<main id="app"></main>
<footer>
Read-only. Edits go through Obsidian, your editor, or <code>/capture</code> /
<code>/journal</code> / <code>/update</code>. Regenerate with <code>/dashboard</code>.
Hours come from <code>scripts/timesheet.py</code> (session transcripts + the off-session
ledger) and are presence time, not a certified timecard.
</footer>
<script>
const DATA = __DATA__;
const F = n => (Math.round(n*10)/10).toLocaleString();
const esc = s => (s||'').replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const P = DATA.projects, TR = DATA.tracks;
const billable = P.filter(p=>p.billable);
const sum = (a,f) => a.reduce((s,x)=>s+f(x),0);
let charts = [];
function clearCharts(){ charts.forEach(c=>c.destroy()); charts=[]; }

document.getElementById('meta').textContent =
  sum(P,p=>p.open)+' open tasks · '+P.length+' project files · generated '+DATA.generated;

function kpi(label, value, sub, warn){
  return '<div class="kpi'+(warn?' warn':'')+'"><div class="l">'+label+'</div>'+
    '<div class="v">'+value+'</div><div class="s">'+(sub||'')+'</div></div>';
}

function modelNote(){
  return '<strong>How "estimated work" is computed:</strong> for each project, hours logged '+
    'in the last '+DATA.window_days+' days ÷ tasks closed in the same window gives an '+
    'hours-per-task rate; remaining = open tasks × that rate, weighting high-priority tasks '+
    '1.5× and low 0.5×. Projects with fewer than 3 closed tasks in the window inherit the '+
    'vault-wide median of '+DATA.fallback_rate+' h/task and are marked '+
    '<span class="pill est">est</span>. The model assumes remaining tasks resemble finished '+
    'ones, which is exactly where it will be wrong: "submit the thing" is not "rewrite §3".';
}

function overview(){
  const open = sum(P,p=>p.open), overdue = sum(P,p=>p.overdue);
  const remainBillable = sum(billable,p=>p.remaining);
  const paperRemain = sum(TR.papers.filter(e=>!e.done), e=>e.remaining);
  const inFlight = TR.papers.filter(e=>!e.done).length;
  const pending = TR.proposals.filter(e=>!e.done).length;
  const weeksAt = DATA.target_hours_per_week ? remainBillable/DATA.target_hours_per_week : 0;

  let h = '<section class="kpis">'+
    kpi('Open tasks', open, sum(P,p=>p.high)+' high · '+sum(P,p=>p.urgent)+' urgent')+
    kpi('Overdue', overdue, overdue?'past their due date':'nothing past due', overdue>0)+
    kpi('Est. work remaining', F(remainBillable)+' h', 'billable projects only')+
    kpi('Papers to publication', F(paperRemain)+' h', inFlight+' in flight')+
    kpi('Logged, last '+DATA.window_days+' d', F(sum(P,p=>p.hours))+' h',
        F(sum(billable,p=>p.hours))+' h billable'+
        (DATA.unmapped.length? ' · +'+F(sum(DATA.unmapped,u=>u.hours))+' h off-file':''))+
    kpi('Proposals live', pending, 'not yet closed out')+'</section>';

  if (weeksAt) h += '<p class="note">At the configured '+DATA.target_hours_per_week+
    ' h/week that backlog is <strong>'+F(weeksAt)+' weeks</strong> of billable capacity.</p>';

  h += '<section class="charts">'+
    '<div class="card"><h3>Estimated hours remaining</h3><div class="sub">open tasks × '+
      'measured hours-per-task, priority weighted</div><canvas id="c-remain"></canvas></div>'+
    '<div class="card"><h3>Where the hours went</h3><div class="sub">last '+DATA.window_days+
      ' days, billable vs free work</div><canvas id="c-hours"></canvas></div>'+
    '<div class="card"><h3>Weekly rhythm</h3><div class="sub">hours logged (bars) against '+
      'tasks closed (line)</div><canvas id="c-weekly"></canvas></div>'+
    '<div class="card"><h3>Pipeline</h3><div class="sub">papers and proposals by stage</div>'+
      '<canvas id="c-pipe"></canvas></div></section>';

  if (DATA.unmapped.length) h += '<p class="note"><strong>Off-file hours:</strong> '+
    DATA.unmapped.map(u=>esc(u.label)+' '+F(u.hours)+' h').join(' · ')+
    '. Time logged against a charge label with no project file behind it, so it '+
    'carries no tasks and no estimate.</p>';

  h += '<div class="card"><h3>Everything, by remaining effort</h3>'+
    '<div class="sub">click a row for its tasks</div><div id="tbl">'+
    table([...P].sort((a,b)=>b.remaining-a.remaining))+'</div></div>'+
    '<p class="note">'+modelNote()+'</p>';
  document.getElementById('app').innerHTML = h;
  drawOverview();
  wireTable();
}

function table(rows){
  let h = '<table><thead><tr><th data-sort="name">Project</th><th data-sort="charge">Charge</th>'+
    '<th class="num" data-sort="open">Open</th><th class="num" data-sort="overdue">Overdue</th>'+
    '<th class="num" data-sort="hours">Hours</th><th class="num" data-sort="remaining">Est. left</th>'+
    '<th data-sort="next_due">Next due</th><th data-sort="last_touched">Touched</th></tr></thead><tbody>';
  rows.forEach(p=>{
    h += '<tr class="row" data-file="'+esc(p.file)+'"><td><strong>'+esc(p.name)+'</strong>'+
      (p.billable?'':' <span class="pill">free</span>')+
      '<div class="muted small">'+esc(p.status).slice(0,90)+'</div></td>'+
      '<td><span class="pill">'+esc(p.charge||'—')+'</span></td>'+
      '<td class="num">'+p.open+(p.high?' <span class="pill high">'+p.high+'↑</span>':'')+'</td>'+
      '<td class="num">'+(p.overdue?'<span class="pill overdue">'+p.overdue+'</span>':'—')+'</td>'+
      '<td class="num">'+(p.hours?F(p.hours):'—')+'</td>'+
      '<td class="num">'+(p.remaining?F(p.remaining):'—')+
        (p.measured?'':' <span class="pill est">est</span>')+'</td>'+
      '<td>'+(p.next_due||'—')+'</td><td class="muted">'+(p.last_touched||'—')+'</td></tr>';
  });
  return h+'</tbody></table>';
}

let sortKey='remaining', sortDir=-1;
function wireTable(){
  document.querySelectorAll('th[data-sort]').forEach(th=>{
    th.onclick = () => {
      const k = th.dataset.sort;
      sortDir = (k===sortKey) ? -sortDir : -1;
      sortKey = k;
      const host = th.closest('.card').querySelector('#tbl') || th.closest('.card');
      const rows = [...P].sort((a,b)=>{
        const x=a[k], y=b[k];
        if (x===y) return 0;
        if (x===null||x===undefined) return 1;
        if (y===null||y===undefined) return -1;
        return (x<y?-1:1)*sortDir;
      });
      host.innerHTML = table(rows);
      wireTable();
    };
  });
  document.querySelectorAll('tr.row').forEach(tr=>{ tr.onclick = () => detail(tr.dataset.file); });
}

function detail(file){
  const p = P.find(x=>x.file===file); if(!p) return;
  clearCharts();
  const tasks = DATA.tasks[file]||[];
  const open = tasks.filter(t=>!t.done), done = tasks.filter(t=>t.done);
  document.getElementById('app').innerHTML =
    '<div class="card detail"><button class="close" onclick="render()">✕</button>'+
    '<h2>'+esc(p.name)+'</h2><div class="muted small">'+esc(p.file)+' · '+esc(p.status)+'</div>'+
    '<div class="kpis" style="margin-top:.8rem">'+
      kpi('Open', p.open, p.high+' high')+
      kpi('Hours logged', F(p.hours)+' h', 'last '+DATA.window_days+' d')+
      kpi('Rate', p.rate?F(p.rate)+' h/task':'—', p.measured?'measured here':'vault median')+
      kpi('Est. remaining', F(p.remaining)+' h', p.charge||'no charge code')+'</div>'+
    taskList(open,'Open')+taskList(done.slice(-25),'Recently closed')+'</div>';
  window.scrollTo(0,0);
}

function taskList(tasks, title){
  if(!tasks.length) return '';
  let h = '<div class="bucket">'+title+' ('+tasks.length+')</div><ul>';
  tasks.forEach(t=>{
    const b=[];
    if(t.priority==='high') b.push('<span class="pill high">high</span>');
    if(t.urgent) b.push('<span class="pill overdue">urgent</span>');
    if(t.due) b.push('<span class="pill'+(t.due<DATA.today?' overdue':'')+'">📅 '+t.due+'</span>');
    if(t.completed) b.push('<span class="pill">✅ '+t.completed+'</span>');
    (t.people||[]).forEach(p=>b.push('<span class="pill">#'+esc(p)+'</span>'));
    if(t.file && title!=='Open' && title!=='Recently closed')
      b.push('<span class="pill">'+esc(t.file.split('/').pop().replace('.md',''))+'</span>');
    h += '<li class="task'+(t.done?' done':'')+'"><input type="checkbox" disabled '+
      (t.done?'checked':'')+'><span class="text">'+esc(t.display)+'</span>'+
      '<span class="badges">'+b.join('')+'</span></li>';
  });
  return h+'</ul>';
}

function trackView(kind){
  const entries = TR[kind];
  const buckets = [];
  entries.forEach(e=>{ if(buckets.indexOf(e.bucket)<0) buckets.push(e.bucket); });
  const live = entries.filter(e=>!e.done);
  let h = '<section class="kpis">'+
    kpi(kind==='papers'?'Papers tracked':'Proposals tracked', entries.length, live.length+' still open')+
    kpi('Est. work left', F(sum(live,e=>e.remaining))+' h', 'across mapped project files')+
    kpi('Open tasks', sum(live,e=>e.open), 'in the mapped files')+
    kpi('Hours logged', F(sum(entries,e=>e.hours))+' h', 'last '+DATA.window_days+' d')+
    '</section><p class="note">Open, logged and left are the <strong>totals of the mapped '+
    'project file</strong>, not of this one '+kind.slice(0,-1)+'. A file carrying several '+
    'efforts is marked <span class="pill">shared</span> and its numbers are an upper bound.</p>'+
    '<div class="card">';
  buckets.forEach(b=>{
    const rows = entries.filter(e=>e.bucket===b);
    h += '<div class="bucket">'+esc(b)+' ('+rows.length+')</div><table><tbody>';
    rows.forEach(e=>{
      h += '<tr><td style="width:55%">'+(e.done?'✅ ':'')+'<strong>'+esc(e.title)+'</strong>'+
        '<div class="muted small">'+(e.mapped.map(esc).join(', ')||'no project file mapped')+
          (e.shared?' <span class="pill">shared</span>':'')+'</div></td>'+
        '<td class="num">'+(e.open||'—')+'<div class="muted small">open</div></td>'+
        '<td class="num">'+(e.hours?F(e.hours)+' h':'—')+'<div class="muted small">logged</div></td>'+
        '<td class="num">'+(e.remaining?F(e.remaining)+' h':'—')+
          (e.measured?'':' <span class="pill est">est</span>')+
          '<div class="muted small">left</div></td></tr>';
    });
    h += '</tbody></table>';
  });
  document.getElementById('app').innerHTML = h+'</div><p class="note">'+modelNote()+'</p>';
}

function projectsView(){
  const groups = {};
  P.forEach(p=>{ (groups[p.folder] = groups[p.folder]||[]).push(p); });
  let h = '';
  Object.keys(groups).sort().forEach(g=>{
    const rows = groups[g].slice().sort((a,b)=>b.remaining-a.remaining);
    h += '<div class="card"><h3>'+esc(g)+'/</h3><div class="sub">'+rows.length+' files · '+
      sum(rows,p=>p.open)+' open · '+F(sum(rows,p=>p.remaining))+' h estimated remaining</div>'+
      '<div id="tbl">'+table(rows)+'</div></div>';
  });
  document.getElementById('app').innerHTML = h;
  wireTable();
}

function tasksView(){
  const all = [];
  Object.keys(DATA.tasks).forEach(f => DATA.tasks[f].forEach(t => all.push(t)));
  const open = all.filter(t=>!t.done);
  const overdue = open.filter(t=>t.due && t.due < DATA.today).sort((a,b)=>a.due<b.due?-1:1);
  const soon = open.filter(t=>t.due && t.due >= DATA.today).sort((a,b)=>a.due<b.due?-1:1);
  const hot = open.filter(t=>!t.due && (t.priority==='high'||t.urgent));
  document.getElementById('app').innerHTML = '<div class="card">'+
    taskList(overdue,'Overdue')+taskList(soon,'Scheduled ahead')+
    taskList(hot.slice(0,80),'High priority, undated')+'</div>';
}

function drawOverview(){
  const grid = css('--grid');
  Chart.defaults.color = css('--muted');
  Chart.defaults.font.family = '-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif';

  const top = P.filter(p=>p.remaining>0).sort((a,b)=>b.remaining-a.remaining).slice(0,10);
  charts.push(new Chart('c-remain', {type:'bar',
    data:{labels:top.map(p=>p.name), datasets:[{data:top.map(p=>p.remaining),
      backgroundColor:top.map(p=>p.billable?css('--accent'):css('--free')), borderRadius:3}]},
    options:{indexAxis:'y', responsive:true, maintainAspectRatio:false, animation:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>F(c.parsed.x)+' h remaining'}}},
      scales:{x:{beginAtZero:true,grid:{color:grid},title:{display:true,text:'hours'}},
              y:{grid:{display:false}}}}}));

  const byH = P.filter(p=>p.hours>0).sort((a,b)=>b.hours-a.hours).slice(0,10);
  charts.push(new Chart('c-hours', {type:'bar',
    data:{labels:byH.map(p=>p.name), datasets:[
      {label:'billable', data:byH.map(p=>p.billable?p.hours:0), backgroundColor:css('--accent'), borderRadius:3},
      {label:'free work', data:byH.map(p=>p.billable?0:p.hours), backgroundColor:css('--free'), borderRadius:3}]},
    options:{indexAxis:'y', responsive:true, maintainAspectRatio:false, animation:false,
      plugins:{legend:{position:'bottom',labels:{boxWidth:10,usePointStyle:true}}},
      scales:{x:{stacked:true,beginAtZero:true,grid:{color:grid},title:{display:true,text:'hours'}},
              y:{stacked:true,grid:{display:false}}}}}));

  const wk = DATA.weekly;
  charts.push(new Chart('c-weekly', {data:{labels:wk.map(w=>w.week.slice(5)), datasets:[
      {type:'bar', label:'billable h', data:wk.map(w=>w.billable), backgroundColor:css('--accent'),
       borderRadius:3, yAxisID:'y'},
      {type:'bar', label:'free h', data:wk.map(w=>w.free), backgroundColor:css('--free'),
       borderRadius:3, yAxisID:'y'},
      {type:'line', label:'tasks closed', data:wk.map(w=>w.closed), borderColor:css('--done'),
       backgroundColor:css('--done'), tension:.3, yAxisID:'y1'}]},
    options:{responsive:true, maintainAspectRatio:false, animation:false,
      plugins:{legend:{position:'bottom',labels:{boxWidth:10,usePointStyle:true}}},
      scales:{x:{stacked:true,grid:{display:false}},
        y:{stacked:true,beginAtZero:true,grid:{color:grid},title:{display:true,text:'hours'}},
        y1:{position:'right',beginAtZero:true,grid:{display:false},ticks:{precision:0},
            title:{display:true,text:'tasks'}}}}}));

  const buckets = {};
  ['papers','proposals'].forEach(k=>TR[k].filter(e=>!e.done).forEach(e=>{
    buckets[e.bucket] = buckets[e.bucket] || {papers:0,proposals:0};
    buckets[e.bucket][k]++; }));
  const bl = Object.keys(buckets);
  charts.push(new Chart('c-pipe', {type:'bar', data:{labels:bl, datasets:[
      {label:'papers', data:bl.map(b=>buckets[b].papers), backgroundColor:css('--accent'), borderRadius:3},
      {label:'proposals', data:bl.map(b=>buckets[b].proposals), backgroundColor:css('--free'), borderRadius:3}]},
    options:{responsive:true, maintainAspectRatio:false, animation:false,
      plugins:{legend:{position:'bottom',labels:{boxWidth:10,usePointStyle:true}}},
      scales:{x:{stacked:true,grid:{display:false}},
              y:{stacked:true,beginAtZero:true,grid:{color:grid},ticks:{precision:0}}}}}));
}

let tab='overview';
function render(){
  clearCharts();
  if(tab==='overview') overview();
  else if(tab==='papers') trackView('papers');
  else if(tab==='proposals') trackView('proposals');
  else if(tab==='projects') projectsView();
  else tasksView();
}
document.querySelectorAll('#tabs button').forEach(b=>{
  b.onclick = () => {
    document.querySelectorAll('#tabs button').forEach(x=>x.classList.remove('active'));
    b.classList.add('active'); tab = b.dataset.tab; render();
  };
});
render();
</script>
</body>
</html>
"""


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    vault = Path(arg or os.environ.get("RESEARCH_VAULT_DIR") or "~/research-vault").expanduser()
    if not vault.is_dir():
        print(f"error: vault not found: {vault}", file=sys.stderr)
        return 1
    data = build(vault)
    for warn in data["warnings"]:
        print(f"  warning: {warn}", file=sys.stderr)
    out = vault / "dashboard.html"
    out.write_text(TEMPLATE.replace("__DATA__", json.dumps(data)), encoding="utf-8")
    projects = data["projects"]
    print(f"wrote {out}")
    print(f"  {len(projects)} project files · {sum(p['open'] for p in projects)} open · "
          f"{sum(p['done'] for p in projects)} done")
    print(f"  {len(data['tracks']['papers'])} papers · {len(data['tracks']['proposals'])} proposals")
    if data["has_hours"]:
        print(f"  {sum(p['hours'] for p in projects):.1f} h logged in the last {data['window_days']} d"
              f" · {sum(p['remaining'] for p in projects if p['billable']):.0f} h estimated remaining"
              f" (billable)")
    else:
        print("  no time_tracking/config.json: effort columns omitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
