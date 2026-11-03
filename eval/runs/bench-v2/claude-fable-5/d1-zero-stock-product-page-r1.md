---
konan_journal: 2
investigation:
  id: 2026-11-02-products-3-zero-stock-500s
  trigger: "manual (/konan human-report; fingerprint human-1793627233; startsAt 2026-11-02T13:47:13Z; investigation start 2026-11-02T13:47:26Z; trigger latency 13s)"
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-02T13:47:26Z
  concluded: 2026-11-02T13:54:02Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{id} computes a turnover_score by dividing units_ordered by the product's units_in_stock; product 3 holds units_in_stock = 0, so every request to /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "Data-dependent code defect: the /products/{id} handler divides by the product's units_in_stock; product 3 has stock 0, so every GET /products/3 fails with an unhandled ZeroDivisionError (HTTP 500) while products with stock > 0 succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14]
    evidence_against: []
  - id: H2
    statement: "An injected degradation (chaos toggle) produces the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E9]
  - id: H3
    statement: "A process lifecycle or resource failure (crash loop, memory exhaustion, saturation) produces the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E16, E17, E7]
  - id: H4
    statement: "A deploy or configuration change at the 2026-11-02T13:46:51Z process start introduced the failing behavior."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:46:51.041Z"
    quote: '{"ts": "2026-11-02T13:46:51.041Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:46:58.238Z"
    quote: '{"ts": "2026-11-02T13:46:58.238Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "b601b345d8d2", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "[trimmed] File \"[…]/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n[trimmed]\nZeroDivisionError: division by zero"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:46:58.248Z"
    quote: '{"ts": "2026-11-02T13:46:58.248Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "b601b345d8d2", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.299, "client": "127.0.0.1:58292"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:46:59.312Z"
    quote: '{"ts": "2026-11-02T13:46:59.312Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "271e4694c4bc", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 6.842, "client": "127.0.0.1:58293"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:47:02.423Z"
    quote: '{"ts": "2026-11-02T13:47:02.423Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "338458e07409", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 3.41, "client": "127.0.0.1:58296"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:47:04.539Z"
    quote: '{"ts": "2026-11-02T13:47:04.539Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "020a840b453d", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.495, "client": "127.0.0.1:58300"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:47:01.370Z"
    quote: '{"ts": "2026-11-02T13:47:01.370Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "18bc10b48466", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1.204, "client": "127.0.0.1:58295"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:46:53.063Z"
    quote: '{"ts": "2026-11-02T13:46:53.063Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "1d19a668b660", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.234, "client": "127.0.0.1:58289"}'
  - id: E9
    type: probe
    source: "GET /products/3 @ request_id konan-1793627355-91561 (~2026-11-02T13:49:15Z) — HTTP 500"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793627355-91561"}'
  - id: E10
    type: probe
    source: "GET /products @ request_id konan-1793627349-91521 — HTTP 200, product-3 record of the payload"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
  - id: E11
    type: metric
    source: "/metrics @ request_id konan-1793627274-91465 (2026-11-02T13:47:54Z)"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4'
  - id: E12
    type: metric
    source: "/metrics @ request_id konan-1793627274-91465 (2026-11-02T13:47:54Z)"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 4'
  - id: E13
    type: metric
    source: "/metrics, lens scrape after the single konan reproduction probe E9 (~2026-11-02T13:49Z)"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 5'
  - id: E14
    type: metric
    source: "/metrics, lens scrape after the single konan reproduction probe E9 (~2026-11-02T13:49Z)"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 5'
  - id: E15
    type: metric
    source: "/metrics @ request_id konan-1793627274-91465 (2026-11-02T13:47:54Z); same value at the 13:49:13Z lens scrape"
    quote: 'faultline_chaos_enabled 0'
  - id: E16
    type: metric
    source: "/metrics @ request_id konan-1793627274-91465 (2026-11-02T13:47:54Z); 142.07 at the 13:49:13Z lens scrape — continuous, no reset"
    quote: 'process_uptime_seconds 63.77415666705929'
  - id: E17
    type: metric
    source: "/metrics @ request_id konan-1793627274-91465 (2026-11-02T13:47:54Z); unchanged at the 13:49:13Z lens scrape"
    quote: 'process_max_rss_bytes 48971776'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:46:56.179Z"
    quote: '{"ts": "2026-11-02T13:46:56.179Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "645842e2a4b1", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-02T13:47:03.482Z"
    quote: '{"ts": "2026-11-02T13:47:03.482Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "b523174480e9", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}'
