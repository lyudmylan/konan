# Intent: the Grafana Cloud adapter

Work item: #54 (the worked adapter that closes #52). Status: planned. Approval: a person merges the change
request that adds this file.

## Goal

The investigator reads a real observability plane through a read-only adapter: the lab's metrics and logs in
Grafana Cloud, through the open-source `mcp-grafana` server, with every tool it may call named in one
committed allowlist and no write tool reachable, as configuration and never code, with one service account.

## In scope

- `docs/adapters/grafana-cloud.mcp.json`, renamed from `docs/adapters/grafana-cloud.mcp.json.example`: the server
  `mcp-grafana` with the argument `--disable-write`, the tool categories limited to the ones the adapter uses
  (the flag names from the binary's own help), and the two credentials as placeholders from the environment
  (`GRAFANA_URL`, `GRAFANA_SERVICE_ACCOUNT_TOKEN`); no literal token, no stack address. The file is loaded
  per session with `claude --mcp-config docs/adapters/grafana-cloud.mcp.json`, not as a root `.mcp.json`: a root
  file would start the server in every session of this repository, where the lab adapter is the default
  surface; an adapter is opt-in per session.
- `.claude/settings.json`: `allow` entries in the form `mcp__grafana__<tool>` for exactly the read tools the
  connected server serves (pinned from its listing, never from documentation memory), and one entry
  `Bash(printenv KONAN_ADAPTER)`; no wildcard, no server-wide entry, no write tool.
- `skills/investigate/SKILL.md`, Setup step 1: the surface contract is the adapter document that `KONAN_ADAPTER`
  names (read with `printenv KONAN_ADAPTER`), `docs/lab.md` when it is unset; under an adapter document the lab's
  files and probes are out of bounds; the journal's `surface_contract` field names the document in use.
  No other change to the skill, its lenses or the report contract. This exclusion is a rule of the skill,
  not a mechanical boundary: the settings keep `scripts/probe.sh` allowed and the hook is silent on `lab/`
  reads outside blind mode. The mechanical boundary of this adapter is the three layers on the Grafana side; a
  mechanical exclusion of the lab under an adapter is a later work item.
- `docs/adapters/grafana-cloud.md`, the live surface contract: the status line "Status: live"; the surface as the
  pinned tool names (the `mcp__grafana__` names appear only in that list, and no write tool is named in
  that form anywhere in the document); the boundary in three layers (the Viewer service account, `--disable-write`, the
  allowlist); the operator setup of the adapter (the service account, the two variables, the Homebrew formula,
  the session command with `--mcp-config` and `--permission-mode manual`, `/mcp`, `KONAN_ADAPTER`); the
  session command pins the manual permission mode, because the allowlist is not a boundary in the auto
  mode, where the harness's classifier decides for an unlisted call; the citation form of plane evidence
  (the tool, the query, the time); the datasource uids of the plane; the operator setup of the plane,
  carried over from #53; the owner of the adapter; the Alloy run command with its storage flag (the open
  finding of #53); the known gaps, among them that the exclusion of the lab's files and probes is a rule
  of the skill and not a mechanical boundary.
- `AGENTS.md`, the lab boundary: one sentence that under an adapter document the investigator's hand is the adapter's
  read-only MCP tools named in `.claude/settings.json`, and that `KONAN_ADAPTER` names the adapter.
- `README.md`, "Bring your own target": the Grafana Cloud adapter is live, with the session command.
- The receipts: the served tool listing as text in the change request, and the smoke-run journal committed
  under `journals/`.

## Out of scope

The blind run (#55) and the plumbing of `--mcp-config` and `KONAN_ADAPTER` into `eval/run.py`. A trigger profile
from Grafana alerting (#35). Any write tool, `--enable-write-tools`, alert rules. The dashboard tools, read
or write: the stack holds no dashboard of the lab, and every tool the investigator needs is a query tool,
so the category stays off at the server. The hosted Grafana Cloud MCP server (decided against, epic #58).
A mechanical exclusion of the lab's files and probes under an adapter (a hook change; a later work item). The
plugin's `hooks/hooks.json`. The Alloy configuration (merged with #53). The lenses, the report contract,
the journal schema, the oncall and setup skills. Adapters of other targets.

## Acceptance checks

### Automatic checks

1. The MCP configuration names the server, carries exactly the write-tools-off flag and the three enabled
   categories (the flag forms pinned from `mcp-grafana --help` on 2026-11-04: `--disable-write`, and
   `--enabled-tools` with a comma-separated list), takes both credentials from the environment, holds no
   token and no stack address; the example file is gone.
   command: `jq -e '.mcpServers.grafana | .command == "mcp-grafana" and .args == ["--disable-write", "--enabled-tools", "prometheus,loki,datasource"] and .env.GRAFANA_URL == "${GRAFANA_URL}" and .env.GRAFANA_SERVICE_ACCOUNT_TOKEN == "${GRAFANA_SERVICE_ACCOUNT_TOKEN}"' docs/adapters/grafana-cloud.mcp.json >/dev/null && ! grep -Eq 'glsa_|grafana\.net' docs/adapters/grafana-cloud.mcp.json && ! test -e docs/adapters/grafana-cloud.mcp.json.example`
2. The allowlist equals the tool list of the adapter document, holds at least the query tools of Prometheus and
   Loki, and holds no write tool, no wildcard and no server-wide entry.
   command: `diff <(grep -o 'mcp__grafana__[a-z_]*' docs/adapters/grafana-cloud.md | sort -u) <(jq -r '.permissions.allow[]' .claude/settings.json | grep '^mcp__grafana__' | sort -u) && jq -r '.permissions.allow[]' .claude/settings.json | grep -q '^mcp__grafana__query_prometheus$' && jq -r '.permissions.allow[]' .claude/settings.json | grep -q '^mcp__grafana__query_loki_logs$' && ! jq -r '.permissions.allow[]' .claude/settings.json | grep -Eq 'mcp__grafana__(update_|create_|delete_|add_|install_|.*_write|ask_assistant|generate_deeplink|query_sql|query_influxdb|grafana_api_request)|mcp__grafana__\*|^mcp__grafana$'`
3. The adapter selection is wired: the skill reads `KONAN_ADAPTER`, the settings allow that one read, and the adapter
   document and `AGENTS.md` name it.
   command: `grep -q 'printenv KONAN_ADAPTER' skills/investigate/SKILL.md && grep -q 'Bash(printenv KONAN_ADAPTER)' .claude/settings.json && grep -q 'KONAN_ADAPTER' docs/adapters/grafana-cloud.md && grep -q 'KONAN_ADAPTER' AGENTS.md`
4. The adapter document is the live contract: the status, no prepared or go-live wording, the session command,
   the owner, and the Alloy run command with its storage flag.
   command: `grep -q '^Status: live' docs/adapters/grafana-cloud.md && ! grep -qi 'prepared' docs/adapters/grafana-cloud.md && ! grep -q 'TODO at go-live' docs/adapters/grafana-cloud.md && grep -q -- '--mcp-config docs/adapters/grafana-cloud.mcp.json' docs/adapters/grafana-cloud.md && grep -q -- '--permission-mode manual' docs/adapters/grafana-cloud.md && grep -q '^Owner:' docs/adapters/grafana-cloud.md && grep -q 'alloy run --storage.path lab/alloy docs/adapters/grafana-cloud.alloy' docs/adapters/grafana-cloud.md`
5. The smoke-run journal, `journals/2026-11-08-product-page-500s.md`, names the adapter as its surface contract,
   cites plane queries, and cites no lab file, no probe and no lab contract.
   command: `f=journals/2026-11-08-product-page-500s.md && grep -q 'surface_contract: docs/adapters/grafana-cloud.md' "$f" && grep -Eq 'query_prometheus|query_loki' "$f" && ! grep -Eq '(^|[^a-z])lab/|probe\.sh|docs/lab\.md' "$f"`
6. The README section points at the live adapter and its session command in the manual permission mode, and
   no longer calls it an example.
   command: `grep -q -- '--mcp-config docs/adapters/grafana-cloud.mcp.json' README.md && grep -q -- '--permission-mode manual' README.md && ! grep -q 'prepared example adapter' README.md`
7. The quality checks of the contract pass. command: `charter-gate quality --contract charter.toml`

### Manual checks

8. The server connects with the operator's credentials and the tools are pinned from it: a Viewer service
   account and its token in `GRAFANA_SERVICE_ACCOUNT_TOKEN`, the stack address in `GRAFANA_URL`,
   `mcp-grafana` installed, a session started with `--mcp-config docs/adapters/grafana-cloud.mcp.json`; `/mcp`
   shows the server connected and its tool list; the list is recorded as text in the change request, and the
   allowlist and the adapter document hold exactly its read tools. who: the operator with the agent. Not
   automatic: the account and the token are the operator's hands, and the listing needs a live session.
9. No write reaches Grafana: in the session of check 8 the listing holds no write tool; in one session in
   the manual permission mode (`--permission-mode manual`), started with a temporary copy of the
   configuration outside the repository, without `--disable-write` and deleted after the check, a write
   tool is listed, its call is asked and not allowed, and the operator declines; nothing is sent, and the
   committed file keeps its flag. The manual mode is the one the check needs: in the auto mode the
   harness's classifier decides for an unlisted call and may let it through, so the allowlist is a boundary
   in the manual mode only. who: the operator with the agent. Not automatic: it needs the live session, and
   the denial is shown to the operator as the adapter skill asks.
10. The smoke run: with the lab and Alloy running and `KONAN_ADAPTER` set, `/konan <a benign complaint the
    operator chooses>` in the adapter session; the journal read together: every claim cites a plane query (the
    tool, the query, the time), no lab file; the journal is committed under `journals/` and check 5 reads it.
    who: the operator with the agent. Not automatic: it calls the model, in the operator's session.
