---
konan_journal: 1
investigation:
  id: 2026-08-19-order-500s-null-price
  trigger: manual
  complaint: "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  started: 2026-08-19T07:03:58Z
  concluded: 2026-08-19T07:12:29Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "create_order multiplies the resolved product price by the ordered quantity with no null guard, so an order for a product whose price is null raises an unhandled TypeError and returns 500."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "POST /orders raises an unhandled TypeError and returns 500 when the resolved product price is null, because create_order at src/faultline/shop.py:82 computes round(product[\"price\"] * order.quantity, 2) with no null guard; the catalog currently contains exactly one null-priced row (id 4, Mystery Box), which is the probable input. Orders for priced products succeed in the same window."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E9, E11]
    evidence_against: [E17]
  - id: H2
    statement: "The order 500s are caused by a process crash, restart, or resource saturation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E14, E5]
  - id: H3
    statement: "The order 500s are caused by injected chaos, a configuration change, or a partial rollout/deploy."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E16, E13, E5]
  - id: H4
    statement: "The None price comes from a lookup inside create_order that fabricates a default record for an unknown product id (missing 404 handling), rather than from a null-priced catalog row."
    incident_class: software-defect
    state: inconclusive
    evidence_for: []
    evidence_against: [E10, E11]
  - id: H5
    statement: "The root cause is an upstream catalog data change — a product published with a null price — rather than a defect in the order path."
    incident_class: data-db
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E17]
  - id: H6
    statement: "GET /products/3 returns 500 with a ZeroDivisionError — a second defect, distinct from the order failures and not part of the reported incident."
    incident_class: software-defect
    state: validated
    evidence_for: [E12, E15]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 (Unobtainium Ingot, the only catalog row with units_in_stock 0) returns HTTP 500 with a ZeroDivisionError. No end-user request for /products/3 appears in the observable window — the only one on record is the investigator's own probe — so this is a latent defect, not the reported incident. It is reachable by real users: product 3 is a live catalog row."
    evidence: [E12, E15, E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:03:50.166Z"
    quote: "{\"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"394450bbf583\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:03:50.166Z (stack field of E1, final frames)"
    quote: "File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 82, in create_order\n    total_price = round(product[\"price\"] * order.quantity, 2)\n                        ~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~\nTypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:03:50.177Z"
    quote: "{\"message\": \"POST /orders -> 500\", \"request_id\": \"394450bbf583\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 500, \"duration_ms\": 11.703, \"client\": \"127.0.0.1:57741\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:03:51.236Z and 2026-08-19T07:03:54.361Z"
    quote: "{\"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"a0834cf2806f\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\"} … {\"message\": \"unhandled exception: unsupported operand type(s) for *: 'NoneType' and 'int'\", \"request_id\": \"73559fcbbb6a\", \"event\": \"unhandled_exception\", \"exception_type\": \"TypeError\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:03:53.300Z"
    quote: "{\"logger\": \"faultline.shop\", \"message\": \"order created\", \"request_id\": \"663141d2bb4d\", \"event\": \"order_created\", \"order_id\": 3, \"product_id\": 1, \"quantity\": 1, \"total_price\": 49.5}"
  - id: E6
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787123059-49341"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 3\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"500\"} 3"
  - id: E7
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787123059-49341"
    quote: "http_exceptions_total{type=\"TypeError\"} 3"
  - id: E8
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787123059-49341"
    quote: "faultline_chaos_enabled 0"
  - id: E9
    type: probe
    source: "GET /products, request_id konan-1787123073-49360, HTTP 200"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":117},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E10
    type: probe
    source: "GET /products/999, request_id konan-1787123323-49545, HTTP 404"
    quote: "{\"detail\":\"no such product: 999\"}\n-- HTTP 404 in 0.001291s request_id=konan-1787123323-49545"
  - id: E11
    type: probe
    source: "GET /products/4, request_id konan-1787123327-49551, HTTP 200"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0}"
  - id: E12
    type: probe
    source: "GET /products/3, request_id konan-1787123327-49557, HTTP 500"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787123327-49557\"}\n-- HTTP 500 in 0.005174s request_id=konan-1787123327-49557"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:03:43.178Z — the only lifecycle marker in the file"
    quote: "{\"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E14
    type: metric
    source: "/metrics via scripts/probe.sh, request_id konan-1787123059-49341"
    quote: "process_uptime_seconds 36.28025491605513\nprocess_max_rss_bytes 47857664\nhttp_request_duration_seconds_sum{method=\"POST\",path=\"/orders\"} 0.026542335283011198\nhttp_request_duration_seconds_count{method=\"POST\",path=\"/orders\"} 6"
  - id: E15
    type: log
    source: "lab/logs/app.log — full-file scan for path \"/products/3\"; single match"
    quote: "\"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 4.365, \"client\": \"127.0.0.1:57805\""
  - id: E16
    type: log
    source: "lab/logs/app.log — full-file scan for chaos_enabled / chaos_disabled / chaos_failure / simulated_exception events, and for 502/503/504 statuses"
    quote: "(no matching lines)"
  - id: E17
    type: log
    source: "lab/logs/app.log — full-file scan for product_id on the failing request_ids 394450bbf583, a0834cf2806f, 73559fcbbb6a"
    quote: "(no matching lines; product_id appears only on event=order_created lines of the success path)"
