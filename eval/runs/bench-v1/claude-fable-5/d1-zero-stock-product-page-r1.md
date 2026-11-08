---
konan_journal: 1
investigation:
  id: 2026-08-19-products-3-zero-stock-500s
  trigger: "manual (/konan; complaint source=human fingerprint=human-1787175333 labels.alertname=human-report startsAt=2026-08-19T21:35:33Z; investigation start 2026-08-19T21:35:41Z; trigger latency 8s)"
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-08-19T21:35:41Z
  concluded: 2026-08-19T21:38:48Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{id} computes turnover_score as units_ordered / units_in_stock in shop.py get_product (line 64); product 3 has units_in_stock 0, so every request for /products/3 raises ZeroDivisionError and returns HTTP 500 while other product ids succeed."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "Data-dependent code defect: get_product divides units_ordered by product[\"units_in_stock\"]; product id 3 has zero stock, so /products/3 deterministically raises ZeroDivisionError -> HTTP 500; sibling ids on the same route return 200."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9]
    evidence_against: []
  - id: H2
    statement: "Injected chaos, failing dependency, or a config/deploy change causes probabilistic per-request 500s on the product route."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E11, E5, E6, E9]
  - id: H3
    statement: "Process restart/crash loop or resource saturation (memory, worker starvation) produces the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E12, E13, E14]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:35:21.177Z"
    quote: "{\"ts\": \"2026-08-19T21:35:21.177Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"78947014de29\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"... File \\\"<checkout>/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\\nZeroDivisionError: division by zero\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:35:21.187Z"
    quote: "{\"ts\": \"2026-08-19T21:35:21.187Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"78947014de29\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 11.297, \"client\": \"127.0.0.1:65496\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:35:22.258Z, 21:35:25.407Z, 21:35:27.556Z"
    quote: "\"message\": \"GET /products/3 -> 500\", \"request_id\": \"c43c6cab1a21\" ... \"message\": \"GET /products/3 -> 500\", \"request_id\": \"59ddded2dcfb\" ... \"message\": \"GET /products/3 -> 500\", \"request_id\": \"8b089f4cf696\" — each preceded by \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\" with the same shop.py line 64 frame"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:35:15.971Z, 21:35:17.038Z, 21:35:24.331Z"
    quote: "\"message\": \"GET /products/1 -> 200\", \"request_id\": \"efed1aa20d62\" ... \"message\": \"GET /products/2 -> 200\", \"request_id\": \"99776d58bef3\" ... {\"ts\": \"2026-08-19T21:35:24.331Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/2 -> 200\", \"request_id\": \"a5144512c69a\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/2\", \"status\": 200, \"duration_ms\": 0.723, \"client\": \"127.0.0.1:65498\"}"
  - id: E5
    type: metric
    source: "/metrics @ konan-1787175359-72092"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3 | http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 4 | http_exceptions_total{type=\"ZeroDivisionError\"} 4 | (no status 502/503/504 series present)"
  - id: E6
    type: probe
    source: "/products/3 @ konan-1787175471-72239"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787175471-72239\"} -- HTTP 500 in 0.004606s request_id=konan-1787175471-72239"
  - id: E7
    type: probe
    source: "/products @ konan-1787175473-72245"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":118},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}] -- HTTP 200 in 0.001266s request_id=konan-1787175473-72245"
  - id: E8
    type: probe
    source: "/products/1 @ konan-1787175476-72251"
    quote: "{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":118,\"units_ordered\":2,\"turnover_score\":0.01694915254237288} -- HTTP 200 in 0.001408s request_id=konan-1787175476-72251"
  - id: E9
    type: probe
    source: "/products/3, /products/1, /products/4 @ konan-1787175407-72176, konan-1787175409-72182, konan-1787175411-72188, konan-1787175429-72221 (triage lens probes)"
    quote: "-- HTTP 500 in 0.007909s request_id=konan-1787175407-72176 | -- HTTP 500 in 0.003326s request_id=konan-1787175409-72182 | /products/1: -- HTTP 200 in 0.001494s request_id=konan-1787175411-72188 | /products/4: HTTP 200 request_id=konan-1787175429-72221"
  - id: E10
    type: metric
    source: "/metrics @ konan-1787175359-72092"
    quote: "faultline_chaos_enabled 0"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:35:14.145Z (whole file: 25 lines, 21:35:14.145Z–21:35:59.974Z)"
    quote: "{\"ts\": \"2026-08-19T21:35:14.145Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"} — the only startup marker; no lines with event chaos_enabled / chaos_disabled / chaos_failure / simulated_exception"
  - id: E12
    type: probe
    source: "/health @ konan-1787175354-72084 and konan-1787175427-72215"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":40.86357470811345} -- HTTP 200 in 0.001381s request_id=konan-1787175354-72084 | {\"status\":\"ok\",\"uptime_seconds\":112.92610183311626} HTTP 200 request_id=konan-1787175427-72215"
  - id: E13
    type: metric
    source: "/metrics @ konan-1787175359-72092 and konan-1787175412-72194"
    quote: "process_max_rss_bytes 48300032 (both scrapes, ~52s apart) | process_uptime_seconds 45.8406079581473 -> 98.01047079195268"
  - id: E14
    type: metric
    source: "/metrics @ konan-1787175412-72194"
    quote: "http_request_duration_seconds_sum{method=\"GET\",path=\"/products/{product_id}\"} 0.0383392502553761 | http_request_duration_seconds_count{method=\"GET\",path=\"/products/{product_id}\"} 10"
