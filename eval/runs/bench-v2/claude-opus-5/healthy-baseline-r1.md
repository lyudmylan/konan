---
konan_journal: 2
investigation:
  id: 2026-11-03-routine-handover-check
  trigger: manual
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-03T05:59:25Z
  concluded: 2026-11-03T06:10:35Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The shop service is currently returning errors to non-investigator traffic."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E5, E6, E7]
  - id: H2
    statement: "GET /products/{product_id} divides by units_in_stock without a zero guard, so it raises an unhandled ZeroDivisionError and returns HTTP 500 for any product whose units_in_stock is 0; in the catalog as returned, id 3 is the only such row, and no non-investigator request reached it in this process's lifetime."
    incident_class: software-defect
    state: validated
    evidence_for: [E3, E4, E7, E8, E12, E13, E14, E15, E16]
    evidence_against: []
  - id: H3
    statement: "The process crashed and restarted, or is in a restart loop — the first health reading showed only 52 seconds of uptime."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1]
    evidence_against: [E2, E10, E17]
  - id: H4
    statement: "The service is degraded right now by load saturation or a resource leak."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E11, E18]
  - id: H5
    statement: "The null price on product id 4 breaks the order-creation pricing path."
    incident_class: interfaces
    state: inconclusive
    evidence_for: [E12]
    evidence_against: [E16]
latent_findings:
  - statement: "Zero-stock products make their detail page a deterministic HTTP 500: GET /products/{product_id} computes turnover_score as units_ordered / units_in_stock with no zero guard. Reachable by any end user who opens such a product; only investigator probes have triggered it so far."
    evidence: [E13, E14, E15]
  - statement: "The 500 error envelope returns the internal exception class name to the client instead of an opaque error."
    evidence: [E13]
evidence:
  - id: E1
    type: probe
    source: "/health @ request id konan-1793685587-19772"
    quote: |
      {"status":"ok","uptime_seconds":52.681137250037864}
      -- HTTP 200 in 0.004105s request_id=konan-1793685587-19772
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:58:55.247Z"
    quote: '{"ts": "2026-11-03T05:58:55.247Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E3
    type: log
    source: "lab/logs/app.log — the complete set of non-2xx access lines in the file (message and request_id fields extracted)"
    quote: |
      "message": "GET /products/3 -> 500", "request_id": "konan-1793685689-19868"
      "message": "GET /products/3 -> 500", "request_id": "konan-1793685697-19881"
      "message": "GET /products/3 -> 500", "request_id": "konan-1793685717-19923"
      "message": "GET /products/99 -> 404", "request_id": "konan-1793685756-19944"
  - id: E4
    type: log
    source: "lab/logs/app.log — census of distinct request_id values with occurrence counts, whole file (35 lines)"
    quote: |
      1 "0e63f406f718"  1 "155f127ddd85"  1 "3316344e06cb"  1 "56d2f04a0d08"  1 "57546bb8de2e"
      2 "620a93c259ab"  1 "63841df967f1"  2 "bd007fac347b"  1 "bd1320b4d5de"
      1 "konan-1793685587-19772"  1 "konan-1793685588-19777"  1 "konan-1793685672-19843"
      1 "konan-1793685678-19851"  1 "konan-1793685682-19857"  2 "konan-1793685689-19868"
      1 "konan-1793685692-19873"  2 "konan-1793685697-19881"  1 "konan-1793685699-19886"
      1 "konan-1793685699-19891"  1 "konan-1793685709-19909"  1 "konan-1793685712-19917"
      2 "konan-1793685717-19923"  1 "konan-1793685725-19933"  1 "konan-1793685734-19939"
      1 "konan-1793685756-19944"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:59:04.347Z (unstamped request id — non-investigator traffic)"
    quote: '{"ts": "2026-11-03T05:59:04.347Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "155f127ddd85", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.758, "client": "127.0.0.1:64157"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T05:59:00.175Z (unstamped request id — non-investigator traffic)"
    quote: '{"ts": "2026-11-03T05:59:00.175Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "bd007fac347b", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.788, "client": "127.0.0.1:64153"}'
  - id: E7
    type: metric
    source: "/metrics @ request id konan-1793685825-19969 — complete http_requests_total series set"
    quote: |
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/openapi.json",status="200"} 1
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="GET",path="/products/{product_id}",status="404"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E8
    type: metric
    source: "/metrics @ request id konan-1793685825-19969"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 3'
  - id: E9
    type: metric
    source: "/metrics @ request id konan-1793685825-19969"
    quote: "faultline_chaos_enabled 0"
  - id: E10
    type: metric
    source: "/metrics and /health — four readings between 2026-11-03T05:59:47Z and 2026-11-03T06:03:45Z"
    quote: "process_uptime_seconds 53.204902374884114 -> 143.7290967500303 -> (/health uptime_seconds) 164.60727424989454 -> 290.6577577078715"
  - id: E11
    type: metric
    source: "/metrics — same four readings"
    quote: "process_max_rss_bytes 47153152 -> 47153152 -> 47153152 -> 47153152"
  - id: E12
    type: probe
    source: "/products @ request id konan-1793685872-20016"
    quote: |
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001561s request_id=konan-1793685872-20016
  - id: E13
    type: probe
    source: "/products/3 @ request id konan-1793685689-19868 (triage probe)"
    quote: |
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793685689-19868"}
      -- HTTP 500 in 0.010987s request_id=konan-1793685689-19868
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:01:29.465Z — trimmed: the home-directory path prefix is elided and the intermediate framework frames of the stack field are dropped; kept fields are unaltered"
    quote: |
      "ts": "2026-11-03T06:01:29.465Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793685689-19868", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):
        [...]
        File ".../faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
                            ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
      ZeroDivisionError: division by zero"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:01:29.475Z"
    quote: '{"ts": "2026-11-03T06:01:29.475Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793685689-19868", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.016, "client": "127.0.0.1:64191"}'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:01:22.553Z"
    quote: '{"ts": "2026-11-03T06:01:22.553Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1793685682-19857", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.519, "client": "127.0.0.1:64189"}'
  - id: E17
    type: log
    source: "lab/logs/app.log and lab/logs/ directory listing"
    quote: "One \"Started server process [19685]\" line and one `startup` event in the whole file; lab/logs/ contains only app.log, with no rotated .1-.3 backups."
  - id: E18
    type: metric
    source: "/metrics @ request id konan-1793685825-19969 — per-path duration sums and counts"
    quote: |
      http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 0.02018416882492602
      http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 10
      http_request_duration_seconds_sum{method="GET",path="/products"} 0.0025855840649455786
      http_request_duration_seconds_count{method="GET",path="/products"} 3
      http_request_duration_seconds_sum{method="POST",path="/orders"} 0.0031053738202899694
      http_request_duration_seconds_count{method="POST",path="/orders"} 2
