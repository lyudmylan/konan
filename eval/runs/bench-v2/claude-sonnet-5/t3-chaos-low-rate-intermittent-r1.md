---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-intermittent-503-chaos-toggle
  trigger: manual
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-11-02T22:58:28Z
  concluded: 2026-11-02T23:04:28Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos/degradation toggle was switched on (POST /chaos/enable, failure_rate=0.08, error_status=503, extra_latency_ms=0), injecting random 503s on an ~8% subset of requests to routes such as /products/{id} while other requests to the same routes succeed."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal chaos/degradation toggle in faultline was switched on at 2026-11-02T22:58:18.528Z (failure_rate=0.08, error_status=503, extra_latency_ms=0) and remains on, causing a random ~8% subset of requests to routes such as GET /products/1 and GET /products/5 to fail with HTTP 503 while other requests to the same routes succeed."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7]
    evidence_against: []
  - id: H2
    statement: "The 503s on /products/1 and /products/5 are caused by a software defect (unhandled exception or data-dependent bug) in faultline's product-lookup code."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E10]
  - id: H3
    statement: "The 503s stem from an upstream/downstream contract mismatch or a gateway-tier failure between two parties, not an internal switch inside the target."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:58:18.528Z"
    quote: '{"ts": "2026-11-02T22:58:18.528Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "daac0ff27835", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:58:19.898Z"
    quote: '{"ts": "2026-11-02T22:58:19.898Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "8bc955f4966e", "event": "chaos_failure", "method": "GET", "path": "/products/5"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:58:19.898Z"
    quote: '{"ts": "2026-11-02T22:58:19.898Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "8bc955f4966e", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 0.135, "client": "127.0.0.1:62089"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:58:19.953Z"
    quote: '{"ts": "2026-11-02T22:58:19.953Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e79608594162", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:58:19.953Z"
    quote: '{"ts": "2026-11-02T22:58:19.953Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "e79608594162", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.128, "client": "127.0.0.1:62093"}'
  - id: E6
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1793660357-9636, 2026-11-02T22:59:17Z"
    quote: "faultline_chaos_enabled 1"
  - id: E7
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1793660357-9636, 2026-11-02T22:59:17Z"
    quote: 'http_requests_total{method="GET",path="/products/1",status="503"} 1 / http_requests_total{method="GET",path="/products/5",status="503"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 15'
  - id: E8
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1793660357-9636, 2026-11-02T22:59:17Z"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter (no data rows follow — zero series)"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:58:13.592Z"
    quote: '{"ts": "2026-11-02T22:58:13.592Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:58:19.646Z"
    quote: '{"ts": "2026-11-02T22:58:19.646Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "909a8f7a115f", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.459, "client": "127.0.0.1:62071"}'
gaps:
  - "No access-log line for POST /chaos/enable itself appears in the captured window (/chaos is outside the probe allowlist by design, docs/lab.md); the toggle's trigger is inferred from the faultline.chaos logger entry (E1) and the adjacent POST /chaos/enable -> 200 access line sharing request_id daac0ff27835, not independently re-probed."
  - "Did not independently reproduce by probing /products/1 or /products/5 myself; the toggle's logged parameters (failure_rate, error_status) already matched the observed effects exactly and three independent lenses corroborated without disagreement, so an extra confirming probe was judged redundant and skipped to avoid adding investigator-triggered noise to the error-injection counters."
  - "No log history predates process startup at 2026-11-02T22:58:13.592Z (54-line log, fresh process) — whether chaos was toggled earlier in a prior process lifetime cannot be seen."
usage:
  model: claude-sonnet-5
  tokens: 2191465
  wall_clock_seconds: 360
---

# Shop intermittent 503s traced to an active chaos toggle

## Summary

**Root cause identified.** A chaos/degradation toggle inside faultline was switched on
(`POST /chaos/enable`, `failure_rate=0.08`, `error_status=503`, `extra_latency_ms=0`) and
is still active. It injects HTTP 503 on a random ~8% of requests to product-lookup routes
while the rest succeed with no added latency — exactly the shape reported: occasional
errors, success on retry, most users unaffected. Three independent discipline lenses
(infra-process, interfaces, software-defect) converged on the same explanation
independently, and an adversarial judge validated it against the cited evidence with no
disconfirming evidence found. Confidence: high. This is not "probably nothing" — it is a
real, currently-ongoing but low-impact degradation; see Safe next steps.

## Timeline

- **2026-11-02T22:58:13.592Z** — faultline process starts; clean single startup, no
  restart history (E9).
- **2026-11-02T22:58:18.528Z** — chaos mode enabled: `failure_rate=0.08`, `error_status=503`,
  `extra_latency_ms=0` (E1).
- **2026-11-02T22:58:19.646Z** — `GET /products/5` succeeds (200) shortly after the toggle
  (E10) — same route still serving most traffic normally.
- **2026-11-02T22:58:19.898Z** — chaos-injected failure fires on `GET /products/5` → 503
  (E2, E3).
- **2026-11-02T22:58:19.953Z** — chaos-injected failure fires on `GET /products/1` → 503
  (E4, E5).
