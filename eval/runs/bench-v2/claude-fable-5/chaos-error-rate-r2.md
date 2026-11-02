---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-chaos-503s
  trigger: "manual — /konan human report (alertname=human-report, fingerprint=human-1793632868, startsAt=2026-11-02T15:21:08Z; trigger latency 15s to investigation start)"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-02T15:21:23Z
  concluded: 2026-11-02T15:27:41Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos/degradation switch was enabled at 2026-11-02T15:20:45.918Z via POST /chaos/enable (failure_rate=0.4, error_status=503, extra_latency_ms=0) and is still on; it injects 503s into roughly 40% of product and order requests while /health stays green."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside faultline, enabled at 15:20:45.918Z via POST /chaos/enable with failure_rate=0.4 and error_status=503, injects 503s into ~40% of shop requests (products, orders) while it stays on; /health is exempt, so health checks stay green."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E21]
    evidence_against: []
  - id: H2
    statement: "A defect in faultline's own code (unhandled exception or input-dependent failure) causes the intermittent errors."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E19, E5, E6, E4, E12]
  - id: H3
    statement: "The faultline process crashes or restart-loops, and requests fail intermittently during restarts."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E18, E17, E16]
  - id: H4
    statement: "Demand exceeds capacity; the 503s are load shedding or resource exhaustion."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E20, E10, E1, E5]
  - id: H5
    statement: "A gateway, proxy, or contract boundary in front of the service fails on its own and returns the 503s."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E12, E5, E1]
  - id: H6
    statement: "An external provider the shop depends on returns errors that surface as 503s."
    incident_class: third-party
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E11, E12, E5]
latent_findings:
  - statement: "The request counter labels successes of parameterized routes with the route template (path=/products/{product_id}) but chaos-injected 503s with the literal path (path=/products/1), so any per-path error-rate panel splits a route's errors from its successes and understates the error rate."
    evidence: [E10]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:45.918Z"
    quote: '{"ts": "2026-11-02T15:20:45.918Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "d979308827d6", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:45.919Z"
    quote: '{"ts": "2026-11-02T15:20:45.919Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "d979308827d6", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.322, "client": "127.0.0.1:59023"}'
  - id: E3
    type: metric
    source: "/metrics @ 2026-11-02T15:21:32Z (probe konan-1793632892-94591)"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:49.038Z"
    quote: '{"ts": "2026-11-02T15:20:49.038Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "89faeb30e728", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:49.038Z"
    quote: '{"ts": "2026-11-02T15:20:49.038Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "89faeb30e728", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.309, "client": "127.0.0.1:59025"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:55.373Z"
    quote: '{"ts": "2026-11-02T15:20:55.373Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "b8c893175d6b", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.843, "client": "127.0.0.1:59031"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:54.315Z"
    quote: '{"ts": "2026-11-02T15:20:54.315Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e469056d63a3", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:54.316Z"
    quote: '{"ts": "2026-11-02T15:20:54.316Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "e469056d63a3", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.801, "client": "127.0.0.1:59030"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:51.154Z"
    quote: '{"ts": "2026-11-02T15:20:51.154Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "d8cb3ea0186d", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.267, "client": "127.0.0.1:59027"}'
  - id: E10
    type: metric
    source: "/metrics @ 2026-11-02T15:21:32Z (probe konan-1793632892-94591), http_requests_total series"
    quote: |-
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/4",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_requests_total{method="POST",path="/orders",status="503"} 1
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
  - id: E11
    type: probe
    source: "/products, request_id konan-1793633009-94672 @ 2026-11-02T15:23:29Z (first of a 6-probe burst 15:23:29–15:23:32Z that returned 503, 200, 200, 503, 503, 503)"
    quote: |-
      {"error":"service temporarily degraded","request_id":"konan-1793633009-94672"}
      -- HTTP 503 in 0.001255s request_id=konan-1793633009-94672
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:23:29.040Z"
    quote: '{"ts": "2026-11-02T15:23:29.040Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1793633009-94672", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:23:32.338Z (last of 8 chaos_failure lines; the 8 chaos_failure lines and the 8 status-503 access lines in the full log pair one-to-one by request_id)"
    quote: '{"ts": "2026-11-02T15:23:32.338Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1793633012-94697", "event": "chaos_failure", "method": "GET", "path": "/orders"}'
  - id: E14
    type: probe
    source: "/health ×20, request_ids konan-1793633154-94782 … konan-1793633155-94839 @ 2026-11-02T15:25:54–55Z; all 20 returned HTTP 200 (first shown)"
    quote: |-
      {"status":"ok","uptime_seconds":317.1495734581258}
      -- HTTP 200 in 0.004329s request_id=konan-1793633154-94782
  - id: E15
    type: metric
    source: "/metrics @ 2026-11-02T15:26:01Z (probe konan-1793633161-94845)"
    quote: "faultline_chaos_enabled 1"
  - id: E16
    type: metric
    source: "/metrics @ 2026-11-02T15:26:01Z (probe konan-1793633161-94845)"
    quote: "process_uptime_seconds 323.3287105830386"
  - id: E17
    type: metric
    source: "/metrics @ 2026-11-02T15:21:32Z (probe konan-1793632892-94591)"
    quote: "process_uptime_seconds 54.5983112079557"
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:37.821Z (the only startup event in the log; no rotated backups exist)"
    quote: '{"ts": "2026-11-02T15:20:37.821Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E19
    type: metric
    source: "/metrics @ 2026-11-02T15:21:32Z and 15:26:01Z — the counter has zero series in both scrapes (no exception ever counted); grep of lab/logs/app.log for unhandled_exception, simulated_exception, stack, and level ERROR: 0 lines"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E20
    type: metric
    source: "/metrics @ 2026-11-02T15:21:32Z and 15:26:01Z (identical value in both scrapes)"
    quote: "process_max_rss_bytes 48611328"
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:20:42.859Z (last user request before the switch; every request before 15:20:45.918Z returned 200 or 201)"
    quote: '{"ts": "2026-11-02T15:20:42.859Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "0b3b7ee6091f", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.729, "client": "127.0.0.1:59022"}'
