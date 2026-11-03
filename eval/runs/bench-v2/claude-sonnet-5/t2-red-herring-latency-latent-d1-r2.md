---
konan_journal: 2
investigation:
  id: 2026-11-02-chaos-mode-latency-slowdown
  trigger: manual
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-11-02T21:11:51Z
  concluded: 2026-11-02T21:34:41Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos/degradation toggle inside faultline was switched on at 2026-11-02T21:11:29.942Z and never reverted. While active it adds a variable amount of latency (observed ~11ms to ~1473ms per request) to the shop-surface routes (/products, /products/{id}, /orders), while /health and /metrics stay consistently fast — producing the 'whole shop painfully slow' symptom and matching the 'health checks are green and fast' detail. Its configured failure_rate is 0.0, so it produces no error status."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "Chaos/degradation toggle (failure_rate=0.0, error_status=503, extra_latency_ms=1500) enabled at 21:11:29.942Z and left on injects variable latency into /products, /products/{id}, and /orders; /health and /metrics are unaffected; no 503 or any error status results."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17]
    evidence_against: []
  - id: H2
    statement: "faultline's GET /products/{product_id} handler divides units_ordered by units_in_stock with no zero-guard (shop.py line 64); product id 3 has units_in_stock=0, so GET /products/3 deterministically raises ZeroDivisionError and returns HTTP 500. Offered as a candidate explanation for the complaint's 'seeing an error page once' detail, but the complaint predates every recorded occurrence, and both occurrences were investigator-triggered — no customer-attributed request is shown to have hit this path during the complaint window."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E18, E19, E20, E22, E23]
    evidence_against: [E21]
latent_findings:
  - statement: "GET /products/3 deterministically raises an unhandled ZeroDivisionError (shop.py:64, units_ordered / units_in_stock with units_in_stock=0) and returns HTTP 500. Real, reproducible defect, confirmed latent: zero occurrences in telemetry before the investigation's own probes triggered it twice."
    evidence: [E18, E19, E20, E22, E23]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:11:24.009Z"
    quote: '{"ts": "2026-11-02T21:11:24.009Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:11:29.942Z"
    quote: '{"ts": "2026-11-02T21:11:29.942Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "99bb4ca0e02a", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:11:25.824Z (pre-toggle)"
    quote: '{"ts": "2026-11-02T21:11:25.824Z", "message": "GET /products/1 -> 200", "request_id": "916c35de5c40", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.996}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:11:34.530Z (+4.6s post-toggle)"
    quote: '{"ts": "2026-11-02T21:11:34.530Z", "message": "GET /products/2 -> 200", "request_id": "3c9c14cc3c71", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 1442.068}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:11:38.841Z (+8.9s post-toggle)"
    quote: '{"ts": "2026-11-02T21:11:38.841Z", "message": "GET /orders -> 200", "request_id": "95a0c844fee3", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 751.253}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:14:15.556Z (+2m45.6s post-toggle)"
    quote: '{"ts": "2026-11-02T21:14:15.556Z", "message": "GET /products -> 200", "request_id": "konan-1793654054-6091", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 780.818}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:16:41.016Z (+5m11s post-toggle)"
    quote: '{"ts": "2026-11-02T21:16:41.016Z", "message": "GET /health -> 200", "request_id": "konan-1793654201-6220", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.441}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:16:45.119Z (+5m15s post-toggle)"
    quote: '{"ts": "2026-11-02T21:16:45.119Z", "message": "GET /products -> 200", "request_id": "konan-1793654203-6226", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1472.737}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:16:56.354Z (+5m26s post-toggle)"
    quote: '{"ts": "2026-11-02T21:16:56.354Z", "message": "GET /orders -> 200", "request_id": "konan-1793654216-6241", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 10.84}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:24:11.600Z (+12m42s post-toggle)"
    quote: '{"ts": "2026-11-02T21:24:11.600Z", "message": "GET /orders -> 200", "request_id": "konan-1793654650-6386", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1398.254}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:24:17.362Z"
    quote: '{"ts": "2026-11-02T21:24:17.362Z", "message": "GET /orders -> 200", "request_id": "konan-1793654655-6393", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1470.759}'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:24:21.615Z"
    quote: '{"ts": "2026-11-02T21:24:21.615Z", "message": "GET /orders -> 200", "request_id": "konan-1793654660-6400", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 784.194}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:24:25.742Z"
    quote: '{"ts": "2026-11-02T21:24:25.742Z", "message": "GET /orders -> 200", "request_id": "konan-1793654665-6407", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 183.944}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:24:30.484Z"
    quote: '{"ts": "2026-11-02T21:24:30.484Z", "message": "GET /orders -> 200", "request_id": "konan-1793654669-6414", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1154.163}'
  - id: E15
    type: metric
    source: "/metrics probe, request_id konan-1793654401-6299 @ 2026-11-02T21:20:01.412Z"
    quote: "faultline_chaos_enabled 1"
  - id: E16
    type: metric
    source: "/metrics probe, request_id konan-1793654401-6299 @ 2026-11-02T21:20:01.412Z"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 6\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"404\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 2"
  - id: E17
    type: log
    source: "lab/logs/app.log, six GET /metrics requests spanning the window"
    quote: "duration_ms 0.605 (@21:12:09.788Z), 0.493 (@21:13:51.611Z), 0.729 (@21:14:07.538Z), 0.782 (@21:14:31.712Z), 0.689 (@21:16:32.560Z), 0.525 (@21:17:08.925Z) — all sub-millisecond"
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:14:22.413Z"
    quote: '{"ts": "2026-11-02T21:14:22.413Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793654062-6096", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "...File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}'
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:14:22.427Z"
    quote: '{"ts": "2026-11-02T21:14:22.427Z", "message": "GET /products/3 -> 500", "request_id": "konan-1793654062-6096", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 125.555}'
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:14:31.682Z"
    quote: '{"ts": "2026-11-02T21:14:31.682Z", "message": "GET /products/3 -> 500", "request_id": "konan-1793654070-6106", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 1157.138}'
  - id: E21
    type: metric
    source: "/metrics probe, request_id konan-1793653929-6009 @ 2026-11-02T21:12:09.788Z (after the complaint, before E18–E20)"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n(no data rows — zero exceptions recorded)"
  - id: E22
    type: probe
    source: "/products probe, request_id konan-1793654430-6314 @ 2026-11-02T21:20:31.139Z"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-02T21:14:23.046Z"
    quote: '{"ts": "2026-11-02T21:14:23.046Z", "message": "GET /products/4 -> 200", "request_id": "konan-1793654062-6101", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 44.232}'
