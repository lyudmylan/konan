# konan scorecard

Generated 2026-11-02T17:48:16+02:00 — 10 scenario(s) scored, model(s): claude-fable-5.
Deterministic scoring (regex + equality only); semantics: `eval/README.md`.

## Summary

- **Scenarios passed: 7/10**
- Root-cause accuracy: 7/10 (scenarios expecting a root cause)
- False attributions: 0
- Evidence-citation compliance: 10/10
- Tokens: 17443422
- Wall clock: 4174s total

## Scenarios

| Scenario | Model | Verdict | Class | Root cause | False attr | Citations | Tokens | Wall (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 2573526 | 484 |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1977653 | 378 |
| chaos-error-rate | claude-fable-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 1712411 | 311 |
| chaos-latency | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 947226 | 368 |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1567282 | 396 |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2217577 | 496 |
| d1-zero-stock-product-page | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2035336 | 431 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1741232 | 481 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1387191 | 423 |
| d2-null-price-order | claude-fable-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1283988 | 406 |

## Failure detail

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `spread`: no match in the claim surface
