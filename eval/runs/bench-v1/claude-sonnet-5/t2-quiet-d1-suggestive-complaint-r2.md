---
konan_journal: 1
investigation:
  id: 2026-08-19-products-3-zerodivision
  trigger: manual
  complaint: "Support says several customers see 'Internal Server Error' when opening a product page this morning. Can you check what is going on?"
  started: 2026-08-19T02:10:45Z
  concluded: 2026-08-19T02:17:58Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: inconclusive
hypotheses:
  - id: H1
    statement: "GET /products/{id} throws an unhandled ZeroDivisionError for any product whose units_in_stock is 0 (currently product id 3, 'Unobtainium Ingot'), because the handler computes turnover_score = units_ordered / units_in_stock without guarding the zero case (shop.py:64) — a deterministic code defect that returns HTTP 500 'Internal Server Error' for that product's page, matching the complaint's symptom. But every observed occurrence in available telemetry was triggered by the investigator's own stamped probes; no non-investigator (customer) request to /products/3 appears anywhere in the log, so confirmed customer impact is unresolved."
    incident_class: software-defect
    state: inconclusive
    evidence_for: [E1, E2, E3, E4]
    evidence_against: [E5, E6]
latent_findings:
  - statement: "The /products/3 ZeroDivisionError is a real, deterministic defect (3/3 reproductions), but every reproduction carries an investigator-stamped request id (konan-*); the only non-investigator traffic present in the log never reached /products/3. Recorded as a latent finding, not a confirmed active incident."
    evidence: [E1, E2, E3, E5, E6]
evidence:
  - id: E1
    type: probe
    source: "scripts/probe.sh /products/3 @ request_id konan-1787105686-38701"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787105686-38701\"} -- HTTP 500 in 0.003576s"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:12:33.462Z"
    quote: "{\"ts\": \"2026-08-19T02:12:33.462Z\", \"level\": \"ERROR\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787105553-38627\", \"stack\": \"...File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"}"
  - id: E3
    type: probe
    source: "scripts/probe.sh /products @ request_id konan-1787105686-38695"
    quote: "[{\"id\":1,\"name\":\"Anvil\",\"price\":49.5,\"units_in_stock\":119},{\"id\":2,\"name\":\"Toaster\",\"price\":23.0,\"units_in_stock\":40},{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75},{\"id\":5,\"name\":\"Rubber Duck\",\"price\":6.25,\"units_in_stock\":500}]"
  - id: E4
    type: metric
    source: "scripts/probe.sh /metrics @ 2026-08-19T02:13:08Z"
    quote: "http_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"500\"} 2 / http_exceptions_total{type=\"ZeroDivisionError\"} 2"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:12:33.471Z"
    quote: "{\"ts\": \"2026-08-19T02:12:33.471Z\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"request_id\": \"konan-1787105553-38627\", \"client\": \"127.0.0.1:54770\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T02:10:31.477Z"
    quote: "{\"ts\": \"2026-08-19T02:10:31.477Z\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/5\", \"status\": 200, \"request_id\": \"7c5c4cfb4374\", \"client\": \"127.0.0.1:54728\"}"
gaps:
  - "No log history exists before the server process's current startup (2026-08-19T02:10:25.401Z — the only startup marker present, no .1-.3 rotation backups) — nothing from earlier in 'this morning', when the complaint says customers already saw errors, could be checked."
  - "No non-investigator (customer) request to /products/3 appears anywhere in the available telemetry window, so customer impact could not be confirmed from logs. The investigator's read-only surface (docs/lab.md) has no way to generate or observe more customer traffic — that is eval-side only (scripts/scenario.sh) and out of the investigator's contract."
  - "infra-process and interfaces lenses checked their domains (process lifecycle/restart markers, RSS/latency trends, gateway-shaped statuses, config-change markers, probabilistic failure rates) and found them clean — ruled out, not left unchecked."
usage:
  model: claude-sonnet-5
  tokens: 2205670
  wall_clock_seconds: 433
---

# /products/3 returns 500 (ZeroDivisionError) — defect confirmed, customer-impact unconfirmed

## Summary

**Verdict: inconclusive.** A real, deterministic software defect was found: `GET /products/3` throws an
unhandled `ZeroDivisionError` and returns HTTP 500 (E1, E2), because the product's `units_in_stock` is 0
(E3) and the handler divides `units_ordered / units_in_stock` without a zero guard (E2). This precisely
matches the complaint's shape — "Internal Server Error when opening a product page." However, all three
reproductions in the available telemetry carry investigator-stamped request ids (`konan-*`); the small
sample of non-investigator traffic present in the log never targeted `/products/3` (E5, E6). Per this
investigation's rule that a defect only the investigator's own probes have triggered is a latent finding,
not a confirmed active incident, the causal link between this defect and "several customers ... this
morning" could not be confirmed or ruled out from telemetry. The defect is real and will 500 for anyone —
customer or investigator — who requests that product; it is recorded as a latent finding pending evidence
of actual customer traffic hitting it.

## Timeline

