# Intent: the two rounds on claude-fable-5-2 in the repository

Work item: #116. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The two rounds on `claude-fable-5-2` of 2026-11-15 are in the repository as they ran, and the protocol
document says what they are and what they do not claim.

## In scope

- `eval/runs/move-fable-5-2/`, the first round: 30 investigations at 8e62e4e, before the corrections of
  #90 and #110. Committed whole: the journals, the sidecars, `plan.json`, `results.jsonl`, and
  `scorecard.md` as the runner wrote it at its commit (16 of 30). The scorer of main reads the same journals
  as 28 of 30 since #90; the section of the protocol document states both numbers.
- `eval/runs/fable-5-2-round-2/`, the second round: 30 investigations at a07dad8, after both corrections,
  with `--effort high`. Committed whole, the same files (29 of 30).
- No file of a run changes on its way into the repository. The redaction rule of `eval/BENCHMARK.md` for
  archived runs holds: no file of the two folders carries a home-directory path. A file that carries one is
  redacted by that rule, and the change request names the file.
- `usage-readings.md` in each folder: the readings of the usage panel that the leader stated before and
  after each round.
- `eval/BENCHMARK.md`, one section for the two rounds:
  - the pins, the model, the effort level, the version of the harness, the dates;
  - the scores of each round, under the scorer of its commit and under the scorer of main;
  - the false-fail table of each round, one row for each failed run of its scorecard: 14 rows and 1 row;
  - the limits of each round. Both rounds: the sessions loaded instruction files and memory notes of the
    operator; the effort level was `high`, and bench-v2 ran at `xhigh`. The first round: the session context
    named the removed journals (#110), and no file of the round records the effort level. The second round:
    two investigations ran across a sleep of the computer, past the limit of 30 minutes by the clock, and
    the runner did not stop them;
  - one sentence that the two rounds are no part of the published table and support no comparison of
    models.

## Out of scope

The published table (`eval/BENCHMARK-results.md`, the README): bench-v2 stays the round it reports. A
comparison of models. Which instruction files and settings of the operator a run loads: a separate
decision, as in #110. A guard of the runner against a sleep of the computer. A repeat of a run. The
fixtures, the scorer, the runner.

## Acceptance checks

## Automatic checks

1. Each of the two run directories covers its plan: 30 planned, 30 completed, 0 missing.
   command: `test "$(uv run eval/bench.py --runs eval/runs/move-fable-5-2 eval/runs/fable-5-2-round-2 | grep -cE 'missing 0([^0-9]|$)')" = 2`
2. The committed journals of the second round reproduce its score under the scorer of main: 30 runs, none
   failed to complete, pass rate 97% (29 of 30).
   command: `uv run eval/bench.py --runs eval/runs/fable-5-2-round-2 | grep -qE '^\| all \| claude-fable-5-2 \| 30 \| 0 \| 97% '`
3. The committed journals of the first round give 93% (28 of 30) under the scorer of main.
   command: `uv run eval/bench.py --runs eval/runs/move-fable-5-2 | grep -qE '^\| all \| claude-fable-5-2 \| 30 \| 0 \| 93% '`
4. No file of the two folders carries a home-directory path.
   command: `! grep -rIqE '/Users/|/home/[a-z]' eval/runs/move-fable-5-2 eval/runs/fable-5-2-round-2`
5. The protocol document carries the section of the two rounds, as a heading, and the section carries the
   false-fail tables.
   command: `grep -qE '^#+ .*claude-fable-5-2' eval/BENCHMARK.md && grep -A200 -E '^#+ .*claude-fable-5-2' eval/BENCHMARK.md | grep -qi 'false-fail'`
6. The quality checks and the contract checks pass.
   command: `charter-gate quality --contract charter.toml && charter-check all charter.toml`

## Manual checks

7. The false-fail table of each round has one row for each failed run of its scorecard, and each row says
   whether the agent was wrong. who: drafted by the agent, reviewed by an agent that is not the author,
   confirmed by the leader. Not automatic: whether the agent was wrong is a reading.
8. The two investigations of the second round that ran across a sleep of the computer count as completed
   runs, and the section states the deviation. who: the leader. Not automatic: the protocol has no rule for
   a sleep, so it is a decision.
9. Each `usage-readings.md` carries the readings that the leader stated. who: the engineer records them,
   the leader reads them. Not automatic: a person reads the usage panel.
