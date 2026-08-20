---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-latency-chaos-toggle
  trigger: manual (human report via /konan, fingerprint human-1787093392)
  complaint: |-
    Users say every page in the shop got painfully slow in the last few minutes — nothing errors out, it just takes forever. Health checks are green and fast.
  started: "2026-08-18T22:49:57Z"
  concluded: "2026-08-18T22:55:41Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode was enabled on the target (extra_latency_ms=1500, failure_rate=0.0), injecting added latency into every business route (/products, /products/{id}, /orders) while leaving health/metrics endpoints and error rates untouched."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode was enabled on the target (chaos_enabled event, extra_latency_ms=1500, failure_rate=0.0) shortly before the complaint, injecting added latency into business routes (/products, /products/{id}, /orders) while leaving health/metrics endpoints and error rates unaffected — matching \"painfully slow, nothing errors, health checks green\" exactly."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E10, E11]
    evidence_against: []
  - id: H2
    statement: "An unhandled application exception or code-level defect in specific business logic is causing the slowness."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E3, E4, E5]
  - id: H3
    statement: "Process-level resource saturation (memory growth, thread/worker starvation) or a restart loop is causing the slowdown."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E9]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:49:34.290Z"
    quote: '{"ts": "2026-08-18T22:49:34.290Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "03775a2cc889", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:49:31.224Z — last fast business-route request before the chaos_enabled marker"
    quote: '{"ts": "2026-08-18T22:49:31.224Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "89f636d79850", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.713, "client": "127.0.0.1:52730"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:49:37.164Z — first request after the marker"
    quote: '{"ts": "2026-08-18T22:49:37.164Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "cbba8693d492", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 814.269, "client": "127.0.0.1:52732"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:49:40.931Z"
    quote: '{"ts": "2026-08-18T22:49:40.931Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "50d876970183", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1208.959, "client": "127.0.0.1:52735"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:49:46.419Z"
    quote: '{"ts": "2026-08-18T22:49:46.419Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "cb5226619a76", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 793.395, "client": "127.0.0.1:52739"}'
  - id: E6
    type: probe
    source: "/health @ request_id konan-1787093447-32046 (2026-08-18T22:50:47.986Z, ~74s after the chaos_enabled marker)"
    quote: |-
      {"status":"ok","uptime_seconds":79.58823966700584}
      -- HTTP 200 in 0.001631s request_id=konan-1787093447-32046
  - id: E7
    type: probe
    source: "/metrics @ request_id konan-1787093448-32052 (2026-08-18T22:50:48.041Z)"
    quote: -- HTTP 200 in 0.001534s request_id=konan-1787093448-32052
  - id: E8
    type: metric
    source: "/metrics scrapes @ request_id konan-1787093448-32052 and konan-1787093580-32171 — no series line ever follows this header in either scrape"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E9
    type: metric
    source: "two /metrics scrapes ~132s apart: request_id konan-1787093448-32052 vs konan-1787093580-32171"
    quote: |-
      process_uptime_seconds 79.64308662503026 / process_max_rss_bytes 47120384
      process_uptime_seconds 211.95736745884642 / process_max_rss_bytes 47120384
  - id: E10
    type: metric
    source: "/metrics @ request_id konan-1787093580-32171 (2026-08-18T22:53:00Z, current state)"
    quote: faultline_chaos_enabled 1
  - id: E11
    type: metric
    source: "/metrics @ request_id konan-1787093580-32171 — same scrape, health vs. products duration summaries"
    quote: |-
      http_request_duration_seconds_sum{method="GET",path="/health"} 0.010386875830590725
      http_request_duration_seconds_count{method="GET",path="/health"} 4
      http_request_duration_seconds_sum{method="GET",path="/products"} 1.6007195010315627
      http_request_duration_seconds_count{method="GET",path="/products"} 3
gaps:
  - "No tracing/profiling surface exists in this lab (docs/lab.md's metric list has no per-handler timing breakdown), so a silent non-exception-raising code defect inside the business-route handlers cannot be fully ruled out independent of the chaos flag — only the exception-based reading of H2 is directly refuted by E8."
  - "No worker-pool/queue-depth metric exists on the surface, so the thread/worker-starvation clause of H3 is untested rather than refuted — only the restart-loop and memory-growth clauses are refuted by E9."
  - "The configured extra_latency_ms (1500) does not exactly match the observed per-request durations (793-1209ms); the chaos middleware's precise latency-injection semantics (flat add vs. jittered ceiling) are not documented on the investigator's surface, so the magnitude match to H1 is qualitative, not exact."
  - "faultline_chaos_enabled was still 1 at conclusion — the injected latency was not observed to self-resolve during this investigation's window; whether/when it clears was not tracked further."
usage:
  model: claude-sonnet-5
  tokens: 2237648
  wall_clock_seconds: 344
---

# Shop-wide latency spike traced to a chaos-mode latency injection, not an error-producing fault

## Summary

