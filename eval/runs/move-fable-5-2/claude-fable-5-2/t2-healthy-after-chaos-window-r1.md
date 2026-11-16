---
konan_journal: 2
investigation:
  id: 2026-11-15-routine-handover-check
  trigger: "manual (/konan, human profile): source human; fingerprint human-1794751411; labels.alertname human-report; no severity stated; startsAt 2026-11-15T14:03:31Z; investigation start 2026-11-15T14:03:37Z; trigger latency 6 s"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report."
  started: 2026-11-15T14:03:37Z
  concluded: 2026-11-15T14:07:25Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "An operational chaos switch inside the target was on from 2026-11-15T14:02:55.720Z to 14:03:02.037Z (failure rate 0.6, status 503) and injected the two 503 responses on GET /products; the switch is off now and injects nothing."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E4, E5, E6, E7, E8, E9, E10, E11, E27]
    evidence_against: []
  - id: H2
    statement: "An unhandled ZeroDivisionError in the product page handler (the turnover score divides by units_in_stock, which is 0 for product 3) fails requests of end users now, so it is an active incident."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E14, E18, E19, E21, E26]
    evidence_against: [E13, E20, E22, E23, E24, E25]
latent_findings:
  - statement: "GET /products/3 fails each time with HTTP 500 and an unhandled ZeroDivisionError: the product page handler divides units_ordered by units_in_stock, and product 3 has units_in_stock 0. In this process lifetime only the investigator's probes triggered it; no request of an end user reached that page."
    evidence: [E14, E18, E19, E20, E21, E22, E26]
