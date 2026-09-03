---
konan_journal: 1
investigation:
  id: 2026-08-25-shop-wide-slowness-chaos-latency
  trigger: "manual — /konan human profile; fingerprint human-1787633230; alertname human-report; startsAt 2026-08-25T04:47:10Z; investigation start 2026-08-25T04:47:24Z (trigger latency 14 s)"
  complaint: "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast."
  started: 2026-08-25T04:47:24Z
  concluded: 2026-08-25T04:52:04Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A runtime configuration change at 2026-08-25T04:46:54Z enabled chaos mode with extra_latency_ms 1500 (failure_rate 0.0), injecting a per-request variable delay of up to ~1.2 s observed into every shop route while /health and /metrics stay exempt; the flag is still active."
  incident_class: interfaces
hypotheses:
  - id: H1
    statement: "Runtime config change — chaos mode enabled at 04:46:54Z with extra_latency_ms 1500 and failure_rate 0.0 — injects a per-request, variable delay into /products, /products/{id} and /orders, exempting /health and /metrics; still active, so the slowdown is ongoing."
    incident_class: interfaces
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E16, E17, E19, E21, E22]
    evidence_against: []
  - id: H2
    statement: "A code defect (unhandled exception or 5xx on some route or input) produced the reported error page and contributes to the slowness."
    incident_class: software-defect
    state: invalidated
    evidence_for: []
    evidence_against: [E4, E13, E14, E18]
  - id: H3
    statement: "The process crashed/restarted or saturated (memory/CPU) during the window, causing the slowness and a transient error page."
    incident_class: infra-process
    state: invalidated
    evidence_for: []
    evidence_against: [E15, E16, E17, E18, E20]
