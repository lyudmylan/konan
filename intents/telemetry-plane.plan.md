# Plan: the telemetry plane of the adapter proof (#53)

Intent: `intents/telemetry-plane.md`. Written 2026-11-03; the work starts after the leader accepts it in the
conversation.

## The shape of the change

One branch, `53-telemetry-plane`. The work has two hands. The operator's: the Grafana Cloud stack, the write
credentials in a shell, Alloy installed. The agent's: the committed configuration, the validate run, the
operator section of the adapter document, and the receipt in the change request. The plane goes live with the
lab running on the operator computer, one staging, and two Explore views. Nothing of the investigate skill,
the settings, or the contract part of the adapter document changes here.

## Steps

1. Operator, any time before step 4: a Grafana Cloud stack on the free tier; from its portal the Prometheus
   remote-write and the Loki push credentials (a URL, a user and a key for each) exported in a shell under
   the seven names of the intent, with `KONAN_REPO` as the absolute path of this checkout; Alloy installed with
   `brew tap grafana/grafana` and `brew install grafana/grafana/alloy`.
2. Agent: `git mv docs/adapters/alloy-config.example.alloy docs/adapters/grafana-cloud.alloy` (`lab/` is not
   tracked, so the configuration lives with the adapter); the file-match target gains the static label
   `job = "faultline"`; the `stage.json` expressions match the field names of the lab's request lines
   (`event`, `request_id`, verified below); check 1 with placeholder values once Alloy is installed; check 2.
3. Agent: `docs/adapters/grafana-cloud.md`, "Operator setup" rewritten as the steps that run: step 1, the
   validate command, `alloy run docs/adapters/grafana-cloud.alloy` in a shell that holds the seven variables,
   the Homebrew service as the optional form in one line (its own `config.alloy` and `config.env` under
   the Homebrew prefix), the two Explore views, and the LogQL query
   `{job="faultline"} | json | request_id=~"konan-.*"`; the pointer to the example file replaced by the
   pointer to `docs/adapters/grafana-cloud.alloy`; check 3.
4. Operator with the agent: `scripts/lab.sh start`; `alloy run docs/adapters/grafana-cloud.alloy` in a second
   terminal; the D1 staging (eval-side, prompted) with seeded traffic through `scripts/scenario.sh get` and
   `order` and one `scripts/probe.sh` call; Explore, Prometheus and Explore, Loki; the LogQL query; checks 5
   to 8 recorded in the change request as text.
5. The change request: `Closes #53`; checks 1 to 4 run, 5 to 8 recorded; the tier is the one that
   `charter.toml` gives the changed paths (high when this plan changes); the leader's approve in the
   conversation; the merge. The epic (#58) gets the decision of #54 to make next: the hosted Grafana Cloud
   MCP server or the open-source binary.

## Files

`docs/adapters/grafana-cloud.alloy` (renamed from `docs/adapters/alloy-config.example.alloy`),
`docs/adapters/grafana-cloud.md`, `intents/telemetry-plane.md` (check 2, with the work), and this file. Not changed: `docs/adapters/grafana-cloud.mcp.json.example`,
`.claude/settings.json`, `.gitignore`, `skills/**`, `scripts/**`, `docs/product.md` (no code path changes).

## Tests

The four commands of checks 1 to 4; check 1 on the operator computer only.

## What the work changed in this plan (2026-11-03)

- Alloy v1.21.3, installed by the agent from the Grafana tap on the leader's word, deprecates the `env()`
  function for `sys.env()`, and `alloy validate` fails on the deprecation; the configuration uses
  `sys.env()`. The attributes of a block go one per line (`basic_auth`), not comma-separated on one line.
- Check 2 of the intent names `__path__ = sys.env("KONAN_REPO")`; the count of distinct credential names
  is unchanged, because the grep matches inside `sys.env(`. Review round 1 of the change request added two
  clauses to check 2, the stream label `job = "faultline"` and `scrape_interval = "15s"`, so the scope's
  promises have a check; and check 7 says "within a few minutes", tied to the 15 s scrape.
- The draft change request opened after the agent's steps, so the operator's receipt has its place; it
  leaves draft when checks 1 and 5 to 8 are recorded.

## Facts the plan rests on (as of 2026-11-03)

- Alloy on macOS installs from the Grafana tap: `brew tap grafana/grafana`, `brew install
  grafana/grafana/alloy`. Its Homebrew service reads `config.alloy`, `extra-args.txt` and `config.env`
  (export lines) under the Homebrew prefix, not the shell's environment; a foreground `alloy run <path>`
  reads the shell's environment. Source: the Grafana Alloy documentation (set up, install, macOS; configure,
  macOS).
- `alloy validate <path>` checks the syntax, missing components, unset required properties and unknown
  properties, and exits non-zero on a failure. Source: the Grafana Alloy CLI reference.
- The Grafana MCP server exists in two forms: the hosted Grafana Cloud MCP server (OAuth 2.1, public
  preview, user-scoped) and the open-source `mcp-grafana` server (a service-account token in the
  environment, a `--disable-write` flag that removes the write tools). Source: the Grafana Cloud
  documentation (AI tools, MCP servers) and the `mcp-grafana` README. The choice belongs to #54.
- On the operator computer today: no Alloy, no MCP binary, no Grafana or Alloy variable in the shell (names
  checked, never values).
- The lab serves Prometheus text at `127.0.0.1:8000/metrics` (`http_exceptions_total`,
  `http_request_duration_seconds_sum`, `faultline_chaos_enabled` are named in `docs/lab.md`) and writes
  JSON lines to `lab/logs/app.log` with `ts`, `level`, `logger` and `message`; request lines carry
  `request_id`, `event` (`request`, `unhandled_exception`, `order_created`), `method`, `path`, `status`
  and `duration_ms` (read from the committed log on 2026-11-03). `scripts/probe.sh` stamps its requests
  `konan-<epoch>-<pid>`.
