---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-intermittent-503s
  trigger: manual
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-08-19T03:10:12Z
  concluded: 2026-08-19T03:14:41Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A chaos-mode flag enabling an 8% synthetic 503 error rate on /orders and /products endpoints was toggled on via POST /chaos/enable at 2026-08-19T03:09:58.426Z; the flag remained enabled through the end of this investigation."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "The chaos-mode flag (failure_rate=0.08, error_status=503) enabled at 2026-08-19T03:09:58.426Z injected probabilistic 503 failures on /orders and /products/{id}; each observed failure was followed by a 200/201 on the same route roughly 85-90ms later, matching a complaint of an occasional, retry-clearing error most users would not notice."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E13]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:53.497Z"
    quote: '{"ts": "2026-08-19T03:09:53.497Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:58.426Z"
    quote: '{"ts": "2026-08-19T03:09:58.426Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "44afebbf7bb0", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:59.555Z"
    quote: 'chaos_failure event {"request_id": "a2127937f7ad", "event": "chaos_failure", "method": "GET", "path": "/orders"} followed by "GET /orders -> 503", status 503, duration_ms 0.14'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:59.641Z"
    quote: '"GET /orders -> 200", request_id "3cbd345bbcb2", status 200, duration_ms 0.455 — same path, ~86ms after E3'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:59.712Z"
    quote: 'chaos_failure event {"request_id": "7c1d9d70223a", "event": "chaos_failure", "method": "GET", "path": "/products/5"} followed by "GET /products/5 -> 503", status 503, duration_ms 0.132'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:59.797Z"
    quote: '"GET /products/5 -> 200", request_id "9e5efe9f4aaa", status 200, duration_ms 0.416 — same path, ~85ms after E5'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:59.783Z"
    quote: 'chaos_failure event {"request_id": "2afdcf60bd4e", "event": "chaos_failure", "method": "GET", "path": "/products/2"} followed by "GET /products/2 -> 503", status 503, duration_ms 0.13'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:59.869Z"
    quote: '"GET /products/2 -> 200", request_id "a1e5058e7d23", status 200, duration_ms 0.46 — same path, ~86ms after E7'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:59.740Z"
    quote: 'chaos_failure event {"request_id": "2bd511e563d6", "event": "chaos_failure", "method": "POST", "path": "/orders"} followed by "POST /orders -> 503", status 503, duration_ms 0.13'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:09:59.826Z"
    quote: '"POST /orders -> 201", request_id "61181ee46f2e", order_created order_id 4 — same path, ~86ms after E9'
  - id: E11
    type: metric
    source: "/metrics probe @ 2026-08-19T03:10:50Z (request_id konan-1787109050-41175)"
    quote: 'http_requests_total{method="GET",path="/orders",status="503"} 1 / http_requests_total{method="GET",path="/products/2",status="503"} 1 / http_requests_total{method="GET",path="/products/5",status="503"} 1 / http_requests_total{method="POST",path="/orders",status="503"} 1 — 4 failed of ~30 requests; http_exceptions_total has no entries'
  - id: E12
    type: metric
    source: "/metrics probe @ 2026-08-19T03:12:58Z (request_id konan-1787109178-41237)"
    quote: 'faultline_chaos_enabled 1 — flag still on ~3 minutes after E2, with all status=503 counters unchanged from E11 (no new non-investigator traffic arrived since)'
  - id: E13
    type: log
    source: "lab/logs/app.log (full file, all lines)"
    quote: "no line in the observed window contains \"event\": \"unhandled_exception\" or a stack field"
  - id: E14
    type: log
    source: "lab/logs/app.log (full file, all lines)"
    quote: "all non-investigator (non \"konan-\"-prefixed request_id) traffic lines fall between 2026-08-19T03:09:54.222Z and 2026-08-19T03:09:59.942Z; every log line after that timestamp carries a \"konan-\" prefixed request_id"
gaps:
  - "No actor/identity information is available for the client that called POST /chaos/enable beyond request_id 44afebbf7bb0 and client 127.0.0.1:55412 — the surface contract exposes no auth/identity field to attribute who or what toggled the flag."
  - "Only a ~5.7 second window of non-investigator traffic (03:09:54.222Z-03:09:59.942Z) was captured before it stopped; no visibility into user-side retry behavior or whether any user request exhausted its own retries — the surface contract exposes server-side telemetry only, not client experience."
  - "The chaos flag was still enabled at the end of this investigation (E12); this journal does not cover events after 2026-08-19T03:12:58Z."
usage:
  model: claude-sonnet-5
  tokens: 2097977
  wall_clock_seconds: 269
---

# Shop intermittent 503s traced to an enabled chaos flag

## Summary

