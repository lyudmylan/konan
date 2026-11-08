---
konan_journal: 2
investigation:
  id: 2026-11-02-product-detail-500s
  trigger: "manual — /konan human report. Complaint object: source human, fingerprint human-1793663850, labels.alertname human-report (no severity stated by the reporter), startsAt 2026-11-02T23:57:30Z; investigation start 2026-11-02T23:57:38Z; trigger latency 8 s."
  complaint: |-
    Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of.
  started: 2026-11-02T23:57:38Z
  concluded: 2026-11-03T00:05:57Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The detail route's own code divides units_ordered by the product's units_in_stock without handling a zero denominator, so every GET for a catalog row whose units_in_stock is 0 raises an unhandled ZeroDivisionError and returns 500; today exactly one row (product 3) holds 0, and every other row serves 200."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The detail route's own code divides units_ordered by the product's units_in_stock with no handling of a zero denominator; the one catalog row with units_in_stock 0 therefore fails deterministically with an unhandled ZeroDivisionError and a 500, while rows with non-zero stock succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "An operational degradation switch inside the target (chaos or error injection) is injecting the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E9, E10, E11, E12, E13]
  - id: H3
    statement: "A process lifecycle event — crash, restart loop, or hang — is causing the failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E14, E15, E16]
  - id: H4
    statement: "A boundary component (gateway or proxy tier) or an upstream contract mismatch produces the 500s."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E5, E11, E12, E13]
  - id: H5
    statement: "Demand exceeded capacity — saturation of CPU, memory, workers, or connections — and the 500s are the overload symptom."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E5, E7, E15]
  - id: H6
    statement: "The onset is as reported: the failures began inside the hour before the complaint, started by a change at that moment."
    incident_class: infra-process
    state: inconclusive
    evidence_for: []
    evidence_against: [E14]
