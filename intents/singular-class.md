# Intent: one incident class per chaos fixture

Work item: #77. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

Every live fixture states the one incident class that the report contract has decided, so a run after
bench-v1 scores a misclassified degradation switch as a miss.

## In scope

- `eval/scenarios/chaos-error-rate.yaml`, `eval/scenarios/chaos-latency.yaml`,
  `eval/scenarios/t2-red-herring-latency-latent-d1.yaml`, `eval/scenarios/t3-chaos-low-rate-intermittent.yaml`:
  `incident_class: infra-process`, a string. The transition comments ("set accepted for bench-v1 journals")
  go.
- `eval/fixture.schema.json` and pin 15 of `eval/tests.py` keep the set form: a fixture with a true
  ambiguity may still state a set, with its reason in `scoring_notes`. No live fixture uses it after this
  change.
- `eval/tests.py`: one pin — the four fixtures load with the string `infra-process`, and one committed
  bench-v1 journal that answered `interfaces` on one of them fails on class against the live fixture. The
  reversion is a check, not a comment.
- `eval/BENCHMARK.md`, section "Regenerating it": one sentence states that re-scoring the bench-v1 journals
  against the live fixtures fails those four scenarios on class, and that this is the design: bench-v1 is
  scored as pre-registered at its own commit.

## Out of scope

Re-scoring bench-v1. The tier-3 matchers (#75). The scorer, the journal schema, and the cause field (#78).
The lens text of the investigate skill: it carries the definitions since #63 and does not change.

## Acceptance checks

## Automatic checks

1. The four fixtures load with the string `infra-process` as their expected class.
   test: `eval/tests.py`, the pin "singular class". command: `uv run eval/tests.py`
2. A committed bench-v1 journal with class `interfaces` on one of the four scenarios fails on class
   against the live fixture.
   test: the same pin, second case.
3. No fixture carries the transition comment.
   command: `! grep -rq 'set accepted for bench-v1' eval/scenarios/`
4. The quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`

## Manual checks

None: the committed journals and the fixtures are the whole ground of this change.
