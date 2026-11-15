#!/usr/bin/env -S uv run --quiet
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6", "jsonschema>=4.21"]
# ///
"""Semantics pins for the eval scorer. Plain asserts: `uv run eval/tests.py`.

Each test pins one rule from eval/README.md or the report contract's scorer
layer, so a future edit that drifts the semantics fails loudly here."""
import copy
import json
import re
import tempfile
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

import bench
import run as runner
import score

EVAL = Path(__file__).resolve().parent
JV = Draft202012Validator(json.loads((EVAL.parent / "skills/investigate/journal.schema.json").read_text()))
FV = Draft202012Validator(json.loads((EVAL / "fixture.schema.json").read_text()))


def base_core(verdict="root-cause-identified"):
    core = {
        "konan_journal": 1,
        "investigation": {
            "id": "2026-07-31-test",
            "trigger": "manual",
            "complaint": "things are broken",
            "started": "2026-07-31T10:00:00+03:00",
            "concluded": "2026-07-31T10:10:00+03:00",
        },
        "target": {"name": "faultline", "surface_contract": "docs/lab.md"},
        "verdict": verdict,
        "hypotheses": [
            {
                "id": "H1",
                "statement": "the widget frobnicator divides by zero on row 3",
                "incident_class": "software-defect",
                "state": "validated",
                "evidence_for": ["E1"],
                "evidence_against": [],
            }
        ],
        "evidence": [{"id": "E1", "type": "log", "source": "lab/logs/app.log @ T", "quote": "boom"}],
        "gaps": [],
        "usage": {"model": "test-model", "tokens": 1000, "wall_clock_seconds": 600},
    }
    if verdict == "root-cause-identified":
        core["root_cause"] = {
            "hypothesis": "H1",
            "statement": "the widget frobnicator divides by zero on row 3",
            "incident_class": "software-defect",
        }
    else:
        core["hypotheses"][0]["state"] = "invalidated"
    return core


def base_core_v2(verdict="root-cause-identified"):
    """The base journal under contract v2: the root cause names its cause (#78)."""
    core = base_core(verdict)
    core["konan_journal"] = 2
    if verdict == "root-cause-identified":
        core["root_cause"]["cause"] = "unhandled-exception"
    return core


def base_fx(verdict="root-cause-identified"):
    return {
        "konan_fixture": 2,
        "scenario": {"id": "test-scenario", "title": "t"},
        "setup": {"lab": "fresh", "stage": ["scripts/scenario.sh get /x"]},
        "complaint": "things are broken",
        "expected": {
            "verdict": verdict,
            "incident_class": "software-defect" if verdict == "root-cause-identified" else None,
            "cause": "unhandled-exception" if verdict == "root-cause-identified" else None,
            "must_claim": (
                [{"id": "mech", "all_of": ["(?i)divides?\\s+by\\s+zero"]}]
                if verdict == "root-cause-identified"
                else []
            ),
            "must_not_claim": [{"id": "not-chaos", "any_of": ["(?i)chaos"]}],
        },
    }


def check_valid(core, fx):
    assert not list(JV.iter_errors(core)), list(JV.iter_errors(core))[0].message
    assert not list(FV.iter_errors(fx)), list(FV.iter_errors(fx))[0].message


