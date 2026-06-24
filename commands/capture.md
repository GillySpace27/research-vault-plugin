---
description: Quick-capture a one-line task. Drops it into the most likely project file based on content; falls back to `inbox.md` if ambiguous. Ten-second rule — minimal questions, surgical edit.
argument-hint: "\"task text with optional 📅 YYYY-MM-DD, ⏳, 🔼, #person\""
---

# /capture

Fast task capture. The whole point of the vault is that adding a task takes
seconds — this command honors that.

## Instructions

### 1. Parse the task line

`$ARGUMENTS` is the task text. It may already include emoji metadata
(📅 ⏳ ✅ 🔼 🔽) and `#person-handle` references. If not, do **not** invent
any — write only what the user said.

If `$ARGUMENTS` is empty, ask in one short line.

### 2. Resolve relative dates

If the text contains a relative date phrase ("Friday", "next week", "by end
of month", "asap"), resolve to absolute `YYYY-MM-DD` using today's date from
session context. Convert into the `📅 YYYY-MM-DD` form. "asap" → today's date
+ `🔼`.

### 3. Choose the target file

Walk the vault-projects skill's guidance and the project list in `projects.md`.
Pick the single most likely file based on:

- Explicit project name or codename in the text.
- People mentioned (cross-reference vault-people roster).
- Topic keywords.

Project files may live in subfolders (e.g. `projects/`); use the path recorded
in `projects.md`. If the task clearly belongs to a brand-new project, create
`projects/<name>.md` from `_templates/project.md` rather than adding it at the
root. If two or more files are roughly equally likely, default to **`inbox.md`**
(at the vault root) — the user can route it later via `/triage`. Don't ask a
question for a 10-second capture; just note the routing decision in the report.

### 4. Append

Append `- [ ] <task line>` under the target file's `## Open` block. Surgical
edit only — don't touch anything else in the file.

### 5. Report (one line)

```
→ <file>.md: <task line preview>   (assumed: <reason>, if non-obvious)
```

## Notes

- No clarifying questions unless `$ARGUMENTS` is empty. The 10-second rule.
- Never edit the daily note from this command — that's `/journal`'s job.
- Never invent metadata the user didn't supply.
