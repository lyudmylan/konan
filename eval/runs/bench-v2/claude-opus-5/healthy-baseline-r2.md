---
konan_journal: 2
investigation:
  id: 2026-11-03-routine-handover-check
  trigger: "manual — /konan human-report profile; source human; fingerprint human-1793686465; labels.alertname human-report; no severity stated by the reporter; startsAt 2026-11-03T06:14:25Z; investigation start 2026-11-03T06:14:31Z; trigger latency 6s"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-11-03T06:14:31Z
  concluded: 2026-11-03T06:32:29Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "GET /products/{product_id} raises ZeroDivisionError and returns HTTP 500 when the requested row has units_in_stock == 0, because the handler computes units_ordered / units_in_stock with no zero guard; product 3 is such a row."
    incident_class: software-defect
    state: validated
    evidence_for: [E8, E9, E10, E11, E12, E13]
    evidence_against: []
  - id: H2
    statement: "The H1 defect is latent, not an active user-affecting incident: in the observable window no end-user request reached the failing row, and every 500 and every logged exception belongs to an investigator-stamped request."
    incident_class: software-defect
    state: validated
    evidence_for: [E3, E4, E6, E10, E11, E15]
    evidence_against: [E23]
  - id: H3
    statement: "The broken row is reachable by ordinary browsing: product 3 is present in the catalog list that every caller receives, since the list route takes no parameters and the service has no authentication to personalize on."
    incident_class: software-defect
    state: validated
    evidence_for: [E5, E8, E18, E21]
    evidence_against: []
  - id: H4
    statement: "Product 4 carries price null in the live catalog while order creation derives total_price by multiplying price by quantity, so creating an order for product 4 would fail on unguarded arithmetic."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E8, E14, E7]
    evidence_against: []
  - id: H5
    statement: "The detail routes violate their own published contract: /openapi.json declares only 200 and 422, while the service really returns 404 and 500, and the 500 body uses a third error-envelope shape that discloses the internal Python exception class."
    incident_class: interfaces
    state: validated
    evidence_for: [E18, E10, E19, E20, E22]
    evidence_against: []
  - id: H6
    statement: "No active incident affected users in the observable window: all end-user traffic succeeded, the process ran continuously on one PID with no restart, no memory growth trend, no latency decay, no gateway-shaped status, and no error-injection switch active."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E6, E7, E16, E17, E22, E26, E27]
    evidence_against: [E23]
  - id: H7
    statement: "The observable window is too thin to exclude a recurring or intermittent fault outside it: the log begins at process start with no rotated backups, and end-user traffic spans only 8.4 seconds."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E6, E23]
    evidence_against: []
  - id: H8
    statement: "The 32-second uptime seen at baseline was a planned cold start rather than recovery from a crash of a previous process instance."
    incident_class: infra-process
    state: inconclusive
    evidence_for: [E1, E16]
    evidence_against: [E23]
  - id: H9
    statement: "The failure is a property of the zero-stock state and not of product 3 specifically: the published units_ordered and units_in_stock fields are the exact operands of the failing expression, so any catalog row presenting units_in_stock == 0 fails identically for every caller."
    incident_class: software-defect
    state: validated
    evidence_for: [E12, E13, E14, E8]
    evidence_against: []
  - id: H10
    statement: "An ordinary end-user order can drive a currently-working product's units_in_stock to 0 and so widen the H1 defect to any product that sells out, because stock is decremented by ordered quantity."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E12, E13, E7, E18]
    evidence_against: [E8, E24, E25]
