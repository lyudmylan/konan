---
konan_journal: 1
investigation:
  id: 2026-08-19-shop-wide-latency
  trigger: "manual (/konan human profile) — complaint object: source=human, fingerprint=human-1787143764, labels.alertname=human-report, no severity stated by reporter, startsAt=2026-08-19T12:49:24Z; investigation started 2026-08-19T12:49:31Z (trigger latency 7s)"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-19T12:49:31Z
  concluded: 2026-08-19T12:51:31Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Chaos mode was enabled at 12:49:08.218Z with extra_latency_ms=1500, which injects up to ~1.5 s of artificial delay into business endpoints while leaving /health unaffected — every shop path slowed by two to three orders of magnitude from that instant."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A chaos-mode configuration flag enabled at 12:49:08.218Z injects extra latency (extra_latency_ms=1500) into business request handling, causing shop-wide slowness; /health is exempt from the injection, so health checks stay green and fast."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "The reported error page was produced by server-side 5xx responses to user traffic during the slowness window."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E10, E11, E12]
  - id: H3
    statement: "Load saturation — request volume or memory pressure exceeded capacity and queued requests, producing shop-wide latency."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E13]
  - id: H4
    statement: "The one-off error page was a user hitting the zero-stock product detail path, which raises ZeroDivisionError and returns 500."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E14, E15]
    evidence_against: [E10, E11]
