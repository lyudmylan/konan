# Intent: the verdict permission of this repo

Work item: #83. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The check "verdict" runs to completion on every change request of this repo, as the contract says it does.

## In scope

- `charter.toml`: `charter.version = "0.3.1"`, the version of Charter whose verdict template declares
  `actions: read`: the scope that the facts step needs to list the runs of the review workflow on a private
  repo (Charter #63).
- `.github/workflows/verdict.yml`: the line `actions: read` in the permissions block, so that the permissions
  block of the workflow in this repo declares the scope of the template of 0.3.1.
- The defect, for the record: the setup step of Charter 0.3.0 wrote the workflow from a template without the
  scope. The facts step answered 403 on every change request since the adoption (#80), and the check never
  ran. A public repo serves the listing without the scope, which is why Charter itself did not see it.

## Out of scope

Any other change to the workflows. The ruleset of the main branch (#13). The round count of the review loop
(Charter #61).

## Acceptance checks

## Automatic checks

1. The contract names 0.3.1.
   command: `grep -A1 '^\[charter\]' charter.toml | grep -q '^version = "0.3.1"'`
2. The verdict workflow declares the scope.
   command: `grep -qE '^  actions: read' .github/workflows/verdict.yml`
3. The contract checks and the quality checks pass.
   command: `charter-check all charter.toml && charter-gate quality --contract charter.toml`

## Manual checks

4. On the first change request after this one merges, the check "verdict" runs from the main branch without
   the 403 of the facts step, and publishes "ready" or its reasons on the request. who: the leader. Not automatic: the check runs from the
   copy of the workflow on main, so this change request cannot show it.
