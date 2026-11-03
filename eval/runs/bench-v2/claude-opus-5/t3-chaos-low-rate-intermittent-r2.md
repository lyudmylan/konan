---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-503-injection
  trigger: 'manual — /konan adapter, human profile. Complaint object: source human, fingerprint human-1793698795, labels.alertname human-report, no severity stated by the reporter, startsAt 2026-11-03T09:39:55Z. Investigation entered the loop at 2026-11-03T09:40:01Z — trigger latency 6s.'
  complaint: 'A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?'
  started: 2026-11-03T09:40:01Z
  concluded: 2026-11-03T09:46:55Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'An internal error-injection switch in the target was enabled at 09:39:51.023Z with error_status 503, and it short-circuits a fraction of requests to HTTP 503 before route handling; both user-visible failures carry its marker under the same request id as the 503 they produced.'
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: 'An internal operational degradation switch in the target (chaos mode), enabled at 09:39:51.023Z with failure_rate 0.08 and error_status 503, short-circuits a fraction of requests to HTTP 503 while it stays on; this produced the user-visible errors.'
    incident_class: infra-process
    state: validated
    evidence_for: [E3, E4, E5, E7, E8, E9, E14, E16, E18]
    evidence_against: []
  - id: H2
    statement: "The target's own code raises an unhandled error on some input, and that defect produced the user-visible 503s."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E7, E10, E11, E15]
  - id: H3
    statement: 'Demand exceeded capacity — resource exhaustion, queueing, or worker starvation — and degraded the shop.'
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E5, E8, E12, E13, E18, E19]
  - id: H4
    statement: 'A proxy, load balancer, or gateway tier in front of the target failed on its own and returned the 503s.'
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E7, E8, E15]
  - id: H5
    statement: 'The process crashed, restarted, or hung, and the observed 503s are lifecycle fallout.'
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E12, E13, E15, E18]
latent_findings:
  - statement: 'The metric path label is not templated when a request is short-circuited: the injected failure recorded the literal path /products/1 while successful reads of the same route aggregate under /products/{product_id}. An error on any product id therefore mints a new time series, and a per-route error rate cannot be read from the labels.'
    evidence: [E11]
  - statement: 'The product catalogue serves product id 4 with price null while other products carry numeric prices. Whether an order for that product fails is untested — the investigator surface is GET-only, so no order could be placed.'
    evidence: [E17]