latent_findings:
  - statement: "GET /products/3 returns HTTP 500 deterministically for every caller, and the row is listed in the public catalog; in the observable window only investigator probes triggered it, so it is a live user-facing trap that no user has stepped into yet."
    evidence: [E8, E9, E10, E11, E15]
  - statement: "Product 4 (Mystery Box) is served to clients with price null while the order path derives total_price from price; the write path could not be exercised read-only."
    evidence: [E8, E14, E7]
  - statement: "The detail routes return statuses their published schema does not declare, and the 500 envelope differs from the service's other two error shapes while disclosing the Python exception class name."
    evidence: [E18, E10, E19, E20]
  - statement: "The order_created event records no resulting stock value, which is why the stock-decrement question (H10) cannot be settled from logs alone."
    evidence: [E7]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:14:07.176Z"
    quote: '{"ts": "2026-11-03T06:14:07.176Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: probe
    source: "/health, request_id konan-1793686479-20288"
    quote: |-
      {"status":"ok","uptime_seconds":32.04830333311111}
      -- HTTP 200 in 0.002071s request_id=konan-1793686479-20288
  - id: E3
    type: metric
    source: "/metrics, request_id konan-1793686479-20293 (process_uptime_seconds 32.53)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/orders",status="200"} 1
      http_requests_total{method="GET",path="/products",status="200"} 1
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 3
      http_requests_total{method="POST",path="/orders",status="201"} 2
  - id: E4
    type: metric
    source: "/metrics, request_id konan-1793686479-20293 — the http_exceptions_total block carried no series lines at this read"
    quote: |-
      # HELP http_exceptions_total Total unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
      # HELP faultline_chaos_enabled Whether chaos mode is active.
      # TYPE faultline_chaos_enabled gauge
      faultline_chaos_enabled 0
      process_uptime_seconds 32.531228500185534
      process_max_rss_bytes 46563328
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:14:07.937Z — the one end-user catalog list request"
    quote: '{"ts": "2026-11-03T06:14:07.937Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 200", "request_id": "18ba719ee4e5", "event": "request", "method": "GET", "path": "/products", "status": 200, "duration_ms": 1.072, "client": "127.0.0.1:64244"}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:14:08.994Z–06:14:16.291Z — the end-user detail-route and order-list requests, unstamped ids, all 2xx"
    quote: |-
      {"ts": "2026-11-03T06:14:08.994Z", "message": "GET /products/1 -> 200", "request_id": "8189d40fd926", "status": 200, "duration_ms": 1.014}
      {"ts": "2026-11-03T06:14:10.054Z", "message": "GET /products/2 -> 200", "request_id": "0f36bd0b2b44", "status": 200, "duration_ms": 0.978}
      {"ts": "2026-11-03T06:14:15.232Z", "message": "GET /orders -> 200", "request_id": "31e77c401d2e", "status": 200, "duration_ms": 0.847}
      {"ts": "2026-11-03T06:14:16.291Z", "message": "GET /products/5 -> 200", "request_id": "8c4494106a46", "status": 200, "duration_ms": 0.764}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:14:12.114Z and 06:14:13.172Z — the only two orders in the process lifetime"
    quote: |-
      {"ts": "2026-11-03T06:14:12.114Z", "logger": "faultline.shop", "message": "order created", "request_id": "929f18bf9b40", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 1, "total_price": 49.5}
      {"ts": "2026-11-03T06:14:13.172Z", "logger": "faultline.shop", "message": "order created", "request_id": "1cc8123d2bcd", "event": "order_created", "order_id": 2, "product_id": 2, "quantity": 2, "total_price": 46.0}
  - id: E8
    type: probe
    source: "/products, request_id konan-1793687264-20751, HTTP 200"
    quote: '[{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119},{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38},{"id":3,"name":"Unobtainium Ingot","price":999.0,"units_in_stock":0},{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75},{"id":5,"name":"Rubber Duck","price":6.25,"units_in_stock":500}]'
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:16:30.258Z — unhandled exception and its stack, raised by investigator request konan-1793686590-20384"
    quote: |-
      {"ts": "2026-11-03T06:16:30.258Z", "level": "ERROR", "logger": "faultline.request", "message": "unhandled exception: division by zero", "request_id": "konan-1793686590-20384", "event": "unhandled_exception", "exception_type": "ZeroDivisionError"}
        File ".../faultline/src/faultline/shop.py", line 64, in get_product
            "turnover_score": units_ordered / product["units_in_stock"],
                              ~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~
      ZeroDivisionError: division by zero
  - id: E10
    type: probe
    source: "/products/3, request_id konan-1793686697-20569"
    quote: |-
      {"error":"internal server error","exception_type":"ZeroDivisionError","request_id":"konan-1793686697-20569"}
      -- HTTP 500 in 0.005280s
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-11-03T06:16:30.266Z and 06:16:33.470Z — the same input failing again, both investigator requests"
    quote: |-
      {"ts": "2026-11-03T06:16:30.266Z", "message": "GET /products/3 -> 500", "request_id": "konan-1793686590-20384", "status": 500}
      {"ts": "2026-11-03T06:16:33.470Z", "message": "GET /products/3 -> 500", "request_id": "konan-1793686593-20391", "status": 500}
  - id: E12
    type: probe
    source: "/products/1, request_id konan-1793687271-20770, HTTP 200 — turnover_score is exactly 1/119"
    quote: '{"id":1,"name":"Anvil","price":49.5,"units_in_stock":119,"units_ordered":1,"turnover_score":0.008403361344537815}'
  - id: E13
    type: probe
    source: "/products/2, request_id konan-1793687273-20775, HTTP 200 — turnover_score is exactly 2/38"
    quote: '{"id":2,"name":"Toaster","price":23.0,"units_in_stock":38,"units_ordered":2,"turnover_score":0.05263157894736842}'
  - id: E14
    type: probe
    source: "/products/4, request_id konan-1793687275-20780, HTTP 200"
    quote: '{"id":4,"name":"Mystery Box","price":null,"units_in_stock":75,"units_ordered":0,"turnover_score":0.0}'
  - id: E15
    type: metric
    source: "/metrics, later read — exception and 500 counts equal the number of investigator probes of /products/3, and no other exception type ever appeared"
    quote: |-
      http_exceptions_total{type="ZeroDivisionError"} 3
      http_requests_total{method="GET",path="/products/{product_id}",status="500"} 2
  - id: E16
    type: metric
    source: "/metrics and /health, seven reads between 06:14:39Z and 06:17:47Z — each uptime subtracted from the timestamp of its own read implies the same process origin, spread 5 ms over 188 s"
    quote: |-
      06:14:39.214Z  process_uptime_seconds 32.04830333311111   -> origin 06:14:07.166Z
      06:16:38.554Z  process_uptime_seconds 151.39119429211132  -> origin 06:14:07.163Z
      06:17:47.139Z  process_uptime_seconds 219.97773850010708  -> origin 06:14:07.161Z
  - id: E17
    type: metric
    source: "/metrics, four reads at uptimes 32.5 s, 151.4 s, 206.1 s and 317.8 s — identical on every read, and no chaos_enabled / chaos_disabled / chaos_failure event appears anywhere in the log"
    quote: 'faultline_chaos_enabled 0'
  - id: E18
    type: probe
    source: "/openapi.json, request_id konan-1793686582-20371, HTTP 200 — declared responses for the detail route, the parameterless list route, and the order request schema"
    quote: |-
      "responses":{"200":{...},"422":{"description":"Validation Error",...}}
      "/products":{"get":{"tags":["shop"],"summary":"List Products","operationId":"list_products_products_get","responses":{"200":{"description":"Successful Response","content":{"application/json":{"schema":{"items":{"additionalProperties":true,"type":"object"},"type":"array","title":"Response List Products Products Get"}}}}}}}
      "OrderRequest":{"properties":{"product_id":{"type":"integer"},"quantity":{"type":"integer","maximum":1000.0,"minimum":1.0}},"required":["product_id","quantity"]}
  - id: E19
    type: probe
    source: "/products/999, request_id konan-1793686635-20492, HTTP 404; /orders/99, request_id konan-1793686626-20452, HTTP 404"
    quote: |-
      {"detail":"no such product: 999"}
      {"detail":"no such order: 99"}
  - id: E20
    type: probe
    source: "/products/abc, request_id konan-1793686645-20521, HTTP 422"
    quote: '{"detail":[{"type":"int_parsing","loc":["path","product_id"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"abc"}]}'
  - id: E21
    type: probe
    source: "/products?limit=2 (konan-1793687418-20839) and /products?in_stock=true&available=1&hide_out_of_stock=true (konan-1793687420-20844), both HTTP 200 — both bodies byte-identical to the unfiltered list of E8, including id 3"
    quote: 'Query parameters are ignored outright; the five-item body including {"id":3,...,"units_in_stock":0} is returned unchanged.'
  - id: E22
    type: metric
    source: "/metrics — the complete set of statuses the service emitted over its whole observable lifetime; no 502, 503 or 504 series exists on any route"
    quote: '200, 201, 404, 422, 500'
  - id: E23
    type: log
    source: "lab/logs/app.log — file metadata and the absence of rotated backups"
    quote: |-
      lab/logs/app.log  birth=2026-11-03T08:14:07+0200   (= 06:14:07Z, the process start instant)
      wc -l lab/logs/app.log*  ->  18 lab/logs/app.log    (no .1, .2 or .3 backup file exists)
  - id: E24
    type: probe
    source: "/orders, request_id konan-1793687269-20756, HTTP 200 — no order references product 3, so its zero stock is seeded and was not drained"
    quote: '[{"id":1,"product_id":1,"quantity":1,...},{"id":2,"product_id":2,"quantity":2,...}]'
  - id: E25
    type: probe
    source: "/orders/1, request_id konan-1793687404-20830, HTTP 200 — the order record carries no stock snapshot"
    quote: '{"id":1,"product_id":1,"quantity":1,"total_price":49.5,"created_at":"2026-11-03T06:14:12.114+00:00"}'
  - id: E26
    type: metric
    source: "/metrics, four reads — one first-touch step, then flat across 166 s and about 30 further requests; the gauge is documented as a peak high-water mark"
    quote: 'process_max_rss_bytes 46563328 -> 47857664 -> 47857664 -> 47857664'
  - id: E27
    type: probe
    source: "/health, request_id konan-1793687402-20822, HTTP 200 — still the same process, 955 s after the single startup"
    quote: '{"status":"ok","uptime_seconds":955.1585062500089}'