gaps:
  - "The failure could not be reproduced: scripts/probe.sh is GET-only and POST /orders is outside the investigator's surface, so 'keeps failing when they retry' is inferred from the shape of the code path (pure arithmetic, no randomness) plus the absence of chaos and resource pressure — never demonstrated on a repeated input."
  - "The failure path logs no product_id (E17), so attributing the three 500s to catalog row 4 is inference by elimination, not a logged fact. Two failing requests shown to carry the same product id would settle both this and the determinism question."
  - "H4 could not be killed: deciding whether create_order's lookup can fabricate a default null-price record requires reading src/faultline/shop.py above line 82, which is in the faultline checkout — outside the surface contract and deliberately blinded. E10 tests the read path only; that create_order shares that lookup is assumed, not shown."
  - "No provenance telemetry exists for the null price: the target emits no catalog-change, deploy, config, or data-load marker, so it is impossible to date the null or to say whether the price was ever non-null."
  - "The observable window is a single process life from 2026-08-19T07:03:43.178Z; no rotated logs (app.log.1-.3) exist, so nothing before that start is visible and no last-known-good for product 4 could be established."
  - "Two subagents had scripts/probe.sh denied by the permission system and worked from logs alone; one orchestrator command was also denied. Per the boundary rule none was retried in another form, so part of the probe coverage was obtained later and serially by the orchestrator rather than by the lens that requested it."
  - "Investigator probes are telemetry-visible and this investigation perturbed the target's counters: the /products/3 probe (E12) added one 500 and one ZeroDivisionError to faultline's metrics. Investigator GETs begin at 07:04:15.125Z, and any counter read after 07:08:47Z includes an investigator-induced 500."
usage:
  model: claude-opus-5
  tokens: 2534141
  wall_clock_seconds: 511
---

# Order failures: unguarded null product price returns 500 on POST /orders

## Summary

**Root cause identified.** `POST /orders` fails with HTTP 500 because `create_order`
(`src/faultline/shop.py:82`) computes `round(product["price"] * order.quantity, 2)` with no
null guard. When the resolved product price is `None`, the multiplication raises an
unhandled `TypeError` that escapes as a bare 500 (E1, E2, E3). The catalog contains exactly
one null-priced row — id 4, "Mystery Box", `price: null`, `units_in_stock: 75` (E9, E11) —
and it is the probable input, though the failure path logs no `product_id`, so that specific
attribution is inference rather than a logged fact (E17).

This is a **data-dependent defect, not an outage**: the failure follows the input, not the
clock. In the same 7-second window, three orders succeeded (products 1, 2, 1) and three
failed, with a success timestamped *between* two failures (E5). That shape explains the
complaint exactly — the customers who fail are the ones ordering the un-priced item, they
fail on every retry because nothing about the arithmetic is probabilistic, and everyone
else is unaffected. **Impact: 3 of 6 end-user order attempts failed (50%)** in the window
07:03:50.177Z–07:03:54.365Z. No order for product 4 ever persisted — the exception aborts
before write, so retries produce a clean repeat failure with no duplicate or partial order.

Confidence is **high on the mechanism** and **medium on the row-4 attribution**. Health was
green throughout while half of all orders failed — `/health` reports liveness only and never
exercises the order path.

