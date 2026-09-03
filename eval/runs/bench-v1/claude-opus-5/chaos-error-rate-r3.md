---
konan_journal: 1
investigation:
  id: 2026-08-19-chaos-injection-503s
  trigger: "manual — /konan human report; complaint object: source=human, fingerprint=human-1787112153, labels.alertname=human-report (no severity stated by reporter), startsAt=2026-08-19T04:02:33Z; investigation started 2026-08-19T04:02:42Z (trigger latency 9s)"
  complaint: "Users report the shop is intermittently failing — some page loads and orders error out, then work again on retry. It started suddenly a few minutes ago. Our health dashboard is green."
  started: 2026-08-19T04:02:42Z
  concluded: 2026-08-19T04:08:27Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime fault-injection configuration ('chaos mode') was enabled at 2026-08-19T04:02:14.072Z with failure_rate 0.4 and error_status 503, short-circuiting a random subset of business-route requests to 503 in middleware before route resolution, while /health was unaffected."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "A runtime fault-injection configuration ('chaos mode') was enabled at 04:02:14.072Z with failure_rate 0.4 and error_status 503, causing a random subset of business-route requests (/products, /products/{id}, POST /orders) to return 503 while /health kept returning 200."
    incident_class: infra-process
    state: validated
    evidence_for: [E2, E3, E4, E5, E6, E7, E8, E10, E11, E12, E16]
    evidence_against: []
  - id: H2
    statement: "An application code defect — a data-dependent failure affecting specific product ids — is returning 503 for some inputs."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E5, E6, E7, E9, E11, E12]
  - id: H3
    statement: "Resource saturation, a crash loop, or a process restart caused the errors."
    incident_class: load-saturation
    state: invalidated
    evidence_for: []
    evidence_against: [E1, E9, E12, E14]
  - id: H4
    statement: "The observed failures were induced by the investigator's own read-only probes rather than by non-investigator traffic."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E13, E15]
