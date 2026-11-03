---
konan_journal: 2
investigation:
  id: 2026-11-02-product-page-500s
  trigger: "manual — /konan adapter, profile human. Complaint object: source=human, fingerprint=human-1793663217, labels.alertname=human-report (no severity stated by the reporter), startsAt=2026-11-02T23:46:57Z. Investigation entered at 2026-11-02T23:47:04Z — trigger latency 7 s."
  complaint: "Support reports: several customers say a product page errors out with 'Internal Server Error' when they open it — started within the last hour, still happening when they refresh. Other pages load fine for them. No deploys that we know of."
  started: 2026-11-02T23:47:04Z
  concluded: 2026-11-02T23:54:56Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "The GET /products/{product_id} handler computes turnover_score by dividing units_ordered by product[\"units_in_stock\"] with no zero guard, so any catalog row whose units_in_stock is 0 — currently only product id 3 — raises an unhandled ZeroDivisionError and the request returns HTTP 500."
  incident_class: software-defect
  cause: unhandled-exception
hypotheses:
  - id: H1
    statement: "Unguarded division by product[\"units_in_stock\"] in the GET /products/{product_id} handler raises ZeroDivisionError for any row with units_in_stock = 0 (product id 3 is the only such row), failing every observed request for that id with HTTP 500 while rows with non-zero stock succeed."
    incident_class: software-defect
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E12, E13]
    evidence_against: []
  - id: H2
    statement: "An internal operational switch inside the target — chaos mode, error injection, or a feature flag — is injecting the 500s."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E9, E14, E1]
  - id: H3
    statement: "A process lifecycle fault — a crash, a restart loop, or a hang — is causing the failures."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E10, E2, E7, E11]
  - id: H4
    statement: "A boundary component (proxy, gateway, load balancer) or an external dependency is failing and surfacing as errors on the product page."
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E2, E6, E7, E12]
  - id: H5
    statement: "A change in the hour before the report — a deploy, a configuration change, or an edit to the product data — set units_in_stock to 0 for product id 3 and thereby started the failures at that time."
    incident_class: infra-process
    state: inconclusive
    evidence_for: []
    evidence_against: [E10, E2, E14]
