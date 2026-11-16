---
konan_journal: 2
investigation:
  id: 2026-11-15-routine-handover-check
  trigger: "manual: the /konan adapter (human profile); complaint startsAt 2026-11-15T14:15:54Z, investigation start 2026-11-15T14:16:06Z, trigger latency 12 s; the complaint object is in the body"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-15T14:16:06Z
  concluded: 2026-11-15T14:22:09Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "An operational switch inside the target (chaos mode) was on from 14:15:18.288Z to 14:15:24.632Z and injected the 503 responses on three non-investigator requests; the switch is off now and injects no failure now."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E4, E5, E6, E7, E8, E9, E10, E11, E13, E14, E15, E16, E17, E18, E19]
    evidence_against: []
  - id: H2
    statement: "A defect in the target's own code produced the 503 responses on /products and /orders."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E6, E8, E10]
    evidence_against: [E5, E7, E9, E12, E13, E14, E33]
  - id: H3
    statement: "The process is unstable now (a crash, a restart loop, or a hang)."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E20]
    evidence_against: [E1, E3, E21, E22, E23, E24, E25]
  - id: H4
    statement: "GET /products/3 raises an unhandled ZeroDivisionError on every request while the product has units_in_stock 0, because the code divides by that value; only investigator probes triggered it in the visible window, and no non-investigator request failed with it (a latent defect, not the earlier noise and not an active incident)."
    incident_class: software-defect
    state: validated
    evidence_for: [E24, E26, E27, E28, E29, E30, E31, E32, E33, E34]
    evidence_against: []
  - id: H5
    statement: "An external dependency or a gateway tier produced the 503 responses."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E6, E8, E10]
    evidence_against: [E4, E5, E7, E9, E11]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 with an unhandled ZeroDivisionError (the product has units_in_stock 0 and the product page divides by it). Two of two investigator probes failed; no non-investigator request touched /products/3 in the visible window, so there is no observed user impact, but any user request for that page would fail."
    evidence: [E24, E26, E27, E28, E29, E30, E32, E33, E34]
