---
konan_journal: 2
investigation:
  id: 2026-11-15-routine-handover-check
  trigger: "manual (/konan, human profile); complaint raised 2026-11-15T13:47:25Z, investigation started 17 s later"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-15T13:47:42Z
  concluded: 2026-11-15T13:51:27Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "User requests to the shop service are failing now, because get_product divides by units_in_stock, which is 0 for product 3, and raises an unhandled ZeroDivisionError (HTTP 500 on GET /products/3)."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E6, E7, E9, E12]
    evidence_against: [E2, E3, E5, E8]
  - id: H2
    statement: "The service is degraded now by a process-lifecycle event or an operational switch: the process started 32 s before the check (a crash, a restart loop, a hang, or an active chaos switch harms traffic)."
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1, E4]
    evidence_against: [E3, E5, E10, E13]
latent_findings:
  - statement: "GET /products/3 fails on every request with an unhandled ZeroDivisionError (HTTP 500): get_product divides by units_in_stock, which is 0 for product 3. Only investigator probes have triggered it in the observed window (4 of 4 requests, all with konan- request ids); no user request has reached it since the process start at 13:47:10.507Z."
    evidence: [E6, E7, E8, E9, E11, E12]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id=konan-1794750462-98940"
    quote: |-
      {"status":"ok","uptime_seconds":32.408310417085886}
      -- HTTP 200 in 0.001908s request_id=konan-1794750462-98940
  - id: E2
    type: metric
    source: "/metrics at baseline, request_id=konan-1794750463-98945 (the complete http_requests_total block)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E3
    type: metric
    source: "/metrics at baseline, request_id=konan-1794750463-98945 (http_exceptions_total has no series)"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 0
      # HELP process_uptime_seconds Seconds since process start.
      # TYPE process_uptime_seconds gauge
      process_uptime_seconds 32.96384191699326
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:47:10.507Z (the only startup event in the file; no rotated backups exist)"
    quote: |-
      {"ts": "2026-11-15T13:47:10.507Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:47:11.245Z to 13:47:19.579Z (every access line in the file whose request_id does not begin with konan-)"
    quote: |-
      {"ts": "2026-11-15T13:47:11.245Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "fb41d7f06ecc", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 11.813, "client": "127.0.0.1:52485"}
      {"ts": "2026-11-15T13:47:11.261Z", "level": "INFO", "logger": "faultline.request", "message": "GET /health -> 200", "request_id": "258f2ad66e4c", "event": "request", "method": "GET", "path": "/health", "status": 200, "duration_ms": 0.815, "client": "127.0.0.1:52486"}
      {"ts": "2026-11-15T13:47:11.272Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "688bed3c9836", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.168, "client": "127.0.0.1:52487"}
      {"ts": "2026-11-15T13:47:12.321Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "1297d174ff21", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.021, "client": "127.0.0.1:52488"}
      {"ts": "2026-11-15T13:47:13.372Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "a2dada27dcff", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.962, "client": "127.0.0.1:52489"}
      {"ts": "2026-11-15T13:47:15.417Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "d25c10b3f775", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.797, "client": "127.0.0.1:52490"}
      {"ts": "2026-11-15T13:47:16.470Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "16217f5a64a8", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.322, "client": "127.0.0.1:52491"}
      {"ts": "2026-11-15T13:47:18.526Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "6b3f25427a47", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.871, "client": "127.0.0.1:52492"}
      {"ts": "2026-11-15T13:47:19.579Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "c7640ebb9752", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.771, "client": "127.0.0.1:52493"}
  - id: E6
    type: probe
    source: "/products, request_id=konan-1794750561-99093"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001499s request_id=konan-1794750561-99093
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:48:25.832Z (stack trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: |-
      {"ts": "2026-11-15T13:48:25.832Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794750505-99035", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "… File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:48:25.841Z to 13:48:43.229Z (every access line in the file with status 500, and every access line in the file for the path /products/3)"
    quote: |-
      {"ts": "2026-11-15T13:48:25.841Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794750505-99035", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.837, "client": "127.0.0.1:52525"}
      {"ts": "2026-11-15T13:48:31.806Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794750511-99054", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.755, "client": "127.0.0.1:52528"}
      {"ts": "2026-11-15T13:48:39.045Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794750519-99060", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.92, "client": "127.0.0.1:52529"}
      {"ts": "2026-11-15T13:48:43.229Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794750523-99070", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.799, "client": "127.0.0.1:52531"}
  - id: E9
    type: metric
    source: "/metrics at 2026-11-15T13:49:22Z, request_id=konan-1794750562-99098"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E10
    type: metric
    source: "/metrics at 2026-11-15T13:49:22Z, request_id=konan-1794750562-99098 (process_max_rss_bytes was also 46530560 at baseline, request_id=konan-1794750463-98945)"
    quote: |-
      faultline_chaos_enabled 0
      process_uptime_seconds 131.54690037481487
      process_max_rss_bytes 46530560
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:48:26.327Z and 13:48:39.544Z"
    quote: |-
      {"ts": "2026-11-15T13:48:26.327Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794750506-99040", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.439, "client": "127.0.0.1:52526"}
      {"ts": "2026-11-15T13:48:39.544Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "konan-1794750519-99065", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 0.487, "client": "127.0.0.1:52530"}
  - id: E12
    type: probe
    source: "/products/3, request_id=konan-1794750505-99035 (HTTP 500; probe run by the software-defect triage lens; the same request as E7 and the first line of E8)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794750505-99035"}
  - id: E13
    type: log
    source: "lab/logs/app.log, whole file (39 lines, 2026-11-15T13:47:10.507Z to 13:49:22.041Z): count of lines that contain the string chaos (grep -c)"
    quote: "0"
gaps:
  - "No telemetry exists before 2026-11-15T13:47:10.507Z: the process was 32 s old at baseline and the log has no rotated backups, so an earlier process, and the reason for this start, are not visible."
  - "The user-traffic sample is small: 9 non-investigator requests, the last at 13:47:19.579Z. No user request arrived during the investigation, so the state 'now' rests on investigator probes and counters."
  - "The write path (POST /orders) for products 3 and 4 was not tested: POST is outside the read-only surface."
  - "No lens exists for load-saturation, third-party, or data-db; those domains were covered only by the baseline readings (request durations, process_max_rss_bytes)."
  - "lab/server.out was not read: the surface contract lists only lab/logs/app.log."
  - "The session context of the triage lenses and of the orchestrator listed the file names of removed earlier journals, and some of the names mention product 3. The probe of /products/3 is justified by E6 (units_in_stock 0) and by the traffic gap in E5, but the names were visible."
usage:
  model: claude-fable-5-2
  tokens: 1641300
  wall_clock_seconds: 225
---

# Routine handover check: no active incident; one latent defect on GET /products/3

## Summary

**No active incident.** The shop service is healthy at the handover: `/health` answers
200 (E1), every user request since the process start returned 200 or 201 in under 12 ms
(E5), the baseline counters held no 5xx status and no exception series (E2, E3), the
chaos switch is off at both scrapes (E3, E10), and the process has run without a restart
since 13:47:10.507Z (E4, E10).

One **latent defect** rides along: `GET /products/3` fails on every request with an
unhandled `ZeroDivisionError` (HTTP 500), because `get_product` divides by
`units_in_stock`, which is 0 for product 3 (E6, E7, E12). Only investigator probes
triggered it: all four 500 responses carry `konan-` request ids (E8), and the counters
show exactly four (E9). No user reached it in the observed window. The first user who
opens product 3 will get a 500.

Confidence: high for the observed window. The window is short (about 2 minutes of
process life, 9 user requests); see Gaps.

Note for the next shift: the four 500s and the four `ZeroDivisionError` counts now in
the metrics and the log come from this investigation, not from users.

## Timeline

- **13:47:10.507Z** — process start, `faultline 0.1.0 started`; the only startup marker
  in the log (E4).
- **13:47:11.245Z – 13:47:19.579Z** — 9 user requests, all 200/201: health, product
  list, products 1, 2 and 5, two orders, the order list (E5).
- **13:47:25Z** — complaint raised (manual trigger).
- **13:47:42Z** — investigation start; `/health` 200, uptime 32.4 s (E1).
- **13:47:43Z** — baseline metrics: only 200/201 statuses, no exception series, chaos
  switch 0, uptime 32.96 s (E2, E3).
- **13:48:25.832Z** — first investigator probe of `/products/3`: unhandled
  `ZeroDivisionError`, HTTP 500 (E7, E8, E12).
- **13:48:26.327Z** — `/products/4` answers 200 (E11).
- **13:48:31.806Z – 13:48:43.229Z** — three more investigator probes of `/products/3`,
  all 500 (E8).
- **13:49:21Z** — product list: product 3 is the only product with `units_in_stock` 0 (E6).
- **13:49:22Z** — final metrics: four 500s and four `ZeroDivisionError` on the product
  route, chaos switch 0, uptime 131.5 s, peak RSS unchanged (E9, E10).

No configuration, deploy, or flag-change marker exists in the log other than the
process start (E4); the log holds no chaos event line (E13).

## Investigation

**Complaint block.** The complaint object, verbatim:

```json
{
  "source": "human",
  "fingerprint": "human-1794750445",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports." },
  "startsAt": "2026-11-15T13:47:25Z"
}
```

Investigation start: `2026-11-15T13:47:42Z`. Trigger latency: 17 s. The reporter stated
no severity, so none is recorded.

**Setup.** `KONAN_ADAPTER` is unset, so the surface contract is the lab, `docs/lab.md`.
Budget: one triage round, at most 3 deep-dives per round, at most 2 rounds.

**Baseline.** `/health` (E1), `/metrics` (E2, E3), and the full log (18 lines at that
time; E4, E5). All clean: one startup, 9 user requests with 2xx statuses, no ERROR line.

**Triage.** The complaint is vague, so all three lenses ran in parallel, each blind to
the others: software-defect, infra-process, interfaces.

- software-defect: one finding — `GET /products/3` returns 500 with `ZeroDivisionError`
  on each probe; product 3 is the only product with zero stock; only investigator
  probes hit it.
- infra-process: no anomaly — one process, one start, uptime monotonic, RSS flat, chaos
  switch off. It named the short history as a limit.
- interfaces: no anomaly in its domain — no 502/503/504, no chaos toggle. It reproduced
  the `/products/3` failure independently and handed it to the software-defect lens.

**Deep-dive.** None. The triage evidence for H1 was deterministic and complete (four of
four probes, the stack frame, the stock value). H2 had no further evidence within reach:
the surface holds nothing from before the process start.

**Judge.** One fresh judge, given only the hypotheses and the verbatim evidence:

- H1 — invalidated: the mechanism is real, but the prediction of user impact failed.
- The latent claim — validated within the observed window.
- H2 — invalidated; the judge asked for one more check, a whole-file search for chaos
  event lines. The search returned zero lines (E13), which closed that gap.
- The judge also noted that E11 does not bear on user impact; it is cited for the
  latent finding only.

Round 1 ended the investigation. No second round was needed.

## Hypotheses

### H1 — user requests fail on the ZeroDivisionError of product 3 (software-defect) — invalidated

The mechanism exists: product 3 has `units_in_stock` 0 (E6), `get_product` divides by
that value at `shop.py` line 64 (E7), and the response is HTTP 500 with
`ZeroDivisionError` (E12, E9). As an **active incident** the hypothesis fails. Its
prediction was 5xx statuses or an exception series from user traffic. The baseline
scrape, taken before any investigator probe of that path, had neither (E2, E3). All 9
user requests returned 2xx and none asked for product 3 (E5). Every 500 in the log
carries a `konan-` request id (E8), and the counter value 4 equals the number of
investigator probes (E9). The defect is recorded as a latent finding.

What would reverse the verdict: one access line for `/products/3` with status 500 and a
request id that does not begin with `konan-`, or a 500 count above the number of
investigator probes.

### H2 — degradation by a process-lifecycle event or an operational switch (infra-process) — invalidated

The process was only 32 s old at the check (E1, E4), which is a lifecycle marker worth a
test. Each prediction failed. The log holds one startup marker (E4). Uptime runs
unbroken from one start: 32.4 s, 32.96 s, then 131.5 s (E1, E3, E10). The chaos switch
reads 0 at both scrapes (E3, E10) and the log holds no chaos event line (E13). Peak RSS
did not move (E10). User requests after the start all succeeded in under 12 ms (E5). A
recent start alone is not a degradation.

## Safe next steps

- Watch `http_requests_total{path="/products/{product_id}",status="500"}` and
  `http_exceptions_total{type="ZeroDivisionError"}`. Both read 4 from investigator
  probes; any rise is user impact.
- Search `lab/logs/app.log` for `/products/3` access lines whose request id does not
  begin with `konan-`.
- Give the latent defect to the owners of the service, with E7 (file, line, expression)
  and E6 (the zero-stock product).
- Repeat the check after more user traffic; this window held 9 user requests.
- Read the reason for the process start at 13:47:10Z from the operator or deploy record;
  the telemetry surface does not hold it.

## Gaps

- **History.** Nothing exists before 13:47:10.507Z: the process was 32 s old at baseline
  and there are no rotated log backups. An earlier process, and the reason for this
  start, are not visible.
- **Sample size.** 9 user requests, the last at 13:47:19.579Z. No user traffic arrived
  during the investigation; "now" rests on investigator probes and counters.
- **Write path.** `POST /orders` for products 3 and 4 was not tested; POST is outside
  the read-only surface. Product 4 has `"price":null` (E6) and reads without error (E11);
  its behaviour in an order is unknown.
- **Lenses.** No lens exists for load-saturation, third-party, or data-db. Those domains
  were covered only by baseline readings (durations, peak RSS).
- **`lab/server.out`.** Not read; the surface contract lists only `lab/logs/app.log`.
- **Blinding.** The session context of the triage lenses and of the orchestrator listed
  file names of removed earlier journals, some of which mention product 3. The probe of
  `/products/3` is justified by the zero stock (E6) and the traffic gap (E5), but the
  names were visible.
