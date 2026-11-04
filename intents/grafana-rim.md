# Intent: the Grafana Cloud rim

Work item: #54 (the worked rim that closes #52). Status: planned. Approval: a person merges the change
request that adds this file.

## Goal

The investigator reads a real observability plane through a read-only rim: the lab's metrics and logs in
Grafana Cloud, through the open-source `mcp-grafana` server, with every tool it may call named in one
committed allowlist and no write tool reachable, as configuration and never code, reproducible from the
rim document with one service account.

## In scope

- `docs/rims/grafana-cloud.mcp.json`, renamed from `docs/rims/grafana-cloud.mcp.json.example`: the server
  `mcp-grafana` with the argument `--disable-write`, the tool categories limited to the ones the rim uses
  (the flag names from the binary's own help), and the two credentials as placeholders from the environment
  (`GRAFANA_URL`, `GRAFANA_SERVICE_ACCOUNT_TOKEN`); no literal token, no stack address. The file is loaded
  per session with `claude --mcp-config docs/rims/grafana-cloud.mcp.json`, not as a root `.mcp.json`: a root
  file would start the server in every session of this repository, where the lab rim is the default
  surface; a rim is opt-in per session.
- `.claude/settings.json`: `allow` entries in the form `mcp__grafana__<tool>` for exactly the read tools the
  connected server serves (pinned from its listing, never from documentation memory), and one entry
  `Bash(printenv KONAN_RIM)`; no wildcard, no server-wide entry, no write tool.
- `skills/investigate/SKILL.md`, Setup step 1: the surface contract is the rim document that `KONAN_RIM`
  names (read with `printenv KONAN_RIM`), `docs/lab.md` when it is unset; under a rim document the lab's
  files and probes are out of bounds; the journal's `surface_contract` field names the document in use.
  No other change to the skill, its lenses or the report contract. This exclusion is a rule of the skill,
  not a mechanical boundary: the settings keep `scripts/probe.sh` allowed and the hook is silent on `lab/`
  reads outside blind mode. The mechanical boundary of this rim is the three layers on the Grafana side; a
  mechanical exclusion of the lab under a rim is a later work item.
- `docs/rims/grafana-cloud.md`, the live surface contract: the status line "Status: live"; the surface as the
  pinned tool names (the `mcp__grafana__` names appear only in that list, and no write tool is named in
  that form anywhere in the document); the boundary in three layers (the Viewer service account, `--disable-write`, the
  allowlist); the operator setup of the rim (the service account, the two variables, the Homebrew formula,
  the session command with `--mcp-config`, `/mcp`, `KONAN_RIM`); the citation form of plane evidence (the
  tool, the query, the time); the owner of the rim; the Alloy run command with its storage flag (the open
  finding of #53); the known gaps, among them that the exclusion of the lab's files and probes is a rule of
  the skill and not a mechanical boundary.
- `AGENTS.md`, the lab boundary: one sentence that under a rim document the investigator's hand is the rim's
  read-only MCP tools named in `.claude/settings.json`, and that `KONAN_RIM` names the rim.
- `README.md`, "Bring your own target": the Grafana Cloud rim is live, with the session command.
- The receipts: the served tool listing as text in the change request, and the smoke-run journal committed
  under `journals/`.

## Out of scope

The blind run (#55) and the plumbing of `--mcp-config` and `KONAN_RIM` into `eval/run.py`. A trigger profile
from Grafana alerting (#35). Any write tool, `--enable-write-tools`, alert rules. The dashboard tools, read
or write: the stack holds no dashboard of the lab, and every tool the investigator needs is a query tool,
so the category stays off at the server. The hosted Grafana Cloud MCP server (decided against, epic #58).
A mechanical exclusion of the lab's files and probes under a rim (a hook change; a later work item). The
plugin's `hooks/hooks.json`. The Alloy configuration (merged with #53). The lenses, the report contract,
the journal schema, the oncall and setup skills. Rims of other targets.

## Acceptance checks

### Automatic checks

1. The MCP configuration names the server, carries exactly the write-tools-off flag and the three enabled
   categories (the flag forms pinned from `mcp-grafana --help` on 2026-11-04: `--disable-write`, and
   `--enabled-tools` with a comma-separated list), takes both credentials from the environment, holds no
   token and no stack address; the example file is gone.
   command: `jq -e '.mcpServers.grafana | .command == "mcp-grafana" and .args == ["--disable-write", "--enabled-tools", "prometheus,loki,datasource"] and .env.GRAFANA_URL == "${GRAFANA_URL}" and .env.GRAFANA_SERVICE_ACCOUNT_TOKEN == "${GRAFANA_SERVICE_ACCOUNT_TOKEN}"' docs/rims/grafana-cloud.mcp.json >/dev/null && ! grep -Eq 'glsa_|grafana\.net' docs/rims/grafana-cloud.mcp.json && ! test -e docs/rims/grafana-cloud.mcp.json.example`
2. The allowlist equals the tool list of the rim document, holds at least the query tools of Prometheus and
   Loki (the two names are confirmed or corrected from the listing of check 8; the work updates this
   command if they differ), and holds no write tool, no wildcard and no server-wide entry.
   command: `diff <(grep -o 'mcp__grafana__[a-z_]*' docs/rims/grafana-cloud.md | sort -u) <(jq -r '.permissions.allow[]' .claude/settings.json | grep '^mcp__grafana__' | sort -u) && jq -r '.permissions.allow[]' .claude/settings.json | grep -q '^mcp__grafana__query_prometheus$' && jq -r '.permissions.allow[]' .claude/settings.json | grep -q '^mcp__grafana__query_loki_logs$' && ! jq -r '.permissions.allow[]' .claude/settings.json | grep -Eq 'mcp__grafana__(update_|create_|delete_|add_|install_|.*_write|ask_assistant|generate_deeplink|query_sql|query_influxdb|grafana_api_request)|mcp__grafana__\*|^mcp__grafana$'`
3. The rim selection is wired: the skill reads `KONAN_RIM`, the settings allow that one read, and the rim
   document and `AGENTS.md` name it.
   command: `grep -q 'printenv KONAN_RIM' skills/investigate/SKILL.md && grep -q 'Bash(printenv KONAN_RIM)' .claude/settings.json && grep -q 'KONAN_RIM' docs/rims/grafana-cloud.md && grep -q 'KONAN_RIM' AGENTS.md`
4. The rim document is the live contract: the status, no prepared or go-live wording, the session command,
   the owner, and the Alloy run command with its storage flag.
   command: `grep -q '^Status: live' docs/rims/grafana-cloud.md && ! grep -qi 'prepared' docs/rims/grafana-cloud.md && ! grep -q 'TODO at go-live' docs/rims/grafana-cloud.md && grep -q -- '--mcp-config docs/rims/grafana-cloud.mcp.json' docs/rims/grafana-cloud.md && grep -q '^Owner:' docs/rims/grafana-cloud.md && grep -q 'alloy run --storage.path lab/alloy docs/rims/grafana-cloud.alloy' docs/rims/grafana-cloud.md`
5. The smoke-run journal names the rim as its surface contract, cites plane queries, and cites no lab file,
   no probe and no lab contract.
   command: `f=$(grep -l 'surface_contract: docs/rims/grafana-cloud.md' journals/*.md) && test "$(printf '%s\n' "$f" | wc -l | tr -d ' ')" -eq 1 && grep -Eq 'query_prometheus|query_loki' "$f" && ! grep -Eq 'lab/logs|probe\.sh|docs/lab\.md' "$f"`
   (one smoke journal under this rim; the blind run's journal (#55) is scored under its own intent)
6. The README section points at the live rim and its session command, and no longer calls it an example.
   command: `grep -q -- '--mcp-config docs/rims/grafana-cloud.mcp.json' README.md && ! grep -q 'prepared example rim' README.md`
7. The quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`

### Manual checks

8. The server connects with the operator's credentials and the tools are pinned from it: a Viewer service
   account and its token in `GRAFANA_SERVICE_ACCOUNT_TOKEN`, the stack address in `GRAFANA_URL`,
   `mcp-grafana` installed, a session started with `--mcp-config docs/rims/grafana-cloud.mcp.json`; `/mcp`
   shows the server connected and its tool list; the list is recorded as text in the change request, and the
   allowlist and the rim document hold exactly its read tools. who: the operator with the agent. Not
   automatic: the account and the token are the operator's hands, and the listing needs a live session.
9. No write reaches Grafana: in the session of check 8 the listing holds no write tool; in one session started
   with a temporary copy of the configuration outside the repository, without `--disable-write` and deleted
   after the check, a write tool is listed, its call is asked and not allowed, and the operator declines;
   nothing is sent, and the committed file keeps its flag. who: the operator with the agent. Not automatic:
   it needs the live session, and the denial is shown to the operator as the rim skill asks.
10. The smoke run: with the lab and Alloy running and `KONAN_RIM` set, `/konan <a benign complaint the
    operator chooses>` in the rim session; the journal read together: every claim cites a plane query (the
    tool, the query, the time), no lab file; the journal is committed under `journals/` and check 5 reads it.
    who: the operator with the agent. Not automatic: it calls the model, in the operator's session.