def run():
    # 0. The synthetic base pair is contract-valid and passes.
    core, fx = base_core(), base_fx()
    check_valid(core, fx)
    r = score.score_pair(fx, core, JV)
    assert r["passed"] and r["rc_hit"] and r["citations_ok"], r

    # 1. Claim surface excludes invalidated hypotheses and latent findings:
    #    tripwire vocabulary there must NOT fire.
    core = base_core()
    core["hypotheses"].append(
        {"id": "H2", "statement": "chaos mode caused it", "incident_class": "infra-process",
         "state": "invalidated", "evidence_for": [], "evidence_against": ["E1"]}
    )
    core["latent_findings"] = [{"statement": "latent chaos-adjacent oddity", "evidence": ["E1"]}]
    check_valid(core, base_fx())
    r = score.score_pair(base_fx(), core, JV)
    assert r["passed"] and not r["false_attributions"], r

    # 2. Tripwire vocabulary in the ROOT CAUSE fires a false attribution.
    core = base_core()
    core["root_cause"]["statement"] = "chaos mode divides by zero on row 3"
    r = score.score_pair(base_fx(), core, JV)
    assert not r["passed"] and r["false_attributions"] == ["not-chaos"], r

    # 3. must_not_claim is gated on a root-cause-identified verdict: a correct
    #    no-active-incident journal may mention checked-for vocabulary.
    core, fx = base_core("no-active-incident"), base_fx("no-active-incident")
    core["hypotheses"][0] = {
        "id": "H1", "statement": "no chaos, no defect: checks performed and clean",
        "incident_class": "infra-process", "state": "validated",
        "evidence_for": ["E1"], "evidence_against": [],
    }
    check_valid(core, fx)
    r = score.score_pair(fx, core, JV)
    assert r["passed"] and not r["false_attributions"] and r["rc_hit"] is None, r

    # 4. Promoting a phantom cause on the healthy scenario: verdict miss AND tripwire.
    r = score.score_pair(base_fx("no-active-incident"),
                         dict(base_core(), root_cause={"hypothesis": "H1",
                              "statement": "chaos did it", "incident_class": "infra-process"}), JV)
    assert not r["passed"] and not r["verdict_ok"] and r["false_attributions"], r

    # 5. Partial must_claim: every entry must match; the miss is named.
    fx = base_fx()
    fx["expected"]["must_claim"].append({"id": "data", "all_of": ["(?i)row\\s+3", "(?i)unmatchable-xyzzy"]})
    r = score.score_pair(fx, base_core(), JV)
    assert not r["passed"] and r["rc_hit"] is False and r["claim_misses"] == ["data"], r

    # 6. Referential layer: dangling evidence ref is a citation failure.
    core = base_core()
    core["hypotheses"][0]["evidence_for"] = ["E9"]
    r = score.score_pair(base_fx(), core, JV)
    assert not r["citations_ok"] and any("E9" in e for e in r["citation_errors"]), r

    # 7. Referential layer: root_cause must name a VALIDATED hypothesis.
    core = base_core()
    core["hypotheses"][0]["state"] = "inconclusive"
    r = score.score_pair(base_fx(), core, JV)
    assert not r["citations_ok"] and any("not validated" in e for e in r["citation_errors"]), r

    # 8. Referential layer: wall clock must equal concluded - started.
    core = base_core()
    core["usage"]["wall_clock_seconds"] = 601
    r = score.score_pair(base_fx(), core, JV)
    assert not r["citations_ok"] and any("wall_clock" in e for e in r["citation_errors"]), r

    # 9. A schema-invalid journal is a FAILING REPORT, not an input error.
    core = base_core()
    core["evidence"][0]["quote"] = ""
    r = score.score_pair(base_fx(), core, JV)
    assert not r["citations_ok"] and not r["passed"], r

    # 10. Unknown journal contract version is REFUSED (input error).
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write("---\nkonan_journal: 99\n---\nbody\n")
    try:
        score.load_journal(f.name)
        raise AssertionError("version 99 was not refused")
    except score.InputError:
        pass

    # 11. Integration: the committed sample journal passes the committed D1 fixture.
    fx = score.load_fixture(EVAL / "scenarios/d1-zero-stock-product-page.yaml", FV)
    core = score.load_journal(EVAL.parent / "journals/2026-07-30-products-3-500s.md")
    r = score.score_pair(fx, core, JV)
    assert r["passed"], r

    # 12. Integration: the D1 journal does NOT pass the chaos fixture (discrimination).
    fx = score.load_fixture(EVAL / "scenarios/chaos-error-rate.yaml", FV)
    r = score.score_pair(fx, core, JV)
    assert not r["passed"], r

    # 14. Unquoted RFC3339 stamps in the frontmatter stay strings (the contract's own
    #     example writes them unquoted; a model that follows it must not fail citation
    #     compliance on a YAML parsing accident).
    import tempfile
    core = base_core()
    text = "---\n" + yaml.safe_dump(core, sort_keys=False).replace(
        "started: '2026-07-31T10:00:00+03:00'", "started: 2026-07-31T10:00:00+03:00").replace(
        "concluded: '2026-07-31T10:10:00+03:00'", "concluded: 2026-07-31T10:10:00+03:00") + "---\n\nbody\n"
    assert "started: 2026-07-31T10:00:00+03:00\n" in text, text[:400]   # the pin exercises the unquoted form
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
    loaded = score.load_journal(f.name)
    assert isinstance(loaded["investigation"]["started"], str)
    check_valid(loaded, base_fx())
    assert score.score_pair(base_fx(), loaded, JV)["citations_ok"]

    # 15. A fixture may accept a SET of incident classes (taxonomy ambiguity, #63):
    #     any member passes, a non-member still fails, and the plain-string form is
    #     unchanged.
    core, fx = base_core(), base_fx()
    fx["expected"]["incident_class"] = ["software-defect", "infra-process"]
    check_valid(core, fx)
    assert score.score_pair(fx, core, JV)["class_ok"]
    core["root_cause"]["incident_class"] = "infra-process"
    core["hypotheses"][0]["incident_class"] = "infra-process"
    assert score.score_pair(fx, core, JV)["class_ok"]
    core["root_cause"]["incident_class"] = "interfaces"
    core["hypotheses"][0]["incident_class"] = "interfaces"
    r = score.score_pair(fx, core, JV)
    assert r["class_ok"] is False and not r["passed"]

    # 16. Every committed fixture loads and every matcher compiles. load_fixture is the
    #     only place a bad regex surfaces, and until now the pins reached just two
    #     fixtures — so a variable-width lookbehind or a stray bracket in any of the
    #     others passed CI green and raised re.error mid-benchmark, after paid model runs.
    scenarios = sorted((EVAL / "scenarios").glob("*.yaml"))
    assert len(scenarios) >= 10, f"expected the committed corpus, found {len(scenarios)}"
    for path in scenarios:
        score.load_fixture(path, FV)   # validates against the schema and compiles matchers

    # 17. Singular class. The chaos-switch fixtures state ONE class, infra-process (#77). The set of #63 was a
    #     transition for the bench-v1 journals; a live set would score a model that ignores the
    #     lens definitions the same as one that follows them. A committed bench-v1 journal that
    #     answered `interfaces` fails on class against the live fixture.
    for sid in ("chaos-error-rate", "chaos-latency", "t2-red-herring-latency-latent-d1",
                "t3-chaos-low-rate-intermittent"):
        fx = score.load_fixture(EVAL / "scenarios" / f"{sid}.yaml", FV)
        assert fx["expected"]["incident_class"] == "infra-process", sid
    fx = score.load_fixture(EVAL / "scenarios" / "chaos-error-rate.yaml", FV)
    j = score.load_journal(str(EVAL / "runs/bench-v1/claude-opus-5/chaos-error-rate-r1.md"))
    assert j["root_cause"]["incident_class"] == "interfaces"   # the journal is what it was
    r = score.score_pair(fx, j, JV)
    assert r["class_ok"] is False and not r["passed"]

    # 18. Tier-3 calibration (#75). The matchers of the two tier-3 fixtures were first-cut; they are
    #     calibrated on their committed bench-v1 journals and pinned here, so the alternations are read
    #     once, not re-guessed. Checks 1 and 2 of intents/crash-matcher.md. The pin reads claim_misses,
    #     not passed: the class of these journals is the matter of #77.
    runs = EVAL / "runs/bench-v1"
    fx = score.load_fixture(EVAL / "scenarios" / "t3-crash-hard-down.yaml", FV)
    crash = sorted(runs.glob("*/t3-crash-hard-down-r*.md"))
    assert len(crash) == 9, len(crash)
    identified = 0
    for path in crash:
        j = score.load_journal(str(path))
        if j["verdict"] != "root-cause-identified":
            continue
        identified += 1
        assert score.score_pair(fx, j, JV)["claim_misses"] == [], path.name
    assert identified == 8, identified   # one Sonnet run stayed inconclusive
    core = base_core()
    core["root_cause"]["statement"] = ("The process crashed with exit code 1 and the supervisor restarted "
                                       "it within two seconds; the operator cannot restart it by hand.")
    core["hypotheses"][0]["statement"] = core["root_cause"]["statement"]
    assert score.score_pair(fx, core, JV)["claim_misses"] == ["no-restart-after"]
    fx = score.load_fixture(EVAL / "scenarios" / "t3-chaos-low-rate-intermittent.yaml", FV)
    stated = {   # the judgment of the leader, made once in the change request of #75
        "claude-fable-5/t3-chaos-low-rate-intermittent-r1.md": [],
        "claude-fable-5/t3-chaos-low-rate-intermittent-r2.md": [],
        "claude-fable-5/t3-chaos-low-rate-intermittent-r3.md": [],
        "claude-opus-5/t3-chaos-low-rate-intermittent-r1.md": [],
        "claude-opus-5/t3-chaos-low-rate-intermittent-r2.md": ["rare-but-real"],   # sizes nothing
        "claude-opus-5/t3-chaos-low-rate-intermittent-r3.md": [],
        "claude-sonnet-5/t3-chaos-low-rate-intermittent-r2.md": [],
        "claude-sonnet-5/t3-chaos-low-rate-intermittent-r3.md": [],
    }
    found = sorted(p.relative_to(runs).as_posix()
                   for p in runs.glob("*/t3-chaos-low-rate-intermittent-r*.md"))
    assert found == sorted(stated), found   # eight committed journals; one Sonnet run left none
    for rel, misses in stated.items():
        assert score.score_pair(fx, score.load_journal(str(runs / rel)), JV)["claim_misses"] == misses, rel

    # 19. Cause equality, denial in prose (check 1 of intents/cause-field.md). A version 2 journal whose
    #     cause equals the expected cause scores no false attribution whatever its prose says; the same
    #     statement in a version 1 journal fires the tripwire — the artifact the field removes (#78).
    denial = ("the widget frobnicator divides by zero on row 3; chaos is not the cause, and this is "
              "not a chaos toggle")
    core, fx = base_core_v2(), base_fx()
    core["root_cause"]["statement"] = denial
    core["hypotheses"][0]["statement"] = denial
    check_valid(core, fx)
    r = score.score_pair(fx, core, JV)
    assert r["passed"] and r["false_attributions"] == [] and r["cause_got"] == "unhandled-exception", r
    core = base_core()
    core["root_cause"]["statement"] = denial
    core["hypotheses"][0]["statement"] = denial
    assert score.score_pair(fx, core, JV)["false_attributions"] == ["not-chaos"]

    # 20. Cause inequality (check 2): one false attribution, named by the two ids; the class and the
    #     must_claim entries still pass, so the cause is the one thing that failed. A version 2
    #     root-cause journal on a fixture that expects no root cause is a verdict miss and one false
    #     attribution, as the prose tripwires were under version 1 (pin 4).
    core, fx = base_core_v2(), base_fx()
    fx["expected"]["cause"] = "wrong-result"
    check_valid(core, fx)
    r = score.score_pair(fx, core, JV)
    assert not r["passed"] and r["false_attributions"] == ["cause:unhandled-exception"], r
    assert r["cause_expected"] == "wrong-result" and r["class_ok"] and r["rc_hit"], r
    assert "- cause: got `unhandled-exception`, want `wrong-result` — false attribution" in score.render_scorecard([r])
    r = score.score_pair(base_fx("no-active-incident"), base_core_v2(), JV)
    assert not r["verdict_ok"] and r["false_attributions"] == ["cause:unhandled-exception"], r
    r = score.score_pair(score.load_fixture(EVAL / "scenarios/healthy-baseline.yaml", FV), base_core_v2(), JV)
    assert not r["verdict_ok"] and r["false_attributions"] == ["cause:unhandled-exception"], r

    # 21. Fixture cause ids (check 4): every live fixture states a cause of the list, or null exactly
    #     when its verdict is not root-cause-identified; a fixture with an id outside the list is refused
    #     as broken input; a root-cause fixture with the cause null is schema-invalid, refused the same.
    assert len(score.CAUSE_IDS) == 28, len(score.CAUSE_IDS)
    for path in scenarios:
        exp = score.load_fixture(path, FV)["expected"]
        if exp["verdict"] == "root-cause-identified":
            assert exp["cause"] in score.CAUSE_IDS, path.name
        else:
            assert exp["cause"] is None, path.name
    # One list, four copies: the contract table under "Causes, defined", $defs.cause, the six class
    # pairs of the schema, and the plan. The table and the schema are held to each other here.
    contract = (EVAL.parent / "skills/investigate/report-contract.md").read_text()
    section = contract.split("### Causes, defined", 1)[1].split("\n## ", 1)[0]
    table = {cid: cls for cls, cid in re.findall(r"^\| ([a-z-]+) \| `([a-z-]+)` \|", section, re.M)}
    assert set(table) == score.CAUSE_IDS, set(table) ^ score.CAUSE_IDS
    schema = json.loads((EVAL.parent / "skills/investigate/journal.schema.json").read_text())
    pairs = {}
    for rule in schema["properties"]["root_cause"]["allOf"]:
        cls = rule["then"]["properties"]["incident_class"]["const"]
        for cid in rule["if"]["properties"]["cause"]["enum"]:
            assert cid not in pairs, cid   # one class per id
            pairs[cid] = cls
    assert pairs == table, {k: (pairs.get(k), table.get(k)) for k in pairs.keys() | table.keys()
                            if pairs.get(k) != table.get(k)}
    for bad in ("made-up", None):
        fx = base_fx()
        fx["expected"]["cause"] = bad
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            yaml.safe_dump(fx, f)
        try:
            score.load_fixture(f.name, FV)
            raise AssertionError(f"cause {bad!r} was not refused")
        except score.InputError as e:
            assert bad is None or "made-up" in str(e), e

    # 22. Journal cause id (check 5): a version 2 journal with a cause outside the list, or in another
    #     class than its incident_class, or without the field, fails citation compliance — a failing
    #     report, no InputError. A version 1 journal with the field fails the same way.
    for cause in ("made-up", "process-crashed"):
        core = base_core_v2()
        core["root_cause"]["cause"] = cause
        r = score.score_pair(base_fx(), core, JV)
        assert not r["citations_ok"] and not r["passed"], (cause, r)
        assert any(e.startswith("root_cause") for e in r["citation_errors"]), r["citation_errors"]
    core = base_core_v2()
    del core["root_cause"]["cause"]
    assert not score.score_pair(base_fx(), core, JV)["citations_ok"]
    core = base_core()
    core["root_cause"]["cause"] = "unhandled-exception"
    assert not score.score_pair(base_fx(), core, JV)["citations_ok"]

    # 23. Versions (check 3): the committed sample journal, version 1, still passes the D1 fixture now
    #     that the fixture states a cause; a version 2 journal loads and passes; version 3 is refused
    #     like 99 (pin 10).
    fx = score.load_fixture(EVAL / "scenarios/d1-zero-stock-product-page.yaml", FV)
    assert fx["expected"]["cause"] == "unhandled-exception"
    core = score.load_journal(EVAL.parent / "journals/2026-07-30-products-3-500s.md")
    assert core["konan_journal"] == 1 and score.score_pair(fx, core, JV)["passed"]
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write("---\n" + yaml.safe_dump(base_core_v2(), sort_keys=False) + "---\n\nbody\n")
    loaded = score.load_journal(f.name)
    assert loaded["konan_journal"] == 2 and score.score_pair(base_fx(), loaded, JV)["passed"]
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write("---\nkonan_journal: 3\n---\nbody\n")
    try:
        score.load_journal(f.name)
        raise AssertionError("version 3 was not refused")
    except score.InputError:
        pass

    # 24. Matcher widening (#90). Six matchers gained the wordings of the false-fail table of bench-v2
    #     (eval/BENCHMARK.md, the results section). Checks 1 to 3 of intents/matcher-widening.md. The pin
    #     holds the old patterns as literals, so that it reads the widening itself and not a scorecard.
    widened_old = {
        ("chaos-error-rate", "switch-flipped"): "(?i)enab",
        ("chaos-latency", "switch-flipped"): "(?i)enab",
        ("t2-red-herring-latency-latent-d1", "switch-flipped"): "(?i)enab",
        ("t3-chaos-low-rate-intermittent", "switch-flipped"): "(?i)enab",
        ("chaos-error-rate", "spread"): "(?i)intermittent|across|multiple",
        ("d1-zero-stock-product-page", "data-condition"):
            r"(?i)units_in_stock\s*=?\s*0|zero[\s-]stock|stock\s+(is\s+)?0\b",
        ("d1-zero-stock-product-page", "location"): r"(?i)/products/3|product\s*3\b",
        ("t3-chaos-low-rate-intermittent", "rare-but-real"):
            r"(?i)intermittent|occasional|rare|low[\s-]rate|\b(a|small|random)\s+fraction|a\s+few|sporadic"
            r"|probabilist|(?<![\d.])\d\s*%",
    }
    no_restart_added = r"|nothing\s+started\s+it\s+again|no\s+process\s+listening"
    live = {p.stem: score.load_fixture(p, FV) for p in scenarios}

    def matcher(sid, mid):
        return next(e for e in live[sid]["expected"]["must_claim"] if e["id"] == mid)

    crash_now = matcher("t3-crash-hard-down", "no-restart-after")["all_of"][0]
    assert crash_now.endswith(no_restart_added), "the two added forms close the pattern"
    widened_old[("t3-crash-hard-down", "no-restart-after")] = crash_now[: -len(no_restart_added)]
    before = copy.deepcopy(live)
    for (sid, mid), pattern in widened_old.items():
        entry = next(e for e in before[sid]["expected"]["must_claim"] if e["id"] == mid)
        assert entry["all_of"] != [pattern], (sid, mid)   # the live matcher is the widened one
        entry["all_of"] = [pattern]

    # Check 1: the 13 rows of the table that read "No" pass the matcher they failed.
    rows = [
        "claude-fable-5/chaos-error-rate-r1.md", "claude-fable-5/chaos-error-rate-r2.md",
        "claude-fable-5/chaos-error-rate-r3.md", "claude-opus-5/chaos-error-rate-r1.md",
        "claude-opus-5/chaos-error-rate-r2.md", "claude-opus-5/d1-zero-stock-product-page-r1.md",
        "claude-opus-5/d1-zero-stock-product-page-r2.md", "claude-opus-5/t3-chaos-low-rate-intermittent-r1.md",
        "claude-opus-5/t3-chaos-low-rate-intermittent-r3.md", "claude-opus-5/t3-crash-hard-down-r1.md",
        "claude-sonnet-5/chaos-error-rate-r1.md", "claude-sonnet-5/d1-zero-stock-product-page-r3.md",
        "claude-sonnet-5/t3-crash-hard-down-r3.md",
    ]
    refused = "claude-opus-5/t2-healthy-after-chaos-window-r1.md"   # the scorer refuses this journal (#92)
    v2 = EVAL / "runs/bench-v2"
    newly, seen = [], 0
    for path in sorted(v2.glob("*/*.md")):
        rel = path.relative_to(v2).as_posix()
        if rel == refused:
            continue
        seen += 1
        sid = re.sub(r"-r\d+$", "", path.stem)
        j = score.load_journal(str(path))
        old, new = score.score_pair(before[sid], j, JV), score.score_pair(live[sid], j, JV)
        # Check 2: no pass is lost, and the runs that newly pass are the runs of the 13 rows.
        assert new["passed"] or not old["passed"], rel
        if new["passed"] and not old["passed"]:
            newly.append(rel)
        if rel in rows:
            assert old["claim_misses"] and new["claim_misses"] == [], (rel, old["claim_misses"], new["claim_misses"])
    assert seen == 89 and sorted(newly) == sorted(rows), (seen, sorted(set(newly) ^ set(rows)))

    def hits(sid, mid, text):
        return all(re.search(p, text) for p in matcher(sid, mid)["all_of"])

    # Check 3, the vacuous forms: a statement that carries only what every statement carries (a switch
    # that is on, a timestamp, "requests", a product number, a rate) matches no widened matcher.
    flat = ("At 2026-11-02T15:39:37.256Z the switch is on and the requests fail with HTTP 503; "
            "the toggle carries failure_rate 0.08 and every observed non-2xx response is attributed to it.")
    for sid, mid in widened_old:
        if mid in ("switch-flipped", "spread", "rare-but-real"):
            assert not hits(sid, mid, flat), (sid, mid)
    other = "Products 30 and 31 return 500; product id 31 has units_in_stock 10 and a price of 0."
    assert not hits("d1-zero-stock-product-page", "location", other)
    assert not hits("d1-zero-stock-product-page", "data-condition", other)
    back = "The process crashed, the supervisor started it again, and a process is listening on the port."
    assert not hits("t3-crash-hard-down", "no-restart-after", back)

    # Check 3, the wording of the round of 2026-11-15: the statements of the comment on #90, as literals.
    said = {
        "chaos-error-rate": [
            ("The chaos switch inside the service was turned on at 2026-11-15T12:19:08.145Z with failure_rate "
             "0.4 and error_status 503; while it is on, the service injects 503 responses at random into "
             "business requests (product pages, order list, order creation)", ["switch-flipped", "spread"]),
            ("An operational switch inside the target (chaos mode) was turned on at 2026-11-15T12:25:36.289Z "
             "with failure_rate 0.4 and error_status 503; while it is on, the target answers a random share "
             "of business requests with an injected 503", ["switch-flipped"]),
            ("The chaos switch inside the target was turned on at 2026-11-15T12:33:04.517Z with failure_rate "
             "0.4 and error_status 503, and while it is on it injects HTTP 503 into a random fraction of "
             "requests, observed on POST /orders and GET /products/5", ["switch-flipped", "spread"]),
        ],
        "chaos-latency": [
            ("The chaos switch inside the target was turned on at 12:39:26.668Z with failure_rate 0.0 and "
             "extra_latency_ms 1500; while it is on, every business route answers 2xx with an added delay",
             ["switch-flipped"]),
            ("The chaos switch inside the target was turned on at 2026-11-15T12:45:37.802Z with "
             "extra_latency_ms 1500 and failure_rate 0.0; while it is on, every business request (products, "
             "orders) gets an added delay", ["switch-flipped"]),
            ("The service's internal chaos switch was turned on at 12:52:09.653Z with extra_latency_ms 1500 "
             "and failure_rate 0.0", ["switch-flipped"]),
        ],
        "t2-red-herring-latency-latent-d1": [
            ("The chaos switch inside the target was turned on at 2026-11-15T14:43:31.413Z with extra latency "
             "of up to 1500 ms and a failure rate of 0; while it is on, it delays every request on the shop "
             "routes and leaves /health fast", ["switch-flipped"]),
            ("An operational switch inside the target (chaos mode) was turned on at 2026-11-15T14:52:02.479Z "
             "with extra_latency_ms 1500 and failure_rate 0.0; while it is on, it adds a variable delay of up "
             "to about 1500 ms to every business request", ["switch-flipped"]),
            ("The chaos switch inside the target was turned on at 2026-11-15T14:58:19.701Z with "
             "extra_latency_ms 1500 and failure_rate 0.0; while on, it adds a variable delay of up to about "
             "1.5 s to every shop route and leaves /health fast", ["switch-flipped"]),
        ],
        "t3-chaos-low-rate-intermittent": [
            ("An operational chaos switch inside the target was turned on at 2026-11-15T15:04:45.224Z with "
             "failure_rate 0.08 and error_status 503; while it is on, the target injects 503 responses on a "
             "fraction of requests independent of input", ["switch-flipped", "rare-but-real"]),
            ("An operational switch inside the target (chaos mode) was turned on at 2026-11-15T15:10:23.881Z "
             "with failure_rate 0.08 and error_status 503; while on, it injects HTTP 503 into a random share "
             "of requests (observed on three GET routes)", ["switch-flipped", "rare-but-real"]),
            ("An operational error-injection switch inside the target (chaos mode) was turned on at "
             "2026-11-15T15:15:56.681Z with failure_rate 0.08 and error_status 503; while it is on, the "
             "target rejects a random share of requests on every route with HTTP 503",
             ["switch-flipped", "rare-but-real"]),
        ],
    }
    assert sum(len(v) for v in said.values()) == 12
    for sid, statements in said.items():
        for text, mids in statements:
            for mid in mids:
                assert hits(sid, mid, text), (sid, mid, text[:60])
                old_entry = next(e for e in before[sid]["expected"]["must_claim"] if e["id"] == mid)
                if mid == "switch-flipped":   # the form the old matcher did not list
                    assert not re.search(old_entry["all_of"][0], text), (sid, text[:60])

    # The healthy-trap journals. A widened matcher belongs to another fixture, so no result of these
    # journals changes; the pin reads their claim surface against each widened matcher all the same. No
    # journal of the healthy baseline gains a match. Three journals of the two other fixtures gain one
    # each, and the pin names them: the first names the latent defect as its cause (a "Yes" row of the
    # table), the two others describe the closed window with the word "random". A fourth fails here.
    gains = set()
    for run_dir in (EVAL / "runs/bench-v1", v2):
        for trap in ("healthy-baseline", "t2-healthy-after-chaos-window", "t2-quiet-d1-suggestive-complaint"):
            for path in sorted(run_dir.glob(f"*/{trap}-r*.md")):
                rel = path.relative_to(EVAL / "runs").as_posix()
                if rel == f"bench-v2/{refused}":
                    continue
                surface = score.claim_surface(score.load_journal(str(path)))
                for (sid, mid), pattern in widened_old.items():
                    if hits(sid, mid, surface) and not re.search(pattern, surface):
                        gains.add((rel, mid))
    assert gains == {
        ("bench-v2/claude-opus-5/t2-quiet-d1-suggestive-complaint-r3.md", "location"),
        ("bench-v2/claude-sonnet-5/t2-healthy-after-chaos-window-r3.md", "spread"),
        ("bench-v1/claude-fable-5/t2-healthy-after-chaos-window-r3.md", "spread"),
    }, gains
    assert not any("healthy-baseline" in rel for rel, _ in gains)

    print("OK: 24 semantics pins hold")


