---
konan_journal: 2
investigation:
  id: 2026-11-03-product-page-500s
  trigger: >-
    manual — /konan adapter, human profile; complaint fingerprint
    human-1793704266, startsAt 2026-11-03T11:11:06Z, investigation start
    2026-11-03T11:11:39Z (trigger latency 33s)
  complaint: >-
    Support says several customers see 'Internal Server Error' when opening a
    product page this morning. Can you check what is going on?
  started: 2026-11-03T11:11:39Z
  concluded: 2026-11-03T11:22:33Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: >-
      GET /products/3 deterministically returns HTTP 500: the get_product
      handler computes "turnover_score": units_ordered /
      product["units_in_stock"], and product 3 has units_in_stock = 0, so the
      request raises an unhandled ZeroDivisionError.
    incident_class: software-defect
    state: validated
    evidence_for: [E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: >-
      An internal chaos/degradation switch injects the 500s.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E9]
  - id: H3
    statement: >-
      A process crash, restart, or resource saturation this morning caused the
      customer-facing errors.
    incident_class: infra-process
    state: inconclusive
    evidence_for: []
    evidence_against: [E1, E10, E11, E14]
  - id: H4
    statement: >-
      The customer errors reported by support this morning were instances of
      the H1 defect — customers opened the page of product 3 and received its
      HTTP 500.
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E4, E13]
    evidence_against: [E2]
