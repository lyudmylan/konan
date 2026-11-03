---
konan_journal: 2
investigation:
  id: 2026-11-03-product-page-500s
  trigger: "manual — /konan human adapter (docs/triggers.md, human profile). Complaint object: source=human, fingerprint=human-1793690005, labels.alertname=human-report, no severity stated by the reporter, startsAt=2026-11-03T07:13:25Z. Investigation entered the loop at 2026-11-03T07:13:46Z — trigger latency 21s."
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-11-03T07:13:46Z
  concluded: 2026-11-03T07:23:42Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: inconclusive
hypotheses:
  - id: H1
    statement: "The product detail handler computes turnover_score as units_ordered divided by the product's own units_in_stock, with no guard for zero, so the route raises ZeroDivisionError and returns HTTP 500 for any catalog row whose units_in_stock is 0 — today exactly one row, product id 3."
    incident_class: software-defect
    state: validated
    evidence_for: [E5, E6, E7, E8, E9, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "A process lifecycle event — crash, restart loop, or hang — or resource saturation produced the reported Internal Server Errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E13, E14, E15]
  - id: H3
    statement: "An internal operational degradation switch (chaos mode, kill switch, or feature flag) injected the errors into the product page."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E3, E6, E10, E13]
  - id: H4
    statement: "A gateway or proxy tier in front of the target failed on its own, or a boundary contract mismatch produced the 500s rather than the target's own code."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E8, E9, E12]
  - id: H5
    statement: "The customers described in the complaint actually hit H1's mechanism this morning — the impact claim, judged separately from the mechanism."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E5, E6, E9]
    evidence_against: [E3, E4, E12]
latent_findings:
  - statement: "The product detail route returns HTTP 500 for any product whose units_in_stock is 0. The defect is live in the running process and reachable by ordinary customers — product id 3 ships in the public /products listing — but every HTTP 500 in the entire record carries an investigator konan-* request id, so no customer has been observed hitting it."
    evidence: [E5, E6, E9, E12]
  - statement: "The HTTP 500 response body returns the internal Python exception class name to the caller, across the trust boundary."
    evidence: [E6]
  - statement: "Product id 4 serves price: null while every sibling row serves a number; on the read path the route still returns HTTP 200, so this is a data-quality flag and not an observed failure."
    evidence: [E5, E10]
