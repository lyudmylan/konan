# Plan: the benchmark re-run (#81)

Intent: `intents/bench-v2-rerun.md`. Written 2026-11-02; the code starts after the leader accepts it in the
conversation, and the first batch starts after the pre-run review of manual check 8.

## The shape of the round

One branch, `81-bench-v2-rerun`, from main at the merge of the cause field. The runner change lands on the
branch first; its commit is the pin `first-run`. The runs happen from this branch: the runner takes a
worktree of HEAD of the checkout, so the pinned paths the runs see are those of main. Every batch ends in a
commit of `eval/runs/bench-v2/` on the branch; the commit of the last batch is `last-run`. One change
request at the end, `Closes #81`, carries the runner change, the run directory, the regenerated table, the
results section, the README table, and the product line; the review loop runs once, on it.

Why one change request: acceptance checks 1 to 4 and 6 read the run directory and the results section,
which exist only after the last run, and a change request for the runner alone closes no issue.

## Steps

1. `eval/run.py`: `worktree_dir(base=None)` returns `Path(tempfile.mkdtemp(prefix="konan-wt-", dir=base))
   / "wt"`; `main` calls it; the only `mkdtemp` of the file is inside it. The prefix carries neither `eval`
   nor the run id. The docstring says "a detached git worktree of HEAD under a neutral temporary name".
   A side effect worth naming: in blind mode the boundary hook denies a Bash command that mentions `eval/`,
   and the old prefix `konan-eval-<run-id>-` put `eval` into every absolute path of the worktree, so a
   model that wrote its own working directory into a command was denied for the path, not for the content
   (recorded in bench-v1 as headless denials). The neutral name removes that artifact, so the denial counts
   of bench-v2 are not comparable with bench-v1 on that point; the results section says so.
2. `eval/tests.py`, the runner pins: a fifth pin, "neutral worktree" (check 5): `runner.worktree_dir(base=
   tmp)` returns a path under `tmp` whose part below `tmp` contains neither `eval` nor a run id (the
   function takes none) and ends in `wt`; and the source of `eval/run.py` holds exactly one `mkdtemp(`,
   inside `worktree_dir`, so no other call builds a worktree path. The closing line counts 5 runner pins.
3. The pin commit: steps 1 and 2, committed on the branch as "The runner names its worktree neutrally",
   `uv run eval/tests.py` green at it. Its sha is `first-run`. From there to `last-run` the pinned paths
   do not change (check 3); `eval/run.py` and `eval/bench.py` do not change either, by decision.
