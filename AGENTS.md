# konan — repo agent instructions

Read `docs/product.md` for what konan is; this file is how to work here. The shared
AI-SDLC skills (`github-planning`, `github-shipping`, `repo-review`) apply; this file
overrides them where they conflict.

## Lab boundary (hard rule)

- The investigator touches a target only through `scripts/probe.sh` — GET-only,
  path-allowlisted, timeout-guarded — and by reading files under `lab/` (logs). The
  boundary is mechanical, not prompted, and it is enforced by content: a `PreToolUse`
  hook (`hooks/boundary.py`, registered in `.claude/settings.json`) reads every Bash
  command whole and **denies** raw network clients anywhere in it (`curl`, `wget`,
  `http`, `xh`, `nc`, …, inline python/node network calls, `/dev/tcp`), the operator
  surfaces `/simulate` and `/chaos` by any route, and destructive `git push` forms;
  it **allows** exactly the shapes an unattended shift needs (one `scripts/probe.sh`
  call, `git add journals/…`, `git commit -m "…"`); everything else takes the normal
  permission flow — settings rules, then a prompt — and an unattended shift fails
  closed on a prompt. The settings `allow`/`deny` lists stay as the belt (deny rules
  win over any hook allow). Tripwire: the second denial in a session freezes it —
  every further Bash call is denied and the agent is told to stop and page; a denied
  action is a signal to stop, never a puzzle to solve. Changing the hook, its pins, or
  either settings list is a SPEC-grade change (PR with rationale, never casual).
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

- Issue-driven: one branch per issue; the PR body links `Closes #N`. Trivial
  non-behavioral fixes may go direct to main.
- Unattended shift writes: an on-call session (`/oncall`) may write `journals/` and
  git-commit them on the current branch — those two forms are narrowly allowlisted in
  settings so an unattended investigation never blocks on a prompt. Pushing stays
  human. Widening either entry is SPEC-grade, like the probe allowlist.
- Quality gates: `uv run eval/tests.py` (scorer semantics pins) and
  `python3 hooks/tests.py` (boundary decision pins) must pass, the repo-review lens
  before merge, and docs ship with the change. The full corpus-in-CI
  gate (re-run scenarios on skill changes) lands with runner automation, post-v0.1;
  until then skill changes are validated by scoring real journals
  (`eval/README.md` → Scoring a run).
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
- `scripts/alert.sh "<summary>" [alertname] [severity]` — eval-side alert emitter:
  appends one contract-shaped complaint line to `alerts/inbox.jsonl` (the lab trigger
  profile, `docs/triggers.md`); prompts by design, like every operator action.
