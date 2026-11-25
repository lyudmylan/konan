# Intent: the benchmark table renders whole, and its quota section says what it measures

Work item: #93. Approval: a person merges the change request that adds this file.

## Goal

The table that `eval/bench.py` generates renders whole on the code host, and its quota section names the
limit that exists today.

## In scope

- Why: in the committed table of bench-v2, the row of the one run that the scorer refuses carries the
  message of the scorer over eight lines inside one cell, so the table "Every run" breaks at that row. The
  quota section says "a proxy for investigations per 5-hour window", and the provider dissolved that
  window before the round: the weekly meters are the only limit.
- `eval/bench.py`, the status of a run:
  - The status of a run that the scorer refuses is `unscorable: ` and the first line of the message of the
    scorer. The other lines of the message do not enter the table. The command `eval/score.py` over the
    journal prints the whole message.
  - Each status is one line in the table "Every run". A `|` in a status is written as `\|` in that table,
    so that a status never adds a cell. The escape belongs to the markdown table only: the `--json` output
    carries the same one-line status, with `|` not escaped.
- `eval/bench.py`, the quota section:
  - The title is "Quota: runs between quota stops (per model)".
  - The text says these things and no more: a quota stop is a stop of the runner at a limit of the
    subscription; the limits are the weekly meters; a segment is the count of runs before one stop, and the
    last number is the count of runs after the last stop; a line with no segment shows that no stop
    happened, and it measures no limit; the share of a weekly meter for one investigation comes from the
    usage readings of the operator (the protocol, measure (b) of "Quota share").
  - The word "window" leaves the file: the text, the comments, and the name of the function
    `quota_windows`, which becomes `quota_segments`.
  - The counts do not change: the same events make the same segments.
- `eval/tests.py`: two pins, in the group of the coverage pins.
  - A run directory with one journal whose frontmatter is not YAML renders a table "Every run" in which
    each row is one line with the 16 cells of the header, and the status of that run starts with
    `unscorable: `.
  - The quota section of a rendered table has the new title, and its text holds neither "window" nor
    "5-hour".
- `eval/BENCHMARK-results.md`, the committed table of bench-v2: the two parts get the repair, and no number
  changes.
  - The table is not generated again as a whole. The protocol says why: the committed table is the scoring
    as it was pre-registered, and the scorer of the main branch gives other rates for the same journals
    (87%, 87% and 83% in place of 77%, 63% and 73%). A table generated today would change the published
    rates.
  - The agent runs the changed generator into the temp folder
    (`uv run --offline --cache-dir .uv-cache eval/bench.py --runs eval/runs/bench-v2 -o <temp file>`) and
    copies two parts from that output into the committed table: the row of the run that the scorer refuses,
    and the quota section. These two parts do not depend on the version of the scorer.
- `eval/BENCHMARK.md`:
  - Section "What is measured", point "Quota share", measure (a): one sentence that names the section
    "Quota" of `eval/bench.py` and says that a stop is a stop at a weekly meter. It does not repeat the
    text of that section, so the rules of the section stand in one place, and the window is gone.
  - Section "Results - bench-v2", point "Table": one sentence that says that since #93 the committed table
    carries two repairs of its form (the status on one line, the words of the quota section) and that no
    number changed.

## Out of scope

- The scorer `eval/score.py`, and each pin of the scorer in `eval/tests.py`.
- Each number and each reading of the two results sections of `eval/BENCHMARK.md`. The lines of those
  sections that tell the history of the five-hour window stay as they are: they say what was true in their
  round.
- The table of the README, `eval/runs/bench-v2/usage-readings.md`, and the commands of the section
  "Reproduce".
- How the runner detects a quota stop and how the generator counts a segment.
- The files that the contract closes to a run: the fixtures in `eval/scenarios/` and the files of the rounds
  in `eval/runs/`. This work item needs no change there.

## Acceptance checks

## Automatic checks

1. A run that the scorer refuses is one row with 16 cells in the table "Every run", and its status starts
   with `unscorable: `.
   test: `eval/tests.py`, the pin "table, a status is one line".
2. The quota section of a rendered table has the title "Quota: runs between quota stops (per model)", and
   its text holds neither "window" nor "5-hour".
   test: `eval/tests.py`, the pin "table, the quota section".
3. The file of the generator holds the word "window" nowhere.
   command: `! grep -qi 'window' eval/bench.py`
4. The committed table carries the two repairs, as the changed generator prints them. The commands are
   chained with `&&`, so the block fails on the first difference or error. The lines outside the tables
   are equal to those of a table generated now; the row of the refused run is equal to the row generated
   now, it is one line, and it has 16 cells; from the title "Every run" to the end of the file, each line
   that is not empty is a row.
   command:
   ```
   D=$(mktemp -d) &&
   uv run --offline --cache-dir .uv-cache eval/bench.py --runs eval/runs/bench-v2 -o "$D/now.md" &&
   grep -v '^| ' eval/BENCHMARK-results.md > "$D/outside-committed" &&
   grep -v '^| ' "$D/now.md" > "$D/outside-now" &&
   diff "$D/outside-committed" "$D/outside-now" &&
   grep 'unscorable' eval/BENCHMARK-results.md > "$D/row-committed" &&
   grep 'unscorable' "$D/now.md" > "$D/row-now" &&
   diff "$D/row-committed" "$D/row-now" &&
   test "$(wc -l < "$D/row-committed")" -eq 1 &&
   awk -F'|' 'NF != 18 { bad = 1 } END { exit bad }' "$D/row-committed" &&
   awk '/^## Every run/ { on = 1; next } on && NF && !/^[|] .* [|]$/ { bad = 1 } END { exit bad }' eval/BENCHMARK-results.md
   ```
5. No number of the committed table changed: each row of its tables, apart from the row of the refused run,
   is equal to the same row on the main branch at the commit f64d9f6. The command compares the hash of
   those rows with the hash of the same rows at that commit.
   command: `test "$(grep '^| ' eval/BENCHMARK-results.md | grep -v 'unscorable' | shasum -a 256 | cut -d' ' -f1)" = 9ef7348e9633ac4db96d3a303904431af022e95aecb7bfb69d8f4c0557943537`
6. The protocol names the window only where it tells the history of a round: "5-hour" stands once in
   `eval/BENCHMARK.md` (in the results of bench-v1), and the point "Table" of the results of bench-v2 names
   this work item.
   command: `test "$(grep -c '5-hour' eval/BENCHMARK.md)" -eq 1 && grep -q '#93' eval/BENCHMARK.md`
7. The quality checks of the contract pass.
   command: `charter-gate quality --contract charter.toml`

This work item does not change the behaviour of the product: it changes a script of the eval and two
documents. The contract names no product test.

## Manual checks

8. On the code host, the page of `eval/BENCHMARK-results.md` on the branch of the change request shows the
   table "Every run" whole, with the refused run as one row. who: the engineer. Not automatic: no command
   of this repo renders a page of the code host.
