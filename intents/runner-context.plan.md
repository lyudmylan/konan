# Plan: what a benchmark run sees, and what it records (#110)

Intent: `intents/runner-context.md`. Written 2026-11-15. Accepted by the leader in the conversation on
2026-11-15.

## Steps

1. `eval/run.py`, the working copy. A new function `make_working_copy(repo, wt)` replaces the two lines
   that add the worktree and delete the journals. It adds the detached worktree of HEAD as today, removes
   the files under `journals/` from the index and from the directory, writes the tree, and makes one commit
   with no parent from that tree (`git commit-tree`), with the subject "working copy" and a fixed neutral
   author. It checks that commit out detached, creates the empty `journals/` again, and returns the commit
   id. After it, `git status --porcelain` is empty and `git log` shows one commit, "working copy". No
   branch and no ref is created in the repository; the commit has no ref, so no branch or tag shows it,
   and `git gc` removes it later.
2. `eval/run.py`, between runs. A function `reset_working_copy(wt, base)` replaces the loop that deletes
   the journal of the run before: `git reset --hard` to the commit of step 1, then the files under
   `journals/` are deleted and the directory is kept. A journal that the investigator committed is gone
   with the reset, so the next run sees one commit again. `lab/` is ignored by git and is not touched.
3. `eval/run.py`, the effort. An option `--effort` with the levels of the harness (`low`, `medium`,
   `high`, `xhigh`, `max`). A pure function `session_command(claude, model, effort, prompt)` builds the
   command of the session; with a level it carries `--effort <level>`, without one it is the command of
   today. `main()` calls it.
4. `eval/run.py`, the record. `harness_version(claude)` returns the line that `claude --version` prints.
   `register_plan` takes the effort and the version: `plan.json` gains `effort` (the level, or `unset`) and
   `harness_version` (at registration). The effort is part of the compared plan: another level, or none
   when the plan holds one, stops the runner with a message that names both. A `plan.json` without the
   field reads as `unset`, so the run ids on record keep working. The version is not compared: the harness
   updates itself between batches, so each sidecar records the version of its own invocation, and the
   runner prints one line when it differs from the plan (not pinned; the sidecar field is the record). Each
   sidecar gains `effort` and `harness_version`.
5. `eval/run.py`, the docstring: the working copy and the option, in the words of steps 1 to 4.
6. `eval/tests.py`: four runner pins after the five that exist; the closing line says 9 runner pins.
   - `test_runner_working_copy_shows_no_removed_journal`: a temporary repository with two commits and two
     journals; after `make_working_copy` the status is empty and the subjects of `git log` are exactly
     ["working copy"] (check 1).
   - `test_runner_working_copy_takes_a_journal`: `journals/` exists and is empty; a journal written there
     can be added and committed; after `reset_working_copy` the status is empty, `journals/` is empty, and
     the log shows one commit again (check 2, and the last sentence of check 1).
   - `test_runner_records_effort_and_version`: `session_command` with `high` carries `--effort high`, and
     without a level carries no `--effort`; `register_plan` writes `effort` and `harness_version`, and
     `unset` without a level (check 3). The version comes from a stub executable in the test, not from the
     installed harness.
   - `test_runner_refuses_a_changed_effort`: a second `register_plan` with another level, and one with
     none after `high`, exit non-zero and leave `plan.json` unchanged; a `plan.json` without the field
     accepts an invocation without a level (check 4).
7. `eval/README.md`: in the blinding contract, the sentence on the emptied `journals/` says that the
   working copy of a run has a clean status and one commit, so the session context carries no journal name
   and no commit subject of the repository. In the runner section, the option `--effort` and the two new
   fields.
8. `eval/BENCHMARK.md`. The protocol: item 5 names the neutral commit, and a new item 11 names the effort
   level as part of a configuration, given with `--effort` and recorded in `plan.json`. The limits section
   gains one sentence: bench-v1 and bench-v2 record no level; bench-v2 ran at `xhigh`, and its sessions
   carried the names of the journals of that time in their context (from the session records of the
   operator, outside the repository).
9. Manual check 6, after the code: one investigation, `healthy-baseline`, one repetition,
   `--model claude-fable-5-2 --effort high`, under a run id of its own. I search the session record for
   each journal name of the repository and for each of the last twenty commit subjects, and I put the two
   counts and the sidecar fields into the change request. The run folder is not committed.
10. The two commands of `AGENTS.md`, then the automatic checks of the intent by hand. One change request,
    `Closes #110`, on this branch. No file under a code path changes.

## Files

`eval/run.py`, `eval/tests.py`, `eval/README.md`, `eval/BENCHMARK.md`, `AGENTS.md` (the `[--effort <level>]`
token in the runner command), the intent (one line of its scope, for `AGENTS.md`), and this file.

## Tests

The four pins of step 6. `test_bench_coverage_plan_is_pre_registered` calls `register_plan` without the new
arguments and stays as it is: the new arguments have defaults.

## Facts the plan rests on

- The harness puts the output of `git status` and the last five commit subjects into the context of a
  session. In the session records of the round of 2026-11-15 the block lists eleven deleted journals and
  five subjects, in 30 of 30 sessions.
- A run does not see the journal of the run before it today: an investigation writes its journal and does
  not commit it, and the runner deletes the file. Step 2 keeps that true also when an investigator commits.
- The session record of a run holds the effort level. All 30 runs of 2026-11-15 ran at `high` and all 30
  Fable runs of bench-v2 at `xhigh`.

## What the plan does not do

- `git log --all` and `git show <id>` in the working copy still reach the history of the repository, as
  today: a worktree shares the objects of its repository. A copy with a history of its own (an export and a
  new repository) would close that, and it changes how the boundary hook finds its workspace and how the
  runner removes the copy. That is a larger change than this work item.
- Without `--effort` the level comes from the settings and the environment of the operator, and the record
  says `unset`. Making the option required is the stricter choice; the intent leaves it optional.

## Changes after the code review, 2026-11-15

The code review (`/code-review`, on the first commit of the code) gave ten findings. Five changed the code
or the documents:

- Step 1: a working copy that cannot be finished is removed again, so that no half-made worktree stays
  registered in the repository.
- Step 2: the reset also removes untracked files (`git clean`), since a file that the run before left
  behind would show in the status of the next session. A session that the runner killed at its timeout
  can leave the lock of the index; the reset removes a stale lock and tries once more.
- Step 4: the two fields of the sidecar come from one pure function, `invocation_record`, and the pin
  reads that function. The runner checks that the harness exists before it registers a plan, and a dry
  run does not call the harness.
- Step 7: `eval/README.md` states which routes stay open (below).
- `AGENTS.md`: the command line of the runner gains `[--effort <level>]`, one token, so that the reference
  and the protocol say the same.

Not changed, and named here:

- Tracked files outside `eval/` name earlier journals: the top-level README, three files under
  `intents/`, and `hooks/tests.py`. A session that reads them sees the names. In the round of 2026-11-15
  no session opened one of them. This work item closes the route through the session context; these
  files are a decision of their own.
- `eval/bench.py` does not read the effort level. The table of a round does not show it yet.
- A `plan.json` without the field reads as `unset`, also for a run id that ran at a known level before
  this change.

One more fact from the session records of the round of 2026-11-15, found while answering the review: one
session of 30 read a removed journal back from the history, with `git show HEAD:journals/<name>`, after
it saw the name in the session context. With the working copy of step 1 that command finds nothing: the
one commit holds no journal.