gaps:
  - "Log retention covers only the current process lifetime (first line 2026-08-19T21:35:14.145Z; no app.log.1–.3 backups), so the reporter's 'started within the last hour' onset and any earlier known-good state for /products/3 cannot be corroborated or refuted from telemetry."
  - "The lab surface does not expose when product 3's units_in_stock became 0 (data change vs. seeded), so whether the trigger was a stock change or a latent defect meeting existing data is not determinable; no code or DB access under the read-only contract."
  - "Which customers/pages the reporter meant is not in the complaint; the mapping to /products/3 is inferred from telemetry (only failing route/input), not from the reporter."
usage:
  model: claude-fable-5
  tokens: 2034158
  wall_clock_seconds: 187
---

# GET /products/3 returns 500: ZeroDivisionError on zero-stock product in get_product

## Summary

**Verdict: root cause identified (software-defect).** The product detail handler
`get_product` (faultline `shop.py` line 64) computes
`turnover_score = units_ordered / product["units_in_stock"]`. Product id 3
("Unobtainium Ingot") has `units_in_stock: 0` (E7), so every `GET /products/3`
raises `ZeroDivisionError` and returns HTTP 500 (E1, E2, E3, E6, E9). Other product ids
on the same route return 200 (E4, E8, E9). Impact: 4 of 4 user (unstamped) requests to
`/products/3` failed; all other user traffic (`/products`, `/products/1`, `/products/2`,
`POST /orders`) succeeded. The failure is deterministic per input, which matches the
complaint ("still happening when they refresh", "other pages load fine"). Confidence:
high — the stack frame names the expression, counts match exactly (E5), and live
probes reproduce it. Chaos injection (E10, E11) and process/resource faults (E11–E14)
are excluded.

## Timeline

- 21:35:14.145Z — process start, single `startup` marker (E11).
- 21:35:15.971Z / 21:35:17.038Z — `GET /products/1`, `/products/2` → 200 (E4).
- 21:35:21.177Z — first `unhandled_exception` ZeroDivisionError at `shop.py:64` (E1);
  21:35:21.187Z `GET /products/3 -> 500`, request_id `78947014de29` (E2).
- 21:35:22.258Z, 21:35:25.407Z, 21:35:27.556Z — three more `/products/3 -> 500`, same
  exception (E3); 21:35:24.331Z `/products/2 -> 200` interleaved (E4).
- 21:35:54Z–21:36:00Z — baseline: health ok, chaos gauge 0, counters 3×200 / 4×500 /
  4 ZeroDivisionError (E5, E10, E12).
- 21:36:47Z–21:37:09Z — triage probes reproduce 500 on id 3, 200 on ids 1 and 4 (E9);
  uptime monotonic, RSS flat (E12, E13).
- 21:37:51Z–21:37:56Z — orchestrator probes: `/products/3` 500 (E6), listing shows id 3
  with `units_in_stock: 0` (E7), `/products/1` 200 with `turnover_score` (E8).
- No configuration / deploy / chaos change markers exist in the log (E11).

## Investigation

- **Baseline**: `/health` 200, uptime ~41 s, `/metrics` snapshot, full log tail
  (25 lines). 500s already visible, all on `GET /products/3`, all from unstamped clients.
- **Triage** (one round, three lenses in parallel, each blind): software-defect found the
  deterministic ZeroDivisionError pinned to id 3; interfaces found no change markers, no
  chaos, no gateway statuses, 100%/0% split by input; infra-process found single startup,
  monotonic uptime, flat RSS, fast failures.
- **Deep-dive**: skipped — H1's triage evidence was already deterministic and complete;
  the orchestrator added three verbatim probes (E6–E8) for the ledger.
- **Judge**: H1 validated; H2 invalidated; H3 invalidated.

## Hypotheses

### H1 — zero-stock division in `get_product` (software-defect) — validated
For: stack frame names the line and expression (E1); the exception binds to
`GET /products/3 -> 500` by request id (E2) and repeats identically (E3); counts match
(4 exceptions = 4×500, E5); live probes reproduce 500 on id 3 (E6, E9) and 200 on ids
1, 2, 4 (E4, E8, E9); the listing shows id 3 is the only zero-stock product (E7) and the
success path computes `turnover_score` from a non-zero divisor (E8). Against: none.

### H2 — chaos / dependency / config change (interfaces) — invalidated
`faultline_chaos_enabled 0` (E10); no chaos or change markers in the log, the only
lifecycle marker precedes the first known-good request (E11); no 502/503/504 (E5);
failure is 100% on one input and 0% on others (E6, E9), not a per-request fraction.

### H3 — restart / saturation (infra-process) — invalidated
One startup marker (E11); uptime grows monotonically with health ok (E12, E13); peak
RSS identical across ~52 s (E13); mean latency ~3.8 ms including failures (E14).

## Safe next steps

- Read-only: check whether any other product reaches `units_in_stock: 0` (listing E7
  shows only id 3 today); a second zero-stock product would fail the same way.
- Read-only: confirm in source control whether `shop.py` line 64 guards the divisor
  (no code access under the lab contract; out of scope here).
- Note for responders: `/products/4` returns `"price":null` (E7) — served 200, not part
  of this incident, but an irregular payload worth a look.

## Gaps

- Log retention equals the process lifetime; the "last hour" onset cannot be checked.
- When product 3's stock reached 0 is not observable from the surface; whether the
  trigger was a data change or a seeded row is unknown.
- The reporter did not name the page; `/products/3` is inferred as the only failing
  route/input in telemetry.
