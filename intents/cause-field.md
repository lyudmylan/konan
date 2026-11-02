# Intent: the cause field of the journal

Work item: #78. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The scorer compares the cause of a journal by equality on a field, so a correct report that denies a cause in
prose never scores as a false attribution.

## In scope

- `skills/investigate/report-contract.md`: `konan_journal: 2` adds `root_cause.cause`, one id from a closed
  list that the contract defines next to the incident classes. The list is target-generic: no name of a
  target, an endpoint, or a seeded defect; each id belongs to one incident class. The list is part of the
  approval of this work item: `intents/cause-field.plan.md` states it in full before any code, the leader
  accepts the plan with the list in it, and a later change to the list is a change to the contract that goes
  through its own change request. `root_cause.cause` lives inside `root_cause`, which the schema requires
  exactly when the verdict is `root-cause-identified`; a journal with another verdict has no cause, and the
  fixture of such a scenario states `expected.cause: null`. The section "Versioning" records the bump and the
  reason.
- `skills/investigate/journal.schema.json`: the field and its enum under version 2; a version 1 journal
  stays valid against version 1.
- `skills/investigate/SKILL.md`, and the lens or judge text that fills the root cause: the investigator
  writes the field from the list, and the field agrees with `incident_class`.
- `eval/fixture.schema.json` and the ten fixtures under `eval/scenarios/`: `expected.cause`, one id, or
  null when no root cause is expected; the fixture format goes to `konan_fixture: 2`, because a new
  required field is a breaking change of the format.
- `eval/score.py`: it reads versions 1 and 2. A version 1 journal scores as today. On a version 2 journal
  with the verdict `root-cause-identified`, a false attribution is `root_cause.cause` not equal to
  `expected.cause`, and the `must_not_claim` prose entries are not evaluated. `must_claim` stays a prose
  check on the claim surface, where a hit is the thing measured. A fixture whose `expected.cause` is not in
  the list is refused as broken input (exit 2); a journal whose `cause` is not in the list is schema-invalid,
  and so a failing report.
- `eval/tests.py`: the pins of the version 2 semantics, below; the version 1 pins unchanged.
- `eval/README.md`: the scoring semantics of version 2; the paragraph on the limits of the lookbehind guard
  becomes a note on version 1 journals. `eval/BENCHMARK.md`: the lines on passed and false attributions
  name the version 2 rule next to the version 1 rule.
- `docs/product.md`, section v0.2: report contract v2 stays out of scope except this field, pulled forward
  because the benchmark cannot score false attributions from prose.

## Out of scope

The rest of report contract v2 — severity (#24), routing (#23), memory (#28), pacing (#29), epic #37: one
field, not the set. A negation pass over prose in the scorer. Re-scoring bench-v1 under version 2. The
existing committed journals under `journals/` and `eval/runs/` stay version 1; the smoke run of check 8 adds
one version 2 journal.

## Acceptance checks

## Automatic checks

1. A version 2 journal whose `cause` equals the expected cause scores no false attribution, whatever its
   prose says — the pin states "chaos is not the cause" and "not a chaos toggle" in the root-cause
   statement.
   test: `eval/tests.py`, the pin "cause equality, denial in prose". command: `uv run eval/tests.py`
2. A version 2 root-cause journal whose `cause` differs from the expected cause scores one false
   attribution, named by the two ids.
   test: `eval/tests.py`, the pin "cause inequality".
3. A version 1 journal scores as before: the existing pins pass unchanged, and the committed sample journal
   still passes the D1 fixture.
   test: `eval/tests.py`, pins 0 to 18. command: `uv run eval/tests.py`
4. Every live fixture states an `expected.cause` that is an id of the list, or null exactly when its expected
   verdict is not `root-cause-identified`; a fixture with an id outside the list is refused with exit 2.
   test: `eval/tests.py`, the pin "fixture cause ids".
5. A version 2 journal with a cause id outside the list is a failing report, not an input error.
   test: `eval/tests.py`, the pin "journal cause id".
6. The product document states the exception in the out-of-scope line of v0.2.
   command: `grep -A3 'Out of scope for v0.2' docs/product.md | grep -q 'cause field'` (it proves the phrase in
   the line; the leader reads the sense at merge)
7. The quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`

## Manual checks

8. One runner smoke run on one tier-1 fixture produces a journal with `konan_journal: 2` and a cause from
   the list, and the journal scores a pass. who: the engineer. Not automatic: it calls the model and the lab
   on the operator computer and draws on the subscription.
