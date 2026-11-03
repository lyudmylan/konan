---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-503s-degradation-switch
  trigger: "manual (/konan): source=human, fingerprint=human-1793633453, alertname=human-report; complaint startsAt 2026-11-02T15:30:53Z; investigation start 2026-11-02T15:30:59Z (trigger latency 6s)"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: "2026-11-02T15:30:59Z"
  concluded: "2026-11-02T15:36:10Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational chaos degradation switch inside faultline, enabled at 15:30:29.086Z via POST /chaos/enable with failure_rate 0.4 and error_status 503, randomly rejects about 40% of shop requests with injected 503s while /health keeps returning 200."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal chaos/degradation switch, turned on at 15:30:29.086Z with failure_rate 0.4 and error_status 503, injects 503s into a random ~40% of shop requests; retries succeed because the injection is per-request, and the health dashboard stays green because /health is unaffected."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10]
    evidence_against: [E15]
  - id: H2
    statement: "The target's own code raises an unhandled error on specific inputs and fails those requests deterministically."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E8, E11]
  - id: H3
    statement: "The process crashes or restarts repeatedly, and requests fail intermittently during the restarts."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E13, E17]
  - id: H4
    statement: "A proxy, load balancer, or gateway tier in front of the app produces the 503s on its own."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E8]
