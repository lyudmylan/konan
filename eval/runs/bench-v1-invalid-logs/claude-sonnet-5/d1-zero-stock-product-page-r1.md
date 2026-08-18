---
konan_journal: 1
investigation:
  id: 2026-08-18-product-3-500s
  trigger: manual
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-08-18T18:48:21Z
  concluded: 2026-08-18T18:53:32Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/3 unconditionally raises an unhandled ZeroDivisionError in get_product (division by product['units_in_stock']) because product 3 has units_in_stock = 0, so every request to that product's detail page returns HTTP 500 while every other product's page succeeds."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "get_product computes turnover_score as units_ordered / units_in_stock with no guard for a zero divisor; product 3 ('Unobtainium Ingot') has units_in_stock = 0, so its detail route deterministically 500s on every request while other products succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14]
    evidence_against: []
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:48:10.692Z"
    quote: "unhandled exception: division by zero ... exception_type: ZeroDivisionError ... File \".../faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:48:10.703Z"
    quote: "GET /products/3 -> 500, request_id=19b4aea67888, status=500, duration_ms=11.41"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:48:11.765Z"
    quote: "GET /products/3 -> 500, request_id=ce8095211068, status=500, duration_ms=4.871 (unhandled_exception ZeroDivisionError, same shop.py:64 stack)"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:48:14.887Z"
    quote: "GET /products/3 -> 500, request_id=4a6cae08ddc3, status=500, duration_ms=5.002 (unhandled_exception ZeroDivisionError, same shop.py:64 stack)"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:48:17.011Z"
    quote: "GET /products/3 -> 500, request_id=6ddce79b4bf2, status=500, duration_ms=4.776 (unhandled_exception ZeroDivisionError, same shop.py:64 stack)"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:48:05.511Z"
    quote: "GET /products/1 -> 200, request_id=4913b4feb20a, status=200, duration_ms=1.422"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:48:06.571Z and 18:48:13.825Z"
    quote: "GET /products/2 -> 200, request_id=b559d37b5d6a, status=200, duration_ms=0.997 ; GET /products/2 -> 200, request_id=0c8ad0e5008c, status=200, duration_ms=0.771"
  - id: E8
    type: metric
    source: "/metrics @ 2026-08-18T18:48:37Z (probe request_id konan-1787078937-18131)"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3 ; http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 4 ; http_exceptions_total{type=\"ZeroDivisionError\"} 4"
  - id: E9
    type: metric
    source: "/metrics @ 2026-08-18T18:48:37Z (probe request_id konan-1787078937-18131)"
    quote: "faultline_chaos_enabled 0"
  - id: E10
    type: probe
    source: "GET /products/3, request_id konan-1787079070-18288"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787079070-18288\"} -- HTTP 500 in 0.004478s"
  - id: E11
    type: probe
    source: "GET /products, request_id konan-1787079074-18300"
    quote: "[{\"id\":1,...},{\"id\":2,...},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,...},{\"id\":5,...}] -- HTTP 200"
  - id: E12
    type: probe
    source: "GET /products/1, request_id konan-1787079070-18294"
    quote: "{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":118,\"units_ordered\":2,\"turnover_score\":0.01694915254237288} -- HTTP 200"
  - id: E13
    type: probe
    source: "GET /products/4, request_id konan-1787079209-18367"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0} -- HTTP 200"
  - id: E14
    type: probe
    source: "GET /products/5, request_id konan-1787079209-18373"
    quote: "{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500,\"units_ordered\":0,\"turnover_score\":0.0} -- HTTP 200"
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-18T18:29:17.911Z, 18:39:32.880Z, 18:48:03.701Z"
    quote: "event=startup, version=0.1.0 (identical across all three process starts — no version change)"
gaps:
  - "No order_created event for product_id 3 appears anywhere in lab/logs/app.log (no rotated .1-.3 backups exist), so whether units_in_stock reached 0 via legitimate order volume or was seeded at 0 could not be determined from telemetry."
  - "The stack trace's source location (shop.py:64) is the application's own self-report via logs; the investigator's read-only surface (docs/lab.md) does not include reading faultline's source tree, so the line could not be independently inspected outside what the log already quotes."
usage:
  model: claude-sonnet-5
  tokens: 3431908
  wall_clock_seconds: 311
---

# Product 3 detail page: 500 Internal Server Error on every request (zero-stock division)

## Summary