latent_findings:
  - statement: "The HTTP 500 response body returns the internal Python exception class name to the caller alongside the generic error text — an error-handling contract defect, not the cause of this incident."
    evidence: [E12]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:46:46.306Z (stack trimmed to the throwing frames; the absolute directory prefix is elided as ... per this repo's no-private-paths rule)"
    quote: |-
      {"ts": "2026-11-02T23:46:46.306Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "71101de45d6b", "event": "unhandled_exception", "exception_type": "ZeroDivisionError", "stack": "Traceback (most recent call last): ... File \".../src/faultline/shop.py\", line 64, in get_product\n    \"turnover_score\": units_ordered / product[\"units_in_stock\"],\n                      ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~\nZeroDivisionError: division by zero"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:46:46.315Z"
    quote: |-
      {"ts": "2026-11-02T23:46:46.315Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "71101de45d6b", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 9.861, "client": "127.0.0.1:62503"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:46:47.378Z"
    quote: |-
      {"ts": "2026-11-02T23:46:47.378Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "556de4a062d1", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.895, "client": "127.0.0.1:62504"}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:46:50.496Z"
    quote: |-
      {"ts": "2026-11-02T23:46:50.496Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "8704bd2192d4", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.791, "client": "127.0.0.1:62506"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:46:52.617Z"
    quote: |-
      {"ts": "2026-11-02T23:46:52.617Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/3 -> 500", "request_id": "3259d407c396", "event": "request", "method": "GET", "path": "/products/3", "status": 500, "duration_ms": 4.822, "client": "127.0.0.1:62508"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:46:41.151Z"
    quote: |-
      {"ts": "2026-11-02T23:46:41.151Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "15c4f604347b", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 1.007, "client": "127.0.0.1:62500"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:46:49.433Z"
    quote: |-
      {"ts": "2026-11-02T23:46:49.433Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "07243f384988", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.74, "client": "127.0.0.1:62505"}
  - id: E8
    type: metric
    source: "/metrics @ 2026-11-02T23:47:29Z (probe request_id=konan-1793663249-11765)"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 4
      http_exceptions_total{type="ZeroDivisionError"} 4
  - id: E9
    type: metric
    source: "/metrics @ 2026-11-02T23:47:29Z (probe request_id=konan-1793663249-11765)"
    quote: |-
      faultline_chaos_enabled 0
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-02T23:46:39.333Z — the only startup event in the file"
    quote: |-
      {"ts": "2026-11-02T23:46:39.333Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E11
    type: metric
    source: "/metrics, two reads 97 s apart (2026-11-02T23:47:29Z and 2026-11-02T23:49:06Z)"
    quote: |-
      process_uptime_seconds 49.95482587488368
      process_uptime_seconds 147.61447095801122
  - id: E12
    type: probe
    source: "GET /products/3 (request_id=konan-1793663447-12074)"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793663447-12074"}
      -- HTTP 500 in 0.003987s request_id=konan-1793663447-12074
  - id: E13
    type: probe
    source: "GET /products (request_id=konan-1793663449-12079)"
    quote: |-
      [{"id":1,"name":"Anvil","price":49.5,"units_in_stock":118},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":39},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]
      -- HTTP 200 in 0.001466s request_id=konan-1793663449-12079
  - id: E14
    type: log
    source: "lab/logs/app.log — first line of the file; lab/logs/ holds app.log only, with no rotated .1-.3 backups, and the file contains no chaos_enabled, chaos_disabled, chaos_failure, simulated_exception, configuration-change or deploy marker anywhere"
    quote: |-
      {"ts": "2026-11-02T23:46:39.333Z", "level": "INFO", "logger": "uvicorn.error", "message": "Started server process [11673]", "color_message": "Started server process [\u001b[36m%d\u001b[0m]"}
gaps:
  - "Onset is unobservable. The telemetry horizon begins at the process start (E10, E14) and no rotated log backups exist, so the window is minutes long against a complaint that claims an onset within the hour. The reporter's 'started within the last hour' can be neither confirmed nor refuted, and nothing in the surface dates units_in_stock reaching 0 for product id 3."
  - "The origin of the zero stock value is outside the surface contract. Settling H5 needs the change history of the product-data source (version history or mtime of the seed or fixture that defines units_in_stock), which the contract in docs/lab.md does not expose to an investigation."
  - "'No deploys that we know of' is consistent with the evidence but not independently confirmable: the log holds no deploy marker, and the window could not contain one by construction (E14)."
  - "User attribution is inferred, not proven. The four failing requests carry no konan-* stamp, so they are not investigator traffic (E2-E5), and all four predate the first investigator probe of /products/3 by about three minutes (E8 at 23:47:29Z vs E12 at 23:50:47Z). But every client address is loopback with sequential ephemeral ports, and the surface carries no user identity, session, user-agent or non-loopback address — so 'real customers' rests on the complaint, not on telemetry."
  - "Exhaustiveness of the input class is not proven. Determinism is established for product id 3 (E2-E5, E12) and success for ids 1 and 2 (E6, E7); that any other row with units_in_stock = 0 would fail the same way follows from the throwing expression (E1), not from an observation — the catalog currently holds no second zero-stock row (E13)."
  - "The null price on catalog row id 4 (E13) was not exercised by a probe of mine on any route. No exception type other than ZeroDivisionError appears in the counters (E8), so it has not fired in the observed window; whether an arithmetic path elsewhere is unguarded against it is untested. POST routes are outside the GET-only probe surface."
usage:
  model: claude-opus-5
  tokens: 1993854
  wall_clock_seconds: 472
---

# Product page 500s — unguarded division by zero stock on GET /products/{id}

## Summary

**Root cause identified.** The product detail route `GET /products/{product_id}` builds a
`turnover_score` field by dividing `units_ordered` by `product["units_in_stock"]` with no
guard against a zero divisor (E1). Catalog row id 3, "Unobtainium Ingot", currently holds
`units_in_stock: 0` — the only zero in the catalog (E13). Every request for that id raises
an unhandled `ZeroDivisionError` and returns HTTP 500; rows with non-zero stock return 200
on the same route (E6, E7). This is a `software-defect` of the `unhandled-exception`
mechanism: deterministic per input, not probabilistic, not injected, not infrastructure.

The complaint's shape matches the defect exactly: one product page fails, it fails again on
refresh, other pages are fine. Impact in the observed window is four failed requests, all
for `/products/3`, between 23:46:46.315Z and 23:46:52.617Z (E2–E5); none of them is
investigator traffic, and all four predate my first probe of that path by about three
minutes. Confidence in the mechanism is high — the throwing expression is in the stack, the
divisor's value is readable on a healthy endpoint, and the failure reproduces on demand.

Two things the evidence does **not** support, stated plainly because the complaint invites
both. First, onset: the service's telemetry starts at its own process start and the first
`/products/3` request in existence already fails (E10, E2), so there is no last-known-good
and no observable transition — the claim that this began within the last hour is outside
what this surface can judge. Second, the "customers": the failing requests are unstamped
loopback traffic, which rules out the investigator but does not by itself prove human users.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 23:46:39.333Z | Process starts; the only `startup` event in the file, and the first line of the only log file — the telemetry horizon | E10, E14 |
| 23:46:41.151Z | `GET /products/1` → 200 — the route works for a non-zero-stock row | E6 |
| 23:46:46.306Z | First `ZeroDivisionError`, 7 s after start, thrown at the `turnover_score` division | E1 |
| 23:46:46.315Z | First `GET /products/3` → 500, same request id as the exception | E2 |
| 23:46:47.378Z | Second `GET /products/3` → 500 | E3 |
| 23:46:49.433Z | `GET /products/2` → 200 — interleaved success on the same route template | E7 |
| 23:46:50.496Z | Third `GET /products/3` → 500 | E4 |
| 23:46:52.617Z | Fourth `GET /products/3` → 500 — last non-investigator request in the window | E5 |
| 23:47:29Z | Metrics: 4 × 500 and 4 × `ZeroDivisionError` on this route, chaos off | E8, E9 |
| 23:50:47Z | Investigator probe reproduces the 500 on demand | E12 |
| 23:50:49Z | Investigator probe reads the catalog: id 3 has `units_in_stock: 0` | E13 |

No configuration-change, flag-change or deploy marker appears anywhere in the log (E14) —
and, as the Gaps record, the window is too short to have contained one.

## Investigation

**Baseline.** `/health` returned 200 with an uptime of 40.7 s; `/metrics` showed 4 × 500 and
4 × `ZeroDivisionError` concentrated on `/products/{product_id}`, with chaos off; the log
file held 25 lines covering the entire process lifetime.

**Triage — one round, three lenses in parallel, each blind to the others.** All three
domains were spawned: the complaint named a 500, which is defect-shaped, but complaint
framing is untrusted and the baseline could exclude no lens by evidence. `software-defect`
found the throwing frame, identified the zero divisor from the catalog, and reproduced the
failure read-only against four healthy controls. `infra-process` reported no anomaly in its
domain: a single process start, monotonic uptime, flat peak memory, no health flap, chaos
off. `interfaces` reported that the mechanism was not in its domain — the failure is keyed
strictly to one input, the status is 500 rather than a gateway shape, and the durations are
milliseconds — and contributed the discriminator: `units_in_stock: 0` is the only zero in
the catalog, while a *null* `price` on row id 4 still returns 200. All three independently
flagged the same scope limit: the telemetry horizon is far shorter than the claimed onset.

**Deep-dive — skipped, deliberately.** The skill reserves deep-dives for evidence gaps. H1's
triage evidence was already deterministic and complete (throwing expression, divisor value,
on-demand reproduction, controls, counters with no unexplained residue), so it went straight
to the judge. H2–H4 were already carrying disconfirming evidence. No hypothesis had a gap a
targeted probe could close — the one open question, H5, is unreachable through this surface,
not under-probed.

**Judge.** One fresh judge, given the hypothesis list and the verbatim ledger only, no
narrative. It validated H1's mechanism, invalidated H2–H4, and held H5 inconclusive. It
corrected three overreaches in the draft, all of which are carried into this journal: the
universal "every request" was narrowed to "every observed request, and deterministically on
demand"; the failing class was restated as *any* row with `units_in_stock = 0`, of which id 3
is merely the only current instance, rather than id 3 being special; and the claim that *real
customers* were affected was reduced to what the telemetry proves — that the traffic was not
the investigator's. It also noted that `process_max_rss_bytes` is a high-water mark and so
weak evidence against live memory growth, which is why H3 rests on the uptime series and the
request durations (E10, E11, E2, E7) rather than on memory.

## Hypotheses

### H1 — Unguarded division by zero stock on the product detail route — **validated**

The chain closes without a gap. E1 carries the raising frame itself — `"turnover_score":
units_ordered / product["units_in_stock"]` raising `ZeroDivisionError` — stamped
`request_id=71101de45d6b`, and E2 binds that same request id to `GET /products/3 -> 500`.
E13 supplies the divisor's value for that id (`"units_in_stock":0`) from a healthy 200
response. E12 reproduces the failure on demand. E8 leaves no residue: 4 × 500 equals
4 × `ZeroDivisionError` on the same route template, with no other exception type present at
all, so every observed failure *is* this one rather than merely consistent with it. E6 and E7
are interleaved successes on the same route template with non-zero-stock rows.

The defensible scope: every *observed* request for id 3 failed (E2–E5, E12), and the failure
is deterministic on demand. The failing input class is any row with `units_in_stock = 0`,
which follows from the throwing expression rather than from observation — id 3 is the only
such row at present (E13).

### H2 — Injected degradation from an internal switch — **invalidated**

`faultline_chaos_enabled 0` at every read (E9), and the log covers the full process lifetime
with no `chaos_enabled`, `chaos_disabled`, `chaos_failure` or `simulated_exception` event
anywhere in it (E14) — so the switch was not flipped and back inside the observable window.
Decisively, an injector does not produce E1: a real arithmetic frame in the target's own
source, failing as a deterministic function of one catalog row's data. H1 already accounts
for 4 of 4 exceptions, leaving nothing for an injector to explain. What would settle it
beyond doubt: a second, unexported injection hook in the request path that emits no log
event — which would need a read of the target's source, outside this surface.

### H3 — Process lifecycle fault — **invalidated**

One `startup` event only (E10), and the uptime series is monotonic and reconciles to that
single start: 49.955 s at 23:47:29Z and 147.614 s at 23:49:06Z differ by 97.66 s across 97 s
of wall clock, each back-solving to ~23:46:39 (E11). No restart, no second process, no
counter reset. A hang is refuted independently by the request durations — 0.74 ms to 9.861 ms
(E2, E7) — and by `/health` answering 200 throughout. A second `startup` event, or a
decreasing uptime read, would reopen it.

### H4 — Boundary component or external dependency — **invalidated**

The error is manufactured in-process: E1's traceback terminates in the target's own source,
and E12's body is the application's own error envelope rather than a gateway's. The status is
500, not 502/503/504. Latencies of 4–10 ms exclude a dependency stall or timeout (E2, E12),
and the divisor comes from data the application itself serves at 200 (E13). Successes
interleave with failures on the same route by input (E6, E7), which is not a boundary shape.
The stack in E1 is trimmed, so the ledger cannot formally exclude an upstream frame — but the
*raising* frame is local arithmetic on local data, which settles the mechanism.

### H5 — A change in the last hour started it — **inconclusive**

This is the honest open question, and it is open for a structural reason rather than a
missing probe. The absence of a deploy or configuration marker (E14) proves nothing here: the
log begins at process start, so the observable window cannot contain a prior deploy or data
edit by construction. Absence of a marker in a window that starts *after* the suspected
change is not evidence against the change. What the evidence does undercut is only the
timing clause — the first failure lands 7 s after process start (E10, E2), so the failures
did not begin partway through this process's life; they were present from its first traffic.
The origin of `units_in_stock: 0` is entirely unobserved. Settling it needs the change
history of the product-data source, which `docs/lab.md` does not expose to an investigation.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

1. Confirm the input class rather than the single id: read the change history of whatever
   seeds `units_in_stock`, to date when row id 3 reached 0 and to learn whether other rows
   have been at 0 before. This is the one piece of evidence that would settle H5, and it
   lives with whoever owns the product data.
2. Ask whoever owns deploys to check the deploy record directly against the report window.
   The service's own telemetry cannot corroborate "no deploys that we know of".
3. Keep watching `http_exceptions_total{type="ZeroDivisionError"}` and the 500 count on
   `/products/{product_id}`: while the zero-stock row is in the catalog, the counter rises
   once per customer who opens that page, which is the live impact measure.
4. Have the error-handler owner look at the 500 envelope, which returns the internal
   exception class name to the caller (the latent finding, E12).
5. For the next investigation of this target, consider whether log retention should outlive a
   process restart. Every lens hit the same wall: with no rotated backups, no investigation
   can judge an onset claim.

## Gaps

The frontmatter list, elaborated:

- **Onset is unobservable.** The telemetry horizon begins at the process start (E10, E14) and
  there are no rotated log backups, so the window is minutes long against a complaint
  claiming an onset within the hour. "Started within the last hour" is neither confirmed nor
  refuted here, and nothing in the surface dates the zero stock value.
- **The origin of the zero stock value is outside the surface contract.** The change history
  of the product-data source would settle H5; `docs/lab.md` does not expose it.
- **"No deploys that we know of"** is consistent with the evidence but not independently
  confirmable — the log holds no deploy marker, and could not hold one for the relevant
  period by construction.
- **User attribution is inferred.** The four failing requests carry no `konan-*` stamp and all
  predate the first investigator probe of that path by about three minutes, so they are not
  investigator traffic. But all client addresses are loopback with sequential ephemeral
  ports, and the surface carries no identity, session, user-agent or non-loopback address, so
  "real customers" rests on the complaint rather than on telemetry.
- **Exhaustiveness of the input class is not proven.** Determinism holds for id 3 and success
  for ids 1 and 2; that any other zero-stock row would fail identically follows from the
  throwing expression, not from an observation, and no second zero-stock row exists now.
- **The null `price` on row id 4 was not exercised by a probe of mine.** No exception type
  other than `ZeroDivisionError` appears in the counters, so it has not fired in the observed
  window; whether some other arithmetic path is unguarded against it is untested, and POST
  routes are outside the GET-only probe surface.

One note on citation: E1's `stack` field is quoted with its absolute directory prefix elided
as `.../`, because this repo's text rules keep computer file paths out of committed files.
The throwing frame, line number, expression and exception class are quoted unaltered.
