---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-handover-check
  trigger: "manual — /konan human profile. Complaint object: source=human, fingerprint=human-1787139020, labels.alertname=human-report (no severity stated by reporter), startsAt=2026-08-19T11:30:20Z. Investigation start 2026-08-19T11:30:27Z; trigger latency 7s."
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-08-19T11:30:27Z
  concluded: 2026-08-19T11:36:36Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "There is an active, user-facing fault in the shop service at the time of this check."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E4, E12, E15]
  - id: H2
    statement: "GET /products/{id} raises an unhandled ZeroDivisionError and returns HTTP 500 for any product whose units_in_stock is 0, because shop.py:64 divides units_ordered by product['units_in_stock'] with no zero guard. Latent: only konan-stamped investigator traffic has ever triggered it."
    incident_class: software-defect
    state: validated
    evidence_for: [E5, E6, E7, E8, E9, E4]
    evidence_against: []
  - id: H3
    statement: "The service is suffering an infrastructure or process fault — crash loop, restart, memory saturation, or latency degradation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E12]
  - id: H4
    statement: "Injected chaos or a simulated fault is currently degrading the service."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E15, E6]
  - id: H5
    statement: "The published OpenAPI contract for /products/{product_id} and /orders/{order_id} declares only 200 and 422 while both routes serve 404 in practice and the products route also serves 500; the service returns two mutually incompatible error envelopes and leaks an internal Python exception class name to callers."
    incident_class: interfaces
    state: validated
    evidence_for: [E10, E14, E13, E5]
    evidence_against: []
  - id: H6
    statement: "The null price on product 4 causes a downstream failure in the order path."
    incident_class: data-db
    state: inconclusive
    evidence_for: [E11]
    evidence_against: []
latent_findings:
  - statement: "Unguarded division at shop.py:64 makes the product detail page return HTTP 500 for any zero-stock product. Product 3 ('Unobtainium Ingot') is currently the only zero-stock catalog row. No real user has requested it during this process's life, so the defect is armed but unfired — it becomes user-facing the moment any customer opens that product, or any stocked product sells out."
    evidence: [E5, E6, E7, E8]
  - statement: "OpenAPI contract drift: /products/{product_id} and /orders/{order_id} both declare only 200 and 422, but serve 404, and the products route serves 500. A generated client has no branch for either. The two error envelopes are incompatible shapes ({'detail': ...} versus {'error','exception_type','request_id'}), and the 500 body exposes the internal Python exception class name to the caller."
    evidence: [E10, E14, E13, E5]
  - statement: "Product 4 ('Mystery Box') carries price: null where every other catalog row carries a number. The read path handles it cleanly; the order path was not testable read-only."
    evidence: [E11]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id=konan-1787139041-55516"
    quote: '{"status":"ok","uptime_seconds":38.56843450013548} -- HTTP 200 in 0.002662s'
  - id: E2
    type: metric
    source: "/metrics at 2026-08-19T11:30:41Z (baseline, before any probe beyond /health and /metrics)"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n(no series lines — counter family empty)\nfaultline_chaos_enabled 0"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:30:03.109Z"
    quote: '{"ts": "2026-08-19T11:30:03.109Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E4
    type: log
    source: "lab/logs/app.log, complete set of non-konan-stamped request lines, 2026-08-19T11:30:03Z–11:30:12Z (message fields)"
    quote: '"GET /health -> 200", "GET /health -> 200", "GET /products -> 200", "GET /products/1 -> 200", "GET /products/2 -> 200", "POST /orders -> 201", "POST /orders -> 201", "GET /orders -> 200", "GET /products/5 -> 200"'
  - id: E5
    type: probe
    source: "/products/3, request_id=konan-1787139132-55677"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787139132-55677"} -- HTTP 500 in 0.004056s'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T11:32:01.507Z (stack trimmed to the throwing frame; kept fields unaltered)"
    quote: '{"ts": "2026-08-19T11:32:01.507Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787139121-55631", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}'
  - id: E7
    type: metric
    source: "/metrics at 2026-08-19T11:35:48Z (post-triage), correlated with access lines in lab/logs/app.log"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 3 ; http_requests_total{method="GET",path="/products/{product_id}",status="500"} 3 ; the three 500 access lines carry request ids konan-1787139121-55631, konan-1787139129-55661, konan-1787139132-55677'
  - id: E8
    type: probe
    source: "/products, HTTP 200 (catalog row for product 3)"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
  - id: E9
    type: probe
    source: "/products/1 and /products/4, both HTTP 200"
    quote: '"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815 ; /products/4 -> "turnover_score":0.0'
  - id: E10
    type: probe
    source: "/openapi.json, request_id=konan-1787139369-55924 — declared responses for GET /products/{product_id}"
    quote: 'status code keys declared: "200", "422" (no 404, no 5xx)'
  - id: E11
    type: probe
    source: "/products/4, HTTP 200"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}'
  - id: E12
    type: metric
    source: "/metrics, five samples across 2026-08-19T11:30:41Z–11:35:48Z, plus lab/server.out"
    quote: 'process_uptime_seconds 38.63 -> 121.00 -> 146.03 -> 152.15 -> 154.95 -> 345.43 (monotonic, no reset) ; process_max_rss_bytes 47349760 byte-identical at every sample ; lab/server.out holds exactly one "Started server process [55408]"'
  - id: E13
    type: probe
    source: "/products/999, /orders/99, /orders/1"
    quote: 'GET /products/999 -> HTTP 404 {"detail":"no such product: 999"} ; GET /orders/99 -> HTTP 404 {"detail":"no such order: 99"} ; GET /orders/1 -> HTTP 200'
  - id: E14
    type: probe
    source: "/openapi.json, request_id=konan-1787139369-55924 — declared responses for GET /orders/{order_id}"
    quote: 'status code keys declared: "200", "422" (no 404, no 5xx)'
  - id: E15
    type: metric
    source: "/metrics at 2026-08-19T11:35:48Z, request_id=konan-1787139348-55913"
    quote: 'faultline_chaos_enabled 0 ; http_requests_total{method="POST",path="/orders",status="201"} 2 (unchanged since 11:30:09Z) ; process_uptime_seconds 345.4343126669992'
