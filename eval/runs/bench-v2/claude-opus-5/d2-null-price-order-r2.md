---
konan_journal: 2
investigation:
  id: 2026-11-03-order-null-price-500s
  trigger: "manual — /konan adapter, human profile (docs/triggers.md). Complaint object: source human, fingerprint human-1793665299, labels.alertname human-report, no severity stated by the reporter, startsAt 2026-11-03T00:21:39Z. Investigation start 2026-11-03T00:21:53Z — trigger latency 14s."
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-11-03T00:21:53Z
  concluded: 2026-11-03T00:32:52Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "POST /orders computes the order total by multiplying the resolved product's catalog price by the requested quantity with no null check (shop.py:82), so an order whose resolved product carries a null price raises an unhandled TypeError and returns 500, while orders for priced products succeed on the same route in the same seconds."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The order handler multiplies the resolved product's catalog price by the requested quantity with no null check (shop.py:82); an order whose resolved product carries a null price raises TypeError → 500, while priced products succeed. The catalog as served holds exactly one null-priced entry, id 4 'Mystery Box'."
    incident_class: software-defect
    state: validated
    evidence_for: [E3, E4, E6, E7, E8, E9, E10, E11, E13]
    evidence_against: [E14, E10]
  - id: H2
    statement: "An operational degradation switch inside the target (chaos, error injection, feature flag) is injecting the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E3]
    evidence_against: [E17, E5, E6]
  - id: H3
    statement: "Demand exceeded capacity: a resource, worker pool or queue was exhausted, degrading the order route."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E16, E3, E9]
  - id: H4
    statement: "A process lifecycle event (crash, restart, hang) or a configuration or deploy change caused the failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E16, E17]
  - id: H5
    statement: "A boundary component (proxy, gateway, load-balancer tier) or an external provider failed, or the client sent a malformed payload the contract failed to reject."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E15]
    evidence_against: [E6, E15, E3]
  - id: H6
    statement: "The failing input was a product_id absent from the catalog which the order handler resolves to a sentinel record carrying a null price, reaching the same line 82 — so the trigger is unknown-id handling rather than the data of product 4."
    incident_class: software-defect
    state: inconclusive
    evidence_for: []
    evidence_against: [E12]
latent_findings:
  - statement: "The failure path records no request context: the three unhandled_exception lines and their access lines carry request_id but no product_id and no body, while the success path logs product_id via order_created — so the failing input cannot be named from telemetry."
    evidence: [E6, E8, E14]
  - statement: "Contract drift at the published surface: no Product schema exists in components.schemas and price nullability is undeclared (both product responses are typed as free-form objects); POST /orders declares only 201 and 422 yet returned 500, and GET /products/{product_id} declares only 200 and 422 yet returns 404."
    evidence: [E15, E12]
  - statement: "Product id 3 'Unobtainium Ingot' carries a numeric price with units_in_stock 0 and remains orderable under the published request schema, which validates product_id for integer-ness only; no traffic in the window exercised it."
    evidence: [E10, E15]
