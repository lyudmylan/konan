---
konan_journal: 2
investigation:
  id: 2026-11-03-product-detail-zero-stock-500
  trigger: "manual — /konan human report. Complaint object: source=human, fingerprint=human-1793689422, labels.alertname=human-report, no severity stated by the reporter, startsAt=2026-11-03T07:03:42Z. Investigation start 2026-11-03T07:03:55Z; trigger latency 13 s."
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-03T07:03:55Z
  concluded: 2026-11-03T07:10:34Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: 'The product-detail handler computes turnover_score as units_ordered divided by the row''s units_in_stock with no guard for zero, so the one catalog row with units_in_stock 0 (id 3) raises an unhandled ZeroDivisionError and returns HTTP 500 on every request, while every other row returns 200.'
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: 'GET /products/{product_id} divides units_ordered by product["units_in_stock"] without a zero guard; id 3 is the only catalog row with units_in_stock 0, so every request for /products/3 raises an unhandled ZeroDivisionError and returns HTTP 500 while all other ids return 200.'
    incident_class: software-defect
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E8, E13]
    evidence_against: []
  - id: H2
    statement: 'An operational degradation switch inside the target (chaos / injected-failure mode) was on earlier this morning and is off now, and it produced the errors customers saw.'
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E7, E9]
  - id: H3
    statement: 'The process crashed and restarted this morning, and that lifecycle event is what customers hit.'
    incident_class: infra-process
    state: invalidated
    evidence_for: [E1, E14]
    evidence_against: [E8, E11, E13]
  - id: H4
    statement: 'Demand exceeded capacity — resource exhaustion or queue saturation — and the 500s are its symptom.'
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E8, E10, E11]
  - id: H5
    statement: 'The observed HTTP 500s are an artifact of investigator probe traffic only, so there is no customer-facing defect.'
    incident_class: software-defect
    state: invalidated
    evidence_for: [E7, E8, E14]
    evidence_against: [E4, E6, E13]
latent_findings:
  - statement: 'The route serves an HTTP status its own published contract does not declare, and the error body exports an internal exception class name to the client: /openapi.json declares only 200 and 422 for GET /products/{product_id}, while the live failure returns 500 with an exception_type field. A client generated from the spec has no branch for what customers receive.'
    evidence: [E15, E3]
  - statement: 'Catalog row id 4 carries price: null — a second unvalidated nullable field of the same shape as the zero-stock row, unguarded by the list contract. It serves HTTP 200 today and no failure was observed, so it is not part of this incident.'
    evidence: [E6, E12]
evidence:
  - id: E1
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T07:03:32.345Z'
    quote: '{"ts": "2026-11-03T07:03:32.345Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: probe
    source: '/health, request id konan-1793689444-21834'
    quote: '{"status":"ok","uptime_seconds":32.52603600011207} / -- HTTP 200 in 0.002077s request_id=konan-1793689444-21834'
  - id: E3
    type: probe
    source: '/products/3, request id konan-1793689542-21933, HTTP 500'
    quote: '{"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793689542-21933"}'
  - id: E4
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T07:05:42.905Z — event unhandled_exception, exception_type ZeroDivisionError, stack field (absolute path prefix trimmed; kept fields unaltered)'
    quote: |-
      File ".../faultline/src/faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
                            ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
      ZeroDivisionError: division by zero
  - id: E5
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T07:05:42.907Z'
    quote: '{"ts": "2026-11-03T07:05:42.907Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793689542-21933", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 2.697, "client": "127.0.0.1:64609"}'
  - id: E6
    type: probe
    source: '/products, request id konan-1793689830-22056, HTTP 200 — the complete catalog array'
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E7
    type: metric
    source: '/metrics — the only series under this counter'
    quote: 'http_exceptions_total{type="ZeroDivisionError"} 4'
  - id: E8
    type: metric
    source: '/metrics'
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 8'
  - id: E9
    type: metric
    source: '/metrics, request id konan-1793689555-21978; corroborated by log search — no chaos_enabled, chaos_disabled, chaos_failure or simulated_exception event line exists anywhere in lab/logs/app.log'
    quote: 'faultline_chaos_enabled 0'
  - id: E10
    type: log
    source: 'lab/logs/app.log @ 2026-11-03T07:03:38.406Z — a non-investigator request (bare hexadecimal request id)'
    quote: '{"ts": "2026-11-03T07:03:38.406Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "6225c66755a7", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.72, "client": "127.0.0.1:64571"}'
  - id: E11
    type: metric
    source: '/metrics, two reads 70 s apart (request ids konan-1793689447-21847 and konan-1793689517-21883); one PID (21751) across the whole log'
    quote: 'process_max_rss_bytes 46972928 (byte-identical at both reads) / process_uptime_seconds 35.50783829204738 then 105.18936845916323'
  - id: E12
    type: probe
    source: '/products/4, request id konan-1793689543-21941, HTTP 200'
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}'
  - id: E13
    type: probe
    source: 'repeat probes of the same route, interleaved in time'
    quote: '/products/3 returned HTTP 500 with an identical ZeroDivisionError body on 4 of 4 attempts (konan-1793689539-21923, konan-1793689542-21933, konan-1793689544-21948, konan-1793689547-21963); on the same route /products/1 (konan-1793689538-21913), /products/2 (konan-1793689539-21918) and /products/4 (konan-1793689543-21941, konan-1793689545-21958) returned HTTP 200'
  - id: E14
    type: log
    source: 'lab/logs/app.log line 1 @ 2026-11-03T07:03:32.344Z; directory listing of lab/logs/ shows exactly one file, app.log, with no .1-.3 rotated backups'
    quote: '{"ts": "2026-11-03T07:03:32.344Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [21751]"}'
  - id: E15
    type: probe
    source: '/openapi.json, request id konan-1793689666-22015 — the declared responses for the failing route (response content schemas elided at the marks)'
    quote: '"/products/{product_id}":{"get":{"tags":["shop"],"summary":"Get Product","operationId":"get_product_products__product_id__get","parameters":[{"name":"product_id","in":"path","required":true,"schema":{"type":"integer","title":"Product Id"}}],"responses":{"200":{"description":"Successful Response",...},"422":{"description":"Validation Error",...}}}}'