# --- runner (eval/run.py) — the pure pieces ---------------------------------------------
def test_runner_envelope_meta_sums_whole_run_tokens():
    env = {"session_id": "s1", "is_error": False, "num_turns": 7, "duration_ms": 1234,
           "total_cost_usd": 1.5,
           "modelUsage": {"claude-x": {"inputTokens": 10, "outputTokens": 20,
                                       "cacheReadInputTokens": 30, "cacheCreationInputTokens": 40,
                                       "costUSD": 1.5}},
           "permission_denials": [{"tool_name": "Bash", "tool_input": {"command": "ls; curl x"}}],
           "result": "done"}
    m = runner.envelope_meta(env)
    assert m["tokens_total"] == 100 and m["model_usage"]["claude-x"]["costUSD"] == 1.5
    assert m["permission_denials"] == [{"tool": "Bash", "command": "ls; curl x"}]
    assert runner.envelope_meta({"is_error": True, "result": "x"})["tokens_total"] is None


def test_runner_stamps_tokens_once_in_the_machine_core_only():
    j = "---\nusage:\n  model: m\n  tokens: null\n  wall_clock_seconds: 5\n---\n\nBody says tokens: null too.\n"
    out, ok = runner.stamp_tokens(j, 12345)
    assert ok and "  tokens: 12345\n" in out and out.endswith("Body says tokens: null too.\n")
    assert runner.stamp_tokens(j, None) == (j, False)
    assert runner.stamp_tokens("---\nusage:\n  tokens: 7\n---\nx", 1) == ("---\nusage:\n  tokens: 7\n---\nx", False)


