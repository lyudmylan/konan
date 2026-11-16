---
konan_journal: 2
investigation:
  id: 2026-11-15-product-page-500
  trigger: "manual — /konan human report; complaint object: source human, fingerprint human-1794768761, labels.alertname human-report, no severity stated, startsAt 2026-11-15T18:52:41Z; investigation start 2026-11-15T18:52:47Z (trigger latency 6 s)"
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-15T18:52:47Z
  concluded: 2026-11-15T18:58:16Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product handler get_product divides units_ordered by units_in_stock with no guard for zero; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "get_product divides units_ordered by units_in_stock with no guard for zero; product 3 has units_in_stock 0, so each GET /products/3 raises an unhandled ZeroDivisionError and returns 500, while products with stock above zero succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E16]
    evidence_against: []
  - id: H2
    statement: "An operational switch inside the target (chaos mode) injects the 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E18, E1, E9, E16]
  - id: H3
    statement: "A process lifecycle event (the process start at 18:52:23Z, a crash, or a restart loop) causes the failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E11]
    evidence_against: [E12, E13, E9, E1]
  - id: H4
    statement: "The stock record of product 3 is wrong or changed to 0 within the last hour, and this data change is the cause of the onset."
    incident_class: data-db
    state: inconclusive
    evidence_for: [E6]
    evidence_against: [E14, E15]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:52:30.470Z (stack trimmed to its last frame; <checkout> replaces the local path prefix of the target's checkout)"
    quote: '{"ts": "2026-11-15T18:52:30.470Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "15dad346e6e0", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n ... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:52:30.481Z"
    quote: '{"ts": "2026-11-15T18:52:30.481Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "15dad346e6e0", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 11.113, "client": "127.0.0.1:55157"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:52:36.781Z"
    quote: '{"ts": "2026-11-15T18:52:36.781Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "a763dea82ddd", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.591, "client": "127.0.0.1:55162"}'
  - id: E4
    type: metric
    source: "/metrics, request_id konan-1794768774-17905 (2026-11-15T18:52:54Z, before any investigator probe of a product route)"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4'
  - id: E5
    type: metric
    source: "/metrics, request_id konan-1794768774-17905 (2026-11-15T18:52:54Z)"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 4'
  - id: E6
    type: probe
    source: "/products, request_id konan-1794768868-18053"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}] -- HTTP 200 in 0.001823s request_id=konan-1794768868-18053'
  - id: E7
    type: probe
    source: "/products/3, request_id konan-1794768868-18058"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794768868-18058"} -- HTTP 500 in 0.004949s request_id=konan-1794768868-18058'
  - id: E8
    type: probe
    source: "/products/2, request_id konan-1794768869-18063"
    quote: '{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39,"units_ordered":1,"turnover_score":0.02564102564102564} -- HTTP 200 in 0.001318s request_id=konan-1794768869-18063'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:52:33.604Z (between the second and the third failing request of /products/3)"
    quote: '{"ts": "2026-11-15T18:52:33.604Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "c9baf7b8f524", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.774, "client": "127.0.0.1:55159"}'
  - id: E10
    type: metric
    source: "/metrics, request_id konan-1794768872-18078 (2026-11-15T18:54:32Z)"
    quote: 'faultline_chaos_enabled 0'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:52:23.469Z (the only startup event; the file begins at this timestamp and has no rotated backups)"
    quote: '{"ts": "2026-11-15T18:52:23.469Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E12
    type: metric
    source: "/metrics, request_id konan-1794768872-18078 (2026-11-15T18:54:32Z)"
    quote: 'process_uptime_seconds 129.17431395780295'
  - id: E13
    type: probe
    source: "/health, request_id konan-1794768773-17900 (2026-11-15T18:52:53Z)"
    quote: '{"status":"ok","uptime_seconds":30.064957874827087} -- HTTP 200 in 0.001519s request_id=konan-1794768773-17900'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:52:28.411Z"
    quote: '{"ts": "2026-11-15T18:52:28.411Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "0c5affbf33f5", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:52:35.717Z"
    quote: '{"ts": "2026-11-15T18:52:35.717Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "a3dd5c25df4f", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}'
  - id: E16
    type: metric
    source: "/metrics, request_id konan-1794768872-18078 (2026-11-15T18:54:32Z, after three investigator probes of /products/3)"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 7 ; http_exceptions_total{type="ZeroDivisionError"} 7'
  - id: E17
    type: metric
    source: "/metrics, request_id konan-1794768872-18078 (2026-11-15T18:54:32Z)"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="200"} 8'
  - id: E18
    type: metric
    source: "/metrics, request_id konan-1794768774-17905 (2026-11-15T18:52:54Z, 18 s after the last customer failure)"
    quote: 'faultline_chaos_enabled 0'
