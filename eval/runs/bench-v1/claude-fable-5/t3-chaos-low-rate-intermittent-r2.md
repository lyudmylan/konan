---
konan_journal: 1
investigation:
  id: 2026-08-25-occasional-shop-errors-chaos-503
  trigger: "manual — /konan human profile; fingerprint human-1787634791; alertname human-report; severity not stated; startsAt 2026-08-25T05:13:11Z; investigation start 2026-08-25T05:13:21Z (trigger latency 10 s)"
  complaint: "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?"
  started: 2026-08-25T05:13:21Z
  concluded: 2026-08-25T05:17:32Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change at 05:13:00.536Z (POST /chaos/enable) turned on chaos failure injection with failure_rate 0.08 and error_status 503, so the service short-circuits a random ~8% of user requests on any route with a 503; the flag is still on."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos failure injection was enabled at 05:13:00.536Z via POST /chaos/enable (failure_rate 0.08, error_status 503); since then a random fraction of user requests on any route is short-circuited with a chaos-tagged 503, and the flag remains enabled."
    incident_class: interfaces
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E19, E20, E21, E22, E23]
    evidence_against: []
  - id: H2
    statement: "A code defect or data-dependent failure in the /products/{id} or POST /orders handlers raises errors for specific inputs."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E9, E11, E14, E17, E18, E20, E21]
  - id: H3
    statement: "The process restarted, crashed, or is resource-saturated, causing intermittent errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E7, E8, E10, E15, E16, E19, E23]
