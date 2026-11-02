---
konan_journal: 2
investigation:
  id: 2026-11-02-routine-handover-chaos-blip
  trigger: manual
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-02T22:17:04Z
  concluded: 2026-11-02T22:28:02Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos/degradation switch inside faultline was enabled from 22:16:21.320Z to 22:16:27.671Z (failure_rate=0.6, error_status=503) and probabilistically injected exactly one 503 failure on GET /products during that ~6.35-second window before being disabled; traffic on the same route succeeded immediately before, during, and after the window, and the service has run error-free since, confirmed by a cumulative-counter check taken ~7m38s later."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "The 'noise' reported at handover was a brief, internal chaos/degradation-switch toggle (enabled 22:16:21.320Z, disabled 22:16:27.671Z) that probabilistically injected one 503 on GET /products; no other anomaly exists, no restart occurred, and the service is currently healthy with no active incident."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:21.320Z"
    quote: '{"ts": "2026-11-02T22:16:21.320Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "18861eee4b00", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:21.321Z"
    quote: '{"ts": "2026-11-02T22:16:21.321Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "18861eee4b00", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.483, "client": "127.0.0.1:61754"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:22.382Z"
    quote: '{"ts": "2026-11-02T22:16:22.382Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "37a51478a006", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:22.382Z"
    quote: '{"ts": "2026-11-02T22:16:22.382Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "37a51478a006", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.269, "client": "127.0.0.1:61755"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:27.671Z"
    quote: '{"ts": "2026-11-02T22:16:27.671Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "eca8ba3c3f57", "event": "chaos_disabled"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:27.672Z"
    quote: '{"ts": "2026-11-02T22:16:27.672Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/disable -> 200", "request_id": "eca8ba3c3f57", "event": "request", "method": "POST", "path": "/chaos/disable", "status": 200, "duration_ms": 1.132, "client": "127.0.0.1:61760"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:23.440Z"
    quote: '{"ts": "2026-11-02T22:16:23.440Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "ebd1653ff624", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.823, "client": "127.0.0.1:61756"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:26.615Z"
    quote: '{"ts": "2026-11-02T22:16:26.615Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "31819d5b4315", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.735, "client": "127.0.0.1:61759"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:47.730Z"
    quote: '{"ts": "2026-11-02T22:16:47.730Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "7ddb2c4d44e0", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.833, "client": "127.0.0.1:61761"}'
  - id: E10
    type: probe
    source: "GET /health, request_id konan-1793657857-8261, 2026-11-02T22:17:37Z"
    quote: '{"status":"ok","uptime_seconds":80.38267262489535} -- HTTP 200 in 0.002106s'
  - id: E11
    type: metric
    source: "/metrics probe, request_id konan-1793657861-8266, 2026-11-02T22:17:41Z"
    quote: 'http_requests_total{method="GET",path="/products",status="503"} 1 ; faultline_chaos_enabled 0 ; http_exceptions_total header present, zero series emitted'
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-02T22:16:17.467Z (only startup marker in the full log history; no rotated backups exist)"
    quote: '{"ts": "2026-11-02T22:16:17.467Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E13
    type: probe
    source: "GET /health, request_id konan-1793658246-8450, 2026-11-02T22:24:06Z"
    quote: '{"status":"ok","uptime_seconds":469.32076712488197} -- HTTP 200 in 0.001588s'
  - id: E14
    type: metric
    source: "/metrics probe, request_id konan-1793658246-8453, 2026-11-02T22:24:06Z"
    quote: 'http_requests_total{method="GET",path="/products",status="503"} 1 (unchanged from E11) ; faultline_chaos_enabled 0 ; process_uptime_seconds 469.33420508285053 ; process_max_rss_bytes 46792704 (unchanged) ; http_exceptions_total still zero series'
gaps:
  - "Telemetry retention begins at process startup (E12, 22:16:17.467Z); there are no rotated log backups. Anything predating that moment is outside the retained window. This does not bite here — the complaint, the chaos episode, and the whole observed process lifetime all fall inside the ~11-minute window this investigation covered — but it is a structural limit of this lab instance worth naming."
  - "Confirmation that the service has stayed clean rests on two point-in-time probe/metric checks (~70s and ~7m38s after the chaos-disable event, E10/E11 and E13/E14), bridged by the monotonic request and exception counters that did not move between them. This is not continuous monitoring. A transient condition entirely between the two checks that left no counter trace is theoretically possible but unevidenced."
usage:
  model: claude-sonnet-5
  tokens: 3660641
  wall_clock_seconds: 658
---

# Brief chaos-toggle blip on the shop service — resolved before handover

## Summary

**Root cause identified; no incident is active now.** The "noise" reported at handover
was a brief internal chaos/degradation-switch toggle inside faultline: enabled at
22:16:21.320Z, disabled at 22:16:27.671Z (about 6.35 seconds), configured with
`failure_rate=0.6` and `error_status=503`. It probabilistically injected exactly one
503 on `GET /products`; traffic on the same route succeeded immediately before, during,
and after that window. The service has recorded zero new failures, zero exceptions, no
restart, and no memory growth since — confirmed by a follow-up check taken 7 minutes 38
seconds after the toggle was disabled. There is nothing currently wrong with the shop
service. Confidence: high — the mechanism is stated by the application's own log event
names (`chaos_enabled`/`chaos_failure`/`chaos_disabled`), not inferred, and the
"clean since" claim is backed by monotonic counters across a real traffic window, not
just a single snapshot.

