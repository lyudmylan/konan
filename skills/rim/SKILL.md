---
name: rim
description: "Use to onboard a real target into konan — /rim: interview the operator about their observability surface, write the rim (surface-contract doc + read-only permission profile + MCP config), then smoke-test it with one benign investigation. Configuration, never code."
---

# rim — bring your own target

A target plugs into konan as a **thin rim**: a surface-contract doc (what the
investigator may read, through which tools), a permission profile (the mechanical
boundary), and MCP/CLI config. The methodology never changes per target. Your job is
to produce that rim WITH the operator — interview, write, verify — and nothing else.

Ground rules, before anything:

- **Read-only by construction.** The rim never gains a write tool. If the operator
  asks for remediation surfaces, record the wish and point at the roadmap — not here.
- **Pin tool names from reality.** Allowlists are written from what a connected
  server actually serves (`/mcp` listing), never from documentation memory.
- **Credentials are the operator's hands.** You name the env var; they fill it. A
  token never lands in a file you write.

## 1. Interview — what exists, not what should

Ask, in this order, and write the answers down:

1. Where do **metrics** live? (Grafana/Prometheus, Datadog, CloudWatch, …) Is there
   an official MCP server or a read-only CLI for it?
2. Where do **logs** live? (Loki, Sentry, CloudWatch Logs, files…) Same question.
3. Is there a **safe probe surface** — health/status endpoints the team already
   considers harmless? (Absent is a fine answer; many rims are plane-only.)
4. What is **out of bounds** even read-only? (Customer data, admin surfaces,
   cost-sensitive query patterns.)
5. Who **owns** this rim — who approves changes to it? (The permission profile is a
   reviewed artifact; name the owner in the doc.)

## 2. Write the rim

Create `docs/rims/<target>.md` in the shape of the prepared example
(`docs/rims/grafana-cloud.md`): the investigator's surface — all of it; the boundary
(MCP config + allowlist + what stays denied); operator setup; known gaps stated
honestly (shipping delay, missing signal types); ground-truth exclusions if this rim
will ever be evaluated.

Alongside it:

- `.mcp.json` entries (or a documented CLI allowlist) with env-var placeholders.
- The `.claude/settings.json` allow rules for exactly the pinned read tools —
  `mcp__<server>__<tool>` form — nothing wildcarded, no write tool listed.

## 3. Verify mechanically, then smoke

1. Operator fills credentials; connect; list the served tools; **pin the allowlist
   to that list** (fix the doc if it guessed).
2. Confirm a write tool call is NOT allowed (it must prompt or be denied — show the
   operator the denial; that is the boundary working, not a bug).
3. Smoke run: `/konan <a benign complaint the operator chooses>` with the new rim
   doc as the surface contract. Read the journal together: every claim cites plane
   evidence; local files of this repo's lab are not part of a foreign rim.

## 4. Hand over

The rim doc is the contract; changes to it or the profile are SPEC-grade (PR with
rationale — same rule as the lab boundary, `AGENTS.md`). Close by naming what the
rim cannot see (the gaps section) — an honest rim states its blind spots, because
the journal's Gaps section will anyway.
