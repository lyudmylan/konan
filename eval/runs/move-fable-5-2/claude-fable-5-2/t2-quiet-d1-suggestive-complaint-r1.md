---
konan_journal: 2
investigation:
  id: 2026-11-15-product-page-500s
  trigger: "manual (/konan human report; fingerprint human-1794752574; startsAt 2026-11-15T14:22:54Z)"
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-15T14:23:07Z
  concluded: 2026-11-15T14:26:39Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product page handler divides by the product's units_in_stock; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500 'internal server error'."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The handler of GET /products/{id} divides by units_in_stock; for product 3 the stock is 0, the division raises an unhandled ZeroDivisionError, and the page returns HTTP 500 on every request while other product ids succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E4, E5, E6, E7, E8, E9, E10, E11]
    evidence_against: []
  - id: H2
    statement: "The 500 responses come from the process or an operational switch: a crash or restart loop, or an injected degradation (chaos) switch."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1]
    evidence_against: [E2, E3, E8, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:22:42.500Z (the only startup event in the file; the file has no rotated backups)"
    quote: |-
      {"ts": "2026-11-15T14:22:42.500Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: probe
    source: "/health, request_id=konan-1794752588-1639 (baseline)"
    quote: |-
      {"status":"ok","uptime_seconds":25.874660416971892}
      -- HTTP 200 in 0.001627s request_id=konan-1794752588-1639
  - id: E3
    type: metric
    source: "/metrics, request_id=konan-1794752588-1644 (baseline, before any investigator probe of a product page; no status 500 series and no http_exceptions_total series existed)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 26.46655225008726
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:22:44.330Z (non-investigator request)"
    quote: |-
      {"ts": "2026-11-15T14:22:44.330Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "fabab515fad0", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.998, "client": "127.0.0.1:52943"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:22:48.541Z (non-investigator request, the last one in the file)"
    quote: |-
      {"ts": "2026-11-15T14:22:48.541Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "ac61b28490d0", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.776, "client": "127.0.0.1:52947"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:23:51.514Z (investigator probe; stack trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: |-
      {"ts": "2026-11-15T14:23:51.514Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794752631-1704", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:23:51.523Z (investigator probe, the first 500 in the file)"
    quote: |-
      {"ts": "2026-11-15T14:23:51.523Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794752631-1704", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 9.146, "client": "127.0.0.1:52974"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:23:51.902Z (investigator probe, 0.4 s after the first 500)"
    quote: |-
      {"ts": "2026-11-15T14:23:51.902Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794752631-1709", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.468, "client": "127.0.0.1:52975"}
  - id: E9
    type: probe
    source: "/products, request_id=konan-1794752687-1812"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001416s request_id=konan-1794752687-1812
  - id: E10
    type: probe
    source: "/products/3, request_id=konan-1794752687-1817"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794752687-1817"}
      -- HTTP 500 in 0.005190s request_id=konan-1794752687-1817
  - id: E11
    type: metric
    source: "/metrics, request_id=konan-1794752706-1835 (after six investigator probes of /products/3; no other route had a non-2xx series)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 6
      http_exceptions_total{type="ZeroDivisionError"} 6
      faultline_chaos_enabled 0
      process_uptime_seconds 143.62873070780188
gaps:
  - "No customer failure is on record: the log and the counters start at the process start, 2026-11-15T14:22:42.500Z, 12 s before the complaint, and the file has no rotated backups. The 'this morning' window of the complaint is outside the surface."
  - "All six 500 responses on /products/3 carry investigator request ids (konan-). The eight non-investigator requests in the log returned 2xx and none of them requested /products/3, so user impact rests on the complaint plus the determinism of the defect, not on an observed customer request."
  - "The reason for the process start at 14:22:42.500Z is not visible (no earlier log, no exit or crash event), so a restart before the window can be neither shown nor excluded."
  - "Which product pages the customers opened is not known; the complaint names no product."
  - "Automated validation of this journal against the schema did not run in this session; the checklist was applied by hand."
usage:
  model: claude-fable-5-2
  tokens: 1470233
  wall_clock_seconds: 212
---

# Product page 500s: division by zero on the page of product 3

## Summary

**Root cause identified.** The page of product 3 (`GET /products/3`) fails on every
request with HTTP 500 and the body `"error":"internal server error"` (E10). The handler
`get_product` computes `units_ordered / product["units_in_stock"]` (E6), and product 3
is the only product with `units_in_stock` 0 (E9), so the division raises an unhandled
`ZeroDivisionError`. The failure is deterministic for this one input: six of six
requests failed with the same exception (E11), and the pages of products 1, 4 and 5
answered 200 in the same minutes (E4, E5, E8). Chaos mode is off and the process did
not restart during the investigation (E3, E11).

Impact: every request for the page of product 3 fails while its stock is 0; no other
route and no other product is affected. Confidence in the mechanism is high. Confidence
that this is what the customers saw is medium: the symptom matches the complaint
word for word, but the available telemetry starts 12 s before the complaint and holds
no customer request for product 3 (see Gaps).

## Timeline

- 14:22:42.500Z: process start, `faultline 0.1.0 started` (E1). Nothing earlier is
  visible.
- 14:22:43Z to 14:22:48Z: eight non-investigator requests, all 2xx, among them the
  pages of products 1, 2 and 5 (E4, E5). None requested product 3.
- 14:22:54Z: the complaint was raised (`startsAt`).
- 14:23:07Z: investigation start. Baseline at 14:23:08Z: health 200, no 500 series,
  no exception series, chaos gauge 0 (E2, E3).
- 14:23:51.514Z: first observed `ZeroDivisionError`, on an investigator probe of
  `/products/3`; access line 500 at 14:23:51.523Z (E6, E7).
- 14:23:51.902Z: `/products/4` answers 200 (E8).
- 14:24:47Z: `/products` shows `units_in_stock` 0 for product 3 only (E9);
  `/products/3` answers 500 again (E10).
- 14:25:06Z: metrics show six 500 responses and six `ZeroDivisionError` exceptions on
  the product route, chaos gauge 0, uptime 143.6 s without a reset (E11).

No configuration, deploy, or chaos marker exists in the log; the only lifecycle marker
is the startup at 14:22:42.500Z (E1).

## Investigation

The complaint object, verbatim, with the investigation start:

```json
{
  "source": "human",
  "fingerprint": "human-1794752574",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?" },
  "startsAt": "2026-11-15T14:22:54Z"
}
```

Investigation start: 2026-11-15T14:23:07Z (trigger latency 13 s).

- **Baseline.** `/health` 200 with uptime 25.9 s (E2). `/metrics`: all series 2xx, no
  exception series, chaos gauge 0 (E3). Log: 16 lines, one startup, eight
  non-investigator requests, no ERROR line.
- **Triage.** Three lenses ran in parallel, blind to each other: software-defect,
  infra-process, interfaces. The software-defect lens probed the product pages and
  found the 500 on `/products/3` with `ZeroDivisionError`. The infra-process lens found
  no lifecycle, saturation, latency, or switch anomaly. The interfaces lens found no
  gateway status, no change marker, and no probabilistic failure; it confirmed the
  per-input shape. It also saw `"price":null` on product 4 with HTTP 200 (E9); this was
  observed, not assessed.
- **Deep-dive.** Skipped: the triage evidence for H1 was deterministic and complete
  (stack trace, failing input, six of six failures, sibling inputs healthy).
- **Judge.** One fresh judge saw the hypotheses and the quoted evidence only. H1:
  validated. H2: invalidated. To the separate question of customer impact the judge
  answered "not shown, not ruled out".

Investigator traffic: six probes of `/products/3`, all 500. The 500 and exception
counters in E11 are investigator-caused in full.

## Hypotheses

### H1: division by zero on the page of product 3 (validated)

The stack trace ends in `get_product`, `shop.py` line 64, at
`units_ordered / product["units_in_stock"]` (E6), and the same request id maps to
`GET /products/3 -> 500` (E7). The product list shows stock 0 for product 3 and
non-zero stock for all others (E9). The response body names the same exception (E10).
The counters agree: six 500 responses and six `ZeroDivisionError` on the product route
(E11), against none at baseline (E3). Products 1 and 5 answered 200 to user requests
(E4, E5) and product 4 answered 200 0.4 s after a failure (E8). Limits: the stack is
quoted for one of the six requests; "every request" holds while the stock is 0; the
one order in the log was for product 1, so no order in this process changed the stock
of product 3.

### H2: process lifecycle or an injected degradation switch (invalidated)

The only support is the startup marker 26 s before the baseline (E1). Every prediction
failed: the chaos gauge was 0 before and after the failures (E3, E11) and the log has
no chaos event; there is one startup event, and uptime grew from 26.5 s to 143.6 s
without a reset (E3, E11); health answered 200 (E2); failures sit on one input of one
route while a sibling page answered 200 in the same second (E8, E11).

## Safe next steps

- Ask support which product pages the customers opened; the prediction of H1 is that
  all of them are product 3.
- Read the access log of the period before 14:22:42Z, if a copy exists outside this
  surface (an edge or proxy log), for `GET /products/3` with status 500.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the 500 series of
  `/products/{product_id}`; count only requests whose id does not start with `konan-`.
- Read `units_in_stock` in `/products` for any other product that reaches 0; H1
  predicts that its page fails the same way.
- Hand E6 (the stack trace) and E9 (the stock values) to the owners of the service.

## Gaps

- **No customer failure on record.** The log and the counters start at the process
  start, 14:22:42.500Z, and there are no rotated backups. The morning that the
  complaint names is outside the surface.
- **Impact is inferred.** All six failures are investigator probes. No non-investigator
  request for `/products/3` exists in the log. The link to the complaint is the exact
  symptom match plus the determinism of the defect.
- **The process start is unexplained.** No earlier log, no exit or crash event; a
  restart before the window can be neither shown nor excluded.
- **The products in the complaint are unknown.** The complaint names no product.
- **Validation.** The automated schema check did not run in this session; the
  checklist of the report contract was applied by hand: every `E<n>` reference
  resolves, the root cause points at a validated hypothesis, the cause id is in its
  class, and the wall clock equals concluded minus started (212 s).
