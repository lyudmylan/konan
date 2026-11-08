---
konan_journal: 1
investigation:
  id: 2026-08-19-product-page-zero-stock-500
  trigger: "manual — /konan human adapter. Complaint object: source=human, fingerprint=human-1787142255, labels.alertname=human-report, labels.severity absent (reporter stated none), startsAt=2026-08-19T12:24:15Z, generatorURL absent. Investigation started 2026-08-19T12:24:31Z; trigger latency 16s."
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-19T12:24:31Z
  concluded: 2026-08-19T12:29:33Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{product_id} computes turnover_score = units_ordered / units_in_stock without guarding the divisor, so any product whose stock has reached zero raises an unhandled ZeroDivisionError and returns HTTP 500; catalog item 3 is in that state."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "GET /products/{product_id} raises an unhandled ZeroDivisionError and returns HTTP 500 whenever the requested product's units_in_stock is 0, because the handler divides units_ordered by units_in_stock without a guard; item 3 ('Unobtainium Ingot') has units_in_stock 0, so its product page fails on every request."
    incident_class: software-defect
    state: validated
    evidence_for: [E4, E5, E6, E7, E8, E9, E11]
    evidence_against: []
  - id: H2
    statement: "The 500s are operator-injected degradation (chaos mode or a simulated failure) rather than a code defect."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E8, E11, E15]
  - id: H3
    statement: "The 500s are caused by a process-level fault: a crash/restart loop, memory saturation, or latency collapse."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E7, E12]
  - id: H4
    statement: "The customers who reported 'Internal Server Error' on a product page this morning were hitting the H1 defect."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E4, E6, E11]
    evidence_against: [E10, E14]
  - id: H5
    statement: "The error surface of GET /products/{product_id} violates its published contract: it returns a 500 the OpenAPI document does not declare, and the response body discloses the internal Python exception class."
    incident_class: interfaces
    state: validated
    evidence_for: [E5, E13]
    evidence_against: []