gaps:
  - "The observable window is only this process's life, starting 2026-08-19T11:30:03.109Z (E3). lab/logs/ holds app.log alone with no .1-.3 rotated backups, so nothing before that instant is retained. If the handover question includes 'did the shop bounce or misbehave overnight', this surface cannot answer it either way."
  - "No real user traffic has reached the service since 2026-08-19T11:30:12.395Z (E4, E15). Every request in the current window is investigator-stamped. The 'nothing is wrong right now' verdict therefore rests on synthetic probes against an idle shop, not on live user demand — it is a statement about service capability, not about a served user population."
  - "H6 is untestable from the investigator surface: POST /orders is not on the probe allowlist (docs/lab.md), so the null-price order path could not be exercised. Only the eval side may generate that traffic."
  - "Latency was never measured under real load. All timings are single konan probes over a ~6 minute window against an idle service; /metrics exposes a duration summary (sum/count) but no histogram or quantiles, so no tail-latency claim is possible."
  - "Product 3 is the only zero-stock row in the catalog, so H2's universal form ('any product whose stock is 0') generalizes from one instance via the unguarded code line in E6, not from two observed instances."
  - "One Bash call in the orchestrator session and two in the infra-process lens session were denied by the boundary hook. None was worked around; the infra lens re-ran its probe as single calls and its ps liveness check was redundant given the monotonic uptime gauge (E12). No evidence was lost."
usage:
  model: claude-opus-5
  tokens: 2375375
  wall_clock_seconds: 369
---

# Shop service handover check — no active incident, one armed latent defect

## Summary

**Verdict: no active incident.** The shop service is healthy right now. Every one of the
nine real-user requests in the observable window returned 2xx (E4), the exception counter
was empty before the investigation touched anything (E2), chaos is off (E2, E15), and the
process has run since 11:30:03Z with monotonic uptime and byte-flat memory (E12).

Two things belong on the handover note anyway.

