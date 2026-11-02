# konan scorecard

Generated 2026-11-02T21:24:33+02:00 — 20 scenario(s) scored, model(s): claude-fable-5, claude-sonnet-5.
Deterministic scoring (regex + equality only); semantics: `eval/README.md`.

## Summary

- **Scenarios passed: 15/20**
- Root-cause accuracy: 15/20 (scenarios expecting a root cause)
- False attributions: 0
- Evidence-citation compliance: 20/20
- Tokens: 53893008
- Wall clock: 9201s total

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
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 3450833 | 421 |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 5902420 | 488 |
| chaos-error-rate | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3381155 | 518 |
| chaos-latency | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 5501939 | 552 |
| d1-zero-stock-product-page | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 3191717 | 434 |
| d1-zero-stock-product-page | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 1788749 | 314 |
| d1-zero-stock-product-page | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✗ | 0 | ✓ | 3222963 | 571 |
| d2-null-price-order | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 4706238 | 817 |
| d2-null-price-order | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2758669 | 522 |
| d2-null-price-order | claude-sonnet-5 | ✓ root-cause-identified | ✓ | ✓ | 0 | ✓ | 2544903 | 390 |

## Failure detail

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### chaos-error-rate

- must_claim `spread`: no match in the claim surface

### d1-zero-stock-product-page

- must_claim `data-condition`: no match in the claim surface
