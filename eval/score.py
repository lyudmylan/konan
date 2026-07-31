#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6", "jsonschema>=4.21"]
# ///
"""konan eval scorer — deterministic scoring of investigation journals against
ground-truth fixtures, rendered as scorecard.md.

Implements eval/README.md's scoring semantics exactly: regex and equality only,
no interpretation. A journal that violates the report contract is a FAILING
REPORT (scored, citation-noncompliant); a broken fixture or an unreadable
journal is a broken harness (refused, exit 2).

Usage:
    uv run eval/score.py --pair <fixture.yaml> <journal.md> [--pair ...] [-o scorecard.md]

Exit codes: 0 = all scenarios passed; 1 = scored, with failures; 2 = input error.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

EVAL_DIR = Path(__file__).resolve().parent
FIXTURE_SCHEMA = EVAL_DIR / "fixture.schema.json"
JOURNAL_SCHEMA = EVAL_DIR.parent / "skills" / "investigate" / "journal.schema.json"
JOURNAL_VERSION = 1


class InputError(Exception):
    """Broken harness input — refuse to score rather than render a lie."""


def load_fixture(path, validator):
    try:
        fx = yaml.safe_load(Path(path).read_text())
    except (OSError, yaml.YAMLError) as e:
        raise InputError(f"fixture {path}: unreadable ({e})")
    errs = list(validator.iter_errors(fx))
    if errs:
        detail = "; ".join(e.message for e in errs[:3])
        raise InputError(f"fixture {path}: schema-invalid ({detail})")
    for entry in fx["expected"]["must_claim"] + fx["expected"]["must_not_claim"]:
        for pat in entry.get("all_of", []) + entry.get("any_of", []):
            try:
                re.compile(pat)
            except re.error as e:
                raise InputError(f"fixture {path}: bad regex {pat!r} ({e})")
    return fx


def load_journal(path):
    """Parse frontmatter into the machine core. Raises InputError only when the
    file cannot be read as a journal at all, or its contract version is unknown
    — the contract says a scorer refuses versions it does not know."""
    try:
        text = Path(path).read_text()
    except OSError as e:
        raise InputError(f"journal {path}: unreadable ({e})")
    if not text.startswith("---\n") or "\n---\n" not in text:
        raise InputError(f"journal {path}: no frontmatter fences")
    try:
        core = yaml.safe_load(text.split("\n---\n", 1)[0][4:])
    except yaml.YAMLError as e:
        raise InputError(f"journal {path}: frontmatter is not YAML ({e})")
    if not isinstance(core, dict):
        raise InputError(f"journal {path}: frontmatter is not a mapping")
    if core.get("konan_journal") != JOURNAL_VERSION:
        raise InputError(
            f"journal {path}: contract version {core.get('konan_journal')!r} "
            f"(this scorer knows only {JOURNAL_VERSION})"
        )
    return core


def referential_violations(core):
    """The scorer's enforcement layer per the report contract: reference
    resolution and consistency that JSON Schema shape-checking cannot see."""
    out = []
    evidence = core.get("evidence") or []
    hypotheses = core.get("hypotheses") or []
    eids = [e.get("id") for e in evidence]
    hids = [h.get("id") for h in hypotheses]
    if len(set(eids)) != len(eids):
        out.append("duplicate evidence ids")
    if len(set(hids)) != len(hids):
        out.append("duplicate hypothesis ids")
    known = set(eids)
    for h in hypotheses:
        for ref in (h.get("evidence_for") or []) + (h.get("evidence_against") or []):
            if ref not in known:
                out.append(f"{h.get('id')} cites unknown {ref}")
    for lf in core.get("latent_findings") or []:
        for ref in lf.get("evidence") or []:
            if ref not in known:
                out.append(f"latent finding cites unknown {ref}")
    rc = core.get("root_cause")
    if rc:
        states = {h.get("id"): h.get("state") for h in hypotheses}
        if rc.get("hypothesis") not in states:
            out.append(f"root_cause names unknown {rc.get('hypothesis')}")
        elif states[rc.get("hypothesis")] != "validated":
            out.append(f"root_cause hypothesis {rc.get('hypothesis')} is not validated")
    inv = core.get("investigation") or {}
    try:
        wall = int(
            (
                datetime.fromisoformat(str(inv.get("concluded")))
                - datetime.fromisoformat(str(inv.get("started")))
            ).total_seconds()
        )
        if wall < 0:
            out.append("concluded precedes started")
        elif (core.get("usage") or {}).get("wall_clock_seconds") != wall:
            out.append(
                f"wall_clock_seconds {(core.get('usage') or {}).get('wall_clock_seconds')} "
                f"!= concluded - started ({wall})"
            )
    except (TypeError, ValueError):
        out.append("timestamps not ISO 8601")
    return out


def claim_surface(core):
    """root_cause.statement + validated hypotheses' statements. Nothing else —
    not prose, not killed hypotheses, not latent findings."""
    parts = []
    rc = core.get("root_cause")
    if rc and rc.get("statement"):
        parts.append(str(rc["statement"]))
    for h in core.get("hypotheses") or []:
        if h.get("state") == "validated" and h.get("statement"):
            parts.append(str(h["statement"]))
    return " ".join(parts)


def score_pair(fixture, core, journal_validator):
    expected = fixture["expected"]
    schema_errors = [
        f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in journal_validator.iter_errors(core)
    ]
    ref_errors = referential_violations(core)
    citations_ok = not schema_errors and not ref_errors

    verdict_got = core.get("verdict")
    verdict_ok = verdict_got == expected["verdict"]

    rc = core.get("root_cause") or {}
    if expected["incident_class"] is None:
        class_ok = None
    else:
        class_ok = rc.get("incident_class") == expected["incident_class"]

    surface = claim_surface(core)
    claim_misses = []
    for entry in expected["must_claim"]:
        if not all(re.search(p, surface) for p in entry["all_of"]):
            claim_misses.append(entry["id"])
    rc_hit = None if not expected["must_claim"] else not claim_misses

    false_attributions = []
    if verdict_got == "root-cause-identified":
        for entry in expected["must_not_claim"]:
            if any(re.search(p, surface) for p in entry["any_of"]):
                false_attributions.append(entry["id"])

    usage = core.get("usage") or {}
    passed = (
        verdict_ok
        and citations_ok
        and rc_hit is not False
        and class_ok is not False
        and not false_attributions
    )
    return {
        "scenario": fixture["scenario"]["id"],
        "model": usage.get("model", "?"),
        "passed": passed,
        "verdict_ok": verdict_ok,
        "verdict_got": verdict_got,
        "verdict_expected": expected["verdict"],
        "class_ok": class_ok,
        "class_got": rc.get("incident_class"),
        "rc_hit": rc_hit,
        "claim_misses": claim_misses,
        "false_attributions": false_attributions,
        "citations_ok": citations_ok,
        "citation_errors": schema_errors + ref_errors,
        "tokens": usage.get("tokens"),
        "wall_clock_seconds": usage.get("wall_clock_seconds"),
    }


def _mark(ok):
    return {True: "✓", False: "✗", None: "—"}[ok]


def render_scorecard(rows):
    passed = sum(r["passed"] for r in rows)
    rc_rows = [r for r in rows if r["rc_hit"] is not None]
    rc_hits = sum(r["rc_hit"] for r in rc_rows)
    false_total = sum(len(r["false_attributions"]) for r in rows)
    cit_ok = sum(r["citations_ok"] for r in rows)
    tokens = [r["tokens"] for r in rows]
    token_sum = sum(t for t in tokens if isinstance(t, int))
    token_gaps = sum(1 for t in tokens if t is None)
    wall_sum = sum(r["wall_clock_seconds"] or 0 for r in rows)
    models = sorted({r["model"] for r in rows})

    lines = [
        "# konan scorecard",
        "",
        f"Generated {datetime.now().astimezone().isoformat(timespec='seconds')} — "
        f"{len(rows)} scenario(s) scored, model(s): {', '.join(models)}.",
        "Deterministic scoring (regex + equality only); semantics: `eval/README.md`.",
        "",
        "## Summary",
        "",
        f"- **Scenarios passed: {passed}/{len(rows)}**",
        f"- Root-cause accuracy: {rc_hits}/{len(rc_rows)} (scenarios expecting a root cause)",
        f"- False attributions: {false_total}",
        f"- Evidence-citation compliance: {cit_ok}/{len(rows)}",
        f"- Tokens: {token_sum if token_sum else '—'}"
        + (f" ({token_gaps} run(s) not captured)" if token_gaps else ""),
        f"- Wall clock: {wall_sum}s total",
        "",
        "## Scenarios",
        "",
        "| Scenario | Model | Verdict | Class | Root cause | False attr | Citations | Tokens | Wall (s) |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        verdict_cell = f"{_mark(r['verdict_ok'])} {r['verdict_got']}" + (
            "" if r["verdict_ok"] else f" (want {r['verdict_expected']})"
        )
        lines.append(
            f"| {r['scenario']} | {r['model']} | {verdict_cell} "
            f"| {_mark(r['class_ok'])} | {_mark(r['rc_hit'])} "
            f"| {len(r['false_attributions'])} | {_mark(r['citations_ok'])} "
            f"| {r['tokens'] if r['tokens'] is not None else '—'} "
            f"| {r['wall_clock_seconds'] if r['wall_clock_seconds'] is not None else '—'} |"
        )
    failing = [r for r in rows if not r["passed"]]
    if failing:
        lines += ["", "## Failure detail", ""]
        for r in failing:
            lines.append(f"### {r['scenario']}")
            lines.append("")
            if not r["verdict_ok"]:
                lines.append(
                    f"- verdict: got `{r['verdict_got']}`, want `{r['verdict_expected']}`"
                )
            if r["class_ok"] is False:
                lines.append(f"- incident class: got `{r['class_got']}`")
            for m in r["claim_misses"]:
                lines.append(f"- must_claim `{m}`: no match in the claim surface")
            for f in r["false_attributions"]:
                lines.append(f"- must_not_claim `{f}`: FIRED — false attribution")
            for c in r["citation_errors"]:
                lines.append(f"- citation: {c}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--pair",
        nargs=2,
        metavar=("FIXTURE", "JOURNAL"),
        action="append",
        required=True,
        help="a fixture and the journal to score against it (repeatable)",
    )
    ap.add_argument("-o", "--output", help="write scorecard.md here (default: stdout)")
    args = ap.parse_args(argv)

    try:
        fixture_validator = Draft202012Validator(json.loads(FIXTURE_SCHEMA.read_text()))
        journal_validator = Draft202012Validator(json.loads(JOURNAL_SCHEMA.read_text()))
        rows = [
            score_pair(load_fixture(f, fixture_validator), load_journal(j), journal_validator)
            for f, j in args.pair
        ]
    except InputError as e:
        print(f"score.py: {e}", file=sys.stderr)
        return 2

    card = render_scorecard(rows)
    if args.output:
        Path(args.output).write_text(card)
        print(f"score.py: wrote {args.output}", file=sys.stderr)
    else:
        print(card, end="")
    return 0 if all(r["passed"] for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
