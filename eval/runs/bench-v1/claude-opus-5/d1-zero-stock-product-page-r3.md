---
konan_journal: 1
investigation:
  id: 2026-08-19-products-3-zero-stock-500s
  trigger: "manual — /konan human profile (docs/triggers.md); source human, fingerprint human-1787121845, alertname human-report, no severity stated; startsAt 2026-08-19T06:44:05Z, investigation started 2026-08-19T06:44:11Z (trigger latency 6s)"
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-08-19T06:44:11Z
  concluded: 2026-08-19T06:48:25Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{product_id} computes turnover_score as units_ordered / product[\"units_in_stock\"] at shop.py:64 with no effective zero guard, so the one catalog row whose units_in_stock is 0 (id 3) raises an unhandled ZeroDivisionError and returns 500 on every request, while every other id on the same route succeeds."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "Unguarded division in get_product (shop.py:64): turnover_score = units_ordered / product[\"units_in_stock\"]. Product id 3 is the only row in the returned catalog with units_in_stock == 0, so requests for that single product raise an unhandled ZeroDivisionError and return 500; the route itself is healthy for all other ids. Data-dependent, per-input defect."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8]
    evidence_against: []
  - id: H2
    statement: "The 500s are caused by a process lifecycle or resource event — crash, restart, memory exhaustion, or worker starvation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E10, E2, E3]
  - id: H3
    statement: "The 500s are caused by injected chaos, a runtime configuration or flag change, or a partial rollout."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E8, E4, E5]
