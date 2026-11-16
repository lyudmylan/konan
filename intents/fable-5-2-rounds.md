# Intent: the two rounds on claude-fable-5-2 in the repository

Work item: #116. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The two rounds on `claude-fable-5-2` of 2026-11-15 are in the repository as they ran, and the protocol
document says what they are and what they do not claim.

## In scope

- `eval/runs/move-fable-5-2/`, the first round: 30 investigations at 8e62e4e, before the corrections of
  #90 and #110. Committed whole: the journals, the sidecars, `plan.json`, `results.jsonl`, and
  `scorecard.md` as the runner wrote it at its commit. The scorer of main reads the same journals with the
  matchers of #90; the section of the protocol document states both scores.
- `eval/runs/fable-5-2-round-2/`, the second round: 30 investigations at a07dad8, after both corrections,
  with `--effort high`. Committed whole, the same files.
- No file of a run changes on its way into the repository, except the redaction of a home-directory prefix
  to `<checkout>` or `<home>` by the rule of `eval/BENCHMARK.md`; the change request names each redacted
  file. The claim surfaces, the evidence ids and the timestamps are untouched.
- `usage-readings.md` in each folder: the readings of the usage panel that the leader stated before and
  after each round.
- `eval/BENCHMARK.md`, one section for the two rounds, the last section of the file:
  - the pins, the model, the effort level, the version of the harness, the dates;
  - the scores of each round, under the scorer of its commit and under the scorer of main, as in checks 2
    to 4;
  - the false-fail table of each round, one row for each failed run of its scorecard, as in check 6. Each
    row starts with the run id of its round, and no other line of the document starts so;
  - the limits of each round. Both rounds: the sessions loaded instruction files and memory notes of the
    operator; the effort level was `high`, and bench-v2 ran at `xhigh`. The first round: the session context
    named the removed journals (#110), and no file of the round records the effort level. The second round:
    two investigations ran across a sleep of the computer, past the limit of 30 minutes by the clock, and
    the runner did not stop them;
  - one sentence with these words: the two rounds are "no part of the published table" and support "no
    comparison of models".

## Out of scope

The published table (`eval/BENCHMARK-results.md`, the README): bench-v2 stays the round it reports. A
comparison of models. Which instruction files and settings of the operator a run loads: a separate
decision, as in #110. A guard of the runner against a sleep of the computer. A repeat of a run. The
fixtures, the scorer, the runner.

## Acceptance checks

## Automatic checks

1. Each of the two run directories covers its plan: 30 planned, 30 completed, 0 missing.
   command: `test "$(uv run eval/bench.py --runs eval/runs/move-fable-5-2 eval/runs/fable-5-2-round-2 | grep -cE 'planned 30, completed 30, failed [0-9]+, missing 0([^0-9]|$)')" = 2`
2. The committed journals of the second round reproduce its score under the scorer of main: 30 runs, none
   failed to complete, pass rate 97% (29 of 30).
   command: `uv run eval/bench.py --runs eval/runs/fable-5-2-round-2 | grep -qE '^\| all \| claude-fable-5-2 \| 30 \| 0 \| 97% '`
3. The committed journals of the first round give 93% (28 of 30) under the scorer of main.
   command: `uv run eval/bench.py --runs eval/runs/move-fable-5-2 | grep -qE '^\| all \| claude-fable-5-2 \| 30 \| 0 \| 93% '`
4. The scorecard of the first round stays as the runner wrote it at its commit: 16 of 30.
   command: `grep -q 'Scenarios passed: 16/30' eval/runs/move-fable-5-2/scorecard.md`
5. No file of the two folders carries a home-directory path of macOS, Linux or Windows.
   command: `! grep -rIqE '/Users/|/home/[a-z]|/root/|[A-Za-z]:\\Users' eval/runs/move-fable-5-2 eval/runs/fable-5-2-round-2`
6. The protocol document carries the section of the two rounds, as a heading, and the section carries the
   false-fail tables: 14 rows for the first round and 1 row for the second.
   command: `s=$(awk '/^#+ .*claude-fable-5-2/{f=1;next} f&&/^## /{f=0} f' eval/BENCHMARK.md); echo "$s" | grep -qi 'false-fail' && test "$(grep -cE '^\| move-fable-5-2 \| ' eval/BENCHMARK.md)" = 14 && test "$(grep -cE '^\| fable-5-2-round-2 \| ' eval/BENCHMARK.md)" = 1`
7. The section states the sleep of the computer as a limit of the second round.
   command: `s=$(awk '/^#+ .*claude-fable-5-2/{f=1;next} f&&/^## /{f=0} f' eval/BENCHMARK.md); echo "$s" | grep -qi 'sleep'`
8. The section states the limits and what the rounds do not claim: the loaded instruction files of the
   operator, the effort level against the `xhigh` of bench-v2, and the sentence of the scope.
   command: `s=$(awk '/^#+ .*claude-fable-5-2/{f=1;next} f&&/^## /{f=0} f' eval/BENCHMARK.md); echo "$s" | grep -qi 'instruction files' && echo "$s" | grep -q 'xhigh' && echo "$s" | grep -q 'no part of the published table' && echo "$s" | grep -q 'no comparison of models'`
9. The quality checks and the contract checks pass.
   command: `charter-gate quality --contract charter.toml && charter-check all charter.toml`

## Manual checks

10. The false-fail table of each round has one row for each failed run of its scorecard, and each row says
    whether the agent was wrong. who: drafted by the agent, reviewed by an agent that is not the author,
    confirmed by the leader. Not automatic: whether the agent was wrong is a reading.
11. The two investigations of the second round that ran across a sleep of the computer count as completed
    runs. who: the leader. Not automatic: the protocol has no rule for a sleep, so it is a decision.
12. Each `usage-readings.md` carries the readings that the leader stated. who: the engineer records them,
    the leader reads them. Not automatic: a person reads the usage panel.
