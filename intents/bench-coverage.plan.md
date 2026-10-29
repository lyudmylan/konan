# Plan: the coverage line of the benchmark table (#76)

Intent: `intents/bench-coverage.md`. Written 2026-10-29; the code starts after the leader accepts it in the
conversation.

## Steps

1. `eval/run.py`: one function, `register_plan(out, fixture_ids, repeat)`. At the first invocation of a run
   id it writes `<out>/plan.json`: the run id, the scenario ids in sorted order, the repetition count, and
   the time. At a later invocation it reads the file and compares the two lists and the count; a difference
   stops the runner with a message that names both plans and says the plan is pre-registered (exit code 1,
   the file untouched). `main()` calls it right after it computes the output directory, before the todo list.
   A dry run compares but writes nothing: a preview does not pre-register a plan. The batching, the resume
   rule, `results.jsonl`, the sidecars, and `quota-stops.jsonl` do not change. The docstring names the plan
   file.
2. `eval/bench.py`: the option `--plan <file>`; `load_plan(run_dir, explicit)` reads `plan.json` of the run
   directory, or the explicit file for every run directory given; a run directory without a plan and no
   `--plan` is an error that names the missing file. The aggregator never reads the plan from the live
   `eval/scenarios/`. `coverage(rows, plan, run_dir)` gives one record per (run, model): planned = fixtures ×
   repetitions; completed = rows with status ok; failed = the other rows (a quota stop is not a row: `collect`
   drops it today and keeps doing so); missing = the planned (scenario, repetition) pairs without a row; of
   the missing pairs, those with an entry in `quota-stops.jsonl` are "stopped by quota and not resumed", the
   rest "never scheduled"; pairs with a row outside the plan are counted apart and reported, not scored into
   the plan. Both this count and the missing-plan error are held by the pin of check 1. `render` writes, directly under the title and before every table: "Coverage: complete, 90 of 90
   planned runs." or "**Incomplete: 3 of 90 planned runs are missing** (claude-x: 3)."; then a section
   "## Coverage" with one line per (run, model):
   `- bench-v1 claude-sonnet-5: planned 30, completed 24, failed 6, missing 0`, and when missing is above
   zero: `missing 3 (2 stopped by quota and not resumed, 1 never scheduled)`. The words `missing <n>` appear
   on the per-model lines only, so check 1 of `intents/bench-v2-rerun.md` (the `grep -cE 'missing 0([^0-9]|$)'` count equals the
   number of models) reads them and nothing else.
3. `eval/runs/bench-v1/plan.json`, backfilled by hand from the protocol: the ten scenario ids, repeat 3, and
   `"backfilled": true` with the source (protocol items 2 and 3, the results section). The committed
   `eval/BENCHMARK-results.md` is not regenerated: it stays as published; #81 replaces it.
4. `eval/tests.py`: `import bench`; five functions after the runner pins, run from `__main__`, closing line
   `OK: 5 coverage pins hold`. Each cites its check of the intent:
   - `test_bench_coverage_short_plan` (check 1): a temporary run directory with a plan of the ten ids × 3 and
     27 synthetic sidecars of one model (status ok); the rendered text carries "Incomplete: 3 of 30" at its
     head and `missing 3` on the model line. A run directory without a plan is an error, and a sidecar
     outside the plan (a fourth repetition) is counted apart, `1 outside the plan`, not as completed or failed.
   - `test_bench_coverage_complete_plan` (check 2): `eval/runs/bench-v1` renders three lines with `missing 0`,
     one per model, and the Sonnet line says `failed 6`.
   - `test_bench_coverage_quota_stops` (check 3): the directory of check 1 plus a `quota-stops.jsonl` with
     stops for two of the three missing pairs, one of them twice (the backfill of bench-v1 has duplicates),
     and one quota-only sidecar: the line says `missing 3 (2 stopped by quota and not resumed, 1 never
     scheduled)`; the quota sidecar is not a run.
   - `test_bench_coverage_plan_source` (check 4): a copy of `eval/scenarios/` with an eleventh file,
     `zz-added-later.yaml`; `bench.SCEN` points at the copy while `bench.build`, the function `main()`
     renders through, runs on bench-v1: `load_fixtures` returns eleven, and the table still renders
     `missing 0` three times, because the coverage reads the plan file. The committed directory is not
     touched.
   - `test_bench_coverage_plan_is_pre_registered` (check 5): `runner.register_plan` on a temporary directory
     writes the file; a second call with another repeat, and a third with one id fewer, each raise
     `SystemExit` with a non-zero code and leave the file byte-identical; a fourth call with the same plan
     passes and leaves it unchanged; a fifth call with `dry_run=True` on an empty directory leaves no
     `plan.json`: a preview registers nothing.
   The 18 semantics pins and the 4 runner pins do not change.
5. `eval/BENCHMARK.md`: protocol item 10, "Coverage.", after item 9: the runner pre-registers the plan of a
   run id in `plan.json` at the first invocation and refuses another plan under the same id; the table
   carries its coverage line per model — planned, completed, failed, missing, with the quota stops that
   explain a gap — at its head; a table with a missing count above zero is not published as complete
   (check 6 greps "coverage line"). In "Reproduce", the comment "until `results.jsonl` covers the plan"
   becomes "until the coverage line says missing 0". The results section of bench-v1 does not change.
6. The two commands of `AGENTS.md`, then the seven checks of the intent: five by `uv run eval/tests.py`, then the two
   commands (6, 7). One change request,
   `Closes #76`, on this branch. No file under a code path changes.

## Files

`eval/run.py`, `eval/bench.py`, `eval/runs/bench-v1/plan.json` (new), `eval/tests.py`, `eval/BENCHMARK.md`,
and this file.

## Tests

The five coverage pins of step 4. Pin 16 keeps loading every fixture; the runner pins keep their four cases.

## Facts the plan rests on (as of this plan, 2026-10-29)

- `eval/scenarios/` holds ten fixtures; bench-v1 ran each three times per model: 30 sidecars per model, 90 in
  all, none of them a quota stop (the retries overwrote those sidecars; the stops live in `quota-stops.jsonl`,
  70 lines with duplicates from the backfill, so the coverage counts distinct (model, scenario, repetition)
  pairs). Sonnet has 24 journals and 6 failed runs, Fable and Opus 30 journals each.
- The runner takes one model per invocation, so the plan file carries fixtures and repetitions, not models:
  a model that was never started has no directory and no coverage line. The models of a round are named by
  the protocol and checked by hand (#81).
- `collect` in `eval/bench.py` drops a sidecar with `quota_error` and reads the rest; `quota_windows` reads
  `quota-stops.jsonl`; `render` reads the run directories from a module global; `build` is the one path from the run
  directories to the markdown, for `main()` and for the pins. The coverage follows the same inputs and adds
  no new file format.
