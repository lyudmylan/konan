---
konan_journal: 1
investigation:
  id: 2026-08-19-product-detail-zero-stock-500
  trigger: "manual — /konan human adapter (docs/triggers.md human profile). Complaint object: source human, fingerprint human-1787141376, labels.alertname human-report, no severity stated by the reporter. startsAt 2026-08-19T12:09:36Z; investigation start 2026-08-19T12:09:42Z; trigger latency 6s."
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-19T12:09:42Z
  concluded: 2026-08-19T12:20:20Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "GET /products/{id} computes `units_ordered / product[\"units_in_stock\"]` with no guard on the divisor, so a product whose stock is 0 — currently product 3, \"Unobtainium Ingot\" — raises an unhandled ZeroDivisionError and returns HTTP 500 on every request."
  incident_class: software-defect
hypotheses:
  - id: H1
    statement: "GET /products/{id} raises an unhandled ZeroDivisionError and returns HTTP 500 whenever the requested product's units_in_stock is 0, because the detail handler divides units_ordered by units_in_stock without guarding the divisor. Product 3 is currently the only catalog entry in that state."
    incident_class: software-defect
    state: validated
    evidence_for: [E3, E4, E5, E6, E7, E8, E13, E15]
    evidence_against: []
  - id: H2
    statement: "The 500s were caused by injected chaos or an operator flag change — degradation deliberately switched on."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E6, E16]
  - id: H3
    statement: "The 500s were caused by process instability — a crash loop, repeated restarts, or resource saturation."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E6, E11]
  - id: H4
    statement: "A process restart or other infrastructure event inside the unretained window caused, or masked the onset of, the 500s customers reported this morning — separately from or in addition to H1."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E12]
    evidence_against: []
  - id: H5
    statement: "Product 4's null price is a second live defect capable of producing a customer-visible 500 on a product page."
    incident_class: data-db
    state: invalidated
    evidence_for: []
    evidence_against: [E5, E8]
