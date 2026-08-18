# Eval corpus — scenarios with ground truth

This directory is the eval side of konan: labeled scenarios
(`scenarios/<id>.yaml`, shape-enforced by [`fixture.schema.json`](fixture.schema.json))
that stage a condition on the lab, hand the investigator a fixed complaint, and define
what a correct report must and must not claim. The scorer consumes a fixture plus a
journal's machine core; it never interprets prose.

## Blinding contract

Ground truth lives here **because** the investigator never looks here. An
investigation session may touch only the target's surface contract (`docs/lab.md`:
`scripts/probe.sh` + files under `lab/`). Explicitly out of bounds during an
investigation:

- `eval/` — fixtures name defect triggers and expected causes.
- The issue tracker (`gh`) — issue and PR bodies name defect triggers.
- The faultline checkout (`../faultline`) — its SPEC documents the seeded defects.
- Anything else outside the surface contract; past journals in `journals/` are the
  one deliberate exception (incident memory is legitimate practice — ground truth is
  not).

Today this contract is enforced by the investigate skill's setup rule ("touch nothing
outside the surface contract") and by session discipline during manual runs. The eval
runner makes it mechanical: an eval investigation runs in a session whose permissions
deny `gh` and reads outside the repo, with a hook rejecting reads under `eval/` —
that enforcement lands with runner automation (post-v0.1, with the CI gate).

## Fixture format

```yaml
konan_fixture: 1                # fixture contract version
scenario:
  id: d1-zero-stock-product-page
  title: ...                    # one line, human
setup:
  lab: fresh                    # fresh = restart the lab (clean logs/counters) before staging
  stage:                        # eval-side staging, in order; investigator never sees this
    - scripts/scenario.sh get /products     # `get` = seeded user traffic (unstamped ids)
    - sleep 1                               #   — scenarios asserting user impact MUST
    - scripts/scenario.sh get /products/3   #   seed it, or the honest verdict is latent
  notes: ...                    # staging intent, optional
complaint: "..."                # handed to the investigator VERBATIM — fixed per
                                #   scenario so runs are comparable
expected:
  verdict: root-cause-identified    # | no-active-incident | inconclusive
  incident_class: software-defect   # expected root_cause.incident_class; null when
                                    #   verdict is not root-cause-identified
  must_claim:                   # ALL entries must match for a root-cause hit
    - id: mechanism
      all_of: ["(?i)zero.?division"]   # every regex in all_of must match the claim surface
  must_not_claim:               # ANY match = a false attribution
    - id: not-chaos
      any_of: ["(?i)chaos"]
scoring_notes: ...              # nuances the scorer implementer must honor, optional
```

## Scoring semantics (the scorer implements exactly this)

- **Claim surface** = `root_cause.statement` + the `statement` of every hypothesis
  with `state: validated`, concatenated. Nothing else — not prose, not invalidated
  or inconclusive hypotheses (killed hypotheses are results, not claims), and not
  `latent_findings` (see the healthy nuance below).
- **Verdict**: `journal.verdict == expected.verdict`.
- **Class**: when a root cause is expected, `root_cause.incident_class ==
  expected.incident_class`.
- **Root-cause hit**: every `must_claim` entry matches — an entry matches when each
  regex in its `all_of` finds a match somewhere in the claim surface.
- **False attribution**: any `must_not_claim` entry with any `any_of` regex matching
  the claim surface — evaluated only on journals whose verdict is
  `root-cause-identified`, because only then does the machine core claim an active
  cause. (A correct no-active-incident journal may legitimately *mention* defect
  vocabulary in a validated "checks performed" hypothesis; promoting a phantom cause
  flips the verdict, and the tripwires fire on the root cause it then has to state.)
- **Citation compliance** is fixture-independent: schema validity of the journal plus
  referential integrity (every cited `E<n>` resolves; `root_cause.hypothesis` names a
  validated hypothesis) — per the report contract's enforcement layers.
- Regexes are Python-flavored, applied with `re.search`; case-insensitivity is spelled
  in the pattern (`(?i)`), never assumed. Matchers live in fixtures so the scorer stays
  target-generic — no target string ever appears in scorer code.

## Scoring a run

```sh
uv run eval/score.py --pair eval/scenarios/<id>.yaml journals/<id>.md [--pair ...] \
  [-o eval/scorecard.md]
```

