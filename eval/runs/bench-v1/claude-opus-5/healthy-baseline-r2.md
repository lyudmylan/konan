---
konan_journal: 1
investigation:
  id: 2026-08-19-routine-handover-check
  trigger: "manual — /konan human profile; complaint object source=human, fingerprint=human-1787125304, labels.alertname=human-report, no severity stated; startsAt 2026-08-19T07:41:44Z, loop entered 2026-08-19T07:41:48Z (trigger latency 4s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-08-19T07:41:48Z
  concluded: 2026-08-19T07:48:43Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "A fault is actively degrading the shop service for real users during the handover window."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E4, E11, E14, E17]
  - id: H2
    statement: "GET /products/3 returns 500 deterministically because the catalog record for product 3 carries units_in_stock == 0 and the handler computes units_ordered / product[\"units_in_stock\"], dividing by zero."
    incident_class: software-defect
    state: validated
    evidence_for: [E5, E6, E7, E8, E9, E10, E11, E14]
    evidence_against: []
  - id: H3
    statement: "The /products/3 division-by-zero defect has affected real users during this process lifetime."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E8, E10, E11, E14, E15]
  - id: H4
    statement: "Operator-injected chaos or deliberate degradation is active on the target."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E5]
  - id: H5
    statement: "Process instability (crash or restart loop) or resource saturation is affecting the service."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E13]
  - id: H6
    statement: "Product 4's null price is an active data-integrity defect causing failures on the read path."
    incident_class: data-db
    state: invalidated
    evidence_for: []
    evidence_against: [E16]
latent_findings:
  - statement: "GET /products/3 fails with an unhandled ZeroDivisionError on every attempt (3/3), because product 3 is the only catalog row with units_in_stock == 0 and that field is the divisor in the turnover_score computation. No real user request has hit it during this process lifetime — all three failures carry investigator-stamped konan-* request ids. It becomes a user-facing 500 the moment a customer opens that product page."
    evidence: [E5, E6, E7, E8, E9, E14]
  - statement: "Product 4 (\"Mystery Box\") carries price: null while every other catalog row carries a numeric price. The read path tolerates it and returns 200, so this is a data-shape anomaly rather than an active fault; the order/pricing write path could not be tested read-only."
    evidence: [E9, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:41:27.439Z"
    quote: '{"ts": "2026-08-19T07:41:27.439Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:41:28.192Z"
    quote: '{"ts": "2026-08-19T07:41:28.192Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "6d23dcd7a21e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.147, "client": "127.0.0.1:58117"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:41:32.369Z"
    quote: '{"ts": "2026-08-19T07:41:32.369Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "6db5d3301edb", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.764, "client": "127.0.0.1:58120"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:41:36.545Z"
    quote: '{"ts": "2026-08-19T07:41:36.545Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "7bbeae79a375", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.764, "client": "127.0.0.1:58123"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:43:21.476Z (stack trimmed to the throwing frame; kept fields unaltered)"
    quote: '{"ts": "2026-08-19T07:43:21.476Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787125401-51036", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:43:21.484Z"
    quote: '{"ts": "2026-08-19T07:43:21.484Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787125401-51036", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.281, "client": "127.0.0.1:58160"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:43:27.164Z"
    quote: '{"ts": "2026-08-19T07:43:27.164Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787125407-51055", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.525, "client": "127.0.0.1:58163"}'
  - id: E8
    type: probe
    source: "/products/3 @ request_id konan-1787125709-51341 (third, disconfirming attempt)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787125709-51341"}
      -- HTTP 500 in 0.007907s request_id=konan-1787125709-51341
  - id: E9
    type: probe
    source: "/products @ request_id konan-1787125518-51189"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.005176s request_id=konan-1787125518-51189
  - id: E10
    type: metric
    source: "/metrics @ request_id konan-1787125505-51183"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 2'
  - id: E11
    type: metric
    source: "/metrics @ request_id konan-1787125505-51183"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="404"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
  - id: E12
    type: metric
    source: "/metrics @ request_id konan-1787125505-51183"
    quote: 'faultline_chaos_enabled 0'
  - id: E13
    type: metric
    source: "/metrics @ request_ids konan-1787125330-50967, konan-1787125442-51133, konan-1787125505-51183 (three scrapes)"
    quote: |-
      process_uptime_seconds 218.20771679189056
      process_max_rss_bytes 46858240
  - id: E14
    type: log
    source: "lab/logs/app.log — every /products* access line in the process lifetime, with request ids"
    quote: |-
      "message": "GET /products -> 200", "request_id": "6d23dcd7a21e"
      "message": "GET /products/1 -> 200", "request_id": "81c3ca65f4da"
      "message": "GET /products/2 -> 200", "request_id": "252d793bcb15"
      "message": "GET /products/5 -> 200", "request_id": "7bbeae79a375"
      "message": "GET /products -> 200", "request_id": "konan-1787125396-51019"
      "message": "GET /products/3 -> 500", "request_id": "konan-1787125401-51036"
      "message": "GET /products/4 -> 200", "request_id": "konan-1787125403-51048"
      "message": "GET /products/3 -> 500", "request_id": "konan-1787125407-51055"
      "message": "GET /products -> 200", "request_id": "konan-1787125430-51111"
      "message": "GET /products/4 -> 200", "request_id": "konan-1787125442-51141"
      "message": "GET /products/99 -> 404", "request_id": "konan-1787125451-51159"
      "message": "GET /products -> 200", "request_id": "konan-1787125518-51189"
  - id: E15
    type: log
    source: "lab/logs/app.log — all order_created events in the process lifetime"
    quote: |-
      "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 1, "total_price": 49.5
      "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 2, "total_price": 46.0
  - id: E16
    type: probe
    source: "/products/4 @ request_id konan-1787125403-51048"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001513s
  - id: E17
    type: metric
    source: "/metrics @ request_id konan-1787125505-51183"
    quote: 'http_requests_total{method="POST",path="/orders",status="201"} 2'
