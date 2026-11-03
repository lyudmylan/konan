# Intent: the telemetry plane of the rim proof

Work item: #53. Status: planned. Approval: a person merges the change request that adds this file.

## Goal

The lab's metrics and logs are readable in Grafana Cloud the way a real team's telemetry is read, through one
committed Alloy configuration whose credentials live only in the operator's environment.

## In scope

- `docs/rims/grafana-cloud.alloy`: the Alloy configuration of the lab, renamed from
  `docs/rims/alloy-config.example.alloy` (one definition, tracked with the rim; `lab/` holds runtime files
  and is not tracked): a scrape of the lab's `/metrics` at `127.0.0.1:8000` every 15 s into Grafana Cloud
  Prometheus; a tail of `lab/logs/app.log*` (JSON lines) into Grafana Cloud Loki with the static stream
  label `job="faultline"`, `level` and `event` as labels and `request_id` as a field; the
  write credentials and the repository path read from the environment (`GCLOUD_PROM_URL`,
  `GCLOUD_PROM_USER`, `GCLOUD_PROM_KEY`, `GCLOUD_LOKI_URL`, `GCLOUD_LOKI_USER`, `GCLOUD_LOKI_KEY`,
  `KONAN_REPO`); no literal credential and no absolute path in the file.
- `docs/rims/grafana-cloud.md`, "Operator setup": the steps as they run on this stack today: the Homebrew tap
  and formula of Alloy, the validate command, the foreground run from a shell that holds the seven variables
  (the Homebrew service reads its own files under the Homebrew prefix; it is the optional form, in one line),
  the two Explore views that show the shipped data, and the LogQL query that separates konan-stamped probes
  (`request_id` starts with `konan-`) from seeded traffic. The status line of the document stays "prepared":
  the document becomes the surface contract with the rim (#54).
- The receipt of the plane in the change request, as text: the time of one D1 staging, the metric and the
  log lines seen in the two Explore views, and the result of the LogQL query. No stack slug, no key.

## Out of scope

The rim (#54): the MCP server, `.mcp.json`, the tool allowlist, the service account; the choice between the
hosted Grafana Cloud MCP server and the open-source `mcp-grafana` binary is a decision of #54. The blind run
(#55). Sentry; a cloud host for the lab; a change to the lab's code (faultline governs itself); a change to
the investigate skill; a Grafana dashboard or alert rule.

## Acceptance checks

## Automatic checks

1. The Alloy configuration is valid: the validate command exits 0 with placeholder values in the seven
   variables. It runs on the operator computer, where Alloy is installed; it is not part of the quality gate.
   command: `KONAN_REPO=. GCLOUD_PROM_URL=u GCLOUD_PROM_USER=u GCLOUD_PROM_KEY=k GCLOUD_LOKI_URL=u GCLOUD_LOKI_USER=u GCLOUD_LOKI_KEY=k alloy validate docs/rims/grafana-cloud.alloy`
2. The configuration reads six distinct credential names and the path from the environment, holds no
   literal credential and no absolute path, and pins the stream label and the scrape interval; the example
   file is gone.
   command: `test "$(grep -o 'env("GCLOUD_[A-Z_]*")' docs/rims/grafana-cloud.alloy | sort -u | wc -l | tr -d ' ')" -eq 6 && grep -q '__path__ = sys.env("KONAN_REPO")' docs/rims/grafana-cloud.alloy && ! grep -Eq '"/(Users|home)/|glc_' docs/rims/grafana-cloud.alloy && grep -q 'job = "faultline"' docs/rims/grafana-cloud.alloy && grep -q 'scrape_interval = "15s"' docs/rims/grafana-cloud.alloy && ! test -e docs/rims/alloy-config.example.alloy`
   (`sys.env()`, not `env()`: see the plan)
3. The rim document names the tap and formula, the validate command, the foreground run, and the LogQL
   matcher on the konan-stamped request ids; the pointer to the example file is gone.
   command: `grep -q 'brew install grafana/grafana/alloy' docs/rims/grafana-cloud.md && grep -q 'alloy validate' docs/rims/grafana-cloud.md && grep -q 'alloy run' docs/rims/grafana-cloud.md && grep -q 'request_id=~"konan-' docs/rims/grafana-cloud.md && ! grep -q 'alloy-config.example' docs/rims/grafana-cloud.md`
4. The quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`

## Manual checks

5. A Grafana Cloud stack exists, and the six write credentials from its portal plus `KONAN_REPO` are exported
   in the shell that runs Alloy. who: the operator. Not automatic: the account and the credentials are the
   operator's hands; no credential lands in a file that the agent writes.
6. With the lab started, Alloy runs in the foreground with `docs/rims/grafana-cloud.alloy` and reports no error in
   its first minute. who: the operator. Not automatic: it needs the credentials of check 5 and the lab on
   the operator computer.
7. One D1 staging is visible in Grafana Cloud within a few minutes (the scrape interval is 15 s; the log
   shipping adds seconds): the lab's request counter in Explore,
   Prometheus, and its JSON log lines with `request_id` in Explore, Loki. who: the operator with the agent.
   Not automatic: in this work item the plane is read through the browser; the mechanical read lands with
   the rim (#54) and is exercised by the blind run (#55).
8. Seeded traffic and konan-stamped probes are distinguishable: the LogQL query of the rim document returns
   the `konan-` request ids apart from the seeded traffic of `scripts/scenario.sh`. who: the operator with
   the agent. Not automatic: the same reason as check 7.
