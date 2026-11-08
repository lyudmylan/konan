---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-flag-injected-503s
  trigger: 'manual — /konan adapter (source: human, fingerprint: human-1787110860, alertname: human-report, startsAt 2026-08-19T03:41:00Z; investigation started 2026-08-19T03:41:06Z, trigger latency 6s)'
  complaint: 'Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green.'
  started: 2026-08-19T03:41:06Z
  concluded: 2026-08-19T03:49:54Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'A runtime fault-injection flag was enabled on faultline at 2026-08-19T03:40:42.465Z with failure_rate 0.4 and error_status 503, so request middleware now rejects a random share of shop requests with 503 before the route handler runs.'
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: 'Chaos/fault-injection mode was enabled at 2026-08-19T03:40:42.465Z (failure_rate 0.4, error_status 503, extra_latency_ms 0); it injects 503s per-request across shop routes, which produces intermittent failures that succeed on retry.'
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E12]
    evidence_against: []
  - id: H2
    statement: 'The /health endpoint is outside the injection path and samples no shop-route error rate, so it returns 200 during the same window in which shop routes return 503 — the reported green dashboard is a monitoring blind spot, not evidence of health.'
    incident_class: interfaces
    state: validated
    evidence_for: [E8, E10, E11]
    evidence_against: []
  - id: H3
    statement: 'The reported intermittent failures are caused by a data-dependent code defect on the product-detail route (ZeroDivisionError when units_in_stock is 0).'
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E5, E6, E12, E14, E15]
latent_findings:
  - statement: 'GET /products/{id} divides units_ordered by units_in_stock, so product 3 (units_in_stock 0) raises ZeroDivisionError and returns HTTP 500. Deterministic per input. Only investigator probes triggered it: no non-investigator request reached /products/3 in this process life, and the exception counter equals exactly the two konan-attributed exceptions. A user finds this whenever a product goes out of stock.'
    evidence: [E13, E14, E15]
  - statement: 'http_requests_total records the raw path for injection-rejected requests but the templated path for handler-served ones, so no single label set carries the true success/failure ratio of the product-detail route, and raw-path labels grow unbounded with product id (cardinality risk).'
    evidence: [E16]
