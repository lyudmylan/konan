---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-down-simulate-crash
  trigger: manual
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-18T21:55:47Z
  concluded: 2026-08-18T21:59:29Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "A GET request to /simulate/crash caused the faultline process to call exit(1) 0.5s later; the process has not resumed serving since, so every request now fails at the TCP level (connection refused) instead of reaching the application — matching a totally unreachable shop with no error page."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "The faultline process crashed after a /simulate/crash request and has not resumed, causing total connection-level failure for all traffic."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 raises an unhandled ZeroDivisionError (500) in the turnover_score calculation (shop.py:64) when a product's units_in_stock is 0 — a pre-existing, data-dependent defect, observed twice before the crash and unrelated to the current outage."
    evidence: [E5]
evidence:
  - id: E1
    type: probe
    source: "scripts/probe.sh /health, request_id konan-1787090160-28285"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server\n-- HTTP 000 in 0.000176s request_id=konan-1787090160-28285"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:55:32.865Z"
    quote: "{\"ts\": \"2026-08-18T21:55:32.865Z\", \"level\": \"INFO\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"341a04e52c87\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/simulate/crash\", \"status\": 200, \"duration_ms\": 1.489, \"client\": \"127.0.0.1:52073\"}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:55:33.367Z (final line in file, 603/603)"
    quote: "{\"ts\": \"2026-08-18T21:55:33.367Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"341a04e52c87\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:55:30.805Z"
    quote: "{\"ts\": \"2026-08-18T21:55:30.805Z\", \"level\": \"INFO\", \"message\": \"GET /orders -> 200\", \"request_id\": \"fc684a35eb33\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/orders\", \"status\": 200, \"duration_ms\": 0.85, \"client\": \"127.0.0.1:52072\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:52:43.341Z"
    quote: "{\"ts\": \"2026-08-18T21:52:43.341Z\", \"level\": \"ERROR\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787089963-28069\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"}"
gaps:
  - "Could not determine why the process failed to resume after the crash (e.g. a supervisor restart policy or orchestration config) — process/supervisor state (ps, systemd, docker) is outside the investigator's read-only telemetry surface (docs/lab.md: probes + logs + metrics only). Reading the lab's own launcher script (scripts/lab.sh, not target telemetry) shows faultline is started as a bare nohup process with no restart loop, which is consistent with the observed non-recovery but is offered as context, not a cited causal claim — an adversarial judge pass flagged this distinction and it is preserved here rather than papered over."
  - "Only /health was re-probed live to confirm the outage; /products, /orders, and /metrics were not individually re-probed. A TCP-level connection refusal on the port applies uniformly to every path, so further per-endpoint probes were judged unlikely to add information beyond additional stamped investigator traffic."
usage:
  model: claude-sonnet-5
  tokens: 1113966
  wall_clock_seconds: 222
---

# Shop total outage — faultline process crashed via /simulate/crash, never resumed

## Summary

**Root cause identified.** The shop is down because the faultline process itself is
dead, not because it is returning errors. At 2026-08-18T21:55:32.865Z a request to
`/simulate/crash` was served (200), and 0.5s later, at 21:55:33.367Z, the process
logged a CRITICAL "crashing now: exiting with code 1" and stopped (E2, E3). No log
line follows it — the file ends there. A live probe against `/health` after the
complaint returned a TCP-level connection refusal, not an HTTP status (E1),
confirming the process is still not listening. In the seconds immediately before
the crash, the shop was serving `/health`, `/products`, `/products/1`, and `/orders`
normally (E4) — consistent with the complaint's "it was fine ten minutes ago."
Confidence is high for the crash-and-non-recovery mechanism; the deeper question of
*why* nothing restarted the process is out of the investigator's reach (see Gaps).

## Timeline

- 21:55:27–21:55:30Z — normal traffic: `/health`, `/products`, `/products/1`, an
  order created, `/orders` — all 200/201 (E4).
- 21:55:32.865Z — `GET /simulate/crash -> 200` (E2). Request id `341a04e52c87` is not
  `konan-`-prefixed, i.e. it is scenario/end-user-shaped traffic per the lab contract,
  not an investigator probe — the trigger predates and is independent of this
  investigation.
- 21:55:33.367Z — CRITICAL "crashing now: exiting with code 1" (E3). This is the last
  line in `lab/logs/app.log` (603/603 lines).
- 21:55:47Z — investigation starts (complaint `startsAt` 21:55:43Z).
- ~21:56:00Z — investigator probe to `/health` returns connection refused (E1),
  confirming the process is still down at investigation time, roughly 27s after the
  crash and continuously since.

## Investigation

Baseline capture (step 1) was decisive by itself: the first probe (`/health`) failed
at the TCP level rather than returning any HTTP status, and the log tail showed
exactly why — a `/simulate/crash` hit followed by a logged self-exit, with nothing
after it. Because the evidence was already deterministic and complete, and because
live probing is uninformative while the process is down (every path fails identically
at the socket level), the investigation skipped the multi-lens triage fan-out and the
deep-dive round and went straight to judgment, per the loop's short-circuit rule for
deterministic baseline evidence.

One adversarial judge pass was run against H1. It validated the crash-and-outage
correlation (evidence E2–E4 support the prediction: traffic normal, then abrupt crash,
then log silence, then confirmed connection refusal) but flagged that the hypothesis
as originally worded also asserted *why* no restart happened ("no supervisor"), which
is not something the cited telemetry can support — only the lab's own launcher script
shows that, and that script is konan's harness tooling, not target telemetry. The
journal's `root_cause.statement` was narrowed to drop that unsupported clause; the
inference is preserved only as context in Gaps.

## Hypotheses

### H1 — process crash via /simulate/crash, no resumption (validated)

The faultline process crashed 0.5s after serving `/simulate/crash` and has not
resumed. Evidence for: E1 (current connection refusal), E2 (the crash-triggering
request), E3 (the crash log line and end-of-file), E4 (normal traffic immediately
before). No evidence against — no log line, metric, or probe response is inconsistent
with the process being down. The judge validated this reading; the only clause it
would not validate (a specific restart-policy explanation) was removed from the
formal statement rather than asserted past the evidence.

## Safe next steps

- Re-probe `/health` periodically (read-only) to detect when/if the process resumes
  on its own.
- Once the service is reachable again, review `lab/logs/app.log` around the next
  startup marker to see whether it was a manual restart or automatic, which would
  settle the Gaps item about restart policy.
- Separately, `/products/3`'s `ZeroDivisionError` (E5, latent finding) is worth a
  follow-up investigation on its own — it is a real, reproducible defect, just not
  the cause of this outage.

## Gaps

- Why the process didn't resume on its own is not established from target telemetry.
  Process/supervisor inspection (`ps`, systemd, docker, or similar) is outside the
  investigator's read-only surface (`docs/lab.md` limits it to probes, logs, and
  `/metrics`). The lab's launcher script (`scripts/lab.sh`) starts faultline as a bare
  `nohup` process with no restart loop, which is consistent with what was observed,
  but that script is konan's own tooling, not the target's telemetry, so it is
  recorded here as context rather than folded into the cited root cause.
- Only `/health` was re-probed live; the other allowlisted paths were not
  individually re-confirmed as down, since a TCP-level refusal on the port is
  path-independent and further probes were judged not to add information.
