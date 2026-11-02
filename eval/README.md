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

In manual runs this contract is held by the investigate skill's setup rule ("touch
nothing outside the surface contract") and by session discipline. Runner runs make it
mechanical: `eval/run.py` starts each investigation in a detached git worktree of HEAD
with `journals/` emptied (no incident memory) and sets `KONAN_EVAL_BLIND=1`, which
switches the boundary hook (`hooks/boundary.py`) into eval-blind mode — Bash commands
that call `gh`, mention `eval/`, touch the faultline checkout, or run git against eval
are denied by content; Read/Grep/Glob/Edit/Write calls whose paths reach under `eval/`
or into faultline are denied too; a second denial freezes the session. The pins are in
`hooks/tests.py` (blind rows).

## Fixture format

```yaml
konan_fixture: 2                # fixture contract version
scenario:
  id: d1-zero-stock-product-page
  title: ...                    # one line, human
setup:
  lab: fresh                    # fresh = stop the lab, delete lab/logs, start it — clean counters AND logs
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
  cause: unhandled-exception        # expected root_cause.cause of a journal contract v2:
                                    #   one id of the contract's list ("Causes, defined");
                                    #   null when no root cause is expected
  must_claim:                   # ALL entries must match for a root-cause hit
    - id: mechanism
      all_of: ["(?i)zero.?division"]   # every regex in all_of must match the claim surface
  must_not_claim:               # ANY match = a false attribution on a journal contract v1
    - id: not-chaos             # carry the negation lookbehinds (see Scoring semantics)
      any_of: ["(?i)(?<!not )(?<!no )(?<!than )chaos"]
scoring_notes: ...              # nuances the scorer implementer must honor, optional
```

## Scoring semantics (the scorer implements exactly this)

- **Claim surface** = `root_cause.statement` + the `statement` of every hypothesis
  with `state: validated`, concatenated. Nothing else — not prose, not invalidated
  or inconclusive hypotheses (killed hypotheses are results, not claims), and not
  `latent_findings` (see the healthy nuance below).
- **Verdict**: `journal.verdict == expected.verdict`.
- **Class**: when a root cause is expected, `root_cause.incident_class` must equal
  `expected.incident_class` — or be a member of it when the fixture states a set
  (taxonomy ambiguity is a fixture decision, recorded with a reason; the class
  definitions live in the report contract).
- **Root-cause hit**: every `must_claim` entry matches — an entry matches when each
  regex in its `all_of` finds a match somewhere in the claim surface.
- **False attribution** — evaluated only on journals whose verdict is
  `root-cause-identified`, because only then does the machine core claim an active
  cause. (A correct no-active-incident journal may legitimately *mention* defect
  vocabulary in a validated "checks performed" hypothesis; promoting a phantom cause
  flips the verdict, and the check then runs on the root cause it has to state.)
  - Journal contract **v2**: `root_cause.cause != expected.cause` is one false
    attribution, named `cause:<got>`; the `must_not_claim` entries are not evaluated.
    Equality of ids, never a reading of prose — a report may deny a cause in words
    freely. A v2 root-cause journal on a fixture that expects no root cause is a verdict
    miss and one false attribution. A fixture whose `cause` is not in the contract's list
    is broken input (exit 2); a journal whose `cause` is not in the list, or not in the
    class of its `incident_class`, is schema-invalid — a failing report.
  - Journal contract **v1**: any `must_not_claim` entry with any `any_of` regex matching
    the claim surface.
- **Citation compliance** is fixture-independent: schema validity of the journal plus
  referential integrity (every cited `E<n>` resolves; `root_cause.hypothesis` names a
  validated hypothesis) — per the report contract's enforcement layers. The loader
  keeps YAML timestamps as the RFC3339 strings written, quoted or not — a model that
  copies the contract's unquoted example must not fail on a parsing accident.