evidence:
  - id: E1
    type: probe
    source: "/health @ request_id konan-1793665326-13092, 2026-11-03T00:22:06Z"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":42.832596458029}\n-- HTTP 200 in 0.001359s request_id=konan-1793665326-13092"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:21:23.329Z"
    quote: "{\"ts\": \"2026-11-03T00:21:23.329Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E3
    type: metric
    source: "/metrics @ request_id konan-1793665331-13099, 2026-11-03T00:22:11Z — the complete http_requests_total series of that scrape"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3"
  - id: E4
    type: metric
    source: "/metrics @ 2026-11-03T00:22:11Z"
    quote: "http_exceptions_total{type=\"TypeError\"} 3"
  - id: E5
    type: metric
    source: "/metrics @ 2026-11-03T00:22:11Z, and again @ request_id konan-1793665426-13157, 2026-11-03T00:23:46Z"
    quote: "faultline_chaos_enabled 0"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:21:30.317Z (request_id 7545c5eae8c9); two lines identical in message, exception_type and stack tail @ 00:21:31.384Z (65fa8ab19f12) and @ 00:21:34.496Z (09488c45f915)"
    quote: "{\"ts\": \"2026-11-03T00:21:30.317Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"7545c5eae8c9\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\", \"stack\": \"… File \\\"/…/faultline/shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:21:30.327Z; same pairing @ 00:21:31.388Z and @ 00:21:34.500Z"
    quote: "{\"ts\": \"2026-11-03T00:21:30.327Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 500\", \"request_id\": \"7545c5eae8c9\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 500, \"duration_ms\": 10.9, \"client\": \"127.0.0.1:62769\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:21:27.197Z"
    quote: "{\"ts\": \"2026-11-03T00:21:27.197Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"a3d6805c4bf9\", \"event\": \"order_created\", \"order_id\": 1, \"product_id\": 1, \"quantity\": 2, \"total_price\": 99.0}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:21:33.438Z — a success between the failures of E6 @ 00:21:31.384Z and @ 00:21:34.496Z"
    quote: "{\"ts\": \"2026-11-03T00:21:33.438Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"ff5c70782e84\", \"event\": \"order_created\", \"order_id\": 3, \"product_id\": 1, \"quantity\": 1, \"total_price\": 49.5}"
  - id: E10
    type: probe
    source: "/products @ request_id konan-1793665581-13221, 2026-11-03T00:26:21Z — HTTP 200"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":117},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E11
    type: probe
    source: "/products/4 — HTTP 200"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0}"
  - id: E12
    type: probe
    source: "/products/999 (konan-1793665582-13226), /products/0 (konan-1793665584-13231), /products/-1 (konan-1793665592-13242), /products/6 (konan-1793665622-13267) — all HTTP 404"
    quote: "{\"detail\":\"no such product: 999\"} / {\"detail\":\"no such product: 0\"} / {\"detail\":\"no such product: -1\"} / {\"detail\":\"no such product: 6\"}"
  - id: E13
    type: metric
    source: "/metrics @ 2026-11-03T00:22:11Z, reconciled against the six POST /orders access lines of lab/logs/app.log"
    quote: "http_request_duration_seconds_sum{method=\"POST\",path=\"/orders\"} 0.025725249433889985 / http_request_duration_seconds_count{method=\"POST\",path=\"/orders\"} 6 — the logged duration_ms values 1.948 + 1.326 + 1.112 (201s) + 10.9 + 5.43 + 5.009 (500s) = 25.725 ms, equal to the sum over count 6"
  - id: E14
    type: probe
    source: "/orders (konan-1793665584-13236) — HTTP 200; /orders/4 (konan-1793665593-13247) — HTTP 404"
    quote: "the three persisted orders only, product_id 1, 2, 1 (order_id 1, 2, 3) / {\"detail\":\"no such order: 4\"}"
  - id: E15
    type: probe
    source: "/openapi.json @ request_id konan-1793665597-13253 — HTTP 200"
    quote: "\"OrderRequest\":{\"properties\":{\"product_id\":{\"type\":\"integer\"},\"quantity\":{\"type\":\"integer\",\"maximum\":1000.0,\"minimum\":1.0}},\"required\":[\"product_id\",\"quantity\"]} — POST /orders declares responses 201 and 422 only; GET /products/{product_id} declares 200 and 422 only; components.schemas holds ChaosSettings, HTTPValidationError, OrderRequest, ValidationError and no Product schema; both product responses are typed {\"additionalProperties\":true,\"type\":\"object\"}"
  - id: E16
    type: metric
    source: "/metrics @ 2026-11-03T00:22:11Z and @ 2026-11-03T00:23:46Z"
    quote: "process_uptime_seconds 48.06365416594781 then 143.1228463749867 (delta 95.06s over 95s wall, both back-computing to the start of E2); process_max_rss_bytes 48054272 then 48431104"
  - id: E17
    type: log
    source: "lab/logs/app.log, whole file — startup through the present, no rotated .1–.3 backups exist"
    quote: "the only event values present are startup, request, order_created and unhandled_exception; no chaos_enabled, chaos_disabled, chaos_failure or simulated_exception line anywhere in the file"
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-03T00:21:35.557Z — the last request line without a konan-* request_id"
    quote: "{\"ts\": \"2026-11-03T00:21:35.557Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"7b21fda66a53\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 0.862, \"client\": \"127.0.0.1:62773\"}"
  - id: E19
    type: metric
    source: "/metrics @ request_id konan-1793665623-13272, 2026-11-03T00:27:03Z"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3 and http_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3 — unchanged from the 00:22:11Z scrape of E3"
