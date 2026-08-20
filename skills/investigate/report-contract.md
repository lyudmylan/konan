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
konan_journal: 1                # contract version; scorers refuse versions they don't know
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
  scores as a miss.
- **`usage.tokens`** is `null` only when the run genuinely could not capture totals
  (interactive sessions); eval runs must fill it — cost-per-investigation is a
  first-class output.

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
   the scenario fixture's expected class, must-claim and must-not-claim lists, applied
   to the machine core only.

The in-loop judge is part of the system being measured; it never fills the scorecard.
The scorer never interprets; it parses and compares. That separation is why the
machine core exists.

## Versioning

Breaking changes bump `konan_journal`. A scorer refuses a version it does not know —
a wrong score is worse than no score.
