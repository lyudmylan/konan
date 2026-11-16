---
konan_journal: 2
investigation:
  id: 2026-11-15-product-page-500
  trigger: 'manual — /konan (human profile). Complaint object: {"source": "human", "fingerprint": "human-1794767997", "labels": {"alertname": "human-report"}, "annotations": {"summary": "<the complaint field below, verbatim>"}, "startsAt": "2026-11-15T18:39:57Z"}. Investigation start 2026-11-15T18:40:15Z; trigger latency 18 s. No severity stated by the reporter.'
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-15T18:40:15Z
  concluded: 2026-11-15T18:44:23Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product detail handler divides units_ordered by units_in_stock without a guard; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The product detail handler divides units_ordered by units_in_stock without a guard; product 3 has units_in_stock 0, so every request for /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500, while products with non-zero stock return 200."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E13]
    evidence_against: []
  - id: H2
    statement: "The process start at 18:39:38Z (a restart or a rollout) put a wrong build or a changed configuration in place, and that change is the cause of the failures on the product page."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E10, E2]
    evidence_against: [E1, E4, E6, E7, E13, E11]
  - id: H3
    statement: "An operational error-injection switch inside the target is on and injects the HTTP 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E8]
    evidence_against: [E9, E1, E4, E5, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:39:45.405Z (stack trimmed to its last frame; the local path prefix of the target checkout is redacted as <checkout>)"
    quote: '{"ts": "2026-11-15T18:39:45.405Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "9fe7c42fa030", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:39:45.417Z"
    quote: '{"ts": "2026-11-15T18:39:45.417Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "9fe7c42fa030", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 12.604, "client": "127.0.0.1:55020"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:39:51.715Z"
    quote: '{"ts": "2026-11-15T18:39:51.715Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "1710c71bd7e8", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.697, "client": "127.0.0.1:55025"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:39:48.537Z"
    quote: '{"ts": "2026-11-15T18:39:48.537Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "77af988511fe", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.752, "client": "127.0.0.1:55022"}'
  - id: E5
    type: probe
    source: "/products/3, request id konan-1794768111-17331"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794768111-17331"}
      -- HTTP 500 in 0.003821s request_id=konan-1794768111-17331
  - id: E6
    type: probe
    source: "/products, request id konan-1794768111-17326"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.008940s request_id=konan-1794768111-17326
  - id: E7
    type: probe
    source: "/products/1, request id konan-1794768112-17336"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":118,"units_ordered":2,"turnover_score":0.01694915254237288}
      -- HTTP 200 in 0.001564s request_id=konan-1794768112-17336
  - id: E8
    type: metric
    source: "/metrics, request id konan-1794768113-17341 (2026-11-15T18:41:53Z); all http_requests_total and http_exceptions_total series of the scrape"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/products",status="200"} 4
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 7
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_exceptions_total{type="ZeroDivisionError"} 7
  - id: E9
    type: metric
    source: "/metrics, request ids konan-1794768016-17195 (18:40:16Z) and konan-1794768113-17341 (18:41:53Z); the same value in both scrapes"
    quote: "faultline_chaos_enabled 0"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:39:38.429Z (the only startup event in the log; no line is earlier than 18:39:38.428Z and no rotated backup exists)"
    quote: '{"ts": "2026-11-15T18:39:38.429Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E11
    type: metric
    source: "/metrics, request id konan-1794768016-17195 (18:40:16Z), then request id konan-1794768113-17341 (18:41:53Z)"
    quote: |-
      process_uptime_seconds 38.25919033307582
      process_max_rss_bytes 47742976
      process_uptime_seconds 134.61568333301693
      process_max_rss_bytes 47742976
  - id: E12
    type: probe
    source: "/health, request id konan-1794768016-17190"
    quote: |-
      {"status":"ok","uptime_seconds":37.67222991678864}
      -- HTTP 200 in 0.002399s request_id=konan-1794768016-17190
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:41:00.580Z and 2026-11-15T18:41:00.594Z (triage probes of the other product ids)"
    quote: |-
      {"ts": "2026-11-15T18:41:00.580Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794768060-17257", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.477, "client": "127.0.0.1:55051"}
      {"ts": "2026-11-15T18:41:00.594Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "konan-1794768060-17260", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.415, "client": "127.0.0.1:55052"}
gaps:
  - "No telemetry exists before 2026-11-15T18:39:38.428Z: the log starts at the process start and has no rotated backup. The onset ('within the last hour') and the statement 'no deploys' cannot be checked, and H2 stays inconclusive."
  - "The reason for the process start at 18:39:38Z (first start, restart, or rollout) is not visible: the surface has no deploy record and no exit event."
  - "The stock history of product 3 is not visible: the surface shows units_in_stock 0 now, not when or how it became 0. The log has no order for product 3."
  - "The log has no non-investigator request after 18:39:51Z. 'Still happening' rests on three investigator probes of /products/3 (18:41:00Z, 18:41:15Z, 18:41:51Z)."
  - "The source code is outside the surface. The mechanism is read from the stack trace (E1) and the response shapes (E6, E7), not from the code."
  - "Product 4 has price null in the product list (E6). Its page returns 200 (E13). The order path is a POST, outside the read-only surface, so its behaviour with a null price was not tested."
  - "The token total of this run was not captured (usage.tokens is null)."
usage:
  model: claude-fable-5-2
  tokens: 1697395
  wall_clock_seconds: 248
---

# Product 3 page returns HTTP 500: division by zero stock

## Summary

**Verdict: root cause identified (software defect, unhandled exception).** The page of
product 3 fails on every request. The product detail handler computes
`turnover_score` as `units_ordered / units_in_stock` (E1). Product 3 has
`units_in_stock` 0 (E6), so the division raises `ZeroDivisionError` and the request
returns HTTP 500 (E2, E5). Products 1, 2, 4 and 5 have stock above zero and return 200
(E4, E7, E13). The health endpoint stays green during the failures (E12).

Impact: 4 of 4 customer requests for `/products/3` failed between 18:39:45Z and
18:39:51Z (E2, E3). The metrics show 7 failures (E8); 3 of them are investigator
probes. No other route and no other exception type fails (E8).

Confidence: high for the mechanism. The failure is deterministic for one input, the
stack names the division, and the data value explains it. The onset time is not
established: the telemetry starts at a process start at 18:39:38Z (E10), 19 seconds
before the complaint. What ran before that start is out of reach (see Gaps).

## Timeline

- 18:39:38.429Z — the process starts, version 0.1.0 (E10). The only start in the log.
- 18:39:45.405Z — first unhandled `ZeroDivisionError` in `get_product` (E1).
- 18:39:45.417Z — first `GET /products/3 -> 500`, the first request for product 3 in
  the log (E2).
- 18:39:48.537Z — `GET /products/2 -> 200` between two failures (E4).
- 18:39:51.715Z — fourth and last customer failure on `/products/3` in the log (E3).
- 18:39:57Z — the complaint arrives (`startsAt`).
- 18:40:15Z — the investigation starts. Trigger latency: 18 s.
- 18:40:16Z — baseline: health 200 (E12), error-injection gauge 0 (E9), uptime 38 s (E11).
- 18:41:51Z — reproduction: `/products/3` returns 500 with `ZeroDivisionError` (E5);
  the list shows `units_in_stock` 0 for product 3 (E6); `/products/1` returns 200 (E7).
- 18:41:53Z — metrics: 7 responses with status 500, 7 `ZeroDivisionError`, gauge 0,
  uptime 134 s with no reset (E8, E9, E11).

No configuration, flag, or deploy marker is in the log, apart from the process start.

## Investigation

- **Baseline.** Health, metrics, and the full log (25 lines at that time). Health was
  green while `/products/{product_id}` already had 4 responses with status 500 and 4
  `ZeroDivisionError` exceptions.
- **Triage.** Three lenses in parallel, each blind to the others: software defect,
  infrastructure and process, interfaces. All three found the same shape: one input
  fails, always. The infrastructure lens found one start, no restart, no saturation,
  no latency problem (E11). The interfaces lens found no gateway status, no change
  marker, and no probabilistic failure. Both lenses noted the null price of product 4.
- **Deep-dive.** None. The triage evidence for H1 was deterministic and complete. The
  evidence that H2 needs (telemetry before the process start) does not exist on the
  surface, so a deep-dive could not get it.
- **Judge.** One fresh judge, with the hypotheses and the verbatim evidence only.
  Verdicts: H1 validated, H2 inconclusive, H3 invalidated.
- **Budget.** One triage round, zero deep-dive agents, one judge round. The
  investigation stopped because the evidence on the surface was exhausted for H2.

## Hypotheses

### H1 — unguarded division by zero stock (software-defect) — validated

The stack names the throwing operation: `units_ordered / product["units_in_stock"]`
at `shop.py` line 64 (E1). E1 and E2 share one request id, so that exception is the
HTTP 500. The list shows stock 0 for product 3 only (E6). Product 1 returns
`turnover_score` 0.0169…, which is 2 / 118, so the formula holds (E7). Products 2, 4
and 5 return 200 (E4, E13). The counts agree: 7 responses with status 500 and 7
`ZeroDivisionError` exceptions, with no other failing route (E8). The judge found no
evidence against it.

### H2 — the process start brought a wrong build or configuration (infra-process) — inconclusive

For: a process start 7 seconds before the first failure (E10, E2). The judge gave
that timing no weight: the log starts at the process start, so every failure is after
it by construction. Against: the failure does not spread beyond one input (E4, E7,
E13), a data value explains it (E1, E6), and the process started once only (E11). The
judge kept it open because a wrong build or a data change at the start could have
introduced the division or the stock value 0. One record would settle it: a request
for `/products/3` served by a process before 18:39:38Z.

### H3 — an error-injection switch is on (infra-process) — invalidated

The gauge reads 0 in both scrapes (E9). The innermost frame is the business division,
not an injection (E1). The failures are deterministic for one input and absent from
every other route and id (E4, E5, E13). The log has no switch event of any kind.

## Safe next steps

Read-only only.

- Read the inventory history of product 3: when did `units_in_stock` become 0?
  That time is the probable onset.
- Read the deploy and process-manager records for the start at 18:39:38Z. A rollout
  or a data reload at that time would settle H2.
- Read `get_product` in `shop.py` at line 64 and list every field that it uses as a
  divisor.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and
  `http_requests_total{path="/products/{product_id}",status="500"}` to measure the
  customer impact over time.
- Watch the product list for other products that approach `units_in_stock` 0;
  product 2 is at 39 (E6).
- Ask the catalog owner whether `price: null` on product 4 is intended (E6).

## Gaps

- **Before the process start.** The log starts at 18:39:38.428Z and has no rotated
  backup. The complaint says "within the last hour" and "no deploys"; the surface can
  confirm neither. H2 stays inconclusive for this reason.
- **Why the process started.** The surface has no deploy record and no exit event.
- **Stock history.** The surface shows the stock of product 3 now, not its history.
  The log has orders for products 1 and 2 only.
- **Customer traffic after 18:39:51Z.** None is in the log. "Still happening" rests
  on three investigator probes, which all failed.
- **Source code.** It is outside the surface; the mechanism comes from the stack
  trace and the response shapes.
- **Product 4, null price.** The page works. The order path is a POST and was not
  tested.
- **Tokens.** The run did not capture a token total.
