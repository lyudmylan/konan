---
konan_journal: 2
investigation:
  id: 2026-11-02-products-3-zero-stock-500s
  trigger: "manual — /konan human report. Complaint object: source=human, fingerprint=human-1793662432, labels.alertname=human-report, no severity stated by the reporter (never inferred), startsAt=2026-11-02T23:33:52Z. Investigation started 2026-11-02T23:34:10Z; trigger latency 18s."
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-02T23:34:10Z
  concluded: 2026-11-02T23:43:01Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/3 returns HTTP 500 because the product handler computes the derived field turnover_score by dividing units_ordered by the product's units_in_stock, which is 0 for that product, raising a ZeroDivisionError that escapes the handler unhandled."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "The product-detail handler divides by the product's units_in_stock to compute turnover_score; for product 3 that value is 0, so every request for that id raises ZeroDivisionError and returns 500, while every other id succeeds."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E14, E16]
    evidence_against: []
  - id: H2
    statement: "An internal operational switch inside the target (chaos, kill switch, feature flag) is injecting the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E6, E9, E10]
  - id: H3
    statement: "A process lifecycle event — crash, restart, or hang — produced the errors."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E11, E12, E7, E13]
  - id: H4
    statement: "A proxy, gateway, or load-balancer tier, or an upstream dependency boundary, is failing for that one page."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E2, E6, E8]
  - id: H5
    statement: "Demand exceeded capacity and the 500s are a saturation symptom."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E7, E6, E8]
  - id: H6
    statement: "A stock-depletion data change inside the observable window drove product 3's units_in_stock to 0 and began the errors."
    incident_class: data-db
    state: invalidated
    evidence_for: []
    evidence_against: [E14, E15]
  - id: H7
    statement: "Product 3's units_in_stock of 0 arrived by a data change before the start of retained telemetry, rather than being the seeded initial value — i.e. the defect has a datable onset that this surface cannot see."
    incident_class: data-db
    state: inconclusive
    evidence_for: [E5]
    evidence_against: [E15]
