# Plan: the verdict permission of this repo (#83)

Intent: `intents/verdict-permissions.md`. Accepted by the leader in the conversation on 2026-10-29, before
the code.

## Steps

1. `charter.toml`: `charter.version = "0.3.1"`.
2. `.github/workflows/verdict.yml`: `actions: read` in the permissions block, the line of the 0.3.1
   template.
3. The two commands of `AGENTS.md`. One change request, `Closes #83`, with the intent and this plan in it,
   as the adoption did (#80). The leader merges on the two green checks and the intent review, because the
   verdict runs from the copy of the workflow on main.

## Files

`charter.toml`, `.github/workflows/verdict.yml`, `intents/verdict-permissions.md`, and this file.

## Tests

None added: the checks of the intent are commands on the two files, and the proof is the first verdict run
after the merge (manual check 4).
