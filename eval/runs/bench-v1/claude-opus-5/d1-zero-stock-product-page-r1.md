---
konan_journal: 1
investigation:
  id: 2026-08-19-products-3-zero-stock-500s
  trigger: "manual — /konan human report; complaint object: source=human, fingerprint=human-1787120808, labels.alertname=human-report (no severity stated), startsAt=2026-08-19T06:26:48Z; investigation started 2026-08-19T06:26:48Z (trigger latency 0s)"
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-08-19T06:26:48Z
  concluded: 2026-08-19T06:32:15Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The product detail endpoint computes turnover_score as units_ordered / units_in_stock with no zero guard, so product id 3 — the only catalog row whose units_in_stock is 0 — raises an unhandled ZeroDivisionError and returns HTTP 500 on every request."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "GET /products/{id} divides units_ordered by units_in_stock to derive turnover_score without guarding zero; product 3 has units_in_stock 0, so the division raises ZeroDivisionError, which escapes unhandled and returns 500 for that one product id while every other id succeeds."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15]
    evidence_against: []
  - id: H2
    statement: "The 500s are injected by the operator chaos/fault-injection surface rather than caused by a code defect."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E6]
  - id: H3
    statement: "The 500s come from an infrastructure or process fault — a crash, a restart loop, memory saturation, or timeout/worker starvation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E4, E5, E7, E8]
  - id: H4
    statement: "The product route is degrading probabilistically across the catalog (a general availability problem), and product 3 is only the most-observed victim."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E9, E12, E13, E14, E15]
evidence:
  - id: E1
    type: probe
    source: "GET /health — request_id konan-1787120830-47499"
    quote: |
      {"status":"ok","uptime_seconds":40.62600462487899}
      -- HTTP 200 in 0.002505s request_id=konan-1787120830-47499
  - id: E2
    type: metric
    source: "GET /metrics — request_id konan-1787120833-47505 (baseline scrape, before any investigator probe of /products/*)"
    quote: |
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E3
    type: metric
    source: "GET /metrics — request_id konan-1787120833-47505"
    quote: 'faultline_chaos_enabled 0'
  - id: E4
    type: metric
    source: "GET /metrics — request_id konan-1787120833-47505"
    quote: |
      process_uptime_seconds 43.611486749956384
      process_max_rss_bytes 47923200
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:26:29.943Z"
    quote: '{"ts": "2026-08-19T06:26:29.943Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:26:36.928Z (stack trimmed to the throwing frame)"
    quote: '{"ts": "2026-08-19T06:26:36.928Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "68c30ba29ae0", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "… File \"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:26:36.939Z"
    quote: '{"ts": "2026-08-19T06:26:36.939Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "68c30ba29ae0", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 11.341, "client": "127.0.0.1:57278"}'
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:26:38.001Z, 06:26:41.120Z, 06:26:43.241Z (fields trimmed to method/path/status/duration)"
    quote: |
      {"ts": "2026-08-19T06:26:38.001Z", "message": "GET /products/3 -> 500", "request_id": "6787c63d0f70", "path": "/products/3", "status": 500, "duration_ms": 4.686}
      {"ts": "2026-08-19T06:26:41.120Z", "message": "GET /products/3 -> 500", "request_id": "10c572ac21c6", "path": "/products/3", "status": 500, "duration_ms": 4.665}
      {"ts": "2026-08-19T06:26:43.241Z", "message": "GET /products/3 -> 500", "request_id": "c4d80e0a25ad", "path": "/products/3", "status": 500, "duration_ms": 4.862}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-19T06:26:31.758Z, 06:26:32.816Z, 06:26:40.058Z (fields trimmed to method/path/status/duration)"
    quote: |
      {"ts": "2026-08-19T06:26:31.758Z", "message": "GET /products/1 -> 200", "request_id": "2992f42af113", "path": "/products/1", "status": 200, "duration_ms": 1.037}
      {"ts": "2026-08-19T06:26:32.816Z", "message": "GET /products/2 -> 200", "request_id": "59eb8a842c85", "path": "/products/2", "status": 200, "duration_ms": 0.977}
      {"ts": "2026-08-19T06:26:40.058Z", "message": "GET /products/2 -> 200", "request_id": "090a97259468", "path": "/products/2", "status": 200, "duration_ms": 0.759}
  - id: E10
    type: probe
    source: "GET /products — request_id konan-1787121001-47687"
    quote: |
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001456s request_id=konan-1787121001-47687
  - id: E11
    type: probe
    source: "GET /products/3 — request_id konan-1787121003-47693"
    quote: |
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787121003-47693"}
      -- HTTP 500 in 0.003445s request_id=konan-1787121003-47693
  - id: E12
    type: probe
    source: "GET /products/1 — request_id konan-1787121005-47700"
    quote: |
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":118,"units_ordered":2,"turnover_score":0.01694915254237288}
      -- HTTP 200 in 0.001683s request_id=konan-1787121005-47700
  - id: E13
    type: probe
    source: "GET /products/5 — request_id konan-1787121125-47734"
    quote: |
      {"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001554s request_id=konan-1787121125-47734
  - id: E14
    type: probe
    source: "GET /products/4 — request_id konan-1787120920-47636"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0} — HTTP 200'
  - id: E15
    type: probe
    source: "GET /products/3, two consecutive attempts — request_id konan-1787120909-47593 and konan-1787120911-47599"
    quote: |
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787120909-47593"} — HTTP 500
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787120911-47599"} — HTTP 500
gaps:
  - "Onset is unverifiable from the permitted surface. lab/logs/ holds only app.log with no rotated .1–.3 backups, and the file begins at the single startup marker 2026-08-19T06:26:29.943Z (E5) — about two minutes of history against a complaint window of one hour. Telemetry can neither confirm nor refute 'started within the last hour'; the defect may equally have been latent for a long time and only newly exercised."
  - "The provenance and age of the triggering data condition (product 3 reaching units_in_stock 0, E10) are outside the readable surface — there is no inventory audit trail, order history for that id, or last-known-good sample in evidence."
  - "The 'no zero guard' mechanism is read from the traceback's rendered source line (E6), not from the source file, which is outside the investigator's surface. A guard that exists but is ineffective would produce identical evidence."
  - "The complaint's 'no deploys that we know of' could not be checked independently: no deploy, config-change, or flag-change marker of any kind appears in the visible log window, but that window post-dates process start, so absence here is not evidence of absence before it."
  - "Catalog coverage is the five ids returned by /products (E10). If ids exist outside that listing, they were not swept."
  - "scripts/lab.sh status was not pre-approved in this session, so process supervision and restart history before 06:26:29.943Z were not inspected; the single startup marker (E5) is the only lifecycle evidence."