gaps:
  - "Nothing before 2026-11-03T06:14:07Z is observable: the log file was born at the process start instant and no rotated backup exists (E23). An earlier user-visible fault, including one on a previous process instance, cannot be excluded — this is what leaves H8 inconclusive."
  - "End-user traffic covers only 8.4 seconds (06:14:07.910Z–06:14:16.291Z); every request logged afterwards is investigator-stamped. The complaint asks about 'right now', and for users there is no 'now' in this telemetry — only that 8.4-second window."
  - "POST /orders is outside the read-only probe surface, so two questions stay open: whether the order path guards the null price of product 4 (H4), and whether an order decrements units_in_stock (H10). Only the eval harness may place an order; the decisive test is one order consuming a product's whole stock followed by a re-read of its detail route."
  - "The target's own source code is deliberately out of reach under this repo's blinding contract (AGENTS.md, eval/README.md). The judge proposed reading the order-creation handler to settle H4 and H10; that settler was refused by design, not overlooked. The stack trace in E9 is admissible because the service emitted it into its own log."
  - "The response body of the single end-user catalog list request (18ba719ee4e5, E5) is not recorded anywhere. H3 therefore rests on a structural argument — the list route declares no parameters and the service has no securitySchemes (E18), and query parameters are provably ignored (E21) — plus reproduction, not on a recovered body."
  - "konan sees only the target's own telemetry. A failure at a proxy, gateway, load balancer or client in front of the service would be invisible here, so H6 holds for the application tier and not for the whole user path."
  - "lab/server.out was not read: docs/lab.md heads its surface list 'all of it' and names only lab/logs/app.log under Logs. Covering stderr-only crash output would need a contract decision, not a probe."
  - "The rotated-backup check used one glob in lab/logs/ (E23). A different rotation naming scheme, a compressed archive, or another directory would not have appeared in it."
  - "No cross-run comparison was possible: journals/ is empty in this worktree and reading earlier journals from git history required an approval that an unattended session cannot grant, so it was not retried. Catalog bodies from runs with different order histories would have been a second independent test of H10."