gaps:
  - "No telemetry exists before the 13:46:51Z process start: lab/logs/app.log holds one startup marker and no rotated backups (app.log.1–.3 absent). The complaint's 'started within the last hour' cannot be bounded, and no before/after comparison across the start is possible."
  - "No faultline_chaos_enabled sample exists inside the first failure window (13:46:58–13:47:04Z); the first scrape is 13:47:54Z. The invalidation of H2 rests on the two later scrapes plus the reproduction under a 0 gauge."
  - "/products/4 and /products/5 were never fetched by id; the claim that products with stock > 0 succeed rests on products 1 and 2 (3 requests, 3 × 200)."
  - "The trigger of the 13:46:51Z process start (deploy, manual restart, crash of a predecessor) is not observable from the surface contract; H4 stays inconclusive."
usage:
  model: claude-fable-5
  tokens: 1567282
  wall_clock_seconds: 396
---

# Product 3 detail page returns 500 on every request: division by zero on zero stock

## Summary

Root cause identified. The product-detail endpoint `GET /products/{id}` computes a
`turnover_score` by dividing `units_ordered` by the product's `units_in_stock`
(stack frame at faultline `src/faultline/shop.py:64`, E2). Product 3
("Unobtainium Ingot") holds `units_in_stock: 0` (E10), so every request to
`/products/3` raises an unhandled `ZeroDivisionError` and returns HTTP 500 — 5 of 5
requests in the observed window, four from user traffic (E3–E6) and one stamped konan
reproduction (E9). All other observed traffic succeeds: `/products/1` and `/products/2`
return 200, including between failures (E7, E8), `/products` lists fine (E10), and
orders post 201 (E18, E19). Impact is confined to the one product page whose stock is
zero; the failure is deterministic per input, which matches the complaint ("still
happening when they refresh", "other pages load fine"). Confidence is high: the
mechanism, the data condition, the reproduction, and lockstep counters (E11–E14) all
agree, and the adversarial judge validated H1 while invalidating the chaos and
process-lifecycle alternatives.

## Timeline

- 13:46:51Z — process start, faultline 0.1.0 (E1). The only startup marker in the
  available history; no earlier telemetry exists.
- 13:46:53–13:46:56Z — healthy user traffic: `/products/1` 200 (E8), `/products/2` 200,
  order 1 created for product 1 (E18).
- 13:46:58.238Z — first failure: unhandled `ZeroDivisionError` in `get_product` (E2);
  access line `/products/3 -> 500` (E3). This is the first-ever `/products/3` request
  of this process lifetime.
- 13:46:59–13:47:04Z — three more user-traffic failures on `/products/3` (E4, E5, E6),
  with a `/products/2` 200 interleaved at 13:47:01Z (E7) and order 2 created at
  13:47:03Z (E19).
- 13:47:13Z — support complaint raised (trigger `startsAt`).
- 13:47:26Z — investigation start (trigger latency 13 s).
- 13:47:54Z — baseline scrape: 4 × 500 on the detail route, 4 ZeroDivisionErrors,
  chaos gauge 0 (E11, E12, E15).
- ~13:49:15Z — konan reproduction: `/products/3` → 500 with `ZeroDivisionError` body
  (E9); counters move 4 → 5 in lockstep (E13, E14).

## Investigation

Complaint block — the complaint object as received by the `/konan` adapter, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1793627233",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of." },
  "startsAt": "2026-11-02T13:47:13Z"
}
```

Investigation start 2026-11-02T13:47:26Z; trigger latency 13 s.

Rounds as they ran:

1. **Baseline** (13:47:54Z): `/health` 200 with uptime 63.6 s, metrics snapshot
   (E11, E12, E15, E16, E17), log tail of `lab/logs/app.log`. The baseline already
   showed the 500/200 split on the detail route and the `ZeroDivisionError` stacks.
2. **Triage**, three lenses in parallel, each blind to the others: software-defect,
   infra-process, interfaces. Software-defect confirmed determinism by one
   reproduction probe (E9) and found the zero-stock record (E10). Infra-process found
   one startup, monotonic counters, flat RSS, and millisecond latencies — no lifecycle
   or resource anomaly. Interfaces found no dependency, gateway, or configuration
   mechanism, and proved per-input (not per-request) failure via the interleaved 200
   (E7).
3. **Deep-dive**: skipped. H1's triage evidence was deterministic and complete
   (5/5 failures, reproduction, divisor-zero record, lockstep counters), so it went
   straight to the judge per the loop contract.
4. **Judge** (fresh subagent, evidence-only): H1 validated; H2 invalidated; H3
   invalidated; H4 inconclusive. Its settling-evidence items for H2/H4 are recorded
   under Gaps.

Budget use: one triage round of three lenses, zero deep-dive agents, one judge.

## Hypotheses

### H1 — zero-stock division defect (validated)

The handler divides by `units_in_stock` (E2); product 3's stock is 0 (E10); all five
`/products/3` requests fail (E3–E6, E9) while neighbors succeed before, between, and
after the failures (E7, E8). Counters move in lockstep with a single reproduction
(E11→E13, E12→E14), accounting for every request on the route (4 × 500 + 3 × 200 =
count 7). Orders in the window touched only products 1 and 2 (E18, E19), so nothing
changed product 3's stock mid-window. No evidence against.

### H2 — chaos / degradation switch (invalidated)

`faultline_chaos_enabled` reads 0 at both scrapes (E15) and the reproduction (E9)
produced a 500 seconds after a 0-gauge scrape — an active switch cannot explain that.
No `chaos_*` or `simulated_exception` event exists in the full log. Judge's residual
caveat: no gauge sample inside the first failure window (see Gaps).

### H3 — process lifecycle / resource failure (invalidated)

One startup marker (E1), a continuously rising uptime gauge (E16), flat peak RSS
(E17), and millisecond durations on both the 200s and the 500s. The interleaved
`/products/2` 200 (E7) is decisive: a resource failure does not pass one input and
fail another one second apart, repeatedly.

### H4 — deploy or config change at the 13:46:51Z start (inconclusive)

The startup marker (E1) sits inside the complaint window, but a startup is not itself
evidence of a deploy, and no pre-start telemetry exists to compare against. The judge
notes H4 does not compete with H1 on mechanism: the defect is data-dependent and can
predate the restart. What would settle it: any record from before 13:46:51Z — a
request log for `/products/3`, or a deploy/VCS record covering the `turnover_score`
line or the stock value.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

- Hand faultline's owners the failing frame (`src/faultline/shop.py:64`,
  `get_product`, division by `product["units_in_stock"]`) and the zero-stock record
  (E10) as the reproduction recipe.
- Read the inventory data (read-only) for when product 3's stock reached 0 — that
  bounds the real start of user impact, which the logs cannot.
- Scan `/products` for any other record with `units_in_stock: 0`; each such record is
  the same 500 waiting on its detail page.
- Check deploy/runbook records outside the target for the 13:46:51Z process start to
  settle H4.

## Gaps

- **No pre-start telemetry.** The log history begins at the 13:46:51Z startup (E1);
  no rotated backups exist. The complaint's "last hour" window is unverifiable, and
  the route has no observable last-known-good.
- **Chaos gauge unsampled in the first failure window.** First scrape is 13:47:54Z;
  the failures began 13:46:58Z. H2's invalidation rests on the two later scrapes and
  the reproduction under a 0 gauge, not on a sample taken mid-window.
- **Products 4 and 5 never fetched by id.** The "stock > 0 succeeds" half of H1's
  prediction rests on products 1 and 2 only.
- **Cause of the process start unknown.** Whether 13:46:51Z was a deploy, a manual
  restart, or a predecessor's crash is outside the surface contract; H4 stays
  inconclusive.
