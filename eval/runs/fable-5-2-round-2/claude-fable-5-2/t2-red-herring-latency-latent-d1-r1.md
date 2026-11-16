---
konan_journal: 2
investigation:
  id: 2026-11-15-shop-slow-chaos-latency
  trigger: 'manual (/konan, human profile). Complaint object: {"source":"human","fingerprint":"human-1794773705","labels":{"alertname":"human-report"},"annotations":{"summary":"Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."},"startsAt":"2026-11-15T20:15:05Z"}. Investigation start 2026-11-15T20:15:17Z; trigger latency 12 s. No severity stated by the reporter.'
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-15T20:15:17Z
  concluded: 2026-11-15T20:20:26Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The chaos switch inside the target was turned on at 20:14:49.029Z with extra_latency_ms 1500 and failure_rate 0.0; while it is on it injects up to 1.5 s of latency into every shop route and none into /health, and it was still on at 20:19:00Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target was turned on at 20:14:49.029Z with extra_latency_ms 1500 and failure_rate 0.0. While on, it adds latency to the shop routes (/products, /products/{id}, /orders) and not to /health. It is still on."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E17, E22]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled exception for some input, and users received an error response from it (the error page that users report seeing once)."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E18, E19, E20, E21, E23]
    evidence_against: [E13, E14, E15]
  - id: H3
    statement: "Demand exceeds the capacity of the target, and requests slow down under volume."
    incident_class: load-saturation
    state: invalidated
    evidence_for: [E5, E6, E7, E8, E9]
    evidence_against: [E13, E2, E3, E4, E17, E16]
  - id: H4
    statement: "A process restart at 20:14:43 causes the slowness."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E15]
    evidence_against: [E2, E3, E4, E24, E25, E16, E10]