latent_findings:
  - statement: "The metrics label 5xx responses with the raw path (/products/1) while 2xx responses use the route template (/products/{product_id}). A per-route error rate is split across two label sets, so a dashboard that reads one label set under-reports errors."
    evidence: [E9, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:30:29.086Z"
    quote: |-
      {"ts": "2026-11-02T15:30:29.086Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "73fdac9e6941", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:30:29.086Z"
    quote: |-
      {"ts": "2026-11-02T15:30:29.086Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "73fdac9e6941", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.701, "client": "127.0.0.1:59125"}
  - id: E3
    type: metric
    source: "/metrics @ 2026-11-02T15:31:15Z (probe konan-1793633475-95013)"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:30:33.260Z"
    quote: |-
      {"ts": "2026-11-02T15:30:33.260Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "6ecd6ab39d6a", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:30:33.260Z"
    quote: |-
      {"ts": "2026-11-02T15:30:33.260Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "6ecd6ab39d6a", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.312, "client": "127.0.0.1:59128"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:30:32.204Z"
    quote: |-
      {"ts": "2026-11-02T15:30:32.204Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "38451b165ea0", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.796, "client": "127.0.0.1:59127"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:30:38.553Z"
    quote: |-
      {"ts": "2026-11-02T15:30:38.553Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "127d9dfe761f", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.264, "client": "127.0.0.1:59133"}
  - id: E8
    type: probe
    source: "/products/1, 6 repeated probes @ ~2026-11-02T15:32:31Z (request_ids konan-1793633551-95122 … konan-1793633551-95137); results in order: 503, 200, 200, 503, 200, 200; body of the first failing probe"
    quote: '{"error":"service temporarily degraded","request_id":"konan-1793633551-95122"}'
  - id: E9
    type: metric
    source: "/metrics @ 2026-11-02T15:35:48Z (probe konan-1793633748-95263)"
    quote: |-
      http_requests_total{method="GET",path="/products/1",status="503"} 3
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
  - id: E10
    type: metric
    source: "/metrics @ 2026-11-02T15:35:48Z (probe konan-1793633748-95263)"
    quote: "faultline_chaos_enabled 1"
  - id: E11
    type: metric
    source: "/metrics @ ~2026-11-02T15:32:46Z (probe konan-1793633566-95173); the counter has zero samples — only HELP/TYPE lines are present"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:30:21.095Z — the only startup event in the log; no rotated backups exist"
    quote: |-
      {"ts": "2026-11-02T15:30:21.095Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E13
    type: metric
    source: "/metrics @ 2026-11-02T15:35:48Z (probe konan-1793633748-95263); monotonic against 54.46965116588399 @ 15:31:15Z — no reset"
    quote: "process_uptime_seconds 327.6846564579755"
  - id: E14
    type: probe
    source: "/health @ 2026-11-02T15:31:14Z (request_id konan-1793633474-95008), HTTP 200 while chaos was on"
    quote: '{"status":"ok","uptime_seconds":53.75567812495865}'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:30:34.320Z — an order created after the switch went on; all three POST /orders in the log returned 201"
    quote: |-
      {"ts": "2026-11-02T15:30:34.320Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "14133c9b16b0", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.276, "client": "127.0.0.1:59129"}
  - id: E16
    type: metric
    source: "/metrics @ 2026-11-02T15:35:48Z (probe konan-1793633748-95263)"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="200"} 8'
  - id: E17
    type: metric
    source: "/metrics @ 2026-11-02T15:31:15Z (probe konan-1793633475-95013); unchanged at the ~15:32:18Z re-read"
    quote: "process_max_rss_bytes 46743552"
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:30:40.663Z — the last non-investigator request line in the log"
    quote: |-
      {"ts": "2026-11-02T15:30:40.663Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "7b74c9262a7f", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.893, "client": "127.0.0.1:59135"}
gaps:
  - "The complaint's 'orders error out' is not confirmed: all three POST /orders in the log returned 201 (two of them after the switch went on), and the GET-only probe contract cannot exercise POST /orders. With failure_rate 0.4, two post-switch successes occur with probability ~0.36, so this small sample neither confirms nor refutes that the switch covers orders."
  - "The chaos switch's path scope is not observable from the surface. The /health exemption is inferred from an unbroken run of 200s, not from configuration."
  - "No front-tier or gateway logs exist on this surface; a request dropped before reaching the app would be invisible. docs/lab.md describes the lab as a single service, and nothing observed points to a front tier."
  - "Non-investigator traffic stops at 15:30:40.663Z (E18). The current user-facing failure rate can only be estimated from investigator probes (2 of 6 failed, ~33%, consistent with the configured 0.4)."
  - "The actor who enabled the switch is unknown: the enabling request came from client 127.0.0.1:59125 with an unstamped request id (E2), and the operator surface is outside the investigator's contract."
usage:
  model: claude-fable-5
  tokens: 1712411
  wall_clock_seconds: 311
---

# Shop intermittent 503s — chaos degradation switch enabled

## Summary

**Root cause identified.** At 2026-11-02T15:30:29.086Z an operational chaos switch
inside faultline was enabled via `POST /chaos/enable` with `failure_rate 0.4`,
`error_status 503`, and no added latency (E1, E2). From that moment the service
rejects a random ~40% of shop requests with an injected 503 ("service temporarily
degraded"), which is exactly the reported shape: some page loads fail, a retry of the
same request succeeds. `/health` is unaffected and returns 200 throughout (E14),
which is why the dashboard stays green — the classic healthy-monitoring trap. The
switch is still on at the conclusion of this investigation (E10). Confidence is high:
every observed 503 is paired with a `chaos_failure` log line from the app's own
logger, and six investigator probes of one unchanged input reproduced the fault at
the configured rate (E8). One caveat: no order failure appears anywhere in the
telemetry (E15), so the complaint's "orders error out" is unconfirmed (see Gaps).

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 15:30:21.095Z | faultline 0.1.0 starts; the only startup event | E12 |
| 15:30:21.8–26.0Z | Healthy user traffic: 0 failures in 5 requests | E6 |
| 15:30:29.086Z | **Config-change marker:** chaos enabled, rate 0.4, status 503, from 127.0.0.1:59125 | E1, E2 |
| 15:30:33.260Z | First injected failure: GET /products/2 → 503 with paired `chaos_failure` line | E4, E5 |
| 15:30:34.320Z | POST /orders → 201 (orders keep succeeding after the switch) | E15 |
| 15:30:36.4Z, 15:30:38.5Z | Further injected 503s on /products/5 and /products/1 | E7, E9 |
| 15:30:40.663Z | Last non-investigator request in the log | E18 |
| 15:30:53Z | Complaint startsAt (human report) | — |
| 15:31:14–15Z | Baseline: /health 200 "ok"; `faultline_chaos_enabled 1` | E14, E3 |
| ~15:32:31Z | Probe reproduction: /products/1 ×6 → 503, 200, 200, 503, 200, 200 | E8 |
| 15:35:48Z | Conclusion-time check: switch still on; uptime monotonic, no restart | E10, E13 |

## Investigation

**Baseline** (15:31:14–15Z): health 200, metrics snapshot, log tail. The baseline
itself contained the config-change marker (E1) and the live gauge (E3).

**Triage** — three lenses in parallel, each blind to the others:

- *infra-process*: found the enabled switch (E1, E3), found no `chaos_disabled` event
  afterward, and ruled out restart (E12, uptime monotonic), memory pressure (E17),
  and latency injection (durations under 1 ms; `extra_latency_ms: 0` in E1).
- *interfaces*: bracketed the onset (last good request 15:30:26Z, first failure
  15:30:33Z, 4.2s after the marker), reproduced the fault with stamped probes at the
  configured rate (E8), and reclassified its own finding as `infra-process` — the
  503s are made inside the app, not at a boundary (E4, E8). It also surfaced the
  metrics label split (E9 vs E16).
- *software-defect*: found no exceptions anywhere (E11), showed the same input both
  succeeds and fails (E6, E7, E8), and found every 503 paired with a `chaos_failure`
  line.

**Deep-dive**: skipped. The triage evidence for H1 was already deterministic and
complete (marker, gauge, per-503 pairing, probe reproduction), so the hypotheses went
straight to the judge.

**Judge** (adversarial, evidence-only): H1 validated for the core mechanism; H2, H3,
H4 invalidated. The judge flagged two honest limits, both kept: the "orders" part of
the complaint is not shown by any evidence, and "~40% of requests" must not be read
as "all paths" — /health behaves as exempt.

## Hypotheses

### H1 — chaos degradation switch (infra-process) — validated

The switch went on at 15:30:29.086Z with rate 0.4 and status 503 (E1, E2) and is
still on (E3, E10). Every 503 carries a paired `chaos_failure` line with the same
request id at the same millisecond (E4, E5). The same input flips between 200 and 503
(E6, E7), and six probes of /products/1 reproduced 2 failures at ~33%, consistent
with 0.4 on a small sample (E8). User-traffic failure counts went from 0/5 before the
marker to 3/10 after it (E9 and the log window). Against: no order failure exists in
the telemetry (E15) although the complaint names orders — the judge weighed this as a
coverage question, not a refutation, since two successes under rate 0.4 occur ~36% of
the time.

### H2 — per-input software defect — invalidated

The failure is not deterministic per input (E6, E7, E8), `http_exceptions_total` has
zero samples, and the log holds no `unhandled_exception`, stack, or ERROR lines
(E11).

### H3 — crash/restart loop — invalidated

One startup event only (E12); uptime rises monotonically across three readings to
327.7s (E13); RSS flat (E17). Failures answer in under 0.5 ms with a structured body
— not a crash shape.

### H4 — gateway/proxy failure — invalidated

The 503s are produced inside the app: its own logger writes the `chaos_failure` lines
(E4) and the response body is the app's error envelope with a matching request id
(E8). No boundary component is involved; per the report contract, an internal switch
is `infra-process` even with gateway-shaped symptoms.

## Safe next steps

- Ask the operator team who enabled the switch. The audit anchor is the
  `POST /chaos/enable` request at 15:30:29.086Z from `127.0.0.1:59125` (E2).
- Watch `faultline_chaos_enabled` and the log for a `chaos_disabled` event — that
  marker will date the end of user impact.
- Treat any order-failure report that arrives after the switch goes off as a separate
  signal; nothing in this window shows a failed order (E15).
- Review the health dashboard's inputs: `/health` stayed 200 through the whole
  incident (E14). A business-surface signal (per-route 5xx rate) would have caught
  this. When reading per-route error rates, sum the raw-path and template-path label
  sets (latent finding, E9/E16).

## Gaps

1. **Orders unconfirmed.** All three `POST /orders` returned 201 (E15), two of them
   after the switch. The probe contract is GET-only, so orders cannot be exercised.
   A sample of two under rate 0.4 succeeds ~36% of the time, so order coverage is
   neither confirmed nor refuted.
2. **Switch scope unobservable.** Which paths the chaos switch skips (apparently
   `/health`) is inferred from behavior, not read from configuration.
3. **No front tier on this surface.** A request failing before the app would be
   invisible; the lab contract describes a single service, and nothing points to a
   front tier.
4. **User traffic stopped** at 15:30:40.663Z (E18); the live user-facing failure
   rate is estimated from investigator probes only.
5. **Actor unknown.** The enabling request is unstamped and local (E2); the operator
   surface is outside the investigator's contract.
