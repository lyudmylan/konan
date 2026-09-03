---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-injection-503s
  trigger: 'manual — /konan human report (human profile, docs/triggers.md). Complaint startsAt 2026-08-19T16:28:14Z; investigation start 2026-08-19T16:28:20Z; trigger latency 6s.'
  complaint: 'A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?'
  started: 2026-08-19T16:28:20Z
  concluded: 2026-08-19T16:36:45Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'A runtime failure-injection toggle was enabled at 16:28:05.147Z with failure_rate 0.08 and error_status 503; the service attributes every observed non-2xx response to it, and the toggle was still armed at the last observation.'
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: 'A runtime failure-injection toggle was enabled at 16:28:05.147Z (failure_rate 0.08, error_status 503, extra_latency_ms 0); every non-2xx response observed on this process is attributed by the service itself to that injector, and no event has disabled it as of the last scrape.'
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E12, E14, E18]
    evidence_against: [E16]
  - id: H2
    statement: 'The errors come from a data-dependent software defect: a specific product id or route input deterministically fails.'
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E11, E12, E16, E5, E7]
  - id: H3
    statement: 'The errors come from a process-lifecycle fault: a crash, restart, or health-endpoint flap.'
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E13, E14, E15]
  - id: H4
    statement: 'The errors come from load or resource saturation (memory growth, worker starvation, latency degradation under concurrency).'
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E8, E13, E18]
  - id: H5
    statement: 'The injector is unreverted operator or test state rather than a deliberate current setting — something armed it and nothing disarmed it.'
    incident_class: interfaces
    state: inconclusive
    evidence_for: [E4, E14]
    evidence_against: []
latent_findings:
  - statement: 'The metrics layer labels the failure path with the raw request path but the success path with the matched route template, so a route 503s never aggregate with its own 200s and per-route error rate cannot be computed; every distinct product id on the error path creates a new time series (unbounded label cardinality). Not user-facing and not the reported incident.'
    evidence: [E17]
evidence:
  - id: E1
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T16:27:59.913Z'
    quote: '{"ts": "2026-08-19T16:27:59.913Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T16:28:02.000Z'
    quote: '{"ts": "2026-08-19T16:28:02.000Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "84e08ff89ede", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.015, "client": "127.0.0.1:62757"}'
  - id: E3
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T16:28:05.147Z'
    quote: '{"ts": "2026-08-19T16:28:05.147Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "8123f37c59a3", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E4
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T16:28:05.147Z'
    quote: '{"ts": "2026-08-19T16:28:05.147Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "8123f37c59a3", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 3.04, "client": "127.0.0.1:62760"}'
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T16:28:06.515Z'
    quote: '{"ts": "2026-08-19T16:28:06.515Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "b521cb023e4d", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E6
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T16:28:06.516Z'
    quote: '{"ts": "2026-08-19T16:28:06.516Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "b521cb023e4d", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.134, "client": "127.0.0.1:62780"}'
  - id: E7
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T16:28:06.574Z'
    quote: '{"ts": "2026-08-19T16:28:06.574Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "9f75ff65816f", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E8
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T16:28:06.574Z'
    quote: '{"ts": "2026-08-19T16:28:06.574Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "9f75ff65816f", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.135, "client": "127.0.0.1:62784"}'
  - id: E9
    type: log
    source: 'lab/logs/app.log @ 2026-08-19T16:28:06.603Z'
    quote: '{"ts": "2026-08-19T16:28:06.603Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "c09f6a8c30f7", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.438, "client": "127.0.0.1:62786"}'
  - id: E10
    type: metric
    source: '/metrics, probe request_id konan-1787157102-65145 (process_uptime_seconds 222.81524037499912)'
    quote: 'faultline_chaos_enabled 1'
  - id: E11
    type: metric
    source: '/metrics, probe request_id konan-1787157102-65145 — counter declared with no series present'
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E12
    type: metric
    source: '/metrics, probe request_id konan-1787157102-65145 — the only non-2xx series in the entire scrape'
    quote: |-
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E13
    type: metric
    source: '/metrics, two scrapes: konan-1787156918-65011 then konan-1787157102-65145'
    quote: |-
      process_uptime_seconds 38.65834204200655 -> process_uptime_seconds 222.81524037499912
      process_max_rss_bytes 47661056 -> process_max_rss_bytes 47661056
  - id: E14
    type: log
    source: 'lab/logs/app.log, whole file (53 lines at first read, no rotated .1-.3 backups present)'
    quote: 'grep -c "chaos_disabled" = 0 ; grep -c ''"event": "startup"'' = 1'
  - id: E15
    type: probe
    source: '/health, request_id konan-1787156914-65004'
    quote: |-
      {"status":"ok","uptime_seconds":34.418993124971166}
      -- HTTP 200 in 0.002816s request_id=konan-1787156914-65004
  - id: E16
    type: probe
    source: '8 consecutive investigator probes at ~16:36:10Z: /products/1 x4 (konan-1787157370-65225, konan-1787157371-65231, konan-1787157372-65237, konan-1787157372-65243), /products x2 (konan-1787157373-65249, konan-1787157373-65255), /orders x2 (konan-1787157374-65261, konan-1787157374-65267)'
    quote: 'All 8 returned HTTP 200; trailer of the first: -- HTTP 200 in 0.001392s request_id=konan-1787157370-65225'
  - id: E17
    type: metric
    source: '/metrics, probe request_id konan-1787157102-65145 — same endpoint under two different path labels'
    quote: |-
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 19
  - id: E18
    type: log
    source: 'lab/logs/app.log, post-marker window 2026-08-19T16:28:06.220Z-16:28:06.691Z'
    quote: '32 access lines in the window; exactly 2 carry status 503 (E6, E8), all others status 200 or 201 — observed failure fraction 2/32 = 6.3%.'