latent_findings:
  - statement: "The 500 error envelope returns the internal exception class name to the client (\"exception_type\":\"ZeroDivisionError\"), disclosing implementation detail in an error response. Real, but not the cause of the reported incident."
    evidence: [E5]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:43:54.311Z"
    quote: |-
      {"ts": "2026-08-19T06:43:54.311Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "d7ee97056a17", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last): [intermediate framework frames trimmed] File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:43:54.322Z"
    quote: |-
      {"ts": "2026-08-19T06:43:54.322Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "d7ee97056a17", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 11.572, "client": "127.0.0.1:57483"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:43:55.387Z, 06:43:58.509Z, 06:44:00.635Z"
    quote: |-
      "message": "GET /products/3 -> 500", "request_id": "bdcc4982a2d6", "status": 500, "duration_ms": 4.679
      "message": "GET /products/3 -> 500", "request_id": "90275e4914b7", "status": 500, "duration_ms": 4.932
      "message": "GET /products/3 -> 500", "request_id": "72ca3f2891db", "status": 500, "duration_ms": 7.357
  - id: E4
    type: probe
    source: "GET /products, request_id konan-1787121997-48536, HTTP 200"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E5
    type: probe
    source: "GET /products/3, request_id konan-1787121910-48389, HTTP 500 (repeated identically as konan-1787121916-48405, konan-1787121945-48487, konan-1787121947-48493)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787121910-48389"}
  - id: E6
    type: probe
    source: "GET /products/1, /products/4, /products/5 — all HTTP 200"
    quote: |-
      "units_in_stock":118,"turnover_score":0.016949...
      "units_in_stock":75,"turnover_score":0.0
      "units_in_stock":500,"turnover_score":0.0
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:43:57.447Z"
    quote: |-
      {"ts": "2026-08-19T06:43:57.447Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "6c376b88e9d2", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.773, "client": "127.0.0.1:57485"}
  - id: E8
    type: metric
    source: "GET /metrics, request_id konan-1787121864-48371 (baseline)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
      faultline_chaos_enabled 0
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:43:47.296Z — the only startup marker in the log; no restart line follows"
    quote: |-
      {"ts": "2026-08-19T06:43:47.296Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E10
    type: metric
    source: "GET /metrics, baseline konan-1787121864-48371 vs re-probe ~55s later"
    quote: |-
      process_uptime_seconds 37.19629979110323 -> 91.93330616597086 (monotonic, no reset)
      process_max_rss_bytes 47710208 -> 47857664 (+0.31%)
  - id: E11
    type: log
    source: "lab/logs/app.log (whole file) and GET /metrics at process_uptime_seconds 122.24171770806424"
    quote: |-
      zero chaos_enabled / chaos_disabled / chaos_failure / simulated_exception events in the log; faultline_chaos_enabled 0
  - id: E12
    type: log
    source: "lab/logs/ directory listing and lab/logs/app.log first line"
    quote: |-
      lab/logs/ contains only app.log (no .1-.3 rotated backups); first line is the 2026-08-19T06:43:47.295Z process start. Every 500 after 06:44:00.635Z carries an investigator-stamped konan-* request_id; no non-investigator request of any kind is logged after 06:44:00.635Z.
gaps:
  - "Onset cannot be dated. There is no telemetry from before the current process start at 06:43:47.295Z and no rotated log backups (E12), so the reported 'started within the last hour' is uncorroborated. The four user-facing 500s sit in the first ~13 seconds of the only log that exists — a boundary artifact of when logging began, not an observed start."
  - "Current blast radius is unknown in both directions. No non-investigator request of any kind is logged after 06:44:00.635Z (E12), so the telemetry neither shows ongoing user impact nor shows the incident stopping. Every 500 counted after that point is the investigator's own probe."
  - "shop.py:64 was not read — the service source is outside the investigator's surface contract (docs/lab.md). 'No effective zero guard' is inferred from the traceback and the observed behavior; a guard that exists but is wrong would produce identical evidence."
  - "The catalog is only what GET /products returned (E4). Pagination or a larger backing catalog was not excluded, so 'the only zero-stock row' is scoped to the returned list. Any further row with units_in_stock == 0 would be a further 500."
  - "The chaos exclusion rests on two point samples of faultline_chaos_enabled plus the absence of chaos events (E8, E11); that the chaos subsystem logs every toggle is assumed from the contract, not demonstrated. The verdict rests on the data-dependent mechanism, not on the flag."
  - "No out-of-process record of service restarts before 06:43:47Z (supervisor history, OS process start time) is available on this surface, so 'no restart' holds only within the observed window."
  - "When product 3's units_in_stock became 0 is unknown — no inventory change history or row-version timestamp is exposed on the investigator's surface."
usage:
  model: claude-opus-5
  tokens: 1951943
  wall_clock_seconds: 254
---

# /products/3 returns 500 — unguarded divide-by-zero on a zero-stock product

## Summary

**Root cause identified.** `GET /products/{product_id}` computes a `turnover_score` by
dividing `units_ordered` by `product["units_in_stock"]` at `shop.py:64` with no effective
zero guard (E1). Product id 3, `Unobtainium Ingot`, is the only row in the returned catalog
whose `units_in_stock` is `0` (E4), so a request for that one product raises an unhandled
`ZeroDivisionError` and returns HTTP 500, deterministically, on every attempt (E5). Every
other id on the same route returns 200 with a computed `turnover_score` (E6), and a
`/products/2` success sits interleaved between two `/products/3` failures (E7) — the route
is healthy; one input is not. This matches the complaint exactly: one product page fails,
refreshing does not help, other pages are fine.

Confirmed user impact is four failed requests on `/products/3` between 06:43:54.322Z and
06:44:00.635Z (E2, E3), matching the baseline counters (E8) with no hidden failures. Beyond
that the telemetry is silent: no non-investigator request of any kind is logged after
06:44:00.635Z (E12), so the journal does not claim the incident is either ongoing or over.
Confidence in the mechanism is high — the failure was reproduced four times on demand and
the traceback names the throwing expression. Confidence in onset and current rate is low,
and deliberately so; see Gaps.

Note for whoever picks this up: the reporter's "no deploys that we know of" is consistent
with the evidence. This is not a code-change incident in the observed window — it is a
latent defect that fires whenever a catalog row reaches zero stock. Nothing had to be
deployed for it to start.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 06:43:47.295Z | Server process 48243 starts; `faultline 0.1.0 started`. The only startup marker in the log; no restart follows. No telemetry exists before this point. | E9, E12 |
| 06:43:48.047Z–06:43:52.253Z | Normal traffic: `/health` 200, `/products` 200, `/products/1` 200, `/products/2` 200, `POST /orders` 201. | E8 |
| 06:43:54.311Z | First `unhandled_exception`, `ZeroDivisionError` at `shop.py:64`, request d7ee97056a17. | E1 |
| 06:43:54.322Z | `GET /products/3 -> 500`, 11.572 ms — first user-facing failure. | E2 |
| 06:43:55.387Z | `GET /products/3 -> 500`, request bdcc4982a2d6. | E3 |
| 06:43:57.447Z | `GET /products/2 -> 200` — same route succeeds between two failures. | E7 |
| 06:43:58.509Z | `GET /products/3 -> 500`, request 90275e4914b7. | E3 |
| 06:44:00.635Z | `GET /products/3 -> 500`, request 72ca3f2891db — last non-investigator request of any kind in the log. | E3, E12 |
| 06:44:23Z–06:44:24Z | Investigation baseline: `/health` 200, `/metrics` scraped. | E8 |
| 06:45:10Z onward | Investigator probes reproduce the 500 on `/products/3` four times; `/products/1`, `/products/4`, `/products/5` return 200. | E5, E6 |

No configuration, deploy, or flag-change marker appears anywhere in the log — no
`chaos_enabled`, `chaos_disabled`, `chaos_failure`, or `simulated_exception` events (E11).

## Investigation

**Baseline.** `/health` returned 200 with `uptime_seconds` ~36 and `faultline_chaos_enabled`
read 0, but the business surface was already dirty:
`http_requests_total{GET,/products/{product_id},status="500"} 4` and
`http_exceptions_total{type="ZeroDivisionError"} 4` (E8). Green health over a failing
business path is the healthy-monitoring trap, so the counters — not the health endpoint —
set the direction.

**Triage.** All three lenses were spawned in parallel, each blind to the others, because the
baseline excluded no domain by evidence. The software-defect lens returned the mechanism and
reproduced it. The infra-process and interfaces lenses both returned negatives, and both
independently flagged the same scope limit: the telemetry horizon is younger than the
reported incident.

**Deep-dive: none.** H1's triage evidence was already deterministic and complete — the
traceback names the file, line, and expression; the catalog shows the zero divisor; the
failure reproduces on demand and the controls pass. Per the loop's rule, a hypothesis with
complete evidence skips deep-dive rather than re-proving itself, so the round went straight
to the judge. One `GET /products` probe was re-run first-hand so the crux fact did not rest
on a subagent's report.

**Judge.** The judge validated H1 and invalidated H2 and H3, and separately refuted the
claim that onset can be dated from telemetry. It also flagged three over-reads in the
original H1 wording, all of which are corrected in this journal: "no zero guard" is narrowed
to "no *effective* zero guard" (the source was never read); "the only catalog row" is
narrowed to "the only row in the returned catalog" (pagination not excluded); and "every
request for that product" is supported by the mechanism rather than by the eight-request
sample alone.

## Hypotheses

### H1 — unguarded division on zero stock — **validated**

`get_product` divides by `product["units_in_stock"]` (E1) and id 3 is the only returned row
where that value is `0` (E4). For: the traceback names the exact expression (E1); four
non-investigator 500s all on `/products/3` (E2, E3); four investigator reproductions (E5);
three controls on the same route returning 200 with a computed score (E6); an interleaved
same-route success (E7); counters agreeing with the log so no failures are hidden (E8).
Against: nothing. The evidence is a closed chain from input value to throwing expression to
status code.

### H2 — process lifecycle or resource event — **invalidated**

Against: one startup marker with no restart after it (E9); `process_uptime_seconds` rising
monotonically with no counter reset and RSS flat at +0.31% (E10); and the failures completing
in 4.7–11.6 ms with a stack trace (E2, E3) — fast in-process throws, not timeouts or
starvation. Scope caution, per the judge: E12 means this holds for the observed window only,
not for all time. It does not rescue H2, since the observed 500s have a proven non-infra cause.

### H3 — chaos, config change, or partial rollout — **invalidated**

Against: `faultline_chaos_enabled` read 0 at two separate times and zero chaos or
simulated-exception events in the log (E8, E11). Stronger than the flag: injected chaos or a
partial rollout fails by time or by probability, not by product id, and would not raise
`ZeroDivisionError` on that specific arithmetic line. The failure is partitioned by input
(E4, E5, E6), which no rollout mechanism explains.

### Onset — tested and refuted as a telemetry claim

The reported "started within the last hour" could be neither confirmed nor refuted. There is
no telemetry before the process start and no rotated backups (E12, E9). The defect is
data-dependent and would have fired for as long as that row has held zero stock, which may
predate the current process by any amount. Recorded under Gaps rather than as a cause
hypothesis, since it is a scope claim, not a mechanism.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

1. Re-probe `GET /products/3` to confirm the failure still reproduces at the time of reading.
2. Track `http_exceptions_total{type="ZeroDivisionError"}` and
   `http_requests_total{GET,/products/{product_id},status="500"}`, counting only
   non-`konan-*` request ids, to measure real user impact rather than investigator traffic.
3. Read `shop.py:64` in the service repository to confirm directly whether a guard is absent
   or present-but-wrong — the one gap the investigator's surface could not close.
4. Enumerate the full catalog, including any pages beyond the first response, for other rows
   with `units_in_stock == 0`. Each one is a further 500 waiting on the same code path.
5. Check the inventory change history for product 3 to date when its stock reached 0 — that
   timestamp, not the log, is the incident's real onset.
6. Review the 500 error envelope, which returns `exception_type` to the client (E5).
7. Check `"price":null` on product id 4 (E4). It returned 200 and is not implicated here, but
   it is an unvalidated null in the same catalog contract.

## Gaps

1. **Onset is undatable.** No telemetry before 06:43:47.295Z, no rotated backups (E12). The
   four user 500s falling in the log's first ~13 seconds is an artifact of when logging began,
   not evidence of when the incident started. The reporter's "last hour" stands uncorroborated.
2. **Current impact is unknown in both directions.** No non-investigator request appears after
   06:44:00.635Z (E12) — the silence is equally consistent with users still failing and with
   traffic having stopped. No rate or blast-radius claim is made.
3. **Source not read.** `shop.py:64` is outside the surface contract; "no effective zero guard"
   is inferred from traceback plus behavior. A wrong guard would look identical.
4. **Catalog completeness unverified.** Pagination was not excluded (E4), so the zero-stock
   row may not be the only one.
5. **Chaos-toggle logging assumed.** Two point samples of the flag plus absent chaos events
   (E8, E11) exclude injection only if every toggle emits an event — asserted by the contract,
   not demonstrated. The H3 verdict rests on the mechanism instead.
6. **Restart history bounded by the log.** No supervisor or OS-level process history was
   available, so "no restart" holds only within the observed window.
7. **No inventory audit trail** on the investigator's surface to date the stock value's change.