latent_findings:
  - statement: "GET /products/{id} returns 500 (ZeroDivisionError) for any product whose units_in_stock is 0 — turnover_score divides by stock without a zero guard. Product 3 (Unobtainium Ingot, units_in_stock 0) reproduces it deterministically. In this window only the investigator's own probe triggered it; no user request in the log reached that path."
    evidence: [E14, E15, E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:49:08.218Z"
    quote: '{"ts": "2026-08-19T12:49:08.218Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "9e4dca57e724", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:49:03.013Z (pre-chaos baseline)"
    quote: '{"ts": "2026-08-19T12:49:03.013Z", ... "message": "GET /products -> 200", "request_id": "7830c21d5df7", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.217, "client": "127.0.0.1:60750"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:49:11.145Z (post-chaos, user traffic)"
    quote: '{"ts": "2026-08-19T12:49:11.145Z", ... "message": "GET /products -> 200", "request_id": "986f8f47de6e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 862.49, "client": "127.0.0.1:60755"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:49:05.148Z (pre-chaos baseline)"
    quote: '{"ts": "2026-08-19T12:49:05.148Z", ... "message": "POST /orders -> 201", "request_id": "81ffaf1fad93", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 2.19, "client": "127.0.0.1:60752"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:49:16.837Z (post-chaos, user traffic)"
    quote: '{"ts": "2026-08-19T12:49:16.837Z", ... "message": "POST /orders -> 201", "request_id": "f98df3fa8340", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1369.208, "client": "127.0.0.1:60758"}'
  - id: E6
    type: probe
    source: "/products, request_id=konan-1787143814-59628 (67 s after chaos enabled)"
    quote: "-- HTTP 200 in 0.649496s request_id=konan-1787143814-59628"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:49:42.787Z (post-chaos /health)"
    quote: '{"ts": "2026-08-19T12:49:42.787Z", ... "message": "GET /health -> 200", "request_id": "konan-1787143782-59599", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.524, "client": "127.0.0.1:60783"}'
  - id: E8
    type: probe
    source: "/health, request_id=konan-1787143782-59599"
    quote: '{"status":"ok","uptime_seconds":40.54754125000909}'
  - id: E9
    type: metric
    source: "/metrics @ request_id=konan-1787143842-59673"
    quote: "faultline_chaos_enabled 1"
  - id: E10
    type: metric
    source: "/metrics @ request_id=konan-1787143783-59605 (first scrape, before any investigator probe of /products/3; http_exceptions_total carries its header lines and no series, and every http_requests_total series on this scrape is status 200 or 201)"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n# HELP faultline_chaos_enabled Whether chaos mode is active."
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:49:02.251Z (process lifecycle; log covers the whole process life, no rotated backups present)"
    quote: '{"ts": "2026-08-19T12:49:02.251Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E12
    type: metric
    source: "/metrics @ request_id=konan-1787143842-59673 (uptime 100.2 s)"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 2\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 4\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2"
  - id: E13
    type: metric
    source: "/metrics @ request_id=konan-1787143842-59673"
    quote: "process_max_rss_bytes 47497216\nprocess_uptime_seconds 100.19850237504579"
  - id: E14
    type: probe
    source: "/products/3, request_id=konan-1787143829-59658"
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787143829-59658"}\n-- HTTP 500 in 0.110354s request_id=konan-1787143829-59658'
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:50:29.823Z (stack trimmed to the raising frame)"
    quote: '{"ts": "2026-08-19T12:50:29.823Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787143829-59658", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}'
  - id: E16
    type: probe
    source: "/products, request_id=konan-1787143814-59628 (catalog body)"
    quote: '{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0}'
gaps:
  - "No telemetry exists before the process start at 2026-08-19T12:49:02.251Z (E11): lab/logs/ holds only app.log, with no .1-.3 rotated backups. An error page a user saw before that instant is outside all available evidence, which is why H4 cannot be closed."
  - "Chaos configuration history is not on the investigator surface (/chaos is operator surface, refused by probe.sh). Only the single chaos_enabled marker (E1) shows the parameters in force; an earlier chaos window with a non-zero failure_rate, before this process started, cannot be excluded."
  - "No client-side or edge telemetry. Whether the injected ~0.6-1.5 s delay caused a browser or proxy timeout that rendered an error page to a user cannot be tested from the service surface — this is the second unexcluded mechanism for the reported error page."
  - "Triage lenses (software-defect, infra-process, interfaces) and the adversarial judge ran inline in the orchestrator context, not as blind parallel subagents: this session was run under a no-subagent constraint. The lens independence and the judge firewall that normally guard against narrative capture were therefore not in force; the domains were covered, the blindness was not."
  - "User requests are unstamped by design (docs/lab.md), so user impact is counted by exclusion of konan-* request ids rather than by a positive user identifier; per-user impact counts are not available."
usage:
  model: claude-opus-5
  tokens: 695685
  wall_clock_seconds: 120
---

# Shop-wide latency from an enabled chaos flag; the reported error page is unexplained

## Summary

**Root cause identified.** At `2026-08-19T12:49:08.218Z` chaos mode was enabled on
faultline with `extra_latency_ms: 1500` (E1). From that instant every business endpoint
slowed by two to three orders of magnitude: `/products` went from 1.2 ms to 862 ms
(E2 -> E3), `POST /orders` from 2.2 ms to 1369 ms (E4 -> E5). The flag is still on
(`faultline_chaos_enabled 1`, E9) and the effect is still live — an investigator probe
67 seconds later took 649 ms (E6). `/health` is exempt from the injection and answered
in 0.524 ms during the same window (E7, E8), which is exactly why health checks look
green while the shop is painful: this is the healthy-monitoring trap, not a monitoring
fault.

The complaint's second half does **not** resolve. The chaos configuration in force
carries `failure_rate: 0.0` (E1) — it injects delay, not errors — and no user request
in the entire life of this process returned 5xx (E10, E12). The only 500 in the
telemetry is the investigator's own probe (E14, E15). Two mechanisms for the reported
error page survive and neither can be tested from here: a request before the process
started at 12:49:02.251Z (no logs exist for that period, E11), or a client- or
proxy-side timeout caused by the injected delay. Confidence in the latency root cause
is high; the error page is honestly unexplained.

Separately and not part of this incident: `GET /products/{id}` returns 500 for any
zero-stock product (E14, E15, E16). Only the investigator triggered it — it is a latent
defect, and a real one.

## Timeline

- `12:49:02.251Z` — process start, faultline 0.1.0 (E11). All telemetry available to
  this investigation begins here.
- `12:49:03.013Z` - `12:49:05.148Z` — healthy baseline: `/products` 1.217 ms (E2),
  `POST /orders` 2.19 ms (E4).
- `12:49:08.218Z` — **configuration change marker**: `chaos mode enabled`,
  `failure_rate 0.0`, `error_status 503`, `extra_latency_ms 1500` (E1).
- `12:49:11.145Z` — `/products` 862.49 ms (E3). Slowness begins with the flag, not before.
- `12:49:16.837Z` — `POST /orders` 1369.208 ms (E5); checkout is the worst-hit path.
- `12:49:24Z` — complaint raised by a human (trigger `startsAt`), 16 s after the flag flip.
- `12:49:42.787Z` — `/health` 0.524 ms while the shop is slow (E7).
- `12:50:15.286Z` — investigator probe `/products` 649 ms (E6): still degraded, ~67 s in.
- `12:50:29.823Z` — investigator probe of `/products/3` raises ZeroDivisionError (E15):
  latent defect, investigator-triggered.

## Investigation

Baseline first: `/health` (E8), a `/metrics` scrape (E10), and the full log tail. The
log covers the process's entire life (E11), so the baseline and the incident sit in one
continuous record — a rare luxury, and the reason the before/after latency comparison
is decisive rather than suggestive.

Triage covered three lens domains — infra-process (configuration and lifecycle),
software-defect (business-path failures), interfaces (contract and status behavior).
They ran inline rather than as blind parallel subagents, under this session's
no-subagent constraint; the loss of independence is recorded under Gaps rather than
glossed. Infra-process returned the `chaos_enabled` marker immediately (E1) with a
clean step change in latency across it — deterministic enough to skip a deep-dive and
go to the judge, per the skill's rule that deep-dives fill evidence gaps rather than
re-prove.

The deep-dive effort went instead to what the marker does **not** explain. The chaos
config injects no errors (`failure_rate: 0.0`), so the reported error page needed its
own hypothesis; probing the product catalog for data-dependent failures found the
zero-stock 500 (E14). That probe is investigator traffic, and its request id is stamped
`konan-*` — it is a latent finding, not the incident, and the journal counts it as such.

The judge pass (also inline) attacked H1 on two fronts: could the slowness be load
rather than injection, and is the flag correlation causal? Volume refutes load
outright — 16 requests across 100 s and flat RSS (E12, E13). Causality rests on the
step change at the marker plus a confirmed prediction: probe the shop 67 s later and
it must still be slow while `/health` stays fast; it was (E6 vs E7).

## Hypotheses

### H1 — chaos-mode latency injection (validated)

`extra_latency_ms: 1500` enabled at 12:49:08.218Z (E1), still on at scrape time (E9).
Every business path crosses the marker with a two-to-three order of magnitude step:
`/products` 1.217 ms -> 862.49 ms (E2, E3), `POST /orders` 2.19 ms -> 1369.208 ms
(E4, E5). Observed delays vary (146 ms to 1369 ms), consistent with a randomized
injection bounded at 1500 ms rather than a fixed penalty. `/health` does not cross the
step (E7, E8) — the injection spares it, which reproduces the reporter's "health checks
are green and fast" precisely. No evidence against.

### H2 — the error page came from server-side 5xx to users (invalidated)

The chaos config in force injects delay only (`failure_rate: 0.0`, E1). The first
metrics scrape shows `http_exceptions_total` with no series at all and no non-2xx
`http_requests_total` entries (E10), and the log covers the whole process life (E11).
The single 500 that exists arrived later and carries an investigator request id
(E12, E14). Within everything this investigation can observe, no user saw a
server-generated error page.

### H3 — load saturation (invalidated)

16 requests across 100 s of uptime, peak RSS 47.5 MB flat (E12, E13). There is no load
here to saturate. Recorded because "whole shop slow" is the classic saturation
complaint shape and killing it cheaply was worth one metrics read.

### H4 — the error page was the zero-stock product 500 (inconclusive)

The defect is real and deterministic (E14, E15, E16), and it is the only user-reachable
500 known to exist on this surface — a plausible fit for "an error page once". But no
user request to `/products/3` appears anywhere in the log (E10, E11), and the log cannot
see before 12:49:02.251Z. Settling it needs one piece of evidence this surface cannot
give: a request record from before process start. The competing mechanism — a client or
proxy timeout under the injected 1.5 s delay — is equally untested for the same reason.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. Ask the reporters for the approximate wall-clock time and the page or product they
   were on when the error appeared. That single fact discriminates H4 from the
   timeout mechanism, and both from a pre-12:49:02 event.
2. Confirm with whoever operates the target whether the chaos flag flip at
   12:49:08.218Z was intended and by whom — the flag is operator surface, and the
   marker records only that it happened, not who requested it.
3. If any edge, proxy, or browser telemetry exists outside this surface, check it for
   client-side timeouts in the 12:49:08Z onward window — that is where a
   latency-induced error page would be recorded, and it is the gap this surface
   cannot close.
4. Track the zero-stock 500 (E14, E15) as its own defect against the target's repo.
   It is deterministic, user-reachable, and independent of the chaos flag: it will
   outlive this incident.

## Gaps

- **No pre-12:49:02.251Z telemetry.** `lab/logs/` holds only `app.log`, no rotated
  backups (E11). The reported error page may predate every record available, which is
  what keeps H4 open.
- **Chaos history is not visible.** `/chaos` is operator surface and `probe.sh` refuses
  it. Only the one `chaos_enabled` marker (E1) shows parameters; an earlier chaos window
  with a non-zero failure rate cannot be excluded.
- **No client-side or edge telemetry.** A timeout-rendered error page would leave no
  trace on the service surface, so that mechanism is untestable from here.
- **Lens independence was not in force.** Triage lenses and the judge ran inline in the
  orchestrator's context under a no-subagent session constraint. The domains were
  covered; the blindness that guards against narrative capture was not. On a
  less clear-cut incident this would materially weaken the conclusion.
- **User traffic is unstamped by design** (`docs/lab.md`), so user impact is established
  by excluding `konan-*` request ids rather than by a positive user identifier.