**Root cause identified.** A chaos-mode flag (`failure_rate=0.08`, `error_status=503`) was
switched on via `POST /chaos/enable` at 2026-08-19T03:09:58.426Z (E2). In the ~5.7s of
real traffic that followed, it injected four 503s — on `GET /orders`, `POST /orders`,
`GET /products/2`, and `GET /products/5` — each immediately followed by a 200/201 on the
identical route roughly 85-90ms later (E3-E10). That is exactly the shape the complaint
describes: occasional, retry-clears, most people notice nothing. No unhandled exceptions
appear anywhere in the log (E13), and no other lens (process/resource lifecycle,
code-defect signatures) found a competing anomaly. The one open item: the flag was still
on as of the last check (E12), so the same ~8% failure rate will keep firing for any new
traffic — confirmed root cause, but the condition had not resolved by the time this
investigation concluded.

## Timeline (UTC)

- **03:09:53.497Z** — faultline process starts fresh (E1). Baseline traffic from
  03:09:54-03:09:58Z is clean: health checks, product browsing, and one order all 200/201.
- **03:09:58.426Z** — `POST /chaos/enable` sets chaos mode active: `failure_rate=0.08`,
  `error_status=503` (E2). This is the config-change marker — everything after it is
  "after," everything before is "before."
- **03:09:59.555Z-03:09:59.826Z** — four chaos-injected 503s fire, each on a distinct
  request, each followed by a success on the same route ~85-90ms later (E3-E10).
- **03:09:59.942Z** — last non-investigator traffic observed (E14). No further real user
  requests appear in the log after this point.
- **03:10:50Z / 03:12:58Z** — investigator `/metrics` probes confirm the flag is still
  enabled and the failure counters are unchanged (E11, E12) — consistent with "no new
  errors" being explained by "no new traffic," not by resolution.

## Investigation

1. **Baseline** — `/health` (200 OK), `/metrics`, and the log tail were read first.
   The metrics snapshot immediately showed `faultline_chaos_enabled 1` and four 503s
   spread across `/orders` and two `/products/{id}` routes — enough to form a working
   hypothesis before triage even started.
2. **Triage (3 lenses, parallel)** — software-defect, infra-process, and interfaces
   lenses each reviewed the same baseline blind to each other:
   - *software-defect*: no anomalies — no unhandled exceptions, failures spread across
     unrelated routes, and identical inputs succeeded on retry, which is not a
     per-input defect signature.
   - *infra-process*: no anomalies — single startup event, flat RSS, sub-millisecond
     durations even on the failing requests (fast failures, not hangs or saturation).
   - *interfaces*: found the `chaos_enabled` config-change marker (E2) with a sharp
     onset (0 failures before, ~10% after) and the pass/fail interleaving on identical
     routes — textbook injected-degradation shape, not a per-input bug.
   No lens raised a competing hypothesis; all three findings are consistent with a single
   cause.
3. **Deep-dive — skipped.** H1's evidence was already deterministic and complete from
   triage (explicit `chaos_failure` log lines pairing 1:1 with every observed 503, plus
   a same-route retry success for each), so per protocol this went straight to judgment
   rather than a redundant confirm/refute round.
4. **Judge** — an adversarial judge reviewed H1 against the cited evidence only (no
   narrative). Verdict: validated. It flagged one gap in the evidence set as originally
   presented: the `POST /orders` 503 lacked an explicit `chaos_failure` pairing in what
   was shown to it. That pairing existed in the already-gathered log data (now cited as
   E9/E10) — the gap was in what was handed to the judge, not in the underlying
   telemetry. The judge also correctly noted the hypothesis text overstated recovery
   latency ("seconds" vs. the actual ~85-90ms); that wording is corrected above.

## Hypotheses

### H1 — chaos flag toggled on, injecting probabilistic 503s (validated)

Statement: the `POST /chaos/enable` call at 03:09:58.426Z (E2) set an 8% synthetic
failure rate that fired on four requests across `/orders` and `/products/{id}` in the
following ~5.7 seconds, each clearing on the next call to the same route (E3-E10). No
unhandled exceptions occurred (E13), and no other domain (process lifecycle, resource
saturation, code-level defect) produced a competing anomaly. This fully accounts for the
complaint's shape: intermittent, self-resolving on retry, unnoticed by most users.

No evidence against this hypothesis was found.

## Safe next steps

- Keep polling `/metrics` for `faultline_chaos_enabled` and the `status="503"` counters
  — the flag was still on at last check (E12), so the same failure rate will keep
  firing for the next wave of real traffic.
- Watch `lab/logs/app.log` for further `chaos_failure` events correlated with
  non-investigator (non-`konan-`-prefixed) request ids, to see whether the affected
  routes or rate change.
- If an owner for `POST /chaos/enable` calls can be identified through channels outside
  this surface (deploy/change log, whoever runs scenario tooling), confirm whether this
  activation was intentional — the surface contract here has no actor/identity field to
  settle that from telemetry alone.

## Gaps

- No actor/identity is attributable for the client that called `POST /chaos/enable`
  beyond its request id and loopback client address — the lab's telemetry surface has no
  auth/identity field for this.
- Only ~5.7 seconds of non-investigator traffic were captured in the log before it
  stopped; there is no client-side telemetry, so user-level retry behavior (versus
  simply "few users, short window") cannot be confirmed from this surface.
- The chaos flag remained enabled at the end of this investigation (E12); nothing after
  2026-08-19T03:12:58Z is covered here.
