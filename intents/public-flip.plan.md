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
   sentence in `eval/BENCHMARK.md`, the two README issue links as absolute URLs; checks 1, 2, 7 and 8; the
   leader merges.
3. Agent: the tracker sweep (check 3), with any hit corrected in the item's body and named in the change
   request of step 2.
4. Leader, commands given in the conversation: delete-branch-on-merge on; the merged branches deleted;
   the description and the topics from the agent's proposal (check 5).
5. Leader, in the lab repository's session: the author identity of the early commits decided; the two
   commits pushed (check 4).
6. Leader: the history decision for both repositories, recorded on #13 (check 10).
7. Leader: the posts edited in the document; the day chosen.
8. Leader, on the day: the lab repository flipped public, then this repository; the ruleset command from
   #13 run as the first action (check 6); the posts published and the Show HN submitted; the links
   recorded on #13 (check 9).
9. Agent: the checklist of #13 ticked, #13 closed, the milestone closed with its acceptance stated in a
   comment.

## Files

Changed: 62 files under `eval/runs/` (one or a few lines each), `eval/BENCHMARK.md` (one sentence),
`README.md` (two links), `intents/public-flip.md` (with the work, if a check changes), and this file. Not
changed: `docs/product.md`, `skills/**`, `hooks/**`, `scripts/**`, `eval/score.py`, `eval/run.py`, the
fixtures, `eval/scorecard.md`.

## Tests

The commands of checks 1 to 8. `uv run eval/tests.py` and `python3 hooks/tests.py` run unchanged inside
check 8.

## Facts the plan rests on (as of 2026-11-08)

The counts of the intent (the archived runs, the commits, the lab repository's state), verified on
2026-11-08. Beyond them:

- The scorer reads the claim surface (the root cause statement and the validated hypotheses) and the
  evidence references, never the quoted text; a redaction inside a quote changes no score. One archived
  journal is refused by the scorer by design, so the archive is not re-scored in one command; the diff of
  the change request is the proof (check 7).
- The tracker, bodies and comments of every issue and change request, carries no private pattern (3642
  lines swept on 2026-11-08).
- The rulesets endpoint answers 403 on a private repository without a paid plan (verified 2026-08-20 and
  2026-11-08); the ruleset is created after the switch.
