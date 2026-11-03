---
konan_journal: 2
investigation:
  id: 2026-11-03-shop-slow-chaos-latency
  trigger: "manual (/konan, human profile); complaint startsAt 2026-11-03T11:46:22Z, investigation started 2026-11-03T11:46:51Z, trigger latency 29s"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: "2026-11-03T11:46:51Z"
  concluded: "2026-11-03T11:53:49Z"
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "An internal chaos switch, enabled at 2026-11-03T11:46:00.226Z with extra_latency_ms 1500 and failure_rate 0.0, injects up to ~1500 ms of extra latency into the shop endpoints (/products, /products/{id}, /orders) while /health and /metrics stay fast; the switch was still active at the end of the investigation."
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: "An internal chaos switch (event chaos_enabled, extra_latency_ms 1500, failure_rate 0.0), enabled at 2026-11-03T11:46:00.226Z, injects up to ~1500 ms of extra latency into the shop endpoints while /health and /metrics stay fast; it remained active through the investigation and causes the reported slowness."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E18]
    evidence_against: []
  - id: H2
    statement: "The single error page that users report came from the process start window around 2026-11-03T11:45:54Z, or from a time before the current log history begins — not from an error produced by the running process."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E12, E13, E14]
    evidence_against: []
  - id: H3
    statement: "A defect in the target's own code causes the slowness or the error page."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E6, E12, E13]
  - id: H4
    statement: "Demand exceeds capacity; queueing makes the shop slow."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E3, E4, E10, E12, E17]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:46:00.226Z"
    quote: '{"ts": "2026-11-03T11:46:00.226Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "58e9d4fe874d", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.0, "error_status": 503, "extra_latency_ms": 1500}'
  - id: E2
    type: metric
    source: "/metrics via probe konan-1793706412-31894 @ 2026-11-03T11:46:52Z"
    quote: "faultline_chaos_enabled 1"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:45:55.067Z"
    quote: '{"ts": "2026-11-03T11:45:55.067Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "e6d012b77757", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.751, "client": "127.0.0.1:50348"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:46:03.041Z"
    quote: '{"ts": "2026-11-03T11:46:03.041Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "d6ea0d181c5e", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 763.418, "client": "127.0.0.1:50352"}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:45:56.121Z"
    quote: '{"ts": "2026-11-03T11:45:56.121Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "bfcc1b2b4cee", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.726, "client": "127.0.0.1:50349"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:46:06.483Z"
    quote: '{"ts": "2026-11-03T11:46:06.483Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "6a96f9e3ca95", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1243.099, "client": "127.0.0.1:50354"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:46:08.825Z"
    quote: '{"ts": "2026-11-03T11:46:08.825Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "687928892e20", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1276.514, "client": "127.0.0.1:50355"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:46:11.244Z"
    quote: '{"ts": "2026-11-03T11:46:11.244Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "dfff7ce7f319", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 1348.948, "client": "127.0.0.1:50356"}'
  - id: E9
    type: probe
    source: "GET /health, request_id konan-1793706412-31889 @ 2026-11-03T11:46:52Z"
    quote: |-
      {"status":"ok","uptime_seconds":57.96423291694373}
      -- HTTP 200 in 0.002332s request_id=konan-1793706412-31889
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:46:52.069Z"
    quote: '{"ts": "2026-11-03T11:46:52.069Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "konan-1793706412-31889", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.923, "client": "127.0.0.1:50375"}'
  - id: E11
    type: probe
    source: "GET /products, request_id konan-1793706523-32014 @ ~2026-11-03T11:48:43Z"
    quote: "-- HTTP 200 in 0.901107s request_id=konan-1793706523-32014"
  - id: E12
    type: metric
    source: "/metrics via probe konan-1793706412-31894 @ 2026-11-03T11:46:52Z (all samples of http_requests_total)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E13
    type: metric
    source: "/metrics via probe konan-1793706412-31894 @ 2026-11-03T11:46:52Z (the complete http_exceptions_total section; the counter has zero samples)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-03T11:45:54.117Z (first application line of the only log file; no rotated backups exist)"
    quote: '{"ts": "2026-11-03T11:45:54.117Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E15
    type: metric
    source: "/metrics via probe konan-1793706412-31894 @ 2026-11-03T11:46:52Z"
    quote: "process_uptime_seconds 58.310095499968156"
  - id: E16
    type: metric
    source: "/metrics via probe konan-1793706490-31945 @ ~2026-11-03T11:48:10Z"
    quote: "process_uptime_seconds 136.04689487512223"
  - id: E17
    type: metric
    source: "/metrics via probes konan-1793706412-31894 and konan-1793706490-31945 (identical value at both scrapes)"
    quote: "process_max_rss_bytes 48758784"
  - id: E18
    type: metric
    source: "/metrics via probe konan-1793706490-31945 @ ~2026-11-03T11:48:10Z"
    quote: "faultline_chaos_enabled 1"