evidence:
  - id: E1
    type: probe
    source: "GET /health @ 2026-11-03T07:13:51.784Z, request_id konan-1793690031-22197"
    quote: |-
      {"status":"ok","uptime_seconds":42.99736695783213}
      -- HTTP 200 in 0.001847s request_id=konan-1793690031-22197
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:13:08.798Z (the first line of the file)"
    quote: |-
      {"ts": "2026-11-03T07:13:08.798Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E3
    type: metric
    source: "GET /metrics @ 2026-11-03T07:13:58.439Z, request_id konan-1793690038-22205 (trimmed to the request, exception, chaos and uptime families)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 1
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      faultline_chaos_enabled 0
      process_uptime_seconds 49.65197949996218
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:13:10.615Z–07:13:14.843Z — every product-page request made by user traffic (unstamped request ids)"
    quote: |-
      {"ts": "2026-11-03T07:13:10.615Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "c6fc37b7db0e", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.024, "client": "127.0.0.1:64641"}
      {"ts": "2026-11-03T07:13:11.672Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "2c6dc6f4dcf5", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.887, "client": "127.0.0.1:64642"}
      {"ts": "2026-11-03T07:13:14.843Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 200", "request_id": "92b7b8b683c5", "event": "request", "method": "GET", "path": "/products/5", "status": 200, "duration_ms": 0.782, "client": "127.0.0.1:64645"}
  - id: E5
    type: probe
    source: "GET /products @ 2026-11-03T07:14:33.971Z, request_id konan-1793690073-22238"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.002040s request_id=konan-1793690073-22238
  - id: E6
    type: probe
    source: "GET /products/3 @ 2026-11-03T07:17:52.932Z, request_id konan-1793690272-22376 (the fourth of four attempts on this path, all identical)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793690272-22376"}
      -- HTTP 500 in 0.004354s request_id=konan-1793690272-22376
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:15:39.294Z (the stack field is trimmed here and quoted separately as E9; kept fields unaltered)"
    quote: |-
      {"ts": "2026-11-03T07:15:39.294Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793690139-22289", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "..."}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:15:39.302Z — the access line paired with E7, showing the application itself emitted the status"
    quote: |-
      {"ts": "2026-11-03T07:15:39.302Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1793690139-22289", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 8.537, "client": "127.0.0.1:64680"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:15:39.294Z — the last frame of the stack field of E7. Absolute filesystem paths are removed per the repo's private-material rule; the code text is unaltered."
    quote: |-
      File ".../faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
                            ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
      ZeroDivisionError: division by zero
  - id: E10
    type: probe
    source: "GET /products/4 @ 2026-11-03T07:15:54.875Z, request_id konan-1793690154-22310 — control: the same route with non-zero stock"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T07:16:07.480Z — control: an unknown id on the same route, handled deliberately"
    quote: |-
      {"ts": "2026-11-03T07:16:07.480Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/99 -> 404", "request_id": "konan-1793690167-22320", "event": "request", "method": "GET", "path": "/products/99", "status": 404, "duration_ms": 0.383, "client": "127.0.0.1:64686"}
  - id: E12
    type: metric
    source: "GET /metrics @ 2026-11-03T07:23:32Z, request_id konan-1793690612-22469 — the complete http_requests_total family at conclusion"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 4
      http_requests_total{method="GET",path="/metrics",status="200"} 4
      http_requests_total{method="GET",path="/openapi.json",status="200"} 2
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/orders/{order_id}",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 2
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/{product_id}",status="404"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_requests_total{method="POST",path="/orders",status="201"} 1
  - id: E13
    type: metric
    source: "GET /metrics @ 2026-11-03T07:23:32Z, request_id konan-1793690612-22469 — exception, chaos, uptime and memory families"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 4
      faultline_chaos_enabled 0
      process_uptime_seconds 624.0141403328162
      process_max_rss_bytes 46399488
  - id: E14
    type: metric
    source: "process uptime across three readings (konan-1793690031-22197 @ 07:13:51.784Z, konan-1793690143-22299 @ 07:15:43.384Z, konan-1793690201-22354 @ 07:16:41.031Z), against the log inventory of lab/logs/"
    quote: |-
      "uptime_seconds":42.99736695783213
      process_uptime_seconds 154.63913258281536
      "uptime_seconds":212.28760754084215
  - id: E15
    type: log
    source: "lab/server.out — the first log line of the server's stdout, the only other telemetry file named by the surface contract"
    quote: |-
      {"ts": "2026-11-03T07:13:08.798Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [22115]", "color_message": "Started server process [\u001b[36m%d\u001b[0m]"}
gaps:
  - "No telemetry of any kind exists before the process start at 2026-11-03T07:13:08.798Z. lab/logs/ holds only app.log with no .1–.3 rotation backups, and lab/server.out begins at the same instant (E2, E14, E15). The complaint's window — 'this morning' — lies entirely outside the record, so customer impact can be neither confirmed nor refuted. This is a cold-start coverage gap, not evidence destroyed by a restart: a restart would have left a second startup line or a rotation backup, and neither exists."
  - "Only one catalog row has units_in_stock == 0, so H1's generalization to 'any zero-stock product' is read off the quoted expression in E9 and tested on a single row (id 3)."
  - "The stock value of product 3, and the deployed state of the code at the line in E9, are unknown for the complaint's window. The catalog was first observed at 07:14:33.971Z (E5)."
  - "Support's 'several customers' could not be corroborated at all: the complaint carried no ticket ids, no timestamps and no user request ids, and the trigger surface supplies none. Neither the count nor a single instance is backed by a record."
  - "Three classes of the taxonomy have no lens file in this repo — load-saturation, third-party and data-db — so those domains were covered only incidentally by the three lenses that do exist. Per docs/lab.md faultline has no database and no third-party dependency, which narrows but does not eliminate the blind spot."
  - "Write paths were not exercised: scripts/probe.sh is GET-only, so the effect of product 4's null price on order creation is untested."
  - "No edge, proxy or load-balancer tier is attested either way. The surface contract names only app.log and server.out, so an upstream tier's own access log — the place a customer-side 500 for the morning would survive — is outside reach."
usage:
  model: claude-opus-5
  tokens: 2721666
  wall_clock_seconds: 596
---

# Product page 500s — a confirmed zero-stock division defect, with customer impact unprovable

## Summary

**Verdict: inconclusive at the incident level, with a validated defect attached.** The
investigation found, and proved to the line of code, a deterministic mechanism that
produces exactly the reported symptom: the product detail route divides `units_ordered`
by the product's own `units_in_stock` without guarding zero, so every request for a
zero-stock product returns HTTP 500 with `ZeroDivisionError` (E9, E6). Today exactly one
catalog row qualifies — id 3, `"Unobtainium Ingot"`, `"units_in_stock":0` (E5) — so one
of five product pages is dead, and any product that sells out joins it. Two controls bound
the finding: the same route serves id 4 with non-zero stock at HTTP 200 (E10), and an
unknown id returns a clean 404 (E11), so the route is not failing wholesale.

**What cannot be claimed is that any customer was affected.** All four HTTP 500s in the
entire record carry an investigator `konan-*` request id, and the counters close exactly:
`/products/{product_id}` shows 200×5, 404×1, 500×4 (E12), which decomposes into three user
requests (ids 1, 2, 5 — all 200, E4), two investigator probes of id 4, four investigator
probes of id 3, and one investigator probe of id 99. `http_exceptions_total{type="ZeroDivisionError"} 4`
is the only exception series in existence (E13). No unstamped 5xx appears anywhere.

**The reason that is not reassuring** is the coverage gap, and it is the honest centre of
this report. Every byte of telemetry in the surface begins at the process start,
`07:13:08.798Z` (E2, E15) — roughly four minutes before the complaint arrived. There are no
rotation backups and no prior process generation, so the morning the complaint describes has
no telemetry at all. Absence of recorded customer errors there is absence of evidence, not
evidence of absence. The defect is simultaneously **unproven as the morning's incident** and
**live and user-reachable right now**: id 3 ships in the public `/products` listing (E5), so
any customer who opens that row gets the 500 of E6.

Confidence: **high** on the mechanism (reproduced 4 of 4, located to one expression,
double-counted in metrics, three competing families refuted). **None** on the link to the
reported customers — not refuted either, simply unobservable on this surface.

## Timeline

- `2026-11-03T07:13:08.798Z` — process start; `faultline 0.1.0 started` (E2). Server stdout
  begins at the same instant (E15). **Everything before this moment is unobservable.**
- `07:13:09Z–07:13:14Z` — the only user traffic in the record. Product pages for ids 1, 2
  and 5 all return HTTP 200 (E4); a POST /orders returns 201. No user request touches id 3.
- `07:13:25Z` — complaint raised by a human reporter (`startsAt`).
- `07:13:46Z` — investigation enters the loop; trigger latency 21s.
- `07:13:51Z` — baseline: `/health` 200, uptime 43s (E1).
- `07:13:58Z` — baseline metrics: every series 2xx, `http_exceptions_total` carries no
  series at all, `faultline_chaos_enabled 0` (E3).
- `07:14:33Z` — catalog read; id 3 observed at `"units_in_stock":0`, id 4 at `"price":null` (E5).
- `07:15:39Z` — first HTTP 500 of the entire record, from an investigator probe of
  `/products/3`: `ZeroDivisionError` (E7, E8).
- `07:16:07Z` — control: `/products/99` returns a clean 404 (E11).
- `07:17:52Z` — the failure reproduced a fourth time, same body, same class (E6).
- `07:23:32Z` — closing metrics: 500×4 on the product route, all investigator-attributed;
  uptime 624s unbroken; chaos still 0 (E12, E13).

No configuration-change, deploy, flag-change or chaos marker appears anywhere in the
record — `app.log` contains no `chaos_enabled`, `chaos_disabled` or `chaos_failure` event,
and `faultline_chaos_enabled` read 0 at every scrape (E3, E13).

## Investigation

**Baseline** established health, a metrics snapshot and the full log tail, and immediately
surfaced the fact that shaped everything after it: uptime of 43s with a log whose first line
is this generation's startup marker. Metrics are in-process counters, so they can never
describe an earlier generation; the logs would have survived a restart, and there are none.

**Triage** fanned out three lenses in parallel — software-defect, infra-process and
interfaces — each blind to the others, each given only its lens file, the surface contract,
the verbatim complaint and the baseline. The three classes of the taxonomy without a lens
file in this repo are recorded under Gaps rather than silently skipped.

- *software-defect* located the division to one expression via the logged stack and bounded
  it with the id-4 and id-99 controls.
- *infra-process* ruled out its whole family in-window — monotonic uptime across three
  readings matching wall clock, one startup line, flat RSS, chaos off — and, more usefully,
  established that the pre-start blind spot is a cold start rather than erased evidence.
- *interfaces* found no gateway-tier statuses and traced the 500 to the target's own handler,
  pointing away from its own domain; it also noted the declared contract omits any 500 and
  the error body leaks the exception class.

**Deep-dive was deliberately not run.** H1's triage evidence was already deterministic and
complete, and H2–H4 were already refuted with citations; the skill routes such hypotheses
straight to the judge rather than re-proving them. The one real evidence gap — customer
impact in the morning window — is unfillable on this surface, so spawning an agent at it
would have been coverage theater. I did re-probe `/products/3` and re-scrape `/metrics`
myself so the reproduction and the impact reconciliation are first-hand, and I read the
complete log rather than relying on the lenses' excerpts.

**The judge** received only the hypothesis list and the verbatim ledger. It validated H1,
invalidated H2, H3 and H4 in-window, and ruled H5 — the impact claim, which I split from the
mechanism precisely so it could be judged on its own — inconclusive, noting that both the
"for" and "against" lists as offered were overstated. It independently reconciled the probe
ids against the counters and argued the strongest case for `root-cause-identified` before
rejecting it.

## Hypotheses

### H1 — unguarded division on the product detail route — **validated**

The throwing frame is quoted in the telemetry itself (E9):
`"turnover_score": units_ordered / product["units_in_stock"],` raising
`ZeroDivisionError: division by zero`. Id 3 is the only catalog row with `"units_in_stock":0`
(E5), and `/products/3` returned HTTP 500 on 4 of 4 attempts (E6). E10 is a true control —
same route, non-zero stock, HTTP 200, `"turnover_score":0.0` — so the handler is healthy for
other inputs; E11 is a second — an unknown id gets a deliberate 404, so the route has a
working error path and the arithmetic failure is simply not on it. E8 shows the application
itself logging the status, and E12/E13 tie the status counter to the exception counter.

One scope limit, stated rather than hidden: the generalization to "any zero-stock product"
is read off the expression and tested on one row. Note also that id 4 shows
`"units_ordered":0`, so for id 3 the expression is plausibly `0/0` — which raises just the
same. H1 proves a mechanism; it proves no impact. That is H5.

### H2 — process lifecycle or resource saturation — **invalidated** (in-window)

No evidence was offered for it and five items refute it: uptime monotonic across three
readings, 112s elapsed against a 111.642s uptime delta and then 58s against 57.649s, with a
back-computed start equal to E2 (E14); exactly one startup line and no rotation backups
(E2, E14); `process_max_rss_bytes` flat at 46399488 (E13); `/health` 200 on every probe (E1);
one `Started server process` in stdout (E15). The 500 itself cost 8.537ms and uptime
continued unbroken through it — no worker lost, no hang. What would settle the residual: the
previous generation's record, a rotated `app.log` or a host restart history covering the
morning.

### H3 — internal degradation switch — **invalidated** (in-window)

`faultline_chaos_enabled 0` at three separate scrapes (E3, E13) and no chaos event on any log
line. The signature is also wrong for injection: 4 of 4 on one input with 200s on the others
(E6, E10) is per-input determinism, not a probabilistic fraction. What would settle the
residual: the switch state or a flag-change audit trail covering the morning.

### H4 — gateway tier or boundary contract — **invalidated**

The complete status family at conclusion contains only 200, 201, 404 and 500 — no 502, 503 or
504 anywhere (E12). E9 places the fault inside the target's own handler frame, and E8 shows
the application emitting the status itself with its own duration, so no intermediary
synthesized it. What would settle the remainder: edge/proxy access logs, or confirmation that
no such tier fronts the target; the surface contract names none.

### H5 — the impact claim — **inconclusive**

Separated from H1 on purpose. For: the symptom string, the surface and the determinism match
the complaint exactly (E5, E6, E9), and the defect is reachable from the public listing.
Against: every 500 and every exception on record is investigator-stamped, the counters leave
no room for an unattributed one, and the only user product-page requests returned 200 (E3,
E4, E12). Neither list settles it, because the complaint concerns a window with no telemetry
(E2, E14, E15); and the in-record user sample is five requests over about five seconds, which
cannot speak for a morning of traffic either way.

Were the morning's telemetry ever to confirm impact, the mechanism id under this contract
would be `unhandled-exception` in class `software-defect`: the trigger is a data value, but
the fault is the missing guard, and zero stock is a legal business state rather than corrupt
data — the route serves id 4's `null` price at 200 (E10) and handles missing ids at 404 (E11),
so it is the arithmetic that lacks a path, not the data that is wrong. That reasoning is
recorded here deliberately and **not** in the machine core, because this verdict claims no
root cause.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

1. **Ask support for the specifics the complaint lacked** — ticket timestamps, the product
   pages customers opened, and any request ids from the error pages. One zero-stock product
   id in a ticket, or one timestamp inside a surviving log window, converts H5 immediately.
   This is the cheapest decisive step by a wide margin.
2. **Retrieve the morning's telemetry from outside this surface** if it exists anywhere — a
   log shipper, an APM, an upstream proxy's access log, or the host's process-restart
   history for roughly 06:00Z–07:13:08.798Z. The named gap is an artifact of this surface,
   not necessarily of the system.
3. **Check whether log retention survives a restart in the real deployment.** A target whose
   entire error history begins at process start cannot support a morning-after investigation.
   That is the finding most likely to recur beyond this incident.
4. **Re-read the catalog for zero-stock rows** before assuming the blast radius is one page.
   Any product reaching `units_in_stock: 0` becomes a dead page by E9's mechanism, so the
   radius tracks inventory, not code changes.
5. **Review the error envelope** — the 500 body returns the internal exception class to the
   caller (E6), and the declared contract documents no 500 response at all.

## Gaps

The frontmatter list, elaborated. The load-bearing one is the first.

- **The morning has no telemetry.** Everything in the surface starts at `07:13:08.798Z`
  (E2, E15), with no rotation backups and no prior generation (E14). This is positively a
  cold start, not a restart that erased data — a restart would have appended a second startup
  line or left a backup. But the consequence is the same: the window the complaint describes
  cannot be examined, and no verdict about customer impact is available from here. I did
  check the one remaining file in the contract, `lab/server.out`, specifically to close this
  rather than assert it (E15).
- **"Several customers" is uncorroborated in every respect** — no count, no instance, no
  ticket id, no timestamp, no user request id. The complaint is a claim, and the trigger
  profile carried nothing with which to test it.
- **H1 is generalized from one row.** Exactly one product has zero stock today, so the
  "any zero-stock product" reading rests on the quoted expression rather than on a second
  observed instance.
- **The morning's code and data state are unknown.** The catalog was first read at
  `07:14:33.971Z`; nothing establishes id 3's stock, or the deployed code at that line,
  earlier.
- **Three taxonomy classes have no lens** in this repo (load-saturation, third-party,
  data-db), so those domains were covered only incidentally. `docs/lab.md` records that
  faultline has no database and no third-party dependency, which narrows the blind spot
  without removing it.
- **Write paths untested** — the probe surface is GET-only, so product 4's `null` price was
  never exercised through order creation.
- **No edge tier is attested either way**, so the one place a customer-side 500 from the
  morning would plausibly survive is outside the surface contract entirely.
