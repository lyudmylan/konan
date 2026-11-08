---
konan_journal: 1
investigation:
  id: 2026-08-19-products-3-zerodivision
  trigger: "manual — /konan adapter (human profile). Complaint object: source=human, fingerprint=human-1787121314, labels.alertname=human-report (no severity stated by the reporter), startsAt=2026-08-19T06:35:14Z. Investigation started 2026-08-19T06:35:33Z — trigger latency 19s."
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-08-19T09:35:33+03:00
  concluded: 2026-08-19T09:43:00+03:00
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product-detail handler computes turnover_score by dividing units_ordered by product['units_in_stock'] with no zero guard, so every request for product 3 — whose units_in_stock is 0 — raises an unhandled ZeroDivisionError and returns HTTP 500."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "GET /products/3 returns HTTP 500 because the product-detail handler divides units_ordered by product['units_in_stock'] without a zero guard, and product 3's units_in_stock is 0, so the request raises an unhandled ZeroDivisionError."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E5, E6, E7, E13]
    evidence_against: []
  - id: H2
    statement: "The 500s are caused by an infrastructure or process-level fault — a crash/restart loop, resource saturation, or worker starvation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E8, E9, E10, E12, E13]
  - id: H3
    statement: "The 500s were introduced by a configuration change, feature-flag flip, chaos injection, or deploy shortly before onset."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E9, E10, E11, E12]
