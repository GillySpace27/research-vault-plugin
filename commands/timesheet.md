---
description: Per-project hours derived from Claude Code session timestamps plus logged communications. Writes a `## Time` layer into the daily note, and weekly / pay-period rollups.
argument-hint: "[day|week|period] [YYYY-MM-DD] [--write]"
---

# /timesheet

Runs `scripts/timesheet.py`. See the vault-time skill for what the numbers mean
and their limits.

## Instructions

### 1. Resolve arguments

- Scope: `day` (default), `week`, or `period` (pay period; `semi-monthly` or
  `biweekly` per `time_tracking/config.json`).
- Date: default today; resolve any relative reference ("Monday", "last week")
  to absolute `YYYY-MM-DD` first.
- `--write` patches vault files; without it, report to the user only.
- Bare `/timesheet` with no arguments: `day`, today, no write.

### 2. Run it

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/timesheet.py" <scope> <date> [--write]
```

`RESEARCH_VAULT_DIR` must point at the vault (it is set in `settings.json`; if
the script reports the wrong path, pass it inline).

**Never hand-compute or adjust the numbers.** If a figure looks wrong, fix the
inputs (`config.json` mappings, `events.tsv` rows) and re-run.

### 3. Report

Show the table as returned, then at most three lines:

- anything unmapped, and the one-line fix (`timesheet.py init`, then edit
  `time_tracking/config.json`);
- concurrency overlap, if flagged;
- a reminder that this is presence time for review, not a filed timecard.

### 4. Offer the rollup

If the date is a Friday, offer `week --write`. Timecards are typically due
before the period closes, so from a few days before the end of a pay period
onward, offer `period --write` too (re-running later refreshes it in place).

## Notes

- `--write` regenerates the `## Time` section in place; re-running is safe.
- Missing off-session work (email, meetings) means it was never logged to
  `time_tracking/events.tsv`: add rows there, not to the output.