gaps:
  - "No telemetry predates the process start at 2026-11-03T11:45:54Z (one app.log, no rotated backups), so the single error page that users report cannot be traced to any request. The settling evidence — a front-side (proxy, load-balancer, or client) access log for ~11:40–11:50Z — is outside the surface contract."
  - "The actor that enabled the chaos switch is not identifiable from this surface: the enabling request (request_id 58e9d4fe874d, client 127.0.0.1:50351) is unstamped, and the operator chaos surface is outside the probe allowlist."
  - "Host-level resources (CPU, sockets, accept queues) are outside the surface contract; the load-saturation refutation rests on application metrics and the fast /health behavior only."
usage:
  model: claude-fable-5
  tokens: 1587432
  wall_clock_seconds: 418
---

# Shop-wide slowness from an active chaos latency switch

## Summary

Root cause identified. An internal chaos switch was enabled at 11:46:00.226Z with
`extra_latency_ms: 1500` and `failure_rate: 0.0` (E1). From that moment, every observed
shop request (/products, /products/{id}, /orders, GET and POST) slowed from ~1–2 ms to
70–1349 ms while still returning 200/201 (E3–E8); /health and /metrics are exempt from
the injection and stayed at ~1 ms (E9, E10), which is why health checks look green while
users suffer. The switch was still on at the last reading (E18) and a fresh stamped probe
of /products still took 0.9 s (E11). Confidence is high: the onset is a step aligned to
the logged switch event, the magnitude matches the configured cap, and the path
selectivity matches the complaint exactly. The "error page once" part of the complaint
is NOT explained by this cause (failure_rate is 0.0 and zero non-2xx responses exist in
the telemetry window); it remains inconclusive — see H2 and Gaps.

## Timeline

- 11:45:54.117Z — process start, faultline 0.1.0 (E14). Log history begins here.
- 11:45:55–11:45:57Z — unstamped user traffic is fast: /products 1.751 ms (E3),
  /products/1 0.726 ms (E5).
- 11:46:00.226Z — **configuration-change marker**: chaos mode enabled,
  extra_latency_ms 1500, failure_rate 0.0, error_status 503 (E1).
- 11:46:03–11:46:11Z — unstamped user traffic is slow, all 2xx: /products 763 ms (E4),
  /products/1 1243 ms (E6), POST /orders 1277 ms (E7), /orders 1349 ms (E8).
- 11:46:22Z — complaint startsAt (human report).
- 11:46:51Z — investigation starts (trigger latency 29 s).
- 11:46:52Z — baseline: /health 200 in ~1–2 ms (E9, E10); gauge faultline_chaos_enabled 1
  (E2); uptime 58.3 s (E15).
- ~11:48:10Z — second scrape: uptime climbs monotonically to 136.0 s, no restart (E16);
  peak RSS flat (E17); gauge still 1 (E18).
- ~11:48:43Z — fresh stamped probe of /products: 0.901 s (E11). Injection still active.

## Investigation

