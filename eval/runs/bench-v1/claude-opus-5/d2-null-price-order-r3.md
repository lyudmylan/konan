---
konan_journal: 1
investigation:
  id: 2026-08-19-order-500-null-price
  trigger: "manual — /konan adapter (human profile). Complaint object: source=human, fingerprint=human-1787123733, labels.alertname=human-report (no severity stated by the reporter), startsAt=2026-08-19T07:15:33Z. Investigation entered at 2026-08-19T07:15:39Z; trigger latency 6s."
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-19T07:15:39Z
  concluded: 2026-08-19T07:24:54Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "POST /orders has no null guard at src/faultline/shop.py:82, so an order for a catalog product whose price is null evaluates round(None * quantity, 2), raising an unhandled TypeError that escapes as HTTP 500."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "POST /orders returns 500 because src/faultline/shop.py:82 computes round(product[\"price\"] * order.quantity, 2) with no guard against a null price; when the looked-up product's price is None the resulting TypeError is unhandled and escapes as a 500."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E14, E15, E21]
    evidence_against: []
  - id: H2
    statement: "The failing orders were for product_id 4, \"Mystery Box\" — the only catalog entry whose price is null."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E10, E11, E7, E8, E9]
    evidence_against: [E22]
  - id: H3
    statement: "The cause set is exactly product 4: no other input can reach the multiplication with a None price, because an unknown product_id is rejected before the arithmetic."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E10, E12, E13]
    evidence_against: [E21]
  - id: H4
    statement: "The defect harmed non-investigator traffic and is an active incident, not a latent defect reachable only by the investigator's own probes."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E4, E6, E14, E23]
    evidence_against: []
  - id: H5
    statement: "The 500s were caused by injected chaos, a runtime config or flag change, or a deploy."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E16, E18, E1]
  - id: H6
    statement: "The 500s were caused by an infrastructure or process fault — a crash/restart, memory saturation, or a timeout/hang."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E17, E18, E19, E2, E4, E6]
  - id: H7
    statement: "The 500s were probabilistic per-request failures (a flaky dependency or gateway), not data-dependent."
    incident_class: third-party
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E3, E5, E14, E15, E10, E11]
  - id: H8
    statement: "Ordering product 3 (\"Unobtainium Ingot\", units_in_stock 0) or product 5 fails on a separate code path."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E20]
    evidence_against: [E10]
