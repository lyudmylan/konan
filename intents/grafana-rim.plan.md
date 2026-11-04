# Plan: the Grafana Cloud rim (#54)

Intent: `intents/grafana-rim.md`. Written 2026-11-04; the work starts after the leader accepts it in the
conversation.

## The shape of the change

One branch, `54-grafana-rim`. The rim is produced through the rim skill (`/rim`), as the epic decided: the
interview, the written rim, the mechanical verification, the smoke run. Two hands again. The operator's: the
service account and its token, the server installed, the rim session, the answers of the interview, the
reading of the smoke journal. The agent's: the configuration, the allowlist, the one Setup line of the
investigate skill, the rim document, the two documents, the receipts.

## Steps

1. Operator, any time before step 3: in Grafana Cloud, Administration, Users and access, Service accounts: a
   service account with the Viewer role and one token, exported as `GRAFANA_SERVICE_ACCOUNT_TOKEN`; the
   stack address exported as `GRAFANA_URL`; `brew install mcp-grafana` (the Homebrew core formula);
   `mcp-grafana --help` for the exact flag forms. Alloy and the lab run again for step 5.
2. Agent: `git mv docs/rims/grafana-cloud.mcp.json.example docs/rims/grafana-cloud.mcp.json`; the arguments
   `--disable-write` and `--enabled-tools prometheus,loki,datasource` (the flag forms read from
   `mcp-grafana --help` on the operator computer); the two placeholders; check 1.
3. Operator with the agent, the rim skill: the interview, five questions in the conversation (the answers are
   mostly known: Prometheus and Loki in Grafana Cloud through `mcp-grafana`; no probe surface in this rim,
   it is plane-only; out of bounds: the lab's files, `eval/`, the tracker, every write surface; the owner:
   the leader). Then the rim session, `claude --mcp-config docs/rims/grafana-cloud.mcp.json`, and `/mcp`:
   the served tool names, recorded as text; the allowlist written from that list (check 8); the no-write
   check with a temporary copy of the configuration outside the repository, deleted after it (check 9).
4. Agent: `.claude/settings.json` (the pinned entries and `Bash(printenv KONAN_RIM)`); the Setup line of
   `skills/investigate/SKILL.md`; `docs/rims/grafana-cloud.md` rewritten as the live contract (the tool
   names, the three layers, the operator setup, the citation form, the owner, the gaps, the Alloy run command
   with `--storage.path lab/alloy`); one sentence in `AGENTS.md`; the README section; checks 2, 3, 4, 6, 7.
5. Operator with the agent: the lab and Alloy running; `KONAN_RIM=docs/rims/grafana-cloud.md` exported; the
   smoke run `/konan <complaint>` in the rim session; the journal read together and committed under
   `journals/` (check 10); check 5.
6. The change request: `Closes #54` and `Closes #52` (the worked rim is the last item of the rim skill's
   definition of done); the served listing in its text; checks 1 to 7 run, 8 to 10 recorded; the tier is the
   one `charter.toml` gives the changed paths (`intents/**`, `.claude/settings.json` and `AGENTS.md` are
   high); the leader's approve in the conversation; the merge. The onboarding epic (#57) closes with #52,
   with a comment that names what it delivered; the rim-proof epic (#58) continues with the blind run (#55).

## Files

`docs/rims/grafana-cloud.mcp.json` (renamed from the example), `.claude/settings.json`,
`skills/investigate/SKILL.md` (one step), `docs/rims/grafana-cloud.md`, `AGENTS.md` (one sentence),
`README.md` (one section), `journals/<date>-<slug>.md` (the smoke journal), `intents/grafana-rim.md` (with
the work, if a check changes), and this file. Not changed: `docs/rims/grafana-cloud.alloy`, `hooks/**`,
`scripts/**`, `eval/**`, the lenses, `skills/investigate/report-contract.md`,
`skills/investigate/journal.schema.json`, `skills/konan/**`, `skills/oncall/**`, `skills/rim/**`,
`docs/product.md`.

## Tests

The seven commands of checks 1 to 7; `python3 hooks/tests.py` stays green (the hook does not change). Check 5
runs after step 5 only.

## Facts the plan rests on (as of 2026-11-04)

- `mcp-grafana` installs as a Homebrew core formula (`brew info mcp-grafana`), with `uvx mcp-grafana`, a
  release binary, Docker and Go as the other forms. It reads `GRAFANA_URL` and
  `GRAFANA_SERVICE_ACCOUNT_TOKEN`; `--disable-write` removes the write tools (dashboards and folders,
  incidents, alerting writes, annotations, snapshots, deep links, raw SQL); `--disable-<category>` removes a
  category; `--enabled-tools` takes a comma-separated list of categories. The README names about six read
  tools in each of the Prometheus and Loki categories and a datasource list; those names are unpinned, and
  the rim document is the one list, written from the served listing. Source: the `mcp-grafana` README.
- Claude Code expands `${VAR}` in an MCP configuration file; `--mcp-config <file>` loads servers for one
  session; a permission rule `mcp__<server>__<tool>` allows one tool, `mcp__<server>` a whole server; a tool
  that no rule allows asks in an interactive session and fails closed in `-p`. Source: the Claude Code
  documentation (MCP, permissions).
- The investigate skill reads one surface contract in Setup step 1, with `docs/lab.md` as the default; the
  journal schema requires `surface_contract`; the lenses name no lab path. `eval/run.py` sends
  `/konan <complaint>` and nothing else: the rim plumbing of the runner is #55's.
- On the operator computer: no `mcp-grafana` binary; `uvx`, `jq` and Docker present; Alloy v1.21.3; the
  telemetry plane proven on 2026-11-04 (#53).
