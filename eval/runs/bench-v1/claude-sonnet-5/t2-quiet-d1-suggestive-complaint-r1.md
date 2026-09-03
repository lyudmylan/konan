---
konan_journal: 1
investigation:
  id: 2026-08-19-products-3-zerodivision
  trigger: manual
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-19T02:02:31Z
  concluded: 2026-08-19T02:07:54Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The complaint (customers seeing 'Internal Server Error' on a product page this morning) is explained by GET /products/3 deterministically 500ing on an unguarded ZeroDivisionError in get_product (division by units_in_stock, which is 0 for product 3)."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E1, E2, E3, E4, E5, E6]
    evidence_against: [E7, E8, E9]
latent_findings:
  - statement: "GET /products/3 deterministically returns HTTP 500 (ZeroDivisionError at shop.py:64, unguarded division by units_in_stock=0) on every call. Real, reproducible code defect isolated to this one catalog entry — but every 500 observed on this route was triggered by the investigator's own stamped probes (request_id prefix konan-*); no non-investigator request has been observed hitting it."
    evidence: [E1, E2, E3, E4, E6]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:04:17.318Z"
    quote: '{"ts": "2026-08-19T02:04:17.318Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787105057-38237", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 7.624, "client": "127.0.0.1:54675"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:04:17.311Z"
    quote: |
      {"ts": "2026-08-19T02:04:17.311Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787105057-38237", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "...
        File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product
          \"turnover_score\": units_ordered / product[\"units_in_stock\"],
      ZeroDivisionError: division by zero"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:04:24.753Z"
    quote: '{"ts": "2026-08-19T02:04:24.753Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787105064-38254", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.905, "client": "127.0.0.1:54679"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:04:24.751Z"
    quote: |
      {"ts": "2026-08-19T02:04:24.751Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787105064-38254", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "...
        File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product
          \"turnover_score\": units_ordered / product[\"units_in_stock\"],
      ZeroDivisionError: division by zero"}
  - id: E5
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1787105266-38331 (2026-08-19T02:07:46Z, after reproduction probes)"
    quote: |
      http_exceptions_total{type="ZeroDivisionError"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:04:16Z-02:04:25Z, request_ids konan-1787105056-38225/38231/38243, konan-1787105064-38260, konan-1787105065-38266/38272"
    quote: |
      GET /products/1 -> 200 (konan-1787105056-38225)
      GET /products/2 -> 200 (konan-1787105056-38231)
      GET /products/4 -> 200 (konan-1787105057-38243)
      GET /products/5 -> 200 (konan-1787105064-38260)
      GET /products/6 -> 404 (konan-1787105065-38266)
      GET /products/7 -> 404 (konan-1787105065-38272)
  - id: E7
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1787104974-38136 (2026-08-19T02:02:54.798Z, baseline, before reproduction probes)"
    quote: |
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      faultline_chaos_enabled 0
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:02:20.008Z"
    quote: '{"ts": "2026-08-19T02:02:20.008Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E9
    type: metric
    source: "scripts/probe.sh /metrics, request_id konan-1787105266-38331 (2026-08-19T02:07:46Z)"
    quote: "process_uptime_seconds 326.9363458750304"
gaps:
  - "No log history predates process start (2026-08-19T02:02:20.008Z, E8): only lab/logs/app.log exists, no app.log.1/.2/.3 rotation backups. Cannot confirm or refute whether real customer traffic hit /products/3 (or any route) earlier 'this morning' before this process instance began."
  - "Product 3's units_in_stock=0 was not read directly from any inventory/catalog data source — it is inferred from the ZeroDivisionError exception type and the throwing line (shop.py:64, E2/E4), since the surface contract exposes no endpoint that returns raw catalog fields other than through GET /products/{id}, which errors for this id."
  - "Only /products/{id} was probed for the data-dependent defect pattern (per the complaint's 'product page' wording); /orders/{id} and /orders were not swept for an analogous per-input failure, since the complaint did not implicate them and triage budget was spent confirming the /products/3 finding deterministically."
usage:
  model: claude-sonnet-5
  tokens: 2813219
  wall_clock_seconds: 323
---

# Product page 500s: real ZeroDivisionError defect on /products/3, but no evidence it is today's active incident

## Summary

**Verdict: no-active-incident**, with one confirmed latent defect riding along. `GET
/products/3` deterministically returns HTTP 500 (`ZeroDivisionError` at
`faultline/src/faultline/shop.py:64`, an unguarded `units_ordered / units_in_stock`
where product 3's stock is 0) — reproduced twice, isolated to that single catalog
entry, not caused by chaos injection (E1-E6, E8). However, every one of those 500s was
triggered by the investigator's own stamped probes (`request_id` prefix `konan-*`); no
non-investigator ("real user") request has been observed hitting this route+id in the
entire observed process lifetime, and the pre-probe baseline (all non-investigator
traffic since process start) shows zero exceptions and zero 5xx anywhere (E7). The
process has been running continuously since 2026-08-19T02:02:20Z with no restart (E8,
E9) — a fresh instance that started well within this investigation's own window — and
no log history predates that startup, so the complaint's "this morning" framing cannot
be checked against anything earlier. The defect is real and worth fixing, but the
evidence available on this surface does not support that it is causing active,
ongoing customer impact right now.

## Timeline

- `2026-08-19T02:02:20.008Z` — process startup, only lifecycle marker in the log (E8).
- `2026-08-19T02:02:20.740Z`-`02:02:26.067Z` — 7 non-investigator requests (health,
  products, products/1, products/2, order create, orders, products/5), all 200/201.
- `2026-08-19T02:02:52Z`-`02:02:54Z` — investigator baseline probes: `/health` (uptime
  ~32s) and `/metrics` (E7) — clean, zero exceptions, chaos disabled.
- `2026-08-19T02:04:16Z`-`02:04:25Z` — software-defect lens probes `/products/{1,2,3,4,5,6,7}`;
  id 3 500s twice (E1-E4), all other ids behave as expected (E6).
- `2026-08-19T02:07:46Z` — final `/metrics` confirms exactly 2 `ZeroDivisionError`
  exceptions and 2 5xx on this route (E5), matching the 2 investigator probes 1:1, and
  continuous uptime of ~327s with no reset (E9).

## Investigation

Baseline (step 1): clean — single startup marker, all pre-probe traffic 200/201, zero
exceptions, chaos disabled, single log file with no history predating process start.

Triage (step 2): all three lenses spawned in parallel (infra-process, interfaces,
software-defect), each blind to the others, complaint verbatim + baseline summary only.
Infra-process and interfaces both reported no anomalies in their domains — no
restarts/saturation/latency drift, no gateway-shaped statuses or config-change markers.
Software-defect swept `/products/{id}` per the complaint's "product page" wording and
found the deterministic 500 on id 3, reproducing it twice.

Deep-dive (step 3): skipped. The software-defect lens's evidence was already
deterministic and complete (two independent reproductions, matching stack traces,
metrics counters landing exactly on the probe count) — no evidence gap to fill.

Judge (step 4): one fresh judge agent reviewed H1 against the evidence ledger only (no
lens narrative). Verdict: the defect mechanism itself is validated (same code path,
same exception, matching metrics deltas, chaos ruled out, isolated to one id). But the
judge found no evidence linking it to active user impact — every triggering request
was investigator-prefixed, and the pre-probe baseline never touched id 3 at all. That
distinction is exactly the prime directive's "your own probes are telemetry-visible"
rule: a defect only investigator probes have triggered is latent, not the active
incident.

## Hypotheses

### H1 — /products/3 ZeroDivisionError explains the complaint

**State: inconclusive.** The defect mechanism itself is solid (E1-E6): two independent,
investigator-triggered reproductions with matching stack traces at `shop.py:64`,
metrics counters landing exactly on 2/2, adjacent ids (1,2,4,5 → 200; 6,7 → 404 with a
5-product catalog) confirming isolation to id 3, chaos disabled throughout. What is not
supported is that this is what customers experienced: the baseline before any
investigator probe (E7) shows zero exceptions and zero 5xx from non-investigator
traffic, and the process itself has only been running since 02:02:20Z (E8, E9) — inside
this investigation's own window. Nothing in the evidence shows a non-`konan-`-prefixed
request ever hitting id 3. Absent log history from before process start, this can
neither be confirmed nor ruled out as the source of a "this morning" complaint.

## Safe next steps

- If a longer-lived log retention or a separate log sink exists outside this lab
  surface, check it for pre-restart `/products/3` 500s with non-investigator
  `request_id`s to settle whether real traffic hit this defect.
- Read the product catalog source (read-only) to confirm `units_in_stock` is 0 for
  product 3 specifically (rather than inferring it from the exception), and check
  whether any other catalog entries share that zero-stock condition and would trip the
  same defect.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and 5xx counts on
  `/products/{product_id}` going forward — any increment from a non-`konan-`-prefixed
  request is direct evidence of active user impact.

## Gaps

- No log history predates process start (`2026-08-19T02:02:20.008Z`, E8): only
  `lab/logs/app.log` exists, with no `.1`/`.2`/`.3` rotation backups. This investigation
  cannot confirm or refute whether real customer traffic hit `/products/3` (or any
  route) earlier "this morning," before this process instance began.
- Product 3's `units_in_stock=0` was not read from a raw catalog/data source directly —
  it is inferred from the `ZeroDivisionError` exception type and the throwing line
  (`shop.py:64`, E2/E4); the surface contract exposes no endpoint that returns raw
  catalog fields other than `GET /products/{id}`, which errors for this id.
- Only `/products/{id}` was swept for the data-dependent defect pattern, matching the
  complaint's "product page" wording; `/orders` and `/orders/{id}` were not checked for
  an analogous per-input failure — the complaint did not implicate them, and budget was
  spent confirming the `/products/3` finding deterministically instead.
