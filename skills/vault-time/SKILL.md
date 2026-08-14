---
name: vault-time
description: Time tracking for the research vault - derives per-project hours from Claude Code session transcripts plus a logged-communications ledger, and writes a `## Time` layer into the daily note, a weekly rollup, and a pay-period rollup. Use whenever the user asks how long something took, how much time went to a project, what to put on a timecard, or as part of the "update the vault" convention.
---

# Vault time tracking

Answers "where did the day go, and what can I honestly charge it to?"

## Where the numbers come from

1. **Claude Code session transcripts** (`~/.claude/projects/<dir>/*.jsonl`).
   Every line carries an ISO timestamp; the directory name identifies the
   project. Timestamps are clustered into work segments (gap longer than
   `idle_gap_minutes` ends a segment). This is the primary source and needs no
   auth, no API, no memory of what happened.
2. **`time_tracking/events.tsv`** - work with no session behind it: email
   sent, Slack thread, calendar meeting, phone call. Claude appends rows
   during an update sweep; the user can add rows by hand.

`scripts/timesheet.py` merges both. **Never compute these numbers yourself and
never estimate hours from memory** - run the script, quote the script.

## What the number means

It is **presence time at the keyboard, per project**, not certified effort:

- A minute where two projects were open bills half to each, so the per-project
  column always sums to real wall-clock time. The unsplit `Raw` column stays
  visible so the overlap is auditable, not silent.
- Thinking, reading on paper, and hallway conversation are invisible to it.
  They belong in `events.tsv` if they matter.
- An idle browser window is invisible to it too, which is the point.

Say so when reporting: this is a **draft for review**, and the number that goes
on an NWRA timecard is Gilly's call, not the script's.

## Commands

```bash
export RESEARCH_VAULT_DIR=~/path/to/vault          # already set in settings.json
python3 scripts/timesheet.py day    [YYYY-MM-DD] [--write]
python3 scripts/timesheet.py week   [YYYY-MM-DD] [--write]   # ISO week of that date
python3 scripts/timesheet.py period [YYYY-MM-DD] [--write]   # pay period
python3 scripts/timesheet.py init                            # register new source dirs
python3 scripts/timesheet.py --selftest
```

Without `--write` the markdown goes to stdout - use that for a quick answer.
With `--write` it replaces the `## Time` section of:

- `daily_notes/YYYY-MM-DD.md`
- `daily_notes/weekly/YYYY-Www.md`
- `daily_notes/periods/YYYY-MM-DD_to_YYYY-MM-DD.md` (one pay period)

The section is regenerated in place, so re-running is always safe and never
duplicates. Everything else in those files is left untouched.

## When to run it

- **End of a working session, and as step 3.5 of "update the vault"**: run
  `day --write` after the daily-note bullets land, so the `## Time` layer and
  the `## Work log` agree.
- **Friday (or on the last day worked in an ISO week)**: `week --write`.
- **Before the timecard is due**, which is usually *before* the period ends:
  run `period --write` when filling the card in, then again on the last day of
  the period so the vault's record matches what was actually worked. The file
  is regenerated in place, so running it early costs nothing.
- **Any time the user asks** "how long did X take", "how much time on PUNCH
  this week", "what do I put on my timecard": run it and quote it.

`pay_period` in the config is `semi-monthly` (the 1st-15th and the 16th-end of
month) or `biweekly` (every 14 days from `pay_period_anchor`).

## Logging communications

During `/update --comprehensive`, when the external sweep surfaces sent email,
Slack messages, or calendar events tied to a vault project, append a row to
`time_tracking/events.tsv`:

```
2026-08-13T14:05	PUNCH PULSE	6	gmail	reply to Cherilynn re: dome poll
2026-08-13T15:00	HFR Coronal Heating	30	calendar	Step-2 sync with Mari Paz
```

Rules:

- **Real durations for meetings** (calendar gives start and end). Emails and
  chat messages get the default increment unless the user says otherwise -
  never invent a duration that looks precise.
- **One row per event**, append-only. Don't rewrite history.
- **Don't log an email that was drafted inside a session** - the session
  transcript already covers that time; the row would double it.
- **Don't log received mail**, only work actually done.

## Unmapped and non-billable work

`time_tracking/config.json` maps each session directory to a project label, an
NWRA charge code, and a `billable` flag. New directories show up as
`unmapped: <path>` in the table; run `init` and fill in the entry. Personal
work stays in the table with `"billable": false` so the day still reconciles to
24 hours without inflating the billable total.

## Reporting style

Terse. A table and one line of caveat. Flag anything the user must decide:
unmapped directories, a suspiciously long unattended segment, a billable total
that exceeds what the user is allowed to charge in a day.