usage:
  model: claude-opus-5
  tokens: 3594610
  wall_clock_seconds: 1078
---

# Routine handover check — no active incident, one live user-facing trap not yet stepped into

## Summary

**No active incident.** Nothing is wrong with the shop service right now, as far as this
surface can show: every end-user request in the observable history returned 2xx (E3, E6,
E7), the process has run continuously on one PID since a single cold start (E16, E27),
memory is flat (E26), latency improves rather than decays (E19 durations), no
gateway-shaped status has ever been emitted (E22), and no error-injection switch is active
(E17).

The handover should nonetheless not be signed off as quiet, for one reason. `GET
/products/3` fails **deterministically with HTTP 500** for every caller: the handler
computes `units_ordered / units_in_stock` with no zero guard, and that row's stock is zero
(E8, E9, E10, E11). The row is served in the public catalog list, the list route takes no
parameters, and the service has no authentication — so every visitor sees the broken item
and any visitor who opens it gets a 500 (E5, E18, E21). No user has done so yet: all three
500s and all three logged exceptions belong to this investigation's own probes (E15), which
is why the verdict is "no active incident" rather than "root cause identified". This is a
latent defect with a live path to users, not an outage.

Confidence: high on the mechanism and on its user reachability. Moderate on the claim that
nothing was wrong *before* this process started — that is unfalsifiable here, and it is the
honest limit of a 32-second-old log.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 06:14:07.176Z | Single startup marker, `faultline 0.1.0`, PID 20214. The log file itself is born at this instant — nothing earlier is observable. | E1, E23 |
| 06:14:07.910Z | First request, 734 ms after startup: `GET /health -> 200`, 11.796 ms (cold start, the all-time maximum duration anywhere). | E6 |
| 06:14:07.937Z | The one end-user catalog list call, `GET /products -> 200`. | E5 |
| 06:14:08.994Z–06:14:16.291Z | End-user traffic: detail reads of products 1, 2 and 5, two orders created (product 1 qty 1; product 2 qty 2), one order list. All 2xx. | E6, E7 |
| 06:14:16.291Z | **Last end-user request.** Everything after this point is investigator-stamped `konan-` traffic. | E6 |
| 06:14:25Z | Complaint raised by the reporter (`startsAt`). | — |
| 06:14:31Z | Investigation starts. Trigger latency 6 s. | — |
| 06:14:39Z | Baseline: `/health` ok at 32 s uptime; all counters 2xx; `http_exceptions_total` empty; chaos gauge 0. | E2, E3, E4 |
| 06:16:30.258Z | First `ZeroDivisionError` of the process lifetime — raised by an investigator probe of `/products/3`, not by a user. | E9, E11 |
| 06:16:33.470Z | The same input fails again: determinism established. | E11 |
| 06:17:47Z | Seventh uptime reading; implied process origin has not moved (5 ms spread over 188 s). No restart at any point. | E16 |
| 06:27:44Z–06:30:20Z | Deep-dive: catalog arithmetic confirmed exactly (1/119, 2/38); query parameters proven to be ignored, so no caller can be served a list without the broken row. | E12, E13, E21 |
| 06:32:29Z | Concluded. | — |

