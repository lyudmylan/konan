---
konan_journal: 2
investigation:
  id: 2026-11-15-intermittent-503s
  trigger: |-
    manual — /konan human report. Complaint object:
    {"source": "human", "fingerprint": "human-1794745164", "labels": {"alertname": "human-report"}, "annotations": {"summary": "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."}, "startsAt": "2026-11-15T12:19:24Z"}
    Investigation start: 2026-11-15T12:19:36Z (trigger latency 12 s).
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-15T12:19:36Z
  concluded: 2026-11-15T12:23:12Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The chaos switch inside the service was turned on at 2026-11-15T12:19:08.145Z with failure_rate 0.4 and error_status 503; while it is on, the service injects 503 responses at random into business requests (product pages, order list, order creation), and it is still on."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the service was turned on at 12:19:08.145Z (failure_rate 0.4, error_status 503) and injects 503 responses at random into business requests while on."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17, E18, E19]
    evidence_against: []
  - id: H2
    statement: "The service's own code raises an unhandled exception on specific inputs, and those requests fail."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E6, E10]
    evidence_against: [E5, E9, E15, E16, E18, E19]
  - id: H3
    statement: "The process crashes or restarts in a loop, and requests fail while it is down or starting."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E20]
    evidence_against: [E21, E22, E18, E23]
  - id: H4
    statement: "A dependency or gateway tier at the edge of the service fails and returns 503 for part of the traffic."
    incident_class: interfaces
    state: invalidated
    evidence_for: [E6, E8, E10, E12]
    evidence_against: [E1, E5, E7, E9, E11, E13, E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:08.145Z"
    quote: '{"ts": "2026-11-15T12:19:08.145Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "f82a456b865e", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:08.146Z"
    quote: '{"ts": "2026-11-15T12:19:08.146Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "f82a456b865e", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 3.492, "client": "127.0.0.1:51547"}'
  - id: E3
    type: metric
    source: "/metrics @ 2026-11-15T12:19:37Z (request_id=konan-1794745177-94348) and @ 12:21:06Z (request_id=konan-1794745266-94456), same value both reads"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:05.066Z (last request before the switch marker)"
    quote: '{"ts": "2026-11-15T12:19:05.066Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "f3d8c1e212c2", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.756, "client": "127.0.0.1:51546"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:11.244Z"
    quote: '{"ts": "2026-11-15T12:19:11.244Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "788fcff013d1", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:11.244Z (first 5xx in the log)"
    quote: '{"ts": "2026-11-15T12:19:11.244Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "788fcff013d1", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.406, "client": "127.0.0.1:51549"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:16.512Z"
    quote: '{"ts": "2026-11-15T12:19:16.512Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "5299014844d9", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:16.512Z"
    quote: '{"ts": "2026-11-15T12:19:16.512Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "5299014844d9", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.282, "client": "127.0.0.1:51554"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:17.561Z"
    quote: '{"ts": "2026-11-15T12:19:17.561Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "056eb9c91f80", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:17.561Z"
    quote: '{"ts": "2026-11-15T12:19:17.561Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "056eb9c91f80", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.275, "client": "127.0.0.1:51555"}'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:18.613Z (two lines, same request id)"
    quote: |-
      {"ts": "2026-11-15T12:19:18.613Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "342aaed524db", "event": "chaos_failure", "method": "GET", "path": "/orders"}
      {"ts": "2026-11-15T12:19:18.613Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "342aaed524db", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.269, "client": "127.0.0.1:51556"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:19.668Z"
    quote: '{"ts": "2026-11-15T12:19:19.668Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 503", "request_id": "ac55b76cd1d5", "event": "request", "method": "GET", "path": "/products/4", "status": 503, "duration_ms": 0.307, "client": "127.0.0.1:51557"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:19.668Z"
    quote: '{"ts": "2026-11-15T12:19:19.668Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "ac55b76cd1d5", "event": "chaos_failure", "method": "GET", "path": "/products/4"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:20:39.034Z (investigator probe of /orders; two lines, same request id)"
    quote: |-
      {"ts": "2026-11-15T12:20:39.034Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794745239-94440", "event": "chaos_failure", "method": "GET", "path": "/orders"}
      {"ts": "2026-11-15T12:20:39.034Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "konan-1794745239-94440", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.181, "client": "127.0.0.1:51588"}
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:01.946Z (product 1 before the switch marker)"
    quote: '{"ts": "2026-11-15T12:19:01.946Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "f3b3a9a65a42", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 2.774, "client": "127.0.0.1:51543"}'
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:20:38.038Z and 12:20:38.541Z (investigator probes of the two product ids that failed earlier)"
    quote: |-
      {"ts": "2026-11-15T12:20:38.038Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "konan-1794745238-94430", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.598, "client": "127.0.0.1:51586"}
      {"ts": "2026-11-15T12:20:38.541Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794745238-94435", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.455, "client": "127.0.0.1:51587"}
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:13.345Z (an order that succeeded after the switch marker)"
    quote: '{"ts": "2026-11-15T12:19:13.345Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "eed9517b5155", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.013, "client": "127.0.0.1:51551"}'
  - id: E18
    type: metric
    source: "/metrics @ 2026-11-15T12:21:06Z (request_id=konan-1794745266-94456), the complete http_requests_total family"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="503"} 2
      http_requests_total{method="GET",path="/products",status="200"} 3
      http_requests_total{method="GET",path="/products/1",status="503"} 2
      http_requests_total{method="GET",path="/products/4",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 6
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E19
    type: metric
    source: "/metrics @ 2026-11-15T12:21:06Z (request_id=konan-1794745266-94456), the exception counter section: it holds no series, the next line is the next metric"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:00.052Z (the only startup event in the file)"
    quote: '{"ts": "2026-11-15T12:19:00.052Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E21
    type: probe
    source: "/health @ 2026-11-15T12:19:36Z, request_id=konan-1794745176-94343"
    quote: |-
      {"status":"ok","uptime_seconds":36.77656670799479}
      -- HTTP 200 in 0.011784s request_id=konan-1794745176-94343
  - id: E22
    type: metric
    source: "/metrics @ 2026-11-15T12:21:06Z (request_id=konan-1794745266-94456)"
    quote: "process_uptime_seconds 126.32598887523636"
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-11-15T12:19:36.814Z and 12:20:28.585Z (health requests after the switch marker)"
    quote: |-
      {"ts": "2026-11-15T12:19:36.814Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794745176-94343", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 3.022, "client": "127.0.0.1:51576"}
      {"ts": "2026-11-15T12:20:28.585Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1794745228-94402", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.495, "client": "127.0.0.1:51584"}
  - id: E24
    type: metric
    source: "/metrics @ 2026-11-15T12:19:37Z (request_id=konan-1794745177-94348) and @ 12:21:06Z (request_id=konan-1794745266-94456), same value both reads"
    quote: "process_max_rss_bytes 48889856"
gaps:
  - "Nothing before 2026-11-15T12:19:00.051Z is visible: the log holds one process lifetime and has no rotated backups. The complaint says 'a few minutes ago'; the telemetry onset is 12:19:08.145Z, 16 s before the complaint stamp. An earlier process lifetime with the same symptom cannot be checked."
  - "Who or what turned the switch on is unknown: the access line (E2) shows only a local client address, and the operator surface of the switch is outside the investigator's contract. The live settings of the switch are known only from the marker (E1) and the gauge (E3)."
  - "Small sample: 10 non-investigator requests after the marker, 5 failed. The observed rate (0.5) agrees with the configured 0.4 only loosely."
  - "Whether /health is exempt from injection is not proven: 2 of 2 health requests after the marker returned 200 (E23)."
  - "Order bodies are not in the log, so 'the same order fails and then succeeds' is shown for the route POST /orders only (E8, E17), not for one identical input."
  - "No load-saturation lens exists in this skill; saturation was checked only through the infra-process lens (durations in low milliseconds, flat peak memory, E24)."
  - "Token totals were not captured (interactive-style session with subagents)."
usage:
  model: claude-fable-5-2
  tokens: 1302649
  wall_clock_seconds: 216
---

# Intermittent 503s on product pages and orders — chaos switch is on

## Summary

**Root cause identified.** The chaos switch inside the service was turned on at
2026-11-15T12:19:08.145Z with `failure_rate 0.4` and `error_status 503` (E1, E2), and it
is still on (E3). While on, the service injects 503 responses at random into business
requests. Every 5xx in the telemetry is a 503 (E18), and each one has a paired
`chaos_failure` log line with the same request id (E5–E14). Class `infra-process`,
cause `degradation-switch`.

Impact on users (non-investigator traffic only): 5 of 10 business requests after the
marker failed, across `GET /products/1`, `GET /products/4`, `GET /orders` and
`POST /orders` (E6, E8, E10, E11, E12). The same routes succeed on other attempts (E16,
E17), which is the "works again on retry" of the complaint. `/health` stays 200 (E21,
E23), which is why the dashboard is green. Confidence: high — the mechanism is logged by
the service itself and the judge validated it; the limits are the short window and the
small sample (see Gaps).

## Timeline

- 12:19:00.052Z — the service starts; the only startup event (E20).
- 12:19:01.946Z — `GET /products/1 -> 200` (E15). Six requests before the marker, none failed.
- 12:19:05.066Z — last request before the marker, `GET /products/2 -> 200` (E4).
- **12:19:08.145Z — switch marker: `chaos mode enabled`, `failure_rate 0.4`, `error_status 503`, by `POST /chaos/enable -> 200` from a non-investigator request (E1, E2).**
- 12:19:11.244Z — first 5xx: `GET /products/1 -> 503`, with `chaos-injected failure` (E5, E6).
- 12:19:13.345Z — `POST /orders -> 201` succeeds (E17).
- 12:19:16.512Z — `POST /orders -> 503`, injected (E7, E8).
- 12:19:17.561Z — `GET /products/1 -> 503`, injected (E9, E10).
- 12:19:18.613Z — `GET /orders -> 503`, injected (E11).
- 12:19:19.668Z — `GET /products/4 -> 503`, injected (E12, E13).
- 12:19:24Z — the complaint arrives; 12:19:36Z — the investigation starts; `/health` 200, uptime 36.8 s (E21).
- 12:19:37Z — gauge `faultline_chaos_enabled 1` (E3).
- 12:20:38Z — investigator probes of `/products/1` and `/products/4` return 200 (E16).
- 12:20:39.034Z — investigator probe of `/orders` returns 503, injected (E14).
- 12:21:06Z — gauge still 1 (E3); uptime 126.3 s, no reset (E22); all 5xx series are 503 (E18); exception counter empty (E19).

## Investigation

- **Baseline** (12:19:36Z–12:19:37Z): `/health` 200; `/metrics` snapshot with four 503
  series, the gauge `faultline_chaos_enabled 1` and an empty exception counter; the log
  tail, 32 lines, one process lifetime.
- **Triage**: three lenses in parallel, blind to each other — infra-process,
  software-defect, interfaces. All three reported the same switch marker and the paired
  injection lines. The software-defect lens found no exception and no per-input failure,
  and reproduced: products 1 and 4 returned 200, `/orders` returned an injected 503. The
  infra-process lens found one startup, continuous uptime, no saturation. The interfaces
  lens found a sharp onset at the marker and no contract or dependency failure.
- **Deep-dive**: skipped. The triage evidence for H1 was deterministic and complete
  (every failure carries the injection marker), so it went straight to the judge.
- **Judge** (evidence only): H1 validated; H2, H3, H4 invalidated. The judge corrected
  two references of the draft list (H2 cited a product 4 line as product 1; the startup is
  8 s before the marker, 11 s before the first 503). Both corrections are applied here.
- One round, no deep-dive agents; budget not exhausted.

## Hypotheses

### H1 — chaos switch on (infra-process) — validated

The marker (E1) and its request (E2) put the change at 12:19:08.145Z. No 5xx exists
before it (E4, E15 and the other pre-marker requests are 2xx); the first 5xx comes 3 s
after it (E6). All six 503 access lines in the log (five from users, one from an
investigator probe) have a `chaos_failure` line with the same request id (E5–E14), and
the six agree with the metric counts (E18). The same routes both fail and succeed after
the marker (E6/E10 vs E16; E8 vs E17). The gauge reads 1 on both reads (E3). No
exception exists (E19). No evidence against was found.

### H2 — unhandled exception on specific inputs (software-defect) — invalidated

For: product 1 failed two times (E6, E10). Against: both failures carry injection lines
(E5, E9); product 1 returned 200 before the marker and again later (E15, E16); no status
500 exists (E18); the exception counter holds no series (E19).

### H3 — crash or restart loop (infra-process) — invalidated

For: a startup marker 8 s before the switch marker (E20). Against: it is the only
startup; uptime runs without a reset from 36.8 s to 126.3 s (E21, E22); the counters keep
all six failures (E18); `/health` answers 200 (E23).

### H4 — failing dependency or gateway tier (interfaces) — invalidated

For: gateway-shaped status 503 on part of the traffic (E6, E8, E10, E12). Against: each
503 carries the service's own injection line (E5, E7, E9, E11, E13); the marker names
503 as the configured status (E1); no 502 or 504 exists (E18); the failed requests took
under 0.5 ms, so there was no upstream wait. Limit: the service log cannot show a 503
from a tier in front of the service; no telemetry shows such a tier.

## Safe next steps

- Ask the operator of the switch whether the enable at 12:19:08.145Z (request id
  `f82a456b865e`) was intended.
- Keep reading the gauge `faultline_chaos_enabled` and the log for a `chaos_disabled`
  event; after it, check that the 503 series in `http_requests_total` stop growing.
- Read the business routes, not only `/health`, when judging health: `/health` stayed
  200 through the whole incident (E21, E23).

## Gaps

- **Window.** The telemetry starts at 12:19:00.051Z with the process; there are no
  rotated logs. The complaint says "a few minutes ago", the telemetry shows an onset 16 s
  before the complaint stamp. An earlier lifetime of the service cannot be checked.
- **Who turned the switch on.** The access line shows a local client address only (E2).
  The operator surface is outside the investigator's contract, so the settings of the
  switch are known only from the marker and the gauge.
- **Sample.** 10 user requests after the marker, 5 failed; this agrees with the
  configured 0.4 only loosely.
- **Health and injection.** 2 of 2 health requests after the marker returned 200; that
  does not prove `/health` is exempt.
- **Orders.** Order bodies are not logged; fail-then-succeed is shown for the route, not
  for one identical order.
- **Saturation.** No load-saturation lens exists; the infra-process lens checked it
  (low-millisecond durations, flat peak memory, E24).
- **Tokens.** Not captured.
