# Rim: Grafana Cloud (via the official mcp-grafana server) — PREPARED, not yet live

Status: template + prepared configs (#54). It becomes the surface contract when the
telemetry plane (#53) is live and the placeholders below are filled from the real
stack. Until then `docs/lab.md` remains konan's only active rim.

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

## Operator setup (one-time) — the checklist

1. Grafana Cloud free tier: create the stack (any region). Note the stack slug.
2. Create a **service account** with Viewer role + token → env
   `GRAFANA_SERVICE_ACCOUNT_TOKEN`; stack URL → `GRAFANA_URL`.
3. Metrics + logs write keys for Alloy (the portal generates them with the agent
   config): env `GCLOUD_PROM_URL/USER/KEY`, `GCLOUD_LOKI_URL/USER/KEY`.
4. Install Alloy on the operator machine (`brew install grafana-alloy` or the
   portal's installer) and run it with `alloy-config.example.alloy` (paths filled).
5. Start the lab; verify in Grafana Cloud: `faultline_chaos_enabled` visible in
   Explore→Prometheus; JSON lines with `request_id` in Explore→Loki.
6. Fill this doc's TODOs (tool names, datasource uids); land the settings allowlist;
   then the blind run (#55).

## Known gaps of this rim

Same lab behind a real plane: the taxonomy gaps of `docs/lab.md` apply unchanged.
Additional honesty: shipping adds delay — log lines and metric samples arrive with
Alloy's scrape/push cadence (seconds), so "now" in this rim is eventually-now; the
journal's timeline reasons from plane timestamps, not file timestamps.
