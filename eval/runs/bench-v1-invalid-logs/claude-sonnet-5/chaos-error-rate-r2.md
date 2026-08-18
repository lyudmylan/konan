---
konan_journal: 1
investigation:
  id: 2026-08-18-chaos-enabled-intermittent-503s
  trigger: manual
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-08-18T17:21:44Z
  concluded: 2026-08-18T17:25:34Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime fault-injection flag (chaos mode) was switched on via an unstamped external call to POST /chaos/enable at 2026-08-18T17:21:22.371Z with failure_rate=0.4 and error_status=503, causing probabilistic 503 responses on GET /products/* and POST /orders while leaving GET /health unaffected."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos fault-injection was enabled at 17:21:22.371Z (failure_rate=0.4, error_status=503), causing probabilistic 503s on /products/* and /orders that succeed on retry, while /health is exempt from the injected failures — explaining both the user reports and the green dashboard."
    incident_class: interfaces
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "A process restart shortly before the incident window caused the intermittent failures (crash loop or degraded process)."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E15]
    evidence_against: [E16, E17]
  - id: H3
    statement: "An application code defect (unhandled exception, or a bug on specific inputs) causes the intermittent failures."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E9, E10, E11, E12]
evidence:
  - id: E1
    type: probe
    source: "GET /health, request_id=konan-1787073735-15271"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":60.70519079104997} -- HTTP 200 in 0.001569s"
  - id: E2
    type: metric
    source: "GET /metrics scrape @ 2026-08-18T17:22:15Z"
    quote: "faultline_chaos_enabled 1"
  - id: E3
    type: metric
    source: "GET /metrics scrape @ 2026-08-18T17:22:15Z"
    quote: "http_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1"
  - id: E4
    type: metric
    source: "GET /metrics scrape @ 2026-08-18T17:22:15Z"
    quote: "http_requests_total{method=\"GET\",path=\"/products/4\",status=\"503\"} 1"
  - id: E5
    type: metric
    source: "GET /metrics scrape @ 2026-08-18T17:22:15Z"
    quote: "http_requests_total{method=\"GET\",path=\"/products/5\",status=\"503\"} 1"
  - id: E6
    type: metric
    source: "GET /metrics scrape @ 2026-08-18T17:22:15Z"
    quote: "http_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:21:22.371Z"
    quote: "{\"ts\": \"2026-08-18T17:21:22.371Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"bd44c99801c1\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.4, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:21:22.372Z"
    quote: "{\"ts\": \"2026-08-18T17:21:22.372Z\", \"message\": \"POST /chaos/enable -> 200\", \"request_id\": \"bd44c99801c1\", \"method\": \"POST\", \"path\": \"/chaos/enable\", \"status\": 200, \"duration_ms\": 2.211, \"client\": \"127.0.0.1:49185\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:21:25.489Z"
    quote: "{\"ts\": \"2026-08-18T17:21:25.489Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"90479700ca35\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\"} followed by \"GET /products/1 -> 503\", \"status\": 503, \"duration_ms\": 0.272"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:21:27.605Z"
    quote: "{\"ts\": \"2026-08-18T17:21:27.605Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"965d09708359\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\"} followed by \"POST /orders -> 503\", \"status\": 503, \"duration_ms\": 0.272"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:21:16.190Z"
    quote: "{\"ts\": \"2026-08-18T17:21:16.190Z\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"97bff7730617\", \"status\": 200, \"duration_ms\": 1.071}"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:21:31.842Z"
    quote: "{\"ts\": \"2026-08-18T17:21:31.842Z\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"969382b9423c\", \"status\": 200, \"duration_ms\": 0.781}"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:22:15.083Z"
    quote: "{\"ts\": \"2026-08-18T17:22:15.083Z\", \"message\": \"GET /health -> 200\", \"request_id\": \"konan-1787073735-15271\", \"status\": 200, \"duration_ms\": 0.49}"
  - id: E14
    type: log
    source: "lab/logs/app.log (full-file check, 71 lines)"
    quote: "grep -c '\"exception\"' => 0; grep -c '\"stack\"' => 0; no event:\"unhandled_exception\" line present anywhere in the file; every 503 line is immediately preceded by an event:\"chaos_failure\" line with the same request_id (E9, E10)."
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:21:13.024Z–17:21:14.390Z"
    quote: "{\"ts\": \"2026-08-18T17:21:13.024Z\", \"message\": \"Shutting down\"} ... {\"ts\": \"2026-08-18T17:21:14.390Z\", \"logger\": \"uvicorn.error\", \"message\": \"Started server process [15132]\"}"
  - id: E16
    type: log
    source: "lab/logs/app.log (full-file scan, 71 lines)"
    quote: "event:\"startup\" appears exactly twice: @2026-08-18T17:12:45.723Z (PID 14666, initial boot) and @2026-08-18T17:21:14.390Z (PID 15132, restart). No further startup or shutdown lines follow — not a restart loop."
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-08-18T17:21:15.114Z–17:21:19.308Z"
    quote: "Six consecutive successful requests immediately after the restart completed and before chaos was enabled: GET /health -> 200 (x2), GET /products -> 200, GET /products/1 -> 200, POST /orders -> 201, GET /products/2 -> 200 — zero errors in this window."
gaps:
  - "Whether the POST /chaos/enable call (E8, unstamped client 127.0.0.1:49185) was triggered by the eval harness's operator surface or an actual operator action could not be confirmed — /chaos and /simulate are outside the investigator's read-only surface contract (docs/lab.md); only its effect (E7) and footprint (E8) are observable."
  - "The configured failure_rate=0.4 (E7) was not confirmed against a large sample — observed counts (E3–E6) are 1 failure per route on very small N, consistent with but not statistically confirming the configured rate."
  - "No access to faultline's source code to confirm the chaos middleware's exact selection logic (why /health is exempt) beyond the observed behavior (E13 and absence of any chaos_failure on path=/health)."
usage:
  model: claude-sonnet-5
  tokens: 2167451
  wall_clock_seconds: 230
---

# Shop intermittent 503s from an unannounced chaos-mode flag flip

## Summary

**Root cause identified.** At `2026-08-18T17:21:22.371Z` an external, non-investigator
caller flipped the service's fault-injection flag on (`POST /chaos/enable`, E7/E8),
configuring a 40% probabilistic failure rate returning HTTP 503 on any request
(`failure_rate: 0.4, error_status: 503`). From that moment, `GET /products/*` and
`POST /orders` began failing intermittently and non-deterministically — the same route
and input succeeding, then failing, then succeeding again (E9, E11, E12) — exactly
matching the reported "errors, then works again on retry." `GET /health` was never
touched by the injected failures (E13, no `chaos_failure` line ever names `/health`),
which is why the health dashboard stayed green throughout — a monitoring-coverage gap,
not a false signal. Confidence is high: the log directly and explicitly labels each
failing request as `chaos_failure` at the moment it happens, no inference required.

## Timeline

- `17:12:45.723Z` — first process boot (PID 14666), unrelated prior session.
- `17:21:13.024Z`–`17:21:14.390Z` — process restart: shutdown then boot of PID 15132
  (E15). One-off restart, not a loop (E16).
- `17:21:15.114Z`–`17:21:19.308Z` — six clean requests post-restart, zero errors (E17).
- **`17:21:22.371Z`** — chaos mode enabled, `failure_rate=0.4`, `error_status=503`
  (E7), via an unstamped external call (E8) — the config-change marker.
- `17:21:25.489Z` — first chaos-injected failure, `GET /products/1 -> 503` (E9), 3.1s
  after the flag flip.
- `17:21:27.605Z`–`17:21:33.963Z` — further chaos failures interleaved with successes
  across `/products/1`, `/products/4`, `/products/5`, `POST /orders` (E10, E12).
- `17:21:40Z` — human complaint raised (this investigation's trigger).
- `17:22:15.083Z` — investigator probe confirms `/health` still 200 post-chaos (E13).

## Investigation

1. **Baseline**: probed `/health` (E1) and `/metrics` (E2–E6), then read the full log
   tail. The metrics snapshot already showed `faultline_chaos_enabled 1` and scattered
   503s on business routes next to 200/201s on the same routes — the healthy-dashboard
   trap was visible before formal triage even started.
2. **Triage** (3 lenses, parallel, blind to each other):
   - *infra-process*: flagged the restart (E15) but confirmed it wasn't a loop and
     showed no saturation/latency signal — restart isn't self-sufficient as a cause.
   - *interfaces*: identified the `chaos_enabled` config marker as "timeline gold,"
     matched the probabilistic per-route failure shape to injected degradation, and
     flagged the `/health` coverage gap explaining the green dashboard.
   - *software-defect*: found zero exceptions/stack traces, no data-dependent
     (single-input) failure shape, and noted every 503 self-labeled as chaos-injected —
     actively ruled its own domain out.
   All three lenses converged on the same explanation from independent angles, and the
   evidence was already deterministic (an explicit config marker plus explicit
   per-failure attribution), so deep-dive was skipped per the budget rule for
   already-conclusive triage evidence.
3. **Judge** (adversarial, evidence-only, blind to narrative): validated H1, invalidated
   H2 and H3, citing the same timing and attribution evidence.

## Hypotheses

### H1 — Chaos fault-injection flag flip (validated)

The app's own logs self-report both the cause (E7: exact config values) and the
per-failure attribution (E9, E10: `event: chaos_failure` on the same `request_id` as
each 503). The same input (`GET /products/1`) succeeds, fails, then succeeds again
(E11, E9, E12) — only explicable by a probabilistic gate, not a deterministic code
path. `/health` never appears in a `chaos_failure` line and kept returning 200 after
the flag flip (E13), accounting for the green dashboard.

### H2 — Process restart (invalidated)

A restart did occur 8 seconds before the flag flip (E15), but it was a single
transition, not a loop (E16), and six requests succeeded cleanly in the gap between
restart-complete and chaos-enable (E17). Failure onset tracks the chaos-enable
timestamp (+3.1s), not the restart timestamp (+11s) — the restart is coincidental
timing, not causal.

### H3 — Application code defect (invalidated)

No exception or stack trace appears anywhere in the log (E14). Every observed 503 is
immediately preceded by an explicit `chaos_failure` log line for the same request
(E9, E10), and the same input alternates between success and failure (E9/E11/E12) —
the opposite of the deterministic per-input signature a code defect would produce.

## Safe next steps

- Re-run `GET /metrics` periodically (read-only) to watch `faultline_chaos_enabled`
  and route-level 503 counts; the flag returning to `0` would confirm resolution
  without needing write access.
- If a chaos/feature-flag change log exists outside this surface (e.g. a deploy or
  ops audit trail), cross-check its timestamp against `17:21:22.371Z` to identify who
  or what triggered `POST /chaos/enable` — this investigation's surface contract
  (docs/lab.md) does not expose that endpoint's caller identity beyond the client
  address already cited (E8).
- Consider (for whoever owns monitoring, not this investigation) that `/health` not
  reflecting business-route failures is a recurring blind spot worth a dashboard
  review — noted as an observation, not a remediation performed here.

## Gaps

- Could not confirm who or what triggered `POST /chaos/enable` — the `/chaos` and
  `/simulate` endpoints are outside the investigator's read-only surface contract
  (docs/lab.md); only the effect (E7) and the caller's IP/port footprint (E8) were
  observable.
- The configured `failure_rate=0.4` was not statistically confirmed against a large
  sample — observed counts (E3–E6) are single failures per route on small N, consistent
  with but not proof of the exact configured rate.
- No access to source code to confirm why `/health` specifically is exempt from chaos
  injection — inferred only from the absence of any `chaos_failure` line naming
  `/health` (E13).
