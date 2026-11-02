# Investigation journal — the report contract

Every investigation ends in exactly one file: the **journal**. It is both deliverables
at once — the report a human reads and the record the eval scorer consumes — as two
layers of the same file, so the two can never drift:

- **Machine core** — YAML frontmatter, shape-enforced by
  [`journal.schema.json`](journal.schema.json). Everything scoring needs: verdict,
  hypotheses with states, evidence with verbatim quotes, gaps, usage.
- **Human body** — markdown narrative: summary, timeline, the investigation as it
  unfolded, hypothesis discussion, safe next steps.

The scorer reads the machine core only; prose is never scored. A claim that is not in
the machine core was not concluded, however confident the prose sounds — and a claim
in the machine core without evidence references does not validate against the schema.
That is the contract's teeth: evidence citation is enforced by schema, not by review.

## File

`journals/<id>.md`, where `id` is `YYYY-MM-DD-<slug>` — start date plus a short
incident slug. Eval runs may write the same format elsewhere; the contract is the
content, not the location.

## Machine core

```yaml
konan_journal: 2                # contract version (1 or 2); scorers refuse versions they don't know
investigation:
  id: 2026-07-30-example        # matches the filename
  trigger: manual               # what started this, as text: manual | alert-inbox (profile,
                                #   delivery facts). Fields arrive with contract v2 (#24)
  complaint: "..."              # verbatim, as reported — never normalized
  started: 2026-07-30T10:00:00+03:00
  concluded: 2026-07-30T10:12:00+03:00
target:
  name: faultline
  surface_contract: docs/lab.md # the document defining what could be probed
verdict: root-cause-identified  # | no-active-incident | inconclusive
root_cause:                     # required iff verdict is root-cause-identified
  hypothesis: H1                # must point at a validated hypothesis
  statement: "..."              # one sentence, the causal mechanism
  incident_class: software-defect
  cause: unhandled-exception    # v2: one id of the list "Causes, defined", in the class of the root cause
hypotheses:
  - id: H1                      # H1, H2, ... in the order first formed
    statement: "..."            # cause statement: what broke, by what mechanism
    incident_class: software-defect
    state: validated            # validated | invalidated | inconclusive — the judge's verdict
    evidence_for: [E1, E2]      # references into evidence; at least one entry
    evidence_against: []        #   across the two lists, or the schema rejects it
latent_findings:                # defects real but not the incident (e.g. only
  - statement: "..."            #   investigator probes ever triggered them); optional
    evidence: [E3]
evidence:
  - id: E1                      # E1, E2, ... — the single evidence ledger
    type: log                   # log | metric | probe
    source: "lab/logs/app.log @ 2026-07-30T07:01:02Z"
    quote: "..."                # VERBATIM — trimmed, never paraphrased
gaps:                           # what could not be checked, and why; [] must be a
  - "..."                       #   deliberate statement that nothing was out of reach
usage:
  model: claude-fable-5         # the model that ran the investigation
  tokens: null                  # total tokens, or null when the run couldn't capture them
  wall_clock_seconds: 720       # must equal concluded − started
```

Field notes:

- **`verdict`** is the incident-level conclusion. `no-active-incident` is a legitimate
  verdict and still requires evidence — the checks performed are the citations. Latent
  findings ride along without changing the verdict.
- **`hypotheses`** is the complete list considered seriously enough to test, including
  the invalidated and inconclusive ones — killed hypotheses are results, and false
  attributions are scored from this list.
- **Incident classes, defined** (benchmark finding 2026-08-19, #63: models split on
  injected degradation — the definitions below make the call explicit):
  - `software-defect` — the target's own code produces a wrong result or an unhandled
    error for some input; deterministic per-input is the classic shape.
  - `load-saturation` — demand exceeds capacity: queues, resource exhaustion, gradual
    degradation under volume.
  - `infra-process` — the process and the platform it runs on, **including internal
    operational switches**: lifecycle (crash, restart, hang), resources, and
    configuration/feature/chaos toggles that change runtime behavior. An injected
    degradation switch is `infra-process` even when its symptom is gateway-shaped
    statuses or added latency.
  - `third-party` — an external provider's fault: their outage, their quota, their bug.
  - `interfaces` — a **contract surface between parties**: upstream/downstream API
    mismatches, malformed payloads, schema drift, a proxy/gateway tier's own failures.
    Requires an external party or a boundary component; an internal switch is not
    `interfaces`.
  - `data-db` — the data layer: corrupt/missing/inconsistent data, database failures.
