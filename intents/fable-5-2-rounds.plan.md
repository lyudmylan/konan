# Plan: the two rounds on claude-fable-5-2 in the repository (#116)

Intent: `intents/fable-5-2-rounds.md`. Written 2026-11-16. Accepted by the leader in the conversation on
2026-11-16.

## Steps

1. The first round. Copy the directory of the run id `move-fable-5-2` from the working tree of the
   operator, where the runner wrote it, to `eval/runs/move-fable-5-2/`: 30 journals, 30 sidecars,
   `plan.json`, `results.jsonl`, `scorecard.md`. A recursive comparison of the source and the copy shows no
   difference. One commit.
2. The second round. The same for `fable-5-2-round-2`. One commit.
3. The redaction. The command of check 5 runs on both folders. The scan of 2026-11-16 found no
   home-directory path, no mail address and no token in the 126 files, so no file is redacted, and the
   change request says so. The temporary path of the working copy of a run stays, as in the rounds on
   record.
4. `usage-readings.md` in each folder, in the form of the file of bench-v2: the date, the moment, the runs
   so far, the two meters, and what else ran on the same meters between two readings. A deviation from
   the wording of the intent, "before and after each round": the first round has no reading right after
   its last batch; the file says so and gives the next reading on record.
5. `eval/BENCHMARK.md`, a new last section, `## Rounds on claude-fable-5-2 (2026-11-15)`:
   - What the rounds are: the pins (8e62e4e and a07dad8), the model, the effort level, the version of the
     harness, the dates. For the second round the files record the level. For the first round no file
     records it, and the level rests on the session records of the operator.
   - The scores, one table. Its rows start with "First round" and "Second round", not with a run id: the
     score under the scorer of its commit, the score under the scorer of main, the false attributions, and
     the medians that `eval/bench.py` prints.
   - `### False-fail tables`. The columns of the table of bench-v2, with the run id as a first column: run
     id, date, scenario and repetition, what failed, was the agent wrong, the fix. 14 rows start with
     `| move-fable-5-2 | `: 12 with "No" (the matcher `switch-flipped` and its like; the fix is #90,
     merged) and 2 with "Yes" (the suggestive complaint, repetitions 1 and 3). 1 row starts with
     `| fable-5-2-round-2 | `: "Yes" (the suggestive complaint, repetition 1). The table lines start at the
     first column of the file, so that the commands of check 6 count them.
   - `### Limits`. Both rounds: the instruction files and the memory notes of the operator that the
     sessions loaded, with the counts from the session records; the effort level `high` against the `xhigh`
     of bench-v2. The first round: the names of the removed journals in the session context (#110), one
     session that read an earlier journal through the history, and no file that records the effort level.
     The second round: the two investigations across a sleep of the computer, with their clock time and
     their active time, the turns that the harness added, and the runner that did not stop them; the wall
     clock values of these two runs are not usable.
   - The two phrases of the scope, each whole on one line of the file: the two rounds are no part of the
     published table, and they support no comparison of models.
6. The two low findings of the last review of the intent are met in the text and not in the commands: the
   limits name #110, and no line outside the section starts with a run id. The intent does not change.
7. The session records behind the counts of step 5 are outside the repository. I counted again for both
   rounds before I wrote the limits (instruction files, memory notes, journal names, the read through the
   history), and the change request carries the counts.
8. No code changes. `uv run eval/tests.py` and `python3 hooks/tests.py` run as the quality checks. Then the
   commands of checks 1 to 9 of the intent, by hand; the change request records each result. It also
   records the scorecard line of the second round and the lines of `eval/bench.py` that the scores table
   was read from.
9. Manual check 10. The readings exist: the 14 rows were drafted on 2026-11-15 and the 1 row on 2026-11-16,
   and each set was read by two agents that are not the author, one without the draft and one against it.
   Both agreed with every row. The change request carries the heading `## Disagreements` with that
   result. The leader confirms the rows in the conversation or with the merge.
10. Manual check 11. The leader decided in the conversation on 2026-11-16 that the two investigations
    across the sleep count as completed runs. The section states the decision and the strict reading, 27
    of 30.
11. `/code-review` on the branch, then the two commands of `AGENTS.md`, then one change request,
    `Closes #116`. The review loop runs on it, because it adds this plan under `intents/`.
12. After the merge. The working tree of the operator still holds the two directories as untracked files,
    and they stop a checkout of main there. I compare them with the committed copies and remove them only
    after the leader says so.

## Files

- `intents/fable-5-2-rounds.plan.md` (this file)
- `eval/runs/move-fable-5-2/` (63 files and `usage-readings.md`)
- `eval/runs/fable-5-2-round-2/` (63 files and `usage-readings.md`)
- `eval/BENCHMARK.md` (one new last section)

## Tests

No new test: the change adds data and one section of a document. The automatic checks of the intent are
commands, and step 8 runs them.
