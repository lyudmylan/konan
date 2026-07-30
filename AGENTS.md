# konan — repo agent instructions

Read `docs/product.md` for what konan is; this file is how to work here. The shared
AI-SDLC skills (`github-planning`, `github-shipping`, `repo-review`) apply; this file
overrides them where they conflict.

## Lab boundary (hard rule)

- The investigator touches a target only through `scripts/probe.sh` — GET-only,
  path-allowlisted, timeout-guarded — and by reading files under `lab/` (logs). Raw
  `curl`/`wget`/`http`/`xh`/`nc` are deny-listed in `.claude/settings.json` on purpose:
  the boundary is mechanical, not prompted. Changing either list is a SPEC-grade change
  (PR with rationale, never casual).
- `/simulate` and `/chaos` are outside the probe allowlist even though they are GETs:
  faultline serves mutating GETs there (crash, hang, ballast), and chaos state is
  operator surface, not telemetry.
- Scenario triggering is eval-side only (`scripts/scenario.sh`) and deliberately NOT
  pre-approved — it must permission-prompt in an interactive session.
- Never "fix" the lab: faultline's defects are its contract; its repo governs itself.
- Eval integrity: ground-truth defect details and scenario recipes stay out of
  investigator-readable docs in this repo (they live in faultline's SPEC and in eval
  fixtures). Investigations argue from telemetry only.

## Workflow

- Issue-driven: one branch per issue; the PR body links `Closes #N`. Trivial
  non-behavioral fixes may go direct to main.
- Quality gates: none automated yet — the eval harness (#11/#12) becomes the gate.
  Until then: the repo-review lens before merge, and docs ship with the change.
- Public-eventually: everything committed here — files, issue bodies, commit
  messages — must be publishable at the v0.1 flip.

## Commands

- `scripts/probe.sh /path[?query]` — read-only probe; trailer line carries HTTP status,
  duration, and the stamped request id (grep it in the logs to correlate).