gaps:
  - "No source in this surface correlates a customer-originated request to the /products/3 ZeroDivisionError during the complaint window — no session, CDN, or support-ticket log is part of the surface contract. Whether the reported 'error page once' was this defect, a client-side timeout from the chaos latency, or something else cannot be determined from available telemetry."
  - "No source-level confirmation of the chaos toggle's injection distribution — the ~11ms–1473ms spread is consistent with a per-request randomized draw bounded near the configured extra_latency_ms=1500, but the exact mechanism lives in faultline's source, outside the investigator's reach per docs/lab.md."
  - "process_max_rss_bytes was observed as a constant single value (47431680) across every scrape taken — too few independent samples to confirm or rule out a memory-growth trend, though nothing else pointed to one."
usage:
  model: claude-sonnet-5
  tokens: 5519175
  wall_clock_seconds: 1370
---

# Shop-wide slowness traced to an un-reverted chaos-mode latency toggle

## Summary

**Root cause identified.** The reported "whole shop painfully slow" is explained by an
internal chaos/degradation toggle in faultline (`chaos_enabled`, `failure_rate=0.0`,
`error_status=503`, `extra_latency_ms=1500`) that was switched on at
2026-11-02T21:11:29.942Z — 13 seconds before the complaint was reported — and was never
reverted. While active, it adds a variable amount of latency (observed ~11ms to ~1473ms
per request, confirmed on dozens of samples spanning from 4.6 seconds to over 12 minutes
after the toggle) to the shop-surface routes `/products`, `/products/{id}`, and `/orders`,
while `/health` and `/metrics` — a structurally separate interface — stay consistently
fast (sub-millisecond to low-millisecond). This matches the complaint's "health checks are
green and fast" detail exactly: the monitored interface and the degraded interface are
different routes. The toggle's configured failure rate is 0.0, so it produces no error
status on its own — confirmed by zero `503` responses anywhere in the metrics across the
whole investigation.

