---
konan_journal: 2
investigation:
  id: 2026-11-03-product-page-500s
  trigger: "manual — /konan adapter, source human, fingerprint human-1793688600, labels.alertname human-report, no severity stated by the reporter, startsAt 2026-11-03T06:50:00Z; investigation entered 2026-11-03T06:50:11Z (trigger latency 11s)"
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-03T06:50:11Z
  concluded: 2026-11-03T07:00:03Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product-detail handler divides by the product's stock count, so a catalog row with units_in_stock 0 makes it raise an unhandled ZeroDivisionError and return HTTP 500; product 3 is the one such row, and its product page fails on every request."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "GET /products/{product_id} computes `units_ordered / product[\"units_in_stock\"]` and raises an unhandled ZeroDivisionError when the requested product's units_in_stock is 0. Product 3 (Unobtainium Ingot, units_in_stock 0) is the only such row in the catalog, so that one product page returns HTTP 500 deterministically while every other id returns 200, and an unknown id returns a handled 404."
    incident_class: software-defect
    state: validated
    evidence_for: [E5, E6, E7, E8, E9, E11, E14, E17]
    evidence_against: []
  - id: H2
    statement: "An internal operational degradation switch (chaos mode / error injection) is producing the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E7, E10, E12]
  - id: H3
    statement: "A process-lifecycle or host-resource failure — crash, restart loop, hang, memory growth or latency decay — is behind the reported errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E10, E13]
  - id: H4
    statement: "The failure customers met is broader than one input: a route-wide or intermittent product-page failure affecting many or all product ids."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E8, E9, E10, E11, E14, E15, E16]
  - id: H5
    statement: "The customer-visible errors reported for this morning are this same defect met by real user traffic, as recorded in the target's retained telemetry."
    incident_class: software-defect
    state: inconclusive
    evidence_for: []
    evidence_against: [E3, E4, E12]
