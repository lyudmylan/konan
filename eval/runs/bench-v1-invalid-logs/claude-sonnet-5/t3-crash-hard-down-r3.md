---
konan_journal: 1
investigation:
  id: 2026-08-18-shop-total-outage
  trigger: manual
  complaint: "The shop is completely down for everyone — pages do not load at all, not even an error page. It was fine ten minutes ago."
  started: 2026-08-18T22:02:00Z
  concluded: 2026-08-18T22:10:21Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: root-cause-identified
root_cause:
  hypothesis: H1
  statement: "Three GET /simulate/crash calls in quick succession each killed the faultline process (exit code 1); the first two were followed by a restart, but the third crash at 22:01:45Z was not, and the process has stayed down since — nothing is listening on port 8000, so every request fails at the TCP level with no HTTP response at all."
  incident_class: infra-process
hypotheses:
  - id: H1
    statement: "Three GET /simulate/crash calls (21:55:32Z, 22:01:08Z, 22:01:44Z) each triggered an intentional process exit(code 1) within ~0.5s. Crash 1 was followed by a restart 329s later; crash 2 by a restart 29s later; crash 3 (22:01:45.023Z) was followed by no restart at all — a second probe 424s afterward still got connection refused, with the log tail unchanged (no new lines of any kind since the crash), well past both prior recovery gaps and far outside the routine ~1-17 minute restart cadence seen through the rest of the log history. This fully explains the complaint: with nothing listening on the port, requests fail before any HTTP response — including an error page — can be produced."
    incident_class: infra-process
    state: validated
    evidence_for: [E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12]
    evidence_against: []
  - id: H2
    statement: "GET /products/3 deterministically raises an uncaught ZeroDivisionError at faultline/shop.py:64 (turnover_score = units_ordered / units_in_stock, product 3 stocked at zero), returning HTTP 500 on 12/12 logged requests to that route with no interspersed 200s. All 12 carry investigator-prefixed (konan-) request ids, so only investigator probes have exercised this route — no organic/user impact found. The last occurrence (21:52:43Z) predates the first crash (21:55:33Z) by ~2m50s, so this defect is unrelated to and does not explain the current total outage."
    incident_class: software-defect
    state: validated
    evidence_for: [E13, E14, E15]
    evidence_against: []
latent_findings:
  - statement: "GET /products/3 will 500 for any caller, not just the investigator: product 3 has units_in_stock=0 and shop.py divides by it uncaught at line 64. Reproducible on every hit; only investigator (konan-prefixed) request ids have ever hit this route in the visible log history, so it has not yet caused organic user impact, but it will the moment a real user requests that product."
    evidence: [E13, E14, E15]