No configuration-change, deploy, flag or chaos marker appears anywhere in the observable
history (E17) — there is no change event to anchor an onset to, and no onset to find.

## Investigation

**Baseline** (step 1) came back clean and immediately produced the investigation's
governing fact: `process_uptime_seconds` was 32.5 (E4) and the log held 18 lines with no
rotated backups (E23). The counters were therefore useless as history, and the real
question became what the *logs* could and could not show.

**Triage** (step 2) ran all three lenses in parallel — software-defect, infra-process,
interfaces. No lens could be excluded: the complaint names no symptom, and a clean
32-second window excludes nothing. All three converged independently on the same defect
from different directions: the software-defect lens found the stack trace and the
zero-stock row; the infra-process lens settled the lifecycle question (one continuous
process, planned-looking start, no saturation) and noted the 500 path's disproportionate
cost; the interfaces lens found the undeclared statuses and the inconsistent error
envelope, and demonstrated the healthy-monitoring trap directly — `/health` returned
`"status":"ok"` two seconds before the catalog detail route returned a 500.

**No deep-dive round was spawned for H1.** Its triage evidence was already deterministic
and complete — stack trace, failing input, three reproductions, sibling inputs succeeding,
and metric attribution of every 500 to investigator traffic. Re-proving it would have been
ceremony.

**The judge** (step 4) saw only hypotheses and verbatim evidence. It validated H1, H2, H5,
H7 and the narrow reading of H6, and it refused three claims that the ledger did not
actually close: H3 (reachability rested on an investigator's view of the list, not a
user's), H4 (nothing showed the order handler lacks a null guard, and the failure would be
a `TypeError`, a different mechanism), and H8 (intent is not observable). It also raised a
severity question nobody had asked: if orders decrement stock, any product that sells out
becomes a 500 for everyone.

