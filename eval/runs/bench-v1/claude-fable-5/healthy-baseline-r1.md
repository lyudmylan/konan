---
konan_journal: 1
investigation:
  id: 2026-08-20-routine-handover-check
  trigger: "manual (/konan, human profile; alertname=human-report; fingerprint=human-1787203565; startsAt=2026-08-20T05:26:05Z; trigger latency startsAt->start = 12s)"
  complaint: "Routine on-call handover check: anything wrong with the shop service right now? No specific user reports."
  started: 2026-08-20T05:26:17Z
  concluded: 2026-08-20T05:33:47Z
target:
  name: faultline
  surface_contract: docs/lab.md
verdict: no-active-incident
hypotheses:
  - id: H1
    statement: "GET /products/3 fails deterministically with HTTP 500: the product-detail handler computes units_ordered / product['units_in_stock'] (shop.py line 64) and product 3 is the only product with units_in_stock=0, raising ZeroDivisionError. Latent in this process lifetime: only investigator probes have triggered it; no user traffic has hit /products/3 since startup."
    incident_class: software-defect
    state: validated
    evidence_for: [E7, E8, E9, E10, E11]
    evidence_against: []
latent_findings:
  - statement: "Any request to GET /products/3 returns HTTP 500 (ZeroDivisionError at shop.py:64, division by units_in_stock=0). Real and reproducible, but untriggered by user traffic in this process lifetime — latent, not the active incident."
    evidence: [E7, E8, E9, E10]
  - statement: "Product 4 ('Mystery Box') carries price:null in the catalog data; all observed read paths for it returned 200 (detail probe returned turnover_score 0.0). Anomalous data on record, no observed failure."
    evidence: [E7, E11]
evidence:
  - id: E1
    type: probe
    source: "/health @ request_id=konan-1787203595-78760"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":52.5355662079528}\n-- HTTP 200 in 0.002789s request_id=konan-1787203595-78760"
  - id: E2
    type: metric
    source: "/metrics @ request_id=konan-1787203604-78766"
    quote: "http_requests_total{method=\"GET\",path=\"/health\",status=\"200\"} 3\nhttp_requests_total{method=\"GET\",path=\"/orders\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products\",status=\"200\"} 1\nhttp_requests_total{method=\"GET\",path=\"/products/{product_id}\",status=\"200\"} 3\nhttp_requests_total{method=\"POST\",path=\"/orders\",status=\"201\"} 2"
  - id: E3
    type: metric
    source: "/metrics @ request_id=konan-1787203604-78766"
    quote: "# HELP http_exceptions_total Unhandled exceptions by Python class name.\n# TYPE http_exceptions_total counter\n# HELP faultline_chaos_enabled Whether chaos mode is active.\n# TYPE faultline_chaos_enabled gauge\nfaultline_chaos_enabled 0"
  - id: E4
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:25:42.771Z"
    quote: "{\"ts\": \"2026-08-20T05:25:42.771Z\", \"level\": \"INFO\", \"logger\": \"faultline.app\", \"message\": \"faultline 0.1.0 started\", \"event\": \"startup\", \"version\": \"0.1.0\"}"
  - id: E5
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:25:44.593Z"
    quote: "{\"ts\": \"2026-08-20T05:25:44.593Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/1 -> 200\", \"request_id\": \"efd319d76b24\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/1\", \"status\": 200, \"duration_ms\": 1.139, \"client\": \"127.0.0.1:52056\"}"
  - id: E6
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:25:47.719Z"
    quote: "{\"ts\": \"2026-08-20T05:25:47.719Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"POST /orders -> 201\", \"request_id\": \"f1d9a8ad671f\", \"event\": \"request\", \"method\": \"POST\", \"path\": \"/orders\", \"status\": 201, \"duration_ms\": 2.069, \"client\": \"127.0.0.1:52058\"}"
  - id: E7
    type: probe
    source: "/products @ request_id=konan-1787203977-79218"
    quote: "{\"id\":3,\"name\":\"Unobtainium Ingot\",\"price\":999.0,\"units_in_stock\":0},{\"id\":4,\"name\":\"Mystery Box\",\"price\":null,\"units_in_stock\":75}\n-- HTTP 200 in 0.004107s request_id=konan-1787203977-79218"
  - id: E8
    type: probe
    source: "/products/3 @ request_id=konan-1787203711-78852"
    quote: "{\"error\":\"internal server error\",\"exception_type\":\"ZeroDivisionError\",\"request_id\":\"konan-1787203711-78852\"} (HTTP 500 in 0.009s)"
  - id: E9
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:28:31.670Z"
    quote: "{\"ts\": \"2026-08-20T05:28:31.670Z\", \"level\": \"ERROR\", \"logger\": \"faultline.request\", \"message\": \"unhandled exception: division by zero\", \"request_id\": \"konan-1787203711-78852\", \"event\": \"unhandled_exception\", \"exception_type\": \"ZeroDivisionError\", \"stack\": \"... File \\\"/Users/lyudmylan/Projects/faultline/src/faultline/shop.py\\\", line 64, in get_product\\n    \\\"turnover_score\\\": units_ordered / product[\\\"units_in_stock\\\"],\\nZeroDivisionError: division by zero\"}"
  - id: E10
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:28:39.421Z"
    quote: "{\"ts\": \"2026-08-20T05:28:39.421Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/3 -> 500\", \"request_id\": \"konan-1787203719-78867\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/3\", \"status\": 500, \"duration_ms\": 2.697, \"client\": \"127.0.0.1:52104\"}"
  - id: E11
    type: log
    source: "lab/logs/app.log @ 2026-08-20T05:28:32.103Z"
    quote: "{\"ts\": \"2026-08-20T05:28:32.103Z\", \"level\": \"INFO\", \"logger\": \"faultline.request\", \"message\": \"GET /products/4 -> 200\", \"request_id\": \"konan-1787203712-78858\", \"event\": \"request\", \"method\": \"GET\", \"path\": \"/products/4\", \"status\": 200, \"duration_ms\": 0.457, \"client\": \"127.0.0.1:52102\"}"
  - id: E12
    type: probe
    source: "/health @ request_id=konan-1787203689-78822"
    quote: "{\"status\":\"ok\",\"uptime_seconds\":146.62}\n(HTTP 200)"
  - id: E13
    type: log
    source: "lab/server.out @ 2026-08-20T05:25:42.770Z (first line of the file; no output precedes it)"
    quote: "{\"ts\": \"2026-08-20T05:25:42.770Z\", \"level\": \"INFO\", \"logger\": \"uvicorn.error\", \"message\": \"Started server process [78662]\"}"
