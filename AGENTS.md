# konan — repo agent instructions

Read `docs/product.md` for what konan is; this file is how to work here. The repo
follows Charter: the contract is `charter.toml`, and the section "Charter" below holds
the rules of the contract with their identifiers. The skills `tracker` and
`review-loop` of the plugin `charter-practices` apply, and the built-in `/code-review`
before a change request. The rules of the contract hold; this file adds the rules of
this repo on top of them.

## Lab boundary (hard rule)

- The investigator touches a target only through `scripts/probe.sh` — GET-only,
  path-allowlisted, timeout-guarded — and by reading files under `lab/` (logs). Under
  an adapter document (`docs/adapters/<target>.md`, named by `KONAN_ADAPTER` in the environment)
  the investigator's hand is instead the adapter's read-only MCP tools, named one by one
  in `.claude/settings.json`, and the lab's files and probes are out of bounds by the
  rule of the investigate skill; the mechanical boundary of an adapter is on its server
  side (a Viewer account, the server's write tools off, the allowlist). The
  boundary is mechanical, not prompted, and it is enforced by content: a `PreToolUse`
  hook (`hooks/boundary.py`, registered in `.claude/settings.json`) reads every Bash
  command whole and **denies** raw network clients anywhere in it (`curl`, `wget`,
  `http`, `xh`, `nc`, …, inline python/node network calls, `/dev/tcp`), the operator
  surfaces `/simulate` and `/chaos` by any route, and destructive `git push` forms;
  it **allows** exactly the shapes an unattended shift needs (one `scripts/probe.sh`
  call, `git add journals/…`, `git commit -m "…"`; a `cd <session cwd> &&` prefix is
  transparent — same surface, the harness's subagent idiom); everything else takes the normal
  permission flow — settings rules, then a prompt — and an unattended shift fails
  closed on a prompt. The settings `allow`/`deny` lists stay as the belt (deny rules
  win over any hook allow). Tripwire: the second denial in a session freezes it —
  every further Bash call is denied and the agent is told to stop and page; a denied
  action is a signal to stop, never a puzzle to solve. Changing the hook, its pins, or
  either settings list is a SPEC-grade change (PR with rationale, never casual). The
  plugin ships the same hook via `hooks/hooks.json`; in a checkout of this repo the
  settings registration is the active one — do not install the plugin into the repo
  itself (double registration double-counts the tripwire). The hook decides only inside
  a konan workspace (a checkout of this repo, or a directory at or below the marker file
  `.konan-workspace`) and is silent elsewhere; the scope is defined once, in the README
  section "Install as a plugin".
- `/simulate` and `/chaos` are outside the probe allowlist even though they are GETs:
  faultline serves mutating GETs there (crash, hang, ballast), and chaos state is
  operator surface, not telemetry.
- Scenario triggering is eval-side only (`scripts/scenario.sh`) and deliberately NOT
  pre-approved — it must permission-prompt in an interactive session.
- Never "fix" the lab: faultline's defects are its contract; its repo governs itself.
- Eval integrity: ground-truth defect details and scenario recipes stay out of
  investigator-readable docs in this repo — they live in faultline's SPEC and in the
  eval fixtures under `eval/`. Investigations argue from telemetry only; the blinding
  contract (what an investigation session must never read: `eval/`, the issue
  tracker, the faultline checkout) is in `eval/README.md`.

## Workflow

- Issue-driven: one branch per issue; the PR body links `Closes #N`. Every change to a
  source file goes this way, also a small one: the contract locks it.
- Unattended shift writes: an on-call session (`/oncall`) may write `journals/` and
  git-commit them on the current branch — those two forms are narrowly allowlisted in
  settings so an unattended investigation never blocks on a prompt. Pushing stays
  human. Widening either entry is SPEC-grade, like the probe allowlist.
- Quality gates: `uv run eval/tests.py` (scorer + runner pins) and
  `python3 hooks/tests.py` (boundary decision pins, incl. eval-blind rows) must pass
  (they are `checks.quality` of the contract), the built-in `/code-review` before
  merge, and docs ship with the change. Skill changes are
  validated by re-running scenarios with the eval runner (`eval/README.md` → Running
  the corpus with the runner); wiring that into CI is still open (#34).
- Public-eventually: everything committed here — files, issue bodies, commit
  messages — must be publishable at the v0.1 flip.
- Branch safety: platform branch protection is plan-gated while the repo is private, so
  settings deny-rules block the habitual force-push and remote-branch-deletion forms as
  a compensating belt (agent-side accidents, not adversaries). The real ruleset lands at
  the public flip (#13).

## Commands

- `scripts/lab.sh start|stop|status` — run faultline as the lab target
  (`FAULTLINE_DIR` defaults to `../faultline`; logs land in `lab/logs/`, gitignored).
- `scripts/probe.sh /path[?query]` — read-only probe; trailer line carries HTTP status,
  duration, and the stamped request id (grep it in the logs to correlate).
- `scripts/scenario.sh chaos-on|chaos-off|chaos-status|sim|order|get` — eval-side
  scenario triggers and simulated user traffic; prompts by design. Full lab contract:
  `docs/lab.md`.
- `uv run eval/run.py --run-id <id> --model <m> [--repeat N] [--fixtures …]` — the eval
  runner: staged, blinded, headless investigations per fixture; journals + sidecars under
  `eval/runs/<id>/`, scored into `eval/runs/<id>/scorecard.md`. Operator side; it draws
  from the same subscription pool as everything else — batch with `--max-runs`.
- `scripts/alert.sh "<summary>" [alertname] [severity]` — eval-side alert emitter:
  appends one contract-shaped complaint line to `alerts/inbox.jsonl` (the lab trigger
  profile, `docs/triggers.md`); prompts by design, like every operator action.

## Charter

The rules of the contract `charter.toml`, which references the organization source. Each rule ends
with the identifier of its rule in the contract. The scripts of Charter come with the plugin `charter`:
`charter-check`, `charter-gate`, and `charter-setup` are on the path of the shell while the plugin is
enabled.

### How a change moves

- Each change to a source file (code, config, doc) has an issue in the tracker. [change.ticket_per_change]
- Work on a branch. Open a change request that references the issue. A person merges. [tiers.high.approver]
- The author of a change is not its reviewer. [change.author_not_reviewer]
- The contract, this file, the intents, and the workflows are in the high risk tier: a deep review, and
  the leader approves. [tiers.high.paths]
- A person approves each change to a contract. [change.person_approves_contract]
- On GitHub, the workflows `tests` and `verdict` run on each change request. A red check "verdict"
  blocks the merge; its reasons are in the check and in the job log. [checks.quality]

### Plan before the code

A work item has an intent in `intents/<part>.md`: the goal, what is in scope, what is out of scope, and
the acceptance checks. `intents/_template.md` is the form. A person approves the intent through a change
request before the work starts. The skill `tracker` writes the issue and the intent; the issue names the
intent with one line, `Intent: intents/<part>.md`. [tiers.high.paths]
Before the code, the plan `intents/<part>.plan.md`: the steps, the files to change, the tests to add, in
the words of the author. The agent stops and asks the person who holds the work item to accept it; the
code starts after the acceptance. The verdict checks that the plan exists; a change request that changes
only intents needs no plan. [build.plan_before_code]

### Before a push

Two commands must pass: `charter-gate quality --contract charter.toml` runs the quality checks that the
contract lists, and `charter-check all charter.toml` runs the contract checks. [checks.quality]
[instructions.file] [documents.text_checked]

When a file under a declared code path changes, `docs/product.md` changes too, or the change request
has one line in this exact form: `No document change: <reason>`. [documents.code_paths]
A false failure of a gate: `False failure: <gate>: <reason>`. A finding of the intent reviewer that the
author drops: `Dropped finding: <reason>`. One that the leader marks as wrong: `False finding: <reason>`. [checks.quality]

### Text of commits, change requests, and issues

- No private material: no file paths of a computer, no mail addresses, no tokens. [text.private_material_patterns]
- No session links, and no names of other projects of this organization. [text.session_link_patterns]
  [text.project_name_patterns]

### Review and limits

In a review, look also for broken contracts between parts of the system, and for documents that the
change made stale. [documents.necessary]
Stop and ask a person after the limits of the contract: failed runs of the acceptance checks, review
rounds, or refusals in sequence. [limits.acceptance_loop] [limits.review_loop] [limits.refusals]
The intent reviewer gives each finding a severity. A finding at the threshold or above keeps the
author-reviewer loop open; below it, or at the limit, the loop ends and a person decides. The author side
is the skill `review-loop`. [review.threshold] [limits.review_loop]
