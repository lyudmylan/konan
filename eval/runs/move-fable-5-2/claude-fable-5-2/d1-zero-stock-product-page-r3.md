---
konan_journal: 2
investigation:
  id: 2026-11-15-product-3-page-500s
  trigger: |-
    manual — /konan human report. Complaint object: {"source":"human","fingerprint":"human-1794748298","labels":{"alertname":"human-report"},"annotations":{"summary":"Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."},"startsAt":"2026-11-15T13:11:38Z"}. Investigation start: 2026-11-15T13:11:55Z (trigger latency 17 s).
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-15T13:11:55Z
  concluded: 2026-11-15T13:15:31Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product detail handler get_product divides units_ordered by the product's units_in_stock with no guard for zero; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The product detail handler get_product computes turnover_score as units_ordered / units_in_stock with no guard for zero; product 3 has units_in_stock 0, so every GET /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500, while products with stock above zero return 200."
    incident_class: software-defect
    state: validated
    evidence_for: [E4, E5, E6, E8, E9, E10, E2, E3, E13]
    evidence_against: []
  - id: H2
    statement: "A process start (restart or rollout) at 13:11:19Z put a faulty build or state in place, and that start is the cause of the product page errors."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1]
    evidence_against: [E11]
  - id: H3
    statement: "An internal degradation switch (chaos mode) injects the HTTP 500 responses."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E7, E6, E4, E5]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:11:19.620Z — the only startup event in the file; the file has no rotated backups"
    quote: |-
      {"ts": "2026-11-15T13:11:19.620Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:11:21.434Z"
    quote: |-
      {"ts": "2026-11-15T13:11:21.434Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "fc1098231c85", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.009, "client": "127.0.0.1:52135"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:11:22.491Z and 2026-11-15T13:11:29.741Z"
    quote: |-
      {"ts": "2026-11-15T13:11:22.491Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "0200191e7e13", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.867, "client": "127.0.0.1:52136"}
      {"ts": "2026-11-15T13:11:29.741Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "20706e2b7d61", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.762, "client": "127.0.0.1:52140"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:11:26.610Z — the stack field is trimmed to its last frame, with the checkout prefix of its file path redacted as <checkout>"
    quote: |-
      {"ts": "2026-11-15T13:11:26.610Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "62a5a7ecfd4c", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "… File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:11:26.621Z, 13:11:27.683Z, 13:11:30.804Z, 13:11:32.922Z — the four non-investigator requests to /products/3; each has an unhandled_exception line with the same request id and the same last stack frame as E4"
    quote: |-
      {"ts": "2026-11-15T13:11:26.621Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "62a5a7ecfd4c", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 11.251, "client": "127.0.0.1:52138"}
      {"ts": "2026-11-15T13:11:27.683Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "5f5597ce07e5", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.689, "client": "127.0.0.1:52139"}
      {"ts": "2026-11-15T13:11:30.804Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "dc382097742e", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.832, "client": "127.0.0.1:52141"}
      {"ts": "2026-11-15T13:11:32.922Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "4919af61b72e", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.802, "client": "127.0.0.1:52143"}
  - id: E6
    type: metric
    source: "/metrics scraped 2026-11-15T13:11:56Z (request_id=konan-1794748316-97193), before any investigator probe of a product path; no other status=\"500\" series and no other http_exceptions_total series in the scrape"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E7
    type: metric
    source: "/metrics scraped 2026-11-15T13:11:56Z (request_id=konan-1794748316-97193); the log holds no chaos_enabled, chaos_disabled, chaos_failure or simulated_exception event"
    quote: |-
      faultline_chaos_enabled 0
  - id: E8
    type: probe
    source: "/products (request_id=konan-1794748418-97282)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001426s request_id=konan-1794748418-97282
  - id: E9
    type: probe
    source: "/products/3 (request_id=konan-1794748368-97237) — one read-only reproduction at 2026-11-15T13:12:48Z"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1794748368-97237"}
      -- HTTP 500 in 0.005003s request_id=konan-1794748368-97237
  - id: E10
    type: probe
    source: "/products/2 (request_id=konan-1794748369-97247)"
    quote: |-
      {"id":2,"name":"Toaster","price":23.0,"units_in_stock":39,"units_ordered":1,"turnover_score":0.02564102564102564}
      -- HTTP 200 in 0.001339s request_id=konan-1794748369-97247
  - id: E11
    type: metric
    source: "/metrics scraped 2026-11-15T13:11:56Z (request_id=konan-1794748316-97193) and 13:12:51Z (request_id=konan-1794748371-97253); /health probed 13:13:00Z (request_id=konan-1794748380-97267)"
    quote: |-
      process_uptime_seconds 36.69177137501538
      process_uptime_seconds 91.5131039172411
      {"status":"ok","uptime_seconds":100.79441683413461}
      -- HTTP 200 in 0.001431s request_id=konan-1794748380-97267
  - id: E12
    type: log
    source: "lab/logs/app.log @ 2026-11-15T13:11:24.550Z and 2026-11-15T13:11:31.861Z — the only two order_created lines"
    quote: |-
      {"ts": "2026-11-15T13:11:24.550Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "111c71228758", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 2, "total_price": 99.0}
      {"ts": "2026-11-15T13:11:31.861Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "499ee3c00438", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 1, "total_price": 23.0}
  - id: E13
    type: probe
    source: "/products/4 (request_id=konan-1794748527-97381) and /products/5 (request_id=konan-1794748527-97386)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.003999s request_id=konan-1794748527-97381
      {"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001431s request_id=konan-1794748527-97386
gaps:
  - "No telemetry from before the process start at 2026-11-15T13:11:19Z: the log has no rotated backups and the counters began at that start. The onset of the errors ('within the last hour') and the status of /products/3 before the start could not be checked; H2 stays inconclusive for that reason."
  - "Why product 3 has units_in_stock 0 is not visible on the surface: no stock-change event exists in the log, and the two orders in the log are for products 1 and 2 (E12). Whether the zero is a normal sold-out state or wrong data could not be checked."
  - "The interfaces lens was not spawned: the baseline showed only status 500 (no 502/503/504), failures on one input at 100% and not at a rate, and no change marker other than the startup event, which the infra-process lens covered. This is an accepted blind spot."
  - "Token totals of the run could not be captured in this session."
usage:
  model: claude-fable-5-2
  tokens: 1611829
  wall_clock_seconds: 216
---

# Product 3 page returns HTTP 500: division by zero on zero stock

## Summary

**Root cause identified** (software defect, unhandled exception). The product detail
handler `get_product` computes a turnover score as `units_ordered / units_in_stock`
(`shop.py` line 64, E4). Product 3 ("Unobtainium Ingot") has `units_in_stock` 0 (E8),
so every `GET /products/3` raises an unhandled `ZeroDivisionError` and returns HTTP 500
(E5, E9). Impact: all four customer requests to `/products/3` in the readable window
failed (E5, E6); the four other products, the product list, orders and health answer
normally (E2, E3, E10, E13). The failure is deterministic per input and still active: a
read-only reproduction failed the same way (E9). Confidence in the mechanism is high.
The onset is not established: telemetry starts at a process start at 13:11:19Z (E1), 7
seconds before the first error, and nothing earlier is readable — so whether that start
(an unannounced restart or rollout) introduced the fault remains open (H2).

## Timeline

- 13:11:19.620Z — process start: `faultline 0.1.0 started`, the only startup event (E1).
  No configuration, flag or chaos marker follows it (E7).
- 13:11:21Z–13:11:22Z — `/products/1` and `/products/2` answer 200 (E2, E3).
- 13:11:24.550Z — order for product 1 created (E12).
- 13:11:26.610Z — first `ZeroDivisionError`, on the first request to `/products/3` after
  the start (E4, E5).
- 13:11:27Z–13:11:32Z — three more customer requests to `/products/3`, all 500 (E5);
  `/products/2` answers 200 in between (E3).
- 13:11:38Z — complaint raised (`startsAt`).
- 13:11:55Z — investigation start; `/health` answers `ok`.
- 13:11:56Z — metrics: four 500s on the product detail route equal four
  `ZeroDivisionError`; chaos gauge 0 (E6, E7).
- 13:12:48Z — investigator reproduction of `/products/3`: 500, `ZeroDivisionError` (E9).
- 13:12:51Z–13:13:00Z — uptime rises without a reset: one start only (E11).
- 13:15:27Z — `/products/4` and `/products/5` answer 200 (E13).

## Investigation

- **Complaint block.** Complaint object, verbatim:
  `{"source":"human","fingerprint":"human-1794748298","labels":{"alertname":"human-report"},"annotations":{"summary":"Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."},"startsAt":"2026-11-15T13:11:38Z"}`.
  Investigation start: 2026-11-15T13:11:55Z (trigger latency 17 s). No severity was
  stated, so none is recorded.
- **Baseline.** `/health` 200 with uptime 36 s; `/metrics` showed 500s only on the
  product detail route, equal in count to `ZeroDivisionError` exceptions (E6), chaos
  gauge 0 (E7); the log (25 lines, no backups) began with a startup event (E1). The
  healthy-monitoring shape applies: health is green while a business path fails.
- **Triage.** Two lenses in parallel, blind to each other: software-defect and
  infra-process. The interfaces lens was not spawned (see Gaps). Software-defect found
  the exception, the zero-stock input, and reproduced once (E4, E8, E9, E10).
  Infra-process found one process start 7 s before the first error, no restart loop, no
  saturation, no latency problem, and the chaos switch off (E1, E7, E11).
- **Deep-dive.** None. H1's triage evidence was deterministic and complete. H2's
  decisive test needs telemetry from before the start, which the surface does not hold.
- **Judge** (fresh, evidence only, E1–E12): H1 validated; H2 inconclusive — settled
  only by the status of one `GET /products/3` recorded before 13:11:19.620Z; H3
  invalidated. The judge noted that "non-zero stock succeeds" was shown for products 1
  and 2 only.
- **After the judge.** Two probes closed that limit: products 4 and 5 answer 200 (E13).
  The judge did not see E13.
- **Conclusion.** The evidence that would settle H2 is out of reach, so the loop ends
  after one round.

## Hypotheses

### H1 — unguarded division by zero stock in the product detail handler (validated)

The stack names the throwing operation: `"turnover_score": units_ordered /
product["units_in_stock"]` in `get_product` (E4). Product 3 is the only product with
stock 0 (E8). All four customer requests to `/products/3` returned 500 with this
exception (E5), the 500 count equals the exception count (E6), and a new read failed the
same way (E9). The same handler answers 200 for products 1, 2, 4 and 5, all with stock
above zero (E2, E3, E10, E13). No evidence against was found. Limit: H1 gives the
mechanism, not the onset.

### H2 — the process start at 13:11:19Z introduced the fault (inconclusive)

The start precedes the first error by 7 s (E1), but the first error is also the first
request to `/products/3` after the start, so the gap shows when traffic arrived, not
when the fault began. There was one start and no restart loop (E11). A start that
shipped the division or set the stock to 0 would produce exactly the H1 pattern, so the
per-input shape does not refute it. No telemetry from before the start exists. The
reporter knows of no deploy; the telemetry shows a process start all the same.

### H3 — a chaos switch injects the 500s (invalidated)

The gauge reads 0 and the log holds no switch event over the whole process life (E7).
Every 500 is accounted for by a real exception in the handler's own code (E4, E5, E6),
on one input at 100%, not across routes at a rate.

## Safe next steps

Read-only suggestions only.

- Read `get_product` in the faultline source at `shop.py` line 64 to confirm that the
  division has no guard for zero stock.
- Look up, outside this surface, why the process started at 13:11:19Z (process manager
  or deploy records) and find one `GET /products/3` status from before that start (a
  proxy log or an older log archive). A 200 validates H2; a 500 invalidates it.
- Look up in the inventory records when product 3 reached stock 0 and whether that
  value is expected.
- List the catalog for other products with stock 0: each one predicts the same failure.
- Watch `http_exceptions_total{type="ZeroDivisionError"}` against
  `http_requests_total{path="/products/{product_id}",status="500"}`; equal growth means
  the same defect is still the only source of 500s.

## Gaps

- **Nothing before the process start.** The log has no rotated backups and the counters
  began at 13:11:19Z. The onset ("within the last hour") and the pre-start behaviour of
  `/products/3` could not be checked. This keeps H2 inconclusive.
- **The origin of the zero stock.** The surface shows the value (E8) but no event that
  set it; the only orders in the log are for products 1 and 2 (E12). A sold-out state
  and wrong data are both possible.
- **Interfaces lens not spawned.** The baseline excluded its domain with evidence: only
  status 500, a per-input failure at 100%, and no change marker other than the startup
  event, which the infra-process lens covered. The blind spot is accepted and recorded.
- **Token totals.** The session could not capture them; `usage.tokens` is null.
