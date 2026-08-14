#!/usr/bin/env python3
"""
timesheet.py - derive per-project time from Claude Code session transcripts.

Every Claude Code session writes a JSONL transcript under
~/.claude/projects/<dir-key>/<session>.jsonl, and every line carries an ISO
timestamp. Clustering those timestamps gives an evidence-based record of when
work happened and (via the session's working directory) what it was on.

Communications that happen outside a session (email sent, Slack thread,
calendar meeting) are not in the transcripts, so they come from a hand/Claude
appended ledger: time_tracking/events.tsv.

What this measures: *presence* time at the keyboard, per project, split
evenly across projects worked concurrently. It is a defensible starting draft
for a timecard, not a certified timecard.

Usage:
    timesheet.py init                     # write a starter config from observed dirs
    timesheet.py day    [YYYY-MM-DD] [--write]
    timesheet.py week   [YYYY-MM-DD] [--write]
    timesheet.py period [YYYY-MM-DD] [--write]   # pay period (see config)
    timesheet.py period --by-day                 # project x day matrix
    timesheet.py --selftest

--write patches the vault (daily note '## Time' section, weekly/period files);
without it, the markdown goes to stdout.

Vault path: $RESEARCH_VAULT_DIR (falls back to ~/research-vault).
"""

import argparse
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, date, time, timedelta

VAULT = os.path.expanduser(os.environ.get("RESEARCH_VAULT_DIR") or "~/research-vault")
TRANSCRIPTS = os.path.expanduser("~/.claude/projects")
CONFIG_REL = "time_tracking/config.json"
EVENTS_REL = "time_tracking/events.tsv"

DEFAULT_CONFIG = {
    "idle_gap_minutes": 10,
    "min_segment_minutes": 2,
    "default_event_minutes": 6,
    "meeting_weight": 3.0,
    "meeting_sources": ["calendar", "phone"],
    "pay_period": "semi-monthly",
    "pay_period_anchor": "2026-01-05",
    "round_to_hours": 0.25,
    "target_hours_per_week": 0,
    "projects": {},
}

# ---------------------------------------------------------------- config / io


def cfg_path():
    return os.path.join(VAULT, CONFIG_REL)


def load_config():
    cfg = dict(DEFAULT_CONFIG)
    try:
        with open(cfg_path()) as fh:
            cfg.update(json.load(fh))
    except FileNotFoundError:
        pass
    return cfg


def dir_key(dirname):
    """Collapse worktree dirs onto their parent repo: worktrees are the same project."""
    return dirname.split("--claude-worktrees-")[0]


def resolve(cfg, key):
    """dir-key (or an events.tsv label) -> (project label, charge code, billable).

    A worktree name usually says what the work was ("...--claude-worktrees-dkist-
    backup-recovery-83d46a"), so an exact worktree entry in the config wins over
    the collapsed repo entry. That is the only way to split one repo's sessions
    across charge codes.
    """
    entry = cfg["projects"].get(key) or cfg["projects"].get(dir_key(key))
    if entry is None:  # events.tsv may name the project label instead of the dir
        for candidate in cfg["projects"].values():
            if candidate.get("project") == key:
                entry = candidate
                break
    if entry is None:
        if key.startswith("-"):  # an unregistered session directory
            collapsed = dir_key(key)
            return ("unmapped: " + collapsed.replace("-Users-", "", 1).replace("-", "/"), "", True)
        return (key, "", True)  # free-text label from events.tsv
    return (entry.get("project", key), entry.get("charge", ""), entry.get("billable", True))


# ------------------------------------------------------------------ scanning


def parse_ts(raw):
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone().replace(tzinfo=None)


