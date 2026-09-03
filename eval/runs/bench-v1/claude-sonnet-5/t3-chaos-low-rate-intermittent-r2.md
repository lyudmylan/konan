---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-intermittent-503s
  trigger: manual
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-08-19T03:01:23Z
  concluded: 2026-08-19T03:06:32Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos/fault-injection mode was toggled on (POST /chaos/enable, failure_rate 0.08, error_status 503) at 03:01:12.249Z, causing a probabilistic ~8% 503 rate on /orders and /products/{id} routes interleaved with successes on the same routes and inputs."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos-injected fault mode (failure_rate 0.08, error_status 503) is the cause of the intermittent 503s users are seeing."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E14]
    evidence_against: []
  - id: H2
    statement: "Process instability or resource saturation (infra-process domain) is contributing to the errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E4, E5, E6, E10, E11, E12]
  - id: H3
    statement: "A deterministic per-input software defect (e.g. a specific product ID always failing, or an unhandled exception) is causing the errors."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E8, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:01:12.249Z"
    quote: '{"ts": "2026-08-19T03:01:12.249Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "0110ea4dfe06", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:01:12.249Z"
    quote: '{"ts": "2026-08-19T03:01:12.249Z", "message": "POST /chaos/enable -> 200", "request_id": "0110ea4dfe06", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.552}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:01:13.383Z"
    quote: '{"ts": "2026-08-19T03:01:13.383Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "d3e8730592be", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.151}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:01:13.527Z"
    quote: '{"ts": "2026-08-19T03:01:13.527Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "61f2f09473f0", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.14}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:01:13.541Z"
    quote: '{"ts": "2026-08-19T03:01:13.541Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "4668605ecc25", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 0.152}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:01:13.598Z"
    quote: '{"ts": "2026-08-19T03:01:13.598Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "27ff125af40a", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:01:13.513Z"
    quote: '{"ts": "2026-08-19T03:01:13.513Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "63aa3f885b97", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.412}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T03:01:13.685Z"
    quote: '{"ts": "2026-08-19T03:01:13.685Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "d4d2254b02d7", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.438}'
  - id: E9
    type: metric
    source: "GET /metrics via scripts/probe.sh, request_id konan-1787108513-40751, 2026-08-19T03:01:53.873Z"
    quote: "faultline_chaos_enabled 1"
  - id: E10
    type: metric
    source: "GET /metrics via scripts/probe.sh, request_id konan-1787108513-40751, 2026-08-19T03:01:53.873Z (process_uptime_seconds 46.58)"
    quote: "process_max_rss_bytes 47202304"
  - id: E11
    type: metric
    source: "GET /metrics via scripts/probe.sh, request_id konan-1787108775-40896, 2026-08-19T03:06:15Z (process_uptime_seconds 307.85)"
    quote: "process_max_rss_bytes 47202304"
  - id: E12
    type: log
    source: "lab/logs/app.log — full file (57 lines), single occurrence @ 2026-08-19T03:01:07.301Z"
    quote: '{"ts": "2026-08-19T03:01:07.301Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E13
    type: metric
    source: "GET /metrics via scripts/probe.sh, request_id konan-1787108513-40751, 2026-08-19T03:01:53.873Z"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n(no data series follow — zero unhandled exceptions recorded)"
  - id: E14
    type: metric
    source: "GET /metrics via scripts/probe.sh, request_id konan-1787108513-40751, 2026-08-19T03:01:53.873Z"
    quote: 'http_requests_total{method="GET",path="/orders",status="503"} 1 / http_requests_total{method="GET",path="/products/1",status="503"} 1 / http_requests_total{method="GET",path="/products/2",status="503"} 1 / http_requests_total{method="GET",path="/products/5",status="503"} 1'
gaps:
  - "Caller identity for the POST /chaos/enable call (request_id 0110ea4dfe06, client 127.0.0.1:55296) is not recoverable from this surface — the log has no auth/principal field, only a loopback address. Whether the toggle was an intended scenario action or a misdirected call cannot be determined from telemetry alone; the causal mechanism (chaos → 503s) is settled regardless."
  - "Only one incident window (03:01:13Z, ~22 requests, 4 failures) has been observed. Chaos mode remains enabled (faultline_chaos_enabled=1) as of the last check (03:06:15Z) but no further business traffic has hit the service since, so the current real-world impact rate cannot be re-confirmed beyond that single burst."
usage:
  model: claude-sonnet-5
  tokens: 3499438
  wall_clock_seconds: 309
---

# Intermittent 503s on /orders and /products/{id} traced to chaos mode being enabled

## Summary

**Root cause identified.** At 03:01:12.249Z, fault-injection ("chaos") mode was enabled
on the target with an 8% failure rate returning HTTP 503 (E1, E2). Starting one second
later, 4 of roughly 22 requests across `/orders`, `/products/1`, `/products/2`, and
`/products/5` returned 503, each immediately preceded by an explicit `chaos_failure` log
line, interleaved with normal 200/201 responses on the same routes and even the same
input (E3–E8). This matches the reported symptom precisely: occasional errors, success
on retry, most users unaffected (8% is low enough that most single requests succeed).
No process instability, resource growth, or per-input code defect was found (H2, H3
invalidated) — RSS was identical (47,202,304 bytes) across a ~260-second window (E10,
E11), there was exactly one clean startup with no restarts (E12), and the one route/input
that failed once (`/products/1`) also served 200s immediately before and after the same
input (E7, E8, E6) with zero unhandled exceptions ever recorded (E13). Confidence: high
on the causal mechanism; the one open question is who/what triggered the toggle, which
this surface cannot answer (see Gaps).

