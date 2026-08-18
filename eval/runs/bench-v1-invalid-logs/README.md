# bench-v1 — first batch, INVALID (kept for the record, not scored into any table)

30 runs of claude-sonnet-5 (2026-08-18 evening) plus one aborted Opus run. The runner
of that batch restarted the lab process on `setup.lab: fresh` but did **not** delete
`lab/logs`, so every later run in an invocation could read the earlier runs' traffic and
incidents (e.g. the crash-r3 journal describes "three crashes and two restarts" — the
runner's own restarts). The protocol requires a clean lab per fixture; these runs violate
it and are excluded from `eval/BENCHMARK-results.md`. Fixed in the runner the same night;
bench-v1 was restarted from scratch. The journals remain honest records of what the
model did with the telemetry it was given, and two scoring findings came from reading
them (incident-class taxonomy ambiguity for injected degradation; a tripwire firing on a
negation) — tracked as issues.