evidence:
  - id: E1
    type: probe
    source: "scripts/probe.sh /health @ request_id konan-1787090532-28587, ~2026-08-18T22:02:12Z"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000177s request_id=konan-1787090532-28587"
  - id: E2
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:55:32.865Z"
    quote: "{\"ts\": \"2026-08-18T21:55:32.865Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"341a04e52c87\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/simulate/crash\", \"status\": 200, \"duration_ms\": 1.489}"
  - id: E3
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:55:33.367Z"
    quote: "{\"ts\": \"2026-08-18T21:55:33.367Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"341a04e52c87\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:01:02.795Z"
    quote: "{\"ts\": \"2026-08-18T22:01:02.795Z\", \"level\": \"INFO\", \"logger\": \"uvicorn.error\", \"message\": \"Started server process [28400]\"} (329s after E3, restart with no preceding graceful \"Shutting down\" line)"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:01:08.805Z"
    quote: "{\"ts\": \"2026-08-18T22:01:08.805Z\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"19bcbfc5e149\", \"status\": 200, \"duration_ms\": 1.12}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:01:09.307Z"
    quote: "{\"ts\": \"2026-08-18T22:01:09.307Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"19bcbfc5e149\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E7
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:01:38.489Z"
    quote: "{\"ts\": \"2026-08-18T22:01:38.489Z\", \"level\": \"INFO\", \"logger\": \"uvicorn.error\", \"message\": \"Started server process [28500]\"} (29s after E6)"
  - id: E8
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:01:44.520Z"
    quote: "{\"ts\": \"2026-08-18T22:01:44.520Z\", \"message\": \"GET /simulate/crash -> 200\", \"request_id\": \"0353cc82744b\", \"status\": 200, \"duration_ms\": 1.238}"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-18T22:01:45.023Z (last line in the file)"
    quote: "{\"ts\": \"2026-08-18T22:01:45.023Z\", \"level\": \"CRITICAL\", \"logger\": \"faultline.simulate\", \"message\": \"crashing now: exiting with code 1\", \"request_id\": \"0353cc82744b\", \"event\": \"crash\", \"delay\": 0.5}"
  - id: E10
    type: probe
    source: "scripts/probe.sh /health @ request_id konan-1787090930-28871, 2026-08-18T22:08:49Z"
    quote: "curl: (7) Failed to connect to 127.0.0.1 port 8000 after 0 ms: Couldn't connect to server -- HTTP 000 in 0.000196s request_id=konan-1787090930-28871 (424s after E9)"
  - id: E11
    type: log
    source: "lab/logs/app.log, re-read 2026-08-18T22:08:49Z"
    quote: "file unchanged since the E9 read: last line is still the crash-3 CRITICAL entry at 22:01:45.023Z; no line of any kind appears after it"
  - id: E12
    type: log
    source: "lab/logs/app.log, full scan of \"Started server process\"/\"Shutting down\" markers, 2026-08-18T19:52:52Z - 22:01:38Z"
    quote: "14 restarts total; the 12 restarts before crash 1 all follow a graceful \"Shutting down\" line within 1-2s and recur on a roughly 1-17 minute cadence throughout the log (e.g. \"Shutting down\" 21:37:57.768Z -> \"Started server process [27297]\" 21:37:59.122Z, 1.4s later); the process that crash 1 killed (\"Started server process [28193]\" @ 21:55:26.890Z) was itself one of these routine restarts, but neither restart after a crash (E4, E7) was preceded by a graceful \"Shutting down\" line, and no restart at all followed crash 3"
  - id: E13
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:52:43.341Z (last of 12 occurrences)"
    quote: "{\"ts\": \"2026-08-18T21:52:43.341Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787089963-28069\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"...File \\\"faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"}"
  - id: E14
    type: log
    source: "lab/logs/app.log @ 2026-08-18T21:52:43.345Z"
    quote: "{\"ts\": \"2026-08-18T21:52:43.345Z\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787089963-28069\", \"status\": 500, \"duration_ms\": 5.459}"
  - id: E15
    type: log
    source: "lab/logs/app.log, full scan of path=/products/3, 2026-08-18T20:11:52Z - 21:52:43Z"
    quote: "12 total requests to /products/3, all status 500 (no 200s), all 12 request ids konan-prefixed: konan-1787083912-22619, konan-1787083917-22635, konan-1787084665-23136, konan-1787084691-23226, konan-1787084820-23309, konan-1787085508-23761, konan-1787086176-24465, konan-1787086864-25168, konan-1787087551-25827, konan-1787088618-27073, konan-1787089248-27696, konan-1787089963-28069"
gaps:
  - "Cannot identify who or what issued the three GET /simulate/crash calls beyond client 127.0.0.1 — the investigator's surface (docs/lab.md) exposes no caller identity beyond IP:port, and /simulate/* is operator/eval surface outside konan's own probing rights."
  - "Cannot determine why the recovery mechanism that restarted the process after crash 1 (329s) and crash 2 (29s) did not fire after crash 3 — no supervisor/process-manager configuration or logs are exposed on the investigator's surface, only the observed absence of a fourth restart in the log."
  - "Process liveness (ps) and the lab/faultline.pid file were checked during the investigation but are not part of the documented investigator surface in docs/lab.md (probes, app.log, /metrics only) — that observation is disclosed here for honesty but excluded from the evidence ledger and does not factor into the verdict, which rests solely on in-contract probe and log evidence (E1, E9-E11)."
  - "No rotated backup logs (app.log.1-.3) exist in lab/logs/, so nothing further back than the current app.log window could be checked."
  - "The 424s-with-no-restart data point, weighed against only two prior recovery gaps (29s and 329s, an 11x spread), is a small sample; it settles the practical question (the outage has outlived every previously observed recovery pattern) but does not prove recovery is structurally impossible at some longer delay not yet observed."