## Timeline

- **22:16:17.467Z** — process startup, the only startup marker in the retained history (E12).
- **22:16:21.320Z–321Z** — chaos mode enabled via `POST /chaos/enable` (E1, E2).
- **22:16:22.382Z** — chaos-injected 503 on `GET /products`, the only non-2xx/201 status
  ever recorded by this process (E3, E4).
- **22:16:23.440Z, 22:16:26.615Z** — `GET /products/2` and `GET /products` both succeed
  (200) while chaos was nominally still enabled (E7, E8).
- **22:16:27.671Z–672Z** — chaos mode disabled via `POST /chaos/disable` (E5, E6).
- **22:16:47.730Z** — further successful `GET /products`, well after disable (E9).
- **22:17:37Z–41Z** — investigator baseline: health ok, metrics confirm a single 503 and
  chaos off (E10, E11).
- **22:24:06Z** — investigator follow-up, 7m38s after disable: health still ok, 503
  count unchanged, chaos still off, uptime continuous (no restart), memory flat (E13, E14).

## Investigation

**Baseline.** `lab/logs/app.log` held only 28 lines with no rotated backups — the
complete history since a process start ~80 seconds before investigation start. That
one small log already showed the chaos bracket and nothing else unusual, plus a
healthy `/health` and `/metrics` read.

**Triage.** Because the complaint was vague ("anything wrong right now? there was
some noise earlier"), all three available lenses were spawned in parallel, each blind
to the others and to this baseline:
- *infra-process* found only the chaos toggle — no restart, no RSS growth, no latency
  drift.
- *interfaces* found the same toggle, explicitly deferred its classification to
  infra-process per its own lens rule (an internal switch, not a dependency failure),
  and additionally confirmed the observed ~25% failure rate in its small sample was
  consistent with the configured 60% rate under sampling variance.
- *software-defect* found no unhandled exceptions, no data-dependent failure pattern,
  and confirmed the lone 503 was explicitly self-tagged by the app as chaos-injected.

All three converged on one hypothesis (H1) and raised no others. Because the evidence
was already deterministic and complete — named mechanism, exact timestamps, confirmed
by metrics — H1 skipped deep-dive and went straight to the judge.

**Judge, round 1 — inconclusive.** The causal mechanism (switch → one 503) was ruled
well-evidenced. The "clean since, no incident active" half of H1 was not: it rested on
checks taken only ~70–90 seconds after the toggle disabled. The judge named exactly
what would settle it: a check from minutes later, not seconds.

**Targeted gathering.** A fresh `/health` and `/metrics` probe was taken at 22:24:06Z —
7m38s after the disable event (E13, E14) — showing the `GET /products` 503 counter
still at 1 (unchanged, across a real intervening traffic mix), `faultline_chaos_enabled`
still 0, `process_uptime_seconds` climbing continuously with no reset, and
`process_max_rss_bytes` unchanged.

**Judge, round 2 — validated.** The monotonic counters across the full interval (not
just two snapshots) closed the gap: zero new failures, zero new exceptions, no restart,
no memory growth. One adversarial note: the evidence description accompanying E13/E14
originally mis-stated the elapsed gap as "6m39s"; direct subtraction of the timestamps,
cross-checked independently against the uptime-vs-startup arithmetic, gives ~7m38s. This
was a self-description slip, not a data error, and it cuts in the hypothesis's favor
(the real gap checked was longer than claimed) — it does not change the verdict.

## Hypotheses

### H1 — internal chaos/degradation switch (validated)

Statement: the reported noise was a ~6.35-second chaos-switch window that
probabilistically injected one 503 on `GET /products`, now fully resolved.

Evidence for: E1–E14 — the enable/disable bracket (E1, E2, E5, E6), the single
chaos-tagged failure inside it (E3, E4), successful requests on the same route
immediately bracketing and following the failure (E7, E8, E9), the single startup
marker ruling out a restart (E12), and two widely-spaced health/metrics checks (E10,
E11, E13, E14) whose monotonic counters show no new failures, no new exceptions, and
no memory growth across the ~7.5-minute interval between them.

Evidence against: none found by either judge pass.

No other hypothesis was raised — all three triage lenses independently converged on
this one mechanism and found nothing else in their respective domains.

## Safe next steps

- If this toggle cadence is expected to recur, alerting directly on the
  `chaos_enabled`/`chaos_disabled` log events or on `faultline_chaos_enabled` flipping
  would surface the window at the moment it opens, rather than relying on a handover
  conversation to notice it after the fact.
- A future on-call read could extend the confirmed-clean window by taking one more
  `/health`/`/metrics` read later in the shift — read-only, no action needed unless the
  503 counter or `faultline_chaos_enabled` moves.

## Gaps

- Telemetry retention begins at process startup (E12); there are no rotated log
  backups, so nothing before 22:16:17.467Z is visible. This did not bite in this
  investigation — the complaint, the chaos episode, and the entire observed process
  lifetime all fall inside the window actually covered — but it is a structural limit
  of this lab instance worth naming for future handovers.
- "Clean since" rests on two point-in-time checks (~70s and ~7m38s after disable)
  bridged by counters that did not move between them, not on continuous monitoring. A
  transient condition entirely between the two checks that left no counter trace is
  theoretically possible but unevidenced.
