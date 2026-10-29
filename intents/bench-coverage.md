# Intent: the coverage line of the benchmark table

Work item: #76. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

A benchmark table that is short of its pre-registered plan says so on its face.

## In scope

- `eval/bench.py`: it reads the plan of a run from `plan.json` in the run directory — the fixture ids and the
  repetitions — or from an explicit `--plan`; never from the live `eval/scenarios/`, so a fixture added later
  does not turn an old table into a short one. It renders one coverage line per model: planned, completed,
  failed, missing. A missing count above zero appears at the head of the table, never only in a footnote, and the
  quota stops of `quota-stops.jsonl` that explain a gap are counted next to it, so the reader can tell "stopped
  by quota and not resumed" from "never scheduled".
- `eval/run.py`: writes `plan.json` at the first invocation of a run id, and stops with an error when a later
  invocation of the same run id names other fixtures or another repetition count: the plan is pre-registered.
  `eval/runs/bench-v1/plan.json` is backfilled by hand from the protocol (10 fixtures, N = 3).
- `eval/tests.py`: five pins. A run directory with 27 of 30 planned runs renders `missing 3` for that model.
  `eval/runs/bench-v1` renders `missing 0` for each of its three models. The quota stops of
  `quota-stops.jsonl` appear next to a missing count. A fixture added to `eval/scenarios/` leaves bench-v1 at
  `missing 0`. A second invocation of a run id with other fixtures or another repetition count exits non-zero
  and leaves `plan.json` unchanged.
- `eval/BENCHMARK.md`, section "Protocol": a table carries its coverage line; a table with a missing count
  above zero is not published as complete.

## Out of scope

The committed `eval/BENCHMARK-results.md` of bench-v1: it stays as published by this change, and #81 replaces
it with the bench-v2 table; the coverage line applies from bench-v2 on. The batching and resume rules of the runner: unchanged; the runner gains only the plan file. The
format of `results.jsonl` and of the sidecars: unchanged.

## Acceptance checks

## Automatic checks

1. A run directory that is short of its plan renders the missing count of that model at the head of the
   table.
   test: `eval/tests.py`, the pin "coverage, short plan". command: `uv run eval/tests.py`
2. The complete bench-v1 directory renders `missing 0` for each model.
   test: `eval/tests.py`, the pin "coverage, complete plan".
3. The quota stops that explain a gap appear next to the missing count.
   test: `eval/tests.py`, the pin "coverage, quota stops".
4. The plan comes from the run directory, not from the live fixtures: a fixture added to `eval/scenarios/`
   leaves bench-v1 at `missing 0`.
   test: `eval/tests.py`, the pin "coverage, plan source".
5. A second invocation of a run id with other fixtures or another `--repeat` exits non-zero and leaves
   `plan.json` unchanged.
   test: `eval/tests.py`, the pin "coverage, plan is pre-registered".
6. The protocol names the coverage line.
   command: `grep -q 'coverage line' eval/BENCHMARK.md`
7. The quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`

## Manual checks

None.
