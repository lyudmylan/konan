# Intent: the benchmark re-run

Work item: #81. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The benchmark table carries a model result for every tier, or states for a tier why it carries no claim, from
runs that a corrected corpus scores.

## In scope

- The gate before the first run: #75, #76, #77, and #78 merged on main; `uv run eval/tests.py` green; the
  pin commit recorded in `eval/BENCHMARK.md` before the batch starts; and the go of the leader after the
  pre-run review in the conversation (manual check 8). The batch never starts unattended.
- The plan, pre-registered here: the 10 fixtures × 3 models × N = 3 = 90 runs under the run id `bench-v2`.
  The protocol of `eval/BENCHMARK.md` is unchanged: fixed inputs, blinding, a fresh lab per run, batches by
  quota window, a failed run counts and is not retried, a quota stop is retried.
- The pinned paths of the round, named once here: `skills/investigate` (the report contract and the journal
  schema are inside it), `skills/konan`, `skills/oncall`, `hooks/boundary.py`, `eval/score.py`,
  `eval/scenarios/`, `eval/fixture.schema.json`. None of them changes between the first and the last run; a
  change restarts the round under a new run id. `eval/run.py` and `eval/bench.py` are not pinned: their
  changes precede the first run.
- Models: the three of bench-v1 (`claude-fable-5`, `claude-opus-5`, `claude-sonnet-5`) when their ids still
  run, so the tier-3 delta measures the fixture fix and not a model change. When an id does not run, the
  current model of the same tier replaces it and the results section names the substitution.
- Two items from the review of 2026-10-28 against the lessons of the evals course, before the first run:
  `eval/run.py` names its temporary worktree neutrally — neither "eval" nor the run id in the path the model
  sees — a runner-only change; and the `bench-v2` results section carries a false-fail table: date, scenario,
  what failed, whether the agent was wrong, the fix.
- Deliverables: `eval/runs/bench-v2/` committed whole (journals, sidecars, `results.jsonl`,
  `quota-stops.jsonl`, `scorecard.md`); `eval/BENCHMARK-results.md` regenerated from it, with the coverage
  line of #76; a `bench-v2` results section in `eval/BENCHMARK.md` (pin, dates, coverage, the quota measures
  of the protocol, the false-fail table, the tier-3 result, the diff against bench-v1); the README table
  replaced and its tier-3 caveat removed; the v0.2 status line of `docs/product.md` updated.

## Out of scope

Role-tiered configurations (#65). New fixtures. Models beyond the three. The model-run half of the CI gate
(#60). Re-scoring bench-v1 under the new semantics. The origin post and the flip (#13). The other gaps of the
review of 2026-10-28 — a process column, an injection scenario, a judge with an enforced empty tool list,
the triage experiment (#26) — stay on the roadmap or come after the flip.

## Acceptance checks

## Automatic checks

1. The run directory covers the plan: `missing 0` on each of the three coverage lines (30 runs per model,
   completed or failed; a failed run is reported, not retried).
   command: `test "$(uv run eval/bench.py --runs eval/runs/bench-v2 | grep -cE 'missing 0([^0-9]|$)')" = 3`
2. The committed table reproduces from the committed runs.
   command: `uv run eval/bench.py --runs eval/runs/bench-v2 -o eval/BENCHMARK-results.md && git diff --quiet -- eval/BENCHMARK-results.md`
3. The pinned paths of the scope did not change across the round. The results section records both commits
   as `first-run: <sha>` and `last-run: <sha>`; the command reads them from there.
   command: `git diff --quiet $(grep -oE 'first-run: [0-9a-f]+' eval/BENCHMARK.md | tail -1 | cut -d' ' -f2) $(grep -oE 'last-run: [0-9a-f]+' eval/BENCHMARK.md | tail -1 | cut -d' ' -f2) -- skills/investigate skills/konan skills/oncall hooks/boundary.py eval/score.py eval/scenarios eval/fixture.schema.json`
4. The README and the protocol carry the round, and the tier-3 caveat is gone from the README.
   command: `grep -q bench-v2 README.md && grep -q bench-v2 eval/BENCHMARK.md && ! grep -q 'tier-3 fixtures are not yet' README.md`
5. The worktree path hides the round from the model: the path the runner builds for a worktree carries
   neither `eval` nor the run id, whatever call builds it.
   test: `eval/tests.py`, the pin "neutral worktree". command: `uv run eval/tests.py`
6. The results section carries the false-fail table.
   command: `grep -qi 'false-fail' eval/BENCHMARK.md`
7. The quality checks of the contract pass at the pin. command: `charter-gate quality --contract charter.toml`

## Manual checks

8. Before the first batch, the leader reviews in the conversation and gives the go: the pin commit, the model
   ids that answered (check 9), the quota plan for the week (runs per window per model, and what else the
   pool must serve), and the two items of the review. who: the leader. Not automatic: it is the stop point the
   leader set on 2026-10-28; a batch that starts without it is a protocol breach, and the round restarts.
9. Before the first batch, each model id answers one headless call, and the results section records the
   ids that ran. who: the engineer. Not automatic: it calls the model on the subscription.
10. The tier-3 rows differ by model, or the results section states which artifact remains and the tier
    carries no claim again. who: the leader. Not automatic: it is a reading of what the number measures, not a
    comparison.
11. The quota measures of the protocol — runs between quota stops, and the usage-panel deltas per model — are
    recorded in the results section. who: the engineer. Not automatic: the usage panel is read by a person.
12. The false-fail table has one row per failed scenario of `eval/runs/bench-v2/scorecard.md`, with the
    columns of the scope. who: the leader. Not automatic: whether the agent was wrong is a reading.
