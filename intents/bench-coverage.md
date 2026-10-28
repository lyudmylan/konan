# Intent: the coverage line of the benchmark table

Work item: #76. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

A benchmark table that is short of its pre-registered plan says so on its face.

## In scope

- `eval/bench.py`: it learns the plan of a run — the fixture count times the repetitions (`--repeat`,
  default 3), or an explicit `--plan`. It renders one coverage line per model: planned, completed, failed,
  missing. A missing count above zero appears at the head of the table, never only in a footnote, and the
  quota stops of `quota-stops.jsonl` that explain a gap are counted next to it, so the reader can tell "stopped
  by quota and not resumed" from "never scheduled".
- `eval/tests.py`: two pins. A run directory with 27 of 30 planned runs renders `missing 3` for that model.
  `eval/runs/bench-v1` renders `missing 0` for each of its three models.
- `eval/BENCHMARK.md`, section "Protocol": a table carries its coverage line; a table with a missing count
  above zero is not published as complete.

## Out of scope

The committed `eval/BENCHMARK-results.md` of bench-v1: it stays as published; the coverage line applies from
bench-v2 on. The batching and resume rules of the runner (`eval/run.py`): unchanged. The format of
`results.jsonl` and of the sidecars: unchanged.

## Acceptance checks

## Automatic checks

1. A run directory that is short of its plan renders the missing count of that model at the head of the
   table.
   test: `eval/tests.py`, the pin "coverage, short plan". command: `uv run eval/tests.py`
2. The complete bench-v1 directory renders `missing 0` for each model.
   test: `eval/tests.py`, the pin "coverage, complete plan".
3. The quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`

## Manual checks

None.
