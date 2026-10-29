# Plan: the no-restart matcher of the crash fixture (#75)

Intent: `intents/crash-matcher.md`. Written 2026-10-29; the code starts after the leader accepts it in the
conversation.

## Steps

1. `eval/scenarios/t3-crash-hard-down.yaml`: the pattern of `no-restart-after` keeps every form it has and
   gains five, each taken from a committed bench-v1 journal of the fixture:
   - `never (been) restarted` — Fable r1, r2, r3;
   - `not restart` without the "-ed", with a word boundary before "not" — Sonnet r1 ("did not restart");
     the boundary keeps "cannot restart" out;
   - `nothing restarted it` / `nothing restarting it` — Fable r3, Opus r1–r3, Sonnet r3;
   - `no supervisor restarted` / `no process restarted` — Opus r1, r3; Fable r1;
   - `no auto-restart` — Sonnet r1.
   `process-died` stays: it matches the eight root-cause journals today. The `scoring_notes` lose the two
   sentences "Matchers are first-cut (no known-good journal yet); calibrate on the first run and record the
   change." and gain one: the matchers are calibrated on the committed bench-v1 journals (#75) and pinned
   in `eval/tests.py`.
2. `eval/scenarios/t3-chaos-low-rate-intermittent.yaml`: `cause-switch` and `switch-flipped` match all
   eight committed journals and stay. `rare-but-real` keeps its forms and gains two, from the journals:
   `a fraction` / `random fraction` (Opus r1; Fable r2) next to the existing `small fraction`, and a
   one-digit percentage such as "~8%" (Fable r1–r3, Opus r3, Sonnet r3), not preceded by a digit or a dot,
   so that "0.08" and "60%" do not count. The `scoring_notes` gain one sentence: `rare-but-real` was
   calibrated on the committed bench-v1 journals (#75). This fixture carries no "first-cut" mark; check 3
   of the intent already holds for it.
3. `eval/tests.py`: pin 18, "tier-3 calibration", after pin 17 in `run()`; the closing line says 18 pins.
   Four cases:
   - every committed bench-v1 journal of `t3-crash-hard-down` whose verdict is `root-cause-identified`
     (eight) has no claim miss: `process-died` and `no-restart-after` both match (check 1);
   - a synthetic core, the base pair of pin 0 with a root-cause statement that says the process crashed
     and the supervisor restarted it, misses `no-restart-after` and matches `process-died` (check 1, the
     negative case);
   - the seven committed journals of `t3-chaos-low-rate-intermittent` that the pin names have no claim
     miss: Fable r1–r3, Opus r1 and r3, Sonnet r2 and r3 (check 2). The pin reads `claim_misses`, not
     `passed`: the class of those journals is the matter of #77, not of this check;
   - the eighth, Opus r2, misses exactly `rare-but-real`: its surface sizes nothing ("every observed
     non-2xx response"). The pin holds the judgment both ways, so a wider pattern that makes it match
     fails the pin and forces a decision instead of a drift.
4. `eval/README.md`, the paragraph "Corpus — coverage by tier and incident class": "and marked first-cut
   where no journal exists yet" becomes: the tier-3 matchers were first-cut until bench-v1 and are
   calibrated on its committed journals since #75, pinned in `eval/tests.py`.
5. `eval/BENCHMARK.md`: no change. Protocol item 8 governs the first-cut matchers of future fixtures;
   bench-v1 stays scored as pre-registered at its own commit.
6. The two commands of `AGENTS.md`, then the four automatic checks of the intent by hand; check 5 is the
   leader's reading of the patterns against the journals the pin names. One change request, `Closes #75`,
   on this branch. No file under a code path changes.

## Files

The two tier-3 fixtures, `eval/tests.py`, `eval/README.md`, and this file.

## Tests

Pin 18 of `eval/tests.py`, step 3. Pin 16 keeps compiling every matcher, so a bad regex fails there. No
other test changes.

## Facts the plan rests on

- The claim surface is the root-cause statement plus the statements of the validated hypotheses
  (`eval/score.py`, `claim_surface`); the patterns run over that text and nothing else.
- `t3-crash-hard-down` has nine committed bench-v1 journals: eight say `root-cause-identified`, one
  (Sonnet r2) says `inconclusive` with an empty surface. Today `no-restart-after` matches one of the eight
  (Opus r2, "was not restarted"). The recalibrated pattern, run over the eight surfaces, matches all of
  them, and misses three negative statements: "the supervisor restarted it within two seconds", "restarted
  automatically; the operator cannot restart it by hand", "has been restarted and is listening again".
  `process-died` matches all eight today.
- `t3-chaos-low-rate-intermittent` has eight committed journals, not the nine the intent counts: one Sonnet
  run left no journal, the same gap as in the plan of #77. `cause-switch` and `switch-flipped` match all
  eight today; `rare-but-real` matches five. The recalibrated pattern matches seven and misses Opus r2.
- The judgment of step 3, fourth case, is the leader's to confirm: a report that quotes `failure_rate 0.08`
  from the log but does not size the share of failing requests in its own words does not state the fact
  "rare but real".
