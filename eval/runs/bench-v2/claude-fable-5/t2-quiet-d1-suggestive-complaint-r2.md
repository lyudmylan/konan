---
konan_journal: 2
investigation:
  id: 2026-11-03-products-3-500s
  trigger: "manual (/konan, alertname human-report, fingerprint human-1793703690; startsAt 2026-11-03T11:01:30Z, loop entered 11:01:43Z, trigger latency 13s)"
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-03T11:01:43Z
  concluded: 2026-11-03T11:08:30Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "faultline's get_product handler divides units_ordered by product[\"units_in_stock\"]; product 3 is the only product with units_in_stock 0, so every request to its product page raises an unhandled ZeroDivisionError and returns HTTP 500 (\"internal server error\")."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The product-detail handler get_product computes units_ordered / product[\"units_in_stock\"]; product 3 is the only product with units_in_stock 0, so every GET /products/3 raises ZeroDivisionError and returns HTTP 500 with body \"internal server error\", while all other product pages return 200."
    incident_class: software-defect
    state: validated
    evidence_for: [E3, E4, E6, E7, E8, E9, E10, E11, E13, E15]
    evidence_against: []
  - id: H2
    statement: "An internal chaos/degradation switch injects the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E7, E8, E10, E11]
  - id: H3
    statement: "A gateway or proxy tier fails on its own and produces the error pages."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E6]
  - id: H4
    statement: "The process crashes or restarts in a loop, and customers hit errors during restarts."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E2]
    evidence_against: [E1, E12, E14]
