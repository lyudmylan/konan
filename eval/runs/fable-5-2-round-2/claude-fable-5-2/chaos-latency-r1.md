---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-latency-chaos-switch
  trigger: 'manual — /konan human profile. Complaint object: {"source": "human", "fingerprint": "human-1794766924", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."}, "startsAt": "2026-11-15T18:22:04Z"}. Investigation start: 2026-11-15T18:22:17Z (trigger latency 13 s).'
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-11-15T18:22:17Z
  concluded: 2026-11-15T18:26:04Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational chaos switch inside the service was enabled at 18:21:45.203Z with extra_latency_ms 1500 and failure_rate 0.0; while on, it delays every business request by up to about 1.5 s and injects no errors, and it was still on at 18:23:54Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the service was enabled at 18:21:45.203Z with extra_latency_ms 1500 and failure_rate 0.0; while on, it adds a variable delay of up to about 1.5 s to every business request, adds no errors, and leaves /health fast."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E16, E17, E18, E19, E20, E21, E22]
    evidence_against: []
  - id: H2
    statement: "A defect in the service's own code makes specific routes or inputs slow."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E7, E8, E9, E10, E13, E16, E22]
  - id: H3
    statement: "Demand exceeds the capacity of the service and requests queue."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E13, E14, E17, E23]
  - id: H4
    statement: "A process lifecycle event (restart, crash loop, or hang) degraded the service."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E15]
    evidence_against: [E4, E5, E6, E13, E14, E23]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:45.203Z"
    quote: '{"ts": "2026-11-15T18:21:45.203Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "4c0108df310e", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:45.203Z"
    quote: '{"ts": "2026-11-15T18:21:45.203Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "4c0108df310e", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.706, "client": "127.0.0.1:54813"}'
  - id: E3
    type: metric
    source: "/metrics scrape, request_id=konan-1794767034-16311 (18:23:54Z)"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:40.039Z"
    quote: '{"ts": "2026-11-15T18:21:40.039Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "2420e424b92f", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.09, "client": "127.0.0.1:54809"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:41.091Z"
    quote: '{"ts": "2026-11-15T18:21:41.091Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "743f3cf092ef", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.008, "client": "127.0.0.1:54810"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:42.146Z"
    quote: '{"ts": "2026-11-15T18:21:42.146Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "1d033892be44", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.908, "client": "127.0.0.1:54812"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:48.233Z"
    quote: '{"ts": "2026-11-15T18:21:48.233Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "565f30b729a7", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 972.539, "client": "127.0.0.1:54814"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:52.974Z"
    quote: '{"ts": "2026-11-15T18:21:52.974Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "39d399fa3fe7", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1484.853, "client": "127.0.0.1:54816"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:54.427Z"
    quote: '{"ts": "2026-11-15T18:21:54.427Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "e246bea13d2b", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 397.588, "client": "127.0.0.1:54817"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:58.059Z"
    quote: '{"ts": "2026-11-15T18:21:58.059Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "fc5e9aa3e945", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1099.486, "client": "127.0.0.1:54820"}'
  - id: E11
    type: probe
    source: "/products, request_id=konan-1794766963-16232"
    quote: "-- HTTP 200 in 1.139711s request_id=konan-1794766963-16232"
  - id: E12
    type: probe
    source: "/health, request_id=konan-1794766941-16215"
    quote: |-
      {"status":"ok","uptime_seconds":42.2934957081452}
      -- HTTP 200 in 0.001568s request_id=konan-1794766941-16215
  - id: E13
    type: metric
    source: "/metrics scrape, request_id=konan-1794767034-16311 (18:23:54Z) — the complete http_requests_total and http_exceptions_total families"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E14
    type: metric
    source: "/metrics scrape, request_id=konan-1794766942-16220 (18:22:22Z)"
    quote: |-
      process_uptime_seconds 42.867234458215535
      process_max_rss_bytes 47087616
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:39.321Z"
    quote: '{"ts": "2026-11-15T18:21:39.321Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:22:45.729Z"
    quote: '{"ts": "2026-11-15T18:22:45.729Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794766964-16237", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1146.527, "client": "127.0.0.1:54842"}'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:23:13.663Z"
    quote: '{"ts": "2026-11-15T18:23:13.663Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794766993-16271", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.469, "client": "127.0.0.1:54847"}'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:55.904Z"
    quote: '{"ts": "2026-11-15T18:21:55.904Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "0356372524fe", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 414.612, "client": "127.0.0.1:54819"}'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:21:50.426Z"
    quote: '{"ts": "2026-11-15T18:21:50.426Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "6891782e4ab7", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1130.831, "client": "127.0.0.1:54815"}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:22:44.495Z"
    quote: '{"ts": "2026-11-15T18:22:44.495Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1794766963-16232", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1137.266, "client": "127.0.0.1:54841"}'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:22:46.976Z"
    quote: '{"ts": "2026-11-15T18:22:46.976Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1794766965-16242", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1164.836, "client": "127.0.0.1:54843"}'
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:23:31.229Z"
    quote: '{"ts": "2026-11-15T18:23:31.229Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794767010-16302", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 236.256, "client": "127.0.0.1:54851"}'
  - id: E23
    type: metric
    source: "/metrics scrape, request_id=konan-1794767034-16311 (18:23:54Z)"
    quote: |-
      process_uptime_seconds 135.19420791696757
      process_max_rss_bytes 47087616
