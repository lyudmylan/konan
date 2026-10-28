# Intent: the benchmark re-run

Work item: #81. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The benchmark table carries a model result for every tier, tier 3 included, from runs that a corrected corpus
scores.

## In scope

- The gate before the first run: #75, #76, #77, and #78 merged on main; `uv run eval/tests.py` green; the
  pin commit recorded in `eval/BENCHMARK.md` before the batch starts.
- The plan, pre-registered here: the 10 fixtures × 3 models × N = 3 = 90 runs under the run id `bench-v2`.
  The protocol of `eval/BENCHMARK.md` is unchanged: fixed inputs, blinding, a fresh lab per run, batches by
  quota window, a failed run counts and is not retried, a quota stop is retried.
- The pinned paths of the round: `skills/investigate`, `skills/konan`, `skills/oncall`, `hooks/boundary.py`,
  `eval/score.py`, `eval/scenarios/`, `eval/fixture.schema.json`, `skills/investigate/journal.schema.json`.
  None of them changes between the first and the last run; a change restarts the round under a new run id.
- Models: the three of bench-v1 (`claude-fable-5`, `claude-opus-5`, `claude-sonnet-5`) when their ids still
  run, so the tier-3 delta measures the fixture fix and not a model change. When an id does not run, the
  current model of the same tier replaces it and the results section names the substitution.
- Deliverables: `eval/runs/bench-v2/` committed whole (journals, sidecars, `results.jsonl`,
  `quota-stops.jsonl`, `scorecard.md`); `eval/BENCHMARK-results.md` regenerated from it, with the coverage
  line of #76; a `bench-v2` results section in `eval/BENCHMARK.md` (pin, dates, coverage, the quota measures
  of the protocol, the tier-3 result, the diff against bench-v1); the README table replaced and its tier-3
  caveat removed; the v0.2 status line of `docs/product.md` updated.

## Out of scope

Role-tiered configurations (#65). New fixtures. Models beyond the three. The model-run half of the CI gate
(#60). Re-scoring bench-v1 under the new semantics. The origin post and the flip (#13).

## Acceptance checks

## Automatic checks

1. The run directory covers the plan: 30 completed runs per model, `missing 0` on each of the three coverage
   lines.
   command: `test "$(uv run eval/bench.py --runs eval/runs/bench-v2 | grep -c 'missing 0')" = 3`
2. The committed table reproduces from the committed runs.
   command: `uv run eval/bench.py --runs eval/runs/bench-v2 -o eval/BENCHMARK-results.md && git diff --quiet -- eval/BENCHMARK-results.md`
3. The pinned paths did not change across the round. The two commits are the ones the results section
   names as the first and the last run.
   command: `git diff --quiet <first-run commit> <last-run commit> -- skills/investigate skills/konan skills/oncall hooks/boundary.py eval/score.py eval/scenarios eval/fixture.schema.json`
4. The README and the protocol carry the round, and the tier-3 caveat is gone from the README.
   command: `grep -q bench-v2 README.md && grep -q bench-v2 eval/BENCHMARK.md && ! grep -q 'tier-3 fixtures are not yet' README.md`
5. The quality checks of the contract pass at the pin. command: `charter-gate quality --contract charter.toml`

## Manual checks

6. Before the first batch, each model id answers one headless call, and the results section records the
   ids that ran. who: the engineer. Not automatic: it calls the model on the subscription.
7. The tier-3 rows differ by model, or the results section states which artifact remains and the tier
   carries no claim again. who: the leader. Not automatic: it is a reading of what the number measures, not a
   comparison.
8. The quota measures of the protocol — runs between quota stops, and the usage-panel deltas per model — are
   recorded in the results section. who: the engineer. Not automatic: the usage panel is read by a person.