**First, an armed latent defect.** `GET /products/{id}` divides by `units_in_stock` with no
zero guard at `shop.py:64` (E6), so the detail page returns HTTP 500 for any zero-stock
product. Product 3, "Unobtainium Ingot", is currently the only zero-stock row (E8), and it
fails deterministically — 3 attempts, 3 failures (E5, E7). No customer has hit it: all three
500s carry `konan-*` investigator ids, and no user request in the whole log names
`/products/3` (E4, E7). **The investigation created every 500 the metrics now show.** This is
not today's outage; it is tomorrow's. It fires the moment a customer opens that product, or
any stocked product sells out.

**Second, honest scope.** The service has been idle of real users since 11:30:12Z (E15), and
the log only goes back to process start at 11:30:03Z with no rotated backups. So "nothing is
wrong" means "nothing is wrong with the service's capability, as measured by synthetic probes
over six minutes." It is not evidence that the overnight shift was clean.

Confidence: high on the no-incident verdict and on the defect mechanism (deterministic,
reproduced, stack-traced to the exact line). Low on anything before 11:30:03Z, where there is
no evidence at all.

## Timeline

- **11:30:03.109Z** — process start; the only lifecycle marker in the window (E3).
- **11:30:03.817Z–11:30:12.395Z** — the entire real-user traffic of this window: 9 requests, all
  2xx, touching `/products`, `/products/1`, `/products/2`, `/products/5`, `GET /orders`, and two
  `POST /orders` (E4). No user request touched `/products/3`.
- **11:30:41Z** — baseline scrape. `http_exceptions_total` empty; `faultline_chaos_enabled 0` (E2).
  Investigation begins.
- **11:32:01.507Z** — first ZeroDivisionError, from investigator probe `konan-1787139121-55631` (E6).
  Two more follow at 11:32:10.006Z and 11:32:12.357Z, both konan-stamped (E7).
- **11:35:48Z** — post-triage scrape: chaos still 0, `POST /orders` still 2, uptime 345.43s, no
  reset (E15, E12).

No configuration, deploy, or flag-change marker appears anywhere in the window — the only
`event` markers are the single `startup` (E3) and the three `unhandled_exception` lines the
investigation itself caused.

## Investigation

Baseline via `/health`, `/metrics`, and the log tail established a clean, very short window
(~40s at first read). Because the complaint is deliberately vague — a handover check with no
reported symptom — no lens could be excluded on evidence, so all three ran in parallel and blind
to each other: software-defect, interfaces, infra-process.

All three independently reached "no active incident", and all three independently found the same
zero-stock 500 and independently labelled it latent on request-id attribution. That convergence
is worth something, but it is also three lenses agreeing about one small service, not three
independent proofs.

**No deep-dive round was spawned.** The skill reserves deep-dives for filling evidence gaps, and
the surviving findings were already deterministic and complete: a 3-of-3 reproduction with a stack
trace naming the throwing line. The one genuine gap (H6, the null-price order path) is untestable
from the read-only surface, so no deep-dive could have closed it. Budget went to the judge instead.

The judge refuted usefully. It accepted H1, H3, H4 as invalidated and H2 as validated, but caught
that **H5 was half-uncited** — I had claimed contract drift on `/orders/{order_id}` while citing
OpenAPI evidence for `/products/{product_id}` only. It also flagged two miscited columns: E4 was
filed as evidence *against* H2 when it actually supports the latent classification, and E9 was
filed against H6 where it bears on neither side. Both are corrected in the machine core above.
Its H4 caveat was fair too — the chaos gauge had only been read 80 seconds *before* the first 500.

One targeted round closed the two cheap items: a fresh `/metrics` confirmed `faultline_chaos_enabled 0`
after the failures (E15), and `/openapi.json` confirmed `/orders/{order_id}` also declares only
200 and 422 (E14). H5 is validated on both routes. H6 stays inconclusive and is recorded as a gap.

## Hypotheses

### H1 — active user-facing fault — **invalidated**
No supporting evidence exists. Against: every non-investigator request in the complete log is 2xx
(E4); the exception counter was empty before any probe (E2); the log covers the full life of the
process, so nothing is hidden by rotation (E3, E12); no new user traffic has arrived to contradict
this (E15). The claim is bounded to this process's life — see Gaps.

