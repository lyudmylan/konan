# Intent: Charter 0.3.19 and the boundary of a run

Work item: #123. Approval: a person merges the change request that adds this file.

## Goal

The repo follows Charter 0.3.19 and its contract states the boundary of a run of an agent, so that the
leader can turn the runs on with one secret and one label.

## In scope

The work item changes the files below. Each decision in it is of 2026-11-25 and is the leader's with her
merge.

- The order: two change requests. The verdict runs from the main branch, so the scripts of 0.3.1 check the
  contract of the first one, and they refuse a field that they do not know. The first change request holds
  no new field. After its merge the main branch names 0.3.19, and the scripts of 0.3.19 check the second.
  - The first: `charter.version = "0.3.19"`; the workflows `verdict`, `review-intents`, `review-code` and
    `run`; the two templates; `.gitignore`; the rules of `AGENTS.md` that cite no new field (who merges,
    the place of a plan, and which workflow runs on which change request); this intent and its plan. Its
    text links the issue with `Part of`.
  - The second: the new fields of `charter.toml` and the source `v2`; the quality command; `tests.yml`;
    the other rules of `AGENTS.md`. Its text closes the issue.
  - Between the two merges the contract checks of 0.3.19 fail on the main branch, because the contract
    names no product test and no reason for none. No change request other than the second one is open in
    that time.
- `charter.toml`, the source: `source.version = "v2"`. Version 2 of the organization rules sets
  `run.answer_start = "factory"`: after the reports of the reviewers on the change request of a run, the
  workflow `run` starts an agent that answers the findings at `review.threshold` or above, inside the
  limit of 3 rounds. The repo keeps that value. Each answer uses the subscription with no start by a
  person. The variable `CHARTER_RUNS` of the repo with the value `off` stops each run and each answer.
- `charter.toml`, `[boundary]`. A run never changes a file under `no_write`:
  - `charter.toml`, `AGENTS.md`, `CLAUDE.md`, `intents/**`, `.github/**`, `.claude/**`: the list of the
    setup step.
  - `hooks/**`: Claude Code starts a hook of the project outside the sandbox of a run, in the process that
    holds the token of the model. A run that could change the hook could run code there. So a work item
    that changes the boundary hook or its pins is always the work of a person.
  - `scripts/probe.sh` and `scripts/receive.py`: the two scripts that a shift starts without a prompt.
  - `.claude-plugin/**`: the manifest of the plugin, which ships the hook to other computers.
  - `journals/**` and `eval/runs/**`: the records of investigations. A run starts no investigation, so it
    has none to add, and a change of a record changes evidence.
  - `eval/scenarios/**`: the fixtures hold the expected answers, so a change there changes the measure.
  - `.gitignore`: the script that commits the result of a run takes each file that git does not ignore.
  - `LICENSE` and `NOTICE`.

  A run never reads a file under `no_read`: the four patterns of the setup step for `.env` files, and
  `alerts/receiver-token`.

  These stay open to a run, each for its reason. A person merges each change request of a run, and the
  reviewer of the code reads it first.
  - `eval/*.py`, the scorer, the runner, the table script and their pins in `eval/tests.py`: the work
    items on them have automatic checks, and such a work item adds its pin to `eval/tests.py`, so that
    file stays open too. The first run that is planned builds such a work item. A run can so change the
    scorer and its pins in one diff. A change of the measure then shows only in the diff, and the
    reviewer of the code and the person who merges read it.
  - `eval/BENCHMARK-results.md` and `eval/scorecard.md`: scripts generate them from the records, and a
    work item on the table script generates them again.
  - `skills/**`: a run can change the text of a skill, and it cannot show that an investigation follows
    it. That check stays a round of the eval runner, started by the operator.
  - `scripts/**` apart from the two scripts above: the lab scripts and the alert emitter are the side of
    the operator. The shell of a run has no network and no lab, so a run can start none of them against
    a target; a change of one goes through the review and the merge.
  - `docs/**`, `README.md`, `plans/**`: a work item changes its documents and writes its plan.
- `charter.toml`, the other new fields: `review.code_blocks = false`, so the reviewer of the code reports
  and blocks nothing; `documents.absent` with the four patterns of the setup step, and the repo holds no
  such file; `checks.no_product_reason` with this text: "konan is a set of skills that a Claude Code
  session runs against a live target, so each start of the product is a model call against a running
  lab; the parts that are code (the scorer, the boundary hook, the receiver) are tested by the three
  quality commands."
- `charter.toml`, the first quality command: `uv run --offline --cache-dir .uv-cache eval/tests.py`. The
  shell of a run has no network and writes only inside the folder of the repo and the temp folder. `uv`
  fetches the two packages of the tests at its first call, and it writes into its cache at each call. So
  the cache is the folder `.uv-cache` of the repo, which git ignores, and one step fills it before the
  tests: `uv sync --script eval/tests.py --cache-dir .uv-cache`. With `--offline` the command never
  fetches, on each computer and in each workflow. The other two quality commands need Python only, and
  the loopback address for the tests of the receiver.
- The toolchain block of `tests.yml` (both jobs) and of `run.yml`: the step that installs `uv`, then the
  step that fills the cache.
- `tests.yml`, the job `product`: the setup step writes it into each repo. It runs the gate `product`.
  With a reason and no command in the contract, the gate passes, prints the reason, and runs no test. The
  verdict of 0.3.19 reads the check `product` beside the check `tests`.
- `verdict.yml`, the step "Merge, for a tier whose approver is agent": the setup step writes it into each
  repo. It merges only when three settings of a person hold: a tier with the approver `agent`, the flag
  `review.code_blocks`, and the secret `CHARTER_MERGE_TOKEN`. This repo sets none of the three, so the
  step merges nothing.
