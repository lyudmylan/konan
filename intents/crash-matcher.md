# Intent: the no-restart matcher of the crash fixture

Work item: #75. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The fixture `t3-crash-hard-down` measures whether a report states that the process never came back, in the
words that the report contract lets an investigator use.

## In scope

- `eval/scenarios/t3-crash-hard-down.yaml`: the `must_claim` entry `no-restart-after` is recalibrated
  against the nine committed bench-v1 journals of this fixture
  (`eval/runs/bench-v1/<model>/t3-crash-hard-down-r<n>.md`). The fact under test is "the process did not
  return". The alternation accepts the ways those journals state it — "never restarted", "nothing restarted
  it", "no auto-restart", "not restarted" — and keeps the forms it accepts today. The fact stays the
  absence of a restart; a symptom ("refuses every connection") does not count as the fact.
- The other first-cut matchers of tier 3 — `process-died` in the same fixture, and the matchers of
  `t3-chaos-low-rate-intermittent` — are checked the same way against their nine journals. A matcher that
  misses a journal which states the fact correctly is recalibrated in the same change. The `scoring_notes`
  of both fixtures lose the "first-cut" mark.
- `eval/tests.py`: one pin runs the two tier-3 fixtures over their committed bench-v1 journals, so the
  calibration is pinned and not re-guessed. It includes one negative case: a root-cause statement that says
  the process restarted does not match `no-restart-after`.
- `eval/README.md`: the sentence on the first-cut status of the tier-2 and tier-3 matchers reflects the
  calibrated state. Protocol item 8 of `eval/BENCHMARK.md` (a first-cut matcher may be calibrated after the
  first run) stays: it governs the first-cut matchers of future fixtures; after this change no live fixture
  is first-cut.

## Out of scope

Re-scoring bench-v1: it stays scored as pre-registered at its commit (`eval/BENCHMARK.md`, "Regenerating
it"). The incident-class label of `t3-chaos-low-rate-intermittent`: #77. The scorer, the journal schema,
and the fixture schema: #78. A new tier-3 fixture.

## Acceptance checks

## Automatic checks

1. Each bench-v1 journal of `t3-crash-hard-down` whose verdict is `root-cause-identified` matches
   `no-restart-after` and `process-died`; a statement that says the process restarted does not match
   `no-restart-after`.
   test: `eval/tests.py`, the pin "tier-3 calibration". command: `uv run eval/tests.py`
2. The matchers of `t3-chaos-low-rate-intermittent` match the journals that the pin names as stating the
   fact. The list of journals is the human judgment, made once, in the change request that adds the pin (the
   class label is not part of this check; it is #77).
   test: the same pin.
3. The first-cut marks are gone from the two fixtures.
   command: `! grep -q 'first-cut' eval/scenarios/t3-crash-hard-down.yaml eval/scenarios/t3-chaos-low-rate-intermittent.yaml`
4. The quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`

## Manual checks

5. The leader reads the recalibrated matchers against the journals the pin names, and confirms that no
   alternation was widened beyond the wording of those journals. who: the leader. Not automatic: it is a
   reading of meaning, and a calibration pinned on the same nine journals must not become overfitting.