latent_findings:
  - statement: "The published API contract does not admit the observed failure: POST /orders declares only 201 and 422 responses, so the 500 users receive is an undeclared response, and the product schemas declare no type or nullability for price, so a null price violates no documented contract at the read edge."
    evidence: [E21, E10, E11]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:21.549Z"
    quote: "{\"ts\": \"2026-08-19T07:15:21.549Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"4d02a2a48d9a\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\", \"stack\": \"Traceback (most recent call last):\\n … \\n  File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:21.560Z"
    quote: "{\"ts\": \"2026-08-19T07:15:21.560Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 500\", \"request_id\": \"4d02a2a48d9a\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 500, \"duration_ms\": 12.001, \"client\": \"127.0.0.1:57850\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:22.617Z"
    quote: "{\"ts\": \"2026-08-19T07:15:22.617Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"080ad366a415\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\", \"stack\": \"… File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\"} — stack byte-identical to E1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:22.622Z"
    quote: "{\"ts\": \"2026-08-19T07:15:22.622Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 500\", \"request_id\": \"080ad366a415\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 500, \"duration_ms\": 5.529, \"client\": \"127.0.0.1:57852\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:25.743Z"
    quote: "{\"ts\": \"2026-08-19T07:15:25.743Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"0d937a5fd7d3\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\", \"stack\": \"… File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 82, in create_order\\n    total_price = round(product[\\\"price\\\"] * order.quantity, 2)\\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'\"} — stack byte-identical to E1"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:25.747Z"
    quote: "{\"ts\": \"2026-08-19T07:15:25.747Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 500\", \"request_id\": \"0d937a5fd7d3\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 500, \"duration_ms\": 5.228, \"client\": \"127.0.0.1:57854\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:18.430Z"
    quote: "{\"ts\": \"2026-08-19T07:15:18.430Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"aeff428396bf\", \"event\": \"order_created\", \"order_id\": 1, \"product_id\": 1, \"quantity\": 2, \"total_price\": 99.0}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:19.490Z"
    quote: "{\"ts\": \"2026-08-19T07:15:19.490Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"0b8b9af30175\", \"event\": \"order_created\", \"order_id\": 2, \"product_id\": 2, \"quantity\": 1, \"total_price\": 23.0}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:24.682Z"
    quote: "{\"ts\": \"2026-08-19T07:15:24.682Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"56774a222618\", \"event\": \"order_created\", \"order_id\": 3, \"product_id\": 1, \"quantity\": 1, \"total_price\": 49.5}"
  - id: E10
    type: probe
    source: "GET /products — request_id konan-1787124248-50174, HTTP 200"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":117},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E11
    type: probe
    source: "GET /products/4 — request_id konan-1787123964-50027, HTTP 200"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0}"
  - id: E12
    type: probe
    source: "GET /products/99 — request_id konan-1787123965-50039, HTTP 404"
    quote: "{\"detail\":\"no such product: 99\"}"
  - id: E13
    type: probe
    source: "GET /products/6 — request_id konan-1787123964-50033, HTTP 404 (same shape returned for /products/0 and /products/-1)"
    quote: "{\"detail\":\"no such product: 6\"}"
  - id: E14
    type: metric
    source: "GET /metrics — request_id konan-1787124278-50186"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3 / http_request_duration_seconds_count{method=\"POST\",path=\"/orders\"} 6"
  - id: E15
    type: metric
    source: "GET /metrics — request_id konan-1787124278-50186"
    quote: "http_exceptions_total{type=\"TypeError\"} 3 — the only http_exceptions_total series present"
  - id: E16
    type: metric
    source: "GET /metrics — request_id konan-1787124278-50186"
    quote: "faultline_chaos_enabled 0"
  - id: E17
    type: metric
    source: "GET /metrics — request_id konan-1787124278-50186"
    quote: "process_uptime_seconds 564.049040208105 / process_max_rss_bytes 47398912 — max_rss byte-identical across four samples spanning ~525s; http_request_duration_seconds_sum{method=\"POST\",path=\"/orders\"} 0.027471123496070504 over _count 6"
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:14.550Z"
    quote: "{\"ts\": \"2026-08-19T07:15:14.550Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"} — the only lifecycle line in the file; lab/logs/ holds app.log only (no .1-.3 rotation backups), and no chaos_enabled, chaos_disabled, chaos_failure or simulated_exception event appears anywhere in it"
  - id: E19
    type: probe
    source: "GET /health — request_id konan-1787123750-49827, HTTP 200"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":35.686682750005275} — later samples 111.93, 150.823, 259.8, 564.05 advance 1:1 with wall clock, no counter reset"
  - id: E20
    type: probe
    source: "GET /orders — request_id konan-1787123963-50021, HTTP 200"
    quote: "three orders only, product_ids 1, 2, 1 — no order for product 3, 4 or 5 exists; GET /orders/4 -> HTTP 404 {\"detail\":\"no such order: 4\"}"
  - id: E21
    type: probe
    source: "GET /openapi.json — request_id konan-1787123842-49974, HTTP 200"
    quote: "OrderRequest.quantity: {\"type\":\"integer\",\"maximum\":1000,\"minimum\":1}; POST /orders declares responses 201 and 422 only; product responses typed {\"type\":\"object\",\"additionalProperties\":true} with no price type or nullability declared"
  - id: E22
    type: log
    source: "lab/logs/app.log — complete file, 24 lines, read in full"
    quote: "Each failing request_id carries exactly two lines: the unhandled_exception line and the access line (4d02a2a48d9a -> E1+E2; 080ad366a415 -> E3+E4; 0d937a5fd7d3 -> E5+E6). No order_created line exists for any failure, and the access line records method, path, status, duration_ms, client — never the request body. No log line, metric label or probe response on the permitted surface names the product_id of any failed order."
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:15:21.549Z–07:15:26.805Z"
    quote: "The three failing request_ids (4d02a2a48d9a, 080ad366a415, 0d937a5fd7d3) are bare 12-hex ids with no \"konan-\" prefix; every investigator probe is stamped konan-<epoch>-<pid>. No unprefixed request_id appears after 07:15:26.805Z, and http_request_duration_seconds_count{method=\"POST\",path=\"/orders\"} has stayed at 6 through the final scrape."