**Root cause identified.** At 2026-08-18T22:49:34.290Z the target's chaos mode was enabled
with `extra_latency_ms=1500` and `failure_rate=0.0` (E1). Every business-route request after
that instant — `/products`, `/products/{id}`, `/orders` — ran 793-1209ms instead of the
1-2ms seen immediately before (E2-E5), while `/health` and `/metrics` kept responding in
~0.5-1.6ms throughout (E6, E7, E11) and zero exceptions were ever recorded (E8). This is
exactly the reported shape: everything in the shop is painfully slow, nothing 500s, and
health checks stay green and fast. Confidence is high — three independent lenses converged
on the same marker, and the adversarial judge validated H1 while invalidating the
alternative code-defect and resource-saturation explanations. `faultline_chaos_enabled` was
still `1` at the end of this investigation (E10) — the injected latency has not self-resolved.

## Timeline (UTC)

- `22:49:28.410Z` — process startup, single `startup` event, no restarts since (ties to H3).
- `22:49:31.224Z` — last fast business request: `POST /orders` in 1.713ms (E2).
- `22:49:34.290Z` — **`chaos_enabled`**: `extra_latency_ms=1500`, `failure_rate=0.0` (E1) — the
  onset marker.
- `22:49:37.164Z` — first slow request after the marker: `GET /products` in 814.269ms (E3).
- `22:49:40.931Z`, `22:49:46.419Z` — further slow requests on different routes, 1208.959ms
  and 793.395ms respectively (E4, E5) — confirms the slowdown spans routes, not one input.
- `22:50:47.986Z` / `22:50:48.041Z` — investigator `/health` and `/metrics` probes, both
  sub-2ms during the incident window (E6, E7).
- `22:53:00Z` (probe request_id `konan-1787093580-32171`) — `faultline_chaos_enabled 1`
  still set (E10); `process_uptime_seconds` continuous at 211.96s with `process_max_rss_bytes`
  unchanged at 47120384 vs. an earlier scrape at 79.64s (E9) — process never restarted or
  grew memory.

## Investigation

1. **Baseline** — `/health` and `/metrics` probes fast; log tail already showed the
   `chaos_enabled` marker and the before/after duration jump.
2. **Triage, three lenses in parallel** (software-defect, infra-process, interfaces), each
   given only the lens file, `docs/lab.md`, the complaint, and the baseline summary:
   - *software-defect*: no exceptions anywhere, no data-dependent single-route/input
     pattern — reported nothing in its domain.
   - *infra-process*: process alive, uptime monotonic, RSS flat; flagged the latency
     split (health fast, business routes slow) but attributed the marker itself as an
     interfaces-domain event.
   - *interfaces*: identified `chaos_enabled` as a config/flag-change marker, confirmed
     sharp onset (fast until 22:49:31, slow from 22:49:37), and confirmed the effect was
     deterministic and route-scoped (100% of post-marker business requests slow, no mix
     of fast ones, no 5xx).
   All three converged on the same event with no contradicting evidence — triage evidence
   was deterministic and complete, so no separate deep-dive round was needed.
3. **Judge** — a fresh subagent, given only the hypothesis list and verbatim evidence
   (no narrative), validated H1 and invalidated H2/H3, flagging two residual gaps (silent
   non-exception defect not fully excluded; thread/worker starvation untested) — folded
   into Gaps below.

## Hypotheses

### H1 — chaos-mode latency injection (validated)

The `chaos_enabled` marker (E1) sits exactly between the last fast request (E2) and the
first slow one (E3); every subsequent business-route request across three different
routes stayed slow (E3-E5) while health/metrics stayed fast throughout (E6, E7, E11), and
`failure_rate=0.0` matches the observed zero-exception, all-200s pattern (E8). Still
active at conclusion (E10). No evidence contradicts it.

### H2 — application exception / code defect (invalidated)

`http_exceptions_total` carries no series in any scrape taken (E8), and the slow requests
all returned 200/201 (E3-E5) rather than 500 — the opposite of the data-dependent,
per-input failure shape this lens looks for. Not fully closed: a silent, non-exception
defect (e.g. an inefficient computation) would look identical on this surface; see Gaps.

### H3 — resource saturation / restart loop (invalidated)

`process_uptime_seconds` climbed monotonically (79.64s -> 211.96s) with no reset, and
`process_max_rss_bytes` was identical across both scrapes (E9) — no restart, no memory
growth. Thread/worker-starvation specifically was never measured (no such metric on the
surface); see Gaps.

## Safe next steps

- Re-probe `/metrics` for `faultline_chaos_enabled` and the per-route duration
  sums/counts periodically to see whether the injected latency clears on its own or
  persists.
- If it persists, escalate to whoever owns the chaos/config toggle for this target — this
  investigation's surface is read-only and cannot inspect or change that state.
- Re-check `http_exceptions_total` on any future report of errors (not just slowness) on
  the same routes, since this incident's signature (0.0 failure rate) would look different
  if the toggle's failure rate were nonzero.

## Gaps

- No tracing/profiling surface exists in this lab, so a silent non-exception-raising code
  defect inside the business-route handlers cannot be fully ruled out independent of the
  chaos flag — only the exception-based reading of H2 is directly refuted.
- No worker-pool/queue-depth metric exists on the surface, so the thread/worker-starvation
  clause of H3 is untested rather than refuted.
- The configured `extra_latency_ms` (1500) does not exactly match the observed per-request
  durations (793-1209ms); the chaos middleware's precise latency-injection semantics are
  not documented on the investigator's surface, so the magnitude match to H1 is
  qualitative, not exact.
- Whether/when the injected latency self-resolves was not tracked past this
  investigation's window — `faultline_chaos_enabled` was still `1` at conclusion.
