---
konan_journal: 2
investigation:
  id: 2026-11-15-product-3-page-500s
  trigger: 'manual (/konan, human profile). Complaint object: {"source": "human", "fingerprint": "human-1794747912", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Support reports: several customers say a product page errors out with ''Internal Server Error'' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."}, "startsAt": "2026-11-15T13:05:12Z"}. Investigation start 2026-11-15T13:05:18Z; trigger latency 6 s.'
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-15T13:05:18Z
  concluded: 2026-11-15T13:10:59Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product-detail handler get_product computes turnover_score as units_ordered / units_in_stock with no guard for zero, so every GET /products/3 (units_in_stock 0) raises ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The product-detail handler get_product divides units_ordered by the product's units_in_stock without a guard for zero; product 3 has units_in_stock 0, so every GET /products/3 raises ZeroDivisionError and returns HTTP 500, while the other product ids return 200."
    incident_class: software-defect
    state: validated
    evidence_for: [E3, E4, E6, E7, E8, E9, E10, E11, E12, E2, E5, E18]
    evidence_against: []
  - id: H2
    statement: "The process start at 13:04:54Z was a rollout or restart that put a build or state in place that introduced the failure; before that start the product-3 page worked."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E14, E17]
    evidence_against: [E3]
  - id: H3
    statement: "An operational switch inside the service (chaos mode or a simulated exception) injects the 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E4]
    evidence_against: [E13, E15, E3, E5, E7, E12, E10, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:04:54.059Z (first application line of the only log file; no rotated backups exist)"
    quote: '{"ts": "2026-11-15T13:04:54.059Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:04:55.864Z"
    quote: '{"ts": "2026-11-15T13:04:55.864Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "ba8016b81de2", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.028, "client": "127.0.0.1:52062"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:05:01.021Z (first request to /products/3 in the log; stack trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: '{"ts": "2026-11-15T13:05:01.021Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "2f8d29391ba6", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n … File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:05:01.031Z"
    quote: '{"ts": "2026-11-15T13:05:01.031Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "2f8d29391ba6", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.166, "client": "127.0.0.1:52065"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:05:04.146Z (between the second and the third failing request)"
    quote: '{"ts": "2026-11-15T13:05:04.146Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "f12862010b9d", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.653, "client": "127.0.0.1:52067"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:05:07.301Z (fourth and last user request to /products/3 in the log)"
    quote: '{"ts": "2026-11-15T13:05:07.301Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "2ee7a86077d9", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.751, "client": "127.0.0.1:52071"}'
  - id: E7
    type: metric
    source: "/metrics probe request_id=konan-1794747928-96812 @ 2026-11-15T13:05:28Z (before any investigator probe of a product)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E8
    type: probe
    source: "/products request_id=konan-1794747940-96824"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001639s request_id=konan-1794747940-96824
  - id: E9
    type: probe
    source: "/products/3 request_id=konan-1794747974-96845 (investigator reproduction, software-defect lens)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794747974-96845"}
      -- HTTP 500 in 0.004377s request_id=konan-1794747974-96845
  - id: E10
    type: probe
    source: "/products/4 request_id=konan-1794747978-96857"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001410s request_id=konan-1794747978-96857
  - id: E11
    type: probe
    source: "/products/5 request_id=konan-1794747983-96874"
    quote: |-
      {"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001329s request_id=konan-1794747983-96874
  - id: E12
    type: metric
    source: "/metrics probe request_id=konan-1794748037-96930 @ 2026-11-15T13:07:17Z (after two investigator probes of /products/3 and four investigator probes of other product ids)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 6
      http_exceptions_total{type="ZeroDivisionError"} 6
  - id: E13
    type: metric
    source: "/metrics probe request_id=konan-1794748037-96930 @ 2026-11-15T13:07:17Z (the gauge read the same value at 13:05:28Z, request_id=konan-1794747928-96812)"
    quote: 'faultline_chaos_enabled 0'
  - id: E14
    type: metric
    source: "/metrics probe request_id=konan-1794748037-96930 @ 2026-11-15T13:07:17Z"
    quote: |-
      process_uptime_seconds 143.76428674999624
      process_max_rss_bytes 47955968
  - id: E15
    type: log
    source: "lab/logs/app.log, count of every event value over all 40 lines @ 2026-11-15T13:07:17Z (the 4 lines without an event value are the uvicorn start lines at 13:04:54Z)"
    quote: |-
      2 "event": "order_created"
      27 "event": "request"
      1 "event": "startup"
      6 "event": "unhandled_exception"
  - id: E16
    type: probe
    source: "/orders request_id=konan-1794748037-96925"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-15T13:04:58.968+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T13:05:06.245+00:00"}]
      -- HTTP 200 in 0.001867s request_id=konan-1794748037-96925
  - id: E17
    type: probe
    source: "/health request_id=konan-1794747927-96807"
    quote: |-
      {"status":"ok","uptime_seconds":33.733070916030556}
      -- HTTP 200 in 0.001755s request_id=konan-1794747927-96807
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:04:56.918Z"
    quote: '{"ts": "2026-11-15T13:04:56.918Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "40ac21ff4bad", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.973, "client": "127.0.0.1:52063"}'
gaps:
  - "No telemetry exists from before the process start at 2026-11-15T13:04:54Z: one log file, no rotated backups, all counters start there. The onset 'within the last hour' and the question whether the product-3 page ever worked could not be checked; H2 stays inconclusive."
  - "The surface does not show when or how product 3 reached units_in_stock 0: the order list holds no order for product 3 and the log holds no stock-change event."
  - "The source code is outside the surface. The missing zero guard is read from the one code line that the stack trace quotes, not from the source file."
  - "The log holds no user request to /products/3 after 13:05:07Z. That the failure continues after that time rests on two investigator probes (13:06:14Z, 13:06:37Z)."
  - "Product 4 has a null price and its page returns 200. Whether the null price breaks an order was not checked: POST is outside the probe surface."
  - "The session could not capture its token total; usage.tokens is null."
usage:
  model: claude-fable-5-2
  tokens: 1553185
  wall_clock_seconds: 341
---

# Product 3 page returns HTTP 500 on every request: division by zero on zero stock

## Summary

**Verdict: root cause identified (software defect, unhandled exception), high confidence.**
The page of product 3 ("Unobtainium Ingot") fails on every request with HTTP 500. The
product-detail handler `get_product` computes `turnover_score` as
`units_ordered / units_in_stock` (E3), and product 3 has `units_in_stock` 0 (E8), so the
division raises `ZeroDivisionError` and the request ends as an unhandled exception.
The failure is bound to that one input: 4 of 4 user requests to `/products/3` failed
(E3, E4, E6, E7), two investigator probes reproduced it (E9, E12), and products 1, 2, 4
and 5 return 200 (E2, E5, E18, E10, E11). Orders, the product list and the health
endpoint work (E8, E16, E17) — a green health endpoint beside a failing product page.
The process is alive, memory is flat, and the chaos switch is off (E13, E14).

One point of the complaint is open: the surface holds no telemetry from before the
process start at 13:04:54Z (E1), so the onset time and the statement "no deploys" could
not be checked (H2, inconclusive). That does not change the mechanism: zero stock is a
legitimate state, and the unguarded division is the fault.

## Timeline

All times UTC, 2026-11-15.

- 13:04:54.059 — process start, `faultline 0.1.0 started` (E1). The only startup marker;
  no config, flag or chaos marker follows it (E15).
- 13:04:55.864, 13:04:56.918 — `/products/1` and `/products/2` return 200 (E2, E18).
- 13:05:01.021 — first request to `/products/3` in the log: `ZeroDivisionError` at
  `shop.py` line 64 (E3), answered with 500 at 13:05:01.031 (E4).
- 13:05:02 to 13:05:07 — three more user requests to `/products/3`, all 500; the last at
  13:05:07.301 (E6). `/products/2` returns 200 in between, at 13:05:04.146 (E5).
- 13:05:12 — complaint raised (`startsAt`); 13:05:18 — investigation start.
- 13:05:28 — baseline metrics: 4 responses with status 500 on the product-detail route,
  4 `ZeroDivisionError` exceptions, all from user traffic (E7).
- 13:06:14 — investigator probe of `/products/3` reproduces the 500 (E9); `/products/4`
  and `/products/5` return 200 (E10, E11).
- 13:07:17 — final metrics: 6 and 6, the rise of 2 is the two investigator probes (E12);
  chaos gauge 0 (E13); uptime 143.8 s, memory unchanged (E14).

## Investigation

**Complaint block.** Trigger: manual, `/konan`. Complaint object, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794747912",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of." },
  "startsAt": "2026-11-15T13:05:12Z"
}
```

Investigation start: 2026-11-15T13:05:18Z. Trigger latency: 6 s. The reporter stated no
severity. `KONAN_ADAPTER` was unset, so the surface contract is `docs/lab.md`.

**Baseline.** `/health` 200 with uptime 33.7 s (E17); `/metrics` (E7, E13); the full log,
25 lines at that time, starting at the process start (E1); `/products` (E8). The baseline
already showed the shape: 500 only on `/products/3`, each with a `ZeroDivisionError`.

**Triage (one round, three lenses in parallel, each blind to the others).**

- software-defect: unhandled `ZeroDivisionError` in `get_product`, deterministic for
  product 3, reproduced once (E9); other ids succeed (E10, E11).
- infra-process: no crash, no restart loop, no saturation, chaos off (E13, E14, E15). One
  anomaly: the process started 7 s before the first error and nothing older exists (E1).
- interfaces: no gateway status, no probabilistic failure, no change marker other than
  the startup (E1, E15). Side observation: product 4 has a null price and returns 200.

**Deep-dive.** None. The evidence for H1 was deterministic and complete after triage. The
gap of H2 is not reachable on this surface (no telemetry before 13:04:54Z), so a
deep-dive could not fill it. The orchestrator added two checks: `/orders` (E16) and a
final `/metrics` read (E12, E13, E14).

**Judge (one fresh agent, evidence only).** H1 validated, H2 inconclusive, H3
invalidated. The judge named two holes in the ledger; both are closed here: the third
early 200 is E18, and the lines without an event value are the four uvicorn start lines
(E15 source note).

**Budget.** One triage round and one judge round used; no deep-dive agent.

## Hypotheses

### H1 — unguarded division in `get_product` (software-defect) — validated

The stack names the operation: `"turnover_score": units_ordered / product["units_in_stock"]`
at `shop.py` line 64 (E3), tied to `GET /products/3 -> 500` by request id (E4). Product 3
is the only product with `units_in_stock` 0 (E8). The prediction held on every point:
all six requests to `/products/3` failed (E7, E12), a probe reproduced the same exception
type (E9), ids 1, 2, 4 and 5 succeed (E2, E5, E18, E10, E11), and the exception counter
equals the 500 counter at both reads, 4 = 4 and 6 = 6 (E7, E12). Product 4 has a null
price and still returns 200 (E10), so the price is not the trigger. No evidence against.

### H2 — the process start at 13:04:54Z introduced the failure (infra-process) — inconclusive

For: one startup marker 7 s before the first failure (E1), and uptime values that agree
with that start (E14, E17). Against: the first request to `/products/3` in this process
already failed (E3), so there is no working period inside the visible window, and
nothing older exists. The evidence neither confirms nor refutes a rollout. What would
settle it: one record of `GET /products/3` from a process that ran before 13:04:54Z.
H2 does not compete with H1 on mechanism.

### H3 — an internal degradation switch injects the 500s (infra-process) — invalidated

For: only the 500 status itself (E4). Against: `faultline_chaos_enabled 0` at both reads
(E13); no chaos or simulated-exception event in the whole log (E15); the failure is an
unhandled exception in application code (E3); and the failures are bound to one input,
not spread at a rate (E5, E7, E10, E11, E12).

## Safe next steps

Read-only only.

- Read `get_product` in the faultline source (`shop.py`, line 64) and confirm that no
  guard for zero stock exists.
- Read the inventory history of product 3: when did `units_in_stock` reach 0? That time
  is the likely onset for customers.
- Read the deploy and process-manager records for 13:04:54Z: why did the process start,
  and what ran before? That settles H2.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the status-500 series of
  the product-detail route; list the catalog for other products with zero stock.

## Gaps

- **No telemetry before 13:04:54Z.** One log file, no backups, counters start at the
  process start. The onset "within the last hour" and "no deploys" are unchecked; H2
  stays inconclusive.
- **Stock history.** The surface shows the current stock of product 3 (0), not when or
  how it reached 0. `/orders` holds no order for product 3 (E16).
- **Source code.** Outside the surface. The defect is read from the code line in the
  stack trace (E3).
- **User traffic after 13:05:07Z.** None to `/products/3` in the log. The claim "still
  happening" rests on investigator probes (E9, E12).
- **Null price of product 4.** Its page works (E10). Whether an order for it fails was
  not checked: POST is outside the probe surface.
- **Tokens.** The session could not capture its token total.
