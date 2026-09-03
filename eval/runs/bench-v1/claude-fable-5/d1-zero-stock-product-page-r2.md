---
konan_journal: 1
investigation:
  id: 2026-08-19-products-3-500s
  trigger: 'manual (/konan, human profile): source=human, fingerprint=human-1787175645,
    labels.alertname=human-report, startsAt=2026-08-19T21:40:45Z; investigation started
    2026-08-19T21:41:05Z — trigger latency 20s'
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-08-19T21:41:05Z
  concluded: 2026-08-19T21:44:36Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{id} computes turnover_score = units_ordered / product[\"units_in_stock\"] (shop.py:64, get_product); product 3 has units_in_stock = 0, so every request for /products/3 raises an unhandled ZeroDivisionError and returns 500, while other product pages succeed."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "A data-dependent code defect: get_product (shop.py:64) divides units_ordered by product[\"units_in_stock\"]; product 3 has stock 0, so /products/3 deterministically raises ZeroDivisionError and returns 500 to real (non-investigator) traffic."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E9]
    evidence_against: []
  - id: H2
    statement: "Chaos mode or a simulated fault injection causes the 500s."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E7, E2, E6]
  - id: H3
    statement: "A process crash, restart, or resource exhaustion causes the errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E8, E6]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:40:35.548Z"
    quote: "{\"ts\": \"2026-08-19T21:40:35.548Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"e1deb12443f9\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"... File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\n... ZeroDivisionError: division by zero\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:40:35.559Z (identical exception+500 pairs also at 21:40:36.623/36.628 request_id 5daec58ade93, 21:40:39.765/39.770 db5cc60538fb, 21:40:41.912/41.917 591504c0b476 — all unstamped, non-konan ids)"
    quote: "{\"ts\": \"2026-08-19T21:40:35.559Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"e1deb12443f9\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 11.368, \"client\": \"127.0.0.1:49188\"}"
  - id: E3
    type: metric
    source: "/metrics @ 2026-08-19T21:41:08Z, request_id konan-1787175668-72424"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 4 ; http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3 ; http_exceptions_total{type=\"ZeroDivisionError\"} 4 ; faultline_chaos_enabled 0"
  - id: E4
    type: probe
    source: "/products, request_id konan-1787175714-72479"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":118},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}] -- HTTP 200 in 0.001387s request_id=konan-1787175714-72479"
  - id: E5
    type: probe
    source: "/products/3, request_id konan-1787175710-72472 (triage reproduction; post-probe /metrics)"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787175710-72472\"} -- HTTP 500 in 0.004016s request_id=konan-1787175710-72472 ; then http_exceptions_total{type=\"ZeroDivisionError\"} 5 ; http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 5"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:40:30.335Z and 21:40:38.697Z"
    quote: "{\"ts\": \"2026-08-19T21:40:30.335Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"4ab2c85e277a\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 1.138, \"client\": \"127.0.0.1:49184\"} ; {\"ts\": \"2026-08-19T21:40:38.697Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/2 -> 200\", \"request_id\": \"9652a90b49dd\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/2\", \"status\": 200, \"duration_ms\": 0.847, \"client\": \"127.0.0.1:49190\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T21:40:28.512Z (only lifecycle marker in the file; no rotated backups; no chaos_enabled/chaos_disabled/chaos_failure/simulated_exception events anywhere in the log)"
    quote: "{\"ts\": \"2026-08-19T21:40:28.512Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E8
    type: metric
    source: "/health @ 2026-08-19T21:41:05Z (request_id konan-1787175665-72418) and /metrics @ ~21:41:55Z (triage re-read)"
    quote: "uptime_seconds 37.380468416027725 ; then process_uptime_seconds 88.99256429099478 ; process_max_rss_bytes 48447488 -> 48480256"
  - id: E9
    type: probe
    source: "/products/4, request_id konan-1787175870-72552"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0} -- HTTP 200 in 0.001642s request_id=konan-1787175870-72552"
gaps:
  - "Onset time: the telemetry window is shorter than the complaint's 'started within the last hour' — the log begins at process startup 2026-08-19T21:40:28Z with no rotated backups, and no known-good /products/3 request exists in the window, so 'worked until T' cannot be established from this surface."
  - "'Customers' identification rests on request-id shape only: all failing requests carry unstamped non-konan ids, but every client is 127.0.0.1 (lab traffic simulation), so 'real users' means 'non-investigator traffic', nothing stronger."
  - "Chaos-gauge faithfulness is assumed: faultline_chaos_enabled 0 and the absence of chaos events are taken at face value; the chaos module source is outside the investigator's surface."
  - "No OS/PID history is on the surface, so an external restart-with-log-truncation cannot be excluded by records; the monotonic uptime metric makes it near-impossible."
usage:
  model: claude-fable-5
  tokens: 1793799
  wall_clock_seconds: 211
---

# /products/3 returns 500 on every request: division by zero on a zero-stock product

## Summary