gaps:
  - "No non-investigator traffic in the handover window: the last unstamped request is 2026-11-03T05:59:04.347Z, about 11 minutes before conclusion (E4, E5). 'No failures observed' is therefore not 'users are fine' — it is absence of data."
  - "The 9 non-investigator requests all sit in a 9-second burst beginning 0.7 s after startup (E4, E5, E6). That is the shape of a launch-time smoke run, not organic end-user traffic, so the healthy-traffic evidence may not represent real user behaviour at all."
  - "History before 2026-11-03T05:58:55.247Z is unobservable — one log file, no rotated backups (E17). Whether this process started clean or after an earlier exit cannot be determined, so 'it did not crash' is not claimable; only 'it has not restarted during the observation window' is (E10)."
  - "Whether POST /orders decrements units_in_stock is untestable read-only. If it does, the zero-stock defect arms itself on every product that sells out, not only id 3 — the blast radius would be the whole catalog over time, not one row."
  - "H5 could not be settled: exercising the order-creation pricing path needs a POST, which is a mutation outside the read-only allowlist, and the order-path source is outside the investigator's surface contract (docs/lab.md). Reading that code is not an available substitute."
  - "Catalog completeness is assumed from the /products response (E12): no pagination envelope was observed, but an unlisted or inactive zero-stock row would not appear there."
  - "Saturation and leak conclusions (H4) cover a ~4-minute window carrying ~12 requests at near-zero load, and process_max_rss_bytes is a high-water gauge, not current memory (E11). 'No leak under no load' is not 'no leak'."
  - "Three of the six taxonomy classes have no lens file: load-saturation, third-party, data-db. load-saturation was addressed from metrics instead (H4); third-party and data-db are structurally inapplicable to this target per docs/lab.md (no external provider, no database). These are accepted blind spots, not lens-checked domains."
  - "OpenAPI conformance of the undeclared 500 response shape was raised during triage but is not carried as a cited claim here — no verbatim slice of /openapi.json was captured, and 'no citation, no claim' applies."
  - "One Bash log-extraction command was refused by the boundary hook and deliberately not retried; the same fact was obtained with the Read tool instead (E14). No evidence was lost."
usage:
  model: claude-opus-5
  tokens: 2442318
  wall_clock_seconds: 670
---

# Routine handover check — no active incident, one armed latent defect

## Summary

