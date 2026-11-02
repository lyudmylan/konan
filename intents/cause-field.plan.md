# Plan: the cause field of the journal (#78)

Intent: `intents/cause-field.md`. Written 2026-11-01; accepted by the leader on 2026-11-02, with the list
below in it.

## The closed list of causes

Twenty-eight ids, each in one incident class, none naming a target, an endpoint, or a seeded defect. The list
lives in the report contract next to the incident classes, and in the journal schema as the enum of
`root_cause.cause`; the schema is the one machine copy, and the scorer reads the list from it.

The two fields have two dimensions. The incident class is the discipline that finds and fixes the cause:
one class per lens (a software engineer, an SRE, an integration engineer, and so on). The cause id is the
mechanism the evidence proves: what broke and how, at the granularity of one resource, one process event,
one boundary, or one database behaviour. Three rules keep neighbouring ids apart, and the contract states
them next to the list:

- A resource that ran out: when demand rose, it is `load-saturation` and the id names the resource; when
  the target's own code grows without demand, it is `software-defect` `resource-leak`; when a cap of the
  platform was hit with neither, it is `infra-process` `platform-limit`.
- A third party: konan reads the target from outside and never sees inside a provider, so the `third-party`
  ids name what the boundary shows (errors, slowness, a quota, a wrong answer), not the provider's internal
  cause.
- The data layer: the `data-db` ids name what the database did (did not answer, answered slowly, hit a
  limit, held wrong data, disagreed with the code on the schema).

| Incident class | Cause id | Meaning |
| --- | --- | --- |
| software-defect | `unhandled-exception` | the target's own code raises on some input and the request fails |
| software-defect | `wrong-result` | the target's own code returns a wrong value without an error |
| software-defect | `resource-leak` | the target's own code holds memory, handles, or connections it never frees; growth without demand |
| load-saturation | `cpu-saturated` | demand exhausts the CPU |
| load-saturation | `memory-exhausted` | demand exhausts the memory |
| load-saturation | `connections-exhausted` | demand exhausts a connection pool, sockets, or descriptors |
| load-saturation | `workers-exhausted` | demand exhausts the threads or workers; queues back up |
| load-saturation | `bandwidth-saturated` | demand exhausts the network throughput |
| infra-process | `process-crashed` | the process exited, once and not restarted, or in a loop |
| infra-process | `process-hung` | the process is alive and does not serve |
| infra-process | `platform-limit` | the platform refused the process a resource with no rise in demand: disk full, a descriptor limit, a memory cap |
| infra-process | `degradation-switch` | an operational switch inside the target (chaos, kill switch, feature flag) injects errors or latency while on |
| infra-process | `config-change` | a changed configuration value altered the runtime behaviour |
| infra-process | `deployment-error` | a rollout put the wrong build, a partial rollout, or a missing dependency in place |
| third-party | `provider-outage` | an external provider returns errors or does not answer |
| third-party | `provider-latency` | an external provider answers slowly |
| third-party | `provider-quota` | an external provider rejects on a quota or a rate limit |
| third-party | `provider-wrong-result` | an external provider answers with wrong content |
| interfaces | `contract-mismatch` | a payload, schema, or version mismatch between two parties |
| interfaces | `gateway-failure` | a proxy, load balancer, or gateway tier fails on its own |
| interfaces | `auth-failure` | a boundary rejects credentials, a token, or a permission |
| interfaces | `certificate-expired` | a certificate at a boundary expired or was not rotated |
| interfaces | `connectivity-loss` | the network path between two parties is broken: DNS, routing, a firewall |
| data-db | `database-unavailable` | the database does not answer: down, refusing connections, in failover |
| data-db | `slow-queries` | queries answer slowly: a missing index, a bad plan, lock contention |
| data-db | `database-limit` | the database hit a limit of its own: storage, connections, throughput |
| data-db | `data-inconsistency` | a record or a state is wrong, missing, duplicated, corrupt, or out of sync |
| data-db | `schema-mismatch` | the schema of the database and the code disagree, after a migration or before one |

The ids are target-generic and come from the published incident studies named under "Facts": the
sub-categories of the Microsoft Teams study map onto the six classes, trimmed to what a read-only
investigator can prove from outside the target.

A later change to the list is a change to the report contract, through its own change request. After the
merge the contract table is the reference; this table is the record of the approval, and pin 21 holds the
contract table, the schema enum, and the six class pairs of the schema to one list.

## Steps

