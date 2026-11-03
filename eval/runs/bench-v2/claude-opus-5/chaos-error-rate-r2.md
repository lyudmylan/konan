---
konan_journal: 2
investigation:
  id: 2026-11-03-intermittent-503s
  trigger: >-
    manual — /konan adapter, human profile (docs/triggers.md). Complaint object:
    source=human; fingerprint=human-1793667760; labels.alertname=human-report;
    no severity stated by the reporter, so none recorded; startsAt=2026-11-03T01:02:40Z.
    Investigation entered the loop at 2026-11-03T01:02:59Z (first baseline probe,
    request_id konan-1793667779-14466) — trigger latency 19s.
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-11-03T01:02:59Z
  concluded: 2026-11-03T01:13:41Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: >-
    An operational error-injection switch inside the target was armed at
    2026-11-03T01:02:15.944Z by an inbound request and is still armed; while armed the
    target itself answers a share of business requests with 503 and marks each one as
    injected, so the shop fails intermittently and succeeds on retry.
  incident_class: infra-process
  cause: degradation-switch
hypotheses:
  - id: H1
    statement: >-
      An operational error-injection switch inside the target was armed at 01:02:15.944Z
      (its own event declares failure_rate 0.4, error_status 503, extra_latency_ms 0) and
      remains armed; while armed the target returns 503 to a share of requests on
      /products, /products/{id} and /orders, each 503 carrying the target's own
      injected-failure marker with the same request_id.
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E17, E18, E19, E20]
    evidence_against: []
  - id: H2
    statement: >-
      The target's own code raises an unhandled exception on specific inputs, so
      particular products or orders fail deterministically while others succeed.
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E12, E17, E18]
  - id: H3
    statement: >-
      A boundary component (proxy, load balancer, gateway tier) or an external provider
      is failing or timing out, and the target is relaying its errors.
    incident_class: interfaces
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E3, E5, E6, E18]
  - id: H4
    statement: >-
      A process-lifecycle or resource fault — crash loop, restart, hang, or memory
      exhaustion — is dropping requests.
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E14, E15]
  - id: H5
    statement: >-
      Demand exceeded capacity: queueing or resource exhaustion under volume degraded
      the service.
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E2, E5, E13, E15, E16]
latent_findings:
  - statement: >-
      /health never returned a non-200 in 10 samples while the switch was armed, and no
      non-200 /health series exists in any metrics snapshot, while business routes carried
      503s throughout. Alerting keyed on /health status cannot see this incident class —
      which is exactly why the reporter's dashboard was green. The mechanism (an exempt
      route list, or an injector mounted only on the business routes) is not observable
      from the surface.
    evidence: [E11, E13, E14]
  - statement: >-
      On the item route, successes are counted under the templated path label
      (/products/{product_id}) while failures are counted under the raw path
      (/products/2, /products/5). No single series carries both outcomes for that route,
      so a dashboard grouped by `path` misses the failures silently, and the 503 label set
      grows with every distinct item id. Caveat: every failure observed here was an
      injected one, so whether non-injected non-2xx responses use the raw or the templated
      label is unobserved — this may not survive with the switch disarmed.
    evidence: [E16]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:07.951Z (the only startup event; the file has no rotated backups and begins at process start)"
    quote: |-
      {"ts": "2026-11-03T01:02:07.951Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:12.886Z (last request before the switch; all six request lines between E1 and E3 are 2xx)"
    quote: |-
      {"ts": "2026-11-03T01:02:12.886Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "0343e70c85aa", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.794, "client": "127.0.0.1:63092"}
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:15.944Z (the onset marker; the file holds no disable event and no second enable event)"
    quote: |-
      {"ts": "2026-11-03T01:02:15.944Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "b01a4693e244", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:15.945Z (same request_id as E3; the id carries no konan- prefix, so the arming request was not the investigator's)"
    quote: |-
      {"ts": "2026-11-03T01:02:15.945Z", "level": "INFO", "logger": "faultline.request", "message": "POST /chaos/enable -> 200", "request_id": "b01a4693e244", "event": "request", "method": "POST", "path": "/chaos/enable", "status": 200, "duration_ms": 1.947, "client": "127.0.0.1:63093"}
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:20.125Z (first failure after the switch; marker and access line share request_id a534a5a817cf)"
    quote: |-
      {"ts": "2026-11-03T01:02:20.125Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "a534a5a817cf", "event": "chaos_failure", "method": "GET", "path": "/products/2"}
      {"ts": "2026-11-03T01:02:20.125Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "a534a5a817cf", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.291, "client": "127.0.0.1:63096"}
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:21.182Z (marker and access line share request_id 231418dd90d6)"
    quote: |-
      {"ts": "2026-11-03T01:02:21.182Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "231418dd90d6", "event": "chaos_failure", "method": "POST", "path": "/orders"}
      {"ts": "2026-11-03T01:02:21.182Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "231418dd90d6", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.261, "client": "127.0.0.1:63097"}
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:22.239Z (marker and access line share request_id e0e3a8c82b39)"
    quote: |-
      {"ts": "2026-11-03T01:02:22.239Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "e0e3a8c82b39", "event": "chaos_failure", "method": "GET", "path": "/products"}
      {"ts": "2026-11-03T01:02:22.239Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products -> 503", "request_id": "e0e3a8c82b39", "event": "request", "method": "GET", "path": "/products", "status": 503, "duration_ms": 0.275, "client": "127.0.0.1:63098"}
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:23.294Z (marker and access line share request_id 0d683c739556)"
    quote: |-
      {"ts": "2026-11-03T01:02:23.294Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "0d683c739556", "event": "chaos_failure", "method": "GET", "path": "/products/5"}
      {"ts": "2026-11-03T01:02:23.294Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/5 -> 503", "request_id": "0d683c739556", "event": "request", "method": "GET", "path": "/products/5", "status": 503, "duration_ms": 0.259, "client": "127.0.0.1:63099"}
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:24.352Z (marker and access line share request_id cb980090a68d; with E5–E8 this is 5 of 5 pre-baseline 503s paired to their own injection marker)"
    quote: |-
      {"ts": "2026-11-03T01:02:24.352Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "cb980090a68d", "event": "chaos_failure", "method": "POST", "path": "/orders"}
      {"ts": "2026-11-03T01:02:24.352Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "cb980090a68d", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.249, "client": "127.0.0.1:63100"}
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:25.411Z–01:02:27.530Z (successes interleaved with the failures above, same clients, switch still armed)"
    quote: |-
      {"ts": "2026-11-03T01:02:25.411Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/1 -> 200", "request_id": "8b62a663672e", "event": "request", "method": "GET", "path": "/products/1", "status": 200, "duration_ms": 0.789, "client": "127.0.0.1:63101"}
      {"ts": "2026-11-03T01:02:26.469Z", "level": "INFO", "logger": "faultline.request", "message": "GET /orders -> 200", "request_id": "97c80d123f69", "event": "request", "method": "GET", "path": "/orders", "status": 200, "duration_ms": 0.878, "client": "127.0.0.1:63102"}
      {"ts": "2026-11-03T01:02:27.530Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 200", "request_id": "244695cb68b9", "event": "request", "method": "GET", "path": "/products/4", "status": 200, "duration_ms": 1.039, "client": "127.0.0.1:63103"}
  - id: E11
    type: metric
    source: "/metrics @ 2026-11-03T01:02:59Z, probe request_id konan-1793667779-14473 (the same gauge read 1 in three later samples, the last at 01:06:07Z)"
    quote: |-
      faultline_chaos_enabled 1
  - id: E12
    type: metric
    source: "/metrics @ 2026-11-03T01:02:59Z — the exception counter is declared and carries no series at all; the log holds no unhandled_exception event and no stack field on any line"
    quote: |-
      # HELP http_exceptions_total Unhandled exceptions by Python class name.
      # TYPE http_exceptions_total counter
  - id: E13
    type: metric
    source: "/metrics @ 2026-11-03T01:02:59Z — no /health series with a non-200 status exists in this snapshot or in any later one (a later sample read 10, still with none)"
    quote: |-
      http_requests_total{method="GET",path="/health",status="200"} 3
      http_requests_total{method="GET",path="/products",status="503"} 1
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
      http_requests_total{method="POST",path="/orders",status="503"} 2
  - id: E14
    type: probe
    source: "/health, request_id konan-1793667779-14466, trailer: -- HTTP 200 in 0.001860s request_id=konan-1793667779-14466"
    quote: |-
      {"status":"ok","uptime_seconds":51.272337708156556}
  - id: E15
    type: metric
    source: "/metrics @ 2026-11-03T01:02:59Z (uptime rose monotonically over three samples spanning 187s and back-extrapolates to a start at 01:02:07.94, matching E1; max_rss was byte-identical across all three)"
    quote: |-
      process_uptime_seconds 51.789127374999225
      process_max_rss_bytes 46956544
  - id: E16
    type: metric
    source: "/metrics @ 2026-11-03T01:02:59Z — successes and failures on the one item route carry different path labels"
    quote: |-
      http_requests_total{method="GET",path="/products/{product_id}",status="200"} 5
      http_requests_total{method="GET",path="/products/2",status="503"} 1
      http_requests_total{method="GET",path="/products/5",status="503"} 1
  - id: E17
    type: probe
    source: "/products probed twice, 2.2s apart, identical URL and no parameters — trailer lines verbatim"
    quote: |-
      -- HTTP 200 in 0.001387s request_id=konan-1793667937-14731
      -- HTTP 503 in 0.000925s request_id=konan-1793667939-14741
  - id: E18
    type: probe
    source: "/products 503 response body, probe request_id konan-1793667939-14741 — every observed 503 across /products, /products/{id} and /orders returned this one envelope, carrying the target's own request id"
    quote: |-
      {"error":"service temporarily degraded","request_id":"konan-1793667939-14741"}
  - id: E19
    type: metric
    source: "/metrics @ 2026-11-03T01:02:59Z — the arming request counted once, matching E4; the counter stayed at 1 in every later sample"
    quote: |-
      http_requests_total{method="POST",path="/chaos/enable",status="200"} 1
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-11-03T01:02:10.830Z (the one order attempt before the switch; the two attempts after it are E6 and E9)"
    quote: |-
      {"ts": "2026-11-03T01:02:10.829Z", "level": "INFO", "logger": "faultline.shop", "message": "order created", "request_id": "15c5c2db618f", "event": "order_created", "order_id": 1, "product_id": 1, "quantity": 1, "total_price": 49.5}
      {"ts": "2026-11-03T01:02:10.830Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "15c5c2db618f", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.961, "client": "127.0.0.1:63091"}
gaps:
  - "The declared failure_rate of 0.4 (E3) is the switch's own self-report, never measured independently. The observed share is 5 of 10 non-investigator business requests after the switch — n=10, roughly a 19–81% interval — and those five failures arrived as one unbroken run, which an independent 0.4 draw would produce about 1% of the time. The selector may be stateful or counter-based rather than random; the distribution is not established. E17 shows only that the outcome is not a function of the input URL."
  - "Whether the injection sits above the handler is inferred, not proven: the failure path is 3–5x cheaper than the success path on the same route (E5 0.291ms against E2 0.794ms) and failures are recorded with a raw rather than a templated route label (E16), both consistent with a short-circuit before route resolution. The mount point — middleware, dependency or handler — is not visible on this surface."
  - "The failing traffic is not the investigator's: the konan- request-id prefix separates it cleanly. But non-investigator is not the same as an end user. Every client address in evidence is loopback with contiguous ports (63091–63103) inside a nine-second burst, which is the shape of a scripted driver, not organic demand. Impact is therefore stated as impact on non-investigator traffic, not as a count of affected people."
  - "Counters after 01:02:59Z are contaminated by the investigation's own probes — the triage lenses re-probed paths that had just failed, taking /products/2 503s from 1 to 5. Every user-impact number here comes from the 01:02:59Z baseline snapshot and the pre-baseline log window only."
  - "This repo ships three lenses (software-defect, infra-process, interfaces). No load-saturation, third-party, or data-db lens exists, so those three domains were excluded from telemetry by the orchestrator rather than swept by a specialist. For this target the exclusion is cheap — docs/lab.md records that faultline has no database and no third-party dependency — but load-saturation got no dedicated sweep."
  - "No CPU, thread, worker, or connection-pool metric exists on the surface, so CPU burn and worker starvation are unobservable rather than excluded. process_max_rss_bytes is a high-water mark by definition (E15): its flatness bounds the peak at about 46.9MB and excludes memory exhaustion, but it cannot show current RSS."
  - "/metrics publishes only the boolean switch gauge (E11), never the failure rate or the injected status. The values 0.4 and 503 rest on the single log line E3; if that line had rotated away, the switch's parameters would be unrecoverable from the surface."
  - "The probe allowlist is GET-only, so the investigator could not exercise order creation. All POST /orders evidence (E6, E9, E20) is non-investigator traffic: 1 of 1 attempt succeeded before the switch, 0 of 2 after it — a real signal, but n=3."
  - "Who armed the switch, and why, is outside the telemetry surface. E4 carries a loopback client address and no identity. A human could have armed it in response to trouble in an earlier process lifetime; the log begins at this process's start (E1), so no earlier history is reachable. That residual does not touch the causation of the observed 503s, each of which the target attributes to injection."
  - "Whether non-injected non-2xx responses carry the raw or the templated path label is unobserved, so the second latent finding's reach beyond the armed switch is unconfirmed. A 404 or 422 on the item route would settle it."
  - "The switch's current state was last read at 01:06:07Z. The condition is ongoing as of that reading, not as of this journal's conclusion."
usage:
  model: claude-opus-5
  tokens: 2446858
  wall_clock_seconds: 642
---

# Intermittent 503s across the shop while an error-injection switch is armed

## Summary

**Root cause identified.** An operational error-injection switch inside the target was
armed at 2026-11-03T01:02:15.944Z by an inbound request, and it was still armed at the
last reading (E3, E4, E11, E19). While armed, the target answers a share of business
requests with HTTP 503 and writes its own injected-failure marker for each one — 5 of 5
pre-baseline 503s pair to such a marker by shared request_id (E5–E9). Incident class
`infra-process`, cause `degradation-switch`.

This is the healthy-monitoring trap in its textbook form, and the reporter's green
dashboard is a true reading, not a broken one: /health sits outside the failure path and
returned 200 in all 10 samples taken while the switch was armed, with no non-200 /health
series in any snapshot (E13, E14). The business surface is where the incident lives.

Impact, counted from non-investigator traffic only: 5 of 10 business requests failed in
the nine seconds after the switch was armed, across /products, /products/{id} and
/orders (E5–E10). Order creation is the sharpest edge — 1 of 1 attempt succeeded before
the switch, 0 of 2 after it (E20, E6, E9). Successes continued interleaved throughout
(E10), which is exactly the "works again on retry" the reporter described.

**Confidence: high on cause, onset and locus; low on rate.** The 0.4 figure is the
switch's self-report, and the five observed failures arrived as one unbroken run — a
shape an independent 40% draw makes unlikely. Treat "about 40% of requests" as the
switch's declaration, not as a measurement. Nothing in the evidence supports a claim
about how many real end users were hit; see Gaps.

## Timeline

| Time (UTC) | Event | Evidence |
| --- | --- | --- |
| 01:02:07.951 | Process starts: faultline 0.1.0. One startup event in the whole file; no restart anywhere after it. | E1 |
| 01:02:08.689–01:02:12.886 | Six requests, all 2xx — the clean control window. Includes `GET /products/2 -> 200`, the same path that fails 7s later. | E2 |
| 01:02:10.830 | `POST /orders -> 201`, order 1 created. The only successful order in the record. | E20 |
| **01:02:15.944** | **Configuration change: the error-injection switch is armed** — `failure_rate: 0.4`, `error_status: 503`, `extra_latency_ms: 0`. | E3 |
| 01:02:15.945 | The arming request itself: `POST /chaos/enable -> 200`, same request_id, no `konan-` prefix — not the investigator. | E4, E19 |
| 01:02:20.125 | First failure, 4.18s after the switch: `GET /products/2 -> 503`, preceded by its own injected-failure marker. | E5 |
| 01:02:21.182 | `POST /orders -> 503` — order creation starts failing. | E6 |
| 01:02:22.239 | `GET /products -> 503`. | E7 |
| 01:02:23.294 | `GET /products/5 -> 503`. | E8 |
| 01:02:24.352 | `POST /orders -> 503` — second failed order. | E9 |
| 01:02:25.411–01:02:27.530 | Three successes interleaved, switch still armed: `/products/1`, `/orders`, `/products/4`. | E10 |
| 01:02:40 | Human reports the complaint (`startsAt` of the complaint object). | — |
| 01:02:59 | Investigation enters the loop; baseline captured. Switch gauge reads 1. | E11, E14 |
| 01:06:07 | Last reading of the switch gauge: still 1. No disable event exists in the log. | E3, E11 |

## Investigation

**Baseline** (01:02:59Z): /health 200, a full /metrics snapshot, and the complete
31-line log — which, because the process had been up only 51s, covered the target's
entire lifetime with no rotated backups. That is an unusually clean window: the control
period, the configuration change, and the failures all sit inside one file.

**Triage** — three lenses in parallel, each blind to the others, each given only its
lens file, the surface contract, the verbatim complaint, and the baseline summary:
software-defect, infra-process, interfaces. Those are the three this repo ships; the
load-saturation, third-party and data-db domains were excluded from telemetry by the
orchestrator instead, and that shortcut is recorded in Gaps rather than hidden.

All three converged on the same onset marker, and two of them declined to own it — the
interfaces lens explicitly classified the mechanism as an internal operational switch
and handed it to `infra-process`. That is the triage design working: agreement reached
independently, by lenses that could not see each other's findings.

**Deep-dive: skipped, deliberately.** H1's triage evidence was already deterministic and
complete — every 503 paired to its own injection marker, the switch event quoted, the
gauge still reading 1 — and the competing hypotheses already carried positive
disconfirming evidence, not merely absent support. The loop's rule is that deep-dives
exist to fill evidence gaps, not to re-prove, so H1 went straight to the judge.

**Judge** (fresh agent, evidence-only, no narrative): validated H1's core and **struck
three clauses from it**, which is the most useful thing that happened in this
investigation. It refused "a random ~40% share" (the rate is declared, not measured; the
five failures form one run), refused "before the handler runs" as over-read from the
latency figures alone, and refused to judge the match to the complaint at all, since the
complaint text is deliberately outside its firewall — that last one the orchestrator
holds, and it holds up on onset and symptom shape. The judge also caught a genuine
under-citation: the first ledger quoted only three marker/503 pairs while claiming a 1:1
relationship. The ledger now quotes all five pre-baseline pairs (E5–E9), so the pairing
is carried by citation rather than by assertion. H2–H5 were confirmed invalidated, each
on positive evidence; H5's citations were re-pointed at the counter magnitudes and
latency shape, since the originally cited evidence did not carry the refutation.

## Hypotheses

### H1 — error-injection switch armed inside the target — **validated**

For: the control window is clean (E2), the switch event declares its own parameters
(E3), the arming request is a non-investigator inbound call the target answered 200 (E4,
E19), the first failure follows 4.18s later (E5), all five pre-baseline 503s carry their
own injection marker with a shared request_id (E5–E9), successes interleave throughout
(E10), the gauge still reads 1 (E11), the same URL yields both outcomes 2.2s apart
(E17), and every 503 carries one envelope minted by the target itself (E18).

Against: nothing found.

Reverse causation is excluded for this process lifetime: the six requests before the
switch were all 2xx (E2), so there were no failures to react to, and the switch was
armed by a deliberate inbound call (E4) rather than by an internal reaction.

### H2 — data-dependent unhandled exception in the target's code — **invalidated**

Against: `http_exceptions_total` is declared with HELP and TYPE and carries no series at
all (E12) — the instrumentation exists and never fired, so this is a positive negative,
not an absence argument. The log has no `unhandled_exception` event and no `stack` field.
E17 kills the data-dependent half directly: the identical URL returned 200 and then 503
within 2.2s, so the outcome is not a function of the input. The 503 body is a clean
structured envelope, not a leaked traceback (E18). One non-zero `http_exceptions_total`
series would reopen this.

### H3 — failing boundary component or external provider — **invalidated**

Against: the 503s carry the target's own request_id and its own envelope (E5, E6, E18)
and return in 0.249–0.291ms (E5, E6, E9) — too fast for any hop off the box. The switch
event declares `extra_latency_ms: 0` (E3), which is why no latency signal exists
anywhere to support a timing-out dependency. Scope correction from the judge, and it is
fair: this shows the target minted these 503s itself, not that no proxy stands in front
of it. One outbound-call log line or dependency metric inside the failure window would
reopen it; the surface publishes neither.

### H4 — process-lifecycle or resource fault — **invalidated**

Against: one startup event in a file that begins at process start (E1); uptime rose
monotonically across three samples and back-extrapolates to 01:02:07.94, matching that
event, so the process that logged startup is the process that served the snapshot (E14,
E15); request counters only ever rose. Sub-2ms durations throughout exclude a hang. A
second startup event or a non-monotone uptime would reopen it.

### H5 — load saturation — **invalidated**

Against: total traffic is in the tens of requests across four minutes — /health counted
3 at baseline, the item route 5 lifetime successes (E13, E16) — against flat sub-2ms
latency on every path (E2, E15). Decisively, failures are *faster* than successes (E5 at
0.291ms against E2 at 0.794ms), which is the opposite of queueing and shedding. An
accept-level or queue-depth metric showing volume that `http_requests_total` never saw
would reopen it; the surface publishes none.

## Safe next steps

Read-only only. Remediation is out of scope for this journal, and the operator decision
that follows from the first item is not the investigator's to make.

1. Re-read `faultline_chaos_enabled` on /metrics. While it reads 1, the condition is
   ongoing and the failures continue; that single gauge is the live status of this
   incident.
2. Correlate the arming request's client address (E4, `127.0.0.1:63093`) with whatever
   access records exist outside the target, to establish who armed the switch. The
   target's own telemetry carries no identity beyond that address.
3. Review what the health dashboard actually measures. It reported green truthfully
   throughout a heavy business error rate (E13, E14); any alert keyed on /health status
   is blind to this incident class. A business-surface error-rate signal is what was
   missing.
4. Before trusting a per-route error rate from /metrics, note the label split on the
   item route (E16): grouping by `path` puts successes and failures in different series,
   so the failures are invisible to that query.

## Gaps

The frontmatter list, in short: the 0.4 failure rate is declared by the switch and not
measured (n=10, and the five failures form one unbroken run, so the selector's
distribution is unknown); the injection's mount point above the handler is inferred from
the cheaper failure path and the raw route label, not proven; the failing traffic is
provably not the investigator's but all of it is loopback with contiguous ports in a
nine-second burst, so it reads as a scripted driver and no claim about real end users is
supported; counters after 01:02:59Z are contaminated by the investigation's own probes,
so every impact number here comes from the baseline window; only three lenses exist in
this repo, so load-saturation, third-party and data-db were excluded by the orchestrator
from telemetry rather than swept; no CPU, worker or connection-pool metric exists, and
`process_max_rss_bytes` is a high-water mark that cannot show current RSS; /metrics
publishes only the boolean switch gauge, so the 0.4 and 503 parameters rest on one log
line; the GET-only probe allowlist meant order creation could not be exercised, leaving
the order impact at n=3; who armed the switch and why is outside the telemetry surface;
whether non-injected non-2xx responses use the raw or templated path label is unobserved;
and the switch's state was last read at 01:06:07Z, not at this journal's conclusion.
