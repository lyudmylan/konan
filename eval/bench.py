#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6", "jsonschema>=4.21"]
# ///
"""konan benchmark aggregator — turns eval runner output into the tier × model table.

    uv run eval/bench.py --runs eval/runs/<run-id> [eval/runs/<other-run-id> ...] \
        [-o eval/BENCHMARK-results.md] [--json results.json] [--plan plan.json]

Reads every `<run>/<model>/<scenario>-r<n>.md` journal with its `.meta.json` sidecar,
re-scores each (fixture, journal) pair with eval/score.py (deterministic — the same
verdict the runner recorded), and aggregates per tier and model:

  pass rate (passed / runs), root-cause accuracy (hits / runs expecting a root cause),
  false attributions (count), citation compliance, tokens median (whole run, from the
  sidecar's modelUsage — the journal's stamped value), wall-clock median (harness
  duration_ms from the sidecar; the journal's wall clock is the investigator's own),
  API-equivalent cost median, headless permission denials median.

Runs whose sidecar says status != ok (error, no journal) count as failed runs — a
benchmark never drops its failures. The coverage line per model (#76) — planned, completed,
failed, missing — comes from the pre-registered plan of the run (`<run>/plan.json`, written
by eval/run.py, or `--plan`), never from the live fixtures; a missing count above zero is
stated at the head of the table. Tier comes from the scenario id prefix
(`t2-`, `t3-`; everything else is tier 1), see eval/BENCHMARK.md.
"""
import argparse
import json
import statistics as st
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SCEN = REPO / "eval" / "scenarios"


def tier_of(scenario_id):
    return 2 if scenario_id.startswith("t2-") else 3 if scenario_id.startswith("t3-") else 1


def load_fixtures():
    fv = Draft202012Validator(json.loads((REPO / "eval/fixture.schema.json").read_text()))
    out = {}
    for f in sorted(SCEN.glob("*.yaml")):
        fx = score.load_fixture(str(f), fv)
        out[fx["scenario"]["id"]] = fx
    return out


def collect(run_dirs, fixtures, jv):
    """Every (run, model, scenario, rep) → a row; failed runs included."""
    rows = []
    for rd in run_dirs:
        rd = Path(rd)
        for model_dir in sorted(p for p in rd.iterdir() if p.is_dir()):
            for meta_path in sorted(model_dir.glob("*.meta.json")):
                meta = json.loads(meta_path.read_text())
                if meta.get("quota_error"):
                    continue  # a quota stop is not a run (protocol): retried, or resumed later;
                              # it feeds quota_windows via metas/quota-stops.jsonl, never the table
                sid, rep = meta.get("scenario"), meta.get("rep")
                fx = fixtures.get(sid)
                row = {"run": rd.name, "model": meta.get("model", model_dir.name), "scenario": sid,
                       "tier": tier_of(sid or ""), "rep": rep, "status": meta.get("status"),
                       "tokens": meta.get("tokens_total"), "duration_s": (meta.get("duration_ms") or 0) / 1000
                       if meta.get("duration_ms") is not None else None,
                       "cost_usd": meta.get("total_cost_usd"),
                       "denials": len(meta.get("permission_denials") or []),
                       "passed": False, "passed_class_agnostic": False, "rc_hit": None, "false_attr": 0, "citations_ok": False,
                       "verdict_got": None, "verdict_expected": fx["expected"]["verdict"] if fx else None}
                journal = meta_path.with_name(meta_path.name.replace(".meta.json", ".md"))
                if fx and meta.get("status") == "ok" and journal.exists():
                    try:
                        core = score.load_journal(str(journal))
                        r = score.score_pair(fx, core, jv)
                        class_agnostic = (r["verdict_ok"] and r["citations_ok"] and not r["claim_misses"]
                                          and not r["false_attributions"] and (r["rc_hit"] in (True, None)))
                        row.update({"passed": r["passed"], "passed_class_agnostic": bool(class_agnostic),
                                    "rc_hit": r["rc_hit"],
                                    "false_attr": len(r["false_attributions"]),
                                    "citations_ok": r["citations_ok"], "verdict_got": r["verdict_got"]})
                    except score.InputError as e:
                        row["status"] = f"unscorable: {e}"
                elif not fx:
                    row["status"] = f"unknown scenario {sid!r}"
                rows.append(row)
    return rows


PLAN_FILE = "plan.json"


def load_plan(run_dir, explicit=None):
    """The pre-registered plan of a run (#76): `<run>/plan.json` from eval/run.py, or an explicit
    file; never the live eval/scenarios/, so a fixture added later does not turn an old table
    into a short one."""
    path = Path(explicit) if explicit else Path(run_dir) / PLAN_FILE
    if not path.exists():
        sys.exit(f"bench.py: no plan for {Path(run_dir).name}: {path} is missing; eval/run.py writes it "
                 f"at the first invocation of a run id, or give one with --plan")
    plan = json.loads(path.read_text())
    return {"fixtures": sorted(plan["fixtures"]), "repeat": int(plan["repeat"])}