gaps:
  - "The failing requests' product_id was never observed. The unhandled_exception lines and their access lines carry request_id but no body and no product_id (E6, E7), failed attempts persist no record (E14), and the probe surface is GET-only, so no POST could reproduce one. The attribution to id 4 'Mystery Box' is elimination over the catalog, not observation."
  - "H6 is observationally identical to H1 on the available surface: a lookup defaulting to a sentinel record would print the same stack. The product lookup above shop.py:82 would settle it, but faultline's source is outside the surface contract of docs/lab.md and inside the blinding contract of eval/README.md — a scope boundary, not a read-only one. Either way the class, the cause and the raise site are the same; only the trigger description differs."
  - "'Keeps failing when they retry' was not reproduced. Three independent failures with identical message and stack tail are consistent with determinism; re-issuing a POST is outside the boundary, so determinism rests on the code shape plus E5/E17, not on a demonstration."
  - "The catalog was read at ~00:26Z, about five minutes after the failure window, and the catalog is mutable — product 1 shows units_in_stock 117 after the 3 units sold in E8 and E9. So price: null at failure time is projected backward from probe time (E10, E11)."
  - "No in-window resource gauge beyond uptime and peak RSS exists on the surface (no worker, queue-depth, descriptor or event-loop metric), so load-saturation is excluded by the absence of load and flat latency, not by direct measurement."
  - "No rotated log backups exist; app.log covers only this process lifetime from 00:21:23Z (E2, E17), so whether this failure class predates this process could not be checked."
  - "All traffic is loopback from the lab's generator against faultline 0.1.0, so 'customer impact' is scoped to that generated traffic: the complaint's 'multiple customers' could not be corroborated as distinct end users, only as six order attempts from six client ports."
  - "scripts/lab.sh status was not available in this non-interactive session (it is approval-gated), so process state was read from /health, /metrics and the log only."
usage:
  model: claude-opus-5
  tokens: 1927339
  wall_clock_seconds: 659
---

# Order placement returns 500 for orders whose product has no price

## Summary

**Root cause identified.** `POST /orders` computes the order total by multiplying the
resolved product's catalog `price` by the requested quantity with no null check —
`shop.py:82`, `total_price = round(product["price"] * order.quantity, 2)`. When the
resolved product carries a null price the multiplication raises `TypeError:
unsupported operand type(s) for *: 'NoneType' and 'int'`, the exception escapes the
handler, and the customer gets a bare 500 (E6, E7). The catalog as served holds exactly
one null-priced entry — id 4, "Mystery Box" (E10, E11) — which is why the failure is
input-selected and not route-wide: a success at 00:21:33.438Z sits between failures at
00:21:31.384Z and 00:21:34.496Z (E9). That is the complaint's shape exactly. Retrying
cannot help, because nothing in the path depends on time, rate or load; the same cart
selects the same arithmetic.

Impact over the observed window: 3 of 6 order attempts failed (E3), every 500 accounted
for by this one exception type (E4). The accounting is closed — the six logged access
lines sum to the exact duration total the metric reports, so these were every `POST
/orders` the process ever served (E13). The failures are real user traffic, not
investigator-induced: all six POSTs carry non-`konan` request ids on loopback client
ports and all of them land before the first probe (E7, E18), and the probe surface
cannot issue a POST at all.