usage:
  model: claude-opus-5
  tokens: 1833560
  wall_clock_seconds: 327
---

# Product detail 500s on a zero-stock catalog row

## Summary

**Root cause identified.** `GET /products/{id}` returns an item payload with two derived
fields that the collection view omits — `units_ordered` and `turnover_score` — and
`turnover_score` is computed as `units_ordered / product["units_in_stock"]` with no zero
guard (E6, E12). Product id 3 ("Unobtainium Ingot") is the one catalog row whose
`units_in_stock` is `0` (E10), so that division raises `ZeroDivisionError`, the exception
escapes unhandled, and the request returns HTTP 500 (E6, E7). The failure is
deterministic per input, not probabilistic: `/products/3` failed on 4/4 real user
requests (E7, E8) and 3/3 investigator probes (E11, E15), while every other catalog id —
1, 2, 4, 5 — returned 200 in the same window (E9, E12, E13, E14).

This matches the complaint exactly, including the two details that usually mislead: "still
happening when they refresh" is the determinism, and "other pages load fine" is the
single-id blast radius. The catalog listing `/products` itself returns 200 and includes
the poisoned row (E10) — only the item view computes the ratio, so browsing works and
one product page is dead.

Impact is one product page, hard-down, for every user who opens it. Confidence is high:
the mechanism is in a stack trace, the trigger value is in a probe body, and the throwing
request id `68c30ba29ae0` (E6, E7) is unstamped — real user traffic, not investigator
traffic, so this is an active incident and not a latent finding.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 06:26:29.943 | Process start — `faultline 0.1.0 started`. The only lifecycle marker in the log; no deploy, config-change, or flag-change marker appears anywhere in the visible window. | E5 |
| 06:26:31.758 | User request `GET /products/1` → 200. | E9 |
| 06:26:32.816 | User request `GET /products/2` → 200. | E9 |
| 06:26:36.928 | First recorded failure: unhandled `ZeroDivisionError` at `shop.py:64`, `units_ordered / product["units_in_stock"]`, request id `68c30ba29ae0`. | E6 |
| 06:26:36.939 | Same request id returns `GET /products/3 -> 500`. | E7 |
| 06:26:38.001 – 06:26:43.241 | Three more user 500s, all `/products/3`, all unstamped ids. `/products/2` returns 200 at 06:26:40.058, straddling them. | E8, E9 |
| 06:26:48 | Complaint raised (`startsAt`); investigation starts the same second. | — |
| 06:27:10 – 06:27:13 | Baseline: `/health` 200, uptime 40.6 s; metrics show 4× 500 on the item route and `http_exceptions_total{type="ZeroDivisionError"} 4` — a 1:1 match, so nothing else contributes 500s. `faultline_chaos_enabled 0`. | E1, E2, E3, E4 |
| 06:28:29 – 06:28:40 | Reproduction: `/products/3` fails twice consecutively; `/products/2` and `/products/4` succeed. | E15, E14 |
| 06:30:01 – 06:32:05 | Confirmation sweep: `/products` shows id 3 at `units_in_stock: 0`; `/products/3` 500; `/products/1` and `/products/5` 200 with `turnover_score` present. | E10, E11, E12, E13 |

