---
konan_journal: 2
investigation:
  id: 2026-11-24-product-page-errors-alert
  trigger: alert-inbox (receiver profile, alerts/inbox.jsonl via scripts/receive.py, fingerprint b96506e6a5a56f8a)
  complaint: |-
    {"source": "alert", "fingerprint": "b96506e6a5a56f8a", "labels": {"alertname": "KonanReceiverCheck", "severity": "page"}, "annotations": {"summary": "users report errors when they open a product page"}, "startsAt": "2026-11-24T15:45:21.719931292Z", "generatorURL": ""}
  started: "2026-11-24T15:45:26Z"
  concluded: "2026-11-24T15:48:35Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "Users hit the per-input ZeroDivisionError on GET /products/{id} (product 3, units_in_stock 0) at or before the alert time 2026-11-24T15:45:21Z, and that is what the alert reports."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E6, E7, E8, E9]
    evidence_against: [E2, E13]
  - id: H2
    statement: "An internal degradation switch (chaos) injects errors on product pages."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E12, E8]
  - id: H3
    statement: "A process crash or restart caused user errors around the alert time."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E10, E12]
  - id: H4
    statement: "A contract mismatch: product 4's \"price\": null breaks clients that open its product page."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E7]
    evidence_against: [E11]
  - id: H5
    statement: "The ZeroDivisionError defect is live now and fails deterministically for product 3 only, but in the current process (started 15:37:35Z) every trigger is an investigator probe; no user request has reached any product path."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E4, E5, E6, E7, E8, E11, E13, E14]
    evidence_against: []