gaps:
  - "No pre-restart history. lab/logs/app.log begins at the 07:41:27.439Z startup and no rotated backups (.1-.3) exist, so nothing before this process could be checked. Every claim here is scoped to this process lifetime; 'no user has ever hit product 3' is NOT established, only 'no user hit it since 07:41:27Z'."
  - "Whether product 3's units_in_stock was seeded at 0 or driven to 0 by earlier writes could not be determined. No order in this lifetime touched product 3 (E15), but the catalog seed and the order handler's stock-decrement behavior live in source, which is outside the investigator's surface."
  - "The chaos verdict rests partly on absence of chaos_* log events, with no positive control: proving that a chaos toggle emits a log line would require triggering chaos, which is operator surface and forbidden to the investigator. faultline_chaos_enabled 0 was read only after the failures, not during."
  - "The user-traffic sample is thin and stale: 9 non-investigator requests inside one 8.4-second burst (07:41:28Z-07:41:36Z), and no user traffic at all since 07:41:36Z. 'Nothing wrong right now' therefore rests on synthetic probe evidence plus a small, old user sample - not on live user traffic."
  - "Only three lenses exist in the skill (software-defect, infra-process, interfaces). The taxonomy classes load-saturation, third-party and data-db have no dedicated lens; those domains were covered only incidentally by the three that ran."
  - "The order/pricing write path was never exercised against product 4 (price: null) or product 3, because POST is outside the read-only probe allowlist. Downstream impact of the null price on total_price is untested, not excluded."
  - "Saturation was assessed from process_uptime_seconds and process_max_rss_bytes only. No CPU, file-descriptor, thread or connection-pool metrics exist on this surface, and peak RSS is a high-water mark that cannot show a decline."
usage:
  model: claude-opus-5
  tokens: 2012134
  wall_clock_seconds: 415
---

# Routine handover check — no active incident, one latent 500 waiting on product 3

## Summary

**No active incident.** Every one of the 9 real-user requests in this process's lifetime
succeeded (200/201), the process is stable and unsaturated, and no chaos or degradation is
injected. The handover can be accepted as quiet.