gaps:
  - "Onset: the log and the counters begin at the process start, 2026-11-15T18:52:23Z, and there are no rotated backups. The reported onset (within the last hour) and any earlier success of product 3 could not be checked."
  - "The stock of product 3: the surface shows the state (0), not its history. When and how it became 0 is not visible; no order event names product 3 in this process lifetime."
  - "The process start at 18:52:23Z: the complaint reports no deploys, and the surface cannot show what ran before this start or why the process started."
  - "Customer traffic stops in the log at 18:52:36Z. That the failure is still present after that time rests on three investigator probes (18:53:36Z to 18:54:28Z), not on customer requests."
  - "The source code is outside the surface. The mechanism is read from the stack trace line in E1, not from the code."
usage:
  model: claude-fable-5-2
  tokens: 1443791
  wall_clock_seconds: 329
---

# Product page for product 3 returns 500: division by a stock of zero

## Summary

**Root cause identified.** The handler `get_product` computes `turnover_score` as
`units_ordered / units_in_stock` with no guard for zero (E1). Product 3 has
`units_in_stock` 0 (E6), so every request for `/products/3` raises an unhandled
`ZeroDivisionError` and returns HTTP 500 (E1, E2, E7). Class `software-defect`, cause
`unhandled-exception`.

Impact: one product page. Four of four customer requests for `/products/3` failed
between 18:52:30Z and 18:52:36Z (E2, E3, E4). The other product pages, the product
list, orders, and health answered normally (E6, E8, E9, E13). The failure is
deterministic for this input, so a refresh does not help; this matches the complaint.

Confidence: high for the mechanism — the judge validated it, the exception counter
equals the 500 counter at both scrapes (E4, E5, E16), and a probe reproduced the
failure (E7). Low for the onset: telemetry begins at 18:52:23Z, so "within the last
hour" and the moment the stock reached zero are not confirmed (see Gaps).

## Timeline

All times UTC, 2026-11-15.

- 18:52:23.469 — process start, the only `startup` event in the log (E11). No
  configuration, flag, or chaos marker anywhere in the log.
- 18:52:24–18:52:28 — customer traffic succeeds: health, product list, products 1
  and 2, an order for product 1 (E14).
- 18:52:30.470 — first request for product 3 in this process: unhandled
  `ZeroDivisionError` (E1), then `GET /products/3 -> 500` (E2).
- 18:52:31–18:52:36 — three more customer failures on `/products/3`; the last at
  18:52:36.781 (E3). `/products/2` returns 200 at 18:52:33.604, between failures (E9).
  An order for product 2 succeeds at 18:52:35.717 (E15).
- 18:52:41 — complaint raised (`startsAt`). 18:52:47 — investigation start.
- 18:52:53–18:52:54 — baseline: health 200 (E13); four 500 responses and four
  `ZeroDivisionError` exceptions, all customer traffic (E4, E5); chaos gauge 0 (E18).
- 18:53:36–18:54:28 — three investigator probes of `/products/3`, all 500 (E7 is the
  last). These are investigator traffic, not customer impact.
- 18:54:32 — final scrape: 500 counter 7, exception counter 7 (E16), chaos gauge 0
  (E10), uptime 129 s with no reset (E12).

## Investigation