gaps:
  - 'The window the complaint names — "this morning", before 2026-11-03T07:03:32Z — has no observational substrate on this surface. lab/logs/app.log begins at 07:03:32.344Z with no rotated backups (E14), and every /metrics counter is since-process-start by construction (E11), so a counter cannot hold a pre-start event. Whether a customer hit this defect before that boundary is neither supported nor refuted here.'
  - 'How many customers were affected is not recoverable. All four observed 500s carry konan- probe request ids, and the parity of E7 with E8 (4 exceptions, 4 route 500s) forbids any user-visible 500 on that route since process start. The defect is proven live and deterministic; its user-facing count this morning is not in this record.'
  - 'Whether the 07:03:32Z process start was a first start or a restart that erased earlier evidence cannot be determined: no predecessor PID, shutdown line, signal or non-zero exit appears, and the startup line is line 1 of the only log file (E14).'
  - 'No observation source with retention predating 07:03:32Z exists within this surface contract — no reverse-proxy, load-balancer, CDN access log or error-tracker history. That, or the complaint''s own artifact (ticket timestamp, screenshot, affected order id), is the only thing that could place a real user inside the unrecorded window.'
  - 'Resources other than peak RSS and uptime are unmeasured on this surface: no CPU, queue-depth or connection-pool metrics exist. Load-saturation was therefore excluded on failure signature and a flat RSS high-water mark (E5, E11) rather than on direct contention metrics.'
  - 'Residual on the degradation-switch hypothesis: a toggle inside a predecessor process before 07:03:32Z is unfalsifiable rather than refuted, because no configuration audit trail for the switch and no rotated log cover that window (E14). The invalidation of H2 rests on E4 and E7 — a genuine arithmetic fault in the target''s own source, and ZeroDivisionError as the only exception series — not on the current gauge value.'
usage:
  model: claude-opus-5
  tokens: 1860258
  wall_clock_seconds: 399
---

# Product detail page returns HTTP 500 for the one zero-stock catalog row

## Summary

**Root cause identified, and it matches the reported symptom exactly.** The
product-detail handler builds a `turnover_score` field by dividing `units_ordered` by
the row's `units_in_stock`, with no guard for a zero denominator (E4). Product id 3 —
"Unobtainium Ingot" — is the only row in the catalog with `units_in_stock: 0` (E6), so
every request for `/products/3` raises an unhandled `ZeroDivisionError` and returns
HTTP 500 with the generic "internal server error" body a customer would read as
"Internal Server Error" (E3, E5). The failure is deterministic, not intermittent: 4 of
4 attempts failed, while ids 1, 2 and 4 returned 200 interleaved in time on the same
route (E13). Confidence is high — the evidence is a stack frame at the failing
instruction, not a correlated signal.

Two scope limits belong in the same breath as that conclusion. First, **the defect is
live but every observed 500 is self-induced**: all four carry `konan-` probe request
ids, and the exact parity of 4 exceptions with 4 route 500s (E7, E8) means no customer
received a 500 on that route since the process started. Second, **the window the
complaint names is not observable at all** — the log begins at 07:03:32.344Z, about a
minute before the report reached me, with no rotated backups (E14), and metrics counters
reset there. So this is not a claim that no one was affected; that would overclaim from
silence. It is: the defect reliably produces the reported symptom for any customer who
opens product 3, and this surface cannot show who already did.

