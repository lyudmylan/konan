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
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

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


def base_fx(verdict="root-cause-identified"):
    return {
        "konan_fixture": 1,
        "scenario": {"id": "test-scenario", "title": "t"},
        "setup": {"lab": "fresh", "stage": ["scripts/scenario.sh get /x"]},
        "complaint": "things are broken",
        "expected": {
            "verdict": verdict,
            "incident_class": "software-defect" if verdict == "root-cause-identified" else None,
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

    print("OK: 14 semantics pins hold")


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


def test_runner_recognizes_quota_errors():
    assert runner.looks_like_quota_error({"is_error": True, "result": "You've hit your session limit"})
    assert runner.looks_like_quota_error({"api_error_status": 429})
    assert not runner.looks_like_quota_error({"is_error": True, "result": "journal schema invalid"})


if __name__ == "__main__":
    run()
    for t in (test_runner_envelope_meta_sums_whole_run_tokens,
              test_runner_stamps_tokens_once_in_the_machine_core_only,
              test_runner_recognizes_quota_errors):
        t()
    print("OK: 3 runner pins hold")
