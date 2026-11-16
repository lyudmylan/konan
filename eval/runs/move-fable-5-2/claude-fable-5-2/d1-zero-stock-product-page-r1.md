---
konan_journal: 2
investigation:
  id: 2026-11-15-product-3-page-500s
  trigger: |-
    manual — /konan human report. Complaint object: {"source":"human","fingerprint":"human-1794747526","labels":{"alertname":"human-report"},"annotations":{"summary":"Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."},"startsAt":"2026-11-15T12:58:46Z"}. Investigation start: 2026-11-15T12:58:58Z (trigger latency 12 s).
  complaint: |-
    Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of.
  started: 2026-11-15T12:58:58Z
  concluded: 2026-11-15T13:03:01Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The handler of GET /products/{id} divides units_ordered by the product's units_in_stock to compute turnover_score; product 3 has units_in_stock 0, so every request for its page raises an unhandled ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The handler of GET /products/{id} divides units_ordered by units_in_stock to compute turnover_score; for a product with units_in_stock 0 (product 3) it raises an unhandled ZeroDivisionError and the request returns HTTP 500."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14]
    evidence_against: []
  - id: H2
    statement: "A process lifecycle fault (a crash, a restart loop, or a hang) causes the 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1]
    evidence_against: [E3, E7, E12, E13, E14, E15, E16, E18]
  - id: H3
    statement: "An internal degradation switch (chaos mode) injects the 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E7, E13, E14, E16, E17, E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:58:27.811Z"
    quote: |-
      {"ts": "2026-11-15T12:58:27.811Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:58:34.766Z, request_id d13112fcb7b3; the stack is trimmed to its last frame, with the checkout prefix of its file path redacted"
    quote: |-
      {"ts": "2026-11-15T12:58:34.766Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "d13112fcb7b3", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n ... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:58:34.776Z, request_id d13112fcb7b3 (user traffic, first failure)"
    quote: |-
      {"ts": "2026-11-15T12:58:34.776Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "d13112fcb7b3", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.776, "client": "127.0.0.1:51993"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:58:35.833Z, request_id e9c7030d97dd (user traffic)"
    quote: |-
      {"ts": "2026-11-15T12:58:35.833Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "e9c7030d97dd", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.811, "client": "127.0.0.1:51994"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:58:38.944Z, request_id fcd344f80b36 (user traffic)"
    quote: |-
      {"ts": "2026-11-15T12:58:38.944Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "fcd344f80b36", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.842, "client": "127.0.0.1:51996"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:58:41.057Z, request_id 056c8c4f161e (user traffic, last user request in the log)"
    quote: |-
      {"ts": "2026-11-15T12:58:41.057Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "056c8c4f161e", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 6.16, "client": "127.0.0.1:51999"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:58:37.886Z, request_id 98bcfb2ccddd (user traffic, same route, between the second and the third failure)"
    quote: |-
      {"ts": "2026-11-15T12:58:37.886Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "98bcfb2ccddd", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.771, "client": "127.0.0.1:51995"}
  - id: E8
    type: probe
    source: "/products, request_id konan-1794747569-96488"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001416s request_id=konan-1794747569-96488
  - id: E9
    type: probe
    source: "/products/3, request_id konan-1794747675-96596 (investigator reproduction)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794747675-96596"}
      -- HTTP 500 in 0.004386s request_id=konan-1794747675-96596
  - id: E10
    type: probe
    source: "/products/1, request_id konan-1794747675-96601"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":118,"units_ordered":2,"turnover_score":0.01694915254237288}
      -- HTTP 200 in 0.001379s request_id=konan-1794747675-96601
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:59:55.446Z, request_id konan-1794747595-96511 (investigator probe by the software-defect lens)"
    quote: |-
      {"ts": "2026-11-15T12:59:55.446Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794747595-96511", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.302, "client": "127.0.0.1:52025"}
  - id: E12
    type: metric
    source: "/metrics, request_id konan-1794747539-96473 (first read, 2026-11-15T12:58:59Z; four user requests to /products/3 so far, no investigator request)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
      process_uptime_seconds 31.55242562480271
  - id: E13
    type: metric
    source: "/metrics, request_id konan-1794747678-96606 (last read, 2026-11-15T13:01:18Z; four user and two investigator requests to /products/3 so far; all http_requests_total and http_exceptions_total series present)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 6
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_exceptions_total{type="ZeroDivisionError"} 6
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:00:00.600Z, request_id konan-1794747600-96518 (investigator probe by the software-defect lens, another product on the same route)"
    quote: |-
      {"ts": "2026-11-15T13:00:00.600Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794747600-96518", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.453, "client": "127.0.0.1:52026"}
  - id: E15
    type: probe
    source: "/health, request_id konan-1794747538-96468"
    quote: |-
      {"status":"ok","uptime_seconds":30.967969833873212}
      -- HTTP 200 in 0.002300s request_id=konan-1794747538-96468
  - id: E16
    type: metric
    source: "/metrics, request_id konan-1794747678-96606 (last read, 2026-11-15T13:01:18Z)"
    quote: |-
      faultline_chaos_enabled 0
      process_uptime_seconds 171.1480288747698
      process_max_rss_bytes 48447488
  - id: E17
    type: metric
    source: "/metrics, request_id konan-1794747539-96473 (first read, 2026-11-15T12:58:59Z)"
    quote: |-
      faultline_chaos_enabled 0
      process_max_rss_bytes 48447488
  - id: E18
    type: log
    source: "lab/logs/app.log, all 39 lines at 2026-11-15T13:03:01Z (no rotated backups): the count of each `event` value, as printed by grep, sort and uniq"
    quote: |-
      2 "event": "order_created"
      26 "event": "request"
      1 "event": "startup"
      6 "event": "unhandled_exception"
gaps:
  - "Onset: the telemetry starts at the process start, 2026-11-15T12:58:27.811Z (E1), and the log has no rotated backups. The first request to /products/3 in the log already failed (E3). The surface cannot show whether the page worked before, or when units_in_stock of product 3 became 0, so 'started within the last hour' is not confirmed and not refuted."
  - "The process start 7 s before the first failure (E1, E3): the surface cannot show whether it was a restart, a deploy, or a first start, or which build ran before it. The complaint says no deploy is known; the telemetry cannot check that."
  - "'Still happening' for users: the last user request in the log is at 12:58:41.057Z (E6). After it, only the investigator's probes show that the failure persists (E9, E11)."
  - "The interfaces lens was not spawned. The baseline excluded its domain: only statuses 200, 201 and 500 exist (E13), every 500 carries an in-process exception (E2, E13), and the log holds no change marker other than the one startup (E18)."
  - "Product 4 has a null price (E8) and its page returns 200 (E14). Whether an order for product 4 fails was not checked: POST is outside the probe surface."
  - "The source code of the target is outside the surface contract. The throwing line is known from the stack trace only (E2)."
usage:
  model: claude-fable-5-2
  tokens: 1544956
  wall_clock_seconds: 243
---

# Product 3 page returns HTTP 500: division by zero on zero stock

## Summary

**Root cause identified, class software-defect, cause unhandled-exception.** The handler
of `GET /products/{id}` computes `turnover_score` as `units_ordered / units_in_stock`
(`shop.py` line 64, `get_product`, E2). Product 3 ("Unobtainium Ingot") has
`units_in_stock` 0 (E8), so each request for its page raises an unhandled
`ZeroDivisionError` and returns HTTP 500 with the body `internal server error` (E9).

Impact: four of four user requests to `/products/3` failed between 12:58:34Z and
12:58:41Z (E3–E6). No other route and no other product failed: products 1, 2 and 4
answer 200, and `/health`, `/products` and `POST /orders` have no 5xx (E7, E10, E13,
E14). The failure is deterministic per input, so a page refresh does not help; this
matches the complaint. Two more 500s on `/products/3` are the investigator's own stamped
probes (E9, E11) and are not user impact.

Confidence: high for the mechanism. The exception, the throwing line, the zero stock
value, the reproduction and the counters agree, and the judge validated the hypothesis.
Not established: when the failure began, and whether the process start 7 s before the
first failure was a restart or a deploy (see Gaps).

## Timeline

All times are UTC on 2026-11-15.

- 12:58:27.811 — the process starts, `faultline 0.1.0 started` (E1). This is the only
  startup event in the log (E18), and it is the earliest telemetry available.
- 12:58:34.766 — first unhandled `ZeroDivisionError`, request `d13112fcb7b3` (E2);
  12:58:34.776 — `GET /products/3 -> 500` for the same request (E3).
- 12:58:35.833 — second user failure on `/products/3` (E4).
- 12:58:37.886 — a user request to `/products/2` returns 200 between the failures (E7).
- 12:58:38.944 and 12:58:41.057 — third and fourth user failures on `/products/3`
  (E5, E6). The fourth is the last user request in the log.
- 12:58:46 — the complaint arrives (`startsAt`); 12:58:58 — the investigation starts.
- 12:58:58 to 12:58:59 — baseline: `/health` 200 with uptime 30.97 s (E15); metrics show
  four 500s and four `ZeroDivisionError`, chaos gauge 0 (E12, E17).
- 12:59:29 — `/products` shows product 3 with `units_in_stock` 0 (E8).
- 12:59:55.446 — investigator probe of `/products/3` returns 500 (E11).
- 13:00:00.600 — investigator probe of `/products/4` returns 200 (E14).
- 13:01:15 — investigator reproduction: `/products/3` returns 500 with
  `ZeroDivisionError` (E9); `/products/1` returns 200 with a `turnover_score` (E10).
- 13:01:18 — metrics: six 500s and six `ZeroDivisionError`, all on
  `/products/{product_id}`; uptime 171.15 s, chaos gauge 0 (E13, E16).

No configuration, flag or deploy marker exists in the log apart from the one startup
event (E18).

## Investigation

- **Setup.** `KONAN_ADAPTER` was unset, so the surface contract is `docs/lab.md`. Budget:
  one triage round, at most three deep-dive agents per round, at most two rounds.
- **Baseline.** `/health`, `/metrics`, `/products`, and the whole of `lab/logs/app.log`
  (25 lines at capture). Health was green while one product page failed: the
  healthy-monitoring shape. All 500s sat on `/products/3`, each with an
  `unhandled_exception` line.
- **Triage.** Two lenses in parallel, each blind to the other: software-defect and
  infra-process. The interfaces lens was not spawned; the baseline excluded its domain
  (see Gaps).
  - Software-defect: one deterministic, data-dependent defect on `/products/3`; it
    reproduced the failure once and probed products 1, 4 and 5 (all 200).
  - Infra-process: no process or resource anomaly. One startup, uptime only grows, RSS
    flat, chaos gauge 0, latency normal. It noted the process start 7 s before the first
    failure and the absence of earlier telemetry.
- **Deep-dive.** Skipped. The triage evidence for H1 was already deterministic and
  complete, including a reproduction. The orchestrator ran one more reproduction and one
  comparison probe to quote the responses verbatim (E9, E10).
- **Judge.** One fresh agent with the hypothesis list and the verbatim evidence only, no
  tools. Verdicts: H1 validated, H2 invalidated, H3 invalidated. For H2 and H3 it named
  one settling check each: the count of `startup` events and the count of chaos events in
  the log. Both checks ran (E18): one startup, zero chaos events.
- **Conclusion.** After one round: a validated hypothesis whose prediction a probe
  confirmed.

## Hypotheses

### H1 — division by zero on a product with zero stock (validated)

The stack trace names the operation: `"turnover_score": units_ordered /
product["units_in_stock"]` in `get_product`, `shop.py` line 64 (E2). The request id of
that trace is the request that returned 500 on `/products/3` (E3). Product 3 is the only
product with `units_in_stock` 0 (E8). A healthy response shows the same formula at work:
product 1 has `units_ordered` 2, `units_in_stock` 118 and `turnover_score` 0.0169… (E10).

The prediction held. Every request to `/products/3` failed: four from users (E3–E6) and
two from the investigator (E9, E11). Requests for products 1, 2 and 4 succeeded (E10, E7,
E14). The 500 counter and the `ZeroDivisionError` counter moved together, from 4 to 6,
and no other exception type or failing route exists (E12, E13). No evidence against was
found.

### H2 — a process lifecycle fault (invalidated)

For: the process started 7 s before the first failure (E1, E3). Against: the uptime
values 30.97 s, 31.55 s and 171.15 s all point to that single start (E15, E12, E16), and
the log holds exactly one startup event (E18), so no restart happened during the
failures. Counters grew without a reset (E12, E13), health answered 200 (E15), and the
failures completed in milliseconds with an application exception on one product only (E3,
E7, E14). A crash, a restart loop or a hang predicts none of this. Whether the start
itself brought in the defect is a different question, and the surface cannot answer it
(see Gaps).

### H3 — an injected degradation switch (invalidated)

No evidence for. Against: `faultline_chaos_enabled` was 0 at the first and the last read
(E17, E16), and the log holds no chaos event of any kind (E18). Every 500 is a
`ZeroDivisionError` at the division line (E2, E13). The failures are deterministic and
limited to one input, while the same route serves other products (E7, E14); injected
degradation predicts a spread across routes and inputs.

## Safe next steps

Read-only suggestions only.

- Read `get_product` in `shop.py` at line 64 in the target's repository and confirm that
  the division has no guard for a zero `units_in_stock`.
- Read the stock history of product 3 and find when `units_in_stock` reached 0. That
  dates the onset, which this telemetry cannot.
- List the catalog for other products with `units_in_stock` 0, now or soon; each one
  will fail the same way.
- Find out who or what started the process at 12:58:27Z, and compare the running build
  with the previous one.
- Read the order path for a product with a null price (product 4, E8) in the code.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the 500 counter of
  `/products/{product_id}` for user traffic after 12:58:41Z.

## Gaps

- **Onset.** The telemetry starts at the process start (E1), and no rotated log exists.
  The first request to `/products/3` in the log already failed (E3). The surface cannot
  show whether the page ever worked or when the stock of product 3 became 0. The
  reporter's "started within the last hour" is not confirmed and not refuted.
- **The process start.** A start 7 s before the first failure is on the timeline (E1,
  E3). The surface cannot show whether it was a restart, a deploy or a first start. The
  reporter knows of no deploy; the telemetry cannot check that.
- **"Still happening" for users.** No user request exists in the log after 12:58:41.057Z
  (E6). The persistence of the failure rests on the investigator's probes (E9, E11) and
  on its deterministic shape.
- **Interfaces lens not spawned.** The baseline excluded its domain with evidence: only
  statuses 200, 201 and 500 exist (E13), every 500 carries an in-process exception (E2,
  E13), and the only change marker in the log is the one startup (E18). This is an
  accepted blind spot.
- **Product 4, null price.** The page returns 200 (E14). Whether an order for it fails
  was not checked, because POST is outside the probe surface. It is an observation, not
  a finding.
- **Source code.** The target's code is outside the surface contract. The throwing line
  is known from the stack trace only (E2).