def quota_stopped_pairs(run_dir):
    """Distinct (model, scenario, rep) with a quota stop on record: the file keeps every stop,
    and the backfill of bench-v1 has duplicate lines."""
    pairs = set()
    stops = Path(run_dir) / "quota-stops.jsonl"
    if stops.exists():
        for line in stops.read_text().splitlines():
            try:
                q = json.loads(line)
            except ValueError:
                continue
            pairs.add((q.get("model"), q.get("scenario"), q.get("rep")))
    return pairs


def coverage(rows, plan, run_dir):
    """One record per (run, model): planned, completed, failed, missing; of the missing pairs, how
    many stopped by quota and were not resumed, and how many were never scheduled. Rows outside
    the plan are counted apart. A quota stop is not a row: collect drops it."""
    run_dir = Path(run_dir)
    expected = {(sid, r) for sid in plan["fixtures"] for r in range(1, plan["repeat"] + 1)}
    stopped = quota_stopped_pairs(run_dir)
    by_model = {}
    for row in rows:
        if row["run"] == run_dir.name:
            by_model.setdefault(row["model"], []).append(row)
    out = []
    for model, rs in sorted(by_model.items()):
        present = {(r["scenario"], r["rep"]) for r in rs}
        missing = sorted(expected - present)
        quota = [p for p in missing if (model, p[0], p[1]) in stopped]
        out.append({"run": run_dir.name, "model": model, "planned": len(expected),
                    "completed": sum(1 for r in rs if r["status"] == "ok"),
                    "failed": sum(1 for r in rs if r["status"] != "ok"),
                    "missing": len(missing), "quota_stopped": len(quota),
                    "never_scheduled": len(missing) - len(quota),
                    "outside_plan": len(present - expected)})
    return out


def render_coverage(cov):
    """The head line of the table and the section "Coverage". `missing <n>` appears on the
    per-model lines only, so a reader (or a grep) finds one per model."""
    planned = sum(c["planned"] for c in cov)
    missing = sum(c["missing"] for c in cov)
    if missing:
        short = ", ".join(f"{c['model']}: {c['missing']}" for c in cov if c["missing"])
        head = (f"**Incomplete: {missing} of {planned} planned runs are missing** ({short}). "
                f"Not published as complete.")
    else:
        head = f"Coverage: complete, {planned} of {planned} planned runs."
    lines = ["## Coverage", "",
             "Planned = the pre-registered plan of the run (`plan.json`: fixtures × repetitions); "
             "a quota stop is not a run.", ""]
    for c in cov:
        line = (f"- {c['run']} {c['model']}: planned {c['planned']}, completed {c['completed']}, "
                f"failed {c['failed']}, missing {c['missing']}")
        if c["missing"]:
            line += (f" ({c['quota_stopped']} stopped by quota and not resumed, "
                     f"{c['never_scheduled']} never scheduled)")
        if c["outside_plan"]:
            line += f"; {c['outside_plan']} outside the plan"
        lines.append(line)
    return head, lines


def quota_windows(run_dirs):
    """Per model: how many investigations completed between consecutive quota stops —
    a proxy for 'investigations per 5-hour window' on the subscription (exact only when
    the batch starts near an empty window and nothing else uses the pool)."""
    events = {}
    for rd in run_dirs:
        for meta_path in Path(rd).glob("*/*.meta.json"):
            m = json.loads(meta_path.read_text())
            events.setdefault(m.get("model", "?"), []).append(
                (m.get("started_at") or "", bool(m.get("quota_error")), m.get("status")))
        stops = Path(rd) / "quota-stops.jsonl"          # retries overwrite sidecars; stops are kept here
        if stops.exists():
            for line in stops.read_text().splitlines():
                try:
                    q = json.loads(line)
                except ValueError:
                    continue
                events.setdefault(q.get("model", "?"), []).append((q.get("at") or "", True, "error"))
    out = {}
    for model, evs in events.items():
        evs.sort()
        segments, count = [], 0
        for _, quota, status in evs:
            if quota:
                segments.append(count)
                count = 0
            elif status in ("ok", "no-journal", "timeout", "error"):
                count += 1
        out[model] = {"segments": segments, "open_segment": count}
    return out


def _med(vals):
    vals = [v for v in vals if isinstance(v, (int, float))]
    return st.median(vals) if vals else None


def aggregate(rows):
    """Group by (tier, model) and by (model) overall."""
    groups = {}
    for r in rows:
        for key in ((r["tier"], r["model"]), ("all", r["model"])):
            g = groups.setdefault(key, [])
            g.append(r)
    table = []
    for (tier, model), rs in sorted(groups.items(), key=lambda kv: (str(kv[0][0]), kv[0][1])):
        n = len(rs)
        rc_rows = [r for r in rs if r["rc_hit"] is not None]
        table.append({
            "tier": tier, "model": model, "runs": n,
            "failed_runs": sum(1 for r in rs if r["status"] != "ok"),
            "pass_rate": sum(r["passed"] for r in rs) / n if n else None,
            "pass_rate_class_agnostic": sum(r["passed_class_agnostic"] for r in rs) / n if n else None,
            "rc_accuracy": (sum(r["rc_hit"] for r in rc_rows) / len(rc_rows)) if rc_rows else None,
            "false_attributions": sum(r["false_attr"] for r in rs),
            "citation_rate": sum(r["citations_ok"] for r in rs) / n if n else None,
            "tokens_median": _med([r["tokens"] for r in rs if r["status"] == "ok"]),
            "duration_median_s": _med([r["duration_s"] for r in rs if r["status"] == "ok"]),
            "cost_median_usd": _med([r["cost_usd"] for r in rs if r["status"] == "ok"]),
            "denials_median": _med([r["denials"] for r in rs if r["status"] == "ok"]),
        })
    return table


