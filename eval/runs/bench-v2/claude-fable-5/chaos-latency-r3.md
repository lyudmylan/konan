---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-wide-slowness
  trigger: >-
    manual (/konan human profile; fingerprint human-1793700912; alertname
    human-report; startsAt 2026-11-03T10:15:12Z; investigation start
    2026-11-03T10:15:26Z; trigger latency 14s)
  complaint: >-
    Users say every page in the shop got painfully slow in the last few
    minutes — nothing errors out, it just takes forever. Health checks are
    green and fast.
  started: 2026-11-03T10:15:26Z
  concluded: 2026-11-03T10:20:27Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: >-
    A degradation switch inside faultline — chaos mode, enabled at
    2026-11-03T10:14:48.314Z with extra_latency_ms 1500 and failure_rate 0.0 —
    injects up to ~1.5 s of latency into every business route while /health
    and /metrics stay sub-millisecond; the switch is still on.
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: >-
      Chaos mode, enabled at runtime at 10:14:48.314Z (extra_latency_ms 1500,
      failure_rate 0.0), adds up to ~1.5 s of latency to every business route
      (/products*, /orders*) with zero injected errors, leaves /health and
      /metrics unaffected, and remains active.
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15]
    evidence_against: []
  - id: H2
    statement: >-
      A software defect in a shop code path (possibly data-dependent) makes
      pages slow.
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E8, E16, E17]
  - id: H3
    statement: >-
      A process crash/restart or resource saturation degrades the service.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E18, E19, E20, E15, E12]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:48.314Z"
    quote: >-
      {"ts": "2026-11-03T10:14:48.314Z", "level": "WARNING", "logger":
      "faultline.chaos", "message": "chaos mode enabled", "request_id":
      "06cae2c183a0", "event": "chaos_enabled", "enabled": true,
      "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:48.315Z"
    quote: >-
      {"ts": "2026-11-03T10:14:48.315Z", "level": "INFO", "logger":
      "faultline.request", "message": "POST /chaos/enable -> 200",
      "request_id": "06cae2c183a0", "event": "request", "method": "POST",
      "path": "/chaos/enable", "status": 200, "duration_ms": 2.773,
      "client": "127.0.0.1:49582"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:43.132Z"
    quote: >-
      "message": "GET /products -> 200", "request_id": "ebba518dc28f",
      "status": 200, "duration_ms": 1.607, "client": "127.0.0.1:49578"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:44.190Z"
    quote: >-
      "message": "GET /products/1 -> 200", "request_id": "94404506a559",
      "status": 200, "duration_ms": 1.399, "client": "127.0.0.1:49580"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:45.253Z"
    quote: >-
      "message": "POST /orders -> 201", "request_id": "5e0e663b70b8",
      "status": 201, "duration_ms": 1.85, "client": "127.0.0.1:49581"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:51.102Z"
    quote: >-
      "message": "GET /products -> 200", "request_id": "ca8d313f7e97",
      "status": 200, "duration_ms": 726.528, "client": "127.0.0.1:49583"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:52.812Z"
    quote: >-
      "message": "GET /products/2 -> 200", "request_id": "534d54a8cd77",
      "status": 200, "duration_ms": 642.44, "client": "127.0.0.1:49584"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:55.107Z"
    quote: >-
      "message": "GET /products/1 -> 200", "request_id": "28be5cea4076",
      "status": 200, "duration_ms": 1227.656, "client": "127.0.0.1:49585"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:56.819Z"
    quote: >-
      "message": "POST /orders -> 201", "request_id": "b3783cb24b14",
      "status": 201, "duration_ms": 643.706, "client": "127.0.0.1:49586"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:58.412Z"
    quote: >-
      "message": "GET /products -> 200", "request_id": "16b237556eec",
      "status": 200, "duration_ms": 535.828, "client": "127.0.0.1:49587"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:15:00.924Z"
    quote: >-
      "message": "GET /orders -> 200", "request_id": "d846b66cd7bb",
      "status": 200, "duration_ms": 1445.515, "client": "127.0.0.1:49588"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:15:35.731Z"
    quote: >-
      "message": "GET /health -> 200", "request_id": "konan-1793700935-28315",
      "status": 200, "duration_ms": 0.497, "client": "127.0.0.1:49611"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:15:36.377Z"
    quote: >-
      "message": "GET /metrics -> 200", "request_id": "konan-1793700936-28320",
      "status": 200, "duration_ms": 0.588, "client": "127.0.0.1:49612"
  - id: E14
    type: probe
    source: "/products @ konan-1793700986-28331"
    quote: "-- HTTP 200 in 0.422640s request_id=konan-1793700986-28331"
  - id: E15
    type: metric
    source: "/metrics @ konan-1793701179-28429 (2026-11-03T10:20:21Z approx.)"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 296.7646043749992
  - id: E16
    type: metric
    source: "/metrics @ konan-1793701179-28429 — the counter carries no series; the next line of the scrape is the next # HELP header"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E17
    type: metric
    source: "/metrics @ konan-1793701179-28429"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-03T10:14:42.379Z"
    quote: >-
      {"ts": "2026-11-03T10:14:42.379Z", "level": "INFO", "logger":
      "faultline.app", "message": "faultline 0.1.0 started", "event":
      "startup", "version": "0.1.0"}
  - id: E19
    type: metric
    source: "/metrics @ konan-1793701179-28429"
    quote: "process_max_rss_bytes 47185920"
  - id: E20
    type: metric
    source: "/metrics @ konan-1793700936-28320 (2026-11-03T10:15:36Z)"
    quote: "process_uptime_seconds 54.00951558398083"
gaps:
  - >-
    The actor behind POST /chaos/enable (request_id 06cae2c183a0, client
    127.0.0.1:49582) cannot be attributed from the allowed surface; the logs
    carry no identity beyond the client address.
  - >-
    No business-route traffic exists between 10:14:48.315Z and 10:14:51.102Z,
    so onset precision is limited to that 2.8 s window.
  - >-
    The configured 1500 ms upper bound is not directly observed (maximum seen
    is 1445.515 ms); the per-request delay looks random below the bound.
  - >-
    No dedicated load-saturation, third-party, or data-db lens ran; the lab
    contract declares no database and no third-party dependency, and
    saturation is refuted by E12, E15, E19, E20 (health sub-ms, uptime
    monotonic, flat RSS, trivial request volume).
usage:
  model: claude-fable-5
  tokens: 1335364
  wall_clock_seconds: 301
---

# Shop-wide slowness: chaos latency switch enabled, no errors injected

## Summary

Root cause identified. At 2026-11-03T10:14:48.314Z a runtime degradation
switch inside faultline — chaos mode — was enabled with `extra_latency_ms:
1500` and `failure_rate: 0.0` (E1). From the next business request on, every
shop route (`/products`, `/products/{id}`, `/orders`, `POST /orders`) takes
roughly 420–1446 ms instead of 1–12 ms, and every request still returns
200/201 — which matches the complaint exactly: slow, but nothing errors out.
`/health` and `/metrics` are exempt from the injected latency and answer in
under 1 ms (E12, E13), which is why the health checks stay green. The switch
is still on at the time of this conclusion (E15). Confidence is high: the
onset sits directly on the configuration marker, the same input (`/products/1`)
is fast before and slow after, and the adversarial judge validated the
hypothesis while killing both alternatives.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 10:14:42.379Z | faultline 0.1.0 starts (the only startup event) | E18 |
| 10:14:43–10:14:45 | End-user traffic is healthy: 1.399–1.85 ms on business routes | E3, E4, E5 |
| 10:14:48.314Z | **Configuration marker**: chaos mode enabled, failure_rate 0.0, extra_latency_ms 1500, via `POST /chaos/enable` from 127.0.0.1 | E1, E2 |
| 10:14:51–10:15:00 | All end-user business requests slow: 535.828–1445.515 ms, all 200/201 | E6–E11 |
| 10:15:12Z | Human complaint raised (startsAt) | — |
| 10:15:26Z | Investigation starts (trigger latency 14 s) | — |
| 10:15:35–10:15:36Z | Investigator probes: /health 0.497 ms, /metrics 0.588 ms — monitoring surface unaffected | E12, E13 |
| 10:16:27Z | Investigator probe of /products: 200 in 422.6 ms — slowness live | E14 |
| ~10:20:21Z | Chaos gauge still 1 at uptime 296.76 s; no disable event in the log | E15 |

## Investigation

The complaint arrived through the manual trigger (`/konan`). Complaint object,
verbatim: `{"source": "human", "fingerprint": "human-1793700912", "labels":
{"alertname": "human-report"}, "annotations": {"summary": "Users say every
page in the shop got painfully slow in the last few minutes — nothing errors
out, it just takes forever. Health checks are green and fast."}, "startsAt":
"2026-11-03T10:15:12Z"}`. No severity was stated, so none was recorded.

- **Baseline** (10:15:26–10:16:27Z): /health 200 in 1.6 ms, /metrics snapshot,
  log tail, and one business probe (/products, 422.6 ms). The baseline already
  contained the configuration marker E1 and the duration jump around it.
- **Triage**: three lenses ran in parallel, blind to each other —
  infra-process, interfaces, software-defect. All three converged on the chaos
  marker; software-defect and interfaces found nothing attributable to their
  own domains. Three hypotheses formed.
- **Deep-dive round**: skipped — the triage evidence for H1 was deterministic
  and complete, so the hypotheses went straight to the judge.
- **Judge**: validated H1's core claim, invalidated H2 and H3, and named two
  open sub-claims (/metrics exemption uncited; post-marker route coverage
  incomplete). Both were settled by targeted gathering: the full log
  enumerates all seven post-marker business requests at 419.73–1445.515 ms
  with none fast (E6–E11, E14), and post-marker /metrics requests run at
  0.487–0.588 ms (E13). The judge also flagged "operator" as unattributed —
  the root-cause statement names the switch, not an actor.

## Hypotheses

### H1 — chaos latency switch (validated)

Chaos mode was enabled at runtime with 1500 ms of extra latency and a zero
failure rate (E1, E2). Prediction: business routes jump from single-digit
milliseconds to hundreds of milliseconds bounded by 1500 ms immediately after
the marker, with zero errors, while /health stays sub-millisecond and the
gauge stays 1 until a disable event. Confirmed on every point: before/after on
the same input (E4 → E8: /products/1 from 1.399 ms to 1227.656 ms), all seven
post-marker business requests slow (E6–E11, E14), no errors (E16, E17),
health and metrics exempt (E12, E13), gauge still 1 with no disable event
(E15). Nothing in the ledger offers a rival explanation for a uniform
~1000x jump across routes at a single moment with no errors.

### H2 — software defect (invalidated)

A code defect, data-dependent or not, cannot explain the same input being
fast before the toggle and slow after it (E4 vs E8), nor every route slowing
at one moment. No exceptions were recorded (E16 — weak alone, since some
clients create the series only on first increment) and every request counter
is 200/201 (E17 — the stronger form of the same point). Business logic still
completes correctly (orders are created).

### H3 — crash/restart or resource saturation (invalidated)

One startup event only (E18); uptime rises monotonically 54.0 → 296.76 s
(E20, E15); peak RSS is flat at 47185920 bytes (E19). CPU or event-loop
saturation is refuted by /health answering in under 1 ms while business
routes were slow (E12) — process-wide saturation would slow /health too.

## Safe next steps

- Watch `lab/logs/app.log` for a `chaos_disabled` event and the
  `faultline_chaos_enabled` gauge for a return to 0.
- After any disable event, re-probe `/products` and compare the duration with
  the pre-marker baseline (1–2 ms) to confirm recovery.
- Attribute the `POST /chaos/enable` request (request_id `06cae2c183a0`,
  client `127.0.0.1:49582`) through sources outside this surface — operator
  channels or shell history — read-only.

Remediation (turning the switch off) is out of scope for this journal.

## Gaps

- **Actor attribution.** The enable request came from localhost with a
  non-investigator request id; the allowed surface carries no identity beyond
  the client address, so who flipped the switch is unknown.
- **Onset window.** No business traffic exists between the marker
  (10:14:48.315Z) and the first slow request (10:14:51.102Z); onset is exact
  only to that 2.8 s window.
- **Latency bound.** The configured 1500 ms maximum is inferred from the
  marker, not observed; the highest measured duration is 1445.515 ms and the
  distribution looks random below the bound.
- **Lens coverage.** No dedicated load-saturation, third-party, or data-db
  lens exists in this repo; the lab contract declares no database and no
  third-party dependency, and the saturation shape is refuted by cited
  evidence (E12, E15, E19, E20), so the blind spot is accepted and recorded.
