---
konan_journal: 1
investigation:
  id: 2026-08-19-order-500s-null-price
  trigger: "manual (/konan human profile; complaint object: source=human, fingerprint=human-1787176843, labels.alertname=human-report, startsAt=2026-08-19T22:00:43Z; investigation started 2026-08-19T22:01:12Z; trigger latency 29s)"
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-19T22:01:12Z
  concluded: 2026-08-19T22:06:35Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Product 4 (\"Mystery Box\") carries price=null in the catalog; create_order at shop.py:82 computes product[\"price\"] * order.quantity with no null guard, so every order for that product raises an unhandled TypeError and returns HTTP 500, while orders for numeric-price products succeed."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "Orders for product 4 (\"Mystery Box\"), the only catalog record with price=null, fail with HTTP 500: create_order at shop.py:82 multiplies product[\"price\"] by order.quantity with no null guard, raising an unhandled TypeError; orders for numeric-price products succeed. Data-dependent, so retries of the same product fail again."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E9, E10]
    evidence_against: []
  - id: H2
    statement: "The order failures were caused by injected chaos, a configuration/flag change, or a failing dependency producing probabilistic per-request errors."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E1, E4, E6]
  - id: H3
    statement: "A process lifecycle or resource event (restart loop, memory exhaustion, worker starvation) caused the order failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E11, E12, E4]
latent_findings:
  - statement: "Contract gap at the API boundary: /openapi.json declares only 201 and 422 for POST /orders (the 500 is an undeclared unhandled-exception path), and the /products response schema is a free-form object with no price type or nullability constraint, so a null price passes the boundary unvalidated and only surfaces deep in order pricing."
    evidence: [E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T22:00:21.033Z (third line of the file; no rotated backups exist)"
    quote: "{\"ts\": \"2026-08-19T22:00:21.033Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T22:00:28.069Z (stack field of the unhandled_exception entry, trimmed to the throw site)"
    quote: "File \"<checkout>/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T22:00:28.069Z (identical TypeError stacks, same shop.py line 82, also at 22:00:29.148 request_id ed0cce3ddc01 and 22:00:32.288 request_id 9b699a563486)"
    quote: "{\"ts\": \"2026-08-19T22:00:28.069Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"2d45a2793728\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\", ...}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T22:00:24.933Z–22:00:32.293Z (POST /orders access lines; none carry a konan- request id — all user traffic)"
    quote: "\"POST /orders -> 201\" duration_ms 1.968 @ 22:00:24.933; \"POST /orders -> 201\" duration_ms 1.305 @ 22:00:26.001; \"POST /orders -> 500\" duration_ms 11.622 @ 22:00:28.080; \"POST /orders -> 500\" duration_ms 5.465 @ 22:00:29.153; \"POST /orders -> 201\" duration_ms 1.277 @ 22:00:31.223; \"POST /orders -> 500\" duration_ms 5.906 @ 22:00:32.293"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T22:00:24.932Z (order_created lines also at 22:00:26.000 product_id 2 total_price 23.0 and 22:00:31.222 product_id 1 total_price 49.5; the three 500 requests emit no order_created line and no product_id)"
    quote: "{\"ts\": \"2026-08-19T22:00:24.932Z\", \"level\": \"INFO\", \"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"3b3b93d99f04\", \"event\": \"order_created\", \"order_id\": 1, \"product_id\": 1, \"quantity\": 2, \"total_price\": 99.0}"
  - id: E6
    type: metric
    source: "GET /metrics @ 2026-08-19T22:01:18Z, request_id konan-1787176877-73306 (all GET routes carried status 200 only)"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3"
  - id: E7
    type: metric
    source: "GET /metrics @ 2026-08-19T22:01:18Z, request_id konan-1787176877-73306 (the only exception counter present)"
    quote: "http_exceptions_total{type=\"TypeError\"} 3"
  - id: E8
    type: metric
    source: "GET /metrics @ 2026-08-19T22:01:18Z, request_id konan-1787176877-73306 (additionally: zero chaos_enabled / chaos_disabled / chaos_failure / simulated_exception events anywhere in lab/logs/app.log, which covers the whole process lifetime per E1)"
    quote: "faultline_chaos_enabled 0"
  - id: E9
    type: probe
    source: "GET /products, request_id konan-1787177073-73463, HTTP 200"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":117},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E10
    type: probe
    source: "GET /products/4, request_id konan-1787177073-73469, HTTP 200"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0}"
  - id: E11
    type: metric
    source: "GET /metrics, two scrapes ~12s apart during the investigation (infra-process lens probes)"
    quote: "process_uptime_seconds 152.67757758311927 -> 164.25819383305497 (strictly monotonic, consistent with a single start at 22:00:21Z); process_max_rss_bytes 48414720 (byte-identical between scrapes)"
  - id: E12
    type: probe
    source: "GET /health, request_id konan-1787176877-73300, HTTP 200 (every /health probe during the investigation returned 200)"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":56.68372837500647}"
  - id: E13
    type: probe
    source: "GET /openapi.json, request_id konan-1787176987-73431, HTTP 200"
    quote: "POST /orders declares only \"201\" and \"422\" responses; /products and /products/{product_id} declare their 200 body as {\"additionalProperties\":true,\"type\":\"object\"}"
gaps:
  - "No controlled reproduction: the investigator surface is GET-only, so POST /orders for product 4 could not be probed. Determinism is inferred from the mechanism (E2: None * int must raise) plus three identical failures (E3), not from a repeated trial."
  - "The 500 path logs no product_id (E5), so the tie from the three failed requests to product 4 is by elimination: product 4 is the only null-price record in the catalog (E9)."
  - "Products 3 and 5 were never ordered in the window; the evidence is silent on them. The safe claim is the narrower one: all observed successes reference numeric-price products (E5)."
  - "No user traffic exists after 22:00:33.362Z, so the complaint's 'keeps failing when they retry' rests on the three clustered 500s inside 22:00:28–22:00:32; no later retry traffic was observed."
  - "Triage subagents had some probe/grep commands denied by the session permission system; all findings were re-grounded in direct log reads and orchestrator-run probes, so no claim rests on a blocked command."