gaps:
  - 'The complaint window is not covered by any available telemetry. The process started at 16:27:59.913Z (E1) and app.log has no rotated .1-.3 backups, so nothing before that instant is observable. The reporter says "over the last few minutes"; if user-visible errors predate the process start, this investigation cannot see them and H1 would not explain those.'
  - 'The reported errors were never tied to specific user requests: the complaint carries no timestamps, request ids, or error counts, and no user-side record was available to correlate against the two observed 503s.'
  - 'The injector sampling scope is unverified. failure_rate 0.08 (E3) is the configured literal, not a measured rate; the observed fraction is 2/32 (E18) and 0/8 on investigator probes (E16). Whether the sampler covers all routes or excludes control endpoints (/health, /metrics) could not be determined, because that requires reading faultline source, which is outside the investigator surface (docs/lab.md) and the eval blinding contract.'
  - 'H1 "still armed" rests on a gauge read at one instant (E10) plus the absence of a disable event (E14). Eight live probes did not reproduce a failure (E16); at the configured 8% a zero-failure run of 8 has probability 0.51, so that negative neither confirms nor refutes, and no behavioural proof of a currently firing injector was obtained.'
  - 'Whether the injector was armed deliberately or is leftover test state (H5) is not decidable from telemetry: the enabling call (E4) records a client address but no actor identity.'
  - 'No user-side or client-side telemetry exists in this lab — retry behaviour, user-visible error copy, and abandoned sessions could not be measured, so business impact is inferred from server status codes alone.'
usage:
  model: claude-opus-5
  tokens: 2463705
  wall_clock_seconds: 505
---

# Injected 503 failures from an armed chaos toggle

## Summary

**Not nothing — but not a code bug either.** A runtime failure-injection toggle was
switched on at 16:28:05.147Z, configured to return HTTP 503 at a failure rate of 0.08
with no added latency (E3). Every error observed on this process is attributed by the
service's own logs to that injector: both 503s carry an `event: chaos_failure` warning
sharing the failing request's id (E5/E6, E7/E8), and they are the only non-2xx responses
in the entire metrics scrape (E12). Nothing threw — `http_exceptions_total` has no series
at all (E11).