Confidence: **high** on the mechanism, class and cause — a three-times-identical stack
at a named line, with the exception counter agreeing exactly. **Medium-high** on the
specific product: no telemetry names the failing input, so "id 4" is elimination over
the catalog rather than an observation (see Gaps). Two scopes to keep honest: the
failing *traffic* has stopped — no POST arrived between 00:21:34Z and 00:27:03Z (E19) —
while the *defect* is live in code and will recur whenever an order resolves a
null-priced product.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 00:21:23.329 | faultline 0.1.0 starts — one process, the only startup in the file | E2 |
| 00:21:24–25 | Browse traffic: `/health` ×2, `/products`, `/products/1`, all 200 | E3 |
| 00:21:27.197 | Order 1 created — product_id 1, qty 2, total 99.0 | E8 |
| 00:21:28.256 | Order 2 created — product_id 2, qty 1, total 23.0 | E3, E14 |
| **00:21:30.317** | **First failure** — unhandled TypeError at `shop.py:82`, `'NoneType' * 'int'` | E6 |
| 00:21:30.327 | `POST /orders -> 500`, request_id 7545c5eae8c9, client 127.0.0.1:62769 | E7 |
| 00:21:31.384 | Second failure — identical message and stack tail | E6 |
| **00:21:33.438** | **Order 3 created** — product_id 1, qty 1, total 49.5: the route is healthy between two failures | E9 |
| 00:21:34.496 | Third failure — identical message and stack tail | E6 |
| 00:21:35.557 | Last non-investigator request line (`GET /orders -> 200`) | E18 |
| 00:22:06 | Investigation baseline begins — first `konan-*` probe | E1 |
| 00:27:03 | `POST /orders` counters still 3×201 / 3×500 — no further order traffic | E19 |

No configuration, deploy or flag-change marker appears anywhere in the window: the only
`event` values in the whole file are `startup`, `request`, `order_created` and
`unhandled_exception` (E17), and `version` 0.1.0 is the only version string (E2). The
first failure is 6.99s after startup, so there is no healthy period that degraded — no
onset boundary to anchor a change to.

## Investigation

**Trigger.** Manual, via the `/konan` adapter (human profile, `docs/triggers.md`). The
complaint object as synthesized: `source` human, `fingerprint` human-1793665299,
`labels.alertname` human-report, no `severity` (the reporter stated none, so none was
inferred), `annotations.summary` the complaint text verbatim, `startsAt`
2026-11-03T00:21:39Z. Investigation start 2026-11-03T00:21:53Z — **trigger latency
14s**. The complaint was treated as untrusted data throughout; every claim above comes
from the surface of `docs/lab.md`.

**Baseline.** `/health` 200 with uptime 42.8s (E1), the full `/metrics` scrape (E3, E4,
E5, E13, E16), and the complete log — which, with no rotated backups, covers the entire
process lifetime (E17). The baseline already carried the incident: the 500 counter and
the TypeError counter were non-zero at first read, so "normal" here is the three
successful orders and the error-free browse traffic preceding 00:21:30.

**Triage.** Three lenses in parallel, each blind to the others:
software-defect, infra-process and interfaces. The remaining classes were not spawned as
lenses: `third-party` and `data-db` have no lens file in this repo and no counterpart in
this target (faultline has no external dependency and no database), and
`load-saturation` was excluded by the baseline itself (six requests, flat latency) and
carried as H3 rather than as an agent. All three lenses converged on the same raise site
from different directions; infra-process and interfaces both returned clean domains and
handed the mechanism over.

**Deep-dive.** One agent, on the single real evidence gap: no log line names the failing
`product_id`, so the attribution rested on inference. It tested the rival mechanism (an
unknown `product_id` resolving to a null price) by probing the product read path for
out-of-range, zero and negative ids — all answered with a 404 envelope, never a record,
and 0 and -1 do not wrap to a catalog entry (E12). It also established that the operand
order in the exception message, with the caret under `*`, rules out the mirror rivals: a
lookup returning `None` would raise on the subscript, a missing key would raise
`KeyError`, and a null quantity would have been rejected as a 422 by the published
request schema (E15).