Reachability is not in doubt. The public catalog listing advertises id 3 to every caller
(E6), and the failure is per-input rather than probabilistic (E13) — so a customer who
follows the listing to that product gets a 500 on the first try, every try. The eight
non-investigator requests in the record happened not to touch id 3.

## Timeline

- **2026-11-03T07:03:32.344Z** — process start, PID 21751; this is line 1 of the only
  log file, so nothing earlier survives in any form (E14).
- **2026-11-03T07:03:32.345Z** — `event: startup`, faultline 0.1.0. No deploy, config
  or flag-change marker appears anywhere in the window, and the version does not change
  (E1).
- **07:03:33.085Z – 07:03:38.406Z** — eight non-investigator requests (bare hexadecimal
  request ids, client ports 64564–64571): `/health` ×2, `/products`, `/products/1`,
  `/products/2`, `POST /orders`, `/orders`, `/products/5`. All returned 2xx; none
  requested id 3 (E10).
- **07:03:42Z** — the complaint is raised by a human (`startsAt`).
- **07:03:55Z** — investigation starts; trigger latency 13 s.
- **07:04:04Z – 07:04:07Z** — baseline: `/health` 200 (E2), `/metrics` showing no
  exception series and `faultline_chaos_enabled 0` (E9).
- **07:05:38Z – 07:05:48Z** — triage lenses reproduce the failure. First 500:
  `/products/3` at 07:05:42.905Z, unhandled `ZeroDivisionError` with the stack frame at
  the division (E4), access line `GET /products/3 -> 500` in 2.697 ms (E5).
- **07:07:46Z** — `/openapi.json` read: the route declares only 200 and 422 (E15).
- **07:10:30Z** — full catalog read; id 3 confirmed the sole zero-stock row (E6).

## Investigation

**Baseline** (step 1) found a healthy-looking target: `/health` 200, no exception
series, chaos gauge 0, every logged request 2xx. It also surfaced the constraint that
shaped everything after it — uptime 32.5 s, so the entire observable record was ~36
seconds old and the complaint's window lay outside it. This is the healthy-monitoring
trap in its literal form: a green `/health` while a business surface fails for one
input.

**Triage** (step 2) spawned all three lenses in parallel — infra-process, interfaces,
software-defect — since a vague "Internal Server Error" report excludes none of them on
evidence. Two lenses independently reproduced the same failure on `/products/3`;
software-defect supplied the mechanism from the `stack` field, interfaces supplied the
discriminator (a stable per-input split, not a stable per-request fraction, which is
what rules out injected degradation and a flaky dependency). Infra-process returned
clean and contributed the sharpest negative: one PID, monotonic uptime, byte-identical
peak RSS 70 s apart.

**Deep-dive** (step 3) was deliberately skipped. H1's triage evidence was already
deterministic and complete — a stack frame at the failing instruction plus 4/4
reproduction — and deep-dives exist to fill evidence gaps, not to re-prove. Budget went
to the judge instead.

**Judge** (step 4) validated H1 and invalidated H2–H5, and earned its keep by refusing
two things I had let through. It ruled H1's quantifier ("the only row with zero stock")
**inconclusive**, because the ledger cited a single element of the catalog array and
nothing bounded the catalog at five rows — non-zero stock elsewhere was merely inferable
from 200s. One probe settled it (E6), and the quantifier now stands. It also caught an
arithmetic error in my baseline summary: I had written nine non-investigator requests
where the log holds eight request lines, having counted an `order_created` event line as
a request. The corrected count of eight closes the books exactly against E8 — three user
200s on the detail route plus five investigator 200s equals the counter's 8. The judge's
instruction to lean on counter parity rather than on enumeration is why the user-impact
claim in this journal rests on E7/E8 arithmetic and not on a census of log lines.

It also declined to invalidate H2 on the grounds I had offered. A gauge reading 0 now
says nothing about a past toggle; the invalidation rests instead on a genuine arithmetic
fault in the target's own source and on `ZeroDivisionError` being the only exception
series ever recorded. The residual — a switch in a predecessor process — is recorded as
unfalsifiable, not refuted.

One round, no iteration: a validated hypothesis whose prediction was confirmed by
probing ends the loop (step 5).

## Hypotheses

### H1 — unguarded division in the product-detail handler — **validated**