A **second, unrelated defect** was found and is *not* part of this incident: `GET /products/3`
returns 500 with a `ZeroDivisionError` (E12). Only the investigator's own probe ever requested
that path (E15), so it is recorded as a latent finding, not as user impact.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 07:03:43.178Z | faultline 0.1.0 starts — the only lifecycle marker in the window; no restart follows | E13 |
| 07:03:47.048Z | Order 1 created, product 1, total 99.0 | — |
| 07:03:48.108Z | Order 2 created, product 2, total 23.0 | — |
| 07:03:50.166Z | First unhandled `TypeError` at `shop.py:82`, request `394450bbf583` | E1, E2 |
| 07:03:50.177Z | First user-visible `POST /orders -> 500` | E3 |
| 07:03:51.236Z | Second identical `TypeError`, request `a0834cf2806f` | E4 |
| 07:03:53.300Z | **Order 3 succeeds (product 1) between two failures** — kills any time-based onset | E5 |
| 07:03:54.361Z | Third identical `TypeError`, request `73559fcbbb6a` | E4 |
| 07:03:55.425Z | Last end-user request in the window | — |
| 07:03:58Z | Investigation starts (complaint raised 07:03:58Z — trigger latency ~0s) | — |
| 07:08:43Z | Investigator probe: `GET /products/999` -> clean 404, killing the unknown-id alternative | E10 |
| 07:08:47Z | Investigator probe: `GET /products/3` -> 500 `ZeroDivisionError` (self-induced, latent) | E12, E15 |

No configuration, deploy, or flag-change marker appears anywhere in the window (E16). There
is no "worked until T, broke after T" boundary — the first failure is only 7 seconds after
process start, and successes continue after it.

## Investigation

Complaint object as delivered by the `/konan` manual adapter:

```json
{
  "source": "human",
  "fingerprint": "human-1787123038",
  "labels": { "alertname": "human-report" },
  "annotations": {
    "summary": "Support: multiple customers report that placing an order fails with 'Internal Server Error', and it keeps failing when they retry. Other customers' orders are going through fine."
  },
  "startsAt": "2026-08-19T07:03:58Z"
}
```

Investigation start: `2026-08-19T07:03:58Z` — trigger latency ≈ 0 s (manual trigger).
No `severity` label: the reporter stated none, and severity is never inferred.

**Baseline.** `/health` 200 with ~32 s uptime; `/metrics` showing `POST /orders` split 3×201
against 3×500 with every GET path at 200; `http_exceptions_total{type="TypeError"} 3`;
`faultline_chaos_enabled 0`. The business surface was checked explicitly rather than trusting
health — the healthy-monitoring trap is precisely the shape here.

**Triage — 3 lenses in parallel, each blind to the others.** `software-defect` returned the
mechanism and the data-dependence. `infra-process` returned a clean domain verdict (no
lifecycle event, no saturation) and independently flagged `/health` as a blind spot.
`interfaces` ruled out the change/rollout branch and raised the contract violation: the
catalog serves a null `price` with 200 while the order path treats it as numeric.

**Deep-dives — 2 in parallel, tasked to confirm *and* refute.** Both were partly blocked:
`scripts/probe.sh` was denied to the subagents by the permission system. Per the lab boundary
rule a denial is a signal to stop, never a puzzle to solve, so neither retried it in another
form; both worked from logs and reported the denial. Their most valuable output was negative:
the row-4 attribution is an inference, because no failure-path line records a `product_id`.
The orchestrator then ran the decisive probes directly, including the one test that could have
killed H1 — `GET /products/999`, which returned a clean 404 (E10) rather than a fabricated
null-price record. That probe sweep also turned up the unrelated `/products/3` 500.

**Judge.** A fresh judge saw only the hypothesis list and the verbatim evidence ledger — no
narrative. It validated H1's mechanism but demoted the row-4 clause to "probable input",
refused to invalidate H4 (E10 tests the *read* path; that `create_order` shares that lookup is
assumed), and rejected two mislabeled citations: E17 had been listed as evidence *for* H1 when
it is an absence record that weakens it, and E8 — a gauge sampled during the investigation —
cannot describe flag state at the time of the failures, so E16 carries H3 instead. All three
corrections are applied above.

**Concluded after one round.** Every test the judge named as decisive is out of reach: the
failing `product_id` is not logged by the target, `POST` is outside a GET-only surface, and
`create_order`'s source sits in the blinded faultline checkout. A second round would have
spent budget without moving the evidence.

## Hypotheses

### H1 — Unguarded null price in `create_order` — **validated**

`POST /orders` returns 500 when the resolved product price is null, because `shop.py:82`
multiplies it by quantity with no guard. For: three identical unhandled `TypeError`s, each
tied to a `POST /orders -> 500` on the same request id (E1, E2, E3, E4); metric counts that
agree exactly, 3 500s and 3 `TypeError`s (E6, E7); interleaved successes for priced products
(E5, E9, E11). Against: E17 — the failure path records no `product_id`, so "row 4" is
elimination, not observation. The mechanism stands independently of which row it was.

