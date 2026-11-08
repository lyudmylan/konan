---
konan_journal: 2
investigation:
  id: 2026-11-03-order-500s
  trigger: "manual — /konan human report. Complaint object: source=human, fingerprint=human-1793666243, labels.alertname=human-report, no severity stated by the reporter. startsAt 2026-11-03T00:37:23Z; investigation start 2026-11-03T00:37:30Z; trigger latency 7s."
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-03T00:37:30Z
  concluded: 2026-11-03T00:45:18Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The order-creation path multiplies the product price by the order quantity without guarding against a null price, so an order naming a product whose price is null raises an unhandled TypeError and the request fails with HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The target's own order-creation code raises an unhandled TypeError when it multiplies a null product price by the order quantity, so POST /orders returns 500 for every order naming a null-priced product, deterministically on retry; orders naming a priced product succeed on the same route in the same seconds."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E10, E11]
    evidence_against: []
  - id: H2
    statement: "An operational degradation switch inside the target (chaos, kill switch, or feature flag) injected the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E4]
    evidence_against: [E7, E15, E13, E1, E11]
  - id: H3
    statement: "A process lifecycle event — crash, restart, or hang — caused the order failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E9, E11, E15]
  - id: H4
    statement: "Demand exceeded capacity (workers, memory, or CPU), so orders failed under load."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E11, E15, E4]
  - id: H5
    statement: "The root cause is an incomplete or corrupt catalog record — product 4 holds a null price where a price is required — making this a data-layer defect rather than a code defect."
    incident_class: data-db
    state: invalidated
    evidence_for: [E6, E14, E1]
    evidence_against: [E13]
  - id: H6
    statement: "A payload, schema, or version mismatch between two parties at an API boundary caused the failures."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E13]
    evidence_against: [E1]
