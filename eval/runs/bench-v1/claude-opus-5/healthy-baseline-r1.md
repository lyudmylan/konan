---
konan_journal: 1
investigation:
  id: 2026-08-19-routine-handover-check
  trigger: "manual — /konan adapter (human profile). Complaint object: source=human, fingerprint=human-1787124468, labels.alertname=human-report, severity NOT STATED by reporter, startsAt=2026-08-19T07:27:48Z. Investigation started 2026-08-19T07:27:55Z; trigger latency 7s."
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-08-19T07:27:55Z
  concluded: 2026-08-19T07:37:53Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "No user-impacting incident is in progress: within the only window established on the investigator surface (the single process lifetime from 2026-08-19T07:27:33.103Z), every one of the nine non-investigator requests returned 2xx in 0.766-11.952 ms, and no non-investigator request has produced an error."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E4, E5, E13, E16]
    evidence_against: []
  - id: H2
    statement: "GET /products/{id} raises an unhandled ZeroDivisionError and returns HTTP 500 for catalog rows with units_in_stock == 0, because shop.py:64 computes units_ordered / product[\"units_in_stock\"] with no zero guard; product id 3 (\"Unobtainium Ingot\") is currently the only such row."
    incident_class: software-defect
    state: validated
    evidence_for: [E6, E7, E8, E9, E10, E15]
    evidence_against: []
  - id: H3
    statement: "The H2 defect is unexercised by real traffic rather than being the reported incident: all three observed 500s carry konan- investigator request ids, no non-investigator request touched /products/3 in the observable window, and the complaint reports no symptom at all. Exposure is limited by traffic volume, not by conditions - the row is listed publicly and the failure needs no special state."
    incident_class: software-defect
    state: validated
    evidence_for: [E2, E4, E5, E8, E15, E16]
    evidence_against: []
  - id: H4
    statement: "The service silently restarted, crashed, or is flapping - the failure mode a routine handover check most often uncovers."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E11, E14]
  - id: H5
    statement: "The observed 500s come from injected chaos or a degradation mode rather than a code defect."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E7, E12]
  - id: H6
    statement: "Product id 4 carries price: null where every other row carries a number, and this breaks price-consuming code paths such as order total computation."
    incident_class: software-defect
    state: invalidated
    evidence_for: [E8, E9]
    evidence_against: [E5, E9]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 (unhandled ZeroDivisionError at shop.py:64) deterministically and without credentials, for a product the public catalog lists to every client. No real request has hit it, but nothing gates it - the first user who opens \"Unobtainium Ingot\" gets a 500."
    evidence: [E6, E7, E8, E15]
