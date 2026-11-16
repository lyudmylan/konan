---
konan_journal: 2
investigation:
  id: 2026-11-15-handover-check-shop
  trigger: "manual — /konan human report; fingerprint human-1794772054; alertname human-report; no severity stated; startsAt 2026-11-15T19:47:34Z; trigger latency 13 s"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-15T19:47:47Z
  concluded: 2026-11-15T19:52:47Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "The earlier failures were injected by an operational switch inside the target (chaos mode), on from 19:46:58.200Z to 19:47:04.530Z with status 503 at rate 0.6; the switch is off now and injects no failures now."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10]
    evidence_against: []
  - id: H2
    statement: "An incident is active now for users: GET /products/3 raises an unhandled ZeroDivisionError and users receive HTTP 500."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E11, E12, E13, E14, E15]
    evidence_against: [E16, E8, E12, E13, E14]
  - id: H3
    statement: "The process crashed or restarted, and that restart is the earlier noise."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E17, E18]
    evidence_against: [E19, E20, E2, E3, E4]
latent_findings:
  - statement: "GET /products/3 fails every time with an unhandled ZeroDivisionError (HTTP 500): product 3 has units_in_stock 0 and the handler divides by it. Only investigator probes triggered it; no user request for product 3 is in the log."
    evidence: [E11, E12, E13, E14, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:46:58.200Z"
    quote: |-
      {"ts": "2026-11-15T19:46:58.200Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "9e62f342ae2a", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:46:59.252Z and 2026-11-15T19:46:59.253Z"
    quote: |-
      {"ts": "2026-11-15T19:46:59.252Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "47d055f2081d", "event": "chaos_failure", "method": "GET", "path": "/products"}
      {"ts": "2026-11-15T19:46:59.253Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "47d055f2081d", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.258, "client": "127.0.0.1:55872"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:47:00.307Z"
    quote: |-
      {"ts": "2026-11-15T19:47:00.307Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "333489450499", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
      {"ts": "2026-11-15T19:47:00.307Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "333489450499", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.262, "client": "127.0.0.1:55873"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:47:01.364Z"
    quote: |-
      {"ts": "2026-11-15T19:47:01.364Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "9ce5ccaa8dde", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-11-15T19:47:01.364Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "9ce5ccaa8dde", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.246, "client": "127.0.0.1:55874"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:47:03.475Z (inside the switch window, same path as E2)"
    quote: |-
      {"ts": "2026-11-15T19:47:03.475Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "f84abe460025", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.767, "client": "127.0.0.1:55876"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:47:04.530Z"
    quote: |-
      {"ts": "2026-11-15T19:47:04.530Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "a5822839b99e", "event": "chaos_disabled"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:47:24.584Z (first non-investigator request after E6)"
    quote: |-
      {"ts": "2026-11-15T19:47:24.584Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "106a608c0b9e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.816, "client": "127.0.0.1:55880"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:47:28.799Z (last non-investigator line; every later line carries a konan- request id)"
    quote: |-
      {"ts": "2026-11-15T19:47:28.799Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "9bf6fcfaeb32", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.754, "client": "127.0.0.1:55884"}
  - id: E9
    type: metric
    source: "/metrics @ request_id=konan-1794772208-21837 (about 2026-11-15T19:50:08Z)"
    quote: |-
      faultline_chaos_enabled 0
  - id: E10
    type: metric
    source: "/metrics @ request_id=konan-1794772208-21837 (about 2026-11-15T19:50:08Z); the complete http_requests_total family. The three status 503 series held the same values in the first scrape, request_id=konan-1794772073-21610"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 5
      http_requests_total{method="GET",path="/openapi.json",status="200"} 1
      http_requests_total{method="GET",path="/orders",status="200"} 4
      http_requests_total{method="GET",path="/orders/{order_id}",status="200"} 3
      http_requests_total{method="GET",path="/products",status="200"} 6
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 9
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
      http_requests_total{method="POST",path="/chaos/disable",status="200"} 1
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E11
    type: probe
    source: "/products @ request_id=konan-1794772086-21619 (body trimmed to product 3)"
    quote: |-
      {"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}
      -- HTTP 200 in 0.003646s request_id=konan-1794772086-21619
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:49:00.942Z (stack trimmed to its last frame; redaction: the local path prefix of the target checkout is replaced by <checkout>)"
    quote: |-
      {"ts": "2026-11-15T19:49:00.942Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794772140-21792", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:49:00.950Z"
    quote: |-
      {"ts": "2026-11-15T19:49:00.950Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794772140-21792", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.604, "client": "127.0.0.1:55926"}
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:49:07.894Z"
    quote: |-
      {"ts": "2026-11-15T19:49:07.894Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794772147-21812", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.635, "client": "127.0.0.1:55930"}
  - id: E15
    type: metric
    source: "/metrics @ request_id=konan-1794772208-21837 (about 2026-11-15T19:50:08Z)"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 2
  - id: E16
    type: metric
    source: "/metrics @ request_id=konan-1794772073-21610 (first scrape, 2026-11-15T19:47:53.871Z, after the last non-investigator request E8; the counter family has no series)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E17
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:46:54.350Z (line 3 of the file)"
    quote: |-
      {"ts": "2026-11-15T19:46:54.350Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E18
    type: probe
    source: "/health @ request_id=konan-1794772073-21605 (logged at 2026-11-15T19:47:53.294Z)"
    quote: |-
      {"status":"ok","uptime_seconds":58.95577654102817}
      -- HTTP 200 in 0.001332s request_id=konan-1794772073-21605
  - id: E19
    type: probe
    source: "/health @ request_id=konan-1794772209-21842 (about 2026-11-15T19:50:09Z)"
    quote: |-
      {"status":"ok","uptime_seconds":194.86512500001118}
      -- HTTP 200 in 0.001402s request_id=konan-1794772209-21842
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T19:46:54.350Z (line 1 of the file; the file holds one startup sequence only and has no rotated backups)"
    quote: |-
      {"ts": "2026-11-15T19:46:54.350Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [21452]", "color_message": "Started server process [\u001b[36m%d\u001b[0m]"}
  - id: E21
    type: probe
    source: "/orders @ request_id=konan-1794772087-21629"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T19:47:02.419+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T19:47:26.690+00:00"}]
      -- HTTP 200 in 0.001334s request_id=konan-1794772087-21629
gaps:
  - "The log starts at the process start, 19:46:54.350Z, with no rotated backups. Noise before that time is not visible on this surface."
  - "Who turned the chaos switch on and off, and why, is not visible: the switch state history is operator surface, outside the contract. The log shows the two events and a local client only."
  - "No non-investigator request arrived after 19:47:28.799Z. The healthy state from then on rests on investigator probes only."
  - "Order creation (POST) cannot be probed: the probe is GET-only. Its last evidence is the user order at 19:47:26.691Z. The effect of product 4's null price on an order is untested."
  - "The repo has three lens files (infra-process, interfaces, software-defect). Load, third-party and data-layer domains had no lens; the baseline showed 1 to 4 ms responses and a constant peak memory, and the lab has no database and no third party."
  - "lab/server.out (server stdout) is not in the surface contract's list and was not read."
  - "Token usage was not captured in this interactive session."
usage:
  model: claude-fable-5-2
  tokens: 1429524
  wall_clock_seconds: 300
---

# Handover check: no active incident; earlier 503s came from the chaos switch

## Summary

**No active incident.** The shop service is healthy now: health, products and orders
answer 200 in 1 to 4 ms (E18, E19, E11, E21), and the chaos gauge reads 0 (E9).

The earlier noise is explained. The target's internal chaos switch was on for 6.3
seconds, from 19:46:58.200Z to 19:47:04.530Z, with status 503 at rate 0.6 (E1, E6).
Three of the five user requests in that window failed with 503, and each failure
carries a `chaos_failure` line with the same request id (E2, E3, E4). No 503 exists
outside the window: the complete request counter family holds those three 503 series
only, and they did not move (E10). All five user requests after the switch-off
succeeded (E7, E8). Confidence: high, for what the surface shows.

One latent finding rides along: `GET /products/3` fails every time with an unhandled
`ZeroDivisionError`, because product 3 has zero stock (E11–E14). Only investigator
probes triggered it (E15, E16), so it is not the noise and not an active incident —
but the first user who opens product 3 gets a 500.

The log starts at the process start (19:46:54.350Z). Noise before that time cannot be
seen here (see Gaps).

## Timeline

All times UTC, 2026-11-15.

- 19:46:54.350 — process start, one startup sequence (E17, E20).
- 19:46:55–19:46:56 — four user requests, all 200.
- 19:46:58.200 — **chaos mode enabled**: failure rate 0.6, status 503, no added latency (E1).
- 19:46:59.253 — `GET /products` → 503, chaos-injected (E2).
- 19:47:00.307 — `GET /products/2` → 503, chaos-injected (E3).
- 19:47:01.364 — `GET /products/1` → 503, chaos-injected (E4).
- 19:47:02.420 — `POST /orders` → 201 (order 1, E21); 19:47:03.475 — `GET /products` → 200 (E5).
- 19:47:04.530 — **chaos mode disabled** (E6).
- 19:47:24.584–19:47:28.799 — five user requests, all 200 or 201 (E7, E8). Last user traffic in the log.
- 19:47:34 — complaint raised; 19:47:47 — investigation start.
- 19:47:53 — baseline: health ok, uptime 58.96 s; no exception series (E18, E16).
- 19:49:00.942 and 19:49:07.892 — investigator probes of `/products/3` → 500, `ZeroDivisionError` (E12, E13, E14).
- 19:50:08 — final scrape: chaos gauge 0, 503 counters unchanged, uptime continuous (E9, E10, E19).

## Investigation

Complaint object, as synthesized by the manual trigger:

```json
{
  "source": "human",
  "fingerprint": "human-1794772054",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report." },
  "startsAt": "2026-11-15T19:47:34Z"
}
```

Investigation start: 2026-11-15T19:47:47Z (trigger latency 13 s). `KONAN_ADAPTER` was
unset, so the surface contract is `docs/lab.md`.

- **Baseline.** `/health` 200; `/metrics` snapshot; the log tail (28 lines, one
  startup, one chaos on/off pair, three 503s, no exception). Business surface:
  `/products`, `/products/1`, `/orders` all 200.
- **Triage.** The complaint is vague, so all three lenses ran in parallel:
  infra-process, interfaces, software-defect. Infra-process and interfaces each
  reported the chaos window as closed and found nothing else (no restart, no
  latency or memory drift, no 502/504, no contract violation). Software-defect
  found the `/products/3` failure with its own probes and confirmed the 503s are
  not a code defect.
- **Deep-dive.** None. The triage evidence for each hypothesis was deterministic and
  complete, so the hypotheses went straight to the judge.
- **Judge.** H1 validated; H2 invalidated as worded (the defect is real, the user
  impact is not in the evidence); H3 invalidated. The judge asked for the complete
  list of 503 series; E10 now quotes the whole counter family.

## Hypotheses

### H1 — chaos switch injected the earlier 503s; off now (validated)

E1 and E6 bound the window and give the rate and the status. Each of the three 503s
sits inside the window and has a `chaos_failure` line with the same request id (E2,
E3, E4). The same path that failed at 19:46:59 succeeded at 19:47:03 inside the
window (E5), which fits a probabilistic switch and not a per-input defect; 3 of 5
failed against a configured 0.6. After the switch-off every request succeeded (E7,
E8), the gauge reads 0 (E9), and the counter family holds no other 503 series (E10).
Class `infra-process`: an internal switch, although the status looks gateway-shaped.
The verdict stays `no-active-incident` because the switch is off.

### H2 — users are failing now on `/products/3` (invalidated)

The defect itself is real and deterministic: product 3 has `units_in_stock` 0 (E11),
the handler divides by it (E12), and two probes gave two 500s (E13, E14). But both
exceptions carry investigator request ids, the exception counter equals those two
probes (E15), and it had no series after the last user request (E16, E8). No user
request for product 3 is in the log. The claim survives only as a latent finding.
What would settle it: one non-investigator log line for `GET /products/3`.

### H3 — a crash or restart is the noise (invalidated)

The process started 59 s before the first probe (E17, E18), which made a restart
worth testing. The log holds one startup sequence (E20), uptime grew continuously
between the two health probes (E18, E19), and every failure is tied to the chaos
switch, 5 s or more after the start (E2, E3, E4). A single start is not a restart.
Limit: the log cannot show an earlier process life.

## Safe next steps

Read-only suggestions only.

- Ask the previous shift who turned chaos mode on at 19:46:58Z, and whether it was a
  planned exercise. The telemetry shows the event, not the actor.
- Read the server stdout and any process supervisor record for the time before
  19:46:54Z, to learn whether "earlier" means before this process start.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` and the access log for a
  non-investigator `GET /products/3`. A rise above 2 means users hit the latent defect.
- Hand the latent finding (`/products/3`, zero stock, division in `get_product`) to
  the service owner as a defect report.
- Keep `faultline_chaos_enabled` on the handover checklist; a value of 1 reopens H1.

## Gaps

- **Before the process start.** The log begins at 19:46:54.350Z and has no rotated
  backups. If the reported noise happened before that, this surface cannot show it.
  The chaos window is the only failure the surface holds.
- **Actor and intent of the switch.** The switch's own state history is operator
  surface, outside the contract. The log shows the two events from a local client.
- **No user traffic after 19:47:28.799Z.** "Healthy now" rests on investigator probes
  for the rest of the investigation.
- **Order creation.** The probe is GET-only, so POST `/orders` was not exercised. Its
  last evidence is the user order at 19:47:26.691Z. Product 4 has a null price; its
  effect on an order is untested.
- **Lenses.** Only three lens files exist. Load, third-party and data-layer domains
  had no lens. The baseline gave no sign in those domains (fast responses, constant
  peak memory), and this lab has no database and no third party.
- **Server stdout.** `lab/server.out` is not listed in the surface contract and was
  not read.
- **Usage.** Tokens were not captured in this session.