### H2 — zero-stock ZeroDivisionError — **validated (latent)**
Mechanism is named, not inferred: E6 gives the frame `shop.py:64`,
`units_ordered / product["units_in_stock"]`, unguarded. E8 gives product 3 `units_in_stock: 0`.
E5 gives the matching 500 on that exact route. E9 is the negative control — stocked products return
200 with a finite `turnover_score`, so this is one input failing, not the route failing. Latency is
established by E2 (counter empty before probes) plus E7 (all three 500s konan-stamped) plus E4
(complete user set, no `/products/3`). E4 is cited **for** this hypothesis: it is what proves the
defect is latent rather than active.

### H3 — infra/process fault — **invalidated**
E12 kills each arm: monotonic uptime across six samples and a single server-start line rule out
restart and crash loop; identical RSS rules out growth. E1 shows `/health` at 200 in 2.7ms. Judge's
caveat accepted and recorded in Gaps: `process_max_rss_bytes` is a *max* gauge, so flatness is weaker
proof than it appears, and latency was never tested under real load.

### H4 — injected chaos — **invalidated**
`faultline_chaos_enabled 0` both before (E2) and after (E15) the failures, and no `chaos_enabled`,
`chaos_disabled`, or `chaos_failure` event exists in the log. Independently, the failure signature is
wrong for chaos: deterministic on one input, same exception every time, rather than probabilistic
across routes (E6, E8).

### H5 — OpenAPI contract drift — **validated**
Both `/products/{product_id}` (E10) and `/orders/{order_id}` (E14) declare exactly `200` and `422`.
Both serve 404 in practice, and the products route serves 500 (E13, E5). Two incompatible error
envelopes ship from the same service: `{"detail": ...}` on 404 versus
`{"error","exception_type","request_id"}` on 500. The 500 body also returns the internal Python class
name `ZeroDivisionError` to the caller (E5).

### H6 — null price breaks the order path — **inconclusive**
E11 establishes only the input condition: product 4 carries `price: null`. Nothing exercises the order
path against it. The two `POST /orders -> 201` lines in E4 do not name a product id, so they neither
confirm nor refute. This is an untested inference from a schema oddity, and it is untestable from the
investigator surface — `POST /orders` is not on the probe allowlist. One `POST /orders` for product 4,
eval-side, would settle it.

## Safe next steps

Read-only, for whoever picks up the shift:

1. **Treat the zero-stock 500 as the live risk.** It needs no incident to become one — it needs a
   customer. Worth a tracked defect against faultline regardless of this journal's verdict.
2. **Watch `http_exceptions_total{type="ZeroDivisionError"}` for a non-`konan` request id.** The counter
   sits at 3, all investigator-caused (E7). The first unstamped 500 on `/products/{product_id}` is the
   transition from latent to active, and it is the single cheapest alarm to define.
3. **Re-check with real traffic present.** This verdict was reached against an idle shop (E15). A recheck
   during genuine user load would test what these probes could not.
4. **Settle H6 eval-side.** One `POST /orders` against product 4 resolves the null-price question; it is
   outside the investigator boundary by design.
5. **Note the log horizon before the next handover.** With no rotated backups, each restart erases the
   prior window. If overnight continuity matters, log retention is the thing to change, not the query.

## Gaps

- **No history before 11:30:03.109Z.** One process incarnation, `app.log` with no `.1`–`.3` backups.
  Whether the shop bounced or misbehaved overnight is unanswerable from this surface — not "clean",
  but unknown.
- **No real user traffic during the investigation.** All observed requests since 11:30:12.395Z are
  investigator-stamped (E4, E15). The verdict describes capability under synthetic probes, not a served
  user population.
- **H6 untestable read-only.** `POST /orders` is off the probe allowlist by design (docs/lab.md), so the
  null-price order path could not be exercised.
- **No tail-latency claim possible.** `/metrics` exposes a duration sum/count summary, not a histogram or
  quantiles, and all samples are single probes against an idle service.
- **H2 generalizes from one instance.** Product 3 is the only zero-stock row; the universal form rests on
  the unguarded line in E6 rather than on a second observed zero-stock product.
- **Three denied Bash calls**, one in this session and two in the infra-process lens. None was worked
  around, per the boundary rule that a denial is a signal to stop. No evidence was lost: the lens re-ran
  its probe as single calls, and its `ps` check was redundant against the uptime gauge (E12).
</content>