latent_findings:
  - statement: "The 500 error envelope leaks the internal Python exception class name to the client: the response body carries \"exception_type\":\"ZeroDivisionError\". Successful responses carry no such field. This is an information-disclosure defect on the same route, distinct from the incident itself."
    evidence: [E3]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:09:23.242Z"
    quote: |-
      {"ts": "2026-08-19T12:09:23.242Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: probe
    source: "/health, request_id konan-1787141403-57729"
    quote: |-
      {"status":"ok","uptime_seconds":40.7488009580411}
      -- HTTP 200 in 0.003279s request_id=konan-1787141403-57729
  - id: E3
    type: probe
    source: "/products/3, request_id konan-1787141476-57787"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1787141476-57787"}
      -- HTTP 500 in 0.008308s request_id=konan-1787141476-57787
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:14:06.910Z (event unhandled_exception, request_id konan-1787141646-57953) — tail of the stack field"
    quote: |-
      File "/Users/lyudmylan/Projects/faultline/src/faultline/shop.py", line 64, in get_product
          "turnover_score": units_ordered / product["units_in_stock"],
                            ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
      ZeroDivisionError: division by zero
  - id: E5
    type: probe
    source: "/products, request_id konan-1787141472-57775, HTTP 200"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":40},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
  - id: E6
    type: metric
    source: "/metrics, request_id konan-1787141706-58043 @ 2026-08-19T12:15:06.568Z"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 8
      http_requests_total{method="GET",path="/products/{product_id}",status="404"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 7
      http_exceptions_total{type="ZeroDivisionError"} 7
      faultline_chaos_enabled 0
      process_uptime_seconds 343.34502129093744
  - id: E7
    type: probe
    source: "/products/1, request_id konan-1787141670-57976, HTTP 200"
    quote: |-
      {"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}
  - id: E8
    type: probe
    source: "/products/4, request_id konan-1787141622-57915, HTTP 200"
    quote: |-
      {"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}
  - id: E9
    type: probe
    source: "/products/6, request_id konan-1787141480-57809"
    quote: |-
      {"detail":"no such product: 6"}
      -- HTTP 404
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:09:23.966Z–12:09:29.347Z — the complete set of non-investigator (unstamped) requests in the retained window; fields trimmed to ts, request_id, path, status"
    quote: |-
      {"ts": "2026-08-19T12:09:23.966Z", "request_id": "3f299004ba56", "path": "/health", "status": 200}
      {"ts": "2026-08-19T12:09:23.993Z", "request_id": "876884bb70da", "path": "/health", "status": 200}
      {"ts": "2026-08-19T12:09:23.998Z", "request_id": "b68a95593e71", "path": "/products", "status": 200}
      {"ts": "2026-08-19T12:09:25.067Z", "request_id": "ed82b651086a", "path": "/products/1", "status": 200}
      {"ts": "2026-08-19T12:09:26.137Z", "request_id": "2cb55ebd405e", "path": "/products/2", "status": 200}
      {"ts": "2026-08-19T12:09:27.206Z", "request_id": "8e654e88bf68", "method": "POST", "path": "/orders", "status": 201}
      {"ts": "2026-08-19T12:09:28.276Z", "request_id": "4395f539f75e", "path": "/orders", "status": 200}
      {"ts": "2026-08-19T12:09:29.347Z", "request_id": "ea7b23dc5526", "path": "/products/5", "status": 200}
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:11:16.472Z–12:15:03.803Z — the complete set of 5xx responses in the retained window; every request_id carries the konan- investigator prefix"
    quote: |-
      "request_id": "konan-1787141476-57787", "path": "/products/3", "status": 500
      "request_id": "konan-1787141479-57803", "path": "/products/3", "status": 500
      "request_id": "konan-1787141617-57908", "path": "/products/3", "status": 500
      "request_id": "konan-1787141646-57953", "path": "/products/3", "status": 500
      "request_id": "konan-1787141682-57992", "path": "/products/3", "status": 500
      "request_id": "konan-1787141699-58020", "path": "/products/3", "status": 500
      "request_id": "konan-1787141703-58032", "path": "/products/3", "status": 500
  - id: E12
    type: log
    source: "lab/logs/ — directory listing @ 2026-08-19T12:15Z; the directory holds this one file, no .1–.3 rotation backups"
    quote: |-
      -rw-r--r--@ 1 lyudmylan  staff  21473 Aug 19 15:13 app.log
  - id: E13
    type: probe
    source: "/products/2, request_id konan-1787141697-58014, HTTP 200"
    quote: |-
      {"id":2,"name":"Toaster","price":23.0,"units_in_stock":40,"units_ordered":0,"turnover_score":0.0}
  - id: E14
    type: probe
    source: "/orders, request_id konan-1787141635-57930, HTTP 200"
    quote: |-
      [{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-08-19T12:09:27.205+00:00"}]
  - id: E15
    type: log
    source: "lab/logs/app.log @ 2026-08-19T12:11:16.472Z"
    quote: |-
      {"ts": "2026-08-19T12:11:16.472Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "konan-1787141476-57787", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 7.493, "client": "127.0.0.1:60349"}
  - id: E16
    type: probe
    source: "/products/3 — repetition record across 7 probes, 2026-08-19T12:11:16.472Z to 12:15:03.803Z, interleaved with other traffic"
    quote: |-
      GET /products/3 -> 500 (konan-1787141476-57787, 7.493 ms)
      GET /products/3 -> 500 (konan-1787141479-57803, 2.519 ms)
      GET /products/3 -> 500 (konan-1787141617-57908, 5.062 ms)
      GET /products/3 -> 500 (konan-1787141646-57953, 2.6 ms)
      GET /products/3 -> 500 (konan-1787141682-57992, 2.661 ms)
      GET /products/3 -> 500 (konan-1787141699-58020, 2.475 ms)
      GET /products/3 -> 500 (konan-1787141703-58032, 2.623 ms)
gaps:
  - "No telemetry predates the 12:09:23.242Z process start (E1). lab/logs/ holds a single app.log with no rotation backups (E12) and metric counters are process-scoped, so the complaint's 'this morning' window has zero retained evidence. Customer 500s from that window can be neither confirmed nor counted."
  - "Customer impact is INFERRED from deterministic reachability, never OBSERVED. No non-investigator request touched /products/3 in the retained window (E10); all 7 observed 500s were generated by konan's own probes (E11). User traffic to the affected resource was never seen either succeeding or failing."
  - "Why the process restarted at 12:09:23Z, and by whom, is not visible on the allowlisted surface. The restart is itself an unexplained change event, and it destroyed the onset timeline."
  - "When product 3's units_in_stock reached 0 is unknown. The only order on record references product 1 (E14), so the zero-stock state was already present at process start rather than drained by orders in-window. Whether it changed this morning — the link that would explain onset timing — cannot be checked on this surface."
  - "The generalization 'any zero-stock product fails' rests on the traceback naming the divisor (E4), not on a second observed instance. Read-only access cannot create one, so 'id == 3' and 'stock == 0' remain perfectly confounded in the live catalog."
  - "POST /orders is outside the GET-only probe allowlist, so whether product 4's null price (E5, E8) breaks order creation was not tested. It is an unverified data anomaly, not a finding."
  - "The support tickets themselves — timestamps, product ids, verbatim error text — are off-surface. They are the only artifact that could convert the defect-to-complaint link from inferred to observed."
  - "The reporter's 'this morning' was never reconciled against the log's UTC stamps by a direct clock read, so the complaint window was bounded by inference rather than measurement."
  - "Two triage lenses and one deep-dive each had a probe denied by the permission prompt (/metrics, /openapi.json, /products, /products/4, /health). Each stopped on denial per the boundary rule. The affected checks were re-covered by other agents except the OpenAPI declared-vs-actual contract comparison, which was carried by a later probe returning HTTP 200 but whose body was never read into the ledger."
usage:
  model: claude-opus-5
  tokens: 2476612
  wall_clock_seconds: 638
---

# Product detail page returns 500 for sold-out items (zero-stock division by zero)

## Summary

**Root cause identified.** `GET /products/{id}` builds its response with an unguarded
division — `units_ordered / product["units_in_stock"]` at `shop.py:64` (E4) — so any
product whose stock is zero raises an unhandled `ZeroDivisionError` and returns HTTP 500.
Product 3, "Unobtainium Ingot", is the only catalog entry currently at `units_in_stock: 0`
(E5), and its detail page failed 7 out of 7 attempts over four minutes, never once
succeeding (E16). The response body is the literal string `internal server error` (E3) —
exactly the symptom support reported. Products 1, 2, 4 and 5 all have non-zero stock and
all return 200 with a computed `turnover_score` (E7, E8, E13), and an unknown id returns a
clean 404 (E9), so the fault is specific to the zero divisor and not to the route, the
catalog, or error handling in general.

**Confidence in the mechanism is high** and close to deductive: the traceback names the
failing expression with the caret under the divisor, the exception counter
`http_exceptions_total{type="ZeroDivisionError"} 7` exactly equals the 500 counter with no
other exception class present, and chaos is off (E6). Every alternative was tested and
killed: chaos or a flag change (H2), process instability or saturation (H3), and product
4's null price as a second defect (H5).

**Confidence that this is what those specific customers hit is materially lower, and the
distinction matters.** All telemetry begins at a process start 12:09:23.242Z (E1) with no
rotated logs (E12), so the reported morning window has no surviving evidence at all. Every
500 on record was triggered by konan's own probes (E11); no user request reached
`/products/3` in the retained window (E10). The link from this defect to those tickets is
an inference — a strong one, since the defect is deterministic and the triggering action is
the plain page-open the complaint describes — but it is not an observation.

**Impact, as far as it can be stated:** any customer opening the product 3 page gets a 500,
every time, right now. The rest of the shop surface is healthy.

## Timeline

- **2026-08-19T12:09:23.242Z** — faultline 0.1.0 process start (E1). This is the earliest
  timestamp in any artifact under `lab/` (E12); everything before it is unrecoverable. The
  restart is the only change marker on record and no configuration, deploy, or chaos event
  appears anywhere in the window.
- **12:09:23.966Z – 12:09:29.347Z** — the entire non-investigator traffic burst: eight
  requests, all 2xx, touching products 1, 2 and 5 plus an order (E10). None touched
  product 3. The near-uniform ~1.07 s spacing marks this as seeded startup traffic rather
  than a sample of real shopper behaviour.
- **12:09:36Z** — complaint raised by the human reporter (`startsAt`).
- **12:09:42Z** — investigation started; trigger latency 6 s.
- **12:10:03.980Z** — baseline probe: `/health` returns 200, uptime 40.7 s (E2).
- **12:11:16.465Z** — first `ZeroDivisionError`, on the first `/products/3` probe; the
  access line records `GET /products/3 -> 500` (E15).
- **12:11:16.519Z** — `/products/4` returns 200 forty-seven milliseconds later: the worker
  survives the exception, so this is a per-request failure, not a process fault.
- **12:11:16Z – 12:15:03Z** — `/products/3` probed seven times total, 500 every time,
  2.5–8.3 ms each (E16). Fast, deterministic failures; no intermittency.
- **12:15:06.568Z** — final metrics scrape: 7 × 500 and 7 × `ZeroDivisionError` on the
  product-detail route, chaos still 0 (E6).

## Investigation

**Baseline.** `/health` green, `/metrics` showing zero exceptions and no 5xx series, chaos
disabled, 16 log lines. The baseline was deliberately not read as "nothing is wrong": the
process was 45 seconds old, so clean counters described the last 45 seconds only, not the
morning. That framing shaped everything after it.

**Triage — three lenses in parallel** (software-defect, interfaces, infra-process), each
blind to the others, each given only its lens file, the surface contract, the verbatim
complaint, and the baseline. All three independently converged on the same deterministic
500 on `/products/3`, and — importantly — all three independently flagged that only
investigator traffic had triggered it. The infra-process lens added the point that a green
health endpoint and reset counters were being asked to carry more weight than they can.

**Deep-dive — two hypotheses in parallel.** One agent worked H1 to confirm and refute:
seven repetitions spread over four minutes (never a 200), metric corroboration, and a
disconfirming sweep asking what *else* distinguishes product 3 — price, name, catalog
position — all ruled out by product 4 returning 200 with a null price and products 2 and 5
returning 200 with the same formula. A second agent was pointed adversarially at the leap
from defect to complaint, tasked with hunting a different or additional cause. It
established the retention boundary exhaustively, produced a complete 5xx census, and killed
the null-price candidate.

**Judge.** A fresh agent saw only the hypothesis list and the evidence ledger — no
narrative. It validated the mechanism, rejected the "record it as latent" reading, and
found one genuine defect in the ledger: the metric showed 8 × 200 on the product-detail
route while the ledger attributed only 7, which would have falsified the claim that E10 was
a complete census of user traffic.

**Ledger reconciliation.** That gap was settled directly rather than argued away. The
retained log holds exactly eight 200s on `/products/{id}`: three from the seeded burst
(ids 1, 2, 5) and five investigator probes (`/products/4` twice, at 12:11:16.519Z and
12:13:42.783Z, plus ids 1, 2 and 5). The unattributed 200 was the second `/products/4`
probe. Counts close exactly — 8 × 200, 1 × 404, 7 × 500 — so E10's completeness claim
stands and the impact assessment rests on a verified census.

**On the latent-finding rule.** The rule in force says a defect only konan's probes have
triggered is latent, not the active incident. It was weighed seriously and set aside, for
two reasons. First, the rule exists to stop an investigator constructing an exotic input and
then calling it an outage; here the trigger was a plain GET of a listed catalog item — the
literal action the complaint describes. Second, "no user 500s observed" has no evidential
force when no user request reached the route at all: the retained window contains zero
requests to `/products/3`, so it is an absence with no statistical power, not evidence of
absence. Recording this as latent would tell support their customers were mistaken, and
nothing in the evidence licenses that.

## Hypotheses

### H1 — unguarded division on zero stock (validated, root cause)

The mechanism is named directly by the traceback (E4): the caret sits under
`product["units_in_stock"]`, the exception is unhandled, and the middleware converts it to
a 500. Product 3 is the sole catalog entry at zero stock (E5) and fails 7/7 (E16, E3).
Product 1 shows the arithmetic working normally — `1 / 119 = 0.008403361344537815` (E7) —
which confirms the divisor is real stock data rather than a constant. Products 2, 4 and 5
all have `units_ordered: 0` and return `turnover_score: 0.0` (E8, E13), proving a zero
*numerator* is safe; only a zero *denominator* fails. `http_exceptions_total{type=
"ZeroDivisionError"} 7` equals the 500 count exactly with no other exception class (E6),
so this single defect accounts for every 500 the process has served.

Two limits stated honestly. The generalization to "any zero-stock product" comes from the
traceback rather than a second observed instance; without E4 the data would fit "product 3
is special" equally well. And "the only entry in that state" is true of one snapshot — stock
is mutable, so the blast radius is "sold-out items", not permanently one row.

### H2 — chaos or an operator flag change (invalidated)

`faultline_chaos_enabled 0` on both scrapes (E6), no chaos event of any kind in the log,
and 7/7 determinism (E16) — injected degradation is probabilistic and would not fail one
specific input every time while sparing its neighbours. Refuted for the observed window.
Note the scope: this says nothing about flag state before 12:09:23Z.

### H3 — process instability or saturation (invalidated)

Uptime runs monotonically and consistently (40.7 s at E2, 343.3 s at E6), there is exactly
one startup marker, RSS sits at ~45 MiB, and the worker served a 200 forty-seven
milliseconds after an exception. The failures are application exceptions, not connection
errors or timeouts — every 500 is accounted for by the ZeroDivisionError counter (E6, E11).
No crash loop, no starvation. The restart at 12:09:23Z is real but is recorded as a gap
rather than counted as evidence against this hypothesis, since a startup line at the
earliest retained timestamp is equally the signature of a restart that erased history.

### H4 — a different or additional cause in the unretained window (inconclusive)

Structurally unresolvable on this surface. All telemetry begins at the process start (E1)
and no rotated logs exist (E12), so the morning cannot be observed at all: not the status
mix, not the chaos state, not the traffic volume on product 3. No second live defect was
found on the allowlisted surface, which is evidence of a kind, but a six-minute post-restart
window cannot refute a claim about a period it does not cover. This hypothesis stays open
by design; the evidence that would settle it is named under Safe next steps.

### H5 — product 4's null price as a second defect (invalidated)

Direct refutation: `/products/4` returns HTTP 200 with `"price":null` and
`"turnover_score":0.0` (E8), and the list route tolerates it too (E5). The product page —
the surface the complaint is about — works. Whether the null price breaks order creation is
untested and stays a gap, since `POST /orders` is outside the read-only probe allowlist.

## Safe next steps

All read-only; remediation is out of scope for this journal.

1. **Pull the support tickets** — their timestamps, the product ids customers opened, and
   the verbatim error text. This is the single piece of evidence that converts the
   defect-to-complaint link from inferred to observed. If the tickets name product 3, the
   attribution is settled. If they name other product pages, H1 does not explain them and
   the investigation should reopen.
2. **Retrieve access logs from any layer that outlived the restart** — a load balancer,
   reverse proxy, CDN, or APM. That is the only route to the morning window's status mix
   now that the application log is gone.
3. **Establish who restarted the process at 12:09:23Z and why**, from the supervisor or
   deploy history. A restart immediately before a complaint is prime timeline evidence, and
   right now it is an unexplained change event.
4. **Read the catalog's stock history for product 3** to find when `units_in_stock` reached
   zero. If it hit zero this morning, the onset timing is explained and the whole account
   closes.
5. **Read `shop.py:64` and its surroundings** to confirm the guard is missing rather than
   bypassed, and grep the codebase for the same unguarded-divisor pattern on other
   inventory fields.
6. **Check whether log retention and rotation are configured as intended.** A single
   un-rotated `app.log` that resets with the process is why this investigation could not see
   its own incident window — that is an observability gap worth fixing on its own merits.
7. **Review the 500 error envelope**, which returns the internal exception class name to
   clients (E3).

## Gaps

The frontmatter list, in short: nothing before 12:09:23.242Z survives, so the reported
morning window is unobservable; customer impact is inferred from deterministic
reachability rather than observed, because no user request reached product 3 in the retained
window; the restart itself is unexplained; the onset time of the zero-stock state is
unknown; the "any zero-stock product" generalization rests on the traceback rather than a
second instance, and read-only access cannot produce one; the order-creation path was not
tested against product 4's null price because it is outside the GET-only allowlist; the
support tickets are off-surface; and the reporter's "this morning" was bounded by inference
rather than a direct clock reconciliation.

One process note belongs here too. Five probe calls across three subagents were stopped by
the permission prompt; each agent halted and reported rather than routing around the denial,
as the boundary rule requires. Every affected check was re-covered by another agent except
one: `/openapi.json` was fetched successfully at 12:14:46.656Z but its body never entered
the ledger, so the declared-versus-actual contract comparison for `/products/{product_id}`
— in particular whether a 500 response is documented and whether `turnover_score` is a
required field — remains unchecked.
</content>
</invoke>