Separately, a genuine, reproducible code defect was found and ruled out as the explanation
for the complaint's "seeing an error page once" detail: `GET /products/3` deterministically
raises an unhandled `ZeroDivisionError` (zero stock divides into a turnover-score
calculation) and returns HTTP 500. It is real and latent, but every recorded occurrence
was triggered by this investigation's own probes, after the complaint was received — no
customer-attributed request is shown to have hit it during the complaint window. It rides
along as a latent finding, not the active incident.

Confidence: high on the chaos-toggle root cause (independently confirmed by two lenses,
validated by an adversarial judge across two rounds of targeted probing). The "error page"
detail of the complaint remains unexplained by direct evidence; the zero-stock defect is
the best available candidate but is not confirmed (see Gaps).

## Timeline

- **21:11:24.009Z** (E1) — faultline process starts.
- **21:11:25.824Z** (E3) — pre-toggle baseline: `GET /products/1` in 0.996ms.
- **21:11:29.942Z** (E2) — chaos mode enabled by a non-investigator request
  (`request_id 99bb4ca0e02a`, not `konan-*`-stamped): `failure_rate=0.0`,
  `error_status=503`, `extra_latency_ms=1500`.
- **21:11:34.530Z** (E4) — first elevated sample, `GET /products/2` in 1442.068ms, 4.6s
  after the toggle.
- **21:11:38.841Z** (E5) — `GET /orders` elevated to 751.253ms, 8.9s after the toggle.
- **21:11:43Z** — complaint received via `/konan` (trigger latency to investigation start:
  8 seconds).
- **21:11:51Z** — investigation loop starts.
- **21:12:09.788Z** (E21) — baseline metrics scrape, after the complaint: zero exceptions
  recorded in telemetry at this point.
- **21:14:15.556Z** (E6) — `/products` still elevated (780.818ms), 2m46s after the toggle.
- **21:14:22.413Z–.427Z** (E18, E19) — investigator probe of `/products/3` triggers the
  first `ZeroDivisionError` / HTTP 500.
- **21:14:23.046Z** (E23) — sibling probe `/products/4` succeeds normally (200), confirming
  the defect is isolated to product id 3.
- **21:14:31.682Z** (E20) — second, independent reproduction of the same `/products/3`
  defect.
- **21:16:41.016Z–21:16:45.119Z** (E7, E8) — `/health` fast (0.441ms) while `/products` is
  still elevated (1472.737ms) in the same window.
- **21:16:56.354Z** (E9) — one low-latency `/orders` sample (10.84ms) — initially looked
  like a possible route exemption from the chaos injection.
- **21:20:01.412Z** (E15, E16) — metrics snapshot: chaos toggle still on; no `503` status
  recorded anywhere, for any path, across the whole investigation so far.
- **21:24:11.600Z–21:24:30.484Z** (E10–E14) — five fresh `/orders` probes, all elevated
  (184ms–1471ms), closing the question raised by E9: not a route exemption, a low draw
  from a variable per-request injection.
- **21:34:41Z** — investigation concluded.

## Investigation

1. **Baseline** — confirmed the lab was reachable, process uptime (~42s at first probe),
   `/health` fast, and a `/metrics` snapshot showing `faultline_chaos_enabled 1` already
   set and a `chaos_enabled` log line in the (very short, 21-line) log history.
2. **Triage** — fanned out three lenses in parallel (infra-process, interfaces,
   software-defect), each given only the lens file, the surface contract, the complaint
   verbatim, and the baseline summary. All three converged independently: the two
   infra/interfaces lenses both found the chaos-toggle timeline; the software-defect lens
   found and reproduced the `/products/3` `ZeroDivisionError`, and explicitly flagged it
   as zero-occurrence in customer traffic.
3. **Deep-dive round 1** — one agent live-reconfirmed the chaos-toggle hypothesis with
   fresh probes; found the toggle still active, elevated latency reproduced, and one
   disconfirming data point (a fast `/orders` sample) honestly reported rather than
   discarded.
