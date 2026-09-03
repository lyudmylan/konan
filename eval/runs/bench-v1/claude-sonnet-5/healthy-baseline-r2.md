---
konan_journal: 1
investigation:
  id: 2026-08-19-routine-handover-check
  trigger: "manual (/konan adapter; complaint fingerprint human-1787102842, startsAt 2026-08-19T01:27:22Z, investigation start 2026-08-19T01:27:30Z — trigger latency 8s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: "2026-08-19T01:27:30Z"
  concluded: "2026-08-19T01:35:18Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "GET /products/{id} raises an unhandled ZeroDivisionError (HTTP 500) when the requested product's units_in_stock is 0, from an unguarded division in the turnover_score calculation (shop.py:64). Confirmed reproducibly on product_id=3. Only investigator-stamped probes triggered it in this process life; no organic/simulated traffic requested /products/3."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7]
    evidence_against: []
  - id: H2
    statement: "Product id=4 ('Mystery Box') carries a null price field, unlike every other catalog product which has a numeric price — a data anomaly that could break total_price computation if the product were ever ordered. No order, organic or investigator-issued, has ever referenced product_id=4, and POST /orders is outside the investigator's read-only surface, so whether it actually breaks order creation is unconfirmed."
    incident_class: data-db
    state: validated
    evidence_for: [E8, E9, E10]
    evidence_against: []