**Root cause identified.** Every `GET /products/3` request returns HTTP 500 with an
unhandled `ZeroDivisionError`, because `get_product` computes
`turnover_score = units_ordered / units_in_stock` with no guard for a zero divisor, and
product 3 ("Unobtainium Ingot") has `units_in_stock = 0`. All other products (1, 2, 4, 5)
were probed directly and succeed. This exactly matches the complaint: a specific product
page erroring with "Internal Server Error," reproducible on every refresh, with other
pages unaffected. No chaos injection, config change, or deploy correlates with the
failures — the process version (0.1.0) is unchanged across all restarts observed, and
`faultline_chaos_enabled` is 0. Confidence: high — the defect was reproduced live by the
investigator's own probe in addition to 4 real (non-investigator) user requests failing
identically.

## Timeline

- **2026-08-18T18:29:17.911Z / 18:39:32.880Z / 18:48:03.701Z** — process startups, all
  version 0.1.0 (E15) — rules out a version-bump deploy as the trigger.
- **18:48:05.511Z–18:48:13.825Z** — `/products/1` and `/products/2` succeed (E6, E7),
  interleaved in time with the failures below — the route itself is healthy.
- **18:48:10.692Z–18:48:17.011Z** — four `GET /products/3` requests from real user
  traffic (non-`konan-` request ids) each fail with the identical `ZeroDivisionError`
  stack trace at `shop.py:64` (E1–E5).
- **18:51:10Z (approx.)** — investigator probe reproduces the failure on demand
  (E10, request id `konan-1787079070-18288`).
- **18:51:14Z (approx.)** — investigator probe of `/products` confirms product 3's
  `units_in_stock` is 0 (E11); probe of `/products/1` shows the same formula succeeding
  with a nonzero divisor (E12).
- **18:53:29Z (approx.)** — investigator probes of `/products/4` and `/products/5`
  both succeed (E13, E14), closing the "other products" comparison.

## Investigation

- **Baseline**: `/health` ok; `/metrics` already showed
  `http_requests_total{...path="/products/{product_id}",status="500"} 4` against
  `http_exceptions_total{type="ZeroDivisionError"} 4` on a process barely a minute old.
- **Triage (parallel, 3 lenses)**: software-defect lens found the deterministic
  single-input failure and the exact stack trace; infra-process lens found the current
  process stable (no crash loop, RSS flat at ~48MB, latency normal) and confirmed the
  errors aren't tied to a restart; interfaces lens found no gateway-shaped statuses, no
  probabilistic failure rate, and no config/chaos/deploy marker preceding onset. No
  competing hypothesis was raised.
- **Confirmation**: given deterministic, complete triage evidence, deep-dive was
  skipped per protocol and the hypothesis went straight to the judge.
- **Judge**: validated H1's mechanism, ruled out chaos/infra/config/coincidence using
  only the cited evidence, and flagged one gap — products 4 and 5 hadn't been directly
  probed. Closed by probing both (E13, E14): both succeed.

## Hypotheses

### H1 — zero-stock division defect on `/products/3` (validated)

`get_product` divides by `units_in_stock` without a zero check. Product 3 has
`units_in_stock = 0` (E11), so every request to `/products/3` throws (E1–E5, E10), while
the same code path succeeds for products with nonzero stock (E6, E7, E12, E13, E14).
Exception and 500 counts match 1:1 (E8), chaos is off (E9), and no deploy/version change
precedes the failures (E15). No evidence against.

## Safe next steps

- Read-only: keep monitoring `http_exceptions_total{type="ZeroDivisionError"}` and
  `http_requests_total{path="/products/{product_id}",status="500"}` — the count should
  stay pinned to product 3 traffic only, confirming no spread to other products.
- Read-only: if a product catalog or inventory feed is inspectable elsewhere, check
  whether other products are approaching `units_in_stock = 0` — same code path would
  fail for them too.

## Gaps

- No `order_created` event for `product_id: 3` exists anywhere in `lab/logs/app.log`
  (no rotated `.1`–`.3` backups were present to check further back), so whether the
  zero stock was seeded that way or drained by earlier, unlogged activity could not be
  determined from telemetry alone.
- The investigator's surface contract (`docs/lab.md`) permits only probes and log/metric
  reads, not reading faultline's source tree directly — the `shop.py:64` line and its
  surrounding function were taken from the application's own logged stack trace, not
  independently inspected.