def scan_transcripts(cfg, lo, hi):
    """Return [(start, end, dir_key, weight)] of active segments overlapping [lo, hi)."""
    gap = timedelta(minutes=cfg["idle_gap_minutes"])
    floor = timedelta(minutes=cfg["min_segment_minutes"])
    out = []
    for path in glob.glob(os.path.join(TRANSCRIPTS, "*", "*.jsonl")):
        key = os.path.basename(os.path.dirname(path))
        stamps = []
        try:
            with open(path, errors="replace") as fh:
                for line in fh:
                    # cheap prefilter: skip lines with no timestamp at all
                    if '"timestamp"' not in line:
                        continue
                    try:
                        rec = json.loads(line)
                        stamps.append(parse_ts(rec["timestamp"]))
                    except (ValueError, KeyError, TypeError):
                        continue
        except OSError:
            continue
        if not stamps:
            continue
        stamps.sort()
        seg_start = prev = stamps[0]
        for ts in stamps[1:] + [None]:
            if ts is None or ts - prev > gap:
                end = max(prev, seg_start + floor)
                if end > lo and seg_start < hi:
                    out.append((max(seg_start, lo), min(end, hi), key, 1.0))
                if ts is not None:
                    seg_start = ts
            prev = ts if ts is not None else prev
    return out


def load_events(cfg, lo, hi):
    """time_tracking/events.tsv: ISO8601 <TAB> project <TAB> minutes <TAB> source <TAB> note
    <TAB> weight.

    'project' is a dir-key or a project label; labels are passed through as-is.
    Blank/short lines and '#' comments are ignored.

    A row from a meeting source outweighs concurrent session activity: you were
    in the room, and whatever the keyboard was doing was secondary. The optional
    sixth column overrides the weight for one row.
    """
    path = os.path.join(VAULT, EVENTS_REL)
    out = []
    try:
        fh = open(path)
    except FileNotFoundError:
        return out
    with fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                print(f"warn: {EVENTS_REL}:{lineno} malformed, skipped", file=sys.stderr)
                continue
            try:
                start = parse_ts(parts[0])
            except ValueError:
                print(f"warn: {EVENTS_REL}:{lineno} bad timestamp, skipped", file=sys.stderr)
                continue
            mins = cfg["default_event_minutes"]
            if len(parts) > 2 and parts[2].strip():
                try:
                    mins = float(parts[2])
                except ValueError:
                    pass
            source = parts[3].strip().lower() if len(parts) > 3 else ""
            weight = cfg["meeting_weight"] if source in cfg["meeting_sources"] else 1.0
            if len(parts) > 5 and parts[5].strip():
                try:
                    weight = float(parts[5])
                except ValueError:
                    pass
            end = start + timedelta(minutes=mins)
            if end > lo and start < hi:
                out.append((max(start, lo), min(end, hi), parts[1].strip(), weight))
    return out


# ---------------------------------------------------------------- allocation