Complaint object, as synthesized by the manual trigger adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1794768761",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of." },
  "startsAt": "2026-11-15T18:52:41Z"
}
```

Investigation start: 2026-11-15T18:52:47Z (trigger latency 6 s).

- **Baseline.** `/health` 200 with uptime 30 s (E13); `/metrics` with four 500
  responses on the product route and four `ZeroDivisionError` exceptions (E4, E5); the
  log, 25 lines from the process start (E11).
- **Triage.** Three lenses in parallel, each blind to the others: software-defect,
  infra-process, interfaces. Software-defect found the failing unit (route
  `/products/{product_id}`, input 3) and the throwing operation. Infra-process found no
  anomaly: one start, no saturation, no latency change, no switch on. Interfaces found
  no anomaly: no gateway statuses, no change marker besides the start, failure per
  input and not per request.
- **Deep-dive.** Skipped. The triage evidence for H1 was deterministic and complete.
- **Judge.** One fresh agent with the hypotheses and the verbatim evidence only. H1
  validated; H2 and H3 invalidated; H4 inconclusive. The judge named one weak point for
  H2 (the chaos gauge was quoted only from the late scrape); the baseline scrape
  answers it (E18). Round 2 was not run: H1 is validated with its prediction confirmed
  by probe, and the evidence that would settle H4 is outside the surface.

## Hypotheses

### H1 — unguarded division in `get_product` (software-defect) — validated

The stack trace ends at `shop.py` line 64, `units_ordered / product["units_in_stock"]`
(E1), on the same request id as the 500 access line (E2). The product list shows stock
0 for product 3 only (E6). A probe of `/products/3` reproduced the 500 with the same
exception type (E7). The control runs the same code path with stock 39 and succeeds,
with `turnover_score` equal to 1/39 (E8). The exception counter equals the 500 counter
before the probes (E4, E5) and after them (E16). In the whole log, `/products/3` has
seven 500 responses and no 200 response.

### H2 — chaos switch injects the errors (infra-process) — invalidated

The chaos gauge is 0 at the baseline scrape (E18) and at the final scrape (E10). The
exception is raised on an arithmetic line of the handler (E1). Every 500 has a matching
`ZeroDivisionError` (E16). Product 2 succeeds between failures of product 3 (E9): the
failure follows one input, not a rate.

### H3 — process lifecycle event (infra-process) — invalidated

The start at 18:52:23Z (E11) is the only lifecycle marker. Uptime grows without a reset
(E12, E13), health answers 200 (E13), and the process serves product 2 inside the
failure window (E9). The failure is an exception in handler code (E1). The start is
still an open question for the onset (see Gaps).

### H4 — stock record of product 3 changed to 0 (data-db) — inconclusive

The surface shows the state, stock 0 (E6), and no change. The two order events in this
process name products 1 and 2 (E14, E15). Nothing before 18:52:23Z is visible. Even if
a change set the stock to 0, zero is a legitimate stock value: the change would be the
trigger, and the defect stays in the code (H1).

## Safe next steps

Read-only only.

- Read `shop.py` line 64 in `get_product` and confirm that no guard exists for
  `units_in_stock` equal to 0.
- List the products with `units_in_stock` 0 in the data source. Each one fails the same
  way; a product that sells out becomes one.
- Read the logs from before 18:52:23Z, if they exist outside this surface, to date the
  onset and the moment the stock of product 3 reached 0.
- Find out why the process started at 18:52:23Z, against the report of no deploys.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` against the 500 counter of
  the product route; they move together while this defect is active.

## Gaps

- **Onset.** Telemetry begins at the process start, 18:52:23Z, with no rotated log
  backups. The first request for product 3 in this process already failed. "Started
  within the last hour" is not confirmed and not refuted.
- **Stock history.** The surface has no event for a stock change. When and how the
  stock of product 3 became 0 is unknown; H4 stays inconclusive for this reason.
- **The process start.** The surface cannot show what ran before 18:52:23Z or what
  started the process.
- **Customer traffic after 18:52:36Z.** There is none in the log. The claim that the
  failure persists rests on investigator probes.
- **Source code.** Outside the surface; the mechanism comes from the stack trace.
