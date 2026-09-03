---
konan_journal: 1
investigation:
  id: 2026-08-19-routine-handover-check
  trigger: >-
    manual — /konan human adapter. Complaint object: source=human,
    fingerprint=human-1787139557, labels.alertname=human-report (no severity
    stated by the reporter, so none recorded), startsAt=2026-08-19T11:39:17Z.
    Investigation started 2026-08-19T11:39:22Z; trigger latency 5s.
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-08-19T11:39:22Z
  concluded: 2026-08-19T11:48:00Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: >-
      All four user-facing 503s in the observable window were produced by a
      fault-injection (chaos) window opened at 11:38:38.404Z with failure_rate
      0.6 / error_status 503 and closed at 11:38:44.759Z; the injection is off
      now and no non-investigator request has failed since.
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E14]
    evidence_against: []
  - id: H2
    statement: >-
      A data-dependent defect in the product-detail route divides units_ordered
      by units_in_stock without a zero guard, so GET /products/3
      (units_in_stock 0) raises ZeroDivisionError and returns HTTP 500
      deterministically; in the observable window only investigator probes
      reached it, so it is a latent fault, not the active incident.
    incident_class: software-defect
    state: validated
    evidence_for: [E7, E8, E9, E10, E11, E15]
    evidence_against: []
  - id: H3
    statement: >-
      The product-detail route's metrics are split across two path label sets —
      raw URL paths and the route template — and the only raw-labelled series
      are exactly the four chaos-window 503s, so those errors do not appear in
      queries grouped on the templated path label.
    incident_class: software-defect
    state: validated
    evidence_for: [E6, E12]
    evidence_against: []
  - id: H4
    statement: >-
      GET /products/{product_id} serves HTTP statuses its published OpenAPI
      document does not declare — the document lists only 200 and 422, while
      the route has served 503 and 500.
    incident_class: interfaces
    state: validated
    evidence_for: [E13, E14, E15]
    evidence_against: []
  - id: H5
    statement: >-
      The reported noise was process instability — a crash, restart loop, or
      resource saturation — rather than injected failure.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E19, E20, E21]