### H2 — Crash, restart, or saturation — **invalidated**

One startup marker only (E13); uptime rising with no reset, RSS flat at +16 KB, mean order
latency 4.4 ms over 6 requests (E14); the process survives every 500 and serves a successful
order 1.06 s after the first failure (E5). Nothing resembles a crash or resource pressure.

### H3 — Injected chaos, config change, or rollout — **invalidated**

No `chaos_*` or `simulated_exception` event and no 502/503/504 anywhere in the file (E16); no
redeploy in the window (E13); no onset boundary, since successes continue after the first
failure (E5). Note the judge's correction: `faultline_chaos_enabled 0` (E8) was read *during*
the investigation and cannot speak to flag state at 07:03:50Z — E16 is what carries this.

### H4 — Fabricated default record for an unknown product id — **inconclusive**

`GET /products/999` returns a clean 404 (E10), and a genuine null-priced row exists, so no
fabrication is needed to explain the `None` (E11). But E10 exercises the read path; that
`create_order` uses the same lookup is an assumption. Strongly disfavored by parsimony, not
killed. Settling it needs the lookup statement above `shop.py:82` — blinded, outside the
surface.

### H5 — Upstream catalog data change rather than a code defect — **invalidated**

Invalidated as stated, because it is a false dichotomy: whatever the data, `shop.py:82`
dereferences `price` without a guard and lets the `TypeError` escape as a bare 500 (E2). The
null value is the *trigger*; the missing guard is the *defect*. The separate provenance
question — whether the price was ever non-null — is unfalsifiable from this surface: E9 and
E11 show the data as it is now, never that it changed, and no rotated logs exist (E17).

### H6 — `ZeroDivisionError` on `GET /products/3` — **validated, latent**

A direct observation (E12), on a different path with a different exception type from the
reported incident. The only `/products/3` request in the entire file is the investigator's own
probe (E15), so it must not be counted as user impact. Per the judge, the defensible wording is
"no end-user request appears in the observable window" — *not* "unreachable by users": product 3
is a live catalog row (E9), and it is the only row with `units_in_stock: 0` while single-product
responses carry a `turnover_score` field (E11). That suggests a divide-by-stock mechanism, but no
stack frame was captured for it, so the mechanism is unconfirmed.

## Safe next steps

Read-only observations only; remediation is out of scope for this journal.

1. Watch `http_requests_total{method="POST",path="/orders",status="500"}` against
   `http_exceptions_total{type="TypeError"}` — they should continue to move 1:1 while the
   null-priced row remains orderable.
2. Re-read `GET /products` periodically to confirm row 4 stays the only null-priced row; a
   second such row widens the blast radius immediately.
3. Watch for the first end-user (12-hex id) request to `/products/3`; that would convert the
   latent H6 finding into live user impact.
4. Two telemetry gaps are worth raising with the target's owners, because they are what
   blocked this investigation from certainty: the failed-order log line carries no
   `product_id` or request body, and the service emits no catalog-change or data-load marker.
5. Treat `/health` as liveness-only for alerting purposes — it returned 200 throughout a 50%
   order failure rate.

## Gaps

- **No reproduction.** The probe surface is GET-only and `POST /orders` is outside it, so the
  complaint's "keeps failing when they retry" is inferred from the code path's shape, not
  demonstrated on a repeated input.
- **No `product_id` on the failure path**, so row 4 is inference by elimination (E17). Two
  failing requests carrying the same product id would settle attribution and determinism at once.
- **H4 not killed.** Deciding it requires reading `shop.py` above line 82 — in the faultline
  checkout, outside the surface contract and deliberately blinded.
- **No provenance telemetry** for the null price: no catalog-change, deploy, or data-load
  marker exists, so the null cannot be dated and H5's change claim cannot be tested.
- **One process life only.** The window starts at 07:03:43.178Z with no rotated logs, so no
  last-known-good for product 4 exists.
- **Probe denials.** Subagents were denied `scripts/probe.sh` and, per the boundary rule, did
  not retry in another form; the orchestrator ran those probes serially afterwards. Coverage was
  reached, but later and less independently than designed.
- **Investigator traffic perturbed the target.** The `/products/3` probe added a 500 and a
  `ZeroDivisionError` to faultline's counters (E12); investigator GETs begin at 07:04:15.125Z,
  and counter reads after 07:08:47Z include an investigator-induced 500.
