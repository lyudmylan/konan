---
konan_journal: 2
investigation:
  id: 2026-11-15-routine-handover-check
  trigger: "manual (/konan human report; fingerprint human-1794751013, alertname human-report, no severity stated, startsAt 2026-11-15T13:56:53Z)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-15T13:57:04Z
  concluded: 2026-11-15T14:01:35Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "Users of the shop fail right now with HTTP 500 on the product detail route, because the handler divides by units_in_stock and raises an unhandled ZeroDivisionError."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E7, E8, E9, E10]
    evidence_against: [E2, E3, E6, E12]
  - id: H2
    statement: "The process is unstable: it crashed or restarted just before the check and is in a restart loop, hung, or degraded on resources."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E5, E4]
    evidence_against: [E1, E4, E5, E12, E13]
  - id: H3
    statement: "An operational degradation switch (chaos mode) injects errors or latency into user traffic."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E6, E12]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 with an unhandled ZeroDivisionError on each request while product 3 has units_in_stock 0 (the product detail handler divides by units_in_stock); only investigator probes triggered it, and no non-investigator request touched product 3 since the process start."
    evidence: [E6, E7, E8, E9, E10, E11, E12]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id=konan-1794751028-99566 (logged 2026-11-15T13:57:08.521Z)"
    quote: |-
      {"status":"ok","uptime_seconds":29.020616750232875}
      -- HTTP 200 in 0.002102s request_id=konan-1794751028-99566
  - id: E2
    type: metric
    source: "/metrics, request_id=konan-1794751029-99571 (logged 2026-11-15T13:57:09.102Z); the complete http_requests_total family"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E3
    type: metric
    source: "/metrics, request_id=konan-1794751029-99571; http_exceptions_total has no series, the chaos gauge reads 0"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 0
  - id: E4
    type: metric
    source: "/metrics, request_id=konan-1794751029-99571"
    quote: |-
      process_uptime_seconds 29.602359457872808
      process_max_rss_bytes 46923776
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:56:39.511Z (the only startup event in the file as read at 13:58:44Z; the file has no rotated backups)"
    quote: |-
      {"ts": "2026-11-15T13:56:39.511Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:56:40.238Z to 13:56:48.615Z (every access line with a non-investigator request id in the file as read at 13:58:44Z; fields trimmed to ts, message, request_id, duration_ms)"
    quote: |-
      {"ts": "2026-11-15T13:56:40.238Z", "message": "GET /health -> 200", "request_id": "599b93feb8b0", "duration_ms": 11.892}
      {"ts": "2026-11-15T13:56:40.262Z", "message": "GET /health -> 200", "request_id": "62b3557a12af", "duration_ms": 0.565}
      {"ts": "2026-11-15T13:56:40.263Z", "message": "GET /products -> 200", "request_id": "559ebef8fb4e", "duration_ms": 0.808}
      {"ts": "2026-11-15T13:56:41.318Z", "message": "GET /products/1 -> 200", "request_id": "c18e0f618f76", "duration_ms": 1.048}
      {"ts": "2026-11-15T13:56:42.375Z", "message": "GET /products/2 -> 200", "request_id": "07340b0fb10a", "duration_ms": 0.994}
      {"ts": "2026-11-15T13:56:44.438Z", "message": "POST /orders -> 201", "request_id": "33cba654908d", "duration_ms": 1.801}
      {"ts": "2026-11-15T13:56:45.499Z", "message": "POST /orders -> 201", "request_id": "ae1f6cdf158e", "duration_ms": 1.317}
      {"ts": "2026-11-15T13:56:47.558Z", "message": "GET /orders -> 200", "request_id": "be69ef693cf3", "duration_ms": 0.857}
      {"ts": "2026-11-15T13:56:48.615Z", "message": "GET /products/5 -> 200", "request_id": "323037dd3788", "duration_ms": 0.754}
  - id: E7
    type: probe
    source: "/products, request_id=konan-1794751136-99706"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.002012s request_id=konan-1794751136-99706
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:58:06.084Z (stack trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: |-
      {"ts": "2026-11-15T13:58:06.084Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794751086-99675", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:58:06.092Z"
    quote: |-
      {"ts": "2026-11-15T13:58:06.092Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794751086-99675", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.001, "client": "127.0.0.1:52660"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:58:14.572Z and 13:58:14.574Z (second probe of the same path; the stack field of the ERROR line is trimmed, its last frame equals the frame in E8)"
    quote: |-
      {"ts": "2026-11-15T13:58:14.572Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794751094-99688", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"}
      {"ts": "2026-11-15T13:58:14.574Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794751094-99688", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.697, "client": "127.0.0.1:52662"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:58:06.471Z"
    quote: |-
      {"ts": "2026-11-15T13:58:06.471Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794751086-99680", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.434, "client": "127.0.0.1:52661"}
  - id: E12
    type: metric
    source: "/metrics, request_id=konan-1794751124-99694 (logged 2026-11-15T13:58:44.041Z); the complete http_requests_total and http_exceptions_total families and the gauges"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/openapi.json",status="200"} 1
      http_requests_total{method="GET",path="/orders",status="200"} 3
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
      faultline_chaos_enabled 0
      process_uptime_seconds 124.54388370784
      process_max_rss_bytes 46923776
  - id: E13
    type: probe
    source: "/health, request_id=konan-1794751124-99699 (logged 2026-11-15T13:58:44.494Z)"
    quote: |-
      {"status":"ok","uptime_seconds":124.99684033310041}
      -- HTTP 200 in 0.001311s request_id=konan-1794751124-99699
gaps:
  - "Nothing before the process start at 2026-11-15T13:56:39.511Z is observable: the log starts at the startup line, there are no rotated backups, and the counters start at zero. The surface does not show why the process started then, or whether an earlier process failed."
  - "The observation window is about 125 seconds, with nine non-investigator requests in 9 seconds (13:56:40Z to 13:56:48Z) and none after. Slow memory growth, latency drift, and a restart loop with a longer period are not visible in a window this short."
  - "Order placement (POST /orders) for product 3 (units_in_stock 0) and product 4 (price null) was not tested: the probe surface is GET-only."
  - "Token totals were not captured: the session does not expose them to the investigation."
usage:
  model: claude-fable-5-2
  tokens: 1613909
  wall_clock_seconds: 271
---

# Routine handover check: no active incident; one latent defect on product 3

## Summary

**No active incident.** At the time of the check the shop service answered every
non-investigator request with 200 or 201 (E6), had no exception series and no non-2xx
series before the investigator's probes (E2, E3), reported health `ok` twice (E1, E13),
and had its chaos switch off (E3, E12). One **latent defect** rides along:
`GET /products/3` fails with HTTP 500 and an unhandled `ZeroDivisionError` on each
request, because product 3 has `units_in_stock` 0 and the product detail handler divides
by that value (E7, E8, E9, E10). Only the investigator's two probes triggered it; no user
requested product 3 (E6). The next user request for product 3 will fail. Confidence is
high for the observed window and limited by it: the process was 29 seconds old at the
first probe (E1, E5), and nothing before its start is observable.

Complaint object, verbatim, as the manual trigger built it:

```json
{
  "source": "human",
  "fingerprint": "human-1794751013",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports." },
  "startsAt": "2026-11-15T13:56:53Z"
}
```

Investigation start: 2026-11-15T13:57:04Z (trigger latency 11 seconds).

## Timeline

All times UTC, 2026-11-15.

- 13:56:39.511 — process start, `faultline 0.1.0 started` (E5). The only startup event.
- 13:56:40.238 to 13:56:48.615 — nine non-investigator requests, all 200 or 201,
  0.565 ms to 11.892 ms; the slowest is the first request after the start (E6).
- 13:57:08 to 13:57:09 — baseline: health `ok`, uptime 29.0 s (E1); all request series
  2xx (E2); no exception series, chaos gauge 0 (E3); memory peak 46923776 bytes (E4).
- 13:58:06.084 — first investigator probe of `/products/3`: `ZeroDivisionError`, HTTP 500
  (E8, E9). `/products/4` returns 200 at 13:58:06.471 (E11).
- 13:58:14.572 — second investigator probe of `/products/3`: same exception, HTTP 500
  (E10).
- 13:58:44 — closing snapshot: two 500s and two `ZeroDivisionError` counts, equal to the
  two investigator probes; chaos gauge 0; memory peak unchanged; uptime 124.5 s (E12);
  health `ok`, uptime 125.0 s (E13).

No configuration, deploy, or switch-change marker appears in the log other than the
startup line.

## Investigation

- **Setup.** `KONAN_ADAPTER` unset, so the surface contract is `docs/lab.md`. Budget:
  the default.
- **Baseline.** `/health`, `/metrics`, and the full log (18 lines at that time). Clean:
  E1 to E6.
- **Triage.** Three lenses in parallel, each blind to the others: infra-process,
  interfaces, software-defect. Infra-process: no anomaly (one start, monotonic uptime,
  flat memory peak, no latency trend, chaos off). Interfaces: no anomaly (no
  gateway-shaped status, no validation error, well-formed responses); it corrected the
  baseline count of non-investigator requests from ten to nine. Software-defect: one
  finding, the 500 on `/products/3`, with the caveat that both failures are its own
  probes.
- **Deep-dive.** None. The triage evidence for the defect was deterministic and complete
  (two of two probes, a stack frame naming the divisor, a control probe on product 4),
  and no deep-dive can reach the remaining gaps (see Gaps).
- **Verification.** The orchestrator re-read the log, took a closing `/metrics` and
  `/health` snapshot (E12, E13), and probed `/products` for the stock values (E7).
- **Judge.** One fresh judge, evidence only. H1 invalidated, H2 invalidated, H3
  invalidated; the latent defect claim validated. The judge's limits are in Gaps.

## Hypotheses

### H1 — users fail with HTTP 500 on the product detail route (software-defect): invalidated

The mechanism is real (E7, E8, E9, E10), but the prediction of user impact failed. Before
the first probe of `/products/3` the counters held no 500 series and the exception
family was empty (E2, E3). All nine non-investigator requests returned 2xx, and none
requested product 3 (E6). The two 500s and the two exceptions in the closing snapshot
equal the investigator's two probes (E12, with E9 and E10). The defect is therefore a
latent finding, not the active incident. What would settle it the other way: one access
line with a non-investigator request id and status 500 on the product detail route.

### H2 — the process is unstable (infra-process): invalidated

The process started 29 seconds before the first probe (E5, E4), which is the only fact
for this hypothesis. Against it: one startup event (E5), health `ok` twice (E1, E13), an
identical memory peak in both scrapes (E4, E12), and four uptime readings that all give
the same start time, 13:56:39.5 (E1, E4, E12, E13). No evidence shows a crash, because
nothing in the telemetry predates this process. What would settle it: a record of what
started the process at 13:56:39, or an exit record of an earlier process.

### H3 — a degradation switch injects errors or latency (infra-process): invalidated

No evidence supports it. The chaos gauge reads 0 in both scrapes (E3, E12), the log has
no chaos event, and all nine non-investigator requests are 2xx at 11.9 ms or less (E6).
The only non-2xx responses have a different, traced cause in handler code (E8, E10).
Both gauge samples came after the user traffic ended; for the traffic window itself the
nine clean requests are the evidence.

## Safe next steps

- Watch `http_requests_total{path="/products/{product_id}",status="500"}` and
  `http_exceptions_total{type="ZeroDivisionError"}`: the values 2 and 2 are investigator
  probes; any rise is user impact from the latent defect.
- Hand the latent defect to the owners of the service with E7 to E10: the divisor in the
  product detail handler is 0 for product 3.
- Read the record of what started the process at 13:56:39Z (a launcher or supervisor
  log), to learn whether the start followed a failure.
- Repeat the `/metrics` and `/health` read later in the shift, to cover memory growth
  and latency drift over a longer window.
- Note for the owners: product 4 has `price` null in the product list (E7). No failure
  was observed for it; `/products/4` returns 200 (E11).

## Gaps

- **Before the start.** The log begins at the startup line at 13:56:39.511Z, no rotated
  backups exist, and the counters start at zero. A fault that ended with a restart would
  be invisible here. "Healthy" means healthy since this start.
- **Short window.** About 125 seconds of telemetry, nine non-investigator requests in
  9 seconds, and none after 13:56:48Z. Slow memory growth, latency drift, and a restart
  loop with a period longer than the window are not excluded.
- **Order placement.** `POST /orders` for product 3 and for product 4 was not tested;
  the probe surface is GET-only by contract.
- **Token totals.** Not captured; the session does not expose them to the investigation.