latent_findings:
  - statement: "The /health contract covers liveness only — it reports status and uptime_seconds and asserts nothing about business-route success or fault-injection state — so it read green at 04:02:47Z while chaos mode was still enabled. This is a monitoring-coverage gap, real but not the cause of the 503s. The signal IS exposed on /metrics as faultline_chaos_enabled, so the gap is in the health contract, not in the telemetry."
    evidence: [E8, E10, E15, E16]
  - statement: "Fault injection is still active at 2026-08-19T04:07:55Z, roughly 5.5 minutes after onset — the failure burst in the log stopped only because non-investigator traffic stopped at 04:02:25.654Z, not because the fault was cleared."
    evidence: [E16, E18]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-19T04:02:06.081Z"
    quote: '{"ts": "2026-08-19T04:02:06.081Z", "level": "INFO", "logger": "faultline.app", "message": "faultline 0.1.0 started", "event": "startup", "version": "0.1.0"}'
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-19T04:02:14.072Z"
    quote: '{"ts": "2026-08-19T04:02:14.072Z", "level": "WARNING", "logger": "faultline.chaos", "message": "chaos mode enabled", "request_id": "ea146c08e2c7", "event": "chaos_enabled", "enabled": true, "failure_rate": 0.4, "error_status": 503, "extra_latency_ms": 0}'
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-19T04:02:16.131Z"
    quote: '{"ts": "2026-08-19T04:02:16.131Z", "level": "WARNING", "logger": "faultline.request", "message": "chaos-injected failure", "request_id": "1f81fe6e04f3", "event": "chaos_failure", "method": "GET", "path": "/products"}'
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-19T04:02:11.010Z"
    quote: '{"ts": "2026-08-19T04:02:11.010Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 200", "request_id": "b303f0f84cf6", "event": "request", "method": "GET", "path": "/products/2", "status": 200, "duration_ms": 0.784}'
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-19T04:02:18.246Z"
    quote: '{"ts": "2026-08-19T04:02:18.246Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/2 -> 503", "request_id": "038b73733cdd", "event": "request", "method": "GET", "path": "/products/2", "status": 503, "duration_ms": 0.276}'
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-19T04:02:19.300Z"
    quote: '{"ts": "2026-08-19T04:02:19.300Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 503", "request_id": "af373b7c8cca", "event": "request", "method": "POST", "path": "/orders", "status": 503, "duration_ms": 0.264}'
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-19T04:02:22.475Z"
    quote: '{"ts": "2026-08-19T04:02:22.475Z", "level": "INFO", "logger": "faultline.request", "message": "POST /orders -> 201", "request_id": "750cd2e2109c", "event": "request", "method": "POST", "path": "/orders", "status": 201, "duration_ms": 1.27}'
  - id: E8
    type: metric
    source: "/metrics scraped 2026-08-19T04:02:51Z (request_id konan-1787112171-43547)"
    quote: "faultline_chaos_enabled 1"
  - id: E9
    type: metric
    source: "/metrics scraped 2026-08-19T04:02:51Z (request_id konan-1787112171-43547)"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n(no series emitted — zero unhandled exceptions over the whole process lifetime)"
  - id: E10
    type: metric
    source: "/metrics scraped 2026-08-19T04:02:51Z (request_id konan-1787112171-43547)"
    quote: "http_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"503\"} 2\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 4\nhttp_requests_total{method=\"GET\",path=\"/products/2\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/4\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/5\",status=\"503\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"503\"} 1\nhttp_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3"
  - id: E11
    type: log
    source: "lab/logs/app.log, 33 lines spanning 2026-08-19T04:02:06.081Z–04:02:51.486Z, one startup line, no rotation backups"
    quote: "Six \"event\": \"chaos_failure\" lines — 04:02:16.131Z (GET /products), 04:02:18.246Z (GET /products/2), 04:02:19.300Z (POST /orders), 04:02:20.358Z (GET /products), 04:02:21.416Z (GET /products/5), 04:02:25.654Z (GET /products/4) — matching the six 503 responses in E10 one-to-one, with no unexplained 503 residue."
  - id: E12
    type: log
    source: "lab/logs/app.log, 2026-08-19T04:02:16.131Z–04:02:25.654Z"
    quote: "All six 503 responses carry duration_ms between 0.259 and 0.283; 200/201 responses on the same routes in the same window carry duration_ms between 0.784 and 1.931."
  - id: E13
    type: log
    source: "lab/logs/app.log, 2026-08-19T04:02:16.131Z–04:02:25.654Z"
    quote: "Every request_id associated with a 503 — 1f81fe6e04f3, 038b73733cdd, af373b7c8cca, f5116f220f8d, 9c17a01d61bb, cc2b489d2690 — is an unstamped 12-hex-char id. Investigator probes carry the \"konan-\" prefix."
  - id: E14
    type: metric
    source: "/metrics scraped 2026-08-19T04:02:51Z (request_id konan-1787112171-43547)"
    quote: "process_uptime_seconds 45.41527379117906\nprocess_max_rss_bytes 47333376"
  - id: E15
    type: probe
    source: "GET /health, request_id konan-1787112167-43534, 2026-08-19T04:02:47Z"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":41.53835920803249}\n-- HTTP 200 in 0.001398s"
  - id: E16
    type: metric
    source: "/metrics scraped 2026-08-19T04:07:55Z (request_id konan-1787112475-43690)"
    quote: "faultline_chaos_enabled 1\nprocess_uptime_seconds 349.8447829161305"
  - id: E17
    type: probe
    source: "GET /products x3, request_ids konan-1787112465-43661, konan-1787112465-43667, konan-1787112466-43673, 2026-08-19T04:07:45Z–04:07:46Z"
    quote: "-- HTTP 200 in 0.001564s\n-- HTTP 200 in 0.001344s\n-- HTTP 200 in 0.001359s"
  - id: E18
    type: log
    source: "lab/logs/app.log @ 2026-08-19T04:02:25.654Z"
    quote: '{"ts": "2026-08-19T04:02:25.654Z", "level": "INFO", "logger": "faultline.request", "message": "GET /products/4 -> 503", "request_id": "cc2b489d2690", "event": "request", "method": "GET", "path": "/products/4", "status": 503, "duration_ms": 0.271} — the last non-investigator request in the log; all later lines carry konan- request ids.'
