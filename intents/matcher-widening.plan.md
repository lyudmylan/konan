# Plan: the widened matchers of the corpus (#90)

Intent: `intents/matcher-widening.md`. Written 2026-11-15; the code starts after the leader accepts it in the
conversation.

## Steps

1. `switch-flipped`, one expression in four fixtures (`chaos-error-rate`, `chaos-latency`,
   `t2-red-herring-latency-latent-d1`, `t3-chaos-low-rate-intermittent`): the pattern keeps `enab` and gains
   two forms, each with word boundaries and each taken from a committed bench-v2 journal:
   - `turned on` - Opus chaos-error-rate r1;
   - `armed` - Opus chaos-error-rate r2.
   The four lines stay identical (check 4). The twelve rows on #90 all say "turned on".
2. `spread` (`chaos-error-rate`) keeps its three forms and gains four:
   - `random` / `randomly`, as a whole word - Fable r1 ("fast random HTTP 503 failures"), Fable r3;
   - `a fraction` / `small fraction` / `random fraction` - Opus r1;
   - `probabilist` - Sonnet r1;
   - a percentage of something, one or two digits before "% of" - Fable r2 ("roughly 40% of product and
     order requests").
3. `data-condition` (`d1-zero-stock-product-page`) gains one form: the field name, then one to three words,
   then a zero with a word boundary - Opus r1 ("units_in_stock, which is 0"), Sonnet r3 ("units_in_stock
   equal to 0"). "units_in_stock 10" does not match.
4. `location` (same fixture) gains `product id 3` with a word boundary after the 3 - Opus r2.
5. `rare-but-real` (`t3-chaos-low-rate-intermittent`): the form `a|small|random fraction` becomes
   `a|small|random` followed by `fraction`, `share` or `subset` - Opus r1 ("a subset of requests"), Opus r3
   ("a share of incoming requests").
6. `no-restart-after` (`t3-crash-hard-down`) keeps every form and gains two: `nothing started it again` -
   Opus r1; `no process listening` - Sonnet r3.
7. Each widened matcher gets one comment line in its fixture: widened on the false-fail table of bench-v2
   (#90), pin 24 of `eval/tests.py`.
8. `eval/tests.py`: pin 24, "matcher widening", after pin 23 in `run()`; the closing line says 24 pins. Five
   cases:
   - the 13 rows of the table that read "No", named by path, have no claim miss (check 1);
   - over the journals of bench-v2, scored once with the fixtures as committed and once with the six old
     patterns put back (the pin holds them as literals): every run that passes under the old patterns
     passes under the new ones, and the runs that newly pass are those 13 (check 2). The one journal the
     scorer refuses (Opus `t2-healthy-after-chaos-window` r1, #92) is skipped by name;
   - vacuous forms, one synthetic statement per matcher, none matches (check 3): "the switch is on" with a
     timestamp and the word "requests"; "product 30" and "product id 31"; "units_in_stock 10"; a statement
     that says the supervisor restarted the process; a statement that carries only `failure_rate 0.08`;
   - the twelve statements of the comment on #90, as literal strings, each match the widened matchers of
     their fixture (check 3);
   - the healthy-trap journals: no `healthy-baseline` journal of bench-v1 or bench-v2 matches a widened
     matcher that it did not match before. Three journals of the other two healthy-trap fixtures gain one
     match each, and the pin names them, so that a fourth fails the pin: bench-v2 Opus
     `t2-quiet-d1-suggestive-complaint` r3 (`location`: it names the latent defect as the cause, a "Yes" row
     of the table), bench-v2 Sonnet and bench-v1 Fable `t2-healthy-after-chaos-window` r3 (`spread`: each
     describes the closed window with the word "random"). These matchers belong to other fixtures, so no
     result of a healthy-trap journal changes.
9. `eval/README.md`: one sentence where the calibration of the tier-3 matchers is named: six matchers were
   widened on the false-fail table of bench-v2 (#90) and pinned in `eval/tests.py`.
10. `eval/BENCHMARK.md`: no change. bench-v2 stays scored as pre-registered at its commit.
11. The two commands of `AGENTS.md`, then the automatic checks of the intent by hand. One change request,
    `Closes #90`, on this branch. No file under a code path changes.

## Files

Six fixtures under `eval/scenarios/`, `eval/tests.py`, `eval/README.md`, and this file.

## Tests

Pin 24 of `eval/tests.py`, step 8. Pin 16 keeps compiling every matcher. Pin 18 stays as it is and holds
with the new patterns.

## Facts the plan rests on

- I ran the patterns of steps 1 to 6 in a copy of the repository, not in the repository. bench-v2: 64 of
  89 scored journals pass under the old patterns and 77 under the new ones; the 13 that newly pass are the
  13 rows of the table; no pass is lost. The 33 pins of `eval/tests.py` hold.
- With the new patterns the scorer gives Fable 26 of 30 and Sonnet 25 of 30 on bench-v2. These are the
  numbers "by content" that the leader confirmed on 2026-11-03.
- The round of 2026-11-15 (not committed): 16 of 30 under the old patterns, 28 of 30 under the new ones.

## Three places where the plan is narrower than the table, for the leader

- `switch-flipped`: the table also names "switched on" and "toggled", and #90 names "switched on". No
  committed journal carries either, and manual check 6 asks that no alternation goes beyond the wording of
  the journals. The plan leaves both out.
- `rare-but-real`: the table and #90 name "a decimal rate tied to the word rate". Pin 18 holds the
  judgment of #75 that bench-v1 Opus r2 sizes nothing, and its statement carries "failure_rate 0.08". With
  the decimal form that journal matches and pin 18 fails. The 13 rows pass without it. The plan leaves it
  out, and the pin of step 8 holds a statement with only the decimal rate as a non-match.
- `no-restart-after`: the table also names "the listener was absent". Opus r1 passes on "nothing started it
  again" alone, and the intent of #75 says that a symptom is not the fact. The plan leaves it out. "no
  process listening" is the only wording of Sonnet r3 for the fact, and the table reads that row as "No", so
  it stays in.