One thing should be carried into the next shift, though. `GET /products/3` fails with an
unhandled `ZeroDivisionError` on **every** attempt — 3 of 3 — because product 3
("Unobtainium Ingot") is the only catalog row with `units_in_stock: 0`, and that field is the
divisor in the handler's `turnover_score` computation (E5, E9). This is **latent, not active**:
all three failures carry investigator-stamped `konan-*` request ids, and the full enumeration of
every `/products*` access line (E14) shows no real user has requested product 3 since this
process started. The defect is one customer click away from becoming a user-facing 500, and
because it is data-dependent it will not appear in any aggregate error rate until then.

Confidence is high on the mechanism (a stack trace names the throwing expression) and high on
the "no user impact so far" attribution — but that attribution is bounded by a log that only
reaches back to 07:41:27Z. See Gaps.

## Timeline

- **07:41:27.439Z** — process start, single startup marker, faultline 0.1.0 (E1). No earlier
  history survives; this is the horizon of everything below.
- **07:41:28.165Z – 07:41:36.545Z** — the entire body of real-user traffic: 9 requests
  (2×`/health`, `/products`, `/products/1`, `/products/2`, `/products/5`, 2×`POST /orders`,
  `/orders`), all 200/201 (E2, E3, E4, E14). Orders were placed against products 1 and 2 only
  (E15).
- **07:41:36.545Z** — last real-user request. No user traffic after this point.
- **07:41:44Z** — complaint raised (`startsAt`); **07:41:48Z** — investigation entered.
- **07:42:06Z onward** — investigator baseline probes (`/health`, `/metrics`).
- **07:43:21.476Z** — first `/products/3` probe → unhandled `ZeroDivisionError` (E5, E6).
- **07:43:27.164Z** — reproduced (E7).
- **07:48:29Z** — third, deliberately disconfirming `/products/3` probe → 500 again (E8).

No configuration, deploy, or flag-change marker appears anywhere in the log — no
`chaos_enabled`, `chaos_disabled`, `chaos_failure`, or `simulated_exception` event exists.

## Investigation

**Baseline.** `/health` returned 200 with `uptime_seconds` 39. That low uptime was the first
real signal: the whole observable history is this one short-lived process, 18 log lines at the
time of reading, with no rotated backups. Metrics showed all-200/201 counters, no
`http_exceptions_total` series at all, and `faultline_chaos_enabled 0`.

**Triage.** The complaint names no symptom, so no lens domain could be excluded by evidence;
all three available lenses (software-defect, interfaces, infra-process) ran in parallel, each
blind to the others. They converged independently on the same picture: no live failure, and a
deterministic per-input 500 on `/products/3` that only investigator probes had triggered. The
interfaces lens usefully ruled out the probabilistic shapes — a fixed-input signature is not a
partial rollout or a flaky dependency.

**Deep-dive: skipped by design.** The software-defect evidence was already deterministic and
complete — stack trace, throwing expression, the distinguishing input, and counter-level
attribution. Per the skill, such a hypothesis goes straight to the judge rather than
re-proving itself.

**Judge.** The adversarial judge did real damage and is worth recording honestly. It refused
to bless three things: (a) an unaccounted 200 on the `/products/{product_id}` route that could
have concealed a successful `/products/3` request, which would have killed "deterministic";
(b) the possibility that the two `POST /orders` had *decremented* product 3's stock to zero,
making the zero user-created state rather than a static condition; (c) "deterministic" resting
on n=2 from a single prober seconds apart. It also caught a genuine arithmetic error in my
baseline — I had counted 8 user requests where the log shows 9.

**Round two** settled all three from telemetry. Enumerating every `/products*` line (E14)
reconciled the route counters exactly (5×200 = products 1, 2, 5 from users plus two
`/products/4` probes; the "unaccounted" 200 was simply my own second `/products/4` probe) and
showed **no `/products/3` request has ever returned 200**. The `order_created` events (E15)
name products 1 and 2 only, so no order in this lifetime touched product 3's stock. A third,
deliberately disconfirming `/products/3` probe (E8) failed identically, taking the sample to
3/3. The judge's remaining objections were temporal rather than logical — they are recorded as
Gaps, not waved away.