latent_findings:
  - statement: "The 500 error body returns the Python exception class name to the client, exposing an internal implementation detail on the public error path."
    evidence: [E6]
  - statement: "The published API schema declares only 200 and 422 for GET /products/{product_id}, while the service also serves 404 and 500 on that route — both are undeclared responses."
    evidence: [E6, E11, E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:49:45.222Z"
    quote: |-
      {"ts": "2026-11-03T06:49:45.222Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
      {"ts": "2026-11-03T06:49:45.222Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [21332]"}
  - id: E2
    type: probe
    source: "/health @ 06:50:14Z, request_id konan-1793688614-21409"
    quote: |-
      {"status":"ok","uptime_seconds":29.14955437509343}
      -- HTTP 200 in 0.001657s request_id=konan-1793688614-21409
  - id: E3
    type: metric
    source: "/metrics @ 06:50:18Z, request_id konan-1793688618-21414 — baseline, before any investigator probe of a product page"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 1
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      faultline_chaos_enabled 0
      process_uptime_seconds 33.58872320805676
      process_max_rss_bytes 46907392
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:49:47.052Z–06:49:51.286Z — every product-page request by non-investigator (unstamped) traffic in the retained window"
    quote: |-
      {"ts": "2026-11-03T06:49:47.052Z", "message": "GET /products/1 -> 200", "request_id": "62aab5c70c3b", "event": "request", "status": 200, "duration_ms": 1.027}
      {"ts": "2026-11-03T06:49:48.112Z", "message": "GET /products/2 -> 200", "request_id": "29fbe9ec2e25", "event": "request", "status": 200, "duration_ms": 0.988}
      {"ts": "2026-11-03T06:49:51.286Z", "message": "GET /products/5 -> 200", "request_id": "9c8d34e224cd", "event": "request", "status": 200, "duration_ms": 0.7}
  - id: E5
    type: probe
    source: "/products @ 06:50:54Z, request_id konan-1793688654-21430"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001598s request_id=konan-1793688654-21430
  - id: E6
    type: probe
    source: "/products/3 @ 06:54:04Z, request_id konan-1793688844-21583"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793688844-21583"}
      -- HTTP 500 in 0.003442s request_id=konan-1793688844-21583
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:54:04.505Z — stack trimmed to its terminal frames; framework frames and the absolute path prefix elided, kept text unaltered"
    quote: |-
      {"ts": "2026-11-03T06:54:04.505Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793688844-21583", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n  ...\n  File \".../src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:51:36.393Z–06:54:04.507Z — every request to the failing page in the file, four of four"
    quote: |-
      {"ts": "2026-11-03T06:51:36.393Z", "message": "GET /products/3 -> 500", "request_id": "konan-1793688696-21466", "status": 500, "duration_ms": 7.45}
      {"ts": "2026-11-03T06:51:48.218Z", "message": "GET /products/3 -> 500", "request_id": "konan-1793688708-21482", "status": 500, "duration_ms": 2.655}
      {"ts": "2026-11-03T06:52:24.688Z", "message": "GET /products/3 -> 500", "request_id": "konan-1793688744-21517", "status": 500, "duration_ms": 2.881}
      {"ts": "2026-11-03T06:54:04.507Z", "message": "GET /products/3 -> 500", "request_id": "konan-1793688844-21583", "status": 500, "duration_ms": 2.637}
  - id: E9
    type: probe
    source: "/products/4 @ 06:51:45Z, request_id konan-1793688705-21477 — the other odd catalog row (price null), same route, non-zero stock"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001612s
  - id: E10
    type: metric
    source: "/metrics @ 06:52:44Z, request_id konan-1793688764-21533"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 3
      http_exceptions_total{type="ZeroDivisionError"} 3
      faultline_chaos_enabled 0
      process_max_rss_bytes 46907392
      (no 502, 503 or 504 series on any path)
  - id: E11
    type: probe
    source: "/products/999 @ 06:54:02Z, request_id konan-1793688842-21576 — unknown id, to separate the 500 from the generic bad-input answer"
    quote: |-
      {"detail":"no such product: 999"}
      -- HTTP 404 in 0.001456s request_id=konan-1793688842-21576
  - id: E12
    type: log
    source: "lab/logs/app.log, whole file (34 lines) plus the directory listing of lab/logs/"
    quote: |-
      Non-`request` event values present in the file: "event": "startup" (06:49:45.222Z), "event": "order_created" (06:49:49.174Z, order_id 1, product_id 1, quantity 1), "event": "unhandled_exception" (4 lines, all exception_type ZeroDivisionError, all with konan-* request ids). No chaos_enabled, chaos_disabled, chaos_failure or simulated_exception line exists. `ls lab/logs/` returns `app.log` alone — no .1-.3 rotation backups, so no line predates 06:49:45.222Z.
  - id: E13
    type: metric
    source: "/metrics and /health, samples 06:50:18Z–06:52:15Z"
    quote: |-
      process_uptime_seconds 33.58872320805676 (06:50:18Z) -> 123.70 (06:51:48Z) -> 147.8735577079933 (/health body) -> 150.09 (06:52:15Z); http_requests_total{method="GET",path="/health",status="200"} 3 -> 4 with no reset
  - id: E14
    type: probe
    source: "/products/1 @ 06:59:10Z, request_id konan-1793689150-21647 — confirms the quotient fields independently of the stack frame"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}
      -- HTTP 200 in 0.001522s request_id=konan-1793689150-21647
  - id: E15
    type: probe
    source: "/products/2 @ 06:59:15Z, request_id konan-1793689155-21652"
    quote: |-
      {"id":2,"name":"Toaster","price":23.0,"units_in_stock":40,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001362s request_id=konan-1793689155-21652
  - id: E16
    type: probe
    source: "/products/5 @ 06:59:16Z, request_id konan-1793689156-21657"
    quote: |-
      {"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001481s request_id=konan-1793689156-21657
  - id: E17
    type: probe
    source: "/products @ 06:59:09Z, request_id konan-1793689149-21642 — catalog re-read at the end of the investigation"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001552s request_id=konan-1793689149-21642
  - id: E18
    type: probe
    source: "/openapi.json @ 06:59:54Z, request_id konan-1793689194-21683 — the declared responses of the failing route"
    quote: |-
      "/products/{product_id}":{"get":{"tags":["shop"],"summary":"Get Product","operationId":"get_product_products__product_id__get","parameters":[{"name":"product_id","in":"path","required":true,"schema":{"type":"integer","title":"Product Id"}}],"responses":{"200":{"description":"Successful Response",...},"422":{"description":"Validation Error",...}}}}
gaps:
  - "The telemetry horizon is shorter than the complaint window. The log file begins at the process start 06:49:45.222Z (E1) and lab/logs/ holds no rotation backups (E12), so almost all of the reported morning has no retained data on this surface. Correlating the complaint with request records needs retention that outlives the process."
  - "No non-investigator request to the failing page exists in the record: all four recorded 500s carry konan-* investigator request ids (E8), and the exception counter had no series at all before the first investigator probe of that page (E3). The defect is live at the origin for any requester, but no individual customer request can be matched to it from this surface. Edge or load-balancer access logs and the support tickets' timestamps are outside the surface contract (docs/lab.md) and were not read."
  - "A restart loop before 06:49:45Z cannot be excluded. The file begins at a process start, and process-scoped counters cannot tell a first clean start from the newest restart in a loop (E1, E13). A supervisor's restart count is outside the surface."
  - "Source code is outside the surface contract, so the general rule 'every zero-stock row fails' rests on one quoted stack frame (E7) plus one observed zero-stock row (E5, E17) and the quotient confirmed on a healthy row (E14). No second zero-stock product existed to test, and a caller-conditional branch inside the handler cannot be excluded formally — a weak alternative that would still be a defect in the same class."
  - "Whether placing an order lowers units_in_stock — and so whether more product pages can enter the failing set with no code change — is untested. The one order_created event (product 1) precedes the first catalog read (E12, E5), so no before/after comparison exists; the data shows units_ordered rose to 1 for that product (E14) but says nothing about the stock side."
  - "The unstamped traffic in the window (E4) cannot be confirmed as real customer browsing. Eight requests in six seconds right after startup fit a smoke pass as well as they fit browsing, so E4 supports 'the other traffic in the window saw 200', not 'customers were fine'."
  - "Front-end, cache and CDN tiers are outside the surface contract and no telemetry from them was available. A cached 200 for the failing page could mask the origin 500 in a browser, and the step from the customer-visible product page to GET /products/{product_id} is an assumption — no front-end evidence was read."
  - "Severity was not stated by the reporter and was not inferred; the complaint carries no ticket count, no timestamps and no product identity, so the reported volume ('several customers') could not be checked against any surface."
usage:
  model: claude-opus-5
  tokens: 2464707
  wall_clock_seconds: 592
---

# Product page for a zero-stock item returns 500 on every request

## Summary

**Root cause identified.** The product-detail route computes a turnover score by dividing
units ordered by units in stock. For a catalog row whose `units_in_stock` is `0` that
division raises an unhandled `ZeroDivisionError`, the request fails with HTTP 500, and the
response body carries `"exception_type":"ZeroDivisionError"` (E6, E7). Product 3
(`Unobtainium Ingot`) is the one row in the catalog at zero stock (E5, E17), so exactly one
product page is broken — and it is broken for every request: four of four attempts returned
500 across two and a half minutes (E8). Every other product id answers 200, including the
other odd row (`price: null`, E9) and the ids real traffic opened earlier (E4), re-checked at
the end of the investigation (E14, E15, E16); an unknown id returns a handled 404 (E11). The
list page `/products` stays healthy, because the failing computation exists only in the
single-item representation.

The complaint's symptom matches this defect exactly, and several customers opening the *same*
product page is consistent with a page that fails for everyone. Two limits on the claim, both
deliberate. First, the failure is **input-determined, not probe-determined**: the divisor comes
from catalog data, not from the caller — other investigator requests on the same route
succeeded (E9, E11, E14), the degradation switch reads `0` (E3, E10), and no injection event
exists (E12). So the page is live-broken for any user who opens it. Second, **no customer
request to that page survives in the retained telemetry**: all four recorded 500s are the
investigator's own (E8), and the log begins 65 seconds before this investigation started (E1,
E12). The reported customer impact is therefore consistent with this cause and uncorroborated
by request records — not disproved. Confidence in the mechanism: high. Confidence that this
is what the customers met: moderate, limited only by retention.

Alternative causes were tested and killed: injected degradation (E3, E7, E10, E12), process
or host failure (E1, E2, E10, E13), and a route-wide or intermittent product-page failure
(E4, E8, E9, E10, E11, E14, E15, E16).

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 06:49:45.222Z | Process start — `faultline 0.1.0 started`, pid 21332. Retained telemetry begins here; nothing earlier survives. | E1, E12 |
| 06:49:47Z–06:49:51Z | Non-investigator traffic opens product pages 1, 2 and 5 — all 200, sub-millisecond. No zero-stock page among them. | E4 |
| 06:49:49.174Z | `order_created` for product 1, quantity 1 — the only business mutation in the window. | E12 |
| 06:50:00Z | Complaint raised by support (`startsAt` of the complaint object). | — |
| 06:50:11Z | Investigation starts. | — |
| 06:50:18Z | Baseline metrics: no exception series at all, degradation switch `0`, uptime 33.6s. | E3 |
| 06:50:54Z | Catalog read: product 3 is the only row with `units_in_stock` 0. | E5 |
| 06:51:36.386Z | First reproduction: `unhandled exception: division by zero` at the turnover-score division; `GET /products/3 -> 500`. | E7, E8 |
| 06:51:45Z–06:54:04Z | Controls and repeats: product 4 (`price: null`) 200; unknown id 404; product 3 500 again, three more times. | E8, E9, E11 |
| 06:59:09Z–06:59:16Z | Currency check at the end: catalog unchanged, products 1, 2 and 5 all 200 now. | E14, E15, E16, E17 |
| 07:00:03Z | Conclusion. No configuration, deploy or flag-change marker appears anywhere in the window. | E12 |

## Investigation

**Baseline.** `/health` 200 with 29s uptime (E2), metrics with no exception series and the
degradation switch off (E3), and the whole log — 16 lines at that moment, no rotation backups
(E12). The business surface was checked, not only health: `/products` served the catalog (E5).
Baseline was clean, which made the horizon itself the first finding.

**Triage — three lenses in parallel, each blind to the others** (software-defect, interfaces,
infra-process). No lens was skipped: 34 seconds of telemetry could not exclude any domain by
evidence. All three converged on the same place from different directions. The software-defect
lens reproduced the failure and named the throwing operation; the interfaces lens established
the failure is deterministic per input, not probabilistic and not gateway-shaped, and found no
change marker; the infra-process lens excluded injection, restart, saturation and latency decay
from counters and uptime. Two lenses independently flagged that every recorded 500 was
investigator traffic.

**Deep-dive — none spawned.** H1's triage evidence was already deterministic and complete
(reproduction, stack frame, divisor identified, same-route controls passing), so it went
straight to the judge. Two cheap blast-radius probes were run inline instead of delegating
them: an unknown id (E11) to separate the 500 from the generic bad-input answer, and one more
reproduction (E6, E8). One of the budgeted three deep-dive agents was spent on nothing, which
is the intended outcome when triage is already decisive.

**Judge — adversarial, evidence-only.** The judge saw the hypothesis list and the verbatim
ledger, never the narrative. It validated H1 while rejecting two words of its original wording
("whenever" and "on every request") as outrunning their citations, and it struck E4 from H1's
support as a mis-citation that invites the wrong reading — real traffic never confirmed the
defect. It confirmed H2, H3 and H4 as invalidated with scope caveats, kept H5 inconclusive,
and separated the two claims that matter: the defect is live at the origin for any requester,
while "only investigator traffic ever triggered it" is true for the retained window and
unknowable before it. Its two reachable "what would settle it" items were then run inline — a
currency re-check of the passing ids and a fresh catalog read (E14, E15, E16, E17), which
closed H4's residual. Its other items (source code, supervisor restart count, edge logs) lie
outside the surface contract and are recorded as gaps. The judge's wording discipline is
carried into this report: the mechanism is claimed, the customer-impact link is stated as
consistency, not as proof.

## Hypotheses

### H1 — zero-stock division in the product-detail handler — **validated**

The handler computes `"turnover_score": units_ordered / product["units_in_stock"]` (E7). At
that expression only a zero denominator yields `ZeroDivisionError`; a wrong type would raise
`TypeError`. Product 3 carries `units_in_stock: 0` (E5), confirmed unchanged at the end of the
investigation (E17). The error envelope and the exception log line share one request id (E6,
E7), and the access line records the status (E8). The same code path returns 200 with
`turnover_score: 0.0` when the denominator is 75 (E9) and `0.008403361344537815` when it is
119 with 1 unit ordered (E14) — the quotient is confirmed from the response surface alone,
independently of the stack frame. Spread is one input on one route: four failures on that id,
zero failures across eight requests to the other four ids and an unknown id (E4, E8, E9, E11,
E14, E15, E16), and no 5xx series on any other path (E10). E4 is deliberately **not** cited in
support: it shows other ids succeeding, and reading it as confirmation of the defect would
claim real traffic met the failure, which it did not.

### H2 — injected degradation — **invalidated**

`faultline_chaos_enabled 0` at 06:50:18Z and 06:52:44Z, before and after three of the four
failures (E3, E10). No `chaos_*` or `simulated_exception` event exists anywhere in the file
(E12) — an absence-of-data argument, so it carries no weight on its own. The weight is
positive: E7 gives a sufficient independent cause in the target's own code, and an injector
would have to fire at exactly that expression, with exactly that exception class, only for the
one row at zero stock, and never for ids 1, 2, 4, 5 or 999.

### H3 — process lifecycle or host resources — **invalidated inside the retained window**

One `startup` event and one process line, no second start and no exit line (E1, E12). Uptime
rises monotonically and every sample puts the start at 06:49:45.2Z; the health counter goes
3 → 4 without resetting, which a restart loop would zero (E13). Peak RSS is byte-identical
across samples two minutes apart, and no gateway statuses exist (E10). Durations run from
0.38 ms to 7.45 ms, so nothing hangs; health answered 200 on every probe (E2). The honest
limit: the file *begins* at a process start, so a crash-restart at 06:49:45Z fits this data
equally well — recorded as a gap, not as support.

### H4 — route-wide or intermittent failure — **invalidated**

Coverage of the catalog is complete: ids 1, 2, 5 at 200 from other traffic (E4) and at 200
again at 06:59 (E14, E15, E16), id 4 at 200 (E9), id 3 at 500 four of four (E8), unknown id at
404 (E11). Exception lines map one-to-one onto requests for the failing id (E12, E8).
"Intermittent" is excluded in the strong sense — 4 of 4 against 0 of 8. The caveat that
survives: "one input" is a property of today's data, not of the code. Any row that reaches zero
stock joins the failing set, and whether orders lower stock is untested (see Gaps).

### H5 — the reported customer impact is corroborated by retained telemetry — **inconclusive**

What the data does establish: the retained window holds no 500 to non-investigator traffic. All
four 500s carry `konan-*` ids (E8), and the exception counter had no series at all at 06:50:18Z,
by which moment all three non-investigator product-page requests had completed — the product-detail
200 count of 3 (E3) matches the three access lines exactly (E4). Log and counters agree. What it
cannot establish: that no customer saw an error this morning. The file starts at 06:49:45.222Z
with no backups (E12), so most of the reported morning has no data. A claim of "no customer
impact" would rest on absence of retention, not on an observation of normal service — so it is
not made here.

## Safe next steps

Read-only, in order of what each would settle:

1. **Pull edge or load-balancer access records for `GET /products/3` covering the morning
   before 06:49:45Z** and match them against the support tickets' timestamps. This is the
   single piece of evidence that would move H5 from inconclusive to settled, in either
   direction.
2. **Ask support for the ticket times and, if captured, which product page each customer
   opened.** Different product pages across tickets would mean this defect is not the whole
   story; the same page would corroborate it.
3. **Re-probe `/products/3` read-only** before and after any change window, as the
   confirmation signal that the state has changed.
4. **Watch `http_exceptions_total{type="ZeroDivisionError"}` and the 500 series on
   `/products/{product_id}`** for growth that does not carry a `konan-*` request id — that
   would be live customer impact, observed rather than inferred.
5. **Re-read `/products`** when stock values move, to see whether another row has reached zero
   and joined the failing set.

Remediation is out of scope for this journal.

## Gaps

The frontmatter list, in short: the telemetry horizon (4m19s) is far shorter than the
complaint window and nothing survives the process start; no non-investigator request to the
failing page exists in the record, and the surfaces that would hold one — edge logs, support
tickets — are outside the surface contract; a restart loop before the window cannot be
excluded from process-scoped counters; the generalization from "this zero-stock row fails" to
"any zero-stock row fails" rests on one stack frame and one observed row, because source code
is out of reach and no second zero-stock product existed to test; whether ordering lowers
stock, and so whether the failing set can grow on its own, is untested; the unstamped traffic
in the window cannot be confirmed as real customers rather than a smoke pass; front-end and
cache tiers are invisible from here, so a cached 200 could hide the origin 500 from a browser;
and the complaint itself carried no severity, count, timestamps or product identity, so the
reported volume could not be checked against any surface.

One quoting note: the stack trace in E7 is trimmed to its terminal frames, with framework
frames and the absolute path prefix elided so the journal stays publishable. Kept text is
unaltered.