- **`incident_class`** comes from the taxonomy: `software-defect`, `load-saturation`,
  `infra-process`, `third-party`, `interfaces`, `data-db`. A new lens may extend the
  taxonomy; scenario fixtures pin the expected class per scenario, so an invented class
  scores as a miss. Under contract v2 the root cause also names its `cause` (the list
  under "Causes, defined", below).
- **`usage.tokens`** is `null` only when the run genuinely could not capture totals
  (interactive sessions); eval runs must fill it — cost-per-investigation is a
  first-class output.

### Causes, defined

Contract v2 (#78). `root_cause.cause` names the mechanism of the root cause with one id of
the list below, in the class of the root cause: the schema rejects a cause outside its
class, and the eval scorer compares the id with the fixture's expected cause by equality —
a false attribution is an inequality of ids, never a reading of prose, so a report may deny
a cause in words freely. The id states the mechanism; the statement states the instance.

The two fields have two dimensions. The incident class is the discipline that finds and
fixes the cause: one class per lens (a software engineer, an SRE, an integration engineer,
and so on). The cause id is the mechanism the evidence proves: what broke and how, at the
granularity of one resource, one process event, one boundary, or one database behaviour.
Three rules keep neighbouring ids apart:

- **A resource that ran out.** When demand rose, it is `load-saturation` and the id names
  the resource. When the target's own code grows without demand, it is `software-defect`
  `resource-leak`. When a cap of the platform was hit with neither, it is `infra-process`
  `platform-limit`.
- **A third party.** konan reads the target from outside and never sees inside a provider,
  so the `third-party` ids name what the boundary shows (errors, slowness, a quota, a wrong
  answer), not the provider's internal cause.
- **The data layer.** The `data-db` ids name what the database did: did not answer,
  answered slowly, hit a limit, held wrong data, disagreed with the code on the schema.

| Class | Cause id | Meaning |
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

The list is target-generic: no name of a target, an endpoint, or a seeded defect. A change
to the list is a change to this contract, through its own change request.

## Citation discipline

Every evidence entry is one observed fact, quoted verbatim:

- **`log`** — `source` is the file plus the quoted line's timestamp; `quote` is the
  line itself (trim unrelated fields if long, never alter kept ones).
- **`metric`** — `source` is where the metric was read; `quote` is the metric name,
  labels, and value as scraped.
- **`probe`** — `source` is the probed path plus its request id; `quote` is the
  response body or trailer line, verbatim.

Hypotheses cite by reference (`E<n>`), never by restating. The schema enforces shape
(every hypothesis carries at least one reference); the scorer enforces resolution
(every reference names an existing entry). Between them: no citation, no claim.

## Body

After the frontmatter, these sections in order:

1. **`# <title>`** — one line naming the incident.
2. **`## Summary`** — verdict first, then mechanism, impact, and confidence in a
   paragraph a responder can act on without reading further.
3. **`## Timeline`** — key events with timestamps, each anchored to evidence ids;
   include configuration/deploy/flag-change markers found in telemetry.
4. **`## Investigation`** — the rounds as they ran: baseline, triage lenses spawned,
   deep-dives, judge verdicts. Brief — this is the audit trail, not a novel.
5. **`## Hypotheses`** — one subsection per hypothesis: statement, final state, the
   for/against evidence discussed in prose (referencing `E<n>` ids).
6. **`## Safe next steps`** — read-only suggestions only; remediation never appears
   in a journal.
7. **`## Gaps`** — the frontmatter list, elaborated.

## Enforcement layers

1. **Schema** (`journal.schema.json`, JSON Schema 2020-12, strict — unknown fields are
   errors): field shapes, enums, id patterns, at-least-one-citation per hypothesis,
   `root_cause` required exactly when the verdict claims one.
2. **Scorer** (deterministic, eval-side): referential integrity — every `E<n>`
   reference resolves, `root_cause.hypothesis` names a `validated` hypothesis,
   `wall_clock_seconds` matches the timestamps — then ground-truth comparison against
   the scenario fixture's expected class, expected cause (v2: equality of ids),
   must-claim list, and must-not-claim list (v1 only), applied to the machine core only.

The in-loop judge is part of the system being measured; it never fills the scorecard.
The scorer never interprets; it parses and compares. That separation is why the
machine core exists.

## Versioning

Breaking changes bump `konan_journal`. A scorer refuses a version it does not know —
a wrong score is worse than no score.

- **v2** (#78): `root_cause.cause`, one id of the list under "Causes, defined", required
  when the verdict is `root-cause-identified`. The reason: the benchmark cannot score a
  false attribution from prose — a correct report that denied a cause in words was scored
  as if it had claimed it. A version 1 journal stays valid against version 1: the schema
  validates both versions, and a version 1 journal carries no `cause`.