**Complaint block** — the complaint object as synthesized by the `/konan` adapter
(human profile, `docs/triggers.md`), verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1793706382",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast." },
  "startsAt": "2026-11-03T11:46:22Z"
}
```

Investigation start: 2026-11-03T11:46:51Z (trigger latency 29 s). No severity was
stated, so none was recorded.

**Rounds as they ran:**

1. **Baseline** (11:46:52Z): /health 200 fast (E9), metrics scrape (E2, E12, E13, E15,
   E17), log tail — which already contained the chaos marker (E1) and the latency step
   (E3→E4).
2. **Triage** — three lenses spawned in parallel, blind to each other: infra-process,
   interfaces, software-defect. All three converged: the switch marker and latency step
   (infra-process, interfaces), clean process lifecycle (infra-process: E14–E17), no
   code-defect signature (software-defect: E12, E13, E5/E6). The load-saturation domain
   has no dedicated lens; it was covered from baseline metrics and recorded as H4.
3. **Deep-dive** — skipped. H1's triage evidence was deterministic and complete
   (marker, gauge, step, live probe); H3/H4 were already killed; H2's missing evidence
   (pre-start telemetry, front-side logs) does not exist on the surface contract, so no
   deep-dive could fill it.
4. **Judge** — adversarial, evidence-only: H1 validated (prediction confirmed, not only
   correlated; the judge flagged that "still active" needed the second gauge read, which
   the infra lens had captured — added as E18), H2 inconclusive (unfalsifiable from this
   ledger; settling evidence named in Gaps), H3 and H4 invalidated.

Budget: one triage round, zero deep-dive agents, one judge round — concluded inside the
first round.

## Hypotheses

### H1 — chaos latency switch (infra-process / degradation-switch) — validated

The switch event (E1) sits exactly in the 7-second gap between the last fast user
request (E5, 11:45:56) and the first slow one (E4, 11:46:03). Every post-switch duration
(E4, E6–E8, E11) falls inside the configured 0–1500 ms band — the spread (70.9 ms to
1348.9 ms across the full window) suggests a randomized delay up to the cap rather than
a fixed delay; the exact distribution is not readable from this surface. The gauge reads
1 at both scrapes (E2, E18) with monotonic uptime between them (E15, E16), so the same
process kept the switch on. /health stays ~1 ms during the slow period (E9, E10) — the
injection excludes the health path, which reconciles "green and fast health checks" with
the user reports. Nothing contradicts H1.

### H2 — the one error page predates the log history (infra-process) — inconclusive

The running process produced zero non-2xx responses (E12) and zero exceptions (E13)
since start (E14), so the error page did not come from a request this process served.
The process started at 11:45:54Z, inside the complaint's "last few minutes" window — a
user hitting the down-or-starting service would see a browser or gateway error page that
this telemetry can never record. But the positive half is unverifiable: no telemetry
predates E14, and a proxy error, a client-side failure, or a misremembered detail in the
(untrusted) complaint fit the same absence of evidence. The judge ruled it
unfalsifiable from this ledger.

### H3 — software defect (software-defect) — invalidated

The identical input /products/1 is fast at 11:45:56 (E5) and slow at 11:46:06 (E6), both
200 — the opposite of a data-dependent defect. Zero exceptions (E13), zero error
statuses (E12), and a step onset aligned to a logged configuration event are the
signature of a switch, not of the target's own code.

### H4 — load saturation (load-saturation) — invalidated

Total traffic is roughly a dozen requests over the process lifetime (E12); peak RSS is
byte-identical across scrapes (E17); the degradation is a step at the switch marker
(E1, E3→E4), not a gradient; and /health answers in ~1 ms during the slow period (E10),
which a saturated listener or worker pool would not do.

## Safe next steps

Read-only suggestions; remediation is out of scope.

- Watch `faultline_chaos_enabled`: the slowness prediction is that shop-path latency
  returns to ~1–2 ms the moment the gauge reads 0.
- The chaos configuration carries `error_status: 503` at `failure_rate: 0.0`. If the
  rate ever rises above zero, intermittent 503s will interleave with successes — watch
  the gauge and the status labels of `http_requests_total` together.
- For the single error page: pull the access log of whatever sits in front of the
  target (proxy, load balancer, or the reporting client's own timestamped failure) for
  ~11:40–11:50Z. That is the judge's named settling evidence for H2.
- Operator-side (outside the investigator's surface): read the chaos state and its
  change history to establish who enabled the switch at 11:46:00Z.

## Gaps

1. **No pre-start telemetry.** The only log file begins at the startup line (E14); no
   rotated backups exist. Whatever users saw before 11:45:54Z — including, possibly, the
   one error page — left no trace on this surface.
2. **No front-side view.** No proxy, load-balancer, or client log is on the surface
   contract, so a non-2xx served from in front of the target (or a connection failure
   during the start window) cannot be observed. This is the settling evidence for H2.
3. **Switch actor unknown.** The enabling request is unstamped (E1: request_id
   58e9d4fe874d, client 127.0.0.1:50351); the operator chaos surface is outside the
   probe allowlist, deliberately.
4. **No host-level metrics.** CPU, socket, and queue readings are not on the surface;
   H4's refutation rests on application metrics and the fast /health behavior, which the
   judge accepted with that caveat.