gaps:
  - "The reporter's health dashboard definition is outside the surface contract. Its greenness is explained only indirectly: /health returns 200 and is exempt from injection (E9-series counters, E14); the dashboard's actual query was not verifiable."
  - "Who or what sent POST /chaos/enable is not identifiable from the surface: the access line records only client 127.0.0.1:59023 (E2); the telemetry has no identity or change-audit field."
  - "The /health exemption is statistical: 20 consecutive 200s under a 0.4 injection rate (chance ≈ 4×10⁻⁵, E14) plus zero non-200 health series; the switch's exempt-path configuration is operator surface and not readable."
  - "failure_rate=0.4 is the configured value (E1). Measured post-enable user-traffic rate was 4 of 10 requests (E10, corrected for pre-enable requests) and 4 of 6 investigator probes (E11) — consistent, but the samples are small."
usage:
  model: claude-fable-5
  tokens: 1977653
  wall_clock_seconds: 378
---

# Shop intermittent 503s — internal chaos degradation switch enabled

## Summary

Root cause identified. At 2026-11-02T15:20:45.918Z an operator-surface request
(`POST /chaos/enable`, client 127.0.0.1:59023) enabled faultline's internal chaos
switch with `failure_rate=0.4`, `error_status=503`, `extra_latency_ms=0` (E1, E2).
From that moment, each product or order request has a ~40% chance of an injected
HTTP 503 ("service temporarily degraded"); retries usually succeed, which matches
the reported symptom exactly. The switch was still on at the last read,
15:26:01Z (E15), so user impact is ongoing until an operator turns it off.
`/health` is exempt from the injection (20/20 investigator probes returned 200
while the switch was on, E14), which is why a health-based dashboard stays green —
the classic healthy-monitoring trap. Confidence is high: the enable marker, the
live gauge, a one-to-one pairing of every 503 with a `chaos_failure` log line
(E13), and a confirmed prediction on fresh stamped probes (E11, E12) all agree.

## Timeline

- 15:20:37.821Z — process start, faultline 0.1.0 (E18).
- 15:20:38–15:20:42.859Z — user traffic all 200/201; last pre-change success `GET /products/2 -> 200` (E21).
- 15:20:45.918Z — **change marker**: chaos mode enabled, rate 0.4, status 503 (E1, E2).
- 15:20:49.038Z — first injected 503 on user traffic, `GET /products/1` (E4, E5).
- 15:20:49–15:20:57.503Z — user 503s on `/products`, `/products/1`, `/products/4`, `POST /orders`, interleaved with successes on the same paths (E6, E7, E8, E9, E10).
- 15:21:08Z — human complaint raised (`startsAt`).
- 15:21:23Z — investigation start (trigger latency 15 s).
- 15:21:31–32Z — baseline: `/health` 200, `faultline_chaos_enabled 1` (E3).
- 15:23:29–32Z — prediction test: 6 stamped probes, 4 injected 503s with `konan-*` ids in `chaos_failure` lines (E11, E12, E13).
- 15:25:54–55Z — `/health` exemption test: 20/20 probes 200 (E14).
- 15:26:01Z — final read: switch still on, same process (uptime 323 s), RSS flat (E15, E16, E20).

