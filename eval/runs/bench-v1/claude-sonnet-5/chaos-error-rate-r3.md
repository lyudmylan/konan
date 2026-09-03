---
konan_journal: 1
investigation:
  id: 2026-08-18-chaos-mode-503s
  trigger: manual
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: "2026-08-18T22:40:37Z"
  concluded: "2026-08-18T22:46:00Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime chaos/fault-injection flag was flipped on via POST /chaos/enable at 2026-08-18T22:40:12.461Z (failure_rate=0.4, error_status=503), which makes the service return HTTP 503 on a random subset of requests to /products, /products/{id}, and /orders while /health stays unaffected; because injection is per-request rather than per-input, retrying the same route commonly succeeds."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos/fault-injection mode, enabled via POST /chaos/enable at 22:40:12.461Z (failure_rate=0.4, error_status=503, still active at conclusion), causes intermittent 503s on business routes (/products, /products/{id}, /orders) while /health is untouched; failures are per-request and probabilistic, so same-route retries frequently succeed. Fully explains the complaint's onset, retry-recovers-it shape, order failures, and green health dashboard."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11]
    evidence_against: []
  - id: H2
    statement: "The intermittent 5xx responses come from an unhandled software exception or a data-dependent code defect in the request-handling code, rather than injected degradation."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E12]
  - id: H3
    statement: "The intermittent 5xx responses come from process instability — a crash/restart loop, memory/resource saturation, or creeping latency — rather than the application layer."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E14, E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:40:12.461Z"
    quote: |-
      {"ts": "2026-08-18T22:40:12.461Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "c934e63c93fc", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:40:12.462Z (same request_id as E1)"
    quote: |-
      {"ts": "2026-08-18T22:40:12.462Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "c934e63c93fc", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 1.942, "client": "127.0.0.1:52630"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:40:15.581Z"
    quote: |-
      {"ts": "2026-08-18T22:40:15.581Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e1af6210781f", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-08-18T22:40:15.581Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "e1af6210781f", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.38, "client": "127.0.0.1:52633"}
  - id: E4
    type: log
    source: "lab/logs/app.log — /products/1 before (22:40:06.287Z) and after (22:40:21.900Z) the E3 failure"
    quote: |-
      {"ts": "2026-08-18T22:40:06.287Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "dee6d9173030", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.113, "client": "127.0.0.1:52626"}
      {"ts": "2026-08-18T22:40:21.900Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "12c13a8ab047", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.954, "client": "127.0.0.1:52640"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:40:18.732Z"
    quote: |-
      {"ts": "2026-08-18T22:40:18.732Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "6f8dd8b07f7f", "event": "chaos_failure", "method": "GET", "path": "/products"}
      {"ts": "2026-08-18T22:40:18.732Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "6f8dd8b07f7f", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.247, "client": "127.0.0.1:52636"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:42:17.722Z (independent re-probe during the interfaces-lens triage pass, request_id konan-1787092937-31557)"
    quote: |-
      {"ts": "2026-08-18T22:42:17.722Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1787092937-31557", "event": "chaos_failure", "method": "GET", "path": "/products"}
      {"ts": "2026-08-18T22:42:17.722Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "konan-1787092937-31557", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.234, "client": "127.0.0.1:52678"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:43:17.640Z (orchestrator probe of /orders, request_id konan-1787092997-31636)"
    quote: |-
      {"ts": "2026-08-18T22:43:17.640Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1787092997-31636", "event": "chaos_failure", "method": "GET", "path": "/orders"}
      {"ts": "2026-08-18T22:43:17.641Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "konan-1787092997-31636", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.319, "client": "127.0.0.1:52686"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:43:20.095Z (retry, request_id konan-1787093000-31642, ~2.5s after E7, same route)"
    quote: |-
      {"ts": "2026-08-18T22:43:20.095Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "konan-1787093000-31642", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.435, "client": "127.0.0.1:52687"}
  - id: E9
    type: metric
    source: "probe /metrics, request_id=konan-1787093091-31675 @ 2026-08-18T22:44:51Z (final scrape, process_uptime_seconds 287.06 — over 4.5 minutes after the E1 trigger)"
    quote: |-
      faultline_chaos_enabled 1
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products",status="503"} 2
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/orders",status="200"} 2
      http_requests_total{method="GET",path="/orders",status="503"} 1
      process_uptime_seconds 287.06497954088263
      process_max_rss_bytes 46579712
  - id: E10
    type: probe
    source: "probe /health, request_id=konan-1787092866-31418 @ 2026-08-18T22:41:06Z (baseline, ~54s after E1)"
    quote: |-
      {"status":"ok","uptime_seconds":62.54120620782487} -- HTTP 200 in 0.001471s
  - id: E11
    type: log
    source: "lab/logs/app.log — all 5 access lines matching path \"/health\" across the full log (grep -c confirms 5/5, first and last shown)"
    quote: |-
      {"ts": "2026-08-18T22:40:05.206Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "715f2433655c", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 11.648, "client": "127.0.0.1:52623"}
      {"ts": "2026-08-18T22:42:23.363Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1787092943-31588", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.419, "client": "127.0.0.1:52681"}
  - id: E12
    type: metric
    source: "probe /metrics, request_id=konan-1787093091-31675 @ 2026-08-18T22:44:51Z (http_exceptions_total series block, scraped in full — no series line follows the TYPE header)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E13
    type: log
    source: "full read of lab/logs/app.log — the only event:startup line"
    quote: |-
      {"ts": "2026-08-18T22:40:04.465Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E14
    type: metric
    source: "probe /metrics, request_id=konan-1787092868-31424 @ 2026-08-18T22:41:08Z (baseline scrape, first reading taken)"
    quote: |-
      process_uptime_seconds 64.48460733285174
      process_max_rss_bytes 46579712
gaps:
  - "The caller of POST /chaos/enable is not attributable from telemetry: the access log (E2) carries no auth/actor/identity field, so whether this was an operator action, an automated trigger, or a scheduled job cannot be determined from the surface contract's telemetry alone."
  - "The empirical failure ratio was not measured at high sample size. By conclusion, business-route (non-investigator-baseline) requests showed roughly 4 failures out of ~14 samples (E9) — directionally consistent with the configured failure_rate=0.4 (E1) but too small a sample to confirm the rate statistically; no counter separates the configured rate from an observed one."
  - "POST /orders (order creation) itself was not observed to fail during this investigation — all 3 creation attempts across the whole log succeeded. Whether chaos injection applies symmetrically to the write path, or the sample was simply too small to catch it, is not resolved from available evidence."
  - "extra_latency_ms is configured at 0 (E1); latency-only degradation (slow but non-erroring responses) was not separately probed for, since duration_ms values observed on both successes and chaos failures stayed sub-2ms throughout."
usage:
  model: claude-sonnet-5
  tokens: 3341568
  wall_clock_seconds: 323
---

# Intermittent 503s on /products and /orders — chaos mode enabled mid-session

## Summary

**Root cause identified.** A runtime chaos/fault-injection flag was switched on via
`POST /chaos/enable` at `2026-08-18T22:40:12.461Z`, configured with `failure_rate=0.4`
and `error_status=503` (E1). From that moment, the service began returning HTTP 503 on
a randomly-selected subset of requests to `/products`, `/products/{id}`, and `/orders`
(E3, E5, E7), while leaving the same routes' other requests, and `/health` entirely,
unaffected (E4, E9, E10, E11). Because the injection is applied per-request rather than
per-input, a same-route retry frequently succeeds (E4, E8) — matching the complaint's
"work again on retry" shape exactly. This fully explains the reported symptoms: sudden
onset a few minutes before the report, intermittent page-load and order failures, and a
green health dashboard (chaos never touches `/health`). The condition was still active
at the time of writing (E9) — chaos mode has not been disabled since E1, and no
`chaos_disabled` event appears anywhere in the log.

No unhandled exceptions, no restart, and no resource saturation were found (E12, E13,
E14, E9) — the two alternative hypotheses tested (software defect, process
instability) are both invalidated.

## Timeline

- `22:40:04.465Z` — process startup, single `event: startup` line, no restarts
  afterward (E13).
- `22:40:12.461Z` — **trigger**: `chaos_enabled` flag flip, `failure_rate=0.4`,
  `error_status=503` (E1), immediately preceded by `POST /chaos/enable -> 200` on the
  same request id (E2).
- `22:40:15.581Z` — first chaos-injected failure, `GET /products/1 -> 503` (E3),
  sandwiched between successful `GET /products/1` calls at `22:40:06.287Z` and
  `22:40:21.900Z` (E4) — same route and input, alternating outcomes.
- `22:40:18.732Z` — second chaos-injected failure, `GET /products -> 503` (E5).
- `22:40:30Z` — complaint received (`startsAt`), ~18s after the trigger.
- `22:40:37Z` — investigation loop entered (trigger latency ~7s).
- `22:42:17Z` — live re-probe during triage confirms chaos still injecting failures on
  `/products` (E6).
- `22:43:17.640Z` — orchestrator probe confirms `/orders` is also affected:
  `GET /orders -> 503` (E7).
- `22:43:20.095Z` — retry on `/orders` ~2.5s later succeeds (E8), same route.
- `22:44:51Z` — final metrics read: `faultline_chaos_enabled 1`, still on, over 4.5
  minutes after the trigger (E9).

## Investigation

1. **Baseline** — `/health` (E10) and `/metrics` snapshot taken first; the metrics
   snapshot already showed `faultline_chaos_enabled 1` and mixed 200/503 counts on
   `/products*`, and the log tail already contained the `chaos_enabled` marker (E1) and
   two `chaos_failure` events (E3, E5) — a strong lead before triage even started.
2. **Triage** — three lenses spawned in parallel, each blind to the others, given only
   the lens file, `docs/lab.md`, the complaint verbatim, and the baseline summary:
   - *infra-process*: no anomalies — clean single startup, flat RSS, no latency
     degradation, `/health` never flapped.
   - *interfaces*: found the decisive evidence — the config-change marker (E1)
     immediately followed by degraded behavior, a stable-shaped probabilistic failure
     rate, and independently re-confirmed the condition was still live with its own
     probe (E6).
   - *software-defect*: no anomalies — zero exceptions, zero stack traces, and the
     same input (`/products/1`) both succeeded and failed, ruling out a deterministic
     per-input defect.
   All three lenses converged on the same mechanism without seeing each other's work.
3. **Deep-dive** — skipped for H1: the triage evidence for the config-change mechanism
   was already deterministic (an explicit log marker naming the exact flip, matched
   `request_id` to `chaos_failure` events, live reproducibility). Per protocol, a
   hypothesis whose triage evidence is already deterministic and complete goes straight
   to the judge. Before doing so, the orchestrator probed `/orders` directly (E7, E8)
   to confirm the complaint's "orders error out" clause, since triage evidence so far
   only covered `/products*`.
4. **Judge** — one adversarial judge, given only the hypothesis statement and the
   verbatim cited evidence (no narrative). Verdict: **validated** for the causal
   mechanism. The judge flagged two claims that outran the evidence as originally
   worded: an unsupported precise "~40% observed rate" and an unsupported "operator
   action" attribution (no actor/identity field in the access log). Both were corrected
   in this journal's hypothesis wording and moved to Gaps rather than asserted as fact.

## Hypotheses

### H1 — chaos mode enabled, causing intermittent 503s (validated)

Evidence for: E1–E11. The config-change marker (E1) is followed within ~3s by the
first matching failure (E3, same causal chain via shared `request_id` pattern across
E3/E5/E7). The failure is spread across three different routes (`/products`,
`/products/1`, `/orders`), not concentrated on one — a gateway/injection shape, not a
single code path. `/health` is never touched (E10, E11). The condition persisted,
unchanged, for the full 4.5-minute investigation window (E9) with no `chaos_disabled`
marker ever appearing.

### H2 — software defect (invalidated)

Evidence against: E3, E4, E12. The same input (`/products/1`) alternates between
success and failure (E3/E4) — a deterministic code defect would fail that input
consistently, not intermittently. `http_exceptions_total` carries zero recorded
exception types across the whole investigation (E12), and no `unhandled_exception`
event or stack trace appears anywhere in the log.

### H3 — process instability (invalidated)

Evidence against: E13, E14, E9. Exactly one startup event, ever (E13).
`process_uptime_seconds` moves from `64.48` at the baseline scrape (E14) to `287.06` at
the final scrape (E9) — consistent with elapsed wall-clock time (~223s of real time
passed between the two probes), not a reset. `process_max_rss_bytes` is identical
(`46579712`) at both the baseline (E14) and final (E9) scrape — flat, no leak, no
saturation. Response durations stayed sub-2ms on both successes and chaos-injected
failures throughout, ruling out latency-based degradation as well.

## Safe next steps

- Re-probe `/metrics` periodically (read-only) to confirm whether `faultline_chaos_enabled`
  eventually returns to `0` on its own, or whether it requires an explicit operator
  action to clear.
- If this were a real production target (not the lab), the next read-only step would be
  pulling the calling identity/audit trail for whatever issued the `POST
  /chaos/enable`-equivalent config change, from whatever system owns that config —
  outside this investigation's surface contract here.
- Continue monitoring `/orders` and `/products*` access logs for the failure pattern to
  confirm it stays confined to those routes and does not spread.

## Gaps

- The caller of `POST /chaos/enable` is not attributable from telemetry — the access
  log carries no auth/actor/identity field on that request, so whether this was a
  human operator, an automated job, or something else cannot be determined from the
  surface contract's telemetry alone.
- The empirical failure ratio was not measured at high sample size — roughly 4 failures
  out of ~14 non-baseline business-route samples by conclusion (E9), directionally
  consistent with the configured `failure_rate=0.4` (E1) but not a statistically
  confirmed observed rate.
- `POST /orders` (order creation) itself was never observed to fail in this
  investigation (3/3 succeeded) — whether the write path is subject to the same
  injection, or the sample was simply too small to catch it, is unresolved.
- Latency-only degradation was not separately probed for; all observed durations
  (successes and failures alike) stayed sub-2ms, consistent with the configured
  `extra_latency_ms=0` (E1), but this wasn't independently stress-tested.