def _pct(v):
    return "—" if v is None else f"{100 * v:.0f}%"


def _num(v, fmt="{:.0f}"):
    return "—" if v is None else fmt.format(v)


def render(rows, table, run_names, cov=None):
    head, cov_lines = render_coverage(cov) if cov is not None else (None, [])
    out = ["# konan benchmark — results", ""]
    if head:
        out += [head, ""]
    out += [f"Runs: {', '.join(run_names)}. {len(rows)} investigations. Protocol and limits: `eval/BENCHMARK.md`.",
            "Deterministic scoring (eval/score.py); tokens = whole run incl. subagents; duration = harness wall clock.",
            "Pass rate is the pre-registered metric; the class-agnostic column ignores only the incident-class label (taxonomy issue tracked separately).",
            "Medians cover completed investigations (status ok); failed runs count in Runs/Failed and their consumption stays in the sidecars.", ""]
    if cov_lines:
        out += cov_lines + [""]
    out += ["## Per tier × model", "",
           "| Tier | Model | Runs | Failed | Pass rate | Pass (class-agnostic) | Root-cause acc. | False attr. | Citations | Tokens (median) | Wall s (median) | Cost $ (median) | Denials (median) |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for t in table:
        out.append(f"| {t['tier']} | {t['model']} | {t['runs']} | {t['failed_runs']} | {_pct(t['pass_rate'])} | "
                   f"{_pct(t['pass_rate_class_agnostic'])} | {_pct(t['rc_accuracy'])} | {t['false_attributions']} | {_pct(t['citation_rate'])} | "
                   f"{_num(t['tokens_median'])} | {_num(t['duration_median_s'])} | "
                   f"{_num(t['cost_median_usd'], '{:.2f}')} | {_num(t['denials_median'], '{:.1f}')} |")
    qw = quota_windows(RUN_DIRS)
    out += ["", "## Quota: investigations completed between quota stops (per model)", "",
            "A proxy for investigations per 5-hour window on the subscription; exact only when a batch starts "
            "near an empty window with nothing else on the pool. Segments = runs before each stop; the last "
            "number is the open segment.", ""]
    for model, q in sorted(qw.items()):
        out.append(f"- {model}: {q['segments'] or '—'} + open {q['open_segment']}")
    out += ["", "## Every run", "",
            "| Run | Model | Scenario | Tier | Rep | Status | Verdict | Expected | Passed | RC | False attr | Citations | Tokens | Wall s | Cost $ | Denials |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in sorted(rows, key=lambda r: (r["tier"], r["scenario"] or "", r["model"], r["rep"] or 0)):
        out.append(f"| {r['run']} | {r['model']} | {r['scenario']} | {r['tier']} | {r['rep']} | {r['status']} | "
                   f"{r['verdict_got'] or '—'} | {r['verdict_expected'] or '—'} | {'✓' if r['passed'] else '✗'} | "
                   f"{'—' if r['rc_hit'] is None else ('✓' if r['rc_hit'] else '✗')} | {r['false_attr']} | "
                   f"{'✓' if r['citations_ok'] else '✗'} | {_num(r['tokens'])} | {_num(r['duration_s'])} | "
                   f"{_num(r['cost_usd'], '{:.2f}')} | {r['denials']} |")
    return "\n".join(out) + "\n"


RUN_DIRS = []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", nargs="+", required=True, help="eval/runs/<run-id> directories")
    ap.add_argument("-o", "--output", help="write the markdown table here (default: stdout)")
    ap.add_argument("--json", help="also write rows + table as JSON here")
    ap.add_argument("--plan", help="the pre-registered plan, for every run directory given (default: <run>/plan.json)")
    a = ap.parse_args()
    RUN_DIRS.extend(a.runs)
    fixtures = load_fixtures()
    jv = Draft202012Validator(json.loads((REPO / "skills/investigate/journal.schema.json").read_text()))
    rows = collect(a.runs, fixtures, jv)
    table = aggregate(rows)
    cov = []
    for rd in a.runs:
        cov += coverage(rows, load_plan(rd, a.plan), rd)
    md = render(rows, table, [Path(r).name for r in a.runs], cov)
    if a.output:
        Path(a.output).write_text(md)
        print(f"bench.py: wrote {a.output} ({len(rows)} runs)")
    else:
        sys.stdout.write(md)
    if a.json:
        Path(a.json).write_text(json.dumps({"rows": rows, "table": table, "coverage": cov}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
