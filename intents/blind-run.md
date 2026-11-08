# Intent: the blind run on the Grafana Cloud adapter

Work item: #55. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

One blind investigation of the D1 scenario, in a fresh session that reads Grafana Cloud through the adapter
and nothing else, whose committed journal passes the D1 fixture under the deterministic scorer and is
linked from the README as the real-stack receipt.

## In scope

- The form of the run: the runner's recipe by hand, with the adapter (the "Manual runs" paragraph of
  `eval/README.md`). A detached git worktree of `main` whose directory name carries no `eval` (the blind
  rule of the hook matches the word inside a path); `journals/` emptied in the worktree (no incident
  memory: the smoke journal of 2026-11-08 investigates the same defect); `KONAN_EVAL_BLIND=1` (the hook's
  blind mode, mechanical); `KONAN_ADAPTER=docs/adapters/grafana-cloud.md`; the two credentials of the
  adapter in the environment; and one headless session, run by the agent's session with a 30-minute
  timeout, with the command the plan's step 4 gives (the fixture's complaint verbatim after `/konan`).
  A headless session fails closed on a tool outside the allowlist, so the adapter's boundary holds without
  a prompt; `acceptEdits` lets the investigator write its journal, as the runner does. The model is the
  one of the smoke run, `claude-fable-5-1`, and the journal's `usage.model` records it.
- The staging, eval-side, in the main checkout where the lab runs and Alloy tails: the fixture's
  `setup.lab: fresh` (the lab stopped, `lab/logs` deleted, the lab started), then its `stage` list, command
  by command, with `scripts/scenario.sh` (unstamped user traffic). Alloy keeps tailing the new log file.
  The plane also holds the earlier traffic of the same defect (2026-11-04 and 2026-11-08); the investigator
  may read it as history. The investigator never sees the staging.
- The receipts. The journal, copied from the worktree to `journals/<date>-<slug>.md` under the name the
  investigator gave it (when that name is the smoke journal's, `2026-11-08-product-page-500s.md`, the
  blind journal is renamed `<date>-<slug>-blind.md` before the copy; the smoke journal is never
  overwritten), with `usage.tokens` stamped from the envelope's `modelUsage` total (the runner's
  definition: every category, subagents included) and `usage.model` as reported. The envelope's kept
  fields as `eval/runs/2026-11-blind-grafana/d1-zero-stock-product-page-r1.meta.json` (the runner's
  fields: session id, turns, durations, cost, tokens per model, permission denials). The scorecard
  `eval/runs/2026-11-blind-grafana/scorecard.md` from `eval/score.py` with one pair, the D1 fixture and
  the journal. The hook's denial count of the session, in the change request.
- `README.md`, "Measured before believed": one sentence that links the journal and its scorecard as the
  real-stack receipt, the D1 defect found through Grafana Cloud queries only.
- The tracker: #55 closes with the change request; epic #58 closes with a comment that names what it
  delivered, as #55 is its last child.
- A calibration before the run, not committed: the smoke journal of the adapter, scored against the D1
  fixture, passes 1/1 (run on 2026-11-08; the matchers hit the claim surface of an adapter journal). The
  record is in the change request.

## Out of scope

The plumbing of `--mcp-config` and `KONAN_ADAPTER` into `eval/run.py`: a code change to the runner and its
tests, and the runner restarts the lab inside its own worktree, where Alloy does not tail; it is a later
work item, noted on #58. More scenarios on this adapter (after v0.2). Any change to the D1 fixture or the
scorer: when the blind journal fails a matcher, the failure is the result, recorded, not tuned away.
`eval/scorecard.md`, the corpus-v1 regression gate, is unchanged; this run lives under `eval/runs/`. The
investigate skill, the adapter document, the allowlist, the hook. Sentry.

## Acceptance checks

When the journal fails a matcher or its verdict differs from the fixture, checks 2 to 4 are replaced by one
record in the change request: the scorecard as it came out, committed under `eval/runs/2026-11-blind-grafana/`,
and the leader decides what the receipt is; the README sentence waits for that decision.

### Automatic checks

The selector of the blind journal is written out in each of checks 1 to 4, so that every command runs on
its own.

1. The blind journal is committed, names the adapter as its surface contract, cites plane queries, cites
   no lab file, and is the one journal under this adapter besides the smoke journal. A journal that
   mentions a lab path in prose fails this check too, and the leader judges it.
   command: `f=$(grep -l 'surface_contract: docs/adapters/grafana-cloud.md' journals/*.md | grep -v '^journals/2026-11-08-product-page-500s.md$') && test "$(printf '%s\n' "$f" | wc -l | tr -d ' ')" -eq 1 && grep -Eq 'query_prometheus|query_loki' "$f" && ! grep -Eq '(^|[^a-z])lab/|probe\.sh|docs/lab\.md' "$f"`
2. The journal passes the D1 fixture under the scorer, and the committed scorecard and sidecar exist.
   command: `f=$(grep -l 'surface_contract: docs/adapters/grafana-cloud.md' journals/*.md | grep -v '^journals/2026-11-08-product-page-500s.md$') && uv run eval/score.py --pair eval/scenarios/d1-zero-stock-product-page.yaml "$f" >/dev/null && grep -q 'Scenarios passed: 1/1' eval/runs/2026-11-blind-grafana/scorecard.md && test -f eval/runs/2026-11-blind-grafana/d1-zero-stock-product-page-r1.meta.json`
3. The tokens are recorded: the journal's `usage.tokens` is the sidecar's total, a number.
   command: `f=$(grep -l 'surface_contract: docs/adapters/grafana-cloud.md' journals/*.md | grep -v '^journals/2026-11-08-product-page-500s.md$') && t=$(jq -r .tokens_total eval/runs/2026-11-blind-grafana/d1-zero-stock-product-page-r1.meta.json) && test "$t" != null && grep -q "^  tokens: $t$" "$f"`
4. The README links the journal and the scorecard.
   command: `f=$(grep -l 'surface_contract: docs/adapters/grafana-cloud.md' journals/*.md | grep -v '^journals/2026-11-08-product-page-500s.md$') && grep -q "$f" README.md && grep -q 'eval/runs/2026-11-blind-grafana/scorecard.md' README.md`
5. The quality checks and the contract checks pass.
   command: `charter-gate quality --contract charter.toml && charter-check all charter.toml`

### Manual checks

6. The blinding held: the session ran in a worktree whose `journals/` was empty, with `KONAN_EVAL_BLIND=1`;
   the hook's state file of that session shows its denial count, zero or each denial named; and the
   session's tool-use list (the transcript of the headless session and of its agents, which the harness
   keeps outside the repository under the session id of the envelope) shows no Read, Grep, Glob or Bash
   call on `lab/` or on the probe script. The change request records all three. who: the agent writes the
   record, the leader reads it. Not automatic: the state file and the transcripts live outside the
   repository, and the mechanical exclusion of the lab under an adapter is a later work item (the #58
   decision of 2026-11-08).
7. The staging ran as the fixture says, after a fresh lab, with Alloy reporting no error, and before the
   session started; the change request records the timestamps of the staging and of the session's start.
   who: the agent writes the record, the leader reads it. Not automatic: the lab and Alloy run outside the
   repository.
