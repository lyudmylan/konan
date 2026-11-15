# Intent: the widened matchers of the corpus

Work item: #90. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

A correct report in other words passes the prose matchers of the corpus, and no matcher matches a word that
every statement carries.

## In scope

- `eval/scenarios/`: the six matchers that the false-fail table of bench-v2 names (`eval/BENCHMARK.md`, the
  results section): `spread`, `switch-flipped`, `data-condition`, `location`, `rare-but-real`,
  `no-restart-after`. Each matcher gets the wordings of its rows in that table. The wordings stay in the
  table and in the fixtures; this file does not repeat them.
- `switch-flipped` is one expression in four fixtures: `chaos-error-rate`, `chaos-latency`,
  `t2-red-herring-latency-latent-d1`, `t3-chaos-low-rate-intermittent`. The widening reaches all four, and
  the four stay identical. A round of 30 investigations on `claude-fable-5-2`, run on 2026-11-15 and not
  committed, failed this matcher in 12 runs across the four fixtures, with the verdict, the class, the
  cause id and the citations right. Its rows are in a comment on #90.
- The rule of the widening: every added alternative is anchored, and none matches a word that every
  statement carries ("requests", a timestamp).
- A reference check runs the widened matchers over the 89 scorable journals of bench-v2 (the 90th is
  refused by the scorer, #92): the 13 rows of the table
  that read "No" pass, no passing row changes, no healthy-trap journal changes its result, and the
  journals that gain a match on a widened matcher of another fixture are named in the pin.
- `eval/tests.py`: one pin, "matcher widening", that covers the six matchers, negative-tested with the
  vacuous forms that the review of the round named.
- `eval/README.md` and `eval/BENCHMARK.md`: one sentence each. The first names the widening where the
  calibration of the matchers is described; the second says that the committed table of bench-v2 is the
  pre-registered scoring and reproduces at its own commit.
- The fixtures are pinned paths of a round, so the change lands between rounds, and the next round
  measures it.

## Out of scope

New fixtures. The report contract. The scorer: it stays regex and equality, and no model judges a claim.
The investigate skill: no instruction tells the investigator which word to write. Re-scoring bench-v2: its
table stays as pre-registered. The two runs of the round of 2026-11-15 that failed on
`t2-quiet-d1-suggestive-complaint`: they are the agent's error, and the corpus does not change for them.

## Acceptance checks

## Automatic checks

1. Each of the 13 rows of the false-fail table of bench-v2 that read "No" passes the matcher it failed, on
   its committed journal.
   test: `eval/tests.py`, the pin "matcher widening". command: `uv run eval/tests.py`
2. Over the 89 scorable journals of bench-v2 (the 90th is refused by the scorer, #92), no run that passed
   under the old matchers fails under the new ones, and the runs that newly pass are the runs of those 13
   rows. No healthy-trap journal changes its result; the three that gain a match on a matcher of another
   fixture are named in the pin, and a fourth fails it.
   test: the same pin.
3. Each widened matcher rejects its vacuous forms: a statement whose only match would be a word that every
   statement carries does not match. Each widened matcher accepts the wording of its rows: for
   `switch-flipped`, `spread` and `rare-but-real`, a statement of the rows on #90 as a literal string in
   the pin, copied from the comment on #90 into the test and not into this file; for the other three,
   check 1 on the committed journals of their rows in the table.
   test: the same pin.
4. `switch-flipped` is the same expression in the four fixtures that carry it.
   command: `test "$(grep -l 'id: switch-flipped' eval/scenarios/*.yaml | wc -l | tr -d ' ')" -eq 4 && test "$(grep -h -A1 'id: switch-flipped' eval/scenarios/*.yaml | grep all_of | sort -u | wc -l | tr -d ' ')" -eq 1`
5. The quality checks and the contract checks pass.
   command: `charter-gate quality --contract charter.toml && charter-check all charter.toml`

## Manual checks

6. The leader reads the widened matchers against the rows of the table and the rows on #90, and confirms
   that no alternation was widened beyond the wording of those journals. who: the leader. Not automatic: it
   is a reading of meaning, and a calibration pinned on the same journals must not become overfitting.