gaps:
  - "No per-request attribution: no log field ties a single delay to the switch. The link rests on the onset timing, the 1500 ms cap, and the fast /health."
  - "Who enabled the switch, and why, is not in telemetry. The enable request carries a non-investigator id from 127.0.0.1; the operator surface is outside the investigator's contract."
  - "Thin pre-switch baseline: three business requests in the 6 s between process start and the switch. The log has no rotated backups, so nothing before 18:21:39Z is visible."
  - "User traffic in the log ends at 18:21:58.059Z. The slowness after that time rests on investigator probes only."
  - "The surface has no CPU metric and no in-flight request metric. Load saturation is excluded by request counts, non-overlapping requests, flat peak RSS, and a fast /health, not by CPU."
  - "The complaint says requests take forever; the largest observed duration is 1484.853 ms. Client-side time as users see it is outside the surface."
  - "The switch state 'still on' holds at 18:23:54Z only; the state after that scrape was not read."
  - "A slow internal dependency (for example storage) was not tested as a separate hypothesis; the surface exposes no dependency telemetry. The 1500 ms cap and the onset at the switch event argue against it."
  - "Token totals were not captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1274385
  wall_clock_seconds: 227
---

# Shop-wide latency from an enabled chaos switch (latency only, no errors)

## Summary

**Verdict: root cause identified.** An operational chaos switch inside the service was
enabled at 18:21:45.203Z with `extra_latency_ms: 1500` and `failure_rate: 0.0` (E1, E2).
From the first business request after it, every business route went from 1–2 ms
(E4, E5, E6) to 236–1485 ms (E7–E10, E16, E18–E22), all with status 200/201 and no
exceptions (E13). `/health` stayed under 2 ms (E12, E17), which is why health checks are
green and fast. The gauge still read `faultline_chaos_enabled 1` at 18:23:54Z (E3).

User impact, counting non-investigator traffic only: six business requests after the
switch, all slow (397.588–1484.853 ms), none failed (E7, E8, E9, E10, E18, E19).
Class `infra-process`, cause `degradation-switch`. Confidence is high: the switch
parameters predict the symptom exactly (latency only, capped at 1500 ms, health exempt),
and investigator probes confirmed the prediction. The limits are in Gaps.

## Timeline

All times UTC, 2026-11-15.

- 18:21:39.321 — process start, the only `startup` event in the log (E15).
- 18:21:40.039–18:21:42.146 — three business requests at 1.008–1.908 ms (E4, E5, E6).
- **18:21:45.203 — configuration marker: `chaos mode enabled`, `failure_rate 0.0`,
  `extra_latency_ms 1500`, through `POST /chaos/enable -> 200` (E1, E2).**
- 18:21:48.233 — first slow business request, `GET /products` 972.539 ms (E7).
- 18:21:50.426–18:21:58.059 — five more slow user requests on `/products`,
  `/products/{id}`, `POST /orders`, `GET /orders` (E19, E8, E9, E18, E10). Last user
  request in the log.
- 18:22:04 — complaint raised. 18:22:17 — investigation start.
- 18:22:21 — `/health` 200 in 0.001568 s, uptime 42.29 s (E12). 18:22:22 — first
  metrics scrape (E14).
- 18:22:44–18:22:46 — investigator probes of `/products`, `/products/1`, `/orders`:
  1137–1165 ms (E11, E20, E16, E21).
- 18:23:13.663 — `/health` 0.469 ms (E17).
- 18:23:31.229 — investigator probe of `/products/1`: 236.256 ms (E22).
- 18:23:54 — `faultline_chaos_enabled 1`; uptime 135.19 s, peak RSS unchanged (E3, E23).

## Investigation

**Baseline.** `/health` green and fast (E12). Metrics: only 200/201 statuses, no
exception series, chaos gauge 1, uptime 42.87 s (E13, E14, E3). Log: one startup, then a
step in business latency right after a `chaos_enabled` warning (E1, E15). Business
surface probed directly: three routes at about 1.14–1.17 s (E11, E16, E20, E21).

