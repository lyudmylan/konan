---
konan_journal: 2
investigation:
  id: 2026-11-15-handover-check
  trigger: "manual: /konan human report; complaint startsAt 2026-11-15T19:23:05Z, investigation start 2026-11-15T19:23:17Z, trigger latency 12 s; fingerprint human-1794770585, alertname human-report, no severity stated"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-15T19:23:17Z
  concluded: 2026-11-15T19:26:57Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The route GET /products/{product_id} raises an unhandled ZeroDivisionError for a product whose units_in_stock is 0 (product 3); the division is in get_product, field turnover_score. Up to the last reading only an investigator probe triggered it; no non-investigator request was observed to fail."
    incident_class: software-defect
    state: validated
    evidence_for: [E6, E7, E8, E9, E10, E5, E2]
    evidence_against: []
  - id: H2
    statement: "The process is unstable: it crashed or restarts in a loop, and that affects the service now."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1, E3]
    evidence_against: [E2, E9, E4, E5]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 with an unhandled ZeroDivisionError: get_product divides by units_in_stock, and product 3 has units_in_stock 0. Only an investigator probe triggered it; any user request for product 3 would fail the same way."
    evidence: [E6, E7, E8, E9]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id konan-1794770601-19880"
    quote: |-
      {"status":"ok","uptime_seconds":31.03465100005269}
      -- HTTP 200 in 0.001621s request_id=konan-1794770601-19880
  - id: E2
    type: metric
    source: "/metrics, request_id konan-1794770602-19885 (logged 2026-11-15T19:23:22.014Z); the complete http_requests_total series plus chaos and process gauges; http_exceptions_total had no series line"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
      faultline_chaos_enabled 0
      process_uptime_seconds 31.546896958258003
      process_max_rss_bytes 46972928
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:22:50.479Z (the only startup event; the file has no backup files)"
    quote: |-
      {"ts": "2026-11-15T19:22:50.479Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:22:56.431Z"
    quote: |-
      {"ts": "2026-11-15T19:22:56.431Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "efadefe3bf2c", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.879, "client": "127.0.0.1:55548"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:22:59.531Z (the last of 9 non-investigator access lines, 19:22:51.202Z to 19:22:59.531Z, all status 200 or 201)"
    quote: |-
      {"ts": "2026-11-15T19:22:59.531Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "73cc47dc9f5f", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.791, "client": "127.0.0.1:55550"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:24:06.870Z (the only ERROR line; stack trimmed to its last frame; the local path prefix is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T19:24:06.870Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794770646-19974", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:24:06.878Z (the only access line with a status outside 200/201)"
    quote: |-
      {"ts": "2026-11-15T19:24:06.878Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794770646-19974", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.617, "client": "127.0.0.1:55586"}
  - id: E8
    type: probe
    source: "/products, request_id konan-1794770668-20005"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001511s request_id=konan-1794770668-20005
  - id: E9
    type: metric
    source: "/metrics, request_id konan-1794770690-20031 (the last reading); the complete http_requests_total and http_exceptions_total series plus chaos and process gauges"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/metrics",status="200"} 2
      http_requests_total{method="GET",path="/orders",status="200"} 3
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_exceptions_total{type="ZeroDivisionError"} 1
      faultline_chaos_enabled 0
      process_uptime_seconds 119.88989075040445
      process_max_rss_bytes 46972928
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:24:06.405Z"
    quote: |-
      {"ts": "2026-11-15T19:24:06.405Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794770646-19969", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.851, "client": "127.0.0.1:55585"}
  - id: E11
    type: probe
    source: "/orders, request_id konan-1794770689-20022"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T19:22:55.375+00:00"},{"id":2,"product_id":2,"quantity":2,"total_price":46.0,"created_at":"2026-11-15T19:22:56.430+00:00"}]
      -- HTTP 200 in 0.001476s request_id=konan-1794770689-20022
gaps:
  - "No history before 2026-11-15T19:22:50.479Z: the log starts at the process start and has no backup files, so a crash before that start, or a restart loop with a period above 120 s, cannot be excluded from this surface. The launcher's start and exit history would settle it; it is outside the surface contract."
  - "The observation window is short: about 120 s of process life and 9 non-investigator requests in about 8 s. Slow memory growth or latency drift cannot be seen in it."
  - "Product 4 has price null in the catalog (E8). The read paths return 200 (E10). The order path is POST, outside the read-only surface, so the effect of a null price on an order was not checked; no order for product 4 exists (E11)."
  - "The 500 on /products/3 was produced once. Determinism rests on the stack trace (E6) and the stock value (E8), not on a repeat."
  - "lab/server.out (server stdout) is not in the surface list of docs/lab.md and was not read."
  - "The lab has no database, no third party and no load: the lenses for those classes do not exist and were not run."
usage:
  model: claude-fable-5-2
  tokens: 1228049
  wall_clock_seconds: 220
---

# Handover check of the shop service: no active incident, one latent defect

## Summary

**No active incident.** At the check, the service was up, every non-investigator request
succeeded (9 of 9, statuses 200 and 201, E2, E4, E5), the chaos switch was off and the
process showed one start and no uptime reset (E2, E3, E9). One **latent defect** rides
along: `GET /products/3` returns HTTP 500 with an unhandled `ZeroDivisionError`, because
`get_product` divides by `units_in_stock` and product 3 has stock 0 (E6, E7, E8). Only an
investigator probe triggered it; no user request for product 3 exists in the window. Any
user who opens product 3 gets a 500. Confidence in the verdict is high for the window
observed, and the window is short: about 120 s of process life.

## Complaint

```json
{
  "source": "human",
  "fingerprint": "human-1794770585",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports." },
  "startsAt": "2026-11-15T19:23:05Z"
}
```

Investigation start: 2026-11-15T19:23:17Z (trigger latency 12 s).

## Timeline

- 19:22:50.479Z: process start, `faultline 0.1.0 started` (E3). The only startup event.
- 19:22:51.202Z to 19:22:59.531Z: 9 non-investigator requests, all 200 or 201, two
  orders created (E4, E5, E11).
- 19:23:21Z to 19:23:22Z: baseline probes. Health ok, uptime 31 s, no non-2xx series, no
  exception series, chaos 0 (E1, E2).
- 19:24:06.405Z: investigator probe `GET /products/4` returns 200 (E10).
- 19:24:06.870Z: investigator probe `GET /products/3` raises `ZeroDivisionError` and
  returns 500 (E6, E7).
- 19:24:50Z (about): last metrics reading. One 500 and one exception, both from the
  investigator probe; uptime 119.9 s, peak memory unchanged (E9).

No configuration, deploy or chaos marker exists in the log.

## Investigation

- **Baseline.** `/health`, `/metrics` and the full log (18 lines at that time). Clean.
- **Triage.** Three lenses in parallel, each blind to the others: software-defect,
  infra-process, interfaces. The infra-process and interfaces lenses reported no
  anomaly. The software-defect lens probed the business surface and found the 500 on
  `/products/3`, and noted `price: null` on product 4.
- **Deep-dive.** None. The stack trace and the stock value made the evidence for H1
  deterministic and complete, so H1 went straight to the judge.
- **Judge.** H1 validated, H2 invalidated. The judge corrected one count (9
  non-investigator access lines, not 10) and named the open item for H2: the launcher's
  start and exit history.

## Hypotheses

### H1: unhandled ZeroDivisionError on a product with stock 0 (validated, latent)

The stack names `shop.py` line 64 in `get_product`, with `product["units_in_stock"]` as
the divisor (E6). Product 3 is the only product with stock 0 (E8), and the 500 on
`/products/3` carries the same request id (E7). The same route returns 200 for products
1, 2, 5 and 4 (E5, E10, E2). Before the probe there was no 500 and no exception series
(E2); after it there is exactly one of each (E9), and both carry a `konan-` request id.
The defect is real, and it is not an incident: no user traffic hit it in the window.

### H2: unstable process, crash or restart loop (invalidated)

The process was 31 s old at the first probe (E1, E3), which is what raised the question.
The predictions failed: one startup event (E3), uptime rose from 31.5 s to 119.9 s with
no reset (E2, E9), and every request around the start succeeded (E4, E5). A normal first
start gives the same 31 s. What happened before 19:22:50Z is out of reach (see Gaps).

## Safe next steps

- Read the launcher's start and exit history for this process, to confirm one start.
- Look at the next metrics readings for `http_requests_total{path="/products/{product_id}",status="500"}`
  above 1: a rise without a `konan-` request id in the log is user impact from H1.
- Read the log for the first order of product 4 and check its `total_price`.
- Repeat this check after a longer uptime, to see memory and latency over time.

## Gaps

- **No history before the start.** The log starts at 19:22:50Z and has no backup files.
  An earlier crash, or a slow restart loop, cannot be excluded from this surface.
- **Short window.** About 120 s and 9 user requests. Slow drift is invisible.
- **Null price on product 4.** Observed (E8), harmless on the read paths (E10). The
  order path is POST and outside the read-only surface, so the effect was not checked.
- **One reproduction.** The 500 was produced once; determinism rests on the code line in
  the stack and the stock value.
- **Server stdout not read.** `lab/server.out` is not in the surface list of the contract.
- **Classes without a lens.** Load, third party and data layer have no lens and no
  telemetry in this lab.