def test_runner_user_error_detection_ignores_investigator_probes():
    log = ('{"event": "request", "path": "/products/3", "status": 500, "request_id": "konan-1-2"}\n'
           '{"event": "request", "path": "/products", "status": 200, "request_id": "abc"}\n')
    assert not runner.user_error_landed(log)
    log += '{"event": "request", "path": "/products", "status": 503, "request_id": "u-9"}\n'
    assert runner.user_error_landed(log)


def test_runner_recognizes_quota_errors():
    assert runner.looks_like_quota_error({"is_error": True, "result": "You've hit your session limit"})
    assert runner.looks_like_quota_error({"api_error_status": 429})
    assert not runner.looks_like_quota_error({"is_error": True, "result": "journal schema invalid"})


def test_runner_worktree_name_is_neutral():
    # Check 5 of intents/bench-v2-rerun.md: the path the runner builds for a worktree carries neither
    # `eval` nor a run id, whatever call builds it — the blind-mode hook never denies a command for the
    # path alone, and the model cannot read the round off its working directory.
    with tempfile.TemporaryDirectory() as tmp:
        wt = runner.worktree_dir(base=tmp)
        below = wt.relative_to(tmp).as_posix()
        assert "eval" not in below and below.startswith("konan-wt-") and wt.name == "wt", below
    src = (EVAL / "run.py").read_text()
    assert src.count("mkdtemp(") == 1, "one call builds the worktree path"
    assert "mkdtemp(" in src.split("def worktree_dir", 1)[1].split("\ndef ", 1)[0]