**Triage.** Three lenses in parallel, each blind to the others: infra-process,
software-defect, interfaces. All three pointed independently at the switch event at
18:21:45.203Z. Infra-process: no restart, no memory growth. Software-defect: no
exception, and the slowness is not bound to a route or an input. Interfaces: no
dependency failure signal, response shapes intact; it assigned the switch to
infra-process.

**Deep-dive.** Skipped. The triage evidence for H1 was deterministic and the baseline
probes had already confirmed its prediction; no evidence gap remained that a deep-dive
could fill within the surface.

**Judge.** One fresh judge, evidence only. H1 validated; H2, H3, H4 invalidated. The
judge's ledger carried ids E1–E17 as here, with E16 and E22 together under one id, and
E14 and E23 together under one id. It also carried one negative whole-file statement
(no `chaos_disabled` event, no `unhandled_exception` event, no `stack` field, no user
request after E10, in 30 lines read at 18:23:54Z); that statement is not a quote, so it
is not a ledger entry here. The judge flagged three business requests counted in E13
but not cited; they are now E18, E20, E21 (E19 completes the per-route list), and all
are slow. Its other open points are under Gaps.

## Hypotheses

### H1 — chaos switch adds latency (validated)

The switch event states its own parameters: latency up to 1500 ms, failure rate 0.0
(E1). The prediction was: business routes slow but successful after 18:21:45.203Z and
fast before; `/health` unaffected; gauge 1; no exceptions. Every part holds. Before:
1.09, 1.008, 1.908 ms (E4, E5, E6). After: every one of the ten business requests in
the log is between 236.256 and 1484.853 ms, none above the 1500 ms cap (E7, E8, E9, E10,
E16, E18, E19, E20, E21, E22; E11 is the probe trailer for E20). Statuses are 200/201
only and the exception family is empty (E13). `/health` is 0.469 ms while the switch is
on (E17, E12). The gauge reads 1 (E3). No evidence against.

### H2 — software defect on specific routes or inputs (invalidated)

The same input, `/products/1`, took 1.008 ms before the switch (E5), then 1484.853 ms,
1146.527 ms, and 236.256 ms (E8, E16, E22). A defect bound to a route or an input
predicts a stable duration per input. All business routes slowed at the same moment
(E7, E9, E10), with no exception (E13). Settling check named by the judge: the duration
of `GET /products/1` after the gauge reads 0.

### H3 — load saturation (invalidated)

The service handled 22 requests in about 135 s (E13, E23). The slow user requests did
not overlap in time, so no queue could form. Peak RSS is identical across both scrapes
(E14, E23). `/health` answered in 0.5–1.6 ms during the slow period (E12, E17). The
surface has no CPU metric (see Gaps).

### H4 — process lifecycle event (invalidated)

The process did start 6 s before the slowness (E15), which made this worth testing.
Against it: requests after that start were fast (E4, E5, E6); there is one startup only
(E15); uptime rose from 42.87 s to 135.19 s between scrapes 92 s apart, so no reset
(E14, E23); every request completed (E13).

## Safe next steps

Read-only only.

- Ask the operator who sent the enable request at 18:21:45.203Z (request id
  `4c0108df310e`, E2) and whether the switch state is intended.
- Watch `faultline_chaos_enabled` on `/metrics` and the log for a `chaos_disabled`
  event. When the gauge reads 0, probe `/products/1` once: about 1 ms closes H2 fully.
- Read the access lines of user traffic (request ids without the `konan-` prefix) after
  18:21:58Z to measure continued user impact.
- Observation outside this incident, not tested: the `/products` response lists product
  4 with `"price":null` (probe `konan-1794766963-16232`). One probe of `/products/4`
  would show whether that record is served cleanly.

## Gaps

- **No per-request attribution.** No log field marks a request as delayed by the switch.
  The causal link is the onset timing, the 1500 ms cap, and the exempt `/health`.
- **Actor unknown.** The enable request has a non-investigator id from 127.0.0.1 (E2).
  Who sent it is not in telemetry, and the operator surface is outside the contract.
- **Thin baseline.** Three business requests in 6 s before the switch; no rotated log
  backups, so no history before 18:21:39Z.
- **User traffic ends at 18:21:58.059Z.** Later slowness is shown by investigator
  probes only.
- **No CPU or in-flight metric.** H3 is excluded by counts, timing, memory, and
  `/health`, not by CPU.
- **Magnitude versus the complaint.** "Takes forever" was reported; the largest
  observed duration is 1484.853 ms. Client-side time is outside the surface.
- **Switch state is time-bound.** "Still on" holds at 18:23:54Z.
- **Dependency rival not tested separately.** The surface exposes no dependency
  telemetry; the cap and the onset at the switch event argue against a slow dependency.
- **Tokens not captured** in this session.
