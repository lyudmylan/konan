# konan scorecard

Generated 2026-08-02T07:48:55+03:00 — 5 scenario(s) scored, model(s): claude-fable-5.
Deterministic scoring (regex + equality only); semantics: `eval/README.md`.

## Summary

- **Scenarios passed: 5/5**
- Root-cause accuracy: 4/4 (scenarios expecting a root cause)
- False attributions: 0
- Evidence-citation compliance: 5/5
- Tokens: — (5 run(s) not captured)
- Wall clock: 32520s total

## Scenarios

| Scenario | Model | Verdict | Class | Root cause | False attr | Citations | Tokens | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | — | 840 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | — | 480 |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | — | 29880 |
| chaos-latency | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | — | 900 |
| healthy-baseline | claude-fable-5 | ✓ no-active-incident | — | — | 0 | ✓ | — | 420 |
