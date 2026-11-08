---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-intermittent-503s
  trigger: manual
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-02T15:08:32Z
  concluded: 2026-11-02T15:16:36Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "faultline's internal chaos switch, enabled at 2026-11-02T15:07:56.882Z via POST /chaos/enable with failure_rate 0.4 and error_status 503 and never disabled, injects fast random HTTP 503 failures into business endpoints while /health stays 200."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal degradation switch (chaos mode), enabled at 15:07:56.882Z with failure_rate 0.4 and error_status 503, randomly rejects business-endpoint requests with sub-millisecond 503s; retries succeed because injection is random per request, and /health is untouched, so the health dashboard stays green."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E25]
    evidence_against: [E26]
  - id: H2
    statement: "A code defect in the target (the ZeroDivisionError in get_product for a product with units_in_stock 0) is the cause of the user-reported intermittent failures."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E14, E15, E16, E17, E18]
    evidence_against: [E19, E4, E5, E6, E8]
  - id: H3
    statement: "Demand exceeded capacity (load saturation), causing the intermittent errors."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E7, E23, E24]
  - id: H4
    statement: "The process crashed or restarted, causing the intermittent errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E20, E21, E22]
latent_findings:
  - statement: "GET /products/3 deterministically returns HTTP 500: get_product (shop.py line 64) computes units_ordered / product[\"units_in_stock\"] and product 3 has units_in_stock 0 (ZeroDivisionError). Only investigator (konan-stamped) probes have triggered it, so it is latent, not the active incident; product 3 is in the public /products listing, so any user request would trigger it."
    evidence: [E14, E15, E16, E17, E18]
  - statement: "Chaos-injected 503s are counted in http_requests_total under the raw path label (e.g. path=\"/products/1\") while handled responses use the route-template label (path=\"/products/{product_id}\"), so an error-rate query grouped by route template does not count the injected failures."
    evidence: [E24]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:07:56.882Z"
    quote: |-
      {"ts": "2026-11-02T15:07:56.882Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "3f605943cc04", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:07:56.883Z"
    quote: |-
      {"ts": "2026-11-02T15:07:56.883Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "3f605943cc04", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.082, "client": "127.0.0.1:58921"}
  - id: E3
    type: metric
    source: "/metrics @ ~2026-11-02T15:12:09Z (probe konan-1793632329-94333)"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:08:06.365Z"
    quote: |-
      {"ts": "2026-11-02T15:08:06.365Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "c886a273814f", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:08:06.366Z"
    quote: |-
      {"ts": "2026-11-02T15:08:06.366Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "c886a273814f", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.313, "client": "127.0.0.1:58929"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:08:07.430Z"
    quote: |-
      {"ts": "2026-11-02T15:08:07.430Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "b279497d40c0", "event": "chaos_failure", "method": "GET", "path": "/orders"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:08:07.431Z"
    quote: |-
      {"ts": "2026-11-02T15:08:07.431Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "b279497d40c0", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.509, "client": "127.0.0.1:58930"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:08:00.008Z"
    quote: |-
      {"ts": "2026-11-02T15:08:00.008Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "6f3709b38117", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.202, "client": "127.0.0.1:58923"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:08:08.488Z"
    quote: |-
      {"ts": "2026-11-02T15:08:08.488Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "3eb84ebe81e0", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 1.331, "client": "127.0.0.1:58931"}
  - id: E10
    type: probe
    source: "/orders/3, request_id konan-1793632296-94295"
    quote: |-
      {"error":"service temporarily degraded","request_id":"konan-1793632296-94295"}
      -- HTTP 503 in 0.001054s request_id=konan-1793632296-94295
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:11:36.528Z"
    quote: |-
      {"ts": "2026-11-02T15:11:36.528Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1793632296-94295", "event": "chaos_failure", "method": "GET", "path": "/orders/3"}
  - id: E12
    type: probe
    source: "/health, request_id konan-1793632123-94128"
    quote: |-
      {"status":"ok","uptime_seconds":55.0562771668192}
      -- HTTP 200 in 0.001442s request_id=konan-1793632123-94128
  - id: E13
    type: metric
    source: "/metrics @ ~2026-11-02T15:12:09Z (probe konan-1793632329-94333); no non-200 /health series exists"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3"
  - id: E14
    type: probe
    source: "/products/3, request_id konan-1793632295-94290"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793632295-94290"}
      -- HTTP 500 in 0.010388s request_id=konan-1793632295-94290
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:11:35.825Z (stack trimmed to the raising frame)"
    quote: |-
      {"ts": "2026-11-02T15:11:35.825Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793632295-94290", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last): ... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E16
    type: probe
    source: "/products/3 (repeat), request_id konan-1793632350-94341"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793632350-94341"}
      -- HTTP 500 in 0.005371s request_id=konan-1793632350-94341
  - id: E17
    type: probe
    source: "/products, request_id konan-1793632263-94224 (excerpt: product 3)"
    quote: "{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0}"
  - id: E18
    type: metric
    source: "/metrics @ ~2026-11-02T15:12:09Z (probe konan-1793632329-94333)"
    quote: "http_exceptions_total{type=\"ZeroDivisionError\"} 1"
  - id: E19
    type: metric
    source: "/metrics @ 2026-11-02T15:08:44Z (baseline, probe konan-1793632124-94133); no series lines followed this counter header"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-02T15:07:48.885Z; the only startup event in the log"
    quote: |-
      {"ts": "2026-11-02T15:07:48.885Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E21
    type: metric
    source: "/metrics @ 2026-11-02T15:08:44Z (baseline, probe konan-1793632124-94133)"
    quote: "process_uptime_seconds 55.694637916982174"
  - id: E22
    type: metric
    source: "/metrics @ ~2026-11-02T15:12:09Z (probe konan-1793632329-94333)"
    quote: "process_uptime_seconds 260.43476541689597"
  - id: E23
    type: metric
    source: "/metrics, identical value in both scrapes (konan-1793632124-94133 at uptime 55.69s and konan-1793632329-94333 at uptime 260.43s)"
    quote: "process_max_rss_bytes 47923200"
  - id: E24
    type: metric
    source: "/metrics @ ~2026-11-02T15:12:09Z (probe konan-1793632329-94333)"
    quote: |-
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 12
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1
  - id: E25
    type: log
    source: "lab/logs/app.log, grep -c per event name, read ~2026-11-02T15:14Z"
    quote: |-
      grep -c "chaos_enabled" -> 1
      grep -c "chaos_disabled" -> 0
  - id: E26
    type: probe
    source: "first prediction-test batch, 8 GET probes 15:11:03Z–15:11:08Z (/products, /products/1, /orders, /products/2, /orders/1, /products/4, /orders/2, /products/5), all returned HTTP 200; first trailer quoted"
    quote: "-- HTTP 200 in 0.004063s request_id=konan-1793632263-94224"
gaps:
  - "Who or what enabled the chaos switch is outside the telemetry surface: the POST /chaos/enable came from 127.0.0.1:58921 with no konan- request-id prefix (E2), which excludes the investigator but identifies no actor."
  - "The user-facing error rate after 15:08:08.488Z is unmeasurable: no non-investigator traffic appears in the log after E9, so impact scale rests on the two quoted user failures plus the still-on gauge."
  - "The first prediction-test batch of 8 investigator probes all passed (E26), a ~1.7% outcome if each request fails at rate 0.4; windowed or scoped injection cannot be excluded from telemetry alone, though the second batch (4/8 injected 503s, E10/E11) confirms injection was live."
  - "Whether /health is exempt from injection or merely lucky is undetermined: only 3 health samples exist (E13)."
  - "The reporting dashboard's actual query is outside the surface; a /health-based check staying green is consistent with the evidence (E12, E13), but the dashboard itself was not inspected."
usage:
  model: claude-fable-5
  tokens: 2573526
  wall_clock_seconds: 484
---

# Intermittent shop 503s: an internal chaos switch, enabled and left on

## Summary

Root cause identified: faultline's internal chaos switch was enabled at
2026-11-02T15:07:56.882Z (`POST /chaos/enable`, failure_rate 0.4, error_status 503)
and was never disabled. While on, it rejects a random ~40% of business-endpoint
requests with sub-millisecond HTTP 503s. This matches every reported symptom:
failures are intermittent, retries succeed (the same request passed and failed
seconds apart), both product pages and orders are hit, onset was sudden (22 seconds
before the complaint's start time), and the health dashboard stays green because
/health is untouched. The switch was still on at the end of the investigation
(`faultline_chaos_enabled 1`). Confidence is high: the service's own telemetry
labels each failure `chaos_failure`, and live investigator probes reproduced the
injected 503s. One real but latent defect rides along: `GET /products/3` fails
deterministically with a ZeroDivisionError (division by `units_in_stock` 0) — only
investigator probes have triggered it, but any user who opens that product page
would hit it.

## Timeline

- 15:07:48.885Z — faultline 0.1.0 starts; the only startup event (E20).
- 15:07:56.882Z — **configuration-change marker:** chaos mode enabled, failure_rate
  0.4, error_status 503, via POST /chaos/enable from 127.0.0.1:58921 (E1, E2).
- 15:08:00.008Z — user GET /products/1 → 200 (E8).
- 15:08:06.365Z — first injected user failure: GET /products/1 → 503, tagged
  `chaos_failure` (E4, E5). Same input as E8: random, not input-dependent.
- 15:08:07.430Z — injected user failure: GET /orders → 503 (E6, E7).
- 15:08:08.488Z — user GET /products/4 → 200; "works again on retry" (E9).
- 15:08:18Z — complaint startsAt (reporter).
- 15:08:32Z — investigation starts (trigger latency 14 s).
- 15:08:43–44Z — baseline: /health 200, no exception series, uptime 55.69 s
  (E12, E19, E21).
- 15:11:03–08Z — prediction test, batch 1: 8/8 investigator probes pass (E26).
- 15:11:35–38Z — batch 2: 4/8 probes get injected 503s with `chaos_failure` events
  carrying konan-stamped request ids (E10, E11); GET /products/3 → 500
  ZeroDivisionError (E14, E15).
- ~15:12:09Z — gauge still on: `faultline_chaos_enabled 1`, uptime 260.43 s
  monotonic, RSS flat (E3, E22, E23).
- ~15:12:30Z — /products/3 repeat → 500 again; deterministic (E16).
- 15:16:36Z — investigation concluded.

## Investigation

Complaint object (manual trigger, recorded verbatim):

```
source: human
fingerprint: human-1793632098
labels.alertname: human-report
annotations.summary: "Users report the shop is intermittently failing — some page
  loads and orders error out, then work again on retry. It started suddenly a few
  minutes ago. Our health dashboard is green."
startsAt: 2026-11-02T15:08:18Z
investigation start: 2026-11-02T15:08:32Z (trigger latency 14 s)
```

Rounds as they ran:

1. **Baseline** (15:08:43Z): health 200, metrics snapshot, full log read. The
   baseline itself surfaced the chaos_enabled marker and two user-traffic 503s.
2. **Triage**, three lenses in parallel (infra-process, software-defect,
   interfaces), each given only the lens file, the surface contract, the verbatim
   complaint, and the baseline summary. All three converged on the chaos switch;
   software-defect and interfaces reported no anomaly of their own domain beyond
   the metrics label split (E24); infra-process confirmed no restart, no memory
   growth, no latency shift.
3. **Deep-dive** (orchestrator-level, cheap): H1's prediction — a mix of 200s and
   injected 503s on stamped probes — tested with 16 business-endpoint probes.
   Batch 1: 8/8 passed (E26, logged as evidence against). Batch 2: 4/8 injected
   503s (E10, E11), confirming live injection; plus the /products/3 500 (E14),
   re-probed once to establish determinism (E16).
4. **Judge** (fresh agent, claims + verbatim evidence only): H1 validated, H2–H4
   invalidated, L1 validated, L2's metric fact supported but its dashboard
   inference not — the inference was dropped. The judge's settling item for H1
   (one enable, no toggles) was closed by E25.

## Hypotheses

### H1 — chaos degradation switch (validated)

An internal operational switch injects random 503s at rate 0.4 since
15:07:56.882Z and is still on. For: the enable marker and its POST (E1, E2), the
live gauge (E3), user failures explicitly tagged `chaos_failure` (E4–E7), the
same input passing then failing (E8, E5), recovery on the next request (E9),
reproduction on stamped probes (E10, E11), green health (E12, E13), and exactly
one enable with zero disables (E25). Against: one 8-probe pass streak (E26),
P ≈ 1.7% under the configured rate — unexplained, recorded as a gap.

### H2 — software defect as the active incident (invalidated)

A real ZeroDivisionError exists (E14–E18) but cannot be the reported incident:
no exception series existed during the user-facing failure window (E19), the user
errors are chaos-tagged 503s, not 500s (E4–E6), and the failures are random per
request (E8 vs E5), the opposite of a deterministic per-input defect. It survives
as latent finding L1.

### H3 — load saturation (invalidated)

Failures complete in 0.3–0.5 ms (E5, E7) — no queueing; peak RSS is flat across
the window (E23); total request counts are in the dozens (E24).

### H4 — process crash or restart (invalidated)

One startup event (E20); uptime rises monotonically 55.69 s → 260.43 s with no
reset (E21, E22).

## Safe next steps

- Page the operator who owns the chaos/degradation switch: the enable call came
  from localhost at 15:07:56.883Z (E2). If it was not intentional, the operator —
  not the investigator — decides on turning it off.
- Watch `faultline_chaos_enabled` to confirm when the switch goes off, and
  re-check business-endpoint status codes afterward.
- Review the health dashboard's query: it reads green while business endpoints
  fail. Add business-endpoint error rates, and note that chaos-injected 503s sit
  under raw-path labels, which a route-template grouping misses (E24).
- Before any fix for latent finding L1, reproduce it read-only via
  `GET /products/3` and check for other zero-stock products in `/products`.

## Gaps

The frontmatter list, elaborated: the actor behind the enable call is outside the
telemetry surface (the request carries no identity); user impact after
15:08:08.488Z cannot be quantified because no non-investigator traffic followed;
the 8-probe pass streak leaves windowed or scoped injection formally open even
though batch 2 proved injection live; /health's exemption is observed on only 3
samples; and the dashboard's own query was never inspected — its greenness is
explained consistently, not verified.
