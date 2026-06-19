---
name: vault-people
description: Canonical roster of people the user works with — full names, affiliations, role on which projects, and the short handles the user writes (e.g. #firstname-lastname). Use whenever a person reference appears in a task, email, conversation, or daily note, and when deciding which handle to write into a task.
---

# Vault people

Hot cache of the people the user works with most. The full per-person profiles
live under `memory/people/<name>.md` — see the vault-memory skill for the
tiered lookup pattern.

## Roster

<!--
  This table is the user's canonical roster. It starts empty — `/start` and
  `/update --comprehensive` populate it as collaborators come up, and the user
  can edit it directly. Keep the columns stable.

  An example of a filled-in roster ships at `_examples/people.example.md` in
  the plugin — read it to see the intended shape, but do NOT copy its contents
  in as real people.
-->

| Handle | Full name | Affiliation | Role / context |
|---|---|---|---|
| _(empty — seed via `/start`)_ | | | |

## When a reference is ambiguous

If the user writes a bare first name with no further context, prefer the most
recently-active collaborator with that name — but always **ask before guessing**
unless the surrounding context makes it unambiguous. Getting the wrong person
assigned to a task is worse than a one-line clarification.

## When a new person comes up

1. Use the handle the user uses in conversation, or coin a
   `#firstname-lastname` handle in lowercase-hyphen form.
2. If they'll recur, add them to the table above (in this live skill file) and
   create `memory/people/<name>.md` with role, affiliation, and the project
   files they appear in.
3. If they're one-off, just tag and move on.

## Cross-references

People also appear in project files under `## People`. Those entries are the
project-specific context (what they do *on that project*); this roster is the
general identity.
