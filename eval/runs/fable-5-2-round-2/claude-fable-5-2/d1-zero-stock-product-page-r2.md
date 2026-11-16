---
konan_journal: 2
investigation:
  id: 2026-11-15-product-page-500
  trigger: 'manual — /konan human report. Complaint object: {"source": "human", "fingerprint": "human-1794768368", "labels": {"alertname": "human-report"}, "annotations": {"summary": <the complaint field below, verbatim>}, "startsAt": "2026-11-15T18:46:08Z"}. No severity stated by the reporter. Investigation start 2026-11-15T18:46:21Z; trigger latency 13 s.'
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-15T18:46:21Z
  concluded: 2026-11-15T18:51:03Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product-detail handler computes turnover_score as units_ordered / units_in_stock with no guard for zero; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500, while products with non-zero stock succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The product-detail handler divides units_ordered by units_in_stock; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns 500, while other product ids succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E7, E9, E10, E11, E12, E17, E18]
    evidence_against: []
  - id: H2
    statement: "An operational degradation switch inside the target (chaos mode) injects the 500 errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E2, E4, E5, E16, E17]
  - id: H3
    statement: "A process-lifecycle fault (crash, restart loop, or hang) causes the errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E13, E14, E15, E5, E16, E19]
  - id: H4
    statement: "A rollout or configuration change at the process start (18:45:48.780Z) put the failing behaviour in place; before that start, /products/3 worked."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E3]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:45:48.780Z (line 3; the only startup event in the file)"
    quote: '{"ts": "2026-11-15T18:45:48.780Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:45:55.744Z (stack trimmed to its last frame, marked ...; the local path prefix is redacted as <checkout>)"
    quote: '{"ts": "2026-11-15T18:45:55.744Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "2283e4fab75e", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n ... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:45:55.753Z (the first request to /products/3 in the file)"
    quote: '{"ts": "2026-11-15T18:45:55.753Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "2283e4fab75e", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.273, "client": "127.0.0.1:55086"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:46:02.064Z (the fourth and last non-investigator request to /products/3; request ids 8bd22b3e6ea5 @ 18:45:56.817Z and 8945d390e2a4 @ 18:45:59.942Z have the same shape, status 500, each after a ZeroDivisionError line)"
    quote: '{"ts": "2026-11-15T18:46:02.064Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "942f6af4050e", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.746, "client": "127.0.0.1:55091"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:45:58.880Z (between two /products/3 failures)"
    quote: '{"ts": "2026-11-15T18:45:58.880Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "33ad793ced77", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.756, "client": "127.0.0.1:55088"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:45:50.565Z"
    quote: '{"ts": "2026-11-15T18:45:50.565Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "0a373d69fcfb", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.141, "client": "127.0.0.1:55082"}'
  - id: E7
    type: metric
    source: "/metrics probe request_id=konan-1794768387-17579, logged 2026-11-15T18:46:27.674Z (baseline; before any investigator request to /products/*)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E8
    type: metric
    source: "/metrics probes request_id=konan-1794768387-17579 (baseline) and request_id=konan-1794768532-17732 (final); same value in both"
    quote: "faultline_chaos_enabled 0"
  - id: E9
    type: probe
    source: "/products request_id=konan-1794768492-17704"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001603s request_id=konan-1794768492-17704
  - id: E10
    type: probe
    source: "/products/3 request_id=konan-1794768429-17621 (investigator reproduction, software-defect lens)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794768429-17621"}
      -- HTTP 500 in 0.004653s request_id=konan-1794768429-17621
  - id: E11
    type: probe
    source: "/products/1 request_id=konan-1794768434-17647 (software-defect lens)"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":118,"units_ordered":2,"turnover_score":0.01694915254237288}
      -- HTTP 200 in 0.001327s request_id=konan-1794768434-17647
  - id: E12
    type: probe
    source: "/products/4 request_id=konan-1794768444-17679 (software-defect lens)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001564s request_id=konan-1794768444-17679
  - id: E13
    type: probe
    source: "/health request_id=konan-1794768387-17572, logged 2026-11-15T18:46:27.109Z (baseline)"
    quote: |-
      {"status":"ok","uptime_seconds":38.32506929105148}
      -- HTTP 200 in 0.001695s request_id=konan-1794768387-17572
  - id: E14
    type: metric
    source: "/metrics probes request_id=konan-1794768387-17579 (logged 18:46:27.674Z), request_id=konan-1794768436-17660 (logged 18:47:16.701Z), request_id=konan-1794768532-17732 (final); one value per probe, in that order"
    quote: |-
      process_uptime_seconds 38.89024437498301
      process_uptime_seconds 87.9173425831832
      process_uptime_seconds 183.83996416581795
  - id: E15
    type: metric
    source: "/metrics probes request_id=konan-1794768387-17579 (baseline) and request_id=konan-1794768532-17732 (final); same value in both"
    quote: "process_max_rss_bytes 47710208"
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:46:01.000Z (between two /products/3 failures)"
    quote: '{"ts": "2026-11-15T18:46:01.000Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "3ad1c1a3bfbf", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.413, "client": "127.0.0.1:55090"}'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:47:09.870Z (the access line of the reproduction in E10; a second investigator request to /products/3, request_id konan-1794768447-17692, logged status 500 @ 18:47:27.696Z after a ZeroDivisionError line)"
    quote: '{"ts": "2026-11-15T18:47:09.870Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794768429-17621", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 3.892, "client": "127.0.0.1:55122"}'
  - id: E18
    type: metric
    source: "/metrics probe request_id=konan-1794768532-17732 (final; after two investigator requests to /products/3)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 6
      http_exceptions_total{type="ZeroDivisionError"} 6
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:47:28.127Z (the request right after the second investigator 500)"
    quote: '{"ts": "2026-11-15T18:47:28.127Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "konan-1794768448-17697", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.445, "client": "127.0.0.1:55131"}'