gaps:
  - "No /health response is timestamped inside the failure burst (04:02:16.131Z–04:02:25.654Z). The health-coverage finding rests on a green /health at 04:02:47Z while chaos was still enabled (E15, E16), not on a green health check concurrent with a live 503."
  - "Health's exemption from injection is inferred, not proven: only 5 /health calls exist and none returned 503. At failure_rate 0.4 an unexempt endpoint would pass 5 times with probability ~0.08, so exemption is likely but not established from telemetry alone."
  - "Who enabled chaos mode, and why, is not identifiable from the investigator's surface. The enabling request (ea146c08e2c7, E2) is unstamped, and /chaos is operator surface excluded from the probe allowlist by docs/lab.md."
  - "The injection rate was not measured. The 0.4 figure is read from the configuration marker (E2); observed non-investigator failures were 6 of 13 business requests over ~10 seconds, and 3 confirmation probes of /products all returned 200 (E17) — a non-reproduction on far too few samples to refute or measure a 0.4 rate."
  - "The log begins at process start (04:02:06.081Z) with no rotation backups, so no telemetry exists for any period before that. If the complaint refers to an earlier window, this investigation cannot speak to it."
  - "Impact is inferred from server-side counters on non-investigator traffic (E13). There is no client-side or end-user telemetry on the investigator's surface, so the reporter's 'users' could not be corroborated directly."
  - "Two of three triage lenses had scripts/probe.sh denied by the permission system and worked from logs and metrics only; one denial also occurred in the main session on a piped probe form. No live reproduction was obtained from those lenses, and per the boundary rule the denials were not worked around."
usage:
  model: claude-opus-5
  tokens: 1634705
  wall_clock_seconds: 345
---

# Intermittent 503s on shop routes from an enabled fault-injection flag

## Summary

**Root cause identified.** A runtime fault-injection configuration — faultline's "chaos
mode" — was enabled at `2026-08-19T04:02:14.072Z` with `failure_rate: 0.4` and
`error_status: 503` (E2). From that moment, a random subset of business-route requests
was short-circuited to 503 in middleware before the request reached handler code, while
`/health` continued to return 200. This reproduces every element of the complaint: page
loads and orders erroring out, the same route working moments later, a sudden onset a
few minutes ago, and a green health dashboard.

The mechanism is confirmed rather than inferred. Each of the six 503 responses in the
metrics snapshot has a matching `chaos_failure` log line, one-to-one, with no
unexplained 503 left over (E10, E11) — so no residual failure needs another
explanation. `/products/2` returned 200 at `04:02:11.010Z` and 503 at `04:02:18.246Z`
(E4, E5), which straddles the flag flip and rules out any input-dependent defect. The
503s return in 0.26–0.28 ms against 0.78–1.93 ms for successes on the same routes (E12),
the signature of a short-circuit above the application. `http_exceptions_total` is empty
(E9): nothing crashed.

Two details matter for response. **The fault is still active** — `faultline_chaos_enabled 1`
at `04:07:55Z` (E16). The failure burst in the log ends at `04:02:25.654Z` only because
non-investigator traffic stopped there (E18), not because anything recovered; the shop
will fail again as soon as traffic resumes. And the green dashboard is not a monitoring
outage: `/health` reports liveness only, and the injection state is already exposed on
`/metrics` as `faultline_chaos_enabled` — the gap is in what the health check asserts,
not in what the service publishes.

