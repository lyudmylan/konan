---
konan_journal: 2
investigation:
  id: 2026-11-03-order-500s-null-price
  trigger: "manual — /konan adapter, human profile (docs/triggers.md). Complaint object: source=human, fingerprint=human-1793664617, labels.alertname=human-report, no severity stated by the reporter, startsAt=2026-11-03T00:10:17Z. Investigation entered 2026-11-03T00:10:32Z — trigger latency 15s."
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-03T00:10:32Z
  concluded: 2026-11-03T00:18:07Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "create_order multiplies the product's stored price by the requested quantity with no guard against a null price, so an order for a product whose price is null raises an unhandled TypeError and the request fails with HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The order-creation code multiplies the product's stored price by the requested quantity with no null guard; a product served with price null therefore raises TypeError and returns HTTP 500 before the order is persisted, while orders for priced products succeed. The served catalog holds exactly one such record — product 4, Mystery Box, price null, 75 units in stock, hence selectable — which is the inferred trigger."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E21, E22]
    evidence_against: [E23]
  - id: H2
    statement: "The root cause is an invalid catalog record — product 4 holds a null price where a number is required — and the order code is a victim of bad data rather than the defect."
    incident_class: data-db
    state: invalidated
    evidence_for: [E10, E11]
    evidence_against: [E22]
  - id: H3
    statement: "An internal operational switch (chaos or fault injection) was active and injected the HTTP 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E16, E18, E8]
  - id: H4
    statement: "Demand exceeded capacity; the HTTP 500 responses are a symptom of resource exhaustion or queueing."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E20, E19, E18, E17, E14]
  - id: H5
    statement: "Customers sent malformed or mismatched order payloads, which the service rejected."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E22, E8]