latent_findings:
  - statement: "Undeclared error status plus internal-detail disclosure on GET /products/{product_id}: the OpenAPI document declares only 200 and 422, while the live 500 body names the Python exception class. Real, but separate from the outage mechanism."
    evidence: [E5, E13]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:24:05.632Z"
    quote: |-
      {"ts": "2026-08-19T12:24:05.632Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: probe
    source: "/health, request_id=konan-1787142278-58293"
    quote: |-
      {"status":"ok","uptime_seconds":32.42565762507729}
      -- HTTP 200 in 0.001799s request_id=konan-1787142278-58293
  - id: E3
    type: metric
    source: "/metrics, request_id=konan-1787142281-58299 (baseline, before any investigator product probes)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      faultline_chaos_enabled 0
      process_uptime_seconds 35.58942254213616
      (no http_exceptions_total series emitted)
  - id: E4
    type: probe
    source: "/products, request_id=konan-1787142341-58345"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001438s request_id=konan-1787142341-58345
  - id: E5
    type: probe
    source: "/products/3, request_id=konan-1787142347-58370"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787142347-58370"}
      -- HTTP 500 in 0.009817s request_id=konan-1787142347-58370
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:25:47.841Z"
    quote: |-
      {"ts": "2026-08-19T12:25:47.841Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1787142347-58370", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last): ... File \"<checkout>/src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:25:47.849Z"
    quote: |-
      {"ts": "2026-08-19T12:25:47.849Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787142347-58370", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 9.006, "client": "127.0.0.1:60484"}
  - id: E8
    type: metric
    source: "/metrics, read after investigator product probes"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 9
      http_exceptions_total{type="ZeroDivisionError"} 5
      faultline_chaos_enabled 0
  - id: E9
    type: probe
    source: "/products/4, request_id=konan-1787142350-58381 (control: the other suspicious row, price null)"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
      -- HTTP 200 in 0.001363s request_id=konan-1787142350-58381
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:24:07.463Z – 2026-08-19T12:24:11.744Z (unstamped = real user traffic)"
    quote: |-
      {"ts": "2026-08-19T12:24:07.463Z", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "39e0ef98c279", "status": 200, "duration_ms": 0.615}
      {"ts": "2026-08-19T12:24:08.533Z", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "f84ae7ae1771", "status": 200, "duration_ms": 1.261}
      {"ts": "2026-08-19T12:24:11.744Z", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "f5354e22d90f", "status": 200, "duration_ms": 0.783}
      (no user request to /products/3 appears anywhere in the retained log)
  - id: E11
    type: probe
    source: "/products/{1,2,3,4,5}, repeated probes, request ids listed"
    quote: |-
      /products/3 -> HTTP 500 ZeroDivisionError on 5 of 5 attempts: konan-1787142347-58370, konan-1787142355-58405, konan-1787142355-58417, konan-1787142363-58445, konan-1787142366-58456
      same route, same window, other ids -> HTTP 200: /products/1 konan-1787142355-58399, /products/2 konan-1787142355-58411, /products/4 konan-1787142356-58423, /products/5 konan-1787142356-58429
  - id: E12
    type: metric
    source: "/metrics, three successive reads 12:24:41Z / 12:25:42Z / 12:26:14Z"
    quote: |-
      process_uptime_seconds 35.58942254213616 -> 96.9 -> 129.31505854218267 (monotonic, no reset)
      process_max_rss_bytes 47120384 (identical at all three reads)
      lab/logs/app.log contains exactly one line with "event": "startup"
  - id: E13
    type: probe
    source: "/openapi.json, operation get_product_products__product_id__get"
    quote: |-
      "responses":{"200":{"description":"Successful Response",...},"422":{"description":"Validation Error",...}}
  - id: E14
    type: log
    source: "lab/logs/ and lab/server.out, retention check at 2026-08-19T12:28Z"
    quote: |-
      lab/logs/ contains only app.log — no rotated backups app.log.1–.3.
      Earliest timestamp in lab/logs/app.log and lab/server.out: "ts": "2026-08-19T12:24:05.632Z"
      Lines with "status": 500 across both files: 5; of those, lines without a konan- request id: 0
  - id: E15
    type: log
    source: "lab/logs/app.log, full-file event scan"
    quote: |-
      no line carries event "chaos_enabled", "chaos_disabled", "chaos_failure", or "simulated_exception"
gaps:
  - "No telemetry survives from before 2026-08-19T12:24:05.632Z — the process start marker, with no rotated app.log backups (E14). The complaint's 'this morning' window is entirely unobserved, so user impact could be neither confirmed nor refuted from the target's surface. This is why H4 is inconclusive rather than validated."
  - "No upstream reverse-proxy, load-balancer, or APM access log is inside the surface contract (docs/lab.md), so no user-attributed record of GET /products/3 -> 500 could be sought outside the app's own restarted log."
  - "The target's source is outside the investigator's surface; the throwing expression is known only from the logged stack trace (E6). It could not be confirmed that no other code path divides by a stock-like field."
  - "Only one catalog row currently has units_in_stock == 0 (E4), so the general rule 'every zero-stock product fails' was inferred from the traced expression rather than observed on a second row. A restock of item 3 would hide the symptom without repairing the defect."
  - "Only three triage lenses exist in this repo (software-defect, infra-process, interfaces). The taxonomy classes load-saturation, third-party, and data-db had no dedicated lens; they were covered only incidentally, and load-saturation only by the latency and RSS observations in E12."
usage:
  model: claude-opus-5
  tokens: 1703228
  wall_clock_seconds: 302
---

# Product page 500s: unguarded division by zero stock on GET /products/{product_id}

## Summary

**Root cause identified.** `GET /products/{product_id}` builds its response with
`turnover_score = units_ordered / product["units_in_stock"]` and does not guard the
divisor (E6). Any product whose stock has reached zero therefore raises an unhandled
`ZeroDivisionError` and the request returns HTTP 500. Exactly one catalog row is in that
state today — item 3, "Unobtainium Ingot", `units_in_stock: 0` (E4) — and it fails on
every request: 5 of 5 attempts returned 500, while items 1, 2, 4 and 5 returned 200 in
the same seconds on the same route (E11). Item 4 is the decisive control: it has
`price: null` and `units_ordered: 0` and still serves 200 with `turnover_score: 0.0`
(E9), which removes the null price and the zero numerator and leaves the zero divisor.
Confidence in the mechanism is high — it is read off a traceback, not inferred from
correlation.

**Impact is real but its attribution to this morning is not proven.** Item 3 is a
publicly listed catalog row (E4), so any customer opening that product page hits the
same 500 — the failure needs no unusual input. But every 500 now in telemetry carries a
`konan-` investigator request id, and the log only reaches back to the process start at
12:24:05.632Z with no rotated backups (E14). The reported morning window is entirely
unobserved. The defect is a credible cause of the complaint and is not a demonstrated
one; H4 stays inconclusive. Note also that this is a moving target: a product that sells
out during the day enters the failing state at that moment, which matches the shape of a
complaint that starts mid-morning.

Two families were killed. Chaos/injection: `faultline_chaos_enabled 0` before and after
(E3, E8), no chaos or simulated-exception event anywhere (E15), and the failure selects
on the path parameter rather than on time or probability (E11). Process-level fault:
uptime rose monotonically 35.6 -> 96.9 -> 129.3 with a single startup line (E1, E12),
RSS flat, and the failing request completed in 9.0 ms (E7) against a 1.4 ms baseline —
no crash loop, no saturation, no latency collapse.

## Timeline

- **2026-08-19T12:24:05.632Z** — faultline 0.1.0 process start (E1). This is the
  retention floor: nothing before it survives anywhere (E14).
- **12:24:06.368Z – 12:24:11.744Z** — real user traffic: `/health` x2, `/products`,
  `/products/1`, `/products/2`, `POST /orders` (201), `/orders`, `/products/5` — all
  200/201 (E10). None of it touched `/products/3`, which is why the baseline looked
  clean. That was a sampling gap, not an absence of the defect.
- **12:24:15Z** — complaint raised by the human reporter (`startsAt`).
- **12:24:31Z** — investigation started; trigger latency 16 s.
- **12:24:38Z – 12:24:41Z** — baseline captured: `/health` 200 (E2), `/metrics` clean,
  no exception series, chaos off (E3).
- **12:25:47.841Z** — first `/products/3` probe: unhandled `ZeroDivisionError` at
  `shop.py:64`, HTTP 500 (E6, E7, E5).
- **12:25:47Z – 12:26:16Z** — four further `/products/3` probes, all 500; ids 1, 2, 4, 5
  all 200 (E11). Counters agree: 5 500s, 5 `ZeroDivisionError` (E8).
- **No configuration, deploy, or flag-change marker appears in the observable window**
  (E15) — there is no change event to anchor an onset to, and none could exist given the
  retention floor.

## Investigation

Baseline (step 1) showed a green `/health`, clean counters, and 16 log lines with zero
non-2xx — the healthy-monitoring shape. The business surface had to be checked
separately, and it was.

Triage (step 2) ran three lenses in parallel and blind: software-defect, infra-process,
interfaces. Those are all the lens files this repo has; the absence of a load-saturation,
third-party, or data-db lens is recorded under Gaps rather than papered over. All three
converged on the same signature independently — one route, one input, deterministic,
`ZeroDivisionError` — and all three flagged the same impact caveat unprompted.

Deep-dive (step 3) was skipped deliberately. H1's triage evidence was already
deterministic and complete: a traceback naming the expression, a control row isolating
the divisor, 5-of-5 reproduction, and counter agreement. Deep-dives fill evidence gaps;
re-proving a settled mechanism would have been ceremony. The one genuine gap — user
attribution — is not reachable by more probing, because the evidence that would settle it
was destroyed by the process restart. One targeted check was run instead: `lab/server.out`
and the log directory were scanned for surviving pre-restart history and for any 500
without a `konan-` id. Both came back empty (E14).

Judge (step 4) received the hypothesis list and the verbatim evidence only. It validated
H1 while narrowing its scope honestly (the general zero-stock rule follows from the traced
expression, not from a second observed row), invalidated H2 and H3, validated H5 as
contract drift rather than deliberate breach, and held H4 inconclusive — naming the single
piece of evidence that would settle it: one pre-restart, user-attributed
`GET /products/3 -> 500` record from an upstream proxy, APM trace, or a request id from a
customer's own error page.

## Hypotheses

### H1 — unguarded division by zero stock (validated)

The mechanism is observed, not inferred. E6 puts the fault at
`"turnover_score": units_ordered / product["units_in_stock"]` in `shop.py:64`; the
divisor is the stock field itself. E4 shows item 3 at `units_in_stock: 0`. E11 shows 5
of 5 failures on that id and 200s on every other id on the same route in the same window.
E8 shows the counters agree exactly: 5 500s on the route template, 5
`ZeroDivisionError`. E9 is the control that kills the two rival input theories — item 4
carries `price: null` and `units_ordered: 0` and still serves 200. No evidence against
was found. Scope limit, stated plainly: the determinism is proven for item 3 in one
process lifetime; the general rule rests on the arithmetic in the traced expression.

### H2 — injected chaos or operator-induced failure (invalidated)

`faultline_chaos_enabled` reads 0 both before and after the failures (E3, E8), and no
`chaos_enabled`, `chaos_disabled`, `chaos_failure`, or `simulated_exception` event exists
in the log (E15). The decisive point is not the flag but the selectivity: injected
degradation is time-scoped or probabilistic, whereas this failure binds to one path
parameter and never interleaves with success on that input (E11).

### H3 — process-level fault: crash loop, saturation, latency collapse (invalidated)

`process_uptime_seconds` rose monotonically across three reads with no reset, and the log
holds exactly one `startup` line (E1, E12) — no restart. RSS was byte-identical at all
three reads (E12); the judge rightly discounted that as possibly a single sample, so the
refutation rests on the uptime and the startup count. The failing request took 9.0 ms
(E7) against a 1.4–1.8 ms baseline (E2, E4) — exception-handling cost, not a hang. A
`ZeroDivisionError` traceback is an application-logic fault, not an OOM kill.

### H4 — the morning reports were this defect (inconclusive)

The defect is real and customer-reachable: item 3 is publicly listed (E4) and fails
deterministically (E11), so no unusual input is needed to hit it. That makes it a credible
cause. It does not make it a demonstrated one. Every 500 in evidence is `konan-` traffic
(E11) — the investigator's own probes cannot establish user impact. E10 shows the only
real user traffic in the retained log went to items 1, 2 and 5, all 200, and never touched
item 3. But E14 sets the retention floor at the same second the process started, with no
rotated backups, so that clean user record covers roughly six seconds of this morning, not
the morning. Absence of user 500s here is absence of evidence, not evidence of absence.
Both directions fail, so the verdict stands at inconclusive for the attribution while the
root cause itself is validated.

### H5 — undeclared 500 and internal-detail disclosure (validated)

The OpenAPI operation `get_product_products__product_id__get` declares only 200 and 422
(E13), while the live response is a 500 whose body carries
`"exception_type":"ZeroDivisionError"` (E5). Both halves are directly observed. Two
qualifications: an undeclared 500 is the default of framework-generated OpenAPI, so this
is contract drift rather than a broken promise; and the leak is bounded — the class name
reaches the client, while the file, line, and stack stay server-side (E6), and the body
does return a stable `request_id`. Recorded as a latent finding: real, separate from the
outage mechanism.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

1. **Settle H4 where the evidence still lives.** Look for a pre-restart, user-attributed
   `GET /products/3 -> 500` — an upstream reverse-proxy or load-balancer access log, an
   APM trace, or the `request_id` printed on a customer's own error page — timestamped
   inside the reported morning window and lacking the `konan-` prefix. The proxy access
   log is the most likely place to have survived the app restart. None of these are inside
   the current surface contract, so this needs a human with wider access.
2. **Ask the reporter for specifics.** Which product page, and roughly what time? If the
   answer is "Unobtainium Ingot", H4 closes immediately. Support ticket text and any
   screenshot of the error page may carry the request id.
3. **Check the catalog for other zero-stock rows on the next read.** Item 3 is the only
   one now (E4), but the failing condition is a state, not an identity — any product that
   sells out enters it. Re-reading `/products` periodically shows the blast radius as it
   moves.
4. **Fix the retention gap before the next incident.** The whole attribution question was
   lost to a process restart with no rotated backups (E14). Log retention that survives a
   restart is the difference between "credible cause" and "proven cause" on the next
   investigation.

## Gaps

- **The morning is unobserved.** Nothing survives from before 12:24:05.632Z — the
  process start — and there are no rotated `app.log` backups (E14). The complaint's whole
  window is outside the evidence. This is the single reason H4 is inconclusive.
- **No upstream telemetry in the contract.** `docs/lab.md` grants the app's own logs,
  metrics, and GET probes; it grants no proxy log, no APM, no tracing backend. The one
  place a surviving user-attributed 500 could live is out of reach.
- **Source is out of reach.** The throwing expression is known only from the logged stack
  (E6). Whether any other handler divides by a stock-like field could not be checked.
- **One zero-stock row only.** The general rule was inferred from the traced arithmetic,
  not observed on a second row (E4). A restock of item 3 would hide the symptom while the
  defect remains.
- **Three lenses, six taxonomy classes.** Only software-defect, infra-process, and
  interfaces lenses exist here. load-saturation, third-party, and data-db had no dedicated
  lens; load-saturation was touched only by the latency and RSS observations in E12, and
  the other two not at all. Those are accepted blind spots, not cleared domains.