## Hypotheses

### H1 — a fault is actively degrading the shop service for users — *invalidated*
All 9 user requests returned 200/201 (E2, E3, E4, E14); the only non-2xx results on the whole
route are 2 investigator 500s and 1 investigator 404 (E11); both orders succeeded (E17). No
user-attributed error exists in the process lifetime. Scoped, per Gaps, to that lifetime.

### H2 — `/products/3` 500s by division by zero on `units_in_stock == 0` — *validated*
E5 carries the throwing frame verbatim:
`"turnover_score": units_ordered / product["units_in_stock"]`, raising `ZeroDivisionError`.
E9 shows product 3 is the sole catalog row with `units_in_stock: 0`. Three attempts, three
identical failures (E6, E7, E8), zero successes on that id (E14), and the exception counter
(E10) and 500 counter (E11) both equal exactly the investigator's attempt count. The judge's
n=2 objection was answered by raising it to 3/3 and by proving the absence of any 200.

### H3 — the defect has affected real users — *invalidated*
Every 500 carries a `konan-*` id (E6, E7, E8). The attribution is structurally sound rather
than merely observed: E6/E7 prove a 500 *does* emit a normal access line, so a user hit could
not have gone unlogged, and E11's 500 count matches the investigator's probes exactly. E15
further shows no order touched product 3. The claim holds for this process lifetime and is
explicitly not extended beyond it.

### H4 — injected chaos or operator degradation — *invalidated*
`faultline_chaos_enabled 0` (E12) and no `chaos_*` event in the log. The verdict leans mainly
on H2 already explaining both 500s with a real stack trace (E5); the bare-negative weakness of
the log argument is recorded in Gaps.

### H5 — process instability or saturation — *invalidated*
Exactly one startup marker (E1); `process_uptime_seconds` advanced monotonically across four
scrapes (42.99 → 126.37 → 154.76 → 218.21) with no reset, so no restart occurred; peak RSS was
identical at 46,858,240 bytes across scrapes (E13). Latency never degraded — the only
double-digit sample, 12.2 ms, is the cold-start `/health`; business paths stayed ≤ 1.8 ms.

### H6 — product 4's null price is an active read-path defect — *invalidated*
`/products/4` returns 200 with `price: null` and `turnover_score: 0.0` (E16). The read path
tolerates the null, so it is an anomaly, not a fault. The write path is untested — see Gaps.

## Safe next steps

All read-only; remediation is out of scope for this journal.

1. Treat `/products/3` as a real defect ticket despite the quiet shift — it is deterministic,
   customer-triggerable, and invisible to error-rate alerting until a customer finds it.
2. Ask whether any *other* catalog row can reach `units_in_stock: 0`. Product 3 is the only one
   today (E9), but if the order path decrements stock, this defect is a general
   sold-out-product bug rather than a single bad row. That question needs the source, not the
   telemetry surface.
3. Confirm whether product 4's `price: null` is intentional for a "Mystery Box" product before
   assuming it is a data error — and check the order/pricing path against it, which needs a
   write surface this investigation does not have.
4. Consider whether log retention across restarts is adequate. This investigation could see
   only ~4 minutes of history; a handover check deserves more.

## Gaps

The frontmatter list in full: no pre-restart log history (so all claims are scoped to this
process, and "no user has *ever* hit product 3" is explicitly not established); no way to tell
whether product 3's zero stock was seeded or written; no positive control proving chaos toggles
would have been logged; a thin and stale user sample (9 requests in one 8.4-second burst, none
in the last several minutes); only three of the six taxonomy classes have a dedicated lens
(load-saturation, third-party and data-db were covered only incidentally); the order write path
could not be exercised against products 3 or 4 under the read-only boundary; and saturation was
judged from uptime and peak RSS alone, with no CPU, fd, thread or pool metrics on this surface.