**No active incident.** Nothing is failing for users right now: every one of the 9
non-investigator requests in this process's lifetime returned 2xx (E4, E5, E6), and
every non-2xx line in the log carries this investigator's `konan-` request-id prefix
(E3) — the three 500s and one 404 are all mine. The injected-degradation switch is off
(E9), the process has not restarted during the observation window (E10), peak memory is
byte-identical across four scrapes (E11), and latency is sub-11 ms everywhere (E18).

**But the handover should not be signed off as quiet.** Two things qualify that verdict.

First, a real defect is armed and user-reachable. `GET /products/{product_id}` computes
`turnover_score` as `units_ordered / product["units_in_stock"]` with no zero guard
(E14), so the detail page of any zero-stock product is a deterministic HTTP 500.
Product 3 (`Unobtainium Ingot`, `units_in_stock: 0`) is currently the only such row
(E12), and it failed 3 times out of 3 while the other ids returned 200 six times out of
six (E7). No user has hit it yet — which is luck, not protection: it is a plain
product-detail view, one click away for anyone browsing that product. This is a
**latent** finding, not the active incident, precisely because only my own probes
triggered it.

Second, the healthy evidence is thinner than it looks. All non-investigator traffic sits
in a 9-second burst right after startup, and nothing user-shaped has arrived in the ~11
minutes since. The honest reading is "no failure has been observed", not "users are
fine" — there were barely any users to observe.

Confidence: high on the defect mechanism (the stack names the dividing expression
directly), high on "no observed user-facing failure", low on "the service is healthy
under real traffic" — that was never tested.

## Timeline

- **05:58:55.247Z** — process start, single `startup` event, faultline 0.1.0 (E2, E17).
  No configuration, deploy, or chaos-change marker appears anywhere in the log.
- **05:58:55.965Z – 05:59:04.347Z** — the only non-investigator traffic: 9 requests
  across `/health`, `/products`, `/products/1`, `/products/2`, `/products/5`,
  `POST /orders` ×2 (orders 1 and 2 created), `GET /orders`. All 2xx, 0.758–12.879 ms
  (E5, E6).
- **05:59:04.347Z onward** — no further non-investigator traffic for the rest of the
  investigation (E4).
- **05:59:25Z** — investigation starts.
- **05:59:47.918Z** — first probe: `/health` ok, uptime 52.68 s (E1). The short uptime
  raised H3.
- **06:01:29.465Z** — first `/products/3` probe raises `ZeroDivisionError`; the stack
  names the divisor (E14, E15). Reproduced at 06:01:37.187Z and 06:01:57.399Z (E3).
- **06:03:45Z** — final metrics scrape: 3 × 500 and 3 × `ZeroDivisionError`, all
  investigator-attributable; chaos off; uptime monotonic; peak RSS unchanged (E7–E11).
- **06:10:35Z** — concluded.

## Investigation

**Baseline** — `/health`, `/metrics`, and the full 18-line log tail. Health was green,
but `uptime_seconds` of 52.68 was the first thing worth resolving: a fresh start and a
crash-restart look identical in a health response. One `startup` event and one
"Started server process" line, with no rotated log backups, settled it as a clean start
(E2, E17).

**Triage** — three lenses in parallel, blind to each other: software-defect,
infra-process, interfaces. The taxonomy has six classes and this repo ships three lens
files; the three missing domains are recorded under Gaps rather than silently dropped.
software-defect and interfaces independently found the `/products/3` 500 and
independently labelled it latent. infra-process found nothing and said so.

**Deep-dive** — none spawned. H2's triage evidence was already deterministic and
complete (3/3 reproductions on one id, 0/6 on the others, exception type, access line,
and counter agreement), and the report contract routes such a hypothesis straight to the
judge rather than re-proving it. The remaining hypotheses were either killed by baseline
evidence or blocked by the read-only boundary, which no amount of deep-diving moves.

**Judge** — the adversarial pass was the most useful step of this investigation and
changed the write-up in four ways:

1. It rejected "unstamped means end user" as an unestablished inference, and pointed out
   that the non-investigator traffic sits entirely in a 9-second post-startup burst.
   Correct. The claim is now "non-investigator traffic", and the smoke-run shape is a
   recorded gap.
2. It flagged that "at handover time" had no supporting data at all, since no user
   traffic exists in the last minutes. Correct, and it is now the lead caveat of the
   summary rather than a footnote.
3. It called the trimmed `stack` field the single highest-value piece of missing
   evidence, because without it "`units_in_stock` is the divisor" was a one-row
   correlation. Correct — so I went back and read it (E14). The divisor is confirmed
   literally, which is what licenses the "any zero-stock product" quantifier in H2.