- Pairs are explicit: journals are blind to scenarios (blinding contract), so the
  journal→fixture mapping is the run's knowledge, never the journal's.
- Exit codes: `0` all scenarios passed; `1` scored, with failures — the CI-gate
  signal; `2` broken input, refused. The line matters: an invalid **fixture** or an
  unreadable/unknown-version journal is a broken harness (refused, nothing rendered);
  a schema-invalid **journal** is a failing report (scored, citation-noncompliant).
- A scenario passes when the verdict matches, the class matches (when one is
  expected), every `must_claim` entry hits, no `must_not_claim` fires, and the
  journal is citation-compliant (contract schema + referential integrity: references
  resolve, the root cause names a validated hypothesis, wall clock matches the
  timestamps).
- The scorer's semantics are pinned by `uv run eval/tests.py` — run it after any
  change to the scorer, either schema, or the semantics in this README.

**Running the corpus, v0.1 (manual):** per fixture — restart the lab, execute the
`stage` list (`scenario.sh` prompts by design), run the investigate skill in a fresh
session handing it the fixture's `complaint` verbatim (blinding contract in force),
then score all pairs into `eval/scorecard.md`. Runner automation is post-v0.1.

**The healthy-baseline nuance** (discovered in #9's smoke runs): on faultline the
seeded defects are permanently latent — a competent read-only investigator will find
D1 on a perfectly healthy system. The healthy scenario therefore expects
`no-active-incident` with latent findings *permitted and unpenalized* (the claim
surface excludes `latent_findings` by construction), while its `must_not_claim`
entries fire if a latent defect is promoted to the active incident. "Found nothing"
is not the bar; "didn't invent an incident" is.

**The observer effect**: scenarios asserting user impact seed non-investigator
traffic (`scenario.sh get` / `order` — unstamped request ids) in their `stage` block.
Without seeded traffic the investigator's own `konan-*` probes are the only trigger
evidence, and the honest conclusion is "mechanism proven, user impact not evidenced".

## Corpus — coverage by tier and incident class

Tier 1 = single cause, evidenced (corpus v1, the regression gate). Tier 2 = attribution
traps and a healthy battery (the null verdict under pressure, past vs present). Tier 3 =
faint or dead surfaces. Tiers 2–3 landed with corpus v2 (#49); their matchers are
calibrated on the tier-1 known-good journals where the mechanism is shared, and marked
first-cut where no journal exists yet.

| Tier | Scenario | Class exercised | Expected verdict |
| --- | --- | --- | --- |
| 1 | `d1-zero-stock-product-page` | software-defect (data-dependent, GET path) | root-cause-identified |
| 1 | `d2-null-price-order` | software-defect (data-dependent, write path — log-driven) | root-cause-identified |
| 1 | `chaos-error-rate` | infra-process (degradation switch, error mode; config-change marker) | root-cause-identified |
| 1 | `chaos-latency` | infra-process (degradation switch, latency-only — no errors) | root-cause-identified |
| 1 | `healthy-baseline` | — (no incident) | no-active-incident |
| 2 | `t2-quiet-d1-suggestive-complaint` | — (complaint asserts errors; telemetry shows none; D1 latent) | no-active-incident |
| 2 | `t2-red-herring-latency-latent-d1` | infra-process (latency is the incident; latent D1 in plain sight) | root-cause-identified |
| 2 | `t2-healthy-after-chaos-window` | — (a closed degradation window; counters and old logs remain) | no-active-incident |
| 3 | `t3-crash-hard-down` | infra-process (process exited; logs the only surviving surface) | root-cause-identified |
| 3 | `t3-chaos-low-rate-intermittent` | infra-process (8% failure rate; faint signal, dismissive complaint) | root-cause-identified |

**Classes this lab cannot exercise** (stated so corpus scores are never read as
methodology completeness — see the lab gaps in `docs/lab.md`): `load-saturation`
(no real load generator; injected latency is the flag, not load), `third-party` (no
external dependency), `data-db` (no real database; the seeded rows stand in for data
issues but the failure mode is application code), and the gateway shapes of
`interfaces` (no proxy tier — no genuine 502/504 path).

Corpus-next, after v1 scores exist: migrate ai-incident-investigator's adversarial
corpus; add `/simulate`-based process scenarios (crash → hard-down with logs as the
only surviving surface; memory ballast → resource-growth shape).
