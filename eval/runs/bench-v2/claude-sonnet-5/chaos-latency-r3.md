---
konan_journal: 2
investigation:
  id: 2026-11-02-shop-wide-slowness
  trigger: manual
  complaint: "Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast."
  started: 2026-11-02T19:38:38Z
  concluded: 2026-11-02T19:51:22Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode, an internal degradation switch, was enabled on the target (extra_latency_ms=1500, failure_rate=0.0), injecting variable extra latency into business-route requests while leaving /health, /metrics, and error rates untouched."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "Chaos mode, an internal operational switch, was enabled at 2026-11-02T19:38:18.163Z (POST /chaos/enable, failure_rate=0.0, extra_latency_ms=1500) and from then injected variable, jittered extra latency into the business routes /products, /products/{product_id}, and /orders — observed durations ranged ~31ms to ~1.42s across 2xx responses on all three routes, roughly 100x to 1000x the ~1ms pre-toggle baseline — while /health and /metrics remained untouched at sub-3ms average and zero exceptions or non-2xx statuses were recorded on any of the three routes. This matches the complaint exactly: every shop page painfully slow, nothing errors, health checks green and fast."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17, E18, E19]
    evidence_against: [E5]
latent_findings:
  - statement: "GET /products/{product_id} raises an unhandled ZeroDivisionError and returns 500 for any product whose units_in_stock is 0 (reproduced twice, on product 3, 'Unobtainium Ingot'), because the handler divides units_ordered by units_in_stock unconditionally. Only the investigator's own two probes triggered it in this window — no non-investigator traffic touched this code path — so this is a latent defect, not part of the reported slowness incident."
    evidence: [E20, E21, E22, E23, E24]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:38:12.230Z"
    quote: '{"ts": "2026-11-02T19:38:12.230Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:38:12.988Z"
    quote: '{"ts": "2026-11-02T19:38:12.988Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "c69732865c1a", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.158, "client": "127.0.0.1:60627"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:38:18.163Z"
    quote: '{"ts": "2026-11-02T19:38:18.163Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "682e382602d1", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:38:20.905Z"
    quote: '{"ts": "2026-11-02T19:38:20.905Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "c1cf3e0f093e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 682.288, "client": "127.0.0.1:60631"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:42:06.291Z"
    quote: '{"ts": "2026-11-02T19:42:06.291Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793648526-2277", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 31.336, "client": "127.0.0.1:60673"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:45:06.451Z"
    quote: '{"ts": "2026-11-02T19:45:06.451Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "konan-1793648705-2341", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 483.67, "client": "127.0.0.1:60686"}'
  - id: E7
    type: metric
    source: "/metrics probe, request_id konan-1793648978-2472, 2026-11-02T19:49:38Z"
    quote: 'http_request_duration_seconds_sum{method="GET",path="/products"} 3.749417080776766 / http_request_duration_seconds_count{method="GET",path="/products"} 10'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:38:22.882Z"
    quote: '{"ts": "2026-11-02T19:38:22.882Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "a257a26df3e2", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 935.184, "client": "127.0.0.1:60632"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:38:24.170Z"
    quote: '{"ts": "2026-11-02T19:38:24.170Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "f892d4c0a2ce", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 226.124, "client": "127.0.0.1:60633"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:49:23.417Z"
    quote: '{"ts": "2026-11-02T19:49:23.417Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1793648962-2457", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1367.075, "client": "127.0.0.1:60706"}'
  - id: E11
    type: metric
    source: "/metrics probe, request_id konan-1793648978-2472, 2026-11-02T19:49:38Z"
    quote: 'http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 3.1516621271148324 / http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 6'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:38:26.321Z"
    quote: '{"ts": "2026-11-02T19:38:26.321Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "0b9808837d5a", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1085.441, "client": "127.0.0.1:60634"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:38:29.076Z"
    quote: '{"ts": "2026-11-02T19:38:29.076Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "e7e7ed89727b", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 321.791, "client": "127.0.0.1:60637"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:49:16.098Z"
    quote: '{"ts": "2026-11-02T19:49:16.098Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1793648954-2452", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1423.036, "client": "127.0.0.1:60703"}'
  - id: E15
    type: metric
    source: "/metrics probe, request_id konan-1793648978-2472, 2026-11-02T19:49:38Z"
    quote: 'http_request_duration_seconds_sum{method="GET",path="/orders"} 1.7448272081092 / count 2; http_request_duration_seconds_sum{method="POST",path="/orders"} 1.0873706673737615 / count 2'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:39:26.188Z"
    quote: '{"ts": "2026-11-02T19:39:26.188Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793648366-2151", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.456, "client": "127.0.0.1:60657"}'
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:45:16.466Z"
    quote: '{"ts": "2026-11-02T19:45:16.466Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793648716-2362", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.497, "client": "127.0.0.1:60691"}'
  - id: E18
    type: metric
    source: "/metrics probe, request_id konan-1793648978-2472, 2026-11-02T19:49:38Z"
    quote: 'http_request_duration_seconds_sum{method="GET",path="/health"} 0.014358375687152147 / http_request_duration_seconds_count{method="GET",path="/health"} 5'
  - id: E19
    type: metric
    source: "/metrics probe, request_id konan-1793648978-2472, 2026-11-02T19:49:38Z"
    quote: 'faultline_chaos_enabled 1'
  - id: E20
    type: metric
    source: "/metrics probe, request_id konan-1793648978-2472, 2026-11-02T19:49:38Z"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2 / http_exceptions_total{type="ZeroDivisionError"} 2'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:48:47.959Z"
    quote: 'unhandled exception: division by zero — File "faultline/shop.py", line 64, in get_product: "turnover_score": units_ordered / product["units_in_stock"] — ZeroDivisionError: division by zero (request_id konan-1793648927-2435)'
  - id: E22
    type: probe
    source: "/products probe, request_id konan-1793648526-2277"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:48:47.976Z"
    quote: '{"ts": "2026-11-02T19:48:47.976Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793648927-2435", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 612.155, "client": "127.0.0.1:60698"}'
  - id: E24
    type: log
    source: "lab/logs/app.log @ 2026-11-02T19:49:08.229Z"
    quote: '{"ts": "2026-11-02T19:49:08.229Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793648948-2447", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.119, "client": "127.0.0.1:60701"}'
