---
konan_journal: 1
investigation:
  id: 2026-08-19-products-3-500s
  trigger: manual
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: "2026-08-19T02:19:39Z"
  concluded: "2026-08-19T02:23:11Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product-detail handler get_product (faultline shop.py:64) computes turnover_score as units_ordered / units_in_stock without guarding a zero denominator; product 3 ('Unobtainium Ingot') is the catalog's only units_in_stock=0 row, so every load of its product page raises an unhandled ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "GET /products/3 deterministically raises an unhandled ZeroDivisionError at shop.py:64 in get_product — turnover_score divides units_ordered by product['units_in_stock'], and product 3 has units_in_stock=0 — so every request for that product's page returns 500; reproducible by any caller since the trigger is which product id is requested, an ordinary customer action, not an investigator-specific condition."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5]
    evidence_against: []
  - id: H2
    statement: "The 500s are caused by process instability (crash/restart loop, resource exhaustion) rather than application code."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7]
  - id: H3
    statement: "The 500s come from injected chaos/fault degradation, a failing dependency, or a gateway/proxy layer rather than the application's own handler code."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E9]
latent_findings:
  - statement: "Product 4 ('Mystery Box') serves price: null with HTTP 200 on its detail route — a possible data/contract defect, unrelated to the 500s (which the exception accounting fully explains)."
    evidence: [E10]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:20:52.701Z"
    quote: |-
      {"ts": "2026-08-19T02:20:52.701Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787106052-38960", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "...File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E2
    type: probe
    source: "GET /products/3, request_id konan-1787106052-38960"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787106052-38960"} -- HTTP 500 in 0.008610s request_id=konan-1787106052-38960'
  - id: E3
    type: probe
    source: "GET /products, request_id konan-1787106025-38938"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
  - id: E4
    type: metric
    source: "GET /metrics, request_id konan-1787106100-39002"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1
  - id: E5
    type: probe
    source: "GET /products/1, request_id konan-1787106100-39008 (representative of /products/1, /products/4, /products/5, all units_in_stock>0)"
    quote: '{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:19:23.048Z"
    quote: '{"ts": "2026-08-19T02:19:23.048Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E7
    type: metric
    source: "GET /metrics, request_id konan-1787106100-39002"
    quote: "process_uptime_seconds 137.48617725004442"
  - id: E8
    type: metric
    source: "GET /metrics, request_id konan-1787106025-38932"
    quote: "faultline_chaos_enabled 0"
  - id: E9
    type: probe
    source: "GET /products/3, request_id konan-1787106052-38960"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787106052-38960"}'
  - id: E10
    type: probe
    source: "GET /products/4, request_id konan-1787106052-38966"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}'
gaps:
  - "The service process restarted shortly before this investigation began (process_uptime_seconds ~62s at the first probe), and lab/logs/app.log holds no entries predating that restart (no rotated .1/.2/.3 backups present). No non-investigator (non-'konan-'-prefixed) request in the visible log window targeted /products/3, so the complaint's specific claims of 'this morning' and 'several customers' could not be independently corroborated against historical traffic. The defect's determinism — any caller requesting product id 3 hits the same code path and 500s, with no chaos or special conditions required — is what supports concluding root cause despite this gap, not direct historical log evidence."
usage:
  model: claude-sonnet-5
  tokens: 1943301
  wall_clock_seconds: 212
---

# Product page 500s: unguarded division by zero for out-of-stock catalog item

## Summary