Root cause identified. `GET /products/{id}` computes `turnover_score = units_ordered / product["units_in_stock"]` in `get_product` (`shop.py:64`). Product 3 ("Unobtainium Ingot") has `units_in_stock: 0` (E4), so every request for `/products/3` raises an unhandled `ZeroDivisionError` and returns HTTP 500 (E1, E2). The failure is deterministic and data-dependent: 5 of 5 requests to `/products/3` failed, including one investigator reproduction (E5), while `/products/1`, `/products/2` (E6), `/products/4` (E9), and the `/products` list (E4) all return 200. Real (non-investigator) traffic is affected — all four pre-investigation 500s carry unstamped request ids (E2). This matches the complaint exactly: one product page errors on every refresh; other pages load fine. Confidence is high; the adversarial judge validated H1 and invalidated the two alternatives on direct disconfirming evidence.

## Timeline

- 2026-08-19T21:40:28Z — process start, the only lifecycle marker; no chaos or config-change events anywhere in the log (E7).
- 21:40:30–21:40:38Z — `/products/1` and `/products/2` return 200 (E6).
- 21:40:35.548Z — first `unhandled_exception` `ZeroDivisionError` at `shop.py:64`; the paired access line is `GET /products/3 -> 500` (E1, E2).
- 21:40:36.6Z, 21:40:39.7Z, 21:40:41.9Z — three more identical exception+500 pairs on `/products/3`, all unstamped (user) request ids; a `/products/2 -> 200` sits between two of them (E2, E6).
- 21:40:45Z — complaint stamped (`startsAt`); 21:41:05Z — investigation start (trigger latency 20s).
- 21:41:05–21:41:08Z — baseline: `/health` 200, uptime 37s, `faultline_chaos_enabled 0`, `ZeroDivisionError` counter at 4 (E3, E8).
- ~21:41:50Z — triage reproduction: `/products/3` returns 500 with `exception_type: ZeroDivisionError`; both counters advance by exactly 1 (E5).
- 21:43:xx–21:44:30Z — judge validates H1; follow-up probe `/products/4 -> 200` closes the judge's open item (E9).

## Investigation

- **Baseline**: `/health` 200 (uptime 37s), `/metrics` snapshot, full log read (25 lines, no backups). The baseline itself already showed the anomaly: 4× `GET /products/3 -> 500` with `ZeroDivisionError` stacks, everything else 2xx.
- **Triage**: three lenses in parallel — software-defect, infra-process, interfaces. Software-defect confirmed the deterministic per-input failure and reproduced it once (E5). Infra-process found a clean lifecycle: no restart, flat RSS, low latency (E7, E8). Interfaces found no chaos/config/deploy marker and noted the per-input (not per-request) failure shape (E3, E7).
- **Deep-dive**: skipped — triage evidence was deterministic and complete; hypotheses went straight to the judge.
- **Judge**: validated H1; invalidated H2 and H3 on direct disconfirming evidence. Flagged one open item (`/products/4` untested) and two overreaches (see Gaps).
- **Round 2 gathering**: one probe, `/products/4 -> 200` (E9), closing the open item.

## Hypotheses

### H1 — data-dependent division-by-zero in get_product (validated)

The stack names the exact operation: `shop.py:64`, `"turnover_score": units_ordered / product["units_in_stock"]` (E1). The catalog shows the divisor is 0 only for product 3 (E4). Every `/products/3` request fails (E2, E5 — 5 of 5, including a live reproduction that advanced both the 500 counter and the `ZeroDivisionError` counter by exactly 1), while sibling inputs on the same route succeed before, between, and after the failures (E6, E9). The exception counter equals the 500 counter (E3), so no other error type hides in the totals. Nothing on the surface contradicts it.

### H2 — chaos/injected degradation (invalidated)

`faultline_chaos_enabled 0` (E3) and zero chaos/simulated-fault events in a log that starts before the first error (E7). The failure shape is also wrong for injection: deterministic per-input, tied to a real data condition at a real code line, with successes interleaved on the same route (E2, E6).

### H3 — process crash/restart/resource exhaustion (invalidated)

One startup marker (E7), monotonic uptime consistent with that start time, RSS flat within ~32 KB (E8), and the process served 200s between the 500s (E6). The errors are in-request exceptions in a stable process.

## Safe next steps

Read-only suggestions only:

- Watch `http_exceptions_total{type="ZeroDivisionError"}` against `http_requests_total{...,status="500"}` to track ongoing user impact until the defect is fixed.
- If retention allows elsewhere (outside this lab's surface), check when product 3's `units_in_stock` reached 0 — that moment is the true onset the current log window cannot show.
- Note for the responder: `units_ordered` is exposed on `/products/4` (E9) but not on the `/products` list (E4) — the list and detail views disagree on shape; worth a look while in that code.

## Gaps

- The log window starts at 21:40:28Z with no rotated backups, so the complaint's "started within the last hour" onset cannot be verified; no known-good `/products/3` request exists on the surface.
- "Customers" is inferred from unstamped (non-`konan-*`) request ids; all clients are 127.0.0.1 in this lab, so the claim is "non-investigator traffic", not verified end users.
- The chaos gauge and event log are trusted to reflect runtime chaos state; the chaos module source is outside the investigator-readable surface.
- No OS/PID history is available on the surface to formally exclude an external restart with log truncation; the monotonic uptime metric (E8) makes this near-impossible.
