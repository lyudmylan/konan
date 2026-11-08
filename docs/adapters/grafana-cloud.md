# Adapter: Grafana Cloud, through the official mcp-grafana server

Status: live. The telemetry plane (#53) ships the lab's metrics and logs to Grafana Cloud
with the committed Alloy configuration `grafana-cloud.alloy`; the adapter (#54) reads them
back through the open-source `mcp-grafana` server, with every tool the investigator may
call named below and in `.claude/settings.json`. This document is the surface contract
of that adapter. `docs/lab.md` stays the contract of the lab adapter, the default.

Owner: the leader of this repository. A change to this document, to
`docs/adapters/grafana-cloud.mcp.json` or to the allowlist in `.claude/settings.json` goes
through a change request at the high tier of `charter.toml`, with its reason.

This is the first non-lab adapter: the investigator's whole evidence surface is Grafana
Cloud — metrics (Prometheus) and logs (Loki) shipped from the lab by Grafana Alloy —
exactly like a real team's stack. Under this adapter the local files under `lab/` and the
probe script are **out of bounds**: evidence is what the plane serves.

## A session under this adapter

In a shell that holds the two credentials of the adapter (the operator setup below):

```sh
export KONAN_ADAPTER=docs/adapters/grafana-cloud.md
claude --permission-mode manual --mcp-config docs/adapters/grafana-cloud.mcp.json
```

The investigate skill reads `KONAN_ADAPTER` in its Setup step and takes this document as the
surface contract; the journal's `surface_contract` field names it. `/mcp` in the session
shows the server `grafana` connected with the tools of the surface, and nothing else.

## The investigator's surface — all of it

The server starts with `--disable-write` and `--enabled-tools prometheus,loki,datasource`
(`grafana-cloud.mcp.json`). The tools below are the ones a connected session listed on
2026-11-04; each name, prefixed with the server's name as the settings write it, is one
allow entry of `.claude/settings.json`, and the two lists are kept equal (the intent's
check 2). When the
server version changes, the list is pinned again from a listing, never from documentation.

1. **Prometheus**, instant and range queries over the shipped metrics, and their names,
   labels and metadata: `mcp__grafana__query_prometheus`,
   `mcp__grafana__query_prometheus_histogram`, `mcp__grafana__list_prometheus_metric_names`,
   `mcp__grafana__list_prometheus_metric_metadata`, `mcp__grafana__list_prometheus_label_names`,
   `mcp__grafana__list_prometheus_label_values`.
2. **Loki**, LogQL over the shipped JSON log lines, their labels, their volume and their
   patterns: `mcp__grafana__query_loki_logs`, `mcp__grafana__query_loki_stats`,
   `mcp__grafana__query_loki_patterns`, `mcp__grafana__list_loki_label_names`,
   `mcp__grafana__list_loki_label_values`, `mcp__grafana__analyze_loki_labels`.
3. **Datasource metadata**, to address 1 and 2: `mcp__grafana__list_datasources`,
   `mcp__grafana__get_datasource`, `mcp__grafana__check_datasources_health`.

What the plane holds for the lab: the metrics `http_requests_total`,
`http_exceptions_total`, the request duration summary, `faultline_chaos_enabled` and the
process gauges, scraped every 15 s; the log stream `{job="faultline"}` with the labels
`level` and `event` and the JSON fields `request_id`, `method`, `path`, `status`,
`duration_ms`, parsed with `| json`. Under this adapter the investigator sends no probe, so
every request line is user traffic or the eval-side staging; the matcher
`request_id=~"konan-.*"` marks the probes of the lab adapter, when both adapters share a stack. The
datasource uids of a Grafana Cloud stack are `grafanacloud-prom` (Prometheus) and
`grafanacloud-logs` (Loki); `list_datasources` confirms them.

## How to cite plane evidence

Every claim cites the tool, the query, the time range, and what came back: the metric
value, or the log line quoted with its `ts`. The journal's timeline reasons from plane
timestamps. Two shapes:

- `query_prometheus`, `sum by (status) (http_requests_total{path="/products/{product_id}"})`,
  the range, the values per status.
- `query_loki_logs`, `{job="faultline"} | json | status="500"`, the range, the quoted line.

## Boundary

Three mechanical layers on the Grafana side, and one rule of the skill on the lab side:

1. **The service account has the Viewer role.** Grafana refuses a write from it, whatever
   the server sends.
2. **The server serves no write tool.** `--disable-write` removes them, and the three
   enabled categories leave out dashboards, alerting, annotations, incidents, snapshots
   and the raw API tool. The token lives in the environment
   (`GRAFANA_SERVICE_ACCOUNT_TOKEN`), never in a file of this repository.
3. **The settings allow exactly the served read tools**, one entry each, no wildcard, no
   server-wide rule. A tool outside the list asks in an interactive session in the
   manual permission mode (`--permission-mode manual`, the mode of the session command
   above); in the auto mode the harness's classifier decides for it instead, so a
   session under this adapter runs in the manual mode; a headless session fails closed. The
   boundary hook stays active for Bash.
4. **The lab is out of bounds by the rule of the skill, not mechanically.** The Setup step
   of the investigate skill excludes the files under `lab/` and the probe script under a
   adapter document; the settings keep the probe allowed and the hook is silent on `lab/`
   reads outside blind mode. A mechanical exclusion under an adapter is a later work item.

Also out of bounds, read-only or not: `eval/` (the ground truth), the tracker, the
faultline checkout (the blinding contract of `eval/README.md`), and in Grafana
everything that is not a metric or log query: dashboards, alert rules, annotations,
user and team data.

## Operator setup — the telemetry plane (#53)

The steps as they run on the operator computer. The credentials live in the shell
that runs Alloy; none of them lands in a file of this repo.

1. Grafana Cloud, free tier: create the stack (any region). The stack slug stays out
   of this repo.
2. In the stack's portal, the write credentials for Alloy: the Prometheus remote-write
   endpoint and the Loki push endpoint, each with a user and a key. Export them, with
   the absolute path of this checkout, in the shell that will run Alloy:
   `GCLOUD_PROM_URL`, `GCLOUD_PROM_USER`, `GCLOUD_PROM_KEY`, `GCLOUD_LOKI_URL`,
   `GCLOUD_LOKI_USER`, `GCLOUD_LOKI_KEY`, `KONAN_REPO`. The Loki URL is the push path,
   `https://<loki host>/loki/api/v1/push`; the base address alone answers 405.
3. Install Alloy from the Grafana tap: `brew tap grafana/grafana`, then
   `brew install grafana/grafana/alloy`. Validate the committed configuration:
   `alloy validate docs/adapters/grafana-cloud.alloy` exits 0 (with placeholder values in
   the seven variables it is the intent's check 1).
4. Start the lab (`scripts/lab.sh start`); in the shell of step 2, run Alloy in the
   foreground: `alloy run --storage.path lab/alloy docs/adapters/grafana-cloud.alloy`. The
   storage flag keeps Alloy's position files under the untracked `lab/`; without it
   Alloy writes a `data-alloy/` directory into the checkout. It scrapes `/metrics` every
   15 s and tails `lab/logs/app.log*` as JSON lines — stream label `job="faultline"`,
   `level` and `event` as labels, `request_id` as a field. The Homebrew service is the
   optional form: it reads its own `config.alloy` and `config.env` under the Homebrew
   prefix, not this shell. Loki refuses lines older than its maximum age (a week by
   default), so an old log under `lab/logs/` is moved aside before the first run.
5. Verify in Grafana Cloud, within a few minutes of traffic (15 s scrapes, log shipping
   adds seconds): Explore → Prometheus,
   `http_requests_total` (and `faultline_chaos_enabled` when chaos is on);
   Explore → Loki, `{job="faultline"} | json` shows the request lines with their
   `request_id`.
6. Distinguish probes from traffic: `{job="faultline"} | json | request_id=~"konan-.*"`
   returns the konan-stamped probes only (`scripts/probe.sh` stamps
   `konan-<epoch>-<pid>`); seeded traffic (`scripts/scenario.sh get`, `order`) carries
   the lab's own ids.

## Operator setup — the adapter (#54)

1. In the stack's Grafana: Administration, Users and access, Service accounts; add a
   service account with the **Viewer** role and one token. Export the token as
   `GRAFANA_SERVICE_ACCOUNT_TOKEN` and the stack address as `GRAFANA_URL`
   (`https://<stack>.grafana.net`), in the shell of the adapter sessions.
2. Install the server: `brew install mcp-grafana` (the Homebrew core formula; the
   README of the server also offers `uvx mcp-grafana`, a release binary, Docker and
   Go).
3. Start a session as above and type `/mcp`: the server `grafana` is connected and lists
   the tools of the surface. That listing is the source of the allowlist; when it
   differs from the list above, the list and the settings change together, through a
   change request.
4. With the lab and Alloy running (the plane must hold data) and `KONAN_ADAPTER` exported,
   `/konan <complaint>` runs an investigation under this adapter.

The no-write check of the adapter skill: once, with a temporary copy of the configuration
outside this repository, without `--disable-write` and in the manual permission mode, the
write tools are listed and a call of one of them asks and is declined; the committed file
keeps its flag.

## Known gaps of this adapter

- Same lab behind a real plane: the taxonomy gaps of `docs/lab.md` apply unchanged.
- Shipping adds delay: log lines and metric samples arrive with Alloy's scrape and push
  cadence (seconds), so "now" in this adapter is eventually-now; the journal's timeline
  reasons from plane timestamps, not file timestamps.
- No probe surface: the investigator cannot ask the service anything directly. A signal
  that only a request would reveal (an endpoint's current answer) is invisible here;
  it is a latent finding at best, from the counters.
- The exclusion of the lab's files and probes under this adapter is a rule of the skill, not
  a mechanical boundary (the Boundary section, layer 4); a journal that cites a local
  file fails the review, not a hook.
- The tool list is pinned to one server version; a new version can add or rename tools,
  and the allowlist is pinned again from the listing.
