---
konan_journal: 1
investigation:
  id: 2026-08-25-intermittent-503s-chaos-failure-rate
  trigger: "manual (/konan, human profile; fingerprint human-1787634164; alertname human-report; no severity stated; startsAt 2026-08-25T05:02:44Z; investigation start 2026-08-25T05:02:58Z; trigger latency 14s)"
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-08-25T05:02:58Z
  concluded: 2026-08-25T05:08:18Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change at 05:02:35.027Z enabled chaos mode with failure_rate 0.08 and error_status 503 (extra_latency_ms 0), so about 8% of shop requests on any route are answered with a fast, injected 503 tagged chaos_failure while the next request on the same route succeeds — an occasional error that works on retry."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode enabled at 05:02:35.027Z (failure_rate 0.08, error_status 503, extra_latency_ms 0) injects a probabilistic ~8% 503 on every shop request; retries on the same route succeed; the gauge stays 1 and fresh probes still hit 503s, so the condition is active."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E24, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E20, E21]
    evidence_against: []
  - id: H2
    statement: "The users' occasional errors are unhandled exceptions from a code defect, such as the ZeroDivisionError in get_product for a product with units_in_stock 0 (/products/3)."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E17, E18, E19, E22]
    evidence_against: [E10, E24, E4, E7, E19, E20]
  - id: H3
    statement: "The errors come from a process crash/restart (connection refusals during restart) or from resource saturation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E25, E15, E16, E5, E8, E24, E21]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 with ZeroDivisionError in get_product (turnover_score divides units_ordered by units_in_stock; product 3 is the only product with units_in_stock 0). Only one investigator probe (konan-1787634293-37922) ever triggered it; no user request reached /products/3."
    evidence: [E17, E18, E19, E22, E24]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:35.027Z"
    quote: '{"ts": "2026-08-25T05:02:35.027Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "12a8f866394e", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:35.028Z"
    quote: '{"ts": "2026-08-25T05:02:35.028Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "12a8f866394e", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.738, "client": "127.0.0.1:65513"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:32.958Z (last user request before the change marker)"
    quote: '{"ts": "2026-08-25T05:02:32.958Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "718c6bdaa2f4", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.15, "client": "127.0.0.1:65511"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:36.268Z"
    quote: '{"ts": "2026-08-25T05:02:36.268Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "f09397db7eaa", "event": "chaos_failure", "method": "POST", "path": "/orders"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:36.268Z"
    quote: '{"ts": "2026-08-25T05:02:36.268Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "f09397db7eaa", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.138, "client": "127.0.0.1:65525"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:36.354Z (next user request on the same route after E5)"
    quote: '{"ts": "2026-08-25T05:02:36.354Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "502a507012a1", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 0.666, "client": "127.0.0.1:65531"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:36.454Z"
    quote: '{"ts": "2026-08-25T05:02:36.454Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "7b00e4a54415", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:36.454Z"
    quote: '{"ts": "2026-08-25T05:02:36.454Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "7b00e4a54415", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.132, "client": "127.0.0.1:49154"}'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:36.541Z (next user request on the same route after E8)"
    quote: '{"ts": "2026-08-25T05:02:36.541Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "ed4d219db74e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.405, "client": "127.0.0.1:49160"}'
  - id: E10
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787634189-37839 @ 2026-08-25T05:03:09Z (complete http_requests_total and http_exceptions_total sections, before any investigator probe of a shop route)"
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 3 / http_requests_total{method="GET",path="/orders",status="200"} 5 / http_requests_total{method="GET",path="/products",status="200"} 6 / http_requests_total{method="GET",path="/products",status="503"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 17 / http_requests_total{method="POST",path="/chaos/enable",status="200"} 1 / http_requests_total{method="POST",path="/orders",status="201"} 5 / http_requests_total{method="POST",path="/orders",status="503"} 1 / # HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter / # HELP faultline_chaos_enabled Whether chaos mode is active. / faultline_chaos_enabled 1'
  - id: E11
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787634338-37967 @ 2026-08-25T05:05:38Z"
    quote: "faultline_chaos_enabled 1"
  - id: E12
    type: probe
    source: "/products, request_id=konan-1787634325-37949 @ 2026-08-25T05:05:25Z"
    quote: '{"error":"service temporarily degraded","request_id":"konan-1787634325-37949"} -- HTTP 503 in 0.000903s request_id=konan-1787634325-37949'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:05:25.810Z"
    quote: '{"ts": "2026-08-25T05:05:25.810Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1787634325-37949", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:30.035Z (line 3 of the file; the only startup event; lab/logs/ holds app.log only, no rotated backups)"
    quote: '{"ts": "2026-08-25T05:02:30.035Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E15
    type: probe
    source: "/health, request_id=konan-1787634188-37833 @ 2026-08-25T05:03:08Z"
    quote: '{"status":"ok","uptime_seconds":38.73581974999979} -- HTTP 200 in 0.001935s request_id=konan-1787634188-37833'
  - id: E16
    type: metric
    source: "/metrics via scripts/probe.sh @ 2026-08-25T05:03:09Z (konan-1787634189-37839) and @ 2026-08-25T05:05:38Z (konan-1787634338-37967)"
    quote: "process_uptime_seconds 39.49051733291708 / process_uptime_seconds 188.48658249992877 / process_max_rss_bytes 47054848 / process_max_rss_bytes 47054848"
  - id: E17
    type: probe
    source: "/products/3, request_id=konan-1787634293-37922 @ 2026-08-25T05:04:53Z (software-defect lens)"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787634293-37922"} -- HTTP 500 in 0.010037s request_id=konan-1787634293-37922'
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:04:53.905Z (stack trimmed to its last frame)"
    quote: '{"ts": "2026-08-25T05:04:53.905Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787634293-37922", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n ... ZeroDivisionError: division by zero"}'
  - id: E19
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787634338-37967 @ 2026-08-25T05:05:38Z"
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1'
  - id: E20
    type: metric
    source: "/metrics via scripts/probe.sh, request_id=konan-1787634338-37967 @ 2026-08-25T05:05:38Z (complete http_requests_total section at conclusion)"
    quote: 'http_requests_total{method="GET",path="/health",status="200"} 5 / http_requests_total{method="GET",path="/metrics",status="200"} 4 / http_requests_total{method="GET",path="/orders",status="200"} 7 / http_requests_total{method="GET",path="/products",status="200"} 7 / http_requests_total{method="GET",path="/products",status="503"} 2 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 18 / http_requests_total{method="GET",path="/products/{product_id}",status="500"} 1 / http_requests_total{method="POST",path="/chaos/enable",status="200"} 1 / http_requests_total{method="POST",path="/orders",status="201"} 5 / http_requests_total{method="POST",path="/orders",status="503"} 1'
  - id: E21
    type: probe
    source: "/orders, request_id=konan-1787634325-37955 @ 2026-08-25T05:05:25Z"
    quote: "-- HTTP 200 in 0.001348s request_id=konan-1787634325-37955"
  - id: E22
    type: probe
    source: "/products, request_id=konan-1787634285-37909 @ 2026-08-25T05:04:45Z (response body excerpt, software-defect lens)"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
  - id: E23
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:36.555Z (the last request line with a non-konan request id in the file)"
    quote: '{"ts": "2026-08-25T05:02:36.555Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "bcff33c2a9d2", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.46, "client": "127.0.0.1:49161"}'
  - id: E24
    type: log
    source: "lab/logs/app.log, count over all request lines with 12-hex-char (non-konan) request ids between 2026-08-25T05:02:30.795Z and 05:02:36.555Z, excluding the POST /chaos/enable line (E2)"
    quote: "before E1: 5 requests, all status 200/201 (GET /health x2, GET /products, GET /products/1, POST /orders); after E1: 32 requests, 30 with status 200/201 and 2 with status 503 (E5, E8); all 32 have duration_ms below 3; every GET /products/{id} among them is /products/1, /products/2 or /products/5; no line with event unhandled_exception or status 500 carries a non-konan request id"
  - id: E25
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:02:30.034Z (line 1 of the file; color_message field trimmed)"
    quote: '{"ts": "2026-08-25T05:02:30.034Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [37674]"}'
gaps:
  - "The log and the process both begin at 05:02:30.034Z (E25, E14); nothing before that instant is on this surface. If the users' 'last few minutes' started earlier, an error from a previous process (or a connection refusal during its restart, which leaves no app.log line) cannot be confirmed or refuted here."
  - "No user traffic exists after 05:02:36.555Z (E23); the 6.25% user error rate rests on 32 requests (E24), and persistence after that time is shown by the gauge (E11) and investigator probes (E12, E13) only."
  - "Who or what issued POST /chaos/enable from 127.0.0.1:65513 (E2), and whether the change was intended, is on the operator surface and outside the read-only contract."
  - "The decisive counterfactual (disable chaos and observe zero 503s) is a mutation and outside the read-only boundary."
  - "No CPU, thread, or connection gauges exist on /metrics; saturation is excluded only by peak RSS (E16, a peak value, not current usage), monotonic uptime (E15, E16) and sub-3 ms durations (E24, E5, E8, E21)."
  - "Retry by the same client is an interpretation: E6 and E9 show the next request on the same route succeeding from a different client port, not a retry by the client that received the 503."
  - "POST /orders cannot be exercised read-only; the injected 503 on the order path is seen in user traffic (E4, E5) but not reproduced by a probe."
  - "The journal frontmatter was not machine-validated against journal.schema.json in this session: the validator command needed a permission prompt that an unattended run cannot answer; shape was checked by hand."
usage:
  model: claude-fable-5
  tokens: 1862184
  wall_clock_seconds: 320
---

# Intermittent shop 503s after chaos mode was enabled with an 8% failure rate

## Summary

**Verdict: root cause identified (H1, incident class: interfaces — runtime configuration change). This is not nothing.** At 05:02:35.027Z a `chaos_enabled` marker was logged with `failure_rate: 0.08`, `error_status: 503`, `extra_latency_ms: 0` (E1), raised by a `POST /chaos/enable` from `127.0.0.1:65513` (E2). Before the marker, all 5 user requests succeeded (E3, E24). After it, 2 of 32 user requests (6.25%) were answered with a fast 503 (0.13 ms), one on `POST /orders` (E4, E5) and one on `GET /products` (E7, E8); each 503 is paired with a `chaos_failure` event with the same request id, and the next request on the same route succeeded (E6, E9). The gauge `faultline_chaos_enabled` read 1 at 05:03:09Z and still at 05:05:38Z (E10, E11), and an investigator probe of `/products` at 05:05:25Z got the same injected 503 (E12, E13) while `/orders` returned 200 in the same second (E21). Impact: every shop route (products, product detail, orders — reads and order creation) for every user since 05:02:35.027Z, at roughly 1 request in 12; no latency change and no data corruption signal. Confidence: high — one logged change marker 1.2 s before the first user 503, a status split of 0/5 before vs 2/32 after, explicit `chaos_failure` tags on every user error, the gauge still on, and a fresh reproduction; the judge validated H1 with no evidence against it.

The complaint's framing ("works on retry, most people notice nothing") is exactly what an 8% per-request failure injection looks like from the outside. The failure is active and will keep hitting about 8% of shop requests — including order creation — until the configuration is changed.

A separate, latent defect rode along: `GET /products/3` returns 500 with `ZeroDivisionError` in `get_product` because product 3 has `units_in_stock: 0` (E17, E18, E22). Only one investigator probe triggered it (E19, E20, E24). It is not the incident.

## Timeline

- 05:02:30.034Z — process start: `Started server process [37674]` (E25); `faultline 0.1.0 started` at 05:02:30.035Z (E14). The log begins here.
- 05:02:30.795Z–05:02:32.958Z — user traffic normal: 5 requests, all 200/201, durations 0.9–16.8 ms (E24); last known-good `POST /orders -> 201` at 05:02:32.958Z (E3).
- **05:02:35.027Z — change marker: `chaos mode enabled`, `failure_rate: 0.08`, `error_status: 503`, `extra_latency_ms: 0` (E1); `POST /chaos/enable -> 200` from `127.0.0.1:65513` (E2).**
- 05:02:36.268Z — first known-bad: `chaos-injected failure` on `POST /orders` (E4) → `POST /orders -> 503` in 0.138 ms (E5); next `POST /orders -> 201` at 05:02:36.354Z (E6).
- 05:02:36.454Z — second: `chaos-injected failure` on `GET /products` (E7) → `GET /products -> 503` in 0.132 ms (E8); next `GET /products -> 200` at 05:02:36.541Z (E9).
- 05:02:36.555Z — last user request in the log, `GET /products/1 -> 200` (E23). After the marker: 32 user requests, 30 × 2xx, 2 × 503 (E24).
- 05:02:44Z — complaint raised (`startsAt`); 05:02:58Z — investigation start (trigger latency 14 s).
- 05:03:08Z–05:03:09Z — baseline: `/health` 200 in 1.9 ms, uptime 38.7 s (E15); metrics show exactly one 503 series per failed route, no exception series, `faultline_chaos_enabled 1` (E10).
- 05:04:45Z–05:04:53Z — software-defect lens: `/products` lists product 3 with `units_in_stock: 0` (E22); `/products/3` → 500 `ZeroDivisionError` (E17, E18). Latent, konan-* only.
- 05:05:25Z — orchestrator probe `/products` → injected 503 (E12), paired `chaos_failure` (E13); `/orders` → 200 in 1.3 ms (E21).
- 05:05:38Z — conclusion snapshot: `faultline_chaos_enabled 1` (E11), uptime 188.5 s monotonic, peak RSS unchanged at 47054848 (E16), `/products` 503 count now 2 (users' one plus E12), the only 500 is the one investigator probe (E19, E20).

## Investigation

- **Baseline** (orchestrator): `/health`, `/metrics`, the full log (53 lines at the time), then `/products` and `/orders` for the business surface. The log already held the chaos marker and two `chaos_failure` events; health fast; no exceptions; the `/products` probe itself drew an injected 503.
- **Triage** — three lenses in parallel, blind to each other: infra-process, interfaces, software-defect. Each triage prompt carried the four prescribed items plus a short block of mechanical boundary rules (one probe per command, relative paths, no git, no operator-surface strings in commands) — added because the session's boundary tripwire is session-wide and a subagent denial would freeze the investigation. No command was denied. Findings converged: a single change marker at 05:02:35.027Z with 0/5 errors before and 2/32 after, both tagged `chaos_failure`, same routes succeeding around them (interfaces); one startup, monotonic uptime, flat peak RSS, sub-3 ms durations, 503s fast not slow (infra-process); no user-facing exception, and a latent deterministic `/products/3` 500 triggered only by the lens's own probe (software-defect).
- **Deep-dive**: none spawned. H1's triage evidence was deterministic and complete (marker + before/after counts + paired `chaos_failure` tags + gauge + fresh reproduction), so it went straight to the judge; H2 and H3 were already contradicted by complete log and metrics scans.
- **Judge** (fresh agent, evidence-only, no tools): H1 validated; H2 invalidated; H3 invalidated for the observed window with a named blind spot before 05:02:30Z. The judge's evidence flags are folded in: E24 (not E3) carries the "no errors before the marker" claim; E6/E9 are "next request on the same route succeeded", not a proven client retry; `process_max_rss_bytes` is a peak, not current RSS; the unquoted log line 1 is now E25. All of these are recorded under Gaps.
- **Boundary note**: no target-touching command was denied. Two orchestrator-side commands did not run: a compound shell command for journal validation was rejected by a harness shape check (braces with quotes), and a `perl -i` edit of the journal needed a permission prompt. Neither touched the target; the journal was fixed with the file editor and validated by hand (see Gaps).

## Hypotheses

### H1 — injected 503s from the chaos configuration change (validated)

Statement: chaos mode enabled at 05:02:35.027Z with `failure_rate 0.08` and `error_status 503` answers about 8% of shop requests with a fast 503; the rest succeed; nothing else changes. For: the marker and its request (E1, E2); 0/5 user errors before, 2/32 after (E3, E24); each user 503 paired with a `chaos_failure` event under the same request id (E4+E5, E7+E8); the same route succeeding right after (E6, E9); metrics showing exactly those two 503s and no exception series before any investigator touched a shop route (E10); the gauge still 1 at conclusion (E11); a fresh investigator 503 with its own `chaos_failure` pair (E12, E13) while `/orders` succeeded in the same second (E21); counters consistent with the log at conclusion (E20). Against: none. Across users and probes, 3 injected 503s in 38 shop requests (7.9%) sits on the configured rate.

### H2 — the errors are unhandled exceptions from a code defect (invalidated)

The defect is real: product 3 has `units_in_stock: 0` (E22) and `GET /products/3` divides by it in `get_product` (E17, E18). But the user errors are 503s tagged `chaos_failure` (E4, E5, E7, E8), not 500s; no exception series and no 500 series existed before any investigator probe (E10); no user request went to `/products/3` (E24); and at conclusion the single `ZeroDivisionError` and single 500 equal the one investigator probe (E19, E20). Kept as a latent finding.

### H3 — process crash/restart or resource saturation (invalidated for the observed window)

One process start at 05:02:30.034Z–.035Z (E25, E14); uptime monotonic 38.7 s → 188.5 s, peak RSS unchanged at 47054848 (E15, E16); the 503s completed in 0.13 ms (E5, E8) and every user request under 3 ms (E24); `/orders` 200 in 1.3 ms at 05:05:25Z (E21). The process that answered the baseline counted the pre-marker user requests (E10 vs E24), so no restart happened inside the window. What happened before 05:02:30.034Z is not on this surface (Gaps).

## Safe next steps

- Read-only: identify who or what issued `POST /chaos/enable` at 05:02:35.028Z from `127.0.0.1:65513` (E2) — an operator action, a stale scenario, or an unintended trigger; that answer settles whether the change was intended.
- Read-only: keep watching `faultline_chaos_enabled` and the `status="503"` series on `/products` and `POST /orders`; a `chaos_disabled` event followed by flat 503 counters would confirm the mechanism end to end.
- Read-only: ask the reporters for the time of their first error; if it predates 05:02:30.034Z, it belongs to a previous process whose log is not on this surface.
- Do not read `/health` as "the shop is fine" here: `/health` and `/metrics` never drew an injected 503 across 9 investigator calls (E10, E20), while `/products` did (E12).
- Latent: `/products/3` (zero stock) 500s deterministically on the `turnover_score` division (E18); product 4 has `price: null` and returns 200 on the read path (software-defect lens), but the order path for both inputs is untested.

## Gaps

- **Nothing before 05:02:30.034Z.** The log and the process both begin there (E25, E14); no rotated backups exist. A previous process's errors or restart-time connection refusals cannot be confirmed or refuted.
- **Small user sample, no user traffic after 05:02:36.555Z (E23).** The 6.25% rate rests on 32 requests (E24); persistence is shown by the gauge (E11) and konan-* probes (E12, E13).
- **Change origin unknown.** The operator surface behind `POST /chaos/enable` (E2) is outside the read-only contract.
- **No counterfactual.** Disabling chaos is a mutation and outside the boundary.
- **No CPU/thread/connection gauges.** Saturation is excluded by peak RSS (E16), uptime and durations only.
- **"Retry" is interpretive.** E6 and E9 show the next request on the same route from a different client port, not the same client retrying.
- **Order path not probeable.** The injected 503 on `POST /orders` is seen in user traffic (E4, E5) but cannot be reproduced read-only.
- **No machine validation of the frontmatter in this session.** The validator needed a permission prompt; the shape (schema keys, E-id resolution, `root_cause` → validated H1, `wall_clock_seconds` = 320 = 05:08:18Z − 05:02:58Z, id = filename) was checked by hand.