4. The pre-run review (manual check 8), in the conversation, before the first batch: the pin sha; the
   model ids that answered one headless call (check 9: on 2026-11-02 `claude-sonnet-5`, `claude-opus-5`,
   `claude-fable-5` each answered "ok", so no substitution); the quota plan for the week; the two items
   (step 1 and the false-fail table of step 8). The leader gives the go. The quota plan, accepted by the
   leader on 2026-11-02 with her readings: the five-hour window no longer exists (dissolved by the
   provider), so the weekly meter is the one limit; the usage panel read 15 percent of the week and 29
   percent of the Fable week, with the reset on 2026-11-03 at 22:00 (Asia/Jerusalem). The order Sonnet,
   Opus, Fable; inside each model the tier-1 fixtures first, then tier 2, then tier 3 (the order of
   `--fixtures`); batches of ten (`--max-runs 10`), one model at a time, for the granularity of the
   commits, resumed until the model's thirty runs are done; the weekly meter read before and after each
   model's runs, and after the first batch of ten, which sizes the share of one investigation on the
   current plan (check 11). Sonnet and Opus run before the reset; Fable runs after it, on a fresh Fable
   week (bench-v1 measured 2.2 to 3.3 percent of the weekly Fable quota per investigation, so the thirty
   Fable runs are most of a week, and 71 percent of the old week would not hold them with margin for the
   leader's own sessions). The leader states what else the pool must serve, and the batches move
   accordingly.
5. The batches: `uv run eval/run.py --run-id bench-v2 --model <m> --repeat 3 --max-runs <k> --fixtures
   <the ten fixtures in tier order>`. The first invocation registers the plan (ten ids, three
   repetitions). The runner resumes by run id; a quota stop is retried; a failed run counts and is not
   retried; the scorecard regenerates after each batch. After each batch: `git add eval/runs/bench-v2`,
   one commit "bench-v2: batch <n>, <model>, <k> runs". The weekly meter readings go into
   `eval/runs/bench-v2/usage-readings.md` (date, model, runs so far, the two meters as read), the raw
   data of check 11, committed with the batch; the leader reads the panel and states the numbers in the
   conversation (decided 2026-11-02: the readings stay manual; the runner does not touch the OAuth token
   of the CLI). The session stays open while a batch runs (the runner is a background process of the
   session), or the leader starts the batch from her terminal with the same command; either way the
   invocation is on record in `results.jsonl`.
6. After the last run: `uv run eval/bench.py --runs eval/runs/bench-v2 -o eval/BENCHMARK-results.md`
   (check 2); the coverage line says `missing 0` three times (check 1).
7. `eval/BENCHMARK.md`: a section "## Results — bench-v2 (...)" (the heading of check 4), with the bullets
   of the bench-v1 section in the same order: pin (`first-run: <sha>`, `last-run: <sha>`, the pinned
   paths), models and ids (the substitution line: none), dates, table, coverage, quota measured (the
   windows from `eval/bench.py`, the weekly deltas from the readings file), failure modes observed, the
   false-fail table (step 8), the tier-3 result (manual check 10, the leader's reading: the rows differ by
   model, or the artifact that remains and no claim), the diff against bench-v1 (both pass columns per
   model, as the generator renders them), and the denial-count caveat of step 1. The "Reproduce" block
   gains the bench-v2 lines.
8. The false-fail table, in that section, with the columns date, scenario, what failed, whether the agent
   was wrong, the fix. One row per failed scenario of `eval/runs/bench-v2/scorecard.md` (manual check 12).
   I draft each row from the failure detail of the scorecard and the journal; the leader confirms or
   corrects each row in the conversation before the change request. A row whose fix is a fixture or scorer
   change names the issue to file; the fix is not applied in this round, because the pinned paths do not
   change.
9. `README.md`: the table under "The same skills, three models" replaced by the bench-v2 rows (the
   model-overall rows of the generated table, same columns); the paragraph on the two pass columns
   rewritten to what bench-v2 shows; the sentence "The tier-3 fixtures are not yet trustworthy ..."
   replaced by the tier-3 reading (check 4); "bench-v2" named with its dates and its ninety runs.
10. `docs/product.md`, v0.2 exit criteria, the bullet "Benchmark v1 published": its closing sentences on
    the tier-3 re-run updated to the state after bench-v2 (the date, and whether tier 3 carries a number).
    `eval/` is not a code path of the contract, so this document change is by the intent, not by the
    contract rule.
11. One line left open by the review of the cause field (its round 3, low): `intents/cause-field.md`, In
    scope, the `eval/tests.py` bullet becomes "the pins of the version 2 semantics named in the acceptance
    checks; the version 1 pins unchanged." In this change request, because it touches `intents/` and the
    loop of its own change request was at its limit.
12. The checks: 1 to 7 of the intent, the two commands of `AGENTS.md`, and the manual checks 8 to 12 as
    stated. One change request, `Closes #81`, the review loop, the leader's approve in the conversation,
    the merge.

## Files

`eval/run.py`, `eval/tests.py`, `eval/runs/bench-v2/` (new: the journals, the sidecars, `plan.json`,
`results.jsonl`, `quota-stops.jsonl`, `scorecard.md`, `usage-readings.md`), `eval/BENCHMARK-results.md`,
`eval/BENCHMARK.md`, `README.md`, `docs/product.md`, `intents/cause-field.md` (one line), and this file.
Not changed: the pinned paths of the intent, and `eval/bench.py`.

## Tests

The runner pin of step 2. Checks 1, 2, 3, 4, 6 and 7 are commands, run at the end of the round. The
semantics pins and the coverage pins stay as they are.

## Facts the plan rests on (as of 2026-11-02)

- main is at the merge of the cause field; `uv run eval/tests.py` prints 23 semantics, 4 runner, and 5
  coverage pins.
- `eval/run.py` builds the worktree with `tempfile.mkdtemp(prefix=f"konan-eval-{a.run_id}-")`, the only
  `mkdtemp` of the file, from HEAD of the checkout.
- The three model ids of bench-v1 each answered "ok" to a one-word headless call on 2026-11-02.
- bench-v1 quota measures: about 24 Sonnet runs between quota stops, 11 to 15 Opus, 11 Fable in a shared
  window; 2.2 to 3.3 percent of the weekly Fable quota per investigation. The smoke run of the cause field
  (Sonnet, the D1 fixture) took 3.0 million tokens and 650 seconds.
- The README carries the bench-v1 table and the tier-3 caveat sentence; the product bullet on the benchmark
  ends with the tier-3 re-run condition.