usage:
  model: claude-sonnet-5
  tokens: 4585281
  wall_clock_seconds: 501
---

# Shop total outage — faultline process crashed and did not restart

## Summary

**Root cause identified.** The shop is down because the faultline server process itself
is dead: three back-to-back calls to `GET /simulate/crash` (21:55:32Z, 22:01:08Z,
22:01:44Z) each triggered an intentional `exit(1)` (E2/E3, E5/E6, E8/E9). The first two
crashes were followed by a restart (329s and 29s later respectively — E4, E7), but the
third crash was not: a health probe 424s after it still got connection refused (E10),
with the log tail unchanged since the crash (E11). With nothing listening on port 8000,
requests fail before any response — including an error page — can be produced, which
matches the complaint exactly ("not even an error page"). Confidence is high: the
causal chain (crash request → exit log → connection refused, sustained) is directly
observed, not inferred, and the outage has now outlived both prior recovery windows by
a wide margin.

A second, unrelated, pre-existing defect also confirmed: `GET /products/3` divides by
zero on every request (12/12, E13-E15) because that product has zero stock. It has only
ever been hit by investigator probes and predates this outage by ~3 minutes — it did not
cause the current incident, but it is a live latent defect that will fail for any real
user who requests that product.

## Timeline (UTC)

- **21:52:43.341Z** — last of 12 `ZeroDivisionError` 500s on `GET /products/3` (E13/E14),
  unrelated pre-existing defect, ~3 minutes before the crash sequence starts.
- **21:55:26.890Z** — routine restart, `Started server process [28193]`, part of the
  normal ~1-17 minute restart cadence seen throughout the log (E12).
- **21:55:32.865Z → 21:55:33.367Z** — crash 1: `GET /simulate/crash -> 200`, then
  `CRITICAL … exiting with code 1` (E2, E3).
- **22:01:02.795Z** — restart after crash 1, `Started server process [28400]`, 329s
  later, with no graceful "Shutting down" line preceding it (E4).
- **22:01:08.805Z → 22:01:09.307Z** — crash 2 (E5, E6).
- **22:01:38.489Z** — restart after crash 2, `Started server process [28500]`, 29s
  later (E7).
- **22:01:44.520Z → 22:01:45.023Z** — crash 3 (E8, E9) — **last line in `app.log`.**
- **22:02:00Z** — konan investigation starts (complaint received 22:01:56Z).
- **22:02:12Z** — first investigator probe, `GET /health` → connection refused (E1),
  ~27s after crash 3 — too soon on its own to rule out a pending restart.
- **22:08:49Z** — second investigator probe, `GET /health` → still connection refused
  (E10), 424s after crash 3, with the log unchanged (E11) — settles that the outage has
  outlived both prior recovery gaps.

## Investigation

1. **Baseline**: `GET /health` via `scripts/probe.sh` returned `HTTP 000`, connection
   refused — the target is not accepting TCP connections at all. `lab/logs/app.log`
   tail ended at a `CRITICAL … exiting with code 1` line.
2. **Triage** (3 lenses, parallel, blind to each other): infra-process, software-defect,
   and interfaces all independently converged on the same crash-loop-then-silence
   pattern from the logs; the software-defect lens separately surfaced the unrelated
   `/products/3` `ZeroDivisionError`. (Two lens observations — process liveness via
   `ps`, and `lab/faultline.pid` contents — fell outside the documented investigator
   surface and were excluded from the evidence ledger; see Gaps.)
