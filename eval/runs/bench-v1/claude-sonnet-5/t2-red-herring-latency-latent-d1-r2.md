---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-latency-shop-slowdown
  trigger: manual
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-19T02:37:59Z
  concluded: 2026-08-19T02:51:00Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode was enabled via POST /chaos/enable at 2026-08-19T02:37:39.338Z with extra_latency_ms=1500, injecting a randomized delay (spanning roughly 0-1500ms, not a fixed tax) into shop routes (/products, /products/{id}, /orders, /orders/{id}) for real and investigator traffic alike, producing the reported shop-wide slowness while /health and /metrics stayed fast."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode's extra_latency_ms=1500 (enabled at E3) injects a randomized delay spanning roughly 0-1500ms into shop routes, for both investigator and non-investigator traffic, while /health and /metrics are structurally exempt regardless of chaos state."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "The complaint's claim of seeing an error page once is not corroborated by any user-facing (non-investigator) error on this surface: zero non-investigator requests received a 4xx/5xx status anywhere in the log, and chaos's own error injection was configured at failure_rate=0.0."
    incident_class: interfaces
    state: validated
    evidence_for: [E3, E10, E12]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 deterministically raises an unhandled ZeroDivisionError (500) in shop.py:64's turnover_score calculation because product_id=3 has units_in_stock=0. Reproduced twice. Only the investigator's own probes ever exercised this route in the observed log (both occurrences carry konan-* request ids) — no non-investigator traffic hit /products/3, so this is a real defect not evidenced as part of the active incident."
    evidence: [E13, E14, E15, E16, E17]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:37:33.397Z"
    quote: "{\"ts\": \"2026-08-19T02:37:33.397Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:37:34.173Z"
    quote: "{\"ts\": \"2026-08-19T02:37:34.173Z\", \"message\": \"GET /products -> 200\", \"request_id\": \"6cb73fb334f4\", \"status\": 200, \"duration_ms\": 1.149, \"client\": \"127.0.0.1:55002\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:37:39.338Z"
    quote: "{\"ts\": \"2026-08-19T02:37:39.338Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"9763db1ba46a\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.0, \"error_status\": 503, \"extra_latency_ms\": 1500}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:37:42.355Z"
    quote: "{\"ts\": \"2026-08-19T02:37:42.355Z\", \"message\": \"GET /products -> 200\", \"request_id\": \"b66214fa2f13\", \"status\": 200, \"duration_ms\": 957.937, \"client\": \"127.0.0.1:55008\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:37:42Z-02:37:50Z (non-investigator client ids)"
    quote: "duration_ms 957.937 (GET /products), 1234.005 (GET /products/2), 476.836 (GET /products/1), 1322.992 (POST /orders), 430.998 (GET /orders) -- all status 200/201, all immediately after E3"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:38:29.454Z"
    quote: "{\"ts\": \"2026-08-19T02:38:29.454Z\", \"message\": \"GET /health -> 200\", \"request_id\": \"konan-1787107109-39619\", \"status\": 200, \"duration_ms\": 0.492, \"client\": \"127.0.0.1:55038\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log, investigator (konan-*) request ids, 2026-08-19T02:38Z-02:46Z"
    quote: "shop-route duration_ms samples, chronological: 6.393, 272.953, 215.115, 1309.559, 1434.495, 705.915, 573.581, 1435.792, 602.415, 392.321, 74.945 -- span from near pre-chaos baseline up to near the configured 1500ms cap, never exceeding it"
  - id: E8
    type: log
    source: "lab/logs/app.log, investigator (konan-*) GET /metrics requests, 2026-08-19T02:38Z-02:47Z"
    quote: "duration_ms samples: 0.575, 0.857, 0.527, 0.516, 0.519, 0.731, 0.516 -- 7 samples across the whole chaos window, none elevated"
  - id: E9
    type: metric
    source: "scripts/probe.sh /metrics (checked repeatedly through the investigation)"
    quote: "faultline_chaos_enabled 1"
  - id: E10
    type: metric
    source: "scripts/probe.sh /metrics (checked before /products/3 was ever probed)"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n(zero sample lines follow)"
  - id: E11
    type: metric
    source: "scripts/probe.sh /metrics"
    quote: "process_uptime_seconds 257.9842782081105 -- single continuous reading; only one startup event (E1) exists in the entire log, no counter reset"
  - id: E12
    type: log
    source: "lab/logs/app.log, full file (42 lines), all non-investigator (non konan-*) request ids"
    quote: "every non-investigator request in the complete log has status 200 or 201 -- zero 4xx/5xx among non-investigator traffic anywhere in the log"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:46:12.266Z"
    quote: "{\"ts\": \"2026-08-19T02:46:12.266Z\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787107571-39987\", \"status\": 500, \"duration_ms\": 459.79, \"client\": \"127.0.0.1:55099\"}"
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:46:12.250Z"
    quote: "{\"ts\": \"2026-08-19T02:46:12.250Z\", \"level\": \"ERROR\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787107571-39987\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"<checkout>/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\n...\\nZeroDivisionError: division by zero\"}"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:46:19.935Z"
    quote: "{\"ts\": \"2026-08-19T02:46:19.935Z\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787107579-39995\", \"status\": 500, \"duration_ms\": 907.653, \"client\": \"127.0.0.1:55100\"}"
  - id: E16
    type: probe
    source: "scripts/probe.sh /products response body"
    quote: "{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0}"
  - id: E17
    type: log
    source: "lab/logs/app.log, full file (42 lines), grep for path \"/products/3\""
    quote: "the only two log lines mentioning path /products/3 are E13 and E15, both carrying konan-* (investigator) request ids -- no non-investigator client ever requested /products/3"