- **2026-11-02T22:58:24Z** — human complaint received ("A couple of users mention an
  occasional error... works on retry...").
- **2026-11-02T22:58:28Z** — investigation started (trigger latency: 4s).
- **2026-11-02T22:59:13Z–22:59:17Z** — investigator baseline probes (`/health`, `/metrics`):
  chaos still enabled, exception counters still empty (E6, E7, E8).
- **2026-11-02T23:04:28Z** — investigation concluded.

## Investigation

**Complaint** (verbatim, from `/konan`): source `human`, fingerprint `human-1793660304`,
`labels.alertname: human-report` (no severity stated, none inferred), `annotations.summary`:
"A couple of users mention an occasional error in the shop over the last few minutes — it
works on retry, most people notice nothing. Probably nothing?", `startsAt`:
2026-11-02T22:58:24Z. Investigation start stamp: 2026-11-02T22:58:28Z. Trigger latency: 4s.

**Baseline** — `/health` returned `{"status":"ok","uptime_seconds":59.5}`; `/metrics`
already showed `faultline_chaos_enabled 1` and two `503`s on `/products/1` and
`/products/5` against mostly `200`s; the full log (54 lines, one process lifetime) showed
the toggle being enabled and the two chaos-injected failures directly. The anomaly was
visible in the baseline itself, before any lens ran.

**Triage** — all three lenses (infra-process, interfaces, software-defect) were spawned
in parallel, blind to each other, against the same baseline (the complaint was vague, so
no domain could be excluded up front). All three independently named the same mechanism:
an internal chaos toggle, class `infra-process`. The interfaces lens explicitly
reclassified it out of its own domain per the contract's classification rule. The
software-defect lens ruled out a code defect: zero exception-counter activity (E8) and the
same route (`/products/5`) succeeding elsewhere in the same burst (E10) rules out a
deterministic per-input bug.

**Deep-dive — skipped.** H1's evidence was already deterministic and complete: the log
directly states the injected mechanism's parameters (E1) and directly tags the two
failing requests with that mechanism via matching `request_id`s (E2–E5) — not an inferred
correlation. Per the loop's rule, a hypothesis this complete goes straight to the judge.

**Judge** — reviewed H1/H2/H3 against only the cited evidence, blind to this narrative.
Verdict: H1 validated, H2 invalidated, H3 invalidated. One caveat noted: no access-log
line for `POST /chaos/enable` itself appears in the window (it is outside the probe
allowlist), so the triggering call is inferred from the logger entry and the adjacent
200 sharing its request id — judged not to undermine the causal claim.

## Hypotheses

### H1 — chaos toggle injecting random 503s (validated)

The `faultline.chaos` logger recorded the toggle turning on with explicit parameters
(E1: `failure_rate=0.08, error_status=503, extra_latency_ms=0`). The two observed
failures are tagged by the app itself as `chaos_failure` on the *same request ids* that
produced the 503 responses (E2↔E3, E4↔E5) — direct causal attribution, not correlation.
`faultline_chaos_enabled 1` still read true over a minute later (E6), and the request
counts (2 failures / 17 requests ≈ 12%, consistent with an 8% rate at low sample size,
E7) match. No evidence against.

### H2 — software defect (invalidated)

No supporting evidence found. `http_exceptions_total` carries zero series (E8) — no
unhandled exception was recorded near either 503. `/products/5` returned 200 shortly
before its own failure (E10), so the failure is not a deterministic per-input bug. The
same request ids are already explained by H1's `chaos_failure` tag.

### H3 — interfaces / contract mismatch (invalidated)

No supporting evidence found. E1 is itself the record of an in-process switch
(`faultline.chaos` logger) — an internal mechanism, not a boundary component — which
directly contradicts the "not an internal switch" premise. No gateway, proxy, or
contract-violation evidence appears anywhere in the log or metrics.

## Safe next steps

- Watch `/metrics` for `faultline_chaos_enabled` and the growth of `{status="503"}`
  counters on `/products/*` routes to confirm the rate holds near the declared 8% and
  does not climb.
- Use the stamped `request_id` on any further user reports to confirm they fall inside
  this chaos-enabled window before attributing them to the same cause.
- Confirm, read-only, whether this toggle is an intentional/expected test state (recent
  journal history shows a similar toggle around a handover) and when it is expected to
  be turned off — this investigation makes no change and triggers nothing itself.

## Gaps

- No access-log line for `POST /chaos/enable` itself appears in the captured window
  (`/chaos` is outside the probe allowlist by design); the trigger is inferred from the
  logger entry (E1) and the adjacent 200 sharing its request id, not independently
  re-probed.
- Did not independently reproduce by probing `/products/1` or `/products/5` myself — the
  toggle's logged parameters already matched the observed effects exactly, and three
  independent lenses agreed with no disagreement, so an extra confirming probe was judged
  redundant and skipped to avoid adding investigator-triggered noise to the counters.
- No log history predates process startup at 2026-11-02T22:58:13.592Z (fresh process,
  54-line log) — whether chaos was toggled earlier in a prior process lifetime is not
  visible.
