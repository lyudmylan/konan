# Intent: adopt Charter

Work item: #79. Status: done. Approval: a person merges the change request that adds this file.

## Goal

This repo follows Charter: a contract that names the organization source and the version of Charter,
and a rules file that carries the rules of the contract with their identifiers.

## In scope

- `charter.toml`: the contract, written by the setup step of Charter, with the quality checks, the code
  paths, and the tiers of this repo. The values are in the file, not here.
- `AGENTS.md`: the rules of this repo stay. The section "Charter" adds the rules of the contract with
  their identifiers. The references to the skills of the previous framework become `tracker`,
  `review-loop`, and the built-in `/code-review`. The sentence that allowed trivial fixes direct to
  main goes: the organization locks one ticket and one change request per change.
- `CLAUDE.md`: one sentence points to the contract and to the section "Charter".
- `.github/workflows/`: `tests`, `verdict`, and `review-intents`, written by the setup step; they fetch
  Charter at the tag of `charter.version`. `gates.yml` goes: `tests` runs the same two commands from the
  contract.
- `intents/_template.md`, and this file as the first intent. The contract sets `build.plan_before_code`:
  from the next work item on, the plan `intents/<part>.plan.md` comes before the code. This change request
  is the bootstrap and carries no plan.

## Out of scope

A ruleset on the main branch: the repo is private on the free plan; the check "verdict" informs, and a
person merges. A change to `docs/product.md` or `docs/architecture.md`: both exist and stay.

## Acceptance checks

## Automatic checks

1. The contract passes the contract checks against the organization source, and the rules file agrees
   with it. command: `charter-check all charter.toml`
2. The two quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`
3. The three workflows exist and the old one is gone.
   command: `test -f .github/workflows/tests.yml -a -f .github/workflows/verdict.yml -a -f .github/workflows/review-intents.yml -a ! -e .github/workflows/gates.yml`

4. `CLAUDE.md` points to the contract, no instruction file names the skills of the previous framework, and
   `AGENTS.md` no longer allows trivial fixes direct to main.
   command: `sh -c 'grep -q charter.toml CLAUDE.md && ! grep -nE "shipping|repo-review" CLAUDE.md AGENTS.md && ! grep -niE "trivial|direct to main" AGENTS.md'`

## Manual checks

5. On the change request that adds this file, the check `tests` runs and the intent reviewer posts its
   report; the check "verdict" runs from the next change request on, because GitHub runs it from the main
   branch. who: the leader. Not automatic: the runs need the two secrets on GitHub.
6. In a session of Claude Code in this repo, `charter-check` and `charter-gate` are on the path, from the
   installed plugin. who: the leader. Not automatic: the plugin is installed per computer.
   The run of 2026-10-01, by the leader, in a new session: `charter-check all charter.toml` ran by name
   and passed against the organization source.
