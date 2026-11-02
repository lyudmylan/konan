---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-intermittent-503s
  trigger: manual
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-02T18:58:09Z
  concluded: 2026-11-02T19:06:47Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos/degradation switch was flipped on the running process at 2026-11-02T18:57:45.216Z (failure_rate 0.4, error_status 503), injecting probabilistic 503 failures into business routes (/products, /orders) while /health and /metrics kept answering 200 — explaining intermittent page/order failures against a green health dashboard."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operator-style chaos/degradation switch inside the target process was enabled mid-session (failure_rate 0.4, error_status 503), injecting probabilistic 503 errors into business routes (/products, /orders) while leaving /health and /metrics untouched."
    incident_class: infra-process
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E8, E11, E12, E14, E15, E16, E17]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled exception or returns a wrong result for specific inputs, causing the intermittent failures (a software defect)."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E7, E8, E9, E10, E11, E12, E18]
  - id: H3
    statement: "Demand briefly exceeded capacity (CPU, memory, connections, or workers), causing intermittent request failures under load (load-saturation)."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E10, E19]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:37.234Z"
    quote: "{\"ts\": \"2026-11-02T18:57:37.234Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:37.987Z"
    quote: "{\"ts\": \"2026-11-02T18:57:37.987Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 200\", \"request_id\": \"52edcf1b9b1d\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 1.086, \"client\": \"127.0.0.1:60332\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:45.216Z"
    quote: "{\"ts\": \"2026-11-02T18:57:45.216Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"b4cbf779caca\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.4, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:45.216Z"
    quote: "{\"ts\": \"2026-11-02T18:57:45.216Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /chaos/enable -> 200\", \"request_id\": \"b4cbf779caca\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/chaos/enable\", \"status\": 200, \"duration_ms\": 2.505, \"client\": \"127.0.0.1:60336\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:47.273Z"
    quote: "{\"ts\": \"2026-11-02T18:57:47.273Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"51fe0ce0f334\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:47.273Z"
    quote: "{\"ts\": \"2026-11-02T18:57:47.273Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 503\", \"request_id\": \"51fe0ce0f334\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 503, \"duration_ms\": 0.274, \"client\": \"127.0.0.1:60337\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:50.445Z"
    quote: "{\"ts\": \"2026-11-02T18:57:50.445Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"be34a515e204\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:50.446Z"
    quote: "{\"ts\": \"2026-11-02T18:57:50.446Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 503\", \"request_id\": \"be34a515e204\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.261, \"client\": \"127.0.0.1:60340\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:56.765Z"
    quote: "{\"ts\": \"2026-11-02T18:57:56.765Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"8308886b2905\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/4\"}"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:56.765Z"
    quote: "{\"ts\": \"2026-11-02T18:57:56.765Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/4 -> 503\", \"request_id\": \"8308886b2905\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/4\", \"status\": 503, \"duration_ms\": 0.276, \"client\": \"127.0.0.1:60346\"}"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:48.332Z"
    quote: "{\"ts\": \"2026-11-02T18:57:48.332Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"a4a11a42d9e6\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 0.79, \"client\": \"127.0.0.1:60338\"}"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:57:54.652Z"
    quote: "{\"ts\": \"2026-11-02T18:57:54.652Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"1e732e0c8366\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 0.806, \"client\": \"127.0.0.1:60344\"}"
  - id: E13
    type: probe
    source: "scripts/probe.sh /health, request_id konan-1793645978-445"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":121.20791633287445} -- HTTP 200 in 0.001782s"
  - id: E14
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793645982-465"
    quote: "faultline_chaos_enabled 1"
  - id: E15
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793645982-465"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3"
  - id: E16
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793645982-465"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 2"
  - id: E17
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793645982-465"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 2"
  - id: E18
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793645982-465"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter"
  - id: E19
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1793645982-465"
    quote: "process_uptime_seconds 124.8907762079034"
gaps:
  - "Resource growth over time could not be assessed: only one process_max_rss_bytes reading was taken (46,841,856 bytes, via E19's scrape), so no second time-separated sample exists to check for a leak trend. Does not change the verdict — the chaos toggle fully accounts for the observed failures — but it is a genuine blind spot."
  - "This lab ships no dedicated load-saturation or data-db lens (faultline has no real database and no distributed topology per docs/lab.md), so load-saturation was assessed through the infra-process/interfaces lenses' latency and resource checks rather than a lens built for that class, and data-db/third-party classes have no telemetry surface at all in this lab — not probed as separate hypotheses."
  - "The origin of the POST /chaos/enable call (who or what triggered it) is outside the investigator's surface: docs/lab.md classifies /chaos as operator surface, not telemetry, so only the effect (the chaos_enabled log line, E3) is observable, not the caller."
usage:
  model: claude-sonnet-5
  tokens: 3381155
  wall_clock_seconds: 518
---

# Shop intermittent 503s traced to a chaos/degradation switch enabled mid-session

## Summary

**Root cause identified.** At 2026-11-02T18:57:45.216Z an internal chaos/degradation switch was
enabled on the running `faultline` process (`failure_rate 0.4`, `error_status 503`, via
`POST /chaos/enable -> 200`, E3/E4). From that moment, roughly 40% of requests to business
routes (`/products`, `/orders`, and product-id lookups) returned `503` (E5–E10), while `/health`
and `/metrics` kept answering `200` throughout (E13, E15) — exactly the complaint's shape: some
page loads and orders error out, then succeed on retry, against a green health dashboard. No
unhandled exception was ever recorded (E18), the same inputs succeeded on other attempts during
the same window (E11, E12), and the onset was a clean step function immediately after the toggle
rather than a gradual climb (E2 vs. E5) — ruling out a software defect and load-saturation
respectively. Confidence: high: an explicit log line declares the mechanism and its parameters,
a live metric corroborates the switch is still on, and the request pattern matches the declared
0.4 failure rate exactly on the affected routes only. Safe to treat as resolved once the switch is
turned off through the operator surface (out of scope for this read-only investigation).