latent_findings:
  - statement: "The route's published contract does not cover the response customers actually receive: GET /products/{product_id} declares only 200 and 422 — no 5xx — and types its 200 body as additionalProperties true with no per-field types, so neither the undeclared 500 nor the catalog value that triggers it could be caught by a schema check."
    evidence: [E17]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:57:13.478Z"
    quote: |-
      {"ts": "2026-11-02T23:57:13.478Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "dd0444a4d3fc", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last):\n […] File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:57:13.487Z"
    quote: |-
      {"ts": "2026-11-02T23:57:13.487Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "dd0444a4d3fc", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.032, "client": "127.0.0.1:62583"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:57:14.551Z, 23:57:17.671Z, 23:57:19.790Z — the remaining three 500s, each from an unstamped client"
    quote: |-
      {"ts": "2026-11-02T23:57:14.551Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "26fcba008b73", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.91, "client": "127.0.0.1:62584"}
      {"ts": "2026-11-02T23:57:17.671Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "c137a8647a36", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 5.235, "client": "127.0.0.1:62586"}
      {"ts": "2026-11-02T23:57:19.790Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "15e521beea49", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.714, "client": "127.0.0.1:62590"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:57:14.546Z, 23:57:17.667Z, 23:57:19.786Z — the exception line of each remaining 500, tied by request_id; stacks identical to E1 and trimmed here"
    quote: |-
      {"ts": "2026-11-02T23:57:14.546Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "26fcba008b73", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "[…] line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}
      {"ts": "2026-11-02T23:57:17.667Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "c137a8647a36", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "[…] line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}
      {"ts": "2026-11-02T23:57:19.786Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "15e521beea49", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "[…] line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\nZeroDivisionError: division by zero"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:57:16.609Z — a success interleaved between the second and third failure"
    quote: |-
      {"ts": "2026-11-02T23:57:16.609Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "b3061cc76b97", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.695, "client": "127.0.0.1:62585"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:57:08.298Z and 23:57:09.358Z — the other two non-investigator successes on the detail route"
    quote: |-
      {"ts": "2026-11-02T23:57:08.298Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "def8060aa4af", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.044, "client": "127.0.0.1:62580"}
      {"ts": "2026-11-02T23:57:09.358Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "873a910fe331", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.977, "client": "127.0.0.1:62581"}
  - id: E7
    type: metric
    source: "/metrics, probe request_id konan-1793663884-12316 @ 2026-11-02T23:58:04Z — the baseline reading, before any investigator request to the detail route"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E8
    type: metric
    source: "/metrics, probe request_id konan-1793664119-12501 @ 2026-11-03T00:01:59Z — the closing reading"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 6
      http_exceptions_total{type="ZeroDivisionError"} 6
  - id: E9
    type: metric
    source: "/metrics @ 2026-11-02T23:58:04Z, @ 23:59:33Z and @ 2026-11-03T00:01:59Z — unchanged at every reading"
    quote: "faultline_chaos_enabled 0"
  - id: E10
    type: probe
    source: "GET /products — HTTP 200"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E11
    type: probe
    source: "GET /products/3, request_id konan-1793663962-12357 @ 2026-11-02T23:59:22Z — investigator reproduction"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793663962-12357"}
      -- HTTP 500 in 0.004378s request_id=konan-1793663962-12357
  - id: E12
    type: probe
    source: "GET /products/4 — HTTP 200"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
  - id: E13
    type: probe
    source: "GET /products/5 — HTTP 200"
    quote: |-
      {"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500,"units_ordered":0,"turnover_score":0.0}
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:57:06.501Z–23:57:06.502Z — the first lines of the file; the only startup markers in it, and no rotation backups (.1–.3) exist"
    quote: |-
      {"ts": "2026-11-02T23:57:06.501Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [12208]"}
      {"ts": "2026-11-02T23:57:06.502Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E15
    type: metric
    source: "/metrics @ 2026-11-02T23:58:04Z, @ 23:59:33Z and @ 2026-11-03T00:01:59Z — monotonic uptime, flat memory"
    quote: |-
      process_uptime_seconds 57.94910745904781 -> 146.542568749981 -> 293.32438062503934
      process_max_rss_bytes 47972352 -> 47988736 -> 48414720
  - id: E16
    type: probe
    source: "GET /health, request_id konan-1793663991-12408"
    quote: |-
      {"status":"ok","uptime_seconds":165.4810662921518}
      -- HTTP 200
  - id: E17
    type: probe
    source: "GET /openapi.json — HTTP 200; the declared responses of GET /products/{product_id}"
    quote: "only \"200\" and \"422\" are declared, no 5xx; the 200 schema is {\"type\":\"object\",\"additionalProperties\":true} with no per-field types"
gaps:
  - "Onset is unverifiable from telemetry. lab/logs/app.log begins at the process start (E14) and no rotation backups (.1–.3) exist, so nothing predates 2026-11-02T23:57:06.501Z — about 3 minutes of retention at the first reading, against a complaint window of an hour. The first retained request for product 3 already failed, 7 seconds after start; that is a property of the retention window, not an observed onset. 'Within the last hour' can be neither confirmed nor denied, and there is no last-known-good for this route."
  - "What would settle the onset lies outside the investigator's surface: the moment product 3's units_in_stock became 0, and the ship time of the detail route's code. Whichever came later is the true onset. Neither is in the probe allowlist or in the logs."
  - "No source was read. The mechanism is proven from the runtime stack (E1, E4) and from probing (E11, E12, E13), so the claim is that the division ran unguarded for a zero denominator — not that the file contains no guard at all. A guard testing for None but not for 0, or one on the wrong field, would look identical in telemetry."
  - "'Several customers' is not corroborated. The four non-investigator 500s come from 127.0.0.1 on near-consecutive ports (62583, 62584, 62586, 62590) and the access line carries no user-agent or upstream IP, so the requests are non-investigator but not demonstrably distinct people — the port pattern fits one caller making successive requests. The count of 4 is also a floor bounded by retention, not a total."
  - "The order path could not be exercised: the probe surface is GET-only, so the exposure of POST /orders to the zero-stock row — and to the null-priced row 4 seen in E10 and E12 — is unknown. The null price itself produced no observed failure."
  - "faultline_chaos_enabled covers one named switch, and every reading of it (E9) post-dates the four user-facing failures. An injector is refuted by the data-selective reproduction (E11 against E12 and E13, taken while the gauge read 0), not by the gauge's timing; a differently-named flag was never observable."
  - "Three of the six taxonomy classes have no lens in this repo: only software-defect, infra-process and interfaces ship under skills/investigate/lenses/. load-saturation was excluded from baseline evidence (E15, E7, E5) rather than by its own lens; third-party and data-db have no surface in this lab at all — faultline has no external dependency and no database (docs/lab.md, 'Known gaps of this lab')."
usage:
  model: claude-opus-5
  tokens: 2104505
  wall_clock_seconds: 499
---

# Product detail route returns 500 for the one sold-out catalog row

## Summary

**Root cause identified.** The product detail route computes a `turnover_score` by dividing
`units_ordered` by the product's `units_in_stock`, and does not handle a zero denominator.
Product 3 ("Unobtainium Ingot") holds `units_in_stock: 0` (E10), so every request for that
one product raises an unhandled `ZeroDivisionError` and returns HTTP 500 (E1, E2, E4),
while every other row returns 200 — including a request for product 2 that lands *between*
two failures (E5). I reproduced the failure on demand (E11) and confirmed the healthy
contrast on products 4 and 5 (E12, E13). The failure is deterministic per input, which is
exactly why a customer's refresh never clears it: nothing is intermittent, nothing is
overloaded, and the fault is keyed to the data in the row, not to the request.

Confidence is high. The mechanism is reproducible, the counters move one-for-one with it
(`http_exceptions_total{type="ZeroDivisionError"}` equals the 500 count on the route at both
readings, E7 and E8), and four competing families were killed with evidence: no injected
degradation (E9, E11), no process lifecycle event (E14, E15, E16), no boundary or gateway
tier (E1, E11), no saturation (E15, E7 — 11 requests total on the route, every response
under 11 ms).

**Impact, stated precisely.** Four non-investigator 500s are in retained telemetry (E2, E3),
all on `/products/3`, all before any investigator traffic touched that route (E7). The two
further 500s in the closing counter (E8) are my own stamped reproductions. Four is a floor,
not a total — retention covers only about three minutes.

**The severity is wider than one row.** The blast radius is set by data, not by product
identity: *any* row whose `units_in_stock` reaches 0 enters it. For a shop, selling out is a
normal state, so the correct reading is "every product that sells out breaks its own detail
page", of which product 3 is today's single instance. The snapshot is one row of five; the
exposure is the whole catalog over time.

**What I could not establish:** when this began. The complaint says "within the last hour";
the log starts about three minutes before the report and keeps no backups, so the onset claim
is untestable from here, and I record it as inconclusive rather than confirmed or refuted.
The reporter's "no deploys that we know of" is consistent with the retained log — it holds no
configuration, flag or deploy marker of any kind — but that window is far too short to be
evidence about deploys.

## Timeline

| Time (UTC) | Event |
| --- | --- |
| 23:57:06.501 | Process start, PID 12208, faultline 0.1.0 (E14). Log and retention begin here — nothing earlier exists. |
| 23:57:08.298 | `GET /products/1` → 200 (E6) |
| 23:57:09.358 | `GET /products/2` → 200 (E6) |
| 23:57:13.478 | First `ZeroDivisionError`, at the `turnover_score` division (E1) |
| 23:57:13.487 | `GET /products/3` → 500, 10.032 ms — user-facing failure 1 (E2) |
| 23:57:14.546–.551 | Exception, then `GET /products/3` → 500 — failure 2 (E3, E4) |
| 23:57:16.609 | `GET /products/2` → 200 in 0.695 ms, *between* failures 2 and 3 (E5) |
| 23:57:17.667–.671 | Failure 3 (E3, E4) |
| 23:57:19.786–.790 | Failure 4 (E3, E4) — the last non-investigator 500 in telemetry |
| 23:57:30 | Complaint raised (`startsAt`) |
| 23:57:38 | Investigation starts — trigger latency 8 s |
| 23:58:04 | Baseline metrics: 500 count 4, `ZeroDivisionError` 4, chaos gauge 0 (E7, E9) |
| 23:59:22 | Investigator reproduction: `/products/3` → 500 (E11) |
| 23:59:31–:32 | Investigator controls: `/products/4`, `/products/5` → 200 (E12, E13) |
| 00:01:59 | Closing metrics: 500 count 6, `ZeroDivisionError` 6, chaos gauge still 0, uptime 293.3 s monotonic (E8, E9, E15) |

No configuration, feature-flag or deploy marker appears anywhere in the retained log.

## Investigation

### Complaint block

The complaint object, as the `/konan` adapter synthesized it:

```json
{
  "source": "human",
  "fingerprint": "human-1793663850",
  "labels": { "alertname": "human-report" },
  "annotations": {
    "summary": "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  },
  "startsAt": "2026-11-02T23:57:30Z"
}
```

No `severity` label: the reporter stated none, and severity is never inferred. Investigation
start: **2026-11-02T23:57:38Z** — trigger latency **8 seconds**.

### Rounds

**Baseline.** `/health` returned 200 with an uptime of 51.4 s; `/metrics` already showed the
shape of the incident (4 × 500 and 3 × 200 on the detail route, 4 × `ZeroDivisionError`,
chaos gauge 0); the whole log was 25 lines. The healthy-monitoring trap was live here: health
was green throughout while the business surface failed.

**Triage — three lenses in parallel, each blind to the others.** software-defect,
infra-process and interfaces, every one given only its lens file, the surface contract, the
verbatim complaint and the baseline. The software-defect lens reproduced the fault and found
the zero divisor in the catalog listing; infra-process ruled out its own family and reported
the retention limit as a finding of its own; interfaces ruled out gateway and dependency
shapes, and found the contract gap recorded as a latent finding. The three agreed without
contact.

**Deep-dive — deliberately skipped.** H1's triage evidence was already deterministic and
complete: the prediction ("the row with stock 0 fails, all others succeed") had been probed
in both directions. The loop's own rule is that deep-dives fill evidence gaps rather than
re-prove, so H1 went straight to the judge, with one round and two of the three lens budget
items unspent.

**Judge — adversarial, evidence-only.** The judge saw the hypothesis list and the verbatim
quotes, never the story. It validated H1 and confirmed all four refutations, and returned
five corrections, all of which are carried above:

1. "No zero guard" was a source-code claim resting on a runtime stack — trimmed to "ran
   unguarded for a zero denominator" (gap 3).
2. Product 1 had no observed result, so "every other row succeeds" was partly unproven — the
   log already held `GET /products/1` → 200 (E6), which closes it with non-investigator
   evidence.
3. Only one of the four 500s had been tied to an exception line by `request_id` — the other
   three were in the log and are now cited per request (E4).
4. "Real users" overreached: the clients are localhost ports with no identity field, and 4 is
   a retention floor (gap 4). The closing counter (E8) makes the investigator delta explicit.
5. H6 was listed as refuted on the strength of missing data. The judge was right: an absent
   log cannot refute an onset, so H6 is **inconclusive**.

The judge also noted that the chaos gauge readings all post-date the failures, so the honest
refutation of H2 is the data-selective reproduction rather than the gauge — recorded in gap 6.

## Hypotheses

### H1 — zero denominator in the detail route — **validated**

Every request for the one row with `units_in_stock: 0` fails; every row with non-zero stock
succeeds. The stack names the operation and the field (E1, E4); the catalog listing shows
product 3 as the only zero-stock row (E10); the reproduction fails on demand (E11) and the
controls succeed (E12, E13), each returning `turnover_score: 0.0` — a zero *numerator* is
safe, only the zero denominator throws, which is why order traffic is not needed to trigger
it and why a refresh cannot clear it. Non-investigator traffic shows the same split: 500 on
product 3 (E2, E3) against 200 on products 1 and 2 (E5, E6), interleaved in time. Nothing
offered against it.

The limit of the claim: the defect is proven at runtime, not in source (gap 3), and the
exposure grows with the data — any row that sells out joins it.

### H2 — injected degradation switch — **invalidated**

The gauge reads 0 at every sampling (E9), but the decisive refutation is the shape of the
failure, not the gauge: the reproduction failed at 23:59:22 while the gauge read 0, and it
failed on exactly the row whose stored value makes the arithmetic impossible (E10, E11) while
neighbours served 200 (E12, E13). An injector does not choose its victim by `units_in_stock`.
Caveat in gap 6: every gauge reading post-dates the user-facing failures.

### H3 — process crash, restart loop, or hang — **invalidated**

One startup marker, one PID (E14); uptime rises at wall-clock rate with no reset and memory
is flat across three readings (E15); `/health` answers 200 throughout (E16). Decisive on its
own: a dead or hung process does not emit a structured 500 in 4.7 ms (E2, E3).

### H4 — gateway tier or upstream contract mismatch — **invalidated as a cause**

The fault is inside the target's own code (E1), and a direct probe reproduces it with the
target's own error body (E11) — no intermediary is needed to explain anything. No 502, 503 or
504 appears anywhere. The contract *surface* finding that came from this lens is real but
secondary, and rides along as a latent finding (E17): the route declares no 5xx at all, so the
response customers receive is outside its published contract.

### H5 — load saturation — **invalidated**

Volume is the refutation: 11 requests on the route across the process lifetime (E7, E8), every
response under 11 ms, nothing queued. The cleanest single item is E5 — a 0.695 ms success
sitting between two failures, which no saturated system produces. Memory is flat (E15). Noted
honestly: the surface exposes no CPU or worker-pool gauge, so this rests on volume and latency,
which is sufficient at this volume.

### H6 — onset inside the hour before the report — **inconclusive**

E14 marks where retention begins; it bounds what can be known rather than refuting the claim,
so this is inconclusive, not invalidated — the hypothesis is untestable from the surface, and
the first retained failure being 7 seconds after process start says nothing about onset. The
second half of the statement ("a change at that moment started them") has neither support nor
opposition: no change marker exists in the window, and the window is too short to make that
absence meaningful. Under the H1 mechanism the true onset is whichever came later — the code
shipping, or the stock reaching 0.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. **Fix the onset outside telemetry.** Ask whoever owns catalog data when product 3's
   `units_in_stock` became 0, and compare that with the ship time of the detail route. The
   later of the two is the onset; no amount of probing here can supply it.
2. **Size the real exposure, not the snapshot.** `GET /products` lists the whole catalog
   read-only (E10) — today only row 3 is at 0, but the question to carry forward is which rows
   are heading there, since selling out is normal.
3. **Watch the two counters that move one-for-one with this defect:**
   `http_exceptions_total{type="ZeroDivisionError"}` and
   `http_requests_total{method="GET",path="/products/{product_id}",status="500"}`. When reading
   them, subtract investigator traffic: 2 of the 6 at 00:01:59Z are konan-stamped reproductions.
4. **Preserve the current `lab/logs/app.log` before rotation drops it.** Short retention is
   what cost this investigation the onset; the next investigation will pay the same price.
5. **Review two things this investigation saw but could not test:** the null `price` on row 4
   (`"price":null` with a 200 on its detail route, E10, E12) and the undeclared 5xx on the
   route's published contract (E17). Both need the order path, which is write-shaped and
   outside the read-only surface.

## Gaps

The seven entries in the machine core, in short: **the onset is unknowable here** (retention is
~3 minutes against an hour-long complaint window, and no backups exist), and **what would settle
it is outside the surface** (the stock value's change history, the code's ship time). **No source
was read**, so the mechanism is "divided unguarded", not "has no guard anywhere". **"Several
customers" is uncorroborated** — the callers are localhost ports with no identity field, and 4
is a floor set by retention. **The order path was never exercised**, so the zero-stock row's and
the null-priced row's behaviour there is unknown. **The chaos gauge was only ever read after the
failures**, so an injector is refuted by the reproduction's data-selectivity, not by the gauge.
And **three taxonomy classes had no lens**: load-saturation was excluded from baseline evidence
instead of by its own lens, while third-party and data-db have no surface in this lab at all.