**One deep-dive round** (step 3, one agent — the only open question telemetry could move)
settled the reachability question and split the severity question. H3 is now confirmed
structurally: the list route declares no parameters at all, the service has no
`securitySchemes`, and query parameters are provably ignored (E18, E21), so no caller can
receive a list without the broken row. On severity, the published `units_ordered` and
`units_in_stock` fields turned out to be the exact operands of the failing expression
(E12: 1/119; E13: 2/38), which proves the general form — **any** zero-stock row fails, not
just product 3 (H9, validated). Whether a user can *create* that state (H10) remains
unproven: the arithmetic hints at it (119+1 = 120, 38+2 = 40, round seeds), but no stock
write appears anywhere in telemetry, the one real zero is a seed rather than a decrement
(E24), and the decisive test needs a POST this boundary forbids.

**Budget and boundary.** One triage round, one deep-dive agent, one judge — inside budget.
No probe left the GET allowlist and no command was denied. The judge's proposed settler for
H4 and H10 — read the order-creation handler — was declined: the target's source is blinded
by contract, and an investigation that reads the code it is meant to diagnose from telemetry
stops measuring anything. That refusal is recorded as a gap, not worked around.

## Hypotheses

### H1 — zero-stock division — **validated**

The service's own log carries the mechanism verbatim: `"turnover_score": units_ordered /
product["units_in_stock"]` at `shop.py", line 64`, raising `ZeroDivisionError` (E9). The
catalog gives the input: product 3 holds `"units_in_stock":0` (E8). Three probes, three
identical 500s (E10, E11). The four other catalog ids return 200 on the same route (E12,
E13, E14), so this is a data-dependent defect in one code path, not a route-wide or
infrastructure fault. The judge's one correction is adopted into H9: the trigger is the
zero-stock *state*, not the id.

### H2 — latent, not active — **validated**, bounded

At baseline, after all end-user traffic had already happened, the only status series in
existence were 200 and 201 and the exception block was empty (E3, E4): no end-user request
ever received a non-2xx. Every 500 and every exception carries a `konan-` id (E15, E10,
E11). The bound, cited against it: E23 means an earlier process instance would leave no
trace, so "no user has ever hit this" is a claim about the observable window only. A second
caveat worth recording for the reader — the "end-user" label rests on the absence of the
`konan-` prefix, and that traffic's metronomic ~1 s cadence followed by a dead stop looks
more like seeded smoke traffic than people.

### H3 — the broken row is user-reachable — **validated** (upgraded from inconclusive)

The judge was right that an investigator's list read proves nothing about a user's list.
The deep-dive answered it structurally instead: `/products` has no `parameters` key at all,
`components.schemas` contains no `securitySchemes`, and two deliberately filter-shaped
query strings returned byte-identical bodies including id 3 (E18, E21). A route with no
inputs and no identity has nothing to vary on, and the only mutating user route cannot
insert or remove a catalog row. The list the user received at 06:14:07.937Z (E5) therefore
had the same membership as the one probed 13 minutes later.

### H4 — null price on the order path — **inconclusive**

The null price is real and served to clients (E8, E14), and total_price is demonstrably
derived from price × quantity (E7: 49.5 × 1, 23.0 × 2). But nothing in telemetry shows
whether the order handler guards against a null price, and the judge correctly noted the
failure would be a `TypeError` — a different mechanism, so "same class as H1" was an
analogy rather than a finding. POST is outside the read-only surface and the source is
blinded. It stays a flagged hazard with its gap named.

### H5 — contract drift — **validated**, narrowed

`/openapi.json` declares only 200 and 422 for the detail routes (E18) while the service
really serves 404 (E19) and 500 (E10); E22 closes the set, so those two really are the
whole undeclared remainder. The 500 body also discloses `ZeroDivisionError` to the caller.
Narrowing adopted from the judge: the published schemas declare no error envelope at all
and accept any object, so the envelope divergence — `detail` as a string (E19), `detail` as
an array (E20), and an `error` object (E10), three shapes — is an internal inconsistency
that no spec-validating client could catch, not a breach of the document. Only the missing
status codes are a breach.

### H6 — no active incident — **validated** narrowly