4. **Judge round 1** — ruled both hypotheses inconclusive: H1's claim that `/orders` is
   affected was contradicted by the one fast sample; H2's customer-impact claim was
   unestablished.
5. **Deep-dive round 2** — targeted gathering per the judge's "what would settle it":
   5 fresh `/orders` probes, all elevated (184–1471ms), with chaos confirmed on
   immediately before and after — settled the route-scope question.
6. **Judge round 2 (final)** — H1 validated (chaos toggle causes shop-wide latency,
   matches failure_rate/no-503 prediction exactly, timing fits the complaint within 13
   seconds); H2 invalidated as an explanation for the complaint specifically (defect is
   real, but postdates nothing — every occurrence postdates the complaint and is
   investigator-caused), and rides along as a latent finding instead.

## Hypotheses

### H1 — chaos-mode latency toggle (validated)

An internal degradation switch, armed with `extra_latency_ms=1500` and `failure_rate=0.0`,
was enabled 13 seconds before the complaint and never turned off. Evidence for: the exact
timing match (E2 vs. complaint time), the sharp before/after contrast on `/products` (E3
vs. E4), persistence from seconds to over 12 minutes after the toggle on every shop route
including `/orders` (E5–E14), the untouched speed of `/health`/`/metrics` throughout
(E7, E17), and the complete absence of any `503` or non-{200,201,404,500} status anywhere
in the metrics (E16), exactly matching the toggle's own `failure_rate=0.0`. No evidence
against survived scrutiny — a single fast `/orders` sample (E9) was resolved by 5/5 fresh
same-route probes (E10–E14) all landing elevated, consistent with a variable per-request
draw rather than a route exemption.

### H2 — zero-stock division defect (invalidated as cause of the complaint; latent)

`GET /products/3` deterministically throws `ZeroDivisionError` (E18) and returns HTTP 500
(E19, E20) because product id 3 has `units_in_stock: 0` (E22) and the handler divides by
it unguarded. A sibling product on the same route succeeds (E23), confirming the failure
is isolated to this one input — the classic data-dependent defect shape. However, a
metrics scrape taken 26 seconds after the complaint (E21) shows zero exceptions recorded
at that point, and the only two occurrences in the entire investigation both carry
investigator-stamped request ids, generated nearly 2.5 minutes after the complaint. The
complaint cannot be explained by an event that had not yet happened. The defect is real
and worth tracking, but it is a latent finding, not the active incident.

## Safe next steps

- Watch `faultline_chaos_enabled` on `/metrics`; it is still `1` as of this investigation's
  close — confirm with whoever owns the toggle whether it is expected to still be on.
- Track shop-route `p95`/`p99` latency (`http_request_duration_seconds_sum`/`_count` for
  `/products`, `/products/{product_id}`, `/orders`) against `/health` latency as a
  standing pair — the gap between them is the fastest read-only signal that this toggle
  (or another like it) is active again.
- Add a read-only alert on `http_exceptions_total{type="ZeroDivisionError"} > 0` so a real
  future occurrence on `/products/3` is caught immediately, rather than discovered only
  when an investigation happens to probe that id.
- If customer-impact confirmation is ever needed for the `/products/3` defect, a
  non-investigator-stamped `request_id` hitting that path with a 500 status, at or before
  a future complaint's timestamp, would settle it — no such correlation source exists in
  the current surface contract.

## Gaps

- No source in this surface correlates a customer-originated request to the
  `/products/3` `ZeroDivisionError` during the complaint window — no session, CDN, or
  support-ticket log is part of the surface contract. Whether the reported "error page
  once" was this defect, a client-side timeout from the chaos latency, or something else
  cannot be determined from available telemetry.
- No source-level confirmation of the chaos toggle's injection distribution — the
  ~11ms–1473ms spread is consistent with a per-request randomized draw bounded near the
  configured `extra_latency_ms=1500`, but the exact mechanism lives in faultline's source,
  outside the investigator's reach per `docs/lab.md`.
- `process_max_rss_bytes` was observed as a constant single value (47431680) across every
  scrape taken — too few independent samples to confirm or rule out a memory-growth
  trend, though nothing else pointed to one.