evidence:
  - id: E1
    type: probe
    source: "/health, request id konan-1794751426-99914"
    quote: |-
      {"status":"ok","uptime_seconds":54.22897687507793}
      -- HTTP 200 in 0.001531s request_id=konan-1794751426-99914
  - id: E2
    type: metric
    source: "/metrics scrape 1, request id konan-1794751426-99919 (log ts 2026-11-15T14:03:46.556Z)"
    quote: |-
      faultline_chaos_enabled 0
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:02:51.877Z (the only startup event in the log; the log has no backup files)"
    quote: |-
      {"ts": "2026-11-15T14:02:51.877Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:02:55.720Z"
    quote: |-
      {"ts": "2026-11-15T14:02:55.720Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "9e97f4242ebf", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.6, "error_status": 503, "extra_latency_ms": 0}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:02:56.774Z"
    quote: |-
      {"ts": "2026-11-15T14:02:56.774Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "7ff492624552", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:02:56.774Z"
    quote: |-
      {"ts": "2026-11-15T14:02:56.774Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "7ff492624552", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.284, "client": "127.0.0.1:52686"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:03:00.987Z"
    quote: |-
      {"ts": "2026-11-15T14:03:00.987Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "dd5e1262d671", "event": "chaos_failure", "method": "GET", "path": "/products"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:03:00.987Z"
    quote: |-
      {"ts": "2026-11-15T14:03:00.987Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "dd5e1262d671", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.324, "client": "127.0.0.1:52690"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:03:02.037Z"
    quote: |-
      {"ts": "2026-11-15T14:03:02.037Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode disabled", "request_id": "1cd7067a94df", "event": "chaos_disabled"}
  - id: E10
    type: metric
    source: "/metrics scrape 2, request id konan-1794751513-160 (log ts 2026-11-15T14:05:13.907Z); the only series with status 503 in the scrape, and the same value as in scrape 1"
    quote: |-
      http_requests_total{method="GET",path="/products",status="503"} 2
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:03:22.085Z (the first GET /products after the disable line)"
    quote: |-
      {"ts": "2026-11-15T14:03:22.085Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "7330497b5258", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 0.647, "client": "127.0.0.1:52694"}
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:03:24.178Z"
    quote: |-
      {"ts": "2026-11-15T14:03:24.178Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "da90ac1baca7", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.329, "client": "127.0.0.1:52696"}
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:03:26.276Z (the last request in the log that is not the investigator's)"
    quote: |-
      {"ts": "2026-11-15T14:03:26.276Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "7cbe44d4401b", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.919, "client": "127.0.0.1:52699"}
  - id: E14
    type: probe
    source: "/products, request id konan-1794751496-115"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001983s request_id=konan-1794751496-115
  - id: E15
    type: probe
    source: "/orders, request id konan-1794751496-120"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-15T14:02:59.933+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-15T14:03:24.177+00:00"}]
      -- HTTP 200 in 0.001344s request_id=konan-1794751496-120
  - id: E16
    type: probe
    source: "/products/1, request id konan-1794751497-125"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}
      -- HTTP 200 in 0.001433s request_id=konan-1794751497-125
  - id: E17
    type: probe
    source: "/products/4, request id konan-1794751505-146"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001553s request_id=konan-1794751505-146
  - id: E18
    type: probe
    source: "/products/3, request id konan-1794751504-141"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794751504-141"}
      -- HTTP 500 in 0.008921s request_id=konan-1794751504-141
  - id: E19
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:05:04.947Z (stack trimmed to its last frame, with the checkout prefix of its file path redacted)"
    quote: |-
      {"ts": "2026-11-15T14:05:04.947Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1794751504-141", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:05:04.954Z (the first of the only two access lines for /products/3 in the log)"
    quote: |-
      {"ts": "2026-11-15T14:05:04.954Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794751504-141", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.065, "client": "127.0.0.1:52737"}
  - id: E21
    type: probe
    source: "/products/3 (repeat), request id konan-1794751511-155"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794751511-155"}
      -- HTTP 500 in 0.003484s request_id=konan-1794751511-155
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-11-15T14:05:11.066Z (the second of the only two access lines for /products/3 in the log)"
    quote: |-
      {"ts": "2026-11-15T14:05:11.066Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1794751511-155", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.718, "client": "127.0.0.1:52739"}
  - id: E23
    type: metric
    source: "/metrics scrape 1, request id konan-1794751426-99919, before any probe of a product page; the exception counter had no series"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
  - id: E24
    type: metric
    source: "/metrics scrape 1, request id konan-1794751426-99919; the only series for the product page path, no series with status 500"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
  - id: E25
    type: metric
    source: "/metrics scrape 2, request id konan-1794751513-160"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 7
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
  - id: E26
    type: metric
    source: "/metrics scrape 2, request id konan-1794751513-160"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 2
  - id: E27
    type: metric
    source: "/metrics scrape 2, request id konan-1794751513-160"
    quote: |-
      faultline_chaos_enabled 0
      process_uptime_seconds 142.04412125004455
      process_max_rss_bytes 46612480
gaps:
  - "Nothing before the process start at 2026-11-15T14:02:51.877Z is visible: the log has no backup files and the counters begin at that start. Whether that start was a restart after a crash, and whether noise happened before it, could not be checked."
  - "Traffic that is not the investigator's stopped at 2026-11-15T14:03:26.276Z. The state after that time rests on the investigator's probes only."
  - "Order creation (POST /orders) is outside the GET-only probe surface. Its last observed result is the 201 at 2026-11-15T14:03:24.178Z."
  - "Who turned the chaos switch on and off, and why, is on the operator surface and out of reach."
  - "Memory and latency trends rest on two scrapes 87 s apart; a slow growth is not measurable in that span."
usage:
  model: claude-fable-5-2
  tokens: 1496560
  wall_clock_seconds: 228
---

# Routine handover check: no active incident; one past chaos window and one latent defect

## Summary

**Verdict: no active incident.** The shop service answers correctly on health, the
product list, the order list, and the product pages that users requested (E1, E14,
E15, E16, E13). The "noise earlier" matches one event: an operational chaos switch
inside the target was on for 6.3 seconds, from 14:02:55.720Z to 14:03:02.037Z, and
injected two 503 responses on `GET /products` (E4–E9). The switch is off (E2, E27),
the 503 counter did not move after it (E10), and the next `GET /products` returned
200 (E11). Confidence is high for the window that the telemetry covers.

One latent defect rides along: `GET /products/3` fails each time with HTTP 500 and a
`ZeroDivisionError`, because product 3 has zero units in stock (E14, E18, E19, E21).
Only the investigator's probes triggered it (E20, E22, E23, E26); no user request
reached that page in this process lifetime. The telemetry starts at the process start,
14:02:51.877Z (E3); anything before it is a gap.

## Timeline

All times are 2026-11-15, UTC.

- 14:02:51.877 — process start, the only startup event in the log (E3).
- 14:02:55.720 — chaos switch on: failure rate 0.6, status 503, no added latency (E4).
- 14:02:56.774 — first injected failure, `GET /products -> 503` (E5, E6).
- 14:03:00.987 — second injected failure, `GET /products -> 503` (E7, E8).
- 14:03:02.037 — chaos switch off (E9).
- 14:03:22.085 — `GET /products -> 200`, the first after the switch went off (E11).
- 14:03:24.178 — `POST /orders -> 201` (E12).
- 14:03:26.276 — last request that is not the investigator's, `GET /products/5 -> 200` (E13).
- 14:03:31 — complaint raised (`startsAt`); 14:03:37 — investigation start.
- 14:03:46 — baseline probes: health ok, chaos gauge 0, no exception series (E1, E2, E23, E24).
- 14:04:56–14:04:57 — probes of the product list, the order list, and product 1: all 200 (E14, E15, E16).
- 14:05:04.947 — the investigator's probe of `/products/3` raises `ZeroDivisionError`, HTTP 500 (E18, E19, E20).
- 14:05:05 — probe of `/products/4`: 200 (E17).
- 14:05:11.066 — repeat probe of `/products/3`: HTTP 500 again (E21, E22).
- 14:05:13.907 — second metrics scrape: 503 count unchanged at 2, exception count 2, chaos gauge 0 (E10, E25, E26, E27).

## Investigation

Complaint object, as the manual trigger built it:

```json
{
  "source": "human",
  "fingerprint": "human-1794751411",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Routine on-call handover check: anything wrong with the shop service right now? There was some noise earlier but nobody filed a report." },
  "startsAt": "2026-11-15T14:03:31Z"
}
```

Investigation start: 2026-11-15T14:03:37Z (trigger latency 6 s). `KONAN_ADAPTER` was
unset, so the surface contract is `docs/lab.md`.

- **Baseline.** `/health` 200 (E1); `/metrics` scrape 1 (E2, E23, E24); the full log,
  29 lines from the process start (E3).
- **Triage.** The complaint is vague, so all three lenses ran in parallel:
  infra-process, interfaces, software-defect. All three reported the same past event,
  the chaos window (E4–E9), and no active anomaly. All three named the same limit:
  the telemetry begins at the process start. No lens ran a probe.
- **Business surface check by the orchestrator.** Probes of `/products`, `/orders`,
  `/products/1` returned 200 (E14, E15, E16). The product list showed two unusual
  records: product 3 with `units_in_stock` 0 and product 4 with `price` null (E14).
  Product 1's page showed a `turnover_score` that equals units ordered over units in
  stock (E16), so both records were probed. Product 4 returned 200 (E17). Product 3
  returned 500 twice (E18, E21).
- **Deep-dive.** None. The evidence for both hypotheses was already deterministic
  and complete, so both went straight to the judge.
- **Judge.** H1 validated. H2 invalidated as an active incident; the judge read the
  defect itself as real and latent. The judge noted that the product page 200 count
  rose from 5 to 7 between the scrapes (E24, E25); the two requests are the
  investigator's probes of product 1 and product 4 (E16, E17).

Budget used: one triage round, zero deep-dive agents, one judge round.

## Hypotheses

### H1 — a chaos switch inside the target injected the two 503 responses (validated)

The enable line carries failure rate 0.6 and status 503 (E4). Each of the two 503
access lines (E6, E8) has a `chaos_failure` line with the same request id and the same
timestamp (E5, E7), and both fall before the disable line (E9). The 503 counter reads
2 in both scrapes and `/products` is the only path with a 503 series (E10). The first
`GET /products` after the disable line returned 200 (E11), and the gauge of the switch
reads 0 in both scrapes (E2, E27). No evidence against was found. The class is
infra-process: the switch is internal to the target, although its symptom is a 503.
This hypothesis explains the past noise; it is not an active incident.

### H2 — a division by zero on the product page fails user requests now (invalidated)

The defect is real: product 3 has zero units in stock (E14), its page returns 500 on
each probe (E18, E21), and the stack names the division of `units_ordered` by
`units_in_stock` (E19). The claim of user impact fails. The only two access lines for
`/products/3` carry the investigator's request ids (E20, E22). The exception counter
had no series before the probes (E23) and reads exactly 2 after them (E26). The
product page path had no 500 series before the probes (E24) and has 2 after them
(E25). The last user request to a product page returned 200 (E13). The defect is
recorded as a latent finding.

## Safe next steps

- Read the operator records for the two switch requests (request ids `9e97f4242ebf`
  and `1cd7067a94df`) to learn who ran the chaos window and why.
- Watch the access log for a request to `/products/3` whose id does not start with
  `konan-`. Such a line turns the latent defect into user impact.
- When reading `http_exceptions_total{type="ZeroDivisionError"}`, subtract 2: this
  investigation caused both counts.
- Give the latent finding (E19: the division in the product page handler) to the
  owner of the service code for a read of the zero-stock case.
- Read any record of the process from before 14:02:51Z (a supervisor log, a deploy
  record) to learn whether that start was a restart.

## Gaps

- **Before the process start.** The log begins at 14:02:51.877Z with one startup event
  (E3), there are no backup files, and the counters begin there too. A crash, a
  restart, or noise before that time is not visible on this surface. The reporter's
  "noise earlier" matches the chaos window, but an earlier event cannot be excluded.
- **No user traffic after 14:03:26.276Z** (E13). The state after that rests on the
  investigator's probes.
- **Order creation.** `POST /orders` is outside the GET-only probe surface; its last
  observed result is the 201 at 14:03:24.178Z (E12).
- **The origin of the chaos window.** Who toggled the switch is on the operator
  surface, which the investigator does not read.
- **Trends.** Two scrapes 87 s apart show the same peak memory (E27); a slow growth
  is not measurable in that span.