evidence:
  - id: E1
    type: probe
    source: "/health, request konan-1794752167-1239 (2026-11-15T14:16:07.439Z)"
    quote: |-
      {"status":"ok","uptime_seconds":53.02526712464169}
      -- HTTP 200 in 0.001659s request_id=konan-1794752167-1239
  - id: E2
    type: metric
    source: "/metrics, request konan-1794752167-1245 (2026-11-15T14:16:07.960Z)"
    quote: "faultline_chaos_enabled 0"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:14.428Z (the only startup event in the file; no backup files exist)"
    quote: |-
      {"ts": "2026-11-15T14:15:14.428Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:18.288Z"
    quote: |-
      {"ts": "2026-11-15T14:15:18.288Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "f653e57c50c1", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:19.348Z"
    quote: |-
      {"ts": "2026-11-15T14:15:19.348Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "590b6d54c3f0", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:19.349Z"
    quote: |-
      {"ts": "2026-11-15T14:15:19.349Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "590b6d54c3f0", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.298, "client": "127.0.0.1:52863"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:22.519Z"
    quote: |-
      {"ts": "2026-11-15T14:15:22.519Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "523b815b9690", "event": "chaos_failure", "method": "POST", "path": "/orders"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:22.519Z"
    quote: |-
      {"ts": "2026-11-15T14:15:22.519Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "523b815b9690", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.293, "client": "127.0.0.1:52866"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:23.575Z"
    quote: |-
      {"ts": "2026-11-15T14:15:23.575Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "a3d66308284a", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:23.576Z"
    quote: |-
      {"ts": "2026-11-15T14:15:23.576Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "a3d66308284a", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.275, "client": "127.0.0.1:52867"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:24.632Z"
    quote: |-
      {"ts": "2026-11-15T14:15:24.632Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "d9b2a694d3d6", "event": "chaos_disabled"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:20.407Z (inside the chaos window)"
    quote: |-
      {"ts": "2026-11-15T14:15:20.407Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "9dbf30a9d5a4", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.849, "client": "127.0.0.1:52864"}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:44.692Z (after the chaos window)"
    quote: |-
      {"ts": "2026-11-15T14:15:44.692Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "c7f19f25894b", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.718, "client": "127.0.0.1:52869"}
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:15:46.795Z (after the chaos window)"
    quote: |-
      {"ts": "2026-11-15T14:15:46.795Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "1e6d34bdc404", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.335, "client": "127.0.0.1:52871"}
  - id: E15
    type: metric
    source: "/metrics, request konan-1794752167-1245 (2026-11-15T14:16:07.960Z)"
    quote: 'http_requests_total{method="GET",path="/products",status="503"} 2'
  - id: E16
    type: metric
    source: "/metrics, request konan-1794752167-1245 (2026-11-15T14:16:07.960Z)"
    quote: 'http_requests_total{method="POST",path="/orders",status="503"} 1'
  - id: E17
    type: metric
    source: "/metrics, request konan-1794752276-1394 (2026-11-15T14:17:56.459Z)"
    quote: 'http_requests_total{method="GET",path="/products",status="503"} 2'
  - id: E18
    type: metric
    source: "/metrics, request konan-1794752276-1394 (2026-11-15T14:17:56.459Z)"
    quote: 'http_requests_total{method="POST",path="/orders",status="503"} 1'
  - id: E19
    type: metric
    source: "/metrics, request konan-1794752276-1394 (2026-11-15T14:17:56.459Z)"
    quote: "faultline_chaos_enabled 0"
  - id: E20
    type: metric
    source: "/metrics, request konan-1794752167-1245 (2026-11-15T14:16:07.960Z)"
    quote: "process_uptime_seconds 53.5463539166376"
  - id: E21
    type: metric
    source: "/metrics, request konan-1794752276-1394 (2026-11-15T14:17:56.459Z)"
    quote: "process_uptime_seconds 162.048099541571"
  - id: E22
    type: metric
    source: "/metrics, request konan-1794752167-1245 (2026-11-15T14:16:07.960Z)"
    quote: "process_max_rss_bytes 47710208"
  - id: E23
    type: metric
    source: "/metrics, request konan-1794752276-1394 (2026-11-15T14:17:56.459Z)"
    quote: "process_max_rss_bytes 47710208"
  - id: E24
    type: probe
    source: "/products, request konan-1794752193-1263 (2026-11-15T14:16:33.410Z)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":120},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001940s request_id=konan-1794752193-1263
  - id: E25
    type: probe
    source: "/orders, request konan-1794752193-1268 (2026-11-15T14:16:33.883Z)"
    quote: |-
      [{"id":1,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T14:15:46.794+00:00"}]
      -- HTTP 200 in 0.001286s request_id=konan-1794752193-1268
  - id: E26
    type: probe
    source: "/products/3, request konan-1794752271-1378 (2026-11-15T14:17:51.632Z)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794752271-1378"}
      -- HTTP 500 in 0.008624s request_id=konan-1794752271-1378
  - id: E27
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:17:51.625Z (the logger field and all stack frames but the last are trimmed, marked by the three dots; the checkout prefix of the file path is redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T14:17:51.625Z", "level": "ERROR", "message": "unhandled exception: division by zero", "request_id": "konan-1794752271-1378", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "...  File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E28
    type: probe
    source: "/products/3, request konan-1794752276-1389 (2026-11-15T14:17:56.093Z, the repeat)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794752276-1389"}
      -- HTTP 500 in 0.003550s request_id=konan-1794752276-1389
  - id: E29
    type: metric
    source: "/metrics, request konan-1794752276-1394 (2026-11-15T14:17:56.459Z)"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 2'
  - id: E30
    type: metric
    source: "/metrics, request konan-1794752276-1394 (2026-11-15T14:17:56.459Z)"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2'
  - id: E31
    type: probe
    source: "/products/4, request konan-1794752272-1383 (2026-11-15T14:17:52.123Z)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001530s request_id=konan-1794752272-1383
  - id: E32
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:17:56.090Z (the second and last unhandled_exception line in the file up to 14:17:56.459Z; the logger and stack fields are trimmed)"
    quote: |-
      {"ts": "2026-11-15T14:17:56.090Z", "level": "ERROR", "message": "unhandled exception: division by zero", "request_id": "konan-1794752276-1389", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"}
  - id: E33
    type: metric
    source: "/metrics, request konan-1794752167-1245 (2026-11-15T14:16:07.960Z, before any probe of /products/3; the counter has no series between its TYPE line and the next HELP line)"
    quote: |-
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E34
    type: metric
    source: "/metrics, request konan-1794752167-1245 (2026-11-15T14:16:07.960Z; the only series of this path at that time)"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5'
gaps:
  - "Nothing before the process start at 2026-11-15T14:15:14.428Z is visible: one log file, no backups, and the counters start at the process start. Noise before that time is out of reach."
  - "The reason for the process start at 14:15:14.428Z is unknown: the log holds no crash or exit event before it, and the launcher record is not on the surface."
  - "The actor behind the two chaos toggle requests is unknown: both carry an unstamped request id and a loopback client address; the operator surface is out of bounds."
  - "The log does not show whether the POST /orders -> 201 at 14:15:46.795Z was a retry of the POST /orders that failed at 14:15:22.519Z."
  - "The /products/3 failure rests on two of two probes plus the quoted division; it holds only while units_in_stock is 0."
  - "Only three lenses exist (infra-process, software-defect, interfaces) and all three ran; load-saturation, third-party and data-db had no lens. Latency was checked from the duration sums and the access lines only."
  - "Token totals were not captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1488649
  wall_clock_seconds: 363
---

# Routine handover check: no active incident; a closed chaos window explains the earlier noise

## Summary

**No active incident.** The shop service is healthy now: `/health`, `/products` and
`/orders` answer 200 (E1, E24, E25), the chaos gauge reads 0 (E2, E19), and the 503
counters did not move between the two metric reads (E15 to E18).

The earlier noise was one short window of injected errors. Chaos mode, an operational
switch inside the service, was on from 14:15:18.288Z to 14:15:24.632Z with a failure
rate of 0.6 and status 503 (E4, E11). It failed three of the five shop requests in that
window: two `GET /products` and one `POST /orders` (E5 to E10). Each 503 carries a
`chaos_failure` line with the same request id. The same routes succeeded after the
window (E13, E14). Confidence is high for the visible window.

One latent finding rides along: `GET /products/3` returns 500 with a
`ZeroDivisionError` (E26 to E28). Only the investigator's two probes triggered it; no
user request touched that page in the visible window (E33, E34). It is not the earlier
noise and not an active incident, but any user who opens that page gets an error.

The visible window starts at the process start, 14:15:14.428Z (E3). Noise before that
time cannot be checked on this surface.

## Timeline

All times UTC, 2026-11-15.

- 14:15:14.428 — process start, the only startup marker (E3).
- 14:15:18.288 — **configuration marker:** chaos mode enabled, failure rate 0.6, status 503 (E4).
- 14:15:19.349 — `GET /products` -> 503, injected (E5, E6).
- 14:15:20.407 — `GET /products/2` -> 200 inside the window (E12).
- 14:15:22.519 — `POST /orders` -> 503, injected (E7, E8).
- 14:15:23.576 — `GET /products` -> 503, injected (E9, E10).
- 14:15:24.632 — **configuration marker:** chaos mode disabled (E11).
- 14:15:44.692 — `GET /products` -> 200 (E13).
- 14:15:46.795 — `POST /orders` -> 201 (E14).
- 14:15:54 — complaint raised.
- 14:16:06 — investigation start.
- 14:16:07 — baseline: health 200, chaos gauge 0, no exception series (E1, E2, E33).
- 14:17:51 and 14:17:56 — investigator probes of `/products/3` -> 500, `ZeroDivisionError` (E26, E27, E28, E32).
- 14:17:56.459 — final metrics: chaos gauge 0, 503 counters unchanged, uptime 162 s (E17, E18, E19, E21).

## Investigation

The complaint object, as the `/konan` adapter built it (the reporter stated no
severity). Investigation start: 2026-11-15T14:16:06Z, trigger latency 12 s.

```json
{
  "source": "human",
  "fingerprint": "human-1794752154",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report." },
  "startsAt": "2026-11-15T14:15:54Z"
}
```

- **Baseline.** `/health` 200 (E1); `/metrics` with chaos gauge 0, three historical 503s,
  no exception series (E2, E15, E16, E33); the full log (one file, no backups);
  `/products` and `/orders` 200 (E24, E25).
- **Triage.** The complaint is vague, so all three lenses ran in parallel:
  infra-process, software-defect, interfaces. All three reported the same closed chaos
  window and no ongoing anomaly. The software-defect lens named `/products/3`,
  `/products/4` as pages with no request in the log.
- **Business surface, completed by the orchestrator.** The product list shows product 3
  with `units_in_stock` 0 and product 4 with a null price (E24). One probe each:
  `/products/4` -> 200 (E31), `/products/3` -> 500 (E26). One repeat of `/products/3`
  confirmed it (E28). No deep-dive agent ran: the triage evidence for the chaos window
  was deterministic and complete, and the product-3 test was two probes.
- **Judge.** One fresh judge saw the five hypotheses and the quoted evidence only.
  Verdicts: H1 validated, H2 invalidated, H3 invalidated, H4 validated with scope
  limits, H5 invalidated. For H4 the judge asked for the full list of
  `unhandled_exception` lines; the log holds two, both with investigator ids (E27, E32).
- **Budget.** One triage round, zero deep-dive agents, one judge round.

## Hypotheses

### H1 — a closed chaos window injected the 503s (validated)

The switch went on at 14:15:18.288Z (E4) and off at 14:15:24.632Z (E11). Each of the
three 503 access lines (E6, E8, E10) pairs with a `chaos_failure` line with the same
request id (E5, E7, E9). The counters total three (E15, E16) and did not move by
14:17:56Z (E17, E18). The gauge reads 0 at both reads (E2, E19) and the routes succeed
after the window (E13, E14). The mechanism is a degradation switch in the class
infra-process; it has ended, so the verdict names no root cause of an active incident.

### H2 — a code defect produced the 503s (invalidated)

The 503s exist (E6, E8, E10), but all three are attributed to injection (E5, E7, E9).
A request inside the window succeeded on a product page (E12), the routes recovered
without a restart (E13, E14), and no exception was counted at baseline (E33).

### H3 — the process is unstable now (invalidated)

The process was young at baseline (E20), but there is one startup marker (E3), and the
two uptime reads give the same start time (E20, E21). Health and the business routes
answer in about 2 ms (E1, E24, E25). Peak memory is flat (E22, E23).

### H4 — `/products/3` raises a ZeroDivisionError; latent (validated)

Product 3 has `units_in_stock` 0 (E24). The product page divides by that value
(E27). Two of two probes returned 500 (E26, E28); product 4, with stock 75, returned
200 (E31). The exception counter and the 500 counter both read 2 (E29, E30), equal to
the two investigator probes, and both `unhandled_exception` lines carry investigator
ids (E27, E32). Before the probes the exception counter had no series and the product
route had only 200s (E33, E34). This is a latent finding, not the incident.

### H5 — an external dependency or gateway produced the 503s (invalidated)

The status is gateway-shaped (E6, E8, E10), but the service's own chaos logger set the
status (E4) and logged each injection (E5, E7, E9), and the window closed with the
switch (E11). No evidence shows a dependency or a gateway.

## Safe next steps

Read-only suggestions only.

- Ask the operator who enabled chaos mode at 14:15:18Z and whether it was planned.
- Tell the next on-call person that `/products/3` returns 500 while its stock is 0, and
  pass the quoted stack frame (E27) to the service owner.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the `status="500"` series
  of `/products/{product_id}`: growth from requests without the investigator id prefix
  means user impact.
- Watch `faultline_chaos_enabled`: a value of 1 means the switch is on again.
- If the reported noise was before 14:15:14Z, look for an earlier log or the launcher
  record; this surface does not hold them.

## Gaps

- **Before the process start.** The log and the counters start at 14:15:14.428Z. There
  are no backup files. Noise before that time is out of reach.
- **Why the process started.** No crash or exit event precedes the startup marker, and
  the launcher record is not on the surface.
- **Who set the switch.** The two toggle requests carry unstamped ids and a loopback
  client address. The operator surface is out of bounds for the investigator.
- **The failed order.** The log does not show whether the later successful order was a
  retry of the order that failed at 14:15:22.519Z.
- **Determinism of the product-3 failure.** Two of two probes plus the quoted division.
  It holds only while the stock is 0.
- **Lens coverage.** Three lenses exist and all three ran. Load-saturation, third-party
  and data-db have no lens. Latency was checked from duration sums and access lines.
- **Tokens.** The session could not capture token totals.