# --- coverage (eval/bench.py, eval/run.py) — the pins of intents/bench-coverage.md ----------
SCENARIO_IDS = sorted(p.stem for p in (EVAL / "scenarios").glob("*.yaml"))


def _coverage_dir(tmp, model="test-model", present=27):
    """A run directory with a plan of every fixture × 3 and the first `present` of the 30 pairs
    as synthetic sidecars (status ok; the coverage needs no journal)."""
    run_dir = tmp / "bench-t"
    (run_dir / model).mkdir(parents=True)
    pairs = [(sid, r) for sid in SCENARIO_IDS for r in (1, 2, 3)]
    (run_dir / "plan.json").write_text(json.dumps({"run_id": "bench-t", "fixtures": SCENARIO_IDS, "repeat": 3}))
    for sid, r in pairs[:present]:
        (run_dir / model / f"{sid}-r{r}.meta.json").write_text(json.dumps(
            {"model": model, "scenario": sid, "rep": r, "status": "ok", "quota_error": False}))
    return run_dir, pairs[present:]


def _render(run_dir):
    return bench.build([run_dir])[3]   # the path main() renders through


def _missing_zero_lines(md):
    return [l for l in md.splitlines() if re.search(r"missing 0(\D|$)", l)]


def test_bench_coverage_short_plan():
    # Check 1: a run directory short of its plan renders the missing count at the head of the
    # table and on the model line, never only in a footnote.
    with tempfile.TemporaryDirectory() as tmp:
        run_dir, _ = _coverage_dir(Path(tmp))
        (run_dir / "test-model" / "healthy-baseline-r4.meta.json").write_text(json.dumps(   # outside the plan
            {"model": "test-model", "scenario": "healthy-baseline", "rep": 4, "status": "ok", "quota_error": False}))
        md = _render(run_dir)
        (Path(tmp) / "no-plan" / "m").mkdir(parents=True)
        try:
            bench.load_plan(Path(tmp) / "no-plan")
            raise AssertionError("a run directory without a plan was accepted")
        except SystemExit as e:
            assert e.code not in (0, None) and "plan.json" in str(e.code), e.code
    head = md.splitlines()[2]
    assert head.startswith("**Incomplete: 3 of 30 planned runs are missing** (test-model: 3)"), head
    assert ("- bench-t test-model: planned 30, completed 27, failed 0, missing 3 "
            "(0 stopped by quota and not resumed, 3 never scheduled); 1 outside the plan") in md, md
    assert md.index("## Coverage") < md.index("## Per tier")