gaps:
  - "The exact latency-injection mechanism (uniform jitter across 0-1500ms vs. some other distribution) cannot be confirmed without faultline's source, which is deliberately outside the investigator's reach per the lab boundary (docs/lab.md); the empirical duration spread (E7) is consistent with randomized jitter but the precise algorithm is unverified."
  - "The /health exemption from chaos latency rests on a single sample (E6), unlike /metrics which was verified with 7 samples (E8) spread across the whole window. Not re-verified with additional /health probes."
  - "Cannot confirm whether any real user hit /products/3 before this log window began or through a path this app does not log: only one process startup exists (E1) and no rotated backup logs (.1-.3) are present, so no history predates 2026-08-19T02:37:33.397Z. The ZeroDivisionError latent finding is classified as latent based only on the evidence available in this window."
  - "The eval-side operator surface (/chaos state details, scenario recipes, ground-truth defect catalog) is out of investigator reach by design (docs/lab.md); this investigation argues only from the read-only telemetry surface listed there."
usage:
  model: claude-sonnet-5
  tokens: 4027052
  wall_clock_seconds: 781
---

# Shop-wide slowness traced to a chaos-mode latency toggle; reported error page not corroborated by user-facing traffic

## Summary

**Verdict: root-cause-identified.** A chaos-mode toggle (`POST /chaos/enable`, logged at 2026-08-19T02:37:39.338Z with `extra_latency_ms=1500`) injected a randomized delay into shop routes (`/products`, `/products/{id}`, `/orders`, `/orders/{id}`) immediately afterward, spanning roughly 0-1500ms across 16+ sampled requests from both real and investigator traffic (E4, E5, E7). `/health` and `/metrics` stayed fast throughout — under 1ms across 8 samples (E6, E8) — which matches the complaint's own observation that "health checks are green and fast." This is a config-change-driven latency injection (`incident_class: interfaces`), not a code defect, process crash, or resource-saturation issue: the software-defect and infra-process triage lenses independently found no unhandled exceptions, no 5xx among user traffic, no restart, and no saturation signature.

The complaint's second claim — "some also mention seeing an error page once" — has **no corroborating server-side evidence**: across the complete log, every non-investigator request returned 200/201 (E12), and chaos's own error path (`error_status=503`) was configured with `failure_rate=0.0`, i.e. never armed. A real, reproducible defect was found during deep-dive probing — `GET /products/3` deterministically 500s with a `ZeroDivisionError` (division by zero on `units_in_stock=0`, E13-E16) — but both occurrences were triggered only by the investigator's own probes (E17); no user traffic is evidenced to have hit that route. It rides along as a **latent finding**, not the confirmed cause of the reported error page. Confidence is high on the latency root cause, moderate on the error-page non-corroboration (the log window is short and cannot see before process start).

## Timeline (UTC)

