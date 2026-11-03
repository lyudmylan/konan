---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-slowness-chaos-toggle
  trigger: manual
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-02T20:54:44Z
  concluded: 2026-11-02T21:07:57Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operator-side chaos toggle enabled at 20:54:22.466Z injected added latency (extra_latency_ms=1500) into business routes while sparing /health, producing the shop-wide slowness."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operator-side chaos toggle (event=chaos_enabled, failure_rate=0.0, error_status=503, extra_latency_ms=1500) was flipped on at 20:54:22.466Z by non-investigator traffic, injecting added latency into business routes (/products, /products/{id}, /orders) while leaving /health and /metrics unaffected — explaining the shop-wide slowness with health checks staying green and fast."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "GET /products/{id} deterministically raises an unhandled ZeroDivisionError (units_ordered divided by units_in_stock=0) for product id 3, independent of chaos mode; however no non-investigator traffic in the retained log window ever reached this route, so the defect has no confirmed link to the complaint's 'saw an error page once' claim — it rides along as a latent finding, not the active incident."
    incident_class: software-defect
    state: validated
    evidence_for: [E10, E11, E12, E13]
    evidence_against: []
latent_findings:
  - statement: "A deterministic, chaos-independent ZeroDivisionError on GET /products/3 (units_in_stock=0) exists in the target's code, but only investigator probes triggered it in the retained telemetry — no confirmed customer impact."
    evidence: [E10, E11, E12, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:54:16.537Z"
    quote: "{\"event\": \"startup\", \"message\": \"faultline 0.1.0 started\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:54:22.466Z"
    quote: "{\"event\": \"chaos_enabled\", \"request_id\": \"05e875bfaa3c\", \"enabled\": true, \"failure_rate\": 0.0, \"error_status\": 503, \"extra_latency_ms\": 1500}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:54:17.291Z (pre-toggle)"
    quote: "{\"event\": \"request\", \"method\": \"GET\", \"path\": \"/health\", \"status\": 200, \"duration_ms\": 0.713}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:54:18.350Z (pre-toggle)"
    quote: "{\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 1.0}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:54:27.812Z (post-toggle)"
    quote: "{\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 759.609}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:54:25.984Z (post-toggle)"
    quote: "{\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/2\", \"status\": 200, \"duration_ms\": 348.115}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:54:29.218Z (post-toggle)"
    quote: "{\"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 341.534}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:55:17.044Z (investigator probe, 55s after E2)"
    quote: "{\"event\": \"request\", \"method\": \"GET\", \"path\": \"/health\", \"status\": 200, \"duration_ms\": 1.356, \"request_id\": \"konan-1793652917-5424\"}"
  - id: E9
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-02T21:01:04Z (request_id konan-1793653664-5838)"
    quote: "faultline_chaos_enabled 1"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T20:59:45.982Z-20:59:45.997Z (investigator probe konan-1793653184-5596)"
    quote: "{\"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\"} ... File \"src/faultline/shop.py\", line 64, in get_product: \"turnover_score\": units_ordered / product[\"units_in_stock\"] -> ZeroDivisionError: division by zero ... {\"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 1187.484}"
  - id: E11
    type: probe
    source: "scripts/probe.sh /products @ 2026-11-02T21:08:37Z (request_id konan-1793653717-5854)"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":119},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E12
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-11-02T21:01:04Z (request_id konan-1793653664-5838)"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 2 ; http_exceptions_total{type=\"ZeroDivisionError\"} 2"
  - id: E13
    type: log
    source: "lab/logs/app.log lines 8,9,14,15,16 — every non-konan-prefixed (non-investigator) request line touching /products*"
    quote: "GET /products -> 200 @20:54:17.293Z; GET /products/1 -> 200 @20:54:18.350Z; GET /products -> 200 @20:54:24.577Z; GET /products/2 -> 200 @20:54:25.984Z; GET /products/1 -> 200 @20:54:27.812Z — never /products/3, /products/4, /products/5, or any /orders/{id}"
gaps:
  - "No rotated log backups (app.log.1-.3) exist for this run, so any traffic before process startup at 20:54:16.537Z is unrecoverable — if a real customer hit /products/3 before this window, it would not be visible here."
  - "This surface has no request-volume/concurrency gauge (docs/lab.md's metrics list), so H1's 'not customer load' rests on the chaos toggle being a sufficient alternative explanation, not on a positive measurement that traffic volume was normal."
  - "The lab is a single service with no gateway/proxy tier (docs/lab.md 'Known gaps'), so a client-side-timeout explanation for the single 'error page' report — plausible given the elevated post-toggle latencies even without a server-side 5xx — could not be tested on this surface."
usage:
  model: claude-sonnet-5
  tokens: 3727880
  wall_clock_seconds: 793
---

# Shop-wide slowness traced to an operator chaos toggle; an unrelated latent 500 found on product id 3

## Summary

**Root cause identified.** The shop-wide slowness users reported is explained by an
operator-side chaos toggle (`event: chaos_enabled`, non-investigator traffic) switched on
at 20:54:22.466Z, which injects `extra_latency_ms: 1500` into business routes. Request
durations on `/products`, `/products/{id}`, and `/orders` jumped from sub-2ms to 55-760ms
immediately after (E2-E7), while `/health` and `/metrics` stayed under 2ms throughout
(E3, E8) — matching the complaint's own observation that health checks read green and
fast while the shop felt slow. `faultline_chaos_enabled` was still `1` at the time of
writing (E9): **the incident is ongoing.**

The complaint's second claim — "some also mention seeing an error page once" — has no
confirmed explanation in current telemetry. A deep-dive did find a real, deterministic,
chaos-independent defect: `GET /products/3` throws an unhandled `ZeroDivisionError`
(stock is 0 for that product) and returns HTTP 500 (E10, E11). But the complete retained
log shows no non-investigator traffic ever reached that route (E13) — only the
investigation's own probes triggered it twice (E12). This rides along as a **latent
finding**, not a confirmed cause of the reported error page. Confidence in the latency
root cause is high; confidence that the latent 500 explains the error-page claim is low.

## Timeline

- **20:54:16.537Z** — process start, single `startup` event, no restarts since (E1).
- **20:54:17.291Z-20:54:19.407Z** — pre-toggle baseline: all routes sub-2ms (E3, E4).
- **20:54:22.466Z** — chaos toggle flips on via non-investigator request (E2): config-change marker.
- **20:54:24.577Z-20:54:30.579Z** — business routes degrade to 55-760ms in the same window (E5, E6, E7).
- **20:54:35Z** — human complaint raised, ~13s after the toggle — consistent with "the last few minutes."
- **20:54:44Z** — investigation started.
- **20:55:17.044Z** — investigator confirms `/health` still fast (1.356ms) 55s after the toggle (E8).
- **20:59:45.982Z-20:59:54.705Z** — deep-dive reproduces `ZeroDivisionError` on `GET /products/3` twice (E10).
- **21:01:04Z** — metrics confirm exactly 2 `/products/{id}` 500s and 2 `ZeroDivisionError`s ever recorded (E12); chaos still enabled (E9).
- **21:08:37Z** — product data confirms id=3 is the only product with `units_in_stock: 0` (E11).
- **21:07:57Z** — investigation concluded.

## Investigation

**Baseline**: `/health` fast and green, but `/metrics` showed `faultline_chaos_enabled 1`
and an already-elevated `/products/{product_id}` duration average — an immediate lead.
Reading the full log tail surfaced the `chaos_enabled` marker at 20:54:22.466Z with
`extra_latency_ms: 1500`, `failure_rate: 0.0`.

**Triage** (three lenses, parallel, blind to each other): infra-process, interfaces, and
software-defect all independently converged on the chaos toggle as the latency mechanism,
and all three independently flagged the same gap — no 5xx or exception evidence anywhere
to explain "saw an error page once," and `failure_rate: 0.0` means chaos's own
`error_status: 503` path cannot have fired.

**Deep-dive** (one agent, software-defect lens, targeting the error-page gap): used
`/openapi.json` and `/products` to find the valid id range and edge cases, then probed
product ids at the edges. `/products/3` (the only zero-stock product) deterministically
500'd with a `ZeroDivisionError`; ids 1, 2, 4, 5 and out-of-range ids (404) were all clean.
Metrics counters matched the reproduction 1:1, and the full log showed no non-investigator
request had ever reached that route.

**Judge** (fresh agent, evidence only): validated H1 (chaos toggle causes the slowness,
not load/saturation — citing the spared `/health` samples and the named mechanism in E2)
and validated H2 as stated (the defect is real and chaos-independent, but its link to the
complaint's error-page claim remains unconfirmed by customer traffic evidence).

## Hypotheses

### H1 — chaos toggle, validated
Statement, evidence, and state as in the machine core. The judge's strongest point: a
saturated worker pool would ordinarily queue the trivial `/health` check behind other
requests too, so sparing it while degrading business routes argues for route-level
injection rather than process-wide saturation (reinforces E3/E8 vs E5/E6/E7).

### H2 — zero-stock division defect, validated (as a latent finding)
Statement, evidence, and state as in the machine core. The defect mechanism itself is
airtight (an unconditional `ZeroDivisionError` from `units_ordered / product["units_in_stock"]`
when stock is 0 is deterministic, not probabilistic). What is NOT established is that any
real customer traffic ever exercised it during this incident window — the complete,
unrotated log shows otherwise (E13).

## Safe next steps

- Re-read `/metrics` and `lab/logs/app.log` periodically while `faultline_chaos_enabled`
  remains `1` to confirm when the toggle is turned off and whether latency returns to
  baseline (read-only confirmation, not remediation).
- If the "error page once" report recurs, capture the client-side timestamp and any
  visible error text promptly — it would narrow whether it correlates with a future
  `/products/3`-style hit or is a client timeout against the elevated latency.
- Treat the `/products/3` `ZeroDivisionError` as a standing latent defect to watch: a
  read-only periodic probe of `/metrics`'s `http_exceptions_total{type="ZeroDivisionError"}`
  would reveal if it starts incrementing from non-investigator traffic in the future.

## Gaps

- No rotated log backups exist for this process run, so any customer traffic before
  20:54:16.537Z (the only `startup` event) is unrecoverable.
- This surface has no request-volume/concurrency gauge, so "not customer load" for H1
  rests on the chaos toggle being a sufficient alternative explanation rather than a
  direct measurement that traffic volume was normal.
- The lab has no gateway/proxy tier, so a client-timeout explanation for the single
  error-page report — plausible given the elevated latencies alone — could not be tested
  on this surface.
