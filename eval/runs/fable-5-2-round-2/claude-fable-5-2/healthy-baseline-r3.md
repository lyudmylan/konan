---
konan_journal: 2
investigation:
  id: 2026-11-15-handover-check
  trigger: "manual — /konan human profile; source human; fingerprint human-1794770886; labels.alertname human-report; no severity stated; startsAt 2026-11-15T19:28:06Z; investigation start 2026-11-15T19:28:19Z (trigger latency 13 s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-15T19:28:19Z
  concluded: 2026-11-15T19:33:18Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The shop fails user requests now: GET /products/{id} raises an unhandled ZeroDivisionError for a product with units_in_stock 0 (product 3) and returns HTTP 500."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E7, E8, E9, E10, E12]
    evidence_against: [E2, E6]
  - id: H2
    statement: "The process crashed or restarted shortly before the check, and that interrupted service."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E4, E5]
    evidence_against: [E6, E13]
  - id: H3
    statement: "An internal degradation switch (chaos mode) injects errors or latency now."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E12, E13]
latent_findings:
  - statement: "GET /products/3 fails on every call with HTTP 500: get_product divides by units_in_stock, which is 0 for product 3 (unhandled ZeroDivisionError). Only investigator probes triggered it in the visible window (since 2026-11-15T19:27:52Z); no user request touched it."
    evidence: [E6, E7, E8, E9, E10, E11, E12, E14]