evidence:
  - id: E1
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T09:39:46.096Z'
    quote: '{"ts": "2026-11-03T09:39:46.096Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T09:39:48.962Z — last user request before the switch'
    quote: '{"ts": "2026-11-03T09:39:48.962Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "7dbe6c4805b0", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.936, "client": "127.0.0.1:49289"}'
  - id: E3
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T09:39:51.023Z'
    quote: '{"ts": "2026-11-03T09:39:51.023Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "c885942bac4b", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}'
  - id: E4
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T09:39:52.107Z'
    quote: '{"ts": "2026-11-03T09:39:52.107Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "8e81267e40a0", "event": "chaos_failure", "method": "GET", "path": "/products/1"}'
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T09:39:52.107Z — same request_id as E4'
    quote: '{"ts": "2026-11-03T09:39:52.107Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "8e81267e40a0", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.21, "client": "127.0.0.1:49292"}'
  - id: E6
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T09:39:52.201Z'
    quote: '{"ts": "2026-11-03T09:39:52.201Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "a8085fe40931", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.421, "client": "127.0.0.1:49298"}'
  - id: E7
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T09:39:52.244Z'
    quote: '{"ts": "2026-11-03T09:39:52.244Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "121ee54f5413", "event": "chaos_failure", "method": "GET", "path": "/orders"}'
  - id: E8
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T09:39:52.244Z — same request_id as E7'
    quote: '{"ts": "2026-11-03T09:39:52.244Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 503", "request_id": "121ee54f5413", "event": "request", "method": "GET", "path": "/orders", "status": 503, "duration_ms": 0.139, "client": "127.0.0.1:49301"}'
  - id: E9
    type: metric
    source: '/metrics, probe request_id konan-1793698825-27076'
    quote: 'faultline_chaos_enabled 1'
  - id: E10
    type: metric
    source: '/metrics, probe request_id konan-1793698825-27076 — counter declared, no series'
    quote: '# HELP http_exceptions_total Unhandled exceptions by Python class name. / # TYPE http_exceptions_total counter'
  - id: E11
    type: metric
    source: '/metrics, probe request_id konan-1793698825-27076'
    quote: 'http_requests_total{method="GET",path="/products/1",status="503"} 1 / http_requests_total{method="GET",path="/orders",status="503"} 1 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 16 / http_requests_total{method="GET",path="/orders",status="200"} 4'
  - id: E12
    type: probe
    source: '/health, probe request_id konan-1793698821-27071'
    quote: '{"status":"ok","uptime_seconds":35.319709416944534} / -- HTTP 200 in 0.001887s'
  - id: E13
    type: metric
    source: '/metrics, probe request_id konan-1793698825-27076'
    quote: 'process_max_rss_bytes 47136768 / process_uptime_seconds 38.98884795792401 / http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 0.007902917452156544 / http_request_duration_seconds_count{method="GET",path="/products/{product_id}"} 16'
  - id: E14
    type: metric
    source: '/metrics, probe request_id konan-1793698825-27076 — exactly one successful enable call'
    quote: 'http_requests_total{method="POST",path="/chaos/enable",status="200"} 1'
  - id: E15
    type: log
    source: 'lab/logs/app.log, whole file (55 lines, 2026-11-03T09:39:46.096Z to 09:40:25Z); lab/logs/ directory listing'
    quote: 'Census of the file: exactly one startup event, exactly one chaos_enabled event, no chaos_disabled event, no unhandled_exception event, no stack field, no line at ERROR level. The directory holds only app.log — no .1-.3 rotation backups.'
  - id: E16
    type: log
    source: 'lab/logs/app.log, counted over user request lines (unprefixed hex request ids; investigator probes carry the konan- prefix)'
    quote: 'Before the switch at 09:39:51.023Z: 0 of 5 user requests non-2xx. After it: 2 of 32 user requests returned 503 (6.25%). Last user request at 09:39:52.556Z.'
  - id: E17
    type: probe
    source: '/products, probe request_id konan-1793699208-27220'
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":116},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":36},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}] / -- HTTP 200 in 0.001539s'
  - id: E18
    type: metric
    source: '/metrics, probe request_id konan-1793699210-27225 — final read, 386s after the first'
    quote: 'faultline_chaos_enabled 1 / process_uptime_seconds 424.5592256670352 / process_max_rss_bytes 47136768 / http_requests_total{method="GET",path="/products/1",status="503"} 1 / http_requests_total{method="GET",path="/orders",status="503"} 1'
  - id: E19
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T09:39:46.817Z — the maximum duration_ms across all user request lines in the file'
    quote: '{"ts": "2026-11-03T09:39:46.817Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "fe883c507999", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 12.074, "client": "127.0.0.1:49284"}'
gaps:
  - 'No telemetry exists before 2026-11-03T09:39:46.096Z: that line is the process start and the first line of app.log, and no rotation backups exist (E15). The reporter said "the last few minutes", so most of their window has no data at all — errors served by any earlier process instance are invisible from this surface.'
  - 'The complaint''s "it works on retry" is not verified as a retry. No request id, session, or client field links the 503 at 09:39:52.107Z (client port 49292) to the 200 at 09:39:52.201Z (port 49298). The evidence shows an independent later request to the same path succeeding, which is weaker than a confirmed retry.'
  - 'The 8% figure is the switch''s configured failure_rate (E3), not a measured rate. Measured user impact is 2 of 32 requests after the switch — a sample far too small to bound the true rate.'
  - 'Three taxonomy classes have no lens file in this repo (load-saturation, third-party, data-db); only infra-process, interfaces, and software-defect were spawned. Those domains were covered solely by the orchestrator reading metrics and logs, not by a dedicated lens.'
  - 'A defect that returns 503 deliberately without raising would leave the same trace as an injected failure. Excluding it would need the target''s source, which the blinding contract puts out of reach; the exclusion here rests on both 503s carrying a chaos_failure marker under their own request id.'
  - 'An upstream proxy or gateway returning 503s that never reached the target cannot be refuted from the target''s own logs, and no front-tier access log is in the surface contract.'
  - 'Whether an order for product id 4 (price null, E17) fails is untested: the investigator surface is GET-only, so no order could be placed.'
  - 'Who enabled the switch, and whether it was intended, is not in the telemetry. The log records the enabling call under request id c885942bac4b (E3) but carries no actor identity.'
usage:
  model: claude-opus-5
  tokens: 1633930
  wall_clock_seconds: 414
---

# Shop 503s: an error-injection switch left on in the target

## Summary