latent_findings:
  - statement: "The published contract neither types the price field nor declares the observed status: /products and /products/{product_id} declare their responses as untyped objects with no price field, and POST /orders declares only 201 and 422, so a null price violates no declared schema and the 500 is an undeclared response. Real and separately fixable; not the failure mechanism itself."
    evidence: [E22]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:08.824Z (request 5f0c28117042; long `stack` field trimmed)"
    quote: |-
      {"ts": "2026-11-03T00:10:08.824Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "5f0c28117042", "event": "unhandled_exception", "exception_type": "TypeError"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:08.824Z — tail of the `stack` field of request 5f0c28117042, rendered from its escaped newlines; home-directory path prefix of the frame elided"
    quote: |-
      line 82, in create_order
          total_price = round(product["price"] * order.quantity, 2)
                              ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~
      TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:09.894Z (request 5cc483520fd5; long `stack` field trimmed)"
    quote: |-
      {"ts": "2026-11-03T00:10:09.894Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "5cc483520fd5", "event": "unhandled_exception", "exception_type": "TypeError"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:13.017Z (request 430e2e474549; long `stack` field trimmed)"
    quote: |-
      {"ts": "2026-11-03T00:10:13.017Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "430e2e474549", "event": "unhandled_exception", "exception_type": "TypeError"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:08.834Z"
    quote: |-
      {"ts": "2026-11-03T00:10:08.834Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "5f0c28117042", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 11.131, "client": "127.0.0.1:62694"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:09.898Z"
    quote: |-
      {"ts": "2026-11-03T00:10:09.898Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "5cc483520fd5", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 5.502, "client": "127.0.0.1:62695"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:13.021Z"
    quote: |-
      {"ts": "2026-11-03T00:10:13.021Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "430e2e474549", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 4.953, "client": "127.0.0.1:62697"}
  - id: E8
    type: metric
    source: "/metrics @ 2026-11-03T00:10:52Z (probe konan-1793664652-12771)"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
  - id: E9
    type: metric
    source: "/metrics @ 2026-11-03T00:10:52Z (probe konan-1793664652-12771)"
    quote: 'http_exceptions_total{type="TypeError"} 3'
  - id: E10
    type: probe
    source: "/products (probe konan-1793664724-12798, HTTP 200)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,...},{"id":2,"name":"Toaster","price":23.0,...},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,...}]
  - id: E11
    type: probe
    source: "/products/4 (probe konan-1793664733-12805, HTTP 200)"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:05.704Z"
    quote: |-
      {"ts": "2026-11-03T00:10:05.704Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "4fbad772c19e", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:06.764Z"
    quote: |-
      {"ts": "2026-11-03T00:10:06.764Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "c8d20f19b671", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:11.958Z"
    quote: |-
      {"ts": "2026-11-03T00:10:11.958Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "831198d9da12", "event": "order_created", "order_id": 3, "product_id": 1, "quantity": 1, "total_price": 49.5}
  - id: E15
    type: metric
    source: "/metrics @ 2026-11-03T00:10:52Z (probe konan-1793664652-12771)"
    quote: 'faultline_chaos_enabled 0'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:10:01.825Z, plus reported absences across the whole file"
    quote: |-
      {"ts": "2026-11-03T00:10:01.825Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
      [reported absence: no second startup marker, and no chaos_enabled / chaos_disabled / chaos_failure / simulated_exception event, in any line of the file; lab/logs/app.log.1 does not exist, so this file is the complete history of this process]
  - id: E17
    type: probe
    source: "/health (probe konan-1793664645-12764, HTTP 200)"
    quote: '{"status":"ok","uptime_seconds":43.848281792132184}'
  - id: E18
    type: metric
    source: "/metrics, two readings: probe konan-1793664652-12771 @ 00:10:52Z, then probe konan-1793664757-12847 @ ~00:12:37Z"
    quote: |-
      process_uptime_seconds 51.00515375006944
      process_uptime_seconds 155.25241716695018
  - id: E19
    type: metric
    source: "/metrics, the same two readings (probes konan-1793664652-12771 and konan-1793664757-12847)"
    quote: |-
      process_max_rss_bytes 47677440
      process_max_rss_bytes 48037888
  - id: E20
    type: metric
    source: "/metrics @ 2026-11-03T00:10:52Z (probe konan-1793664652-12771)"
    quote: |-
      http_request_duration_seconds_sum{method="POST",path="/orders"} 0.02606033463962376
      http_request_duration_seconds_count{method="POST",path="/orders"} 6
  - id: E21
    type: probe
    source: "/orders (probe konan-1793664733-12810, HTTP 200)"
    quote: "returns exactly three orders, ids 1, 2 and 3, with no gaps in the id sequence"
  - id: E22
    type: probe
    source: "/openapi.json (probe konan-1793664746-12833, HTTP 200)"
    quote: 'POST /orders declares only 201 and 422 responses; OrderRequest validates product_id as a bare integer and quantity as 1..1000, both required, with no product-state check; /products and /products/{product_id} declare their responses as {"type":"object","additionalProperties":true} — no price field, no price type'
  - id: E23
    type: log
    source: "lab/logs/app.log — reported absence across all logged lines"
    quote: "[reported absence: no POST /orders line that returned 500 carries a product_id field; order_created, the only event carrying product_id, is never reached on the failing path; no request payload is logged]"
gaps:
  - "The failing requests' product_id is not recorded (E23) and POST is outside the GET-only probe allowlist, so the trigger — product 4 — is an inference from catalog state plus the throw site, never an observed field."
  - "The failure could not be replayed: probe.sh is GET-only and only the eval harness may send orders. Retry determinism is inferred from three byte-identical exceptions (E1, E3, E4) over a stateless arithmetic expression, not from a re-run."
  - "The catalog was read at ~00:10:51Z, about 38 seconds after the last failure. A continuous process with no observed writer makes a change improbable, but nothing positively excludes one."
  - "E10 is treated as the complete catalog: ids 1-5 are contiguous and no pagination is declared, but completeness is assumed rather than stated."
  - "Nothing proves the dict in create_order is the same record GET /products/4 serves; a serializer or conversion step yielding None would fit the stack equally well."
  - "E8, E9, E15 and E20 all come from a single scrape at 00:10:52Z — four items, one observation. Their reach back into the failure window rests on the process-continuity argument (E16, E18)."
  - "E16 and E23 are reported absences; an absence is only as good as the search behind it."
  - "The surface exposes no CPU metric, no current RSS (only the peak gauge), and no thread, worker or file-descriptor counts, so those saturation families were excluded by latency and volume rather than measured directly."
  - "No history exists before 00:10:01.825Z — no rotated log covers an earlier process generation."
  - "The source around shop.py line 82 was not read (eval blinding); the file and line are known only as the log prints them."
usage:
  model: claude-opus-5
  tokens: 1767130
  wall_clock_seconds: 455
---

# Orders fail with HTTP 500 for one product: an unguarded null price

## Summary

**Verdict: root cause identified — a software defect in the order-creation path.** The
code computes an order total as `product["price"] * order.quantity` with no guard
against a null price (E2). The served catalog contains one product whose price is
`null` and which is in stock, and therefore selectable: product 4, "Mystery Box", 75
units (E10, E11). An order for such a product raises an unhandled `TypeError`, which
the outer middleware turns into a generic HTTP 500 — the "Internal Server Error" the
customers saw (E1, E5). Three order attempts failed this way, each with a
byte-identical exception message, type and final frame (E1, E3, E4); all three
successful orders named a priced product (E12, E13, E14).

This explains both halves of the complaint. The failure is conditioned on the input,
not on time or chance: the stored price does not change between attempts, so a customer
who selected that product fails on every retry, while every customer who selected a
priced product succeeds. Confidence in the mechanism is high — it is observed directly
in the stack, not inferred. Confidence in the specific trigger is good but lower: it is
an inference, because the error path logs no `product_id` (E23).

**Impact, stated conditionally rather than as a rate.** Orders for a null-priced product
fail every time; orders for priced products all succeeded (E12-E14). The raw 3-of-6
split (E8) must **not** be published as a user-facing failure rate — n is six, inside an
11-second scripted traffic window, and the proportion only reflects how many of those
requests happened to select the unpriced product. No customer data was corrupted: the
exception fires before persistence, and `/orders` returns exactly ids 1, 2 and 3 with no
gaps (E21), so failed attempts wrote nothing and consumed no order id.

Health was green throughout (E17) while the business transaction was failing — the
reason this investigation checked the order surface rather than trusting `/health`.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 00:10:01.825 | Process starts, faultline 0.1.0. Single generation; no config, deploy or chaos marker appears anywhere in its life | E16 |
| 00:10:05.704 | Order 1 succeeds, product 1, total 99.0 | E12 |
| 00:10:06.764 | Order 2 succeeds, product 2, total 23.0 | E13 |
| 00:10:08.824 | First unhandled `TypeError` at the price multiplication | E1, E2 |
| 00:10:08.834 | That request returns HTTP 500 after 11.131 ms | E5 |
| 00:10:09.894 | Second `TypeError`, byte-identical message, type and final frame | E3 |
| 00:10:09.898 | Second HTTP 500, 5.502 ms | E6 |
| 00:10:11.958 | Order 3 **succeeds**, product 1 — a success between two failures, which rules out a degradation window | E14 |
| 00:10:13.017 | Third `TypeError`, again identical | E4 |
| 00:10:13.021 | Third HTTP 500, 4.953 ms | E7 |
| 00:10:14.080 | End-user traffic window closes | — |
| 00:10:17 | Complaint raised (`startsAt` of the complaint object) | — |
| 00:10:32 | Investigation enters the loop; trigger latency 15 s | — |
| 00:10:45.662 | First investigator probe — 32.6 s after the last failure, so no investigator traffic can have contributed to it | E17 |

No configuration-change, deploy or flag-change marker exists in the telemetry: the log
holds one startup line and no switch event, and no rotated backup could hide one (E16).

## Investigation

**Baseline.** `/health` green (E17); `/metrics` showed the order route split 3×201 /
3×500 with exactly three `TypeError`s process-wide (E8, E9) and the chaos gauge at zero
(E15); the log held 24 lines covering the whole process life from startup (E16).

**Triage — three lenses in parallel, each blind to the others.** Neither the complaint
nor the baseline could exclude any lens domain by evidence, so all three ran.
*software-defect* found the deterministic throw site and then the null-priced catalog
row (E2, E10, E11). *interfaces* independently found the same catalog state, placed the
cause outside its own domain, and added the onset shape (failures interleaved with
successes, no boundary) plus the contract gap (E22). *infra-process* returned three
negative findings — no restart or lifecycle event, no resource saturation, healthy and
fast latency (E16, E18, E19, E20) — and noted that one process both succeeding and
failing inside eight seconds cannot be produced by an infra cause.

**Deep-dive — deliberately skipped.** The mechanism was already deterministic and
complete from triage, and the single remaining evidence gap (the unlogged `product_id`)
is unclosable on a GET-only, read-only surface. A deep-dive would have re-proved the
mechanism rather than filled the gap, so the budget went unspent and the hypotheses went
straight to the judge.

**Judge.** The judge received the hypothesis list and the verbatim evidence ledger only,
with no lens reasoning or narrative. It validated H1, invalidated H2 through H5, and
corrected three things now reflected above: retry determinism is *inferred* rather than
observed; the root-cause claim and the trigger claim are separate, the latter being an
inference; and the 3-of-6 split is an artifact of request mix, not an impact rate. It
also confirmed that no investigator probe could have contributed to the failures, on
three independent grounds — ordering, method and request accounting.

## Hypotheses

### H1 — Unguarded null price in the order total. **Validated.**

The mechanism is observed, not inferred: E2 names the expression
`total_price = round(product["price"] * order.quantity, 2)`, E1 names the exception with
`NoneType` as the left operand, and E5 ties the same `request_id` to the 500 ten
milliseconds later. The counts reconcile with no residue: three 500s and three 201s
(E8), exactly three `TypeError`s process-wide (E9) so no other failure hides, three
successes all for priced products (E12-E14), and order ids 1-3 without gaps (E21).

The trigger is the inferred part. `None` can only have come from the price lookup — a
missing key would raise `KeyError`, not `TypeError` — product 4 is the only null-priced
record in the served catalog, and it is in stock and passes the bare-integer
`product_id` validation (E10, E11, E22). Against it stands E23: no failing request logs
its `product_id`, so this link is reasoning over catalog state, not an observed field.

E22 is the quiet decisive item: the service publishes only 201 and 422 for this route,
so the 500 is the target's own contract violation whatever the client sent.

### H2 — Invalid catalog record as root cause. **Invalidated.**

E10 and E11 prove only that product 4 holds `price: null` with 75 units in stock. They
do not establish that the record is *wrong*. The record is complete and self-consistent,
it is served with HTTP 200, and no second copy exists for it to be out of sync with. E22
cuts against the hypothesis: no declared price field and no price type exist, so nothing
marks a null price as invalid data — a null price may well be a legitimate domain state
for a "Mystery Box". A value the code cannot handle is not a data inconsistency; an
inconsistency needs a reference to be inconsistent with, and the telemetry offers none.

Ownership decides the attribution. Hold the data fixed and add a guard, or return the
declared 422, and the request becomes correct; change the data and keep the code, and the
next null-priced product crashes it again. Even if a constraint did exist and row 4 broke
it, a correct program answers bad data with 422, not a `TypeError`. Bad data would be a
contributing condition at most, and the taxonomy permits one cause: `software-defect` /
`unhandled-exception`.

### H3 — Injected degradation via an operational switch. **Invalidated.**

`faultline_chaos_enabled 0` (E15) is a post-hoc reading on its own, 39 s after the last
failure — but E16 extends it backwards: one startup marker, no switch event of any kind
in the complete history, and no rotated file to hide one, over a single continuous
process (E18). The interleaving kills it independently: success at 00:10:11.958Z sits
between failures at 00:10:09.898Z and 00:10:13.021Z (E14), which is not a switch window.
And an injector raises a synthetic or labelled error, where this is a genuine `TypeError`
on a real application line.

### H4 — Load saturation. **Invalidated.**

Six order requests in the entire process life, mean 4.3 ms (E20). The failures were
themselves fast — 11.1, 5.5 and 5.0 ms (E5, E6, E7) — and the first is slowest only
because it formatted a stack trace; the last is the quickest, so nothing degraded along
the timeline. Peak RSS moved 47.68 MB to 48.04 MB (E19), uptime is continuous with no
reset (E18), health is green (E17). Saturation also carries the wrong signature: 503,
504 or timeouts, not a deterministic exception at a named line.

### H5 — Malformed client payloads. **Invalidated.**

E2 settles the direction of the fault: the `None` is the *left* operand, which is the
server-side catalog value, while the client's `quantity` is the well-formed `int`. The
request reached line 82 inside `create_order`, so it passed validation. A malformed body
would be a 422 by the service's own declared contract (E22), and no 422 counter exists at
all for this route (E8) — nothing was ever rejected. Both operands are internal to the
target, so there is no boundary between parties for an interfaces cause to live at. The
unlogged-payload gap (E23) cannot rescue this hypothesis: whatever the client sent
satisfied the schema, by the fact that it reached the arithmetic.

## Safe next steps

Read-only suggestions; remediation is out of scope for a journal.

1. **Observe the trigger directly** — have the eval harness send one order for
   `product_id: 4` and one for a priced product, then compare the two log traces. That is
   the single step which converts the trigger from inference to observation. Harness
   only: konan is read-only and cannot send orders.
2. **Close the diagnostic blind spot** — the error path logs no `product_id` and no
   payload (E23), which is why this investigation ends with an inference rather than a
   fact. Carrying the request's `product_id` onto the exception line would make this class
   of failure self-evident in the log.
3. **Audit the catalog for the same shape** — read `/products` for any other record that
   is in stock yet lacks a price. Only product 4 holds that shape now (E10); the question
   is whether the catalog can produce more.
4. **Read the code around `shop.py:82`** — outside this investigation's reach under eval
   blinding, and the place where the guard's absence can be confirmed and the
   null-vs-missing-key question settled.
5. **Reconcile the published contract** — `POST /orders` declares no 500 and the product
   schemas declare no price type (E22), so neither the failure nor the state that causes
   it is visible to a client reading the contract.

## Gaps

The unlogged `product_id` is the one that matters: with a GET-only probe surface and no
payload logging, the link from the null price to those three specific requests is
reasoning, not observation, and the conclusion marks it as such. For the same reason the
failure could not be replayed — retry determinism rests on three byte-identical
exceptions over a stateless expression (E1, E3, E4), which is strong but still inference.

Three narrower holes sit under the trigger claim: the catalog was read ~38 s after the
last failure and nothing positively excludes a change in between; E10 is assumed to be
the complete catalog because ids 1-5 are contiguous and no pagination is declared; and
nothing proves the dict inside `create_order` is the record `/products/4` serves — a
serializer yielding `None` would fit the stack equally well.

On the ledger's own weaknesses: E8, E9, E15 and E20 are four items from a single scrape
at 00:10:52Z, so their reach back into the failure window depends on the
process-continuity argument (E16, E18) rather than on independent readings. E16 and E23
are reported absences, and an absence is only as good as the search behind it — H3's
invalidation survives mainly because H1's mechanism is positively established, not
because of the absence alone.

On the surface's limits: there is no CPU metric, no current RSS (only the peak gauge),
and no thread, worker or file-descriptor count, so those saturation families were
excluded by latency and volume rather than measured. No history exists before
00:10:01.825Z, as no rotated log covers an earlier generation. The source around
`shop.py:82` was not read under eval blinding; the file and line are known only as the
log prints them.

One contamination note in the other direction: investigator probes do appear in the data
they read. The uptime and RSS deltas (E18, E19) are probe-driven, and the GET counters
include probe traffic, so no GET volume here should be read as user demand. The probes
cannot have touched the failures themselves — the earliest is 32.6 s after the last 500,
all were GETs against a POST route, and the order count was still six at the scrape
(E20).