gaps:
  - "Behavior before 2026-08-20T05:25:42Z is unobservable: lab/logs/app.log is the only log file (no rotated backups) and lab/server.out begins at that startup with no prior output. The lab runtime directory (pid file, logs) was created at the same minute, so this reads as a fresh planned start, not lost history — but nothing earlier can be checked from the surface."
  - "The observation window for user impact is short (~3 minutes of process lifetime, 14 non-investigator requests); a low-rate intermittent failure could hide below this sample size."
  - "The interfaces triage lens could not re-probe /metrics itself (permission gate); it argued from the log file and the orchestrator's baseline metrics capture instead."
usage:
  model: claude-fable-5
  tokens: 2020397
  wall_clock_seconds: 450
---

# Routine handover check: shop service healthy; latent 500 on /products/3

## Summary

**Verdict: no active incident.** All non-investigator traffic since process start (2026-08-20T05:25:42Z) succeeded — 14 access lines, all 200/201 (E2, E5, E6), `http_exceptions_total` empty and chaos off (E3), health green with monotonically advancing uptime (E1, E12). One **latent, validated defect** rides along: `GET /products/3` deterministically returns HTTP 500 with a `ZeroDivisionError` from `shop.py:64` (`units_ordered / product["units_in_stock"]`), because product 3 ("Unobtainium Ingot") is the only product with `units_in_stock: 0` (E7–E10). Only investigator probes have triggered it; no user has hit that route in this process lifetime, but the next user who opens product 3 will get a 500. Confidence is high inside the observation window; the window itself is short (~3 minutes — see Gaps).

## Timeline