## Investigation

Baseline (health, metrics scrape, log tail) surfaced the `chaos_enabled` marker and
the live gauge immediately. Triage fanned out three parallel lenses — infra-process,
interfaces, software-defect — all blind to each other. All three converged on the
chaos switch and independently ruled out their own domains' alternatives (no
restarts, no exceptions, no dependency failures, no resource pressure). The
orchestrator formed six hypotheses; H1's triage evidence was near-deterministic, so
no deep-dive agents were spawned — one cheap prediction test (the 6-probe burst) ran
instead. The adversarial judge validated H1's core claim, killed H2–H6, and flagged
three evidence gaps: the 503↔marker pairing was unverified in aggregate, the /health
exemption rested on 3 samples, and "still on" needed a fresh read. Targeted gathering
settled all three (E13, E14, E15). One judge item — the dashboard's own definition —
is out of surface and recorded as a gap.

## Hypotheses

### H1 — chaos degradation switch (infra-process) — validated

The switch was enabled at 15:20:45.918Z (E1) through the operator endpoint (E2) and
never disabled (gauge still 1 at both reads, E3, E15; no `chaos_disabled` event in
the log). Every 503 in the log pairs one-to-one with a `chaos_failure` line sharing
its request id — 8 of 8 (E4/E5, E7/E8, E12, E13). The same path fails and then
succeeds (E5 then E6; E9 then E8), which matches a probabilistic injector and the
"works on retry" complaint, and rules out any input-dependent mechanism. The
prediction test confirmed live injection: 4 of 6 stamped probes drew 503s whose ids
appear in `chaos_failure` lines (E11, E12). User impact is real and not
probe-induced: the pre-complaint 503s at 15:20:49–57Z are unstamped user traffic
(E5, E8, E10). `/health` is exempt (E14), explaining the green dashboard within this
surface's limits.

### H2 — software defect — invalidated

No exception was ever counted and no stack, ERROR line, or exception event exists in
the log (E19). The same input both fails and succeeds seconds apart (E5, E6), and
every traced 503 carries the injection marker (E4, E12).

### H3 — process crash / restart loop — invalidated

Exactly one startup event (E18); uptime climbs monotonically across reads, 54.6 s →
323.3 s, with no reset (E17, E16). The 503s are fast, well-formed application
responses, not connection failures.

### H4 — load saturation — invalidated

Request volumes are tiny (E10), durations are sub-millisecond (E5), peak RSS is flat
across the window (E20), and the injector adds no latency (`extra_latency_ms: 0`,
E1).

### H5 — gateway / boundary failure (interfaces) — invalidated

The investigator's own request id comes back in the 503 body and appears in the
target's log stamped `chaos_failure` (E11, E12): the target itself generates the
503. Sub-millisecond durations (E5) leave no room for a failing tier in between, and
the status and rate match the internal switch's configuration (E1).

### H6 — third-party provider — invalidated

Same mechanism evidence as H5: the failures are generated and stamped inside the
target (E4, E12), with response times that exclude an external call (E5, E11).

## Safe next steps

Read-only; remediation is the operator's decision, outside this report.

- Watch `faultline_chaos_enabled` on `/metrics` and the `chaos_disabled` event in
  `lab/logs/app.log` — they will mark the recovery point when the switch is turned
  off.
- Identify the sender of `POST /chaos/enable` at 15:20:45.919Z from sources outside
  this surface (operator shell history, automation schedules, change records); the
  log records only `client 127.0.0.1:59023` (E2).
- Review what the health dashboard actually queries: `/health` is exempt from the
  injection while business paths fail, so a health-endpoint-only panel cannot see
  this incident class.
- When reading per-path error panels, note the labeling split in
  `http_requests_total` (latent finding): successes use the route template, injected
  503s the literal path, so grouped-by-path error rates understate.

## Gaps

- **Dashboard definition.** "Our health dashboard is green" could only be explained
  indirectly: `/health` returns 200 and is exempt from injection. The dashboard's
  own query is outside the surface contract and was not verified.
- **Change attribution.** The telemetry carries no identity for the enable request —
  only an ephemeral client ip:port. Who or what flipped the switch cannot be
  answered from this surface.
- **Exemption proof.** The `/health` exemption is statistical (20/20 passes,
  chance ≈ 4×10⁻⁵ under the 0.4 rate) plus zero non-200 health series; the switch's
  exempt-path configuration is operator surface and deliberately unreadable.
- **Rate precision.** The 40% failure rate is the configured value; measured samples
  (4/10 user requests, 4/6 probes) are consistent but small.