1. `skills/investigate/report-contract.md`: the machine core example says `konan_journal: 2` and
   `root_cause.cause: unhandled-exception  # one id of the cause list, in the class of the root cause`. A
   field note "Causes, defined" carries the table above and the three rules, after the incident classes. The section
   "Versioning" records version 2: the field, the reason (the benchmark cannot score a false attribution
   from prose), and that a version 1 journal stays valid against version 1.
2. `skills/investigate/journal.schema.json`: one file for both versions. `konan_journal` is `enum [1, 2]`;
   `root_cause.cause` is an enum of the twenty-eight ids, in `$defs.cause`; under version 2 the root cause
   requires `cause`, under version 1 it must not carry it; a `cause` outside its class is schema-invalid
   (six if/then pairs on the root cause, one per class), so the field agrees with `incident_class` by shape,
   not by review. The title names both versions.
3. `skills/investigate/SKILL.md`, "Conclusion — write the journal", the Verdict bullet: the root cause names
   its `cause`, one id of the contract's list, in the class of the root cause; the id states the mechanism,
   the statement the instance. The lenses and the judge do not change: the orchestrator writes the journal.
4. `eval/fixture.schema.json`: `konan_fixture: 2` (a new required field is a breaking change of the fixture
   format; every fixture of the repo changes in this change request). `expected.cause` is required: a string
   when the expected verdict is `root-cause-identified`, null otherwise. The membership in the list is the
   scorer's check (step 6), so the list has one machine copy.
5. The ten fixtures under `eval/scenarios/`: `konan_fixture: 2` and `expected.cause`:
   `degradation-switch` for `chaos-error-rate`, `chaos-latency`, `t2-red-herring-latency-latent-d1`,
   `t3-chaos-low-rate-intermittent`; `process-crashed` for `t3-crash-hard-down`; `unhandled-exception` for
   `d1-zero-stock-product-page` and `d2-null-price-order`; null for `healthy-baseline`,
   `t2-healthy-after-chaos-window`, `t2-quiet-d1-suggestive-complaint`. The `must_not_claim` lists stay:
   they score version 1 journals. One known limit, stated in the fixture notes of `d2-null-price-order`:
   the two seeded defects share the id `unhandled-exception`, so a version 2 journal that blames the other
   defect is caught by the `must_claim` entries on the mechanism and the operation, not by the cause.
6. `eval/score.py`: `load_journal` accepts versions 1 and 2 and refuses the rest (pin 10 keeps its version
   99). The cause ids are read from the journal schema. `load_fixture` refuses a fixture whose
   `expected.cause` is a string outside the list (`InputError`, exit 2). `score_pair`: on a version 2
   journal with the verdict `root-cause-identified`, the false attributions are `[]` when
   `root_cause.cause == expected.cause` and otherwise one entry, `cause:<got>`; the row gains `cause_got`
   and `cause_expected`; the `must_not_claim` entries are not evaluated. A version 2 root-cause journal on a
   fixture that expects no root cause is a verdict miss and one false attribution, as the prose tripwires
   were for version 1. A version 1 journal scores as today. The scorecard's failure detail prints the
   cause line as "cause: got `x`, want `y` — false attribution"; `eval/bench.py` counts the entries as it
   does and does not change.
7. `eval/tests.py`: `base_fx` gains `expected.cause` (`unhandled-exception`, null for the healthy form) and
   `konan_fixture: 2`; `base_core` keeps version 1, and `base_core_v2()` is version 2 with the cause
   `unhandled-exception`. The 18 semantics pins, the runner pins and the coverage pins keep their asserts.
   Five new pins, 19 to 23, each citing its check:
   - 19 "cause equality, denial in prose" (check 1): a version 2 journal whose cause equals the expected
     cause and whose root-cause statement says "chaos is not the cause" and "not a chaos toggle" scores
     no false attribution and passes; the same statement in a version 1 journal fires `not-chaos`, which
     is the artifact the field removes.
   - 20 "cause inequality" (check 2): the fixture expects `wrong-result`, the journal says
     `unhandled-exception`, same class: one false attribution, `cause:unhandled-exception`, with
     `cause_expected` `wrong-result` on the row; `passed` false; the class check still passes.
   - 21 "fixture cause ids" (check 4): every live fixture loads, its cause is in the list or null exactly
     when its verdict is not `root-cause-identified`; a fixture with the cause `made-up` raises
     `InputError`; a root-cause fixture with the cause null is schema-invalid and raises `InputError`.
     The same pin reads the table under "Causes, defined" in the contract and asserts that its ids equal
     `$defs.cause`, that the union of the six class enums of the schema equals `$defs.cause`, and that
     the class of each id is the same in the table and in the schema pair: one list, four copies.
   - 22 "journal cause id" (check 5): a version 2 journal with the cause `made-up` fails citation
     compliance and does not pass, with no `InputError`; so does one whose cause is `process-crashed` under
     the class `software-defect`.
   - 23 "versions" (check 3): the committed sample journal, version 1, still passes the D1 fixture with the
     field in it; version 3 is refused like version 99.
   The closing line says 23 pins. Check 3 is the existing pins 0 to 18, unchanged in their asserts.
