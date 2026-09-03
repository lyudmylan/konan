---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-injected-503s
  trigger: >-
    manual (human profile, /konan adapter) — complaint object:
    source=human, fingerprint=human-1787144021,
    labels.alertname=human-report (no severity stated by the reporter),
    startsAt=2026-08-19T12:53:41Z; investigation started 2026-08-19T12:53:49Z
    (trigger latency 8s)
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-08-19T12:53:49Z
  concluded: 2026-08-19T12:59:52Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change enabled chaos mode (failure_rate 0.08, error_status 503) at 12:53:34.280Z, after which a fraction of requests to every shop route were rejected with 503 before reaching handler code; the flag is still enabled."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A runtime configuration change enabled chaos mode (failure_rate 0.08, error_status 503); the service then short-circuited a fraction of requests to 503 independently of route, method or input."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E11, E12, E15, E16, E17, E18]
    evidence_against: []
  - id: H2
    statement: "An unhandled exception in a request handler causes the errors."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E3, E6, E7, E8, E14]
  - id: H3
    statement: "Load or resource saturation causes the errors."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E10, E11]
  - id: H4
    statement: "A data-dependent defect makes specific inputs (e.g. product 2) fail while others succeed."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E7, E8]
  - id: H5
    statement: "The process crashed or restarted, dropping in-flight requests."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E13]