def test_bench_coverage_complete_plan():
    # Check 2: the complete bench-v1 renders `missing 0` for each of its three models — on the
    # model lines and nowhere else — and its failed runs stay counted.
    md = _render(EVAL / "runs/bench-v1")
    lines = _missing_zero_lines(md)
    assert len(lines) == 3 and all(l.startswith("- bench-v1 claude-") for l in lines), lines
    assert "- bench-v1 claude-sonnet-5: planned 30, completed 24, failed 6, missing 0" in md
    assert md.splitlines()[2] == "Coverage: complete, 90 of 90 planned runs."


def test_bench_coverage_quota_stops():
    # Check 3: the quota stops that explain a gap are counted next to the missing count, as
    # distinct pairs (the backfill of bench-v1 has duplicate lines); a quota stop is not a run.
    with tempfile.TemporaryDirectory() as tmp:
        run_dir, missing = _coverage_dir(Path(tmp))
        (sid1, r1), (sid2, r2) = missing[0], missing[1]
        stops = [{"model": "test-model", "scenario": sid1, "rep": r1, "at": "2026-08-19T00:00:00Z"}] * 2
        stops.append({"model": "test-model", "scenario": sid2, "rep": r2, "at": "2026-08-19T01:00:00Z"})
        (run_dir / "quota-stops.jsonl").write_text("\n".join(json.dumps(s) for s in stops) + "\n")
        (run_dir / "test-model" / f"{sid1}-r{r1}.meta.json").write_text(json.dumps(
            {"model": "test-model", "scenario": sid1, "rep": r1, "status": "error", "quota_error": True}))
        md = _render(run_dir)
    assert "missing 3 (2 stopped by quota and not resumed, 1 never scheduled)" in md, md
    assert "completed 27, failed 0," in md, md