Confidence is high on the mechanism and on the fault still being enabled. Confidence is
lower on the failure *rate*: 0.4 is read from the configuration marker, never measured,
and three confirmation probes of `/products` all returned 200 (E17) — too few samples to
say anything. Who enabled the flag is not answerable from the investigator's surface.

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 04:02:06.081Z | faultline 0.1.0 starts; the only startup in the log | E1 |
| 04:02:06.8–04:02:11.0Z | Six non-investigator requests, zero failures — the healthy baseline | E4 |
| **04:02:14.072Z** | **Config-change marker: chaos mode enabled, failure_rate 0.4, error_status 503** | **E2** |
| 04:02:16.131Z | First injected failure, 2.06s after the flip: `GET /products` → 503 | E3 |
| 04:02:18.246Z | `GET /products/2` → 503 — the same path that returned 200 at 04:02:11 | E4, E5 |
| 04:02:19.300Z | `POST /orders` → 503 — order path now affected | E6 |
| 04:02:22.475Z | `POST /orders` → 201 — succeeds between two failures | E7 |
| 04:02:25.654Z | Last injected failure and last non-investigator request | E11, E18 |
| 04:02:33Z | Human reports the complaint (`startsAt`) | — |
| 04:02:42Z | Investigation starts (trigger latency 9s) | — |
| 04:02:47Z | `/health` probed: 200, green, while chaos still enabled | E15 |
| 04:02:51Z | Baseline metrics: `faultline_chaos_enabled 1`, no exceptions, no restart | E8, E9, E14 |
| 04:07:45–04:07:55Z | Confirmation probes: 3× `/products` → 200; **chaos still enabled** | E16, E17 |

## Investigation

**Baseline.** `/health` returned 200 with `uptime_seconds` 41.5 (E15), and the metrics
snapshot showed 503s already recorded against `/products`, `/products/{id}` and
`POST /orders` alongside successes (E10). Uptime placed process start at 04:02:06.081Z,
which meant the 33-line log covered the *entire* process lifetime — nothing was hidden
before it.

**Triage — three lenses in parallel, each blind to the others.** All three were spawned
because a vague complaint cannot exclude any domain by evidence.

- *infra-process*: domain clean. One startup line, monotonic uptime across three samples,
  RSS flat at ~47 MB, no connection refusals; and the 503s were *faster* than the
  successes, the opposite of a saturation signature (E12, E14).
- *software-defect*: domain clean, and it killed the data-dependent shape outright — the
  same input `/products/2` produced both 200 and 503 seven seconds apart (E4, E5), and
  `http_exceptions_total` was empty (E9).
- *interfaces*: found the onset marker and the health-contract gap, and established the
  before/after split — 6 requests and 0 failures before the flip, 6 failures after.

**Deep-dive: skipped, deliberately.** The contract sends a hypothesis straight to the
judge when its triage evidence is already deterministic and complete. The 1:1
`chaos_failure`→503 mapping (E11) left no evidence gap for a deep-dive to fill.

**Judge.** One fresh judge received only the hypothesis list and the verbatim evidence
ledger — no lens reasoning, no narrative. It validated H1, invalidated H2, H3 and H4,
and corrected several over-reads in my draft framing, all of which are reflected above:
the 0.4 rate is configured and not measured; "succeeds on retry" is really "the same
route yields both outcomes" since no literal retry appears in telemetry; health's
exemption from injection is inferred from very few samples; and "user-visible" is an
inference from unstamped server-side traffic, not from user telemetry. It also observed
that the 503 counters use raw paths (`/products/2`) while the 200 counters use the route
template (`/products/{product_id}`), placing the injection *before* route resolution —
independent support for the middleware mechanism.

**One targeted follow-up.** The judge named the single piece of evidence that would
settle the health-coverage finding in its strong form: a `/health` line timestamped
inside the failure burst. That is not obtainable retroactively, so I probed the
prediction forward instead — 3× `/products` then `/health`. All returned 200 (E17), so
the strong form remains unsettled; but the same round established the load-bearing fact
that chaos is *still enabled* (E16).