gaps:
  - "Onset cannot be dated: the only log file starts at the process start (2026-11-15T18:45:48.780Z) and no rotated backup exists, so the complaint's 'started within the last hour' cannot be checked; the first /products/3 request in the file already fails."
  - "H4 stays open: whether a rollout or a configuration change at the process start introduced the division or the zero stock needs a comparison with the release and configuration that ran before the start; that is outside the surface contract."
  - "Why and when units_in_stock of product 3 became 0 is not visible: the surface has no data-layer telemetry and no history of the stock value."
  - "'Still happening' rests on investigator probes: the last non-investigator request in the log is at 18:46:02.064Z; after it, only konan-* requests exist."
  - "The detail page of product 5 was never requested by a user or by a probe; its stock in the list is 500."
  - "lab/server.out (server stdout) was not read; the investigator's surface in docs/lab.md names lab/logs/app.log as the log source."
usage:
  model: claude-fable-5-2
  tokens: 1447464
  wall_clock_seconds: 282
---

# Product 3 detail page returns HTTP 500: division by zero on a zero stock value

## Summary

**Verdict: root cause identified (software defect, unhandled exception).** The
product-detail handler computes `turnover_score` as `units_ordered / units_in_stock`
(E2). Product 3 has `units_in_stock` 0 (E9), so every `GET /products/3` raises an
unhandled `ZeroDivisionError` and returns HTTP 500 with the body "internal server
error" (E3, E4, E10). The failure is deterministic for that one input: 4 of 4 user
requests failed (E7), and 2 of 2 investigator reproductions failed (E17, E18). Products
with non-zero stock succeed on the same route, also between the failures (E5, E11, E12),
and orders succeed (E16). This matches the complaint: one product page fails, a refresh
does not help, other pages load.

Impact: every visitor of the product 3 detail page. No other route and no other product
shows an error. Chaos mode is off (E8) and the process is stable (E13, E14, E15).

Confidence: high for the mechanism. Open: the onset time and whether a rollout at the
process start introduced the defect (H4, see Gaps). The telemetry shows a process start
at 18:45:48.780Z (E1), 7 seconds before the first observed failure; the complaint says
"No deploys that we know of".

## Timeline

All times UTC, 2026-11-15.

- 18:45:48.780 — process start, `faultline 0.1.0 started` (E1). The log has no earlier line.
- 18:45:50.565 — `GET /products/1 -> 200` (E6).
- 18:45:55.744 — first `ZeroDivisionError` at `shop.py` line 64, `get_product` (E2).
- 18:45:55.753 — first `GET /products/3 -> 500`, same request id (E3).
- 18:45:56.817, 18:45:59.942 — second and third user 500 on `/products/3` (E4, source note).
- 18:45:58.880 — `GET /products/2 -> 200` between the failures (E5).
- 18:46:01.000 — `POST /orders -> 201` between the failures (E16).
- 18:46:02.064 — fourth and last user 500 on `/products/3` (E4).
- 18:46:08 — complaint raised (`startsAt`).
- 18:46:21 — investigation start (trigger latency 13 s).
- 18:46:27 — baseline: health ok, uptime 38 s (E13); 4 × 500 and 4 × `ZeroDivisionError`
  (E7); chaos gauge 0 (E8).
- 18:47:09.870 — investigator reproduction, `GET /products/3 -> 500` (E10, E17).
- 18:47:27.696 — second investigator reproduction, 500 (E17, source note).
- 18:47:28.127 — `GET /products/2 -> 200` right after it (E19).
- 18:48:12 — product list: `units_in_stock` 0 for id 3 only (E9).
- 18:48:52 — final metrics: 6 × 500, 6 × `ZeroDivisionError`, uptime 183.8 s (E18, E14).

No configuration, flag, or chaos marker exists in the log. The only change marker is the
process start (E1).

## Investigation

**Trigger.** Manual, `/konan`. Complaint object:

```json
{
  "source": "human",
  "fingerprint": "human-1794768368",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of." },
  "startsAt": "2026-11-15T18:46:08Z"
}
```

Investigation start: 2026-11-15T18:46:21Z. `KONAN_ADAPTER` was unset, so the surface
contract is `docs/lab.md`.

**Baseline.** `/health` 200 (E13). `/metrics`: all 5xx on `/products/{product_id}`, one
exception type, chaos gauge 0, uptime 38.9 s (E7, E8, E14). Log: one file, one startup,
four 500s, all on `/products/3`.

**Triage (one round, three lenses in parallel, each blind to the others).**

- software-defect: one failing unit, `GET /products/3`; the divisor is the stock value;
  one reproduction (E10); contrast probes on ids 1 and 4 (E11, E12).
- infra-process: no anomaly that explains the 500s; one process start and no restart
  (E1, E14); memory flat (E15); chaos off (E8).
- interfaces: no anomaly; the failure is per input, not per request; no gateway-shaped
  status; no change marker except the process start; one more reproduction (E17, source
  note).

The orchestrator checked the lens quotes against the log by request id and took the
product list (E9) and the final metrics (E18) directly.

**Deep-dive.** None. The triage evidence for H1 was deterministic and complete, so H1
went straight to the judge. H2 and H3 had only disconfirming evidence. H4 has no
evidence in reach of the surface.

**Judge (fresh agent, evidence only).** H1 validated; H2 invalidated; H3 invalidated;
H4 inconclusive. The judge named the settling evidence for H4: the difference between
the release and configuration before 18:45:48.780Z and the one started then, at
`shop.py` line 64 and at the stock of product 3. That evidence is outside the surface
contract, so no second round ran.

## Hypotheses

### H1 — division by zero on product 3's zero stock (validated)

The stack names the operation: `"turnover_score": units_ordered / product["units_in_stock"]`
at `shop.py` line 64 in `get_product` (E2), tied to the 500 by request id (E3). The
list endpoint shows stock 0 for id 3 only (E9). All six observed requests to
`/products/3` failed, four from users and two from the investigator (E4, E7, E10, E17,
E18), with one `ZeroDivisionError` per 500. Ids 1 and 4 return 200 with a
`turnover_score` equal to `units_ordered / units_in_stock` (E11, E12). No evidence
against. Limits from the judge: E9 was taken after the failures, so the zero divisor at
failure time rests on the stack (E2); "every" means 6 of 6 observed requests in this
process.

### H2 — chaos mode injects the errors (invalidated)

The chaos gauge is 0 in the first and the last scrape (E8), and the log holds no chaos
event. The failures hit one input, 6 of 6, with a real arithmetic frame (E2, E4, E17),
while other routes and inputs succeed in between (E5, E16). An injected failure rate
predicts a spread over routes and inputs; that spread does not exist.

### H3 — process crash, restart loop, or hang (invalidated)

One startup event (E1). Three uptime values grow in step with the clock and point to
the same start (E14). Health is ok (E13), peak memory is flat (E15), the 500s take 3 to
10 ms (E3, E4, E17), and other requests succeed between and after the failures (E5,
E16, E19). The process is alive and serves.

### H4 — a rollout or configuration change at the process start (inconclusive)

E1 and E3 are compatible only: the failure exists at the first observed request after
the start. No known-good `/products/3` request and no earlier state exist in the
telemetry, so the prediction is untested. If H4 is true, H1 is still the mechanism; H4
is about when and how the defect or the zero stock arrived.

## Safe next steps

Read-only suggestions:

- Compare `get_product` at `shop.py` line 64 in the running release with the release
  before the process start at 18:45:48.780Z. This settles H4.
- Find what started the process at 18:45:48.780Z in the deploy and restart records.
- Read the history of `units_in_stock` for product 3: when did it reach 0, and by what?
- List all products with `units_in_stock` 0 in the catalog; H1 predicts the same 500 on
  the detail page of each one.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and
  `http_requests_total{path="/products/{product_id}",status="500"}`; subtract requests
  with a `konan-` request id to count user impact.

## Gaps

- **Onset.** The log starts at the process start, with no rotated backup. The
  complaint's "within the last hour" cannot be checked, and no last known-good request
  for product 3 exists.
- **H4.** The comparison of releases and configuration is outside the surface contract.
- **The zero stock.** The surface has no data-layer telemetry. Whether 0 is a correct
  stock value (sold out) or wrong data is not visible; the two orders in the log are for
  products 1 and 2.
- **"Still happening".** User traffic in the log ends at 18:46:02.064Z. The two later
  failures are investigator probes; they prove that the defect persists, not that users
  still hit it.
- **Product 5.** Its detail page was not requested; its stock is 500.
- **`lab/server.out`.** Not read; `docs/lab.md` names `lab/logs/app.log` as the
  investigator's log source.
