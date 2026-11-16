---
konan_journal: 2
investigation:
  id: 2026-11-15-product-page-500s
  trigger: "manual: /konan adapter, human profile; complaint startsAt 2026-11-15T14:28:09Z, fingerprint human-1794752889; trigger latency 11 s"
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-15T14:28:20Z
  concluded: 2026-11-15T14:33:53Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The 'Internal Server Error' that customers reported on a product page comes from the target's own code: the handler of GET /products/{id} divides by the product's units_in_stock, which is 0 for product 3, raises an unhandled ZeroDivisionError, and returns HTTP 500 on every request for that page."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E4, E5, E6, E7, E8, E9, E10, E11]
    evidence_against: [E2]
  - id: H2
    statement: "An operational degradation switch inside the target (chaos mode) injects the 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E10, E11]
  - id: H3
    statement: "The errors come from the process lifecycle: the process crashed or restarted, and customers saw errors around the restart."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E3]
    evidence_against: [E1, E11, E12]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 on every request (3 of 3): the product-detail handler divides by units_in_stock, which is 0 for product 3, and raises an unhandled ZeroDivisionError. Only investigator probes triggered it. It produces the symptom of the complaint for any visitor of that page."
    evidence: [E5, E6, E7, E8, E9, E10, E11]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id konan-1794752906-1990 (baseline)"
    quote: |-
      {"status":"ok","uptime_seconds":27.832067500334233}
      -- HTTP 200 in 0.002174s request_id=konan-1794752906-1990
  - id: E2
    type: metric
    source: "/metrics, request_id konan-1794752906-1995, read at 2026-11-15T14:28:26Z (baseline); the complete request-counter, exception-counter and chaos sections"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 1
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 0
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:27:58.501Z and 14:27:58.502Z (the first lines of the file; no rotated backup exists; first line trimmed)"
    quote: |-
      {"ts": "2026-11-15T14:27:58.501Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [1901]", [...]}
      {"ts": "2026-11-15T14:27:58.502Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:28:00.329Z, 14:28:01.390Z, 14:28:04.545Z (every end-user request to a product page in the file)"
    quote: |-
      {"ts": "2026-11-15T14:28:00.329Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "a47ce79b3395", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.013, "client": "127.0.0.1:53011"}
      {"ts": "2026-11-15T14:28:01.390Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "d2c4481c6436", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.965, "client": "127.0.0.1:53012"}
      {"ts": "2026-11-15T14:28:04.545Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "d00f65827f96", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.777, "client": "127.0.0.1:53015"}
  - id: E5
    type: probe
    source: "/products/3, request_id konan-1794752952-2039 (triage, software-defect lens)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794752952-2039"}
      -- HTTP 500 in 0.009631s request_id=konan-1794752952-2039
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:29:12.651Z (stack trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: |-
      {"ts": "2026-11-15T14:29:12.651Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794752952-2039", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n [...] File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:29:12.660Z"
    quote: |-
      {"ts": "2026-11-15T14:29:12.660Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794752952-2039", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.822, "client": "127.0.0.1:53039"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:29:16.566Z and 14:29:31.875Z (the two later requests for the same page; with E7, the complete set of 500 access lines in the file)"
    quote: |-
      {"ts": "2026-11-15T14:29:16.566Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794752956-2067", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.664, "client": "127.0.0.1:53043"}
      {"ts": "2026-11-15T14:29:31.875Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794752971-2115", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.995, "client": "127.0.0.1:53050"}
  - id: E9
    type: probe
    source: "/products, request_id konan-1794752948-2027 (triage, software-defect lens)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001563s request_id=konan-1794752948-2027
  - id: E10
    type: probe
    source: "/products/4, request_id konan-1794752952-2044, and /products/1, request_id konan-1794752956-2072 (0.2 s and 0.35 s after a failed /products/3 request)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001641s request_id=konan-1794752952-2044
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}
      -- HTTP 200 in 0.001353s request_id=konan-1794752956-2072
  - id: E11
    type: metric
    source: "/metrics, request_id konan-1794753066-2159, read at 2026-11-15T14:31:06Z (the complete product-page, exception, chaos and uptime series; no other non-2xx series exists in this read)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 3
      http_exceptions_total{type="ZeroDivisionError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 187.95333512499928
  - id: E12
    type: probe
    source: "/health, request_id konan-1794752965-2089 (access line in lab/logs/app.log @ 2026-11-15T14:29:25.061Z)"
    quote: |-
      {"status":"ok","uptime_seconds":86.57129291724414}
      -- HTTP 200 in 0.001376s request_id=konan-1794752965-2089
gaps:
  - "No telemetry exists from before 2026-11-15T14:27:58.501Z: the log starts at a process start, it has no rotated backup, and the counters start at zero. The period that the complaint names ('this morning') could not be read, so the reported errors are neither confirmed nor denied."
  - "No end-user request for /products/3 exists in the readable window (about 3 minutes, 8 end-user requests). The effect of the latent defect on customers is not observed; it is inferred from 3 investigator probes."
  - "Whether an earlier process existed, how it ended, and whether chaos mode was on in it could not be read. Server stdout (lab/server.out) and any process supervisor record are outside the surface contract and were not opened."
  - "The complaint names no product, no count and no time. Nobody from Support was asked in this run."
  - "The rule 'units_in_stock 0 gives a 500' rests on one product: product 3 is the only product with zero stock, so a second zero-stock page could not be probed."
usage:
  model: claude-fable-5-2
  tokens: 1628916
  wall_clock_seconds: 333
---

# Product page "Internal Server Error": no customer failure in telemetry; the page of product 3 fails for every visitor

## Summary

**Verdict: no active incident in the readable telemetry, with one latent finding that
matches the complaint.** Since the process start at 14:27:58Z every end-user request
succeeded (8 of 8, including the product pages 1, 2 and 5 — E2, E4), health is green
(E1) and chaos mode is off (E2, E11). The telemetry does not reach back before that
start, so the errors that Support reports for "this morning" are neither confirmed nor
denied.

The latent finding: `GET /products/3` returns HTTP 500 `internal server error` on every
request (E5, E7, E8). The handler computes `units_ordered / product["units_in_stock"]`
(E6), and product 3 is the only product with `units_in_stock` 0 (E9). The product pages
1, 2, 4 and 5 return 200 (E4, E10). Only investigator probes triggered the defect (all
three 500 lines carry `konan-` request ids — E7, E8, E11), which is why it is a latent
finding and not the verdict. It is still the one mechanism on this target that produces
the reported symptom: a customer who opens the page of product 3 gets this error now.

Confidence: high that the defect exists and is live (judge: validated); none, from
telemetry, that customers hit it (judge: inconclusive). One record from before
14:27:58Z would settle it.

### Complaint block

```json
{
  "source": "human",
  "fingerprint": "human-1794752889",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?" },
  "startsAt": "2026-11-15T14:28:09Z"
}
```

Investigation start: 2026-11-15T14:28:20Z (trigger latency 11 s). No severity was
stated, so none is recorded.

## Timeline

All times UTC, 2026-11-15.

- **14:27:58.501** — process start, `faultline 0.1.0 started`; the only startup marker
  in the log (E3). No configuration, deploy or flag-change marker exists after it.
- **14:27:59 – 14:28:04** — end-user traffic: `/health` ×2, `/products`, `/products/1`,
  `/products/2`, `POST /orders` (201), `GET /orders`, `/products/5` — all 2xx (E2, E4).
- **14:28:09** — complaint raised (adapter stamp).
- **14:28:20** — investigation start.
- **14:28:26** — baseline: health ok, uptime 27.8 s (E1); no non-2xx series, no
  exception series, `faultline_chaos_enabled 0` (E2).
- **14:29:08** — product list: product 3 has `units_in_stock` 0 (E9).
- **14:29:12.651** — first `ZeroDivisionError`, on an investigator probe of
  `/products/3` (E5, E6, E7); `/products/4` returns 200 0.2 s later (E10).
- **14:29:16.566, 14:29:31.875** — the same page fails again on two more investigator
  probes (E8); `/products/1` returns 200 between them (E10).
- **14:29:25** — uptime 86.6 s, consistent with the one start (E12).
- **14:31:06** — final metrics: 3 responses with status 500, 3 `ZeroDivisionError`,
  chaos 0, uptime 188.0 s (E11). No end-user request arrived after 14:28:04.

## Investigation

- **Setup.** `KONAN_ADAPTER` is unset, so the surface contract is `docs/lab.md`.
- **Baseline.** `/health`, `/metrics` and the full log (16 lines at that time). Clean:
  all 2xx, no exceptions, chaos off. The one notable fact: the process started 11 s
  before the complaint, and nothing older is on the surface.
- **Triage.** Three lenses in parallel, blind to each other: software-defect,
  infra-process, interfaces. All three reported the `/products/3` failure; the
  infra-process and interfaces lenses found no anomaly in their own domain (process
  alive, memory flat, latency in milliseconds, plain in-process 500 and no gateway
  status, chaos off, no change marker besides the start).
- **Deep-dive.** Skipped. The triage evidence for the defect was already deterministic
  and complete (3 of 3 failures, stack, the differing input). The evidence that the
  open questions need is from before the process start and is not on the surface, so a
  deep-dive agent had nothing to gather.
- **Judge.** One fresh agent, evidence only. H1: mechanism validated, link to the
  customers' reports inconclusive. H2: invalidated for the readable window. H3:
  inconclusive. For both inconclusive verdicts the judge named the same settling
  evidence: a record from before 14:27:58.501Z.
- **Conclusion.** Evidence exhausted after one round. By the rule of the investigate
  skill, a defect that only investigator probes triggered is a latent finding.
- **Check after the judge.** The log was read to its end (34 lines, last line
  14:31:06.440Z). The `event` values in it are `startup`, `request`, `order_created`
  and `unhandled_exception` only; no chaos event exists.

## Hypotheses

### H1 — the product-detail handler divides by zero stock (software-defect): inconclusive

The hypothesis has two claims, and the judge ruled on each.

- *The mechanism exists and is live: validated.* `/products/3` failed on 3 of 3
  requests with `ZeroDivisionError` (E5, E7, E8); the stack names the division by
  `product["units_in_stock"]` (E6); product 3 is the only product with stock 0 (E9);
  the pages with non-zero stock return 200 for end users and for probes (E4, E10); the
  counters hold exactly 3 responses with status 500 and 3 `ZeroDivisionError`, and no
  other exception type (E11). This claim is the latent finding.
- *It is what customers experienced: inconclusive.* At 14:28:26Z, 17 s after the
  complaint, no non-2xx response and no exception had been counted (E2). Every 500 in
  the log carries a `konan-` request id (E7, E8). No end-user request for `/products/3`
  exists. The period of the complaint is before the first log line.

The state in the machine core is the state of the whole statement: inconclusive.

### H2 — chaos mode injects the errors (infra-process): invalidated

The gauge reads 0 at both metric reads (E2, E11). All three 500s are one exception
type on one page, while other pages answered 200 within 0.35 s (E10, E11). Nothing is
left for a switch to explain in the readable window. Limit: the window starts at
14:27:58Z; the state of the switch in an earlier process is unknown.

### H3 — crash or restart of the process (infra-process): inconclusive

For: the process started 11 s before the complaint (E3). Against: one startup marker
only, and three uptime reads that all point to that one start (E1, E12, E11); the
500s came 74 to 93 s after the start and repeat on demand, so the restart does not
explain them. What stays open is the real claim: whether an earlier process existed
and failed requests. The surface cannot show it.

## Safe next steps

Read-only only.

- Ask Support for the product (id or URL) and the time of the failed page views. A
  product 3 answer supports H1; another product points to a second cause.
- Read a record from before 14:27:58Z, if one exists outside this surface: the server
  stdout, a process supervisor log, or an upstream access log. It settles H1's link to
  the customers and H3.
- Watch `http_requests_total{method="GET",path="/products/{product_id}",status="500"}`
  and `unhandled_exception` log lines for request ids without the `konan-` prefix.
  The first one is the proof of customer impact.
- Read `get_product` in `shop.py` at line 64 for its handling of `units_in_stock` 0.
- Re-read `/products` from time to time: each further product that reaches stock 0 is
  a further page to check.

## Gaps

- **Nothing before the process start.** The log begins at 14:27:58.501Z, it has no
  rotated backup, and the counters began at zero. "This morning" is not readable.
- **No customer request to the failing page.** The readable window holds 8 end-user
  requests in about 3 minutes, none of them for `/products/3`. The customer effect of
  the defect is inferred from investigator probes.
- **The earlier process.** Its existence, its end, and its chaos state are unknown.
  `lab/server.out` and supervisor records are outside the surface contract and were
  not opened.
- **The complaint is thin.** No product, no count, no time; Support was not asked.
- **One zero-stock product.** The rule "stock 0 gives a 500" could be probed on product
  3 only.