evidence:
  - id: E1
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:40:42.465Z'
    quote: '{"ts": "2026-08-19T03:40:42.465Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "4feee85382b1", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:40:44.522Z'
    quote: '{"ts": "2026-08-19T03:40:44.522Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "cc798f60f022", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E3
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:40:44.523Z'
    quote: '{"ts": "2026-08-19T03:40:44.523Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "cc798f60f022", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.277, "client": "127.0.0.1:55767"}'
  - id: E4
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:40:39.407Z (last known-good user request before the marker)'
    quote: '{"ts": "2026-08-19T03:40:39.407Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "e777e4acbe48", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.796, "client": "127.0.0.1:55764"}'
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:40:45.580Z'
    quote: '{"ts": "2026-08-19T03:40:45.580Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "26a6f6998402", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.841, "client": "127.0.0.1:55768"}'
  - id: E6
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:40:51.902Z'
    quote: '{"ts": "2026-08-19T03:40:51.902Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "1b311450d130", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.28, "client": "127.0.0.1:55775"}'
  - id: E7
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:40:52.959Z'
    quote: '{"ts": "2026-08-19T03:40:52.959Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "83ed46a8f7ae", "event": "chaos_failure", "method": "GET", "path": "/orders"}'
  - id: E8
    type: metric
    source: '/metrics via probe konan-1787111387-42845'
    quote: 'faultline_chaos_enabled 1'
  - id: E9
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:40:34.264Z (only startup marker in the file; no rotated backups exist)'
    quote: '{"ts": "2026-08-19T03:40:34.264Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E10
    type: probe
    source: '/health via probe konan-1787110876-42358 @ 2026-08-19T03:41:16.547Z (34s after the marker, chaos active)'
    quote: '{"status":"ok","uptime_seconds":42.294038499938324}  -- HTTP 200 in 0.002943s request_id=konan-1787110876-42358'
  - id: E11
    type: metric
    source: '/metrics via probe konan-1787111387-42845'
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 18 — with no non-200 /health series at all, beside http_requests_total{method="GET",path="/products",status="503"} 7, {method="GET",path="/orders",status="503"} 2, {method="GET",path="/products/1",status="503"} 3'
  - id: E12
    type: metric
    source: '/metrics via probe konan-1787110877-42364 (baseline scrape, after all user traffic)'
    quote: '# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter — followed by no series at all (zero unhandled exceptions during the entire user-traffic window)'
  - id: E13
    type: probe
    source: '/products/3 via probe konan-1787110977-42569'
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787110977-42569"}'
  - id: E14
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T03:42:57.310Z (stack trimmed to its final frames)'
    quote: '{"ts": "2026-08-19T03:42:57.310Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787110977-42569", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}'
  - id: E15
    type: metric
    source: '/metrics via probe konan-1787111387-42845 (was empty at baseline, E12)'
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 2'
  - id: E16
    type: metric
    source: '/metrics via probe konan-1787111387-42845'
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="200"} 9 and http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2, alongside http_requests_total{method="GET",path="/products/1",status="503"} 3, {method="GET",path="/products/3",status="503"} 1, {method="GET",path="/products/4",status="503"} 1 — no {path="/products/{product_id}",status="503"} series exists'
gaps:
  - 'Who enabled the flag, and whether it was authorized, is unverifiable from telemetry: the marker names request_id 4feee85382b1 from client 127.0.0.1:55766, but /chaos is operator surface outside the probe allowlist, so the actor and intent cannot be read.'
  - 'No dashboard, alert rule, or monitor configuration exists on the readable surface. "The dashboard is green" is corroborated only by /health returning 200 throughout (E10, E11); the monitor itself was never inspected.'
  - 'The user-traffic sample is small: 10 non-investigator shop requests after the marker, 5 of which failed (50%). That cannot statistically distinguish the configured failure_rate 0.4 from nearby rates; the rate is taken from the marker (E1), not inferred from counts.'
  - 'Logs cover only this process life (startup 03:40:34.264Z, E9) and no rotated app.log.1-.3 backups exist, so no state before that instant is knowable. The /products/3 defect is therefore "unhit in the observed window", not "never hit".'
  - 'Investigator probes contaminated the counters: both ZeroDivisionError exceptions (E15) and much of the later /health, /products and /metrics volume are konan-generated. Metric totals in this journal must not be read as user impact.'
  - 'Chaos remained enabled at conclusion (E8); the incident was still active when this journal was written, so no recovery or duration-of-impact figure is available.'
usage:
  model: claude-opus-5
  tokens: 2261572
  wall_clock_seconds: 528
---

# Intermittent shop 503s from an enabled fault-injection flag

## Summary

**Root cause identified.** A runtime fault-injection ("chaos") flag was enabled on faultline
at 2026-08-19T03:40:42.465Z with `failure_rate: 0.4`, `error_status: 503`,
`extra_latency_ms: 0` (E1). Since that instant the request middleware rejects a random
share of shop requests with HTTP 503 *before* the route handler runs — each rejection is
logged as `chaos_failure` and paired with the 503 access line under the same request id
(E2, E3). Because the choice is made per request rather than per input, the same URL
returns 200 and 503 seconds apart (E5, E6), which is exactly the reported "errors out,
then works again on retry".

Impact is user-visible and ongoing. Every user request before the marker succeeded; of the
10 non-investigator shop requests after it, 5 failed (50%) across four distinct routes —
`/products`, `/products/1`, `/products/4` and `/orders` — so both browsing and order
retrieval are affected. The flag was still enabled when this investigation concluded (E8).

The green dashboard is explained and is not reassuring: `/health` sits outside the
injection path and reports only liveness and uptime, so it answered 200 in the same seconds
that shop routes answered 503 (E10, E11). This is the healthy-monitoring trap — health was
never evidence that the shop worked.