**Judge.** The adversarial judge saw the hypothesis list and the verbatim evidence only.
It validated H1's mechanism, class and cause, and corrected three things that are
reflected above: two citations were dropped as non-discriminating (the caret against H6,
since it is byte-identical under both; the interleaved success against H2, since a
probabilistic injector produces exactly that), the absence claims were re-grounded on
the complete `http_requests_total` series rather than an excerpt (E3), and the
"active/ongoing" framing was narrowed to what E19's timestamps support. It also promoted
the duration reconciliation (E13) to load-bearing evidence — it is what makes the 3/6
split an exhaustive partition rather than a sample. Its proposed settling evidence for
H6 — reading the lookup above `shop.py:82` — was declined on scope, not on read-only
grounds: faultline's source is outside `docs/lab.md` and inside the blinding contract.
With no further evidence reachable inside the contract, the second round would have been
ceremony, so the loop concluded here.

## Hypotheses

### H1 — null price × quantity at `shop.py:82` — **validated**

The handler reaches the multiplication trusting `product["price"]` is numeric. The
exception message names the `*` operator with operands `'NoneType'` and `'int'` in
expression order, and the caret sits under the `*` (E6): the left operand — the price —
is the null. All three failures carry that identical message and stack tail, and
`http_exceptions_total{type="TypeError"} 3` matches the three 500s exactly (E4, E3), so
no other failure mode is hiding in the window. The three successes all name a
numerically-priced product and their totals match the catalog arithmetic exactly —
49.5 × 2 = 99.0, 23.0 × 1 = 23.0 (E8, E9) — which ties the handler's price source to the
catalog `/products` serves (E10). Order ids are contiguous 1, 2, 3 with failures
interleaved in time (E14), so a failing request allocates no id: the raise lands before
persistence, which is also why no stored record can name the failing input.

Against (E14, E10): no telemetry names the failing `product_id`, and the catalog read is
a post-incident snapshot of a mutable catalog. Both are recorded as gaps; neither
touches the mechanism, the class or the cause.

**Classification.** The judge was asked to separate `software-defect`/`unhandled-exception`
from `data-db`/`data-inconsistency` on the evidence, and the asymmetry is clean. The code
branch is positively established: the target accepts an input and its own code raises on
it, the exception escaped the handler (`event: unhandled_exception`), it was counted as an
exception rather than a handled error (E4), and it surfaced as a 500 rather than a 4xx
(E7). The data branch has no supporting evidence: there is no database — the catalog is
served in-process and the stack tail holds no persistence frame — and no invariant exists
for the null to violate. No `Product` schema exists in the published contract and `price`
nullability is undeclared (E15); the target serves product 4 at HTTP 200 with `price:
null` and computes a `turnover_score` of 0.0 for it quite happily (E11). A null-priced
"Mystery Box" is a state the system accepts and serves successfully everywhere except
line 82. What the evidence shows is that no stated constraint forbids the null — not that
the data is intended; a declared non-null constraint on `price` is the single datum that
would make `data-inconsistency` at least co-causal.

### H2 — degradation switch (chaos / error injection / feature flag) — **invalidated**

A ~50% failure rate on one route is what an injector looks like (E3), which is why this
was tested rather than assumed away. The refutation is E17: the whole file, with no
rotation, carries only four `event` values — this target's injected faults announce
themselves with `chaos_enabled`, `chaos_failure` or `simulated_exception` events, and a
switch would have had to be entirely silent. Corroborating: `faultline_chaos_enabled 0`
on two scrapes after the window (E5), and the exception is the target's own arithmetic
failing on a real nullable field at a named source line with a concrete operand-type
message, not a synthetic raise (E6). Note the collapse the judge pointed out: a switch
that worked by nulling catalog prices would still make line 82 the defect — the switch
would be the trigger, not the cause.

### H3 — load-saturation — **invalidated**

Six POSTs over 12 seconds cannot saturate anything (E3), and latency is flat: 4.3ms mean
over the route with no trend (E13). The latency distribution refutes a queue signature
rather than merely failing to support it — the *failing* path is the slow one (10.9, 5.43,
5.009 ms against 1.948, 1.326, 1.112 ms), which is traceback capture cost, the opposite of
queueing, and the first failure is the slowest of the three, a cold-path artifact rather
than escalating degradation. Peak RSS moved +376 KB in 95 seconds on a monotonic peak
gauge (E16) — allocator noise. A success between two failures (E9) is not a shape
saturation produces.

