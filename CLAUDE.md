# Claude Code instructions

Read `AGENTS.md` first — it is how to work in this repo (lab boundary, workflow,
commands).

`docs/product.md` is the product source of truth — ground planning and scope decisions
in it. The shared AI-SDLC skills (`github-planning`, `github-shipping`, `repo-review`)
apply here.

Rules that matter in this repo:

- konan touches investigation targets **read-only**; only the eval harness may trigger
  scenarios (see the lab boundary in product.md).
- No custom loop or orchestration code — harness primitives only (architecture stance in
  product.md).
- The repo is private until v0.1; artifact-first publishing policy applies (product.md).
