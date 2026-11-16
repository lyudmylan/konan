---
konan_journal: 2
investigation:
  id: 2026-11-15-chaos-switch-503
  trigger: "manual — /konan human report (profile: human). Complaint object: source=human, fingerprint=human-1794766528, labels.alertname=human-report, no severity stated, startsAt=2026-11-15T18:15:28Z. Investigation start 2026-11-15T18:15:35Z; trigger latency 7 s."
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-15T18:15:35Z
  concluded: 2026-11-15T18:19:43Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An operational chaos switch inside the target was turned on at 2026-11-15T18:15:10.017Z (failure_rate 0.4, error_status 503); while it is on, the target itself answers a random share of requests on the business routes with an injected HTTP 503, and it was still on at 18:17:09Z."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target was turned on at 2026-11-15T18:15:10.017Z with failure_rate 0.4 and error_status 503; while on, the target injects HTTP 503 on a random share of requests across the business routes; the switch is still on."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E19, E20, E21, E22, E24, E28, E29]
    evidence_against: []
  - id: H2
    statement: "The shop's own code raises an unhandled exception on specific inputs (specific product ids or order payloads), and those requests fail."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E7, E8, E9, E17, E18]
  - id: H3
    statement: "The process crashes or restarts in a loop, and requests fail around each restart."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E25]
    evidence_against: [E2, E3, E21, E26, E27]
  - id: H4
    statement: "A proxy or gateway tier in front of the shop produces the 503 responses on its own."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E19, E20, E21]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:10.017Z"
    quote: '{"ts": "2026-11-15T18:15:10.017Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "f83b4b7d3cc5", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:04.909Z"
    quote: '{"ts": "2026-11-15T18:15:04.909Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "d92994d42012", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.988, "client": "127.0.0.1:54725"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:06.962Z (last request line before E1; all 7 request lines between startup and E1 have status 200 or 201)"
    quote: '{"ts": "2026-11-15T18:15:06.962Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "d7ba535cd21f", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.788, "client": "127.0.0.1:54726"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:10.018Z"
    quote: '{"ts": "2026-11-15T18:15:10.018Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "f83b4b7d3cc5", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.713, "client": "127.0.0.1:54727"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:12.070Z"
    quote: '{"ts": "2026-11-15T18:15:12.070Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "cd8a988f856c", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:12.070Z"
    quote: '{"ts": "2026-11-15T18:15:12.070Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "cd8a988f856c", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.288, "client": "127.0.0.1:54728"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:03.854Z"
    quote: '{"ts": "2026-11-15T18:15:03.854Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "95266ece1764", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.034, "client": "127.0.0.1:54724"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:13.120Z and 18:15:13.121Z (two lines, same request id)"
    quote: |-
      {"ts": "2026-11-15T18:15:13.120Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "88a23cafb840", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
      {"ts": "2026-11-15T18:15:13.121Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "88a23cafb840", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.296, "client": "127.0.0.1:54729"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:19.450Z"
    quote: '{"ts": "2026-11-15T18:15:19.450Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "7f30be321375", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.806, "client": "127.0.0.1:54736"}'
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:14.175Z (two lines, same request id)"
    quote: |-
      {"ts": "2026-11-15T18:15:14.175Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e50917d7a6f9", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
      {"ts": "2026-11-15T18:15:14.175Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "e50917d7a6f9", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.254, "client": "127.0.0.1:54730"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:15.228Z and 18:15:15.229Z (two lines, same request id)"
    quote: |-
      {"ts": "2026-11-15T18:15:15.228Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "2d7f7ddd059c", "event": "chaos_failure", "method": "POST", "path": "/orders"}
      {"ts": "2026-11-15T18:15:15.229Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "2d7f7ddd059c", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.257, "client": "127.0.0.1:54731"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:16.284Z"
    quote: '{"ts": "2026-11-15T18:15:16.284Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "d585a7f641c4", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.772, "client": "127.0.0.1:54732"}'
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:17.342Z (two lines, same request id)"
    quote: |-
      {"ts": "2026-11-15T18:15:17.342Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "162aa4e16375", "event": "chaos_failure", "method": "GET", "path": "/products/5"}
      {"ts": "2026-11-15T18:15:17.342Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "162aa4e16375", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 0.418, "client": "127.0.0.1:54733"}
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:18.395Z (two lines, same request id)"
    quote: |-
      {"ts": "2026-11-15T18:15:18.395Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "f1a8bc39004b", "event": "chaos_failure", "method": "POST", "path": "/orders"}
      {"ts": "2026-11-15T18:15:18.395Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "f1a8bc39004b", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.265, "client": "127.0.0.1:54735"}
  - id: E15
    type: metric
    source: "/metrics read at 2026-11-15T18:15:47Z (request id konan-1794766547-15747); every status=503 series in the scrape"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 2
  - id: E16
    type: metric
    source: "/metrics read at 2026-11-15T18:15:47Z (konan-1794766547-15747) and again at 2026-11-15T18:17:09Z (konan-1794766629-15853); same line both times"
    quote: "faultline_chaos_enabled 1"
  - id: E17
    type: metric
    source: "/metrics read at 2026-11-15T18:15:47Z and 2026-11-15T18:17:09Z; the exceptions counter has its HELP and TYPE lines and no series line, the next line is the HELP of the next metric"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E18
    type: log
    source: "lab/logs/app.log, whole file read (38 lines, 2026-11-15T18:15:02.055Z to 18:17:00.913Z); absence observation, not a quoted line"
    quote: 'lines with "event": "unhandled_exception" = 0; lines with a "stack" field = 0; request lines with a 5xx status other than 503 = 0'
  - id: E19
    type: probe
    source: "/orders, request id konan-1794766619-15834 (investigator request; one of five read-only requests sent 18:16:58Z–18:17:00Z, the other four returned 200)"
    quote: |-
      {"error":"service temporarily degraded","request_id":"konan-1794766619-15834"}
      -- HTTP 503 in 0.000971s request_id=konan-1794766619-15834
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:16:59.734Z"
    quote: '{"ts": "2026-11-15T18:16:59.734Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "konan-1794766619-15834", "event": "chaos_failure", "method": "GET", "path": "/orders"}'
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:16:59.734Z"
    quote: '{"ts": "2026-11-15T18:16:59.734Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "konan-1794766619-15834", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.187, "client": "127.0.0.1:54768"}'
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:20.506Z"
    quote: '{"ts": "2026-11-15T18:15:20.506Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "103b6eaa580a", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.892, "client": "127.0.0.1:54737"}'
  - id: E23
    type: probe
    source: "/health, request id konan-1794766546-15742 (sent one second before the first read of E16)"
    quote: |-
      {"status":"ok","uptime_seconds":44.52082995790988}
      -- HTTP 200 in 0.001622s request_id=konan-1794766546-15742
  - id: E24
    type: log
    source: "lab/logs/app.log, whole file read (38 lines); absence observation, not a quoted line"
    quote: 'lines with "event": "chaos_disabled" = 0'
  - id: E25
    type: log
    source: "lab/logs/app.log @ 2026-11-15T18:15:02.055Z (the only line with event startup in the file)"
    quote: '{"ts": "2026-11-15T18:15:02.055Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E26
    type: metric
    source: "/metrics read at 2026-11-15T18:15:47Z (konan-1794766547-15747)"
    quote: "process_uptime_seconds 44.980566875077784"
  - id: E27
    type: metric
    source: "/metrics read at 2026-11-15T18:17:09Z (konan-1794766629-15853)"
    quote: "process_uptime_seconds 127.39913708297536"
  - id: E28
    type: metric
    source: "/metrics read at 2026-11-15T18:17:09Z (konan-1794766629-15853); every status=503 series in the scrape"
    quote: |-
      http_requests_total{method="GET",path="/orders",status="503"} 1
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 2
  - id: E29
    type: log
    source: "lab/logs/app.log, whole file read (38 lines, 2026-11-15T18:15:02.055Z to 18:17:00.913Z); count observation, not a quoted line"
    quote: 'request lines with "status": 503 = 7; lines with "event": "chaos_failure" = 7; each 503 request line shares its request_id with one chaos_failure line; first 503 line at 2026-11-15T18:15:12.070Z'
gaps:
  - "The log starts at the process start, 2026-11-15T18:15:02.055Z, and has no backup files. The complaint says 'a few minutes ago'; nothing before this process start is visible, so an earlier failure period, and the reason for this start, could not be checked."
  - "The actor behind the switch is unknown. Telemetry shows only POST /chaos/enable from client 127.0.0.1:54727 without the investigator prefix (E4)."
  - "The switch state and its parameters were not read directly: /chaos is operator surface and out of bounds. The state rests on the gauge (E16) and the log (E1, E24); the 0.4 rate rests on E1 alone. Observed: 7 of 15 business requests failed after the marker (6 of 10 user requests, 1 of 5 investigator requests)."
  - "User impact after 2026-11-15T18:15:21.560Z was not observed: the log holds no user request after that time. The later 503 (E19) is investigator traffic."
  - "Whether /health is exempt from the injection is not shown: one 200 with the switch on (E23) is the likely result at a 0.4 rate in any case."
  - "No client-side record of the user responses exists on this surface, so the absence of a proxy tier is shown for one investigator request only (E19–E21)."
  - "Inputs that nobody requested are untested. Orders are POST and the probe is GET-only; for example GET /products lists a product with price null, and no order on it appears in the log."
usage:
  model: claude-fable-5-2
  tokens: 1097877
  wall_clock_seconds: 248
---

# Chaos switch enabled: injected 503 on about half of shop requests

## Summary

**Root cause identified (infra-process, degradation-switch).** At 2026-11-15T18:15:10.017Z
a request to `POST /chaos/enable` turned on the target's internal chaos switch with
`failure_rate 0.4` and `error_status 503` (E1, E4). From that moment the target itself
answers a random share of requests on `/products`, `/products/{id}`, `/orders` and
`POST /orders` with an injected 503. Every 503 in the log has a `chaos_failure` line on
the same request id (E29), no 503 exists before the marker (E3), and the same input
fails and then succeeds (E7, E8, E9), which matches "works again on retry".

Impact on users in the visible window: 6 of 10 requests failed after the marker,
including both order attempts (E11, E14). The switch was still on at 18:17:09Z (E16), and
a read-only investigator request at 18:16:59Z received an injected 503 (E19–E21). The
health endpoint stayed 200 (E23), which explains the green dashboard. Confidence is high
on the mechanism; the actor and the time before 18:15:02Z are unknown (see Gaps).

## Timeline

- 18:15:02.055Z — the process starts; the only startup event in the log (E25).
- 18:15:02.775Z–18:15:06.962Z — 7 requests, all 200 or 201, including a created order (E2, E3, E7).
- 18:15:10.017Z — **switch marker**: chaos mode enabled, failure_rate 0.4, error_status 503 (E1), by `POST /chaos/enable -> 200` from 127.0.0.1:54727 (E4).
- 18:15:12.070Z — first 503, `GET /products`, with a `chaos_failure` line (E5, E6).
- 18:15:13.120Z–18:15:18.395Z — five more injected 503: `/products/1`, `/products/2`, `POST /orders`, `/products/5`, `POST /orders` (E8, E10, E11, E13, E14).
- 18:15:16.284Z, 18:15:19.450Z, 18:15:20.506Z — the same routes answer 200 (E12, E9, E22).
- 18:15:21.560Z — last user request in the log.
- 18:15:28Z — complaint raised; 18:15:35Z — investigation starts.
- 18:15:46Z — `/health` 200 (E23); 18:15:47Z — gauge reads 1, six 503 counted, no exception series (E15, E16, E17), uptime 44.98 s (E26).
- 18:16:59.734Z — investigator request to `/orders` receives an injected 503 (E19, E20, E21).
- 18:17:09Z — gauge still 1 (E16), seven 503 counted (E28), uptime 127.40 s, no restart (E27).

## Investigation

Complaint object, as synthesized by the manual trigger:

```json
{
  "source": "human",
  "fingerprint": "human-1794766528",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green." },
  "startsAt": "2026-11-15T18:15:28Z"
}
```

Investigation start: 2026-11-15T18:15:35Z (trigger latency 7 s).

- **Baseline.** `/health` 200 with uptime 44.5 s; `/metrics` with six 503 across business
  routes, no exception series, `faultline_chaos_enabled 1`; the log of 32 lines from the
  process start.
- **Triage.** Three lenses in parallel, each blind to the others: software-defect,
  infra-process, interfaces. All three reported the same marker and the same pairing of
  503 lines with `chaos_failure` lines. The software-defect lens found no exception
  signature. The infra-process lens found one startup and no saturation signal. The
  interfaces lens found a sharp onset 2.05 s after the marker and assigned the class to
  infra-process.
- **Deep-dive.** Skipped: the triage evidence was deterministic and complete. One
  confirming probe series replaced it: five read-only requests at 18:16:58Z–18:17:00Z,
  one of which received an injected 503 (E19–E21), then a second metrics read (E16, E27, E28).
- **Judge.** One fresh judge on hypotheses and verbatim evidence only: H1 validated;
  H2, H3, H4 invalidated. The judge's limits are recorded under Gaps; its request for a
  whole-file count of 503 lines against `chaos_failure` lines is answered by E28 and E29.
- **Budget.** One triage round, no deep-dive agents, one judge round.

## Hypotheses

### H1 — chaos switch injects 503 (infra-process) — validated

The marker (E1) carries the parameters and its access line (E4) shows how it was set.
Before it, all requests succeeded (E2, E3). After it, each of the seven 503 request lines
pairs with a `chaos_failure` line on the same request id (E5/E6, E8, E10, E11, E13, E14,
E20/E21; count in E29), and the metrics agree at both reads (E15, E28). The same input
fails and succeeds: `/products/1` (E7, E8, E9), `/products` (E6, E12), `GET /orders`
(E22, E21). The gauge reads 1 at both reads (E16) and the log has no `chaos_disabled`
line (E24). The prediction "a new request series still shows some 503 with a
`chaos_failure` line" was confirmed by probing (E19–E21). No evidence against.

### H2 — unhandled exception on specific inputs (software-defect) — invalidated

The exception counter has no series at both reads (E17) and the log has no
`unhandled_exception` line and no stack (E18). Independent of that instrumentation, the
failures are not tied to an input (E7, E8, E9), and the list route, which takes no input,
also fails (E5, E6). A 5xx request line without a `chaos_failure` line would reopen it.

### H3 — crash or restart loop (infra-process) — invalidated

One startup sits 8 s before the marker (E25), which is the only point for it. Against:
requests succeeded between the start and the marker (E2, E3), the uptime grows without a
reset from 44.98 s to 127.40 s (E26, E27), and failures continue 117 s after the start
(E21). A second startup line or a lower uptime value would reopen it.

### H4 — a proxy tier produces the 503 (interfaces) — invalidated

The one 503 observed from the client side carries the application's body and request id
(E19), and the application logged both the injection and the 503 for that id (E20, E21).
All seven 503 are application-produced, so no symptom remains for a proxy to explain. The
refutation from the client side rests on one request (see Gaps).

## Safe next steps

- Ask the operators who sent `POST /chaos/enable` at 18:15:10.017Z from 127.0.0.1:54727, and whether it was intended (E4).
- Have an operator read the switch state on the operator surface and compare it with E1 and E16.
- Keep reading `faultline_chaos_enabled` and the `status="503"` series of `http_requests_total` on `/metrics`; a `chaos_disabled` log line marks the end of the incident.
- Compare the source of the health dashboard with the business routes: `/health` stayed 200 while `/products` and `/orders` returned 503 (E23, E15).
- Look for records from before 18:15:02Z (older logs, a process supervisor) to test the complaint's "a few minutes ago".

## Gaps

- **Before the process start.** The log begins at 18:15:02.055Z with no backups. The
  complaint says the failures began "a few minutes ago"; the visible onset is the marker
  at 18:15:10.017Z, 18 s before the complaint. An earlier failure period, and the reason
  for this process start, are out of reach.
- **The actor.** Only the client address and the absence of the investigator prefix are
  known (E4).
- **Switch state and rate.** `/chaos` is operator surface. The state rests on the gauge
  and the log; the 0.4 rate rests on E1. Observed share: 7 of 15 business requests.
- **Current user impact.** No user request appears after 18:15:21.560Z; the later 503 is
  investigator traffic and is not counted as user impact.
- **Health exemption.** One 200 on `/health` with the switch on does not show an exemption.
- **Proxy tier.** No client-side record of user responses; shown absent for one request only.
- **Untested inputs.** Orders are POST and the probe is GET-only. `GET /products` lists a
  product with price null; no order on it appears in the log, so nothing is claimed.