- Regexes are Python-flavored, applied with `re.search`; case-insensitivity is spelled
  in the pattern (`(?i)`), never assumed. Note `(?i)` is a global inline flag in
  Python: it applies to lookbehinds too, so `(?<!not )` already blocks "Not" and "NOT"
  and a separate `(?<!Not )` is dead weight.
  Tripwire convention (v1 journals — the committed bench-v1 journals among them):
  `must_not_claim` vocabulary carries fixed-width negation lookbehinds
  (`(?<!not )(?<!no )(?<!than )`) so a correct report may *deny* a cause ("a defect, not
  chaos") without firing them.
  **Know what that guard does not cover.** Python requires a fixed-width lookbehind, so
  it only sees the characters immediately before the term. "not chaos" is blocked;
  "not **a** chaos toggle", "not **the** chaos switch" and "not resource saturation"
  are not — any intervening article defeats it, and those are the common phrasings in a
  real report. Nor can a lookbehind see a negation that *trails* the term ("chaos is not
  the cause"). Widening the alternation cannot fix this: it trades false positives for
  false negatives and never converges, because scoring prose for the *absence* of a
  claim is the wrong shape for a regex. The structural fix is the cause field of journal
  contract v2 (#78): the scorer compares ids by equality, and the guard matters only to
  v1 journals, where a `must_not_claim` hit on a report that reads as a denial is a known
  artifact, not a verdict. Matchers live in fixtures so the scorer stays target-generic —
  no target string ever appears in scorer code.

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
  expected), every `must_claim` entry hits, no false attribution is scored (v2: the
  cause id equals the expected one; v1: no `must_not_claim` fires), and the
  journal is citation-compliant (contract schema + referential integrity: references
  resolve, the root cause names a validated hypothesis, wall clock matches the
  timestamps).
- The scorer's semantics are pinned by `uv run eval/tests.py` — run it after any
  change to the scorer, either schema, or the semantics in this README.

**Running the corpus with the runner:**

```sh
uv run eval/run.py --run-id 2026-08-19-bench --model claude-sonnet-5 --repeat 3 \
  [--fixtures eval/scenarios/*.yaml] [--max-runs 5] [--timeout-min 30] [--dry-run]
```

Per (fixture, repetition) the runner gives the fixture a clean lab when it says
`setup.lab: fresh` (process restarted **and** `lab/logs` deleted — counters reset with
the process, log files do not), executes the `stage` list (operator side — the runner may use curl,
the investigator may not), runs `/konan <complaint verbatim>` in a fresh headless
session (`claude -p --model <m> --permission-mode acceptEdits`) inside a blinded
worktree, copies the journal to `eval/runs/<run-id>/<model>/<scenario>-r<n>.md`, writes
`<scenario>-r<n>.meta.json` from the run's JSON envelope (session id, turns, duration,
`modelUsage` = tokens for the whole run including subagents, API-equivalent cost,
permission denials), appends a line to `results.jsonl`, and finally scores every pair of
the run into `eval/runs/<run-id>/scorecard.md`. Runs already present are skipped
(resume with the same `--run-id`); the batch stops on a quota / rate-limit error.
Probabilistic fixtures (`--restage-check`, default: `chaos-error-rate`,
`t3-chaos-low-rate-intermittent`) must land at least one user-visible 5xx in the log
before the investigation starts — the runner restages up to three times and records the
count in the sidecar (`restages`). A run that exceeds `--timeout-min` is killed and
recorded as `timeout` (a failed run, not retried); two consecutive timeouts stop the batch.

**Tokens, defined:** the runner stamps the journal's `usage.tokens: null` with the
run's total tokens = input + output + cache-read + cache-creation across every model
call of the session, subagents included (from the envelope's `modelUsage`; the per-
category breakdown and the cost stay in the sidecar). Manual runs keep `null` honestly.
Wall clock in headless runs is clean (no human pauses); `duration_ms` in the sidecar is
the harness's own measurement.

**Manual runs** remain valid for exploration: restart the lab, execute the `stage` list
(`scenario.sh` prompts by design), run the investigate skill in a fresh session with
the fixture's `complaint` verbatim (blinding contract in force), score the pairs.
`eval/scorecard.md` stays the committed corpus-v1 scorecard (regression gate); benchmark
runs live under `eval/runs/`.

**The healthy-baseline nuance** (discovered in #9's smoke runs): on faultline the
seeded defects are permanently latent — a competent read-only investigator will find
D1 on a perfectly healthy system. The healthy scenario therefore expects
`no-active-incident` with latent findings *permitted and unpenalized* (the claim
surface excludes `latent_findings` by construction), while a promoted latent defect
is a false attribution (v2: a cause stated against an expected null; v1: its
`must_not_claim` entries fire). "Found nothing"
is not the bar; "didn't invent an incident" is.

**The observer effect**: scenarios asserting user impact seed non-investigator
traffic (`scenario.sh get` / `order` — unstamped request ids) in their `stage` block.
Without seeded traffic the investigator's own `konan-*` probes are the only trigger
evidence, and the honest conclusion is "mechanism proven, user impact not evidenced".

## Corpus — coverage by tier and incident class

Tier 1 = single cause, evidenced (corpus v1, the regression gate). Tier 2 = attribution
traps and a healthy battery (the null verdict under pressure, past vs present). Tier 3 =
faint or dead surfaces. Tiers 2–3 landed with corpus v2 (#49); their matchers are
calibrated on the tier-1 known-good journals where the mechanism is shared; the tier-3
matchers were first-cut until bench-v1 and are calibrated on its committed journals since
#75, pinned in `eval/tests.py`.

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
