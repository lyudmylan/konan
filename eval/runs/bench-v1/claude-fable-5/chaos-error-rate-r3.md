---
konan_journal: 1
investigation:
  id: 2026-08-19-intermittent-503s-chaos-enabled
  trigger: "manual (/konan; complaint fingerprint human-1787159504, alertname human-report, startsAt 2026-08-19T17:11:44Z; investigation start 2026-08-19T17:11:52Z; trigger latency 8s)"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-08-19T17:11:52Z
  concluded: 2026-08-19T17:14:10Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change — chaos mode enabled at 17:11:27.700Z (failure_rate 0.4, error_status 503) and still active — injects 503 responses on a probabilistic share of shop requests (products, orders) before the handler runs, while /health is unaffected."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Chaos mode was enabled at runtime (17:11:27.700Z, failure_rate 0.4, error_status 503) and is injecting 503s on ~40% of shop requests across all user routes; /health is exempt, so the health dashboard stays green; the flag is still on."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E14, E15]
    evidence_against: []
  - id: H2
    statement: "A code defect (unhandled exception or data-dependent failure) in the shop routes causes the page-load and order errors."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E8, E9, E10, E12, E14]
  - id: H3
    statement: "A process restart/crash loop or resource saturation (memory, worker starvation) causes the intermittent failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E11, E12, E13, E15]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:11:27.700Z"
    quote: "{\"ts\": \"2026-08-19T17:11:27.700Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"ae9ffa19d95b\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.4, \"error_status\": 503, \"extra_latency_ms\": 0}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:11:27.701Z"
    quote: "\"message\": \"POST /chaos/enable -> 200\", \"request_id\": \"ae9ffa19d95b\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/chaos/enable\", \"status\": 200, \"duration_ms\": 2.413, \"client\": \"127.0.0.1:63384\""
  - id: E3
    type: metric
    source: "/metrics via probe konan-1787159516-67180 @ 2026-08-19T17:11:56Z"
    quote: "faultline_chaos_enabled 1"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:11:29.770Z–17:11:29.771Z"
    quote: "{\"ts\": \"2026-08-19T17:11:29.770Z\", \"level\": \"WARNING\", \"logger\": \"faultline.request\", \"message\": \"chaos-injected failure\", \"request_id\": \"9e1b95657040\", \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products\"} / {\"ts\": \"2026-08-19T17:11:29.771Z\", ... \"message\": \"GET /products -> 503\", \"request_id\": \"9e1b95657040\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 503, \"duration_ms\": 0.312, \"client\": \"127.0.0.1:63385\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:11:32.967Z–17:11:32.968Z"
    quote: "\"message\": \"chaos-injected failure\", \"request_id\": \"324adcc74cea\", \"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\" / \"message\": \"POST /orders -> 503\", \"request_id\": \"324adcc74cea\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 503, \"duration_ms\": 0.309"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:11:36.170Z, 17:11:37.241Z, 17:11:38.309Z, 17:11:39.380Z"
    quote: "\"event\": \"chaos_failure\", \"method\": \"POST\", \"path\": \"/orders\" (request_id b721925fa7a5 -> \"POST /orders -> 503\") / \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/1\" (request_id b4dc9c2157cb -> \"GET /products/1 -> 503\") / \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/orders\" (request_id ff49c2db5db3 -> \"GET /orders -> 503\") / \"event\": \"chaos_failure\", \"method\": \"GET\", \"path\": \"/products/4\" (request_id 0099a6169c2f -> \"GET /products/4 -> 503\")"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:11:20.396Z–17:11:24.634Z"
    quote: "\"message\": \"GET /health -> 200\" (17:11:20.396Z) / \"message\": \"GET /products -> 200\", \"request_id\": \"281001f47572\" (17:11:20.426Z) / \"message\": \"GET /products/1 -> 200\", \"request_id\": \"fdd2db084edc\" (17:11:21.494Z) / \"message\": \"POST /orders -> 201\", \"request_id\": \"1bbc47f9e3f2\" (17:11:22.565Z) / \"message\": \"GET /products/2 -> 200\", \"request_id\": \"e9d1d478d0f1\" (17:11:24.634Z)"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:11:30.837Z, 17:11:34.037Z, 17:11:35.100Z"
    quote: "\"message\": \"GET /products/1 -> 200\", \"request_id\": \"3ba99bf2ca32\", \"status\": 200, \"duration_ms\": 0.809 / \"message\": \"GET /products -> 200\", \"request_id\": \"0845edbbfec8\", \"status\": 200, \"duration_ms\": 0.963 / \"message\": \"GET /products/5 -> 200\", \"request_id\": \"c225286ce313\", \"status\": 200, \"duration_ms\": 0.91"
  - id: E9
    type: metric
    source: "/metrics via probe konan-1787159516-67180 @ 2026-08-19T17:11:56Z"
    quote: "http_requests_total{method=\"GET\",path=\"/orders\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 2 / http_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products/1\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products/4\",status=\"503\"} 1 / http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 5 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 1 / http_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 2"
  - id: E10
    type: metric
    source: "/metrics via probe konan-1787159516-67180 @ 2026-08-19T17:11:56Z"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3 / # TYPE http_exceptions_total counter (no series)"
  - id: E11
    type: probe
    source: "/health via probe konan-1787159515-67174"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":35.962016500066966} -- HTTP 200 in 0.001430s request_id=konan-1787159515-67174"
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-08-19T17:11:19.659Z"
    quote: "{\"ts\": \"2026-08-19T17:11:19.659Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"} (sole startup event; no unhandled_exception/stack lines in the file)"
  - id: E13
    type: metric
    source: "/metrics via probes konan-1787159516-67180 @ 17:11:56Z and konan-1787159642-67266 @ 17:13:59Z"
    quote: "process_uptime_seconds 36.61189516703598 -> process_uptime_seconds 162.56094312504865 / process_max_rss_bytes 46989312 -> process_max_rss_bytes 47022080"
  - id: E14
    type: probe
    source: "/products/1 via probe konan-1787159566-67245 (~17:12:46Z; same input that returned 503 at 17:11:37.241Z)"
    quote: "-- HTTP 200 in 0.001334s request_id=konan-1787159566-67245"
  - id: E15
    type: metric
    source: "/metrics via probe konan-1787159642-67266 @ 2026-08-19T17:13:59Z"
    quote: "faultline_chaos_enabled 1 / http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 4 / # TYPE http_exceptions_total counter (no series)"