The absence of any change marker before the failures is itself notable: nothing in
telemetry supports a deploy or flag flip as the trigger, which is consistent with the
reporter's "no deploys that we know of" — though see Gaps, since the visible window
post-dates process start.

## Investigation

**Baseline.** `/health` green, uptime 40.6 s, RSS 46 MB, chaos gauge 0 (E1, E3, E4).
The healthy-monitoring trap applies squarely here: `/health` was 200 throughout and
carries no `status="500"` series at all (E2), so liveness monitoring would never have
paged on this. The business surface told the whole story — the item route already
showed 4× 500 against 3× 200 at baseline, with an exception counter matching the 500
count exactly (E2).

**Triage — three lenses in parallel,** each blind to the others: software-defect,
infra-process, interfaces. All three converged on the same shape and, usefully,
disagreed with nothing. software-defect isolated the throwing frame and the per-input
determinism. infra-process returned a clean negative in its own domain — one startup
marker, monotonic uptime, flat RSS, millisecond fast-fail durations rather than
timeouts — and handed the failure out of its domain rather than manufacturing a finding.
interfaces found no config/flag/deploy marker and no gateway-shaped errors, and
contributed the decisive asymmetry: the collection view serves the same record fine, so
the divergence lives in the item-view-only computed fields.

No lens was skipped for the classes this lab can exercise; `data-db` and `third-party`
have no lens file in this repo and no separate surface to probe here — the data
condition was reached through the product surface itself (E10). That limitation is
recorded in Gaps rather than assumed away.

**Deep-dive: none spawned.** Per the loop's own rule, a hypothesis whose triage evidence
is already deterministic and complete skips the deep-dive and goes to the judge. H1 had
mechanism (stack frame), trigger value (`units_in_stock: 0`), and repeat determinism
before deep-dive would have started; spending agents to re-prove it would have been
ceremony. Instead the orchestrator verified the decisive evidence first-hand (E10, E11,
E12) rather than accept it second-hand from a lens.

**Judge.** Ran adversarial on the hypothesis list and evidence quotes alone, with no
narrative. It validated H1 and killed H2–H4. It also caught a real discrepancy and
resolved it correctly: the baseline scrape reads 4 `ZeroDivisionError`s while the log
census counts 6 — the difference is exactly the two investigator probes made after that
scrape (4 user + 2 konan = 6), so the counters are consistent, not contradictory. Two
residuals it raised were closed afterward: id 5 was never probed (now E13, 200), and a
full-catalog sweep was missing (now complete — ids 1, 2, 4, 5 all 200, id 3 100% fail).

**On the complaint's onset claim.** A fifth proposition — that telemetry could establish
the failure began within the last hour — was tested and failed. It is not a cause
statement, so it is recorded as a gap rather than as a hypothesis, but it is worth
stating plainly: the report's "started within the last hour" is unconfirmed in either
direction, and nothing in this journal depends on it.

## Hypotheses

### H1 — Unguarded division by `units_in_stock` in the item view — **validated**

*Statement:* `GET /products/{id}` derives `turnover_score` as
`units_ordered / units_in_stock` with no zero guard; product 3 has `units_in_stock` 0, so
the division raises `ZeroDivisionError`, escapes unhandled, and returns 500 for that id
alone.

*For:* The mechanism is quoted directly from the traceback (E6), naming the file, line,
and expression. The causal link is not mere co-occurrence — E6 and E7 share request id
`68c30ba29ae0`, so the request that raised is the request that returned 500. The trigger
value is in a probe body: id 3 is the only catalog row at `units_in_stock: 0` (E10). The
derived field is confirmed present and computed on the success path (E12: id 1 →
`turnover_score` 0.0169; E13, E14: ids 5 and 4 → 0.0). Scope is input-bound: all seven
observed 500s are `/products/3` (E7, E8, E11, E15) and all other ids return 200 (E9,
E12, E13, E14). The exception counter equals the 500 count 1:1 at baseline (E2), so no
second failure mode hides underneath.