gaps:
  - "Chaos mode could not be disabled to directly observe reversion to baseline latency: chaos-off is operator/eval-side only (scripts/scenario.sh), outside the investigator's read-only surface (docs/lab.md)."
  - "The exact latency-injection distribution (whether extra_latency_ms=1500 is a fixed cap for a random draw or some other formula) could not be confirmed from source code — deliberately outside the investigator's reach per the blinding contract. It was instead inferred from telemetry: 9 post-toggle /products samples (31–693ms) plus 5 more across /products/{product_id} and /orders (226–1423ms), all below the 1500ms cap, forming a stable skewed distribution rather than a flat per-request tax."
  - "/orders/{id} and /openapi.json were not probed; the three routes named in the hypothesis (/products, /products/{product_id}, /orders) were judged sufficient to represent 'every page' given the complaint's shape and the investigation budget."
  - "Whether the ZeroDivisionError latent defect has ever affected real user traffic is unknown — no non-investigator request touched a zero-stock product in the observed window, so its real-world impact could not be assessed from telemetry alone."
usage:
  model: claude-sonnet-5
  tokens: 6485960
  wall_clock_seconds: 764
---

# Shop-wide slowness traced to a chaos-mode latency switch

## Summary

**Root cause identified.** Chaos mode — an internal degradation switch on the faultline
target — was enabled at 19:38:18Z (`extra_latency_ms=1500`, `failure_rate=0.0`) shortly
before the process's own traffic began. From that point on, every business route
(`/products`, `/products/{product_id}`, `/orders`) returned correctly (status 2xx, no
exceptions) but with sharply elevated and jittered latency — individual requests ranging
from ~31ms to ~1.42s, against a ~1ms pre-toggle baseline — while `/health` and `/metrics`
stayed sub-3ms throughout. That is exactly the complaint: every shop page painfully slow,
nothing errors out, health checks green and fast. Confidence is high: three independent,
blind triage lenses converged on the same mechanism, and an adversarial judge validated
it only after evidence covered all three named routes and the one anomalous fast sample
was shown to sit inside a stable, strongly-skewed latency distribution rather than
contradicting it. One unrelated, genuine defect — a reproducible `ZeroDivisionError` on
`/products/{id}` for zero-stock products — surfaced during probing and is recorded
separately as a latent finding; it was triggered only by the investigator's own probes
and plays no part in this incident.

## Timeline

- **19:38:12.230Z** — faultline process starts (E1).
- **19:38:12.988Z** — pre-toggle baseline: `GET /products` in 1.158ms (E2).
- **19:38:18.163Z** — **configuration-change marker**: `POST /chaos/enable` logged as
  `event=chaos_enabled`, `failure_rate=0.0`, `extra_latency_ms=1500` (E3).
- **19:38:20.905Z onward** — business-route latency jumps immediately: `/products` 682ms
  (E4), `/products/2` 935ms (E8), `/products/1` 226ms (E9), `POST /orders` 1085ms (E12),
  `GET /orders` 322ms (E13) — while `/health` stays at 0.456ms (E16).
- **19:38:34Z** — human complaint received: "Users say every page in the shop got
  painfully slow in the last few minutes — nothing errors out, it just takes forever.
  Health checks are green and fast."
- **19:38:38Z** — investigation starts (trigger latency: 4s).
- **19:41–19:49Z** — targeted sampling across all three named routes confirms sustained,
  jittered elevation (E6, E7, E10, E11, E14, E15), chaos gauge still `1` (E19).