evidence:
  - id: E1
    type: probe
    source: "/health, request_id konan-1787124487-50360"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":34.88981629209593}\n-- HTTP 200 in 0.001581s request_id=konan-1787124487-50360"
  - id: E2
    type: metric
    source: "/metrics, request_id konan-1787124492-50366, scraped 2026-08-19T07:28:12Z - before any investigator probe of /products/*"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2\n# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\nfaultline_chaos_enabled 0\nprocess_uptime_seconds 39.817986082984135"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:27:33.103Z - the only startup marker in the file"
    quote: "{\"ts\": \"2026-08-19T07:27:33.103Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:27:42.226Z - last of the nine non-investigator request lines"
    quote: "{\"ts\": \"2026-08-19T07:27:42.226Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/5 -> 200\", \"request_id\": \"e973790855a2\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/5\", \"status\": 200, \"duration_ms\": 0.766, \"client\": \"127.0.0.1:57980\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log - complete set of non-2xx request lines, extracted by grep -E '\"status\": (4|5)[0-9][0-9]'; five lines, every one konan-stamped"
    quote: "{\"ts\": \"2026-08-19T07:29:07.341Z\", ..., \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787124547-50429\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 7.759}\n{\"ts\": \"2026-08-19T07:29:12.454Z\", ..., \"request_id\": \"konan-1787124552-50452\", ..., \"status\": 500, \"duration_ms\": 2.503}\n{\"ts\": \"2026-08-19T07:29:23.141Z\", ..., \"message\": \"GET /orders/99 -> 404\", \"request_id\": \"konan-1787124563-50491\", ..., \"status\": 404}\n{\"ts\": \"2026-08-19T07:29:23.189Z\", ..., \"message\": \"GET /products/99 -> 404\", \"request_id\": \"konan-1787124563-50497\", ..., \"status\": 404}\n{\"ts\": \"2026-08-19T07:29:34.153Z\", ..., \"request_id\": \"konan-1787124574-50524\", ..., \"status\": 500, \"duration_ms\": 2.774}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:29:07.334Z - stack trimmed to the terminal frames, kept verbatim"
    quote: "{\"ts\": \"2026-08-19T07:29:07.334Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787124547-50429\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"Traceback (most recent call last): ... File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\\nZeroDivisionError: division by zero\"}"
  - id: E7
    type: probe
    source: "/products/3, request_id konan-1787124547-50429 (reproduced identically at konan-1787124552-50452 and konan-1787124574-50524)"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787124547-50429\"}\n-- HTTP 500 in 0.008584s request_id=konan-1787124547-50429"
  - id: E8
    type: probe
    source: "/products, request_id konan-1787124645-50600"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":119},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":38},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]\n-- HTTP 200 in 0.001553s request_id=konan-1787124645-50600"
  - id: E9
    type: probe
    source: "/products/4, request_id konan-1787124547-50435 - control: zero numerator, non-zero divisor"
    quote: "{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75,\"units_ordered\":0,\"turnover_score\":0.0}\n-- HTTP 200 in 0.001394s"
  - id: E10
    type: probe
    source: "/products/1 and /products/99 - controls: non-zero divisor, and missing id"
    quote: "{\"id\":1,...,\"units_in_stock\":119,\"turnover_score\":0.008403361344537815} -- HTTP 200\n/products/99 -- HTTP 404 {\"detail\":\"no such product: 99\"}"
  - id: E11
    type: metric
    source: "/metrics, process_uptime_seconds sampled across the investigation 07:28:07Z-07:37:28Z"
    quote: "process_uptime_seconds 34.89 -> 39.817986082984135 -> 94.21 -> 95.67 -> 125.29 -> 595.3340082080103 (monotonic, no reset; 595.33 s back-solves to 07:27:33.1Z)"
  - id: E12
    type: log
    source: "lab/logs/app.log (whole file) and /metrics at 07:28:12Z, 07:29:07Z, 07:29:51Z"
    quote: "faultline_chaos_enabled 0 (every scrape); zero chaos_enabled / chaos_disabled / chaos_failure / simulated_exception events anywhere in the log"
  - id: E13
    type: log
    source: "lab/logs/app.log - duration_ms of all nine non-investigator request lines, 07:27:33.840Z-07:27:42.226Z"
    quote: "/health 200 11.952 ; /health 200 0.886 ; /products 200 1.087 ; /products/1 200 1.03 ; /products/2 200 0.949 ; /orders 201 1.741 ; /orders 201 1.266 ; /orders 200 0.849 ; /products/5 200 0.766"
  - id: E14
    type: log
    source: "lab/logs/ filesystem metadata and the first line of lab/logs/app.log (local time is UTC+3)"
    quote: "drwxr-xr-x@ 3 lyudmylan  staff     96 Aug 19 10:27:33 2026 lab/logs\nfirst line: {\"ts\": \"2026-08-19T07:27:33.103Z\", ..., \"message\": \"Started server process [50263]\"}"
  - id: E15
    type: metric
    source: "/metrics after investigator probing of /products/3 - the counters the probes themselves created"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 3\nhttp_exceptions_total{type=\"ZeroDivisionError\"} 3"
  - id: E16
    type: log
    source: "lab/logs/app.log @ 2026-08-19T07:37:40Z - count of non-investigator request lines, grep '\"event\": \"request\"' | grep -vc 'konan-'"
    quote: "9"
gaps:
  - "The observable window is one process lifetime only, opening 2026-08-19T07:27:33.103Z - 15 seconds before the complaint was raised. lab/logs/ was itself created in that same second (E14), so no earlier faultline telemetry exists on the investigator surface. Nothing can be said about the service before 07:27:33Z."
  - "There has been no non-investigator traffic at all since 07:27:42.226Z - roughly ten minutes of silence up to the conclusion (E16). 'Nothing is wrong right now' therefore rests on an 8.4-second burst of nine requests that had already stopped six seconds before the complaint, not on a live traffic sample. Absence of user impact after that point is untested, not confirmed."
  - "Those nine requests are known only to be non-konan-stamped, which docs/lab.md defines as the simulated end-user channel. Whether they represent organic browsing or a startup smoke sequence is not observable; their ordering (health, health, products, product 1, product 2, order, order, orders, product 5) and consecutive client ports 57972-57980 are consistent with a scripted sequence."
  - "'No elevated latency' is asserted against no SLO and no historical baseline - only against the other eight samples in the same burst (E13). The 11.952 ms outlier is read as cold start because it is the first request after the startup marker."
  - "The judge asked for a read of shop.py:64 to convert the reachability claim into proof. Deliberately NOT done: the faultline checkout is outside the investigator surface under the blinding contract (AGENTS.md, eval/README.md). Reachability rests instead on the unauthenticated probe reproducing 3/3 (E7) and the row being publicly listed (E8)."
  - "A check of scripts/lab.sh log-retention behaviour via grep was blocked by the permission boundary and was not retried, per the stop-on-denial rule. The question was closed another way - lab/logs/ was created at the startup second (E14) - so no earlier log could have been overwritten there."
  - "Whether product 4's price: null breaks order creation is unresolved: POST /orders is outside the GET-only probe allowlist, so the price-consuming path cannot be exercised read-only (H6)."
  - "Load and saturation, third-party dependency, and data/DB lenses were not spawned - no lens files exist for them, and docs/lab.md records that this lab has no real database, no third-party dependency, and no distributed topology. Accepted as a blind spot rather than covered by theatre."
usage:
  model: claude-opus-5
  tokens: 2556764
  wall_clock_seconds: 598
---

# Routine handover check: no active incident, one unexercised 500 on /products/3

## Summary

**No active incident.** Nothing is failing for real traffic. Within the only window
that exists on the investigator surface — the single faultline process lifetime that
began 2026-08-19T07:27:33.103Z — all nine non-investigator requests returned 2xx in
0.766–11.952 ms (E4, E13), `http_exceptions_total` was empty before I probed anything
(E2), chaos was off at every scrape (E12), and uptime rose monotonically with no
restart (E11). Every non-2xx line in the log is my own (E5).

**But do not read that as "the shop is fine."** Probing found a real, deterministic
defect: `GET /products/3` returns HTTP 500 with an unhandled `ZeroDivisionError` at
`shop.py:64`, where `units_ordered / product["units_in_stock"]` runs with no zero
guard (E6, E7). Product 3, "Unobtainium Ingot", is the only catalog row with
`units_in_stock: 0` (E8) — and `/products` lists it to every client. Nothing gates the
failure: no auth, no flag, no rare state. It has caused zero user errors only because
no real request has happened to open that product. Ticket it; do not page for it.

Confidence: high on both halves. The defect mechanism is proved by a stack trace naming
the failing expression plus a 3/3 reproduction with matching controls, not by
correlation. The "no incident" half is honest but narrow — see Gaps: the user channel
has been silent for about ten minutes, so it is better stated as *no fault observed in
a small sample* than as *the service is verified healthy right now*.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 07:27:33.103 | faultline 0.1.0 starts; `lab/logs/` created in the same second — the observable window opens here, and nothing precedes it | E3, E14 |
| 07:27:33.840–07:27:42.226 | All non-investigator traffic: nine requests, all 2xx, 0.766–11.952 ms. Touches products 1, 2, 5 — never 3 | E4, E13 |
| 07:27:42.226 | Last non-investigator request. The user channel goes silent and stays silent | E16 |
| 07:27:48 | Complaint raised (`startsAt`) — routine handover question, no symptom named | — |
| 07:27:55 | Investigation begins; trigger latency 7 s | — |
| 07:28:12 | Baseline `/metrics`: `http_exceptions_total` has no series at all; chaos 0 | E2 |
| 07:29:07.334 | **First 500 in the service's life — caused by my probe.** ZeroDivisionError, `shop.py:64` | E6, E7 |
| 07:29:12, 07:29:34 | Reproduced twice more, identical, all konan-stamped | E5 |
| 07:37:28 | Uptime 595.33 s, still one lifetime; non-investigator request count still 9 | E11, E16 |

No configuration, deploy, or flag-change marker appears anywhere in the window — no
`chaos_*` or `simulated_exception` event exists (E12). There is no behaviour-change
boundary to explain, because no behaviour changed.

## Investigation

**Baseline** — `/health`, `/metrics`, and the full log tail (E1, E2, E3). Clean and
quiet: 39.8 s of uptime, nine 2xx requests, no exception series, chaos off.

**Triage** — the complaint names no symptom, so no lens could be excluded on complaint
evidence. Three lenses ran in parallel, each blind to the others:
`software-defect`, `interfaces`, `infra-process`. All three independently found the
same thing — the `/products/3` 500 — and all three independently flagged it as
investigator-triggered. `load-saturation`, `third-party`, and `data-db` were not
spawned: no lens files exist, and `docs/lab.md` records this lab has none of those
substrates. Recorded as a blind spot in Gaps rather than papered over.

**Deep-dive — skipped, deliberately.** Triage evidence for H2 was already
deterministic and complete: a stack trace naming the failing expression, a 3/3
reproduction, and the controls that bound it (product 4 with a zero *numerator* returns
200; product 99 returns a clean 404). Deep-dives fill evidence gaps; there was no gap
to fill, so the budget went to judging instead.

**Judge, round 1** — validated H2, killed H5 and H6, and refused H1/H3 as *worded*:
both said "ever" while every source covered one process lifetime, the latency claim
cited nothing, and H4's dismissal leaned on a log file whose retention was unproven.

**Round 2** — I supplied the settling items: the complaint text and timestamp, the
eight unshown durations, and the log-directory birth time. The judge accepted the
re-scoped H1 and H3, overturned nothing in H2/H5/H6, and made two corrections I have
adopted:

1. **"Latent" was the wrong word.** The defect is *unexercised*, not dormant. Latent
   implies special conditions are needed; here the only thing standing between the bug
   and a user is that nobody clicked that row. The Summary and the latent finding say so.
2. **The complaint's silence is not evidence of health.** "No specific user reports"
   removes an objection (there is no earlier reported window to check) but adds no
   affirmative signal. H1 rests on E2/E4/E5/E13 alone.

It also pressed for a read of `shop.py:64` to prove reachability. I declined — the
faultline checkout is outside the investigator surface under the blinding contract.
The claim rests on telemetry instead: an unauthenticated probe reproducing 3/3, and
the row appearing in the public catalog.

## Hypotheses

### H1 — No user-impacting incident in progress — **validated** (scoped)

For: nine non-investigator requests, all 2xx, 0.766–11.952 ms (E4, E13); baseline
`http_exceptions_total` empty *before* I probed, which covers all nine since they had
finished by 07:27:42 (E2); every non-2xx line in the file is konan-stamped (E5); count
unchanged at 9 ten minutes later (E16).

The scope is the claim's limit and I state it rather than hide it: this covers one
process lifetime and an 8.4-second traffic burst. It is not a verified-healthy
certificate for "right now" — after 07:27:42 there is no traffic to be healthy or
unhealthy.

### H2 — ZeroDivisionError on zero-stock products — **validated**

For: the stack terminates at the failing expression itself,
`units_ordered / product["units_in_stock"]` at `shop.py:64` (E6); 500 reproduced 3/3
(E7, E5, E15); product 3 is the only row with `units_in_stock: 0` (E8). The controls
close the "exactly those rows" direction: product 4 has `units_ordered: 0` and returns
200, so a zero *numerator* is harmless (E9); products 1 returns 200 (E10); 2 and 5
returned 200 to real traffic (E4). This is mechanism, not correlation — division raises
for a zero divisor and nothing else.

### H3 — The defect is unexercised, not the reported incident — **validated** (reworded)

For: all three 500s carry konan ids (E5); `http_requests_total` for
`/products/{product_id}` was 3 at baseline, matching exactly the three real hits on ids
1, 2 and 5 (E2, E4) — so no real request touched product 3; the complaint names no
symptom.

What this may **not** claim, per the judge and stated plainly: the defect is reachable
without any special condition. `/products` advertises product 3 to every client (E8),
and the 500 needs no credentials. Exposure is bounded by traffic volume, not by
difficulty. The next user who opens that item gets a 500 on the first try.

### H4 — Silent restart, crash, or flap — **invalidated**

Against: one startup marker in the file (E3); uptime monotonic across six samples,
34.89 → 595.33, back-solving to 07:27:33.1Z (E11). Round 1 correctly held that E3 only
counts if the log survives restarts. E14 closes it from the other side: `lab/logs/` was
*created* at 10:27:33 local — the startup second — and `app.log` begins with
"Started server process [50263]". No earlier process could have logged there and been
overwritten. What remains is not a restart but a boundary: history before 07:27:33
does not exist on this surface (Gaps).

### H5 — Injected chaos — **invalidated**

Against: no `chaos_*` or `simulated_exception` event anywhere, `faultline_chaos_enabled 0`
at every scrape (E12). More decisive than the absent markers: the stack terminates in
product source, not a fault-injection module (E6), and the failure is confined to the
one row whose divisor is zero — 3/3 on that row, 0/4 on the others (E7, E8, E9, E10).
An injector does not explain that.

### H6 — `price: null` on product 4 breaks price-consuming paths — **invalidated**

For: product 4 is the only row with a null price (E8, E9). Against: everything after
"and this breaks" was inference with no observation behind it. `/products/4` serves
the null through at 200 (E9), and the exhaustive non-2xx extraction contains no error
other than the three product-3 500s (E5). "Mystery Box" with an unknown price may well
be intentional. The write path that would settle it is outside a GET-only surface, so
this stays an unverified observation, not a finding.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. **Ticket the `/products/3` 500 against `shop.py:64`** — a zero-stock guard on
   `turnover_score`. Bug queue, not a page: no user has hit it. Treat urgency as a
   function of how likely someone is to open an out-of-stock item.
2. **Re-check with real traffic present.** This conclusion rests on nine requests in
   8.4 seconds. Whoever takes the shift should re-read `/metrics` once genuine traffic
   is flowing and confirm `http_exceptions_total` stays empty and
   `http_requests_total{path="/products/{product_id}",status="500"}` gains no
   *unstamped* increments.
3. **Sweep the catalog for other zero-divisor rows** by reading `/products` — today
   product 3 is the only one, but the same defect fires for any row that reaches
   `units_in_stock: 0`, so a product selling out creates a new 500 with no code change.
4. **Settle the `price: null` question** by reading the order-total code path, or by
   watching for an `http_exceptions_total{type="TypeError"}` series after an order
   containing item 4 — both outside this investigation's read-only GET surface.

## Gaps

- **One process lifetime, and it opened 15 seconds before the complaint.** `lab/logs/`
  was created in the startup second (E14), so nothing before 07:27:33.103Z exists on
  the investigator surface. A handover question about the previous shift cannot be
  answered from here at all.
- **The user channel has been silent since 07:27:42.226Z** — about ten minutes at
  conclusion (E16). "Nothing is wrong right now" is backed by a burst that had already
  ended six seconds *before* the complaint was raised. After that point, absence of
  impact is untested rather than confirmed. This is the single biggest limit on the
  verdict.
- **Traffic provenance is not observable.** The nine requests are known only to be
  non-konan-stamped, which `docs/lab.md` defines as the simulated end-user channel.
  Their ordering and consecutive client ports 57972–57980 look like a scripted sequence
  rather than organic browsing; if so, H1 rests on zero organic requests.
- **"No elevated latency" has no reference point** — no SLO, no history, only the other
  eight samples in the same burst (E13).
- **`shop.py:64` was not read**, deliberately: the faultline checkout is outside the
  investigator surface under the blinding contract. Reachability is argued from probe
  and catalog telemetry instead (E7, E8).
- **A `scripts/lab.sh` grep was blocked by the permission boundary and not retried**,
  per the stop-on-denial rule. The underlying question — could an earlier log have been
  overwritten — was closed another way, via E14.
- **`POST /orders` is outside the GET-only allowlist**, so the price-null question
  (H6) cannot be exercised read-only.
- **Three taxonomy lenses were not spawned** — load-saturation, third-party, data-db.
  No lens files exist for them and `docs/lab.md` records that this lab has no database,
  no third-party dependency, and no distributed topology. Accepted as a blind spot, not
  covered by theatre.