## Timeline (UTC)

- `18:57:37.234Z` — process start, clean single startup (E1).
- `18:57:37.234Z`–`18:57:42.156Z` — healthy baseline traffic: `/health`, `/products`,
  `/products/{id}`, and one `POST /orders -> 201` all succeed (E2).
- `18:57:45.216Z` — **change marker**: `chaos_enabled` (failure_rate 0.4, error_status 503) via
  `POST /chaos/enable -> 200` (E3, E4).
- `18:57:47.273Z` onward — intermittent `503`s begin on `/products`, `/orders`, `/products/4`,
  interleaved with continuing `200`s on the same routes (E5–E12).
- `18:58:09Z` — investigation start (this session).
- `18:59:38Z`–`18:59:42Z` — investigator baseline probes: `/health` 200 (E13), `/metrics` 200,
  showing `faultline_chaos_enabled 1` still active (E14) and zero exceptions recorded (E18).
- `19:06:47Z` — investigation concluded.

## Investigation

1. **Baseline** — probed `/health` (E13) and `/metrics` (E14–E19) directly; read `lab/logs/app.log`
   in full. Health was green and the process was freshly started (~125s uptime), but the metrics
   snapshot already showed `faultline_chaos_enabled 1` and a mix of `200`/`503` on business routes
   — the healthy-monitoring trap named in the investigate skill.
2. **Triage** — fanned out all three available lenses in parallel, each blind to the others, given
   only the lens file, the surface contract, the complaint, and the baseline summary:
   - `infra-process` — found the `chaos_enabled` switch (E3) as the direct cause; checked lifecycle
     (single startup, uptime consistent with no restart), latency (sub-millisecond throughout, no
     saturation shape), and resource growth (insufficient data, correctly left unclaimed).
   - `interfaces` — independently found the same step-function pattern around the toggle, confirmed
     health/metrics routes were untouched, and correctly deferred classification: an internal switch
     is `infra-process`, not `interfaces` (no external party or boundary component involved).
   - `software-defect` — found zero unhandled exceptions, no data-dependent failure shape (same
     product ids succeed repeatedly), and failures spread across unrelated routes rather than
     concentrated on one operation — ruling the class out from its own domain's evidence.
3. **Deep-dive — skipped.** H1's triage evidence was already deterministic and complete (a direct
   log line naming the mechanism and its exact parameters, corroborated by a live metric and a
   request pattern matching the declared rate on exactly the affected routes), so per the skill's
   rule it went straight to judgment rather than re-proving itself.
4. **Judge** — a fresh adversarial subagent, shown only the hypothesis list and verbatim evidence
   (no narrative), validated H1 and invalidated H2 and H3 (see Hypotheses below).

## Hypotheses

### H1 — chaos/degradation switch (validated)

An operator-style switch inside the process was enabled mid-session, injecting probabilistic
`503`s into business routes while leaving `/health`/`/metrics` untouched. For: the explicit
`chaos_enabled` declaration with its exact parameters (E3) immediately following the toggle
request (E4); paired `chaos_failure`/`503` lines on `/products` (E5, E6) and `/orders` (E7, E8);
the live `faultline_chaos_enabled 1` gauge (E14); the metric counts showing failures only on
business paths (E16, E17) against a clean `200`-only count on `/health` (E15); and retries on the
same inputs succeeding elsewhere in the window (E11, E12). No evidence against. The judge's
verdict: validated — every clause of the statement maps to a cited line, and nothing contradicts it.

### H2 — software defect (invalidated)

Considered because intermittent failures can be a data-dependent defect shape. Against: the
failing requests are tagged by the application itself as `chaos_failure` (E5, E6, E7, E8), not as
an exception; the exception counter has zero recorded series for the whole window (E18); and the
same product id (`/products/1`) that would reveal a deterministic per-input defect instead
succeeds repeatedly (E11, E12). The judge's verdict: invalidated — the system's own log tag is a
direct alternative attribution, stronger than an absence-of-evidence argument.

### H3 — load-saturation (invalidated)

Considered because intermittent failures can be a capacity symptom. Against: the onset is a clean
step function at the toggle timestamp, not a gradual climb from the healthy baseline (E2 vs. the
toggle at E3); the failing request resolves in 0.276ms (E10) — faster than normal successful
requests, the opposite of a saturation/timeout latency signature; and process uptime tracks
wall-clock with no gap, crash, or stall (E19). The judge's verdict: invalidated — the failure's
own latency rules out a capacity explanation.

## Safe next steps

- Confirm current chaos/operator state via the metrics surface (`faultline_chaos_enabled`) before
  and after any remediation, to verify the switch returns to `0`.
- If the switch was flipped by a scheduled or automated process, review that trigger's audit trail
  (outside this investigation's read-only surface) rather than the application code — no defect was
  found in the application itself.
- Re-run the baseline probes (`/health`, `/metrics`) after remediation to confirm the `503` series
  stops growing on `/products` and `/orders`.

## Gaps

- Resource growth over time could not be assessed from a single RSS sample; not load-bearing for
  this verdict but a real blind spot (see frontmatter `gaps`).
- No dedicated load-saturation or data-db lens exists in this lab; those classes were covered
  partially (load-saturation, via the other lenses' latency/resource checks) or not at all
  (data-db/third-party, which have no telemetry surface in this lab per `docs/lab.md`).
- The caller behind `POST /chaos/enable` is not observable from the investigator's read-only
  surface — `/chaos` is operator surface, not telemetry, so only its effect was investigated.