evidence:
  - id: E1
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:46:48.807Z"
    quote: "{\"ts\": \"2026-08-25T04:46:48.807Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 200\", \"request_id\": \"d62f7e40fe58\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 1.228, \"client\": \"127.0.0.1:65364\"}"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:46:49.873Z"
    quote: "{\"ts\": \"2026-08-25T04:46:49.873Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"f4263730dc19\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 1.001, \"client\": \"127.0.0.1:65365\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:46:50.945Z"
    quote: "{\"ts\": \"2026-08-25T04:46:50.945Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"d45ddc00eeff\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 2.127, \"client\": \"127.0.0.1:65366\"}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:46:54.013Z"
    quote: "{\"ts\": \"2026-08-25T04:46:54.013Z\", \"level\": \"WARNING\", \"logger\": \"faultline.chaos\", \"message\": \"chaos mode enabled\", \"request_id\": \"60d6b10dd1ce\", \"event\": \"chaos_enabled\", \"enabled\": true, \"failure_rate\": 0.0, \"error_status\": 503, \"extra_latency_ms\": 1500}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:46:54.014Z"
    quote: "{\"ts\": \"2026-08-25T04:46:54.014Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /chaos/enable -> 200\", \"request_id\": \"60d6b10dd1ce\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/chaos/enable\", \"status\": 200, \"duration_ms\": 2.632, \"client\": \"127.0.0.1:65367\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:46:57.209Z"
    quote: "{\"ts\": \"2026-08-25T04:46:57.209Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products -> 200\", \"request_id\": \"a4fd5814d0ea\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products\", \"status\": 200, \"duration_ms\": 1127.28, \"client\": \"127.0.0.1:65368\"}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:47:00.107Z"
    quote: "{\"ts\": \"2026-08-25T04:47:00.107Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"3fad5b07911f\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 444.623, \"client\": \"127.0.0.1:65371\"}"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:47:04.116Z"
    quote: "{\"ts\": \"2026-08-25T04:47:04.116Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"b0cd287362aa\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 1218.361, \"client\": \"127.0.0.1:65373\"}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:48:24.360Z (investigator probe konan-1787633304-37125)"
    quote: "{\"ts\": \"2026-08-25T04:48:24.360Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"konan-1787633304-37125\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 101.074, \"client\": \"127.0.0.1:65402\"}"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:48:30.574Z (investigator probe konan-1787633309-37160)"
    quote: "{\"ts\": \"2026-08-25T04:48:30.574Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /orders -> 200\", \"request_id\": \"konan-1787633309-37160\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 1189.442, \"client\": \"127.0.0.1:65407\"}"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:48:25.737Z (investigator probe konan-1787633305-37137)"
    quote: "{\"ts\": \"2026-08-25T04:48:25.737Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /health -> 200\", \"request_id\": \"konan-1787633305-37137\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/health\", \"status\": 200, \"duration_ms\": 0.514, \"client\": \"127.0.0.1:65404\"}"
  - id: E12
    type: metric
    source: "/metrics request_id=konan-1787633379-37214"
    quote: "faultline_chaos_enabled 1"
  - id: E13
    type: metric
    source: "/metrics request_id=konan-1787633379-37214"
    quote: "# TYPE http_exceptions_total counter\n# HELP faultline_chaos_enabled Whether chaos mode is active."
  - id: E14
    type: metric
    source: "/metrics request_id=konan-1787633379-37214"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 5\nhttp_requests_total{method=\"GET\",path=\"/metrics\",status=\"200\"} 4\nhttp_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 4\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 5\nhttp_requests_total{method=\"POST\",path=\"/chaos/enable\",status=\"200\"} 1\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2"
  - id: E15
    type: metric
    source: "/metrics request_id=konan-1787633252-37080 (04:47:32Z) then konan-1787633379-37214 (04:49:39Z)"
    quote: "process_uptime_seconds 44.50194387510419\nprocess_uptime_seconds 171.33859662502073"
  - id: E16
    type: metric
    source: "/metrics request_id=konan-1787633252-37080 then konan-1787633379-37214"
    quote: "process_max_rss_bytes 47595520\nprocess_max_rss_bytes 47611904"
  - id: E17
    type: probe
    source: "/health request_id=konan-1787633251-37074"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":43.633590042125434}\n-- HTTP 200 in 0.002139s request_id=konan-1787633251-37074"
  - id: E18
    type: log
    source: "lab/logs/app.log (whole file, 32 lines, no .1–.3 backups) @ 2026-08-25T04:49:39Z"
    quote: "grep -c -E '\"status\": (4|5)[0-9][0-9]' lab/logs/app.log -> 0\ngrep -c -E 'unhandled_exception|chaos_failure|simulated_exception|chaos_disabled' lab/logs/app.log -> 0"
  - id: E19
    type: metric
    source: "/metrics request_id=konan-1787633379-37214"
    quote: "http_request_duration_seconds_sum{method=\"GET\",path=\"/products\"} 2.8595894158352166\nhttp_request_duration_seconds_count{method=\"GET\",path=\"/products\"} 4\nhttp_request_duration_seconds_sum{method=\"GET\",path=\"/health\"} 0.020316418260335922\nhttp_request_duration_seconds_count{method=\"GET\",path=\"/health\"} 5"
  - id: E20
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:46:48.043Z"
    quote: "{\"ts\": \"2026-08-25T04:46:48.043Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}\ngrep -c '\"event\": \"startup\"' lab/logs/app.log -> 1"
  - id: E21
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:47:01.819Z"
    quote: "{\"ts\": \"2026-08-25T04:47:01.819Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"9644157d92aa\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 629.65, \"client\": \"127.0.0.1:65372\"}"
  - id: E22
    type: log
    source: "lab/logs/app.log @ 2026-08-25T04:47:32.534Z (investigator probe konan-1787633252-37080)"
    quote: "{\"ts\": \"2026-08-25T04:47:32.534Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /metrics -> 200\", \"request_id\": \"konan-1787633252-37080\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/metrics\", \"status\": 200, \"duration_ms\": 0.601, \"client\": \"127.0.0.1:65395\"}"
gaps:
  - "The reported 'error page once' has no server-side trace: zero 4xx/5xx lines, zero exception events, no exception counter series (E13, E14, E18). A client- or proxy-side timeout on a ~1.2 s response, or an error before the visible window, cannot be excluded from this surface."
  - "Telemetry begins at the process startup line 2026-08-25T04:46:48.043Z (E20); lab/logs/app.log has no rotated backups, so nothing before that startup is observable — an earlier process, a restart, or an earlier error is outside reach."
  - "CPU saturation is not measured on this surface (no CPU metric exists); it is excluded only indirectly by /health staying sub-millisecond between slow shop-route requests (E9, E10, E11)."
  - "The chaos delay's distribution (0–1500 ms uniform or otherwise) is inferred from extra_latency_ms 1500 and observed values 101–1218 ms; no config or code beyond the marker is within the surface."
  - "The journal frontmatter was not machine-validated in this session: running the schema validator needed a permission prompt, which the read-only shift treats as a stop signal."
usage:
  model: claude-fable-5
  tokens: 1102605
  wall_clock_seconds: 280
---

# Shop-wide slowness after chaos mode enabled with 1500 ms extra latency

## Summary

**Verdict: root cause identified (H1, class `interfaces` — runtime configuration change).** At `2026-08-25T04:46:54.013Z` an unstamped `POST /chaos/enable` turned chaos mode on with `extra_latency_ms: 1500` and `failure_rate: 0.0` (E4, E5). From the first shop request after that marker, every business route (`/products`, `/products/{id}`, `GET /orders`, `POST /orders`) went from ~1–2 ms (E1–E3) to 101–1218 ms per request (E6–E10, E21), varying on identical inputs, while `/health` and `/metrics` stayed at ~0.5 ms (E11, E22) — which is exactly why the health checks read green and fast. All responses are still 200/201 (E14); the flag is still set at the last scrape (E12), so the slowdown is ongoing. Confidence is high for the slowness. The reported "error page once" is **not** explained by any telemetry on the surface: no 4xx/5xx, no exceptions, `failure_rate` is 0.0 (E13, E18, E4) — see Gaps.

## Complaint block

```json
{
  "source": "human",
  "fingerprint": "human-1787633230",
  "labels": { "alertname": "human-report" },
  "annotations": { "summary": "Users say the whole shop got painfully slow in the last few minutes; some also mention seeing an error page once. Health checks are green and fast." },
  "startsAt": "2026-08-25T04:47:10Z"
}
```

Investigation start: `2026-08-25T04:47:24Z` (trigger latency 14 s).

## Timeline

| Time (UTC) | Event | Evidence |
|---|---|---|
| 04:46:48.043 | Process start: `faultline 0.1.0 started` — the only startup marker; log history begins here | E20 |
| 04:46:48.807 – 04:46:50.945 | Known-good traffic: `/products` 1.228 ms, `/products/1` 1.001 ms, `POST /orders` 2.127 ms | E1, E2, E3 |
| 04:46:54.013 | **Config change marker**: `chaos_enabled`, `failure_rate 0.0`, `error_status 503`, `extra_latency_ms 1500`, via unstamped `POST /chaos/enable` | E4, E5 |
| 04:46:57.209 | First known-bad: `GET /products` 1127.28 ms, status 200 | E6 |
| 04:47:00 – 04:47:04 | `/products/1` 444.6 ms, `POST /orders` 629.65 ms, `GET /orders` 1218.4 ms — all 2xx | E7, E21, E8 |
| 04:47:10 | Human complaint raised (`startsAt`) | — |
| 04:47:24 – 04:47:32 | Investigation start; baseline `/health` 0.002 s, `/metrics` 0.601 ms, `faultline_chaos_enabled 1`, uptime 44.5 s | E17, E22, E15 |
| 04:48:24 – 04:48:30 | Investigator probes: `GET /orders` 101 ms then 1189 ms on the same input; `/health` 0.514 ms in between | E9, E10, E11 |
| 04:49:39 | Final scrape: chaos flag still 1, uptime 171.3 s monotonic, RSS flat, all counters 2xx, no exception series | E12, E15, E16, E14, E13 |

## Investigation

- **Baseline** (04:47:31–32Z): `/health` 200 in 2 ms with uptime 43.6 s (E17); `/metrics` showed `faultline_chaos_enabled 1`, no exception series, all request series 2xx; log had 21 lines starting at process startup.
- **Triage** — three lenses in parallel, each blind to the others: `infra-process`, `interfaces`, `software-defect`. All three converged: single startup and monotonic uptime (infra), a sharp-onset config-change marker with a route-independent, per-request latency step (interfaces), and no exception or 5xx anywhere, no data-dependent shape (software-defect).
- **Deep-dive**: skipped. H1's triage evidence — marker, before/after step on identical inputs, live probes reproducing the variance, flag still set — was deterministic and complete; H2 and H3 were negative findings over the complete counter and log surface.
- **Judge** (evidence-only, adversarial): H1 **validated**; H2 **invalidated** (scope: current process lifetime); H3 **invalidated**. The judge flagged two uncited sub-claims of H1 — a post-marker `POST /orders` duration and a `/metrics` duration — both already in the log and added as E21, E22. It noted that the "error page" remains unexplained and that CPU is unmeasured; both are recorded under Gaps.

## Hypotheses

### H1 — chaos-mode latency injection (interfaces) — validated

Last known-good `POST /orders` at 04:46:50.945Z took 2.127 ms (E3); the `chaos_enabled` marker with `extra_latency_ms 1500` lands at 04:46:54.013Z (E4, E5); the first request after it, `GET /products`, takes 1127.28 ms (E6). The same inputs before and after differ by ~400× (`/products/1`: 1.001 ms E2 vs 444.623 ms E7). Two investigator probes of `GET /orders` six seconds apart return 101 ms and 1189 ms (E9, E10) — per-request, not per-input, which is the injected-degradation shape rather than a code defect. `/health` (0.514 ms, E11) and `/metrics` (0.601 ms, E22) are exempt, matching the complaint's "health checks are green and fast". `faultline_chaos_enabled 1` at the final scrape (E12) and zero `chaos_disabled` events (E18) show the change is still in force. No evidence against.

### H2 — code defect / 5xx behind the error page (software-defect) — invalidated

`http_exceptions_total` has no series (E13); every `http_requests_total` series is 200/201 (E14); the whole log has zero status ≥ 400 lines and zero exception events (E18); the chaos marker has `failure_rate 0.0`, so its 503 injection is inert (E4). No failing unit (route + input) exists to trace. Refutation is bounded to the visible window (see Gaps).

### H3 — process crash/restart or saturation (infra-process) — invalidated

One startup marker only (E20); `process_uptime_seconds` 44.5 → 171.3 across two scrapes, monotonic (E15); `process_max_rss_bytes` +16 KB (E16); `/health` stays 200 and sub-millisecond between slow shop requests (E17, E11); counters never reset (E14, E18). The process is alive and degraded, not restarting.

## Safe next steps

Read-only suggestions; remediation is out of scope for this journal.

- Identify who or what issued the unstamped `POST /chaos/enable` from `127.0.0.1:65367` at 04:46:54.013Z (E5) — whether it was an intended exercise.
- Re-scrape `/metrics` for `faultline_chaos_enabled` and look for a `chaos_disabled` event to confirm when the condition ends.
- Ask the reporters for the URL, text, and time of the "error page"; compare against client/proxy timeout settings, since server-side errors are absent for this process lifetime.
- Check whether any log or process history exists before 04:46:48.043Z outside this surface (E20) — the current process started only six seconds before the config change.

## Gaps

- **Error page unexplained.** Nothing on the surface shows a non-2xx response or exception (E13, E14, E18). A client- or proxy-side timeout on a ~1.2 s response, or an error before the visible window, is consistent with the report but is inference, not evidence.
- **No history before 04:46:48Z.** The log has one startup line and no rotated backups (E20); an earlier process, restart, or error is outside reach.
- **CPU unmeasured.** No CPU metric exists on this surface; saturation is excluded only indirectly by the `/health` latency pattern (E9–E11).
- **Delay distribution inferred.** The 0–1500 ms range is read from `extra_latency_ms 1500` and observed values 101–1218 ms; the actual sampling rule is outside the surface.
- **Schema validation not run.** Running the frontmatter validator required a permission prompt; per the boundary rules that is a stop signal, so the machine core was checked by hand only.
