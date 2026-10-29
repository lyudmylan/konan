# Plan: one incident class per chaos fixture (#77)

Intent: `intents/singular-class.md`. Written 2026-10-29; the code starts after the leader accepts it in the
conversation.

## Steps

1. The four fixtures `eval/scenarios/chaos-error-rate.yaml`, `chaos-latency.yaml`,
   `t2-red-herring-latency-latent-d1.yaml`, `t3-chaos-low-rate-intermittent.yaml`: the line
   `incident_class: [infra-process, interfaces]` with its three comment lines becomes
   `incident_class: infra-process`. Nothing else in the fixtures changes.
2. `eval/tests.py`: pin 17, "Singular class", after pin 16 in `run()`; the closing line says 17 pins. Two
   cases:
   - the four fixtures load through `score.load_fixture` with the string `infra-process` as
     `expected.incident_class` (check 1);
   - the committed journal `eval/runs/bench-v1/claude-opus-5/chaos-error-rate-r1.md`, whose root cause says
     `interfaces`, scores `class_ok` false and `passed` false against the live `chaos-error-rate` fixture
     (check 2). The pin asserts the journal's class first, so a later edit of the journal cannot make the
     case vacuous.
   Pin 15 stays as it is: the set form is still valid for a fixture with a true ambiguity.
3. `eval/BENCHMARK.md`, the bullet "Regenerating it" of the bench-v1 results section: one sentence after
   "was the label.": re-scoring the bench-v1 journals against the live fixtures fails those four scenarios on
   class in 24 of their 35 committed journals, by design; bench-v1 is scored as pre-registered at its own commit, and
   the live fixtures state the one class the contract decided (#77).
4. The two commands of `AGENTS.md`, then the five checks of the intent by hand. One change request,
   `Closes #77`, on this branch. No file under a code path changes.

## Files

The four fixtures of the intent, `eval/tests.py`, `eval/BENCHMARK.md`, and this file.

## Tests

Pin 17 of `eval/tests.py`, step 2. Pin 16 keeps loading every fixture, so a typo in a changed line fails
there. No other test changes.

## Facts the plan rests on

- The scorer accepts a string or a set for `expected.incident_class` and compares the root cause's class
  by membership (`eval/score.py`, `score_pair`); a string is the one-member case.
- The four scenarios have 35 committed bench-v1 journals, not 36: one Sonnet run of the low-rate chaos
  scenario left no journal. Counted with `score.load_journal` over the committed files, 24 of the 35 name
  `interfaces` as the class of the root cause. The pin uses one of them.