latent_findings:
  - statement: "The 500 response body returns the internal Python exception class name to the caller, an information-disclosure and error-contract defect independent of the division bug."
    evidence: [E4]
  - statement: "The API description declares only 200 and 422 for the product-detail path and no 5xx at all, so clients have no declared shape for the error this route actually returns — contract drift."
    evidence: [E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:33:38.191Z (request_id 9b62b4f06d5d)"
    quote: '{"ts": "2026-11-02T23:33:38.191Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "9b62b4f06d5d", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 10.798, "client": "127.0.0.1:62417"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:33:38.181Z (request_id 9b62b4f06d5d; stack trimmed to its final frames, kept fields unaltered)"
    quote: '{"ts": "2026-11-02T23:33:38.181Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "… shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:33:39.258Z, 23:33:42.379Z, 23:33:44.473Z (three further access lines, same path)"
    quote: '"message": "GET /products/3 -> 500", "request_id": "bc79ee842b83" … "message": "GET /products/3 -> 500", "request_id": "997a8db9d40c" … "message": "GET /products/3 -> 500", "request_id": "53edae111ebb" — each preceded by an "event": "unhandled_exception" line with "exception_type": "ZeroDivisionError"'
  - id: E4
    type: probe
    source: "/products/3 (request_id konan-1793662545-11375)"
    quote: 'HTTP 500 — {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793662545-11375"}'
  - id: E5
    type: probe
    source: "/products (request_id konan-1793662689-11476)"
    quote: 'HTTP 200 — [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E6
    type: probe
    source: "/products/4 (request_id konan-1793662558-11404)"
    quote: 'HTTP 200 — {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:33:33.015Z, 23:33:34.062Z, 23:33:41.312Z"
    quote: '"message": "GET /products/1 -> 200" … "duration_ms": 1.713, "request_id": "2b03980b8e87" … "message": "GET /products/2 -> 200" … "duration_ms": 0.665, "request_id": "e42e3730f5a4" … "message": "GET /products/2 -> 200" … "duration_ms": 0.773, "request_id": "8ae613cb320d"'
  - id: E8
    type: metric
    source: "/metrics (request_id konan-1793662462-11274) — the baseline read, taken before any investigator probe of /products/3"
    quote: 'http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4 / http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3 / http_requests_total{method="GET",path="/products",status="200"} 1 / http_requests_total{method="POST",path="/orders",status="201"} 2 / http_exceptions_total{type="ZeroDivisionError"} 4'
  - id: E9
    type: metric
    source: "/metrics (request_ids konan-1793662462-11274 and konan-1793662552-11392)"
    quote: 'faultline_chaos_enabled 0 (both reads)'
  - id: E10
    type: log
    source: "lab/logs/app.log, whole file (25 lines at baseline, 27 later) — absence check"
    quote: 'No line carries "event": "chaos_enabled", "chaos_disabled", "chaos_failure", or "simulated_exception"'
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:33:31.006Z"
    quote: '{"ts": "2026-11-02T23:33:31.006Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"} — the only startup event in the file; no shutdown and no second startup line'
  - id: E12
    type: probe
    source: "/health (request_id konan-1793662584-11438) plus the uptime series across four reads"
    quote: 'HTTP 200 — {"status":"ok","uptime_seconds":173.73136145900935}; the series 39.67851445893757, 51.79, 141.17188304197043, 173.73136145900935 is monotonic and every value implies process start at 2026-11-02T23:33:31Z'
  - id: E13
    type: metric
    source: "/metrics (request_id konan-1793662552-11392)"
    quote: 'http_request_duration_seconds_sum{method="GET",path="/products/{product_id}"} 0.033498791279271245 over _count 8 (4.19 ms mean); process_max_rss_bytes 48005120, identical to the value read 90 s earlier'
  - id: E14
    type: probe
    source: "/orders (request_id konan-1793662651-11457)"
    quote: 'HTTP 200 — [{"id":1,"product_id":1,"quantity":2,"total_price":99.0,"created_at":"2026-11-02T23:33:36.124+00:00"},{"id":2,"product_id":2,"quantity":1,"total_price":23.0,"created_at":"2026-11-02T23:33:43.417+00:00"}]'
  - id: E15
    type: log
    source: "lab/logs/app.log and lab/logs/ directory listing — retention check"
    quote: 'The file begins at "ts": "2026-11-02T23:33:31.006Z"; lab/logs/ contains only app.log, with no rotated .1–.3 backups. The first request naming id 3 anywhere in the record is already a 500, at 23:33:38.181Z — 7.2 s after startup.'
  - id: E16
    type: probe
    source: "/openapi.json (request_id konan-1793662571-11433)"
    quote: 'For path /products/{product_id} the declared responses are "responses":{"200":{...},"422":{...}} — no 5xx declared'
gaps:
  - "No telemetry exists before 2026-11-02T23:33:31.006Z: the log opens at the startup line and lab/logs/ holds no rotated backups (E15). The hour the complaint names is therefore unobservable, there is no last-known-good for /products/3, and the onset cannot be dated."
  - "The target's source is outside the investigator's surface by contract, so 'the division is unguarded' is established from the raising expression in the traceback (E2), not from reading the handler."
  - "Whether product 3's units_in_stock of 0 is the seeded initial value or the result of a write is unobservable — the surface carries no write or audit record (H7)."
  - "The reporter's 'no deploys that we know of' can be neither confirmed nor refuted: the only version signal is the startup line's faultline 0.1.0 (E11), with no earlier startup to compare against."
  - "A process start did occur inside the complaint's hour — uptime was 173.7 s at the last read (E12). H3 refutes a lifecycle event as the cause, not a recent start; the benign reading is that the lab target was started for this session, but the record cannot distinguish that from an earlier restart whose logs are gone."
  - "/metrics exposes no concurrency, queue, or connection series, so saturation (H5) is unmeasured on those dimensions rather than measured-and-clean; H5 was killed by determinism and by total volume, not by a queue reading."
  - "Product id 5 was never probed; 'only id 3 fails' rests on ids 1, 2 and 4 succeeding (E6, E7) plus id 3 being the catalog's only zero-stock row (E5)."
  - "All client addresses in the lab are loopback (E1), so the four failures are attributable to non-investigator traffic but not demonstrably to real end users."
  - "This repo ships triage lenses for software-defect, infra-process and interfaces only. load-saturation and data-db were tested by the orchestrator against metrics and probes rather than by a dedicated lens, and third-party was excluded only by the absence of any external-call signal on the surface."
usage:
  model: claude-opus-5
  tokens: 2560299
  wall_clock_seconds: 531
---

# /products/3 returns 500 on every request: zero-stock divisor in the product-detail handler

## Summary

**Root cause identified.** The product-detail route raises an unhandled `ZeroDivisionError`
for one product. The handler computes a derived field, `turnover_score`, as
`units_ordered / product["units_in_stock"]` (E2). Product 3 — "Unobtainium Ingot" — is the
only row in the catalog whose `units_in_stock` is `0` (E5), so every request for that id
divides by zero and returns HTTP 500, while every other id returns 200 (E6, E7). The
failure is deterministic per input, which is why the reporter's customers still see the
error when they refresh: every attempt on that id in the record failed — four from
non-investigator traffic (E1, E3) plus the read-only reproduction (E4) — with no success
at any point.

This matches the complaint's shape exactly — one product page errors, other pages load
fine. The impact is confined to the detail page of a single sold-out product; the catalog
listing, the other product pages, order creation and `/health` were all healthy throughout
(E8). Nothing suggests a deploy, a toggle, or infrastructure: the internal degradation
switch is off (E9), no switch event appears anywhere in the record (E10), one process has
run unbroken since 23:33:31Z (E11, E12), and resource and latency readings are flat (E13).

Confidence in the mechanism is high — the traceback names the throwing expression, and a
read-only probe reproduced the 500 on the first attempt (E4). Confidence in the **onset**
is low, and that limit is real: the retained log covers about three minutes, so the
investigation cannot date when this began or confirm the "within the last hour" framing.
A notable second-order effect: the catalog endpoint advertises product 3 at HTTP 200
(E5) while its detail page is completely unservable, so the broken page is reachable from
a healthy listing.

## Timeline

- **2026-11-02T23:33:31.006Z** — process start, `faultline 0.1.0` (E11). No telemetry of any
  kind exists before this instant (E15).
- **23:33:33.015Z – 23:33:34.062Z** — `/products/1` and `/products/2` → 200 (E7).
- **23:33:36.124Z** — order 1 created for product 1 (E14).
- **23:33:38.181Z** — first observed failure: `ZeroDivisionError` at the `turnover_score`
  expression, request `9b62b4f06d5d` (E2), returned as `GET /products/3 -> 500` 10 ms later
  (E1). This is the *first* request naming id 3 anywhere in the record — there is no
  error-free period for it to regress from (E15).
- **23:33:39.258Z, 23:33:42.379Z, 23:33:44.473Z** — three further `/products/3` → 500 from
  unstamped, non-investigator traffic (E3). A `/products/2` → 200 interleaves at
  23:33:41.312Z (E7), between two of the failures — the failure is input-selective, not
  time-sliced.
- **23:33:43.417Z** — order 2 created for product 2 (E14). No order ever touched product 3.
- **23:34:10.673Z** — investigation begins; `/health` → 200.
- **23:34:22.787Z** — baseline metrics: 4 × 500 and 4 × `ZeroDivisionError` (E8), read
  *before* any investigator probe of the failing route. This ordering is what fixes the four
  failures as non-investigator traffic rather than self-inflicted.
- **23:35:45.111Z** — a read-only investigator probe reproduces the 500 (E4).
- **No configuration, deploy, or flag-change marker appears anywhere in the record** (E10, E11).

## Investigation

**Baseline.** `/health` returned 200 with `status: ok` while the business surface was
already failing — the healthy-monitoring shape the loop warns about, so the business
endpoints were checked directly rather than inferred from health. The baseline metrics read
(E8) captured the counter state before any investigator probe touched `/products/{id}`,
which later proved decisive for attribution.

**Triage.** All three lenses this repo ships were spawned in parallel, each blind to the
others: software-defect, infra-process, interfaces. None could be excluded up front — the
complaint named a symptom, not a mechanism.

- *software-defect* found the deterministic per-input failure, named the throwing expression
  from the traceback, and identified `units_in_stock: 0` as the sole discriminator between
  the failing and succeeding inputs.
- *infra-process* reported its domain clear on all three counts: no lifecycle anomaly
  (single startup marker, monotonic uptime across four reads), no saturation (flat peak RSS,
  flat latency mean), no active internal switch.
- *interfaces* confirmed the split was by path parameter with zero interleaving, found no
  gateway-shaped status anywhere, and surfaced the undeclared-5xx contract drift (E16).

**Deep-dive: deliberately skipped.** The loop's rule is that a hypothesis whose triage
evidence is already deterministic and complete goes straight to the judge; deep-dives fill
evidence gaps rather than re-prove. H1 was reproduced and had its mechanism named in a
traceback; H2–H5 were already dead on exclusionary readings; and the one genuinely open
question — onset — cannot be answered by any probe, because the evidence that would settle
it has not been retained. Spawning agents here would have been coverage theater. One cheap
orchestrator probe was added instead (`/orders`, E14) to test whether an order had depleted
product 3 inside the window. None had.

**Judge.** One fresh judge saw only the hypothesis list and the verbatim ledger — no lens
reasoning, no narrative. It validated H1, invalidated H2–H6, and corrected this report in
four ways, all adopted: that `E9`/`E10` are weaker than they look (a point-in-time gauge
read taken after the window, and an absence check against guessed event names), so H2 rests
properly on `E2`/`E6`; that H3 must not be sold as "no recent start", since uptime of 173.7 s
means a start *did* occur inside the complaint's hour and only the causal link is refuted;
that `E14` and `E16` belong in H1's support, because no order for product 3 means its
`units_ordered` is 0 and the expression is `0/0`, making the zero *denominator* the sole
discriminator; and that "user-visible" overstates loopback lab traffic, so this journal
says "non-investigator traffic" throughout.

## Hypotheses

### H1 — zero-stock divisor in the product-detail handler — **validated**

The traceback carries the mechanism literally: the frame, the line, and the expression
`units_ordered / product["units_in_stock"]` (E2). A `ZeroDivisionError` at that expression
entails a zero denominator at that instant — the exception's own semantics, not an
inference about the data. The 500 access line and the exception line share request id
`9b62b4f06d5d` 10 ms apart (E1, E2), so they are one request, and the pairing repeats three
more times (E3).

E6 is the decisive control: product 4 has stock 75 and `units_ordered: 0` and returns 200
with `turnover_score: 0.0`. A zero *numerator* is therefore safe, and the field is computed
on the success path. Product 4 also carries `price: null` and still serves, which removes
null-field handling as a competing cause. E5 shows product 3 is the catalog's only
zero-stock row, and E14 shows no order exists for product 3 — so its expression is `0/0`
and the denominator is the only discriminator. E16 argues this is a defect rather than
intended behaviour: the route declares no 5xx at all.

Honest limit: "unguarded" is established in effect, because the raising expression appears
in the traceback, but the surrounding source was never read — the target's source is outside
the investigator's surface by contract.

### H2 — internal degradation switch — **invalidated**

`faultline_chaos_enabled 0` (E9) and the absence of any switch event (E10) are the obvious
citations and the weaker ones: the gauge was read twice, both times after the incident
window, and an absence check can only cover event names chosen in advance. The hypothesis
dies on E2 and E6 instead. The exception arises at a named application source line, and the
same code path returns a genuine computed value from genuine data for another product. A
switch would have to forge a `ZeroDivisionError` at that exact expression, key it to the one
product whose stock is 0, and emit no event — a mechanism indistinguishable from H1 and with
nothing in the record favouring it. What would settle it absolutely: the switch's own
implementation, which is outside this surface.

### H3 — process crash, restart, or hang — **invalidated as the cause**

One startup marker, no shutdown line, no second startup (E11), and four monotonic uptime
reads that all imply the same start instant (E12) — uptime resets on restart, so no restart
occurred after 23:33:31Z. The causal link fails independently: a `/products/2` → 200 at
23:33:41.312Z sits between failures at 23:33:39.258Z and 23:33:42.379Z (E7, E3), and no
lifecycle event produces that interleaving. Sub-2 ms successes (E7) argue against a hang
better than the flat max-RSS does, since a high-water mark would not fall during one either.
**Stated precisely:** a process start *did* happen within the complaint's hour; what is
refuted is that it caused the errors. See Gaps.

### H4 — gateway, proxy, or upstream dependency — **invalidated**

The 500 body carries the application's own `exception_type` and echoes the request id the
application assigned (E4) — a front tier does not know the app's exception class. The error
is raised in-process inside the handler frame (E2), the application's own counters
incremented for both the 500 and the exception (E8), and the same route template succeeds for
another id (E6), so no tier is failing "that one page". Note the limit: this refutes a
boundary component as the *cause*, not the existence of one. Loopback client addresses are
consistent with a local front tier, since every client would look local in this lab.

### H5 — load saturation — **invalidated**

Total volume across the entire process life was ten requests (E8) — not demand exceeding
capacity. The real kill is determinism rather than the capacity readings: every
`/products/3` request in the record failed (E15) and every other-id request succeeded (E6,
E7), and saturation does not respect a product id. The latency mean (E13) is near-worthless
on eight samples, where the fast failures inflate it.

### H6 — in-window stock depletion — **invalidated**

The only two orders are for products 1 and 2 (E14), so nothing depleted product 3 during the
observable window. And E15 removes the onset itself: the first request naming id 3 is
already a 500, 7.2 s after startup, so no error-free period exists for a trigger to explain.

### H7 — pre-telemetry data change vs. seeded value — **inconclusive**

Whether `units_in_stock: 0` is product 3's seeded initial value or the result of a write
before 23:33:31Z is simply not observable here. E5 is a single state read taken after
everything and can never evidence a change over time; it supports "stock is 0 now", which
already belongs to H1. A seed-file edit minutes before startup would satisfy the complaint's
"within the last hour" and leave no trace on this surface. What would settle it: the product
record's origin — the seeded fixture definition, or a write/audit record for that field.
Neither is on the investigator's surface. This distinction does not change the root cause:
the failure requires the division to be unguarded whenever stock reaches zero, and zero stock
is a normal business state for a sold-out item, not corrupt data.

## Safe next steps

Read-only only; remediation is out of scope for this journal.

- **Quantify the live blast radius**: watch `http_exceptions_total{type="ZeroDivisionError"}`
  and the 500 series on `/products/{product_id}` to measure the ongoing non-investigator
  failure rate.
- **Close the scope gap**: probe `/products/5`, the one catalog id never exercised, and
  re-read `/products` to see whether any other row has reached `units_in_stock: 0` since.
  Any sold-out product should be expected to show this same behaviour.
- **Anchor the onset**: ask the reporter for the exact product page and the first-noticed
  time. The telemetry cannot date the onset, and the reporter's own timing is the only
  remaining source for it.
- **Recover the missing history**: log rotation is configured for `.1`–`.3` backups but none
  are present (E15). Whoever owns retention can say whether an earlier `app.log` existed
  before 23:33:31Z — that would settle both the onset and H7.
- **For a code owner** (outside konan's read-only surface): reading the handler around the
  `turnover_score` expression would confirm whether any guard covers a zero divisor, and
  reading the catalog seeding for product 3 would resolve H7.
- **Track the two latent findings** separately from the incident: the exception class leaking
  into the client-facing 500 envelope (E4), and the route declaring no 5xx (E16).

## Gaps

The frontmatter list, elaborated:

**The observable window is about three minutes, against a complaint that spans an hour.**
This is the dominant limitation of this investigation. The log opens at its own startup line
and no rotated backups exist (E15), so there is no last-known-good for `/products/3`, no
datable onset, and no way to confirm or refute either "started within the last hour" or "no
deploys that we know of" — the only version signal in the record is `faultline 0.1.0` at
startup, with nothing earlier to compare it against. A process start *did* occur inside that
hour (uptime 173.7 s at the last read, E12); the benign reading is that the lab target was
started for this session, but the record cannot distinguish that from an earlier restart
whose logs are gone.

**Source is out of reach by contract.** "The division is unguarded" rests on the raising
expression in the traceback (E2), not on reading the handler. Likewise, whether the internal
switch *could* synthesise this exception (H2) and whether `0` is product 3's seeded value
(H7) both require reads outside the investigator's surface.

**Two dimensions were argued rather than measured.** `/metrics` exposes no concurrency,
queue, or connection series, so H5 is unmeasured on those axes and was killed by determinism
and total volume instead. Product id 5 was never probed, so "only id 3 fails" rests on ids 1,
2 and 4 succeeding plus id 3 being the only zero-stock row.

**Attribution stops short of real end users.** All lab client addresses are loopback (E1).
The four original failures are firmly non-investigator traffic — the baseline metrics read
(E8) already showed 4 × 500 before the first investigator probe of that route, and the
counts reconcile exactly with the four unstamped access lines — but loopback traffic in a lab
cannot be shown to be real customers.

**Lens coverage is narrower than the taxonomy.** This repo ships triage lenses for
software-defect, infra-process and interfaces. load-saturation (H5) and data-db (H6, H7) were
tested by the orchestrator against metrics and probes rather than by a dedicated lens, and
third-party was excluded only by the absence of any external-call signal on the surface — a
blind spot accepted knowingly, not a domain cleared by a specialist.
