---
konan_journal: 2
investigation:
  id: 2026-11-15-product-page-500s
  trigger: |-
    manual — /konan, the human profile of docs/triggers.md. Complaint object, verbatim:
    {"source": "human", "fingerprint": "human-1794753345", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"}, "startsAt": "2026-11-15T14:35:45Z"}
    Investigation start 2026-11-15T14:35:58Z; trigger latency 13 s. The reporter stated no severity.
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-15T14:35:58Z
  concluded: 2026-11-15T14:43:02Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product-detail handler divides units_ordered by the product's units_in_stock; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500 'internal server error', while the other four product pages return 200."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The product-detail handler divides units_ordered by units_in_stock; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500 'internal server error'."
    incident_class: software-defect
    state: validated
    evidence_for: [E4, E5, E6, E7, E8, E9, E10, E11, E14, E15]
    evidence_against: [E3]
  - id: H2
    statement: "A process failure produced the errors: the process crashed or hung this morning and came back at 14:35:33Z, and customers saw errors around that failure."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E2]
    evidence_against: [E13, E16]
  - id: H3
    statement: "An operational degradation switch (chaos mode) inside the target injects HTTP 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E10, E11, E12, E14, E16]
evidence:
  - id: E1
    type: probe
    source: "/health, request id konan-1794753359-2346, 2026-11-15T14:35:59Z (baseline)"
    quote: |-
      {"status":"ok","uptime_seconds":26.0668180831708}
      -- HTTP 200 in 0.002188s request_id=konan-1794753359-2346
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:35:33.035Z (line 3 of the file; the first line is at 14:35:33.034Z; no rotated backups exist)"
    quote: |-
      {"ts": "2026-11-15T14:35:33.035Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E3
    type: metric
    source: "/metrics, request id konan-1794753359-2351, 2026-11-15T14:35:59Z (baseline, after all non-investigator traffic and before any investigator probe of a product page): http_exceptions_total has no series"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 0
  - id: E4
    type: probe
    source: "/products/3, request id konan-1794753403-2420, 2026-11-15T14:36:43Z"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794753403-2420"}
      -- HTTP 500 in 0.010252s request_id=konan-1794753403-2420
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:36:43.125Z (stack trimmed to its last frame, with the checkout prefix of its file path redacted as <checkout>)"
    quote: |-
      {"ts": "2026-11-15T14:36:43.125Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794753403-2420", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n … File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:36:43.134Z through 14:36:51.896Z: the five access lines with a status of 500 or above; the 39-line log holds no other such line, and all five carry investigator request ids (konan-)"
    quote: |-
      {"ts": "2026-11-15T14:36:43.134Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794753403-2420", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 9.327, "client": "127.0.0.1:53117"}
      {"ts": "2026-11-15T14:36:47.424Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794753407-2440", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.721, "client": "127.0.0.1:53120"}
      {"ts": "2026-11-15T14:36:51.865Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794753411-2450", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.659, "client": "127.0.0.1:53122"}
      {"ts": "2026-11-15T14:36:51.881Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794753411-2453", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.616, "client": "127.0.0.1:53123"}
      {"ts": "2026-11-15T14:36:51.896Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794753411-2456", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.412, "client": "127.0.0.1:53124"}
  - id: E7
    type: probe
    source: "/products, request id konan-1794753399-2404, 2026-11-15T14:36:39Z"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001297s request_id=konan-1794753399-2404
  - id: E8
    type: probe
    source: "/products/1, request id konan-1794753407-2445, 2026-11-15T14:36:47Z"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}
      -- HTTP 200 in 0.001401s request_id=konan-1794753407-2445
  - id: E9
    type: probe
    source: "/products/4, request id konan-1794753403-2425, 2026-11-15T14:36:43Z"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001304s request_id=konan-1794753403-2425
  - id: E10
    type: metric
    source: "/metrics, request id konan-1794753475-2529, 2026-11-15T14:37:55Z: the complete set of http_requests_total series"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/openapi.json",status="200"} 1
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 8
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 5
      http_requests_total{method="POST",path="/orders",status="201"} 1
  - id: E11
    type: metric
    source: "/metrics, request id konan-1794753475-2529, 2026-11-15T14:37:55Z: the only http_exceptions_total series"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 5
  - id: E12
    type: metric
    source: "/metrics, request id konan-1794753475-2529, 2026-11-15T14:37:55Z"
    quote: |-
      faultline_chaos_enabled 0
  - id: E13
    type: metric
    source: "/metrics, request id konan-1794753475-2529, 2026-11-15T14:37:55Z (116.5 s after E1)"
    quote: |-
      process_uptime_seconds 142.62985933292657
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:36:51.923Z and 14:36:58.556Z: product ids 2 and 4 answer 200 in the same seconds as the failures of product 3"
    quote: |-
      {"ts": "2026-11-15T14:36:51.923Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "konan-1794753411-2462", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.431, "client": "127.0.0.1:53126"}
      {"ts": "2026-11-15T14:36:58.556Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794753418-2487", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.445, "client": "127.0.0.1:53130"}
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:35:34.847Z through 14:35:39.085Z: the complete set of non-investigator product-detail requests in the log; none is for /products/3"
    quote: |-
      {"ts": "2026-11-15T14:35:34.847Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "2fc79e46c411", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.063, "client": "127.0.0.1:53078"}
      {"ts": "2026-11-15T14:35:35.909Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "7a4f107b2ccd", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1.078, "client": "127.0.0.1:53079"}
      {"ts": "2026-11-15T14:35:39.085Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "8e6e39762dbe", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.77, "client": "127.0.0.1:53083"}
  - id: E16
    type: log
    source: "lab/logs/app.log, all 39 lines (14:35:33.034Z through 14:37:55Z): the four distinct event values of the file, with counts 1 startup, 28 request, 1 order_created, 5 unhandled_exception; no chaos_enabled, chaos_disabled, chaos_failure or simulated_exception line, and no crash, exit or shutdown message"
    quote: |-
      "event": "startup"
      "event": "request"
      "event": "order_created"
      "event": "unhandled_exception"
gaps:
  - "No telemetry exists before the process start at 2026-11-15T14:35:33.034Z: the log begins there, has no rotated backups, and the counters began at zero. The period of the complaint ('this morning') is not observed."
  - "No customer request to /products/3 is in the telemetry. All five HTTP 500 responses are investigator probes, and the three non-investigator product-page requests (ids 1, 2, 5) returned 200. That the customers hit this defect rests on the symptom match (a product page, the body 'internal server error') and on the absence of any other failing path; the judge held this attribution inconclusive."
  - "The complaint names no product, no time and no count, so it could not be matched to requests."
  - "When units_in_stock of product 3 became 0 is unknown: the log carries no stock-change event, so the onset of the failure cannot be dated."
  - "How an earlier process instance ended, or whether one existed, is out of reach: the surface carries no host or launcher record. H2 stays inconclusive."
  - "The automated check of this journal against the schema was not run (no interpreter without approval in this session); the checklist was applied by hand."
usage:
  model: claude-fable-5-2
  tokens: 1780856
  wall_clock_seconds: 424
---

# Product page 3 returns HTTP 500: division by zero on zero stock

## Summary

**Verdict: root cause identified.** `GET /products/3` fails on every request with HTTP 500
and the body `{"error":"internal server error", …}` (E4). The product-detail handler
computes `turnover_score` as `units_ordered / units_in_stock` (E5), and product 3 is the
only product with `units_in_stock` 0 (E7), so the division raises an unhandled
`ZeroDivisionError`. Five of five requests to `/products/3` failed (E6, E10, E11); the
other four product pages return 200 (E8, E9, E14, E15). Class: software defect,
data-dependent and deterministic per input. Chaos mode is off and there is no restart
during the observation (E12, E13, E16).

**Impact and confidence.** Any customer who opens product 3 ("Unobtainium Ingot") gets the
error; the other product pages, the product list, and orders work. Confidence in the
mechanism is high: the judge validated it. Confidence that this is what the customers saw
this morning is medium, and it is a limit of the telemetry, not a finding: the process
started at 14:35:33Z (E2), nothing earlier is recorded, and no customer request to
`/products/3` is in the log — all five failures are investigator probes (E6), and no
exception existed before those probes (E3). The reported symptom matches the defect, and
no other failing path exists on the surface.

## Timeline

All times UTC, 2026-11-15.

- 14:35:33.035 — process start, `faultline 0.1.0 started` (E2). The earliest telemetry.
  The only lifecycle or change marker in the log (E16).
- 14:35:34–14:35:39 — non-investigator traffic: `/products/1`, `/products/2`,
  `/products/5` return 200 (E15). No request to `/products/3`.
- 14:35:45 — the complaint is raised (`startsAt`). 14:35:58 — investigation start.
- 14:35:59 — baseline: health `ok`, uptime 26 s (E1); no exception series, chaos 0 (E3).
- 14:36:39 — the product list shows product 3 with `units_in_stock` 0 (E7).
- 14:36:43.125 — first `ZeroDivisionError`, on an investigator probe of `/products/3`
  (E4, E5, E6).
- 14:36:47–14:36:51 — four more HTTP 500 on `/products/3`, all investigator probes (E6);
  `/products/1`, `/products/2`, `/products/4` return 200 in the same seconds (E8, E9, E14).
- 14:37:55 — metrics: 5 × 500 on the product-detail route, 5 × `ZeroDivisionError`,
  chaos 0, uptime 142.6 s without a reset (E10–E13).

## Investigation

**Complaint object** (human profile, `docs/triggers.md`), verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794753345",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?" },
  "startsAt": "2026-11-15T14:35:45Z"
}
```

Investigation start: 2026-11-15T14:35:58Z. Trigger latency: 13 s.

**Baseline.** Health 200 with uptime 26 s (E1); a 16-line log that begins at the process
start (E2); every request counter 2xx; no exception series; chaos 0 (E3). The baseline
was clean, and it covered only 26 seconds of process life.

**Triage.** Three lenses in parallel, each blind to the others: software-defect,
infra-process, interfaces.

- software-defect: `/products/3` returns 500 with `ZeroDivisionError`, twice of twice;
  the stack names the `turnover_score` division; product 3 alone has stock 0.
- interfaces: the same failure, three of three; no gateway-shaped status, no change
  marker except the startup. It handed the finding to the software-defect domain.
- infra-process: no anomaly. One startup, steady uptime, flat memory
  (`process_max_rss_bytes 46645248` at both scrapes), chaos 0. It flagged that the
  process is young and that nothing earlier is recorded.

The probes of the lenses produced E4 and E7–E9; the log confirms each by request id.

**Deep-dive.** Skipped. The triage evidence for H1 was deterministic and complete (five
reproductions, the stack trace, the distinguishing input). For H2 and H3 the surface holds
no further evidence to gather.

**Judge.** One fresh judge, evidence only.

- H1: mechanism **validated**. The attribution to the customers' errors of this morning:
  **inconclusive**, because the complaint period is outside the telemetry. The settling
  evidence it named is a record from that period of a non-investigator request to
  `/products/3` with status 500 — out of reach on this surface.
- H2: **inconclusive** and unsupported. A start is proven, a crash is not.
- H3: **invalidated**. The exception count equals the 500 count, so no 500 is left for
  an injected failure.

Two open points of the judge were closed after its verdict. The eight 200 responses on
the product-detail route (E10) are three non-investigator requests (E15) and five
investigator probes of ids 1, 1, 2, 4, 4 — none is a `/products/3` success. The log
holds no chaos event (E16).

**Conclusion.** Evidence on the surface is exhausted, so no second round ran. The verdict
names the validated mechanism as the root cause of the reported symptom, which reproduces
now on the business surface. The unproven attribution is stated in Gaps, not hidden.

## Hypotheses

### H1 — division by zero on product 3 (software-defect) — validated

The handler divides by `units_in_stock` (E5: `shop.py` line 64,
`"turnover_score": units_ordered / product["units_in_stock"]`). Product 3 has stock 0
(E7). Every request to `/products/3` returned 500 with `ZeroDivisionError` (E4, E6), and
the counters agree: five 500 responses, five exceptions of that one type, on that one
route (E10, E11). The formula reproduces on the healthy products: product 1 returns
`turnover_score` 0.0084…, which is 1/119 (E8); product 4 returns 0.0, which is 0/75 (E9).
Products 2 and 4 answered 200 in the same seconds as the failures (E14), and customers'
requests to products 1, 2 and 5 answered 200 (E15).

Against, for the link to the complaint only: before the investigator probed a product
page, the exception counter had no series (E3). No customer triggered this defect in the
recorded window.

### H2 — process crash or hang (infra-process) — inconclusive

For: the process was 26 s old at the baseline (E1) and the log begins with its startup
(E2). Against: uptime rose without a reset through the observation (E13), and the log
holds one startup and no crash, exit or shutdown line (E16). A routine start fits the
same evidence, and H2 explains none of the observed 500 responses, which all occurred
while the process was up. The record of an earlier instance would settle it; the surface
has none.

### H3 — chaos mode injects 500s (infra-process) — invalidated

`faultline_chaos_enabled` is 0 before and after the failures (E3, E12). The log has no
chaos event (E16). The 500s sit on one product id while other ids answer 200 in the same
seconds (E10, E14), and `ZeroDivisionError` accounts for every one of them (E11).

## Safe next steps

Read-only only.

- Ask support for the product (or URL) and the time of the failing customer requests,
  and compare them with product 3.
- Look for records older than 14:35:33Z outside this surface (the host's process manager,
  any log store) for non-investigator 500 responses on `/products/3`.
- Watch `http_requests_total{path="/products/{product_id}",status="500"}` and
  `http_exceptions_total{type="ZeroDivisionError"}`: growth from requests without the
  `konan-` prefix confirms customer impact.
- Read the product list from time to time: by this mechanism, any other product whose
  `units_in_stock` reaches 0 is predicted to fail the same way. This is a prediction, not
  an observation.
- Hand E5 (file, line, expression) to the owner of the service code.

## Gaps

- **The complaint period is not observed.** The log begins at the process start,
  14:35:33.034Z, has no rotated backups, and the counters began at zero.
- **No customer failure is in the telemetry.** All five 500 responses are investigator
  probes. The link between the defect and the customers' reports rests on the matching
  symptom and on the absence of any other failing path. The judge held it inconclusive.
- **The complaint is unspecific.** No product, time or count to match against requests.
- **The onset cannot be dated.** Nothing records when the stock of product 3 became 0.
- **The earlier process instance is out of reach.** No host or launcher record on the
  surface; H2 stays inconclusive.
- **Journal validation.** The automated schema check did not run in this session; the
  checklist was applied by hand.