Not nothing. An internal error-injection switch inside faultline ("chaos mode") was
enabled at 09:39:51.023Z configured to return HTTP 503 at a rate of 0.08, and it was
still on at the last reading, 424s into the process (E3, E9, E18). Both user-visible
failures in the observed window are attributable to it at the individual-request level:
each 503 access line shares its `request_id` with a `chaos_failure` marker logged in the
same millisecond — `8e81267e40a0` for `GET /products/1` and `121ee54f5413` for
`GET /orders` (E4/E5, E7/E8). That request-id pairing, not the before/after contrast, is
what carries the verdict.

Impact matches the reporter's description in shape and in size: 2 of 32 user requests
after the switch returned 503 (E16), the failures are spread across two unrelated routes
rather than tied to one input, and the same path returned 200 ninety-four milliseconds
later (E6). The switch injects no latency (`extra_latency_ms: 0`), and the two 503s were
the two fastest responses in the file — 0.21 ms and 0.139 ms against a 0.49 ms route mean
(E3, E5, E8, E13), the signature of a short-circuit before route handling rather than a
failing handler.

Confidence in the mechanism is high. Two qualifications belong in the same breath. First,
exposure is ongoing, not resolved: the quiet span since 09:39:52.556Z is absence of user
traffic, not recovery — the switch is armed and no `chaos_disabled` event exists (E15,
E16, E18). Second, the evidence covers a 39-second window that begins at the process
start, so the earlier part of the reporter's "last few minutes" is not merely clean — it
is unobservable (E15). The verdict is about the failures that telemetry can see.

## Timeline

- **09:39:46.096Z** — process start, the first line in the log and the start of all
  available telemetry (E1). Nothing before this point can be checked.
- **09:39:46.817Z – 09:39:48.962Z** — five user requests, all 2xx: product browsing and
  an order created (E2, E16). This is the clean baseline.
- **09:39:51.023Z** — **configuration-change marker.** `chaos mode enabled`,
  `failure_rate: 0.08`, `error_status: 503`, `extra_latency_ms: 0` (E3). Arrived through
  one successful `POST /chaos/enable`; the metric counter shows exactly one such call, so
  this configuration is the live one (E14).
- **09:39:52.107Z** — first user-visible failure: `chaos_failure` on `GET /products/1`,
  and the 503 under the same request id `8e81267e40a0` (E4, E5).
- **09:39:52.201Z** — the same path returns 200 (E6).
- **09:39:52.244Z** — second user-visible failure: `chaos_failure` on `GET /orders`, 503
  under request id `121ee54f5413` (E7, E8).
- **09:39:52.556Z** — last user request. User traffic stops; six orders were created in
  the window and all six returned 201 (E16).
- **09:39:55Z** — the human complaint is raised (`startsAt`); the loop starts at
  09:40:01Z.
- **09:40:21Z – 09:46:50Z** — investigator probes only. `/health` ok, business surface
  serving, switch still reading `1` at uptime 424.6s (E12, E17, E18).

## Investigation

Baseline came from `/health`, a `/metrics` scrape, and the full log file. The uptime of
35s at first contact was the first thing worth noting — it put a hard floor under how far
back any evidence could reach.

Triage fanned out all three lenses the repo provides — infra-process, software-defect,
interfaces — in parallel, each blind to the others. All three converged on the same
mechanism independently, and each cleared its own domain with cited checks. The
software-defect lens additionally reported the metric-label finding recorded above as
latent. No lens was skipped for cost; the three absent taxonomy classes have no lens file
in this repo, which is recorded as a gap rather than passed over.

No deep-dive round was spawned. The triage evidence for H1 was already deterministic at
the request-id level, and the skill sends such a hypothesis straight to the judge rather
than re-proving it.

The adversarial judge saw only the hypothesis list and the verbatim evidence, never the
narrative. It validated H1 and invalidated H2–H5, and it corrected three things that are
reflected above rather than argued away:

1. **"Works on retry" was not shown.** The 503 and the later 200 are different requests
   from different client ports. The claim is now scoped to what the log supports, and the
   shortfall is in Gaps.
2. **The 8% rate was read off the configuration, not measured.** 2 of 32 cannot bound a
   true rate. Both figures are now stated for what they are.
3. **The before/after contrast is weak evidence.** At an 8% rate, 0 failures in 5
   pre-switch requests is the expected result either way; H1 rests on the request-id
   pairing instead.

The judge also questioned the `infra-process` class on the grounds that the switch was
flipped by a deliberate API call. The report contract settles that explicitly: an
internal operational switch is `infra-process` "even when its symptom is gateway-shaped
statuses", so the class stands, with `cause: degradation-switch`.