gaps:
  - "The product_id of a failed order is not recoverable from any permitted surface (E22): order_created is emitted only after the price arithmetic succeeds, and the access line never carries the request body. The attribution of the failures to product 4 (H2) is therefore an inference from the catalog, not a direct observation."
  - "The catalog was read minutes after the failures (E10, E11). Its state at 07:15:21Z is not in evidence, so a price that changed between the failures and the probe is not excluded."
  - "H3's exclusivity claim cannot be settled read-only: the clean 404s in E12/E13 come from GET /products/{product_id}, a different route from POST /orders. Whether create_order shares that lookup — and so rejects an unknown product_id before line 82 — needs the source of create_order, which is outside the surface contract and outside the blinding boundary."
  - "The converse of the prediction is only partly tested: orders are observed to succeed for products 1 and 2 (E7, E8, E9); products 3 and 5 have never been ordered (E20). Confirming they order fine needs a POST, which the GET-only probe allowlist forbids."
  - "Whether product 4 is orderable from a live storefront right now — the real forward exposure — is not observable from this surface. Non-investigator traffic stopped at 07:15:26.805Z (E23), so the measured blast radius is bounded by the traffic that happened to arrive, not by the defect's reach."
  - "Whether the null price is itself an upstream catalog-data fault (a product published without a price) or a deliberate sentinel the order path should handle is not distinguishable from telemetry; the two readings put the defect in different components."
usage:
  model: claude-opus-5
  tokens: 2107280
  wall_clock_seconds: 555
---

# Orders fail with 500 for a product whose price is null

## Summary

