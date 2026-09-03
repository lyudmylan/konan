---
name: setup
description: "Use to onboard into konan on this machine — /setup: check prerequisites, wire the faultline lab, run a first investigation, and score it. Agent-run; the few manual steps are named and nothing else is manual."
---

# setup — agent-run onboarding

You are onboarding a new operator. Do the work yourself; ask before anything that
creates or downloads; stop with exact instructions when a prerequisite is missing.
The operator's manual steps are, by policy, only these: installing Claude Code,
cloning this repo, trusting the workspace, and approving operator-surface prompts
(lab start, scenario staging). Everything else is yours.

## 1. Prerequisites — check, never assume

Run the checks; report a single table of pass/fail:

- `claude --version` — any current version (this session running proves it).
- `git --version` — 2.x.
- `uv --version` — needed by the lab and the eval scorer. Missing → tell the
  operator exactly: `brew install uv` (macOS) or the installer at
  https://docs.astral.sh/uv/getting-started/installation/ — and stop.
- `python3 --version` — 3.11+ (the boundary hook and scorer use it).

## 2. The lab (faultline)

1. Locate it: `$FAULTLINE_DIR` if set, else `../faultline` beside this repo.
2. Absent → ask: "Clone faultline beside this repo?" On yes:
   `git clone https://github.com/lyudmylan/faultline ../faultline`. On no: ask
   where it lives and tell the operator to set `FAULTLINE_DIR`.
3. Start it: `scripts/lab.sh start` — this prompts; that is by design (operator
   surface). Then verify through the boundary: `scripts/probe.sh /health` — expect
   HTTP 200 and a `request_id=konan-…` trailer.

## 3. First investigation (demo run, not an eval run)

Say what is about to happen in two lines: konan investigates read-only through an
allowlisted probe; a content-based hook denies everything else; "no incident" is a
legitimate verdict.

Then run the investigate loop via the manual trigger skill with exactly this
complaint: `/konan Routine check: is the shop service healthy right now? No user
reports.` Let it conclude.

## 4. Read the result together

- Open the newest `journals/*.md`. Explain the machine core in four lines: the
  verdict; hypotheses with judge states; the evidence ledger (no citation, no
  claim — schema-enforced); gaps and usage.
- Note: on this lab a competent investigator usually finds the seeded defects as
  **latent findings** even when healthy — that is the observer-effect rule working,
  not a false alarm.

## 5. Score it

`uv run eval/score.py --pair eval/scenarios/healthy-baseline.yaml journals/<file>.md`

Expect 1/1 when the verdict is no-active-incident. A different verdict is not a
setup failure — read the journal; the lab may genuinely have an active condition
(say so, and point at `docs/lab.md` for the eval-side controls). Make clear this
demo was watched, not blind — eval runs use `eval/run.py` (blinded; `eval/README.md`).

## 6. Hand over

Close with the map, one line each: `/konan <complaint>` — investigate now;
`/oncall` — take a shift (alert inbox + Monitor); `docs/product.md` — what konan
is; `docs/lab.md` — the lab contract; `eval/README.md` — evals and blinding;
`AGENTS.md` — the boundary and the rules. Stop the lab if the operator is done:
`scripts/lab.sh stop`.

Boundaries: this skill installs nothing global, edits nothing outside the repo, and
never touches `/simulate` or `/chaos` — staging scenarios is a deliberate operator
act (`scripts/scenario.sh`, prompts by design).