def allocate(intervals, lo, hi):
    """Minute-resolution sweep. Returns (normalized, raw, wall_minutes).

    A minute claimed by two projects at once is split between them in proportion
    to their weights, so the per-project column always sums to real wall-clock
    time. Sessions weigh 1 and meetings weigh `meeting_weight` (3 by default,
    i.e. 75/25 against one concurrent session). 'raw' keeps the unsplit
    per-project totals so the overlap is visible rather than silent.
    """
    span = int((hi - lo).total_seconds() // 60)
    active = defaultdict(dict)
    for start, end, key, weight in intervals:
        a = max(0, int((start - lo).total_seconds() // 60))
        b = min(span, int(-(-(end - lo).total_seconds() // 60)))
        for m in range(a, b):
            active[m][key] = max(active[m].get(key, 0.0), weight)
    norm, raw = defaultdict(float), defaultdict(float)
    for weights in active.values():
        total = sum(weights.values())
        for key, weight in weights.items():
            norm[key] += weight / total
            raw[key] += 1.0
    return norm, raw, len(active)


def target_hours(cfg, lo, hi):
    """Expected billable hours over [lo, hi): weekdays only, elapsed days only.

    A part-time appointment (soft money, a funding shortfall, a partial FTE) is
    the difference between "I am behind" and "that is the deal", so the target
    is stated rather than left for the reader to hold in their head.
    """
    per_week = cfg.get("target_hours_per_week")
    if not per_week:
        return 0.0
    today = date.today()
    days = [lo.date() + timedelta(days=n) for n in range((hi - lo).days)]
    workdays = [d for d in days if d.weekday() < 5 and d <= today]
    return len(workdays) * per_week / 5.0


def q(cfg, minutes):
    step = cfg["round_to_hours"]
    return round(minutes / 60.0 / step) * step


# ------------------------------------------------------------------ rendering


def render(cfg, lo, hi, title):
    intervals = scan_transcripts(cfg, lo, hi) + load_events(cfg, lo, hi)
    norm, raw, wall = allocate(intervals, lo, hi)
    if not norm:
        return f"_No tracked activity for {title}._\n"

    merged = defaultdict(lambda: [0.0, 0.0])  # several dirs can be one project
    for key, mins in norm.items():
        merged[resolve(cfg, key)][0] += mins
        merged[resolve(cfg, key)][1] += raw[key]
    rows = [(p, c, b, m, r) for (p, c, b), (m, r) in merged.items()]
    rows.sort(key=lambda r: -r[3])

    billable_total = sum(r[3] for r in rows if r[2])
    lines = [
        f"| Project | Charge | Hours | Raw |",
        f"|---|---|---|---|",
    ]
    dust = 0.0
    for project, charge, billable, mins, rawmins in rows:
        if q(cfg, mins) == 0:  # rounds away; keep the table readable
            dust += mins
            continue
        label = project if billable else f"{project} (non-billable)"
        lines.append(f"| {label} | {charge} | {q(cfg, mins):.2f} | {q(cfg, rawmins):.2f} |")
    if dust:
        lines.append(f"| _{sum(1 for r in rows if q(cfg, r[3]) == 0)} project(s) under "
                     f"the rounding floor_ | | 0.00 | {q(cfg, dust):.2f} |")
    lines.append(f"| **Billable total** | | **{q(cfg, billable_total):.2f}** | |")
    lines.append(f"| Wall clock at keyboard | | {q(cfg, wall):.2f} | |")
    target = target_hours(cfg, lo, hi)
    if target:
        lines.append(f"| Target ({cfg['target_hours_per_week']} h/wk) | | "
                     f"{target:.2f} | {billable_total / 60.0 / target:.0%} met |")

    overlap = sum(r[4] for r in rows) - sum(r[3] for r in rows)
    notes = [
        "",
        f"_{title}. Generated {datetime.now():%Y-%m-%d %H:%M} by `scripts/timesheet.py` "
        f"from Claude Code session transcripts (idle gap {cfg['idle_gap_minutes']} min) "
        f"and `{EVENTS_REL}`. Presence time, not a certified timecard: review before "
        f"it goes on one._",
    ]
    if overlap > 1:
        notes.append(
            f"_Concurrency: {q(cfg, overlap):.2f} h of the Raw column is double-counted "
            f"parallel work. The Hours column splits those minutes by weight "
            f"(meetings {cfg['meeting_weight']:g}x sessions)._"
        )
    unmapped = [r[0] for r in rows if r[0].startswith("unmapped: ")]
    if unmapped:
        notes.append(
            f"_{len(unmapped)} unmapped source dir(s): add them to `{CONFIG_REL}` "
            f"to get a project name and charge code._"
        )
    return "\n".join(lines + notes) + "\n"


def render_by_day(cfg, lo, hi, title):
    """Project x day matrix: the shape a timecard actually wants."""
    days = [lo + timedelta(days=n) for n in range((hi - lo).days)]
    per_day, totals = {}, defaultdict(float)
    for start in days:
        norm, _, _ = allocate(
            scan_transcripts(cfg, start, start + timedelta(days=1))
            + load_events(cfg, start, start + timedelta(days=1)),
            start, start + timedelta(days=1))
        merged = defaultdict(float)
        for key, mins in norm.items():
            merged[resolve(cfg, key)] += mins
        per_day[start.date()] = merged
        for who, mins in merged.items():
            totals[who] += mins
    if not totals:
        return f"_No tracked activity for {title}._\n"

    order = sorted(totals, key=lambda w: -totals[w])
    head = " | ".join(f"{d.day:02d}" for d in days)
    lines = [f"| Project | Charge | {head} | Total |",
             "|---|---|" + "---|" * (len(days) + 1)]
    for who in order:
        if q(cfg, totals[who]) == 0:
            continue
        project, charge, billable = who
        label = project if billable else f"{project} (nb)"
        cells = " | ".join(
            f"{q(cfg, per_day[d.date()].get(who, 0)):.2f}".replace("0.00", "-")
            for d in days)
        lines.append(f"| {label} | {charge} | {cells} | {q(cfg, totals[who]):.2f} |")
    daily_billable = [sum(m for w, m in per_day[d.date()].items() if w[2]) for d in days]
    cells = " | ".join(f"{q(cfg, m):.2f}".replace("0.00", "-") for m in daily_billable)
    lines.append(f"| **Billable/day** | | {cells} | **{q(cfg, sum(daily_billable)):.2f}** |")
    return "\n".join(lines) + (
        f"\n\n_{title}, by day. Columns are days of the month; `-` is under the "
        f"0.25 h rounding floor. `(nb)` = non-billable. Generated "
        f"{datetime.now():%Y-%m-%d %H:%M} by `scripts/timesheet.py`. Presence time, "
        f"not a certified timecard._\n")


# -------------------------------------------------------------------- writing


def splice(path, heading, body, header=None):
    """Replace the `heading` section of a markdown file, or append it."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path) as fh:
            text = fh.read()
    except FileNotFoundError:
        text = (header or "") + "\n"
    block = f"{heading}\n\n{body}"
    if heading in text:
        start = text.index(heading)
        rest = text[start + len(heading):]
        nxt = rest.find("\n## ")
        tail = rest[nxt + 1:] if nxt != -1 else ""
        text = text[:start] + block + ("\n" + tail if tail else "")
    else:
        text = text.rstrip("\n") + "\n\n" + block
    with open(path, "w") as fh:
        fh.write(text)
    return path


# ------------------------------------------------------------------- periods


def period_bounds(cfg, day):
    """[start, end) of the pay period containing `day`. End is exclusive."""
    if cfg.get("pay_period", "semi-monthly") == "biweekly":
        anchor = date.fromisoformat(cfg["pay_period_anchor"])
        start = anchor + timedelta(days=14 * ((day - anchor).days // 14))
        return start, start + timedelta(days=14)
    # semi-monthly: the 1st-15th and the 16th-end of month
    if day.day <= 15:
        return day.replace(day=1), day.replace(day=16)
    nxt = (day.replace(day=28) + timedelta(days=4)).replace(day=1)
    return day.replace(day=16), nxt


def cmd_init():
    cfg = load_config()
    for path in sorted(glob.glob(os.path.join(TRANSCRIPTS, "*"))):
        if not os.path.isdir(path):
            continue
        key = dir_key(os.path.basename(path))
        guess = key.replace("-Users-", "", 1).replace("-", "/")
        guess = guess.split("/", 1)[1] if "/" in guess else guess  # drop the username
        cfg["projects"].setdefault(key, {"project": guess, "charge": "", "billable": True})
    os.makedirs(os.path.dirname(cfg_path()), exist_ok=True)
    with open(cfg_path(), "w") as fh:
        json.dump(cfg, fh, indent=2, sort_keys=True)
    print(f"wrote {cfg_path()} with {len(cfg['projects'])} source dirs; "
          f"fill in project names + charge codes.")


def selftest():
    cfg = dict(DEFAULT_CONFIG)
    lo = datetime(2026, 1, 1, 9, 0)
    hi = lo + timedelta(hours=4)
    a = (lo, lo + timedelta(minutes=60), "A", 1.0)
    b = (lo + timedelta(minutes=30), lo + timedelta(minutes=90), "B", 1.0)
    norm, raw, wall = allocate([a, b], lo, hi)
    assert wall == 90, wall                      # union of 0-60 and 30-90
    assert raw["A"] == 60 and raw["B"] == 60
    assert abs(norm["A"] - 45) < 1e-9, norm      # 30 solo + 30 shared/2
    assert abs(sum(norm.values()) - wall) < 1e-9  # normalized == wall clock
    norm, _, wall = allocate([a], lo, hi)
    assert wall == 60 and norm["A"] == 60
    m = (lo, lo + timedelta(minutes=60), "M", 3.0)          # a meeting outweighs a session
    norm, raw, wall = allocate([a, m], lo, hi)
    assert wall == 60 and raw["M"] == 60
    assert abs(norm["M"] - 45) < 1e-9 and abs(norm["A"] - 15) < 1e-9, norm   # 75 / 25
    assert abs(sum(norm.values()) - wall) < 1e-9
    assert q(cfg, 55) == 1.0 and q(cfg, 8) == 0.25   # quarter-hour rounding
    wt = {"projects": {"-repo": {"project": "R", "charge": "C1"},
                       "-repo--claude-worktrees-x-ab12": {"project": "X", "charge": "C2"}}}
    assert resolve(wt, "-repo--claude-worktrees-x-ab12")[0] == "X"   # worktree entry wins
    assert resolve(wt, "-repo--claude-worktrees-y-cd34")[0] == "R"   # falls back to the repo
    assert period_bounds(cfg, date(2026, 1, 6)) == (date(2026, 1, 1), date(2026, 1, 16))
    assert period_bounds(cfg, date(2026, 1, 16)) == (date(2026, 1, 16), date(2026, 2, 1))
    assert period_bounds(cfg, date(2026, 2, 28)) == (date(2026, 2, 16), date(2026, 3, 1))
    assert period_bounds(cfg, date(2026, 12, 31)) == (date(2026, 12, 16), date(2027, 1, 1))
    past = dict(cfg, target_hours_per_week=20)   # a fully elapsed week: Mon-Fri
    assert target_hours(past, datetime(2026, 1, 5), datetime(2026, 1, 12)) == 20.0
    assert target_hours(past, datetime(2026, 1, 10), datetime(2026, 1, 12)) == 0.0  # weekend
    assert target_hours(cfg, datetime(2026, 1, 5), datetime(2026, 1, 12)) == 0.0    # unset
    bi = dict(cfg, pay_period="biweekly")
    assert period_bounds(bi, date(2026, 1, 6)) == (date(2026, 1, 5), date(2026, 1, 19))
    assert period_bounds(bi, date(2026, 1, 4))[0] == date(2025, 12, 22)  # before anchor
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", nargs="?", default="day",
                    choices=["day", "week", "period", "init"])
    ap.add_argument("date", nargs="?", help="anchor date, YYYY-MM-DD (default today)")
    ap.add_argument("--write", action="store_true", help="patch the vault files")
    ap.add_argument("--by-day", action="store_true",
                    help="project x day matrix instead of one total (week/period)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.mode == "init":
        return cmd_init()

    cfg = load_config()
    day = date.fromisoformat(args.date) if args.date else date.today()

    if args.mode == "day":
        lo, hi = datetime.combine(day, time()), datetime.combine(day, time()) + timedelta(days=1)
        body = render(cfg, lo, hi, f"Time for {day}")
        target = os.path.join(VAULT, "daily_notes", f"{day}.md")
        header = f"# {day}: Daily Note\n"
    elif args.mode == "week":
        start = day - timedelta(days=day.weekday())
        lo, hi = datetime.combine(start, time()), datetime.combine(start, time()) + timedelta(days=7)
        iso = start.isocalendar()
        label = f"Week of {start} ({iso[0]}-W{iso[1]:02d})"
        body = (render_by_day(cfg, lo, hi, label) if args.by_day
                else render(cfg, lo, hi, label))
        if args.write:  # the written rollup carries both shapes
            body = render(cfg, lo, hi, label) + "\n" + render_by_day(cfg, lo, hi, label)
        target = os.path.join(VAULT, "daily_notes", "weekly", f"{iso[0]}-W{iso[1]:02d}.md")
        header = f"# {iso[0]}-W{iso[1]:02d}: Week of {start}\n"
    else:
        start, end = period_bounds(cfg, day)
        lo, hi = datetime.combine(start, time()), datetime.combine(end, time())
        label = f"Pay period {start} to {end - timedelta(days=1)}"
        body = (render_by_day(cfg, lo, hi, label) if args.by_day
                else render(cfg, lo, hi, label))
        if args.write:
            body = render(cfg, lo, hi, label) + "\n" + render_by_day(cfg, lo, hi, label)
        target = os.path.join(VAULT, "daily_notes", "periods", f"{start}_to_{end - timedelta(days=1)}.md")
        header = f"# Pay period {start} to {end - timedelta(days=1)}\n"

    if args.write:
        print("wrote " + splice(target, "## Time", body, header))
    else:
        print(body)


if __name__ == "__main__":
    main()