latent_findings:
  - statement: "The 500 error envelope returns the internal Python exception class name to callers ('exception_type':'ZeroDivisionError'), disclosing implementation detail in a client-facing response. Exposure is unquantified — every probe was from loopback and the route's auth posture is not on the investigator surface."
    evidence: [E6]
  - statement: "GET /products/{product_id} declares only 200 and 422 in /openapi.json, but emits 500 and 404 in live traffic; neither response shape is described, so generated clients have no typed handling for either."
    evidence: [E6, E11, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:35:01.899Z"
    quote: "{\"ts\": \"2026-08-19T06:35:01.899Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"b838193d818d\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"Traceback (most recent call last):\\n  … \\n  File \\\"<checkout>/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\\nZeroDivisionError: division by zero\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:35:01.910Z"
    quote: "{\"ts\": \"2026-08-19T06:35:01.910Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"b838193d818d\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 11.341, \"client\": \"127.0.0.1:57373\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:35:02.972Z, 06:35:06.095Z, 06:35:08.217Z — the other three user-traffic 500s, each preceded by an identical ZeroDivisionError stack at shop.py line 64"
    quote: "{\"ts\": \"2026-08-19T06:35:02.972Z\", … \"message\": \"GET /products/3 -> 500\", \"request_id\": \"57dc5e1322ce\", … \"status\": 500, \"duration_ms\": 4.903}\n{\"ts\": \"2026-08-19T06:35:06.095Z\", … \"message\": \"GET /products/3 -> 500\", \"request_id\": \"cbf392118a7c\", … \"status\": 500, \"duration_ms\": 4.962}\n{\"ts\": \"2026-08-19T06:35:08.217Z\", … \"message\": \"GET /products/3 -> 500\", \"request_id\": \"165dda376b87\", … \"status\": 500, \"duration_ms\": 5.023}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:34:56.726Z, 06:34:57.787Z, 06:35:05.030Z — same-route successes interleaved with the failure window"
    quote: "{\"ts\": \"2026-08-19T06:34:56.726Z\", … \"message\": \"GET /products/1 -> 200\", \"request_id\": \"74061635494e\", … \"status\": 200, \"duration_ms\": 1.017}\n{\"ts\": \"2026-08-19T06:34:57.787Z\", … \"message\": \"GET /products/2 -> 200\", \"request_id\": \"acb4fd185308\", … \"status\": 200, \"duration_ms\": 0.919}\n{\"ts\": \"2026-08-19T06:35:05.030Z\", … \"message\": \"GET /products/2 -> 200\", \"request_id\": \"41de7623cd3c\", … \"status\": 200, \"duration_ms\": 0.772}"
  - id: E5
    type: probe
    source: "GET /products — request id konan-1787121555-48148"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":118},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":39},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]\n-- HTTP 200 in 0.001347s request_id=konan-1787121555-48148"
  - id: E6
    type: probe
    source: "GET /products/3 — request id konan-1787121553-48142"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787121553-48142\"}\n-- HTTP 500 in 0.004552s request_id=konan-1787121553-48142"
  - id: E7
    type: probe
    source: "GET /products/4 — control: units_ordered is 0 but units_in_stock is non-zero"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0}\n-- HTTP 200"
  - id: E8
    type: metric
    source: "GET /metrics — baseline scrape, request id konan-1787121338-47934"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 4\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2\nhttp_exceptions_total{type=\"ZeroDivisionError\"} 4\nfaultline_chaos_enabled 0\nprocess_uptime_seconds 43.47255512489937\nprocess_max_rss_bytes 47906816"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:34:54.910Z — the only lifecycle marker in the file, and the file's first line"
    quote: "{\"ts\": \"2026-08-19T06:34:54.910Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E10
    type: metric
    source: "GET /metrics — later scrape, ~94s after the baseline scrape"
    quote: "process_max_rss_bytes 47939584\nprocess_uptime_seconds 137.23982787504792\nfaultline_chaos_enabled 0\nhttp_exceptions_total{type=\"ZeroDivisionError\"} 6"
  - id: E11
    type: probe
    source: "GET /openapi.json — request id konan-1787121448-48074"
    quote: "\"info\":{\"title\":\"faultline\",…\"version\":\"0.1.0\"} … GET /products/{product_id}: \"responses\":{\"200\":{\"description\":\"Successful Response\",…},\"422\":{\"description\":\"Validation Error\",…}}"
  - id: E12
    type: log
    source: "lab/logs/app.log — event tally over the whole file; lab/logs/ directory listing"
    quote: "1 \"event\": \"startup\"; 28 \"event\": \"request\"; 7 \"event\": \"unhandled_exception\"; 2 \"event\": \"order_created\". Zero occurrences of \"chaos_enabled\", \"chaos_disabled\", \"chaos_failure\", \"simulated_exception\". lab/logs/ contains only app.log — no .1-.3 rotated backups exist."
  - id: E13
    type: log
    source: "lab/logs/app.log — per-id outcome tally for GET /products/{id}"
    quote: "/products/1 -> 200 (x1); /products/2 -> 200 (x2); /products/3 -> 500 (x7, of which 4 carry unstamped user request ids and 3 are konan-* investigator probes); /products/4 -> 200 (x2); /products/5 -> 200 (x1); /products/999 -> 404 (x1)."
gaps:
  - "Onset is undetermined. Telemetry begins at process start 2026-08-19T06:34:54.910Z (E9) and lab/logs/ holds no rotated backups (E12), so there is no observation of /products/3 before that instant and every counter in E8/E10 is process-scoped. The reporter's 'started within the last hour' can be neither confirmed nor refuted; the honest statement is 'first observed at 06:35:01.899Z'. The mechanism is a static data condition, equally consistent with a defect that has failed this product for a long time and was only now reported."
  - "'No deploys that we know of' could not be checked. The investigator surface carries no deploy, release, or change history — only a version string observed once (0.1.0 in E9 and E11), which is a snapshot, not a history."
  - "The change history of product 3's units_in_stock value is not on the surface, so it is unknown whether stock recently reached 0 or has been 0 all along — this is the same question as the onset gap, from the data side."
  - "Whether other products will hit the same failure as their stock reaches 0 is not observable. Product 3 is the only row with units_in_stock 0 in the current catalog (E5); stock trajectories are not exposed."
  - "The route's authentication posture is unknown — all probes came from loopback — so the exposure of the leaked exception class name in the 500 envelope (E6) is unquantified."
  - "Path-templated metrics (E8) collapse the product id, so /metrics alone cannot localize the failure to product 3; only log correlation can. Anyone writing an alert for this needs the log dimension."
  - "faultline source was not read — the blinding contract keeps the investigator to telemetry. The code frame at shop.py line 64 is known only from the logged stack trace (E1), not from reading the file."
usage:
  model: claude-opus-5
  tokens: 2119852
  wall_clock_seconds: 447
---

# Product 3 detail page returns 500 — unguarded division by zero stock

## Summary

**Root cause identified.** `GET /products/{product_id}` computes a `turnover_score`
field by dividing `units_ordered` by `product["units_in_stock"]` with no guard against a
zero divisor (E1). Product 3, "Unobtainium Ingot", has `units_in_stock: 0` (E5), so every
request for that one page raises an unhandled `ZeroDivisionError` and returns HTTP 500
(E2, E3, E6). This is deterministic, not transient — 7 of 7 requests for id 3 failed,
while every other product id returned 200 (E13). That is exactly why refreshing does not
help, and why the reporter's other pages load fine.

Impact in the observed window is 4 failed user page loads, all on `/products/3` (E13);
the other three failures were this investigation's own probes and must not be counted as
customer impact. The catalog listing at `/products` still returns 200 and still lists
product 3 (E5), so customers can keep reaching the broken page. Any product whose stock
reaches 0 would fail identically; product 3 is the only such row today (E5).

Confidence is high. The mechanism is closed end to end: the raise site is named in the
stack, the zero divisor is visible in the catalog payload, a control product with a zero
*numerator* but non-zero stock returns 200 with `turnover_score: 0.0` (E7), and the
failure reproduces on demand.

One thing this investigation could **not** establish: when it started. See Gaps.

## Timeline

All timestamps UTC, as logged.

- **06:34:54.910Z** — faultline 0.1.0 starts; the only lifecycle marker in the log, and
  the first line of the file (E9). Telemetry has no visibility before this instant.
- **06:34:55–06:34:57Z** — user traffic succeeds on `/products`, `/products/1`,
  `/products/2` (E4).
- **06:35:01.899Z** — first `unhandled_exception`: `ZeroDivisionError` at
  `shop.py:64`, `"turnover_score": units_ordered / product["units_in_stock"]` (E1).
  This is the **first observed** failure, not a proven onset.
- **06:35:01.910Z** — the matching access line, `GET /products/3 -> 500` (E2).
- **06:35:02.972Z / 06:35:06.095Z / 06:35:08.217Z** — three further user 500s, all on
  `/products/3`, all with the identical stack (E3). Interleaved with them,
  `GET /products/2 -> 200` at 06:35:05.030Z (E4).
- **06:35:14Z** — complaint raised by support (`startsAt`); investigation starts
  06:35:33Z.
- **06:35:34Z onward** — investigator probes begin (`konan-*` request ids), confirming
  the failure still reproduces (E6).

**No configuration, deploy, or flag-change marker appears anywhere in the window**: zero
`chaos_enabled` / `chaos_disabled` / `chaos_failure` / `simulated_exception` events (E12),
`faultline_chaos_enabled 0` at both scrapes (E8, E10), and the running version 0.1.0 (E9)
matches `/openapi.json` (E11).

## Investigation

**Baseline** — `/health` returned 200 with a 39s uptime; `/metrics` showed 4× 500 against
`/products/{product_id}` and `http_exceptions_total{type="ZeroDivisionError"} 4` with
chaos disabled (E8); the 25-line log tail already contained the full stack trace (E1).
The baseline itself falsified the healthy-monitoring trap in the useful direction: health
was green while the business surface was failing.

**Triage** — three lenses in parallel, each blind to the others: software-defect,
infra-process, interfaces. All three converged on the same mechanism and, importantly,
two of them ruled *their own* domain out with evidence rather than claiming it. The
interfaces lens also caught a trap worth recording: the aggregate error rate on
`/products/{product_id}` reads ~57%, which resembles injected or partial degradation
until you disaggregate by path parameter, at which point it resolves into one always-broken
id among several always-healthy ones (E13).

**Deep-dive — deliberately skipped.** H1's triage evidence was already deterministic and
complete: raise site, zero divisor, reproduction, and a discriminating control (E7). Per
the loop's rule, a hypothesis that is already settled goes straight to the judge rather
than paying for re-proof. Budget spent: one triage round, zero deep-dive agents, one judge.

**Judge** — validated H1; invalidated H2 and H3; validated both latent findings after
striking an unsupported "unauthenticated" modifier from the leak claim. It also refuted a
claim the narrative was drifting toward — that telemetry confirms the reported onset — and
corrected H3's incident class from `interfaces` to a change-management/infra class. Both
corrections are carried into the record above.

## Hypotheses

### H1 — unguarded division by zero stock in the product-detail handler — **validated**

The stack in E1 names the raise site and the exact expression; E5 independently shows
product 3 carries `units_in_stock: 0`; E2 and E3 tie all four user-facing 500s to that
stack; E6 reproduces it on demand. E7 is the discriminating control — product 4 has
`units_ordered: 0` with non-zero stock and returns 200 with `turnover_score: 0.0`, which
kills the rival reading that a zero *numerator*, or product 4's `null` price, is the
trigger. It isolates the divisor. E13 gives the clean partition: 7/7 failures on id 3,
0/6 on every other id.

Nothing was offered against it. The one caveat carried forward is arithmetic, not causal:
"every request" generalizes from 7 trials, which is acceptable only because the mechanism
is deterministic over stored data and chaos injection is independently excluded (E8, E10).

### H2 — infrastructure or process fault — **invalidated**

Every limb fails against evidence. Crash/restart loop: E9 is the sole lifecycle marker
and the file's first line, E12 confirms exactly one `startup` event with no rotated
backups that could hide a second, and `process_uptime_seconds` climbs monotonically
43.47 → 137.24 across E8 and E10 — a restart between those scrapes is arithmetically
excluded. Saturation: E4 shows same-route requests completing in 0.77–1.02 ms interleaved
in time with the failures, and RSS is flat at ~47.9 MB (E8, E10). The decisive argument is
shape, not magnitude: a resource fault is indifferent to the request path, but E13 shows
failure correlated perfectly with one product id and never with any other. Saturation
cannot select for `id=3`.

### H3 — introduced by a configuration change, flag flip, chaos injection, or deploy — **invalidated**

The chaos and flag limbs are refuted directly: `faultline_chaos_enabled 0` at both scrapes
(E8, E10) and zero chaos or simulation events across the whole log (E12). The deploy limb
is weaker as evidence — a version string observed once (E9, E11) is a snapshot, not a
change history, and the process did start 7 seconds before the first failure, which is
trivially true of any short process lifetime. It is invalidated rather than inconclusive
because H1 supplies a complete deterministic mechanism grounded in stored data: even if a
deploy had shipped that line, it would explain *when* the defect entered, never *why*
requests fail. The incident class is software-defect either way.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

- Confirm the blast radius by reading `/products` for any other row with
  `units_in_stock: 0` — today product 3 is the only one (E5), and that set will change as
  stock moves.
- If an upstream gateway, CDN, or external APM keeps access logs, read them for
  `/products/3` outcomes before 06:34:54.910Z. That is the one artifact that would date
  the onset and settle the reporter's "within the last hour".
- Check the change history for product 3's `units_in_stock` value, wherever that data is
  edited — the same onset question from the data side.
- When writing an alert for this shape, key it on the log dimension, not `/metrics`: the
  path template collapses the product id (E8), so metrics alone cannot localize it.

## Gaps

- **Onset is undetermined**, and this is the most important limit on the report. The log
  begins at process start (E9) with no rotated backups (E12), so there is simply no
  observation of `/products/3` before 06:34:54.910Z, and every counter in E8/E10 resets at
  start. The absence of earlier failures is explained entirely by the absence of earlier
  data. Because the cause is a static data condition, the telemetry is equally consistent
  with a defect that has failed this page for a long time and was only now noticed and
  reported. "First observed at 06:35:01.899Z" is the defensible statement.
- **"No deploys that we know of" could not be verified.** No deploy, release, or change
  record is on the investigator surface; only a single version observation (0.1.0).
- **Stock history is not visible**, so whether product 3 recently fell to 0 or has been
  there all along is unknown — the onset gap from the data side.
- **Future blast radius is not observable**: any product reaching 0 stock would fail the
  same way, but stock trajectories are not exposed.
- **Auth posture of the route is unknown** — all probes came from loopback — so the
  exposure of the leaked exception class name (E6) is unquantified. That is why the
  latent finding claims disclosure but not reachability.
- **Metrics cannot localize the failure** to a product id because the path is templated
  (E8); log correlation was required.
- **faultline source was not read.** The blinding contract keeps this investigation to
  telemetry, so the code frame at `shop.py:64` is known only from the logged stack trace
  (E1), never from the file.
