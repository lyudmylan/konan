# Plan: the public flip (#13)

Intent: `intents/public-flip.md`. Written 2026-11-08; the work starts after the leader accepts it in the
conversation and after the merge of the intent.

## The shape of the work

Two hands. The agent's: the redaction of the archived runs, the README links, the sentence in the
benchmark protocol, the tracker sweep, the proposals, the checks, the record. The leader's: the settings,
the lab repository's push and flip, the history decision, the switch, the ruleset, the posts. Every
operator step comes as one command or one click in the conversation, never as a description.

## Steps

1. Agent: the five earlier journals (the open change request of the redaction); the leader merges it.
2. Agent, one change request: the archived runs under `eval/runs/` redacted (`<checkout>`, `<home>`), the
   sentence in `eval/BENCHMARK.md`, the two README issue links as absolute URLs; checks 1, 2 and 7; the
   leader merges.
3. Agent: the tracker sweep (check 3), with any hit corrected in the item's body and named in the change
   request of step 2.
4. Leader, commands given in the conversation: delete-branch-on-merge on; the merged branches deleted;
   the description and the topics from the agent's proposal (check 5).
5. Leader, in the lab repository's session: the author identity of the early commits decided; the two
   commits pushed (check 4).
6. Leader: the history decision for this repository, recorded on #13 (check 9).
7. Leader: the posts edited in the document; the day chosen.
8. Leader, on the day: the lab repository flipped public, then this repository; the ruleset command from
   #13 run as the first action (check 6); the posts published and the Show HN submitted; the links
   recorded on #13 (check 8).
9. Agent: the checklist of #13 ticked, #13 closed, the milestone closed with its acceptance stated in a
   comment.

## Files

Changed: 62 files under `eval/runs/` (one or a few lines each), `eval/BENCHMARK.md` (one sentence),
`README.md` (two links), `intents/public-flip.md` (with the work, if a check changes), and this file. Not
changed: `docs/product.md`, `skills/**`, `hooks/**`, `scripts/**`, `eval/score.py`, `eval/run.py`, the
fixtures, `eval/scorecard.md`.

## Tests

The commands of checks 1 to 7. `uv run eval/tests.py` and `python3 hooks/tests.py` run unchanged inside
check 7.

## Facts the plan rests on (as of 2026-11-08)

- 62 files under `eval/runs/` carry the home path (38 in bench-v1, 6 in bench-v1-invalid-logs, 18 in
  bench-v2), almost all as the lab checkout's prefix in quoted stack traces, a few as recorded commands in
  sidecars; no other private pattern hits the archived runs.
- The scorer reads the claim surface (the root cause statement and the validated hypotheses) and the
  evidence references, never the quoted text; a redaction inside a quote changes no score.
- The hook's test fixture `ls /Users/x/Projects/faultline/` is a one-letter user; check 1 requires two.
- The tracker bodies carry no private pattern (swept on 2026-11-08, 893 lines of issue bodies).
- The lab repository: scan clean, LICENSE and NOTICE added, README links this repository; two commits
  unpushed; early commits by a personal e-mail address (its session's report of 2026-11-08).
- This repository's history: three commit messages with a session link (2026-08-06), forty-one commits
  authored under a personal e-mail address.
- The rulesets endpoint answers 403 on a private repository without a paid plan (verified 2026-08-20 and
  2026-11-08); the ruleset is created after the switch.