- `02:37:33.397Z` — faultline process starts (E1); only startup marker in the log.
- `02:37:34Z`-`02:37:36Z` — pre-chaos baseline traffic, all sub-13ms (E2).
- `02:37:39.338Z` — **config-change marker**: chaos mode enabled, `failure_rate=0.0, error_status=503, extra_latency_ms=1500` (E3).
- `02:37:42Z`-`02:37:50Z` — first non-investigator requests after the toggle show elevated latency: 431-1323ms (E4, E5).
- `02:38:29Z`-`02:47:23Z` — investigator baseline/triage/deep-dive probing: shop routes show a continuous spread of durations from 6ms to 1436ms (E7); `/health` (E6) and `/metrics` (E8) stay under 1ms throughout, including immediately after the largest shop-route spikes.
- `02:46:12.250Z`-`02:46:19.935Z` — deep-dive probe of `/products/3` (product with `units_in_stock=0`, E16) deterministically raises `ZeroDivisionError`, reproduced twice (E13-E15); both hits are investigator-originated (E17).
- `02:51:00Z` — investigation concluded.

## Investigation

1. **Baseline**: read `/health`, `/metrics`, and the full `lab/logs/app.log` (only 21 lines at first read, no rotated backups — a genuinely fresh process). Found the chaos-enabled config marker and elevated shop-route durations immediately after it.
2. **Triage** (3 lenses, parallel, blind to each other): infra-process found no restart/crash/saturation signature and confirmed the latency onset aligns with the config marker, not a lifecycle event. interfaces found the same config-marker onset boundary and flagged the error-page claim as uncorroborated. software-defect found zero exceptions, zero 5xx, and no data-dependent failure shape at that point in the investigation.
3. **Judge round 1**: H1 (chaos latency) came back **inconclusive** — one investigator probe to `/products` shortly after the toggle ran in only 6.4ms, and no timing evidence had been cited for `/metrics` staying fast. H2 (error page uncorroborated) came back **validated**.
4. **Deep-dive** (interfaces lens, targeted): gathered 11 more shop-route samples and 5 more `/metrics` samples to characterize the distribution, and reproduced a real `GET /products/3` 500 (ZeroDivisionError) along the way.
5. **Judge round 2** (fresh judge, evidence-only): H1 **validated** — the wider sample set shows a continuous spread consistent with randomized jitter, not a bimodal "some exempt" pattern, and `/metrics`'s 7 sub-ms samples settle the exemption claim. H2 **validated**. The `/products/3` defect confirmed as a latent finding, not the active incident, since only investigator request ids ever hit that route.

## Hypotheses

### H1 — Chaos-mode latency injection (validated)
Chaos was enabled with `extra_latency_ms=1500` at E3; every shop-route sample taken afterward (E4, E5, E7 — 16+ points total) falls somewhere between near-baseline and ~1436ms, never above the configured cap, while `/health` (E6) and `/metrics` (E8, 7 samples) never show elevation. This is the direct, evidenced cause of "the whole shop got painfully slow" while "health checks are green and fast."

### H2 — Reported error page not corroborated by user-facing evidence (validated)
Every non-investigator request in the complete log returned 200/201 (E12); chaos's configured error path had `failure_rate=0.0` (E3); the exception counter was zero before any defect-triggering probe occurred (E10). The complaint's "error page" sighting has no matching server-side signal in this surface.

## Safe next steps

- Re-check `/metrics` and `faultline_chaos_enabled` periodically (read-only) to see when/if chaos mode is toggled off and latency returns to baseline.
- If the error-page reports continue or recur, capture the exact route/product a user was viewing when it happened — that would let a future investigation correlate it against routes like `/products/3` where a real (if currently unconfirmed-by-user-traffic) defect exists.
- No remediation actions taken or suggested here — out of scope for this read-only investigation.

## Gaps

- The exact latency-injection distribution (uniform jitter vs. another shape) can't be confirmed without faultline's source, which is deliberately out of the investigator's reach.
- The `/health` chaos-exemption claim rests on a single sample vs. seven for `/metrics` — thinner evidence, though it did not change the judge's verdict.
- No log history predates the single process startup at 02:37:33.397Z (no rotated backups exist), so whether any real user hit `/products/3` before this window, or through an unlogged path, cannot be determined — the ZeroDivisionError defect is recorded as latent on that basis, not ruled out as user-facing.
- The eval-side operator surface (`/chaos`, scenario recipes, ground-truth defect catalog) is out of investigator reach by design; this investigation argues only from `docs/lab.md`'s read-only surface.
