---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-latency-slowness
  trigger: manual
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-19T02:27:22Z
  concluded: 2026-08-19T02:35:55Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime chaos-mode toggle (POST /chaos/enable) injected variable extra latency into every business-path route (/products, /products/{id}, /orders) starting 2026-08-19T02:27:01.187Z, making the shop feel painfully slow while /health and /metrics stayed fast."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "A runtime chaos-mode config toggle was flipped at 2026-08-19T02:27:01.187Z (configured failure_rate=0.0, error_status=503, extra_latency_ms=1500), injecting variable extra latency into /products, /products/{id}, and /orders while leaving /health and /metrics untouched, producing the sitewide slowness users reported."
    incident_class: interfaces
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "The 'error page' a user reported seeing once corresponds to a server-side 5xx response or unhandled exception recorded in faultline's own telemetry."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E14, E15]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:26:55.259Z"
    quote: '{"ts": "2026-08-19T02:26:55.259Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:26:56.008Z"
    quote: '{"ts": "2026-08-19T02:26:56.008Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "7f71c403e83d", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.092, "client": "127.0.0.1:54902"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:26:58.128Z"
    quote: '{"ts": "2026-08-19T02:26:58.128Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "80138fbb0fe2", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.92, "client": "127.0.0.1:54904"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:27:01.187Z"
    quote: '{"ts": "2026-08-19T02:27:01.187Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "ca1c83497ded", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:27:04.467Z"
    quote: '{"ts": "2026-08-19T02:27:04.467Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "072dbf27ec42", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1220.47, "client": "127.0.0.1:54907"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:27:11.824Z"
    quote: '{"ts": "2026-08-19T02:27:11.824Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "97b40945eb01", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1497.191, "client": "127.0.0.1:54910"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:27:13.426Z"
    quote: '{"ts": "2026-08-19T02:27:13.426Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "bef9bcbbce63", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 538.136, "client": "127.0.0.1:54911"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:28:09.953Z"
    quote: '{"ts": "2026-08-19T02:28:09.953Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787106489-39239", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.509, "client": "127.0.0.1:54936"}'
  - id: E9
    type: probe
    source: "/products via scripts/probe.sh @ 2026-08-19T02:30:52Z, request_id=konan-1787106652-39348"
    quote: "-- HTTP 200 in 0.135168s request_id=konan-1787106652-39348"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:30:52.680Z"
    quote: '{"ts": "2026-08-19T02:30:52.680Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1787106652-39348", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 132.36, "client": "127.0.0.1:54958"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:30:53.882Z"
    quote: '{"ts": "2026-08-19T02:30:53.882Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1787106652-39354", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 905.885, "client": "127.0.0.1:54959"}'
  - id: E12
    type: metric
    source: "/metrics @ 2026-08-19T02:30:58Z"
    quote: "faultline_chaos_enabled 1"
  - id: E13
    type: metric
    source: "/metrics @ 2026-08-19T02:30:58Z"
    quote: "http_request_duration_seconds_sum{method=\"GET\",path=\"/products/{product_id}\"} 2.664965125033632\nhttp_request_duration_seconds_count{method=\"GET\",path=\"/products/{product_id}\"} 3"
  - id: E14
    type: metric
    source: "/metrics @ 2026-08-19T02:30:58Z"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 4\nhttp_requests_total{method=\"GET\",path=\"/metrics\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 2\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3\nhttp_requests_total{method=\"POST\",path=\"/chaos/enable\",status=\"200\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2"
  - id: E15
    type: metric
    source: "/metrics @ 2026-08-19T02:30:58Z"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter"
gaps:
  - "The exact latency-injection distribution is unresolved: post-marker durations on the same route varied from 132ms to 1497ms rather than a flat +1500ms (E5, E6, E7, E9/E10, E11). Confirming whether this is randomized jitter or something else would require reading faultline's chaos-injection code, which is out of the investigator's reach by design (docs/lab.md, eval/README.md blinding contract)."
  - "The user's reported 'error page seen once' has no corresponding evidence anywhere in faultline's server-side telemetry: the complete single-process log (no rotation, 23 lines covering the entire process lifetime since E1) shows zero 4xx/5xx statuses and zero exception events, and http_exceptions_total has never incremented (E14, E15). It may be a client-side or gateway timeout artifact of the induced latency, a misattribution, or something outside this surface — browser/proxy/CDN telemetry is not part of the investigator's contract and could not be checked."
  - "The caller who triggered POST /chaos/enable (client 127.0.0.1:54906, request_id ca1c83497ded, E4) is not attributable beyond its client address — caller identity and the operator/eval trigger surface (scripts/scenario.sh) are outside the investigator's reach by design."
usage:
  model: claude-sonnet-5
  tokens: 2745307
  wall_clock_seconds: 513
---

# Shop-wide slowness from a chaos-mode latency injection

## Summary

**Root cause identified.** At 2026-08-19T02:27:01.187Z a runtime chaos-mode toggle was
flipped on faultline (`POST /chaos/enable`, E4: `failure_rate=0.0`, `error_status=503`,
`extra_latency_ms=1500`). From that instant, every probed request against the shop's
business routes — `/products`, `/products/{id}`, `/orders` — slowed from roughly 1-2ms to
somewhere between 132ms and 1497ms, sustained for at least the ~4 minutes this
investigation ran (E2/E3 pre-marker vs E5-E7/E9-E11 post-marker), while `/health` and
`/metrics` stayed sub-millisecond throughout (E8) and health checks stayed green — which
matches the complaint exactly ("Health checks are green and fast"). This is the classic
healthy-monitoring trap: the health endpoint is not on the affected code path. Confidence
is high: three independent triage lenses converged on the same mechanism, and a live
re-probe minutes later confirmed the degradation was still active and chaos mode was
still flagged on (E12).

The second complaint detail — "some also mention seeing an error page once" — could
**not** be confirmed. faultline's own telemetry shows zero 4xx/5xx responses and zero
exceptions across its entire process lifetime (E14, E15), and chaos is configured with
`failure_rate=0.0`, meaning it structurally cannot have emitted its own configured 503
(E4). This claim rides as an open gap, not a validated finding — see Gaps.

## Timeline

- **02:26:55.259Z** (E1) — process startup, only startup marker in the log; no restarts
  or crashes occurred during the investigation window.
- **02:26:55 - 02:26:58Z** (E2, E3) — pre-incident baseline: `/products` 1.092ms,
  `/orders` (POST) 1.92ms.
- **02:27:01.187Z** (E4) — chaos-mode config-change marker: latency injection enabled,
  error injection configured but disabled (`failure_rate=0.0`).
- **02:27:04 - 02:27:13Z** (E5, E6, E7) — first post-marker requests on `/products` and
  `/orders`, all 200/201 but 500-1500x slower than baseline.
- **02:28:09.953Z** (E8) — `/health` still sub-millisecond, confirming the degradation is
  confined to business routes.
- **02:30:52 - 02:30:58Z** (E9, E10, E11, E12, E13, E14, E15) — investigator re-probe
  ~3m52s after the marker: `/products` and `/orders` still elevated (132ms, 906ms) but at
  different magnitudes than the first post-marker readings; `/metrics` confirms
  `faultline_chaos_enabled 1` and a complete absence of any 4xx/5xx or exception
  telemetry since startup.

## Investigation

**Baseline** (orchestrator): `/health` and `/metrics` probed directly — health green and
fast, but `/metrics` immediately surfaced `faultline_chaos_enabled 1` and a logged
`POST /chaos/enable` call, an anomaly worth chasing before any lens was spawned.

**Triage** — all three available lenses spawned in parallel (infra-process, interfaces,
software-defect), each given only the lens file, `docs/lab.md`, the verbatim complaint,
and the baseline summary above:
- *infra-process*: flagged the same latency onset, ruled out crash/restart (single
  startup marker, monotonic uptime) and resource saturation (flat RSS).
- *interfaces*: identified the `chaos_enabled` marker as the sharp-onset config change,
  noted `failure_rate=0.0` structurally disables error injection, flagged per-route
  latency magnitude as inconsistent (not a flat +1500ms).
- *software-defect*: found zero exceptions and zero 4xx/5xx anywhere; latency spread
  "everywhere" rather than concentrated on one route/input, which the lens attributes to
  infra/injected degradation, not a code defect — ruled itself out.

**Deep-dive**: skipped a subagent round — the triage evidence (config marker plus tight
before/after timestamp correlation, replicated independently by three lenses) was
already deterministic. Instead the orchestrator gathered one more round of live evidence
directly: a fresh probe of `/products` and `/orders` and a fresh `/metrics` scrape, to
confirm the incident was still active and to actively hunt for any disconfirming 5xx.

**Judge** (fresh subagent, evidence-only, no narrative): first pass returned H1
**inconclusive** — it had no `/orders`-route evidence and flagged the 132ms-1497ms
magnitude spread as unexplained — and H2 **invalidated**. The orchestrator had the
missing `/orders` evidence already in hand (E3, E6, E7, E11) and resubmitted the
complete evidence set to the same judge; H1 was then **validated** on the strength of a
clean, non-overlapping pre/post separation across all three routes, sustained almost 4
minutes later. H2 remained **invalidated**.

## Hypotheses

### H1 — chaos-mode latency injection (validated)

A runtime config toggle (`POST /chaos/enable`, E4) injected variable extra latency into
`/products`, `/products/{id}`, and `/orders`. Every pre-marker reading on these routes
(E2, E3: 1.092-1.92ms) is faster than every post-marker reading (E5, E6, E7, E9/E10, E11:
132.36-1497.191ms), a clean separation with zero overlap, sustained from 11 seconds to
nearly 4 minutes after the marker, while `/health` (E8) and `/metrics` stayed unaffected.
The judge validated this after the `/orders`-route gap was closed, noting the per-request
magnitude jitter (132ms-1497ms vs. the configured 1500ms) as a residual open question but
not a disconfirmation of the causal link.

### H2 — server-side error behind the reported error page (invalidated)

Tested and killed: chaos is configured with `failure_rate=0.0` so it cannot have emitted
its own configured 503 (E4); the complete single-process log shows only 200/201 statuses
throughout (E14); and `http_exceptions_total` has never incremented (E15). Nothing in
faultline's own telemetry attributes to a server-side error. The judge's suggested
settling evidence — a client-side or proxy/CDN artifact — is outside the investigator's
surface contract and was not available.

## Safe next steps

- Re-scrape `/metrics` periodically (read-only) to confirm whether `faultline_chaos_enabled`
  reverts to `0` and business-route latency returns to baseline, to bound the incident's
  end time.
- If the "error page" report recurs, capture the specific timestamp and any client-visible
  status/response so it can be correlated against `lab/logs/app.log` and `/metrics`
  precisely, since this run's telemetry had nothing to anchor it to.
- Review who/what calls the chaos-control surface in this environment, from outside the
  investigator's read-only contract, since faultline's own logs only show a client address
  (127.0.0.1:54906) with no further identity.

## Gaps

- The exact latency-injection distribution is unresolved: post-marker durations on the
  same route varied from 132ms to 1497ms rather than a flat +1500ms (E5, E6, E7, E9/E10,
  E11). Confirming whether this is randomized jitter or something else would require
  reading faultline's chaos-injection code, which is out of the investigator's reach by
  design (`docs/lab.md`, the `eval/README.md` blinding contract).
- The user's reported "error page seen once" has no corresponding evidence anywhere in
  faultline's server-side telemetry: the complete single-process log (no rotation, 23
  lines covering the entire process lifetime) shows zero 4xx/5xx statuses and zero
  exception events, and `http_exceptions_total` has never incremented (E14, E15). It may
  be a client-side or gateway timeout artifact of the induced latency, a misattribution,
  or something outside this surface — browser/proxy/CDN telemetry is not part of the
  investigator's contract and could not be checked.
- The caller who triggered `POST /chaos/enable` (client 127.0.0.1:54906, request_id
  `ca1c83497ded`, E4) is not attributable beyond its client address — caller identity and
  the operator/eval trigger surface (`scripts/scenario.sh`) are outside the investigator's
  reach by design.