**Root cause identified.** `GET /products/3` ("Unobtainium Ingot") deterministically
returns HTTP 500. The product-detail handler (`shop.py:64`, `get_product`) computes
`turnover_score = units_ordered / units_in_stock` with no guard for a zero
denominator; product 3 is the only catalog row with `units_in_stock: 0`, so any
request for its page raises an unhandled `ZeroDivisionError` (E1) and returns a
generic 500 body (E2). Every other catalog item (`units_in_stock > 0`) serves the
same field successfully (E5). Chaos injection, process instability, and
gateway/dependency failure were each checked and ruled out (E6–E9) — this is a plain
application code defect, not infrastructure or injected fault. Impact: 1 of 5 catalog
products (any customer who opens that specific product's page) sees "Internal Server
Error"; other pages are unaffected, consistent with "some customers" rather than a
site-wide outage. Confidence: high on mechanism; the exact "this morning" / "several
customers" framing in the complaint could not be corroborated against prior traffic
because the process restarted just before this investigation and no log history
survives that restart (see Gaps) — but the defect is data-driven and caller-
independent, so it reproduces for any real customer who lands on that product.

## Timeline

- **02:19:23Z** — service process starts fresh (E6); no prior restart markers in the
  visible log.
- **02:19:23Z–02:19:29Z** — pre-existing seed/simulated traffic (non-investigator
  request ids) exercises `/health`, `/products`, `/products/1`, `/products/2`,
  `/orders`, `/products/5` — all 200/201, none targeting product 3.
- **02:20:22Z–02:20:25Z** — investigator baseline probes: `/health`, `/metrics`,
  `/products` — all clean, chaos disabled (E8).
- **02:20:52.701Z** — investigator probe `GET /products/3` triggers the unhandled
  `ZeroDivisionError` (E1); response logged as `GET /products/3 -> 500` immediately
  after.
- **02:20:52.759Z** — investigator probe `GET /products/4` (also `units_in_stock`
  non-zero-adjacent case, `price: null`) returns 200, isolating the failure to
  product 3 specifically (E10, latent finding).
- **02:21:40Z** — metrics scrape confirms exactly one `ZeroDivisionError` and one
  500, both attributable to the single `/products/3` probe (E4).

## Investigation

1. **Baseline** — `/health`, `/metrics`, `/products` all clean: chaos off, uptime
   normal, no prior exceptions.
2. Rather than fan out generic discipline lenses against a still-vague complaint, the
   product catalog itself supplied the next cheap, targeted test: the two untested
   product ids (3, 4) from the `/products` listing, one of which (`id=3`) had a
   suspicious `units_in_stock: 0`. Probing it reproduced the reported symptom
   immediately and completely (E1, E2) — a hypothesis whose evidence arrived
   deterministic and complete, per the skill's guidance to skip deep-dive
   re-proving in that case.
3. Widened the check: all other catalog items (E5), a second `/metrics` scrape
   (E4, E7, E8), and the startup log (E6) — to actively rule out the standing
   alternative explanations (process instability, chaos/gateway) before concluding.
4. **Judge, round 1** — an initial hypothesis statement conflated "the defect is
   real and deterministic" with "this is definitely what the complaint's historical
   timing refers to." The judge correctly returned inconclusive on that conflated
   claim, and named the missing evidence: a pre-investigation, non-investigator log
   entry hitting `/products/3`. Confirmed that evidence is structurally unavailable
   (fresh restart, no rotated log backups) — not just unfound.
5. **Judge, round 2** — hypothesis restated to test the mechanism claim alone
   (deterministic, caller-independent defect), plus two alternative hypotheses
   (H2 infra-process, H3 interfaces/chaos) built from evidence already in hand.
   All three verdicts returned clean: H1 validated, H2 and H3 invalidated.

## Hypotheses

### H1 — Unguarded zero-denominator division in get_product (validated)

`shop.py:64` divides `units_ordered` by `units_in_stock` when building
`turnover_score`. Product 3 has `units_in_stock: 0` (E3); requesting its page
raises `ZeroDivisionError` (E1) and returns 500 (E2, E9). Every other product,
all with nonzero stock, serves the same computed field without error (E5).
Metrics show exactly one exception and one 5xx in the observed window, both
attributable to this single trigger (E4). Judge verdict: validated — the
evidence supports the mechanism cleanly, and the trigger condition (which
product id a caller requests) is ordinary customer navigation, not something
only an investigator's probe shape could hit.

### H2 — Process instability (invalidated)

One continuous startup sequence, no repeated `startup` events, uptime climbing
monotonically across scrapes, unremarkable RSS (E6, E7). No basis for a
crash/restart-loop or resource-exhaustion explanation.

### H3 — Injected chaos / dependency / gateway failure (invalidated)

`faultline_chaos_enabled` is 0 throughout (E8); the lab topology has no
gateway in front of the service; the 500 body itself names an application-level
Python exception (`ZeroDivisionError`), not a timeout or upstream-5xx shape (E9).

## Safe next steps

- Read the current catalog (`GET /products`) periodically to watch for any other
  item whose `units_in_stock` reaches 0 — each such item will 500 on its detail
  page under the current code, by the same mechanism.
- Compare `http_exceptions_total{type="ZeroDivisionError"}` against
  `http_requests_total{path="/products/{product_id}",status="500"}` over time to
  confirm both stay yoked (would indicate this is still the only 5xx source on
  that route) or diverge (would indicate a second cause has appeared).
- If corroborating "since this morning" matters operationally, check whether any
  log aggregation or metrics retention outside this lab's `lab/logs/` window
  captured pre-restart traffic — this investigation's surface contract
  (`docs/lab.md`) does not expose one.

## Gaps

- The service process restarted shortly before this investigation began
  (`process_uptime_seconds` ~62s at the first probe), and `lab/logs/app.log` holds
  no entries predating that restart — no rotated `.1`/`.2`/`.3` backups exist. No
  non-investigator request in the visible window targeted `/products/3`, so the
  complaint's specific "this morning" / "several customers" framing could not be
  independently corroborated against historical traffic. Root cause is still
  concluded because the defect is data-driven and caller-independent (any request
  for that product id 500s, with no chaos or special condition required) — but this
  is an explicit evidentiary limit, not a claim that pre-restart traffic was
  observed.
