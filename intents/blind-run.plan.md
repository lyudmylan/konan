# Plan: the blind run on the Grafana Cloud adapter (#55)

Intent: `intents/blind-run.md`. Written 2026-11-08; the work starts after the leader accepts it in the
conversation and after the merge of the intent.

## The shape of the work

One branch for #55. The eval side (staging, the headless session, the receipts) is the agent's session;
the investigator is a fresh headless session in a blinded worktree. The leader reads the journal and the
record, then approves the change request. The operator's hands: none during the run; the credentials of the
adapter are already in the operator's shell configuration, which the agent's session sources.

## Steps

1. Agent: the calibration. `uv run eval/score.py --pair eval/scenarios/d1-zero-stock-product-page.yaml
   journals/2026-11-08-product-page-500s.md` passes 1/1 (done on 2026-11-08, repeated at the start of the
   work); the summary goes into the change request.
2. Agent, in the main checkout: the fresh lab (`scripts/lab.sh stop`, `lab/logs` deleted, `scripts/lab.sh
   start`), Alloy still running and reporting no error; then the fixture's `stage` list, one
   `scripts/scenario.sh` call after another with the fixture's sleeps; the time of the last staged request
   noted. A minute later, Alloy has shipped the lines (its log shows no error).
3. Agent: the worktree, `git worktree add ../konan-blind-d1 main`; in it, every file under `journals/`
   deleted; the hook's state file of the new session does not exist yet.
4. Agent: the headless session, from the worktree, with the adapter's credentials sourced,
   `KONAN_ADAPTER=docs/adapters/grafana-cloud.md` and `KONAN_EVAL_BLIND=1` exported, the fixture's
   `complaint` read into the prompt verbatim: `claude -p --model claude-fable-5-1 --permission-mode
   acceptEdits --mcp-config docs/adapters/grafana-cloud.mcp.json --output-format json "/konan <complaint>"`,
   a 30-minute timeout, the envelope saved. The start and end times noted.
5. Agent: the receipts. The journal copied to `journals/` under its own name; `usage.tokens` stamped from
   the envelope (`modelUsage`, every category, every model); the sidecar written from the envelope's kept
   fields; `uv run eval/score.py --pair <fixture> <journal> -o eval/runs/2026-11-blind-grafana/scorecard.md`;
   the hook's state file of the session read for the denial count; the worktree removed.
6. Agent: `README.md`, one sentence under "Measured before believed" that links the journal and the
   scorecard. The checks 1 to 5. The two commands of `AGENTS.md` before the push.
7. The change request: `Closes #55`; the tier is the one `charter.toml` gives the changed paths
   (`intents/**` is high); the record of checks 6 and 7 in its text; the leader reads the journal and
   approves in the conversation; the merge. Then epic #58 closes with a comment that names what it
   delivered.

When the journal fails a matcher or the verdict differs from the fixture, step 5 still writes the scorecard
as it comes out, the change request says so, and the leader decides what the receipt is.

## Files

Added: `journals/<date>-<slug>.md` (the blind journal), `eval/runs/2026-11-blind-grafana/scorecard.md`,
`eval/runs/2026-11-blind-grafana/d1-zero-stock-product-page-r1.meta.json`. Changed: `README.md` (one
sentence), `intents/blind-run.md` (with the work, if a check changes), and this file. Not changed:
`eval/run.py`, `eval/score.py`, the fixtures, `eval/scorecard.md`, `skills/**`, `hooks/**`,
`.claude/settings.json`, `docs/adapters/**`.

## Tests

The commands of checks 1 to 5. `uv run eval/tests.py` and `python3 hooks/tests.py` run unchanged inside
check 5.

## Facts the plan rests on (as of 2026-11-08)

- The runner's recipe (`eval/run.py`, `eval/README.md`): a detached worktree of HEAD, `journals/` emptied,
  `KONAN_EVAL_BLIND=1`, `claude -p --model <m> --permission-mode acceptEdits --output-format json
  "/konan <complaint>"`, the envelope's `modelUsage` summed over every category and model as the tokens of
  the run, the journal's `usage.tokens` stamped with it. The runner has no adapter plumbing and starts the
  lab inside the worktree.
- The hook's blind rule denies a Bash command that carries the word `eval` in a path, so the worktree
  directory is named without it.
- A headless session fails closed on a tool that no rule allows (the adapter document, Boundary, layer 3);
  the allowlist of `.claude/settings.json` travels with the worktree.
- Alloy tails `lab/logs/app.log*` under `KONAN_REPO`, the main checkout; a deleted and recreated log file
  is picked up again by the file match. The smoke run of 2026-11-08 shipped the staged lines within a
  minute.
- The D1 fixture's matchers hit the claim surface (the root cause statement and the validated
  hypotheses) of the smoke journal written under the adapter: scored 1/1 on 2026-11-08.
- `eval/score.py --pair <fixture> <journal> [-o file]` exits 0 when the scenario passes.
