---
konan_journal: 1
investigation:
  id: 2026-08-19-product-page-500-report
  trigger: >-
    manual — /konan human adapter. Complaint object: source human,
    fingerprint human-1787140822, labels.alertname human-report (no severity
    stated by the reporter), startsAt 2026-08-19T12:00:22Z. Investigation
    entered at 2026-08-19T12:00:29Z; trigger latency startsAt -> start = 7s.
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-19T12:00:29Z
  concluded: 2026-08-19T12:06:33Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: >-
      GET /products/{product_id} computes turnover_score as
      units_ordered / units_in_stock with no effective zero guard; product 3
      carries units_in_stock 0, so its detail page raises ZeroDivisionError and
      returns HTTP 500 deterministically, while every other product id returns 200.
    incident_class: software-defect
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E8, E9, E10]
    evidence_against: []
  - id: H2
    statement: >-
      The 500s originate from injected chaos or an operator-set fault rate
      rather than from a code defect.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E7, E10, E5]
  - id: H3
    statement: >-
      A process-level fault — crash, restart loop, memory saturation or worker
      starvation — produced the errors.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E1, E6, E10]
  - id: H4
    statement: >-
      The null price on product 4 is the trigger for the product-page 500s.
    incident_class: data-db
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E3]
  - id: H5
    statement: >-
      Real (non-investigator) customers reached the H1 failure path and received
      HTTP 500 — i.e. the complaint describes a customer-facing incident that is
      observable in this target's telemetry.
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E14, E2]
latent_findings:
  - statement: >-
      Live, reachable, deterministic defect: any user who opens the detail page
      of a product with units_in_stock 0 (currently product 3, "Unobtainium
      Ingot", which is listed in the public catalogue) receives HTTP 500. Five
      out of five reproductions; only investigator probes have triggered it so far.
    evidence: [E3, E4, E5, E6, E7, E8, E9, E10]
  - statement: >-
      Contract drift: /openapi.json declares only 200 and 422 for
      /products/{product_id}, while the live service serves 404 and 500 on that
      route, and the 200 body schema is additionalProperties true — so neither
      the undeclared 500 nor the nullable price field is catchable by a consumer.
    evidence: [E15, E4, E3]
evidence:
  - id: E1
    type: probe
    source: "/health — request_id konan-1787140845-57057"
    quote: |-
      {"status":"ok","uptime_seconds":34.76684316713363}
      -- HTTP 200 in 0.003259s request_id=konan-1787140845-57057
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:00:10.746Z"
    quote: |-
      {"ts": "2026-08-19T12:00:10.746Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E3
    type: probe
    source: "/products — request_id konan-1787140870-57148"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.002841s request_id=konan-1787140870-57148
  - id: E4
    type: probe
    source: "/products/3 — request_id konan-1787140929-57298"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787140929-57298"}
      -- HTTP 500 in 0.011239s request_id=konan-1787140929-57298
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:02:09.308Z (stack trimmed to its tail; kept fields unaltered)"
    quote: |-
      {"ts": "2026-08-19T12:02:09.308Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787140929-57298", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n ... \n  File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:02:09.318Z"
    quote: |-
      {"ts": "2026-08-19T12:02:09.318Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787140929-57298", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.253, "client": "127.0.0.1:60214"}
  - id: E7
    type: log
    source: "lab/logs/app.log — five /products/3 500s, distinct request ids, 12:02:09.318Z / 12:02:20.155Z / 12:02:29.440Z / 12:02:31.288Z / 12:02:33.457Z, each preceded by an identical ZeroDivisionError unhandled_exception line at shop.py:64; last one quoted"
    quote: |-
      {"ts": "2026-08-19T12:02:33.457Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787140953-57369", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.506, "client": "127.0.0.1:60222"}
  - id: E8
    type: probe
    source: "/products/4 — the null-price row — request_id konan-1787140958-57381"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001410s request_id=konan-1787140958-57381
  - id: E9
    type: probe
    source: "/products/1 — request_id konan-1787140956-57375"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}
      -- HTTP 200 in 0.001329s request_id=konan-1787140956-57375
  - id: E10
    type: metric
    source: "/metrics"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7
      http_requests_total{method="GET",path="/products/{product_id}",status="404"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 5
      http_exceptions_total{type="ZeroDivisionError"} 5
  - id: E11
    type: metric
    source: "/metrics, plus grep over lab/logs/app.log"
    quote: |-
      faultline_chaos_enabled 0
      (grep -c 'chaos' lab/logs/app.log = 0 — no chaos_enabled / chaos_disabled / chaos_failure line anywhere in the log)
  - id: E12
    type: metric
    source: "/metrics read twice — 2026-08-19T12:00:49Z and 2026-08-19T12:02:17Z"
    quote: |-
      process_uptime_seconds 38.7070573749952   (12:00:49Z)
      process_uptime_seconds 126.82376037514769 (12:02:17Z)
      process_max_rss_bytes 47104000            (identical at both reads)
  - id: E13
    type: log
    source: "lab/logs/app.log — the complete set of non-investigator (unstamped) requests, 12:00:11.472Z–12:00:16.812Z; last one quoted"
    quote: |-
      GET /health -> 200, GET /health -> 200, GET /products -> 200, GET /products/1 -> 200, GET /products/2 -> 200, POST /orders -> 201, GET /orders -> 200, GET /products/5 -> 200 — all 200/201, max duration_ms 16.298, none requesting /products/3. Example: {"ts": "2026-08-19T12:00:16.812Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "241cba95ce88", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.969, "client": "127.0.0.1:60158"}
  - id: E14
    type: log
    source: "lab/logs/ directory listing and request-id census over lab/logs/app.log"
    quote: |-
      ls lab/logs/ -> app.log only (no rotated .1–.3 backups); first line of app.log is the 12:00:10.746Z startup marker. Every one of the five recorded 500s carries a konan-* request id (konan-1787140929-57298, konan-1787140940-57328, konan-1787140949-57355, konan-1787140951-57363, konan-1787140953-57369) — investigator traffic.
  - id: E15
    type: probe
    source: "/openapi.json, and /products/999"
    quote: |-
      "/products/{product_id}": responses declared: {"200": {...}, "422": {...}} — no 404, no 500; 200 body schema {"type":"object","additionalProperties":true}. Live: /products/999 -> {"detail":"no such product: 999"} -- HTTP 404 in 0.001184s
gaps:
  - >-
    No telemetry survives from the complaint's window. The process started at
    2026-08-19T12:00:10.746Z (E2) and lab/logs/ holds no rotated backups (E14),
    so nothing this target recorded earlier "this morning" is readable; /metrics
    counters are process-scoped and reset at the same boundary.
  - >-
    No independent vantage point exists on this surface to corroborate the
    reported customer errors — no edge/load-balancer/CDN access log, no
    client-side error reporting, and no request ids or timestamps from the
    support tickets themselves. H5 cannot be settled from this target at all.
  - >-
    Application source was not read — it is outside the surface contract. The
    H1 mechanism rests on the runtime stack trace (E5); "no effective zero
    guard" is inference from observed behaviour, not from reading shop.py:64.
  - >-
    Detail-route coverage in this investigation is partial: ids 1, 3, 4 and 999
    were probed directly; id 5 and id 2 appear only in pre-investigation user
    traffic (E13). Product 3 is the only catalogue row with units_in_stock 0
    (E3), so the generalisation in H1 is sound for this catalogue but was not
    probe-verified on every id.
  - >-
    Lens coverage: only three lenses exist in this repo (software-defect,
    infra-process, interfaces) and all three were run. The taxonomy's
    load-saturation, third-party and data-db classes had no dedicated lens;
    data-db was reached only obliquely, as H4.
usage:
  model: claude-opus-5
  tokens: 1885762
  wall_clock_seconds: 364
---

# Product-page "Internal Server Error" report — no observed incident, one live defect found

## Summary

**Verdict: no active incident in any telemetry this target retains — but a real,
live, deterministic defect was found that produces exactly the reported symptom.**

`GET /products/{product_id}` computes `turnover_score` as
`units_ordered / units_in_stock`. Product 3 ("Unobtainium Ingot") currently has
`units_in_stock: 0`, so its detail page raises `ZeroDivisionError` and returns
HTTP 500 — five out of five attempts, with the stack terminating at
`shop.py:64` (E4, E5, E6, E7). Every other product id returns 200 (E8, E9). The
list page renders product 3 fine; only the detail handler divides.

What the telemetry does **not** show is any customer hitting it. All five
recorded 500s carry `konan-*` request ids — they are my own probes (E14). Every
non-investigator request on record, 12:00:11Z–12:00:16Z, returned 200 or 201,
and none of them opened `/products/3` (E13). The service process began at
12:00:10.746Z with no rotated logs behind it (E2, E14), so the window the
complaint describes — "this morning" — is simply not observable from here. The
reported customer errors are therefore neither confirmed nor contradicted; they
are unevidenced.

Confidence: high on the mechanism (stack trace at a named expression,
deterministic reproduction, clean negative control, exception counter matching
the 500 count exactly). High on the absence of *observed* user impact. Zero
visibility into the complained-of period.

For a responder, the actionable line is: the defect is live and reachable right
now, product 3 is listed in the public catalogue, and any customer who opens its
page will get an Internal Server Error. That matches what Support described. It
is treated here as a latent finding rather than a confirmed outage only because
no user request in surviving telemetry ever reached it.

## Timeline

- **2026-08-19T12:00:10.746Z** — service process starts; `faultline 0.1.0
  started` (E2). This is the earliest observable moment; nothing before it
  survives (E14). No configuration, deploy, or flag-change marker appears
  anywhere in the log — and no chaos event at all (E11).
- **12:00:11.472Z – 12:00:16.812Z** — all real (unstamped) user traffic on
  record: health checks, the product list, product detail pages 1, 2 and 5, an
  order created (201) and the order list. All 200/201, max 16.3 ms (E13).
- **12:00:22Z** — complaint raised by a human via Support (`startsAt`).
- **12:00:29Z** — investigation starts (trigger latency 7 s).
- **12:00:45Z** — baseline: `/health` 200, uptime 34.8 s (E1); `/metrics` shows
  no `http_exceptions_total` series at all and no non-2xx status.
- **12:02:09.308Z** — first 500 anywhere on record, and it is mine: probe of
  `/products/3` raises `ZeroDivisionError` at `shop.py:64` (E5, E6).
- **12:02:20Z – 12:02:33Z** — four further independent reproductions, all
  `/products/3`, all 500 (E7).
- **12:02:17Z** — uptime 126.8 s, RSS unchanged at 47.1 MB: no restart, no
  growth across the whole error window (E12).
- **12:06:33Z** — investigation concluded.

## Investigation

**Baseline.** `/health` 200 with 34.8 s uptime, `/metrics` with zero exception
series and only 2xx statuses, a 16-line log, and the product catalogue — which
immediately showed two data oddities worth carrying forward: product 3 with
`units_in_stock: 0` and product 4 with `price: null` (E3).

**Triage — one round, three lenses in parallel** (software-defect,
infra-process, interfaces — the complete lens set in this repo, none excludable
by the complaint). Each was blind to the others and received only its lens file,
the surface contract, the verbatim complaint, and the baseline. All three
independently converged on the same deterministic `/products/3` failure, and all
three independently flagged the same evidence gap: nothing survives from before
12:00:10Z.

**Deep-dive: skipped, deliberately.** Triage evidence for H1 was already
deterministic and complete — reproduced five times with distinct request ids, a
stack trace naming the throwing expression, a negative control on sibling ids,
and an exception counter matching the 500 count exactly. Deep-dives fill
evidence gaps; there was no gap left to fill that another probe could close.
The one genuinely open question — whether real users hit it — is unanswerable
from this surface at any budget, so it went to the judge as H5 rather than to a
deep-dive agent.

**Judge.** One fresh adversarial judge, given the evidence ledger and the
hypothesis list with no narrative. It validated H1, invalidated H2, H3, H4 and
H5, and rejected H5's original citation list as circular — the 500 counts
offered in support of user impact are counts of my own probes. That correction
is the reason this journal's verdict is `no-active-incident` rather than
`root-cause-identified`: the mechanism is proven, the impact claim is not.

## Hypotheses

### H1 — ZeroDivisionError on a zero-stock product (validated)

`turnover_score = units_ordered / product["units_in_stock"]` at `shop.py:64`
divides by a catalogue field that is legitimately zero for an out-of-stock item.
Product 3 is the only row with `units_in_stock: 0` (E3), and it is the only id
that fails. For: the stack trace names the expression with the operand carets
under the division (E5); the exception is bound to the 500 by shared request id
(E6); five reproductions across 24 seconds (E7); sibling ids return 200 with a
computed `turnover_score` (E8, E9); `http_exceptions_total{type=
"ZeroDivisionError"} 5` exactly equals the 500 count, so no second exception
type hides inside the same status (E10). Against: nothing.

Two sub-claims are weaker than the rest and are scoped accordingly: the source
was never read, so "no effective zero guard" is inference from behaviour; and
"every other id returns 200" is established for this five-row catalogue by
pooling probes (ids 1, 4) with prior user traffic (ids 1, 2, 5).

### H2 — Injected chaos or an operator-set fault rate (invalidated)

`faultline_chaos_enabled 0`, and `grep -c 'chaos'` over the log returns 0 — a
window that covers the entire life of the process, since the log begins at its
own startup marker and has no rotated backups (E11, E2, E14). Beyond the
absence: injection would not produce a genuine `ZeroDivisionError` inside
application arithmetic (E5), nor a failure bound to one input while siblings
succeed (E7 against E8, E9).

### H3 — Process fault: crash, restart loop, saturation, starvation (invalidated)

`process_uptime_seconds` runs 38.71 → 126.82 across an 88-second wall gap —
monotonic, no reset — and back-extrapolates to the single startup marker; there
is exactly one `event: startup` line and no shutdown line (E12, E2). RSS is
byte-identical at both reads, and it is a peak gauge, so it never exceeded
47.1 MB. Latency contradicts starvation: `/health` 3.3 ms (E1), and the failing
requests are themselves 2.5–10.3 ms (E6, E7). The second uptime read precedes
the last three 500s, but E10 closes that gap: a restart would zero the counters,
and the cumulative 500 count of 5 spans all five events.

### H4 — The null price on product 4 (invalidated)

Directly falsified: `/products/4` — the null-price row — returns 200 with
`"turnover_score": 0.0` (E8). The converse fails too; the failing row has a
non-null price of 999.0 (E3). Null price is neither sufficient nor present in
the failure.

### H5 — Customers actually hit this defect this morning (invalidated)

Separable from H1 and does not inherit its verdict: H1 is a claim about
mechanism, H5 a claim about impact. Proving the mechanism raises the prior on
H5 but supplies no evidence for it. All five recorded 500s are `konan-*`
stamped (E14) — investigator-generated errors cannot evidence customer impact.
The complete set of real user requests returned 200/201 and never touched
`/products/3` (E13). And the complaint's `startsAt` of 12:00:22Z sits before the
first 500 on record, in a period during which this process had served only the
clean traffic of E13 — with nothing at all retained from before 12:00:10.746Z
(E2, E14).

Invalidated is scoped to what is observable: no user request reached the failing
path in any surviving telemetry. It is **not** a claim that Support is wrong.
The evidence that would settle it is upstream and does not exist on this
surface — see Gaps.

## Safe next steps

All read-only; remediation is out of scope for this journal.

1. Correlate against the tickets: ask Support for the affected customers' request
   ids, exact timestamps, or the product they were viewing. A ticket naming
   product 3 (or any zero-stock item) would convert H5 from unevidenced to
   confirmed at essentially no cost.
2. Check whether any upstream vantage point retains the morning — edge, load
   balancer, CDN access logs, or client-side error reporting. This target's own
   history begins after the complaint window.
3. Read `/products` periodically and note which rows show `units_in_stock: 0`:
   that set is the current blast radius of the defect, and it changes as stock
   moves. Today it is exactly product 3.
4. Review log retention for this service. With no rotated backups present, a
   process restart erases the record — which is precisely what blocked this
   investigation.
5. Track the OpenAPI drift separately (E15): 404 and 500 are served but
   undeclared, and the 200 body schema constrains nothing. That is a contract
   defect in its own right, not an incident cause.

## Gaps

- **The complained-of window is unobservable.** The process started at
  12:00:10.746Z and `lab/logs/` holds only `app.log` with no `.1`–`.3` backups
  (E2, E14). `/metrics` counters are process-scoped and reset at the same
  boundary. Nothing this service recorded earlier this morning can be read.
- **No independent vantage point.** No edge, load-balancer or CDN log, no
  client-side error reporting, and no request ids or timestamps from the support
  tickets. H5 is not merely unsettled here — it is unsettleable from this
  target, whatever the budget.
- **Source not read.** Application code is outside the surface contract, so the
  mechanism rests on the runtime stack trace. "No effective zero guard" is an
  inference from observed behaviour, not from reading `shop.py:64`.
- **Partial detail-route coverage.** Ids 1, 3, 4 and 999 were probed; ids 2 and
  5 appear only in pre-investigation user traffic (E13). Since product 3 is the
  only catalogue row with zero stock (E3), the generalisation holds for this
  catalogue, but it was not probe-verified id by id.
- **Lens coverage.** All three lenses that exist in this repo were run
  (software-defect, infra-process, interfaces). The taxonomy is wider: no
  dedicated lens exists for load-saturation, third-party or data-db, and
  data-db was reached only obliquely, as H4.