evidence:
  - id: E1
    type: probe
    source: "/health, request id konan-1794770899-20229"
    quote: |-
      {"status":"ok","uptime_seconds":27.59968883311376}
      -- HTTP 200 in 0.001680s request_id=konan-1794770899-20229
  - id: E2
    type: metric
    source: "/metrics, request id konan-1794770900-20236 (baseline scrape, 2026-11-15T19:28:20Z); the complete http_requests_total block and the empty http_exceptions_total block"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E3
    type: metric
    source: "/metrics, request id konan-1794770900-20236 (baseline scrape)"
    quote: "faultline_chaos_enabled 0"
  - id: E4
    type: metric
    source: "/metrics, request id konan-1794770900-20236 (baseline scrape)"
    quote: |-
      process_uptime_seconds 28.164641249924898
      process_max_rss_bytes 47464448
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:27:52.172Z (first lines of the file; no rotated backups exist; the first line is trimmed after the message field)"
    quote: |-
      {"ts": "2026-11-15T19:27:52.172Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [20132]"
      {"ts": "2026-11-15T19:27:52.172Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:27:52.888Z to 19:28:01.240Z — every access line whose request id has no konan- prefix (fields trimmed to ts, message, request_id)"
    quote: |-
      "ts": "2026-11-15T19:27:52.888Z", "message": "GET /health -> 200", "request_id": "e2888a682cc6"
      "ts": "2026-11-15T19:27:52.918Z", "message": "GET /products -> 200", "request_id": "d8efb82d1545"
      "ts": "2026-11-15T19:27:52.919Z", "message": "GET /health -> 200", "request_id": "c2b1589b36c0"
      "ts": "2026-11-15T19:27:53.974Z", "message": "GET /products/1 -> 200", "request_id": "b5068af8fa6c"
      "ts": "2026-11-15T19:27:55.026Z", "message": "GET /products/2 -> 200", "request_id": "fa5369d33817"
      "ts": "2026-11-15T19:27:57.081Z", "message": "POST /orders -> 201", "request_id": "840a0080a7db"
      "ts": "2026-11-15T19:27:58.134Z", "message": "POST /orders -> 201", "request_id": "b51723c4f1e6"
      "ts": "2026-11-15T19:28:00.186Z", "message": "GET /orders -> 200", "request_id": "4a2a22039a5d"
      "ts": "2026-11-15T19:28:01.240Z", "message": "GET /products/5 -> 200", "request_id": "bd6f2e3d9717"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:29:24.219Z (stack trimmed to its last frame; <checkout> replaces the local path prefix of the target's checkout)"
    quote: |-
      {"ts": "2026-11-15T19:29:24.219Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794770964-20377", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "… File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n … ZeroDivisionError: division by zero"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:29:24.227Z"
    quote: |-
      {"ts": "2026-11-15T19:29:24.227Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794770964-20377", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.294, "client": "127.0.0.1:55660"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:29:30.486Z and 19:29:30.489Z (first line trimmed before the stack field)"
    quote: |-
      {"ts": "2026-11-15T19:29:30.486Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794770970-20402", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"
      {"ts": "2026-11-15T19:29:30.489Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794770970-20402", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.876, "client": "127.0.0.1:55663"}
  - id: E10
    type: probe
    source: "/products, request id konan-1794771012-20448"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001421s request_id=konan-1794771012-20448
  - id: E11
    type: probe
    source: "/products/4, request id konan-1794771012-20453"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001376s request_id=konan-1794771012-20453
  - id: E12
    type: metric
    source: "/metrics, request id konan-1794770993-20422 (scrape at 2026-11-15T19:29:53Z); no other series in this scrape has a status outside 200/201"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
  - id: E13
    type: metric
    source: "/metrics, request id konan-1794770993-20422 (scrape at 2026-11-15T19:29:53Z)"
    quote: |-
      faultline_chaos_enabled 0
      process_uptime_seconds 121.4328569159843
      process_max_rss_bytes 47464448
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:29:13.597Z and 19:29:23.695Z — the two investigator requests that raised the 200 count of the product route from 3 (E2) to 5 (E12); fields trimmed to ts, message, request_id"
    quote: |-
      "ts": "2026-11-15T19:29:13.597Z", "message": "GET /products/5 -> 200", "request_id": "konan-1794770953-20345"
      "ts": "2026-11-15T19:29:23.695Z", "message": "GET /products/4 -> 200", "request_id": "konan-1794770963-20372"
  - id: E15
    type: probe
    source: "/products/999, request id konan-1794771013-20458"
    quote: |-
      {"detail":"no such product: 999"}
      -- HTTP 404 in 0.001545s request_id=konan-1794771013-20458
  - id: E16
    type: probe
    source: "/orders, request id konan-1794771013-20464"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T19:27:57.080+00:00"},{"id":2,"product_id":2,"quantity":2,"total_price":46.0,"created_at":"2026-11-15T19:27:58.133+00:00"}]
      -- HTTP 200 in 0.002384s request_id=konan-1794771013-20464
gaps:
  - "No telemetry exists before 2026-11-15T19:27:52.172Z: the log starts at the startup event and has no rotated backups, so a first start and a restart after a failure look the same (H2 stays inconclusive). A process supervisor or system log is outside the surface."
  - "The user traffic sample is small: 9 requests in 9 seconds, the last at 19:28:01.240Z. 'No user impact' holds for that window only."
  - "No user request touched /products/3 in the visible window; whether real users request that product is unknown."
  - "POST is outside the read-only surface: an order for product 4 (price null) and an order for product 3 (stock 0) were not tested."
  - "The surface has no CPU or worker gauge; saturation was read from latency and peak RSS only."
usage:
  model: claude-fable-5-2
  tokens: 1627495
  wall_clock_seconds: 299
---

# Handover check of the shop service: no active incident, one latent defect on product 3

## Summary

**No active incident.** At the check, health was green (E1), every one of the 9 user
requests since process start returned 200 or 201 (E6, E2), no exception was counted
before the investigation (E2), the chaos switch was off (E3, E13), and peak memory was
flat (E4, E13). The business surface answers: product list, order list, product detail,
and a clean 404 for a missing id (E10, E16, E11, E15).

**One latent defect rides along.** `GET /products/3` returns HTTP 500 on every call: the
product-detail handler divides by `units_in_stock`, and product 3 has stock 0 (E7, E8,
E9, E10). Only investigator probes (`konan-` request ids) triggered it; no user request
touched product 3 in the visible window (E6). The two `ZeroDivisionError` counts and the
two 500s now in the metrics belong to this investigation (E12) — subtract them when you
read the counters.

**One open point.** The process was 27 seconds old at the check (E1, E5). The log has
nothing before that start, so the evidence cannot tell a first start from a restart
after a failure (H2, inconclusive).

Confidence: high for "no user-facing failure between 19:27:52Z and 19:30:13Z"; the
window is short and the sample small (see Gaps).

Complaint object as delivered by the `/konan` adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794770886",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports." },
  "startsAt": "2026-11-15T19:28:06Z"
}
```

Investigation start: 2026-11-15T19:28:19Z (trigger latency 13 s).

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 19:27:52.172 | Process start: server process 20132, `startup` event, version 0.1.0. First line of the log. | E5 |
| 19:27:52.888 – 19:28:01.240 | 9 user requests, all 200/201; two orders created. | E6, E16 |
| 19:28:06 | Complaint raised (handover check). | — |
| 19:28:19 | Investigation start; `/health` ok, uptime 27.6 s. | E1 |
| 19:28:20 | Baseline scrape: only 200/201 series, no exception series, chaos 0, uptime 28.2 s. | E2, E3, E4 |
| 19:29:24.219 | First investigator probe of `/products/3`: unhandled `ZeroDivisionError`, HTTP 500. | E7, E8 |
| 19:29:30.489 | Second investigator probe of `/products/3`: same exception, HTTP 500. | E9 |
| 19:29:53 | Scrape: 2 exceptions, 2 statuses 500, both on the product route; chaos 0; uptime 121.4 s; peak RSS unchanged. | E12, E13 |
| 19:30:12 – 19:30:13 | Product list shows product 3 with stock 0; product 4 returns 200; missing id returns 404; order list returns 200. | E10, E11, E15, E16 |

No configuration, deploy, or chaos marker appears in the log apart from the single
`startup` event.

## Investigation

- **Setup.** `KONAN_ADAPTER` unset, so the surface contract is `docs/lab.md`. Budget:
  one triage round, at most 3 deep-dives per round, at most 2 rounds.
- **Baseline.** `/health` (E1), `/metrics` (E2–E4), full read of `lab/logs/app.log`
  (18 lines at that time; E5, E6). Normal: 200/201 only, durations 0.8–12.1 ms (the
  12.1 ms is the first request after start), no WARNING or ERROR line.
  `lab/server.out` was also opened once; it repeats the app log and is not cited.
- **Triage.** The complaint is vague, so all three lenses ran in parallel, blind to
  each other: infra-process, interfaces, software-defect.
  - infra-process: no anomalies. One startup, uptime in step with the clock, peak RSS
    flat, chaos off. Limit named: nothing visible before the start.
  - interfaces: no anomalies. No 502/503/504, no 422, well-formed JSON on the shop
    routes.
  - software-defect: one finding — deterministic 500 on `/products/3`
    (`ZeroDivisionError`), triggered by its own probes only.
- **Deep-dive.** Skipped. The triage evidence for the defect was already deterministic
  and complete (two of two probes, the stack frame, the stock value, a control product),
  and nothing a GET-only probe can reach would settle H2.
- **Orchestrator checks.** Second scrape (E12, E13), verbatim product list (E10),
  control product 4 (E11), missing id (E15), order list (E16).
- **Judge.** A fresh judge saw the claims and the verbatim evidence only. Verdicts:
  H1 invalidated as an incident claim (defect real, no user impact), H2 inconclusive,
  H3 invalidated, latent finding validated. The judge asked for the two 200 requests
  between the scrapes; E14 accounts for them.
- **Conclusion.** No second round: the one item that would settle H2 (a record of an
  earlier process exit) is outside the surface.

## Hypotheses

### H1 — users fail now on the product-detail defect (software-defect) — invalidated

The defect is real: two investigator requests to `/products/3` each raised
`ZeroDivisionError` at `shop.py` line 64 and returned 500 (E7, E8, E9); the product list
shows `units_in_stock` 0 for product 3 only (E10); the counters show exactly two
exceptions and two 500s (E12). The incident claim fails: both failing request ids carry
the `konan-` prefix, the baseline scrape before any such probe had no exception series
(E2), and every user request returned 200 or 201 (E6). What would reverse it: one access
line `GET /products/3 -> 500` with a request id without the `konan-` prefix.

### H2 — a crash or restart shortly before the check interrupted service (infra-process) — inconclusive

For: the process was 27.6 s old at the first probe (E1, E4) and the log opens with a
start at 19:27:52.172Z (E5). Against: service was clean from the first request on (E6),
and uptime rose in step with the clock with no reset (E13). The evidence proves a start,
not a crash: the log has nothing before it. What would settle it: a record of a process
exit before 19:27:52Z from a process supervisor or system log.

### H3 — a degradation switch injects errors or latency now (infra-process) — invalidated

`faultline_chaos_enabled` is 0 at both scrapes (E3, E13). No status outside 200/201
existed at baseline (E2), and the only errors since then are the two 500s that match the
two `ZeroDivisionError` counts one to one (E12). No evidence for.

### Latent finding — `/products/3` always fails

Validated by the judge with two limits: "only investigator probes" covers the time since
19:27:52Z only, and "every call" rests on two of two probes plus the stack frame (E7).
Product 4 on the same route is the control: stock 75, HTTP 200, `turnover_score` 0.0
(E11). E14 shows the other two investigator requests on that route, both 200.

## Safe next steps

Read-only only.

- Watch `http_exceptions_total{type="ZeroDivisionError"}` and
  `http_requests_total{path="/products/{product_id}",status="500"}`. Both stand at 2
  from this investigation; a higher value with a request id without the `konan-` prefix
  is user impact.
- Read the process supervisor or system log for an exit before 19:27:52Z, to settle H2.
- Report the defect to the owner of the service with E7 and E10: the division by
  `units_in_stock` at `shop.py` line 64.
- Watch the stock of the other products in the product list (E10). If stock falls with
  orders — not verified here — a product that reaches 0 meets the same division.
- Ask the owner about product 4, `price` null (E10): its effect on an order is untested.

## Gaps

- **Before the start.** The log begins at 19:27:52.172Z and has no backups. The surface
  shows nothing about the time before it; H2 cannot be settled from here.
- **Small sample.** 9 user requests in 9 seconds, none after 19:28:01.240Z. The verdict
  describes that window.
- **Product 3 and users.** No user request touched `/products/3`; the rate at which
  real users ask for it is unknown.
- **POST untested.** The surface is GET-only. An order for product 4 (`price` null) or
  product 3 (stock 0) was not tested.
- **No CPU or worker gauge.** Saturation was read from latency and peak RSS only.
- **Tokens.** The session could not capture token totals (`usage.tokens: null`).
