# The lab: running faultline, and what konan may touch

konan develops and is measured against [faultline](https://github.com/lyudmylan/faultline),
a deliberately unreliable HTTP service. This doc is the lab contract: how to run it and
the complete telemetry surface the investigator is allowed to see.

## Running the lab

```sh
scripts/lab.sh start    # needs a faultline checkout; FAULTLINE_DIR defaults to ../faultline
scripts/lab.sh status
scripts/lab.sh stop
```

Base URL `http://127.0.0.1:8000` (`KONAN_LAB_PORT` / `KONAN_LAB_BASE` override). Runtime
artifacts live under `lab/` (gitignored): the service's JSON logs in `lab/logs/`, server
stdout in `lab/server.out`.

## The investigator's surface — all of it

1. **Probes** — `scripts/probe.sh /path[?query]`, GET-only against the allowlist
   `/health`, `/metrics`, `/openapi.json`, `/products`, `/products/{id}`, `/orders`,
   `/orders/{id}`. Each probe stamps an `X-Request-ID` and prints a trailer line with
   HTTP status, duration, and that id — grep the id in the logs to correlate.
2. **Logs** — `lab/logs/app.log` (rotating, plus `.1`–`.3` backups), one JSON object per
   line. Base fields: `ts`, `level`, `logger`, `message`, `request_id` (request-scoped
   lines), `event`, and `stack` on unhandled exceptions. `event` values include
   `request` (access line: adds `method`, `path`, `status`, `duration_ms`, `client`),
   `unhandled_exception` (adds `exception_type`), `chaos_enabled` / `chaos_disabled` /
   `chaos_failure`, `simulated_exception`, `startup`, `order_created`.
3. **Metrics** — `/metrics`, Prometheus text format: `http_requests_total{method,path,status}`,
   `http_request_duration_seconds_sum`/`_count`, `http_exceptions_total{type}`,
   `faultline_chaos_enabled`, `process_uptime_seconds`, `process_max_rss_bytes`.

Everything else — `/chaos`, `/simulate/*` — is operator/eval surface; `probe.sh` refuses
it mechanically (faultline serves mutating GETs there).

## Eval-side controls (not for the investigator)

`scripts/scenario.sh` wraps the operator surface: `chaos-on [rate] [status] [latency_ms]`,
`chaos-off`, `chaos-status`, `sim <path>` (e.g. `sim status/500`), and
`order <product_id> [quantity]`. It is deliberately not pre-approved in settings — see
the lab boundary in `AGENTS.md`.

## Ground truth stays outside

The defect catalog and scenario recipes live in the faultline repo (its SPEC) and,
starting with #11, in eval fixtures — deliberately outside the investigator's reach.
Investigations argue from the surface above, nothing else.