def test_bench_coverage_plan_source():
    # Check 4: the plan comes from the run directory, not from the live fixtures: an eleventh
    # fixture in the scenarios directory leaves bench-v1 at `missing 0`. The directory is a
    # copy, so the committed corpus is not touched.
    with tempfile.TemporaryDirectory() as tmp:
        scen = Path(tmp) / "scenarios"
        scen.mkdir()
        for p in (EVAL / "scenarios").glob("*.yaml"):
            (scen / p.name).write_text(p.read_text())
        text = (EVAL / "scenarios/healthy-baseline.yaml").read_text()
        assert text.count("  id: healthy-baseline\n") == 1
        (scen / "zz-added-later.yaml").write_text(text.replace("  id: healthy-baseline\n", "  id: zz-added-later\n"))
        live = bench.SCEN
        try:
            bench.SCEN = scen   # the live directory, for build(): eleven fixtures
            assert len(bench.load_fixtures()) == len(SCENARIO_IDS) + 1
            md = _render(EVAL / "runs/bench-v1")
        finally:
            bench.SCEN = live
    assert len(_missing_zero_lines(md)) == 3, md
    assert "Coverage: complete, 90 of 90 planned runs." in md


def test_bench_coverage_plan_is_pre_registered():
    # Check 5: a second invocation of a run id with other fixtures or another --repeat exits
    # non-zero and leaves plan.json unchanged; the same plan passes; a dry run writes nothing.
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "bench-t"
        runner.register_plan(out, SCENARIO_IDS, 3)
        before = (out / "plan.json").read_bytes()
        for ids, rep in ((SCENARIO_IDS, 2), (SCENARIO_IDS[:-1], 3)):
            try:
                runner.register_plan(out, ids, rep)
                raise AssertionError("another plan was accepted under the same run id")
            except SystemExit as e:
                assert e.code not in (0, None), e.code
            assert (out / "plan.json").read_bytes() == before
        runner.register_plan(out, list(reversed(SCENARIO_IDS)), 3)   # the same plan, in any order
        assert (out / "plan.json").read_bytes() == before
        runner.register_plan(Path(tmp) / "bench-dry", SCENARIO_IDS, 3, dry_run=True)
        assert not (Path(tmp) / "bench-dry" / "plan.json").exists()   # a preview registers nothing


if __name__ == "__main__":
    run()
    for t in (test_runner_envelope_meta_sums_whole_run_tokens,
              test_runner_stamps_tokens_once_in_the_machine_core_only,
              test_runner_user_error_detection_ignores_investigator_probes,
              test_runner_recognizes_quota_errors,
              test_runner_worktree_name_is_neutral):
        t()
    print("OK: 5 runner pins hold")
    for t in (test_bench_coverage_short_plan, test_bench_coverage_complete_plan,
              test_bench_coverage_quota_stops, test_bench_coverage_plan_source,
              test_bench_coverage_plan_is_pre_registered):
        t()
    print("OK: 5 coverage pins hold")