latent_findings:
  - statement: "Metrics label the request path inconsistently between success and injected failure: 200s roll up under the templated path /products/{product_id} while the 503 recorded the literal path /products/2. Failures appear to be counted before route templating, which admits unbounded label cardinality on the error path and makes per-route error ratios uncomputable (numerator and denominator land in different series)."
    evidence: [E11, E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:34.280Z"
    quote: '{"ts": "2026-08-19T12:53:34.280Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "ab4ee700ec54", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: metric
    source: "/metrics via probe.sh, request_id konan-1787144046-59890, served 2026-08-19T12:54:06.621Z"
    quote: "faultline_chaos_enabled 1"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:35.481Z"
    quote: '{"ts": "2026-08-19T12:53:35.481Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "5745f6b4af5f", "event": "chaos_failure", "method": "GET", "path": "/products/2"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:35.481Z"
    quote: '{"ts": "2026-08-19T12:53:35.481Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "5745f6b4af5f", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.138, "client": "127.0.0.1:60827"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:35.567Z"
    quote: '{"ts": "2026-08-19T12:53:35.567Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "7feff825e08d", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.439, "client": "127.0.0.1:60833"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:35.524Z"
    quote: '{"ts": "2026-08-19T12:53:35.524Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "a02befb8b910", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:35.609Z"
    quote: '{"ts": "2026-08-19T12:53:35.609Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "ee545679142a", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:35.623Z"
    quote: '{"ts": "2026-08-19T12:53:35.623Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "08ef3188da19", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E9
    type: metric
    source: "/metrics via probe.sh, request_id konan-1787144384-60019"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n(no series emitted — zero unhandled exceptions for the whole process lifetime; no log line in app.log carries event unhandled_exception, an exception_type field, or a stack field)"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:29.297Z (the only startup marker in the file)"
    quote: '{"ts": "2026-08-19T12:53:29.297Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E11
    type: metric
    source: "/metrics via probe.sh, request_id konan-1787144384-60019"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/2\",status=\"503\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 2\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 6\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 18\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 4"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:32.207Z (last request before the chaos_enabled marker)"
    quote: '{"ts": "2026-08-19T12:53:32.207Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "fda4c1b5cc07", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.066, "client": "127.0.0.1:60817"}'
  - id: E13
    type: probe
    source: "/health, request_id konan-1787144041-59879"
    quote: '{"status":"ok","uptime_seconds":31.870067999931052}\n-- HTTP 200 in 0.003635s request_id=konan-1787144041-59879'
  - id: E14
    type: metric
    source: "/metrics via probe.sh, request_ids konan-1787144046-59890 and konan-1787144384-60019 (≈5.5 min apart)"
    quote: "process_max_rss_bytes 47169536 (identical in both scrapes); http_request_duration_seconds_sum/_count give sub-millisecond means on every route (e.g. /products/{product_id} 0.00906529207713902 / 18 = 0.50 ms). The four 503s are the fastest requests in the log at duration_ms 0.127–0.138, versus 0.38–0.77 ms for successes on the same routes."
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:34.281Z"
    quote: '{"ts": "2026-08-19T12:53:34.281Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "ab4ee700ec54", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.723, "client": "127.0.0.1:60818"}'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:53:35.809Z (last non-investigator request in the file)"
    quote: '{"ts": "2026-08-19T12:53:35.809Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "a8fa37724eb6", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.449, "client": "127.0.0.1:60850"}'
  - id: E17
    type: log
    source: "lab/logs/app.log, counted over 2026-08-19T12:53:29.297Z–12:53:35.809Z (whole non-investigator window)"
    quote: "Non-investigator requests before the chaos_enabled marker (12:53:34.280Z): 5, of which 0 failed. After the marker: 32, of which 4 failed — 12.5% observed. Every chaos_failure line falls after the marker; no failure of any kind precedes it."
  - id: E18
    type: metric
    source: "/metrics via probe.sh, request_id konan-1787144384-60019, at process_uptime_seconds 375.09 (≈2026-08-19T12:59:44Z)"
    quote: "faultline_chaos_enabled 1\nprocess_uptime_seconds 375.0878717910964\n(503 counters unchanged from the 12:54:06Z scrape: /products 1, /products/2 1, POST /orders 2. http_requests_total emits no 4xx or other 5xx series at all.)"
gaps:
  - "Attribution of the chaos_enable call is outside the investigator's surface. E15 shows POST /chaos/enable returning 200 to a loopback caller (request_id ab4ee700ec54), but the telemetry carries no caller identity, no auth outcome, and no change-management marker. Whether this was a sanctioned operator or eval action or an unexpected one cannot be settled from logs and metrics alone — and per docs/lab.md the /chaos surface is operator/eval-side, deliberately outside the probe allowlist, so the investigator cannot query its state directly."
  - "\"Real end users\" is not established, only \"not investigator traffic\". Investigator probes carry the konan- request-id prefix and none of the failing requests do; but E15 shows that non-konan traffic is not necessarily a shopper, and every client in the log is loopback (127.0.0.1, one contiguous ephemeral port block). The complaint asserts user reports; the telemetry corroborates non-investigator traffic receiving 503s, which is weaker."
  - "The configured failure_rate of 0.08 is recorded (E1) but not confirmed by observation. The observed 4/32 = 12.5% is statistically compatible with p=0.08 at n=32 (expected 2.56) but cannot verify the rate; the sample is too small."
  - "E5 shows the same path returning 200 86 ms after a 503, which proves the route is not deterministically broken — but it is a distinct request_id and is not provably the user's retry. The failure-selection mechanism (per-request roll vs time-windowed vs counter-based) is not determined by the available telemetry."
  - "Current user-facing exposure could not be measured: all non-investigator traffic stops at 12:53:35.809Z (E16), so the absence of new 503s after that point is a traffic gap, not evidence of recovery. Generating shop traffic to measure it is eval-side, not an investigator action."
  - "Only three lenses exist in this repo (infra-process, software-defect, interfaces); the taxonomy in the report contract also names third-party, data-db and load-saturation. Per docs/lab.md faultline has no database and no third-party dependency, so those domains have no surface to examine here; load-saturation was assessed from metrics directly rather than through a dedicated lens."
usage:
  model: claude-opus-5
  tokens: 1342627
  wall_clock_seconds: 363
---

# Occasional shop 503s from an enabled chaos-injection flag

## Summary

**Not nothing — and not resolved.** At 12:53:34.280Z a runtime configuration change
enabled faultline's chaos mode with `failure_rate: 0.08` and `error_status: 503` (E1).
From that moment a fraction of requests to every shop route were rejected with HTTP 503
before reaching handler code, independently of route, method or input. In the 6 seconds
of shop traffic that followed, 4 of 32 requests failed (E17) across `GET /products`,
`GET /products/2` and `POST /orders` twice (E3, E6, E7, E8) — including two failed
checkouts. Before the change, 5 requests and zero failures (E12, E17).

This explains the complaint precisely. "Occasional" is the per-request failure roll;
"works on retry" is the same route returning 200 moments after a 503 (E4 → E5); "most
people notice nothing" is a single-digit failure percentage. The reporter's instinct
that it was probably nothing is the one part that does not hold up.

**The flag is still enabled.** `faultline_chaos_enabled 1` at 12:59:44Z, six minutes
after the change, with no `chaos_disabled` event anywhere in the log and no TTL field in
the configuration (E18, E1). The reason no new 503s appear is that shop traffic stopped
at 12:53:35.809Z (E16) — a traffic gap, not a recovery. Any traffic that arrives now is
exposed at the same rate.

Confidence in the mechanism is high and rests on self-reporting rather than inference:
the service labels each failure `chaos_failure` (E3, E6, E7, E8), and the log and metrics
corroborate one-for-one — four `chaos_failure` events, four 503s in the counters (E11).
Confidence in *who* made the change is nil; that is outside the investigator's surface
and is the open question below.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 12:53:29.297Z | Process starts — the only startup marker in the file; uptime monotonic thereafter, so no restart in the window | E10 |
| 12:53:30.038Z–12:53:32.207Z | Normal baseline: 5 shop requests, 0 failures, sub-ms latency, order 1 created | E12, E17 |
| **12:53:34.280Z** | **Configuration change — chaos mode enabled, `failure_rate: 0.08`, `error_status: 503`, `extra_latency_ms: 0`** | **E1** |
| 12:53:34.281Z | The enabling call itself: `POST /chaos/enable -> 200` from a loopback client | E15 |
| 12:53:35.481Z | First user-visible failure — `GET /products/2 -> 503`, 1.2 s after the change | E3, E4 |
| 12:53:35.524Z | `POST /orders -> 503` — a failed checkout | E6 |
| 12:53:35.567Z | `GET /products/2 -> 200` — the same route succeeding 86 ms later | E5 |
| 12:53:35.609Z | `POST /orders -> 503` — a second failed checkout | E7 |
| 12:53:35.623Z | `GET /products -> 503` — the catalogue route, which takes no input | E8 |
| 12:53:35.809Z | Last shop request. Traffic stops; error counters freeze at 4 | E16, E18 |
| 12:53:41Z | Complaint raised by a human reporter | — |
| 12:54:06.621Z | First investigator metrics scrape — chaos flag still 1 | E2 |
| 12:59:44Z | Final scrape — chaos flag still 1, counters unchanged, no 4xx/5xx series beyond the four 503s | E18 |

## Investigation

**Baseline.** `/health` returned 200 (E13); `/metrics` showed `faultline_chaos_enabled 1`
and 503s spread across three route/method pairs; `lab/logs/app.log` was 54 lines covering
the entire process lifetime, so the window read was complete rather than sampled — no
rotated backups existed.

**Triage — three lenses in parallel, blind to each other.** infra-process, software-defect
and interfaces. Every lens whose domain the lab can exercise was spawned; the taxonomy's
remaining classes have no surface here (see Gaps). All three independently landed on the
same 12:53:34.280Z configuration marker, and the two that could have claimed the incident
for their own domain instead ruled themselves out: infra-process reported a clean process
lifecycle, and software-defect reported zero unhandled exceptions.

**Deep-dive — skipped deliberately.** The triage evidence was already deterministic and
complete: the service self-labels its injected failures, and the pre/post boundary at the
configuration marker is clean. Deep-dives exist to fill evidence gaps, not to re-prove
what the telemetry states outright, so the hypotheses went straight to the judge.

**Judge.** A fresh judge saw only the claim list and the verbatim evidence — no lens
reasoning, no narrative. It validated H1 as the proximate cause, invalidated H2–H5 on
direct negative evidence, and pushed back on four points, all of which changed this
report:

1. *"Retries succeed because the failure roll is per-request"* — overreach. E5 is a
   different request id, not provably the user's retry. Narrowed to what the evidence
   shows: the route is not deterministically broken. The selection mechanism is now a Gap.
2. *The 12.5% observed rate does not confirm the configured 0.08* — correct at n=32.
   The report no longer presents the observation as validating the configured rate.
3. *"Real users" was inferred from the absent `konan-` prefix* — and E15 shows non-konan
   traffic that is not a shopper either. Downgraded throughout to "non-investigator
   traffic", and recorded as a Gap.
4. *An unaccounted-requests gap suggesting a hidden second failure mode* — this one I
   could close. It came from an excerpt in the ledger I gave the judge, not from the
   service: the full scrape reconciles exactly (39 requests at the baseline scrape,
   accounting for the two pre-chaos `/health` calls, the operator call and the
   investigator's own probes), and `http_requests_total` emits **no 4xx or non-503 5xx
   series at all** (E18). No second failure mode is hiding behind this one.

The judge also flagged the reachable chaos control plane as the finding that needs an
owner. I have recorded that as a Gap rather than a finding: `docs/lab.md` establishes
`/chaos` as deliberate operator and eval surface in this lab, and I hold no evidence
about its authentication or exposure. Naming it a vulnerability would be speculation.

## Hypotheses

### H1 — Chaos-mode configuration change (**validated**) — the root cause

A runtime configuration change enabled probabilistic 503 injection across all routes.

*For:* the configuration event with its exact parameters (E1) and the call that set it
(E15); the flag observed set, twice, minutes apart (E2, E18); four failures the service
itself labels `chaos_failure` (E3, E6, E7, E8); a clean pre/post boundary — 0 failures in
5 requests before, 4 in 32 after (E12, E17); metrics matching the log one-for-one (E11);
and the mechanism signature in E14 — the 503s are the *fastest* requests in the file
(0.127–0.138 ms vs 0.38–0.77 ms for successes), i.e. rejected before the handler runs.

*Against:* nothing. The failure spread across two methods and three handlers, including
the parameterless `/products` collection route, rules out any single-handler explanation.

*Not claimed:* that the observed 12.5% confirms the configured 8%, that E5 is a retry of
E4, or that the change was unauthorised.

### H2 — Unhandled exception in a handler (**invalidated**)

`http_exceptions_total` has no series at all, and no log line carries
`unhandled_exception`, `exception_type` or `stack` (E9). All four failures are attributed
to chaos injection (E3, E6, E7, E8) and are sub-millisecond (E14), which is not how a
handler exception presents. This ruling covers unhandled exceptions in this window; a
*caught* defect returning 503 deliberately would leave no such trace. What would revive
it: a 5xx whose request id has no matching `chaos_failure` event.

### H3 — Load or resource saturation (**invalidated**)

Peak RSS is byte-identical across scrapes ~5.5 minutes apart, and all successful durations
are sub-millisecond (E14); traffic is ~32 requests over 6 seconds (E11, E17); no restart
(E10). Decisively, saturation makes failures *slower* — here they are the fastest requests
in the log. The signature is inverted. Honest limit: RSS is a weak saturation proxy and
the surface exposes no CPU, queue-depth or concurrency metric; the ruling rests mainly on
the inverted latency signature and on traffic volume far too low to saturate anything.

### H4 — Data-dependent defect on specific inputs (**invalidated**)

`GET /products/2` returned 503 at 12:53:35.481Z and 200 at 12:53:35.567Z, 86 ms later
(E4, E5) — the input is not deterministically fatal. `GET /products` (E8) takes no input
at all, and `POST /orders` failed twice with different payloads (E6, E7). "Most inputs
succeed, specific inputs fail" is a real defect shape, so this was worth testing; it is
not what happened here.

### H5 — Process crash or restart (**invalidated**)

One startup marker only (E10), `process_uptime_seconds` monotonic across four samples
(31.87 → 37.33 → 120.64 → 375.09) with no reset, cumulative counters never discontinuous,
and `/health` 200 on every attempt (E13, E18).

## Safe next steps

Read-only, in priority order:

1. **Confirm with the operator or eval owner whether the 12:53:34.280Z chaos enable was
   intentional** (E1, E15). This is the whole decision. If it was a sanctioned test, the
   incident is a scenario left running; if not, it is an unexplained control-plane call.
   The telemetry cannot answer it — the answer lives with whoever holds the operator
   surface.
2. **Treat the flag as live.** It has been on for six minutes with no disable event and
   no TTL (E1, E18). The quiet period is absent traffic, not recovery — anyone reading the
   error counters as "stable" is reading a stopped clock.
3. **Re-scrape `/metrics` for `faultline_chaos_enabled` and the 503 counters** to track
   whether the flag clears and whether exposure resumes when traffic returns.
4. **Note for whoever owns dashboards:** per-route error ratios on `/products/{id}` are
   currently uncomputable, because successes and injected failures land in different label
   series (latent finding, E11, E18). Alerting built on that ratio would not have fired.

Remediation — disabling the flag — is out of scope for this investigation and for the
investigator's surface.

## Gaps

- **Who enabled chaos, and whether it was authorised.** E15 records the call returning 200
  to a loopback client, but the surface carries no caller identity, auth outcome, or
  change-management marker, and `/chaos` is operator/eval surface the investigator may not
  probe (`docs/lab.md`). This is the single largest gap: the mechanism is settled, the
  provenance is not.
- **"Real end users" is not established** — only "not investigator traffic". The
  `konan-` prefix separates my probes from everything else, but E15 proves non-konan
  traffic need not be a shopper, and every client in the log is loopback within one
  contiguous port block. The complaint asserts user reports; the telemetry corroborates
  non-investigator traffic receiving 503s, which is a weaker claim, and this report makes
  only the weaker one.
- **The 0.08 failure rate is recorded, not verified.** 4/32 = 12.5% is compatible with
  p=0.08 at n=32 but cannot confirm it.
- **The failure-selection mechanism is undetermined.** E5 shows the route is not
  deterministically broken, but per-request roll, time-window and counter-based schemes
  are indistinguishable from this telemetry, and E5 is not provably a retry of E4.
- **Current exposure is unmeasured.** Shop traffic ends at 12:53:35.809Z (E16); generating
  more is an eval-side action, not an investigator one. The rate at which live users would
  fail right now is inferred from the still-set flag, not observed.
- **Lens coverage is narrower than the taxonomy.** Only infra-process, software-defect and
  interfaces lenses exist in this repo. Per `docs/lab.md` faultline has no database and no
  third-party dependency, so `data-db` and `third-party` have no surface to examine;
  `load-saturation` was assessed directly from metrics (H3) rather than through a
  dedicated lens, which is a thinner treatment than a lens would give.