8. `eval/README.md`: the fixture format shows `konan_fixture: 2` and `expected.cause`; the scoring
   semantics state the false attribution of version 2 as an inequality of ids and the version 1 rule as
   the rule for version 1 journals; the paragraph on the lookbehind guard becomes a note on version 1
   journals, the committed bench-v1 journals among them, and its pointer to this work item becomes the
   statement of the rule. `eval/BENCHMARK.md`, "What is measured": the two lines on passed and false
   attributions name the version 2 rule next to the version 1 rule, so the protocol and the scorer agree.
9. `docs/product.md`, the line "Out of scope for v0.2": "report contract v2 (except its cause field, pulled
   forward because the benchmark cannot score false attributions from prose)". `skills/**` is a code path,
   so this document change is the one the contract asks for.
10. The two commands of `AGENTS.md`, then checks 1 to 7 of the intent: five by `uv run eval/tests.py`, two
    commands. Check 8, the smoke run: one runner invocation on `d1-zero-stock-product-page` with one model
    (`--run-id smoke-78 --repeat 1 --fixtures eval/scenarios/d1-zero-stock-product-page.yaml`), after the
    leader's go in the conversation, because it calls the model and the lab; its journal, version 2 with a
    cause from the list, and its sidecar are committed under `eval/runs/smoke-78/` as the evidence of the
    check. One change request, `Closes #78`, on this branch.

## Files

`skills/investigate/report-contract.md`, `skills/investigate/journal.schema.json`,
`skills/investigate/SKILL.md`, `eval/fixture.schema.json`, the ten fixtures under `eval/scenarios/`,
`eval/score.py`, `eval/tests.py`, `eval/README.md`, `eval/BENCHMARK.md`, `docs/product.md`,
`eval/runs/smoke-78/` (new), and this file. `eval/bench.py`, `eval/run.py`, the lenses, the committed journals under `journals/` and
`eval/runs/bench-v1/` do not change.

## Tests

Pins 19 to 23 of step 7. Pin 16 keeps loading every fixture against the new fixture schema, so a fixture
without `expected.cause` fails there. Pin 11 keeps the version 1 sample journal passing.

## Facts the plan rests on (as of this plan, 2026-11-01)

- The journal schema gates `root_cause` on the verdict with one if/then/else; `incident_class` is a free
  string there, by design (a lens may extend the taxonomy), so the cause-to-class pairs are the first shape
  rule on the class.
- The scorer's `JOURNAL_VERSION` is a single integer and `load_journal` refuses every other value; pin 10
  uses 99 as the unknown version, so it stays as it is.
- Seven of the ten fixtures expect a root cause; their mechanisms are three: a switch, a process exit, an
  unhandled exception on a data condition. Three fixtures expect `no-active-incident`.
- `eval/bench.py` reads `len(r["false_attributions"])` from the scorer's row and nothing else of it, so the
  cause entry needs no change there.
- No published standard fixes a closed list of root causes. ITIL leaves the categorization scheme to the
  organization and keeps it apart from the root cause. The Google SRE Workbook (Appendix C) trends two
  coarse dimensions, the trigger and the root cause, over its own postmortems. The Microsoft Teams study
  (Ghosh et al., SoCC 2022) classifies 152 incidents into seven categories with sub-categories: software
  bugs, infrastructure (capacity), deployment errors, configuration bugs, dependency failures, database or
  network, auth failures. Microsoft's AutoARTS (USENIX ATC 2023) has 346 leaf tags in a hierarchy and
  argues that one root cause is too few. The outage study of Gunawi et al. (SoCC 2016) uses UPGRADE,
  NETWORK, BUGS, CONFIG, LOAD, CROSS, POWER, NATDIS. The list above takes the Teams sub-categories, which
  map onto the six classes, at the granularity a read-only investigator can prove.