*Against:* Nothing. The one weakness worth naming is not counter-evidence but a scope
limit: "no zero guard" is read from the traceback's rendered source line, since the
source file is outside the surface (see Gaps).

*Blast radius note:* an optional derived field takes down the entire product resource
rather than degrading that one field — the exception propagates with no
application-level handler (E6). That is why the page is hard-down rather than showing a
missing score.

### H2 — Injected chaos / fault injection — **invalidated**

`faultline_chaos_enabled 0` at baseline (E3), and no `chaos_enabled`, `chaos_disabled`,
`chaos_failure`, or `simulated_exception` event appears anywhere in the log. The gauge
alone would be weak — a point-in-time read could postdate a disable — but the absence of
any `chaos_disabled` event in a file that begins at process start (E5) closes that
escape. Independently, E6 is a real application stack frame in `shop.py`, not a synthetic
raise.

### H3 — Infrastructure or process fault (crash, restart loop, saturation, starvation) — **invalidated**

One startup marker in the whole file (E5), no shutdown or second start. Uptime advances
monotonically across scrapes — 40.6 s at 06:27:10 (E1), 43.6 s at 06:27:13 (E4) —
so no restart hid between them. Peak RSS 46 MB, flat (E4). The failing requests are
fast-fail at 4.6–11.3 ms (E7, E8) and return a typed application exception, not a
gateway timeout or a starved worker. This excludes infra fault only for the process's
observed lifetime, which is also a Gap — but it is moot for causation, since H1 supplies
a complete in-process cause.

### H4 — Probabilistic degradation of the product route — **invalidated**

The route-level failure rate of roughly 55% at baseline (4 × 500 vs 3 × 200, E2) is an
artifact of traffic mixing ids, not a failure probability. Split by input it is a clean
partition: 100% fail for id 3, 0% for ids 1, 2, 4, 5. Two consecutive `/products/3`
probes both failed (E15) where a probabilistic fault would sometimes pass, and id 2
returned 200 at 06:26:40 (E9) — between 500s at 06:26:38 and 06:26:41 (E8) — so
successes and failures interleave in time while staying perfectly separated by input.
This is the data-dependent defect shape, not a saturation curve.

## Safe next steps

Read-only only; remediation is out of scope and deliberately absent.

- Confirm the guard question at the source: inspect `src/faultline/shop.py` around line 64
  in the target's own repository to see whether a zero guard is absent or present but
  ineffective. That closes the one inferential step in H1.
- Establish the age of the data condition: check inventory history for product 3 to learn
  when `units_in_stock` reached 0. That, not the log, is what can confirm or refute the
  reporter's "within the last hour" — and it distinguishes a new defect from an old one
  newly exercised.
- Sweep the rest of the catalog for the same trigger shape: any other row at
  `units_in_stock: 0` is a product page that is already dead or one restock away from it.
  `/products` (E10) exposes the field for every id.
- For detection, note that no existing signal would have caught this. `/health` stayed
  200 throughout (E1, E2). A rule on `http_exceptions_total` or on per-path
  `http_requests_total{status="500"}` would have paged at the first failure; a rule on
  process liveness never will.
- Extend log retention. The current window (E5, and no rotated backups) is shorter than
  the complaint window, which is why onset is unanswerable here and would be unanswerable
  for the next incident too.

## Gaps

1. **Onset is unverifiable.** `lab/logs/` holds only `app.log`, with no `.1`–`.3`
   rotated backups, and the file begins at the single startup marker at 06:26:29.943Z
   (E5) — roughly two minutes of history against a one-hour complaint window. The first
   `/products/3` request on record already fails (E6, E7); there is no last-known-good
   sample for that id anywhere in evidence. Telemetry can neither confirm nor refute
   "started within the last hour."
2. **The data condition's provenance is unreadable.** How and when product 3 reached
   `units_in_stock: 0` (E10) is outside the surface — no inventory audit trail, no order
   history for that id.
3. **The source file was not read.** "No zero guard" comes from the traceback's rendered
   source line (E6); `src/faultline/` is outside the investigator's surface. A guard that
   exists but is wrong would produce identical evidence.
4. **"No deploys that we know of" was not independently checked.** No deploy, config, or
   flag-change marker appears in the visible window — but that window post-dates process
   start, so this is a limit of the horizon, not a confirmation.
5. **Catalog coverage is the five ids `/products` returns** (E10). Ids outside that
   listing, if any exist, were not swept.
6. **Process history before 06:26:29.943Z was not inspected.** `scripts/lab.sh status` is
   not pre-approved in this session and was not run; the startup marker (E5) is the only
   lifecycle evidence, so H3's exclusion covers the observed lifetime only.