latent_findings:
  - statement: "POST /orders declares only responses 201 and 422 in the target's own OpenAPI document, so the 500 it returns is undeclared; the declared OrderRequest validates only field types and the quantity range, so the API offers no declared rejection for an order the service cannot price. A contract-completeness gap in the documented surface, not a cause of this incident."
    evidence: [E13]
  - statement: "The collection and item representations of the same product diverge: /products/4 carries units_ordered and turnover_score, which the /products collection entry for id 4 omits. No declared contract is violated, since the product response schemas declare no properties at all. Observed by investigator probes only; no user impact is claimed."
    evidence: [E14, E6, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:37:12.675Z"
    quote: |-
      {"ts": "2026-11-03T00:37:12.675Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'", "request_id": "2ed3b604b46c", "event": "unhandled_exception", "exception_type": "TypeError", "stack": "Traceback (most recent call last):\n  [frames trimmed]\n  File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:37:12.685Z"
    quote: |-
      {"ts": "2026-11-03T00:37:12.685Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 500", "request_id": "2ed3b604b46c", "event": "request", "method": "POST", "path": "/orders", "status": 500, "duration_ms": 10.926, "client": "127.0.0.1:62867"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:37:09.555Z"
    quote: |-
      {"ts": "2026-11-03T00:37:09.555Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "6ef84a393bc6", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
  - id: E4
    type: metric
    source: "/metrics @ probe konan-1793666263-13544"
    quote: |-
      http_requests_total{method="POST",path="/orders",status="201"} 3
      http_requests_total{method="POST",path="/orders",status="500"} 3
  - id: E5
    type: metric
    source: "/metrics @ probe konan-1793666263-13544"
    quote: 'http_exceptions_total{type="TypeError"} 3'
  - id: E6
    type: probe
    source: "/products @ probe konan-1793666440-13712, HTTP 200"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":117},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E7
    type: metric
    source: "/metrics @ probe konan-1793666263-13544"
    quote: "faultline_chaos_enabled 0"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:37:05.673Z — the only startup marker in the file; no .1–.3 rotated backups exist"
    quote: |-
      {"ts": "2026-11-03T00:37:05.673Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E9
    type: metric
    source: "/metrics and /health across probes konan-1793666263, konan-1793666372, konan-1793666385"
    quote: |-
      process_uptime_seconds 37.503415958955884 ; process_uptime_seconds 146.58386187488213 ; {"status":"ok","uptime_seconds":159.9116570840124}
  - id: E10
    type: probe
    source: "/orders @ probe konan-1793666459-13721, HTTP 200"
    quote: |-
      [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-03T00:37:09.555+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-03T00:37:10.617+00:00"},{"id":3,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-03T00:37:15.810+00:00"}]
  - id: E11
    type: log
    source: "lab/logs/app.log, POST /orders status sequence from non-investigator clients, 2026-11-03T00:37:09.556Z–00:37:16.875Z"
    quote: |-
      201 @ 00:37:09.556Z client 127.0.0.1:62865 ; 201 @ 00:37:10.618Z client 127.0.0.1:62866 ; 500 @ 00:37:12.685Z client 127.0.0.1:62867 request_id 2ed3b604b46c ; 500 @ 00:37:13.748Z client 127.0.0.1:62868 request_id f5770dd2ee53 "duration_ms": 5.49 ; 201 @ 00:37:15.811Z client 127.0.0.1:62869 ; 500 @ 00:37:16.875Z client 127.0.0.1:62870 request_id a0575d78bf19 "duration_ms": 5.195
  - id: E12
    type: metric
    source: "/metrics @ probes konan-1793666263-13544 (uptime 37.50s) and konan-1793666372 (uptime 146.58s)"
    quote: "process_max_rss_bytes 47644672"
  - id: E13
    type: probe
    source: "/openapi.json @ probe konan-1793666384-13669, HTTP 200"
    quote: |-
      create_order_orders_post declares only responses "201" and "422". OrderRequest: {"product_id":{"type":"integer"},"quantity":{"type":"integer","maximum":1000.0,"minimum":1.0},"required":["product_id","quantity"]}. Product response schemas: {"additionalProperties":true,"type":"object"} with no property definitions. Operational toggle default: "error_status":{"type":"integer","maximum":599.0,"minimum":400.0,"title":"Error Status","default":503}
  - id: E14
    type: probe
    source: "/products/4 @ probe konan-1793666405-13696, HTTP 200"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
  - id: E15
    type: log
    source: "lab/logs/app.log, whole-file scan of the single process lifetime"
    quote: |-
      No line carries event value chaos_enabled, chaos_disabled, chaos_failure or simulated_exception. GET routes returned status 200 only; the slowest request in the file is a cold-start /health at "duration_ms": 12.517
gaps:
  - "No telemetry records POST /orders request bodies — docs/lab.md defines the request event as method, path, status, duration_ms and client only — so the failing product_id is inferred by elimination (E1 proves the price operand was null; E6 shows exactly one null-priced record) and never observed directly. The investigator could not close this read-only: probe.sh is GET-only and POST /orders is outside the investigator surface. One log line binding request_id 2ed3b604b46c, f5770dd2ee53 or a0575d78bf19 to a product_id would close it; the units_ordered 0 in E14 does not, being equally consistent with three failed attempts and with none."
  - "Successful orders were observed for products 1 and 2 only (E10). Products 3 and 5 were never ordered in this window, so 'orders for priced products succeed' is evidenced for those two products alone; product 3 additionally holds units_in_stock 0 (E6), a separate untested path."
  - "The lab exposes no CPU metric (docs/lab.md, Metrics), so CPU starvation was excluded by the 5–11 ms failure durations (E11) rather than measured directly."
  - "Evidence covers one process lifetime only: a single startup marker at 00:37:05.673Z with no rotated backups (E8), so no pre-00:37:05Z history was available and this defect's first occurrence in time is unknown."
  - "Customer identity is not establishable from this surface. The three failures arrived on three distinct connections (E11), but all non-investigator traffic originates from 127.0.0.1, so 'multiple customers' in the complaint is consistent with but not proven by the telemetry."
usage:
  model: claude-opus-5
  tokens: 2342381
  wall_clock_seconds: 468
---

# Order placement fails with 500 for orders naming a null-priced product

## Summary

**Verdict: root cause identified.** `POST /orders` computes an order total by multiplying
the product's price by the requested quantity, with no guard for a missing price. When an
order names a product whose `price` is null, that multiplication raises an unhandled
`TypeError` — `unsupported operand type(s) for *: 'NoneType' and 'int'` — and the request
ends as HTTP 500 (E1, E2). The failure is a property of the input, not of the moment or of
the process, so a customer who retries the same cart fails again every time, which is
exactly the "keeps failing when they retry" in the complaint. Customers whose carts name a
priced product are unaffected and succeed on the same route in the same seconds (E10, E11).

Impact in the observed window, counting non-investigator traffic only: **3 of 6 order
attempts failed** (E4), on one route. No order was partially written — only the three
successful orders exist (E10). Every read surface stayed healthy, all 200s under 13 ms
(E15), and `/health` reported `ok` throughout — the healthy-monitoring shape, where a green
health endpoint sits above a failing business transaction.

Confidence is high on the mechanism, which is proved verbatim by the exception and its
throwing frame (E1) and holds whichever product id arrived. The specific product is an
**inference, not an observation**: the raise proves the price operand was null, and the
catalog holds exactly one null-priced record, `{"id":4,"name":"Mystery Box","price":null}`
(E6, E14). No telemetry records order request bodies, so that last link is closed by
elimination rather than observed — see Gaps.

The null price is the *input* that triggers the defect; the missing guard is the defect.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 00:37:05.673 | Process starts, `faultline 0.1.0 started`. The only startup marker; no rotated backups, so this is the whole process history. | E8 |
| 00:37:06–00:37:07 | Reads healthy: GET /health, /products, /products/1 all 200 under 13 ms. | E15 |
| 00:37:09.556 | Order succeeds, 201 — product 1, quantity 2, total 99.0. | E3, E11 |
| 00:37:10.618 | Order succeeds, 201 — product 2, quantity 1, total 23.0. | E10, E11 |
| 00:37:12.675 | **First failure.** Unhandled `TypeError` at the price × quantity multiplication. | E1 |
| 00:37:12.685 | That request ends 500 after 10.926 ms. | E2 |
| 00:37:13.748 | Second failure, 500 — identical message and identical final frame, 5.49 ms. | E11 |
| 00:37:15.811 | Order succeeds, 201 — product 1 again, interleaved between the failures. | E10, E11 |
| 00:37:16.875 | Third failure, 500 — identical message and frame, 5.195 ms. | E11 |
| 00:37:42 onward | Investigator probes begin (`konan-*`), read-only. Exception count stays at 3. | E5, E9 |

No configuration, deploy, or flag-change marker appears anywhere in the window — the
declared toggle events are absent from the entire file (E15) and the switch reads off (E7).
There is no "good until T, bad after T" step: successes and failures interleave second by
second from the start (E11).

## Investigation

**Baseline.** Health, a metrics snapshot, and the full 24-line log tail. The baseline itself
carried the split — 3 × 201 against 3 × 500 on `POST /orders`, with
`http_exceptions_total{type="TypeError"} 3` matching the 500 count 1:1 — plus a single
startup marker and chaos off.

**Triage — three lenses in parallel, each blind to the others.** All three domains were live:
the baseline could not exclude infra-process or interfaces with evidence, and a skipped lens
is an accepted blind spot.

- *software-defect* returned the throwing frame, found the single null-priced catalog record
  by probing `/products` and `/products/4`, and confirmed the per-input determinism.
- *infra-process* excluded its own domain on evidence: uptime monotonic to the hundredth of a
  second across three readings (a restart or counter reset is impossible in-window), peak RSS
  byte-identical, failures 5–11 ms rather than timeouts, no time-shaped failure window.
- *interfaces* excluded injection and dependency failure — notably that the toggle's declared
  error status is 503 while the observed status is 500 — and independently surfaced the same
  null-price record, plus a response-shape divergence.

The two exclusion lenses converged on the same handoff without seeing each other's work.

**Deep-dive: skipped, deliberately.** H1's triage evidence was already deterministic and
complete, and the loop sends such a hypothesis straight to the judge — deep-dives fill
evidence gaps, they do not re-prove. The one real gap (which product the failing requests
named) is a telemetry gap no read-only probe could close, so a deep-dive agent would have
spent tokens re-deriving what E1 and E6 already show. I verified the catalog and the order
list myself instead.

**Judge.** One fresh judge, given the hypothesis list with verbatim quotes and the taxonomy
definitions, and no narrative. It validated H1, invalidated H2–H6, and imposed three wording
conditions, all of which this journal honors: the success clause is narrowed to the two
products actually observed, the product id is stated as an inference rather than an
observation, and H6's contract gap rides along as a latent finding instead of a cause.

## Hypotheses

### H1 — unguarded null price in the order total — **validated**

The mechanism needs no inference. E1 names the event (`unhandled_exception`), the type
(`TypeError`), the operand types (`'NoneType' and 'int'`), and the statement that raised:
`total_price = round(product["price"] * order.quantity, 2)` in `create_order`. E2 binds the
same `request_id` to `POST /orders -> 500`. E4 and E5 close the window: three 500s, three
`TypeError`s, so no second failure mechanism hides among them. E11 shows all three ERROR
lines carrying an identical message and identical final frame — one defect, three times, not
three defects. E10 accounts for all three successes.

Determinism is the part that matches the complaint most precisely. A per-request probabilistic
fault would not repeat one operand-type error at one line; a per-input fault fails identically
on every retry of the same cart, while leaving other carts untouched.

### H2 — injected degradation via an operational switch — **invalidated**

The 3-of-6 fraction resembles a ~50% injection rate, which is why this was worth testing. E4
is a base rate with no mechanism behind it: it is equally the fraction of requests that named
the null-priced product. Against it: `faultline_chaos_enabled 0` (E7); none of the four
declared toggle events appear anywhere in the file, which covers the whole process life with
no rotation gap (E15, E8); the toggle's declared error status is 503 while the observed status
is 500 (E13); and an injected fault does not raise inside the target's own arithmetic at a
named line (E1). One `chaos_enabled` line, or one reading of `faultline_chaos_enabled 1`
inside 00:37:12–00:37:16, would overturn this.

### H3 — process crash, restart, or hang — **invalidated**

E8 gives one startup marker with no rotated backups, so no earlier start is hidden. E9 shows
uptime tracking wall clock within 0.08 s over 109 s — a restart resets that counter and a hang
breaks it. E11 shows failures answering in 5–11 ms with an application stack, 201s interleaved
between them; a dead process serves nothing, a hung one does not answer in 5 ms. A second
`startup` event, or an uptime reading below an earlier one, would overturn it.

### H4 — load saturation — **invalidated**

Six order requests in total is not demand (E4). Peak RSS is byte-identical across 109 seconds
(E12). Failures complete in 5–11 ms and the slowest request in the entire file is a cold-start
`/health` at 12.517 ms (E11, E15). The failure mode is a `TypeError`, not a timeout, a 503, or
a 429. Sustained order volume with rising durations and a moving RSS high-water mark would
settle it the other way.

### H5 — data-layer defect (corrupt catalog record) — **invalidated**

This was the serious rival to H1: it reads the *same* evidence into a different class, and
getting it wrong is a false attribution rather than a near miss. Three reasons it fails.

First, the contract scopes `data-db` ids to what a database did, and this target runs no real
database (`docs/lab.md`, "Known gaps of this lab"). E6 and E14 are HTTP 200 bodies from the
service's own in-process store, not database behaviour.

Second, `data-inconsistency` requires that the record be *wrong*, and no evidence establishes
that a price is required. E13 shows the opposite: the product response schemas declare no
properties at all, and both read paths return the null price with HTTP 200 (E6, E14) — the
read path treats a null price as a legal catalog state. The only component in the system that
treats null as impossible is the unguarded multiplication (E1).

Third, the class names the discipline that fixes the cause. The fix here is a guard or a
validation on the order path, written by a software engineer; there is no migration, no schema
disagreement, and no data-layer behaviour to repair. What would settle it the other way: a
declared schema or constraint making `price` non-nullable, which would make the record itself
the defect.

### H6 — API contract mismatch — **invalidated as a cause**

The refutation comes from H6's own citation. E13 shows `OrderRequest` as `product_id: integer`
and `quantity: integer, 1..1000`; the client sent a type-valid payload, the server accepted it,
and then the server's own code raised (E1). There is no mismatch between two parties, and the
class definition requires an external party or a boundary component — neither appears. The
undeclared 500 is a *consequence* of the raise, not its cause; the causality runs the other
way. The genuine contract gap it surfaced rides along as a latent finding.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. Search the rotating log (`lab/logs/app.log` plus any `.1`–`.3` backups as they appear) for
   earlier `exception_type: TypeError` lines, to learn whether this predates the observed
   window — E8 bounds the current evidence to one process lifetime.
2. Watch `http_exceptions_total{type="TypeError"}` and
   `http_requests_total{method="POST",path="/orders",status="500"}` over time to measure the
   ongoing failure rate and confirm whether the defect is still being hit.
3. Ask the catalog's owner whether a null `price` on "Mystery Box" is an intended state. That
   answer decides where a fix belongs, and it is a question for a human, not a probe.
4. Ask support for the cart contents of one affected customer. That is the cheapest way to
   confirm the inferred product id from outside the telemetry surface.
5. Check the remaining priced products (`/products/3`, `/products/5`) for other incomplete
   records before assuming product 4 is the only affected input.

## Gaps

- **The failing product id is inferred, not observed.** Order request bodies appear in no
  telemetry: `docs/lab.md` defines the `request` event as `method`, `path`, `status`,
  `duration_ms`, `client`. E1 proves the price operand was null; E6 shows exactly one
  null-priced record; the link between them is elimination. This was not closable read-only —
  `probe.sh` is GET-only and `POST /orders` is outside the investigator surface. A log line
  binding a failing `request_id` to a `product_id` would close it. The `units_ordered: 0` in
  E14 does **not**: a zero count fits three failed attempts and no attempt equally well.
- **The success claim is narrower than it sounds.** Only products 1 and 2 were actually
  ordered successfully (E10). Products 3 and 5 were never exercised, and product 3 holds
  `units_in_stock: 0` (E6) — a separate path this investigation did not test.
- **No CPU metric exists** on this surface (`docs/lab.md`, Metrics). CPU starvation was
  excluded from the 5–11 ms failure durations rather than measured.
- **One process lifetime of history.** A single startup marker and no rotated backups (E8)
  mean the defect's first occurrence in time is unknown; it may long predate this window.
- **Customer identity is not establishable.** The three failures arrived on three distinct
  connections (E11), but all non-investigator traffic originates from `127.0.0.1`, so the
  complaint's "multiple customers" is consistent with the telemetry without being proven by it.