## Hypotheses

### H1 — degradation switch injecting 503s — **validated**

The switch was armed at 09:39:51.023Z with `error_status: 503` (E3), one enable call
produced it (E14), no disable event exists and it still reads `1` 424s into the process
(E15, E18). Both failures carry a `chaos_failure` marker sharing the request id of the
503 access line (E4/E5, E7/E8). Supporting but weak: the before/after split (E16) and the
sub-millisecond fail-fast durations. Nothing in the window argues against it.

### H2 — unhandled exception in the target's own code — **invalidated**

`http_exceptions_total` carries no series at all after the full traffic window (E10), and
the file holds no `unhandled_exception` event, no `stack` field, and no ERROR line (E15).
The "on some input" clause dies directly: `/products/1` returned 200 at 09:39:52.201Z,
94 ms after returning 503 (E5, E6), and the 503s span two unrelated routes (E11). Both
failures are attributed by the target itself to injection (E4, E7). Residual: a defect
returning 503 without raising would look identical — in Gaps.

### H3 — load saturation — **invalidated**

The maximum `duration_ms` across every user request line in the file is 12.074 ms, and
that is a `/health` call at process start; every other user line is under 2 ms (E19,
E13). Peak RSS is 47136768 bytes and identical across readings 386s apart, so growth is
zero (E13, E18). The switch injects no latency (E3), and the failures were *faster* than
the successes (E5, E8) — the opposite of queueing. Total user traffic was roughly 37
requests in 6 seconds.

### H4 — front proxy or gateway failure — **invalidated**

The target wrote both 503 lines itself, with its own request ids, durations, and client
addresses (E5, E8), so the responses were generated in the application, not in front of
it. The honest limit: an application log cannot refute a failure upstream that never
reached the application — in Gaps.

### H5 — crash, restart, or hang — **invalidated**

`process_uptime_seconds` 38.99 at the first scrape reconciles exactly with the 09:39:46.096Z
start (E1, E13), the file holds exactly one `startup` event and no rotation backups (E15),
uptime climbs monotonically to 424.6s (E18), and `/health` answers 200 in 1.9 ms, so the
process is not hung (E12). Scoped to the observed window: whether an earlier instance
existed before 09:39:46.096Z cannot be determined from this surface, which is the first
gap.

## Safe next steps

- **Confirm intent with whoever ran the enable call.** The log records it under request id
  `c885942bac4b` but no actor identity (E3). Whether this switch is expected in this
  environment right now is an operator question, not a telemetry one, and it decides
  whether this is a live incident or expected lab state.
- **Re-read `/metrics` before concluding anything about user impact.** `faultline_chaos_enabled`
  is a point-in-time gauge; "still on" is established as of 09:46:50Z and no later.
- **Watch for `chaos_failure` events once real traffic resumes.** Observed impact is
  bounded by the 32 user requests that happened to arrive; the rate question needs a
  sample of at least a couple of hundred requests to answer.
- **To settle "works on retry" properly**, correlate on a client-stable field rather than
  on path and time; the present access-line fields cannot link a retry to its failure.
- **Treat the metric-label finding as a measurement blocker, not cosmetics** — while
  short-circuited requests record literal paths, per-route error rates cannot be read
  from the counters at all (E11).

Remediation is out of scope for this journal.

## Gaps

The frontmatter list, elaborated in order of how much it limits the verdict:

1. **The window starts at the process start.** All 19 evidence items fall between
   09:39:46.096Z and 09:46:50Z. The reporter's "last few minutes" reaches further back
   than any available telemetry, and no rotated backups exist (E15). If users saw errors
   before 09:39:46.096Z, nothing in this surface can confirm or deny it, and H5 is
   untested rather than refuted for that earlier span.
2. **"Works on retry" is unverified as a retry** — different client ports, no correlating
   field (E5, E6).
3. **The 8% is configured, not measured** (E3 versus E16).
4. **Three classes had no lens**: load-saturation, third-party, data-db have no lens file
   in this repo. Those domains were checked only by the orchestrator's own reading of
   metrics and logs. This is an accepted blind spot, recorded rather than hidden.
5. **A non-raising 503 defect is not excluded** by exception counters alone; the target's
   source is out of reach under the blinding contract.
6. **An upstream tier cannot be refuted** from the target's own logs; no front-tier log is
   in the surface contract.
7. **Product id 4 serves `price: null`** (E17) and ordering it could not be tested — the
   investigator surface is GET-only.
8. **No actor identity** for the switch enable call (E3).