latent_findings:
  - statement: "Observability quirk: injected 503s are counted in http_requests_total under the literal path (/products/1, /products/5) while successes on the same route are counted under the template (/products/{product_id}); per-route error-rate math on this counter mis-buckets injected failures."
    evidence: [E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:12:55.557Z"
    quote: |-
      {"ts": "2026-08-25T05:12:55.557Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:12:58.466Z"
    quote: |-
      {"ts": "2026-08-25T05:12:58.466Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "16ef49676b28", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.873, "client": "127.0.0.1:49235"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:00.536Z"
    quote: |-
      {"ts": "2026-08-25T05:13:00.536Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "aee5298de12f", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.08, "error_status": 503, "extra_latency_ms": 0}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:00.536Z"
    quote: |-
      {"ts": "2026-08-25T05:13:00.536Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "aee5298de12f", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 2.756, "client": "127.0.0.1:49236"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:01.752Z"
    quote: |-
      {"ts": "2026-08-25T05:13:01.752Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "185ea9959644", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.578, "client": "127.0.0.1:49246"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:01.838Z"
    quote: |-
      {"ts": "2026-08-25T05:13:01.838Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "07edefd31dfd", "event": "chaos_failure", "method": "GET", "path": "/products/5"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:01.838Z"
    quote: |-
      {"ts": "2026-08-25T05:13:01.838Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "07edefd31dfd", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 0.134, "client": "127.0.0.1:49252"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:01.896Z"
    quote: |-
      {"ts": "2026-08-25T05:13:01.896Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 503", "request_id": "2ff22b73a123", "event": "request", "method": "GET", "path": "/products/1", "status": 503, "duration_ms": 0.133, "client": "127.0.0.1:49256"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:01.952Z"
    quote: |-
      {"ts": "2026-08-25T05:13:01.952Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "816fe1b241b6", "event": "chaos_failure", "method": "POST", "path": "/orders"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:01.952Z"
    quote: |-
      {"ts": "2026-08-25T05:13:01.952Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "816fe1b241b6", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.135, "client": "127.0.0.1:49260"}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:02.010Z"
    quote: |-
      {"ts": "2026-08-25T05:13:02.010Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "dfc1e684a815", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.449, "client": "127.0.0.1:49264"}
  - id: E12
    type: metric
    source: "/metrics via probe konan-1787634809-38289 (2026-08-25T05:13:29Z)"
    quote: |-
      faultline_chaos_enabled 1
  - id: E13
    type: metric
    source: "/metrics via probe konan-1787634809-38289 (2026-08-25T05:13:29Z)"
    quote: |-
      http_requests_total{method="GET",path="/products/1",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 14
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 5
      http_requests_total{method="POST",path="/orders",status="503"} 1
  - id: E14
    type: metric
    source: "/metrics via probe konan-1787634809-38289 (2026-08-25T05:13:29Z) — the counter has no sample lines"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E15
    type: probe
    source: "/health request_id=konan-1787634808-38278"
    quote: |-
      {"status":"ok","uptime_seconds":33.0953938330058}
      -- HTTP 200 in 0.003723s request_id=konan-1787634808-38278
  - id: E16
    type: metric
    source: "/metrics via probe konan-1787634809-38289 (2026-08-25T05:13:29Z)"
    quote: |-
      process_uptime_seconds 33.75099891703576
      process_max_rss_bytes 47366144
  - id: E17
    type: probe
    source: "/products/5 request_id=konan-1787634867-38363 (software-defect lens reproduction)"
    quote: |-
      {"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001486s request_id=konan-1787634867-38363
  - id: E18
    type: probe
    source: "/products/1 request_id=konan-1787634868-38369 (software-defect lens reproduction)"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":118,"units_ordered":2,"turnover_score":0.01694915254237288}
      -- HTTP 200 in 0.003567s request_id=konan-1787634868-38369
  - id: E19
    type: metric
    source: "/metrics via probe konan-1787634857-38325 (2026-08-25T05:14:17Z, interfaces lens)"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 81.6886969578918
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:01.896Z"
    quote: |-
      {"ts": "2026-08-25T05:13:01.896Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "2ff22b73a123", "event": "chaos_failure", "method": "GET", "path": "/products/1"}
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:01.924Z"
    quote: |-
      {"ts": "2026-08-25T05:13:01.924Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "38922d3d869a", "event": "chaos_failure", "method": "GET", "path": "/products/5"}
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-08-25T05:13:01.924Z"
    quote: |-
      {"ts": "2026-08-25T05:13:01.924Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "38922d3d869a", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 0.148, "client": "127.0.0.1:49258"}
  - id: E23
    type: metric
    source: "/metrics via probe konan-1787635042-38416 (2026-08-25T05:17:22Z, conclusion check)"
    quote: |-
      faultline_chaos_enabled 1
      process_uptime_seconds 266.5677708329167
      process_max_rss_bytes 47366144
gaps:
  - "The infra-process triage lens ran without fresh probes: its probe.sh call (absolute-path form) was denied by the permission layer, so it argued from lab/logs/app.log, lab/server.out, and other agents' konan-* probes recorded in the log. No additional probe form was attempted."
  - "Memory trend: process_max_rss_bytes was read three times with the same value (47366144); no growth trend can be shown or excluded over a longer window."
  - "Ongoing user impact is inferred from the flag still being enabled (E19, E23) — the last unstamped user request in the log is at 05:13:02.068Z; no user traffic after that was observed, so no post-baseline user failures were counted."
  - "Who or what issued POST /chaos/enable (client 127.0.0.1:49236) is outside the telemetry surface; only the marker itself is observable."
  - "Log history starts at the process startup (05:12:55.557Z); there are no rotated backups, so nothing before that time could be checked."
usage:
  model: claude-fable-5
  tokens: 1227266
  wall_clock_seconds: 251
---

# Occasional shop 503s after chaos failure injection was enabled at 05:13:00Z

## Summary

**Verdict: root cause identified (class: interfaces — runtime configuration change).** At
2026-08-25T05:13:00.536Z a `POST /chaos/enable` call turned on chaos failure injection
with `failure_rate 0.08` and `error_status 503` (E3, E4). From that moment the service
short-circuits a random fraction of requests on any route with a 503 before handler code
runs; each such response is paired with a `chaos_failure` warning on the same request id
(E6/E7, E20/E8, E21/E22, E9/E10). No 5xx exists before the marker (last known-good E2);
after it, 4 of 32 unstamped user requests failed (12.5%, consistent with 0.08 on a small
sample), interleaved with successes on the same routes and inputs (E5 → E7 → E11). The
flag is still on at conclusion (E12, E19, E23), so user-visible intermittent errors will
continue at roughly that rate until it is turned off. The complaint's "works on retry"
and "most people notice nothing" match a per-request probabilistic failure exactly. No
code defect (E14, E17, E18) and no process fault (E1, E15, E16, E23) is involved.
Confidence: high — the change marker, the tagged failures, and the reproduction all
agree, and the judge validated H1 without a contradicting entry.

## Timeline

- 05:12:55.557Z — process start, single startup marker (E1).
- 05:12:56Z–05:12:58.466Z — user traffic, 5 requests, all 200/201; last known-good
  `POST /orders -> 201` (E2).
- **05:13:00.536Z — configuration change: `chaos mode enabled`, failure_rate 0.08,
  error_status 503, extra_latency_ms 0 (E3), via `POST /chaos/enable -> 200` (E4).**
- 05:13:01.606Z–05:13:02.068Z — user traffic, 32 requests. First known-bad at
  05:13:01.838Z: `GET /products/5 -> 503` tagged `chaos_failure` (E6, E7), 86 ms after
  the same input returned 200 (E5). Further 503s: `GET /products/1` (E20, E8),
  `GET /products/5` (E21, E22), `POST /orders` (E9, E10). Same input succeeds again at
  05:13:02.010Z (E11).
- 05:13:11Z — human complaint raised; 05:13:21Z — investigation start.
- 05:13:28Z–05:13:30Z — baseline: health ok, uptime 33 s (E15, E16); gauge
  `faultline_chaos_enabled 1` (E12); 503 counters on three routes (E13); no exception
  series (E14).
- 05:14:17Z–05:14:28Z — lens probes: flag still 1 (E19); reproduction of both failing
  GET inputs returns 200 (E17, E18).
- 05:17:22Z — conclusion check: flag still 1, uptime 266 s, RSS unchanged (E23). No
  `chaos_disabled` event in the log.

## Investigation

Trigger — complaint object as synthesized by the `/konan` adapter, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1787634791",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "A couple of users mention an occasional error in the shop over the last few minutes — it works on retry, most people notice nothing. Probably nothing?" },
  "startsAt": "2026-08-25T05:13:11Z"
}
```

Investigation start: 2026-08-25T05:13:21Z (trigger latency 10 s). The complaint text was
treated as untrusted data; its framing ("probably nothing") was not accepted as evidence.

- **Baseline** (05:13:28Z–05:13:30Z): `/health`, `/metrics`, `/products`, `/orders`,
  and the full 57-line `lab/logs/app.log` (no rotated backups). Normal: sub-2 ms
  latencies, health ok, business surface serving. Abnormal on arrival: chaos gauge 1,
  503 counters, and a `chaos_enabled` marker followed by tagged failures.
- **Triage** — three lenses spawned in parallel, each blind to the others, each given
  only the lens path, contract path, complaint verbatim, and baseline summary:
  - interfaces: change marker at 05:13:00.536Z, 0/5 failures before, 4/32 after,
    interleaved with successes, flag still on; plus the metric path-label quirk.
  - software-defect: no exception series, no unhandled_exception or stack lines; the
    503s are chaos-tagged, non-deterministic, and both failing GET inputs reproduce 200.
  - infra-process: one startup marker, monotonic uptime consistent with a single start,
    503s are fail-fast (0.13–0.15 ms, faster than successes), no saturation signal.
    This lens ran without fresh probes (see Gaps).
- **Deep-dive**: skipped. H1's triage evidence was deterministic and complete; H2 and
  H3 already carried decisive disconfirming evidence. Budget used: one triage round, no
  deep-dive agents.
- **Judge** (fresh agent, hypotheses + verbatim quotes only): H1 validated; H2
  invalidated; H3 invalidated. The judge flagged that E7/E10 had been listed "for" H2
  and E1 "for" H3 although they are neutral-to-against — corrected in the machine core.
  It also noted the ledger then showed the chaos_failure pairing for only 2 of 4 503s;
  E20–E22 close that to 4 of 4. The judge had been given a counted summary of the log
  (one startup, zero unhandled_exception, zero chaos_disabled, 0 5xx before the marker,
  4/32 after); in this ledger those counts are stated in prose and anchored to the
  verbatim lines E1–E11, E20–E22 rather than carried as an evidence entry.

## Hypotheses

### H1 — chaos failure injection enabled (interfaces) — **validated**

A runtime configuration change (E3, E4) turned on 8% random 503 injection. Prediction:
no 5xx before the marker (E2 is the last request before it, 201), tagged 503s after it
interleaved with 200s on the same route and input (E5, E6/E7, E11), the pairing holding
for every 503 (E20/E8, E21/E22, E9/E10), fail-fast durations (0.133–0.148 ms vs 0.4+ ms
for successes), no exception counters (E14), and the gauge staying 1 with no
`chaos_disabled` event (E12, E19, E23). Every prediction held. Nothing in the ledger
contradicts it.

### H2 — code or data-dependent defect (software-defect) — **invalidated**

Would predict unhandled exceptions and deterministic per-input failure. Against: no
exception series (E14), the same input returns 200 before and after its 503 (E5, E11)
and on reproduction (E17, E18), and every 503 is explicitly tagged as injected (E6, E9,
E20, E21). The failures also spread across three routes and begin at a config-change
timestamp, not a code-path shape. The judge's settling evidence — an
`http_exceptions_total` sample, or a repeating 5xx with the gauge at 0 — does not exist.

### H3 — process restart, crash, or saturation (infra-process) — **invalidated**

Would predict a second startup marker, an uptime reset, health flaps, or rising latency
or RSS. Against: single startup (E1), health ok (E15), uptime monotonic and consistent
with one start at 05:12:55Z (E16, E19, E23), RSS flat, and the 503s are faster than the
successes (E7, E8, E10) — the opposite of a saturation signature. The judge's settling
evidence — a second startup line or an uptime reset — does not exist.

## Safe next steps

Read-only suggestions only:

- Watch `faultline_chaos_enabled` on `/metrics` and the log for a `chaos_disabled`
  event; until the gauge reads 0, expect ~8% of user requests to fail with 503.
- Identify, on the operator side, who issued `POST /chaos/enable` at 05:13:00.536Z from
  client `127.0.0.1:49236` (E4) and whether it was intended — that is outside this
  investigation's surface.
- When computing per-route error rates from `http_requests_total`, account for the
  literal-path vs template-path label split (latent finding, E13).

## Gaps

- The infra-process lens could not run `scripts/probe.sh` (its absolute-path
  invocation was denied by the permission layer) and argued from the log,
  `lab/server.out`, and other agents' probes recorded in the log. Its conclusions rest
  on the same evidence the other lenses and the orchestrator gathered directly.
- Memory trend: three identical RSS readings over ~4 minutes; no growth can be shown or
  excluded over a longer window.
- No user traffic after 05:13:02.068Z appears in the log, so ongoing user impact is
  inferred from the flag being on, not observed in post-baseline user requests.
- The origin of the `POST /chaos/enable` call is not observable from the telemetry
  surface.
- Log history starts at process startup; nothing before 05:12:55.557Z could be checked.