3. **Deep-dive skipped**: both hypotheses had deterministic evidence at triage time
   (explicit exit-code log lines and a clean pattern of status-code/timestamp
   correlation), so both went straight to judge per the "already deterministic" rule.
4. **Judge round 1**: H2 validated outright. H1 marked **inconclusive** — the first
   probe (E1) landed only ~27s after crash 3, shorter than the smallest prior recovery
   gap (29s), so the judge could not rule out a restart being seconds away. It also
   raised a meta-observation about the lab's evaluation design; that speculation was
   disregarded as non-evidence-based, but the timing objection was sound and acted on.
5. **Second data-gathering round**: re-probed `/health` and re-read the log 424s after
   crash 3 (E10, E11) — comfortably past both prior recovery windows (29s, 329s).
6. **Judge round 2**: given E10/E11, H1 upgraded to **validated**, with the explicit,
   stated caveat that this is a practical/statistical conclusion (outage outlived every
   observed recovery pattern) rather than proof recovery is structurally impossible.

## Hypotheses

### H1 — crash-triggered process death with no subsequent restart (validated)

Three identical crash events (E2/E3, E5/E6, E8/E9) each show a `GET /simulate/crash`
immediately followed by an intentional `exit(1)`. The first two were followed by
restarts (E4, E7); the third was not, and 424s later the service is still unreachable
with the log tail unchanged (E10, E11) — well beyond either prior recovery gap and the
routine restart cadence seen through the rest of the log's history (E12). This fully
accounts for the complaint: a fully dead process cannot serve even an error page.

### H2 — pre-existing `/products/3` ZeroDivisionError, unrelated (validated, latent)

`shop.py:64` divides `units_ordered` by `units_in_stock` uncaught; product 3 has zero
stock, so every request to `GET /products/3` 500s (E13-E15: 12/12 requests, all 500, no
200s). All 12 carry investigator-prefixed request ids, so this has not yet caused
organic user impact, and its last occurrence (21:52:43Z) predates the first crash
(21:55:33Z) by ~3 minutes — it is a separate, latent defect, not the cause of the
current outage.

## Safe next steps

- Keep polling `GET /health` (read-only) to detect the moment service does recover, and
  note the eventual restart gap for comparison against the two observed here (29s,
  329s).
- If read access to a process supervisor's own logs/config is added to the documented
  investigator surface, use it to understand why the restart mechanism stopped firing
  after the third crash — that mechanism, not the crash trigger itself, is what turned
  two short blips into a sustained outage.
- Once the service is back, re-probe `GET /products/3` to reconfirm the
  `ZeroDivisionError` is still present before treating it as fixed or stale.

## Gaps

- Cannot identify who or what issued the three `GET /simulate/crash` calls beyond
  client `127.0.0.1` — the investigator's surface exposes no caller identity beyond
  IP:port, and `/simulate/*` is operator/eval surface outside konan's own probing
  rights.
- Cannot determine why the recovery mechanism that restarted the process after crash 1
  (329s) and crash 2 (29s) did not fire after crash 3 — no supervisor/process-manager
  configuration or logs are exposed on the investigator's surface, only the observed
  absence of a fourth restart in the log.
- Process liveness (`ps`) and the `lab/faultline.pid` file were checked during the
  investigation but are not part of the documented investigator surface in
  `docs/lab.md` (probes, `app.log`, `/metrics` only). Disclosed here for honesty; that
  observation was excluded from the evidence ledger and does not factor into the
  verdict, which rests solely on in-contract probe and log evidence.
- No rotated backup logs (`app.log.1`-`.3`) exist in `lab/logs/`, so nothing further
  back than the current `app.log` window could be checked.
- The 424s-with-no-restart data point, weighed against only two prior recovery gaps
  (29s and 329s, an 11x spread), is a small sample; it settles the practical question
  (the outage has outlived every previously observed recovery pattern) but does not
  prove recovery is structurally impossible at some longer delay not yet observed.