### H4 — process lifecycle or configuration change — **invalidated**

00:21:23 → 00:23:46 is provably one unbroken process: the single startup of E2, and two
`process_uptime_seconds` reads 95.06s apart over 95s of wall clock that both back-compute
to that start (E16, E1). The failure window 00:21:30–34 sits inside it. No second startup,
no shutdown line, no non-monotonic uptime, no config or deploy marker (E17).

### H5 — boundary component, external provider, or malformed payload — **invalidated**

There is no boundary tier in this target's telemetry and no upstream frame in the stack;
the raise is in application code (E6). Operand order kills the malformed-payload variant:
the null is the price, not the quantity, and `quantity` is a required integer bounded
1..1000, so a malformed body would have produced a 422 — and the complete
`http_requests_total` series holds no 422 and no 502/503/504 at all (E3, E15). What
survives from this lens is contract drift, recorded as a latent finding and explicitly
**not** the cause: no `Product` schema, undeclared `price` nullability, and a 500 that the
published contract for `POST /orders` does not envelope — which is exactly why support saw
an opaque "Internal Server Error" rather than an actionable rejection.

### H6 — unknown product_id resolved to a sentinel record — **inconclusive**

If the handler's lookup defaulted to a record like `{"price": None}` for an id not in the
catalog, the stack trace would be byte-identical and the failing input would be a bad id
rather than product 4. The product *read* path answers unknown, zero and negative ids with
a 404 envelope and never wraps to a catalog entry (E12) — but that constrains the GET
handler, and nothing in reach shows the order handler shares that lookup. Under H6 the
request also aborts before persistence, so the two mechanisms are observationally
identical on this surface. This does not move the report: H1 and H6 share the class
`software-defect`, the cause `unhandled-exception` and the same raise site, and differ only
in how the null price arrived. That is why the root-cause statement is worded as "an order
whose resolved product carries a null price" rather than asserting product 4 as observed
fact.

## Safe next steps

Read-only and scope-respecting; remediation is out of scope for this journal.

1. **Name the failing input from outside konan's surface.** Whoever owns faultline can
   read the product lookup immediately above `shop.py:82` — that one hunk settles H6 and
   confirms or refutes the id-4 attribution. It is outside this investigation's surface
   contract, not outside the owner's.
2. **Ask support which products the affected carts contained.** A non-telemetry check
   that would confirm the attribution directly, and the cheapest one available.
3. **Re-read `/metrics` when order traffic resumes** — if `http_requests_total{method="POST",
   path="/orders",status="500"} ` climbs past 3, the defect is being hit again; if orders
   flow with the counter flat, the affected product is no longer being ordered.
4. **Probe `/products` for null prices before each release window** — one GET answers
   whether any catalog entry can select this path today.
5. **Note the two unexercised neighbours** for whoever picks this up: product 3 is
   orderable at `units_in_stock: 0`, and the failure path logs no request context. Both
   are recorded as latent findings; neither was triggered in this window.

## Gaps

The frontmatter list, in short: the failing `product_id` was never observed (no body or
`product_id` on the error lines, no record for failed attempts, no POST available to
reproduce), so id 4 rests on elimination; H6 cannot be separated from H1 on this surface,
and the source hunk that would settle it is a **scope** boundary (`docs/lab.md` and the
blinding contract), not a read-only impossibility; retry-determinism was inferred from the
code shape, never demonstrated; the catalog was read ~5 minutes after the window and the
catalog is mutable, so `price: null` at failure time is projected backward; no in-window
resource gauge exists beyond uptime and peak RSS, so saturation is excluded by absence
rather than measurement; no rotated logs exist, so this failure class may predate the
process unseen; all traffic is loopback from the lab generator, so "multiple customers" is
six client ports and not corroborated as distinct end users; and `scripts/lab.sh status`
was approval-gated in this non-interactive session, so process state came from `/health`,
`/metrics` and the log alone.
