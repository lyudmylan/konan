# Plan: the benchmark table renders whole (#93)

Intent: `intents/bench-table-cells.md`, checks 1-7.

## Steps

1. `eval/bench.py`: the status of a refused run is `unscorable: ` plus the first line of the scorer's
   message; a table cell escapes `|` (helper `_cell`, markdown only, `--json` keeps the raw status).
2. `eval/bench.py`: rename `quota_windows` to `quota_segments`; new title and text of the quota section;
   no "window" left in the file.
3. `eval/tests.py`: two pins in the coverage group, added to the runner list.
4. Run the changed generator over `eval/runs/bench-v2` into a temp file; copy only the quota section and
   the row of the refused run into `eval/BENCHMARK-results.md`. No other row changes.
5. `eval/BENCHMARK.md`: measure (a) of "Quota share" names the section and the weekly meter; the point
   "Table" of bench-v2 gets one sentence on #93.

## Files

- `eval/bench.py`, `eval/tests.py`, `eval/BENCHMARK-results.md`, `eval/BENCHMARK.md`, this plan.

## Tests

- `eval/tests.py`: `test_bench_table_status_is_one_line` (one row, 16 cells, `unscorable: `, `|` escape)
  and `test_bench_table_quota_section` (new title; no "window", no "5-hour").