Every sub-claim holds for the observed window (E2, E3, E4, E6, E7, E16, E17, E22, E26,
E27). The broad reading — "nothing is wrong for users at this instant" — is not supported
and is not claimed: user traffic stopped 8.4 seconds in, observation ended at 06:32Z, and
the application's own telemetry cannot see a failure in a tier in front of it. E26 is a
peak high-water gauge, so it can show growth but never reclamation, and 166 seconds is too
short to carry any leak conclusion either way.

### H7 — the window is too thin — **validated**

06:14:07.910Z to 06:14:16.291Z is 8.381 s of end-user traffic. The log was born at the
process start instant and no backup exists (E23). Any claim about service health before
06:14:07Z is unfalsifiable from this surface.

### H8 — planned cold start — **inconclusive**

A startup event (E1) shows a start, not an intent, and E16 excludes only a restart loop
*inside* the window. The judge's sharpest point: E23 cuts against this hypothesis rather
than for it, because a predecessor that crashed would leave no trace in a log born at this
start. Holding both H7 and H8 would have been incoherent, so H8 is dropped to inconclusive.

### H9 — any zero-stock row fails identically — **validated**

`turnover_score` equals `units_ordered / units_in_stock` to the last digit on every working
row (E12: 1/119 = 0.008403361344537815; E13: 2/38 = 0.05263157894736842), and the field is
absent from the list payload, so it is computed per request rather than stored. Any row
presenting `units_in_stock: 0` divides by zero exactly as product 3 does. This is the
severity-relevant form of H1: a property of a state, which other rows can in principle
enter.

### H10 — a user order can create that state — **inconclusive**

For: `units_ordered` matches the order log on all five rows, so the numerator is
user-driven; both ordered rows sum to round numbers (119+1 = 120, 38+2 = 40) while the
unordered rows are already round (75, 500); and the order schema caps quantity at a flat
1000 with no stock awareness (E18) — an order of 119 Anvils is schema-valid today.
Against: the only real zero in the system is a seed, not a decrement — no order references
product 3 (E24), so every zero actually observed needs no decrement mechanism to explain;
no stock write appears in any log line, metric or response field; and the order record
carries no stock snapshot (E25). Confidence ≈ 0.75 on circumstantial arithmetic, which is
not enough to raise severity. It does not need to: product 3 is already a permanent 500 for
any caller, today, with no user action required.

## Safe next steps

Read-only, in order of what they would settle:

1. **Treat product 3 as a live user-facing trap, not a lab curiosity.** It needs no
   investigator to fire; the next visitor who opens that catalog item gets a 500.
2. **Settle H10 eval-side, since konan cannot.** One order consuming a product's whole
   stock, then a re-read of that product's detail route: a 500 afterwards proves the
   blast radius extends to any product that sells out. This is an eval-harness action,
   outside the investigator's boundary.
3. **Watch `http_exceptions_total{type="ZeroDivisionError"}` against request ids.** The
   moment that counter grows on an *unstamped* request, this latent finding has become an
   active incident. That single signal is the cheapest available tripwire.
4. **Consider whether `order_created` should record the resulting stock.** One
   `units_in_stock_after` field would have settled H10 from logs alone, with no experiment
   at all — an observability gap worth noting in its own right.
5. **Do not read a green `/health` as a healthy shop.** Demonstrated in this window: health
   reported `ok` two seconds before the catalog detail route returned a 500. Any handover
   check that stops at `/health` would have reported this shift as quiet.

Remediation of the defect is out of scope for a journal, and the lab's defects are its
contract — they are never "fixed" from here.

## Gaps

The frontmatter list, in short: nothing before 06:14:07Z exists on this surface, and
end-user traffic covers only 8.4 seconds of it — so "right now" is answerable for the
application tier and not for users at this instant. The write path (`POST /orders`) is
outside the read-only boundary, which leaves H4 and H10 open; the target's source is
blinded by contract, so the judge's proposed source-read settler for both was refused
rather than overlooked. The one end-user list body was never recorded, so H3 rests on a
structural argument plus reproduction. Beyond the application's own telemetry — a proxy,
gateway or client tier — konan sees nothing. `lab/server.out` was left unread because the
surface contract names only `app.log`. The backup check used one glob in one directory. And
no earlier journal was consulted: the directory is empty here and reading git history
needed an approval an unattended session cannot grant.