This explains the reporter's symptom shape exactly. The failure is per-request and
random, not per-input: `GET /products/1` returned 200 at 16:28:06.428Z, 503 at
16:28:06.516Z, then 200 again at 16:28:06.603Z (E9). That is why it "works on retry" and
why "most people notice nothing" — at an 8% rate most sessions never see it.

**The condition has not cleared.** `faultline_chaos_enabled` still reads 1 at 222s of
uptime (E10) and no `chaos_disabled` event exists anywhere in the log (E14). The errors
stopped appearing in the log because user traffic stopped at 16:28:06.691Z, not because
anything was fixed. Confidence in the mechanism is high; confidence that it accounts for
what these specific users saw is lower, and the reason is in Gaps — the reporter's "last
few minutes" extends further back than any telemetry available here.

## Timeline

- **16:27:59.913Z** — process starts, `faultline 0.1.0 started` (E1). This is the earliest
  observable instant; nothing before it exists in telemetry.
- **16:28:00.700Z – 16:28:03.074Z** — clean traffic: health, products, order creation, all
  2xx. `GET /products/1 -> 200` (E2). Baseline normal.
- **16:28:05.147Z** — **configuration-change marker.** `chaos mode enabled`,
  `failure_rate: 0.08`, `error_status: 503`, `extra_latency_ms: 0` (E3), set through
  `POST /chaos/enable -> 200` from a non-investigator client (E4).
- **16:28:06.220Z – 16:28:06.691Z** — 32 requests; exactly 2 fail (E18).
- **16:28:06.515/.516Z** — first failure: `chaos_failure` then `GET /products/1 -> 503`,
  same request id `b521cb023e4d`, `duration_ms` 0.134 (E5, E6).
- **16:28:06.574Z** — second failure: `chaos_failure` then `POST /orders -> 503`, same
  request id `9f75ff65816f`, `duration_ms` 0.135 (E7, E8).
- **16:28:06.603Z** — the same path succeeds again on retry (E9).
- **16:28:14Z** — human complaint raised (`startsAt`); investigation starts 16:28:20Z.
- **16:32:22Z** — toggle still armed: `faultline_chaos_enabled 1` (E10).
- **~16:36:10Z** — 8 investigator probes, all 200; no failure reproduced (E16).

## Investigation

**Baseline** established a healthy pre-marker period and immediately surfaced two things
worth explaining: uptime of only 34s, and `faultline_chaos_enabled 1`.

**Triage** ran all three lenses in parallel, each blind to the others, because a vague
complaint excludes no domain by evidence. All three converged independently:
software-defect returned negative findings and killed the data-dependent shape by
reproducing `GET /products/1` as 200 three times; infra-process found a single startup
marker, monotonic uptime, byte-identical RSS and flat latency, so no lifecycle or
saturation fault; interfaces identified the config-change marker as the onset and found
the toggle still armed.

**Deep-dive was skipped by design.** Per the loop's rule, a hypothesis whose triage
evidence is already deterministic goes straight to the judge — deep-dives fill evidence
gaps rather than re-prove. H1's mechanism was already closed by request-id attribution.

**The judge refused to bless H1 as written**, and it was right. It separated the earned
core (a toggle was enabled; observed non-2xx responses are attributed to it) from three
overreaching riders: that 8% is a *measured* rate rather than a config literal; that
"still armed" holds now rather than at the last observation; and that this accounts for
"every error the users saw" — unsupported, since all evidence describes a process that
began ~34s before the investigation. It also caught that the `POST /orders` 503 access
line had not been closed by request id.

**Response.** I closed the request-id chain (E8 — same id `9f75ff65816f` as E7), restated
H1 to the claim the evidence earns, and ran the judge's implied decisive test: 8 live
read-only probes to see the injector fire. All 8 returned 200 (E16). At 8% a zero-failure
run of 8 has probability 0.51, so this is uninformative rather than exculpatory — it is
recorded as evidence *against* H1 in the machine core and as a gap, not argued away.

## Hypotheses

### H1 — armed failure injector *(validated)*