The evidence is mechanism, not proximity. E4 is a stack frame inside the target's own
source at the division expression itself, with `ZeroDivisionError` raised and unhandled.
E6 supplies the zero denominator for id 3 and, as the complete catalog, establishes that
it is the only such row. E12 is the useful control: id 4 returns
`"turnover_score":0.0` with `units_in_stock: 75`, which proves the field is computed per
request on the response path rather than stored — so the denominator is read from the row
on every call. E13 is the prediction check, and its time-interleaving is what excludes
"something was wrong during a window": the discriminator is the id, not the clock.
E7 and E8 close the arithmetic — 4 `ZeroDivisionError`, the only exception series, equal
to 4 route 500s, leaving no unexplained residue and no second failure mode.

### H2 — an operational degradation switch was on earlier — **invalidated**

E4 shows a real arithmetic fault in application source; an injected failure does not
raise from a genuine division expression in the frame. E7's parity leaves no room for a
simulated exception anywhere in the record, and no chaos or simulated-exception event
line exists in the log (E9). Residual, recorded under Gaps: for the window before
07:03:32Z there is no log at all, so a toggle in a predecessor process is unfalsifiable
rather than refuted.

### H3 — a crash and restart is what customers hit — **invalidated**

E1 and E14 prove a process *started*; they do not prove one *died*. No predecessor PID,
shutdown line, signal or non-zero exit appears — and E14 establishes that the startup
line is line 1 of the only log file, so a predecessor could not appear here even if one
existed. "The startup timestamp falls in the morning, and the complaint says morning" is
correlation. The hypothesis also fails independently on its second half: E11 shows one
PID with monotonic uptime across the window, so no restart occurred during the 500s, and
E8 with E13 attribute those 500s entirely to the id-3 defect.

### H4 — demand exceeded capacity — **invalidated**

Refuted on three independent axes. Volume: E8 totals 12 requests on the route, not a
saturation regime. Resources: E11's peak RSS is byte-identical 70 s apart under active
probing, which a leak or memory-pressure story cannot survive. Shape: E10 at 0.72 ms,
and decisively E5 — the *failing* request completed in 2.697 ms. Saturation failures are
slow and gateway-shaped (queued, timed out, 503/504). A 500 arriving in under 3 ms with
a code-level stack is categorically the wrong shape.

### H5 — the 500s are a probe artifact, so there is no customer-facing defect — **invalidated**

The premise holds and is retained in the Summary and Gaps: all four 500s carry `konan-`
ids, and the parity of E7 with E8 makes it arithmetically impossible for a
non-investigator request to have received a 500 on that route since process start. The
conclusion does not follow. E4 locates the fault in shipped code, E6 shows the
user-facing listing advertises id 3 to every caller, and E13 shows the failure is
deterministic rather than probe-dependent. Eight user requests across a 5.3-second
window that happened not to touch id 3 is absence of evidence, not evidence of absence.
"Latent" here is a statement about traffic luck, not about code health.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. **Recover the unobservable window from outside the process.** Any access log with
   retention predating 2026-11-03T07:03:32Z — reverse proxy, load balancer, CDN — or an
   error-tracker history, searched for requests to `/products/3` with bare (non-`konan-`)
   request ids and their status codes. This is the one thing that converts "unsupportable"
   into a user-impact number.
2. **Ask Support for the complaint's own artifacts.** Ticket timestamps, screenshots, the
   product the customers were viewing, or affected session ids. A reported product id
   that is not 3 would mean a second defect this investigation has not seen; an id of 3
   would place real users inside the unrecorded window.
3. **Check log retention as its own finding.** `lab/logs/` holds a single file with no
   rotated backups, so a process start erases the prior record. Any incident reported
   more than a few minutes after it happens is currently uninvestigable from this surface.
4. **Confirm the catalog surface for the other unvalidated row.** Product id 4 carries
   `price: null` (E6, E12) and serves 200 today. Reading whether any other endpoint
   performs arithmetic on `price` would establish whether that row is a second latent
   failure or benign.
5. **Compare the published contract with live behavior for the whole API.** The detail
   route declares only 200 and 422 while serving 500 with an internal class name (E15,
   E3); the same check is worth running on the remaining routes.

## Gaps

The frontmatter list, in brief: the complaint's window before 07:03:32Z has no
observational substrate on this surface, so the number of affected customers is not
recoverable and the pre-boundary claim is unsupportable rather than refuted; whether that
process start was a first start or an evidence-erasing restart cannot be determined; no
external observation source with longer retention exists within the surface contract;
resources other than peak RSS and uptime are unmeasured, so load-saturation was excluded
on failure signature rather than on contention metrics; and a degradation switch in a
predecessor process remains unfalsifiable.

What was **not** out of reach: the mechanism, the failing input, the determinism of the
failure, the completeness of the catalog, the absence of injected degradation in this
process generation, and process lifecycle within the window. Those are settled on cited
evidence.