latent_findings:
  - statement: "Deterministic per-input defect, still live: GET /products/3 raises ZeroDivisionError at the turnover_score computation in get_product (shop.py line 64, division by units_in_stock, which is 0 for product 3) and returns HTTP 500. Users hit it on 2026-11-08 in the previous process; in the current process only investigator probes have triggered it. Earlier journals record the same defect (journals/2026-08-06-products-3-user-500s.md)."
    evidence: [E6, E7, E8, E9, E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-24T15:37:35.906Z"
    quote: '{"ts": "2026-11-24T15:37:35.906Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-24T15:37:36.420Z (the only non-investigator request line logged on 2026-11-24; the other non-investigator lines that day are the startup lines)"
    quote: '{"ts": "2026-11-24T15:37:36.420Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "18296b74fe2f", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 9.454, "client": "127.0.0.1:56800"}'
  - id: E3
    type: metric
    source: "/metrics @ request_id konan-1795535255-20265"
    quote: "faultline_chaos_enabled 0"
  - id: E4
    type: metric
    source: "/metrics @ request_id konan-1795535255-20265"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 5'
  - id: E5
    type: metric
    source: "/metrics @ request_id konan-1795535255-20265"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 5'
  - id: E6
    type: probe
    source: "/products/3 @ request_id konan-1795535256-20277"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1795535256-20277"}
      -- HTTP 500 in 0.003756s request_id=konan-1795535256-20277
  - id: E7
    type: probe
    source: "/products @ request_id konan-1795535256-20282"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":120},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-08T14:05:23.778Z (event unhandled_exception, request_id 10c3bf72f201; stack fragments)"
    quote: |-
      "exception_type": "ZeroDivisionError"
      shop.py\", line 64, in get_product
      \"turnover_score
      ZeroDivisionError: division by zero
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-08T14:05:24.846Z"
    quote: '{"ts": "2026-11-08T14:05:24.846Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "3848d702f204", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 6.404, "client": "127.0.0.1:63807"}'
  - id: E10
    type: metric
    source: "/metrics @ request_id konan-1795535255-20265"
    quote: "process_uptime_seconds 599.4321556659415"
  - id: E11
    type: probe
    source: "/products/1, /products/2, /products/4, /products/5 and /openapi.json — investigator probes reported by the triage lenses (2026-11-24T15:45:56Z–15:47:11Z)"
    quote: '/products/{1,2,4,5} -> HTTP 200; /products/4 body carries "price":null; /openapi.json response schema for these routes: additionalProperties: true'
  - id: E12
    type: log
    source: "lab/logs/app.log, whole file (search for chaos events and lifecycle markers)"
    quote: |-
      no chaos_enabled / chaos_disabled / chaos_failure events
      {"ts": "2026-11-08T19:20:05.199Z", "level": "INFO", "logger": "uvicorn.error", "message": "Shutting down"}
      {"ts": "2026-11-08T19:20:05.301Z", "level": "INFO", "logger": "uvicorn.error", "message": "Application shutdown complete."}
  - id: E13
    type: metric
    source: "/metrics @ request_id konan-1795535134-18682 (baseline scrape, log ts 2026-11-24T15:45:34.966Z — the first investigator request, 13 s after the alert's startsAt)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 2
      faultline_chaos_enabled 0
      process_uptime_seconds 479.0436322498135
  - id: E14
    type: log
    source: "lab/logs/app.log, every 2026-11-24 line with path /products/3 (fields trimmed: ts, request_id, status)"
    quote: |-
      "ts": "2026-11-24T15:45:56.600Z" "request_id": "konan-1795535156-18933" "status": 500
      "ts": "2026-11-24T15:45:58.734Z" "request_id": "konan-1795535158-18972" "status": 500
      "ts": "2026-11-24T15:47:08.584Z" "request_id": "konan-1795535228-19809" "status": 500
      "ts": "2026-11-24T15:47:10.997Z" "request_id": "konan-1795535230-19850" "status": 500
      "ts": "2026-11-24T15:47:11.014Z" "request_id": "konan-1795535231-19853" "status": 500
      "ts": "2026-11-24T15:47:36.121Z" "request_id": "konan-1795535256-20277" "status": 500
gaps:
  - "The source of the alert is outside the lab surface: generatorURL is empty and the lab has no Prometheus history, so the investigation cannot see what rule or which sender fired the alert at 15:45:21Z. The telemetry shows no event that could make it fire."
  - "Client-side behaviour is not observable: whether a client breaks on product 4's \"price\": null is untested (H4 rests on server-side evidence only)."
  - "Probe evidence for products 1, 2, 4, 5 and /openapi.json (E11) comes from the triage lenses' reports, not from a probe the orchestrator re-ran."
usage:
  model: claude-opus-5-5
  tokens: null
  wall_clock_seconds: 189
---

# Product page errors alert (KonanReceiverCheck): no active incident

## Summary

**Verdict: no active incident.** The alert says that users get errors on a product page. The telemetry shows no user request to any product page in the current process. The process started at 15:37:35Z (E1). Up to the first investigator request at 15:45:34Z, 13 seconds after the alert's `startsAt`, the service handled 2 health requests and nothing else (E2, E13). The chaos switch is off (E3, E13) and the process did not restart (E10). One real defect rides along as a latent finding: `GET /products/3` raises `ZeroDivisionError` every time, because product 3 has zero stock (E6, E7, E8). Users hit it on 2026-11-08 in the previous process (E9). Today only the investigator's probes hit it (E14). Confidence is high for "no user impact in the current process". What fired the alert is outside the lab surface (Gaps).

## Timeline

- 2026-11-08T14:05:23Z – 14:05:30Z — users get HTTP 500 on `/products/3`; ZeroDivisionError in `get_product` (E8, E9).
- 2026-11-08T19:20:05Z — clean shutdown (E12).
- 2026-11-24T15:37:35.906Z — process starts, faultline 0.1.0 (E1).
- 2026-11-24T15:37:36.420Z — one health check, 200; the only non-investigator request today (E2).
- 2026-11-24T15:45:21.7Z — the alert's `startsAt` (complaint).
- 2026-11-24T15:45:26Z — investigation starts (latency 5 s).
- 2026-11-24T15:45:34Z — baseline scrape: only `/health` requests counted, chaos 0 (E13).
- 2026-11-24T15:45:56Z onward — investigator probes trigger the product 3 defect six times (E14, E4, E5).

No configuration, deploy or flag-change marker appears in the log (E12).

## Investigation

- **Baseline:** `/health` 200, `/metrics` with only health counters, log tail since startup (E1, E2, E13).
- **Triage:** three lenses in parallel — software-defect, infra-process, interfaces. The software-defect lens found the per-input ZeroDivisionError on product 3. The infra-process lens found no restart, flat memory, chaos off. The interfaces lens found no gateway statuses and flagged product 4's null price as a possible client-side contract problem.
- **Deep-dive:** skipped; the defect evidence from triage was deterministic and complete.
- **Judge:** H1 invalidated as stated (no user impact), H2, H3 and H4 invalidated; H5 partly validated, with one item open: whether the 5 counted errors were all investigator probes. The judge's settling evidence was gathered: the log holds exactly 5 investigator requests to `/products/3` before scrape konan-1795535255-20265, and no other (E14, E5). The judge also asked for the 500 counter before 15:45:21Z; the baseline scrape (E13) shows no product request at all up to 15:45:34Z, which settles H1.

## Hypotheses

### H1 — users hit the product 3 defect at the alert time (invalidated)

The defect is real (E6, E7, E8) and users hit it before (E9). But the current process served no user product request before the alert: the only non-investigator request is a health check (E2), and the baseline counters hold only health requests (E13).

### H2 — chaos switch injects errors (invalidated)

`faultline_chaos_enabled 0` (E3, E13), no chaos events anywhere in the log (E12), and the failure is a genuine Python exception in application code (E8).

### H3 — crash or restart (invalidated)

The process started almost 8 minutes before the alert (E1), uptime grew without reset (E10), and the previous stop was a clean shutdown (E12).

### H4 — null price breaks clients (invalidated as the alert's cause)

`/products/4` returns 200 and the schema allows any price value (E11). Client-side breakage is untested (Gaps).

### H5 — defect live, investigator-only in the current process (validated)

Product 3 is the only product with zero stock (E7) and the only failing input (E11). All six 500s today carry investigator request ids (E14), matching the counters (E4, E5).

## Safe next steps

- Read the Alertmanager rule and sender behind `KonanReceiverCheck` to learn why it fired with no matching telemetry; its name suggests a check of the receiver path.
- Read the code path of `get_product` in shop.py around line 64 to confirm the handling of zero stock; earlier journals already record this defect.
- Watch `http_requests_total{path="/products/{product_id}",status="500"}` for non-investigator requests.

## Gaps

- The alert's source is outside the lab surface: `generatorURL` is empty and the lab keeps no Prometheus history, so the rule that fired cannot be seen.
- Client behaviour on product 4's null price is not observable from the server.
- E11 rests on the triage lenses' probes, not on a probe the orchestrator re-ran.