evidence:
  - id: E1
    type: probe
    source: "/health @ request_id konan-1793703711-30163 (2026-11-03T11:01:51Z)"
    quote: |-
      {"status":"ok","uptime_seconds":36.841181749943644}
      -- HTTP 200 in 0.001567s request_id=konan-1793703711-30163
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:01:14.515Z"
    quote: |-
      {"ts": "2026-11-03T11:01:14.515Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [30070]"}
  - id: E3
    type: metric
    source: "/metrics @ request_id konan-1793703909-30344 (2026-11-03T11:05:09Z)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
  - id: E4
    type: metric
    source: "/metrics @ request_id konan-1793703909-30344 (2026-11-03T11:05:09Z)"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E5
    type: metric
    source: "/metrics @ request_id konan-1793703909-30344 (2026-11-03T11:05:09Z)"
    quote: |-
      faultline_chaos_enabled 0
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:03:34.651Z (stack trimmed to the throwing frame)"
    quote: |-
      {"ts": "2026-11-03T11:03:34.651Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793703814-30262", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last): … File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:03:34.659Z"
    quote: |-
      {"ts": "2026-11-03T11:03:34.659Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793703814-30262", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 7.751, "client": "127.0.0.1:50054"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:03:41.483Z"
    quote: |-
      {"ts": "2026-11-03T11:03:41.483Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793703821-30267", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.509, "client": "127.0.0.1:50055"}
  - id: E9
    type: probe
    source: "/products @ request_id konan-1793703908-30339 (2026-11-03T11:05:08Z; array trimmed to one element)"
    quote: |-
      {"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}
      -- HTTP 200 in 0.002264s request_id=konan-1793703908-30339
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:03:49.091Z"
    quote: |-
      {"ts": "2026-11-03T11:03:49.091Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1793703829-30289", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.45, "client": "127.0.0.1:50058"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:03:32.064Z"
    quote: |-
      {"ts": "2026-11-03T11:03:32.064Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1793703812-30257", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.449, "client": "127.0.0.1:50053"}
  - id: E12
    type: metric
    source: "/metrics @ request_id konan-1793703909-30344 (2026-11-03T11:05:09Z)"
    quote: |-
      process_uptime_seconds 235.02982037491165
  - id: E13
    type: metric
    source: "/metrics @ request_id konan-1793703909-30344 (2026-11-03T11:05:09Z)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:01:20.571Z"
    quote: |-
      {"ts": "2026-11-03T11:01:20.571Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "c7ef6544fd7c", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.833, "client": "127.0.0.1:50027"}
  - id: E15
    type: probe
    source: "/products/3 @ request_id konan-1793704102-30439 (2026-11-03T11:08:22Z)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793704102-30439"}
      -- HTTP 500 in 0.007402s request_id=konan-1793704102-30439
gaps:
  - "Telemetry before 2026-11-03T11:01:14.515Z does not exist on the surface: lab/logs/ holds only app.log (no rotated backups), and the log begins at process start. The customers' own morning 500s predate it and cannot be quoted; all four 500s counted in E3 came from konan-* investigator probes."
  - "The chaos switch state before 11:01:14Z is unobservable; the gauge and the log cover only the running process. The judge's settling item (a chaos-state audit record for the earlier morning) is not on the surface."
  - "Process start history before 11:01:14Z is unobservable: no supervisor record is on the surface, so first-start cannot be distinguished from restart, and H4 stays inconclusive for the pre-log window."
  - "No gateway or proxy log is on the surface; docs/lab.md documents a single-service topology, so H3's residual pre-log window could not be checked against a proxy log."
usage:
  model: claude-fable-5
  tokens: 2120531
  wall_clock_seconds: 407
---

# Product page 500s: division by zero on the zero-stock product

## Summary

Root cause identified. The product-detail handler `get_product` divides `units_ordered` by `product["units_in_stock"]` (E6). Product 3 ("Unobtainium Ingot") is the only product with `units_in_stock: 0` (E9). Every GET /products/3 raises an unhandled `ZeroDivisionError` and returns HTTP 500 with the body `"internal server error"` (E6, E7, E8, E15) — the exact words the customers report. All other product pages return 200 (E10, E11, E13). The failure is deterministic per input: four requests to /products/3, four 500s, zero successes (E3, E4). Confidence in the mechanism is high. One caveat holds: the process restarted at 11:01:14Z (E2) and the log before that point is gone, so the customers' own morning errors cannot be quoted — the deterministic reproduction is the bridge from the complaint to the defect.

## Timeline

- 2026-11-03T11:01:14.515Z — process 30070 starts; the only startup marker in the log, and the only change marker in the window (E2). All telemetry before this point is unavailable.
- 11:01:15–11:01:20Z — unstamped (non-investigator) traffic: /products/1, /products/2, /products/5 and orders, all 200/201 (E14). None of it touches /products/3.
- 11:01:30Z — complaint stamped (`startsAt`); support reports customer 500s on a product page "this morning".
- 11:01:43Z — investigation starts. Baseline: health 200, uptime 36.8s, no error series, chaos gauge 0 (E1).
- 11:03:32–11:03:49Z — triage probes: /products/4 → 200 (E11); /products/3 → 500 four times with `ZeroDivisionError` stacks (E6, E7, E8); /products/1 → 200 (E10).
- 11:05:08–11:05:09Z — product list shows product 3 is the only zero-stock product (E9); metrics confirm 4×500 and 4×ZeroDivisionError on the product-detail route, chaos gauge 0, uptime monotonic at 235s (E3, E4, E5, E12, E13).
- 11:08:22Z — confirmation probe captures the 500 body verbatim: `"internal server error"` (E15).
- 11:08:30Z — investigation concluded.

## Investigation

Baseline (orchestrator): health, metrics, log tail — service healthy, but the process was 37 seconds old and the log held no history from the complaint window. Triage: three lenses in parallel (infra-process, software-defect, interfaces), each with the lens file, the surface contract, the complaint verbatim, and the baseline summary. The software-defect lens reproduced the 500 deterministically on /products/3 and pulled the stack trace; the interfaces lens excluded chaos, gateway shapes, and dependencies; the infra-process lens excluded lifecycle and resource anomalies in the observable window and corrected the baseline (no rotated log backups exist). Triage evidence was deterministic and complete, so no deep-dive round ran — the four hypotheses went straight to the judge with the verbatim evidence ledger. The judge validated H1's mechanism, invalidated H2 and H3 for the logged window, held H4 inconclusive for the pre-log window, and named one fillable gap: no 500 response body was cited. One confirmation probe filled it (E15). The remaining settling items (pre-restart logs, chaos audit history, supervisor start history, proxy logs) are outside the surface contract and are recorded as gaps.

## Hypotheses

### H1 — division by zero in get_product (validated)

Every request to /products/3 fails with HTTP 500 and `ZeroDivisionError`; the stack trace names the throwing line — `"turnover_score": units_ordered / product["units_in_stock"]` at `shop.py` line 64 (E6, E7, E8). Product 3 is the only product with `units_in_stock: 0` (E9), and the only product page that fails: /products/1 and /products/4 return 200 (E10, E11), and the counters agree exactly — four 500s (E3), four ZeroDivisionError exceptions (E4), five 200s on the same route (E13). The response body is the complained symptom verbatim: `"internal server error"` (E15). The judge validated the mechanism. The link to the morning customer reports is inference from determinism, not observation — see Gaps.

### H2 — chaos switch (invalidated)

The gauge reads 0 (E5), the log holds no chaos events across its whole span, and the failure is deterministic on one input rather than probabilistic across routes (E7, E8 vs E10, E11). The stack trace places the exception inside real handler code, not an injector (E6).

### H3 — gateway failure (invalidated)

The 500s carry an application stack trace (E6) and are counted by the application's own metrics (E3); no 502/503/504 series exists. The error is born inside the target.

### H4 — crash/restart loop (inconclusive)

A restart did happen 16 seconds before the complaint was stamped (E2), and nothing on the surface explains why. Inside the observed window the loop shape is refuted: uptime rises monotonically from 36.8s to 235.0s (E1, E12) and non-investigator traffic right after start succeeded (E14). A pre-log crash cycle is neither shown nor excluded; the supervisor's start history would settle it and is not on the surface.

## Safe next steps

- Read-only: re-probe GET /products/3 after any fix lands; a 200 with a well-formed body confirms the repair.
- Read-only: watch `http_exceptions_total{type="ZeroDivisionError"}` and the 500 series on `/products/{product_id}` for growth from non-`konan-*` traffic — that would confirm live customer impact directly.
- Read-only: list zero-stock products via GET /products to know the blast radius; today it is product 3 only, but any product whose stock drops to 0 will start failing the same way.
- If any telemetry exists outside this surface (host syslog, supervisor history, gateway or CDN logs), pull the window before 11:01:14Z to time the onset of the customer-reported errors and settle H4.

## Gaps

The four frontmatter gaps share one root: the process restart at 11:01:14.515Z truncated the evidence window, and the surface contract offers nothing older. Concretely: (1) the customers' own 500s cannot be quoted — every observed 500 is an investigator probe; (2) the chaos state before the restart is unknowable from the gauge and log alone; (3) first-start versus restart cannot be distinguished without supervisor history, leaving H4 inconclusive; (4) no proxy tier log exists to double-check the pre-log window, though the documented topology has no proxy tier at all.
