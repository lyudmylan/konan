---
konan_journal: 2
investigation:
  id: 2026-11-02-order-500s
  trigger: "manual (/konan adapter; complaint fingerprint human-1793643100, startsAt 2026-11-02T18:11:40Z, investigation start 2026-11-02T18:11:43Z — trigger latency 3s)"
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: "2026-11-02T18:11:43Z"
  concluded: "2026-11-02T18:20:25Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "faultline's create_order handler (shop.py:82) computes total_price = product[\"price\"] * order.quantity with no null-price guard; product 4 (\"Mystery Box\") is the catalog's only price=null row, so every order referencing it raises an unhandled TypeError and returns 500, while orders for priced products succeed."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "POST /orders fails with an unhandled TypeError at shop.py:82 in create_order — total_price multiplies product['price'] by the quantity, and the exception message's operand order ('NoneType' and 'int') proves the price was None; product 4 is the catalog's only null-price row, so orders for it 500 while orders for priced products succeed (observed for products 1 and 2). Data-dependent code defect on the write path; active user impact, three failures in one burst."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10]
    evidence_against: []
  - id: H2
    statement: "The 500s are caused by process instability — crash/restart loop or resource saturation — rather than application code."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E7, E11]
  - id: H3
    statement: "The 500s come from injected degradation (chaos mode), a failing dependency, or a gateway/proxy failure rather than the application's own handler code."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E7, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:11:19.685Z — process start, the only startup in the window"
    quote: |-
      {"ts": "2026-11-02T18:11:19.685Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:11:26.658Z — request_id eadf778545b6 (stack trimmed to the raise site)"
    quote: |-
      {"ts": "2026-11-02T18:11:26.658Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "eadf778545b6", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:11:26.668Z — request_id eadf778545b6"
    quote: |-
      {"ts": "2026-11-02T18:11:26.668Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "eadf778545b6", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 11.574, "client": "127.0.0.1:60025"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:11:27.725Z–27.729Z — request_id 3ad84800c6fa, identical message and raise site to E2"
    quote: |-
      {"ts": "2026-11-02T18:11:27.725Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "3ad84800c6fa", "event": "unhandled_exception", "exception_type": "TypeError"}
      {"ts": "2026-11-02T18:11:27.729Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "3ad84800c6fa", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.494, "client": "127.0.0.1:60026"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:11:30.844Z–30.848Z — request_id 32f752fede53, identical message and raise site to E2"
    quote: |-
      {"ts": "2026-11-02T18:11:30.844Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "32f752fede53", "event": "unhandled_exception", "exception_type": "TypeError"}
      {"ts": "2026-11-02T18:11:30.848Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "32f752fede53", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 4.953, "client": "127.0.0.1:60028"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T18:11:23.548Z, 18:11:24.599Z, 18:11:29.786Z — the three successful orders; the third lands between the second and third failures (E4, E5), proving the write path stayed alive mid-incident"
    quote: |-
      {"ts": "2026-11-02T18:11:23.548Z", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"ts": "2026-11-02T18:11:24.599Z", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
      {"ts": "2026-11-02T18:11:29.786Z", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E7
    type: metric
    source: "probe /metrics, request_id=konan-1793643142-98638 @ 2026-11-02T18:12:22Z — baseline, first investigator probe, taken after the whole failure burst"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 63.24067774997093
      process_max_rss_bytes 47857664
  - id: E8
    type: probe
    source: "probe /products, request_id=konan-1793643166-98649 @ 2026-11-02T18:12:46Z"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E9
    type: probe
    source: "probe /products/4, request_id=konan-1793643362-98780 @ ~2026-11-02T18:16:02Z"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
  - id: E10
    type: probe
    source: "probe /orders, request_id=konan-1793643362-98775 @ ~2026-11-02T18:16:02Z"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-02T18:11:23.548+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-02T18:11:24.599+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-02T18:11:29.786+00:00"}]
  - id: E11
    type: metric
    source: "probe /metrics, request_id=konan-1793643682-98887 @ 2026-11-02T18:19:42Z — closing reconciliation, ~540s after baseline"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
      http_exceptions_total{type="TypeError"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 602.6970511251129
      process_max_rss_bytes 47857664
gaps:
  - "Telemetry starts at process boot (E1, 18:11:19.685Z); nothing precedes it — the true onset is unverifiable. Within the observable window the defect is present from the first order burst, about four seconds after boot."
  - "Product-4 attribution is a closed inference, not a direct observation: POST bodies are not logged and failed orders emit no order_created event (E2, E4, E5 name no product_id), so no single log line names the failing product. The exception message's operand order ('NoneType' and 'int') proves the price operand was None; the catalog has exactly one null-price row (E8, E9); and the closing counter block shows no catalog-mutating traffic anywhere in the process lifetime (E11) — but no individual failing request was ever directly observed naming product 4."
  - "No read-only reproduction is possible: POST /orders is outside the probe allowlist by design (docs/lab.md is GET-only) — determinism rests on three identical failures already in the log, not a controlled reproduction by this investigation."
  - "'Keeps failing when they retry' is corroborated only by three identical failures inside one ~4-second burst (18:11:26.658Z–18:11:30.844Z; E2, E4, E5); no later retry traffic was observed — the closing counter block (E11) shows zero additional POST /orders of either status across the ~540s investigation window."
  - "User-vs-investigator attribution rests on the request-id convention: the three failing requests and all six order attempts carry plain hex request ids, not the konan-* prefix the probe tool stamps, and all predate the investigator's first probe (first probe ~18:12:22Z, E7; failures 18:11:26Z–18:11:31Z) — read as end-user/complaint-matching traffic per the surface contract, not investigator-triggered."
  - "Whether product 4's null price is bad catalog data or unpriced-by-design (a 'Mystery Box' whose price is revealed at checkout) is outside this surface; the answer decides whether the safe next step is a data correction or an orderability guard."
usage:
  model: claude-sonnet-5
  tokens: 2758669
  wall_clock_seconds: 522
---

# Order-creation 500s — unguarded null price on product 4 (Mystery Box)

## Summary

Root cause identified. The order-creation handler `create_order` (faultline
`shop.py:82`) computes `total_price = round(product["price"] * order.quantity, 2)`
with no null-price guard; product 4, "Mystery Box", is the catalog's only
`price: null` row (E8, E9), so every order for it raises an unhandled `TypeError`
and returns 500, while orders for priced products succeed — three identical user
failures in one burst, with a successful order landing *between* the second and
third failures on the same route (E4, E5, E6). The exception message's operand
order (`'NoneType' and 'int'`) is load-bearing: it proves the *price* was None, not
the quantity (E2). Process health, chaos state, and dependency shapes were checked
and ruled out (H2, H3 invalidated) — this matches the complaint exactly: some
customers fail every time (deterministic per product), others go through fine.
Impact is confined to orders referencing product 4 while its price is null, and any
product whose price becomes null would join the same failure mode.

## Timeline

All times UTC, from telemetry.

- **18:11:19.685Z** — process start, faultline 0.1.0 (E1); no telemetry precedes it.
- **18:11:23.548Z, 18:11:24.599Z** — two successful user orders, products 1 and 2
  (E6).
- **18:11:26.658Z** — first user failure: `TypeError` at `shop.py:82` in
  `create_order` → `POST /orders` 500, request `eadf778545b6` (E2, E3).
- **18:11:27.725Z** — second identical user failure, request `3ad84800c6fa` (E4).
- **18:11:29.786Z** — user success *between* failures: order 3, product 1 (E6) —
  the write path is alive mid-incident.
- **18:11:30.844Z** — third identical user failure, request `32f752fede53` (E5);
  last failure in the window.
- **18:11:40Z** — human complaint stamped (`startsAt`); **18:11:43Z** investigation
  start (trigger latency 3s).
- **18:12:22Z** — baseline: counters show `POST /orders` 201=3 / 500=3,
  `TypeError`=3, chaos off, uptime 63.2s (E7) — all six order attempts and all
  three failures already happened before this first probe.
- **18:12:46Z–18:16:02Z** — triage sweep: catalog's only null-price row is product
  4 (E8), confirmed by `/products/4` showing zero completed orders ever for it
  (E9); `/orders` lists only products 1/1/2, never 4 (E10).
- **18:19:42Z** — closing reconciliation: counters unchanged from baseline
  (201=3/500=3/TypeError=3), chaos still off, RSS unchanged, uptime monotonic to
  602.7s — no further order traffic during the whole investigation (E11).
- **18:20:25Z** — concluded.

## Investigation

Baseline showed the incident shape immediately: the only 5xx series in the counter
block was `POST /orders` 500=3 against 201=3 on the same route, with
`http_exceptions_total{type="TypeError"}` exactly matching (E7) — a data-dependent
write-path split, on a process that had already finished failing before the
investigator's first probe.

Triage ran three lenses in parallel, blind to each other, each given only its lens
file, the surface contract, the complaint verbatim, and the baseline summary.
Software-defect pulled the full stack trace (raise site `shop.py:82`, operation
`create_order`), confirmed the 1:1 TypeError-to-500 pairing, and read the catalog —
the only null-price row is product 4, with zero orders ever completed for it (E8,
E9, E10). Infra-process returned a clean domain: single startup, monotonic uptime,
flat RSS across a ~220s recheck, fail-fast millisecond durations on the failing
requests themselves, chaos gauge off on every read (E1, E7, and its own recheck
folded into E11) — explicitly ruling out crash/restart/saturation/toggle mechanisms.
Interfaces found the same null-price catalog row but attributed the mechanism to
the software-defect lens: no 502/503/504 anywhere, no config/flag/deploy/chaos
markers in the complete log, the stack terminating in local application arithmetic,
not a boundary or dependency frame (E2, E7).

Selection: **no deep-dives**. H1's evidence was already deterministic and complete
from triage — the null price is directly observed in the catalog, the raise site is
named in the stack, and the one remaining link (which product the failing orders
targeted) is structurally unfillable through this surface: POST bodies are not
logged and failed orders emit no `order_created` event. That is a gap to record,
not a query to run. All three hypotheses went straight to the judge.

The judge (fresh context, cited evidence only) validated H1 and invalidated H2 and
H3, flagging the same structural gap on its own — that product-4 attribution is an
elimination argument (the catalog's only null-price row), not a logged fact — while
confirming the count reconciliation leaves no residue: every POST /orders is
accounted for, and successes' totals match the catalog's non-null prices exactly.

Budget: one triage round (3 lenses), zero deep-dives of a permitted three, one
judge — concluded in round 1. Tokens: subagents alone consumed roughly 145k; the
orchestrator's own share is not measurable in an interactive session, so the
machine core records `tokens: null`.

## Hypotheses

### H1 — data-dependent code defect on the write path (validated)

`POST /orders` fails with an unhandled `TypeError` at `shop.py:82`: `total_price =
round(product["price"] * order.quantity, 2)` with a None price. The accounting is
exact — 3 user 500s, 3 TypeErrors, the only exception series and the only 5xx
series (E7); all three failures carry the identical raise site (E2, E4, E5). The
catalog's single null-price row is product 4, which has never completed an order
(E8, E9); successes for priced products interleave inside the failure window (E6),
and `/orders` never lists product 4 (E10). Failures are fail-fast, milliseconds each
(E3, E4, E5), and all predate the investigator's first probe — pure user impact.

### H2 — process instability (invalidated)

A single startup event covers the entire window, with no second startup or uptime
reset (E1, E7, E11); RSS is identical at baseline and at the closing recheck ~540s
later (E7, E11), and chaos stayed off on every read. Failures return in 5–12 ms, and
a clean 201 landed between two 500s (E4, E5, E6): instability does not selectively
fail one input while serving the same route correctly seconds apart with a single
deterministic exception type.

### H3 — injected degradation / dependency / gateway (invalidated)

Chaos gauge reads 0 at baseline and at the closing recheck, with zero
`chaos_enabled`/`chaos_disabled`/`chaos_failure`/`simulated_exception` events
anywhere in the log (E7, E11). The stack terminates at a local multiply inside
`create_order`, not a dependency or transport frame (E2), and the only 5xx series
anywhere is the app's own 500 — no 502/503/504 exists to attribute to an
intermediary (E7).

## Safe next steps

Read-only suggestions; remediation is out of scope for this report.

- Hand to the service owners: guard the `total_price` computation in `create_order`
  (`shop.py:82`) against a null `product["price"]` — any product whose price
  becomes null fails identically.
- Ask the data owners whether product 4's null price is bad data or
  unpriced-by-design (gap 6); the answer decides data fix vs orderability guard.
- Observability: failed order attempts log no `product_id` (gap 2 exists because of
  it) — adding the target product to order-failure logs would turn this
  investigation's one inference into a direct observation.
- Watch `http_exceptions_total{type="TypeError"}` and `http_requests_total{...,
  path="/orders", status="500"}` (E7, E11): any further growth means ongoing user
  impact.

## Gaps

The machine core lists six. In brief: telemetry starts at boot, so true onset is
unverifiable (1); the product-4 link is a closed inference — operand order plus a
unique null-price row — never a directly logged failing request (2); no read-only
reproduction is possible for a POST (3); retry corroboration is confined to the one
observed burst, with no later retry traffic seen (4); user-vs-investigator
attribution rests on the request-id convention (5); whether the null price is bad
data or by design is outside this surface (6).