Confidence is high, and it does not rest on inference: the injector names itself in the
logs, states its own configuration, and labels every failure it causes. Two independent
findings surfaced along the way and are recorded as latent, not as this incident.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 03:40:34.264 | faultline 0.1.0 starts. Single startup marker; no restart anywhere in the window. | E9 |
| 03:40:34.999 – 03:40:39.407 | Baseline user traffic: 6 requests, all 200/201. Zero failures. Last known-good is `GET /products/2 -> 200`. | E4 |
| **03:40:42.465** | **Configuration change marker — `chaos_enabled`, `failure_rate: 0.4`, `error_status: 503`.** | **E1** |
| 03:40:44.522 | First injected failure, 2.06s after the marker: `chaos_failure` on `GET /products`, then 503 under the same request id. | E2, E3 |
| 03:40:45.580 | `GET /products/1 -> 200` — a success on a route that fails moments later. | E5 |
| 03:40:51.902 | `GET /products/1 -> 503` — same input, opposite outcome. Per-request, not per-input. | E6 |
| 03:40:52.959 | `chaos_failure` on `GET /orders` — the ordering surface is affected too. | E7 |
| 03:41:06 | Investigation starts; complaint received 03:41:00 (trigger latency 6s). | — |
| 03:41:16.547 | `/health` answers 200 while chaos is active — the green dashboard, reproduced. | E10 |
| 03:42:57.310 | Investigator probe of `/products/3` raises ZeroDivisionError (latent defect, konan-caused). | E13, E14 |
| 03:49:54 | Conclusion. `faultline_chaos_enabled 1` — still active. | E8 |

## Investigation

**Baseline.** `/health` 200 with 42s uptime, `/metrics`, and the 33-line log tail. Two
things stood out immediately: `faultline_chaos_enabled 1` with a `POST /chaos/enable` in the
counters, and `http_exceptions_total` completely empty (E12) — 5xx responses without a
single exception, which already argued against a crashing code path.

**Triage — three lenses in parallel, each blind to the others.** The obvious cause was
visible in the baseline, but the loop runs triage anyway because secondary causes hide
behind obvious ones; that discipline is what produced the two latent findings.

- *infra-process*: domain clean. One startup only, uptime monotonic (42.83 → 122.48s), flat
  peak RSS across four scrapes, no unhandled exceptions, and the 503s were the *fastest*
  requests in the file (0.27ms) — fail-fast, not timeouts. Explicitly handed the 503 pattern
  onward. It did flag the health-coverage gap.
- *interfaces*: found the change marker and built the onset timeline (last-good 03:40:39.407,
  first-bad 03:40:44.522), showed the same input yielding both outcomes, and noted every 503
  carries a `chaos_failure` line.
- *software-defect*: independently ruled the reported symptom *out* of its own domain
  (spread across routes, non-deterministic, no exceptions) — and while probing found a
  genuine, unrelated defect on `/products/3`, plus a metrics labelling bug.

**Deep-dive: skipped, deliberately.** Per the loop, a hypothesis whose triage evidence is
already deterministic and complete goes straight to the judge. The injector logs its own
configuration and labels each failure it causes; there was no evidence gap left to fill, and
re-proving it would have been ceremony.

**Judge (adversarial, evidence-only).** The judge took the claims without the narrative and
pushed back usefully on three of four:

- It **struck a contaminated evidence item**. A lens had computed "8 failures / 20 shop
  requests = 40.0%, exactly matching `failure_rate: 0.4`". That match was an artifact of
  pooling konan's own probes with user traffic at one moment. The user-only figure is 5/10 =
  50%, and at n=10 the interval is far too wide to identify 0.4 anyway. The seductive
  "exactly matches" number is gone from this journal; the rate is cited from the marker.
- It **corrected a count**: 6 pre-marker user requests, not 7 (one line was an
  `order_created` sharing a request id with its access line).
- It **refused an unevidenced clause**. "The dashboard reads green" is imported from the
  complaint — no monitor configuration is on the readable surface. H2 is stated only as what
  was observed. It also noted the original `/health` evidence was too thin on its own (4
  post-marker 200s survive 40% injection ~13% of the time by chance) and verified with 12
  further probes: 16 consecutive post-marker `/health` 200s, ~3e-4 by chance.
