# Intent: what a benchmark run sees, and what it records

Work item: #110. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

A benchmark run sees no name of an earlier journal and no commit subject of the repository, and its files
say at which effort level and on which version of the harness it ran.

## In scope

- `eval/run.py`, the working copy of a run. The runner deletes the files under `journals/` in a detached
  worktree, so that a run has no incident memory. The harness puts the output of `git status` and the last
  commit subjects into the context of each session, and the deleted journals are listed there by name. In
  the round of 2026-11-15 (30 investigations on `claude-fable-5-2`, not committed) every session record
  carries the names. After the change the working copy of a run has a clean `git status`, and its history
  holds no commit subject of the repository. The investigator still writes its journal to `journals/` and
  commits it there.
- `eval/run.py`, the record of a run. An option `--effort <level>` goes to each session. `plan.json` and
  each sidecar record the level and the version of the harness. Without the option the record reads
  `unset`: the settings of the operator decided. The level is part of the pre-registered plan (#76): a
  later invocation of the same run id with another level is refused.
- `eval/tests.py`: the pins of the checks below.
- `AGENTS.md`: the command line of the runner, in the section "Commands", names the option.
- `eval/README.md`, the blinding contract: the sentence on the emptied `journals/` says that the names are
  gone too. `eval/BENCHMARK.md`, the protocol: the effort level is part of a configuration, and the limits
  section says that bench-v2 ran at `xhigh` with the journal names in the session context (from the session
  records of the operator, outside the repository).

## Out of scope

Which instruction files and settings of the operator a run loads: a run loads them today, and that is a
separate decision. The boundary hook and its pins. The fixtures, the scorer, the journal schema. bench-v2:
its runs and its table stay as they are.

## Acceptance checks

## Automatic checks

1. The working copy that the runner builds has an empty `git status --porcelain`, and its `git log` holds
   no commit subject of the source repository. The only commit that a run adds is the investigator's own
   journal commit.
   test: `eval/tests.py::test_runner_working_copy_shows_no_removed_journal`. command: `uv run eval/tests.py`
2. The working copy has an empty `journals/` directory, and a journal written there can be added and
   committed.
   test: `eval/tests.py::test_runner_working_copy_takes_a_journal`
3. With `--effort high` the command of the session carries the level, and `plan.json` and the sidecar
   record `high` and the version of the harness, as `claude --version` prints it. Without the option they
   record `unset` for the level.
   test: `eval/tests.py::test_runner_records_effort_and_version`
4. A second invocation of a run id with another effort level, or with none when the run id recorded one,
   is refused before any investigation starts.
   test: `eval/tests.py::test_runner_refuses_a_changed_effort`
5. The quality checks and the contract checks pass.
   command: `charter-gate quality --contract charter.toml && charter-check all charter.toml`

## Manual checks

6. One investigation with the changed runner, one fixture, one repetition: the session record names no
   journal of the repository and no commit subject of the repository, and the sidecar records the effort
   level and the version. The change request records the fixture, the two counts and the sidecar fields.
   who: the agent writes the record, the leader reads it. Not automatic: the session record lives outside
   the repository, and the run calls the model.