- **19:48:47.959Z** — an investigator probe to `/products/3` (zero stock, E22) surfaces
  an unrelated `ZeroDivisionError` (E21), reproduced at 19:49:08.226Z (E24) — orthogonal
  to the slowness incident.
- **19:51:22Z** — investigation concludes: root cause identified, one latent finding
  recorded.

## Investigation

**Baseline.** Read the surface contract (`docs/lab.md`); probed `/health` and
`/metrics`; read the log tail, which at that point covered the process's entire ~78s
lifetime.

**Triage.** Fanned out three lenses in parallel, each blind to the others, given only
the lens file, the surface contract, the complaint, and the baseline: `infra-process`,
`interfaces`, `software-defect`. `infra-process` and `interfaces` independently surfaced
the same `chaos_enabled` toggle as the anomaly — `interfaces` correctly deferred
classification to `infra-process` per its own internal-switch carve-out.
`software-defect` found zero exceptions and zero non-2xx statuses in its window and
reported no findings.

**Judge round 1.** Evidence for the chaos hypothesis was already deterministic from
triage, so per the loop's own rule it skipped a separate deep-dive subagent and went
straight to the judge. Verdict: **inconclusive** — one low-latency `/products` sample
(31ms, E5) appeared while the chaos gauge stayed on, and the judge asked whether the
injection was a flat per-request tax or probabilistic. Reading the injection's
implementation was proposed but is out of bounds (ground truth stays outside the
investigator's reach per the lab contract).

**Round 2 — targeted gathering.** Took a burst of 5 more `/products` probes: 4 of 5
landed in the 450–693ms range, one at 112ms — a stable, skewed distribution, not a
one-off. Re-judged: **inconclusive** again, this time because only `/products` had been
directly tested, while H1 names `/products/{product_id}` and `/orders` too.

**Round 3 — full coverage.** Probed `/products/{product_id}` (non-zero-stock products)
and `/orders` directly; combined with existing simulated-end-user-traffic evidence on
the same routes. One of these probes (`/products/3`) incidentally surfaced the
`ZeroDivisionError`, reproduced once more to confirm determinism, then set aside as a
latent finding. Final judge verdict: **validated** — all three routes show the same
signature (elevated, jittered, always 2xx, always below the 1500ms cap), and `/health`
stays sub-3ms across the entire window.

## Hypotheses

### H1 — chaos-mode latency injection (validated)

Chaos mode was enabled as an internal degradation switch, injecting variable latency
into the three business routes named in the complaint while leaving `/health`,
`/metrics`, and error rates untouched. **For:** the toggle marker itself (E3); sharp
onset immediately after it on all three routes (E4, E8, E9, E12, E13); sustained
elevation under continued sampling (E6, E10, E14) with metric aggregates confirming the
mean duration on every business route is two to three orders of magnitude above
`/health`'s (E7, E11, E15, E18); the chaos gauge staying `1` throughout (E19); zero
exceptions or non-2xx statuses on any of the three routes (consistent with
`failure_rate=0.0`). **Against:** one `/products` sample at 31ms (E5) while the gauge
was still `1` — examined directly; it sits inside a distribution of otherwise
112–935ms samples with no flat repeated value, consistent with jittered/probabilistic
injection rather than contradicting the switch's effect.

## Safe next steps

- Keep watching `faultline_chaos_enabled` and `http_request_duration_seconds` by route;
  this incident's signature (elevated business-route latency, flat `/health`, zero
  errors) is a known read on that dashboard going forward.
- Confirm, read-only, who or what enabled chaos mode at 19:38:18Z and whether/when it is
  scheduled to turn off — this investigation can observe the switch but not act on it.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and `GET
  /products/{product_id}` 500s on zero-stock products going forward, in case real user
  traffic starts hitting the latent defect found in this session.
- Do not modify the chaos switch or the `ZeroDivisionError` from here — remediation is
  out of scope for an investigation; file both as defects for their owning team.

## Gaps

- Chaos mode could not be disabled to directly observe reversion to baseline latency:
  chaos-off is operator/eval-side only (`scripts/scenario.sh`), outside the
  investigator's read-only surface.
- The exact latency-injection distribution could not be confirmed from source code,
  deliberately outside the investigator's reach per the blinding contract; it was
  instead inferred from 14 post-toggle samples across all three named routes, all below
  the configured 1500ms cap, forming a stable skewed distribution rather than a flat tax.
- `/orders/{id}` and `/openapi.json` were not probed; the three routes named in the
  hypothesis were judged sufficient to represent "every page" given the complaint's
  shape and the investigation budget.
- Whether the `ZeroDivisionError` latent defect has ever affected real user traffic is
  unknown — no non-investigator request touched a zero-stock product in the observed
  window.