latent_findings:
  - statement: "The /products/3 ZeroDivisionError (H1) is a live, reproducible defect on the catalog's only zero-stock item, but it has caused zero observed user impact in this process's life — every request that touched /products/3 carried an investigator konan-* request id."
    evidence: [E3, E4, E6, E7]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:27:07.857Z — organic/simulated traffic before the investigation, unstamped request id"
    quote: |-
      {"ts": "2026-08-19T01:27:07.857Z", "message": "GET /products/1 -> 200", "request_id": "be9c2061a645", "event": "request", "method": "GET", "path": "/products/1", "status": 200}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:27:15.158Z — organic/simulated traffic before the investigation, unstamped request id"
    quote: |-
      {"ts": "2026-08-19T01:27:15.158Z", "message": "GET /products/5 -> 200", "request_id": "6a2c1c7f0127", "event": "request", "method": "GET", "path": "/products/5", "status": 200}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:30:41.895Z — unhandled exception from the deep-dive's reproduction of /products/3, stack trimmed to the throwing frame"
    quote: |-
      {"ts": "2026-08-19T01:30:41.895Z", "level": "ERROR", "message": "unhandled exception: division by zero", "request_id": "konan-1787103041-36701", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "...File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:30:41.903Z — resulting response for the same request id as E3"
    quote: |-
      {"ts": "2026-08-19T01:30:41.903Z", "message": "GET /products/3 -> 500", "request_id": "konan-1787103041-36701", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.196}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T01:30:48.476Z — second independent reproduction"
    quote: |-
      {"ts": "2026-08-19T01:30:48.476Z", "level": "ERROR", "message": "unhandled exception: division by zero", "request_id": "konan-1787103048-36713", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"}
  - id: E6
    type: metric
    source: "probe /metrics, request_id=konan-1787103176-36753 @ 2026-08-19T01:32:56Z — closing counter block, taken after both reproductions"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 2
  - id: E7
    type: probe
    source: "probe /products, request_id=konan-1787103176-36759 @ 2026-08-19T01:32:56Z — full catalog, confirms product 3's zero stock and isolates the anomaly on product 4"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E8
    type: probe
    source: "probe /products/4, request_id=konan-1787102970-36593 @ 2026-08-19T01:29:30Z"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
  - id: E9
    type: probe
    source: "probe /products, request_id=konan-1787103176-36759 @ 2026-08-19T01:32:56Z — same catalog snapshot as E7, cited again for product-4 isolation"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E10
    type: log
    source: "lab/logs/app.log — probe /orders, request_id=konan-1787102971-36600 @ 2026-08-19T01:29:31Z"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-08-19T01:27:10.976+00:00"},{"id":2,"product_id":2,"quantity":2,"total_price":46.0,"created_at":"2026-08-19T01:27:12.037+00:00"}]
gaps:
  - "POST /orders (order creation) is outside the investigator's read-only probe surface; H2's causal claim — that ordering product 4 would break total_price computation — could not be tested and stays unconfirmed."
  - "The organic-traffic-absence claim in H1 (no non-investigator request ever hit /products/3) rests on two representative log lines (E1, E2) and the request-id-prefix convention, not an exhaustive count; the judge flagged this as the weakest-supported clause."
  - "The investigation window covers ~350s of process uptime with real business traffic confined to the first ~9s after startup (10 requests, then silence); slower-onset failure modes outside this window are unobserved, not excluded."
  - "faultline's source code and the eval scenario fixtures are deliberately outside investigator reach (docs/lab.md); product 4's intended semantics (e.g. a deliberately-unpriced 'mystery' item vs. a data defect) cannot be settled from telemetry alone."
usage:
  model: claude-sonnet-5
  tokens: 2214438
  wall_clock_seconds: 468
---

# Routine handover check — no active incident; one latent defect, one open data anomaly

## Summary

**Verdict: no active incident.** A routine on-call handover check with no specific
user reports. Baseline was clean on every axis a human would ask about first: healthy
process, zero exceptions, all-2xx traffic, chaos disabled. The triage sweep (three
lenses, blind to each other) surfaced two items worth naming to the incoming
on-call, neither of which is currently hurting a user: (1) a confirmed, deterministic
`ZeroDivisionError` on `GET /products/3` (H1) — real, reproducible, but only ever
triggered by this investigation's own probes, never by traffic before it; and (2) an
isolated `price: null` on product 4 "Mystery Box" (H2) — a genuine data anomaly, never
exercised by any order, whose downstream effect on order creation could not be tested
because order creation sits outside the investigator's read-only surface. Confidence
is high on the descriptive facts for both; H1's mechanism is fully confirmed, H2's
consequence is explicitly unconfirmed and flagged as such.

## Timeline

- **01:27:05.970Z** — process startup (only startup event in the log; uptime rose
  monotonically at every later check, E6).
- **01:27:06–01:27:15Z** — pre-investigation organic/simulated traffic: `/health` x2,
  `/products`, `/products/1`, `/products/2` x2 orders, `/orders`, `/products/5` — all
  200/201 (E1, E2).
- **01:27:22Z** — complaint raised (`startsAt`); **01:27:30Z** — investigation started
  (8s trigger latency).
- **01:27:46–01:29:03Z** — baseline probes (`/health`, `/metrics`) clean: uptime
  monotonic, `faultline_chaos_enabled 0`, `http_exceptions_total` empty.
- **01:29:03–01:30:37Z** — triage sweep (infra-process, interfaces, software-defect
  lenses, single message, blind to each other). Infra-process: no anomalies.
  Software-defect: no anomalies from its own probing (404s on invalid ids were clean).
  Interfaces: flagged `price: null` on product 4 (E8) as a minor shape anomaly.
- **01:30:41.895Z, 01:30:48.476Z** — deep-dive reproduces `GET /products/3` →
  `ZeroDivisionError` → 500, twice, deterministically (E3, E4, E5).
- **01:32:56Z** — closing counters: `http_exceptions_total{type="ZeroDivisionError"} 2`
  (E6), full catalog snapshot (E7/E9) isolates the anomaly to product 3 (stock) and
  product 4 (price); order history (E10) shows product 4 was never ordered.
- **01:33:xxZ** — judge validates both H1 and H2 as stated, with a caveat on H1's
  "no organic traffic" sub-claim (evidence is representative, not exhaustive).
- **01:35:18Z** — concluded.

## Investigation

Baseline (`/health`, `/metrics`) was clean: process 40s old at first check with no
restart markers, `faultline_chaos_enabled 0`, zero exception counters, all logged
requests 200/201. Because the complaint was vague ("anything wrong… no specific user
reports"), all three lenses ran anyway — a vague complaint excludes no domain.

Infra-process and software-defect lenses came back clean from their own probing.
Interfaces lens surfaced one item: product 4's `price: null`, unlike every other
product's numeric price — not a formal schema violation (`/openapi.json` declares
`/products` responses as unconstrained), but an inconsistent shape worth naming.

I confirmed the product-4 fact directly (`GET /products/4`, E8) and checked order
history (`GET /orders`, E10): no order has ever referenced product 4. One deep-dive
agent then tested this as a hypothesis (software-defect lens, confirm-and-refute
mode) and, in the course of probing adjacent products for comparison, independently
reproduced a second, unrelated, fully deterministic defect: `GET /products/3` throws
`ZeroDivisionError` (`shop.py:64`, dividing by `units_in_stock` which is 0 for that
product) — reproduced twice with full stack traces (E3, E4, E5). I verified myself,
reading the raw log, that every request touching `/products/3` in this process's
life carried a `konan-*` investigator request id; pre-investigation organic traffic
only ever hit products 1, 2, and 5 (E1, E2) — so per the prime directive on
investigator-visible probes, this is a **latent** finding, not active user impact.

Both hypotheses (H1: the ZeroDivisionError mechanism plus its zero-user-impact
claim; H2: the null-price anomaly plus its untested-consequence claim) went to a
fresh, blind judge with only the hypothesis statements and verbatim evidence — no
narrative. Both were validated exactly as scoped: the judge confirmed H1's mechanism
and its impact claim (with a caveat that the "no organic traffic" evidence is
representative rather than exhaustive), and confirmed H2's descriptive claims while
noting it correctly avoids asserting the untested causal consequence.

Budget: one triage round (3 lenses), one deep-dive, one judge pass — both
hypotheses resolved without needing a second round.

## Hypotheses

### H1 — `/products/3` ZeroDivisionError

**Validated.** `shop.py:64` divides `units_ordered / units_in_stock` when computing
`turnover_score`; product 3 has `units_in_stock: 0` (E7), so every request to
`GET /products/3` throws (E3, E5) and returns 500 (E4). `http_exceptions_total`
confirms exactly 2 occurrences (E6), matching my 2 reproductions. No organic request
touched `/products/3` in this process's life (E1, E2 show organic traffic elsewhere);
every 500 in the log carries a `konan-*` id. Recorded as a latent finding — real,
reproducible, zero current user impact.

### H2 — product 4 null price

**Validated** (as scoped — descriptive claims only). Product 4 is the only catalog
item with `price: null`; all others (1, 2, 3, 5) have numeric prices (E7, E9). No
order, ever, has referenced product 4 (E10). The hypothesis explicitly does not
claim ordering it would fail — that would require `POST /orders`, which is outside
this investigation's read-only surface — so it stays an open data anomaly, not a
confirmed defect.

## Safe next steps

- Nothing requires immediate action for the handover — no user-facing failure is
  in progress.
- `/products/3` will 500 the moment any real user opens that product page; watching
  `http_exceptions_total{type="ZeroDivisionError"}` and the `/products/{product_id}`
  500 series is the read-only early-warning signal.
- Product 4's null price is worth a read-only look at the catalog source of truth
  (is it intentional — a "reveal at checkout" item — or a data-entry gap?) before it
  is ever ordered; if an eval-side/controlled order against product 4 is authorized
  outside this investigation, that would settle H2's open causal question directly.

## Gaps

Four, matching the machine core:

1. **H2's causal claim is untestable from here.** Order creation (`POST /orders`)
   is not on the investigator's GET-only allowlist, so whether a null price actually
   breaks `total_price` computation is unconfirmed.
2. **H1's "no organic traffic" claim rests on representative, not exhaustive,
   evidence.** Two log lines (E1, E2) plus the `konan-*` request-id convention
   support it; a full count of every `/products/3` request by id-prefix would make
   it airtight, and the judge named this as the item's weakest-supported clause.
3. **Window is short.** ~350s of process uptime, with real business traffic
   confined to the first ~9 seconds after startup, then silence until my own
   probes. Slower-onset failure modes are unobserved, not excluded.
4. **Ground truth stays outside by design.** faultline's source and the eval
   scenario fixtures are off-limits (`docs/lab.md`); product 4's intended semantics
   can't be settled from telemetry alone.