## Hypotheses

### H1 — Fault injection enabled at 04:02:14.072Z — **validated**

Cause statement: chaos mode was enabled with `failure_rate 0.4` and `error_status 503`,
short-circuiting a random subset of business-route requests in middleware.

*For*: the config-change marker itself (E2); the first failure 2.06s later (E3); the 1:1
mapping of six `chaos_failure` lines to six 503s with no residue (E10, E11); the
pre/post flip contrast on an identical input (E4, E5); the fail-fast duration signature
(E12); order path both failing and succeeding within three seconds (E6, E7); and the
gauge still reading 1 at both 04:02:51Z and 04:07:55Z (E8, E16).

*Against*: nothing found. The prediction — that the flag is set and business routes fail
while health does not — held on every check.

### H2 — Data-dependent application defect — **invalidated**

*Against*: `/products/2` returned 200 then 503 across the flip (E4, E5), so the outcome
is not a function of the input. `POST /orders` both failed and succeeded (E6, E7). Every
503 is already accounted for by an injection line (E11), leaving nothing for a code path
to explain. No unhandled exceptions at all (E9). The 503s are *cheaper* than the
successes (E12); a data-dependent defect normally costs work rather than saving it. The
raw-path 503 labels in E10 look like specific ids failing — that is a labelling artifact
of the pre-route short-circuit, not a data pattern.

### H3 — Saturation, crash loop, or restart — **invalidated**

*Against*: exactly one startup line and no rotation backups (E1, E11); uptime monotonic
and consistent with that start (E14, E16); RSS flat at ~47 MB (E14); every response
under 2 ms with `extra_latency_ms: 0` in the config marker (E12, E2); no exceptions
(E9). Scoped to the observed window — no telemetry exists before 04:02:06.081Z.

### H4 — Investigator-induced failures — **invalidated**

*Against*: all six failing request ids are unstamped 12-hex ids while investigator
probes carry the `konan-` prefix (E13), and every investigator probe returned 200 (E15,
E17). The first 503 at 04:02:16.131Z also precedes the first konan probe at ~04:02:47Z.
The impact counted here is therefore non-investigator traffic only, as the prime
directive requires.

## Safe next steps

Read-only only; remediation is out of scope for this journal and for konan.

1. **Treat this as ongoing, not resolved.** `faultline_chaos_enabled` still reads 1 (E16).
   Re-scrape `/metrics` to confirm current state before anyone closes the report — the
   quiet log is absence of traffic (E18), not recovery.
2. **Ask the operator who enabled chaos mode at 04:02:14.072Z** and whether it was
   intentional. Request `ea146c08e2c7` is unstamped and `/chaos` is outside the
   investigator's surface, so this is not answerable from telemetry.
3. **Measure the real failure rate** with a larger sample of business-route probes if a
   rate figure is needed; 0.4 is currently a configured value, not an observed one.
4. **Consider whether the health check should surface `faultline_chaos_enabled`.** The
   signal is already on `/metrics`; a dashboard that alerted on the gauge, or on the
   business-route 5xx ratio, would not have read green during this incident.

## Gaps

The full list is in the machine core. The ones that most limit this conclusion:

- No `/health` sample inside the failure burst, so the health-coverage finding is
  supported in its weaker form only — green health while injection was enabled, not
  green health concurrent with a live 503.
- Health's exemption from injection is likely (5 calls, 0 failures) but not proven from
  telemetry.
- The actor behind the config change is outside the investigator's surface by design.
- The failure rate was never measured; the 3 confirmation probes returning 200 (E17) are
  a non-reproduction on too small a sample to mean anything either way.
- No telemetry exists before process start at 04:02:06.081Z.
- No client-side telemetry exists, so the reporter's "users" are corroborated only
  indirectly, via unstamped server-side traffic.
- Two triage lenses were denied `scripts/probe.sh` by the permission system and worked
  from logs and metrics alone; the denials were not worked around, per the boundary rule.