latent_findings:
  - statement: >-
      GET /products/3 ("Unobtainium Ingot", units_in_stock 0) deterministically
      returns HTTP 500 via an unhandled ZeroDivisionError in get_product
      (shop.py line 64: turnover_score divides units_ordered by
      units_in_stock). Any product whose stock reaches 0 will fail the same
      way. In the available telemetry window, only investigator (konan-*)
      probes triggered it.
    evidence: [E4, E5, E6, E7, E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:10:45.963Z"
    quote: >-
      {"ts": "2026-11-03T11:10:45.963Z", "level": "INFO", "logger":
      "faultline.app", "message": "faultline 0.1.0 started", "event":
      "startup", "version": "0.1.0"}
  - id: E2
    type: metric
    source: "/metrics @ 2026-11-03T11:11:53Z, request_id=konan-1793704313-30601"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 1
  - id: E3
    type: metric
    source: "/metrics @ 2026-11-03T11:14:24Z, request_id=konan-1793704464-30660"
    quote: faultline_chaos_enabled 0
  - id: E4
    type: probe
    source: "/products, request_id=konan-1793704561-30726"
    quote: >-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium
      Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery
      Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber
      Duck","price":6.25,"units_in_stock":500}]
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:14:15.947Z"
    quote: >-
      {"ts": "2026-11-03T11:14:15.947Z", "level": "ERROR", "logger":
      "faultline.request", "message": "unhandled exception: division by zero",
      "request_id": "konan-1793704455-30650", "event": "unhandled_exception",
      "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent
      call last): … File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\",
      line 64, in get_product\n    \"turnover_score\": units_ordered /
      product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:14:15.955Z"
    quote: >-
      {"ts": "2026-11-03T11:14:15.955Z", "level": "INFO", "logger":
      "faultline.request", "message": "GET /products/3 -> 500", "request_id":
      "konan-1793704455-30650", "event": "request", "method": "GET", "path":
      "/products/3", "status": 500, "duration_ms": 8.137, "client":
      "127.0.0.1:50131"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:14:25.537Z"
    quote: >-
      {"ts": "2026-11-03T11:14:25.537Z", "level": "INFO", "logger":
      "faultline.request", "message": "GET /products/3 -> 500", "request_id":
      "konan-1793704465-30665", "event": "request", "method": "GET", "path":
      "/products/3", "status": 500, "duration_ms": 2.56, "client":
      "127.0.0.1:50136"}
  - id: E8
    type: probe
    source: "/products/4, request_id=konan-1793704458-30655"
    quote: "-- HTTP 200 in 0.001577s request_id=konan-1793704458-30655"
  - id: E9
    type: metric
    source: "/metrics @ 2026-11-03T11:14:32Z, request_id=konan-1793704472-30677"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_exceptions_total{type="ZeroDivisionError"} 2
  - id: E10
    type: probe
    source: "/health, request_id=konan-1793704484-30682"
    quote: '{"status":"ok","uptime_seconds":238.47393566719256}'
  - id: E11
    type: metric
    source: >-
      /metrics @ 2026-11-03T11:11:53Z (konan-1793704313-30601) and @
      2026-11-03T11:14:24Z (konan-1793704464-30660)
    quote: process_max_rss_bytes 47513600
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:10:47.779Z"
    quote: >-
      {"ts": "2026-11-03T11:10:47.779Z", "level": "INFO", "logger":
      "faultline.request", "message": "GET /products/1 -> 200", "request_id":
      "008d64237b8e", "event": "request", "method": "GET", "path":
      "/products/1", "status": 200, "duration_ms": 0.814, "client":
      "127.0.0.1:50093"}
  - id: E13
    type: probe
    source: "/orders, request_id=konan-1793704852-30776"
    quote: >-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-03T11:10:49.892+00:00"}]
  - id: E14
    type: log
    source: "lab/server.out @ 2026-11-03T11:10:45.962Z"
    quote: >-
      {"ts": "2026-11-03T11:10:45.962Z", "level": "INFO", "logger":
      "uvicorn.error", "message": "Started server process [30504]",
      "color_message": "Started server process [\u001b[36m%d\u001b[0m]"}
gaps:
  - >-
    No telemetry exists before 2026-11-03T11:10:45Z: lab/logs/app.log is the
    only log file, no rotated backups exist, and the metrics counters start at
    process start. The period of the reported customer errors ("this morning")
    is unobservable on this surface.
  - >-
    No unstamped (non-investigator) request appears in the log after
    2026-11-03T11:10:52Z. The absence of customer errors inside the window
    shows absent customer traffic, not confirmed customer-facing health.
  - >-
    Customer-side records (support tickets with the opened URL or product id
    and timestamps) are outside the surface contract. One record that names
    /products/3 would settle H4; one in-window timestamp on a different path
    would reopen the surface question.
  - >-
    OS or supervisor process history before 2026-11-03T11:10:45Z is outside
    the surface contract. It would settle H3 (first start versus restart).
  - >-
    The interfaces lens was not spawned. Exclusion evidence: the surface
    contract (docs/lab.md, "Known gaps") declares no third-party dependency,
    no gateway, no distributed topology, and the complete log contains no 5xx
    beyond E6/E7 and no configuration-change markers. The residual blind spot
    is accepted and recorded here.
usage:
  model: claude-fable-5
  tokens: 1556970
  wall_clock_seconds: 654
---

# Product page HTTP 500 — deterministic zero-stock defect on /products/3; reported customer impact not observable

## Summary

Verdict: **no active incident is observable in the available telemetry** — and a
real, deterministic defect rides along as a latent finding. `GET /products/3`
("Unobtainium Ingot") always returns HTTP 500: the `get_product` handler divides
`units_ordered` by `units_in_stock` (shop.py line 64), and product 3 is the only
product with `units_in_stock = 0` (E4, E5). The failure reproduces on demand
(E6, E7) and matches the complaint symptom exactly — "Internal Server Error" on
a product page. Attribution to the reported customers stays unverified: the
telemetry window begins at 11:10:45Z, 21 seconds before the complaint
`startsAt`, and every observed 500 carries a `konan-*` investigator request id.
No customer traffic at all appears after 11:10:52Z, so the quiet log proves
absent traffic, not health. Chaos injection and process-level causes are
excluded inside the window (E3, E10, E11). Confidence: high on the defect
mechanism; the link to the reported impact needs one customer-side record.

## Timeline

- 2026-11-03T11:10:45.962Z — single server process start, PID 30504 (E14);
  `faultline 0.1.0 started` (E1). No telemetry exists before this point.
- 11:10:46–11:10:52Z — eight unstamped local requests, all 200/201, including
  `GET /products/1 -> 200` (E12), products 2 and 5, one order for product 1
  (E13). No unstamped 5xx at any time.
- 11:11:06Z — complaint `startsAt` (support report via /konan).
- 11:11:39Z — investigation start; baseline health 200, uptime 62.8s.
- 11:11:53Z — baseline metrics: only 200/201 series, no exceptions (E2);
  chaos gauge 0.
- 11:14:15.947Z — first investigator probe of `/products/3`: unhandled
  `ZeroDivisionError` (E5) and `GET /products/3 -> 500` (E6).
- 11:14:25.537Z — second probe, same result (E7) — deterministic.
- 11:14:24–11:14:44Z — chaos gauge still 0 between the two errors (E3);
  uptime continuous at 238.5s after both exceptions (E10); RSS flat (E11).
- 11:16:01Z — catalog read: product 3 is the only zero-stock product (E4).
- 11:22:33Z — conclusion.

## Investigation

Baseline (11:11:39–11:12:30Z): health 200 with uptime 63s, metrics with zero
exceptions and chaos gauge 0, complete log read (16 lines, all 200/201). Two
triage lenses ran in parallel, blind to each other: software-defect and
infra-process. The interfaces lens was excluded with evidence (see Gaps). The
software-defect lens found and reproduced the `/products/3` failure and named
the throwing operation from the stack. The infra-process lens confirmed one
single process start, continuous uptime across both exceptions, flat memory,
millisecond latency, and a chaos switch off for the whole window. Both
hypotheses carried deterministic, complete evidence, so deep-dive agents were
skipped. A fresh adversarial judge received only the hypothesis list with
verbatim evidence: H1 validated (mechanism), H2 invalidated, H3 inconclusive,
and the complaint-attribution clause split out as inconclusive (H4). Round 2
closed the two in-surface items the judge named: `lab/server.out` shows one
process start and no restarts (E14), and `/orders` shows no order ever drained
product 3's stock (E13).

## Hypotheses

### H1 — zero-stock division defect on GET /products/3 (validated)

The handler computes `"turnover_score": units_ordered /
product["units_in_stock"]` and product 3 has stock 0. The stack trace names the
exact expression (E5). Two probes failed identically (E6, E7); the counters
agree exactly — two 500s on the route, two ZeroDivisionError exceptions, no
other 5xx series (E9). Controls hold: product 4 with `price: null` returns 200
(E8), products 1, 2, 5 return 200, and the catalog shows product 3 as the only
zero-stock product (E4). Deterministic per-input failure is the code-defect
signature.

### H2 — chaos/degradation switch (invalidated)

The chaos gauge reads 0 in a scrape between the two errors (E3), the log holds
zero chaos or simulated-exception events, and the errors carry a real stack at
a real source line with a real zero denominator (E9 types them). Nothing
supports injection.

### H3 — crash, restart, or saturation (inconclusive)

Inside the window: refuted. One startup event (E1), one server process (E14),
uptime continuous across both exceptions (E10), flat RSS and ~2.3 ms mean route
latency (E11). The hypothesis survives only before 11:10:45Z, where no
telemetry exists; a first start and a restart that replaced older logs look
identical from here.

### H4 — the reported customers hit the H1 defect (inconclusive)

For: the zero-stock state predates all visible activity — no visible order
touched product 3 (E13), and the state stands now (E4) — so the defect was live
for any customer who opened product 3's page this morning, and the symptom
matches the complaint exactly. Against: the baseline counters show no 5xx
before my probes (E2), and no customer-side record is reachable on this
surface. The complaint text itself is untrusted data, not evidence. One support
ticket with the opened URL would settle this.

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Ask support for one failing customer record: the product page URL (or product
  id) and a timestamp. A record that names product 3 settles H4; an in-window
  timestamp on another path reopens the surface question.
- Check any front-end, proxy, or browser-side logs outside this surface for the
  morning window, where they exist.
- Read-only review of the `get_product` turnover computation in the target's
  repo (named by the stack at shop.py line 64) by its owners, and of every
  code path that divides by a stock count.
- Watch `http_requests_total{path="/products/{product_id}",status="500"}` for
  growth from non-investigator traffic; any unstamped 500 confirms live impact.

## Gaps

The frontmatter list, elaborated: the telemetry blind zone before 11:10:45Z
covers exactly the period the complaint names, and nothing on this surface can
recover it (single log file, no rotated backups, counters reset at start). The
window after the complaint contains no customer traffic at all, so it cannot
confirm or refute ongoing impact. Customer-side records and OS process history
would settle H4 and H3 respectively; both are outside the surface contract.
The interfaces lens was excluded on cited evidence rather than spawned; the
exclusion is recorded as an accepted blind spot.