latent_findings:
  - statement: >-
      GET /products/3 returns HTTP 500 to any caller right now and the product
      is listed in the public catalog, so the fault is user-reachable; it has
      simply not been hit by real traffic in the observable window.
    evidence: [E7, E8, E9, E10]
  - statement: >-
      Catalog stock values are consistent with order creation decrementing
      units_in_stock (the two ordered products stand one below a round number —
      119 and 39 — while un-ordered products are 75 and 500). If stock is
      mutable this way, any product reaching zero acquires the H2 500, so the
      blast radius grows with normal business activity. Suggestive, not proven.
    evidence: [E9, E18, E22]
  - statement: >-
      Chaos-window 503s are recorded under raw URL path labels, which is both a
      per-route error-rate blind spot and unbounded metric label cardinality.
    evidence: [E6, E12]
  - statement: >-
      The published OpenAPI document declares no error statuses for the product
      detail route, so a generated client has no defined handling for the 500
      or 503 the route can serve.
    evidence: [E13, E14, E15]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:38:38.404Z"
    quote: |-
      {"ts": "2026-08-19T11:38:38.404Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "d512f8040bcc", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:38:39.468Z"
    quote: |-
      {"ts": "2026-08-19T11:38:39.468Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "85684e14f68d", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:38:44.759Z"
    quote: |-
      {"ts": "2026-08-19T11:38:44.759Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "43394e30b211", "event": "chaos_disabled"}
  - id: E4
    type: metric
    source: "/metrics @ request_id konan-1787139798-56328"
    quote: "faultline_chaos_enabled 0"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:39:04.820Z"
    quote: |-
      {"ts": "2026-08-19T11:39:04.820Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "771db5aed543", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.134, "client": "127.0.0.1:59860"}
  - id: E6
    type: metric
    source: "/metrics @ request_id konan-1787139798-56328"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
  - id: E7
    type: probe
    source: "/products/3 @ request_id konan-1787139663-56209"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787139663-56209"}
      -- HTTP 500 in 0.009956s
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:41:03.206Z"
    quote: |-
      event "unhandled_exception", request_id "konan-1787139663-56209", exception_type "ZeroDivisionError", stack tail: File ".../faultline/shop.py", line 64, in get_product / "turnover_score": units_ordered / product["units_in_stock"], / ZeroDivisionError: division by zero
  - id: E9
    type: probe
    source: "/products @ request_id konan-1787139788-56315"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.003425s
  - id: E10
    type: metric
    source: "/metrics @ request_id konan-1787139798-56328"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:39:09.078Z"
    quote: |-
      {"ts": "2026-08-19T11:39:09.078Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "952001f5acad", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.785, "client": "127.0.0.1:59865"}
  - id: E12
    type: metric
    source: "/metrics @ request_id konan-1787139798-56328"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 4
      http_request_duration_seconds_count{method="GET",path="/products/1"} 1
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 6
  - id: E13
    type: probe
    source: "/openapi.json @ request_id konan-1787139700-56287"
    quote: |-
      "/products/{product_id}":{"get":{...,"responses":{"200":{...},"422":{"description":"Validation Error",...}}}}
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:38:41.593Z"
    quote: |-
      {"ts": "2026-08-19T11:38:41.593Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "739976056308", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.295, "client": "127.0.0.1:59854"}
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:41:06.993Z"
    quote: |-
      {"ts": "2026-08-19T11:41:06.993Z", ... "message": "GET /products/3 -> 500", "request_id": "konan-1787139666-56222", "status": 500}
  - id: E16
    type: probe
    source: "/health @ request_id konan-1787139574-56100"
    quote: |-
      {"status":"ok","uptime_seconds":59.576084999833256}
      -- HTTP 200 in 0.001517s
  - id: E17
    type: probe
    source: "/orders @ request_id konan-1787139788-56321"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-08-19T11:38:42.656+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-08-19T11:39:06.949+00:00"}]
      -- HTTP 200 in 0.001434s
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:39:06.949Z"
    quote: |-
      {"ts": "2026-08-19T11:39:06.949Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "7272afd7c1b1", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E19
    type: metric
    source: "/metrics @ request_id konan-1787139798-56328"
    quote: |-
      process_uptime_seconds 283.56973345787264
      process_max_rss_bytes 47726592
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:38:34.585Z"
    quote: |-
      {"ts": "2026-08-19T11:38:34.585Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E21
    type: log
    source: "lab/logs/ directory listing @ 2026-08-19T11:39:40Z"
    quote: |-
      -rw-r--r--@ 1 lyudmylan  staff  7267 Aug 19 14:39 app.log
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:38:42.656Z"
    quote: |-
      {"ts": "2026-08-19T11:38:42.656Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "27df9c6f386f", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 1, "total_price": 49.5}
gaps:
  - >-
    Telemetry horizon is ~5 minutes. lab/logs/app.log is the only log file — no
    rotated .1-.3 backups exist (E21) — and its first line is the process start
    at 11:38:34.584Z (E20); all counters are process-scoped and were zero then.
    Nothing before that instant is observable by any instrument in the contract.
  - >-
    The reporter said "earlier" without a time, and the complaint was raised at
    11:39:17Z. The chaos window opened 3.8s after telemetry begins, so it is the
    only candidate visible rather than a confirmed identification. Whether the
    noise the reporter heard is this window, or something before 11:38:34.584Z,
    cannot be settled from the available surface. Settling evidence would be an
    access record that outlives the process — an upstream proxy/LB log or a
    persisted Prometheus scrape.
  - >-
    "No real user hit /products/3" is a weak absence claim: the product-detail
    route saw only 8 requests in the whole window (E12 plus the two raw-labelled
    503s), and counters reset on restart.
  - >-
    Whether units_in_stock is mutable — decremented by order creation — is not
    established. The catalog numbers (E9) against the two orders (E18, E22) are
    suggestive only. Confirming it means reading faultline's source, which the
    blinding contract in eval/README.md puts out of reach for an investigation.
  - >-
    H3's mechanism is unproven. The label split is directly observed, but
    attributing it to the chaos short-circuit bypassing route resolution rests
    on n=2 raw-labelled requests; a broader "any response produced before route
    resolution" explanation fits the same data. Settling it needs the metrics
    middleware source, out of bounds for the same reason.
  - >-
    The write path was never exercised by the investigator — probe.sh is
    GET-only and order creation is eval-side. Order-creation health rests on one
    organic event at 11:39:06.949Z (E18) plus a read-back (E17), both several
    minutes stale at conclusion.
  - >-
    Latency and saturation are assessed at near-zero traffic. Flat RSS and a
    single exception series (E19) are consistent with a healthy service and
    equally consistent with an idle one; they discriminate little at this volume.
usage:
  model: claude-opus-5
  tokens: 1560368
  wall_clock_seconds: 518
---

# Routine handover check: no active incident, one live user-reachable fault on /products/3

## Summary

**No active incident.** The shop service is serving its business surface normally
right now: catalog, product detail, and order listing all return 200, chaos
injection is off, and no non-investigator request has failed since 11:38:44.759Z
(E4, E5, E9, E17). The "noise earlier" corresponds to the only user-facing
degradation visible in telemetry — a 6.4-second fault-injection window
(failure_rate 0.6, error_status 503) opened at 11:38:38.404Z and closed at
11:38:44.759Z, which cost **4 real user requests** across 3 paths (E1, E2, E3,
E6, E14). That window is closed and needs no action.

Two caveats belong on the handover, and they matter more than the resolved
window:

1. **A live, user-reachable 500.** `GET /products/3` fails deterministically for
   any caller, right now — the route divides by `units_in_stock`, which is 0 for
   that product, and the product is listed in the public catalog (E7, E8, E9,
   E10). No real user has hit it in the observable window, which is why the
   verdict is "no active incident" rather than "incident" — but that is traffic
   luck, not health. Treat it as a fault waiting for its first customer.
2. **The window is only ~5 minutes wide.** The log has no rotated backups and
   begins at the process start (E20, E21). If the reporter's "noise" predates
   11:38:34.584Z, no instrument in the contract can see it. I can neither
   confirm nor exclude anything before that instant.

Confidence: high on the chaos window and on the `/products/3` mechanism (both
deterministic, both reproduced). Low on the claim that the chaos window *is*
what the reporter noticed — see Gaps.

## Timeline

- **11:38:34.585Z** — process start, `faultline 0.1.0 started` (E20). Telemetry
  begins here; nothing earlier is observable (E21).
- **11:38:36.346Z** — last known-good before injection: `GET /products/1 -> 200`.
- **11:38:38.404Z** — **configuration-change marker**: `chaos mode enabled`,
  `failure_rate: 0.6`, `error_status: 503`, `extra_latency_ms: 0` (E1).
- **11:38:39.468Z – 11:38:43.704Z** — four `chaos_failure` lines, each paired by
  request id with a 503 access line, all unstamped (real user traffic): 2×
  `/products`, 1× `/products/1`, 1× `/products/2` (E2, E6, E14).
- **11:38:42.656Z** — order 1 created *during* the window (E22) — failure was
  probabilistic, not total.
- **11:38:44.759Z** — **configuration-change marker**: `chaos mode disabled` (E3).
- **11:39:04.820Z – 11:39:09.078Z** — user traffic resumes clean: `/products`,
  `/products/1`, `/orders`, `/products/5` all 200; order 2 created (E5, E11, E18).
- **11:39:17Z** — complaint raised (`startsAt`); investigation starts 11:39:22Z.
- **11:41:03.206Z / 11:41:06.993Z** — investigator probes of `/products/3` raise
  `ZeroDivisionError` twice, HTTP 500 both times (E7, E8, E15).
- **11:47:18Z** — final state confirmed: chaos off, business surface 200,
  uptime continuous at 283.6s with no restart (E4, E9, E17, E19).

## Investigation

**Baseline.** `/health` 200, uptime ~60s, chaos gauge 0, and — importantly — no
`http_exceptions_total` series at all (E16). The full log was 30 lines, so the
entire process history was readable directly.

**Triage.** The complaint is vague ("anything wrong?"), so no lens domain could
be excluded by evidence; all three available lenses ran in parallel and blind:
`infra-process`, `software-defect`, `interfaces`. Findings deduplicated into H1–H4,
plus H5 as the process-instability alternative the infra lens closed off.

**Deep-dive.** Skipped by design. Every surviving hypothesis had deterministic,
complete triage evidence — chaos markers bracketing exactly four paired failures,
a stack trace naming the failing expression, a metric label split visible in a
single scrape. Deep-dives exist to fill evidence gaps, not to re-prove; the
remaining gaps are all blocked by the telemetry horizon or the blinding contract,
which no further probing can reach. I confirmed current business-surface state
myself (E9, E17) rather than trusting a green `/health` alone.

**Judge.** The adversarial pass refused to bless the first draft and was right
three times, all of which changed this journal:

- It rejected identifying the chaos window with the reporter's "noise" — the
  window opens 3.8s after telemetry begins, so this is a streetlight inference.
  H1 was narrowed to what the evidence shows, and the identification moved to Gaps.
- It called the original wording self-contradictory: "business surface healthy"
  alongside a live 100%-failing product page. The Summary now leads with that
  tension instead of burying it.
- It flagged that scoping the defect to "product 3" may understate blast radius
  if stock is mutable. That became a latent finding with its evidence and its
  limits stated.

It also flagged that an unstamped request enabled chaos, implying an
authorization question. The lab contract answers this one: `docs/lab.md` defines
`/chaos` as operator/eval surface driven by `scripts/scenario.sh`, deliberately
unstamped so scenario traffic is distinguishable from `konan-*` probes. Expected
operator action, not an unauthorized actor.

## Hypotheses

### H1 — chaos-injection window (validated)

All four user-facing 503s fall between the enable marker (E1) and the disable
marker (E3), each `chaos_failure` line pairing by request id with its 503 access
line. The counter arithmetic closes exactly: E6's 503 series sum to 4, matching
the four logged failures. Failure was probabilistic, not total — order 1 was
created inside the window (E22) and `/products/1` returned 200 before and after
it. Current state is confirmed off (E4) with clean user traffic since (E5).
*Against:* nothing. *Limit:* this establishes what the window was and that it is
closed, not that it is what the reporter heard.

### H2 — latent ZeroDivisionError on /products/3 (validated, latent)

The stack trace names the expression and line (E8); the catalog independently
confirms product 3 has `units_in_stock: 0` (E9); the same route succeeds for
products with non-zero stock, including real user traffic to `/products/5` (E11).
Two probes, two identical failures, and the counters agree exactly:
`http_exceptions_total{type="ZeroDivisionError"} 2` (E10). Both 500s carry
`konan-` ids (E7, E15), so **user impact so far is zero** — scoped to the
observable window, where the route saw 8 requests total. This is a latent
finding by the skill's own test: only investigator probes triggered it.

### H3 — split path labels on the metrics surface (validated as fact)

One logical route reports under both raw URL paths and the route template, and
the only raw-labelled series are precisely the four chaos 503s (E6, E12). The
non-chaos 500s *are* templated, which is what makes the split visible. Stated
here as the observed fact; the causal mechanism is not proven (see Gaps).
Practical effect: a per-route error-rate query grouped on `path="/products/{product_id}"`
showed 0% errors during a window in which real users received 503s.

### H4 — undeclared statuses vs OpenAPI (validated, low significance)

The published document lists only 200 and 422 for the route (E13), which has
served 503 (E14) and 500 (E15). Recorded for completeness, but its weight is
small: the 503 half exists only because injection was on, and the 500 half
disappears with H2. An undeclared 500 is also the framework default. This is a
documentation nit, not contract drift with independent user impact.

### H5 — process instability or saturation (invalidated)

Exactly one startup marker exists in the whole log (E20) and uptime advanced
monotonically to 283.6s with no counter reset (E19) — one continuous process,
no crash, no restart loop. The process kept counting straight through both
unhandled exceptions. Peak RSS was byte-identical across four samples spanning
~220s (E19). Killed. Note the weak form of this evidence at near-zero traffic:
it shows nothing happened, not that the service is robust.

## Safe next steps

All read-only; remediation is out of scope for a journal.

- Treat `/products/3` as the live item from this handover: it returns 500 to any
  caller now, and the product is in the public catalog. Worth an owner and a
  ticket before a customer finds it.
- Confirm whether `units_in_stock` is decremented by order creation. If it is,
  the H2 fault is not scoped to one seeded product — any product reaching zero
  stock acquires it. Answerable from faultline's own source by someone outside
  the blinding contract.
- Check whether per-route error-rate alerting groups on the templated `path`
  label. If so, H3 means injected or pre-route-resolution 503s do not raise it —
  a missed-alert path worth knowing about before it matters.
- If any record of the service exists outside this process — upstream proxy or
  LB access logs, a persisted Prometheus scrape — check the period before
  11:38:34.584Z. That is the only way to answer what the reporter actually heard.

## Gaps

Elaborated in the frontmatter list. In short: the telemetry horizon is ~5 minutes
and begins at process start, so anything genuinely "earlier" is unobservable;
the identification of the chaos window with the reported noise is unproven; the
absence of user impact on `/products/3` rests on a small sample; stock mutability
and H3's mechanism both need source access the blinding contract forbids; the
write path was never exercised because the probe surface is GET-only; and
saturation signals carry little information at this traffic volume.