gaps:
  - "Who or what issued POST /chaos/enable (client 127.0.0.1:63384, request_id ae9ffa19d95b) and why: /chaos is operator surface outside the investigator's contract, so intent cannot be determined from telemetry."
  - "Observed user-traffic failure share (6 of 12 post-marker requests) is a small sample; the configured failure_rate 0.4 is taken from the chaos_enabled marker, not measured at scale."
usage:
  model: claude-fable-5
  tokens: 1449249
  wall_clock_seconds: 138
---

# Intermittent 503s on shop routes after chaos mode was enabled at runtime

## Summary

**Root cause identified (class: interfaces / runtime configuration change).** At
2026-08-19T17:11:27.700Z chaos mode was enabled on faultline via `POST /chaos/enable`
with `failure_rate 0.4`, `error_status 503`, `extra_latency_ms 0` (E1, E2). From that
moment, a probabilistic share of shop requests (GET /products, GET /products/{id},
GET /orders, POST /orders) is rejected with 503 before the handler runs; each 503 is
tagged `chaos_failure` under the same request_id (E4–E6). Retries succeed because the
injection is probabilistic (E8, E14). `/health` is not covered by the injection (E10,
E15) and the process itself is healthy (E11–E13) — hence the green dashboard. The flag
was still on at 17:13:59Z (E15). Impact: 6 of 12 user requests after the marker failed
with 503, including 2 of 3 order attempts. Confidence: high — every prediction of H1
checked out, the judge validated it, and the alternatives (code defect, process/resource
issue) are invalidated by evidence.

## Timeline

- 17:11:19.659Z — process start, single startup marker (E12).
- 17:11:20.396Z–17:11:24.634Z — all 7 user requests succeed, incl. order 1 created (E7).
- **17:11:27.700Z — config change: `chaos_enabled`, failure_rate 0.4, status 503 (E1, E2).**
- 17:11:29.770Z — first `chaos_failure` / `GET /products -> 503` (E4).
- 17:11:32.967Z, 17:11:36.170Z — two `POST /orders -> 503` (E5, E6).
- 17:11:37.241Z–17:11:39.381Z — 503s on /products/1, GET /orders, /products/4 (E6), interleaved with 200s on the same routes (E8).
- 17:11:44Z — complaint received; 17:11:52Z investigation start.
- 17:11:56Z — baseline: health 200, `faultline_chaos_enabled 1` (E3, E10, E11).
- 17:13:59Z — `faultline_chaos_enabled 1` still; no `chaos_disabled` event in the log (E15).

## Investigation

1. Baseline (17:11:55Z): /health 200, /metrics snapshot, 32-line log tail. The chaos marker and the `chaos_failure` tags were visible already in the baseline.
2. Triage: three lenses in parallel (interfaces, software-defect, infra-process). All three independently anchored the onset to E1; software-defect found no exceptions and no data-dependent shape; infra-process found no restart, no saturation, no latency change.
3. Deep-dive: skipped — H1's triage evidence was deterministic and complete.
4. Judge: H1 validated; H2, H3 invalidated. The judge asked for two strengtheners: a per-request_id join of every 503 to a `chaos_failure` line and a fresh chaos gauge. Both gathered: the join is 1:1 for all six 503s (E4–E6) and the gauge is still 1 at 17:13:59Z (E15).

## Hypotheses

### H1 — chaos mode enabled at runtime injects 503s (validated)
For: config marker E1/E2; live gauge E3/E15; no 503 before the marker E7; every 503 tagged `chaos_failure` with matching request_id E4–E6; interleaved successes E8/E14; counters spread across all shop routes E9; health unaffected E10/E11. Against: none.

### H2 — software defect (invalidated)
No exception counters or stack lines (E10, E12); same input returns 503 then 200 (E6 vs E14, E8); failures spread across every shop route (E9); every 503 carries the chaos tag (E4–E6). Nothing left for a defect to explain.

### H3 — process restart or resource saturation (invalidated)
Single startup marker (E12); uptime monotonic and RSS flat (E13); health 200 throughout (E11, E15); 503s served in ~0.3 ms — fast rejections, not timeouts (E4).

## Safe next steps

- Read-only: watch `faultline_chaos_enabled` and the `chaos_failure` event rate; a `chaos_disabled` log event marks the end of the injection.
- Identify the operator action behind request_id `ae9ffa19d95b` (client 127.0.0.1:63384) through operator-side records — outside this investigator's surface.
- Dashboard note: the health check does not exercise shop routes; a business-surface signal (5xx share on /products, /orders) would have caught this.

## Gaps

- The caller and intent of `POST /chaos/enable` cannot be established from telemetry; `/chaos` is operator surface outside `docs/lab.md`.
- The failure share is measured on 12 post-marker user requests; the 0.4 rate is the configured value from E1, not a large-sample measurement.