usage:
  model: claude-fable-5
  tokens: 2011499
  wall_clock_seconds: 323
---

# Orders for the null-price product 4 ("Mystery Box") fail with 500

## Summary

Root cause identified. `POST /orders` returns HTTP 500 for orders of product 4
("Mystery Box"), the only catalog record with `price: null` (E9, E10). The handler
`create_order` at `shop.py:82` computes `product["price"] * order.quantity` with no
null guard, which raises an unhandled `TypeError` that escapes to the middleware and
becomes a bare 500 (E2, E3). The failure is data-dependent, not probabilistic: retries
of the same product hit the same code path and fail every time, while orders for
numeric-price products succeed in the same seconds (E4, E5) — exactly the complaint's
shape ("keeps failing when they retry", "other customers' orders are going through
fine"). User impact: 3 of 6 real order attempts failed (50%) in the window
22:00:28–22:00:32Z; no investigator traffic is mixed into that count. Confidence is
high, with one stated limit: the tie to product 4 is by elimination (single null-price
record), since the 500 path logs no product_id and the read-only surface forbids a
reproduction POST.

## Timeline

- 22:00:21.033Z — process start, faultline 0.1.0, single startup marker for the whole
  log (E1). No configuration, chaos, flag, or deploy change markers appear anywhere in
  the log after it (E8).
- 22:00:24.933Z, 22:00:26.001Z — successful orders, products 1 and 2 (E4, E5).
- 22:00:28.069Z — first unhandled `TypeError` at `shop.py:82`; access line
  `POST /orders -> 500` at 22:00:28.080 (E2, E3, E4).
- 22:00:29.148Z — second identical failure (E3, E4).
- 22:00:31.223Z — successful order (product 1) between the failures (E4, E5).
- 22:00:32.288Z — third identical failure; last user order traffic (E3, E4).
- 22:00:33.362Z — last unstamped user request (`GET /orders -> 200`).
- 22:00:43Z — complaint raised (`startsAt`); 22:01:12Z — investigation start
  (trigger latency 29s).
- 22:01:12–22:01:18Z — baseline: health 200 (E12), metrics snapshot (E6, E7, E8).
- ~22:02–22:04Z — triage probes: catalog reveals product 4 with `price: null`
  (E9, E10); OpenAPI contract gap noted (E13).

## Investigation

Baseline (health, metrics, log tail) already showed the defect shape: three 201s and
three 500s on `POST /orders`, three `TypeError` exceptions, chaos off. Triage fanned
out three parallel lenses — software-defect, interfaces, infra-process — each given
only the lens file, the surface contract, the complaint verbatim, and the baseline.
The software-defect lens pinned the throw site and the per-input interleaving; the
interfaces lens ruled out change events and found the null-price record via
`GET /products`; the infra-process lens ruled out restarts, saturation, and latency
drift. Triage evidence for H1 was deterministic and complete, so no deep-dive round
was needed; all three hypotheses went to a fresh adversarial judge with claims and
verbatim evidence only. The judge validated H1 and invalidated H2 and H3, flagging
the elimination-based product tie and the impossibility of controlled reproduction —
both recorded as gaps.

## Hypotheses

### H1 — null-price product defect (validated)

Orders for product 4 fail because `create_order` multiplies a `None` price by the
quantity (E2). All three 500s carry the identical stack (E3) and match the exception
counter exactly (E6, E7). Product 4 is the only null-price record (E9, E10); every
observed success references a numeric-price product (E5). Failures interleave with
successes seconds apart on the same route (E4), which excludes any global degradation.
Nothing in the evidence contradicts H1.

### H2 — injected chaos / config change / dependency (invalidated)

The chaos gauge reads 0 and the full-lifetime log contains zero chaos or simulation
events (E8, anchored by E1). All 5xx are confined to one route (E6), the failures are
fast in-process exceptions rather than gateway-shaped errors (E4), and there is no
onset step — a success occurs after two failures. The judge invalidated; what would
overturn it is a chaos/config marker before 22:00:28 correlated with the failing
request ids.

### H3 — process lifecycle / resource event (invalidated)

Single startup, strictly monotonic uptime, byte-identical RSS between scrapes (E1,
E11), health 200 throughout (E12), and millisecond-fast 500s interleaved with 201s
(E4). The judge invalidated; a second startup event or an uptime reset inside
22:00:21–22:00:33 would overturn it.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

- Watch `http_requests_total{method="POST",path="/orders",status="500"}` and
  `http_exceptions_total{type="TypeError"}` for growth — any increase means users are
  still hitting the defect.
- Re-probe `GET /products` periodically for other records with `price: null`; today
  only product 4 carries one.
- Ask support to confirm from tickets that the affected customers were ordering
  "Mystery Box" (product 4) — this would close the elimination gap without touching
  the target.

## Gaps

Elaborated from the frontmatter list: the surface is GET-only, so the failure could
not be reproduced under a stamped request id; the 500 path logs no product_id, so the
product tie is by elimination against a catalog with exactly one null-price record;
products 3 and 5 were never ordered in the window, so the "numeric prices succeed"
claim is bounded to the observed successes; no post-22:00:33Z user traffic exists to
directly corroborate the retry claim; and a few subagent probe/grep invocations were
denied by session permissions but every finding was re-grounded through allowed reads
and orchestrator probes.