- The five workflows: as the setup step of 0.3.19 writes them from the values of the contract and the two
  steps of the toolchain. No line is changed by hand.
- `intents/_template.md` and the new `plans/_template.md`: as the setup step writes them. The plan of a
  new work item is `plans/<part>.md`. The plans that exist stay at `intents/<part>.plan.md`, and the plan
  of this work item is there too, because the verdict of 0.3.1 reads a plan only there.
- `AGENTS.md`: the section "Charter" takes the rules of the template of 0.3.19 (who merges, the place of a
  plan, the boundary of a run, no file for one decision, the reviewer of the code), one rule on the answer
  of an agent to the findings on a run, and the reason for no product test. The sections of konan name
  the new quality command and the step that fills the cache. One new paragraph says what a run meets in
  this repo: the boundary hook governs a run as it governs each session in a checkout, so a run gets a
  denial for a command that names a raw network client or an operator surface, and the second denial
  freezes it. Such a run ends as blocked, with the reason on the issue.
- No change of `docs/product.md` and of `docs/architecture.md`: the work item changes no file under a code
  path, and no part of the product changes.

## Out of scope

- The secret `CHARTER_RUN_TOKEN` and the label `charter-run`. A person creates them, and no run starts
  before.
- The first run. It belongs to the work item of the issue that it builds.
- A change of the boundary hook for a run, for example no freeze in a run. It changes a safety behaviour,
  so it is a work item of its own with its own intent. The issue #125 holds the risk and the facts.
- The tier whose approver is `agent`, and the end of the shadow period of the reviewer of the code. A
  person merges each change request.
- A product test.
- The ruleset of the main branch.
- A move of the plans that exist to `plans/`.

## Acceptance checks

## Automatic checks

The commands `charter-check`, `charter-gate` and `charter-setup` below are those of Charter 0.3.19. Checks 1
to 6 hold after the second change request. Check 7 holds in full after the second, and on the first with
the one difference that it names.

1. The contract names 0.3.19 and the source `v2`.
   command: `grep -A1 '^\[charter\]' charter.toml | grep -q '^version = "0.3.19"' && grep -A3 '^\[source\]' charter.toml | grep -q '^version = "v2"'`
2. The contract checks pass.
   command: `charter-check all charter.toml`
3. The quality commands pass with no fetch, after the step that fills the cache.
   command: `uv sync --script eval/tests.py --cache-dir .uv-cache && charter-gate quality --contract charter.toml`
4. Git ignores the cache.
   command: `git check-ignore -q .uv-cache/x`
5. The settings of a run can be written, and they close the boundary hook.
   command: `charter-check boundary charter.toml | grep -q 'hooks'`
6. The boundary gate refuses a run that changed the hook, and passes a run that changed a skill and its
   plan.
   command: `printf 'hooks/boundary.py\n' > /tmp/changed-1 && ! charter-gate boundary --contract charter.toml --changed /tmp/changed-1 && printf 'skills/oncall/SKILL.md\nplans/x.md\n' > /tmp/changed-2 && charter-gate boundary --contract charter.toml --changed /tmp/changed-2`
7. The five workflows and the two templates are equal to the output of `charter-setup`, run into an empty
   folder with the values of the contract and the two steps of the toolchain. The arguments of
   `charter-setup` below must be equal to the values of `charter.toml`; a change of the contract changes
   them. The three `diff` commands run one by one, and the check reads what they print, not the exit
   status of the block. After the second change request each prints nothing.
   On the first, the `diff -r` prints one difference, `tests.yml`, and the two other commands print
   nothing.
   command:
   ```
   D=$(mktemp -d) && mkdir "$D/out"
   printf '%s\n' '- uses: astral-sh/setup-uv@v5     # the quality checks of this repo run with uv' '- name: Fill the package cache of the eval tests, inside the folder of the repo' '  run: uv sync --script eval/tests.py --cache-dir .uv-cache' > "$D/toolchain.yml"
   charter-setup --target "$D/out" --repo konan --source https://github.com/lyudmylan/charter-org --source-version v2 --leader lyudmylan --code-path 'skills/**' --code-path 'hooks/**' --code-path 'scripts/**' --high-path 'hooks/**' --high-path '.claude/settings.json' --high-path 'scripts/probe.sh' --high-path 'scripts/receive.py' --quality 'uv run --offline --cache-dir .uv-cache eval/tests.py' --quality 'python3 hooks/tests.py' --quality 'python3 scripts/tests.py' --toolchain "$D/toolchain.yml" < /dev/null
   diff -r .github/workflows "$D/out/.github/workflows"
   diff intents/_template.md "$D/out/intents/_template.md"
   diff plans/_template.md "$D/out/plans/_template.md"
   ```
8. On the first change request, the contract checks of 0.3.1 pass, so the verdict of the main branch can
   be ready.
   command: `charter-check all charter.toml` with the scripts of the tag `charter--v0.3.1`
9. On the second change request, the check `tests` passes, and the check `product` passes by the reason
   in `checks.no_product_reason`, with no product test run.
   command: `gh pr checks <number>` shows both as pass.

## Manual checks

10. On the second change request, the check "verdict" runs with the scripts of 0.3.19 and prints the
    lines of the code review and of the product test. who: the engineer. Not automatic: the verdict runs
    from the main branch after the first merge, so no command on a branch shows it.
11. The three quality commands pass with the network closed and with writes only in the folder of the repo
    and the temp folder. who: the engineer, with the system sandbox of the developer computer. Not
    automatic: the sandbox of a run exists only on a machine of the code host, and the first run is the
    real test.
