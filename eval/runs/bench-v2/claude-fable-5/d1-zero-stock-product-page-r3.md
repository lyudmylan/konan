---
konan_journal: 2
investigation:
  id: 2026-11-02-products-3-zero-stock-500s
  trigger: "manual (/konan, alertname human-report, fingerprint human-1793628514, startsAt 2026-11-02T14:08:34Z; investigation started 2026-11-02T14:08:49Z - trigger latency 15s)"
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-02T14:08:49Z
  concluded: 2026-11-02T14:16:00Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The get_product handler (shop.py line 64) divides units_ordered by product['units_in_stock'] with no guard for zero stock; product 3 ('Unobtainium Ingot') has units_in_stock 0, so every GET /products/3 raises ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The GET /products/{id} handler computes turnover_score as units_ordered / product['units_in_stock'] without a zero guard (shop.py line 64); product 3 has units_in_stock 0, so every GET /products/3 raises ZeroDivisionError and returns 500, while products with nonzero stock return 200."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E5, E6, E7, E9, E10, E13, E14]
    evidence_against: []
  - id: H2
    statement: "An internal chaos/degradation switch injects the 500 errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E12]
  - id: H3
    statement: "A process crash or restart loop degrades the service and causes the errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E4, E11, E12]
  - id: H4
    statement: "A gateway tier or an external dependency fails and produces the errors."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E4, E6, E10]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:08:12.179Z"
    quote: '{"ts": "2026-11-02T14:08:12.179Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:08:19.166Z (stack trimmed to the final frame)"
    quote: |-
      {"ts": "2026-11-02T14:08:19.166Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "0c33c50d7e23", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:08:19.177Z"
    quote: '{"ts": "2026-11-02T14:08:19.177Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "0c33c50d7e23", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 12.031, "client": "127.0.0.1:58544"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:08:22.305Z"
    quote: '{"ts": "2026-11-02T14:08:22.305Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "943ddf442329", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.801, "client": "127.0.0.1:58546"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T14:08:25.496Z (last user-traffic 500; later /products/3 hits carry konan-* investigator ids)"
    quote: '{"ts": "2026-11-02T14:08:25.496Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "6d146d8ee888", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 5.984, "client": "127.0.0.1:58549"}'
  - id: E6
    type: metric
    source: "GET /metrics @ 2026-11-02T14:09:06Z (request_id konan-1793628546-92565)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
  - id: E7
    type: metric
    source: "GET /metrics @ 2026-11-02T14:09:06Z (request_id konan-1793628546-92565)"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 4'
  - id: E8
    type: metric
    source: "GET /metrics @ 2026-11-02T14:09:06Z (request_id konan-1793628546-92565)"
    quote: "faultline_chaos_enabled 0"
  - id: E9
    type: probe
    source: "GET /products (request_id konan-1793628739-92686)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001696s request_id=konan-1793628739-92686
  - id: E10
    type: probe
    source: "GET /products/3 (request_id konan-1793628739-92691)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793628739-92691"}
      -- HTTP 500 in 0.005459s request_id=konan-1793628739-92691
  - id: E11
    type: probe
    source: "GET /health @ 2026-11-02T14:09:05Z (request_id konan-1793628545-92560)"
    quote: |-
      {"status":"ok","uptime_seconds":53.38685929100029}
      -- HTTP 200 in 0.016394s request_id=konan-1793628545-92560
  - id: E12
    type: metric
    source: "GET /metrics @ ~2026-11-02T14:13:15Z (request_id konan-1793628795-92700)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 7
      http_exceptions_total{type="ZeroDivisionError"} 7
      faultline_chaos_enabled 0
      process_uptime_seconds 303.54553600004874
      process_max_rss_bytes 48676864
  - id: E13
    type: probe
    source: "GET /products/4 (request_id konan-1793628954-92732)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.003824s request_id=konan-1793628954-92732
  - id: E14
    type: probe
    source: "GET /products/5 (request_id konan-1793628954-92737)"
    quote: |-
      {"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001789s request_id=konan-1793628954-92737
gaps:
  - "No telemetry exists before the process start at 2026-11-02T14:08:12.179Z (single log file, no rotated backups), so the complaint's 'started within the last hour' onset is checkable only from 14:08:12; the first observed failure is 14:08:19.177Z."
  - "No chaos-state reading exists inside the user-failure window 14:08:12-14:08:25; the gauge reads 0 at 14:09:06Z and ~14:13:15Z, bracketing the window (the judge's settling item for H2)."
  - "How product 3's units_in_stock reached 0 is outside the surface: the log shows no order for product 3, and the data layer is not probeable; the zero may be seed state or may predate the log window."
  - "Process continuity is inferred from uptime-gauge arithmetic and counter monotonicity; a supervisor/OS process record (PID, start time) is outside the surface contract (the judge's settling item for H3)."
  - "The surface contract (docs/lab.md) documents a single service with no gateway tier; the judge's settling evidence for H4 (a front-tier access log for request_id 0c33c50d7e23) does not exist on this surface."
usage:
  model: claude-fable-5
  tokens: 2035336
  wall_clock_seconds: 431
---

# Product page /products/3 returns 500: unguarded division by zero on a zero-stock product

## Summary

Root cause identified. `GET /products/3` fails deterministically with HTTP 500 because
the `get_product` handler computes `"turnover_score": units_ordered /
product["units_in_stock"]` (shop.py line 64) with no guard for zero stock, and product 3
("Unobtainium Ingot") is the only product with `units_in_stock: 0` (E2, E9). Every hit on
that page fails — four user requests between 14:08:19Z and 14:08:25Z (E3, E5) and every
investigator reproduction after them (E10) — while all other routes, including sibling
product pages, stay healthy (E4, E13, E14). The exception counter and the 500 counter
move one-for-one (4/4 then 7/7: E6, E7, E12), so this single defect accounts for every
failure; no second failure mode hides in the counts. Chaos injection is off (E8, E12),
the process never restarted (E1, E11, E12), and the error body is the application's own
exception, not a gateway shape (E10). Confidence is high: the defect was reproduced on
demand and the judge validated H1 against adversarial review. The defect is still active
at conclusion — any user who opens the product 3 page will get the error.

## Timeline

- **14:08:12.179Z** — process start, "faultline 0.1.0 started" (E1). The only
  change-marker in telemetry; no deploy/config/flag events appear in the log.
- **14:08:13–14:08:15Z** — user traffic: `/products/1`, `/products/2` → 200.
- **14:08:17.106Z** — `POST /orders` → 201 (order 1, product 1).
- **14:08:19.166/.177Z** — first user failure: ZeroDivisionError, `GET /products/3` → 500
  (E2, E3).
- **14:08:20–14:08:25.496Z** — three more user 500s on `/products/3`, interleaved with a
  `/products/2` → 200 (E4) and a successful `POST /orders` → 201; last user 500 at
  14:08:25.496Z (E5).
- **14:08:34Z** — complaint raised (support report via /konan; `startsAt`).
- **14:08:49Z** — investigation started (trigger latency 15 s).
- **14:09:05–06Z** — baseline: health 200 (E11); metrics show 4×500 = 4×ZeroDivisionError,
  chaos off (E6, E7, E8).
- **14:10:25Z** — triage lens reproduces the 500 with a stamped probe.
- **14:12:19Z** — `/products` shows product 3 stock 0 (E9); `/products/3` → 500
  reproduced (E10).
- **14:13:15Z** — final scrape: 7×500 = 7×ZeroDivisionError = 4 user + 3 investigator
  probes; uptime 303.5 s, monotonic; chaos still 0 (E12).
- **14:14:14Z** — `/products/4` and `/products/5` → 200 with turnover_score computed
  (E13, E14).
- **14:16:00Z** — concluded.

## Investigation

Baseline (health, metrics, log tail) already carried the signal: four user 500s on
`GET /products/3` with ZeroDivisionError stacks, siblings healthy. Three triage lenses
ran in parallel, each blind to the others: **software-defect** confirmed the
deterministic per-input failure and found the zero-stock datum (E9, E10);
**infra-process** found its domain clean — one startup, monotonic uptime, chaos off, no
saturation (E1, E8, E11, E12); **interfaces** found no dependency, contract, or gateway
evidence and anchored the onset to the startup marker (E1, E6, E10). The triage evidence
was deterministic and complete, so the hypotheses skipped deep-dive and went straight to
a fresh adversarial judge, which saw only the hypothesis list and verbatim quotes. The
judge validated H1 and invalidated H2–H4, noting one open sampling point (siblings
checked only at products 1–2); closing probes on `/products/4` and `/products/5`
(E13, E14) answered it. A full-log grep for `chaos_enabled`, `chaos_disabled`,
`chaos_failure`, and `simulated_exception` events returned none (a negative check; not
quotable as a ledger entry).

## Hypotheses

### H1 — zero-stock division defect (validated)

The stack names the exact expression and line (E2); the request_id ties the exception to
the user-visible 500 (E2→E3); `/products` shows product 3 as the only zero-stock product
(E9); the failure reproduces on demand (E10); every product with nonzero stock returns
200 with `turnover_score` computed (E4, E13, E14); and the 500 counter equals the
ZeroDivisionError counter at both scrapes (E6, E7, E12), so this defect accounts for all
failures. Classic data-dependent software defect: most inputs succeed, one specific
input fails, deterministically.

### H2 — chaos/degradation switch (invalidated)

`faultline_chaos_enabled` is 0 at both scrapes bracketing and following the failures
(E8, E12), no chaos events appear in the log, and H1 leaves no residual failures for an
injector to explain.

### H3 — crash/restart loop (invalidated)

Exactly one startup event (E1); uptime arithmetic puts the start at the same instant at
both readings (E11: 53.4 s at 14:09:05; E12: 303.5 s at ~14:13:15); counters rise
monotonically (4→7, never reset); and a 200 lands three seconds after a 500 on the same
route (E4), which no degraded-process model explains.

### H4 — gateway or dependency failure (invalidated)

The error body is the application's own, with a Python `exception_type` and an echoed
request id (E10), not a 502/503/504 gateway shape; the stack ends in first-party code
(E2); failures take 5–12 ms, compute-shaped rather than timeout-shaped (E3, E5, E10);
and all failures confine to one route and one status while a sibling succeeds in the
same seconds (E4, E6).

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Have engineering read `get_product` in faultline's shop.py at line 64 — the
  turnover_score expression needs a zero-stock guard; any product whose stock reaches 0
  will reproduce this incident.
- Find out, through operator-side access, how product 3's `units_in_stock` became 0 —
  seed data or a stock depletion before 14:08:12Z; telemetry cannot see it (gap 3).
- Watch `http_exceptions_total{type="ZeroDivisionError"}` against non-investigator
  traffic for continued user impact until the defect is fixed; the page still fails.
- Observation while reading `/products`: product 4 ("Mystery Box") carries
  `"price": null` (E9, E13). It served 200 here, but a null price is a datum worth a
  look by the same team.

## Gaps

1. **Pre-window telemetry.** The log starts at the process start (14:08:12.179Z, E1)
   and has no rotated backups, so the complaint's "within the last hour" onset cannot be
   traced earlier. First observed failure: 14:08:19.177Z.
2. **Chaos state inside the user-failure window.** The gauge was read at 14:09:06Z and
   ~14:13:15Z (both 0); no reading exists inside 14:08:12–14:08:25. The judge named this
   as the settling evidence for H2; the bracket plus the absence of chaos log events is
   the honest best available.
3. **Origin of the zero stock.** No order for product 3 appears in the log, and the data
   layer is outside the probe allowlist; whether stock 0 is seed state or predates the
   log window is unobservable from this surface.
4. **Process identity.** No supervisor/OS record (PID, start time) is on the surface;
   process continuity rests on uptime arithmetic and counter monotonicity (judge's
   settling item for H3).
5. **No front tier.** The surface contract documents a single service; the judge's
   settling evidence for H4 (a front-tier access log) does not exist in this lab.