**Root cause identified — a software defect in the order path.** `POST /orders`
computes `total_price = round(product["price"] * order.quantity, 2)` at
`src/faultline/shop.py:82` with no guard against a null price. When the ordered
product's price is `None`, the multiplication raises `TypeError: unsupported operand
type(s) for *: 'NoneType' and 'int'`; nothing catches it, so it escapes to the client
as HTTP 500 "Internal Server Error" (E1, E2, E15). The failure is deterministic in the
input, which is exactly the reported shape: the same customer ordering the same product
fails on every retry, while customers ordering other products succeed — a success is
logged *between* two failures (E9), so no time-varying condition is involved.

Impact is confined to `POST /orders`: 3 failures against 3 successes in a 4.2-second
window, 07:15:21.549Z–07:15:25.747Z, all in non-investigator traffic (E14, E23). No
partial writes — the exception precedes persistence, so no failed order left a row
(E20). Health stayed green throughout (E19), which is why the complaint reached support
before it reached monitoring.

Confidence is high on the mechanism and lower on the input. Only one catalog entry has
a null price — product 4, "Mystery Box" (E10, E11) — so it is the probable input, but
the failing requests' bodies are not recoverable from any permitted surface (E22). The
adversarial judge held that attribution at *inconclusive*, and this journal keeps it
there: what is proven is that *a product with a null price* reached line 82, not which
id the customers sent.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 07:15:14.550Z | faultline 0.1.0 starts — the only lifecycle marker in the retained log; no config, flag, deploy or chaos marker appears anywhere | E18 |
| 07:15:18.430Z | Order 1 created, product_id 1, total 99.0 | E7 |
| 07:15:19.490Z | Order 2 created, product_id 2, total 23.0 — last known-good order | E8 |
| 07:15:21.549Z | First unhandled TypeError at `shop.py:82` | E1 |
| 07:15:21.560Z | `POST /orders -> 500`, 12.001 ms | E2 |
| 07:15:22.617Z | Second TypeError, byte-identical stack | E3 |
| 07:15:22.622Z | `POST /orders -> 500`, 5.529 ms | E4 |
| 07:15:24.682Z | **Order 3 created, product_id 1** — a success between two failures | E9 |
| 07:15:25.743Z | Third TypeError, byte-identical stack | E5 |
| 07:15:25.747Z | `POST /orders -> 500`, 5.228 ms | E6 |
| 07:15:26.805Z | Last non-investigator request; `POST /orders` count has stayed at 6 since | E23, E14 |
| 07:15:33Z | Complaint raised by support | — |
| 07:15:39Z | Investigation starts (trigger latency 6s) | — |

No configuration, deploy or flag-change marker exists in the window (E18), so the
onset is not change-driven.

## Investigation

**Baseline.** `/health` returned 200 with the process 35s old; `/metrics` showed
`POST /orders` split 3×201 / 3×500, `http_exceptions_total{type="TypeError"} 3`, and
`faultline_chaos_enabled 0`; the log was 24 lines covering the whole process life. The
business surface was already contradicting the green health endpoint at baseline — the
healthy-monitoring shape.

**Triage — three lenses in parallel, each blind to the others.** software-defect,
infra-process and interfaces. None was skipped, so no domain was accepted as a blind
spot. All three converged on the same line of code and independently excluded their own
domains: infra-process ruled out crash, restart, saturation and latency; interfaces
ruled out change-driven onset and gateway/dependency flakiness, and added the contract
gap now recorded as a latent finding.

**Deep-dive — one hypothesis, one agent.** Triage evidence for the mechanism was
already deterministic, so the deep-dive was aimed only at the gap: could anything *other
than* product 4 supply a `None` price — in particular, could an unknown product_id
reach the arithmetic through a default record? It enumerated the catalog (one null
price, product 4), probed ids 6/99/0/-1 (all clean 404s on the read path), and returned
the finding that matters most here: the failing request bodies are unrecoverable, so
the product attribution is inference, not observation.

**Judge — adversarial, evidence-only.** The judge saw the hypothesis list and the
verbatim quotes, never the narrative. It validated H1, H4, and the three refutations
(H5, H6, H7), and it pushed back on two claims this investigation had been ready to
state more strongly:

- **H2 and H3 were downgraded to inconclusive.** The catalog snapshot was taken minutes
  after the failures, and E12/E13's 404s come from `GET /products/{id}`, not from the
  order path — a read-path 404 does not prove the write path guards its lookup.
- **H4's arithmetic was corrected.** The 50% error rate holds over the whole six-request
  session, not over the 4.2-second window quoted with it; within that window three of
  four `POST /orders` failed (75%). The journal uses both figures correctly above.
- The judge also flagged that "real users" overreaches what the evidence shows — all
  clients are `127.0.0.1` on a lab target — so this journal says *non-investigator
  traffic* throughout, which is what E23 supports.

Both of the judge's settling items (a failure record carrying the product_id; the body
of `create_order`) are unreachable from the permitted surface, so a second round could
not close them. The investigation concluded rather than manufacture certainty.

## Hypotheses

### H1 — unguarded null price at `shop.py:82` → **validated**

Three failures, three byte-identical tracebacks terminating at the same frame (E1, E3,
E5), each immediately followed by a 500 on `POST /orders` (E2, E4, E6). The Python
error message puts `NoneType` on the left of the `*`, which is `product["price"]`; the
right operand cannot be the null, because `OrderRequest.quantity` is typed
`{"type":"integer","minimum":1,"maximum":1000}` and a null or zero quantity would be
rejected as 422 before reaching line 82 (E21). `http_exceptions_total{type="TypeError"}
3` is the only exception series and matches the 500 count exactly (E15) — one cause, no
second failure mode hiding behind it. Nothing argues against it.

### H2 — the failing input was product 4, "Mystery Box" → **inconclusive**

Product 4 is the only catalog entry of five with `price: null`, on both the collection
and the item route (E10, E11), and every observed success is a numerically-priced
product (E7, E8, E9). That makes it the strongly probable input. It is not proven:
no permitted surface records the product_id of a failed order (E22), and the catalog
was read after the fact. Settling it needs a failure record that carries the request's
product_id — an observability change in the target, not more probing.

### H3 — the cause set is exactly product 4 → **inconclusive**

Unknown ids 404 cleanly on the read path (E12, E13), and the traceback shape argues
against a synthesized record: `product["price"]` subscripted successfully and yielded
`None`, so `product` was a mapping — a missing lookup returning `None` outright would
have failed at the subscript with "'NoneType' object is not subscriptable", not at the
`*`. But that is inference about code, and `POST /orders` documents no 404 at all
(E21), so the order path's miss behaviour is genuinely unobserved. Held open.

### H4 — active incident, not a latent finding → **validated**

All three failing request_ids are bare 12-hex ids; every investigator probe carries a
`konan-` prefix (E23). The defect was therefore triggered by traffic other than this
investigation's — the incident is real, not self-inflicted. Scope: 3 of 6 `POST /orders`
over the session (50%), 3 of 4 within the failure window (75%). `POST /orders` has taken
no further traffic since 07:15:26.805Z, so no failures are accruing right now — but that
reflects absent traffic, not a fixed defect.

### H5 — chaos, config change or deploy → **invalidated**

One startup marker and no rotation backups, so the retained log spans a single
continuous process life covering the failures; no `chaos_enabled`, `chaos_disabled`,
`chaos_failure` or `simulated_exception` event exists anywhere in it (E18), and
`faultline_chaos_enabled` reads 0 (E16). The traceback names a real application source
frame rather than an injected generic error (E1). Noted honestly: the chaos gauge is a
probe-time reading and cannot by itself speak for 07:15:21Z — the refutation rests on
the absence of any toggle *event*, which the log would have recorded.

### H6 — infrastructure or process fault → **invalidated**

Uptime advances 1:1 with wall clock across four samples with no counter reset, against a
single startup at 07:15:14.550Z (E19, E18) — no crash or restart across the window.
`process_max_rss_bytes` is a monotone high-water mark and is byte-identical across all
samples (E17), so peak memory never grew: no leak, no saturation. The failures completed
in 5–12 ms (E2, E4, E6) — a fast error path, not a timeout or hang. The largest is the
first, consistent with one-off traceback formatting.

### H7 — probabilistic or dependency-driven failure → **invalidated**

An in-process exception with an application source frame (E1, E3, E5), a single
exception type, and no 502/503/504 series anywhere (E14, E15) exclude a gateway or
upstream fault. Note on citation discipline: the interleaved success (E9) is *not* what
kills this hypothesis — a probabilistic fault predicts interleaving too. What kills it
is the persistent null in the catalog (E10, E11) plus three identical stacks at one
line: a random fault would not land on the same operand every time.

### H8 — product 3 or 5 fails on a separate path → **inconclusive**

Raised because product 3 shows `units_in_stock: 0` (E10), which suggests a stock branch
that has never been exercised. Neither product has ever been ordered (E20), and absence
of an attempt is not evidence of a failure path. Both carry well-formed prices (999.0
and 6.25), so neither can hit the H1 mechanism. Closing this needs a POST, which the
investigator's GET-only allowlist forbids.

## Safe next steps

Read-only and observational only:

1. **Confirm the attribution without guessing** — inspect the order path's handling of a
   product with no price, and check whether the catalog's null price for product 4 is
   intended (a sentinel for an unpriced item) or a data fault (a product published
   without a price). The two readings put the defect in different components.
2. **Close the observability gap the investigation exposed** — no telemetry names the
   product_id of a failed order, which is what forced H2 to stay inconclusive. Logging
   the ordered product_id on the failure path (or emitting an attempt event before the
   price arithmetic) would make this class of incident directly attributable instead of
   inferable. This is worth filing independently of the defect itself.
3. **Watch for recurrence** — `http_requests_total{method="POST",path="/orders",status="500"}`
   and `http_exceptions_total{type="TypeError"}` are exact counters for this failure; a
   green `/health` will not move when they do (E19), so alert on the business surface.
4. **Check the API contract** — `POST /orders` returns an undeclared 500 and the product
   schemas declare no nullability for `price` (E21). Clients cannot distinguish this
   from any other server fault.

Remediation is out of scope for this journal, and konan touches the target read-only.

## Gaps

- **The failing requests' inputs are unrecoverable.** Each failure carries exactly two
  log lines — the exception and the access line — and neither records the body (E22).
  This is the single reason H2 is inconclusive rather than validated.
- **The catalog was read after the fact.** E10 and E11 are minutes later than the
  failures; the catalog's state at 07:15:21Z is not in evidence.
- **The order path's lookup is unobservable.** E12/E13's clean 404s come from the read
  route. Whether `create_order` shares that lookup needs its source, which is outside
  the surface contract and the blinding boundary — so H3 cannot be closed by any amount
  of further probing.
- **The prediction's converse is only partly tested.** Products 3 and 5 have never been
  ordered (E20); confirming they order fine needs a POST, which the allowlist forbids.
- **Forward exposure is unknown.** Non-investigator traffic stopped at 07:15:26.805Z
  (E23), so the measured blast radius is bounded by the traffic that arrived, not by the
  defect's reach. Whether product 4 is orderable from a live storefront now is not
  visible from this surface.
- **Cause of the null price is undetermined** — upstream catalog-data fault versus
  intended sentinel is not distinguishable from telemetry.

No lens was skipped at triage: software-defect, infra-process and interfaces all ran, so
no domain was accepted as a blind spot.