latent_findings:
  - statement: "GET /products/3 fails with HTTP 500, ZeroDivisionError: the product has units_in_stock 0 and the product detail code divides by it. Only the investigator's own probe triggered it in this process lifetime; no user request received it."
    evidence: [E18, E19, E20, E21, E23]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:49.029Z"
    quote: |-
      {"ts": "2026-11-15T20:14:49.029Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "6d738ea7d79a", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:43.872Z"
    quote: |-
      {"ts": "2026-11-15T20:14:43.872Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "cff8050c4d51", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.545, "client": "127.0.0.1:56243"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:44.922Z"
    quote: |-
      {"ts": "2026-11-15T20:14:44.922Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "78babce5d4f3", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.086, "client": "127.0.0.1:56244"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:45.976Z"
    quote: |-
      {"ts": "2026-11-15T20:14:45.976Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "2d69f1d38a49", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.827, "client": "127.0.0.1:56245"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:52.550Z"
    quote: |-
      {"ts": "2026-11-15T20:14:52.550Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "20f33864b315", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1468.411, "client": "127.0.0.1:56248"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:54.639Z"
    quote: |-
      {"ts": "2026-11-15T20:14:54.639Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "451baead8c5b", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1029.794, "client": "127.0.0.1:56249"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:56.549Z"
    quote: |-
      {"ts": "2026-11-15T20:14:56.549Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "8619afd5a7af", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 851.858, "client": "127.0.0.1:56250"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:58.837Z"
    quote: |-
      {"ts": "2026-11-15T20:14:58.837Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "065f4ada71ae", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1242.541, "client": "127.0.0.1:56251"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:15:00.220Z"
    quote: |-
      {"ts": "2026-11-15T20:15:00.220Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "cb2c93fdefa1", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 323.069, "client": "127.0.0.1:56252"}
  - id: E10
    type: metric
    source: "/metrics @ 2026-11-15T20:16:43Z (request_id konan-1794773803-23694)"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 120.26037424989045
      process_max_rss_bytes 47251456
  - id: E11
    type: probe
    source: "/health (request_id konan-1794773722-23563)"
    quote: |-
      {"status":"ok","uptime_seconds":39.366518332622945}
      -- HTTP 200 in 0.001699s request_id=konan-1794773722-23563
  - id: E12
    type: probe
    source: "/products (request_id konan-1794773736-23577)"
    quote: |-
      -- HTTP 200 in 1.212955s request_id=konan-1794773736-23577
  - id: E13
    type: metric
    source: "/metrics @ 2026-11-15T20:16:43Z (request_id konan-1794773803-23694); the complete list of http_requests_total series at that time"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/orders/{order_id}",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E14
    type: metric
    source: "/metrics @ 2026-11-15T20:16:43Z (request_id konan-1794773803-23694); the complete http_exceptions_total block at that time, no series line follows the TYPE line"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:43.127Z (the only startup event; the file starts at 20:14:43.126Z and has no rotated backups)"
    quote: |-
      {"ts": "2026-11-15T20:14:43.127Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E16
    type: metric
    source: "/metrics @ 2026-11-15T20:15:22Z (request_id konan-1794773722-23568)"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 39.592713499907404
      process_max_rss_bytes 47251456
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:16:16.955Z"
    quote: |-
      {"ts": "2026-11-15T20:16:16.955Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794773776-23669", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.477, "client": "127.0.0.1:56288"}
  - id: E18
    type: probe
    source: "/products/3 (request_id konan-1794773927-23757)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794773927-23757"}
      -- HTTP 500 in 1.327752s request_id=konan-1794773927-23757
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:18:48.540Z (the only ERROR line in the file; stack trimmed to its last frame, and the local path prefix of the target's checkout is redacted as <faultline>)"
    quote: |-
      {"ts": "2026-11-15T20:18:48.540Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794773927-23757", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<faultline>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E20
    type: metric
    source: "/metrics @ 2026-11-15T20:19:00Z (request_id konan-1794773940-23770)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1
      http_exceptions_total{type="ZeroDivisionError"} 1
      faultline_chaos_enabled 1
      process_uptime_seconds 256.9357698750682
      process_max_rss_bytes 47251456
  - id: E21
    type: probe
    source: "/products (request_id konan-1794773736-23577); response body trimmed to the record of product 3"
    quote: |-
      {"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:49.030Z"
    quote: |-
      {"ts": "2026-11-15T20:14:49.030Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "6d738ea7d79a", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.777, "client": "127.0.0.1:56247"}
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:18:48.557Z"
    quote: |-
      {"ts": "2026-11-15T20:18:48.557Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794773927-23757", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 1325.435, "client": "127.0.0.1:56297"}
  - id: E24
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:43.843Z"
    quote: |-
      {"ts": "2026-11-15T20:14:43.843Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "d2d2521bcf0c", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 11.771, "client": "127.0.0.1:56241"}
  - id: E25
    type: log
    source: "lab/logs/app.log @ 2026-11-15T20:14:43.873Z"
    quote: |-
      {"ts": "2026-11-15T20:14:43.873Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "c14874937330", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 1.939, "client": "127.0.0.1:56242"}
gaps:
  - "No telemetry exists before the process start at 20:14:43.126Z: one log file, no rotated backups, counters start at zero. The complaint says 'the last few minutes', and the process was 22 s old when the complaint arrived. The 'error page once' report can be neither confirmed nor excluded for the time before that start, including an error page caused by the restart itself."
  - "The actor behind the switch is not visible: the enable request came from 127.0.0.1 with no identity field, and the operator surface (/chaos) is outside the investigator's allowlist. The switch state was read only through the gauge and the log."
  - "The surface has no CPU metric. Load saturation was excluded by request volume, the step-shaped onset and the fast /health, not by a CPU reading."
  - "The repo has three lenses (infra-process, software-defect, interfaces). No lens exists for load-saturation, third-party or data-db; load was tested as H3 by the orchestrator, and the lab has no third party and no real database (docs/lab.md, known gaps)."
  - "That /health and /metrics are exempt from the injected latency rests on samples (two /health requests and five /metrics requests, all under 1 ms after the switch), not on a reading of code. /orders/{order_id} has one sample (241.931 ms)."
  - "The injected delay varies per request (153 ms to 1468 ms observed, all under the configured 1500 ms); its distribution was not characterised."
usage:
  model: claude-fable-5-2
  tokens: 1491354
  wall_clock_seconds: 309
---

# Shop routes slow: a chaos switch injects up to 1.5 s of latency per request

## Summary

**Verdict: root cause identified** — `infra-process` / `degradation-switch`. The chaos
switch inside the target was turned on at 20:14:49.029Z with `extra_latency_ms` 1500 and
`failure_rate` 0.0 (E1, E22). From the next request on, every shop route takes 153 ms to
1468 ms where it took 1–2 ms before (E2–E4 against E5–E9, E12). `/health` stays under
1 ms while the switch is on (E11, E17), which is why the health checks are green and
fast. The switch was still on at 20:19:00Z (E20); no `chaos_disabled` event is in the log.

**Impact:** all user requests on `/products`, `/products/{id}`, `/orders` and
`POST /orders` after 20:14:49Z were slow; all of them succeeded (2xx). **The "error page"
is not confirmed:** in this process lifetime no user request received a non-2xx status
(E13, E14), and the switch is configured to inject no errors (`failure_rate` 0.0, E1).
Telemetry before the process start at 20:14:43Z does not exist (see Gaps).

**Latent finding, not the incident:** `GET /products/3` returns HTTP 500 with a
`ZeroDivisionError` — product 3 has `units_in_stock` 0 and the detail code divides by it
(E18, E19, E21). Only the investigator's probe triggered it (E20, E23). A user who opens
product 3 gets an error page; no user did so in the observed window.

**Confidence:** high for the slowness (deterministic marker, step onset, live
reproduction, judge validated). The error-page report stays open only for the time before
the log starts.

## Timeline

All times UTC, 2026-11-15.

- 20:14:43.127 — process start, the only `startup` event (E15).
- 20:14:43.843–20:14:45.976 — five requests, all fast: `/health` 11.771 ms and 1.939 ms
  (E24, E25), `/products` 1.545 ms (E2), `/products/1` 1.086 ms (E3), `POST /orders`
  1.827 ms (E4). These are all the request lines before the switch.
- **20:14:49.029 — configuration-change marker: `chaos_enabled`, `failure_rate` 0.0,
  `error_status` 503, `extra_latency_ms` 1500 (E1), by `POST /chaos/enable` from
  127.0.0.1 (E22).**
- 20:14:52.550 — first slow request: `GET /products` 1468.411 ms (E5).
- 20:14:54.639–20:15:00.220 — every user request is slow: 1029.794 ms, 851.858 ms,
  1242.541 ms, 323.069 ms (E6–E9).
- 20:15:05 — complaint raised (`startsAt`); 20:15:17 — investigation start.
- 20:15:22 — `/health` 200 in 1.7 ms (E11); `faultline_chaos_enabled 1`, uptime 39.59 s (E16).
- 20:15:37 — investigator probe `/products` 200 in 1.213 s (E12): slowness reproduced.
- 20:16:16.955 — `/health` 0.477 ms with the switch on (E17).
- 20:16:43 — all request series 2xx, no exception series, switch on, uptime 120.26 s
  (E10, E13, E14).
- 20:18:48.540 — investigator probe `/products/3`: unhandled `ZeroDivisionError`, HTTP 500
  (E18, E19, E23). Investigator traffic, latent finding.
- 20:19:00 — switch still on; the one 500 and the one exception are the investigator's (E20).

## Investigation

**Complaint object** (adapter `/konan`, human profile):

```json
{
  "source": "human",
  "fingerprint": "human-1794773705",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast." },
  "startsAt": "2026-11-15T20:15:05Z"
}
```

Investigation start: 2026-11-15T20:15:17Z (trigger latency 12 s). `KONAN_ADAPTER` was
unset, so the surface contract is `docs/lab.md`.

**Baseline.** `/health` green and fast (E11). `/metrics`: only 2xx series, no exception
series, `faultline_chaos_enabled 1`, uptime 39.59 s (E16). Log: one startup, a
`chaos_enabled` WARNING, request durations 1–2 ms before it and 323–1468 ms after it.
Business surface checked, not only health: `/products` 1.213 s (E12), `/orders` 0.155 s,
`/products/1` 0.528 s.

**Triage (one round, three lenses in parallel, blind to each other).**

- infra-process: chaos switch on with latency injection; latency step at the marker;
  `/health` and `/metrics` exempt; one startup, no restart loop, memory flat.
- software-defect: no anomaly in its domain; slowness on all routes and not
  input-dependent; no exception or error evidence.
- interfaces: the marker and the sharp onset; classified the mechanism as an internal
  switch (`infra-process`), not an interface failure; no contract violations.

No lens found evidence for the error page.

**Deep-dive.** Skipped for H1: the triage evidence was deterministic and complete
(marker, before/after durations, live gauge, live reproduction). Two targeted probes
followed the first judge round, on the inputs that the product list marks as unusual:
`/products/3` (stock 0) returned 500 (E18); `/products/4` (price null) returned 200.

**Judge, round 1** (evidence only): H1 validated; H2, H3, H4 invalidated. The judge's
limits on H1 are in the wording above: the added latency varies up to 1500 ms; "still on"
holds as of the last reading; the `/health` exemption rests on samples.

**Judge, round 2** (fresh judge, H2 only, with the new `/products/3` evidence): H2 as
stated invalidated — part (a) "the defect exists" validated, part (b) "users received an
error response from it" invalidated for the whole process lifetime. The defect is
recorded as a latent finding.

## Hypotheses

### H1 — chaos switch injects latency (infra-process) — validated

The `chaos_enabled` marker (E1) carries the full configuration: 1500 ms extra latency,
failure rate 0.0. The request that set it is in the access log (E22) and in the counters
(E13). Before the marker the shop routes take 1–2 ms (E2–E4); the first request after it
takes 1468 ms (E5), and all later shop requests are slow, never above 1500 ms (E6–E9,
E12). `/health` is not affected (E11, E17). The gauge reads 1 at every reading (E16, E10,
E20). The prediction "a shop probe is slow now, a health probe is fast now" was confirmed
by probing. No evidence against.

### H2 — unhandled exception gives users an error page (software-defect) — invalidated

A defect exists: `GET /products/3` raises `ZeroDivisionError` in the product detail code
because `units_in_stock` is 0 (E18, E19, E21). But the only 500 and the only exception
carry the investigator's request id (E20, E23). Before that probe, the counters held only
2xx series and no exception series (E13, E14), and no user request line names product 3.
So no user received an error from it in this process lifetime. The window starts at the
process start (E15). The evidence that would reopen it: one failed request with a
non-investigator id, from a source that covers the time before 20:14:43Z.

### H3 — load saturation — invalidated

The requests are slow (E5–E9), but demand is tiny: 23 requests in 120 s, 8 of them the
investigator's own `/health` and `/metrics` calls (E13). The onset is a step between two
adjacent requests at the marker, not a rise with volume (E2–E4 against E5). `/health`
answers in 0.477 ms in the same period (E17). Peak memory is unchanged (E16, weak
evidence). A CPU reading would settle it fully; the surface has none.

### H4 — process restart causes the slowness (infra-process) — invalidated

The process did start 22 s before the complaint (E15). But all five requests between the
start and the marker were fast (E2, E3, E4, E24, E25), so there is no warm-up slowness,
and uptime rises without a reset across the readings (E16, E10). The slowness starts at
the marker, not at the start.

## Safe next steps

Read-only suggestions; remediation is out of scope of a journal.

- Ask the operators who sent `POST /chaos/enable` at 20:14:49Z and whether it was
  intended; the request id is `6d738ea7d79a`.
- Watch `faultline_chaos_enabled` and the next `chaos_disabled` log event; compare shop
  route durations before and after it to confirm recovery.
- Ask the users who saw the error page for the time and the page; compare with any
  record that covers the time before 20:14:43Z (an earlier process log, a proxy log).
- Hand the latent finding to the owners of the target: `GET /products/3`, request id
  `konan-1794773927-23757`, stack in the log line at 20:18:48.540Z.
- Note for monitoring owners: `/health` does not see this degradation; a latency reading
  of a business route would.

## Gaps

- **Nothing before 20:14:43.126Z.** One log file, no backups, counters from zero. The
  complaint speaks of "the last few minutes", the process was 22 s old. The error-page
  report is open for that earlier time only, including a possible error during the
  restart itself.
- **No actor for the switch.** The enable request shows a loopback client and no
  identity; the operator surface is outside the investigator's allowlist.
- **No CPU metric.** Load saturation is excluded by volume, onset shape and the fast
  `/health`, not by a CPU reading.
- **Lens coverage.** Three lenses exist. Load was tested by the orchestrator as H3;
  third-party and data-db have no lens, and the lab has neither a third party nor a real
  database.
- **Exemption by samples.** `/health` and `/metrics` being exempt from the injected
  latency rests on seven fast samples, not on code; `/orders/{order_id}` has one sample.
- **Delay distribution.** The injected delay varies per request (153–1468 ms observed);
  it was not characterised.