## Timeline

- **03:01:07.301Z** — process startup, clean, single occurrence (E12).
- **03:01:12.249Z** — `POST /chaos/enable` returns 200; `chaos_enabled` log line shows
  `failure_rate: 0.08, error_status: 503, extra_latency_ms: 0` (E1, E2). This is the
  config-change marker.
- **03:01:13.382–383Z** — first failure: `GET /orders` → chaos_failure → 503 (E3), 1.13s
  after the toggle.
- **03:01:13.427–13.772Z** — burst of ~22 requests on `/products`, `/products/1`,
  `/products/2`, `/products/5`, `/orders`, `POST /orders`; 3 more chaos-tagged 503s land
  in this window on `/products/2` (E4), `/products/5` (E5), `/products/1` (E6), each
  sandwiched between 200s on the same route/input (E7, E8).
- **03:01:53.873Z** — baseline `/metrics` scrape: `faultline_chaos_enabled 1`,
  `process_max_rss_bytes 47202304`, zero exception series (E9, E10, E13, E14).
- **03:06:15Z** (approx, request_id konan-1787108775-40896) — follow-up `/metrics`
  scrape: RSS unchanged at 47,202,304 bytes after ~260s (E11); no new 503s recorded
  (request counters unchanged since the initial burst).

## Investigation

1. **Baseline** — `/health` (200 OK), `/metrics` snapshot, and the full `lab/logs/app.log`
   tail were read first. The chaos-toggle marker and the matching 503 pattern were
   already visible at this stage.
2. **Triage (3 lenses, parallel, blind to each other)** — infra-process, interfaces,
   software-defect, each given only the lens file, the surface contract, the complaint,
   and the baseline summary above.
   - infra-process: no lifecycle/latency/saturation anomaly found; flagged that only one
     RSS sample existed at that point (a real gap, later closed — see below).
   - interfaces: confirmed the config-change marker, the gateway-shaped probabilistic
     failure rate matching the declared 0.08, and no contract violations.
   - software-defect: no per-input determinism, no exception-counter activity; the
     4 failures span 4 different routes/inputs, each of which also served 200s.
3. **Deep-dive skipped** — H1's triage evidence was already deterministic and complete
   (an explicit, timestamped config-change log line whose declared parameters
   quantitatively match the observed failure pattern), so per protocol it went straight
   to the judge rather than a redundant deep-dive round.
4. **Judge (adversarial, evidence-only)** — validated H1's causal claim, but correctly
   flagged that "deliberately enabled" oversteps what the log alone proves (no caller
   identity available — recorded as a gap, not a blocker to the causal verdict). The
   judge also caught that a second `/metrics` scrape existed in the log that hadn't been
   pulled into evidence, which would settle H2's saturation question. That scrape was
   fetched (E11): RSS flat, H2 fully invalidated.

## Hypotheses

### H1 — Chaos-injected failures (validated)

Enabling chaos mode (E1, E2) is followed, within 1.1s, by 503s appearing exactly where
and at roughly the rate the toggle declared (E3–E6, E14: 4 total 503s, matching a ~18%
observed rate on a small sample against a configured 8% rate — consistent given only
~22 requests). Every failing route also served successes on the same input around the
same second (E7, E8), which is the signature of probabilistic injected degradation, not
a deterministic bug or a failing dependency. No evidence contradicts this hypothesis.

### H2 — Process instability / saturation (invalidated)

No restart or crash markers anywhere in the 57-line log (E12) — only one startup.
Latency stayed sub-millisecond throughout, including for the 503 responses themselves
(E3–E6 show 0.128–0.152ms durations — fast rejections, not stalls). RSS was identical
(47,202,304 bytes) at uptime 46.58s and again at uptime 307.85s (E10, E11) — flat across
a 260-second window, ruling out a leak or growth trend in the observed period.

### H3 — Deterministic per-input software defect (invalidated)

The clearest disproof: `GET /products/1` returned 200 at 03:01:13.513Z (E7), 503 at
03:01:13.598Z (E6), and 200 again at 03:01:13.685Z (E8) — same input, three different
outcomes within 172ms, which a per-input code defect cannot produce. `http_exceptions_total`
carries zero series (E13) — no unhandled exception has ever incremented it. The 4
failures are spread across 4 different routes/inputs rather than repeating on one.

## Safe next steps

- Re-scrape `/metrics` after some elapsed time to confirm chaos mode has since been
  turned off (`faultline_chaos_enabled` should read 0) and no further business impact
  has accumulated.
- If the elevated error rate persists or recurs, correlate future `chaos_enabled` /
  `chaos_disabled` log markers against whatever schedule or trigger owns them, to
  confirm this is expected/bounded rather than a runaway toggle.
- No read-only telemetry check can identify the caller of `POST /chaos/enable`; if that
  matters, it needs to be answered outside this surface (e.g. whoever owns the chaos
  toggle for this environment).

## Gaps

- Caller identity for the `POST /chaos/enable` call (request_id `0110ea4dfe06`, client
  `127.0.0.1:55296`) is not recoverable from this surface — the log has no auth/principal
  field, only a loopback address. Whether the toggle was an intended scenario action or a
  misdirected call cannot be determined from telemetry alone; the causal mechanism
  (chaos → 503s) is settled regardless.
- Only one incident window (03:01:13Z, ~22 requests, 4 failures) has been observed.
  Chaos mode remains enabled (`faultline_chaos_enabled=1`) as of the last check
  (03:06:15Z) but no further business traffic has hit the service since, so the current
  real-world impact rate cannot be re-confirmed beyond that single burst.