4. It argued H5 was testable read-only by reading the order-path source. **This one I
   reject**: the surface contract limits the investigator to probes, logs, and metrics,
   and the target's source is deliberately outside that surface. The stack field in
   E14 is telemetry the service emitted, which is a different thing from reading the
   repository. H5 stays inconclusive.

It also corrected my evidence bookkeeping on H3: the startup event supports "started
recently" and refutes only "restart loop". H3 is scored as invalidated for the loop,
with the unobservable pre-start history recorded as a gap instead.

## Hypotheses

### H1 — the service is currently erroring for non-investigator traffic — *invalidated*

Every non-2xx access line in the file is `konan-`stamped (E3), and the counters
reconcile exactly: 3 × 500 and 1 × 404 on `/products/{product_id}` (E7), 3 ×
`ZeroDivisionError` (E8), matching the three request ids that appear twice in the census
— once for the access line, once for the exception line (E4). The 9 unstamped requests
are all 2xx (E5, E6). What this does **not** establish is that users are healthy now;
see the first two gaps.

### H2 — zero-stock products 500 on the detail route — *validated*

The mechanism is quoted, not inferred: `"turnover_score": units_ordered /
product["units_in_stock"]` in `get_product`, with the caret line pointing at the
division and `ZeroDivisionError: division by zero` below it (E14). That also explains the
route asymmetry — the list route does not compute the field, so `/products` stays 200
(E12) while `/products/3` fails. Determinism: 3 failures on id 3 (E3), against 6
successes on other ids (E7), including `/products/4` at 200 (E16). The catalog shows
exactly one zero-stock row (E12). Latent, not active: all three failures carry
investigator request ids, and no unstamped request touched id 3 (E3, E4).

The uncomfortable part is in the gaps: if order creation decrements stock, this defect
arms itself on any product that sells out, and id 3 is just the first to arrive at zero.

### H3 — crash or restart loop — *invalidated*

Four uptime readings rise monotonically with wall clock, 53.2 s → 290.7 s across about
four minutes (E10), against a single startup marker and no rotated logs (E2, E17). No
restart happened while I watched. Why the process started at 05:58:55 is not in evidence
at all, so I claim nothing about an earlier exit.

### H4 — saturation or resource leak — *invalidated*

Peak RSS is byte-identical across four scrapes (E11) and per-path latency is flat to
sub-millisecond (E18; the 12.879 ms outlier is the cold-start `/health`). Scoped to the
observed window only — ~12 requests is not load, and the gauge is a high-water mark.

### H5 — null price breaks order pricing — *inconclusive*

Product 4 carries `"price":null` where every other row has a number (E12), and order
creation derives a total from price. The read paths survive it — `/products/4` returns
200 (E16) — but the pricing path cannot be exercised without a POST, which the read-only
boundary forbids. Flagged as a data shape worth a second pair of eyes, asserted as
nothing.

## Safe next steps

Read-only, in priority order:

1. **Treat the zero-stock 500 as the handover's one real item.** Ask whoever owns the
   catalog whether product 3 is expected to sit at zero stock, and whether order
   creation decrements stock — that answer decides whether this is one broken page or a
   whole-catalog time bomb. Both questions are answerable without touching the service.
2. **Get real traffic under observation before trusting the green verdict.** This check
   saw 9 requests in a 9-second burst. A handover sign-off deserves a window that
   contains actual user traffic; until then, "healthy" is untested rather than confirmed.
3. **Watch `http_exceptions_total` and the 500 series on
   `/products/{product_id}`** (E7, E8) for any count that arrives without a `konan-`
   request id — that is the signal that a user has found product 3.
4. **Note the error-envelope disclosure** (E13): the 500 body hands the client the
   internal exception class name. Worth raising with the service owner as hygiene.
5. **If the undeclared 500 shape matters for consumers**, capture
   `/openapi.json` and compare its declared responses for `/products/{product_id}`
   against observed statuses — triage raised this, and this journal deliberately does
   not claim it uncited.

Remediation is out of scope here; every item above is an observation or a question.

## Gaps

The frontmatter list, in short: no user traffic in the handover window and a smoke-run
shape to what traffic there was; no visibility before process start; the
stock-decrement question and the null-price pricing path both unreachable read-only;
catalog completeness assumed; the healthy-resource reading covers four idle minutes;
three taxonomy classes had no lens (one covered by metrics, two structurally
inapplicable); the OpenAPI conformance point left uncited on purpose; and one refused
Bash command, not retried, whose fact was recovered through the Read tool.