- It **scoped the latent claim**: "only investigator probes *ever* hit it" is not knowable
  from a 380-second process life, so the claim is now bounded to the observed window.

H1 was validated; H3 — the reported failures as a code defect — was killed. The judge's
corrections are reflected in the machine core above.

## Hypotheses

### H1 — fault-injection flag (validated) → root cause

The marker states the mechanism and its parameters in its own words (E1), the first injected
failure lands 2.06s later (E2, E3), and nothing failed in the 4.4 seconds of traffic before
it (E4). The prediction that separates injection from a code defect — *probabilistic per
request, not deterministic per input* — holds directly: `/products/1` returned 200 at
03:40:45.580 and 503 at 03:40:51.902 (E5, E6). Failures spread over four routes including
`/orders` (E7), and no unhandled exception accompanies any of them (E12), which is what an
edge rejection looks like and is not what a failing handler looks like. The gauge confirms
the state persists (E8).

### H2 — health endpoint blind spot (validated, as scoped)

`/health` returned 200 at 03:41:16.547, 34 seconds after injection began (E10), and the
counters show no non-200 health result at all while shop routes accumulated 503s (E11). The
endpoint reports liveness and uptime only; it samples no shop-route error rate. The judge
verified non-injection with 16 consecutive post-marker successes. Stated narrowly: `/health`
stays 200 during shop-route failure. Whether the customer's dashboard consumes `/health` is
outside the readable surface and is recorded as a gap.

### H3 — data-dependent code defect as the reported cause (invalidated)

Worth testing, because a real defect of this shape does exist here — which is exactly why it
needed killing rather than assuming. It fails as an explanation of the complaint on four
counts: the user-visible failures are 503 with no exception recorded (E12), each is preceded
by a `chaos_failure` line naming the injector (E2, E3), the same input produced both success
and failure (E5, E6), and the only exceptions in the process life are two ZeroDivisionErrors
raised by konan's own probes (E14, E15) — never by user traffic. The defect is real but it is
a **latent finding**, not this incident. Recording it as the cause would have been a false
attribution of a genuinely broken thing.

## Safe next steps

All read-only; remediation is out of scope for this journal.

1. **Confirm the flag's origin with whoever holds operator access.** The marker carries
   request_id `4feee85382b1` from client `127.0.0.1:55766` (E1). Ask first whether this was
   an intended exercise — a running chaos experiment and an unauthorized toggle look
   identical from telemetry, and only the operator side can tell them apart. It is still
   enabled (E8).
2. **Check what the health dashboard actually polls.** If it polls `/health` alone, this
   class of incident is invisible to it by construction (E10, E11). Consider whether a
   business-surface check belongs in the monitor.
3. **Hand the `/products/3` defect to the owning team** (E13, E14). It is deterministic and
   customer-facing the moment any product reaches zero stock — independent of this incident.
   Note `/products/4` also returns `"price": null`, same route, same data-hazard class,
   observed but not seen to fail.
4. **Note the metrics labelling split** (E16): per-route error ratios cannot be read off
   `http_requests_total` today, and raw-path labels grow with product id.
5. **Re-baseline once the flag is off** to confirm the shop error rate returns to zero, and
   to distinguish any residual failures from injected ones.

## Gaps

The frontmatter list, in brief: the flag's *author and intent* are unreachable because
`/chaos` is operator surface, not telemetry; the *monitor itself* was never inspected, so the
complaint's "dashboard is green" is corroborated only by `/health` behaviour; the *user
sample is small* (10 post-marker requests), so the observed 50% is not a measurement of the
configured 0.4 and is not used as one; *no history exists before 03:40:34.264Z* because the
log holds one process life with no rotated backups, which bounds the latent finding to the
observed window; *investigator probes contaminated the counters*, including both
ZeroDivisionErrors, so metric totals here are not user impact; and the *incident was still
active at conclusion*, so no duration-of-impact figure exists.

Nothing in this list blocks the root-cause verdict — H1 rests on the injector's own logged
configuration and its per-failure labelling, none of which depends on the unreachable items.