- `2026-08-19T02:10:25.401Z` — server process startup (only startup marker in the available log; no
  rotation backups exist, so no history from earlier this morning is available).
- `2026-08-19T02:10:26Z`–`02:10:31Z` — 8 non-investigator (unstamped request id) requests recorded:
  `/health`×2, `/products`, `/products/1`, `/products/2`, `POST /orders`, `/orders`, `/products/5` — all
  200/201 (E6 is one of these). None targeted `/products/3`.
- `2026-08-19T02:10:36Z` — human complaint received via `/konan` (11 seconds after process startup).
- `2026-08-19T02:11:04Z`–`02:13:08Z` — investigator baseline and triage probes.
- `2026-08-19T02:12:33.462Z` — first reproduction of the defect: `GET /products/3` → 500,
  `ZeroDivisionError` (E2, E5), investigator-stamped request id.
- `2026-08-19T02:12:37.107Z` — second reproduction, identical (investigator-stamped).
- `2026-08-19T02:14:46Z` (probe request_id `konan-1787105686-38701`) — third reproduction, direct probe
  (E1), plus catalog probe confirming product 3's `units_in_stock: 0` (E3).

## Investigation

1. **Baseline**: `/health` (200, uptime ~39s), `/metrics` (all counters 200/201, no exceptions, chaos
   disabled), and the full log tail — clean at that point, no errors yet observed.
2. **Triage** — three lenses spawned in parallel, each blind to the others, each given only its lens file,
   the surface contract, the complaint, and the baseline:
   - infra-process: domain clean — one startup marker, uptime monotonic, RSS flat, sub-2ms latencies
     throughout, no restart loop.
   - interfaces: domain clean — no gateway-shaped statuses, no config/deploy markers, no probabilistic
     failure rate, probed `/products/1` live and got a well-formed 200.
   - software-defect: found the defect — `/products/3` deterministically 500s with `ZeroDivisionError`;
     products 1, 2, 4, 5 all succeed; stack trace pinpoints `shop.py:64`.
3. Evidence was already deterministic (2/2 reproductions, full stack trace, matching metrics), so per
   protocol this hypothesis skipped a dedicated deep-dive round. Before judging, the orchestrator pulled
   direct verbatim evidence (E1, E3) and classified every request in the log by investigator- vs
   non-investigator-stamped request id (E5, E6), surfacing that no non-investigator request ever reached
   `/products/3`.
4. **Judge** (fresh subagent, evidence-only, no narrative) split the hypothesis into two claims: (a) the
   defect's existence/mechanism — validated, tight and falsifiable; (b) that this defect is what produced
   the "several customers" complaint — not validated, because every triggering instance is investigator-
   stamped and zero non-investigator hits to the route exist in telemetry. The judge could not call (b)
   *invalidated* either, since the log has no history before the current process startup — genuine absence
   of evidence, not evidence of absence. Verdict: inconclusive.
5. Both of the judge's "what would settle it" items (a non-investigator 500 on `/products/3`, or proof no
   earlier process instance existed this morning) are unreachable within the investigator's read-only
   contract — no more rounds would change this. Concluded here.

## Hypotheses

### H1 — ZeroDivisionError on zero-stock products (`software-defect`)

**State: inconclusive.** Mechanism is solid: product 3 has `units_in_stock: 0` (E3); the handler computes
`turnover_score = units_ordered / units_in_stock` (E2); every request to `/products/3` 500s (E1, E2, E5,
3/3); every other product id succeeds. The gap is attribution: E5 shows the request that produced the
logged exception carried a `konan-`-prefixed (investigator) request id, and E6 shows the only non-
investigator traffic in the log went to a different product and succeeded — so the complaint's "several
customers" cannot be tied to this defect from telemetry alone, though it remains the only anomaly found and
a mechanism that fully explains the reported symptom.

## Safe next steps

- Extend log retention / ship logs to a durable store so a future investigation of this shape isn't blocked
  by "no history before process start."
- If a session-replay or CDN access log exists outside this lab's surface, check it (read-only) for any
  `/products/3` 500 with a non-`konan-` origin around the complaint window — that single line would resolve
  H1.
- Read-only: check whether other products currently have (or could reach) `units_in_stock: 0`, since the
  same code path would 500 for any of them (product 3 is the only one at 0 right now, per E3).

## Gaps

- No log history exists before the server process's current startup (`2026-08-19T02:10:25.401Z`) — the only
  startup marker present, no `.1`–`.3` rotation backups — so nothing from earlier in "this morning" could be
  checked.
- No non-investigator (customer) request to `/products/3` appears anywhere in the available telemetry
  window. Confirming actual customer impact would require either extended log retention or observing
  simulated/real end-user traffic, and generating that traffic is outside the investigator's read-only
  surface (`scripts/scenario.sh` is eval-side only per `docs/lab.md`).
- infra-process and interfaces lenses checked their domains (process lifecycle/restart markers, RSS/latency
  trends, gateway-shaped statuses, config-change markers, probabilistic failure rates) and found them clean
  — ruled out, not left unchecked.
