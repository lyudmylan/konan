# Rim: Grafana Cloud (via the official mcp-grafana server) — PREPARED, not yet live

Status: prepared. The telemetry plane (#53) ships the lab's data with the committed
Alloy configuration `grafana-cloud.alloy`; the document becomes the surface contract
with the rim (#54), when the tool names below are pinned from the real stack. Until
then `docs/lab.md` remains konan's only active rim.

This is the first non-lab rim: the investigator's whole evidence surface is Grafana
Cloud — metrics (Prometheus) and logs (Loki) shipped from the lab by Grafana Alloy —
read through the official `mcp-grafana` server. For an investigation under this rim,
the local files under `lab/` are **out of bounds**: evidence is what the observability
plane serves, exactly like a real team's stack.

## The investigator's surface — all of it

1. **Prometheus queries** via mcp-grafana query tools — instant and range queries
   against the lab's shipped metrics (`http_requests_total`, duration summaries,
   `http_exceptions_total`, `faultline_chaos_enabled`, process gauges).
2. **Loki queries** via mcp-grafana log tools — LogQL over the shipped JSON log
   lines; `request_id` distinguishes user traffic from `konan-*` probes.
3. **Read-only Grafana metadata** (datasource list) as needed to address 1–2.

TODO at go-live (#53): pin the EXACT tool names the server exposes — connect once,
list tools, then write the allowlist below from what is actually served; never from
documentation memory. Write tools (dashboards, alerting, incident annotations) stay
out: absent from the allowlist, denied by default.

## Boundary (mechanical, as always)

- `.mcp.json` — see `grafana-cloud.mcp.json.example`: the mcp-grafana server with a
  **read-scoped service-account token** from env (`GRAFANA_SERVICE_ACCOUNT_TOKEN`),
  never a file, never committed.
- `.claude/settings.json` (at go-live): `allow` exactly the read tools pinned above
  (`mcp__grafana__<tool>` form); no write tool listed; the boundary hook stays active
  for Bash (probes are not part of this rim — the plane is the surface).
- The blinding contract is unchanged: `eval/`, the tracker, and the faultline
  checkout stay out of bounds during investigations.

## Operator setup — the telemetry plane (#53)

The steps as they run on the operator computer. The credentials live in the shell
that runs Alloy; none of them lands in a file of this repo.

1. Grafana Cloud, free tier: create the stack (any region). The stack slug stays out
   of this repo.
2. In the stack's portal, the write credentials for Alloy: the Prometheus remote-write
   endpoint and the Loki push endpoint, each with a user and a key. Export them, with
   the absolute path of this checkout, in the shell that will run Alloy:
   `GCLOUD_PROM_URL`, `GCLOUD_PROM_USER`, `GCLOUD_PROM_KEY`, `GCLOUD_LOKI_URL`,
   `GCLOUD_LOKI_USER`, `GCLOUD_LOKI_KEY`, `KONAN_REPO`.
3. Install Alloy from the Grafana tap: `brew tap grafana/grafana`, then
   `brew install grafana/grafana/alloy`. Validate the committed configuration:
   `alloy validate docs/rims/grafana-cloud.alloy` exits 0 (with placeholder values in
   the seven variables it is the intent's check 1).
4. Start the lab (`scripts/lab.sh start`); in the shell of step 2, run Alloy in the
   foreground: `alloy run docs/rims/grafana-cloud.alloy`. It scrapes `/metrics` every
   15 s and tails `lab/logs/app.log*` as JSON lines — stream label `job="faultline"`,
   `level` and `event` as labels, `request_id` as a field. The Homebrew service is the
   optional form: it reads its own `config.alloy` and `config.env` under the Homebrew
   prefix, not this shell.
5. Verify in Grafana Cloud, within a few minutes of traffic (15 s scrapes, log shipping
   adds seconds): Explore → Prometheus,
   `http_requests_total` (and `faultline_chaos_enabled` when chaos is on);
   Explore → Loki, `{job="faultline"} | json` shows the request lines with their
   `request_id`.
6. Distinguish probes from traffic: `{job="faultline"} | json | request_id=~"konan-.*"`
   returns the konan-stamped probes only (`scripts/probe.sh` stamps
   `konan-<epoch>-<pid>`); seeded traffic (`scripts/scenario.sh get`, `order`) carries
   the lab's own ids.

## Operator setup — the rim (#54, not yet)

These steps belong to the rim and stay as prepared: a **service account** with the
Viewer role and its token in env `GRAFANA_SERVICE_ACCOUNT_TOKEN`, the stack URL in
`GRAFANA_URL`; the exact tool names pinned from a connected server (the TODO above);
the settings allowlist; then the blind run (#55).

## Known gaps of this rim

Same lab behind a real plane: the taxonomy gaps of `docs/lab.md` apply unchanged.
Additional honesty: shipping adds delay — log lines and metric samples arrive with
Alloy's scrape/push cadence (seconds), so "now" in this rim is eventually-now; the
journal's timeline reasons from plane timestamps, not file timestamps.