Enabled at 16:28:05.147Z with the exact status it produced (E3). Causally closed, not
merely correlated: both failures carry a `chaos_failure` warning under the same request
id as the 503 access line (E5/E6, E7/E8). Sharp onset against a clean baseline (E2), and
the two 503s are the only non-2xx series that exist (E12) with zero exceptions (E11).
Still armed at last read (E10), never disabled (E14). Against it: 8 probes did not
reproduce a failure (E16) — too small a sample to weigh against the rest.

### H2 — data-dependent software defect *(invalidated)*

Killed on the classic signature test. The same input returns 200, 503, 200 in sequence
(E9), and reproduced 200 on repeat probes (E16). Decisively, E12 leaves no residual error
for a defect to explain — every non-2xx is injector-attributed (E5, E7). The failures
also short-circuit in 0.134/0.135ms versus 0.4–0.7ms for successes (E6, E8): no handler
code ran.

### H3 — process lifecycle fault *(invalidated)*

Exactly one startup event (E14), uptime monotonic 38.66 → 222.82 across scrapes with no
counter reset, RSS byte-identical (E13), health 200 (E15). The process is alive and
un-restarted. Noted honestly: the freshly-started process (E1) is itself a fact this
investigation cannot explain, only bound.

### H4 — load or resource saturation *(invalidated)*

Saturation errors queue and arrive slow; these arrived in 0.134/0.135ms (E6, E8), faster
than the success path. Flat RSS and flat latency across scrapes (E13), and the service
absorbed 32 requests in 471ms with 30 successes (E18).

### H5 — unreverted operator or test state *(inconclusive)*

The injector was armed through a live HTTP endpoint by a non-investigator client (E4) and
nothing ever disabled it (E14). Whether that was deliberate or leftover is not decidable
from telemetry — the log records a client address, not an actor. This matters because the
remedy differs: a deliberate setting is a scheduling question, leftover state is a
change-management one.

## Safe next steps

Read-only suggestions only.

1. **Ask the operator who armed the injector** whether it is intended. The enabling call
   is at 16:28:05.147Z from client `127.0.0.1:62760` (E4). This is the single fastest way
   to close H5, and it decides whether anything needs doing at all.
2. **Confirm the toggle state at decision time** with a fresh `/metrics` read of
   `faultline_chaos_enabled` — E10 is one instant, and the answer may have changed.
3. **Get the reporter to pin the window**: approximate first-error time, any error text or
   request id. That is the one piece that would settle whether H1 explains what these
   users actually hit, per the first Gap.
4. **Check whether log retention covers the complaint window** — no rotated backups were
   present (E14); if retention is the limiting factor, that is worth knowing before the
   next incident.
5. **Do not treat the metrics label split as cosmetic** if per-route error alerting is
   planned — see the latent finding; a route's 503s never aggregate with its 200s (E17).

Remediation — disabling the injector — is out of scope for this journal and outside the
investigator's read-only boundary.

## Gaps

The frontmatter list in full, with the two that matter most:

**The complaint window is not covered by telemetry.** Everything here describes a process
that started at 16:27:59.913Z (E1), roughly 14 seconds before the complaint was raised
and with no rotated logs behind it. The reporter said "the last few minutes." If users saw
errors before this process existed, they are invisible to every check performed, and H1
would not explain them. The mechanism is proven; its coverage of the reported symptom is
inferred from shape-match, not from correlated user records.

**The injector's sampling scope is unverified.** `failure_rate: 0.08` is the configured
literal (E3), not a measurement — observed fractions were 2/32 (E18) and 0/8 (E16).
Determining whether the sampler covers control endpoints such as `/health` and `/metrics`
would require reading faultline's source, which sits outside the investigator surface in
`docs/lab.md` and outside the eval blinding contract. I did not read it. If injection does
cover control endpoints, then E10 and E15 are themselves sampled reads — a caveat that
cannot be closed from telemetry alone.

Also open: no actor identity on the enabling call, and no user-side telemetry in this lab,
so business impact rests on server status codes alone.