- **05:25:42.770Z** — server process 78662 starts; first line of `lab/server.out`, no prior output (E13). Application startup event follows at .771Z (E4). Fresh lab start, not a crash recovery: the runtime directory was created at this same minute.
- **05:25:43–05:25:52Z** — simulated user traffic: health checks, product browses, two orders created — all 200/201 (E5, E6).
- **05:26:05Z** — complaint raised (`startsAt`); investigation start 05:26:17Z.
- **05:26:35–05:26:44Z** — baseline probes: health ok, metrics all-2xx, exceptions empty, chaos off (E1, E2, E3).
- **05:28:31.670Z** — investigator probe `GET /products/3` → 500, unhandled `ZeroDivisionError` with full stack (E8, E9). First error of any kind in the log.
- **05:28:32.103Z** — investigator probe `GET /products/4` → 200 (E11): failure is specific to product 3.
- **05:28:39.421Z** — repeat probe `/products/3` → 500 again (E10): deterministic.

No configuration, deploy, flag-change, or chaos markers appear anywhere in the telemetry (E3; full-log grep found only the startup event).

## Investigation

1. **Baseline** — health, metrics, log tail: clean; process ~1 minute old.
2. **Triage** — three lenses in parallel (infra-process, interfaces, software-defect), each given only the lens file, the surface contract, the verbatim complaint, and the baseline. Infra-process: no anomalies (single startup, monotonic uptime, flat RSS, sub-2ms latencies). Interfaces: no anomalies (no chaos/config markers, no gateway-shaped failures, no onset to explain). Software-defect: found the deterministic `/products/3` 500 and the product-4 null price.
3. **Deep-dive** — skipped: the triage evidence for H1 was already deterministic and complete (two reproductions, stack trace, distinguishing input isolated).
4. **Judge (round 1)** — H1 (the defect) **validated**. The null hypothesis ("no active incident") **inconclusive**: the judge asked for the reason behind the 05:25:42Z process start (planned vs crash recovery) and for topology assurance (sole instance).
5. **Round 2** — targeted gathering: `lab/server.out` begins at the start with no prior output (E13); the runtime directory was created at the same minute; the surface contract declares a single service at 127.0.0.1:8000 with no distributed topology. Judge re-verdict: null hypothesis **validated**.

## Hypotheses

### H1 — data-dependent ZeroDivisionError on /products/3 (validated)

The product-detail handler divides `units_ordered` by `product["units_in_stock"]`; product 3 is the only catalog row with stock 0 (E7). Both probes of `/products/3` returned 500 with `exception_type: ZeroDivisionError` (E8, E10), and the stack names `shop.py` line 64 exactly at that division (E9). Adjacent and sibling ids succeed — products 1, 2, 5 in user traffic (E5) and product 4 by probe (E11) — so this is one route, one input: the classic data-dependent defect shape. Evidence against: none. **Scope:** latent — the only `unhandled_exception` entries and 500s in the whole log carry `konan-*` request ids (investigator probes, per the probes-are-telemetry-visible rule); zero non-investigator traffic has hit `/products/3` since startup.

### Null hypothesis — no active incident (validated by the judge, round 2)

Carried by the verdict rather than the hypothesis list (it names no cause or class). For: all non-investigator requests 200/201 (E2, E5, E6), exceptions counter empty and chaos off (E3), health green with monotonic uptime (E1, E12), fresh planned start rather than crash recovery (E13, E4), single-instance topology per the surface contract. Round 1 was inconclusive pending the start-reason and topology evidence; round 2 closed both.

## Safe next steps

- Watch for non-investigator 500s on `/products/3`: `grep '"path": "/products/3"' lab/logs/app.log` filtered to non-`konan-*` request ids, or the `http_requests_total{path="/products/{product_id}",status="500"}` counter (it will now read 2 from investigator probes — treat that as the floor).
- Read `shop.py:64` (`get_product`) in the faultline repo to confirm the division guard is absent, and check whether any other handler divides by `units_in_stock`.
- Check whether product 4's `price: null` (E7) flows into any computation the way `units_in_stock: 0` does — same table, same anomalous-data shape, currently harmless on all observed read paths.

(Remediation — fixing the handler or the data — is out of scope for this journal.)

## Gaps

- **Pre-start history**: telemetry begins at 05:25:42Z; there are no rotated log backups and `server.out` starts at that line. Directory timestamps say the lab itself was created then, so nothing earlier likely existed — but that cannot be proven from the surface.
- **Short window**: ~3 minutes of process lifetime and 14 user requests is a small sample; an intermittent low-rate failure would not have surfaced.
- **Lens re-probe blocked**: the interfaces lens could not independently re-scrape /metrics (permission gate) and relied on the baseline capture; its conclusions were corroborated by the other lenses' probes.
